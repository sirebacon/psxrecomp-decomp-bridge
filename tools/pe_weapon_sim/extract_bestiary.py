"""Offline enemy stat inventory for every room on both US discs (Bestiary groundwork).

Reads the room sector table (g_RoomSectorTable) for maps 1-440, builds each actor script's
control flow (decode_enemy_actions.flow) and evaluates its setup code up to the last stat
write. Stats are written with Entity_SetField -> Entity_WriteFieldByCmd (battle/context.c):

    0x29 rank, 0x2A kind (logged ID = kind<<8 | rank)   0x28 EXP (+0x0E)
    0x2C HP (+0x10)        0x3D defense (+0x8C)          0x3E charge step (+0x8E)
    0x3F critical chance   0x45 poison tick (+0x96)       0x5A / 0x5B BP base / factor
    0x5C drop (+0x9E)      0x5D steal (+0x9F)
    0x64 cyanide, 0x65 acid, 0x66 tranq, 0x6A steal resist, 0x6B heat, 0x6C frost
    (status_flags2 2-bit fields: 0 average, 1 strong, 2 weak), 0x6D boss (can't escape)

Common enemies compute HP / defense as (N10 * base) >> 16 through operand cells, where
shared cell N10 comes from story variable V80 (65536 on a first playthrough), and roll drop /
steal with Script_Random (uniform [lo, hi), flow_opcodes.c). The evaluator enumerates small
Random ranges exactly (probabilities), forks story-variable reads over {end-of-run snapshot,
0} (labelled variants) and forks unknown values both ways. Unsupported handlers are no-ops
whose non-literal operands become unknown. A static setup evaluation, not an AI trace.
No game connection; the PST snapshot only supplies the handler and room tables.
"""
import argparse, hashlib, heapq, json, re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from .decode_enemy_actions import flow
from .extract_animations import ram_from_pst
from .extract_enemy_scripts import BRIDGE, PROJECT, sectors, word
from .local_power import OPS
from .script_decisions import signed as s32

FIELDS = {0x29: 'rank', 0x2A: 'kind', 0x28: 'exp', 0x2C: 'hp', 0x3D: 'defense', 0x3E: 'charge',
          0x3F: 'crit', 0x45: 'poison', 0x5A: 'bp_base', 0x5B: 'bp_factor', 0x5C: 'drop',
          0x5D: 'steal', 0x64: 'cyanide', 0x65: 'acid', 0x66: 'tranq', 0x6A: 'steal_resist',
          0x6B: 'heat', 0x6C: 'frost', 0x6D: 'boss'}
BYTE = {'rank', 'kind', 'drop', 'steal', 'crit'}
SIGNED16 = {'poison'}
U16 = {'exp', 'defense', 'charge', 'bp_base', 'bp_factor'}   # EnemyCombatant widths (battle.h)
TWO_BITS = {'cyanide', 'acid', 'tranq', 'steal_resist', 'heat', 'frost'}
MAPS = range(1, 441)
MAX_RANDOM = 256
UNKNOWN = 'unknown'


def stat_value(name, value):
    if value == UNKNOWN: return value
    if name in BYTE: return value & 255
    if name in U16: return value & 65535
    if name in TWO_BITS: return value & 3
    if name == 'boss': return value & 1
    if name in SIGNED16:
        value &= 65535
        return value - 65536 if value >= 32768 else value
    return value & 0xFFFFFFFF if name == 'hp' else value


def slugs():
    out = {}
    for p in (PROJECT/'parasite-eve-decomp/configs/USA/overlays').glob('room_m*.yaml'):
        m = re.match(r'room_m(\d+)_?(.*)\.yaml$', p.name)
        if m: out[int(m.group(1))] = m.group(2) or None
    return out


def block(map_id):
    """Story block from the decomp's docs/ROOMS.md (map numbers follow story order for 1-287)."""
    for lo, hi, name in ((1, 34, 'Day 1'), (35, 56, 'Days 1-2'), (57, 89, 'Day 2'), (90, 160, 'Day 3'),
                         (161, 190, 'Day 4'), (191, 270, 'Days 4-5'), (271, 287, 'Day 6'),
                         (288, 318, 'Chrysler (EX)'), (319, 381, 'late addition'),
                         (382, 424, 'Chrysler (EX)'), (425, 433, 'special scene'), (434, 437, 'Chrysler (EX)')):
        if lo <= map_id <= hi: return name
    return None


