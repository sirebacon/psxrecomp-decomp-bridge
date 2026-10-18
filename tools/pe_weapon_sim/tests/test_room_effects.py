"""Room-library effect timelines (115 / 122 / 136) and effect-driven enemy actions."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim import room_effects as RE
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.effect_actions import actions, effect_profile
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.tests.test_source_combat import config, foe


class FixedAt:
    def __init__(self, d): self.d = d
    def sample(self, rng): return self.d


class TrigTests(unittest.TestCase):
    def test_retail_quarter_table(self):
        self.assertEqual((RE.rsin(0), RE.rsin(0x400), RE.rcos(0), RE.rcos(0x800)), (0, 4096, 4096, -4096))
        self.assertEqual(RE.rsin(-0x400), -4096)
        self.assertEqual(RE.rcos(0x180) ** 2 + RE.rsin(0x180) ** 2 // 1 > 4096 * 4096 * 0.99, True)


class TaskTests(unittest.TestCase):
    def test_spawn_then_stop_gate_same_pass_does_not_release(self):
        class One(RE._NoParticles):
            def init(self): pass
            def step(self, age, fx): return 1 if age >= 3 else 0
        fx = RE.TaskEffect([(5, 0, 0), (2, 0, 0), (0, 0, 0)], lambda v: One())
        self.assertEqual(fx.run()['release'], 5)        # freed on update 4, op0 sees 0 on update 5

    def test_return2_waits_for_particles(self):
        class Two:
            def init(self): self.left = 3
            def step(self, age, fx): return 2
            def update_particles(self):
                a = 1 if self.left > 0 else 0; self.left -= 1; return a
        self.assertEqual(RE.TaskEffect([(5, 0, 0), (2, 0, 0), (0, 0, 0)], lambda v: Two()).run()['release'], 5)


class EffectTimelineTests(unittest.TestCase):
    def test_line_burst(self):
        self.assertEqual(RE.line_burst(0, 23), dict(contacts=[42], release=374))
        self.assertEqual(RE.line_burst(0x104 + 23, 23)['contacts'], [])          # strict radius
        self.assertEqual(RE.line_burst(0, 23, in_floor=False), dict(contacts=[], release=36))   # freed at 35, released at 36
        self.assertEqual(RE.line_burst(0, 23, duration=60, countdown=20)['contacts'], [42, 62, 82])

    def test_orbit_flare(self):
        r = RE.orbit_flare(800, 63, 4000)
        self.assertEqual(r['contacts'][0], 74)
        near = RE.orbit_flare(300, 63, 4000)
        self.assertEqual(len(near['contacts']), 3)                                # side flares hit up close
        self.assertLess(RE.orbit_flare(800, 63, 1200)['release'], r['release'])   # misses leave earlier

    def test_dropped_flare(self):
        hit = RE.dropped_flare(48, 500, 480, 63)
        self.assertTrue(hit['contacts'])
        self.assertGreater(hit['release'], hit['contacts'][0])
        self.assertEqual(RE.dropped_flare(48, 2500, 480, 63)['contacts'], [])     # lands short

    def test_action_timing_conversion(self):
        self.assertEqual(RE.as_action_timing(dict(contacts=[42], release=374)),
                         dict(windup=42, recovery=332, contact=True, contacts=1))
        self.assertFalse(RE.as_action_timing(dict(contacts=[], release=374))['contact'])


class CatalogTests(unittest.TestCase):
    def test_actions_are_slot3_with_literal_params(self):
        rows = [a for _, _, a in actions()]
        self.assertTrue(rows and all(a['slot'] >= 3 for a in rows))
        self.assertEqual({a['effect'] for a in rows}, {115, 122, 136})

    def test_logged_enemy_profile(self):
        p = effect_profile(dict(loc='126', name='0x0012'), C)
        self.assertEqual((p['effect'], p['slot'], p['params']['lift']), (122, 3, 4096))
        self.assertEqual(p['params']['speed_range'], [32, 64])


class CombatTests(unittest.TestCase):
    def fight(self, d):
        enemy = {**foe(100000), 'loc': '126', 'name': '0x0012'}
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1),
                            dict(level=21, stat22=67, offense=180, defense=220), [enemy], FixedAt(d),
                            random.Random(5), time_cap=20.0,
                            source_options=dict(trace=True, shared_cells=C, effect_actions=True,
                                                static_enemy_catalog=True, enemy_defaults=dict(source_action_slot=0)))

    def test_effect_hits_use_slot3_power_and_geometry(self):
        r = self.fight(500)
        self.assertEqual((r['effect_action_matches'], r['power_catalog_matches']), (1, 1))
        hits = [e['damage'] for e in r['_source_events'] if e['event'] == 'enemy_hit']
        self.assertTrue(hits and all(h == 90 - 220 // 5 for h in hits))
        self.assertEqual([e for e in self.fight(2500)['_source_events'] if e['event'] == 'enemy_hit'], [])


if __name__ == '__main__':
    unittest.main()
