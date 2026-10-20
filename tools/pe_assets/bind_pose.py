"""Render Aya and the retarget targets at the bind pose (all bone angles zero) and at Aya's row 13."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
import retarget as T
from PIL import Image, ImageDraw

aya_blob = R.image_blob(T.AYA_AREA + 8); aya = R.model(aya_blob, R.records(aya_blob, 0x0C)[0][0])
aya_vram = [0] * (1024 * 512); R.upload_tims(R.image_blob(T.AYA_AREA + 3), aya_vram)
rows = {s: (aya_blob, o) for o, s, g in R.records(aya_blob, 0x10)}
models = [('Aya', aya, aya_vram)]
for name, m, slot in T.TARGETS:
    blob = R.room_blob(m); vram = R.room_vram(m)
    d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = R.word(blob, at + 12 * i + 4)
        if w >> 24 == slot: off, trailing = w & 0xffffff, R.word(blob, at + 12 * i + 8)
    md = R.model(blob, off)
    if (trailing >> 8) & 0xF: R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
    models.append((name, md, vram))
R.NOTEX = False
cell = 170
sheet = Image.new('RGB', (cell * len(models), (cell + 14) * 4), (10, 10, 12)); dr = ImageDraw.Draw(sheet)
for j, (label, view) in enumerate((('bind front', 'front'), ('bind side', 'side'))):
    for i, (name, md, vram) in enumerate(models):
        im = R.render(md, R.pose(md, [0, 0, 0], [[0, 0, 0]] * md['parts']), vram, view, cell)
        if im: sheet.paste(im, (cell * i, (cell + 14) * j + 14))
    dr.text((4, (cell + 14) * j + 1), label + ': ' + ', '.join(m[0] for m in models), fill=(255, 255, 0))
tr, ang = R.anim_frame_at(*rows[13], 0)
for j, view in ((2, 'front'), (3, 'side')):
    for i, (name, md, vram) in enumerate(models):
        a = ang if name == 'Aya' else T.retarget_frame(ang, T.mapping(aya['cmds'], md['cmds']), [[0, 0, 0]] * md['parts'], md['parts'])
        im = R.render(md, R.pose(md, tr, a), vram, view, cell)
        if im: sheet.paste(im, (cell * i, (cell + 14) * j + 14))
    dr.text((4, (cell + 14) * j + 1), 'row 13 frame 0 ' + view, fill=(255, 255, 0))
p = os.path.join(R.OUT, 'bind_pose.png'); sheet.save(p); print(p)
for name, md, vram in models:
    c = T.chains(md['cmds'])
    print(name, {k: [md['ptab'][q][3] for q in v] for k, v in c.items() if k in ('chest', 'armA', 'head', 'armB', 'legA')})
