"""Build a recipe pack into a ready character pack, from the player's own Parasite Eve disc.

A recipe pack (bridge findings D8 §5) shares no game data: it holds pack.json ("kind": "recipe"),
LICENSE, and per character characters/<folder>/character.json plus recipe.json naming where the
model is on the disc:

    {"room": 25, "slot": 3, "disc": 1}

This tool runs build_skin.py's builder against the player's disc images (pe_disc.py: no fixed
paths, no RAM snapshot) and writes a normal "assets" pack, <id>-<version>.zip, into the folder the
Wardrobe reads (F1 > Collection > Wardrobe > Packs shows it). The built files come from the
player's own disc and are for their own use: don't share the result, share the recipe.

    python tools/pe_assets/pe_pack_build.py RECIPE (zip or folder) --disc1 DISC1.cue [--disc2 DISC2.cue] --out PACKS_DIR

Needs Python 3.8+ and Pillow (pip install pillow). Exit status 0 when every character built.
"""
import argparse, io, json, os, re, shutil, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

ID_RE = re.compile(r'^[a-z0-9][a-z0-9-]{0,30}$')
FOLDER_RE = re.compile(r'^[A-Za-z0-9_$-][A-Za-z0-9._$-]{0,46}$')
TIERS = ('extra', 'outfit', 'supporting', 'main', 'special')
BUILT = ['texture.bin', 'model.bin'] + ['day%d.bin' % d for d in range(1, 9)] + ['rooms.bin', 'meta.bin']
MAX_JSON = 16384


class RecipeError(Exception):
    pass


