"""Retarget prototype: play Aya's player animations on another character's skeleton (offline).

Every humanoid shares one body plan (hips -> chest -> arm / head / arm chains, hips -> pelvis -> two
legs) with different chain lengths. Aya's rotations are mapped chain by chain, index for index; a
target segment past the end of Aya's chain keeps the character's own idle angle; the root translation
is scaled by the leg-length ratio. Renders a grid: rows = Aya animation frames, columns = Aya and the
targets, to tools/pe_assets/renders/retarget_*.png (local only).

    PYTHONPATH=tools python tools/pe_assets/retarget.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
from PIL import Image, ImageDraw

AYA_AREA = 12   # jacket + jeans, 29 bones; per-day rows for this skeleton: image entries 31-38
TARGETS = [('Daniel', 25, 3), ('Maeda', 25, 4), ('Baker?', 41, 3), ('Maya', 11, 2)]


def tree(cmds):
    par, st, cur = {}, [], None
    for c in cmds:
        if c == -1: st.append(cur)
        elif c == -2: cur = st.pop()
        else: par[c] = cur; cur = c
    kids = {}
    for k in sorted(par):
        kids.setdefault(par[k], []).append(k)
    return kids


def chains(cmds):
    """{chain name: [part, ...]} for root, chest chains (armA, head, armB) and the two legs."""
    kids = tree(cmds)
    def run(n):
        out = [n]
        while len(kids.get(n, [])) == 1: n = kids[n][0]; out.append(n)
        return out
    root = kids[None][0]
    chest, pelvis = kids[root][0], kids[root][1]
    a, h, b = kids[chest][:3]
    l1, l2 = kids[pelvis][:2]
    return dict(root=[root], chest=[chest], pelvis=[pelvis], armA=run(a), head=run(h), armB=run(b), legA=run(l1), legB=run(l2))


def mapping(src_cmds, dst_cmds):
    s, d = chains(src_cmds), chains(dst_cmds)
    m = {}
    for k, parts in d.items():
        for i, p in enumerate(parts):
            if i < len(s[k]): m[p] = s[k][i]
    return m


import math

CORRECT = ('chest', 'pelvis', 'head', 'armA', 'armB')   # chain roots whose rest orientation may differ


def transpose(M): return [[M[j][i] for j in range(3)] for i in range(3)]


def to_yxz(M):
    """Inverse of RotMatrixYXZ (M = Ry*Rx*Rz) in 4096-per-turn units."""
    sx = max(-1.0, min(1.0, -M[1][2]))
    x = math.asin(sx)
    y = math.atan2(M[0][2], M[2][2])
    z = math.atan2(M[1][0], M[1][1])
    return [int(round(a * 4096 / (2 * math.pi))) & 4095 for a in (x, y, z)]


def corrections(src_cmds, dst_cmds, src_idle, dst_idle, joints=CORRECT):
    """{target part: delta matrix} so that R_target = R_aya @ delta keeps the target's own rest pose
    at the chain roots (delta = inv(R_aya_idle) @ R_target_idle)."""
    s, d = chains(src_cmds), chains(dst_cmds)
    out = {}
    for k in joints:
        sp, dp = s[k][0], d[k][0]
        if sp < len(src_idle) and dp < len(dst_idle):
            out[dp] = R.mm(transpose(R.rot_yxz(src_idle[sp])), R.rot_yxz(dst_idle[dp]))
    return out


def retarget_frame(ang, mp, idle, parts, corr=None):
    out = []
    for p in range(parts):
        if p in mp and mp[p] < len(ang):
            a = ang[mp[p]]
            if corr and p in corr: a = to_yxz(R.mm(R.rot_yxz(a), corr[p]))
            out.append(a)
        else:
            out.append(idle[p] if p < len(idle) else [0, 0, 0])
    return out


def aligned_mapping(src, dst):
    """Chain mapping aligned on the mesh: each chain's heaviest segment (most vertices: the hand on an
    arm, the skull on the head chain) lines up with Aya's, so a character whose upper-arm mesh sits one
    segment earlier (Daniel) still gets Aya's upper-arm motion on it."""
    s, d = chains(src['cmds']), chains(dst['cmds'])
    heavy = lambda md, ch: max(range(len(ch)), key=lambda i: md['ptab'][ch[i]][1])
    m = {}
    for k, parts in d.items():
        off = heavy(dst, parts) - heavy(src, s[k]) if k in ('armA', 'armB', 'head') else 0
        for i, p in enumerate(parts):
            j = i - off
            if 0 <= j < len(s[k]): m[p] = s[k][j]
    return m


