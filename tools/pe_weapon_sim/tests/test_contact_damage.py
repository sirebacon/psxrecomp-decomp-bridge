"""Enemy body-contact damage (contact_damage.py) and its Menu_MainUpdate rules in source_combat."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.contact_damage import contact_of
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C, MULTI_KIND, cells_key
from pe_weapon_sim.tests.test_source_combat import config, foe


class ContactTests(unittest.TestCase):
    def test_script_values(self):
        ck = cells_key({**C, MULTI_KIND: 1})
        self.assertEqual(contact_of(dict(loc='332', name='0x0015', hp=45), ck), 8)    # actor 7 field 65
        self.assertEqual(contact_of(dict(loc='332', name='0x0015', hp=170), ck), 7)   # actor 6
        self.assertEqual(contact_of(dict(loc='245', name='0x0421'), ck), 10)

    def _fight(self, rate, **pe):
        class Fixed:
            def sample(self, rng): return 600
        opts = dict(hp=10 ** 6, shared_cells={**C, MULTI_KIND: 1}, contact_damage=dict(ord=rate, boss=rate),
                    enemy_defaults=dict(charge_step=1, windup=10, recovery=10, power=0))
        if pe: opts['pe'] = pe
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=19, stat22=60, offense=160, defense=205),
                            [dict(foe(10 ** 6), loc='332', name='0x0015', hp=45)], Fixed(), random.Random(4), time_cap=60.0,
                            source_options=opts)

    def test_window_caps_rate_and_damage_is_flat(self):
        out = self._fight(10 ** 6)                        # contact every chance it gets
        self.assertGreater(out['contact_hits'], 0)
        self.assertEqual(out['contact_damage'], 8 * out['contact_hits'])
        self.assertLessEqual(out['contact_hits'], 60 * 29.95 / 0x5A + 1)   # one per 90 updates at most

    def test_barrier_blocks(self):
        out = self._fight(10 ** 6, spells=[], start=500, script={'Barrier': 1})
        self.assertGreater(out.get('contact_barrier', 0), 0)


if __name__ == '__main__':
    unittest.main()
