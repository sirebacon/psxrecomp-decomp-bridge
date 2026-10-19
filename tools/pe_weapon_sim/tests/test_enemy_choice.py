"""Distance-gated enemy attack choice (enemy_choice.py) and its source_combat wiring."""
import random, unittest

from pe_weapon_sim import engine, rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.enemy_choice import GatedEnemy, Interval, choice_profile, slot_plans
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C
from pe_weapon_sim.source_enemy import EnemyClock
from pe_weapon_sim.tests.test_source_combat import config, foe

FARM = dict(loc='358', name='0x000A')       # map 358 actor 4: slot 0 below 630, slot 3 above 1000


def plan(lo=None, hi=None, power=10, slot=0, windup=5, recovery=5):
    iv = dict(lo=lo, lo_strict=True, hi=hi, hi_strict=True)              # lo < d < hi, game units
    return dict(kind='anim', windup=windup, recovery=recovery, reset=False,
                power=dict(power=power, action_slot=slot), interval=iv)


def run_enemy(e, n):
    out = []
    for i in range(n):
        strike, _ = e.tick()
        if strike: out.append((i, e.current['action_slot']))
    return out


class CatalogTests(unittest.TestCase):
    def test_farming_enemy_guards(self):
        rows = {r['slot']: Interval.from_dict(r['interval']) for r in choice_profile(FARM, C)}
        self.assertEqual(set(rows), {0, 3})
        self.assertTrue(rows[0].contains(629) and not rows[0].contains(630))
        self.assertTrue(rows[3].contains(1001) and not rows[3].contains(1000))

    def test_farming_enemy_plans(self):
        p = slot_plans(FARM, C)
        self.assertEqual((p[0]['kind'], p[0]['windup'], p[0]['recovery']), ('window', 9, 18))   # early bound
        late = slot_plans(FARM, C, 'late')[0]
        self.assertEqual((late['windup'], late['recovery']), (21, 6))
        self.assertEqual(p[3]['kind'], 'noeffect')                     # slot 3 loads no effect: no damage path
        self.assertEqual((p[0]['power']['action_slot'], p[3]['power']['action_slot']), (0, 3))

    def test_unresolved_identity_has_no_plans(self):
        self.assertEqual(slot_plans(dict(loc='333', name='0x001A'), C), {})


class GatedEnemyTests(unittest.TestCase):
    def make(self, plans, d, **kw):
        return GatedEnemy(EnemyClock(9000, charge=9000), plans, distance=d, aya_radius=100,
                          rng=random.Random(1), **kw)

    def test_distance_picks_slot(self):
        plans = {0: plan(hi=630, slot=0), 3: plan(lo=1000, slot=3)}
        self.assertEqual(run_enemy(self.make(plans, 500), 6)[0][1], 0)
        self.assertEqual(run_enemy(self.make(plans, 1200), 6)[0][1], 3)

    def test_strike_at_windup_after_decision(self):
        e = self.make({0: plan(hi=630, windup=7)}, 100)
        self.assertEqual(run_enemy(e, 9)[0][0], 7)                     # decide on tick 0, hit 7 ticks later

    def test_no_guard_holds_and_waits(self):
        e = self.make({0: plan(hi=630), 3: plan(lo=1000, slot=3)}, 800)
        self.assertEqual(run_enemy(e, 200), [])
        self.assertGreater(e.stats['none'], 2)
        self.assertEqual(e.clock.charge, 9000)                          # charge is kept
        e.distance = 100
        self.assertTrue(run_enemy(e, 80))

    def test_ambiguous_rule(self):
        plans = {0: plan(hi=900, slot=0), 1: plan(lo=500, slot=1)}
        first = self.make(plans, 700)
        self.assertEqual({s for _, s in run_enemy(first, 600)}, {0})
        uni = self.make(plans, 700, ambiguous='uniform')
        self.assertEqual({s for _, s in run_enemy(uni, 3000)}, {0, 1})
        self.assertGreater(uni.stats['ambiguous'], 0)


class CombatTests(unittest.TestCase):
    def fight(self, d, choice=True, seed=5):
        class Fixed:
            def sample(self, rng): return d
        enemy = {**foe(100000), **FARM}
        return engine.fight(source_behavior_rules(rules.CURRENT), config(rof=1), dict(level=33, stat22=79, offense=350),
                            [enemy], Fixed(), random.Random(seed), time_cap=30.0,
                            source_options=dict(shared_cells=C, static_enemy_catalog=True, enemy_choice=choice,
                                                enemy_defaults=dict(source_action_slot=0)))

    def test_close_uses_slot0_far_uses_slot3(self):
        near, far = self.fight(400), self.fight(1400)
        self.assertEqual(near.get('choice_matches'), 1)
        self.assertGreater(near.get('choice_strikes_slot0', 0), 0)
        self.assertEqual(near.get('choice_strikes_slot3', 0), 0)
        self.assertGreater(far.get('choice_strikes_slot3', 0), 0)
        self.assertEqual(far.get('choice_strikes_slot0', 0), 0)

    def test_dead_band_never_attacks(self):
        r = self.fight(800)
        self.assertEqual(r['damage_taken'], 0)
        self.assertGreater(r.get('choice_waits', 0), 0)

    def test_opt_in(self):
        self.assertNotIn('choice_matches', self.fight(400, choice=False))


if __name__ == '__main__':
    unittest.main()
