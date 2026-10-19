"""Room effect modules (room_lib class + field-engine object) as exact timelines, offline.

A room module effect (e.g. room 146's effect 40) is a room_lib class: RoomLib_PlantScript plants
g_RoomScript (FieldFx_GetSlot), RoomLib_Spawn6 sets script vars from the enemy script's
Pm_ScriptSendCommand0 (vars[index] = value), and RoomLib_RegisterPairedTables runs each update:
FieldFx_UpdateSlots(update list) | FieldFx_RunScript(init list, spawn sizes); a -1 result calls
RoomLib_CloseTarget, which sets the owner's action state to 4 (the action completes).

Ported (src/main/fieldfx/object_script.c): the command interpreter (start slot, wait, register
set/add/sub/load/store, conditional and plain jumps, -1 halt, -3 free all), the 0x40-slot
dispatch (first free slot; flag 2 frees after the slot's own handler; counter += 1 after each
dispatched handler), FieldFx_FreeSlot's -1 when the script is halted and no slot is left,
FieldFx_IsLastSlotHalted, and the owner action state 1 -> 2 at the start of each slot pass
(FieldFx_RegisterOwnerContact needs 2). Not ported: the owner-disabled check at the end of
FieldFx_UpdateSlots (interruption by the owner's own state), drawing.

Module handlers ported: room_lib/falling_sprite_burst.c (ten hospital / Chrysler rooms).
Contact: FieldFx_IsPlayerWithinRadius (X/Z, Aya's hit_cylinder radius + extra), registered by
the re-arm tick (room_rearm_timer.h) as at most one contact per `reload` updates.
"""
import random, re, struct
from functools import lru_cache

from .enemy_reach import animation, bones_at, decode_frame, model, room_blob
from .room_handlers import overlay


def s16(v): v &= 0xFFFF; return v - 0x10000 if v & 0x8000 else v
def s8(v): v &= 0xFF; return v - 0x100 if v & 0x80 else v


class ModuleObject:
    """FieldFxObject: script state + 0x40 dispatch slots (slot data held as Python dicts)."""

    def __init__(self, commands, init, update, rng):
        self.commands = commands; self.init = init; self.update = update; self.rng = rng
        self.wait = self.pc = 0; self.slot_count = 0; self.halted = 0
        self.regs = [0] * 16; self.vars = [0] * 9; self.context = None
        self.slots = [dict(flag=0, id=0, counter=0, data=None) for _ in range(0x40)]
        self.action_state = 1; self.contacts = []; self.age = 0; self.closed = None

    # FieldFx_StartSlot / ActivateSlot
    def start_slot(self, ident):
        for i, s in enumerate(self.slots):
            if s['flag'] == 0:
                s.update(flag=1, id=ident, counter=0, data={})
                self.slot_count += 1
                self.init[ident](self, s, s['data'])
                return s['data']
        self.regs[14] = 1
        return None

    def free_slot(self, s):
        s['flag'] = 0; self.slot_count -= 1
        return -1 if (self.halted == 1 and self.slot_count == 0) else 0

    def last_slot_halted(self): return self.halted == 1 and self.slot_count == 1

    def update_slots(self):
        result = 0
        if self.action_state == 1: self.action_state = 2
        for s in self.slots:
            if s['flag'] == 1:
                self.update[s['id']](self, s, s['data'])
                s['counter'] = (s['counter'] + 1) & 0xFFFF
            if s['flag'] == 2: result |= self.free_slot(s)
        return result

    def run_script(self):
        result = 0; stopped = False
        if self.wait:
            self.wait -= 1; return 0
        while not stopped:
            command = self.commands[self.pc]
            cmd = command - (1 << 32) if command >= 1 << 31 else command
            if cmd == -3:
                for s in self.slots:
                    if s['flag']:
                        s['flag'] = 0; self.slot_count -= 1
                        if self.halted == 1 and self.slot_count == 0: result = -1
            if cmd == -2: command = cmd = 0
            if cmd != -1:
                high = (command >> 16) & 0xFFFF; op = high; operand = s16(command)
                if op == 1: self.start_slot(operand & 0xFF)
                if op == 2: stopped = True; self.wait = operand
                if 0x10 <= high < 0x20: self.regs[op - 0x10] = operand
                if 0x20 <= high < 0x30: self.regs[op - 0x20] += operand
                if 0x30 <= high < 0x40: self.regs[op - 0x30] -= operand
                if 0x40 <= high < 0x50: self.regs[op - 0x40] = self.vars[operand & 0xFFFF]
                if 0x50 <= high < 0x60: self.vars[operand & 0xFFFF] = self.regs[op - 0x50]
                if 0x1000 <= high < 0x2000 and s16(self.regs[(high & 0xF00) >> 8]) == operand: self.pc += s8(op)
                if 0x2000 <= op < 0x3000 and self.regs[(op & 0xF00) >> 8] != operand: self.pc += s8(op)
                if 0x3000 <= op < 0x4000: self.pc += s8(op)
            else:
                self.halted = 1; stopped = True
            if self.halted == 0: self.pc += 1
            elif self.slot_count == 0: result = -1
        return result

    def tick(self):
        """One RoomLib_RegisterPairedTables call; returns True once closed."""
        result = self.update_slots() | self.run_script()
        self.age += 1
        if result == -1 and self.closed is None: self.closed = self.age
        return self.closed is not None

    def register_contact(self):
        if self.action_state == 2: self.contacts.append(self.age)


# ---- room_lib/falling_sprite_burst.c ------------------------------------------------------

