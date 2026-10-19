"""Room 256 boss effects (room_m256.py) and the serial-action enemy freeze."""
import random, unittest

from pe_weapon_sim import engine, rules, room_m256 as M
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.room_modules import task_plan, task_spec
from pe_weapon_sim.tests.test_source_combat import config, foe

BOSS = dict(loc='256', name='0x0223')


class HelperTests(unittest.TestCase):
    def test_look_and_vector_conventions(self):
        self.assertEqual(M.look_angles((0, 0, 0), (0, 0, -100)), (0, 2048))      # forward is -Z, yaw 2048
        x, y, z = M.angles_to_vector(0, 2048, 100)
        self.assertAlmostEqual(z, -100, places=6); self.assertAlmostEqual(x, 0, places=6)
        self.assertLess(M.angles_to_vector(0x200, 0, 100)[1], 0)                 # positive pitch rises (y up is negative)

    def test_ease_takes_short_way(self):
        self.assertEqual(M.ease(4000, 100, 4096) & 4095, 100)
        self.assertEqual(M.ease(0, 1000, 2048), 500)

    def test_swing_segments(self):
        angles, durations = M.SWING_BRANCHES['ahead']
        self.assertEqual(M.swing_offset(durations[0] - 1, angles, durations), angles[0])
        self.assertEqual(M.swing_offset(sum(durations[:2]) - 1, angles, durations), angles[1])
        self.assertEqual(M.swing_offset(sum(durations), angles, durations), 0)   # released


class PlanTests(unittest.TestCase):
    def test_programs_registered(self):
        self.assertEqual(task_spec(256, 132)['controller'], 'RoomM256_TrailEmitter')
        self.assertEqual(task_spec(256, 131)['controller'], 'RoomM256_ScatterDropEmitter')

    def test_scatter_contacts_follow_distance(self):
        tp = task_plan(BOSS, 4, C)
        self.assertEqual(tp['action']['command'], 131)                           # found behind the swing class
        near, far = (tp['run'](d, 100, random.Random(1))['contacts'] for d in (600, 2000))
        self.assertTrue(near and far and near[0] < far[0])

    def test_trail_turn_scale_decides_contact(self):
        tp = task_plan(BOSS, 3, C)
        tp['scene']['trail_turn_scale'] = 1000
        hit = tp['run'](1000, 100, random.Random(1))['contacts']
        self.assertTrue(hit and 60 < hit[0] < 90)


class SerialActionTests(unittest.TestCase):
    def run_one(self, serial):
        class Fixed:
            def sample(self, rng): return 600
        opts = dict(hp=10 ** 7, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=50))
        if serial: opts['serial_action'] = True
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                            [foe(100000)], Fixed(), random.Random(2), time_cap=30.0, source_options=opts)

    def test_enemies_freeze_while_aya_acts(self):
        off, on = self.run_one(False), self.run_one(True)
        self.assertGreater(on['serial_frozen_updates'], 0)
        self.assertLess(on['turns'], off['turns'])                               # no gauge gain while acting
        self.assertNotIn('serial_frozen_updates', off)


if __name__ == '__main__':
    unittest.main()