class Recipe:
    """A recipe pack's files, from a zip or a folder, by relative path."""

    def __init__(self, path):
        self.path = path
        if os.path.isdir(path):
            self.zip = None
            names = []
            for root, _, files in os.walk(path):
                for f in files:
                    names.append(os.path.relpath(os.path.join(root, f), path).replace(os.sep, '/'))
        else:
            try: self.zip = zipfile.ZipFile(path)
            except zipfile.BadZipFile: raise RecipeError('%s is neither a folder nor a zip' % path)
            names = [i.filename for i in self.zip.infolist() if not i.is_dir()]
        for n in names:
            parts = n.split('/')
            if n.startswith('/') or '\\' in n or ':' in n or '..' in parts or '.' in parts:
                raise RecipeError('unsafe name in the recipe: %s' % n)
        self.names = set(names)

    def read(self, name, limit=MAX_JSON):
        if name not in self.names: raise RecipeError('%s is missing' % name)
        if self.zip:
            info = self.zip.getinfo(name)
            if info.file_size > limit: raise RecipeError('%s is too large' % name)
            return self.zip.read(name)
        full = os.path.join(self.path, *name.split('/'))
        if os.path.getsize(full) > limit: raise RecipeError('%s is too large' % name)
        return open(full, 'rb').read()

    def json(self, name):
        try: return json.loads(self.read(name).decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as e: raise RecipeError('%s: %s' % (name, e))


def read_recipe(path):
    """(pack.json, LICENSE bytes, [(folder, character.json, recipe.json)]), checked."""
    r = Recipe(path)
    pack = r.json('pack.json')
    if pack.get('format') != 1: raise RecipeError('pack.json format is not 1')
    if pack.get('kind') != 'recipe': raise RecipeError('pack.json kind is not "recipe" (an assets pack needs no building)')
    pid = pack.get('id')
    if not isinstance(pid, str) or not ID_RE.match(pid) or pid in ('pe1', 'local'):
        raise RecipeError('bad pack id %r (a-z, 0-9, -; at most 31; not pe1 or local)' % pid)
    licence = r.read('LICENSE')
    chars = []
    folders = sorted({n.split('/')[1] for n in r.names if n.startswith('characters/') and n.count('/') >= 2})
    for folder in folders:
        if not FOLDER_RE.match(folder) or len(pid) + 1 + len(folder) > 63:
            raise RecipeError('character folder %r: bad name' % folder)
        char = r.json('characters/%s/character.json' % folder)
        rec = r.json('characters/%s/recipe.json' % folder)
        if not isinstance(char.get('name'), str) or char.get('tier') not in TIERS:
            raise RecipeError('%s/character.json needs a name and a tier (%s)' % (folder, ', '.join(TIERS)))
        for k in ('room', 'slot'):
            if not isinstance(rec.get(k), int): raise RecipeError('%s/recipe.json needs an integer %s' % (folder, k))
        if rec.get('disc', 1) not in (1, 2): raise RecipeError('%s/recipe.json disc must be 1 or 2' % folder)
        chars.append((folder, char, rec))
    if not chars: raise RecipeError('no characters/<folder>/ with character.json and recipe.json')
    return pack, licence, chars


def build_pack(recipe_path, discs, out_dir, log=print):
    """Build into out_dir/<id>-<version>.zip; returns (zip path, built folders, failed folders)."""
    import render_models as R
    import build_skin as B
    pack, licence, chars = read_recipe(recipe_path)
    R.use_discs(discs)
    built, failed = [], []
    out_pack = dict(pack, kind='assets', built_from='recipe %s %s' % (pack['id'], pack.get('version', '')))
    work = tempfile.mkdtemp(prefix='pe_pack_')
    try:
        files = {}
        for folder, char, rec in chars:
            disc = rec.get('disc', 1)
            if disc not in discs:
                failed.append((folder, 'needs disc %d' % disc)); continue
            dest = os.path.join(work, folder)
            try:
                B.build(folder, rec['room'], rec['slot'], disc, out_dir=dest, install_it=False)
                missing = [f for f in BUILT[:10] if not os.path.isfile(os.path.join(dest, f))]
                if missing: raise RuntimeError('builder left out %s' % ', '.join(missing))
            except Exception as e:                        # one character's failure doesn't stop the rest
                failed.append((folder, str(e))); continue
            files['characters/%s/character.json' % folder] = json.dumps(char, indent=2).encode()
            for f in BUILT:
                p = os.path.join(dest, f)
                if os.path.isfile(p): files['characters/%s/%s' % (folder, f)] = open(p, 'rb').read()
            built.append(folder)
        if not built: return None, built, failed
        os.makedirs(out_dir, exist_ok=True)
        name = '%s-%s.zip' % (pack['id'], re.sub(r'[^A-Za-z0-9.]+', '_', str(pack.get('version', '0'))))
        target = os.path.join(out_dir, name)
        tmp = target + '.part'
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('pack.json', json.dumps(out_pack, indent=2))
            z.writestr('LICENSE', licence)
            for n in sorted(files): z.writestr(n, files[n])
        os.replace(tmp, target)                            # never a half-written pack in packs/
        return target, built, failed
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    import pe_disc
    ap = argparse.ArgumentParser(description='Build a Parasite Eve recipe pack from your own disc.')
    ap.add_argument('recipe', help='the recipe pack: a .zip or a folder')
    ap.add_argument('--disc1', help='Disc 1 (.cue or .bin)')
    ap.add_argument('--disc2', help='Disc 2 (.cue or .bin)')
    ap.add_argument('--out', required=True, help="the Wardrobe's packs folder (<preferences>/packs)")
    a = ap.parse_args(argv)
    discs = {}
    try:
        if a.disc1: discs[1] = pe_disc.Disc(a.disc1)
        if a.disc2: discs[2] = pe_disc.Disc(a.disc2)
        if not discs: ap.error('give --disc1 and/or --disc2')
        target, built, failed = build_pack(a.recipe, discs, a.out)
    except (RecipeError, pe_disc.DiscError) as e:
        print('error:', e); return 2
    for folder, why in failed: print('  %s: not built (%s)' % (folder, why))
    if not target:
        print('nothing built'); return 1
    print('built %d of %d characters into %s' % (len(built), len(built) + len(failed), target))
    print('Restart the game; F1 > Collection > Wardrobe > Packs lists it. Built from your disc: keep it to yourself.')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
