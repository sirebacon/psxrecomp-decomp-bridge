"""Parasite Energy in battle (parasite_energy.py) and its source_combat wiring."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.parasite_energy import PE, MEDICINE
from pe_weapon_sim.tests.test_source_combat import config, foe


class PETests(unittest.TestCase):
    def test_level_table_and_regen(self):
        p = PE(20, ['Heal1'], start=100)
        self.assertEqual(p.pe, 100 << 16)
        before = p.step
        for _ in range(100): p.regen()
        self.assertGreater(p.pe, 100 << 16)
        self.assertLess(p.step, before)                    # Menu_MainUpdate: the step decays
        self.assertGreaterEqual(p.step, 0x1999)

    def test_costs_and_heals(self):
        p = PE(30, ['Heal2', 'Heal3'], start=600, rules='current', heal_rules='vanilla')
        self.assertEqual(p.heal_amount('Heal2', 500), 60)
        self.assertEqual(PE(30, ['Heal2'], heal_rules='current').heal_amount('Heal2', 500), 150)
        light = PE(30, ['Heal3'], start=600, pe_light=True)
        self.assertEqual(light.cost('Heal3'), (500 << 16) * 2 // 3)

    def test_policy_quick_heal_half_bar_and_items(self):
        p = PE(20, ['Heal2'], start=500)
        self.assertEqual(p.choose(100, 300, 4500, False, False), ('Heal2', 'half'))
        self.assertIsNone(p.choose(280, 300, 9000, False, False))
        empty = PE(20, [], start=0, bag={0x07: 1})
        self.assertEqual(empty.choose(100, 300, 4500, False, False), (('item', 0x07), 'half'))
        self.assertEqual(MEDICINE[0x09], 400)

    def test_barrier_drains_pe(self):
        p = PE(20, ['Barrier'], start=300)
        self.assertEqual(p.cost('Barrier'), p.max // 3)
        p.cast('Barrier'); self.assertTrue(p.barrier)
        before = p.pe
        p.barrier_hit(10, 200)
        self.assertEqual(before - p.pe, 10 * ((p.max * 4) // 200))
        p.barrier_hit(10 ** 4, 200)
        self.assertFalse(p.barrier); self.assertEqual(p.pe, 0x10000)

    def test_scripted_casts(self):
        p = PE(20, [], start=400, script={'Detox': 1, 'Haste': 1, 'Heal2': 1})
        self.assertEqual(p.choose_scripted(300, 300, 9000), ('Haste', 'full'))
        self.assertEqual(p.choose_scripted(300, 300, 9000, poisoned=True)[0], 'Detox')
        self.assertEqual(p.choose_scripted(100, 300, 4500, hasted=True), ('Heal2', 'half'))
        p.cast('Heal2'); self.assertIsNone(p.choose_scripted(100, 300, 4500, hasted=True))

    def test_scripted_items_and_medic(self):
        p = PE(30, [], start=900, bag={0x0D: 1, 0x08: 2}, items={0x0D: 1, 0x08: 1}, script={'Medic': 1})
        self.assertEqual(p.scripted_item(300, 300, 4500, {'poison'}), (('item', 0x0D), 'half'))
        self.assertEqual(p.scripted_item(100, 300, 4500), (('item', 0x08), 'half'))
        p.cast(('item', 0x08)); self.assertIsNone(p.scripted_item(100, 300, 4500))   # logged count used up
        self.assertEqual(p.choose_scripted(300, 300, 9000, ailing={'dark'})[0], 'Medic')
        self.assertEqual(p.heal_of('FullRecover', 300), 300)
        self.assertEqual(p.heal_of(('item', 0x0D), 300), 0)

    def test_energy_shot_matches_live_cast(self):
        # Live cast 2026-10-19, room 273: level 33, PE 1420/1420, 0x0125 defense 85 -> 572 logged.
        from pe_weapon_sim.parasite_energy import energy_shot_damage
        self.assertEqual(energy_shot_damage(360, 147, 33, 1420, 1420, 85), 572)     # base 219
        self.assertEqual(energy_shot_damage(350, 147, 33, 1420, 1420, 85), 566)     # save-derived inputs (base 217)
        self.assertNotEqual(3 * 217 - 85 // 5, 572)                                  # defense isn't split by RoF
        self.assertEqual(energy_shot_damage(350, 147, 33, 710, 1420, 85), 349)       # half PE

    def test_liberate_matches_log(self):
        # Rooms 273 (3 targets, defenses 85/70/55 -> 283/298/313) and 432 (1 target, def 50 -> 256), level 33.
        from pe_weapon_sim.parasite_energy import liberate_power
        self.assertEqual([liberate_power(350, 33, 3) - d for d in (85, 70, 55)], [283, 298, 313])
        self.assertEqual(liberate_power(350, 33, 1) - 50, 256)

    def test_haste_first_boss_turn(self):
        p = PE(25, ['Haste'], start=300)
        self.assertEqual(p.choose(300, 300, 9000, True, True), ('Haste', 'full'))


class CombatTests(unittest.TestCase):
    def test_heals_extend_survival(self):
        class Fixed:
            def sample(self, rng): return 600
        out = []
        for pe in (None, dict(spells=['Heal1', 'Heal2'])):
            opts = dict(hp=300, serial_action=True, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=120))
            if pe: opts['pe'] = pe
            out.append(engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=20, stat22=66, offense=175, defense=210),
                                    [foe(4000)], Fixed(), random.Random(2), time_cap=90.0, source_options=opts))
        off, on = out
        self.assertGreater(on['healed'], 0)
        self.assertGreater(on['time'], off['time'])
        self.assertNotIn('pe_casts', off)

    def test_powers_pause_enemies(self):
        # A PE power pauses the enemies (user observation): a longer cast animation adds no hits.
        class Fixed:
            def sample(self, rng): return 600
        def run(cast):
            opts = dict(hp=300, serial_action=True, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=120),
                        pe=dict(spells=['Heal1', 'Heal2'], cast_updates=cast))
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=20, stat22=66, offense=175, defense=210),
                                [foe(1500)], Fixed(), random.Random(2), time_cap=90.0, source_options=opts)
        short, long = run(10), run(600)
        self.assertGreater(long['pe_casts'], 0)
        self.assertGreater(long['pe_pause_s'], short['pe_pause_s'])
        self.assertEqual(long['pe_casts'], short['pe_casts'])
        self.assertEqual(long.get('hits_taken', 0), short.get('hits_taken', 0))

    def _fight(self, pe, hp=150, power=120, foe_hp=4000, level=20, **extra):
        class Fixed:
            def sample(self, rng): return 600
        opts = dict(hp=hp, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=power), pe=pe, **extra)
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=level, stat22=66, offense=175, defense=210),
                            [foe(foe_hp)], Fixed(), random.Random(2), time_cap=120.0, source_options=opts)

    def test_revive_item_and_preraise(self):
        dead = self._fight(dict(spells=[], start=0))
        item = self._fight(dict(spells=[], start=0, bag={0x12: 1}))
        pre = self._fight(dict(spells=[], start=1200, script={'Preraise': 1}), level=33)
        self.assertNotIn('revived', dead)
        self.assertEqual(item['revive_item'], 1)
        self.assertEqual(pre['revive_preraise'], 1)
        self.assertGreater(item['time'], dead['time'])

    def test_gene_heal_ticks(self):
        out = self._fight(dict(spells=[], start=500, script={'GeneHeal': 1}), hp=400, power=60)
        self.assertEqual(out['pe_cast_GeneHeal'], 1)
        self.assertGreater(out['gene_healed'], 0)

    def test_steals_need_armor_bit(self):
        # Battle_ApplyEnemyAttack: steals only with armor effect bit 0x10 (literal source), 40% each.
        from pe_weapon_sim.economy import source_stats
        base = dict(source_stats.player_inputs(20, None))
        def run(fx):
            class Fixed:
                def sample(self, rng): return 600
            aya = dict(base, armor_effect_flags=fx)
            opts = dict(hp=10 ** 6, player_status=True, steals=True, pe=dict(spells=[], start=0, bag={0x06: 20}),
                        enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=30, effect_type=10))
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [foe(3000)], Fixed(),
                                random.Random(2), time_cap=60.0, source_options=opts)
        self.assertNotIn('status_stole_item', run(0))
        self.assertGreater(run(0x10).get('status_stole_item', 0), 0)

    def test_energy_shot_spends_all_pe(self):
        out = self._fight(dict(spells=[], start=500, script={'EnergyShot': 1}), hp=10 ** 6, power=10)
        self.assertGreater(out['energy_shot_damage'], 0)

    def test_barrier_and_haste_in_combat(self):
        class Fixed:
            def sample(self, rng): return 600
        def run(script):
            opts = dict(hp=10 ** 6, player_max_hp=300, enemy_defaults=dict(charge_step=90, windup=10, recovery=10, power=120),
                        pe=dict(spells=[], start=500, script=script, max_hp=300))
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=20, stat22=66, offense=175, defense=210),
                                [foe(3000)], Fixed(), random.Random(2), time_cap=60.0, source_options=opts)
        base, barrier, haste = run({}), run({'Barrier': 1}), run({'Haste': 1})
        self.assertGreater(barrier['barrier_absorbed'], 0)
        self.assertLess(barrier['damage_taken'], base['damage_taken'])
        self.assertEqual(haste['pe_cast_Haste'], 1)


if __name__ == '__main__':
    unittest.main()
