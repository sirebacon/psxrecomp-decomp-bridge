"""Catalog every Bestiary creature's 3D model: disc location, skeleton, and a local render.

Joins findings/data/pe-bestiary-draft-2026-10-19.json (stat blocks with their room / actor) to the
room model whose bank slot is that actor. Writes findings/data/pe-enemy-model-catalog-2026-10-19.json
and findings/pe-enemy-model-catalog-2026-10-19.md (locations and metadata only), and renders each
distinct mesh to tools/pe_assets/renders/enemies/ (local only, git-ignored): shaded geometry, plus a
textured view when a save state in one of its rooms holds the textures in VRAM.

    PYTHONPATH=tools python tools/pe_assets/catalog_enemies.py [--no-render]
"""
import glob, json, os, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import render_models as R  # noqa: E402
from pst_vram import map_of, sections, vram_of  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / 'findings/data/pe-bestiary-draft-2026-10-19.json'
OUT_JSON = ROOT / 'findings/data/pe-enemy-model-catalog-2026-10-19.json'
OUT_MD = ROOT / 'findings/pe-enemy-model-catalog-2026-10-19.md'
RENDERS = Path(__file__).resolve().parent / 'renders' / 'enemies'


def room_models(m, cache={}):
    if m not in cache:
        blob = R.room_blob(m)
        d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
        packed = R.word(R.ram, 0x9337c + (m - 1) * 8); start = R.word(R.ram, 0x93378 + (m - 1) * 8)
        lba = R.BASE + start + (packed & 255) + ((packed >> 8) & 4095)
        slots = {}
        for i in range(desc >> 22):
            w = R.word(blob, at + 12 * i + 4)
            slots[w >> 24] = (w & 0xffffff, R.word(blob, at + 12 * i + 8))
        cache[m] = (blob, lba, slots)
    return cache[m]


def mesh_key(blob, off):
    md = R.model(blob, off)
    return (blob[off + 2], len(md['V']), tuple(md['cmds']), tuple(p[3] for p in md['ptab'])), md


def render_mesh(m, slot, label, path, vram=None):
    blob, lba, slots = room_models(m)
    off, trailing = slots[slot]
    md = R.model(blob, off)
    if vram is not None and (trailing >> 8) & 0xF:
        R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
    rows = sorted([(s, o) for o, s, g in R.records(blob, 0x10) if g == slot])
    try: tr, ang = R.anim_frame(blob, rows[0][1], md['parts']) if rows else ([0, 0, 0], [])
    except Exception: tr, ang = [0, 0, 0], []
    W = R.pose(md, tr, ang)
    R.NOTEX = vram is None
    views = [R.render(md, W, vram, v, 240) for v in ('front', 'side')]
    if not views[0]: return False
    img = Image.new('RGB', (480, 262), (20, 20, 24))
    for i, v in enumerate(views): img.paste(v, (240 * i, 22))
    ImageDraw.Draw(img).text((6, 4), label, fill=(255, 255, 0))
    img.save(path); return True


