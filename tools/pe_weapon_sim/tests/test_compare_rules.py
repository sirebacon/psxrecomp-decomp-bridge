"""compare_rules build sources and proposal guard."""
import unittest

from pe_weapon_sim.compare_rules import builds, class_builds, proposal_from


class ClassBuildTests(unittest.TestCase):
    def test_class_builds_reuse_frozen_aya(self):
        ref = {b['seed']: b for b in builds(['Disc2'], 2, ['C'])}
        rows = list(class_builds(['Disc2'], 2))
        self.assertEqual({r['group'] for r in rows}, {'class_' + c for c in ('handgun', 'machine', 'rifle', 'shotgun', 'grenade')})
        for r in rows:
            self.assertEqual(r['aya'], ref[r['seed']]['aya'])            # only the gun differs
            self.assertEqual(r['armor'], ref[r['seed']]['armor'])
        p90 = next(r for r in rows if r['group'] == 'class_machine')
        self.assertEqual((p90['gun'], p90['cfg']['eff']['mode'], p90['cfg']['eff']['commands']), ('P90', 'all', 2))

    def test_d5_uses_built_in_effects_only(self):
        for r in class_builds(['D5'], 1):
            self.assertNotIn('quickdraw', r['cfg']['eff'])


class ProposalTests(unittest.TestCase):
    def test_attack_all_multi_only(self):
        r, tf = proposal_from('exp:AAm_40')
        self.assertEqual((r['all_mode_power_pct'], r['all_mode_multi_only'], tf), (40, True, None))

    def test_combined_rules_and_weapon_edits(self):
        r, tf = proposal_from('exp:AAo_40|cfg:@G3A3.power+45,5.rof+1,3.magazine*1.5')
        self.assertTrue(r['all_mode_ordinary_only'])
        cfg = {b['gun']: b['cfg'] for b in class_builds(['D5'], 1)}
        self.assertEqual(tf(cfg['G3A3'])['power'], cfg['G3A3']['power'] + 45)
        self.assertEqual(tf(cfg['M9 3'])['power'], cfg['M9 3']['power'])                  # other weapons untouched
        self.assertEqual(tf(cfg['M203 4'])['eff']['rof'], cfg['M203 4']['eff']['rof'] + 1)  # eff fields reachable
        self.assertEqual(tf(cfg['MP5PDW'])['magazine'], round(cfg['MP5PDW']['magazine'] * 1.5))
        self.assertIsNot(tf(cfg['G3A3'])['eff'], cfg['G3A3']['eff'])                      # no mutation of the base cfg

    def test_unsupported_keys_refused(self):
        with self.assertRaises(ValueError): proposal_from('exp:E5')                           # abstract-engine key
        with self.assertRaises(ValueError): proposal_from('cfg:4.power=3')


if __name__ == '__main__':
    unittest.main()
