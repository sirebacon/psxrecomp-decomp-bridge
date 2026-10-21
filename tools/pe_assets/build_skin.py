"""Build a player skin bundle from a room character (offline, from the user's own disc).

Output (git-ignored, game-derived): tools/pe_assets/skins/<name>/
    model.bin     player bundle like PE image entry 20 (Aya, jacket): the character's model with its
                  texture moved to the player's slot, plus Aya's bundle animation rows (0-3, 13-23,
                  28) retargeted to the character's skeleton
    day1.bin..day8.bin   the per-day rows (4-12, entries 31-38) retargeted
    rooms.bin     the player rows rooms install (slots 24-47: door opening, room events), retargeted,
                  indexed by a fingerprint of Aya's original (see write_room_rows)
    texture.bin   player texture blob like entry 15: the character's page and palettes in the
                  player's slot (page x=960 y=256, palettes rows 448-449)
The mod hands these to the game instead of the disc's (Scene_LoadEntityTexture steps 3 / 6 and
Scene_LoadEntityTextures step 6). Validated by re-reading model.bin with the same decoders and
rendering frames (--check).

    PYTHONPATH=tools python tools/pe_assets/build_skin.py daniel 25 3 [--check]
    PYTHONPATH=tools python tools/pe_assets/build_skin.py --all
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
import retarget as T

AYA_AREA = 12
META_ONLY = '--meta' in sys.argv    # only meta.bin (gun part), keep the other files
LAYOUT = '--skin-layout' not in sys.argv   # renumber parts to Aya's (AyaLayout); --skin-layout keeps the skin's
HERE = os.path.dirname(__file__)
# The game reads pe_skins/<folder>/ beside its exe (pe_collection.c); folder names as in gen_collection_data.SKINS.
INSTALL_ROOT = os.path.join('D:' + os.sep, 'Recomp Games', 'Parasite Eve Project', 'parasite-eve-recomp', 'build-release', 'pe_skins')


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


def retarget_row(blob, off, aya, md, mp, idle, corr, ratio, layout=None):
    frames = max(1, blob[off + 2])
    hit_vals = struct.unpack_from('<4H', blob, off + 4)
    trs, angs = [], []
    for f in range(frames):
        tr, ang = R.anim_frame_at(blob, off, f)
        skin = T.retarget_world(aya, ang, md, mp, idle, corr, straight=T.straight_parts(md))
        angs.append(layout.angles(skin, ang) if layout else skin)
        trs.append([tr[0] * ratio, tr[1] * ratio, tr[2] * ratio])
    return encode_row(trs, angs, layout.n if layout else md['parts'], hit_vals)


FP_BYTES = 372      # every Aya row is at least this long (header 12 + 3 x 4 + 29 parts x 3 x 4)


def row_length(data, off=0):
    """Bytes a row occupies, walking its channels as Anim_DecodeBoneRotations* (render_models.anim_frame_at):
    a constant channel is 4 bytes, a sampled one ((frames >> 1) + 1) words (shorts) or
    ((frames >> 2) + 1) words (byte angles)."""
    flags, last, frames = data[off], data[off + 1], data[off + 2]
    stride = ((frames >> 1) + 1) * 4
    short = (flags & 3) == 2
    bstride = stride if short else ((frames >> 2) + 1) * 4
    cur = off + 12
    for _ in range(3):
        cur += 4 if R.s16(data, cur) else stride
    for _ in range((last + 1) * 3):
        cur += 4 if (R.s16(data, cur) if short else data[cur]) else bstride
    return cur - off


def fingerprint(data):
    """FNV-1a over a row's whole length, as pe_collection.c computes it from guest memory."""
    h = 0x811C9DC5
    for b in data[:row_length(data)]: h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


def room_player_rows():
    """Distinct player animation rows rooms install (bank_rows[0][24..47], Scene_LoadRoom row records
    with group 0: door opening, room events), both discs, by fingerprint. Cached in skins/."""
    import pickle
    cache = os.path.join(HERE, 'skins', 'room_rows.pkl')
    if os.path.exists(cache): return pickle.load(open(cache, 'rb'))
    rows = {}
    for disc in (1, 2):
        for m in range(1, 1000):
            try:
                b = R.room_blob(m, disc); recs = R.records(b, 0x10)
            except Exception:
                continue
            offs = sorted({o for o, s, g in recs}) + [len(b)]
            for o, s, g in recs:
                if g != 0 or not 24 <= s < 48: continue
                data = bytes(b[o:next(x for x in offs if x > o)])
                if len(data) < FP_BYTES: continue
                data = data[:row_length(data)]
                fp = fingerprint(data)
                if fp in rows and rows[fp] != data: print('  fingerprint collision %08X (room %d slot %d)' % (fp, m, s))
                rows.setdefault(fp, data)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    pickle.dump(rows, open(cache, 'wb'))
    return rows


