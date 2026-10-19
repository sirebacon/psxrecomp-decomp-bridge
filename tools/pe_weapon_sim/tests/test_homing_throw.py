"""Thrown homing projectile + ground eruption (homing_throw.py)."""
import unittest

from pe_weapon_sim.homing_throw import actions, homing_plan, launch_from_sends, timeline
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.room_handlers import handler

LAUNCH = launch_from_sends([(0, 5242880, 65536, 15), (1, 0, 524288, 12), (2, 256, 30, 0)])


class DataTests(unittest.TestCase):
    def test_task_program_from_room_data(self):
        f = handler(154, 166, 14)['fields']
        self.assertEqual(f[0][1], 'RoomEffect_HomingProjectile')
        self.assertEqual(f[7][1], 'RoomEffect_HomingProjectileThrow')
        self.assertEqual(f[12][1], 'RoomEffect_HomingProjectileConfigure')

    def test_catalog_and_launch_values(self):
        rows = {(m, a): x for m, a, x in actions()}
        self.assertEqual(rows[154, 9]['launch'], LAUNCH)
        self.assertEqual(LAUNCH['damping'], 15)
        self.assertIsNotNone(homing_plan(dict(loc='154', name='0x0014'), 3, C))


class TimelineTests(unittest.TestCase):
    def run_at(self, d, lateral):
        return timeline(154, 9, 8, 9, 65536, 65536, 3686, LAUNCH, d, 100, lateral)

    def test_facing_line_misses_launch_line_hits(self):
        self.assertEqual(self.run_at(900, 0)['contacts'], [])
        hit = self.run_at(900, 'aimed')
        self.assertEqual(len(hit['contacts']), 1)
        self.assertEqual(hit['contacts'][0], hit['finish'] + 2)          # eruption first update + tick

    def test_flight_time_grows_with_distance(self):
        a, b = self.run_at(400, 'aimed'), self.run_at(1500, 'aimed')
        self.assertLess(a['finish'], b['finish'])
        for r in (a, b):   # hold >= 24 updates, then play out (oscillation phase dependent, frames 23..41)
            self.assertTrue(25 <= r['release'] - r['finish'] <= 24 + 2 * 19, r)

    def test_launch_after_enter_clip(self):
        self.assertGreaterEqual(self.run_at(400, 'aimed')['finish'], 42)    # 42-frame enter clip at step 1


if __name__ == '__main__':
    unittest.main()