def falling_burst_handlers(scene):
    """init / update tables for the falling sprite burst (handler ids 0-4). scene: dict(
    joint5 = callable(age) -> (rotation, translation) of render matrix 5 in the enemy frame
    scaled to world units, aya = (x, z) in the enemy frame, aya_radius)."""
    def player_within(pos, extra):
        dx = scene['aya'][0] - int(pos[0]); dz = scene['aya'][1] - int(pos[2])
        r = scene['aya_radius'] + extra
        return dx * dx + dz * dz < r * r

    def init_clock(obj, slot, st):
        obj.context = st
        st.update(cooldown=0, hit=0, step=obj.vars[1], tick=obj.vars[2], reload=obj.vars[3])

    def tick_clock(obj, slot, st):                       # ROOM_REARM_TIMER_TICK
        if st['cooldown']: st['cooldown'] -= 1
        if st['hit'] == 1:
            timer = st['cooldown']; st['hit'] = 0
            if timer == 0:
                st['cooldown'] = st['reload']; obj.register_contact()
        if obj.last_slot_halted(): slot['flag'] = 2

    def init_sprite(obj, slot, st):
        R, t = scene['joint5'](obj.age)
        p = [sum(R[i][k] * (0, 20, -40)[k] for k in range(3)) for i in range(3)]
        st.update(x=int(p[0] + t[0]), y=int(p[1] + t[1]), z=int(p[2] + t[2]), scale=0x100, step=0, active=0)
        if obj.regs[1] == 0:
            st['vx'] = obj.rng.randrange(10) - 5; st['vz'] = obj.rng.randrange(10) - 5
        else:
            v = [sum(R[i][k] * (0, 0, -6)[k] for k in range(3)) for i in range(3)]
            st['vx'] = int(v[0]) * 2; st['vz'] = int(v[2]) * 2

    def update_sprite(obj, slot, st):
        if not s16(st['y']) < 0:                           # g_RoomFloorY->y = 0 in the enemy frame
            if s16(st['scale']) >= 0x15: st['scale'] -= 0x14
            else: slot['flag'] = 2
            if st['active'] == 0:
                st['active'] = 1
                for ident in (3, 2):
                    d = obj.start_slot(ident)
                    if d is not None: d.update(x=st['x'], y=0, z=st['z'])
                d = obj.start_slot(4)
        else:
            st['x'] += st['vx']; st['z'] += st['vz']
            st['y'] += st['step'] >> 8; st['scale'] += 0x28; st['step'] += 0x64

    def init_shimmer(obj, slot, st): st.update(scale=0x258, phase=0)

    def update_shimmer(obj, slot, st):
        clock = obj.context; st['scale'] += 3
        if clock['tick'] - 0x1E < slot['counter']:
            st['phase'] = (st['phase'] + 8) & 0xFF
            if st['phase'] >> 4 == 8: slot['flag'] = 2

    def init_pulse(obj, slot, st): st.update(scale=0xC8, depth=0x80)

    def update_pulse(obj, slot, st):
        clock = obj.context
        if clock['tick'] - 0x3C < slot['counter']:
            if st['depth'] >= 5: st['depth'] -= 4
            if clock['tick'] - 0x1E < slot['counter'] and st['scale'] > clock['step'] * 6:
                st['scale'] -= clock['step'] * 6
        else:
            st['scale'] += clock['step']
        if player_within((st.get('x', 0), 0, st.get('z', 0)), s16(st['scale']) >> 3): clock['hit'] = 1
        if slot['counter'] == clock['tick']: slot['flag'] = 2

    def init_particles(obj, slot, st):
        st['p'] = [dict(y=0, vy=-(obj.rng.randrange(100) + 50), live=True) for _ in range(6)]; st['live'] = 6

    def update_particles(obj, slot, st):
        for q in st['p']:
            if q['live']:
                q['y'] += q['vy'] >> 4; q['vy'] += 4
                if q['y'] >= 0:
                    q['live'] = False; st['live'] -= 1
                    if st['live'] == 0: slot['flag'] = 2

    init = {0: init_clock, 1: init_sprite, 2: init_pulse, 3: init_shimmer, 4: init_particles}
    update = {0: tick_clock, 1: update_sprite, 2: update_pulse, 3: update_shimmer, 4: update_particles}
    return init, update


# ---- room_lib/three_particles.c ----------------------------------------------------------

def three_particle_handlers(scene):
    """Debris triplet: three particles fan out at -var3 / 0 / +var3 around render matrix 0's
    forward; position += velocity x speed >> 4 (velocity 4096-unit vectors, 16.16 position), speed
    += var1 (floored at 0); while swing < var5: swing += rand(20..99), rise 10 units; contact
    radius swing >> 4 + Aya's radius (X/Z); a contact before landing flags the clock (re-arm
    reload var6); life var2 (20 after a contact or leaving the floor polygon when var4 == 0).
    The floor polygon is open here (labelled). The seed is (0, 0, +4096) while the engine's forward
    vector (D_800C2258) is (0, 0, -16384), so the debris leaves behind the actor unless the view
    matrix carries an extra half turn (unverified; scene['flip_debris'] is the upper bound)."""
    from .room_effects import rcos, rsin

    def init_clock(obj, slot, st):
        obj.context = st; st.update(cooldown=0, landed=0, reload=obj.vars[6])

    def tick_clock(obj, slot, st):
        if st['cooldown']: st['cooldown'] -= 1
        if st['landed'] == 1:
            timer = st['cooldown']; st['landed'] = 0
            if timer == 0: st['cooldown'] = st['reload']; obj.register_contact()
        if obj.last_slot_halted(): slot['flag'] = 2

    def init_triplet(obj, slot, st):
        R, t = scene['joint0'](obj.age); a = obj.vars[3]
        parts = []
        for yaw in (-a, 0, a):
            c, s_ = rcos(yaw & 0xFFF) / 4096, rsin(yaw & 0xFFF) / 4096
            local = (4096 * s_, 0, 4096 * c * (-1 if scene.get('flip_debris') else 1))   # Ry(yaw) (0, 0, 4096); +Z = behind (engine forward is -Z)
            v = [sum(R[i][k] * local[k] for k in range(3)) for i in range(3)]
            parts.append(dict(x=int(t[0]) << 16, y=int(t[1]) << 16, z=int(t[2]) << 16, vx=int(v[0]), vy=int(v[1]),
                              vz=int(v[2]), swing=0, life=obj.vars[2], mode=1, landed=0, alive=True))
        st.update(parts=parts, remaining=3, speed=obj.vars[0], accel=obj.vars[1], limit=obj.vars[5], keep=obj.vars[4])

    def update_triplet(obj, slot, st):
        clock = obj.context
        for q in st['parts']:
            if not q['alive']: continue
            if q['mode'] == 1:
                q['x'] += (q['vx'] * st['speed']) >> 4; q['y'] += (q['vy'] * st['speed']) >> 4; q['z'] += (q['vz'] * st['speed']) >> 4
            if q['swing'] < st['limit']:
                q['swing'] += obj.rng.randrange(80) + 20; q['y'] -= 0xA0000
            q['life'] -= 1
            if q['life'] == 0: q['alive'] = False; st['remaining'] -= 1
            px, pz = q['x'] >> 16, q['z'] >> 16
            r = scene['aya_radius'] + (q['swing'] >> 4)
            if (scene['aya'][0] - px) ** 2 + (scene['aya'][1] - pz) ** 2 < r * r:
                if q['landed'] == 0: clock['landed'] = 1; q['life'] = 0x14; q['mode'] = 0
                q['landed'] = 1
        st['speed'] = max(0, st['speed'] + st['accel'])
        if st['remaining'] == 0: slot['flag'] = 2

    return {0: init_clock, 1: init_triplet}, {0: tick_clock, 1: update_triplet}


# ---- room_lib/twelve_elements.c -----------------------------------------------------------