def bone_lengths(md, chain):
    """Length of each chain segment = the next segment's offset (translation_z of its child)."""
    return [abs(md['ptab'][chain[i + 1]][3]) if i + 1 < len(chain) else 0 for i in range(len(chain))]


def label_chain(md, chain, kind):
    """Semantic labels for a chain: arm -> shoulder.. / upper / forearm / hand / finger..;
    head -> neck.. / skull / extra..; leg -> by index."""
    if kind == 'leg':
        return {i: ('leg', i) for i in range(len(chain))}
    verts = [md['ptab'][p][1] for p in chain]
    h = max(range(len(chain)), key=lambda i: verts[i])
    lab = {}
    if kind == 'head':
        for i in range(h): lab[i] = ('neck', i - h)          # aligned from the skull
        lab[h] = ('skull', 0)
        for i in range(h + 1, len(chain)): lab[i] = ('extra', i - h)
        return lab
    L = bone_lengths(md, chain)
    f = h - 1
    u = max(range(f), key=lambda i: (L[i], i)) if f > 0 else 0   # ties -> the later segment (Baker 86 / 86)
    for i in range(u): lab[i] = ('shoulder', i - u)           # aligned from the upper arm
    lab[u] = ('upper', 0)
    for i in range(u + 1, f): lab[i] = ('between', i - u)      # e.g. Maeda's elbow piece
    lab[f] = ('forearm', 0); lab[h] = ('hand', 0)
    for i in range(h + 1, len(chain)): lab[i] = ('finger', i - h)
    return lab


def semantic_mapping(src, dst):
    s, d = chains(src['cmds']), chains(dst['cmds'])
    m = {}
    for k, parts in d.items():
        kind = 'arm' if k.startswith('arm') else 'head' if k == 'head' else 'leg' if k.startswith('leg') else None
        if kind is None:
            m[parts[0]] = s[k][0]; continue
        sl = {v: i for i, v in label_chain(src, s[k], kind).items()}
        for i, lab in label_chain(dst, parts, kind).items():
            if lab in sl and lab[0] not in ('between', 'extra'): m[parts[i]] = s[k][sl[lab]]
    return m


def world_rotations(md, ang):
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; cur = I; st = []; out = {}; parent = {}
    last = None
    for c in md['cmds']:
        if c == -1: st.append((cur, last)); continue
        if c == -2: cur, last = st.pop(); continue
        parent[c] = last
        cur = R.mm(cur, R.rot_yxz(ang[c]) if c < len(ang) else I)
        out[c] = cur; last = c
    return out, parent


def retarget_world(src, ang, dst, mp, idle, shoulder=None, straight=None):
    """Target local angles that give each mapped target bone the world orientation of its Aya bone
    (unmapped bones keep the character's idle angle). `shoulder` {part: delta} re-bases shoulder joints
    on the character's own rest angle (R_world = R_aya_world @ delta)."""
    sw, _ = world_rotations(src, ang)
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    tw = {}; out = [None] * dst['parts']; parent = {}
    st = []; last = None
    for c in dst['cmds']:
        if c == -1: st.append(last); continue
        if c == -2: last = st.pop(); continue
        parent[c] = last; last = c
    for c in [x for x in dst['cmds'] if x >= 0]:
        pw = tw[parent[c]] if parent[c] is not None else I
        if c in mp and mp[c] in sw:
            want = sw[mp[c]]
            if shoulder and c in shoulder: want = R.mm(want, shoulder[c])
            local = R.mm(transpose(pw), want)
            out[c] = to_yxz(local)
        else:
            out[c] = [0, 0, 0] if c in (straight or ()) else (idle[c] if c < len(idle) else [0, 0, 0])
            local = R.rot_yxz(out[c])
        tw[c] = R.mm(pw, local)
    return out


