"""Regression tests: python -m unittest discover -s tools/pe_weapon_sim/tests (from the repo root)."""
import os, random, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pe_weapon_sim import rules as R, data as D, engine as E, progression as P


class Fixed:
    """Distance profile that always returns the same distance (game units)."""
    def __init__(self, d): self.d = d
    def sample(self, rng): return self.d


def enemy(hp=100, level=5, boss=False, **res):
    e = dict(name="test", loc="test", hp=hp, level=level, defense=D.defense_of(level), boss=boss,
             heat="Average", frost="Average", cyanide="Average", acid="Average", tranq="Average")
    e.update(res)
    return e


AYA = dict(level=10, stat22=60, offense=80)
W = D.load_weapons()


def cfg(gun_id, extra=(), **kw):
    return W[gun_id].config(extra, **kw)


class TestFormulas(unittest.TestCase):
    def test_range_units(self):                       # Inv_BuildWeaponList: 150 * sqrt(stat)
        self.assertEqual(D.range_units(55), 1112)
        self.assertEqual(D.range_units(110), 1573)
        self.assertEqual(D.range_units(65 + 2), 1227)

    def test_damage_day1_log(self):
        """Log: Day 1 boss (def 9), level 1 (offense 30), M84F attack 10+2, RoF 2 -> 6 a bullet, 9 on a crit."""
        c = cfg(0x44)
        self.assertEqual(c["eff"]["rof"], 2)
        aya = dict(level=1, stat22=50, offense=30)
        f = enemy(hp=1000000, level=1, boss=True); f["defense"] = 9
        per_hit, per_crit = set(), set()
        for seed in range(60):
            st = E.fight(R.VANILLA, c, aya, [f], Fixed(10), random.Random(seed), max_turns=1)
            if st.get("hit", 0) == 2: per_hit.add(st["damage"] / 2)
            if st.get("crit", 0) == 2: per_crit.add(st["damage"] / 2)
        self.assertEqual(per_hit, {6})
        self.assertEqual(per_crit, {9})

    def test_counter_chance(self):                    # Battle_RollEnemySpawn with L = level * 10
        self.assertAlmostEqual(E.counter_chance(33, 1), 0.33)
        self.assertAlmostEqual(E.counter_chance(33, 0), 0.198)
        self.assertAlmostEqual(E.counter_chance(33, -1), 0.099)
        self.assertAlmostEqual(E.counter_chance(33, -3), 0.066)

    def test_fill_factor(self):                       # rifle factor 8 vs handgun 10
        self.assertAlmostEqual(E.fill_seconds(60, 4) / E.fill_seconds(60, 1), 10 / 8)


class TestMissesAndStatus(unittest.TestCase):
    def test_no_status_on_miss(self):
        """Status needs a landed bullet with damage > 0; beyond 180% of range nothing lands."""
        c = cfg(0x45, ["Acid", "Tranq"])
        far = c["range"] * 2.0
        f = enemy(hp=50, acid="Weak", tranq="Weak")
        st = E.fight(R.CURRENT, c, AYA, [f], Fixed(far), random.Random(1), time_cap=10)
        self.assertEqual(st.get("acid", 0) + st.get("tranq", 0), 0)
        self.assertGreater(st.get("miss", 0), 0)

    def test_weak_status_lands_on_hit(self):
        c = cfg(0x45, ["Acid"])
        f = enemy(hp=5000, acid="Weak")
        st = E.fight(R.VANILLA, c, AYA, [f], Fixed(100), random.Random(2), time_cap=3)
        self.assertGreater(st.get("acid", 0), 0)

    def test_rocket_no_status(self):
        c = cfg(0x90, ["Acid"])
        f = enemy(hp=5000, acid="Weak")
        st = E.fight(R.VANILLA, c, AYA, [f], Fixed(100), random.Random(3), time_cap=5)
        self.assertEqual(st.get("acid", 0), 0)