def twelve_element_handlers(scene):
    """Twelve elements start at local z = i x var3 and move z -= var0 each update; below z 10 an
    element turns active and grows phase from 100 by var5 up to var6. An active element collides
    when Aya is inside its floor quad: g_FieldFxCellQuad +-1024 (cell 0x40) scaled by phase/4096
    and the shadow scale (1, 2, 1), i.e. half extents phase/4 across and phase/2 along the
    facing, centred on the actor (active elements sit at its origin). The draw pass flags the
    clock; the re-arm tick registers it (reload 0x28). Each element's timer counts to var1; when
    all twelve have, the counters end (repeatCount 12)."""

    def init_clock(obj, slot, st):
        obj.context = st; st.update(cooldown=0, hit=0, reload=0x28)

    def tick_clock(obj, slot, st):
        if st['cooldown']: st['cooldown'] -= 1
        if st['hit'] == 1:
            timer = st['cooldown']; st['hit'] = 0
            if timer == 0: st['cooldown'] = st['reload']; obj.register_contact()
        if obj.last_slot_halted(): slot['flag'] = 2

    def init_elements(obj, slot, st):
        st.update(z=[i * obj.vars[3] for i in range(12)], state=[0] * 12, phase=[0x64] * 12, timer=[0] * 12,
                  repeat=12, step=obj.vars[0], limit=obj.vars[1], pstep=obj.vars[5], plimit=obj.vars[6])

    def tick_elements(obj, slot, st):
        for i in range(12):
            if st['state'][i] == -1: continue
            if st['state'][i] == 1: st['phase'][i] = min(st['plimit'], st['phase'][i] + st['pstep'])
            st['z'][i] -= st['step']
            if st['z'][i] < 10: st['state'][i] = 1
            st['timer'][i] += 1
            if st['timer'][i] == st['limit']:
                st['repeat'] -= 1
                if st['repeat'] == 0: slot['flag'] = 2
        # Draw pass (same frame): any active element's quad containing Aya flags the clock.
        ax, az = scene['aya']
        for i in range(12):
            if st['state'][i] == 1 and abs(ax) < st['phase'][i] / 4 and abs(az) < st['phase'][i] / 2:
                obj.context['hit'] = 1

    return {0: init_clock, 1: init_elements}, {0: tick_clock, 1: tick_elements}


# ---- room_lib/paired_glow.c (handlers mapped by name from the room's own lists) -----------

def _paired_glow_funcs(scene):
    def nop(obj, slot, st): pass

    def init_clock(obj, slot, st):
        obj.context = st; st.update(cooldown=0, hit=0, reload=0x1E)

    def tick_clock(obj, slot, st):                       # RoomLib_TickPairedGlowTimer (re-arm)
        if st['cooldown']: st['cooldown'] -= 1
        if st['hit'] == 1:
            timer = st['cooldown']; st['hit'] = 0
            if timer == 0: st['cooldown'] = st['reload']; obj.register_contact()
        if obj.last_slot_halted(): slot['flag'] = 2

    def tick_emitter(obj, slot, st):                      # ROOMLIB_PARTICLE_TICK_A: unconditional hit at frame 16
        if slot['counter'] == 0x10: obj.context['hit'] = 1
        if slot['counter'] == 0x20: slot['flag'] = 2

    def reset_sprite(obj, slot, st): st.update(scale=0x100, depth=1)

    def update_sprite(obj, slot, st):
        st['scale'] += 0xF
        st['depth'] += 8 if slot['counter'] < 0x10 else -4
        if st['depth'] <= 0: slot['flag'] = 2

    return {'RoomLib_InitPairedGlowSprite': init_clock, 'RoomLib_InitPairedEmitterWithSound': nop,
            'RoomLib_InitPairedEmitter': nop, 'RoomLib_ResetPairedGlowScale': reset_sprite, 'RoomLib_PairedGlowNopB': nop,
            'RoomLib_TickPairedGlowTimer': tick_clock, 'RoomLib_TickPairedGlowA': tick_emitter,
            'RoomLib_TickPairedGlowB': tick_emitter, 'RoomLib_UpdatePairedGlowSprite': update_sprite, 'RoomLib_PairedGlowNopD': nop}


