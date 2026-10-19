"""Enemy hit-sphere geometry and melee reach (enemy_reach.py)."""
import json, random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.enemy_reach import (ROOT, animation, catalog, decode_frame, model, move_speed, pair_reach,
                                       reach_rows, room_blob, spheres_at)
from pe_weapon_sim.melee_window import melee_rows
from pe_weapon_sim.tests.test_source_combat import config, foe

FARM = dict(loc='358', name='0x000A')


class ModelTests(unittest.TestCase):
    def test_farming_model_spheres_are_its_contact_parts(self):
        m = model(room_blob(358), 4)
        self.assertEqual([s['part'] for s in m['spheres']], melee_rows(FARM, C)[0]['contact_ids'])
        self.assertEqual([s['radius'] for s in m['spheres']], [104, 96, 125, 67])
        self.assertEqual(m['entries'], len(m['spheres']))           # header animation_entry_count

    def test_frame_decode_and_hierarchy(self):
        b = room_blob(358); m = model(b, 4); p = animation(b, 4, 9)
        t, ang = decode_frame(b, p, 0)
        self.assertEqual(len(ang), len(m['parts']))
        with self.assertRaises(ValueError): decode_frame(b, p, b[p + 2])
        yxz, xyz = spheres_at(m, t, ang), spheres_at(m, t, ang, 'XYZ')
        self.assertNotEqual(yxz, xyz)                                  # the order matters; YXZ was validated

    def test_live_validation_record(self):
        v = json.loads((ROOT / 'pe-hit-sphere-validation-2026-10-18.json').read_text())
        self.assertEqual(v['summary']['order_best']['YXZ'], v['summary']['samples'])
        self.assertGreaterEqual(v['summary']['within_7_units'], 10)


class ReachTests(unittest.TestCase):
    def test_pair_reach(self):
        # Enemy sphere 100 ahead (z = -100) radius 50, Aya sphere at her origin radius 50: contact up to 200.
        self.assertAlmostEqual(pair_reach((0, 0, -100, 50), (0, 0, 0, 50), 1.0), 200.0)
        self.assertIsNone(pair_reach((0, -500, 0, 10), (0, 0, 0, 10), 1.0))   # vertically apart

    def test_move_speed_literal(self):
        node = lambda v, mode=0: dict(handler='Script_SetEntityMoveSpeed', args=[dict(mode=mode, value=v)])
        self.assertEqual(move_speed([]), 4096)
        self.assertEqual(move_speed([node(85184)]), 5324)
        self.assertIsNone(move_speed([node(1, 1)]))

    def test_catalog_and_designer_guards(self):
        self.assertAlmostEqual(reach_rows(FARM, C)[0], 575.9, places=1)
        self.assertGreater(sum(1 for v in catalog().values() if v.get('reach')), 180)
        # Close-attack guards sit just inside reach for the 0x0F enemies (d < 330, reach 406.8).
        self.assertGreater(reach_rows(dict(loc='115', name='0x000F'), C)[0], 330)


class CombatTests(unittest.TestCase):
    def fight(self, d, **opts):
        class Fixed:
            def sample(self, rng): return d
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=33, stat22=79, offense=350),
                            [{**foe(100000), **FARM}], Fixed(), random.Random(5), time_cap=30.0,
                            source_options=dict(shared_cells=C, static_enemy_catalog=True,
                                                enemy_defaults=dict(source_action_slot=0), **opts))

    def test_reach_decides_gated_hits(self):
        near, far = self.fight(400, enemy_choice=True, melee_reach=True), self.fight(600, enemy_choice=True, melee_reach=True)
        self.assertGreater(near['damage_taken'], 0)
        self.assertEqual(near.get('melee_reach_misses', 0), 0)
        self.assertEqual(far['damage_taken'], 0)                         # chosen (d < 630) but out of reach (576)
        self.assertEqual(far['melee_reach_misses'], far['melee_reach_strikes'])

    def test_reach_on_fixed_slot_path(self):
        r = self.fight(600, melee_window='early', melee_reach=True)
        self.assertGreater(r['melee_reach_misses'], 0)

    def test_needs_window(self):
        with self.assertRaises(ValueError): self.fight(400, melee_reach=True)


if __name__ == '__main__':
    unittest.main()
