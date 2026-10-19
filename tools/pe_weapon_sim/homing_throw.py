"""Thrown homing projectile + ground eruption (room_lib) as an exact timeline, offline.

Task program (room directory record, e.g. room 154 command 166): table[0] =
RoomEffect_HomingProjectile, table[7] = RoomEffect_HomingProjectileThrow, initializer =
RoomEffect_HomingProjectileConfigure; task script (5,0,0) hold, (2,7,0) spawn the throw,
(2,0,0) spawn the projectile, (0,0,0) stop. The enemy script sets the launch values with
Pm_ScriptSendCommand0 (mode 0: speed, drag, damping; 1: lift, gravity, bounce; 2: the two
report values).

Ported from room_lib/homing_projectile.c:
- Throw controller: arms on the action record's state 1 (cue 1 -> 2). In the exit clip (phase
  = exit mode) it plays forward to frame 28 and turns back to frame 23 until the projectile
  has been finished for 24 updates, then plays to the last frame, sets the cue to 4 (the action
  completes) and returns 1. Interruption (core flags 0x1800, HP <= 0) is not modelled.
- Projectile: follows render matrix 26 (enter clip, frames < 8) or 9 (offset -16, 0, -64);
  launches at exit-clip frame 2. Each update it moves (0, 0, -(speed >> 12)) along its heading;
  the gravity phase bounces off floor - 32 (lift x -bounce/16, speed x damping/16; gravity ends
  when lift <= 0x2FFFFF), then speed -= drag. It finishes when speed <= 0 or, while above
  floor - 0x200, when within 128 units (X/Z) of Aya, and starts the ground eruption (effect
  0x25) at its resting point with vars 1-5 = x, y + 32, z, scriptArg0, scriptArg1.
- Ground eruption (room_lib/ground_eruption.c): the column slot (frames 0..16) flags a
  collision while Aya is within var 4 + her cylinder radius (X/Z) of the centre; the tick
  registers the contact the following update while the owner's action state is 2, then waits
  var 5 updates.
Scenario (labelled): open floor (the walkable-polygon test always reports inside, so no
reflection), Aya stationary at distance along the enemy's heading and lateral units to the
side (0 = on the facing line; 'aimed' = on the projectile's launch line, an upper bound).
"""
from functools import lru_cache

from .enemy_reach import animation, bones_at, decode_frame, model, room_blob


def s32(v): v &= 0xFFFFFFFF; return v - (1 << 32) if v & 0x80000000 else v


@lru_cache(maxsize=32)
def _clip(map_id, actor_type, mode, joints, scale):
    blob = room_blob(map_id); mdl = model(blob, actor_type); p = animation(blob, actor_type, mode)
    if p is None: raise ValueError('missing animation mode %d' % mode)
    out = []
    k = scale / 4096
    for f in range(blob[p + 2]):
        t, a = decode_frame(blob, p, f)
        b = bones_at(mdl, t, a)
        out.append({j: ([[v * k for v in row] for row in b[j][0]], [v * k for v in b[j][1]]) for j in joints if j < len(b)})
    return out


def timeline(map_id, actor_type, enter_mode, exit_mode, enter_step, exit_step, scale, launch,
             distance, aya_radius, lateral=0, limit=3000):
    """dict(contacts, release, finish) in updates from the action start. launch: dict(speed,
    drag, damping, lift, gravity, bounce, arg0, arg1) as the Configure entry stores them."""
    enter = _clip(map_id, actor_type, enter_mode, (9, 26), scale)
    exit_ = _clip(map_id, actor_type, exit_mode, (9, 26), scale)
    if lateral == 'aimed':                              # Aya on the projectile's line (bound)
        R, t = exit_[min(2, len(exit_) - 1)][9]
        lateral = int(t[0] + sum(R[0][k] * (-16, 0, -64)[k] for k in range(3)))
    aya = (lateral, -distance)
    # Animation state (enter clip then exit clip; the throw controller drives exit playback).
    phase, pos = enter_mode, 0; step = enter_step; record_state = 0
    cue = 0; armed = False; finished = 0; done_throw = None
    m = dict(state=0, x=0, y=0, z=0, speed=launch['speed'], drag=launch['drag'], lift=launch['lift'],
             gravity=launch['gravity'], bounce=launch['bounce'] or 10, damping=launch['damping'] or 8)
    proj_done = None; eruption = None; contacts = []
    for age in range(limit):
        clip = enter if phase == enter_mode else exit_
        frame = pos >> 16
        # ---- throw controller (task slot 0) ----
        if record_state == 1 and cue == 0: cue = 1
        if cue == 1: cue = 2; armed = True
        if finished: finished += 1
        if done_throw is None and phase == exit_mode:
            if step >= 0:
                if frame >= 0x1C and finished < 0x18: step = -step
                elif frame >= len(exit_) - 1:
                    cue = 4; done_throw = age
            elif frame < 0x17: step = -step
        # ---- projectile (task slot 1) ----
        if proj_done is None:
            if m['state'] == 0:
                idx = 26 if (phase == enter_mode and frame < 8) else 9
                if phase == exit_mode and frame >= 2: m['state'] = 1
                R, t = clip[min(frame, len(clip) - 1)][idx]
                v = (-16, 0, -64) if idx == 9 else (0, 0, 0)
                p3 = [t[i] + sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]
                m['x'], m['y'], m['z'] = (int(p3[0]) << 16, int(p3[1]) << 16, int(p3[2]) << 16)
            else:
                dz = -(m['speed'] >> 12) << 12
                m['z'] += dz
                if m['gravity']:
                    m['y'] -= m['lift']
                    if (m['y'] >> 16) >= -0x20:
                        m['y'] = -0x20 << 16
                        m['lift'] = s32(-m['lift'] * m['bounce']) // 16 if -m['lift'] * m['bounce'] >= 0 else -((m['lift'] * m['bounce']) // 16)
                        m['speed'] = m['speed'] * m['damping'] // 16
                        if m['lift'] <= 0x2FFFFF: m['gravity'] = 0
                    else:
                        m['lift'] -= m['gravity']
                else:
                    m['speed'] -= m['drag']
                    if m['speed'] <= 0: finished = finished or 1
                if -0x200 < (m['y'] >> 16):
                    dx = (m['x'] >> 16) - aya[0]; dzz = (m['z'] >> 16) - aya[1]
                    if dx * dx + dzz * dzz < 0x80 * 0x80: finished = finished or 1
                if finished:
                    proj_done = age
                    eruption = dict(start=age + 1, x=m['x'] >> 16, z=m['z'] >> 16, cooldown=0, flag=0)
        # ---- ground eruption (separate effect, starts the update after the finish) ----
        if eruption and age >= eruption['start']:
            col = age - eruption['start']
            if eruption['cooldown']: eruption['cooldown'] -= 1; eruption['flag'] = 0
            elif eruption['flag'] == 1:
                eruption['flag'] = 0; eruption['cooldown'] = launch['arg1']; contacts.append(age)
            if col <= 0x10:
                dx = eruption['x'] - aya[0]; dz = eruption['z'] - aya[1]
                r = aya_radius + launch['arg0']
                if dx * dx + dz * dz < r * r: eruption['flag'] = 1
        # ---- animation advance ----
        if done_throw is not None and proj_done is not None:
            return dict(contacts=contacts, release=max(done_throw, proj_done) + 1, finish=proj_done)
        pos += step
        if phase == enter_mode and (pos >> 16) >= len(enter):
            phase, pos, step, record_state = exit_mode, 0, exit_step, 1
        elif phase == exit_mode:
            pos = max(0, min(pos, (len(exit_) - 1) << 16))
    raise ValueError('homing throw did not finish')


