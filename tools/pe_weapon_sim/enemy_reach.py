"""Enemy hit-sphere geometry from room models and animations, offline.

Ports:
- render/object.c Render_SetupEntityPrims: model layout (0x1C header, parts, vertices,
  colours, primitive descriptors, two section vectors, part bounds pairs, projection origin,
  matrix commands). A part with visible == 1 and bounds[2i+1].pad >= 0 owns a hit sphere:
  centre bounds[2i].xyz, radius bounds[2i].pad (x move_speed / 4096), part id i.
- anim/bone_rotations.c Anim_DecodeBoneRotationsByte / Short: root translation channels, then
  per bone YXZ angles (byte samples x 16, or u16), each channel either constant or per-frame.
- render/object.c Render_TransformVertices: bone hierarchy from matrix commands (-1 push,
  -2 pop); a bone's matrix = parent x active[bone]; the root takes the animation translation,
  others (0, 0, parts[bone].translation_z); the sphere centre = bone matrix x bounds vertex.
- scene/room_load.c / entity/frame_update.c: models are room directory field 0x0C records
  (slot = actor type), animation banks field 0x10 (group = actor type, slot = mode).
Coordinates are the model's local frame (y down, PSX convention, facing -z); move_speed / 4096
scales positions (model matrix) and radii (entity/allocation.c sphere test).
Validated read-only against the live game (Eve's 9 spheres over 11 consistent reads: every
centre within 7 units; the entries lag the frame counter by 1-2 frames).

Reach (does a melee hit land): Entity_CheckActionIdMatch registers a hit when a sphere of a
listed contact part overlaps any of Aya's spheres during the window. Scenario: both on the same
floor, facing each other (Aya aims at her target; enemies turn to Aya before attacking), Aya in
her captured idle pose (pe-aya-hit-spheres-2026-10-18.json). `reach` = the largest origin
distance at which some window frame has an overlap.
"""
import json, math, struct
from functools import lru_cache
from pathlib import Path

from .extract_enemy_scripts import PROJECT, sectors

ROOT = Path(__file__).resolve().parents[2] / 'findings/data'
DISC1 = PROJECT / 'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin'


def _u32(b, at): return struct.unpack_from('<I', b, at)[0]


