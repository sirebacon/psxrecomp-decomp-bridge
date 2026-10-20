"""Build a player skin bundle from a room character (offline, from the user's own disc).

Output (git-ignored, game-derived): tools/pe_assets/skins/<name>/
    model.bin     player bundle like PE image entry 20 (Aya, jacket): the character's model with its
                  texture moved to the player's slot, plus Aya's bundle animation rows (0-3, 13-23,
                  28) retargeted to the character's skeleton
    day1.bin..day8.bin   the per-day rows (4-12, entries 31-38) retargeted
    texture.bin   player texture blob like entry 15: the character's page and palettes in the
                  player's slot (page x=960 y=256, palettes rows 448-449)
The mod hands these to the game instead of the disc's (Scene_LoadEntityTexture steps 3 / 6 and
Scene_LoadEntityTextures step 6). Validated by re-reading model.bin with the same decoders and
rendering frames (--check).

    PYTHONPATH=tools python tools/pe_assets/build_skin.py daniel 25 3 [--check]
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
import retarget as T

AYA_AREA = 12
HERE = os.path.dirname(__file__)


def model_extent(blob, off):
    """Byte length of a model block (header .. last UV record), as Render_SetupEntityPrims walks it."""
    parts, verts = blob[off + 2], R.u16(blob, off + 6)
    pk = [R.u16(blob, off + 8 + 2 * k) for k in range(4)]
    mcb = R.u16(blob, off + 0x18)
    at = 0x1C + 12 * parts + 8 * verts + 4 * verts + 12 * sum(pk) + (2 + 2 * parts + 1) * 8
    at += (mcb + 3) // 4 * 4
    return at + 16 * pk[0] + 12 * pk[1], at          # end, start of the UV records


def repack_texture(md, vram):
    """Move the model's texture to the player's slot. Returns (image 64x255 halfwords, palettes
    256x2 halfwords, rewritten UV list)."""
    pages = {t[5] & 0x1FF for t in md['T']}
    if len(pages) != 1: raise ValueError('needs one texture page, has %s' % sorted(pages))
    page = pages.pop()
    if (page >> 7) & 3: raise ValueError('only 4-bit pages')
    px, py = (page & 15) * 64, ((page >> 4) & 1) * 256
    image = [vram[(py + y) * 1024 + px + x] for y in range(255) for x in range(64)]
    cluts = sorted({t[2] for t in md['T']})
    if len(cluts) > 32: raise ValueError('more than 32 palettes')
    pal = [0] * 512; remap = {}
    for i, c in enumerate(cluts):
        cx, cy = (c & 63) * 16, (c >> 6) & 511
        for k in range(16): pal[(i // 16) * 256 + (i % 16) * 16 + k] = vram[cy * 1024 + cx + k]
        remap[c] = ((448 + i // 16) << 6) | ((i % 16) * 16 >> 4)
    T2 = []
    for t in md['T']:
        t = list(t); t[2] = remap[t[2]]; t[5] = (t[5] & ~0x1FF) | 31     # page 31 = x960 y256, 4-bit
        T2.append(t)
    return image, pal, T2


def encode_row(frames_tr, frames_ang, parts, hit_vals):
    """RenderAnimationDataHeader + channels, byte angles (encoding 1): translation channels are
    halfwords, angle channels bytes (x16); a channel whose samples are all equal is stored constant."""
    n = len(frames_ang)
    out = bytearray(struct.pack('<BBBBHHHH', 1, parts - 1, n, 0, *hit_vals))
    def chan_short(vals):
        if all(v == vals[0] for v in vals): return struct.pack('<hh', 1, vals[0])
        body = struct.pack('<h', 0) + b''.join(struct.pack('<h', v) for v in vals)
        size = ((n >> 1) + 1) * 4
        return body.ljust(size, b'\0')
    def chan_byte(vals):
        if all(v == vals[0] for v in vals): return bytes([1, vals[0], 0, 0])
        body = bytes([0]) + bytes(vals)
        size = ((n >> 2) + 1) * 4
        return body.ljust(size, b'\0')
    for axis in range(3):
        out += chan_short([max(-32768, min(32767, int(f[axis]))) for f in frames_tr])
    for b in range(parts):
        for axis in range(3):
            out += chan_byte([((int(f[b][axis]) + 8) // 16) & 255 for f in frames_ang])
    while len(out) % 4: out.append(0)
    return bytes(out)


def retarget_row(blob, off, aya, md, mp, idle, corr, ratio):
    frames = max(1, blob[off + 2])
    hit_vals = struct.unpack_from('<4H', blob, off + 4)
    trs, angs = [], []
    for f in range(frames):
        tr, ang = R.anim_frame_at(blob, off, f)
        angs.append(T.retarget_world(aya, ang, md, mp, idle, corr, straight=set(range(md['parts'])) - set(mp)))
        trs.append([tr[0] * ratio, tr[1] * ratio, tr[2] * ratio])
    return encode_row(trs, angs, md['parts'], hit_vals)


def write_blob(entries_models, entries_rows, tims=()):
    """SceneAssetBlob: data, then a 13-word directory (bankRootEntries +0x0C, bankRowEntries +0x10,
    timEntries +0x28; offset | count << 22), then the record tables."""
    data = bytearray(8)
    recs_m, recs_r = [], []
    for raw, slot, trailing in entries_models:
        off = len(data); data += raw
        while len(data) % 4: data.append(0)
        recs_m.append((len(raw), off | (slot << 24), trailing))
    for raw, rid in entries_rows:
        off = len(data); data += raw
        while len(data) % 4: data.append(0)
        recs_r.append((len(raw), off | (rid << 24), 0))
    dir_off = len(data)
    tables = dir_off + 13 * 4
    at_m = tables; at_r = at_m + 12 * len(recs_m); end = at_r + 12 * len(recs_r)
    words = [0, end, end, at_m | (len(recs_m) << 22), at_r | (len(recs_r) << 22)] + [end] * 8
    data += b''.join(struct.pack('<I', w) for w in words)
    for r in recs_m + recs_r: data += struct.pack('<III', *r)
    struct.pack_into('<II', data, 0, end, dir_off)
    return bytes(data)


def main():
    name, m, slot = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    out_dir = os.path.join(HERE, 'skins', name); os.makedirs(out_dir, exist_ok=True)
    aya_blob = R.image_blob(AYA_AREA + 8)
    aya_off, _, aya_trailing = R.records(aya_blob, 0x0C)[0]
    aya = R.model(aya_blob, aya_off)
    aya_rows = {s: o for o, s, g in R.records(aya_blob, 0x10)}
    aya_idle = R.anim_frame_at(aya_blob, aya_rows[0x15], 0)[1]

    blob = R.room_blob(m); vram = R.room_vram(m)
    d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = R.word(blob, at + 12 * i + 4)
        if w >> 24 == slot: off, trailing = w & 0xffffff, R.word(blob, at + 12 * i + 8)
    md = R.model(blob, off)
    if (trailing >> 8) & 0xF:
        R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
    own = sorted([(s, o) for o, s, g in R.records(blob, 0x10) if g == slot])
    idle = R.anim_frame_at(blob, own[0][1], 0)[1] if own else [[0, 0, 0]] * md['parts']
    mp = T.semantic_mapping(aya, md)
    corr = T.shoulder_deltas(aya, md, mp, aya_idle, idle)
    ratio = T.leg_length(md, md['cmds']) / T.leg_length(aya, aya['cmds'])

    # model bytes with the texture moved to the player's slot
    image, pal, T2 = repack_texture(md, vram)
    end, uv_at = model_extent(blob, off)
    raw = bytearray(blob[off:off + end])
    pos = uv_at
    for i, t in enumerate(T2):
        if i < md['pk'][0]: struct.pack_into('<BBHBBHBBHBBH', raw, pos, *t); pos += 16
        else: struct.pack_into('<BBHBBHBBH', raw, pos, *t); pos += 12

    print(name, 'parts', md['parts'], 'mapped', len(mp), 'leg ratio %.2f' % ratio, 'model bytes', len(raw))
    rows = [(retarget_row(aya_blob, o, aya, md, mp, idle, corr, ratio), s) for s, o in sorted(aya_rows.items())]
    bundle = write_blob([(bytes(raw), 0, aya_trailing)], rows)
    open(os.path.join(out_dir, 'model.bin'), 'wb').write(bundle)
    print('  model.bin', len(bundle), 'bytes (Aya entry 20:', len(aya_blob), ')')
    for day in range(1, 9):
        dblob = R.image_blob(0x16 + 8 + day)
        drows = [(retarget_row(dblob, o, aya, md, mp, idle, corr, ratio), s) for o, s, g in R.records(dblob, 0x10)]
        d_out = write_blob([], drows)
        open(os.path.join(out_dir, 'day%d.bin' % day), 'wb').write(d_out)
    print('  day1..8.bin', len(d_out), 'bytes each (last)')

    # texture blob: Aya's entry-15 blob with the image and palette pixels replaced in place
    tex = bytearray(R.image_blob(AYA_AREA + 3))
    td = R.word(tex, 4); tdesc = R.word(tex, td + 0x28); tat = tdesc & 0x3fffff
    for i in range(tdesc >> 22):
        r = tat + 20 * i
        src = R.word(tex, r + 4); rect = R.word(tex, r + 8); sec = R.word(tex, r + 12); rect2 = R.word(tex, r + 16)
        x, y, w, h = (rect >> 10) & 0x7ff, rect >> 21, rect & 0x3ff, src >> 24 or 256
        if (x, y, w) == (960, 256, 64):
            o = src & 0xffffff
            for k, v in enumerate(image[:w * h]): struct.pack_into('<H', tex, o + 2 * k, v)
        if (x, y, w) == (0, 448, 256):
            o = src & 0xffffff
            for k, v in enumerate(pal[:w * h]): struct.pack_into('<H', tex, o + 2 * k, v)
        if sec & 0xffffff:
            x2, y2, w2, h2 = (rect2 >> 10) & 0x7ff, rect2 >> 21, rect2 & 0x3ff, sec >> 24
            if (x2, y2, w2) == (0, 448, 256):
                o = (src & 0xffffff) + (sec & 0xffffff)
                for k, v in enumerate(pal[:w2 * h2]): struct.pack_into('<H', tex, o + 2 * k, v)
    open(os.path.join(out_dir, 'texture.bin'), 'wb').write(bytes(tex))
    print('  texture.bin', len(tex), 'bytes')
    if '--check' in sys.argv: check(out_dir, name)


def check(out_dir, name):
    """Round trip: decode model.bin / texture.bin with the renderer and draw a few frames."""
    from PIL import Image, ImageDraw
    b = open(os.path.join(out_dir, 'model.bin'), 'rb').read()
    t = open(os.path.join(out_dir, 'texture.bin'), 'rb').read()
    off = R.records(b, 0x0C)[0][0]
    md = R.model(b, off)
    vram = [0] * (1024 * 512); R.upload_tims(t, vram)
    rows = {s: o for o, s, g in R.records(b, 0x10)}
    R.NOTEX = False
    picks = [(0x15, 0), (0, 10), (13, 8), (14, 30), (16, 9), (22, 20)]
    sheet = Image.new('RGB', (200 * len(picks), 220), (10, 10, 12)); dr = ImageDraw.Draw(sheet)
    for i, (s, f) in enumerate(picks):
        if s not in rows: continue
        tr, ang = R.anim_frame_at(b, rows[s], f)
        im = R.render(md, R.pose(md, tr, ang), vram, 'side', 200)
        if im: sheet.paste(im, (200 * i, 20))
        dr.text((200 * i + 4, 4), 'row %d f%d' % (s, f), fill=(255, 255, 0))
    p = os.path.join(R.OUT, 'skin_%s_check.png' % name); sheet.save(p); print('  check', p)


if __name__ == '__main__':
    main()
