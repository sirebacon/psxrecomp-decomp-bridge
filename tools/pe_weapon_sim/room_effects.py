"""Common room-library attack effects as exact task-driven timelines (offline).

Slot 3+ enemy actions are effect-driven: the script loads an effect (Script_GetEntityEffect ->
Scene_LoadRoomAssets), sends its arguments (Pm_ScriptSendCommand0 -> the program initializer),
and Script_RunEntityCommand waits until the effect releases the owner: FieldFx_UpdateTasks
opcode 0 sees no live controller and sets the owner's action state to 4
(src/main/fieldfx/geometry.c:2174). Hits are contacts the controllers latch (player flag
0x4000), delivered by the battle pass.

Ported here (src/overlays/room_lib):
  122 RoomEffect_DroppedFlareEmitter / _DroppedFlareParticle  (dropped_flare.c)
  136 RoomEffect_LineBurstController                            (line_burst.c)
  115 RoomEffect_OrbitFlareController                           (orbit_flare.c)
with the task scripts read from the room directories (identical in every room using them).

FieldFx_UpdateTasks per effect update: script first (delay, op0 stop gate with live count,
op1 variable, op2 spawn = count++ and the controller's mode-0 init, op4 wait, op5 held), then
each live controller's mode 1 with its age; a controller with a particle list also updates the
list (FieldFx_UpdateCallbackList counts entries active at the start of the pass); return 1
frees the slot, return 2 frees it only when that count was 0.

Geometry is an explicit scenario: horizontal distance from the effect origin to Aya, the
emitter height above the floor (122), the walkable-area exit distance along the controller's
path (115, a circle around the origin instead of the room polygon), and Aya's model cylinder
radius (weapon dependent). Aya is stationary. Contact tests are X/Z only, as in
FieldFx_IsPlayerWithinRadius. Particle randomness only moves cosmetic children; it does not
change contact or release here, except the 122 scatter children's lifetimes, which are fixed.
"""
import functools, math, struct

from .extract_enemy_scripts import PROJECT

EXE = PROJECT / 'parasite-eve-recomp/disc/SLUS_006.62.original-backup'
TASKS = {  # task triples from the room directories (rooms 12/14/113/263/333, 113/115/263/333, 126/147/152)
    115: [(5, 0, 0), (1, 6, 30), (1, 0, 0), (2, 0, 0), (1, 0, 1), (2, 0, 0), (1, 0, 2), (2, 0, 0), (4, 2, 0), (0, 0, 0)],
    136: [(5, 0, 0), (1, 6, 51), (4, 29, 0), (2, 0, 0), (0, 0, 0)],
    122: [(5, 0, 0), (1, 6, 37), (4, 66, 0), (1, 0, 1), (2, 0, 0), (0, 0, 0)],
}


@functools.lru_cache(maxsize=1)
def _quarter():
    raw = EXE.read_bytes()
    load = struct.unpack_from('<I', raw, 0x18)[0]
    at = 0x8009589C - load + 0x800                       # g_SineQuarterTable (sym.main.txt)
    return struct.unpack_from('<1025h', raw, at)


def rsin(a):
    """libgte rsin (geo_00.c)."""
    q = _quarter()
    def s1(x):
        if x < 0x801: return q[x] if x < 0x401 else q[0x800 - x]
        return -q[x - 0x800] if x < 0xC01 else -q[0x1000 - x]
    return -s1((-a) & 0xFFF) if a < 0 else s1(a & 0xFFF)


def rcos(a):
    """libgte rcos (geo_01.c)."""
    q = _quarter()
    a = -a if a < 0 else a
    a &= 0xFFF
    if a < 0x801:
        return q[0x400 - a] if a < 0x401 else -q[a - 0x400]
    return -q[0xC00 - a] if a < 0xC01 else q[a - 0xC00]