def main(render=True):
    draft = json.loads(DRAFT.read_text())['enemies']
    meshes = {}; rows = []; missing = []
    for e in draft:
        if e['role'] == 'helper' and not e.get('name'): continue
        for s in e['sources']:
            blob, lba, slots = room_models(s['map'])
            if s['actor'] not in slots: missing.append((e.get('name'), e['id'], s['map'], s['actor'])); continue
            off, _ = slots[s['actor']]
            key, md = mesh_key(blob, off)
            mid = meshes.setdefault(key, dict(id='mesh%03d' % len(meshes), parts=key[0], verts=key[1], names=set(), maps=set(),
                                              first=(s['map'], s['actor'], lba, off)))
            if e.get('name'): mid['names'].add(e['name'])
            mid['maps'].add(s['map'])
            rows.append(dict(name=e.get('name'), enemy_id=e['id'], hp=e['hp'], stats_first_seen=e['first'], map=s['map'], actor=s['actor'],
                             mesh=mid['id'], parts=key[0], verts=key[1], room_lba=lba, offset=off,
                             sector=lba + off // 2048, byte=off % 2048, disc=s['disc']))
    # one render per mesh; textured too when a save state was made in one of its rooms
    saves = {}
    for p in sorted(glob.glob(r'D:/Recomp Games/**/*.pst', recursive=True)):
        try:
            m, _ = map_of(sections(p)[2])
            if m and m not in saves: saves[m] = p
        except Exception: pass
    if render: RENDERS.mkdir(parents=True, exist_ok=True)
    for key, mid in meshes.items():
        name = ' / '.join(sorted(mid['names'])) or '?'
        m, slot, lba, off = mid['first']
        safe = '%s_%s' % (mid['id'], ''.join(c if c.isalnum() else '_' for c in name)[:40])
        mid['render'] = None; mid['textured_render'] = None
        if not render: continue
        label = '%s  %s  (%d parts, %d verts)  map %d slot %d' % (mid['id'], name[:40], mid['parts'], mid['verts'], m, slot)
        if render_mesh(m, slot, label, RENDERS / (safe + '.png')): mid['render'] = 'renders/enemies/%s.png' % safe
        tm = next((x for x in sorted(mid['maps']) if x in saves), None)
        if tm is not None:
            blob, _, slots = room_models(tm)
            tslot = next(s for s, (o, t) in slots.items() if mesh_key(blob, o)[0] == key)
            if render_mesh(tm, tslot, label + '  [textured, save in map %d]' % tm, RENDERS / (safe + '_tex.png'), vram_of(saves[tm])):
                mid['textured_render'] = 'renders/enemies/%s_tex.png' % safe
    if render:
        tiles = sorted(RENDERS.glob('mesh*.png'))
        for k in range(0, len(tiles), 12):
            chunk = tiles[k:k + 12]; sheet = Image.new('RGB', (960, 262 * ((len(chunk) + 1) // 2)))
            for i, t in enumerate(chunk): sheet.paste(Image.open(t), (480 * (i % 2), 262 * (i // 2)))
            sheet.save(RENDERS.parent / ('enemies_sheet_%d.png' % (k // 12)))
    out = [dict(mesh=v['id'], names=sorted(v['names']), parts=v['parts'], verts=v['verts'], maps=sorted(v['maps']),
                first=dict(map=v['first'][0], slot=v['first'][1], room_lba=v['first'][2], offset=v['first'][3],
                           sector=v['first'][2] + v['first'][3] // 2048, byte=v['first'][3] % 2048),
                render=v['render'], textured_render=v['textured_render']) for v in meshes.values()]
    OUT_JSON.write_text(json.dumps(dict(
        locate=('The room blob is the room\'s sectors read in order from room_lba (2048 user-data bytes each); offset is '
                'the model header in it = disc sector:byte. A creature\'s model is the room model whose bank slot equals '
                'its script actor. Renders: tools/pe_assets/renders (local, git-ignored).'),
        meshes=out, appearances=rows, no_model=missing), indent=1), encoding='utf-8')

    L = ['# Enemy model catalog — October 19, 2026', '',
         'The 3D model behind every Bestiary creature, with where to find it on disc. Stats, drops and the stat',
         'blocks\' own locations are in `findings/pe-bestiary-draft-2026-10-19.md`; human characters in',
         '`findings/pe-model-catalog-2026-10-19.md`. Built by `tools/pe_assets/catalog_enemies.py`; every',
         'appearance is in `findings/data/pe-enemy-model-catalog-2026-10-19.json`.', '',
         '**How to find a model:** read the room\'s sectors from its LBA on "Parasite Eve (USA) (Disc N).bin"',
         '(2048 user-data bytes each); the model header sits at the offset, i.e. at disc sector:byte. A',
         'creature\'s model is the room model in the bank slot numbered like its script actor.', '',
         '**Renders** (local only, git-ignored): `tools/pe_assets/renders/enemies/` — one shaded render per mesh,',
         'plus `_tex` when a save state in one of its rooms had the textures loaded; contact sheets',
         '`tools/pe_assets/renders/enemies_sheet_*.png`. Enemy rooms carry no textures of their own.', '',
         '%d distinct meshes for %d creature appearances.' % (len(out), len(rows)), '',
         '| Mesh | Creature(s) | Parts | Verts | Maps | First copy: map / slot, room LBA, offset, sector:byte | Textured render |',
         '|---|---|---:|---:|---|---|---|']
    for v in sorted(out, key=lambda v: (v['first']['map'], v['first']['slot'])):
        f = v['first']; maps = v['maps']
        L.append('| %s | %s | %d | %d | %s | %d / %d, %d, %d, %d:%d | %s |' % (
            v['mesh'], ', '.join(v['names']) or '?', v['parts'], v['verts'],
            ', '.join(map(str, maps[:10])) + (' +%d' % (len(maps) - 10) if len(maps) > 10 else ''),
            f['map'], f['slot'], f['room_lba'], f['offset'], f['sector'], f['byte'], 'yes' if v['textured_render'] else '-'))
    if missing:
        L += ['', 'Stat blocks with no model in their actor\'s slot (set up by another actor): ' +
              ', '.join('%s %s (map %d actor %d)' % (n or '?', i, m, a) for n, i, m, a in missing)]
    OUT_MD.write_text('\n'.join(L) + '\n', encoding='utf-8')
    print(json.dumps(dict(meshes=len(out), appearances=len(rows), no_model=len(missing),
                          textured=sum(bool(v['textured_render']) for v in out))))


if __name__ == '__main__':
    main(render='--no-render' not in sys.argv)
