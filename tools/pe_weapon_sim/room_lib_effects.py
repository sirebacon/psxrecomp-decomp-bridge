"""Shared room_lib effect controllers (decompiled overlays/room_lib/*.c), as task runners for
room_modules.task_plan. Same conventions as room_m256.py: the actor frame faces -Z, Aya stands at
(0, 0, -distance), the floor is y = 0, the floor polygon is not tested, contacts need the owner's
action bits at 0x01 and rewrite them (one hit per action).

RoomEffect_OrbitFlareController (orbit_flare.c), effect 115 in rooms 263/265/333 (0x1A):
  three flares (task var0 = phase 0/1/2). Each follows matrix 25 (or matrix 0 when `attached`)
  x (0, 0, -60) for 52 frames, then flies `radius` per update along
  angle = (-a / 0 / +a) + 0x400 - facing yaw (x += rcos * r, z += rsin * r) and contacts Aya within
  0x39 + her radius (X/Z). RoomLib_SetArgs3 gives (radius, a, attached), e.g. (55, 256, 0).

RoomEffect_LineBurstController (line_burst.c), effect 136:
  a line from the actor to the target point (6 updates), a ring (6 updates), then a glow at the
  target that contacts Aya within 0x104 + her radius for `duration` updates. RoomLib_SlotSet gives
  duration / countdown (literals, 300 / 300 in room 333) and the target X/Z, which the actor script
  computes (labelled: Aya's position when the effect starts).
"""
from .room_m256 import _Task, _Visual, forward_angles, transform
from .room_effects import rcos, rsin


class OrbitFlare:
    def __init__(self, phase, ctx):
        self.phase, self.ctx = phase, ctx
        a = ctx['spawn_angle']
        self.angle0 = (-a, 0, a)[min(phase, 2)]
        self.state, self.frame, self.pos = 0, 0, None

    def step(self, age, upd):
        c = self.ctx; self.frame += 1
        if self.state == 0:
            R, t = c['joint'](0 if c['attached'] else 25)(upd)
            self.pos = transform(R, t, (0, 0, -60))
            if self.frame >= 52:
                R0, _ = c['joint'](0)(upd)
                self.angle = (self.angle0 + 0x400) - forward_angles(R0)[1]
                self.state, self.frame = 1, 0
        elif self.state == 1:
            r = c['radius_step']
            self.pos[0] += rcos(self.angle) * r / 4096; self.pos[2] += rsin(self.angle) * r / 4096
            if (self.pos[0] ** 2 + (self.pos[2] + c['distance']) ** 2) ** 0.5 < 0x39 + c['radius']:
                c['hit'](upd); self.state, self.frame = 2, 0
            elif abs(self.pos[0]) > c['floor_extent'] or abs(self.pos[2]) > c['floor_extent']:
                self.state, self.frame = 2, 0                    # left the walkable area (labelled bound)
        else:
            if self.frame >= 16: return 1
        return 0

    def active(self): return False


class LineBurst:
    def __init__(self, ctx):
        self.ctx, self.state, self.timer = ctx, 0, 0

    def step(self, age, upd):
        c = self.ctx
        self.timer += 1
        if self.state in (0, 1):
            if self.timer >= 6: self.state += 1; self.timer = 0
        elif self.state == 2:
            if c['target_distance'] < 0x104 + c['radius']: c['hit'](upd)
            if self.timer >= c['duration']: self.state, self.timer = 3, 0
        elif self.timer >= 0x20:
            return 1
        return 0

    def active(self): return False


def _static_joint(j):
    """Unresolved animation: identity rotation (facing -Z) at a point 600 above the floor and 200
    ahead of the actor, for every joint (labelled scenario)."""
    return lambda age: ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, -600, -200])


def _base(scene, distance, aya_radius, rng, **kw):
    hits = []
    joint = scene.get('joint') or _static_joint     # labelled fallback when the clip is unresolved
    return dict(joint=joint, static_pose=not scene.get('joint'), distance=distance, radius=aya_radius, rng=rng, hits=hits,
                hit=lambda upd: hits.append(upd) if not hits else None, **kw)