def shoulder_deltas(src, dst, mp, src_idle, dst_idle):
    """Shoulder (first two arm segments) offsets between Aya's and the character's rest orientation,
    in world terms, from their idle frames."""
    sw, _ = world_rotations(src, src_idle); tw, _ = world_rotations(dst, dst_idle)
    d = chains(dst['cmds']); out = {}
    for k in ('armA', 'armB'):
        for p in d[k][:2]:
            if p in mp and mp[p] in sw and p in tw:
                out[p] = R.mm(transpose(sw[mp[p]]), tw[p])
    return out


def leg_length(md, cmds):
    c = chains(cmds)
    return sum(abs(md['ptab'][p][3]) for p in c['legA']) or 1


def main():
    aya_blob = R.image_blob(AYA_AREA + 8); aya_tex = R.image_blob(AYA_AREA + 3)
    aya = R.model(aya_blob, R.records(aya_blob, 0x0C)[0][0])
    aya_vram = [0] * (1024 * 512); R.upload_tims(aya_tex, aya_vram)
    rows = {s: (aya_blob, o) for o, s, g in R.records(aya_blob, 0x10)}
    day = R.image_blob(31 + 1)          # the 29-bone per-day rows (day 2), rows 4-12
    rows.update({s: (day, o) for o, s, g in R.records(day, 0x10)})
    aya_idle = R.anim_frame_at(*rows[0x15], 0)[1]      # the player's start-up action (row 0x15)
    targets = []
    for name, m, slot in TARGETS:
        blob = R.room_blob(m); vram = R.room_vram(m)
        d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
        for i in range(desc >> 22):
            w = R.word(blob, at + 12 * i + 4)
            if w >> 24 == slot: off, trailing = w & 0xffffff, R.word(blob, at + 12 * i + 8)
        md = R.model(blob, off)
        if (trailing >> 8) & 0xF: R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
        own = sorted([(s, o) for o, s, g in R.records(blob, 0x10) if g == slot])
        idle = R.anim_frame(blob, own[0][1], md['parts'])[1] if own else [[0, 0, 0]] * md['parts']
        mp = semantic_mapping(aya, md)
        print(name, 'unmapped parts', [p for p in range(md['parts']) if p not in mp])
        corr = shoulder_deltas(aya, md, mp, aya_idle, idle) if CORRECTED else None
        targets.append((name, md, vram, mp, idle, leg_length(md, md['cmds']) / leg_length(aya, aya['cmds']), corr))
        print(name, 'parts', md['parts'], 'mapped', len(targets[-1][3]), 'leg ratio %.2f' % targets[-1][5])
    R.NOTEX = False
    picks = [(s, f) for s in sorted(rows) for f in (0, None)]
    cell = 180; out = []
    for s, f in picks:
        blob, o = rows[s]; frames = blob[o + 2]
        f = frames // 2 if f is None else f
        if f == 0 and frames <= 1 and s != sorted(rows)[0]: continue
        tr, ang = R.anim_frame_at(blob, o, f)
        row = [R.render(aya, R.pose(aya, tr, ang), aya_vram, 'side', cell)]
        for name, md, vram, mp, idle, ratio, corr in targets:
            tang = retarget_world(aya, ang, md, mp, idle, corr, straight=set(range(md['parts'])) - set(mp))
            row.append(R.render(md, R.pose(md, [int(tr[0] * ratio), int(tr[1] * ratio), int(tr[2] * ratio)], tang), vram, 'side', cell))
        out.append(('row %d frame %d/%d' % (s, f, frames), row))
    for k in range(0, len(out), 8):
        chunk = out[k:k + 8]
        sheet = Image.new('RGB', (cell * (len(TARGETS) + 1), (cell + 16) * len(chunk)), (10, 10, 12))
        dr = ImageDraw.Draw(sheet)
        for j, (label, imgs) in enumerate(chunk):
            for i, im in enumerate(imgs):
                if im: sheet.paste(im, (cell * i, (cell + 16) * j + 16))
            dr.text((4, (cell + 16) * j + 2), label + '   |   Aya, ' + ', '.join(t[0] for t in TARGETS), fill=(255, 255, 0))
        p = os.path.join(R.OUT, 'retarget%s_%d.png' % ('_corrected' if CORRECTED else '', k // 8)); sheet.save(p); print(p)


CORRECTED = '--raw' not in sys.argv

if __name__ == '__main__':
    main()
