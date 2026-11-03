"""Tests for pe_pack_build.py and pe_disc.py.

The recipe checks need nothing. The build test needs the player's own disc, which is never in this
repository: set PE_DISC1 (and optionally PE_DISC2) to a .cue to run it.

    python tools/pe_assets/test_pe_pack_build.py
    PE_DISC1=".../Parasite Eve (USA) (Disc 1).cue" python tools/pe_assets/test_pe_pack_build.py
"""
import json, os, sys, tempfile, unittest, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import pe_pack_build as PB


def write_recipe(root, pack=None, chars=None, licence=True):
    pack = pack or {'format': 1, 'id': 'cast-test', 'name': 'Cast', 'version': '0.1.0', 'kind': 'recipe'}
    chars = chars if chars is not None else {'daniel.pe1': ({'name': 'Daniel', 'tier': 'main'}, {'room': 25, 'slot': 3, 'disc': 1})}
    os.makedirs(root, exist_ok=True)
    open(os.path.join(root, 'pack.json'), 'w').write(json.dumps(pack))
    if licence: open(os.path.join(root, 'LICENSE'), 'w').write('CC0')
    for folder, (char, rec) in chars.items():
        d = os.path.join(root, 'characters', folder)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'character.json'), 'w').write(json.dumps(char))
        if rec is not None: open(os.path.join(d, 'recipe.json'), 'w').write(json.dumps(rec))
    return root


class RecipeChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def refused(self, path, words):
        with self.assertRaises(PB.RecipeError) as e: PB.read_recipe(path)
        self.assertIn(words, str(e.exception))

    def test_good_folder_and_zip(self):
        root = write_recipe(os.path.join(self.tmp, 'r'))
        pack, licence, chars = PB.read_recipe(root)
        self.assertEqual((pack['id'], licence, chars[0][0], chars[0][2]['room']), ('cast-test', b'CC0', 'daniel.pe1', 25))
        z = os.path.join(self.tmp, 'r.zip')
        with zipfile.ZipFile(z, 'w') as out:
            for base, _, files in os.walk(root):
                for f in files:
                    full = os.path.join(base, f)
                    out.write(full, os.path.relpath(full, root).replace(os.sep, '/'))
        self.assertEqual(PB.read_recipe(z)[2][0][0], 'daniel.pe1')

    def test_refusals(self):
        self.refused(write_recipe(os.path.join(self.tmp, 'a'), pack={'format': 1, 'id': 'x', 'kind': 'assets'}), 'kind')
        self.refused(write_recipe(os.path.join(self.tmp, 'b'), pack={'format': 1, 'id': 'Bad_Id', 'kind': 'recipe'}), 'bad pack id')
        self.refused(write_recipe(os.path.join(self.tmp, 'c'), pack={'format': 1, 'id': 'pe1', 'kind': 'recipe'}), 'bad pack id')
        self.refused(write_recipe(os.path.join(self.tmp, 'd'), licence=False), 'LICENSE')
        self.refused(write_recipe(os.path.join(self.tmp, 'e'), chars={'x.pe1': ({'name': 'X', 'tier': 'boss'}, {'room': 1, 'slot': 1})}), 'tier')
        self.refused(write_recipe(os.path.join(self.tmp, 'f'), chars={'x.pe1': ({'name': 'X', 'tier': 'main'}, None)}), 'recipe.json')
        self.refused(write_recipe(os.path.join(self.tmp, 'g'), chars={'x.pe1': ({'name': 'X', 'tier': 'main'}, {'room': 1, 'slot': 1, 'disc': 3})}), 'disc')
        self.refused(write_recipe(os.path.join(self.tmp, 'h'), chars={}), 'no characters')
        z = os.path.join(self.tmp, 'evil.zip')
        with zipfile.ZipFile(z, 'w') as out:
            out.writestr('pack.json', '{}'); out.writestr('../escape', 'x')
        self.refused(z, 'unsafe name')

    def test_missing_disc_is_reported_not_fatal(self):
        root = write_recipe(os.path.join(self.tmp, 'r'), chars={'x.pe1': ({'name': 'X', 'tier': 'main'}, {'room': 25, 'slot': 3, 'disc': 2})})
        target, built, failed = PB.build_pack(root, {}, os.path.join(self.tmp, 'out'))
        self.assertIsNone(target)
        self.assertEqual(failed, [('x.pe1', 'needs disc 2')])


@unittest.skipUnless(os.environ.get('PE_DISC1'), 'set PE_DISC1 to your own disc image to build from it')
class BuildFromDisc(unittest.TestCase):
    def test_daniel(self):
        import pe_disc
        tmp = tempfile.mkdtemp()
        discs = {1: pe_disc.Disc(os.environ['PE_DISC1'])}
        if os.environ.get('PE_DISC2'): discs[2] = pe_disc.Disc(os.environ['PE_DISC2'])
        target, built, failed = PB.build_pack(write_recipe(os.path.join(tmp, 'r')), discs, os.path.join(tmp, 'packs'))
        self.assertEqual((built, failed), (['daniel.pe1'], []))
        with zipfile.ZipFile(target) as z:
            names = set(z.namelist())
            pack = json.loads(z.read('pack.json'))
        self.assertEqual(pack['kind'], 'assets')
        for f in PB.BUILT[:10]: self.assertIn('characters/daniel.pe1/' + f, names)
        self.assertNotIn('characters/daniel.pe1/recipe.json', names)


if __name__ == '__main__':
    unittest.main()
