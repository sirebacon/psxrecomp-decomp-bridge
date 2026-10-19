"""Contact windows for enemy melee actions (slots 0-2, every category), offline.

Source:
- field/actor_collision.c Entity_CheckActionIdMatch (Aya's contact callback, run by
  entity/allocation.c Scene_UpdateEntityPositions for each overlapping hit-sphere pair): a hit
  is registered only while the enemy's active record is in state 1 and the touching enemy
  sphere's part id is one of the record's contact ids (Script_SetObjAnimEntry12 parameters
  0-3, -1 ends the list).
- battle/context.c Entity_TriggerAnimEvent: state 1 starts when the enter clip wraps into the
  exit clip. For categories 1 / 3 the record frame crossing in the exit clip sets state 3,
  which closes the window (it is not the hit itself). A frame at or past the clip's last
  frame never crosses. The exit clip's wrap completes the action.
- entity/combat.c Entity_ResolveDropTable (called from menu/main_update.c on a registered
  contact): category 0 -> state 4 (the action ends on the hit); 2 / 3 -> state 3 (one hit);
  1 -> state unchanged (further contacts may hit until the window closes).
So timing is a window, [open, close], and whether any hit lands depends on 3D sphere contact,
which is not modelled here. Bounds: 'early' = hit at open, 'late' = hit at close.
Note: decode_enemy_actions.timing puts a category 1 / 3 hit at the frame crossing, which is
one update after this window closes.
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .contact_timing import ENTER, EXIT, updates
from .decode_enemy_actions import completion_reset, literal
from .enemy_identity import cells_key, identity_keys

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'


def window(enter_frames, exit_frames, enter_step, exit_step, category, frame):
    """dict(open, close, complete, ends_on_hit, closed_by) in updates from the action's start."""
    if min(enter_frames, exit_frames, enter_step, exit_step) <= 0: raise ValueError('positive clips and steps required')
    e, x = updates(enter_frames, enter_step), updates(exit_frames, exit_step)
    close, by = e + x - 1, 'completion'
    if category in (1, 3) and frame is not None and frame < exit_frames - 1:
        crossing = ((frame + 1) * 65536 + exit_step - 1) // exit_step
        if crossing < x: close, by = e + crossing - 1, 'frame'
    if close < e: raise ValueError('empty contact window')
    return dict(open=e, close=close, complete=e + x, ends_on_hit=category == 0, closed_by=by)


def bounds(w):
    """{'early': dict(windup, recovery), 'late': ...}; category 0 ends one update after its hit."""
    def at(t): return dict(windup=t, recovery=1 if w['ends_on_hit'] else w['complete'] - t)
    return dict(early=at(w['open']), late=at(w['close']))


@lru_cache(maxsize=1)
def actions():
    """[(map, actor_type, row)] for every provable slot 0-2 melee record with a call."""
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
                r = dict(defaults[v[0]], slot=v[0], enter_mode=v[2], exit_mode=v[3], contact_ids=None, declaration_offset=n['offset'])
                if len(v) == 11:
                    ids = []
                    for p in v[5:9]:
                        if p is None: ids = None; break
                        p = p - (1 << 32) if p >= 1 << 31 else p
                        if (p & 0xFF) >= 0x80: break          # s8 -1 ends the list
                        ids.append(p & 0xFF)
                    r.update(category=v[9], hit_frame=v[10], contact_ids=ids)
                recs[v[0]].append(r)
            if h == 'Script_SetBattleEntryCoords' and len(v) == 3 and None not in v: steps[v[0]].add(tuple(v[1:]))
            if h == 'Script_RunEntityCommand' and v and v[0] is not None: calls.add(v[0])
        bank = banks.get((s['map'], s['actor_type']), {})
        for slot, rr in recs.items():
            # Repeated declarations (phase blocks, e.g. room 86) are accepted when every timing field
            # agrees: the window is the same whichever block ran (power is resolved separately).
            timing = {(x['enter_mode'], x['exit_mode'], x.get('category'), x.get('hit_frame'), tuple(x['contact_ids'] or ())) for x in rr}
            if len(timing) != 1 or slot not in calls or (slot in steps and len(steps[slot]) != 1): continue
            r = rr[0]
            if slot in steps: r['enter_step'], r['exit_step'] = next(iter(steps[slot]))
            if r['category'] is None or r['enter_mode'] not in ENTER or r['exit_mode'] not in EXIT: continue
            if r['enter_mode'] not in bank or r['exit_mode'] not in bank: continue
            try: w = window(bank[r['enter_mode']], bank[r['exit_mode']], r['enter_step'], r['exit_step'], r['category'], r['hit_frame'])
            except ValueError: continue
            reset = all(completion_reset(s, c['offset']) for c in s['calls'] if c['slot'] == slot)
            out.append((s['map'], s['actor_type'], dict(w, **bounds(w), slot=slot, category=r['category'], hit_frame=r['hit_frame'],
                        enter_mode=r['enter_mode'], exit_mode=r['exit_mode'],
                        contact_ids=r['contact_ids'], reset_on_completion=reset, declaration_offset=r['declaration_offset'])))
    return out


@lru_cache(maxsize=4)
def catalog(cells=()):
    """{(map, identity): [row per slot]} where all actors resolving to the identity agree."""
    keys = identity_keys(dict(cells))
    cand = defaultdict(lambda: defaultdict(list))
    for m, actor, row in actions():
        for ident, _ in keys.get((m, actor), []):
            cand[m, ident][row['slot']].append(row)
    out = {}
    for k, per in cand.items():
        rows = []
        for slot, rr in sorted(per.items()):
            sig = {json.dumps({x: r[x] for x in ('open', 'close', 'complete', 'ends_on_hit', 'reset_on_completion')}) for r in rr}
            if len(sig) == 1: rows.append(rr[0])
        if rows: out[k] = rows
    return out


def melee_rows(foe, cells=None):
    try: return {r['slot']: r for r in catalog(cells_key(cells)).get((int(foe['loc']), int(foe['name'], 16)), [])}
    except (KeyError, ValueError, TypeError): return {}
