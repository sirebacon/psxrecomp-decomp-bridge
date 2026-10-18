"""Bounded contact timing for category-2 enemy actions (slots 0-2)."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.contact_timing import actions, contact_profile, updates
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.tests.test_source_combat import config, foe, Fixed

BIRD = dict(loc='220', name='0x001D')


class ContactTimingTests(unittest.TestCase):
    def test_only_category2_slots_0_to_2(self):
        rows = [r for _, _, r in actions()]
        self.assertTrue(rows)
        self.assertTrue(all(0 <= r['slot'] < 3 for r in rows))
        self.assertTrue(all(r['early']['windup'] + r['early']['recovery'] == r['complete_updates'] ==
                            r['late']['windup'] + r['late']['recovery'] for r in rows))

    def test_bounds_for_a_logged_enemy(self):
        e, l = contact_profile(BIRD, 'early', C), contact_profile(BIRD, 'late', C)
        self.assertEqual((e['windup'], e['recovery']), (54, 30))
        self.assertEqual((l['windup'], l['recovery']), (83, 1))
        self.assertEqual(e['slot'], l['slot'])

    def test_fixed16_rounding(self):
        self.assertEqual(updates(30, 65536), 30)
        self.assertEqual(updates(30, 98304), 20)        # step 1.5
        self.assertEqual(updates(31, 98304), 21)        # ceil

    def test_rejects_unknown_bound(self):
        with self.assertRaises(ValueError):
            contact_profile(BIRD, 'middle', C)

    def test_combat_option_uses_bounds_only_when_unproved(self):
        enemy = {**foe(100000), 'loc': '220', 'name': '0x001D'}
        aya = dict(level=27, stat22=76, offense=310, defense=0)
        kw = dict(trace=True, shared_cells=C, contact_timing='early', enemy_defaults=dict(charge_step=9000, initial_charge=9000))
        r = engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [enemy], Fixed(), random.Random(5),
                         time_cap=1.0, source_options=kw)
        self.assertEqual(r['contact_timing_matches'], 1)
        r2 = engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [dict(enemy, loc='358', name='0x000C')],
                          Fixed(), random.Random(5), time_cap=1.0, source_options=dict(kw, enemy_action_timing='fast'))
        self.assertEqual(r2.get('contact_timing_matches', 0), 0)    # animation-proven timing wins
        self.assertEqual(r2['action_timing_matches'], 1)


if __name__ == '__main__':
    unittest.main()
