"""Catalog every character-sized model on both discs: where it is, its skeleton, and who it is.

Writes findings/data/pe-model-catalog-2026-10-19.json and findings/pe-model-catalog-2026-10-19.md
(locations and metadata only, no asset data). Offline: disc images + the PST snapshot's RAM tables.

    PYTHONPATH=tools python tools/pe_assets/catalog_models.py
"""
import json, os, struct, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from render_models import BASE, image_blob, model, records, room_blob, u16, ram, word  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'findings/data/pe-model-catalog-2026-10-19.json'
OUT_MD = ROOT / 'findings/pe-model-catalog-2026-10-19.md'
MIN_PARTS = 15

# Identified by rendering (tools/pe_assets render_saves.py / render_batch.py), keyed (map, slot) of
# one appearance; every model with the same mesh (vertex count + skeleton + bone lengths) inherits it.
NAMES = {
    (25, 3): ('Daniel', 'textured (save in map 25 / 275)'), (275, 2): ('Daniel', 'textured'),
    (25, 4): ('Maeda', 'textured (save in map 25 / 276)'), (276, 3): ('Maeda', 'textured'),
    (88, 2): ('Eve (Day 1 form)', 'textured'), (273, 2): ('Eve (Statue of Liberty form)', 'textured'),
    (25, 2): ('Ben', 'textured'), (6, 2): ('Ben', 'shape + rooms'),
    (2, 2): ("Aya's date (Carnegie Hall)", 'textured'),
    (2, 3): ('Usher', 'textured'), (2, 4): ('Usher', 'textured'),
    (48, 2): ('Policewoman (brown hair, vest)', 'textured'),
    (52, 3): ('Police officer (moustache)', 'textured'),
    (190, 3): ('Police officer (cap)', 'textured'),
    (275, 3): ('Crew (grey uniform, cap)', 'textured'), (276, 6): ('Crew (grey uniform, cap)', 'textured'),
    (11, 2): ('Maya (blonde girl, hospital gown)', 'textured from disc'),
    (196, 2): ('Dr. Klamp? (bearded, long coat)', 'untextured: shape + rooms'),
    (41, 3): ('Chief Baker? (heavy-set, dark suit)', 'textured from disc'),
    (44, 4): ('Chief Baker? (heavy-set, dark suit, gun)', 'textured from disc'),
    (4, 3): ('Melissa (opera singer, red gown)', 'textured from disc'),
    (17, 1): ('Opera performer (harlequin)', 'textured from disc'),
    (1, 2): ('Police officer (light uniform)', 'textured from disc'),
    (1, 4): ('Police officer (cap, black jacket)', 'textured from disc'),
    (41, 4): ('NYPD man (brown jacket)', 'textured from disc'),
    (41, 5): ('NYPD man (white shirt, shoulder holster)', 'textured from disc'),
    (43, 4): ('Policewoman (blonde, cap)', 'textured from disc'),
    (44, 3): ('Police dog', 'textured from disc'),
    (17, 2): ('Aya (cutscene pose model)', 'textured from disc'),
    (45, 9): ('Aya (cutscene pose model)', 'textured from disc'),
    (49, 2): ('Opera actress (purple gown)', 'textured from disc'),
    (49, 3): ('Opera performer (doublet)', 'textured from disc'),
    (49, 4): ('Opera performer (robed king)', 'textured from disc'),
    (49, 5): ('Opera performer (knight)', 'textured from disc'),
    (69, 2): ('Eve (47-part form)', 'textured from disc'),
    (90, 2): ('Maeda (with backpack)', 'textured from disc'),
    (94, 4): ('Daniel (gun drawn)', 'textured from disc'),
    (102, 2): ('Police officer (cap, seated / injured pose)', 'textured from disc'),
    (271, 2): ('Sailor? (cap)', 'untextured: shape + rooms'), (271, 4): ('Sailor? (cap)', 'untextured: shape + rooms'),
}
AYA = {10: 'Aya - black evening dress (Day 1 play)', 11: 'Aya - long dress (Day 1 scenes, reduced moveset)',
       12: 'Aya - jacket and jeans (main)', 13: 'Aya - T-shirt and jeans (Disc 2)', 14: 'Aya - transformed form (final battle)'}


