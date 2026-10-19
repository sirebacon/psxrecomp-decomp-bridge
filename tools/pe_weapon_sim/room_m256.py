"""Room 256 (museum) boss effects, ported from the decompiled overlay (room_m256_museum/m256.c,
m256_class.c). Used by room_modules task plans for the 0x0223 boss (also room 432's script copy
only where the same programs are loaded).

Effect 132, slot 3 — RoomM256_TrailEmitter + RoomM256_TrailCallback:
  task script: hold; var6=47; wait 33; spawn controller 1 (ModelPulse, visual); wait 16; var0=0,
  spawn controller 0; wait 16; var0=2, spawn controller 0. Each TrailEmitter spawns one head on its
  age 1 with index = var0. The head starts at matrix 2 x (0,0,-10); its angles are the owner's
  matrix-0 look angles with pitch +0x200 and yaw -0x200 + index*0x200, then yaw +0x800 (it leaves
  backwards and up). Each update: look angles toward Aya; once speed >= 27 a turn angle grows by
  0x50 (max 0x800) and the motion eases toward Aya by rsin(turn) * turnScale >> 12; speed += 6
  while < 50; it moves speed^2 >> 4 along its angles (FieldFx_AnglesToVector, RotMatrixYXZ).
  Contact: Aya within 100 + her radius (X/Z) while the head is within 0x202 of the floor. When it
  reaches the floor, or the task age passes 0x50, it leaves an impact that contacts within
  0xB4 + radius for 16 frames. turnScale = max(0x200, 800 + facing/12 + (100 - L51)/5)
  (actor script 282236..282568; L51 is not resolved: bracket 800..1000).

Effect 131 + class 76, slot 4 — RoomM256_ScatterDropEmitter + RoomM256_ScatterDropCallback,
swung by RoomM256_SwingStep:
  task script: hold; var6=46; spawn controller 1 (SwirlSpark, no contact); wait 50; spawn
  controller 0. On every odd age < 110 the emitter fires a drop from matrix 4 x (0,-30,0) along
  matrix 4's look angles with pitch -0xDC and yaw + rand(-16..15), at 55..62 per update; only
  every other drop (parity) is hazardous. A drop jitters +-16 per axis, lands at floor-16 or after
  24 updates, then slides; contact within 0x19A (flying) / 0x26C (landed) + Aya's radius (X/Z).
  The swing adds a Y rotation to bone 3 once the actor enters mode 11: 0 -> a1 -> a2 -> 0 with
  eased (1 - cos) / 2 segments of the sent durations (m256_class.c RoomM256_SwingConfigure).
  Branches by the actor's facing local L11 (283000..283480): ahead (L11 < 128 or >= 3968):
  (-1100, 700) over (40, 70, 20); right/left: (-1600, 50) / (1200, -450) over (50, 70, 10).

Every contact needs the owner's action bits at 0x01, and rewrites them to 0x19: one hit per action.
Labelled simplifications: Aya stands at (0, 0, -distance) (the trail homes on that point, position
type 1); the floor is y = 0 in the actor frame and the floor polygon is not tested; rand() is Python's.
"""
import math
from functools import lru_cache

from .enemy_reach import bones_at, rot_yxz
from .room_effects import rsin, rcos

AYA_LOOK_Y = 0          # FieldFx_GetActorPosition(player, 1): the entity position (feet, floor level)
SWING_BRANCHES = {'ahead': ((-1100, 700), (40, 70, 20)), 'right': ((-1600, 50), (50, 70, 10)),
                  'left': ((1200, -450), (50, 70, 10))}


def look_angles(frm, to):
    """FieldFx_CalculateLookAngles: (pitch, yaw) in 4096 units."""
    dx, dy, dz = to[0] - frm[0], to[1] - frm[1], to[2] - frm[2]
    yaw = (-round(math.atan2(dz, dx) * 2048 / math.pi) + 1024) & 4095
    pitch = (-round(math.atan2(dy, math.hypot(dx, dz)) * 2048 / math.pi)) & 4095
    return pitch, yaw


def angles_to_vector(pitch, yaw, dist):
    """FieldFx_AnglesToVector: RotMatrixYXZ((pitch, yaw, 0)) x (0, 0, dist)."""
    p, y = pitch * math.pi / 2048, yaw * math.pi / 2048
    return (dist * math.cos(p) * math.sin(y), -dist * math.sin(p), dist * math.cos(p) * math.cos(y))