def write_room_rows(path, rows, aya, md, mp, idle, corr, ratio, layout=None):
    """rooms.bin: 'PERR', count, then count x {fingerprint, offset, size} (offsets from the file
    start), then the retargeted rows."""
    items = sorted(rows.items())
    body = bytearray(); table = []
    head = 8 + 12 * len(items)
    for fp, data in items:
        out = retarget_row(data, 0, aya, md, mp, idle, corr, ratio, layout)
        table.append((fp, head + len(body), len(out))); body += out
        while len(body) % 4: body.append(0)
    open(path, 'wb').write(b'PERR' + struct.pack('<I', len(items)) +
                           b''.join(struct.pack('<III', *t) for t in table) + bytes(body))
    return len(items), head + len(body)


class AyaLayout:
    """Renumber a skin's parts to Aya's indices. Game code names Aya's parts by number: the weapon
    follows part 0x12 (right hand, second finger segment), muzzle / glow effects read matrices[19],
    head turns and anchors use others. Each skin part mapped to an Aya part moves to that index; an
    Aya part the skin lacks becomes a placeholder (no vertices, no hit sphere, Aya's bone offset and
    Aya's own animation) hung from its Aya parent; unmapped skin parts (extra pieces) follow after
    Aya's last index. Parts keep their own vertex ranges (the game reads each part's vertex_start),
    and mapped / extra parts keep the skin's hierarchy, so only the part table, the per-part bounds,
    the matrix commands, the anchor index and the animation channel order change."""

    def __init__(self, aya, md, mp):
        self.n_aya = aya['parts']
        self.aya_parent = parents(aya['cmds'])
        skin_parent = parents(md['cmds'])
        by_aya = {a: s for s, a in mp.items() if a < self.n_aya}
        extras = [s for s in range(md['parts']) if s not in mp or mp[s] >= self.n_aya]
        self.src = []                       # new index -> ('skin', old) | ('aya', aya index)
        for a in range(self.n_aya):
            self.src.append(('skin', by_aya[a]) if a in by_aya else ('aya', a))
        for s in extras: self.src.append(('skin', s))
        self.new_of = {old: i for i, (k, old) in enumerate(self.src) if k == 'skin'}
        self.parent = []
        for i, (k, v) in enumerate(self.src):
            if k == 'skin':
                p = skin_parent[v]
                self.parent.append(None if p is None else self.new_of[p])
            else:
                p = self.aya_parent[v]
                self.parent.append(None if p is None else p)   # Aya parent's new index == its Aya index
        self.aya_tz = {a: aya['ptab'][a][3] for a in range(self.n_aya)}
        self.n = len(self.src)

    def commands(self):
        kids = {i: [] for i in range(self.n)}
        for i, p in enumerate(self.parent):
            if p is not None: kids[p].append(i)
        out = []
        def emit(i):
            out.append(i)
            ks = kids[i]
            for k in ks[:-1]: out.append(-1); emit(k); out.append(-2)
            if ks: emit(ks[-1])
        emit(0)
        if len([c for c in out if c >= 0]) != self.n: raise ValueError('hierarchy does not reach every part')
        return out

    def angles(self, skin_ang, aya_ang):
        return [skin_ang[v] if k == 'skin' else aya_ang[v] for k, v in self.src]

    def model(self, raw, md):
        """Rewrite a model block (header .. UV records) in the new part order."""
        parts, verts = raw[2], R.u16(raw, 6)
        pk = [R.u16(raw, 8 + 2 * k) for k in range(4)]
        mcb = R.u16(raw, 0x18)
        at = 0x1C
        ptab = [raw[at + 12 * i: at + 12 * i + 12] for i in range(parts)]; at += 12 * parts
        geo_start = at; at += 8 * verts + 4 * verts + 12 * sum(pk); geo = raw[geo_start:at]
        sec14 = raw[at:at + 16]; at += 16
        bounds = [raw[at + 16 * i: at + 16 * i + 16] for i in range(parts)]; at += 16 * parts
        proj = raw[at:at + 8]; at += 8
        at += (mcb + 3) // 4 * 4
        uvs = raw[at:]
        new_ptab, new_bounds = [], []
        for k, v in self.src:
            if k == 'skin':
                new_ptab.append(ptab[v]); new_bounds.append(bounds[v])
            else:   # placeholder: no vertices, visible (as Aya's parts), Aya's bone offset, no hit sphere
                new_ptab.append(struct.pack('<HHBxxxi', 0, 0, 1, self.aya_tz[v]))
                new_bounds.append(struct.pack('<hhhhhhhh', 0, 0, 0, 0, 0, 0, 0, -1))
        cmds = self.commands()
        cbytes = struct.pack('<%db' % len(cmds), *cmds)
        while len(cbytes) % 4: cbytes += b'\0'
        head = bytearray(raw[:0x1C])
        head[2] = self.n
        anchor = R.u16(raw, 0x12)
        struct.pack_into('<H', head, 0x12, self.new_of.get(anchor, anchor))
        struct.pack_into('<H', head, 0x18, len(cmds))
        return bytes(head) + b''.join(new_ptab) + geo + sec14 + b''.join(new_bounds) + proj + cbytes + uvs