def evaluate_setup(cfg, start, variables, limit=200000, base=None, stop=None):
    """[(variant, probability, {field: (value, write offset)})] over the setup paths of one script.

    `start` is where evaluation begins; `base` (default `start`) is the script root that jump
    offsets are relative to; `stop` (exclusive) bounds the block, so later phase writes
    (a boss's second-phase HP) don't overwrite the setup values."""
    base = start if base is None else base
    by = {n['offset']: n for n in cfg['nodes']}
    setters = [n['offset'] for n in cfg['nodes'] if n['handler'] == 'Entity_SetField' and len(n['args']) == 2
               and n['args'][0]['mode'] == 0 and (n['args'][0]['value'] & 255) in FIELDS and n['offset'] >= start
               and (stop is None or n['offset'] < stop)]
    if not setters: return []
    last = max(setters)
    states = defaultdict(Fraction)          # (pc, mem, fields, variant) -> probability
    states[(start, (), (), ())] = Fraction(1)
    heap = [start]; queued = {start}; done = defaultdict(Fraction); steps = 0
    while heap:
        pc = heapq.heappop(heap); queued.discard(pc)
        batch = [(k, p) for k, p in states.items() if k[0] == pc]
        for k, _ in batch: del states[k]
        for (pc_, mem_t, fields_t, variant), prob in batch:
            steps += 1
            if steps > limit: raise ValueError('setup evaluation limit')
            for nxt, mem, fields, var, p in _step(by, pc, dict(mem_t), dict(fields_t), variant, prob, base, variables):
                if nxt is None or nxt > last or nxt not in by or nxt <= pc:
                    done[(var, tuple(sorted(fields.items())))] += p
                    continue
                key = (nxt, tuple(sorted(mem.items())), tuple(sorted(fields.items())), var)
                if nxt not in queued: heapq.heappush(heap, nxt); queued.add(nxt)
                states[key] += p
    return [(var, p, dict(f)) for (var, f), p in done.items()]


def _step(by, pc, mem, fields, variant, prob, base, variables):
    n = by[pc]; a = n['args']; h = n['handler']; nxt = pc + 8 + 4 * len(a)

    def read(x):
        if x['mode'] == 0: return s32(x['value'])
        return mem.get((x['mode'], x['value']), UNKNOWN)

    def write(x, v):
        if x['mode'] != 0: mem[(x['mode'], x['value'])] = v if v == UNKNOWN else s32(v)

    # A story variable not yet seen on this path forks over {snapshot, 0}; the value is then
    # remembered in mem, so later reads on the path agree.
    for x in a:
        if x['mode'] == 2 and (2, x['value']) not in mem:
            v = x['value']; out = []
            for val in sorted({s32(variables[v]) if v < len(variables) else 0, 0}):
                m2 = dict(mem); m2[(2, v)] = val
                out += _step(by, pc, m2, dict(fields), tuple(sorted(set(variant) | {('V%d' % v, val)})), prob, base, variables)
            return out

    def branch(test_nonzero, target):
        if test_nonzero == UNKNOWN:
            # One shared flag (not one label per branch) so the two sides can merge again.
            v2 = variant if ('?', 1) in variant else tuple(sorted(variant + (('?', 1),)))
            return [(nxt, mem, fields, v2, prob), (target, dict(mem), dict(fields), v2, prob)]
        return [(nxt if test_nonzero else target, mem, fields, variant, prob)]

    if h == 'Script_AssignValue' and len(a) == 2: write(a[0], read(a[1]))
    elif h == 'Script_EvalExpr' and len(a) == 4:
        op, l, r = read(a[0]), read(a[2]), read(a[3])
        write(a[1], UNKNOWN if UNKNOWN in (op, l, r) or op not in OPS else OPS[op](l, r))
    elif h == 'Script_Random' and len(a) == 3:
        lo, hi = read(a[1]), read(a[2])
        if UNKNOWN in (lo, hi) or lo == hi or not 0 < hi - lo <= MAX_RANDOM:
            write(a[0], UNKNOWN)
        else:
            out = []
            for v in range(lo, hi):
                m2 = dict(mem); m2[(a[0]['mode'], a[0]['value'])] = v
                out.append((nxt, m2, dict(fields), variant, prob / (hi - lo)))
            return out
    elif h == 'Entity_GetField' and len(a) == 2:
        k = read(a[0]); write(a[1], fields.get(k & 255, (UNKNOWN,))[0] if k != UNKNOWN else UNKNOWN)
    elif h == 'Entity_SetField' and len(a) == 2:
        k = read(a[0])
        if k != UNKNOWN: fields[k & 255] = (read(a[1]), pc)     # value and where it was written
    elif h in ('Script_TestBit', 'Script_SetBit', 'Script_ClearBit') and len(a) >= 2:
        x, b = read(a[0]), read(a[1])
        v = UNKNOWN if UNKNOWN in (x, b) else (x & (1 << b) if h == 'Script_TestBit' else
                                                 x | (1 << b) if h == 'Script_SetBit' else x & ~(1 << b))
        write(a[2] if h == 'Script_TestBit' else a[0], v)
    elif h == 'Script_JumpIfZero' and len(a) == 2:
        t, target = read(a[0]), read(a[1])
        if target == UNKNOWN: return [(None, mem, fields, variant, prob)]
        return branch(UNKNOWN if t == UNKNOWN else t != 0, base + target * 2)
    elif h == 'Script_CondBranch' and len(a) == 3:
        l, r, target = read(a[0]), read(a[1]), read(a[2])
        if target == UNKNOWN: return [(None, mem, fields, variant, prob)]
        return branch(UNKNOWN if UNKNOWN in (l, r) else l == r, base + target * 2)
    elif h == 'Script_JumpToEntityOffset' and a:
        t = read(a[0])
        return [(None if t == UNKNOWN else base + t * 2, mem, fields, variant, prob)]
    elif h in ('Entity_MarkCurrentNodeFree', 'Entity_MarkCurrentDead'):
        return [(None, mem, fields, variant, prob)]
    else:
        for x in a:
            if x['mode'] in (1, 3, 4): mem[(x['mode'], x['value'])] = UNKNOWN
    return [(nxt, mem, fields, variant, prob)]


