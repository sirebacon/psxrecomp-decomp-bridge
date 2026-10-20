import os, glob, json
exec(open(__file__.replace('render_saves', 'render_models')).read().split("if __name__ == '__main__':")[0])
exec(open(__file__.replace('render_saves', 'pst_vram')).read().split("if __name__ == '__main__':")[0])
from PIL import Image, ImageDraw
sk = json.load(open(__file__.replace('render_saves.py', 'probe_skeletons.json')))
aya11 = sk['aya']['11']['cmds']
saves = {}
for p in sorted(glob.glob(r'D:/Recomp Games/**/*.pst', recursive=True)):
    try:
        m, _ = map_of(sections(p)[2])
        if m and m not in saves: saves[m] = p
    except Exception: pass
tiles = []
for m, p in sorted(saves.items()):
    vram = vram_of(p)
    blob = room_blob(m)
    d = word(blob, 4); desc = word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = word(blob, at + 12 * i + 4); off, slot = w & 0xffffff, w >> 24; trailing = word(blob, at + 12 * i + 8)
        md = model(blob, off)
        if blob[off + 2] < 15: continue
        if (trailing >> 8) & 0xF: relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
        rows = sorted([(s, o) for o, s, g in records(blob, 0x10) if g == slot])
        try: tr, ang = anim_frame(blob, rows[0][1], md['parts']) if rows else ([0, 0, 0], [])
        except Exception: tr, ang = [0, 0, 0], []
        W = pose(md, tr, ang)
        a, b2 = render(md, W, vram, 'front', 220), render(md, W, vram, 'side', 220)
        if not a: continue
        tile = Image.new('RGB', (440, 242), (20, 20, 24)); tile.paste(a, (0, 22)); tile.paste(b2, (220, 22))
        tag = ' AYA-SKELETON' if md['cmds'] == aya11 else ''
        ImageDraw.Draw(tile).text((6, 4), 'map %d slot %d  %d parts %d verts%s' % (m, slot, md['parts'], len(md['V']), tag), fill=(255, 255, 0))
        tiles.append(tile)
print(len(tiles), 'models from', len(saves), 'save maps')
per = 12
for k in range(0, len(tiles), per):
    chunk = tiles[k:k + per]
    sheet = Image.new('RGB', (880, 242 * ((len(chunk) + 1) // 2)))
    for i, t in enumerate(chunk): sheet.paste(t, (440 * (i % 2), 242 * (i // 2)))
    sheet.save(os.path.join(OUT, 'saves_sheet_%d.png' % (k // per)))
