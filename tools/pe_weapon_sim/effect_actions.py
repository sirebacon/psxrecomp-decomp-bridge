"""Effect-driven enemy actions (slot 3+) for the common room-library effects 115 / 122 / 136.

Catalog: in each decoded actor script, a Script_RunEntityCommand on a literal slot >= 3 whose
preceding 30 instructions load one of these effects (Script_GetEntityEffect #id) and send it
literal arguments (Pm_ScriptSendCommand0); 122's speed may come from a Script_Random range in
the same window. Identity keys come from enemy_identity (optionally with shared cells).
Charge reset at completion is proven per call path as in decode_enemy_actions.

EffectEnemy plays the uninterrupted source timeline (room_effects) from the distance at the
moment the command starts: strikes on the controller contacts (geometric, no hit roll),
completes on the owner release. Scenario inputs (explicit, defaults labelled): emitter height
480 (122), walkable exit 3000 along the path (115), Aya's offset from the line-burst target
point 0 (136: target cells N25..N28 are written elsewhere; 0 = aimed where Aya stands), and
Aya's cylinder radius from her equipped weapon model.
"""
import json, random
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .decode_enemy_actions import completion_reset
from .enemy_identity import cells_key, identity_keys
from . import room_effects as RE

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
EFFECTS = (115, 122, 136)
DEFAULT_SCENARIO = dict(height=480, floor_exit=3000, target_offset=0)


def _lit(a): return a['value'] if a['mode'] == 0 else None


def _signed(v): return v - (1 << 32) if v >= 1 << 31 else v


@lru_cache(maxsize=1)
def actions():
    """[(map, actor_type, action)] with action = dict(slot, effect, params, reset, offset)."""
    dec = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    out = []
    for s in dec['scripts']:
        nodes = sorted(s['nodes'], key=lambda n: n['offset'])
        for k, n in enumerate(nodes):
            if n['handler'] != 'Script_RunEntityCommand' or _lit(n['args'][0]) is None or _lit(n['args'][0]) < 3:
                continue
            window = nodes[max(0, k - 30):k]
            eff = None; sends = []; randoms = {}
            for p in window:
                a = p['args']
                if p['handler'] == 'Script_GetEntityEffect' and _lit(a[0]) in EFFECTS:
                    eff, sends = _lit(a[0]), []
                elif p['handler'] == 'Pm_ScriptSendCommand0' and eff is not None:
                    sends.append(a)
                elif p['handler'] == 'Script_Random' and a[0]['mode'] != 0 and None not in (_lit(a[1]), _lit(a[2])):
                    randoms[(a[0]['mode'], a[0]['value'])] = (_signed(_lit(a[1])), _signed(_lit(a[2])))
            if eff is None or not sends: continue
            params = _params(eff, sends, randoms)
            if params is None: continue
            slot = _lit(n['args'][0])
            reset = completion_reset(s, n['offset'])
            out.append((s['map'], s['actor_type'], dict(slot=slot, effect=eff, params=params, reset=reset,
                                                        offset=n['offset'] - s['root'])))
    return out


def _params(eff, sends, randoms):
    m1 = [a for a in sends if _lit(a[1]) == 1]
    if len(m1) != 1: return None
    a = m1[0]
    if eff == 122:
        speed = _lit(a[2])
        rng = (speed, speed + 1) if speed is not None else randoms.get((a[2]['mode'], a[2]['value']))
        lift = _lit(a[3])
        if rng is None or lift is None: return None
        return dict(speed_range=list(rng), lift=lift)          # Script_Random: [lo, hi)
    if eff == 136:
        duration, countdown = _lit(a[3]), _lit(a[4])
        if None in (duration, countdown): return None
        return dict(duration=duration, countdown=countdown)
    if eff == 115:
        radius, angle, attached = _lit(a[2]), _lit(a[3]), _lit(a[4])
        if None in (radius, angle, attached) or attached: return None   # attached flares follow joint 0
        return dict(radius=radius, angle=angle)
    return None


@lru_cache(maxsize=4)
def catalog(cells=()):
    keys = identity_keys(dict(cells))
    cand = defaultdict(list)
    for m, actor, act in actions():
        for ident, _ in keys.get((m, actor), []):
            cand[m, ident].append(act)
    out = {}
    for k, rows in cand.items():
        sig = {json.dumps({x: r[x] for x in ('slot', 'effect', 'params', 'reset')}, sort_keys=True) for r in rows}
        if len(sig) == 1: out[k] = rows[0]          # one consistent effect action per identity
    return out


def effect_profile(foe, cells=None):
    try: return dict(catalog(cells_key(cells)).get((int(foe['loc']), int(foe['name'], 16))) or {})
    except (KeyError, ValueError, TypeError): return {}


def timeline(action, distance, aya_radius, scenario, rng):
    sc = dict(DEFAULT_SCENARIO, **(scenario or {}))
    p = action['params']; d = int(distance)
    if action['effect'] == 122:
        lo, hi = p['speed_range']
        return RE.dropped_flare(rng.randrange(lo, hi), d, sc['height'], aya_radius, p['lift'])
    if action['effect'] == 136:
        return RE.line_burst(int(sc['target_offset']), aya_radius, p['duration'], p['countdown'])
    return RE.orbit_flare(d, aya_radius, sc['floor_exit'], p['radius'], p['angle'])


class EffectEnemy:
    """Charge -> effect action from the current distance; strikes on contacts; completes at the
    owner release (charge reset at start, or at completion when the script proves it)."""

    def __init__(self, clock, action, *, distance, aya_radius, scenario=None, rng=None):
        self.clock, self.action, self.distance = clock, action, distance
        self.aya_radius, self.scenario = aya_radius, scenario
        self.rng = rng or random.Random(0)
        self.phase, self.age, self.plan = 'charge', 0, None
        self.last_strike_geometric = False
        self.actions = self.contacts = 0

    def tick(self, *, paused=False):
        poison = self.clock.tick(paused=paused); self.last_strike_geometric = False
        if paused or self.clock.incapacitated: return False, poison
        if self.phase == 'charge':
            if self.clock.charge >= 9000:
                if not self.action['reset']: self.clock.charge = 0
                self.plan = timeline(self.action, self.distance, self.aya_radius, self.scenario, self.rng)
                self.phase, self.age = 'action', 0; self.actions += 1
            return False, poison
        self.age += 1
        strike = self.age in self.plan['contacts']
        if strike:
            self.last_strike_geometric = True; self.contacts += 1
        if self.age >= self.plan['release']:
            if self.action['reset']: self.clock.charge = 0
            self.phase = 'charge'
        return strike, poison