def summarize(paths):
    """Group evaluated paths by variant: fixed stats plus drop / steal (and any varying) odds."""
    out = []
    by = defaultdict(list)
    # Split by identity and HP too: an unresolved branch can choose between whole stat blocks.
    ident = lambda f: tuple(str(f[k][0]) if k in f else '' for k in (0x29, 0x2A, 0x2C, 0x28))
    for var, p, f in paths: by[(var, ident(f))].append((p, f))
    for (var, _), rows in sorted(by.items()):
        total = sum(p for p, _ in rows); stats = {}; writes = {}
        for key, name in FIELDS.items():
            dist = defaultdict(Fraction); at = set()
            for p, f in rows:
                if key in f: dist[stat_value(name, f[key][0])] += p / total; at.add(f[key][1])
            if not dist: continue
            stats[name] = next(iter(dist)) if len(dist) == 1 else {str(k): round(float(v), 4) for k, v in sorted(dist.items(), key=lambda kv: -kv[1])}
            writes[name] = sorted(at)
        out.append(dict(variant=dict(var), stats=stats, writes=writes))
    return out


def room_enemies(blob, handlers, variables):
    directory = word(blob, 4)
    def records(field):
        desc = word(blob, directory + field); at = desc & 0x3fffff; count = desc >> 22
        return [word(blob, at + 12 * i + 4) & 0xffffff for i in range(count)]
    blocks = records(20)
    if not blocks: return []
    base = blocks[0]; count = word(blob, base + 4)
    if count > 256: raise ValueError('implausible relocation count')
    roots = [base + word(blob, base + 8 + 4 * i) for i in range(count)]
    # Other record tables bound the scripts, but some hold data words (e.g. map 217 table 36 has
    # 131193): only 4-byte-aligned pointers inside the script area are boundaries.
    bounds = sorted(set(roots + [p for f in (24, 28, 32, 36, 40, 44, 48) for p in records(f) if p % 4 == 0 and p > base]
                        + [len(blob)]))
    out = []
    for actor, start in enumerate(roots):
        if actor == 0: continue
        end = next((v for v in bounds if v > start), len(blob))
        cfg = flow(blob, start, end, handlers)
        keep = lambda v: 'hp' in v['stats'] and ('rank' in v['stats'] or 'kind' in v['stats'])
        try:
            variants = [dict(v, entry=start, how='script start') for v in summarize(evaluate_setup(cfg, start, variables)) if keep(v)]
            if not variants:
                # Boss scripts dispatch to their stat block (an event branch / callback): evaluate
                # each block from its entry (after the last terminator above it) to its end.
                for at, stop in block_entries(cfg):
                    variants += [dict(v, entry=at, how='stat block entry')
                                 for v in summarize(evaluate_setup(cfg, at, variables, base=start, stop=stop)) if keep(v)]
        except ValueError as exc:
            out.append(dict(actor_type=actor, script_start=start, error=str(exc))); continue
        if variants: out.append(dict(actor_type=actor, script_start=start, script_end=end, variants=variants, flow_errors=len(cfg['errors'])))
    return out


