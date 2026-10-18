"""Aya's incoming status effects (Battle_ApplyEnemyAttack / Entity_UpdateTimers ports)."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.economy.source_stats import aya_stats, player_inputs
from pe_weapon_sim.enemy_catalog import lookup
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.player_status import PlayerStatus, armor_effect_flags, POISON, DARKNESS, STIFF_LOCK, STIFF_SLOW, HASTE
from pe_weapon_sim.tests.test_source_combat import config, foe


def roll(v): return lambda: v


class ApplyTests(unittest.TestCase):
    def test_poison_sets_timer_step_period_once(self):
        s = PlayerStatus(28, 10)
        self.assertEqual(s.apply(1, 3, 78, roll(0), 300), (300, 'poison'))
        self.assertEqual((s.flags & 3, s.timers['poison'], s.poison_step, s.poison_period), (POISON, 9000, 3, 78))
        self.assertEqual(s.apply(1, 9, 9, roll(0), 300)[1], 'already')
        self.assertEqual(s.poison_step, 3)

    def test_armor_resist_uses_bits(self):
        s = PlayerStatus(28, 10, effect_flags=armor_effect_flags([1]))      # tail effect 1 -> 0x1
        self.assertEqual(s.apply(1, 3, 78, roll(69), 300)[1], 'resisted')   # 70% poison resist
        self.assertEqual(s.apply(1, 3, 78, roll(70), 300)[1], 'poison')
        d = PlayerStatus(28, 10, effect_flags=armor_effect_flags([3]))      # 0x4 -> darkness
        self.assertEqual(d.apply(4, 0, 0, roll(59), 300)[1], 'resisted')

    def test_cure_immunity_consumed(self):
        s = PlayerStatus(28, 10, flags=0x30)
        self.assertEqual(s.apply(4, 0, 0, roll(0), 300)[1], 'immunity used')
        self.assertEqual(s.flags & 0x30, 0)

    def test_stiffness_removes_haste_and_lock_over_slow(self):
        s = PlayerStatus(28, 10, flags=HASTE)
        self.assertEqual(s.apply(6, 0, 0, roll(0), 300)[1], 'stiffness slow')
        self.assertEqual(s.flags & (HASTE | 0xC0), STIFF_SLOW)
        self.assertEqual(s.apply(6, 0, 0, roll(0), 300)[1], 'already')
        self.assertEqual(s.apply(5, 0, 0, roll(0), 300)[1], 'stiffness lock')
        self.assertEqual(s.apply(6, 0, 0, roll(0), 300)[1], 'already')       # slow can't replace lock

    def test_hp_fraction_effects(self):
        s = PlayerStatus(28, 10)
        self.assertEqual(s.apply(8, 0, 0, roll(0), 301)[0], 150)
        self.assertEqual(s.apply(16, 0, 0, roll(0), 301)[0], 225)
        self.assertEqual(s.apply(9, 0, 0, roll(0), 301)[0], 1)
        b = PlayerStatus(28, 10, flags=0x200)                                 # Barrier blocks 8 / 16
        self.assertEqual(b.apply(8, 0, 0, roll(0), 301)[0], 301)

    def test_defense_down_flag_has_no_timer(self):
        s = PlayerStatus(28, 10); s.apply(7, 0, 0, roll(0), 300)
        for _ in range(5000): s.tick()
        self.assertTrue(s.flags & 0x1000)


class TickTests(unittest.TestCase):
    def test_poison_damage_cadence_and_duration(self):
        s = PlayerStatus(28, 10); s.apply(1, 3, 78, roll(0), 300)
        lost = [s.tick() for _ in range(901)]
        self.assertEqual(sum(1 for x in lost if x), 11)                        # every 78 updates within 900
        self.assertEqual([i for i, x in enumerate(lost) if x][:2], [78, 156])  # reset to 0, then ++ the same tick
        self.assertEqual(s.flags & 3, 0)                                        # 9000 / 10 updates

    def test_darkness_duration_by_level_step(self):
        s = PlayerStatus(aya_stats(33)['status_step3c'], 10); s.apply(4, 0, 0, roll(0), 300)
        n = 0
        while s.dark: s.tick(); n += 1
        self.assertEqual(n, -(-9000 // 28))


class InputsTests(unittest.TestCase):
    def test_status_steps_and_catalog(self):
        self.assertEqual((aya_stats(33)['status_step3c'], aya_stats(33)['status_step3e']), (28, 10))
        self.assertEqual(lookup(dict(loc='126', name='0x0012'), C)['status_period'], 30)


class CombatTests(unittest.TestCase):
    def test_poison_adds_damage_and_darkness_cuts_range(self):
        class Fixed:
            def __init__(self, d): self.d = d
            def sample(self, rng): return self.d
        aya = player_inputs(21, None)
        def run(ps, d=800):
            enemy = {**foe(100000), 'loc': '126', 'name': '0x0012'}
            return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), aya, [enemy], Fixed(d),
                                random.Random(5), time_cap=30.0,
                                source_options=dict(shared_cells=C, effect_actions=True, static_enemy_catalog=True,
                                                    player_status=ps, hp=296, enemy_defaults=dict(source_action_slot=0)))
        self.assertGreater(run(True)['damage_taken'], run(False)['damage_taken'])
        self.assertGreater(run(True).get('player_poison', 0), 0)
        with self.assertRaises(ValueError):
            engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=21, stat22=67, offense=180),
                         [foe(100)], Fixed(500), random.Random(1), time_cap=1.0, source_options=dict(player_status=True))


if __name__ == '__main__':
    unittest.main()