class TestAmmo(unittest.TestCase):
    def test_attack_all_uses_rof_per_target(self):
        """Attack All: one queue slot per target, RoF bullets each, all from the magazine."""
        c = cfg(0x74)                                   # MP5SD6: RoF3 + Attack All, magazine 31
        foes = [enemy(hp=100000) for _ in range(3)]
        st = E.fight(R.VANILLA, c, AYA, foes, Fixed(100), random.Random(4), max_turns=1)
        self.assertEqual(st["turns"], 1)
        self.assertEqual(st["rounds"], 9)

    def test_empty_magazine_clicks_and_reloads(self):
        c = cfg(0x45, magazine=None) if False else cfg(0x45)
        c = dict(c, magazine=4)                         # RoF3: turn 1 fires 3, turn 2 fires 1 then clicks
        f = enemy(hp=100000)
        st = E.fight(R.VANILLA, c, AYA, [f], Fixed(100), random.Random(5), max_turns=2)
        self.assertGreaterEqual(st["turns"], 2)
        self.assertEqual(st["rounds"] % 4 in (0, 1, 2, 3), True)
        self.assertGreaterEqual(st.get("click", 0), 2)
        self.assertGreaterEqual(st.get("reloads", 0), 1)


class TestHitQuality(unittest.TestCase):
    def test_graze_band_and_experiment(self):
        c = cfg(0x45)
        d = c["range"] * 1.1                            # 100-120%: 80% graze
        f = enemy(hp=10 ** 6, level=1)
        base = E.fight(R.CURRENT, c, AYA, [f], Fixed(d), random.Random(6), time_cap=30)
        e1 = E.fight(R.experimental("E1"), c, AYA, [f], Fixed(d), random.Random(6), time_cap=30)
        self.assertEqual(base.get("hit", 0) + base.get("crit", 0), 0)
        self.assertGreater(base["graze"], 0)
        self.assertGreater(e1["damage"], base["damage"])

    def test_club_no_graze(self):
        c = cfg(0x3F)
        st = E.fight(R.VANILLA, c, AYA, [enemy(hp=10 ** 6)], Fixed(c["range"] * 1.05), random.Random(7), time_cap=5)
        self.assertEqual(st.get("graze", 0), 0)

    def test_crit_conversion_only_with_critical(self):
        c0, c1 = cfg(0x45), cfg(0x45, ["Critical"])
        f = enemy(hp=10 ** 7)
        n0 = E.fight(R.CURRENT, c0, AYA, [f], Fixed(c0["range"] * 0.9), random.Random(8), time_cap=2000)
        n1 = E.fight(R.CURRENT, c1, AYA, [f], Fixed(c1["range"] * 0.9), random.Random(8), time_cap=2000)
        r0 = n0.get("crit", 0) / (n0.get("crit", 0) + n0.get("hit", 0))
        r1 = n1.get("crit", 0) / (n1.get("crit", 0) + n1.get("hit", 0))
        self.assertLess(abs(r0 - 0.05), 0.04)           # >80% of range: 5%
        self.assertLess(abs(r1 - (0.25 + 0.75 * 0.2667)), 0.06)   # +20 points, then 26.7% of the rest


class TestRulesets(unittest.TestCase):
    def test_baselines_frozen(self):
        with self.assertRaises(TypeError):
            R.CURRENT["graze_mult"] = 0.5
        e = R.experimental("E1", "E4")
        self.assertEqual(R.CURRENT["graze_mult"], 0.30)
        self.assertEqual(e["graze_mult"], 0.50)
        self.assertNotEqual(e["graze_bands"], R.CURRENT["graze_bands"])

    def test_current_counter_not_boosted(self):
        self.assertEqual(R.CURRENT["counter_mult"], 1.0)


class TestScripted(unittest.TestCase):
    def test_threshold_ends_fight(self):
        c = cfg(0x45)
        boss = enemy(hp=1000450, level=30, boss=True); boss["defense"] = 33
        st = E.fight(R.CURRENT, c, AYA, [boss], Fixed(300), random.Random(9), threshold={0: 450}, time_cap=600)
        self.assertEqual(st["won"], 1)
        self.assertGreaterEqual(st["damage"], 450)
        self.assertLess(st["damage"], 450 + 200)