TERMINATORS = {'Entity_MarkCurrentNodeFree', 'Entity_MarkCurrentDead'}


def block_entries(cfg):
    """(entry, end) of each stat-writing block: from just after the nearest node-free / dead
    marker above its first identity / HP write (skipping a jump that leaves the previous block)
    to the next marker. Jumps inside the block (drop rolls) are followed by the evaluator."""
    nodes = cfg['nodes']; blocks = []; i = 0
    while i < len(nodes):
        n = nodes[i]
        if n['handler'] == 'Entity_SetField' and len(n['args']) == 2 and n['args'][0]['mode'] == 0 and n['args'][0]['value'] in (0x29, 0x2C):
            j = i
            while j > 0 and nodes[j - 1]['handler'] not in TERMINATORS: j -= 1
            while j < i and nodes[j]['handler'] == 'Script_JumpToEntityOffset': j += 1
            while i < len(nodes) and nodes[i]['handler'] not in TERMINATORS: i += 1
            end = nodes[i]['offset'] if i < len(nodes) else nodes[-1]['offset'] + 1
            if nodes[j]['offset'] not in [b[0] for b in blocks]: blocks.append((nodes[j]['offset'], end))
        i += 1
    return blocks


def main():
    ap = argparse.ArgumentParser(__doc__); ap.add_argument('--out', required=True); a = ap.parse_args()
    snapshot = BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst'
    ram = ram_from_pst(snapshot)
    symbols = (PROJECT/'parasite-eve-decomp/configs/USA/sym.main.txt').read_text()
    names = {int(addr, 16): name for name, addr in re.findall(r'(\w+)\s*=\s*(0x[0-9A-Fa-f]+);', symbols)}
    handlers = [names.get(word(ram, 0x910a0+i*4)) for i in range((0x91464-0x910a0)//4)]
    state = BRIDGE/'findings/data/pe-script-state-endgame-2026-10-18.json'
    variables = json.loads(state.read_text())['variables']
    slug = slugs(); rooms = []
    for disc in (1, 2):
        path = PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin'
        with path.open('rb') as f:
            for map_id in MAPS:
                start = word(ram, 0x93378+(map_id-1)*8); packed = word(ram, 0x9337c+(map_id-1)*8)
                if packed >> 20 == 0: continue
                lba = word(ram, 0xb0dd8)+start+(packed & 255)+((packed >> 8) & 4095); count = packed >> 20
                row = dict(disc=disc, map=map_id, place=slug.get(map_id), block=block(map_id), lba=lba, sectors=count)
                try:
                    blob = sectors(f, lba, count)
                    row['sha256'] = hashlib.sha256(blob).hexdigest()
                    row['enemies'] = room_enemies(blob, handlers, variables)
                except Exception as exc:  # noqa: BLE001 - recorded per room, never fatal
                    row['error'] = str(exc)
                rooms.append(row)
    same = defaultdict(set)
    for r in rooms: same[r['map']].add(r.get('sha256'))
    out = dict(scope='Static setup evaluation of room actor scripts (see module docstring); not an AI trace.',
               locate=('Every offset (script_start, entry, writes) is a byte offset into the room blob, the room\'s '
                       'sectors read in order from `lba` (2048 user-data bytes each). Room offset X is in disc sector '
                       'lba + X // 2048 at user-data byte X % 2048 of "Parasite Eve (USA) (Disc N).bin". Each write '
                       'offset is the Entity_SetField instruction that sets that field; `entry` is where the '
                       'evaluation started (script start, or the stat block a boss script dispatches to).'),
               snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
               variables_sha256=hashlib.sha256(state.read_bytes()).hexdigest(),
               fields={hex(k): v for k, v in FIELDS.items()},
               maps_identical_on_both_discs=sorted(m for m, s in same.items() if len(s) == 1 and None not in s),
               rooms=rooms)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding='utf-8')
    print(json.dumps(dict(rooms=len(rooms), errors=sum('error' in r for r in rooms),
                          rooms_with_enemies=sum(bool(r.get('enemies')) for r in rooms),
                          enemy_scripts=sum(len(r.get('enemies', [])) for r in rooms),
                          script_errors=sum('error' in e for r in rooms for e in r.get('enemies', [])))))


if __name__ == '__main__': main()
