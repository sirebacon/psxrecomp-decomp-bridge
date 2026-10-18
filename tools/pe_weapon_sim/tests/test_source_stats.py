"""Aya's source stats / defensive inputs, pinned to the 2026-10-18 read-only live probe."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.economy import bp as BP, equipment as EQ, source_stats as S, tables as T
from pe_weapon_sim.tests.test_source_combat import config, foe, Fixed


def n_jacket_live():
    a = EQ.Item(0x98, "t", "Disc2")                 # N JACKET 34/28/19, run's bonus +32/21/12
    a.bonus = [32, 21, 12]; a.prov = [{("t", 0): b} for b in a.bonus]
    return a


class SourceStatsTests(unittest.TestCase):
    def test_live_eve_fight_values(self):
        s = S.aya_stats(33)
        self.assertEqual((s["defense"], s["offense"], s["stat22"]), (362, 350, 79))
        self.assertEqual(S.armor_inputs(n_jacket_live()), dict(armor_first=66, armor_second=49, critical_resist=30))

    def test_active_time_growth_lags_level(self):
        self.assertEqual(S.stat_level(5, 320), 29)
        self.assertEqual(S.stat_level(0, 320), 32)
        self.assertLess(S.aya_stats(33)["stat22"], T.stat22_of(33))      # legacy linear overstates

    def test_bp_active_time_buys_next_threshold_and_survives_level_ups(self):
        a = BP.Aya(source=True); a.exp = T.LEVEL_EXP[1]                 # level 2: value 10 -> AT level 0
        self.assertEqual(a.stat22, 50)
        a.buy_active_time()                                            # value 20 -> AT level 1
        self.assertEqual((a.stat22, a.at_extra), (51, 10))
        a.exp = T.LEVEL_EXP[2]                                         # level 3: value 30 -> AT level 2
        self.assertEqual(a.stat22, 52)

    def test_critical_resist_formula_branches(self):
        self.assertEqual(S.critical_resist(0), 0)
        self.assertEqual(S.critical_resist(31), 30)
        self.assertEqual(S.critical_resist(84), 50)
        self.assertEqual(S.critical_resist(85), 50)
        self.assertEqual(S.critical_resist(999), 159)

    def test_legacy_default_unchanged(self):
        a = BP.Aya(); a.exp = T.LEVEL_EXP[32]
        self.assertEqual(a.combat(), dict(level=33, stat22=T.stat22_of(33), offense=T.offense_of(33)))

    def test_source_combat_reads_player_armor(self):
        enemy = {**foe(100000), 'loc': '5', 'name': '0x0201'}
        aya = dict(level=20, stat22=79, offense=100, defense=0, armor_first=10, critical_resist=100)
        r = engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [enemy], Fixed(), random.Random(5),
                         time_cap=.1, source_options=dict(trace=True, enemy_defaults=dict(
                             charge_step=9000, initial_charge=9000, windup=1, recovery=1, hit_probability=1,
                             source_action_slot=0, source_shared_cells={10: 65536})))
        hits = [e['damage'] for e in r['_source_events'] if e['event'] == 'enemy_hit']
        self.assertEqual(hits, [5])                                    # power 15 - armor first 10


if __name__ == '__main__':
    unittest.main()