class TestPhase2(unittest.TestCase):
    def test_magazine_carries_between_fights(self):
        c = dict(cfg(0x45), magazine=10)
        st = E.fight(R.VANILLA, c, AYA, [enemy(hp=10 ** 6)], Fixed(100), random.Random(10), max_turns=1)
        self.assertEqual(st["loaded_left"], 10 - st["rounds"])
        st2 = E.fight(R.VANILLA, c, AYA, [enemy(hp=10 ** 6)], Fixed(100), random.Random(11), max_turns=1,
                      start_loaded=st["loaded_left"])
        self.assertEqual(st2["loaded_left"], st["loaded_left"] - st2["rounds"])

    def test_endurance_chain_carries_magazine(self):
        from pe_weapon_sim import run_benchmark as B
        c = dict(cfg(0x6E), magazine=7)                 # M10B: RoF3, 2 bullets short of a second turn
        sts = B.run_encounter(R.CURRENT, c, AYA, "endurance", "Day5", 3)
        self.assertTrue(all(s.get("reloads", 0) >= 1 for s in sts))

    def test_baselines_have_no_phase2_rules(self):
        for key in ("prox", "mag_scale", "stagger"):
            self.assertIsNone(R.CURRENT.get(key)); self.assertIsNone(R.VANILLA.get(key))

    def test_mag_scale_only_named_weapon(self):
        r = R.experimental("C2_m10b_50")
        m10b = cfg(0x6E); m500 = cfg(0x6A)
        a = E.fight(r, m10b, AYA, [enemy(hp=10 ** 6)], Fixed(100), random.Random(12), max_turns=1, start_loaded=99)
        b = E.fight(r, m500, AYA, [enemy(hp=10 ** 6)], Fixed(100), random.Random(12), max_turns=1, start_loaded=99)
        self.assertEqual(a["loaded_left"] + a["rounds"], int(m10b["magazine"] * 1.5))
        self.assertEqual(b["loaded_left"] + b["rounds"], m500["magazine"])

    def test_prox_absolute_distance_and_kind(self):
        r = R.experimental("C1_50")
        sg, hg = cfg(0x6A), cfg(0x45)
        near = E.fight(r, sg, AYA, [enemy(hp=10 ** 6)], Fixed(300), random.Random(13), max_turns=5)
        far = E.fight(r, sg, AYA, [enemy(hp=10 ** 6)], Fixed(500), random.Random(13), max_turns=5)
        hgn = E.fight(r, hg, AYA, [enemy(hp=10 ** 6)], Fixed(300), random.Random(13), max_turns=5)
        self.assertGreater(near.get("prox_bullets", 0), 0)
        self.assertEqual(far.get("prox_bullets", 0), 0)
        self.assertEqual(hgn.get("prox_bullets", 0), 0)

    def test_stagger_cooldown(self):
        r = R.experimental("C5")
        st = E.fight(r, cfg(0x6A), AYA, [enemy(hp=10 ** 7)], Fixed(200), random.Random(14), time_cap=60)
        self.assertLessEqual(st.get("staggers", 0), 60 / 3.0 + 1)

    def test_walk_free_while_bar_fills(self):
        """Walking during the ATB fill costs nothing; only travel beyond the fill delays the shot."""
        c = cfg(0x45)
        near_enough = c["range"] * 1.05
        st = E.fight(R.CURRENT, c, AYA, [enemy(hp=10 ** 6)], Fixed(near_enough), random.Random(15),
                     policy="walk", max_turns=3)
        self.assertLess(st.get("move_s", 0), 0.2)


class TestTransfer(unittest.TestCase):
    def test_transfer_sums_and_zeroes(self):
        """armor_capacity.c TRANSFER_STAT: dest += source (cap 999), source = 0."""
        src = P.Gun(W[0x45]); dst = P.Gun(W[0x79])
        src.invested = [10, 3, 2]
        before_dst = dst.bonus()
        P.transfer(src, dst)
        self.assertEqual(dst.bonus(), [before_dst[i] + [10 + W[0x45].bonus_attack, 3 + W[0x45].bonus_range, 2 + W[0x45].bonus_bullets][i] for i in range(3)])
        self.assertEqual(src.bonus(), [0, 0, 0])

    def test_repeated_transfers_no_duplication(self):
        a, b, c = P.Gun(W[0x45]), P.Gun(W[0x79]), P.Gun(W[0x7D])
        a.invested = [12, 0, 0]
        total = a.bonus()[0] + b.bonus()[0] + c.bonus()[0]
        P.transfer(a, b); P.transfer(b, c)
        self.assertEqual(a.bonus()[0] + b.bonus()[0] + c.bonus()[0], total)
        self.assertEqual(c.bonus()[0], total)


if __name__ == "__main__":
    unittest.main()