def ease(cur, target, weight):
    """FieldFx_EaseAngles for one component: move `cur` toward `target` by delta * weight >> 12."""
    c, t = cur & 4095, target & 4095
    direction = 1 if t > c else -1
    delta = abs(c - t)
    if delta >= 0x801: direction, delta = -direction, 0x1000 - delta
    return (cur + direction * ((delta * weight) >> 12)) & 0xFFFF


@lru_cache(maxsize=32)
def arm_frames(map_id, actor, enter_mode, exit_mode, enter_step, exit_step):
    """Per-update (translation, angles) of the enter then exit clip, and the update the exit clip
    (the swing's mode 11) starts."""
    from .room_modules import room_blob, animation, decode_frame
    blob = room_blob(map_id); out = []; exit_start = None
    for mode, step in ((enter_mode, enter_step), (exit_mode, exit_step)):
        p = animation(blob, actor, mode)
        if p is None: continue
        if mode == exit_mode: exit_start = len(out)
        for f in range(blob[p + 2]):
            t, a = decode_frame(blob, p, f)
            for _ in range(max(1, round(65536 / step))): out.append((t, [list(x) for x in a]))
    if not out: raise ValueError('no clips')
    return out, exit_start


def matrix(map_id, actor, rec, age, joint, add_y3=0, scale=1.0):
    from .room_modules import room_blob, model
    frames, _ = arm_frames(map_id, actor, *rec)
    t, a = frames[min(age, len(frames) - 1)]
    if add_y3:
        a = [list(x) for x in a]; a[3][1] += add_y3
    R, tr = bones_at(model(room_blob(map_id), actor), t, [tuple(x) for x in a])[joint]
    return R, [v * scale for v in tr]


def transform(R, tr, v):
    return [tr[i] + sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]


def forward_angles(R):
    """FieldFx_GetTransformLookAngles: the look angles of R x (0, 0, -1)."""
    d = [-R[i][2] for i in range(3)]
    return look_angles((0, 0, 0), d)


def swing_offset(tick, angles, durations):
    """RoomM256_SwingStep: the bone-3 Y addition `tick` updates after mode 11 (0 after release)."""
    pts = (0,) + tuple(angles) + (0,)
    for seg in range(3):
        if tick < durations[seg]:
            t = tick + 1
            phase = (t * 2048) // durations[seg]
            sweep = pts[seg + 1] - pts[seg]
            return pts[seg] + ((4096 - rcos(phase)) * sweep >> 13)
        tick -= durations[seg]
    return 0


class _Task:
    """FieldFx task script runner with the controller index (op 2's operand)."""
    def __init__(self, script, make):
        self.script, self.make = script, make

    def run(self, stepper, limit=1500):
        pc, delay, held, vars_, live, released = 0, 0, False, [0] * 7, [], None
        for upd in range(1, limit):
            while True:
                if delay:
                    delay -= 1
                    if delay: break
                op, a, b = self.script[pc]; pc += 1
                if op == 0:
                    pc -= 1
                    if held and not live: released = upd; held = False
                    break
                if op == 1: vars_[a] = b
                elif op == 2: live.append([self.make(a, vars_[0]), 0])
                elif op == 4: delay = a; break
                elif op == 5: held = held or a == 0
                else: raise ValueError('task opcode %d' % op)
            for slot in list(live):
                c, age = slot
                r = c.step(age, upd)
                if r == 2 and not c.active(): r = 1
                slot[1] += 1
                if r == 1: live.remove(slot)
            stepper(upd)
            if released is not None: return released
        raise ValueError('task did not release')


class _Visual:
    def step(self, age, upd): return 1 if age >= 40 else 0
    def active(self): return False