def parents(cmds):
    """Parent of each part from the matrix command list (-1 push, -2 pop)."""
    par, stack, cur = {}, [], None
    for c in cmds:
        if c == -1: stack.append(cur); continue
        if c == -2: cur = stack.pop(); continue
        par[c] = cur; cur = c
    return par


def gun_part(mp):
    """The skin part the weapon model follows. The game attaches it (g_GameState.scene_object,
    animation_state 3) to the player's part 0x12 = Aya's right hand, second finger segment
    (room_load.c Scene_LoadEntityTextures). With AyaLayout every skin has a part 0x12 (its own or a
    placeholder), so this is 0x12; without it, the skin's part mapped from 18 / 17 / 16."""
    if LAYOUT: return 0x12
    for aya_part in (18, 17, 16):
        hit = sorted(d for d, s in mp.items() if s == aya_part)
        if hit: return hit[0]
    return 0x12


def write_meta(out_dir, mp):
    """meta.bin: 'PEMT', u32 gun part (pe_collection.c sets the weapon's animation_id to it)."""
    g = gun_part(mp)
    open(os.path.join(out_dir, 'meta.bin'), 'wb').write(b'PEMT' + struct.pack('<I', g))
    return g


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
    if '--all' in sys.argv:            # every character skin in gen_collection_data.SKINS that fits
        from gen_collection_data import SKINS
        for n, p, k, a, folder, src in SKINS:
            if k != 1 or folder == 'eve': continue
            try: build(folder, src[0], src[1])
            except Exception as e: print(folder, 'FAILED', e)
        return
    build(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))


def build(name, m, slot):
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

    layout = AyaLayout(aya, md, mp) if LAYOUT else None
    if layout: raw = bytearray(layout.model(bytes(raw), md))
    print(name, 'parts', md['parts'], '->', layout.n if layout else md['parts'], 'mapped', len(mp), 'leg ratio %.2f' % ratio, 'model bytes', len(raw),
          'gun part', write_meta(out_dir, mp))
    if META_ONLY:
        install(out_dir, name); return
    rows = [(retarget_row(aya_blob, o, aya, md, mp, idle, corr, ratio, layout), s) for s, o in sorted(aya_rows.items())]
    bundle = write_blob([(bytes(raw), 0, aya_trailing)], rows)
    open(os.path.join(out_dir, 'model.bin'), 'wb').write(bundle)
    print('  model.bin', len(bundle), 'bytes (Aya entry 20:', len(aya_blob), ')')
    for day in range(1, 9):
        dblob = R.image_blob(0x16 + 8 + day)
        drows = [(retarget_row(dblob, o, aya, md, mp, idle, corr, ratio, layout), s) for o, s, g in R.records(dblob, 0x10)]
        d_out = write_blob([], drows)
        open(os.path.join(out_dir, 'day%d.bin' % day), 'wb').write(d_out)
    print('  day1..8.bin', len(d_out), 'bytes each (last)')
    n_rr, size_rr = write_room_rows(os.path.join(out_dir, 'rooms.bin'), room_player_rows(), aya, md, mp, idle, corr, ratio, layout)
    print('  rooms.bin', n_rr, 'room animations,', size_rr, 'bytes')

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
    install(out_dir, name)


def install(out_dir, name):
    dest = os.path.join(INSTALL_ROOT, name)
    if os.path.isdir(INSTALL_ROOT.rsplit(os.sep, 1)[0]):
        import shutil
        os.makedirs(dest, exist_ok=True)
        for f in os.listdir(out_dir): shutil.copy2(os.path.join(out_dir, f), os.path.join(dest, f))
        print('  installed', dest)


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
