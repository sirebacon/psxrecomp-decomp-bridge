"""Scaled-rank identities, local-path attack power and their combat use (offline)."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_catalog import lookup, timing_profile
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C, cells_key, scaled_rank, scaled_rank_rules
from pe_weapon_sim.enemy_power import power_profile
from pe_weapon_sim.local_power import TAINT, evaluate, catalog as local_catalog
from pe_weapon_sim.tests.test_source_combat import config, foe, Fixed

FARM = dict(loc='358', name='0x000C')


def node(offset, handler, *args):
    return dict(offset=offset, handler=handler, args=[dict(mode=m, value=v) for m, v in args])


class IdentityTests(unittest.TestCase):
    def test_ten_idioms_all_cell10_times4(self):
        r = scaled_rank_rules()
        self.assertEqual(len(r), 10)
        self.assertTrue(all((v['cell'], v['multiplier']) == (10, 4) for v in r.values()))
        self.assertIn((358, 6), r)

    def test_scaled_rank_arithmetic(self):
        rule = dict(cell=10, multiplier=4)
        self.assertEqual(scaled_rank(0x0008, rule, {10: 65536}), 0x000C)
        self.assertEqual(scaled_rank(0x0008, rule, {10: 98304}), 0x000E)   # scale 1.5
        self.assertIsNone(scaled_rank(0x0008, rule, {}))

    def test_default_catalogs_unchanged_without_cells(self):
        self.assertEqual(lookup(FARM), {})
        self.assertEqual(timing_profile(FARM, 'fast'), {})
        self.assertEqual(power_profile(FARM, 0, C), {})

    def test_first_run_cells_resolve_the_farming_enemy(self):
        self.assertEqual(lookup(FARM, C), dict(rank=12, charge_step=65, periodic_damage=2, status_level=3, status_period=78))
        self.assertEqual(timing_profile(FARM, 'fast', C), dict(windup=42, recovery=30, reset_on_completion=True))
        p = power_profile(FARM, 0, C, scaled_identities=True)
        self.assertEqual((p['power'], p['effect_type'], p['critical_chance']), (82, 0, 15))
        p8 = power_profile(dict(loc='358', name='0x0008'), 0, C, scaled_identities=True)
        self.assertEqual(p8['power'], 47)                                   # the V74 < 272 branch

    def test_local_catalog_requires_cells(self):
        self.assertEqual(local_catalog(()), {})
        c = local_catalog(cells_key(C))
        self.assertEqual(c[(358, 12, 0)]['power'], 82)
        self.assertEqual(c[(358, 8, 0)]['power'], 47)


class EvaluatorTests(unittest.TestCase):
    def test_taint_spreads_but_blocks_control(self):
        nodes = [node(0, 'Script_EvalExpr', (0, 0), (3, 1), (1, 5), (0, 3)),      # O1 = L5 + 3 (L5 unknown)
                 node(24, 'Script_EvalExpr', (0, 15), (3, 2), (4, 10), (0, 47)),   # O2 = N10 * 47
                 node(48, 'Script_JumpIfZero', (3, 1), (0, 0))]
        mem, _ = evaluate(nodes, 0, 48, 0, {10: 65536}, {}, {})
        self.assertIs(mem[(3, 1)], TAINT)
        self.assertEqual(mem[(3, 2)], 65536 * 47)
        with self.assertRaises(ValueError):
            evaluate(nodes, 0, 64, 0, {10: 65536}, {}, {})                        # branch on TAINT

    def test_tainted_rank_write_rejected(self):
        nodes = [node(0, 'Entity_SetField', (0, 41), (1, 9))]
        with self.assertRaises(ValueError):
            evaluate(nodes, 0, 16, 0, {}, {}, {})


class CombatTests(unittest.TestCase):
    def test_shared_cells_option_drives_profiles(self):
        enemy = {**foe(100000), 'loc': '358', 'name': '0x000C'}
        aya = dict(level=27, stat22=76, offense=310, defense=315, armor_first=0, critical_resist=100)
        r = engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [enemy], Fixed(), random.Random(5),
                         time_cap=.1, source_options=dict(trace=True, shared_cells=C, static_enemy_catalog=True,
                             enemy_defaults=dict(charge_step=9000, initial_charge=9000, windup=1, recovery=1,
                                                 hit_probability=1, source_action_slot=0)))
        self.assertEqual((r['catalog_matches'], r['power_catalog_matches']), (1, 1))
        hits = [e['damage'] for e in r['_source_events'] if e['event'] == 'enemy_hit']
        self.assertEqual(hits, [82 - 315 // 5])                                    # power 82 - stat20/5


if __name__ == '__main__':
    unittest.main()