def orbit_flare_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    radius_step, angle, attached = sc.get('steps') or (55, 256, 0)
    ctx = _base(sc, distance, aya_radius, rng, radius_step=radius_step, spawn_angle=angle, attached=attached,
                floor_extent=sc.get('floor_extent', 4000))
    rel = _Task(spec['script'], lambda a, var0: OrbitFlare(var0, ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def line_burst_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    ctx = _base(sc, distance, aya_radius, rng, duration=sc.get('line_duration', 300),
                target_distance=sc.get('line_target_miss', 0))
    rel = _Task(spec['script'], lambda a, var0: LineBurst(ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


class PhasedSparks:
    """RoomEffect_PhasedSparkController + Particle (spark_barrage.c), e.g. room 188 effect 124:
    on every sixth age while its counter (6) lasts, a spark at matrix 6 x (0, 0, -24) rises 0x6E per
    update for 16 updates, then jumps to Aya's position + rand(-600..599) in X and Z and falls 0x6E
    per update to the floor. Falling, it contacts within 0x6E + her radius once within 0x202 of the
    floor; landed, within 0xC8 + radius for 9 updates (owner bits -> 0x19, one hit per action)."""
    def __init__(self, ctx):
        self.ctx, self.left, self.sparks = ctx, 6, []

    def step(self, age, upd):
        c = self.ctx; rng = c['rng']
        if age % 6 == 0 and self.left > 0:
            R, t = c['joint'](6)(upd)
            self.sparks.append(dict(p=transform(R, t, (0, 0, -24)), phase=0, state=0, t=0)); self.left -= 1
        for s in list(self.sparks):
            s['t'] += 1
            near = lambda r: (s['p'][0] ** 2 + (s['p'][2] + c['distance']) ** 2) ** 0.5 < r + c['radius']
            if s['state'] == 0:
                if s['phase'] == 0:
                    s['p'][1] -= 0x6E
                    if s['t'] >= 16:
                        s['phase'], s['t'] = 1, 0
                        s['p'][0] = rng.randrange(1200) - 600; s['p'][2] = -c['distance'] + rng.randrange(1200) - 600
                else:
                    s['p'][1] += 0x6E
                    if s['p'][1] >= 0: s['state'], s['t'], s['p'][1] = 1, 0, 0
                if s['state'] == 0 and near(0x6E) and s['p'][1] >= -0x202: c['hit'](upd)
            else:
                if near(0xC8) and s['t'] < 9: c['hit'](upd)
                if s['t'] >= 16: self.sparks.remove(s)
        return 0 if age < 2 else 2

    def active(self): return bool(self.sparks)


def phased_spark_run(spec, distance, aya_radius, rng, scene=None):
    ctx = _base(scene or {}, distance, aya_radius, rng)
    rel = _Task(spec['script'], lambda a, var0: PhasedSparks(ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def visual_run(spec, distance, aya_radius, rng, scene=None):
    """Controllers with no contact path in their decompiled source (e.g. RoomEffect_WaveSparkController,
    spark_barrage.c: particles only draw). The effect runs to its release without hitting."""
    rel = _Task(spec['script'], lambda a, var0: _Visual()).run(lambda u: None)
    return dict(contacts=[], release=rel)


class GroundSweep:
    """RoomEffect_GroundSweepController (grab_attack.c), room 269 effect 137: starts on the floor at
    matrix 4 x ((side-1) * 350, 0, -400 - rand(256)) with a random heading; 4 updates, then 8 sweeps of
    12 updates moving distance/2 + sin(t * 0x800 / 12) * distance/2 along the heading and 4 updates
    easing the heading toward Aya (weight t * 650) while moving distance/2. Contact within 50 + her
    radius (owner bits -> 0x3D, one hit per action). distance = RoomEffect_GrabSetSlot's value."""
    side = [0]

    def __init__(self, ctx):
        from .room_m256 import look_angles
        c = self.ctx = ctx; rng = c['rng']
        GroundSweep.side[0] = 2 - GroundSweep.side[0]
        R, t = c['joint'](4)(c['start'])
        p = transform(R, t, ((GroundSweep.side[0] - 1) * 350, 0, -(rng.randrange(256)) - 400))
        self.p = [p[0] + rng.randrange(32) - 16, 0, p[2] + rng.randrange(32) - 16]
        self.yaw, self.phase, self.timer, self.sweeps = rng.randrange(4096), 0, 0, 8
        self.look = look_angles

    def step(self, age, upd):
        from .room_m256 import angles_to_vector, ease
        c = self.ctx; self.timer += 1; d = c['sweep_distance']
        if self.phase == 0:
            if self.timer >= 4: self.phase, self.timer = 1, 0
            return 0
        if self.phase == 3:
            return 1 if self.timer >= 16 else 0
        if self.phase == 1:
            s = rsin((self.timer << 11) // 12) * (d // 2) // 4096 + d // 2
        else:
            _, ty = self.look(self.p, (0, 0, -c['distance']))
            self.yaw = ease(self.yaw, ty, (self.timer * 650) & 0xFFFF); s = d // 2
        v = angles_to_vector(0, self.yaw, s); self.p[0] += v[0]; self.p[2] += v[2]
        if (self.p[0] ** 2 + (self.p[2] + c['distance']) ** 2) ** 0.5 < 50 + c['radius']: c['hit'](upd)
        if self.phase == 1 and self.timer >= 12:
            self.sweeps -= 1; self.phase, self.timer = (3 if self.sweeps <= 0 else 2), 0
        elif self.phase == 2 and self.timer >= 4: self.phase, self.timer = 1, 0
        return 0

    def active(self): return False


def ground_sweep_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    steps = sc.get('steps') or (48, 0, 0)
    ctx = _base(sc, distance, aya_radius, rng, sweep_distance=steps[0], start=0)
    def make(a, var0):
        if a: return _Visual()
        return GroundSweep(ctx)
    task = _Task(spec['script'], make)
    rel = task.run(lambda u: ctx.__setitem__('start', u))
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


class RisingSpray:
    """RoomEffect_RisingSprayController + RoomEffect_RisingSprayParticle (grab_attack.c), room 269
    effect 139: on ages 0x10..0x3C one spark per update from matrix 0's point (y - 0x50) along the
    actor's facing yaw + rand(spread) - spread/2 at speed + rand(16); a spark moves its velocity plus
    rsin(t * 292) / 256 vertically for 0x22 updates and contacts Aya within 100 + her radius (X/Z) at
    its swirl point (+-rcos/rsin(swirl) / 128); owner bits -> 0x19, one hit. (speed, spread) =
    RoomEffect_GrabSetPair's pair, e.g. (39, 1024)."""
    def __init__(self, ctx): self.ctx, self.sparks, self.burst = ctx, [], []

    def step(self, age, upd):
        from .room_m256 import angles_to_vector
        c = self.ctx; rng = c['rng']
        self.burst = [b + 1 for b in self.burst if b + 1 < 0x20]      # state-2 burst sparks: no contact, 0x20 life
        if age & 1 and age < 0x3C: self.burst.append(0)
        if 0x10 <= age < 0x3D:
            R, t = c['joint'](0)(upd)
            yaw = forward_angles(R)[1] + rng.randrange(c['spread']) - c['spread'] // 2
            v = angles_to_vector(0, yaw, c['speed'] + rng.randrange(16))
            self.sparks.append(dict(p=[t[0], t[1] - 0x50, t[2]], v=list(v), t=0, swirl=0))
        for s in list(self.sparks):
            s['t'] += 1; s['swirl'] += 200
            s['p'] = [s['p'][i] + s['v'][i] for i in range(3)]
            x = s['p'][0] + rcos(s['swirl']) / 128; z = s['p'][2] + rsin(s['swirl']) / 128
            if (x ** 2 + (z + c['distance']) ** 2) ** 0.5 < 100 + c['radius']:
                c['hit'](upd); self.sparks.remove(s); continue
            if s['t'] >= 0x22: self.sparks.remove(s)
        return 0 if age < 2 else 2

    def active(self): return bool(self.sparks or self.burst)


def rising_spray_run(spec, distance, aya_radius, rng, scene=None):
    sc = scene or {}
    speed, spread, _ = sc.get('steps') or (39, 1024, 0)
    ctx = _base(sc, distance, aya_radius, rng, speed=speed, spread=max(1, spread))
    rel = _Task(spec['script'], lambda a, var0: RisingSpray(ctx) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def grab_run(spec, distance, aya_radius, rng, scene=None):
    """Room 269 slot 5: RoomEffect_OrbitTrailBurst (visual) with the grab class (effect 77,
    grab_attack.c RoomEffect_GrabStartOnProximity): the grab catches Aya when she is within 0x100 of
    the actor's anim entry 6 (matrix 6, X/Z) while its animation frame is 8..14. Labelled: the held
    hits (GrabHold sets the hit flag each animation loop) are counted as one contact."""
    sc = scene or {}
    rel = _Task(spec['script'], lambda a, var0: _Visual()).run(lambda u: None)
    hits = []
    if sc.get('joint'):
        jt = sc['joint'](6)
        for upd in range(8 * sc.get('frame_updates', 2), 15 * sc.get('frame_updates', 2)):
            _, t = jt(upd)
            if (t[0] ** 2 + (t[2] + distance) ** 2) ** 0.5 < 0x100:
                hits.append(upd); break
    return dict(contacts=[h - 1 for h in hits], release=rel)


class SeekingTrail:
    """RoomEffect_SeekingTrailController / ScatterTrailController + particles (trail_burst_attacks.c),
    room 245 effects 140 / 141: one trail on the controller's age 1, from matrix 7 (seeking) or 5
    (scatter, yaw + rand(-256..255)) x (0, 0, -250) (s_JointOffset) with the actor's facing yaw and pitch 0. Each update
    it eases its yaw toward Aya by 0x200 / 4096 and wanders (seeking: from its third update by
    +-(t * 16 + 0x100) or half that; scatter: rand(-400..399) or rand(-256..255)), speed += 2 up to
    60, and moves speed^2 / 16. Contact when any of its last 24 points is within 0x68 (seeking) /
    0x64 (scatter) + Aya's radius (X/Z); the owner bits become 0x3F (one hit). From controller age
    0x20 it stops and fades for 16 updates."""
    def __init__(self, ctx, scatter):
        self.ctx, self.scatter, self.trail, self.age0 = ctx, scatter, None, None

    def step(self, age, upd):
        from .room_m256 import look_angles, angles_to_vector, ease
        c = self.ctx; rng = c['rng']
        if age == 1:
            R, t = c['joint'](5 if self.scatter else 7)(upd)
            R0, _ = c['joint'](0)(upd)
            yaw = forward_angles(R0)[1] + ((rng.randrange(0x200) - 0x100) if self.scatter else 0)
            self.trail = dict(p=list(transform(R, t, (0, 0, -250))), yaw=yaw & 0xFFFF, speed=0x20, t=0, fade=0, hist=[])
        tr = self.trail
        if tr:
            if tr['fade'] == 0:
                tr['t'] += 1
                _, ty = look_angles(tr['p'], (0, 0, -c['distance']))
                tr['yaw'] = ease(tr['yaw'], ty, 0x200)
                if self.scatter:
                    tr['yaw'] += (rng.randrange(800) - 400) if rng.randrange(2) == 0 else (rng.randrange(0x200) - 0x100)
                elif tr['t'] >= 3:
                    rg = tr['t'] * 16 + 0x100
                    tr['yaw'] += (rng.randrange(rg * 2) - rg) if rng.randrange(2) == 0 else (rng.randrange(rg) - (rg >> 1))
                if tr['speed'] < 0x3C: tr['speed'] += 2
                v = angles_to_vector(0, tr['yaw'], tr['speed'] * tr['speed'] // 16)
                tr['p'] = [tr['p'][i] + v[i] for i in range(3)]
            else:
                tr['fade'] += 1
                if tr['fade'] >= 16: self.trail = None
            tr['hist'] = (tr['hist'] + [tuple(tr['p'])])[-24:]
            r = (0x64 if self.scatter else 0x68) + c['radius']
            if any((x ** 2 + (z + c['distance']) ** 2) ** 0.5 < r for x, _, z in tr['hist']): c['hit'](upd)
            if age >= 0x20 and tr['fade'] == 0: tr['fade'] = 1
        return 0 if age < 8 else 2

    def active(self): return self.trail is not None


def seeking_trail_run(spec, distance, aya_radius, rng, scene=None, scatter=False):
    ctx = _base(scene or {}, distance, aya_radius, rng)
    rel = _Task(spec['script'], lambda a, var0: SeekingTrail(ctx, scatter) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def scatter_trail_run(spec, distance, aya_radius, rng, scene=None):
    return seeking_trail_run(spec, distance, aya_radius, rng, scene, scatter=True)


def _segment_distance(a, b, p):
    ax, az, bx, bz, px, pz = a[0], a[2], b[0], b[2], p[0], p[1]
    dx, dz = bx - ax, bz - az; L = dx * dx + dz * dz
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (pz - az) * dz) / L))
    return ((ax + t * dx - px) ** 2 + (az + t * dz - pz) ** 2) ** 0.5


class JointBeacon:
    """Room JointBeacon beams (m005.c / m023.c / m123.c): a beam from a joint point along the actor's
    matrix-0 look angles; its length grows `grow` per update for 5 updates (or is fixed), and Aya is
    hit when she is within `band` + her radius of the segment (FieldFx_IsPlayerInSegmentBand, X/Z
    here) while it lives (owner bits -> 0x11, one hit). Room 5: matrix 0x14, +0x200, band 100,
    13 updates; room 23: joint 8 / 0x10 (task var0), +0x19A, band 0x50, 61 updates; room 123: matrix
    0x17, fixed 0x7D0, band 0x140, 56 updates. The joint's template offset is taken as 0 (labelled)."""
    def __init__(self, ctx, joint, grow, fixed, band, life):
        self.ctx, self.joint, self.grow, self.fixed, self.band, self.life = ctx, joint, grow, fixed, band, life
        self.length = 0; self.t = 0

    def step(self, age, upd):
        from .room_m256 import angles_to_vector
        c = self.ctx; self.t += 1
        R, t = c['joint'](self.joint)(upd); R0, _ = c['joint'](0)(upd)
        pitch, yaw = forward_angles(R0)
        if self.fixed: self.length = self.fixed
        elif self.t <= 5: self.length += self.grow
        v = angles_to_vector(pitch, yaw, self.length)
        end = (t[0] + v[0], t[1] + v[1], t[2] + v[2])
        if _segment_distance(t, end, (0, -c['distance'])) < self.band + c['radius']: c['hit'](upd)
        return 1 if self.t >= self.life else 0

    def active(self): return False


BEACONS = {'RoomM005_Orbiter': dict(index=2, joint=lambda v: 0x14, grow=0x200, fixed=0, band=100, life=13),
           'RoomM023_ScatterEmitter': dict(index=2, joint=lambda v: 0x10 if v else 8, grow=0x19A, fixed=0, band=0x50, life=61),
           'RoomM123_JointTriangleEmitter': dict(index=2, joint=lambda v: 0x17, grow=0, fixed=0x7D0, band=0x140, life=56)}


def beacon_run(spec, distance, aya_radius, rng, scene=None):
    b = BEACONS[spec['controller']]
    ctx = _base(scene or {}, distance, aya_radius, rng)
    make = lambda a, var0: JointBeacon(ctx, b['joint'](var0), b['grow'], b['fixed'], b['band'], b['life']) if a == b['index'] else _Visual()
    rel = _Task(spec['script'], make).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


class _AtAge:
    """Contact at a fixed controller age, optionally only while Aya is within `radius` of an anchor
    (RoomM089_ModelPulse: anchor from RoomM089_SetAnchor, labelled Aya's position; 0xF0, ages < 0x28;
    RoomM123_PulseRing: unconditional at age 32, owner bits -> 0x21)."""
    def __init__(self, ctx, ages, life):
        self.ctx, self.ages, self.life = ctx, ages, life

    def step(self, age, upd):
        if age in self.ages: self.ctx['hit'](upd)
        return 1 if age >= self.life else 0

    def active(self): return False


def model_pulse_run(spec, distance, aya_radius, rng, scene=None):
    ctx = _base(scene or {}, distance, aya_radius, rng)
    miss = (scene or {}).get('pulse_anchor_miss', 0)
    ages = range(1, 0x28) if miss < 0xF0 + aya_radius else ()
    rel = _Task(spec['script'], lambda a, var0: _AtAge(ctx, ages, 0x40) if a == 2 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)


def pulse_ring_run(spec, distance, aya_radius, rng, scene=None):
    ctx = _base(scene or {}, distance, aya_radius, rng)
    rel = _Task(spec['script'], lambda a, var0: _AtAge(ctx, (32,), 40) if a == 0 else _Visual()).run(lambda u: None)
    return dict(contacts=[h - 1 for h in ctx['hits']], release=rel)
