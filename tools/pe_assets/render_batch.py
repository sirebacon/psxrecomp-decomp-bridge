import os, json
exec(open(__file__.replace('render_batch', 'render_models')).read().split("if __name__ == '__main__':")[0])
from PIL import Image, ImageDraw

# Aya's outfits, textured from their own texture entry (bank + 3)
for area in range(10, 15):
    b = image_blob(area + 8); t = image_blob(area + 3)
    off = records(b, 0x0C)[0][0]
    vram = [0] * (1024 * 512); upload_tims(t, vram)
    md = model(b, off); relocate(md, 0x3C0, 0x100, 0x1C0)
    rows = sorted([(s, o) for o, s, g in records(b, 0x10)])
    row = dict(rows).get(0x15, rows[0][1])
    tr, ang = anim_frame(b, row, md['parts'])
    W = pose(md, tr, ang)
    sheet = Image.new('RGB', (900, 300)); [sheet.paste(render(md, W, vram, v), (300 * i, 0)) for i, v in enumerate(('front', 'side', 'back'))]
    sheet.save(os.path.join(OUT, 'aya_area%d.png' % area))

# The 11 meshes that share Aya's 23-part (area 11) skeleton, untextured
os.environ['NOTEX'] = '1'
globals()['NOTEX'] = True
picks = [(2, 2), (6, 2), (11, 2), (41, 3), (44, 4), (48, 2), (52, 3), (108, 2), (196, 2), (271, 2), (271, 4)]
tiles = []
for m, slot in picks:
    blob = room_blob(m)
    d = word(blob, 4); desc = word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = word(blob, at + 12 * i + 4)
        if w >> 24 == slot: off = w & 0xffffff
    md = model(blob, off)
    rows = sorted([(s, o) for o, s, g in records(blob, 0x10) if g == slot])
    tr, ang = anim_frame(blob, rows[0][1], md['parts']) if rows else ([0, 0, 0], [])
    W = pose(md, tr, ang)
    a, b2 = render(md, W, None, 'front', 240), render(md, W, None, 'side', 240)
    tile = Image.new('RGB', (480, 262), (20, 20, 24)); tile.paste(a, (0, 22)); tile.paste(b2, (240, 22))
    ImageDraw.Draw(tile).text((6, 4), 'map %d slot %d  (%d verts)' % (m, slot, len(md['V'])), fill=(255, 255, 0))
    tiles.append(tile)
sheet = Image.new('RGB', (960, 262 * ((len(tiles) + 1) // 2)), (0, 0, 0))
for i, t in enumerate(tiles): sheet.paste(t, (480 * (i % 2), 262 * (i // 2)))
sheet.save(os.path.join(OUT, 'aya11_skeleton_meshes.png'))
print('done')