class TrailHead:
    def __init__(self, index, ctx):
        self.index, self.ctx, self.heads, self.impacts = index, ctx, [], []

    def step(self, age, upd):
        c = self.ctx
        if age == 1:
            R2, t2 = matrix(*c['arm'], age=upd, joint=2)
            R0, _ = matrix(*c['arm'], age=upd, joint=0)
            pos = transform(R2, t2, (0, 0, -10))
            pitch, yaw = forward_angles(R0)
            h = dict(p=list(pos), mp=(pitch + 0x200) & 0xFFFF, my=(yaw - 0x200 + (self.index << 9) + 0x800) & 0xFFFF,
                     speed=(c['rng'].randrange(8)) + 8, turn=0, init=True)
            self.heads.append(h)
        for h in list(self.heads):
            if h.pop('init', False): continue              # callback kind 0: initialise only
            tp, ty = look_angles(h['p'], (0, AYA_LOOK_Y, -c['distance']))
            if h['speed'] >= 0x1B: h['turn'] = min(0x800, h['turn'] + 0x50)
            w = (rsin(h['turn']) * c['turn_scale']) >> 12
            h['mp'] = ease(h['mp'], tp, w & 0xFFFF); h['my'] = ease(h['my'], ty, w & 0xFFFF)
            if h['speed'] < 0x32: h['speed'] += 6
            v = angles_to_vector(h['mp'], h['my'], (h['speed'] * h['speed']) >> 4)
            h['p'] = [h['p'][i] + v[i] for i in range(3)]
            if math.hypot(h['p'][0], h['p'][2] + c['distance']) < 100 + c['radius'] and h['p'][1] >= -0x202:
                c['hit'](upd)
            if h['p'][1] >= 0 or upd > 0x50:
                self.heads.remove(h); self.impacts.append(dict(p=(h['p'][0], 0, h['p'][2]), frame=0))
        for m in list(self.impacts):
            m['frame'] += 1
            if m['frame'] < 0x10 and math.hypot(m['p'][0], m['p'][2] + c['distance']) < 0xB4 + c['radius']: c['hit'](upd)
            if m['frame'] >= 0x18: self.impacts.remove(m)
        return 0 if age < 8 else 2

    def active(self): return bool(self.heads or self.impacts)


class ScatterDrops:
    def __init__(self, ctx):
        self.ctx, self.drops, self.counter = ctx, [], 0

    def step(self, age, upd):
        c = self.ctx; rng = c['rng']
        if age < 110 and age & 1:
            tick = upd - c['swing_start']
            add = swing_offset(tick, *c['swing']) if tick >= 0 else 0
            R4, t4 = matrix(*c['arm'], age=upd, joint=4, add_y3=add)
            pos = transform(R4, t4, (0, -30, 0))
            pitch, yaw = forward_angles(R4)
            v = angles_to_vector(pitch - 0xDC, yaw + (rng.randrange(32) - 16), rng.randrange(8) + 0x37)
            self.drops.append(dict(p=list(pos), v=list(v), hazard=self.counter & 1, state=0, t=0))
            self.counter += 1
        for d in list(self.drops):
            d['t'] += 1
            d['p'] = [d['p'][i] + d['v'][i] for i in range(3)]
            d['p'][0] += rng.randrange(32) - 16; d['p'][2] += rng.randrange(32) - 16
            if d['state'] == 0:
                d['p'][1] += rng.randrange(32) - 16
                if d['p'][1] >= -16 or d['t'] >= 0x18: d['state'], d['p'][1], d['v'][1] = 1, -16, 0
                r = 0x19A
            else: r = 0x26C
            if d['hazard'] and math.hypot(d['p'][0], d['p'][2] + c['distance']) < r + c['radius']: c['hit'](upd)
            if d['t'] >= 0x20: self.drops.remove(d)
        return 0 if age < 2 else 2

    def active(self): return bool(self.drops)


def _ctx(scene, distance, aya_radius, rng, **kw):
    if not scene.get('arm'): raise ValueError('room 256 effect needs the actor animation (scene arm)')
    hits = []
    ctx = dict(arm=scene['arm'], distance=distance, radius=aya_radius, rng=rng, hits=hits,
               hit=lambda upd: hits.append(upd) if not hits else None, **kw)
    return ctx


def trail_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    ctx = _ctx(sc, distance, aya_radius, rng, turn_scale=max(0x200, sc.get('trail_turn_scale', 810)))
    rel = _Task(spec['script'], lambda a, var0: TrailHead(var0, ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def scatter_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    angles, durations = SWING_BRANCHES[sc.get('swing_branch', 'ahead')]
    if sc.get('arm'):
        m, a, rec = sc['arm']; _, exit_start = arm_frames(m, a, *rec)
    else: exit_start = 0
    ctx = _ctx(sc, distance, aya_radius, rng, swing=(angles, durations), swing_start=exit_start or 0)
    rel = _Task(spec['script'], lambda a, var0: ScatterDrops(ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)
