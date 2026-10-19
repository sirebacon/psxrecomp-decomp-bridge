"""Scripted boss HP from the play log: untargetable controllers, a scripted second phase, and parts
removed by script without engaging (calibrate_logged --controllers)."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.tests.test_source_combat import config, foe


class Fixed:
    def sample(self, rng): return 600


def fight(foes, **extra):
    opts = dict(hp=10 ** 7, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=40), **extra)
    return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=20, stat22=66, offense=175, defense=210),
                        foes, Fixed(), random.Random(3), time_cap=120.0, source_options=opts)


class ScriptedBossHpTests(unittest.TestCase):
    def test_controller_is_untargetable_and_need_not_die(self):
        out = fight([dict(foe(10), controller=True), foe(300)])
        self.assertEqual(out['won'], 1)
        self.assertLess(out['damage'], 300 + 10)          # the 10-HP core was never shot

    def test_phase2_refills_once(self):
        plain, phased = fight([foe(300)]), fight([dict(foe(300), phase2_hp=200)])
        self.assertEqual(phased['phase2_refills'], 1)
        self.assertGreater(phased['time'], plain['time'])

    def test_calibration_flags_from_log(self):
        from pe_weapon_sim.calibrate_logged import battles, foe_for
        bs = {b['map']: b for b in battles() if b['boss']}
        if not bs: self.skipTest('play log not available')
        self.assertTrue(any(f.get('_controller') for f in bs['123']['foes']))
        self.assertEqual(sum(bool(f.get('_unengaged')) for f in bs['269']['foes']), 4)
        self.assertEqual([foe_for(f, True).get('phase2_hp') for f in bs['188']['foes'] if f.get('_phase2_hp')], [300])
        self.assertNotIn('controller', foe_for(bs['123']['foes'][-1], False))   # opt-in


if __name__ == '__main__':
    unittest.main()