def _motion_particle_funcs(scene):
    """room_lib/motion_particles*.c (rooms 75 / 80 / 82, 0x0C slot 3): the ground-eruption strips.
    RoomEffect_InitParticleRenderPair builds two chains (FieldFx_BuildParticleChain) of 10 links on
    the floor under matrices 9 and 13, with the actor's rotation: edges +-400 across, each link 300
    further along -Z; links 2..5 turn +-(64 + rand(512)) toward Aya's side (cross product sign),
    links 6+ go straight. RoomEffect_UpdateParticleRenderPair (FieldFx_UpdateStripCollision) lights
    link `step` each update (step += 1, done at 0x64); a lit link fades by 12 brightness per update
    from 32 and hits when Aya stands inside its quad (X/Z) -> owner hit flag; the re-arm tick
    (ROOM_REARM_TIMER_TICK, reload 30) turns that into a contact. Links 0/1 start with tilt 0."""
    import math
    def nop(obj, slot, st): pass

    def init_clock(obj, slot, st):
        obj.context = st; st.update(cooldown=0, hit=0, reload=30)

    def tick_clock(obj, slot, st):
        if st['cooldown']: st['cooldown'] -= 1
        if st['hit'] == 1:
            timer = st['cooldown']; st['hit'] = 0
            if timer == 0: st['cooldown'] = st['reload']; obj.register_contact()
        if obj.last_slot_halted(): slot['flag'] = 2

    def ends_at(n):
        def upd(obj, slot, st):
            if slot['counter'] >= n: slot['flag'] = 2
        return upd

    def chain(joint, age):
        jt = scene['joints'](joint) if scene.get('joints') else None
        R0 = scene['joints'](0)(age)[0] if scene.get('joints') else [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        x, z = (jt(age)[1][0], jt(age)[1][2]) if jt else (0, -200)
        yaw = math.atan2(-R0[0][2], -R0[2][2])               # actor facing (forward = R x (0,0,-1))
        aya = scene['aya']; pts = []; turn = 0.0
        for i in range(11):
            fx, fz = math.sin(yaw), math.cos(yaw)                # forward unit (x, z); facing -Z gives yaw = pi
            sx, sz = -fz, fx                                     # local +X across the strip
            pts.append(((x + sx * 400, z + sz * 400), (x - sx * 400, z - sz * 400)))
            if 2 <= i < 6:
                px, pz = aya[0] - x, aya[1] - z
                cross = fx * pz - fz * px
                ang = (64 + obj_rng[0].randrange(512)) * math.pi / 2048
                yaw += ang if cross < 0 else -ang                 # turn toward Aya's side
            x += fx * 300; z += fz * 300
        return pts

    obj_rng = [None]

    def init_pair(obj, slot, st):
        obj_rng[0] = obj.rng
        st.update(step=0, chains=[chain(9, obj.age), chain(13, obj.age)], lit=[{}, {}])

    def inside(q, p):
        (a, b), (c, d) = q
        poly = [a, b, d, c]; sign = None
        for i in range(4):
            x1, z1 = poly[i]; x2, z2 = poly[(i + 1) % 4]
            cr = (x2 - x1) * (p[1] - z1) - (z2 - z1) * (p[0] - x1)
            if cr != 0:
                if sign is None: sign = cr > 0
                elif (cr > 0) != sign: return False
        return True

    def update_pair(obj, slot, st):
        hit = False
        for k, pts in enumerate(st['chains']):
            lit = st['lit'][k]
            if st['step'] < 10: lit[st['step']] = 32
            for i in list(lit):
                if i < 10 and inside((pts[i], pts[i + 1]), scene['aya']): hit = True
                lit[i] -= 12
                if lit[i] < 1: del lit[i]
        if hit and obj.context is not None: obj.context['hit'] = 1
        st['step'] += 1
        if st['step'] > 0x64: slot['flag'] = 2

    return {'RoomEffect_MotionParticlesInit': init_clock, 'RoomEffect_MotionParticlesAnchor': nop,
            'RoomEffect_InitSpritePair': nop, 'RoomEffect_SeedMotionParticles': nop,
            'RoomEffect_InitParticleRenderPair': init_pair,
            'RoomEffect_MotionParticlesTick': tick_clock, 'RoomEffect_UpdateTimedFade': ends_at(0x3A),
            'RoomEffect_StepSpriteQuad': ends_at(0x3A), 'RoomEffect_StepSpritePair': ends_at(0x10),
            'RoomEffect_UpdateParticleMotion': ends_at(65), 'RoomEffect_UpdateParticleRenderPair': update_pair}


def named_handlers(funcs_factory):
    """Build init / update tables from the room's own list order (names without the room suffix)."""
    def build(scene):
        funcs = funcs_factory(scene); lists = scene['lists']
        strip = lambda n: (n or '').split('__room_')[0]
        init = {i: funcs[strip(n)] for i, n in enumerate(lists['init']) if strip(n) in funcs}
        update = {i: funcs[strip(n)] for i, n in enumerate(lists['update']) if strip(n) in funcs}
        return init, update
    return build


MODULES = {'RoomEffect_FallingBurstInit': falling_burst_handlers, 'RoomLib_InitThreeParticlePackets': three_particle_handlers,
           'RoomLib_InitPairedGlowSprite': named_handlers(_paired_glow_funcs),
           'RoomLib_InitTwelveEffectPackets': twelve_element_handlers,
           'RoomEffect_MotionParticlesInit': named_handlers(_motion_particle_funcs)}


@lru_cache(maxsize=None)
def module_spec(map_id, command):
    """dict(kind, script words) for a room-module effect command, or None."""
    from .room_handlers import handler
    h = handler(map_id, command)
    if not h or not h.get('fields'): return None
    names = [n or '' for _, n in h['fields']]
    if 'PlantScript' not in names[1]: return None
    ov = overlay(map_id); blob = room_blob(map_id)
    infix = re.match(r'RoomLib_(\w*?)PlantScript', names[1]).group(1) if names[1].startswith('RoomLib_') else ''
    if infix:
        script = next((a for a, n in ov['names'].items() if n == 'g_Room%sScript' % infix), None)
        init = next((a for a, n in ov['names'].items() if n == 'g_Room%sInitList' % infix), None)
    else:
        script = next((a for a, n in ov['names'].items() if n.startswith('g_RoomScript__') or n == 'g_RoomScript'), None)
        init = next((a for a, n in ov['names'].items() if n.startswith('g_RoomInitList')), None)
    if script is None or init is None: return None
    first = struct.unpack_from('<I', blob, init - ov['vram'])[0]
    kind = ov['names'].get(first)
    words = []; at = script - ov['vram']
    while True:
        w = struct.unpack_from('<I', blob, at)[0]; words.append(w); at += 4
        if w == 0xFFFFFFFF or len(words) > 256: break
    def names_at(prefix_infix):
        a = next((x for x, n in ov['names'].items() if n == prefix_infix or n.startswith(prefix_infix + '__')), None)
        out = []
        if a is None: return out
        at2 = a - ov['vram']
        while len(out) < 32:
            w = struct.unpack_from('<I', blob, at2)[0]; at2 += 4
            if w == 0xFFFFFFFF: break
            out.append(ov['names'].get(w))
        return out
    lists = dict(init=names_at('g_Room%sInitList' % infix), update=names_at('g_Room%sUpdateList' % infix))
    kind = (kind or '').split('__room_')[0]
    return dict(kind=kind, script=words, lists=lists) if kind in MODULES else dict(kind=kind, script=words, lists=lists, unsupported=True)


@lru_cache(maxsize=256)
def joint_track(map_id, actor_type, enter_mode, exit_mode, enter_step, exit_step, scale, joint=5):
    """age -> (R, t) of render matrix `joint`, scaled to world units: enter clip, exit clip,
    then held at the exit clip's last frame (the base-mode pose is not modelled)."""
    blob = room_blob(map_id); mdl = model(blob, actor_type)
    clips = []
    for mode, step in ((enter_mode, enter_step), (exit_mode, exit_step)):
        p = animation(blob, actor_type, mode)
        if p is None: continue
        n = blob[p + 2]
        for f in range(n):
            t, a = decode_frame(blob, p, f)
            R, tr = bones_at(mdl, t, a)[joint]
            k = scale / 4096
            frame = ([[v * k for v in row] for row in R], [v * k for v in tr])
            for _ in range(max(1, round(65536 / step))): clips.append(frame)
    if not clips: raise ValueError('no clips for joint track')
    return lambda age: clips[min(age, len(clips) - 1)]


def resolve_vars(vars_, rng):
    """Script vars for one run: literal values, Script_Random draws ([lo, hi)), and a uniform
    pick between branch alternatives (labelled: the branch condition is not evaluated)."""
    out = {}
    for i, v in vars_.items():
        if isinstance(v, int): out[i] = v; continue
        c = v[rng.randrange(len(v))] if len(v) > 1 else v[0]
        out[i] = c[1] if c[0] == 'lit' else c[1] + rng.randrange(max(1, c[2] - c[1]))
    return out


def timeline(map_id, command, vars_, joint5, distance, aya_radius, rng=None, regs1=0, limit=4000, joints=None, flip_debris=False):
    """Run a room-module effect: dict(contacts=[ages], release=age). Aya stands at `distance`
    in front of the enemy (enemy frame: -z), the enemy facing her."""
    spec = module_spec(map_id, command)
    if not spec or spec.get('unsupported'): raise ValueError('unsupported room module')
    rng = rng or random.Random(0)
    scene = dict(joint5=joint5, aya=(0, -distance), aya_radius=aya_radius, flip_debris=flip_debris, lists=spec.get('lists', {}))
    if joints: scene['joint0'] = joints(0); scene['joints'] = joints
    init, update = MODULES[spec['kind']](scene)
    obj = ModuleObject(spec['script'], init, update, rng)
    for i, v in resolve_vars(vars_, rng).items(): obj.vars[i] = v
    obj.regs[1] = regs1
    while not obj.tick():
        if obj.age > limit: raise ValueError('module did not close')
    return dict(contacts=obj.contacts, release=obj.closed)


@lru_cache(maxsize=1024)
def slot_record(map_id, actor_type, slot):
    """(enter_mode, exit_mode, enter_step, exit_step) from the actor script's declaration of
    `slot` (Script_SetEntityAnim5/12Args) and Script_SetBattleEntryCoords, else None."""
    import json
    from .decode_enemy_actions import literal
    from .power_gaps import _scripts, ROOT
    s = _scripts().get((int(map_id), actor_type))
    if not s: return None
    decl = [[literal(a) for a in n['args']] for n in s['nodes']
            if n['handler'] in ('Script_SetEntityAnim5Args', 'Script_SetEntityAnim12Args') and literal(n['args'][0]) == slot]
    if len(decl) != 1 or None in decl[0][2:4]: return None
    steps = {tuple(literal(a) for a in n['args'][1:]) for n in s['nodes']
             if n['handler'] == 'Script_SetBattleEntryCoords' and literal(n['args'][0]) == slot}
    if len(steps) > 1: return None
    defaults = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))['initial_records'][slot]
    enter, exit_ = next(iter(steps)) if steps else (defaults['enter_step'], defaults['exit_step'])
    return decl[0][2], decl[0][3], enter, exit_