def launch_from_sends(sends):
    """Configure entries from the enemy script's sends [(mode, a, b, c)]."""
    out = dict(speed=0, drag=0, damping=8, lift=0, gravity=0, bounce=10, arg0=0, arg1=0)
    for mode, a, b, c in sends:
        if mode == 0: out.update(speed=a, drag=b, damping=c or 8)
        elif mode == 1: out.update(lift=a, gravity=b, bounce=c or 10)
        elif mode == 2: out.update(arg0=a, arg1=b)
    return out


@lru_cache(maxsize=1)
def actions():
    """[(map, actor, dict(slot, command, launch, reset))]: slot >= 3 calls preceded (30
    instructions) by Script_GetEntityEffect #id whose room program's table[0] is
    RoomEffect_HomingProjectile, with literal Configure sends (L, #mode, #a, #b, #c)."""
    from .decode_enemy_actions import completion_reset, literal
    from .power_gaps import _scripts
    from .room_handlers import handler
    out = []
    for (m, a), s in _scripts().items():
        nodes = sorted(s['nodes'], key=lambda n: n['offset'])
        for k, n in enumerate(nodes):
            if n['handler'] != 'Script_RunEntityCommand' or literal(n['args'][0]) is None or literal(n['args'][0]) < 3: continue
            command = None; sends = []; ok = True
            for q in nodes[max(0, k - 30):k]:
                v = [literal(x) for x in q['args']]
                if q['handler'] == 'Script_GetEntityEffect' and v[0] is not None: command, sends, ok = v[0], [], True
                elif q['handler'] == 'Pm_ScriptSendCommand0' and command is not None:
                    if None in v[1:5]: ok = False
                    else: sends.append(tuple(s32(x) for x in v[1:5]))
            if command is None or not ok or command < 85: continue
            try: h = handler(m, command, 14)
            except Exception: h = None
            if not h or not h.get('fields') or (h['fields'][0][1] or '') != 'RoomEffect_HomingProjectile': continue
            out.append((m, a, dict(slot=literal(n['args'][0]), command=command, launch=launch_from_sends(sends),
                                   reset=completion_reset(s, n['offset']))))
    return out


def homing_plan(foe, slot, cells, lateral=0):
    """Runnable plan dict(action, run(distance, aya_radius, rng)) for one identity slot, or None."""
    import json
    from collections import defaultdict
    from .enemy_identity import cells_key, identity_keys
    from .enemy_reach import move_speed
    from .power_gaps import _scripts
    from .room_modules import slot_record
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return None
    keys = identity_keys(dict(cells_key(cells)))
    rows = [dict(act, actor=a) for mm, a, act in actions() if mm == m and act['slot'] == slot
            and any(i == ident for i, _ in keys.get((mm, a), []))]
    if not rows or len({json.dumps({k: r[k] for k in ('command', 'launch', 'reset')}, sort_keys=True) for r in rows}) != 1:
        return None
    act = rows[0]; rec = slot_record(m, act['actor'], slot)
    if rec is None: return None
    ms = move_speed(_scripts()[m, act['actor']]['nodes']) or 4096
    def run(distance, aya_radius, rng):
        return timeline(m, act['actor'], rec[0], rec[1], rec[2], rec[3], ms, act['launch'], int(distance), aya_radius, lateral)
    return dict(action=act, run=run, move_speed=ms, lateral=lateral)
