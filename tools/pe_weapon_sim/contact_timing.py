"""Bounded timing for contact-delivered enemy actions (category 2, slots 0-2), offline.

Source (battle/context.c Entity_TriggerAnimEvent): for slots 0-2 the exit clip's wrap
completes the action (state 4, result 1) whatever the category, but only categories 1 / 3 get
their hit from the animation frame crossing. Category 2 is delivered on contact
(entity/combat.c Entity_ResolveDropTable sets state 3 when it resolves a hit for a category
other than 0 / 1). So completion is proven: enter + exit updates; the hit time is not.
Scenario: contact inside the action's own animation, i.e. windup in [enter, enter + exit - 1]
updates ('early' = first exit update, 'late' = last). Contacts after the animation (slow
projectiles) are outside this bound and must come from an effect model. Slot 3+ actions are
excluded: their completion is script-driven, not animation-driven.
Step / clip handling matches decode_enemy_actions.timing (positive fixed16 steps, own bank).
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .decode_enemy_actions import completion_reset, literal
from .enemy_identity import cells_key, identity_keys

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
ENTER, EXIT = (6, 8, 10, 12, 14), (7, 9, 11, 13, 15)


def updates(frames, step):
    return (frames * 65536 + step - 1) // step


@lru_cache(maxsize=1)
def actions():
    """[(map, actor_type, record)] for provable category-2 slot 0-2 actions."""
    inv = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    dec = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    defaults = dec['initial_records']
    banks = {}
    for room in inv['rooms']:
        if room['disc'] != 1: continue
        for s in room.get('scripts', []):
            banks[room['map'], s['actor_type']] = {b['mode']: b['frame_count'] for b in room['animations']
                                                   if b['actor_type'] == s['actor_type']}
    out = []
    for s in dec['scripts']:
        recs, steps, calls = defaultdict(list), defaultdict(set), set()
        for n in s['nodes']:
            v = [literal(x) for x in n['args']]; h = n['handler']
            if h in ('Script_SetEntityAnim12Args', 'Script_SetEntityAnim5Args') and len(v) in (5, 11) and v[0] is not None and 0 <= v[0] < 3:
                r = dict(defaults[v[0]], slot=v[0], effect_type=v[1], enter_mode=v[2], exit_mode=v[3], declaration_offset=n['offset'])
                if len(v) == 11: r.update(category=v[9], hit_frame=v[10])
                recs[v[0]].append(r)
            if h == 'Script_SetBattleEntryCoords' and len(v) == 3 and None not in v: steps[v[0]].add(tuple(v[1:]))
            if h == 'Script_RunEntityCommand' and v and v[0] is not None: calls.add(v[0])
        bank = banks.get((s['map'], s['actor_type']), {})
        for slot, rr in recs.items():
            if len(rr) != 1 or slot not in calls or (slot in steps and len(steps[slot]) != 1): continue
            r = rr[0]
            if slot in steps: r['enter_step'], r['exit_step'] = next(iter(steps[slot]))
            if r['category'] != 2 or r['enter_mode'] not in ENTER or r['exit_mode'] not in EXIT: continue
            if r['enter_mode'] not in bank or r['exit_mode'] not in bank: continue
            if min(r['enter_step'], r['exit_step']) <= 0: continue
            e, x = updates(bank[r['enter_mode']], r['enter_step']), updates(bank[r['exit_mode']], r['exit_step'])
            if x < 2: continue
            reset = all(completion_reset(s, c['offset']) for c in s['calls'] if c['slot'] == slot)
            out.append((s['map'], s['actor_type'], dict(slot=slot, reset_on_completion=reset, enter_updates=e, exit_updates=x, complete_updates=e + x,
                         early=dict(windup=e, recovery=x), late=dict(windup=e + x - 1, recovery=1),
                         declaration_offset=r['declaration_offset'])))
    return out


@lru_cache(maxsize=4)
def catalog(cells=()):
    keys = identity_keys(dict(cells))
    cand = defaultdict(list)
    for m, actor, rec in actions():
        for ident, _ in keys.get((m, actor), []):
            cand[m, ident].append(rec)
    out = {}
    for k, rows in cand.items():
        rows = sorted(rows, key=lambda r: r['slot'])
        sig = [(r['slot'], r['enter_updates'], r['exit_updates']) for r in rows]
        out[k] = rows if len(set(sig)) == len(sig) else None
    return {k: v for k, v in out.items() if v}


def contact_profile(foe, bound, cells=None):
    """{'windup', 'recovery', 'reset_on_completion', 'contact_bound', 'slot'} for the shortest
    (early) or longest (late) bounded contact action of this identity, or {}."""
    if bound not in ('early', 'late'): raise ValueError("bound must be 'early' or 'late'")
    try: rows = catalog(cells_key(cells)).get((int(foe['loc']), int(foe['name'], 16)))
    except (KeyError, ValueError, TypeError): return {}
    if not rows: return {}
    pick = (min if bound == 'early' else max)(rows, key=lambda r: (r['complete_updates'], r['slot']))
    return dict(pick[bound], reset_on_completion=pick['reset_on_completion'], contact_bound=bound, slot=pick['slot'])