@lru_cache(maxsize=1)
def actions():
    """[(map, actor_type, dict(slot, command, vars, kind))]: slot >= 3 calls whose preceding 30
    instructions load a supported room-module effect (Script_GetEntityEffect #id) and send it
    literal variables (Pm_ScriptSendCommand0 L, #index, #value)."""
    from .decode_enemy_actions import literal
    from .power_gaps import _scripts
    out = []
    for (m, a), s in _scripts().items():
        nodes = sorted(s['nodes'], key=lambda n: n['offset'])
        for k, n in enumerate(nodes):
            if n['handler'] != 'Script_RunEntityCommand' or literal(n['args'][0]) is None or literal(n['args'][0]) < 3: continue
            command = None; vars_ = {}; ok = True; randoms = {}
            for p in nodes[max(0, k - 40):k]:
                v = [literal(x) for x in p['args']]
                if p['handler'] == 'Script_GetEntityEffect' and v[0] is not None:
                    command, vars_, ok = v[0], {}, True
                elif p['handler'] == 'Script_Random' and p['args'][0]['mode'] != 0 and None not in v[1:3]:
                    randoms[(p['args'][0]['mode'], p['args'][0]['value'])] = (s16(v[1]), s16(v[2]))
                elif p['handler'] == 'Pm_ScriptSendCommand0' and command is not None:
                    if v[1] is None: ok = False; continue
                    a2 = p['args'][2]
                    if v[2] is not None: cand = ('lit', s16(v[2]))
                    elif (a2['mode'], a2['value']) in randoms: cand = ('rand',) + randoms[(a2['mode'], a2['value'])]
                    else: ok = False; continue
                    # Several sends of one index in the window are branch alternatives (labelled).
                    vars_.setdefault(v[1], [])
                    if cand not in vars_[v[1]]: vars_[v[1]].append(cand)
            if command is None or not ok: continue
            try: spec = module_spec(m, command)
            except (struct.error, IndexError): spec = None
            if not spec or spec.get('unsupported'): continue
            from .decode_enemy_actions import completion_reset
            out.append((m, a, dict(slot=literal(n['args'][0]), command=command, vars=vars_, kind=spec['kind'],
                                   reset=completion_reset(s, n['offset']))))
    return out


@lru_cache(maxsize=4)
def catalog(cells=()):
    """{(map, identity, slot): action} where every actor resolving to the identity agrees."""
    import json
    from collections import defaultdict
    from .enemy_identity import identity_keys
    keys = identity_keys(dict(cells)); cand = defaultdict(list)
    for m, a, act in actions():
        for ident, _ in keys.get((m, a), []): cand[m, ident, act['slot']].append(dict(act, actor=a))
    out = {}
    for k, rows in cand.items():
        if len({json.dumps({x: r[x] for x in ('command', 'vars', 'kind', 'reset')}, sort_keys=True) for r in rows}) == 1:
            out[k] = rows[0]
    return out


def module_plan(foe, slot, cells, scale=None, geometry_upper=False):
    """A runnable plan for one slot, or None: dict(action, run(distance, aya_radius, rng))."""
    from .enemy_identity import cells_key
    from .enemy_reach import move_speed
    from .power_gaps import _scripts
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return None
    act = catalog(cells_key(cells)).get((m, ident, slot))
    if not act: return None
    rec = slot_record(m, act['actor'], slot)
    if rec is None: return None
    ms = scale or move_speed(_scripts()[m, act['actor']]['nodes']) or 4096
    joint = joint_track(m, act['actor'], rec[0], rec[1], rec[2], rec[3], ms)
    joints = lambda j: joint_track(m, act['actor'], rec[0], rec[1], rec[2], rec[3], ms, joint=j)
    def run(distance, aya_radius, rng):
        return timeline(m, act['command'], act['vars'], joint, distance, aya_radius, rng, joints=joints, flip_debris=geometry_upper)
    return dict(action=act, run=run, move_speed=ms)


# ---- room task programs (commands >= 85) on the FieldFx_UpdateTasks port -------------------

class TimedSpawn:
    """room_lib/timed_spawn.c RoomLib_ControlTimedSpawn: a sprite (24-update life) every sixth
    update while age < 0x20; at age 7 (task event active, owner flags 0x01000000) it sets the
    player's 0x4000 flag and the owner's contact bit with no distance test (a scene flash);
    returns 2 from age 8, so it frees once its sprite list is empty."""

    def __init__(self): self.sprites = []

    def init(self): pass

    def step(self, age, fx):
        if age < 0x20 and age % 6 == 0: self.sprites.append(0)
        if age == 7: fx.contacts.append(fx.update)
        return 2 if age >= 8 else 0

    def update_particles(self):
        active = len(self.sprites)
        self.sprites = [a + 1 for a in self.sprites if a + 1 < 24]
        return active


