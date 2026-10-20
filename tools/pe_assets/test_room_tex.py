"""Render one room model textured from the room's own texture blobs (no save state)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
from PIL import Image

m, slot = int(sys.argv[1]), int(sys.argv[2])
blob = R.room_blob(m)
for b in R.room_texture_blobs(m):
    d = R.word(b, 4); desc = R.word(b, d + 0x28); at = desc & 0x3fffff
    rects = []
    for i in range(desc >> 22):
        r = at + 20 * i; rect = R.word(b, r + 8); src = R.word(b, r + 4)
        rects.append(((rect >> 10) & 0x7ff, rect >> 21, rect & 0x3ff, src >> 24 or 256))
    print('blob', len(b), 'tims', rects[:8])
vram = R.room_vram(m)
d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
for i in range(desc >> 22):
    w = R.word(blob, at + 12 * i + 4)
    if w >> 24 == slot: off, trailing = w & 0xffffff, R.word(blob, at + 12 * i + 8)
md = R.model(blob, off)
if (trailing >> 8) & 0xF: R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
rows = sorted([(s, o) for o, s, g in R.records(blob, 0x10) if g == slot])
tr, ang = R.anim_frame(blob, rows[0][1], md['parts']) if rows else ([0, 0, 0], [])
W = R.pose(md, tr, ang)
R.NOTEX = False
im = Image.new('RGB', (600, 300)); im.paste(R.render(md, W, vram, 'front'), (0, 0)); im.paste(R.render(md, W, vram, 'side'), (300, 0))
p = os.path.join(R.OUT, 'roomtex_m%03d_s%d.png' % (m, slot)); im.save(p); print(p)
