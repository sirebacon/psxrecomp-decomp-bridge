"""Why an enemy identity / slot has no source power (enemy_power / local_power rejections)."""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .enemy_identity import FIRST_RUN_SHARED_CELLS, cells_key, identity_keys
from .enemy_power import DECLARATIONS, power_expression

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'


@lru_cache(maxsize=1)
def _scripts():
    d = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    return {(s['map'], s['actor_type']): s for s in d['scripts']}


def actor_slot(row, slot):
    """Per-actor facts for one slot's power declaration."""
    decl = [n for n in row['nodes'] if n['handler'] in DECLARATIONS and n['args'][0] == dict(mode=0, value=slot)]
    chance = [n for n in row['nodes'] if n['handler'] == 'Entity_SetField' and n['args'][0] == dict(mode=0, value=63)]
    lit = {n['args'][1]['value'] for n in chance if n['args'][1]['mode'] == 0}
    out = dict(declarations=len(decl), calls=sum(1 for c in row['calls'] if c['slot'] == slot),
               critical=('none' if not chance else 'literal' if len(lit) == 1 and all(n['args'][1]['mode'] == 0 for n in chance)
                         else 'varies' if len(lit) > 1 else 'non-literal'))
    if decl:
        exprs = [power_expression(row, n) for n in decl]
        out['power_modes'] = [n['args'][4]['mode'] for n in decl]
        out['expressions'] = [e['kind'] if e else 'unproved' for e in exprs]
        out['effect_literal'] = all(n['args'][1]['mode'] == 0 for n in decl)
    return out


def reasons(loc, name, slot, cells=FIRST_RUN_SHARED_CELLS):
    keys = identity_keys(dict(cells_key(cells)))
    m, ident = int(loc), int(name, 16)
    actors = sorted(a for (mm, a), ids in keys.items() if mm == m and any(i == ident for i, _ in ids))
    if not actors: return dict(reason='no actor resolves to this identity', actors=[])
    facts = {a: actor_slot(_scripts()[m, a], slot) for a in actors if (m, a) in _scripts()}
    callers = {a: f for a, f in facts.items() if f['calls']}
    if not callers: return dict(reason='slot never called by these actors', actors=actors, facts=facts)
    for a, f in callers.items():
        if f['declarations'] == 0: return dict(reason='called slot has no declaration in actor script', actors=actors, facts=facts)
        if f['declarations'] > 1: return dict(reason='several declarations for the slot', actors=actors, facts=facts)
        if f['expressions'][0] == 'unproved': return dict(reason='power operand not literal / scaled idiom', actors=actors, facts=facts)
        if f['critical'] != 'literal': return dict(reason='critical chance ' + f['critical'], actors=actors, facts=facts)
        if not f['effect_literal']: return dict(reason='effect type not literal', actors=actors, facts=facts)
    return dict(reason='actors disagree', actors=actors, facts=facts)
