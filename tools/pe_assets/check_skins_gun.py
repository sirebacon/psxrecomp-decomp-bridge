"""Every installed skin: are Aya's hand / finger parts (16-19) real or placeholders, and how far do the
weapon point (part 18 origin) and muzzle point (part 19 origin) sit from the skin's hand mesh across the
bundle animations, against Aya's own numbers. Writes a contact sheet with the two points marked."""
import os, sys, math
sys.path.insert(0, r"D:\Recomp Games\psxrecomp-decomp-bridge\tools")
sys.path.insert(0, r"D:\Recomp Games\psxrecomp-decomp-bridge\tools\pe_assets")
import render_models as R
from gen_collection_data import SKINS
from PIL import Image, ImageDraw

ROOT = r"D:\Recomp Games\Parasite Eve Project\parasite-eve-recomp\build-release\pe_skins"
I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

def mats(md, tr, ang):
    cur = (I, [0, 0, 0]); stack = []; out = {}
    for c in md['cmds']:
        if c == -1: stack.append(cur); continue
        if c == -2: cur = stack.pop(); continue
        Rm = R.rot_yxz(ang[c]) if c < len(ang) else I
        nr = R.mm(cur[0], Rm)
        vec = tr if c == 0 else [0, 0, md['ptab'][c][3]]
        nt = [a + b for a, b in zip(R.mv(cur[0], vec), cur[1])]
        out[c] = (nr, nt); cur = (nr, nt)
    return out

def hand_dist(md, rows, blob):
    """mean / max distance (over sampled frames of every bundle row) from part 18 and 19 origins to the
    nearest vertex of the real parts among 16-19."""
    real = [p for p in (16, 17, 18, 19) if p < md['parts'] and md['ptab'][p][1] > 0]
    d18, d19 = [], []
    for s, o in rows.items():
        n = max(1, blob[o + 2])
        for f in range(0, n, max(1, n // 4)):
            tr, ang = R.anim_frame_at(blob, o, f)
            M = mats(md, tr, ang); W = R.pose(md, tr, ang)
            verts = [W[i] for p in real for i in range(md['ptab'][p][0], md['ptab'][p][0] + md['ptab'][p][1]) if i < len(W) and W[i]]
            if not verts: continue
            for part, acc in ((18, d18), (19, d19)):
                if part in M:
                    q = M[part][1]
                    acc.append(min(math.dist(q, v) for v in verts))
    m = lambda a: (sum(a) / len(a), max(a)) if a else (float('nan'), float('nan'))
    return real, m(d18), m(d19)

def load(path):
    b = open(path, 'rb').read()
    off = R.records(b, 0x0C)[0][0]
    return b, R.model(b, off), {s: o for o, s, g in R.records(b, 0x10)}

# Aya baseline
ab = R.image_blob(12 + 8); ao = R.records(ab, 0x0C)[0][0]; aya = R.model(ab, ao)
arows = {s: o for o, s, g in R.records(ab, 0x10)}
real, a18, a19 = hand_dist(aya, arows, ab)
print('%-16s parts %2d  real hand parts %-16s  gun %5.0f / %5.0f   muzzle %5.0f / %5.0f' % ('AYA', aya['parts'], real, *a18, *a19))

sheet_items = []
for n, p, k, a, folder, src in SKINS:
    if k != 1 or folder == 'eve': continue
    path = os.path.join(ROOT, folder, 'model.bin')
    if not os.path.exists(path): print(folder, 'missing'); continue
    b, md, rows = load(path)
    real, g, mz = hand_dist(md, rows, b)
    flag = ''
    if not math.isnan(g[0]) and (g[0] > a18[0] * 2 + 40 or mz[0] > a19[0] * 2 + 40): flag = '  <-- check'
    print('%-16s parts %2d  real hand parts %-16s  gun %5.0f / %5.0f   muzzle %5.0f / %5.0f%s' % (folder, md['parts'], real, *g, *mz, flag))
    sheet_items.append((folder, b, md, rows))

# contact sheet: aim-ish pose (row 16 frame 9), side view, part 18 (red) and 19 (yellow)
def project(W, size, pts):
    P = [(w[2], -w[1]) if w else None for w in W]          # 'side' view, as R.render
    xs = [q[0] for q in P if q]; ys = [q[1] for q in P if q]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1; sc = (size - 20) / span
    ox, oy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return [((q[2] - ox) * sc + size / 2, (oy - (-q[1])) * sc + size / 2) for q in pts]

cell = 170; cols = 7
rowsN = (len(sheet_items) + cols - 1) // cols
sheet = Image.new('RGB', (cell * cols, (cell + 16) * rowsN), (10, 10, 12)); dr = ImageDraw.Draw(sheet)
R.NOTEX = True
for i, (folder, b, md, rows) in enumerate(sheet_items):
    if 16 not in rows: continue
    tr, ang = R.anim_frame_at(b, rows[16], 9)
    W = R.pose(md, tr, ang); M = mats(md, tr, ang)
    im = R.render(md, W, None, 'side', cell)
    x0, y0 = (i % cols) * cell, (i // cols) * (cell + 16)
    if im: sheet.paste(im, (x0, y0 + 16))
    marks = project(W, cell, [M[18][1], M[19][1]])
    for (x, y), col in zip(marks, ((255, 40, 40), (255, 230, 0))):
        dr.ellipse((x0 + x - 3, y0 + 16 + y - 3, x0 + x + 3, y0 + 16 + y + 3), fill=col)
    dr.text((x0 + 3, y0 + 2), folder, fill=(255, 255, 0))
out = os.path.join(r"D:\Recomp Games\psxrecomp-decomp-bridge\tools\pe_assets\renders", 'skins_gun_check.png')
sheet.save(out); print('sheet', out)