@lru_cache(maxsize=64)
def room_blob(map_id):
    inv = json.loads((ROOT / 'pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    room = next(r for r in inv['rooms'] if r['disc'] == 1 and r['map'] == int(map_id))
    with DISC1.open('rb') as f:
        return sectors(f, room['lba'], room['sectors'])


def _records(blob, field):
    directory = _u32(blob, 4)
    desc = _u32(blob, directory + field); at = desc & 0x3FFFFF
    return [(_u32(blob, at + 12 * i + 4) & 0xFFFFFF, _u32(blob, at + 12 * i + 4) >> 24, blob[at + 12 * i + 11])
            for i in range(desc >> 22)]


def model(blob, actor_type):
    """Parsed model for an actor type, or None."""
    ptr = next((p for p, slot, _ in _records(blob, 0x0C) if slot == actor_type), None)
    if ptr is None: return None
    h = struct.unpack_from('<HBB2x11H', blob, ptr)
    prim_blocks, parts_n, entries_n, verts, p34, p28, p24, p1c, anchor_y, anchor_m, shadow, scale, cmd_bytes, vis = h
    at = ptr + 0x1C
    parts = []
    for i in range(parts_n):
        vs, vc, visible = struct.unpack_from('<HHB', blob, at); tz = struct.unpack_from('<i', blob, at + 8)[0]
        parts.append(dict(visible=visible, translation_z=tz)); at += 12
    at += verts * 8 + verts * 4 + (p34 + p28 + p24 + p1c) * 12
    section = [struct.unpack_from('<4h', blob, at + 8 * k) for k in range(2)]; at += 16
    bounds = [struct.unpack_from('<4h', blob, at + 8 * k) for k in range(parts_n * 2)]; at += parts_n * 16
    origin = struct.unpack_from('<4h', blob, at); at += 8
    commands = list(struct.unpack_from('<%db' % cmd_bytes, blob, at))
    spheres = [dict(part=i, centre=bounds[2 * i][:3], radius=bounds[2 * i][3])
               for i in range(parts_n) if parts[i]['visible'] == 1 and bounds[2 * i + 1][3] >= 0]
    return dict(offset=ptr, parts=parts, bounds=bounds, commands=commands, spheres=spheres,
                cylinder_radius=section[0][3], entries=entries_n)


def animation(blob, actor_type, mode):
    ptr = next((p for p, slot, grp in _records(blob, 0x10) if grp == actor_type and slot == mode), None)
    return ptr


def decode_frame(blob, ptr, frame):
    """(root translation [3], [(ax, ay, az)] per bone) for one animation frame (0..4095 angles)."""
    flags, last_bone, frames = blob[ptr], blob[ptr + 1], blob[ptr + 2]
    if not 0 <= frame < frames: raise ValueError('frame outside clip')
    short = (flags & 3) == 2
    at = ptr + 12; stride = ((frames >> 1) + 1) * 4
    trans = []
    for _ in range(3):
        marker, = struct.unpack_from('<h', blob, at)
        if marker: trans.append(struct.unpack_from('<h', blob, at + 2)[0]); at += 4
        else: trans.append(struct.unpack_from('<h', blob, at + 2 + 2 * frame)[0]); at += stride
    angles = []
    bstride = (((frames >> 2) + 1) * 4) if not short else stride
    for _ in range(last_bone + 1):
        a = []
        for _ in range(3):
            if short:
                marker, = struct.unpack_from('<h', blob, at)
                if marker: v = struct.unpack_from('<H', blob, at + 2)[0]; at += 4
                else: v = struct.unpack_from('<H', blob, at + 2 + 2 * frame)[0]; at += bstride
            else:
                if blob[at]: v = blob[at + 1] * 16; at += 4
                else: v = blob[at + 1 + frame] * 16; at += bstride
            a.append(v)
        angles.append(tuple(a))
    return trans, angles


def _rot(axis, a):
    c, s = math.cos(a * math.pi / 2048), math.sin(a * math.pi / 2048)
    if axis == 'x': return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if axis == 'y': return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _mul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def _app(m, v): return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def rot_yxz(a, order='YXZ'):
    """RotMatrixYXZ: M = Ry * Rx * Rz (validated against live sphere entries; other orders for tests)."""
    m = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    mats = {'X': _rot('x', a[0]), 'Y': _rot('y', a[1]), 'Z': _rot('z', a[2])}
    for k in order: m = _mul(m, mats[k])
    return m


def bones_at(mdl, trans, angles, order='YXZ'):
    """Render matrices in command order (RenderObjectEntity.matrices[k], Render_TransformVertices
    out++ per bone command): [(rotation 3x3, translation)] in the model frame."""
    active = [rot_yxz(a, order) for a in angles]
    stack = []; cur_r = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; cur_t = [0, 0, 0]; out = []
    for c in mdl['commands']:
        if c == -1: stack.append((cur_r, cur_t)); continue
        if c == -2: cur_r, cur_t = stack.pop(); continue
        local_t = trans if c == 0 else [0, 0, mdl['parts'][c]['translation_z']]
        cur_t = [cur_t[i] + _app(cur_r, local_t)[i] for i in range(3)]
        cur_r = _mul(cur_r, active[c])
        out.append((cur_r, cur_t))
    return out


def spheres_at(mdl, trans, angles, order='YXZ'):
    """{part: (x, y, z, radius)} in the model frame for one decoded frame."""
    active = [rot_yxz(a, order) for a in angles]
    stack = []; cur_r = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; cur_t = [0, 0, 0]
    want = {s['part']: s for s in mdl['spheres']}
    out = {}
    for c in mdl['commands']:
        if c == -1: stack.append((cur_r, cur_t)); continue
        if c == -2: cur_r, cur_t = stack.pop(); continue
        if c >= len(active): raise ValueError('bone without animation channel')
        local_t = trans if c == 0 else [0, 0, mdl['parts'][c]['translation_z']]
        t = [cur_t[i] + _app(cur_r, local_t)[i] for i in range(3)]
        r = _mul(cur_r, active[c])
        cur_r, cur_t = r, t
        if c in want:
            p = _app(r, want[c]['centre'])
            out[c] = (t[0] + p[0], t[1] + p[1], t[2] + p[2], want[c]['radius'])
    return out


def move_speed(script_nodes):
    """Script_SetEntityMoveSpeed literal >> 4 (system_opcodes.c); 4096 when never set; None if
    the script sets several values or a non-literal one."""
    vals = set()
    for n in script_nodes:
        if n['handler'] == 'Script_SetEntityMoveSpeed':
            a = n['args'][0]
            if a['mode'] != 0: return None
            vals.add(a['value'] >> 4)
    return 4096 if not vals else (vals.pop() if len(vals) == 1 else None)


@lru_cache(maxsize=1)
def aya_spheres():
    d = json.loads((ROOT / 'pe-aya-hit-spheres-2026-10-18.json').read_text(encoding='utf-8'))
    return [(s['x'], s['y'], s['z'], s['radius']) for s in d['spheres']]


def pair_reach(e, a, scale_r):
    """Largest origin distance d with enemy sphere e (enemy frame) touching Aya sphere a (her
    frame, facing the enemy: (x, y, z) -> (-x, y, -d - z)), or None."""
    ex, ey, ez, er_ = e; ax, ay, az, ar = a
    R = er_ * scale_r + ar
    rem = R * R - (ex + ax) ** 2 - (ey - ay) ** 2
    if rem < 0: return None
    return -ez - az + math.sqrt(rem)


def frame_spheres(blob, mdl, anim_ptr, frame, scale):
    t, ang = decode_frame(blob, anim_ptr, frame)
    k = scale / 4096
    return {p: (x * k, y * k, z * k, r) for p, (x, y, z, r) in spheres_at(mdl, t, ang).items()}


def action_reach(map_id, actor_type, row, scale):
    """dict(reach, frame, part) over the window's exit-clip frames for one melee_window row."""
    from .decode_enemy_actions import literal
    blob = room_blob(map_id); mdl = model(blob, actor_type)
    if mdl is None: raise ValueError('no model')
    exit_mode = row['exit_mode']; ptr = animation(blob, actor_type, exit_mode)
    if ptr is None: raise ValueError('no exit animation')
    frames = blob[ptr + 2]
    last = frames - 1
    if row['closed_by'] == 'frame': last = min(last, row['hit_frame'])
    ids = row['contact_ids']
    if not ids: raise ValueError('no contact ids')
    best = dict(reach=None, frame=None, part=None)
    for f in range(0, last + 1):
        sph = frame_spheres(blob, mdl, ptr, f, scale)
        for p in ids:
            if p not in sph: continue
            for a in aya_spheres():
                d = pair_reach(sph[p], a, scale / 4096)
                if d is not None and (best['reach'] is None or d > best['reach']):
                    best = dict(reach=round(d, 1), frame=f, part=p)
    return best


@lru_cache(maxsize=1)
def catalog():
    """{(map, actor_type, slot): dict(reach, frame, part, move_speed)} for melee_window actions."""
    from .melee_window import actions
    dec = json.loads((ROOT / 'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    nodes = {(s['map'], s['actor_type']): s['nodes'] for s in dec['scripts']}
    out = {}
    for m, actor, row in actions():
        ms = move_speed(nodes.get((m, actor), []))
        if ms is None: out[m, actor, row['slot']] = dict(error='move_speed not literal'); continue
        try: out[m, actor, row['slot']] = dict(action_reach(m, actor, row, ms), move_speed=ms)
        except (ValueError, StopIteration, struct.error, IndexError) as exc:
            out[m, actor, row['slot']] = dict(error=str(exc) or type(exc).__name__)
    return out


def reach_rows(foe, cells=None):
    """{slot: reach} for an identity where every actor resolving to it agrees (within 1 unit)."""
    from collections import defaultdict
    from .enemy_identity import cells_key, identity_keys
    try: key = (int(foe['loc']), int(foe['name'], 16))
    except (KeyError, ValueError, TypeError): return {}
    keys = identity_keys(dict(cells_key(cells)))
    per = defaultdict(list)
    for (m, actor, slot), v in catalog().items():
        if m != key[0]: continue
        if any(ident == key[1] for ident, _ in keys.get((m, actor), [])): per[slot].append(v.get('reach'))
    out = {}
    for slot, vals in per.items():
        if None in vals or max(vals) - min(vals) > 1: continue
        out[slot] = min(vals)
    return out


def main():
    """python -m pe_weapon_sim.enemy_reach: writes findings/data/pe-enemy-reach-2026-10-18.json."""
    rows = [dict(map=m, actor_type=a, slot=s, **v) for (m, a, s), v in sorted(catalog().items())]
    out = dict(scope='melee reach per slot 0-2 action: largest origin distance with contact-part / Aya sphere '
                     'overlap in the contact window (same floor, facing each other, Aya idle pose)',
               validation='pe-hit-sphere-validation-2026-10-18.json', actions=rows)
    (ROOT / 'pe-enemy-reach-2026-10-18.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    ok = [r for r in rows if r.get('reach') is not None]
    print(json.dumps(dict(actions=len(rows), with_reach=len(ok), errors=len([r for r in rows if 'error' in r]))))


if __name__ == '__main__':
    main()