def cdiv(a, b):
    """C integer division (truncates toward zero)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


class TaskEffect:
    """FieldFx_UpdateTasks for one owner. controllers: callable(var0) -> controller with
    init() and step(age) -> 0/1/2 plus particles_active() for return-2 handling."""

    def __init__(self, triples, make_controller):
        self.script, self.make = triples, make_controller
        self.pc, self.delay, self.count, self.vars = 0, 0, 0, [0] * 7
        self.slots, self.held, self.released, self.update = [], False, None, 0
        self.contacts = []

    def step(self):
        self.update += 1
        running = True
        while running:
            if self.delay:
                self.delay -= 1
                if self.delay: break
            op, a, b = self.script[self.pc]; self.pc += 1
            if op == 0:
                self.pc -= 1
                if self.count == 0 and self.held:
                    self.released = self.update; self.held = False
                running = False
            elif op == 1: self.vars[a] = b
            elif op == 2:
                c = self.make(self.vars[0]); c.init(); self.slots.append([c, 0]); self.count += 1
            elif op == 4:
                if b == 1: raise ValueError('variable wait not used by these effects')
                self.delay = a; running = False
            elif op == 5:
                if a == 0: self.held = True
            else:
                raise ValueError('opcode %d unused by these effects' % op)
        for slot in list(self.slots):
            c, age = slot
            result = c.step(age, self)
            active = c.update_particles()                     # count active at the pass start
            if result == 2 and active == 0: result = 1
            slot[1] += 1
            if result == 1:
                self.slots.remove(slot); self.count -= 1

    def run(self, limit=2000):
        while self.released is None:
            if self.update >= limit: raise ValueError('effect did not release')
            self.step()
        return dict(contacts=list(self.contacts), release=self.released)


class _NoParticles:
    def update_particles(self): return 0


class LineBurst(_NoParticles):
    """line_burst.c; Aya at horizontal distance `distance` from the target point."""

    def __init__(self, duration, countdown, distance, radius, in_floor=True):
        self.duration, self.countdown_reset = duration, countdown
        self.distance, self.radius, self.in_floor = distance, radius, in_floor

    def init(self):
        self.state = self.timer = self.countdown = 0

    def step(self, age, fx):
        if self.state == 0:
            self.timer += 1
            if self.timer < 6: return 0
            self.state, self.timer = 1, 0
            return 0 if self.in_floor else 1
        if self.state == 1:
            self.timer += 1
            if self.timer < 6: return 0
            self.state, self.timer = 2, 0
            return 0
        if self.state == 2:
            self.timer += 1
            if self.countdown: self.countdown -= 1
            if self.distance < 0x104 + self.radius and self.countdown == 0:
                fx.contacts.append(fx.update)
                self.countdown = self.countdown_reset
            if self.timer < self.duration: return 0
            self.state, self.timer = 3, 0
            return 0
        self.timer += 1
        return 1 if self.timer >= 0x20 else 0


class OrbitFlare(_NoParticles):
    """orbit_flare.c; origin (0, 0), Aya at (distance, 0); the middle flare heads at Aya,
    the others at -/+ spawn angle. Leaves the walkable area beyond `floor_exit` from origin."""

    def __init__(self, phase, radius, angle, distance, aya_radius, floor_exit):
        self.phase, self.speed, self.spread = phase, radius, angle
        self.distance, self.aya_radius, self.floor_exit = distance, aya_radius, floor_exit

    def init(self):
        self.x = self.z = 0
        self.state = self.frame = 0
        self.angle = {0: -self.spread, 1: 0, 2: self.spread}[self.phase]

    def step(self, age, fx):
        self.frame += 1
        if self.state == 0:
            if self.frame < 52: return 0
            self.state, self.frame = 1, 0
            return 0
        if self.state == 1:
            self.x += cdiv(rcos(self.angle) * self.speed, 4096)
            self.z += cdiv(rsin(self.angle) * self.speed, 4096)
            if self.x * self.x + self.z * self.z > self.floor_exit * self.floor_exit:
                self.state, self.frame = 2, 0
            r = 0x39 + self.aya_radius
            if (self.distance - self.x) ** 2 + self.z ** 2 < r * r:
                fx.contacts.append(fx.update)
                self.state, self.frame = 2, 0
            return 0
        return 1 if self.frame >= 16 else 0


class DroppedFlare:
    """dropped_flare.c: emitter aimed at Aya (phase 1: pitch 0x180), one falling flare and one
    rising spark at age 1; returns 2 from age 2 until its 24-entry particle list is empty."""

    def __init__(self, speed, lift, distance, height, aya_radius):
        self.speed, self.lift, self.distance, self.height, self.aya_radius = speed, lift, distance, height, aya_radius

    def init(self):
        self.pool = [None] * 0x18
        # FieldFx_AnglesToVector((0x180, yaw toward Aya, 0), speed) -> RotMatrixYXZ * (0, 0, speed);
        # world X points at Aya so yaw is 0x400 (rotation y = 90 deg maps +Z to +X).
        sx, cx = rsin(0x180), rcos(0x180)
        sy, cy = rsin(0x400), rcos(0x400)
        m02 = (sy * cx) >> 12; m12 = -sx; m22 = (cy * cx) >> 12
        self.vel = ((m02 * self.speed) >> 12, (m12 * self.speed) >> 12, (m22 * self.speed) >> 12)

    def _acquire(self):
        for i, e in enumerate(self.pool):
            if e is None:
                return i
        return None

    def step(self, age, fx):
        if age == 1:
            for state in (0, 3):
                i = self._acquire()
                if i is not None:
                    self.pool[i] = dict(state=state, x=0, y=-self.height, z=0,
                                        v=list(self.vel), timer=0, swing=0, age=0)
        return 2 if age >= 2 else 0

    def update_particles(self):
        """FieldFx_UpdateCallbackList over RoomEffect_DroppedFlareParticle (floor at y = 0)."""
        active = 0
        radius = cdiv(self.lift * 50, 4096) + self.aya_radius
        for i in range(len(self.pool)):
            p = self.pool[i]                                  # entries spawned at a later index run this pass
            if p is None: continue
            active += 1
            done = False
            st = p['state']
            if st == 0:
                p['x'] += p['v'][0]; p['y'] += p['v'][1]; p['z'] += p['v'][2]; p['v'][1] += 2
                if (self.distance - p['x']) ** 2 + p['z'] ** 2 < radius * radius:
                    self.contact_hits.append(self.fx_update)  # flash only while the task is held
                    p['state'], p['timer'] = 1, 0
                if p['age'] & 1:                              # source: whatever the state now is
                    j = self._acquire()
                    if j is not None:
                        self.pool[j] = dict(state=4, x=p['x'], y=p['y'], z=p['z'], v=[0, 0, 0], timer=0, swing=0, age=0)
                if p['y'] >= 0:                               # reaching the floor wins, even after a contact
                    p['state'], p['timer'] = 2, 0
            elif st == 1:
                p['timer'] += 1
                done = p['timer'] >= 8
            elif st == 2:
                p['timer'] += 1
                done = p['timer'] >= 16
            elif st in (3, 4):
                p['timer'] += 1
                done = p['timer'] >= 24
            if done: self.pool[i] = None
            else: p['age'] += 1
        return active


def dropped_flare(speed, distance, height, aya_radius, lift=4096):
    c = DroppedFlare(speed, lift, distance, height, aya_radius)
    c.contact_hits = []
    fx = TaskEffect(TASKS[122], lambda var0: c)
    while fx.released is None:
        c.fx_update = fx.update + 1
        fx.step()
        if fx.update > 2000: raise ValueError('no release')
    return dict(contacts=c.contact_hits, release=fx.released)


def line_burst(distance, aya_radius, duration=300, countdown=300, in_floor=True):
    return TaskEffect(TASKS[136], lambda var0: LineBurst(duration, countdown, distance, aya_radius, in_floor)).run()


def orbit_flare(distance, aya_radius, floor_exit, radius=32, angle=256):
    return TaskEffect(TASKS[115], lambda var0: OrbitFlare(var0, radius, angle, distance, aya_radius, floor_exit)).run()


def as_action_timing(result):
    """Effect updates -> action windup / recovery: the effect starts with the command; a contact
    on effect update u is delivered by the next battle pass (windup u); the owner sees the
    release one pass after the effect's (total = release). First contact only; None = miss."""
    total = result['release']
    if not result['contacts']:
        return dict(windup=total, recovery=0, contact=False, contacts=0)
    u = result['contacts'][0]
    return dict(windup=u, recovery=max(1, total - u), contact=True, contacts=len(result['contacts']))
