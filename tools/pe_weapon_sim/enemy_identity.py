"""Shared enemy identity resolution: literal rank/kind setters plus the scaled-rank idiom.

Logged enemy IDs are core (kind << 8) | rank (Entity fields 42 / 41). Most actor scripts set
both as literals. Ten scripts (e.g. map 358 actor 6, the run's farming room) then add a
shared-scale increment on a progress-gated branch (V74 >= 272 in map 358):

    Entity_GetField   #41 -> L(x)
    Script_EvalExpr   #15  O(a) = N(cell) * #k          (signed 32)
    Script_EvalExpr   #18  O(b) = O(a) >> 16
    Script_EvalExpr   #0   O(d) = L(x) + O(b)
    Entity_SetField   #41 <- O(d)

so the logged rank is literal + (scale*k >> 16). The same scripts initialise N10 from story
variable V80 (N10 = V80, or 65536 when V80 == 0, map 358 actor 6 root+0x54..0x8c).
FIRST_RUN_SHARED_CELLS records the value read live (read-only) at the end of a first
playthrough: V80 = N10 = 65536, V74 = 720. With a scale the alternate identity is added as a
conditional key next to the literal one; without it nothing changes (historical default).
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .projectile_geometry import s32

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
FIRST_RUN_SHARED_CELLS = {10: 65536}
FIRST_RUN_PROVENANCE = ('read-only live probe 2026-10-18, final Eve fight, isolated session port 4378: '
                        'g_ScriptVariableBank[80]=65536, g_ScriptNodeActiveFlags[10]=65536, V74=720')


def _lit(value): return dict(mode=0, value=value)


@lru_cache(maxsize=1)
def literal_identities():
    """{(map, actor_type): (kind << 8) | rank} for scripts with one literal rank and kind (disc 1;
    both discs' room blobs were verified identical)."""
    inventory = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    out = {}
    for room in inventory['rooms']:
        if room['disc'] != 1: continue
        for script in room.get('scripts', []):
            vals = defaultdict(set)
            for n in script['facts']:
                a = n['args']
                if n['handler'] == 'Entity_SetField' and len(a) == 2 and all(v['mode'] == 0 for v in a):
                    vals[a[0]['value']].add(a[1]['value'])
            if len(vals[41]) == len(vals[42]) == 1:
                out[room['map'], script['actor_type']] = (next(iter(vals[42])) << 8) | next(iter(vals[41]))
    return out


# Sentinel entry in a shared-cells dict (not a real cell): enables multi_kind_identities() keys.
MULTI_KIND = -1


@lru_cache(maxsize=1)
def multi_kind_identities():
    """{(map, actor_type): (rank, kinds)} for scripts that set one literal rank (field 41) but
    several literal kinds (field 42), e.g. room 245 actors 6-8: kind 2 at setup, kind 4 later
    (logged boss 0x0421). Every write to fields 41/42 must be literal; each literal kind is a
    value the script can leave in the core, so each (kind << 8) | rank is a candidate identity.
    Opt-in through MULTI_KIND in the cells passed to identity_keys (historical default unchanged)."""
    inventory = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    out = {}
    for room in inventory['rooms']:
        if room['disc'] != 1: continue
        for script in room.get('scripts', []):
            vals, other = defaultdict(set), set()
            for n in script['facts']:
                a = n['args']
                if n['handler'] != 'Entity_SetField' or not a or a[0] not in (_lit(41), _lit(42)): continue
                if len(a) == 2 and a[1]['mode'] == 0: vals[a[0]['value']].add(a[1]['value'])
                else: other.add(a[0]['value'])
            if not other and len(vals[41]) == 1 and len(vals[42]) > 1:
                out[room['map'], script['actor_type']] = (next(iter(vals[41])), tuple(sorted(vals[42])))
    return out


@lru_cache(maxsize=1)
def rank_default_identities():
    """{(map, actor_type): kind << 8} for scripts that write one literal kind (field 42) and never
    write the rank (field 41), which keeps the combatant template's 0: room 34 actor 4 and room 123
    actors 2-4 -> logged 0x0100. Opt-in with MULTI_KIND (identity fixes)."""
    inventory = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    out = {}
    for room in inventory['rooms']:
        if room['disc'] != 1: continue
        for script in room.get('scripts', []):
            kinds, rank_writes = set(), 0
            for n in script['facts']:
                a = n['args']
                if n['handler'] != 'Entity_SetField' or not a: continue
                if a[0] == _lit(41): rank_writes += 1
                if a[0] == _lit(42):
                    if len(a) == 2 and a[1]['mode'] == 0: kinds.add(a[1]['value'])
                    else: kinds.add(None)
            if len(kinds) == 1 and None not in kinds and rank_writes == 0:
                out[room['map'], script['actor_type']] = next(iter(kinds)) << 8
    return out


@lru_cache(maxsize=1)
def scaled_rank_rules():
    """{(map, actor_type): dict(cell, multiplier, offsets)} for exact five-instruction idioms."""
    decoded = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    out = {}
    for row in decoded['scripts']:
        nodes = row['nodes']
        found = []
        for i in range(4, len(nodes)):
            g, m, s, add, put = nodes[i - 4:i + 1]
            ga, ma, sa, aa, pa = (n['args'] for n in (g, m, s, add, put))
            contiguous = all(nodes[j]['offset'] + 8 + 4 * len(nodes[j]['args']) == nodes[j + 1]['offset'] for j in range(i - 4, i))
            if not (contiguous and g['handler'] == 'Entity_GetField' and put['handler'] == 'Entity_SetField'
                    and all(n['handler'] == 'Script_EvalExpr' for n in (m, s, add))):
                continue
            if not (ga[0] == _lit(41) and ga[1]['mode'] == 1 and pa[0] == _lit(41)
                    and ma[0] == _lit(15) and ma[2]['mode'] == 4 and ma[3]['mode'] == 0
                    and sa[0] == _lit(18) and sa[2] == ma[1] and sa[3] == _lit(16)
                    and aa[0] == _lit(0) and aa[2] == ga[1] and aa[3] == sa[1] and pa[1] == aa[1]):
                continue
            found.append(dict(cell=ma[2]['value'], multiplier=ma[3]['value'], offsets=[n['offset'] for n in (g, m, s, add, put)]))
        sigs = {(f['cell'], f['multiplier']) for f in found}
        if len(sigs) == 1:
            out[row['map'], row['actor_type']] = dict(found[0], occurrences=len(found))
    return out


def scaled_rank(identity, rule, cells):
    cell = rule['cell']
    if cell not in cells: return None
    rank = identity & 255
    inc = s32(cells[cell] * rule['multiplier']) >> 16
    return (identity & 0xFF00) | ((rank + inc) & 255)


def identity_keys(cells=None):
    """{(map, actor_type): [(identity, how)]}: the literal key, plus the scaled-branch key when
    `cells` gives the rule's shared cell."""
    lits = literal_identities()
    rules = scaled_rank_rules() if cells else {}
    out = {}
    for key, ident in lits.items():
        keys = [(ident, 'literal')]
        rule = rules.get(key)
        if rule:
            alt = scaled_rank(ident, rule, cells)
            if alt is not None and alt != ident:
                keys.append((alt, 'scaled_rank cell%d x%d' % (rule['cell'], rule['multiplier'])))
        out[key] = keys
    if cells and cells.get(MULTI_KIND):
        for key, (rank, kinds) in multi_kind_identities().items():
            if key not in out: out[key] = [((k << 8) | rank, 'literal kind %d of %s' % (k, '/'.join(map(str, kinds)))) for k in kinds]
        for key, ident in rank_default_identities().items():
            if key not in out: out[key] = [(ident, 'literal kind, template rank 0')]
    return out


def cells_key(cells):
    return tuple(sorted((int(k), int(v)) for k, v in (cells or {}).items()))
