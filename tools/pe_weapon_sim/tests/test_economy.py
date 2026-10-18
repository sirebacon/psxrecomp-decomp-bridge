"""Phase 3 economy regression tests: python -m unittest discover -s tools/pe_weapon_sim/tests (repo root)."""
import os, random, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pe_weapon_sim import rules as CR
from pe_weapon_sim.economy import (acquisition as AQ, bp as BP, equipment as EQ, evaluation as EV, inventory as INV,
                                   loot as LT, playthrough as PT, policies as PO, rules as ER, tables as T)

CAMP = AQ.load_campaign()
M10B, MAG, M84F, M9 = 0x6E, 0x82, 0x44, 0x45


class Never(random.Random):
    """Every roll fails (returns the top of its range)."""
    def randrange(self, n): return n - 1


class Always(random.Random):
    def randrange(self, n): return 0


def view(**kw):
    return LT.LootView(**kw)


class TestBP(unittest.TestCase):
    def test_enemy_bp_minus_hits(self):
        self.assertEqual(BP.enemy_bp(31, 3, 0), 31)
        self.assertEqual(BP.enemy_bp(31, 3, 4), 19)
        self.assertEqual(BP.enemy_bp(9, 4, 5), 0)

    def test_banked_only_on_level_up_and_capped(self):
        L = BP.Ledger(cap=250)
        L.award(120, 0, 1)
        self.assertEqual((L.banked, L.pool, L.can_spend()), (0, 120, False))
        L.level_up(1)
        self.assertEqual((L.banked, L.pool), (120, 0))
        L.award(200, 0, 2); L.level_up(2)
        self.assertEqual((L.banked, L.capped), (250, 70))
        L.check()

    def test_spend_cost_no_overspend(self):
        L = BP.Ledger()
        L.award(250, 10, 1); L.level_up(1)
        L.spend("attack", 1); L.spend("range", 1)
        with self.assertRaises(ValueError):
            L.spend("range", 1)
        self.assertEqual((L.banked, L.spent["attack"], L.spent["range"]), (50, 100, 100))
        L.check()

    def test_active_time_and_capacity(self):
        a = BP.Aya(); a.exp = T.LEVEL_EXP[20]
        self.assertEqual((a.level, a.stat22), (21, 70))
        a.at_bought += 1
        self.assertEqual(a.stat22, 71)
        a.cap_bought += 2
        self.assertEqual(a.capacity(), T.capacity_of(23))
        self.assertEqual(BP.Aya().capacity(armor_bag=4), T.capacity_of(1) + 4)


