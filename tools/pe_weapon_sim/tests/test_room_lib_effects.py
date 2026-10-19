"""room_lib effect ports (room_lib_effects.py, room_modules motion particles) on real identities."""
import random, unittest

from pe_weapon_sim.enemy_choice import called_plans
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C0, MULTI_KIND

C = {**C0, MULTI_KIND: 1}


def plans(loc, name, seed=0):
    return called_plans(dict(loc=loc, name=name), C, variant_rng=random.Random(seed))


def contacts(plan, distance, seed=1):
    return plan['module']['run'](distance, 120, random.Random(seed))['contacts']


class RoomLibEffectTests(unittest.TestCase):
    def test_1a_species_melee_window_and_orbit_flare(self):
        p = plans('333', '0x001A', 0)
        self.assertEqual(p[1]['kind'], 'window')                      # picked species' own window
        self.assertEqual(p[3]['kind'], 'task')                        # orbit flare (115)
        near, far = contacts(p[3], 700), contacts(p[3], 1800)
        self.assertTrue(near and far and near[0] < far[0])

    def test_188_wave_spark_is_visual_phased_spark_can_hit(self):
        p = plans('188', '0x021A', 0)
        self.assertEqual(contacts(p[4], 1000), [])                    # WaveSpark: no contact path
        p = plans('188', '0x021A', 2)
        self.assertTrue(any(contacts(p[3], 1000, s) for s in range(4)))

    def test_269_sweep_and_spray(self):
        self.assertTrue(contacts(plans('269', '0x021B')[4], 700))
        self.assertTrue(contacts(plans('269', '0x0220')[3], 700))

    def test_245_trails(self):
        p = plans('245', '0x0421', 0)
        self.assertEqual(p[3]['kind'], 'task')
        self.assertTrue(contacts(p[3], 700))

    def test_motion_particle_strip_reaches_by_link(self):
        p = plans('75', '0x000C')
        t = [contacts(p[3], d)[0] for d in (600, 1500, 3000)]
        self.assertEqual(t, sorted(t))
        self.assertLessEqual(t[-1] - t[0], 12)                         # one link (300 units) per update


class RoomBossTests(unittest.TestCase):
    def test_beacons_and_pulses(self):
        self.assertTrue(contacts(plans('5', '0x0201')[3], 1500))
        self.assertEqual(contacts(plans('23', '0x0204')[3], 2600), [])  # beyond the 2050 beam
        self.assertTrue(contacts(plans('89', '0x020E')[3], 1500))
        p = plans('123', '0x0312')
        self.assertEqual(contacts(p[4], 5000), contacts(p[4], 600))    # PulseRing: no distance test

    def test_phase_pick_and_repeated_windows(self):
        p = plans('86', '0x020D')
        self.assertEqual((p[0]['kind'], p[1]['kind']), ('window', 'window'))
        self.assertTrue(p[0].get('phase_pick'))
        powers = {plans('86', '0x020D', s)[0]['power']['power'] for s in range(12)}
        self.assertTrue(powers <= {52, 60, 62, 66} and len(powers) > 1)


if __name__ == '__main__':
    unittest.main()