TASK_CONTROLLERS = {'RoomLib_ControlTimedSpawn': TimedSpawn}


def _burst_orb(spec, distance, aya_radius, rng):
    """Burst orb (room_lib/spark_attacks.c) through Codex's source_projectile.BurstOrb port:
    launch on the task script's controller spawn (+1), speed from the map-156 script distance
    thresholds (orb_speed), hand height 320 (labelled scenario), completion bound
    max(63, impact + 25) as in OrbEnemy (visual tail / pool drain unresolved)."""
    from .source_projectile import BurstOrb, orb_speed, task_spawns
    launches = [e['update'] + 1 for e in task_spawns(spec['script']) if e.get('task') == 0]
    if len(launches) != 1: raise ValueError('ambiguous orb launch')
    orb = None; impact = None; contacts = []
    for age in range(1, 2000):
        if age == launches[0]: orb = BurstOrb(y=-320, vx=orb_speed(distance))
        if orb and orb.alive:
            st = orb.state
            if orb.tick(rng, player_x=int(distance), player_radius=aya_radius): contacts.append(age - 1)
            if st == 0 and orb.state == 1: impact = age
            if st == 0 and orb.state == 5: impact = age
        if impact is not None and age >= max(63, impact + 25): return dict(contacts=contacts, release=age)
    raise ValueError('orb did not complete')


class SoundBurst:
    """room_lib/sound_burst.c: a particle every third update while age < 0x47 from render
    matrix 9 x (0, 0, -60); each particle advances radius += step0 along the owner's facing
    (toward Aya), sideways rsin(phase) * amplitude / 4096 (amplitude += step1, phase += step2),
    lives 0x40 updates and contacts Aya within 100 + her cylinder radius (X/Z). The first
    contact rewrites the owner's 0x3F000000 bits to 0x21, so one hit per effect. The
    controller returns 2 from age 8 and frees when its particle list is empty."""

    def __init__(self, steps, origin, distance, aya_radius):
        self.steps, self.origin, self.distance, self.r = steps, origin, distance, aya_radius
        self.parts = []; self.hit = False

    def init(self): pass

    def step(self, age, fx):
        from .room_effects import rsin
        if age < 0x47 and age % 3 == 0:
            ox, oz = self.origin(age)
            self.parts.append(dict(swing=0, amp=0, phase=0, ox=ox, oz=oz, age=0))
        for q in self.parts:
            q['swing'] += self.steps[0]; q['amp'] += self.steps[1]; q['phase'] += self.steps[2]
            side = rsin(q['phase'] & 0xFFFF if q['phase'] < 0x8000 else q['phase'] - 0x10000) * q['amp'] // 4096
            wx = q['ox'] + side; wz = q['oz'] - q['swing']
            if not self.hit and wx * wx + (wz + self.distance) ** 2 < (100 + self.r) ** 2:
                self.hit = True; fx.contacts.append(fx.update)
        return 2 if age >= 8 else 0

    def update_particles(self):
        active = len(self.parts)
        for q in self.parts: q['age'] += 1
        self.parts = [q for q in self.parts if q['age'] < 0x40]
        return active


def _sound_burst(spec, distance, aya_radius, rng, scene=None):
    from .room_effects import TaskEffect
    sc = scene or {}
    steps = sc.get('steps') or (38, 15, 192)
    origin = sc.get('origin') or (lambda age: (0, -60))
    r = TaskEffect(spec['script'], lambda var0: SoundBurst(steps, origin, distance, aya_radius)).run()
    return dict(contacts=[c - 1 for c in r['contacts']], release=r['release'])


class SparkRing:
    """room_lib/spark_ring_burst.c RoomEffect_SparkRingController: captures Aya's position at
    init; waits 20 updates; then for 32 updates spawns a spark (life 24) and contacts Aya if she
    is within 180 + her radius of the captured point (one hit: owner bits -> 0x21); returns 2
    afterwards and frees when its sparks are gone. Aya is stationary here, so the first state-1
    update hits; dodging needs player movement (not modelled)."""

    def __init__(self, aya_moved=0, aya_radius=100):
        self.state, self.timer, self.parts, self.hit = 0, 0, [], False
        self.moved, self.r = aya_moved, aya_radius

    def init(self): pass

    def step(self, age, fx):
        if self.state == 0:
            self.timer += 1
            if self.timer >= 20: self.state, self.timer = 1, 0
        elif self.state == 1:
            self.timer += 1; self.parts.append(0)
            if not self.hit and self.moved < 180 + self.r: self.hit = True; fx.contacts.append(fx.update)
            if self.timer >= 32: self.state = 2
        else:
            return 2
        return 0

    def update_particles(self):
        active = len(self.parts)
        self.parts = [a + 1 for a in self.parts if a + 1 < 24]
        return active


class BurstSparks:
    """RoomEffect_BurstSparkSpawner + RoomEffect_BurstSparkParticle: at ages 1, 4, 7, ... (8
    pairs) from render matrix 0x11 x (0, 0, 50), a spark moves Ry(yaw) Rx(pitch - 0x200)
    (0, 0, speed) each update (facing Aya, pitched 45 degrees down); it contacts Aya within 50 +
    her radius while above floor - 0x202 (one hit: owner bits -> 0x19), stops on the floor; the
    paired state-4 spark and spent sparks live 16 updates. Returns 2 from age 8."""

    def __init__(self, speed, origin, distance, aya_radius):
        self.speed, self.origin, self.d, self.r = speed, origin, distance, aya_radius
        self.count, self.sparks, self.hit = 0, [], False

    def init(self): pass

    def step(self, age, fx):
        from .room_effects import rcos, rsin
        if age % 3 == 1 and self.count < 8:
            x, y, z = self.origin(age)
            self.sparks.append(dict(x=x, y=y, z=z, state=0, t=0)); self.sparks.append(dict(state=4, t=0))
            self.count += 1
        p = -0x200 & 0xFFF
        dy = -rsin(p) * self.speed // 4096; dz = rcos(p) * self.speed // 4096   # (0, -s d, c d) then facing -z
        for q in self.sparks:
            if q['state'] != 0: continue
            q['t'] += 1; q['y'] += dy; q['z'] -= dz
            if q['x'] ** 2 + (q['z'] + self.d) ** 2 < (50 + self.r) ** 2 and -0x202 < q['y']:
                if not self.hit: self.hit = True; fx.contacts.append(fx.update)
                q['state'], q['t'] = 2, 0
            elif q['y'] >= 0: q['state'], q['t'] = 2, 0
        return 2 if age >= 8 else 0

    def update_particles(self):
        active = len(self.sparks)
        keep = []
        for q in self.sparks:
            if q['state'] in (2, 4):
                q['t'] += 1
                if q['t'] >= 16: continue
            keep.append(q)
        self.sparks = keep
        return active