class TestEquipment(unittest.TestCase):
    def test_bp_bonus_transfers_with_provenance(self):
        src, dst = EQ.Item(M9, "t", "D1"), EQ.Item(M84F, "t", "D1")
        src.add_bonus(2, 3, ("bp", src.uid))
        before = list(src.bonus)
        res = EQ.transfer_stats(src, dst, super_tool=False)
        self.assertEqual(res["moved"], before)
        self.assertFalse(src.alive)
        self.assertEqual(src.bonus, [0, 0, 0])
        self.assertEqual(dst.origin_totals(2)["bp"], 3)
        dst.check()

    def test_cap_and_excess_lost(self):
        src, dst = EQ.Item(M9, "t", "D1"), EQ.Item(M84F, "t", "D1")
        dst.add_bonus(0, 999 - dst.bonus[0], ("bp", dst.uid))
        src.add_bonus(0, 10, ("bp", src.uid))
        res = EQ.transfer_stats(src, dst, super_tool=True)
        self.assertEqual(dst.bonus[0], 999)
        self.assertGreater(res["lost"][0], 0)
        self.assertTrue(src.alive)
        dst.check()

    def test_super_tool_keeps_donor_no_double_extraction(self):
        src, dst = EQ.Item(M9, "t", "D1"), EQ.Item(M84F, "t", "D1")
        EQ.transfer_stats(src, dst, super_tool=True)
        total = list(dst.bonus)
        self.assertTrue(src.alive)
        EQ.transfer_stats(src, dst, super_tool=True)
        self.assertEqual(dst.bonus, total)

    def test_base_stats_never_transfer(self):
        src, dst = EQ.Item(MAG, "t", "D5"), EQ.Item(M84F, "t", "D1")
        base = list(dst.base)
        EQ.transfer_stats(src, dst, super_tool=False)
        self.assertEqual(dst.base, base)

    def test_nontransferable(self):
        with self.assertRaises(EQ.TransferError):
            EQ.transfer_stats(EQ.Item(0x61, "t", "Disc2"), EQ.Item(M84F, "t", "D1"), False)

    def test_mod_transfer_group_rule_and_no_room(self):
        code = T.GUN_FX_CODE["2Cmd"]
        dst = EQ.Item(M84F, "t", "D1"); dst.mods = [1, 0]
        EQ.transfer_mod(EQ.Item(0x47, "t", "Disc2"), dst, code, super_tool=False)
        self.assertIn(code, dst.mods)
        full = EQ.Item(M84F, "t", "D1"); full.mods = [1]
        with self.assertRaises(EQ.TransferError):
            EQ.transfer_mod(EQ.Item(0x47, "t", "Disc2"), full, code, False)
        full2 = EQ.Item(M84F, "t", "D1"); full2.mods = [1]
        EQ.transfer_mod(EQ.Item(M9, "t", "D2-4"), full2, 2, False)      # RoF3 replaces RoF2
        self.assertEqual(full2.mods, [2])

    def test_booster(self):
        g = EQ.Item(M10B, "t", "D5")
        b0 = g.bonus[2]
        EQ.apply_booster(g, 0x25 + 2)
        self.assertEqual(g.bonus[2], b0 + 3)
        self.assertEqual(g.origin_totals(2)["booster"], 3)
        with self.assertRaises(EQ.TransferError):
            EQ.apply_booster(g, 0x29)

    def test_magazine_upgrade(self):
        g = EQ.Item(M10B, "t", "D5")
        self.assertEqual(g.magazine(), 7)
        g.add_bonus(2, 1, ("bp", g.uid))
        self.assertEqual((g.magazine(), g.cfg()["magazine"]), (8, 8))

    def test_permit_slot_cap(self):
        g = EQ.Item(M10B, "t", "D5")
        n = 0
        while EQ.permit_slot(g): n += 1
        self.assertEqual((g.slots(), n), (7, 3))
        self.assertFalse(EQ.permit_slot(EQ.Item(0x6A, "t", "Disc2")))   # M500: 8 slots above its cap 5

    def test_salvage_payout_matches_log(self):
        cat = EQ.Catalog()
        g = EQ.Item(0x6F, "t", "D2-4")
        self.assertEqual(EQ.salvage_payout(g, cat.unlocked["gun"]), 15)   # logged: M11 +1/0/1 2 mods = 15
        cat.unlock_from(g)
        self.assertEqual(EQ.salvage_payout(g, cat.unlocked["gun"]), 19)


class TestLoot(unittest.TestCase):
    def test_pity_threshold_and_reset(self):
        st = LT.LootState(random.Random(1))
        self.assertEqual(st.guarantee(), 25)
        st.rare_dry = 24
        self.assertIsNotNone(st.roll(10, view()))
        self.assertEqual((st.rare_dry, st.pity_hits, st.chance_permille()), (0, 1, 40))

    def test_lucky_find_doubles_progress(self):
        a, b = LT.LootState(Never()), LT.LootState(Never())
        a.roll(10, view()); b.roll(10, view(lucky_find=True))
        self.assertEqual((a.rare_dry, b.rare_dry), (1, 2))

    def test_cascade_priority_and_fallthrough(self):
        all_econ = [m[0] for m in LT.ECON_MODS]
        self.assertEqual(LT.LootState(Always()).pick(10, view())[0], "econ")
        self.assertEqual(LT.LootState(Always()).pick(10, view(econ_unlocked=all_econ)), ("item", T.SUPER_TOOL))
        out = LT.LootState(Always()).pick(10, view(econ_unlocked=all_econ, super_tool_kit=True, permits_held=2))
        self.assertEqual(out, ("item", T.DUPER_JUNK))

    def test_tool_chance_feedback(self):
        st = LT.LootState(random.Random(1))
        self.assertEqual(st.skip("tool", view(tools_held=0), 0), (False, 85))
        self.assertEqual(st.skip("tool", view(tools_held=3), 0), (False, 20))
        self.assertTrue(st.skip("tool", view(tools_held=5), 0)[0])
        self.assertTrue(st.skip("tool", view(tool_kit=True), 0)[0])

    def test_guarantees_only_while_not_skipped(self):
        st = LT.LootState(Never())
        for _ in range(7):
            st.pick(10, view())
        self.assertEqual(st.econ_since, 7)
        self.assertEqual(st.pick(10, view())[0], "econ")
        st2 = LT.LootState(Never())
        for _ in range(5):
            st2.pick(10, view(permits_held=2))
        self.assertEqual(st2.permit_since, 0)

    def test_booster_tier_by_exp(self):
        all_econ = [m[0] for m in LT.ECON_MODS]
        for exp, tier in ((5, 0), (30, 1), (100, 2), (500, 3)):
            class R(random.Random):
                def randrange(self, n): return n - 1 if n in (100, 1000) else 0
            out = LT.LootState(R()).pick(exp, view(econ_unlocked=all_econ, tools_held=5))
            self.assertEqual(out, ("item", 0x1D + tier))

    def test_battle_junk(self):
        st = LT.LootState(random.Random(1))
        self.assertEqual(st.battle_junk(28, 0, False, view()), 5)
        self.assertEqual(st.battle_junk(500, 5, False, view()), 12)
        self.assertEqual(st.battle_junk(500, 5, True, view(scavenger=True)), 37)

    def test_deterministic(self):
        a, b = LT.LootState(random.Random(5)), LT.LootState(random.Random(5))
        self.assertEqual([a.roll(40, view()) for _ in range(200)], [b.roll(40, view()) for _ in range(200)])