def describe(blob, off):
    md = model(blob, off)
    chains = []
    par, st, cur = {}, [], None
    for c in md['cmds']:
        if c == -1: st.append(cur)
        elif c == -2: cur = st.pop()
        else: par[c] = cur; cur = c
    kids = defaultdict(list)
    for k, v in par.items(): kids[v].append(k)
    def length(n):
        k = 0
        while True:
            k += 1
            if len(kids.get(n, [])) != 1: return k
            n = kids[n][0]
    chest = kids[0][0] if kids.get(0) else None
    plan = '/'.join(str(length(c)) for c in kids.get(chest, [])) if chest is not None else ''
    return dict(parts=md['parts'], anims=blob[off + 3], verts=len(md['V']), skeleton=md['cmds'],
                bones=[p[3] for p in md['ptab']], chains=plan)


def main():
    rows, families = [], {}
    aya_skel = {}
    for area in range(10, 15):
        idx = area + 8; blob = image_blob(idx); off = records(blob, 0x0C)[0][0]
        d = describe(blob, off); s0 = u16(ram, 0x930D8 + 2 * idx)
        aya_skel[tuple(d['skeleton'])] = 'Aya area %d' % area
        rows.append(dict(name=AYA[area], how='player bundle', disc='both', source='PE image entry %d (textures %d)' % (idx, area + 3),
                         lba=BASE + s0, offset=off, sector=BASE + s0 + off // 2048, byte=off % 2048, map=None, slot=0, **d))
    mesh_name = {}
    found = []
    for disc in (1, 2):
        for m in range(1, 441):
            packed = word(ram, 0x9337c + (m - 1) * 8)
            if packed >> 20 == 0: continue
            start = word(ram, 0x93378 + (m - 1) * 8); lba = BASE + start + (packed & 255) + ((packed >> 8) & 4095)
            try: blob = room_blob(m, disc)
            except Exception: continue
            dd = word(blob, 4); desc = word(blob, dd + 0x0C); at = desc & 0x3fffff
            for i in range(desc >> 22):
                w = word(blob, at + 12 * i + 4); off, slot = w & 0xffffff, w >> 24
                if off + 0x1C > len(blob) or blob[off + 2] < MIN_PARTS: continue
                try: d = describe(blob, off)
                except Exception: continue
                key = (d['verts'], tuple(d['skeleton']), tuple(d['bones']))
                found.append((disc, m, slot, lba, off, d, key))
                if (m, slot) in NAMES and disc == 1: mesh_name[key] = NAMES[(m, slot)]
    same = defaultdict(set)
    for disc, m, slot, lba, off, d, key in found: same[(m, slot, key)].add(disc)
    seen = set()
    for disc, m, slot, lba, off, d, key in found:
        if (m, slot, key) in seen: continue
        seen.add((m, slot, key))
        name, how = mesh_name.get(key, (None, None))
        rows.append(dict(name=name, how=how, disc='both' if len(same[(m, slot, key)]) == 2 else disc,
                         source='room map %d, model slot %d' % (m, slot), lba=lba, offset=off,
                         sector=lba + off // 2048, byte=off % 2048, map=m, slot=slot,
                         aya_skeleton=aya_skel.get(tuple(d['skeleton'])), **d))
    OUT_JSON.write_text(json.dumps(dict(
        locate=('Room models: the room blob is the room\'s sectors read in order from `lba` (2048 user-data bytes '
                'each); `offset` is the model header (RenderObjectHeader) in that blob = disc sector `sector`, '
                'user-data byte `byte`. Player bundles: PE image entry N (g_PeImageSectorTable 0x800930D8). '
                'Skeleton = matrix-command bytes (-1 push, -2 pop, else part); bones = parts[i].translation_z.'),
        renders='tools/pe_assets/renders (local only, git-ignored; re-create with render_saves.py / render_batch.py)',
        models=rows), indent=1), encoding='utf-8')

    meshes = defaultdict(list)
    for r in rows[5:]: meshes[(r['verts'], tuple(r['skeleton']), tuple(r['bones']))].append(r)
    # one textured render per mesh (first disc-1 copy), from the room's own texture blobs
    from catalog_enemies import render_mesh
    from PIL import Image
    rdir = Path(__file__).resolve().parent / 'renders' / 'characters'; rdir.mkdir(parents=True, exist_ok=True)
    for old in list(rdir.glob('char*.png')) + list(rdir.parent.glob('characters_sheet_*.png')): old.unlink()
    for n, (k, v) in enumerate(sorted(meshes.items(), key=lambda kv: (kv[1][0]['map'], kv[1][0]['slot']))):
        f = next((r for r in v if r['disc'] in ('both', 1)), v[0])
        name = f['name'] or '?'
        safe = 'char%03d_%s' % (n, ''.join(c if c.isalnum() else '_' for c in name)[:40])
        try:
            ok = render_mesh(f['map'], f['slot'], 'char%03d  %s  (%d parts, %d verts)  map %d slot %d' % (n, name[:40], f['parts'], f['verts'], f['map'], f['slot']), rdir / (safe + '.png'))
        except Exception: ok = False
        for r in v: r['render'] = 'renders/characters/%s.png' % safe if ok else None
    tiles = sorted(rdir.glob('char*.png'))
    for k in range(0, len(tiles), 12):
        chunk = tiles[k:k + 12]; sheet = Image.new('RGB', (960, 262 * ((len(chunk) + 1) // 2)))
        for i, t in enumerate(chunk): sheet.paste(Image.open(t), (480 * (i % 2), 262 * (i // 2)))
        sheet.save(rdir.parent / ('characters_sheet_%d.png' % (k // 12)))
    L = ['# Model catalog — October 19, 2026', '',
         'Every character-sized model (%d+ parts) on both US discs, with where to find it. Full detail' % MIN_PARTS,
         '(every appearance, skeleton bytes, bone lengths): `findings/data/pe-model-catalog-2026-10-19.json`.',
         'Built by `tools/pe_assets/catalog_models.py`; renders are local only in `tools/pe_assets/renders/`',
         '(git-ignored, game-derived; re-create with `render_saves.py` / `render_batch.py`). Research for the',
         'model swap: `findings/pe-model-swap-research-2026-10-19.md`.', '',
         '**How to find a model:** read the room\'s sectors from its LBA on "Parasite Eve (USA) (Disc N).bin"',
         '(2048 user-data bytes each); the model header sits at the given offset, i.e. at disc sector:byte.',
         'Textures: the room\'s scratch and texture blobs, the two sector runs in front of the room data',
         '(`Scene_LoadRoom`, `room_load.c:420-489`). Renders: `tools/pe_assets/renders/characters/` and',
         '`characters_sheet_*.png` (local only).', '',
         '## Aya (player bundles)', '',
         '| Outfit | Parts | Chains (arm/head/arm) | Image entry | Disc sector:byte |', '|---|---:|---|---|---|']
    for r in rows[:5]:
        L.append('| %s | %d | %s | %s | %d:%d |' % (r['name'], r['parts'], r['chains'], r['source'].replace('PE image entry ', ''), r['sector'], r['byte']))
    L += ['', '## Identified characters', '',
          '| Character | How identified | Parts | Chains | Aya skeleton? | Appears in maps | First copy: map / slot, room LBA, offset, sector:byte |',
          '|---|---|---:|---|---|---|---|']
    named = sorted(((v[0]['name'], k, v) for k, v in meshes.items() if v[0]['name']), key=lambda t: t[0])
    for name, k, v in named:
        f = v[0]
        L.append('| %s | %s | %d | %s | %s | %s | %d / %d, %d, %d, %d:%d |' % (
            name, f['how'], f['parts'], f['chains'], f['aya_skeleton'] or '-', ', '.join(str(x) for x in sorted({r['map'] for r in v})),
            f['map'], f['slot'], f['lba'], f['offset'], f['sector'], f['byte']))
    L += ['', '## Not yet identified', '',
          'Character-sized meshes not named yet (monsters included). One row per distinct mesh.', '',
          '| Parts | Verts | Chains | Aya skeleton? | Maps | First copy: map / slot, sector:byte |', '|---:|---:|---|---|---|---|']
    for k, v in sorted(((k, v) for k, v in meshes.items() if not v[0]['name']), key=lambda kv: (kv[1][0]['map'], kv[1][0]['slot'])):
        f = v[0]
        maps = sorted({r['map'] for r in v})
        L.append('| %d | %d | %s | %s | %s | %d / %d, %d:%d |' % (f['parts'], f['verts'], f['chains'], f['aya_skeleton'] or '-',
                 ', '.join(map(str, maps[:12])) + (' +%d' % (len(maps) - 12) if len(maps) > 12 else ''), f['map'], f['slot'], f['sector'], f['byte']))
    OUT_MD.write_text('\n'.join(L) + '\n', encoding='utf-8')
    print(json.dumps(dict(models=len(rows), meshes=len(meshes), named_meshes=len(named))))


if __name__ == '__main__':
    main()