def _spark_ring(spec, distance, aya_radius, rng, scene=None):
    from .room_effects import TaskEffect
    r = TaskEffect(spec['script'], lambda var0: SparkRing(0, aya_radius)).run()
    return dict(contacts=[c - 1 for c in r['contacts']], release=r['release'])


def _burst_sparks(spec, distance, aya_radius, rng, scene=None):
    from .room_effects import TaskEffect
    sc = scene or {}
    speed = sc.get('slot_value')
    if speed is None: raise ValueError('burst spark speed (RoomEffect_SetSparkSlot) unresolved')
    jt = sc['joint'](0x11) if sc.get('joint') else None
    def origin(age):
        if not jt: return (0, -300, -50)
        R, t = jt(age)
        return (int(t[0] + R[0][2] * 50), int(t[1] + R[1][2] * 50), int(t[2] + R[2][2] * 50))
    r = TaskEffect(spec['script'], lambda var0: BurstSparks(speed, origin, distance, aya_radius)).run()
    return dict(contacts=[c - 1 for c in r['contacts']], release=r['release'])


class HomingFlash:
    """room_lib/homing_flash.c RoomEffect_FlashSpriteController + RoomEffect_HomingSpark. The
    controller for task var0 = phase 0 / 1 / 2 anchors 300 units ahead of the actor at yaw
    offset -lift / 0 / +lift; after 16 + 4 updates it releases a spark that each update eases
    its yaw toward Aya by (difference x speed) >> 12, moves `distance` units, and contacts her
    within 50 + her radius (one hit per effect: owner bits -> 0x11); the spark lives 36 updates.
    The controller returns 2 four updates later and frees when its sparks are gone."""

    def __init__(self, phase, params, shared, distance, aya_radius):
        self.phase, self.p, self.shared, self.d, self.r = phase, params, shared, distance, aya_radius
        self.state, self.frame, self.sparks = 0, 0, []

    def init(self): pass

    def step(self, age, fx):
        import math
        if self.state == 0:
            self.frame += 1
            if self.frame >= 16: self.state, self.frame = 1, 0
        elif self.state == 1:
            self.frame += 1
            if self.frame >= 4:
                self.state, self.frame = 2, 0
                off = (-1, 0, 1)[self.phase] * self.p['lift']
                yaw = math.pi + off * math.pi / 2048           # facing -z, offset by lift angle units
                x, z = 300 * math.sin(yaw) * -1, 300 * math.cos(yaw)
                self.sparks.append(dict(x=x, z=z, h=yaw, age=0, live=True))
        else:
            self.frame += 1
            if self.frame >= 4: return 2
        return 0

    def update_particles(self):
        import math
        active = len(self.sparks)
        for q in self.sparks:
            q['age'] += 1
            want = math.atan2(-(0 - q['x']), (-self.d) - q['z'])
            diff = (want - q['h'] + math.pi) % (2 * math.pi) - math.pi
            q['h'] += diff * self.p['speed'] / 4096
            q['x'] += -math.sin(q['h']) * self.p['distance']; q['z'] += math.cos(q['h']) * self.p['distance']
            if q['live'] and q['x'] ** 2 + (q['z'] + self.d) ** 2 < (50 + self.r) ** 2:
                q['live'] = False
                if not self.shared['hit']: self.shared['hit'] = True; self.shared['contacts'].append(self.shared['fx'].update)
        self.sparks = [q for q in self.sparks if q['age'] < 36]
        return active


def _homing_flash(spec, distance, aya_radius, rng, scene=None):
    from .room_effects import TaskEffect
    sc = scene or {}
    steps = sc.get('steps') or (80, 400, 150)
    params = dict(distance=steps[0], speed=steps[1], lift=steps[2])
    shared = dict(hit=False, contacts=[], fx=None)
    fx = TaskEffect(spec['script'], lambda var0: HomingFlash(var0, params, shared, distance, aya_radius))
    shared['fx'] = fx
    r = fx.run()
    return dict(contacts=[c - 1 for c in shared['contacts']], release=r['release'])


TASK_RUNNERS = {'RoomEffect_BurstOrbController': _burst_orb, 'RoomEffect_SoundBurstController': _sound_burst,
                'RoomEffect_FlashSpriteController': _homing_flash,
                'RoomEffect_SparkRingController': _spark_ring, 'RoomEffect_BurstSparkSpawner': _burst_sparks}
from .room_m256 import trail_run as _m256_trail, scatter_run as _m256_scatter
TASK_RUNNERS.update({'RoomM256_TrailEmitter': _m256_trail, 'RoomM256_ScatterDropEmitter': _m256_scatter})   # room_m256.py
from .room_lib_effects import orbit_flare_run as _orbit_flare, line_burst_run as _line_burst, phased_spark_run as _phased, visual_run as _visual, ground_sweep_run as _sweep, rising_spray_run as _spray, grab_run as _grab, seeking_trail_run as _seek, scatter_trail_run as _scatter_trail, beacon_run as _beacon, model_pulse_run as _mpulse, pulse_ring_run as _pring
TASK_RUNNERS.update({'RoomEffect_OrbitFlareController': _orbit_flare, 'RoomEffect_LineBurstController': _line_burst,
                     'RoomEffect_PhasedSparkController': _phased, 'RoomEffect_WaveSparkController': _visual,
                     'RoomEffect_GroundSweepController__room_m269_warehouse': _sweep, 'RoomEffect_RisingSprayController': _spray,
                     'RoomEffect_OrbitTrailBurst__room_m269_warehouse': _grab,
                     'RoomEffect_SeekingTrailController': _seek, 'RoomEffect_ScatterTrailController': _scatter_trail,
                     'RoomM005_Orbiter': _beacon, 'RoomM023_ScatterEmitter': _beacon, 'RoomM123_JointTriangleEmitter': _beacon,
                     'RoomM089_SpiralTrail': _mpulse, 'RoomM123_PulseRing': _pring})
