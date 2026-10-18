"""Attack power held in a local / operand cell, resolved per script path (offline, conservative).

enemy_power accepts only a literal power or the adjacent multiply/shift pair. Some common
enemies compute power earlier into a local on a story-gated branch, e.g. map 358 actor 6
(the run's farming room): L2 = (N10*47)>>16, and when V74 >= 272 also rank += (N10*4)>>16
and L2 += (N10*35)>>16 before the slot-0 declaration. The rank the branch writes is what the
log records, so each evaluated path is keyed by the identity it leaves in fields 41/42.

Evaluation: from just after the last instruction this evaluator doesn't support, forward to
the declaration (jumps followed, no loops). Supported: AssignValue, EvalExpr (same operators as
script_decisions), Get/SetField with literal keys, Test/Set/ClearBit, JumpIfZero, CondBranch,
JumpToEntityOffset. Shared cells (mode 4) come from the caller (e.g. FIRST_RUN_SHARED_CELLS);
story variables (mode 2) read on a path are branched over {snapshot value, 0} with the
end-of-run snapshot; locals / operand cells (modes 1 / 3) must be written on the path. Any
other read, a Random, or an unsupported handler drops the path. Paths that reach the same
identity with different powers are rejected. This is a declaration-value catalog, not an AI
interpreter or action probability.
"""
import itertools, json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .beam_scheduling import cdiv
from .enemy_power import DECLARATIONS, power_expression
from .script_decisions import signed

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
SUPPORTED = {'Script_AssignValue', 'Script_EvalExpr', 'Entity_GetField', 'Entity_SetField', 'Script_TestBit',
             'Script_SetBit', 'Script_ClearBit', 'Script_JumpIfZero', 'Script_CondBranch', 'Script_JumpToEntityOffset'}
OPS = {0: lambda l, r: l + r, 1: lambda l, r: l - r, 2: lambda l, r: l | r, 3: lambda l, r: l & r, 4: lambda l, r: l ^ r,
       5: lambda l, r: int(bool(l or r)), 6: lambda l, r: int(bool(l and r)), 7: lambda l, r: int(not l),
       9: lambda l, r: int(l > r), 10: lambda l, r: int(l < r), 11: lambda l, r: int(l == r), 12: lambda l, r: int(l >= r),
       13: lambda l, r: int(l <= r), 14: lambda l, r: int(l != r), 15: lambda l, r: l * r, 16: lambda l, r: cdiv(l, r),
       18: lambda l, r: l >> r, 19: lambda l, r: l, 23: lambda l, r: -l}


class Unknown(Exception):
    pass


class _Taint:
    def __repr__(self): return 'TAINT'


TAINT = _Taint()


def evaluate(nodes, start, stop, base, cells, variables, fields, limit=400):
    """Run start..stop; returns (memory, fields) at stop or raises Unknown / ValueError."""
    by = {n['offset']: n for n in nodes}
    mem = {(4, k): v for k, v in cells.items()}
    mem.update({(2, k): v for k, v in variables.items()})
    fields = dict(fields)
    at, seen = start, set()

    # Taint: an unknown local / operand / shared cell / field becomes TAINT and spreads through
    # arithmetic; it only drops the path when it reaches a branch, a field 41/42 write or the
    # result (checked by the caller). Unknown story variables (mode 2) raise to be branched.
    def read(a):
        if a['mode'] == 0: return signed(a['value'])
        key = (a['mode'], a['value'])
        if key not in mem:
            if a['mode'] == 2: raise Unknown(key)
            return TAINT
        return mem[key]

    def write(a, v):
        if a['mode'] == 0: raise ValueError('literal output')
        mem[(a['mode'], a['value'])] = v if v is TAINT else signed(v)

    def known(v):
        if v is TAINT: raise ValueError('tainted control or identity')
        return v

    for _ in range(limit):
        if at == stop: return mem, fields
        if at in seen: raise ValueError('loop')
        if at not in by: raise ValueError('left the decoded nodes')
        seen.add(at); n = by[at]; a = n['args']; h = n['handler']; nxt = at + 8 + 4 * len(a)
        if h not in SUPPORTED: raise ValueError('unsupported ' + h)
        if h == 'Script_AssignValue': write(a[0], read(a[1]))
        elif h == 'Script_EvalExpr':
            op = known(read(a[0]))
            if op not in OPS: raise ValueError('operator')
            l, r = read(a[2]), read(a[3])
            write(a[1], TAINT if TAINT in (l, r) else OPS[op](l, r))
        elif h == 'Entity_GetField':
            k = known(read(a[0]))
            write(a[1], fields.get(k, TAINT))
        elif h == 'Entity_SetField':
            if a[0]['mode'] != 0: raise ValueError('indirect field key')
            v = read(a[1])
            if a[0]['value'] in (41, 42): known(v)
            fields[a[0]['value']] = v
        elif h in ('Script_TestBit', 'Script_SetBit', 'Script_ClearBit'):
            x, b = read(a[0]), read(a[1])
            v = TAINT if TAINT in (x, b) else (x & (1 << b) if h == 'Script_TestBit' else
                                               x | (1 << b) if h == 'Script_SetBit' else x & ~(1 << b))
            write(a[2] if h == 'Script_TestBit' else a[0], v)
        elif h == 'Script_JumpIfZero':
            if known(read(a[0])) == 0: nxt = known(read(a[1])) * 2 + base
        elif h == 'Script_CondBranch':
            if known(read(a[0])) != known(read(a[1])): nxt = known(read(a[2])) * 2 + base
        elif h == 'Script_JumpToEntityOffset': nxt = known(read(a[0])) * 2 + base
        at = nxt
    raise ValueError('limit')