class TestInventoryAcquisition(unittest.TestCase):
    def test_inventory_counts(self):
        inv = INV.Inventory()
        self.assertEqual(inv.free(10, "D1"), 10 - INV.RESERVE["D1"])
        inv.count[T.TOOL] = 2; inv.stored_count[T.TOOL] = 1
        self.assertEqual(inv.held(T.TOOL), 3)

    def test_fixed_pickups_unique_farming_repeatable(self):
        ev = AQ.build("typical", CAMP, random.Random(3))
        gear = [e["item"] for e in ev if e["type"] == "gear"]
        self.assertEqual(len(gear), len(set(gear)))
        ev_f = AQ.build("farmer", CAMP, random.Random(3))
        self.assertGreater(sum(e["type"] == "battle" for e in ev_f), sum(e["type"] == "battle" for e in ev))
        comp = AQ.build("completionist", CAMP, random.Random(3))
        self.assertTrue({e["item"] for e in comp if e["type"] == "gear"} >= set(gear))
        self.assertFalse(any(e.get("area") == "Chrysler Building" for e in comp))


class TestPlaythrough(unittest.TestCase):
    P = PO.policy_set()

    def test_mod_ablation_keeps_original_and_other_effects(self):
        from pe_weapon_sim.economy.run_followups import remove_effects
        cfg = dict(power=100, magazine=12, eff=dict(commands=2, quickdraw=True, rof=3, critical=True))
        changed = remove_effects(cfg, "neither")
        self.assertEqual(cfg["eff"]["commands"], 2)
        self.assertTrue(cfg["eff"]["quickdraw"])
        self.assertEqual(changed["eff"], dict(commands=1, rof=3, critical=True))
        self.assertEqual(changed["power"], cfg["power"])
        self.assertEqual(changed["magazine"], cfg["magazine"])

    def test_portfolio_delay_removes_marginal_niche(self):
        from pe_weapon_sim.economy.run_followups import envelope
        main = {e: dict(time_mean=2.0, win=1.0) for e in EV.SCORE_SET}
        second = {e: dict(time_mean=1.5, win=1.0) for e in EV.SCORE_SET}
        free = envelope(main, second)
        charged = envelope(main, second, 0.6)
        self.assertAlmostEqual(free["envelope"], 1.5)
        self.assertAlmostEqual(charged["envelope"], 2.0)
        self.assertFalse(charged["secondary_faster"])

    def test_mod_target_cache_isolates_timing_and_base(self):
        from unittest.mock import patch
        from pe_weapon_sim.economy import surrogate as SG
        pol = self.P["C"].copy()
        run = PT.Run(ER.CURRENT, pol, "typical", 1, CAMP)
        old = SG.TIMING
        PO._TARGET_CACHE.clear()
        try:
            with patch.object(pol, "_target", side_effect=[[1], [2], [3]]) as target:
                SG.TIMING = "overlap"
                self.assertEqual(pol.target_mods(run, run.gun, None), [1])
                SG.TIMING = "serial"
                self.assertEqual(pol.target_mods(run, run.gun, None), [2])
                run.gun.base[2] += 1
                self.assertEqual(pol.target_mods(run, run.gun, None), [3])
                self.assertEqual(target.call_count, 3)
        finally:
            SG.TIMING = old
            PO._TARGET_CACHE.clear()

    def test_checkpoint_equipment_is_independent(self):
        run = PT.Run(ER.CURRENT, self.P["C"], "typical", 1, CAMP)
        run.checkpoint("D1")
        snap = run.checkpoints["D1"]
        run.gun.add_bonus(0, 5, ("bp", run.gun.uid))
        run.gun.mods[0] = 0
        run.worn.add_bonus(0, 3, ("bp", run.worn.uid))
        self.assertEqual(snap["_gun"].bonus, snap["bonus"])
        self.assertEqual(snap["_gun"].effect_names(), snap["mods"])
        self.assertEqual(snap["_armor"].bonus, snap["armor_bonus"])

    def test_spearman_ties(self):
        self.assertAlmostEqual(EV.spearman([1, 1, 2], [1, 2, 3]), 3 ** 0.5 / 2)
        self.assertAlmostEqual(EV.spearman([1, 2, 3], [3, 2, 1]), -1)

    def test_surrogate_cache_separates_timing(self):
        from pe_weapon_sim.economy import surrogate as SG
        old = SG.TIMING
        cfg = EQ.Item(M10B, "timing-test", "D5").cfg()
        aya = dict(stat22=73, offense=200)
        try:
            SG._score.cache_clear()
            SG.TIMING = "overlap"
            overlap = SG.score(cfg, aya, 32)
            SG.TIMING = "serial"
            serial = SG.score(cfg, aya, 32)
            SG._score.cache_clear()
            self.assertEqual(serial, SG.score(cfg, aya, 32))
            self.assertLess(serial, overlap)
            SG.TIMING = "overlap"
            self.assertEqual(overlap, SG.score(cfg, aya, 32))
        finally:
            SG.TIMING = old
            SG._score.cache_clear()

    def test_invariants_and_determinism(self):
        r1 = PT.play(ER.CURRENT, self.P["C"], "typical", 11, CAMP, check=True)
        r2 = PT.play(ER.CURRENT, self.P["C"], "typical", 11, CAMP, check=False)
        self.assertEqual(r1.checkpoints["Disc2"]["bonus"], r2.checkpoints["Disc2"]["bonus"])
        self.assertEqual(r1.ledger.earned, r2.ledger.earned)
        r1.ledger.check()
        self.assertGreaterEqual(r1.junk, 0)
        self.assertTrue(all(v >= 0 for v in r1.inv.count.values()))
        self.assertEqual(list(r1.checkpoints), ["D1", "D2-4", "D5", "Disc2"])
        lv = [r1.checkpoints[p]["level"] for p in r1.checkpoints]
        self.assertEqual(lv, sorted(lv))

    def test_every_bonus_point_has_a_source(self):
        run = PT.play(ER.CURRENT, self.P["C"], "typical", 4, CAMP)
        g = run.gun
        for i in range(3):
            o = g.origin_totals(i)
            self.assertEqual(sum(o.values()), g.bonus[i])
            self.assertTrue(set(o) <= {"intrinsic", "bp", "booster"})
        bp_points = sum(v for it in run.items.values() if it.alive for i in range(3)
                        for (k, _), v in it.prov[i].items() if k == "bp")
        sp = run.ledger.spent
        self.assertLessEqual(bp_points * 100, sp["attack"] + sp["range"] + sp["bullets"] + sp["armor"])

    def test_multi_weapon_ownership(self):
        run = PT.play(ER.CURRENT, self.P["D"], "typical", 4, CAMP)
        uids = [run.main, run.second]
        self.assertTrue(run.second is None or len(set(uids)) == 2)
        self.assertTrue(all(run.items[u].alive for u in uids if u))

    def test_ablation_disables_systems(self):
        a1 = PT.play(ER.ablation("A1"), self.P["C"], "typical", 2, CAMP)
        self.assertEqual(a1.m["donors_harvested"], 0)
        self.assertFalse(a1.m["rare"])
        a3 = PT.play(ER.ablation("A3"), self.P["C"], "typical", 2, CAMP)
        self.assertEqual(a3.ledger.total_spent, 0)

    def test_vanilla_economy(self):
        v = PT.play(ER.VANILLA, self.P["C"], "typical", 2, CAMP)
        self.assertFalse(v.m["rare"]); self.assertLess(v.junk, 300)      # vanilla Junk items only
        self.assertFalse(v.m["wayne_guns"]); self.assertEqual(v.m["permits_used"], 0)

    def test_wayne_not_before_day4(self):
        r = PT.play(ER.CURRENT, self.P["C_wayne"], "typical", 3, CAMP, trace=True)
        first = [x for x in r.log if x["kind"] == "wayne_gun"]
        self.assertTrue(not first or first[0]["phase"] != "D1")

    def test_baselines_frozen(self):
        with self.assertRaises(TypeError):
            ER.CURRENT["bp_cost"] = 50
        with self.assertRaises(TypeError):
            CR.CURRENT["hit_pct"] = {}

    def test_combat_engine_integration(self):
        g = EQ.Item(M10B, "t", "D5")
        res = EV.benchmark(CR.CURRENT, g.cfg(), dict(level=24, stat22=73, offense=200), "D5", n=4,
                           suite=("close_normal", "groups"))
        self.assertGreater(res["close_normal"]["win"], 0)
        self.assertGreater(res["suite_time"], 0)


if __name__ == "__main__":
    unittest.main()