SCENE_RUNNERS = {'RoomM256_TrailEmitter', 'RoomM256_ScatterDropEmitter', 'RoomEffect_OrbitFlareController', 'RoomEffect_LineBurstController', 'RoomEffect_PhasedSparkController', 'RoomEffect_WaveSparkController', 'RoomEffect_GroundSweepController__room_m269_warehouse', 'RoomEffect_RisingSprayController', 'RoomEffect_OrbitTrailBurst__room_m269_warehouse', 'RoomEffect_SeekingTrailController', 'RoomEffect_ScatterTrailController', 'RoomM005_Orbiter', 'RoomM023_ScatterEmitter', 'RoomM123_JointTriangleEmitter', 'RoomM089_SpiralTrail', 'RoomM123_PulseRing', 'RoomEffect_SoundBurstController', 'RoomEffect_SparkRingController', 'RoomEffect_BurstSparkSpawner', 'RoomEffect_FlashSpriteController'}


@lru_cache(maxsize=None)
def task_spec(map_id, command):
    """dict(controller, script triples) for a supported room task program, or None."""
    from .room_handlers import handler
    if command < 85: return None
    h = handler(map_id, command, 14)
    if not h or not h.get('fields'): return None
    name = h['fields'][0][1] or ''
    if name not in TASK_CONTROLLERS and name not in TASK_RUNNERS: return None
    ov = overlay(map_id); blob = room_blob(map_id); at = h['fields'][13][0] - ov['vram']
    triples = []
    while len(triples) < 64:
        t = struct.unpack_from('<3H', blob, at); at += 6; triples.append(t)
        if t[0] == 0: break
    return dict(controller=name, script=triples)


def task_timeline(map_id, command, distance=0, aya_radius=0, rng=None, scene=None):
    from .room_effects import TaskEffect
    spec = task_spec(map_id, command)
    if not spec: raise ValueError('unsupported task program')
    if spec['controller'] in TASK_RUNNERS:
        runner = TASK_RUNNERS[spec['controller']]
        if spec['controller'] in SCENE_RUNNERS: return runner(spec, distance, aya_radius, rng or random.Random(0), scene)
        return runner(spec, distance, aya_radius, rng or random.Random(0))
    r = TaskEffect(spec['script'], lambda var0: TASK_CONTROLLERS[spec['controller']]()).run()
    return dict(contacts=[c - 1 for c in r['contacts']], release=r['release'])   # 0-based like timeline()


@lru_cache(maxsize=1)
def task_actions():
    """[(map, actor, dict(slot, command, reset))] for slot >= 3 calls loading a supported task program."""
    from .decode_enemy_actions import completion_reset, literal
    from .power_gaps import _scripts
    out = []
    for (m, a), s in _scripts().items():
        nodes = sorted(s['nodes'], key=lambda n: n['offset'])
        for k, n in enumerate(nodes):
            if n['handler'] != 'Script_RunEntityCommand' or literal(n['args'][0]) is None or literal(n['args'][0]) < 3: continue
            cmds = []; sends = []
            for q in nodes[max(0, k - 30):k]:
                v = [literal(x) for x in q['args']]
                if q['handler'] == 'Script_GetEntityEffect' and v[0] is not None: cmds.append(v[0]); sends = []
                elif q['handler'] == 'Pm_ScriptSendCommand0' and cmds and None not in v[1:5]: sends.append(tuple(s16(x) for x in v[1:5]))
            if not cmds: continue
            try: spec = task_spec(m, cmds[-1])
            except (struct.error, IndexError): spec = None
            if spec is None:
                # The last load can be a motion class (RoomLib Handler C/D/E, PM < 85): use the latest
                # supported task program loaded in the same block (e.g. room 188 slot 4: WaveSpark + C).
                for c_ in reversed(cmds[:-1]):
                    try: s2 = task_spec(m, c_)
                    except (struct.error, IndexError): s2 = None
                    if s2: spec = s2; cmds = cmds + [c_]; break
            if spec is None:
                # Room 256 slot 4 loads its scatter program, then the swing class (PM 76) just before
                # the command: look further back in the same action block for a RoomM256 program.
                for q in reversed(nodes[max(0, k - 80):k]):
                    v0 = literal(q['args'][0]) if q['args'] else None
                    if q['handler'] == 'Script_GetEntityEffect' and v0 is not None and v0 >= 85:
                        try: s2 = task_spec(m, v0)
                        except (struct.error, IndexError): s2 = None
                        if s2 and s2['controller'].startswith('RoomM256_'): spec, cmds = s2, cmds + [v0]
                        break
            if spec: out.append((m, a, dict(slot=literal(n['args'][0]), command=cmds[-1], sends=sends,
                                            reset=completion_reset(s, n['offset']))))
    return out


def task_plan(foe, slot, cells, actor=None):
    import json
    from .enemy_identity import cells_key, identity_keys
    try: m, ident = int(foe['loc']), int(foe['name'], 16)
    except (KeyError, ValueError, TypeError): return None
    keys = identity_keys(dict(cells_key(cells)))
    rows = [dict(act, actor=a) for mm, a, act in task_actions() if mm == m and act['slot'] == slot and actor in (None, a)
            and any(i == ident for i, _ in keys.get((mm, a), []))]
    if not rows or len({json.dumps({k: r[k] for k in ('command', 'reset')}) for r in rows}) != 1: return None
    act = rows[0]
    scene = {}
    if act['sends']:
        mode, a, b, c = act['sends'][-1]
        scene['steps'] = (a, b, c)                         # RoomLib_SetArgs3 argument block
        scene['slot_value'] = a                            # RoomEffect_SetSparkSlot(unused, value)
    rec = slot_record(m, act['actor'], slot)
    if rec:
        from .enemy_reach import move_speed
        from .power_gaps import _scripts
        ms0 = move_speed(_scripts()[m, act['actor']]['nodes']) or 4096
        scene['joint'] = lambda j, rec=rec, ms_=ms0: joint_track(m, act['actor'], rec[0], rec[1], rec[2], rec[3], ms_, joint=j)
        scene['arm'] = (m, act['actor'], tuple(rec))                     # room_m256 runners
        try:
            jt = joint_track(m, act['actor'], rec[0], rec[1], rec[2], rec[3],
                             move_speed(_scripts()[m, act['actor']]['nodes']) or 4096, joint=9)
            def origin(age, jt=jt):
                R, t = jt(age)
                return (int(t[0] + R[0][2] * -60), int(t[2] + R[2][2] * -60))
            scene['origin'] = origin
            ms_ = move_speed(_scripts()[m, act['actor']]['nodes']) or 4096
            scene['joint'] = lambda j, rec=rec, ms_=ms_: joint_track(m, act['actor'], rec[0], rec[1], rec[2], rec[3], ms_, joint=j)
            scene['arm'] = (m, act['actor'], tuple(rec))                 # room_m256 runners
        except (ValueError, IndexError): pass
    return dict(action=act, scene=scene,
                run=lambda distance, aya_radius, rng: task_timeline(m, act['command'], distance, aya_radius, rng, scene))
