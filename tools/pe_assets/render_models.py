"""Render room character models (posed at frame 0 of their first animation) with textures, offline."""
import math, struct, sys, os
from PIL import Image, ImageDraw
from pe_weapon_sim.extract_enemy_scripts import word, sectors, PROJECT, BRIDGE
from pe_weapon_sim.extract_animations import ram_from_pst

ram = ram_from_pst(BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst')
BASE = word(ram, 0xb0dd8)
u16 = lambda b, o: struct.unpack_from('<H', b, o)[0]
s16 = lambda b, o: struct.unpack_from('<h', b, o)[0]
OUT = os.path.join(os.path.dirname(__file__), 'renders')
NOTEX = os.environ.get('NOTEX') == '1'
os.makedirs(OUT, exist_ok=True)


def room_blob(m, disc=1):
    f = open(PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin', 'rb')
    start = word(ram, 0x93378 + (m - 1) * 8); packed = word(ram, 0x9337c + (m - 1) * 8)
    return sectors(f, BASE + start + (packed & 255) + ((packed >> 8) & 4095), packed >> 20)


def room_texture_blobs(m, disc=1):
    """Scene_LoadRoom reads a room as three runs of sectors: a scratch blob and a texture blob (both
    SceneAssetBlobs whose TIM records go to VRAM; room_load.c:427-465), then the room data."""
    f = open(PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin', 'rb')
    start = word(ram, 0x93378 + (m - 1) * 8); packed = word(ram, 0x9337c + (m - 1) * 8)
    scratch, texture = packed & 255, (packed >> 8) & 4095
    out = []
    if scratch: out.append(sectors(f, BASE + start, scratch))
    if texture: out.append(sectors(f, BASE + start + scratch, texture))
    return out


def room_vram(m, disc=1):
    vram = [0] * (1024 * 512)
    for b in room_texture_blobs(m, disc):
        try: upload_tims(b, vram)
        except Exception: pass
    return vram


def image_blob(idx, disc=1):
    f = open(PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin', 'rb')
    s0 = u16(ram, 0x930D8 + 2 * idx); s1 = u16(ram, 0x930D8 + 2 * idx + 2)
    return sectors(f, BASE + s0, s1 - s0)


def records(blob, field):
    d = word(blob, 4); desc = word(blob, d + field); at = desc & 0x3fffff
    return [(word(blob, at + 12 * i + 4) & 0xffffff, word(blob, at + 12 * i + 4) >> 24, blob[at + 12 * i + 11]) for i in range(desc >> 22)]


def upload_tims(blob, vram):
    d = word(blob, 4); desc = word(blob, d + 0x28); at = desc & 0x3fffff
    for i in range(desc >> 22):
        r = at + 20 * i
        src = word(blob, r + 4); rect = word(blob, r + 8); sec = word(blob, r + 12); rect2 = word(blob, r + 16)
        def put(off, rc, h):
            x, y, w = (rc >> 10) & 0x7ff, rc >> 21, rc & 0x3ff
            for yy in range(h):
                for xx in range(w):
                    p = off + 2 * (yy * w + xx)
                    if p + 2 <= len(blob) and 0 <= y + yy < 512 and 0 <= x + xx < 1024:
                        vram[(y + yy) * 1024 + x + xx] = u16(blob, p)
        h = src >> 24 or 256
        put(src & 0xffffff, rect, h)
        if sec & 0xffffff:
            put((src & 0xffffff) + (sec & 0xffffff), rect2, sec >> 24)


def texel(vram, page, clut, u, v):
    px, py, bpp = (page & 15) * 64, ((page >> 4) & 1) * 256, (page >> 7) & 3
    cx, cy = (clut & 63) * 16, (clut >> 6) & 511
    if bpp == 0:
        w = vram[(py + v) * 1024 + px + u // 4]; idx = (w >> ((u & 3) * 4)) & 15
        c = vram[cy * 1024 + cx + idx]
    elif bpp == 1:
        w = vram[(py + v) * 1024 + px + u // 2]; idx = (w >> ((u & 1) * 8)) & 255
        c = vram[cy * 1024 + cx + idx]
    else:
        c = vram[(py + v) * 1024 + px + u]
    if c == 0: return None
    return ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)


def model(blob, off):
    parts, verts = blob[off + 2], u16(blob, off + 6)
    pk = [u16(blob, off + 8 + 2 * k) for k in range(4)]
    mcb = u16(blob, off + 0x18)
    at = off + 0x1C
    ptab = [struct.unpack_from('<HHBxxxi', blob, at + 12 * i) for i in range(parts)]; at += 12 * parts
    V = [struct.unpack_from('<hhh', blob, at + 8 * i) for i in range(verts)]; at += 8 * verts
    at += 4 * verts
    D = [(blob[at + 12 * i + 3], struct.unpack_from('<4H', blob, at + 12 * i + 4)) for i in range(sum(pk))]; at += 12 * sum(pk)
    at += (2 + 2 * parts + 1) * 8
    cmds = list(struct.unpack_from('<%db' % mcb, blob, at)); at += (mcb + 3) // 4 * 4
    T = []
    for i in range(pk[0]): T.append(struct.unpack_from('<BBHBBHBBHBBH', blob, at + 16 * i))
    at += 16 * pk[0]
    for i in range(pk[1]): T.append(struct.unpack_from('<BBHBBHBBH', blob, at + 12 * i))
    return dict(parts=parts, ptab=ptab, V=V, D=D, pk=pk, cmds=cmds, T=T)


def anim_frame(blob, off, parts, frame=0):
    return anim_frame_at(blob, off, frame)


def anim_frame_at(blob, off, frame):
    """Anim_DecodeBoneRotationsByte / Short (anim/bone_rotations.c) for one frame: root translation and
    per-bone YXZ angles. A constant channel is 4 bytes; a sampled one holds one value per frame."""
    flags, last, frames = blob[off], blob[off + 1], blob[off + 2]
    frame = max(0, min(frame, max(frames - 1, 0)))
    cur = off + 12; tr = []
    stride = (frames >> 1) + 1
    for _ in range(3):
        mark = s16(blob, cur)
        tr.append(s16(blob, cur + 2) if mark else s16(blob, cur + 2 + 2 * frame)); cur += 4 if mark else stride * 4
    ang = []
    short = (flags & 3) == 2
    bstride = ((frames >> 2) + 1) * 4 if not short else stride * 4
    for b in range(last + 1):
        a = []
        for _ in range(3):
            if short:
                mark = s16(blob, cur); a.append(u16(blob, cur + 2) if mark else u16(blob, cur + 2 + 2 * frame)); cur += 4 if mark else bstride
            else:
                mark = blob[cur]; a.append((blob[cur + 1] if mark else blob[cur + 1 + frame]) * 16); cur += 4 if mark else bstride
        ang.append(a)
    return tr, ang


def rot_yxz(a):
    x, y, z = [t * 2 * math.pi / 4096 for t in a]
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mm(mm(Ry, Rx), Rz)


def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]


def pose(md, tr, ang):
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    cur = (I, [0, 0, 0]); stack = []; mats = {}
    for c in md['cmds']:
        if c == -1: stack.append(cur); continue
        if c == -2: cur = stack.pop(); continue
        R = rot_yxz(ang[c]) if c < len(ang) else I
        nr = mm(cur[0], R)
        vec = tr if c == 0 else [0, 0, md['ptab'][c][3]]
        nt = [a + b for a, b in zip(mv(cur[0], vec), cur[1])]
        mats[c] = (nr, nt); cur = (nr, nt)
    W = [None] * len(md['V'])
    for p, (vs, vc, vis, tz) in enumerate(md['ptab']):
        R, t = mats.get(p, (I, [0, 0, 0]))
        for i in range(vs, vs + vc):
            if i < len(W): W[i] = [a + b for a, b in zip(mv(R, md['V'][i]), t)]
    return W


def relocate(md, x, y, palette_row):
    """Render_InitPrimBlock: move face texture pages / palettes to where the entity's TIMs went."""
    half = y == 128
    if x == 960 and md['T'] and md['T'][0][5] == 31: return    # already placed (the player)
    page = (((x >> 6) - 8) * 2) + (y >> 7) + ((y >> 8) * 30)
    po = page >> 1 if x != 960 else ((page << 16) & 0xffffffff) >> 17
    pal = palette_row * 64 - 0x7080
    out = []
    for t in md['T']:
        t = list(t)
        quad = len(t) == 12
        vs = [1, 4, 7, 10] if quad else [1, 4, 7]
        if half:
            add = po if t[1] < 128 else po + 1
            for k in vs: t[k] = (t[k] + 128) & 255
            t[5] = (t[5] + add) & 0xffff
        else:
            t[5] = (t[5] + po) & 0xffff
        t[2] = (t[2] + pal) & 0xffff
        out.append(tuple(t))
    md['T'] = out


def render(md, W, vram, view, size=300):
    pts = [w for w in W if w]
    if not pts: return None
    def proj(w):
        x, y, z = w
        if view == 'side': x, z = z, -x
        if view == 'back': x, z = -x, -z
        return x, -y, z
    P = [proj(w) if w else None for w in W]
    xs = [p[0] for p in P if p]; ys = [p[1] for p in P if p]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    sc = (size - 20) / span
    ox, oy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    S = [((p[0] - ox) * sc + size / 2, (oy - p[1]) * sc + size / 2, p[2]) if p else None for p in P]
    img = Image.new('RGB', (size, size), (40, 40, 48)); px = img.load(); zb = [[1e18] * size for _ in range(size)]
    faces = []
    nq, nt = md['pk'][0], md['pk'][1]
    for fi, (kind, idx) in enumerate(md['D']):
        if fi < nq:
            t = md['T'][fi]; uv = [(t[0], t[1]), (t[3], t[4]), (t[6], t[7]), (t[9], t[10])]; clut, page = t[2], t[5]
            faces += [((idx[0], idx[1], idx[2]), (uv[0], uv[1], uv[2]), clut, page), ((idx[1], idx[3], idx[2]), (uv[1], uv[3], uv[2]), clut, page)]
        elif fi < nq + nt:
            t = md['T'][fi]; faces.append(((idx[0], idx[1], idx[2]), ((t[0], t[1]), (t[3], t[4]), (t[6], t[7])), t[2], t[5]))
        else:
            faces.append(((idx[0], idx[1], idx[2]), None, None, None))
    for (a, b, c), uv, clut, page in faces:
        if max(a, b, c) >= len(S) or not (S[a] and S[b] and S[c]): continue
        A, B, C = S[a], S[b], S[c]
        x0, x1 = int(max(0, min(A[0], B[0], C[0]))), int(min(size - 1, max(A[0], B[0], C[0])))
        y0, y1 = int(max(0, min(A[1], B[1], C[1]))), int(min(size - 1, max(A[1], B[1], C[1])))
        den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
        if abs(den) < 1e-9: continue
        wa, wb, wc = W[a], W[b], W[c]
        n = [(wb[1]-wa[1])*(wc[2]-wa[2])-(wb[2]-wa[2])*(wc[1]-wa[1]), (wb[2]-wa[2])*(wc[0]-wa[0])-(wb[0]-wa[0])*(wc[2]-wa[2]), (wb[0]-wa[0])*(wc[1]-wa[1])-(wb[1]-wa[1])*(wc[0]-wa[0])]
        ln = math.sqrt(sum(t * t for t in n)) or 1
        g = int(80 + 150 * abs(n[2 if view != 'side' else 0]) / ln); shade = (g, g, g)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                l1 = ((B[1] - C[1]) * (x - C[0]) + (C[0] - B[0]) * (y - C[1])) / den
                l2 = ((C[1] - A[1]) * (x - C[0]) + (A[0] - C[0]) * (y - C[1])) / den
                l3 = 1 - l1 - l2
                if l1 < 0 or l2 < 0 or l3 < 0: continue
                z = l1 * A[2] + l2 * B[2] + l3 * C[2]
                if z >= zb[y][x]: continue
                if uv and not NOTEX:
                    u = int(l1 * uv[0][0] + l2 * uv[1][0] + l3 * uv[2][0]) & 255
                    v = int(l1 * uv[0][1] + l2 * uv[1][1] + l3 * uv[2][1]) & 255
                    col = texel(vram, page, clut, u, v)
                    if col is None: col = (255, 0, 255)
                else:
                    col = shade
                zb[y][x] = z; px[x, y] = col
    return img


def render_model(blob, slot_off, slot, name, tex_blobs=(), trailing=None, player=False):
    vram = [0] * (1024 * 512)
    for tb in tex_blobs: upload_tims(tb, vram)
    upload_tims(blob, vram)
    md = model(blob, slot_off)
    if player:
        relocate(md, 0x3C0, 0x100, 0x1C0)
    elif trailing is not None and (trailing >> 8) & 0xF:
        relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
    rows = sorted([(s, off) for off, s, g in records(blob, 0x10) if g == slot])
    tr, ang = ([0, 0, 0], [])
    if rows:
        try: tr, ang = anim_frame(blob, rows[0][1], md['parts'])
        except Exception: pass
    W = pose(md, tr, ang)
    views = [render(md, W, vram, v) for v in ('front', 'side', 'back')]
    sheet = Image.new('RGB', (900, 300)); [sheet.paste(im, (300 * i, 0)) for i, im in enumerate(views) if im]
    path = os.path.join(OUT, name + '.png'); sheet.save(path); return path


if __name__ == '__main__':
    m, slot = int(sys.argv[1]), int(sys.argv[2])
    blob = room_blob(m)
    d = word(blob, 4); desc = word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = word(blob, at + 12 * i + 4)
        if w >> 24 == slot: off, trailing = w & 0xffffff, word(blob, at + 12 * i + 8)
    print(hex(trailing), render_model(blob, off, slot, 'm%03d_s%d' % (m, slot), trailing=trailing))
