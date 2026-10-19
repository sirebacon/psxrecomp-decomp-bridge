"""Melee contact windows (Entity_CheckActionIdMatch / Entity_TriggerAnimEvent / Entity_ResolveDropTable)."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decode_enemy_actions import timing
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_catalog import action_catalog
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C, cells_key
from pe_weapon_sim.melee_window import actions, bounds, melee_rows, window
from pe_weapon_sim.tests.test_source_combat import config, foe


class WindowTests(unittest.TestCase):
    def test_frame_closes_window_one_update_before_decoder_hit(self):
        w = window(9, 18, 65536, 65536, 3, 12)
        t = timing(9, 18, 65536, 65536, 12)
        self.assertEqual((w['open'], w['close'], w['complete'], w['closed_by']), (9, 21, 27, 'frame'))
        self.assertEqual(t['windup'], w['close'] + 1)                 # the decoder's "hit" is the closing crossing

    def test_frame_past_clip_never_closes(self):
        w = window(3, 18, 65536, 65536, 3, 20)
        self.assertEqual((w['close'], w['closed_by']), (20, 'completion'))

    def test_category0_ends_on_hit(self):
        w = window(5, 19, 65536, 65536, 0, 17)
        self.assertEqual(bounds(w), dict(early=dict(windup=5, recovery=1), late=dict(windup=23, recovery=1)))

    def test_category2_window_matches_contact_bound(self):
        w = window(6, 10, 65536, 65536, 2, 4)
        self.assertEqual(bounds(w), dict(early=dict(windup=6, recovery=10), late=dict(windup=15, recovery=1)))


class CatalogTests(unittest.TestCase):
    def test_every_category_covered(self):
        cats = {r['category'] for _, _, r in actions()}
        self.assertTrue({0, 2, 3} <= cats)

    def test_decoder_agreement_where_both_exist(self):
        ac = action_catalog(cells_key(C))
        checked = 0
        for (m, i), rows in ac.items():
            mine = melee_rows(dict(loc=str(m), name='0x%04X' % i), C)
            for a in rows:
                r = mine.get(a['slot'])
                if r and r['closed_by'] == 'frame':
                    self.assertEqual(a['windup'], r['close'] + 1); checked += 1
        self.assertGreater(checked, 5)

    def test_previously_untimed_close_attack(self):
        r = melee_rows(dict(loc='104', name='0x000F'), C)[0]
        self.assertEqual((r['category'], r['open'], r['close'], r['contact_ids']), (3, 3, 20, [4, 9, 11, 19]))


class CombatTests(unittest.TestCase):
    def test_option_sets_timing(self):
        class Fixed:
            def sample(self, rng): return 300
        def run(bound):
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=33, stat22=79, offense=350),
                                [{**foe(100000), 'loc': '104', 'name': '0x000F'}], Fixed(), random.Random(3), time_cap=30.0,
                                source_options=dict(shared_cells=C, static_enemy_catalog=True, melee_window=bound,
                                                    enemy_defaults=dict(source_action_slot=0)))
        early, late = run('early'), run('late')
        self.assertEqual(early['melee_window_matches'], 1)
        self.assertGreaterEqual(early['damage_taken'], late['damage_taken'])
        with self.assertRaises(ValueError): run('fast')


if __name__ == '__main__':
    unittest.main()