def _literal_fields(row):
    vals = defaultdict(set)
    for n in row['nodes']:
        a = n['args']
        if n['handler'] == 'Entity_SetField' and len(a) == 2 and all(x['mode'] == 0 for x in a):
            vals[a[0]['value']].add(a[1]['value'])
    return {k: next(iter(v)) for k, v in vals.items() if len(v) == 1}


def resolve_declaration(row, decl, cells, snapshot):
    """[(identity, power, path note)] for one declaration, or [] if unresolved."""
    nodes = sorted(row['nodes'], key=lambda n: n['offset'])
    i = next(k for k, n in enumerate(nodes) if n['offset'] == decl['offset'])
    j = i
    while j > 0 and nodes[j - 1]['handler'] in SUPPORTED:
        j -= 1
    fields = _literal_fields(row)
    # The earliest start (most context) whose paths evaluate; a later start that skipped a write
    # the path needs fails with Unknown, so skipping can't silently change a value.
    for k in range(j, i):
        out = _from(row, nodes, nodes[k]['offset'], decl, cells, snapshot, fields)
        if out: return out
    return []


def _from(row, nodes, start, decl, cells, snapshot, fields):
    branch, results = [], []
    for _ in range(4):                                   # grow the set of branched story variables
        new = None
        results = []
        for combo in itertools.product(*[(snapshot[k], 0) for k in branch]):
            variables = dict(zip(branch, combo))
            try:
                mem, f = evaluate(nodes, start, decl['offset'], row['root'], cells, variables, fields)
            except Unknown as exc:
                key = exc.args[0]
                if key[0] == 2 and key[1] not in branch and key[1] < len(snapshot): new = key[1]; break
                continue
            except ValueError:
                continue
            p = decl['args'][4]
            power = (p['value'] if p['mode'] == 0 else mem.get((p['mode'], p['value'])))
            if power is None or power is TAINT or f.get(41, TAINT) is TAINT or f.get(42, TAINT) is TAINT: continue
            results.append(((f[42] << 8) | (f[41] & 255), power & 65535,
                            ','.join('V%d=%d' % kv for kv in variables.items()) or 'unbranched'))
        if new is None: break
        branch.append(new)
    return results


@lru_cache(maxsize=4)
def catalog(cells=()):
    """{(map, identity, slot): dict(power, effect_type, critical_chance, ...)} for declarations
    enemy_power leaves unresolved, evaluated at `cells` (required)."""
    if not cells: return {}
    cells = dict(cells)
    snapshot = json.loads((ROOT / 'pe-script-state-endgame-2026-10-18.json').read_text())['variables']
    decoded = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    found = defaultdict(list)
    for row in decoded['scripts']:
        chance = [n['args'][1]['value'] for n in row['nodes'] if n['handler'] == 'Entity_SetField'
                  and n['args'][0] == dict(mode=0, value=63) and n['args'][1]['mode'] == 0]
        all_chance = [n for n in row['nodes'] if n['handler'] == 'Entity_SetField' and n['args'][0] == dict(mode=0, value=63)]
        critical = chance[0] & 255 if chance and len(chance) == len(all_chance) and len(set(chance)) == 1 else None
        decls = defaultdict(list)
        for n in row['nodes']:
            if n['handler'] in DECLARATIONS and n['args'][0]['mode'] == 0:
                decls[n['args'][0]['value']].append(n)
        for slot, ns in decls.items():
            if len(ns) != 1 or critical is None: continue
            d = ns[0]
            if d['args'][1]['mode'] != 0 or power_expression(row, d) is not None: continue
            for ident, power, note in resolve_declaration(row, d, cells, snapshot):
                found[row['map'], ident, slot].append(dict(power=power, effect_type=d['args'][1]['value'],
                    critical_chance=critical, actor_type=row['actor_type'], declaration_offset=d['offset'], path=note,
                    cells=dict(cells)))
    return {k: v[0] for k, v in found.items() if all(x['power'] == v[0]['power'] for x in v)}
