"""Player investment policies A-I (plus BP-strategy variants). Decisions read only the current
state (no knowledge of future drops); the casual player's randomness uses the policy stream.

All decisions go through Run's transaction methods, so every change is a verified mechanic.
"""
from .. import data as D
from . import surrogate as SG, tables as T

KIND_NAME = {1: "handgun", 2: "shotgun", 3: "machine", 4: "rifle", 5: "grenade", 6: "rocket", 8: "club"}
WAYNE_BY_KIND = {1: 0x66, 2: 0x6E, 3: 0x78, 4: 0x82, 5: 0x8F}
PREF = {   # preference lists (effect names) for list-driven players
    "casual": ["2Cmd", "Quickdraw", "RoF3", "Heat", "Burst", "Critical", "Frost", "Acid"],
    1: ["2Cmd", "Quickdraw", "Critical", "RoF3", "Frost", "Acid", "Burst", "Tranq"],
    2: ["2Cmd", "Burst", "Quickdraw", "Critical", "RoF3", "Frost", "Tranq", "Acid"],
    3: ["2Cmd", "Quickdraw", "RoF7", "Frost", "Critical", "Acid", "AttackAll", "Tranq"],
    4: ["2Cmd", "Quickdraw", "Critical", "Frost", "RoF3", "Acid", "Tranq", "Burst"],
    5: ["2Cmd", "Quickdraw", "Frost", "Acid", "Critical", "RoF3", "Tranq", "Burst"],
}
ECON_ORDER = ["LuckyFind", "Scavenger", "Bargain", "Salvager"]
_TARGET_CACHE = {}


def cfg_with(item, bonus=None, mods=None):
    """Hypothetical loadout of item with other bonuses / effects (no state change)."""
    b = bonus if bonus is not None else item.bonus
    eff = {"rof": 1}
    for m in (mods if mods is not None else item.effects()):
        name = T.GUN_FX.get(m)
        if name in D.MODS:
            k, v = D.MODS[name]; eff[k] = v
        elif name in D.FLAGS:
            eff[name.lower()] = True
    return dict(weapon=T.WEAPONS.get(item.iid), kind=item.kind, power=item.base[0] + b[0],
                range=D.range_units(item.base[1] + b[1]), magazine=max(1, item.base[2] + b[2]), eff=eff)


class Policy:
    def __init__(self, name, label, fav_kind=None, switch_margin=1.05, transfer_on_switch=True, min_donor=1,
                 tool_reserve=0, harvest_prob=1.0, bp_mode="marginal", bp_weights=None, spend_prob=1.0,
                 bullet_align=True, mods="greedy", buy_tools=2, wayne_guns=1, wayne_pick="best",
                 econ_mods=True, two_weapon=False, at_target=0, cap_target=0, armor_target=0, armor_transfer=True,
                 second_share=0.3):
        self.name, self.label = name, label
        self.fav_kind, self.switch_margin, self.transfer_on_switch = fav_kind, switch_margin, transfer_on_switch
        self.min_donor, self.tool_reserve, self.harvest_prob = min_donor, tool_reserve, harvest_prob
        self.bp_mode, self.bp_weights, self.spend_prob = bp_mode, bp_weights or {}, spend_prob
        self.bullet_align, self.mods, self.buy_tools = bullet_align, mods, buy_tools
        self.wayne_guns, self.wayne_pick, self.econ_mods = wayne_guns, wayne_pick, econ_mods
        self.two_weapon, self.at_target, self.cap_target = two_weapon, at_target, cap_target
        self.armor_target, self.armor_transfer, self.second_share = armor_target, armor_transfer, second_share

    def copy(self, name=None, **kw):
        p = Policy(self.name, self.label)
        p.__dict__.update(self.__dict__); p.__dict__.update(kw)
        if name: p.name = name
        return p

    # ---- hooks ---------------------------------------------------------------------------------
    def after_battle(self, run):
        self.maintain(run, at_wayne=False)

    def at_wayne(self, run):
        self.wayne(run)
        self.maintain(run, at_wayne=True)

    def maintain(self, run, at_wayne):
        self.use_boosters(run)
        self.choose_guns(run, at_wayne)
        self.harvest(run, at_wayne)
        self.buy(run)
        self.install_mods(run)
        self.spend_bp(run, at_wayne)
        self.armor(run, at_wayne)
        self.tidy(run)

    # ---- values --------------------------------------------------------------------------------
    def junk_reserve(self, run):
        start = getattr(self, "wayne_save_from", "D5")
        phases = ("D1", "D2-4", "D5", "Disc2")
        if run.econ["wayne_junk_cost"] and len(run.m["wayne_guns"]) < self.wayne_guns and \
                phases.index(run.phase) >= phases.index(start):
            return run.econ["wayne_junk_cost"]
        return 0

    def item_value(self, run, it):
        new = [m for m in it.effects() if m not in run.catalog.unlocked[run.catalog.side(it)]]
        return it.bonus_sum() + 3 * len(new) + (1000 if it.uid in (run.main, run.armor, run.second) else 0)

    def make_room(self, run, new_item):
        """Bag full on a pickup: harvest a donor with a Tool if one is carried (frees its slot), else
        dismantle (CURRENT) or discard the least valuable carried gear, unless the new item is the
        least valuable; as a last resort drop one consumable (at most 2 per phase)."""
        carried = [it for it in run.inv.gear.values() if it.uid not in (run.main, run.armor, run.second)]
        donors = [it for it in carried if it.is_gun and it.bonus_sum() > 0 and it.transferable]
        if donors and run.tools_available() > 0 and run.has("donors"):
            run.do_transfer_stats(max(donors, key=lambda x: x.bonus_sum()), run.gun, "make room")
            if run.free() > 0:
                return True
            carried = [it for it in run.inv.gear.values() if it.uid not in (run.main, run.armor, run.second)]
        if not carried:
            return self._drop_consumable(run)
        worst = min(carried, key=lambda it: self.item_value(run, it))
        if self.item_value(run, worst) > self.item_value(run, new_item) + (2 if new_item.is_gun else 0):
            return self._drop_consumable(run) if self.item_value(run, new_item) >= 3 else False
        if run.econ["catalog"]:
            run.dismantle(worst)
        else:
            run.retire(worst, "discard")
        return run.free() > 0

    def _drop_consumable(self, run):
        cut = run.inv.reserve_cut.get(run.phase, 0)
        if cut >= 2:
            return False
        run.inv.reserve_cut[run.phase] = cut + 1
        run.tx("drop_consumable", phase=run.phase)
        return run.free() > 0

    def hyp_mods(self, run, item):
        """Effects the item could carry now: its own, plus (CURRENT) Catalog effects in its slots."""
        if not (run.econ["catalog"] and run.has("catalog")):
            return item.effects()
        return self.target_mods(run, item, budget=None)

    def hyp_score(self, run, item, extra=None, aya=None):
        b = item.bonus if extra is None else [min(999, item.bonus[i] + extra[i]) for i in range(3)]
        return SG.score(cfg_with(item, b, self.hyp_mods(run, item)), aya or run.aya.combat(), run.defense_ref(), run.crules)

    # ---- guns ----------------------------------------------------------------------------------
    def candidates(self, run, at_wayne):
        pool = list(run.inv.gear.values()) + (list(run.inv.stored.values()) if at_wayne else [])
        guns = [it for it in pool if it.is_gun and it.alive and it.kind != 8 and it.transferable]
        if self.fav_kind:
            fav = [g for g in guns if g.kind == self.fav_kind]
            if fav:
                return fav
        return guns

    def choose_guns(self, run, at_wayne):
        cur = run.gun
        guns = self.candidates(run, at_wayne)
        if self.two_weapon:
            short = [g for g in guns if g.kind != 4] or guns
            rifles = [g for g in guns if g.kind == 4]
            self._switch(run, cur, short, at_wayne)
            if rifles:
                best = max(rifles, key=lambda g: SG.dps(cfg_with(g, None, self.hyp_mods(run, g)), run.aya.combat(),
                                                       run.defense_ref(), "keepaway", 1.0, run.crules))
                if run.second != best.uid and best.uid != run.main:
                    old = run.sec
                    run.equip(best, "second")
                    if old and old.alive and old.bonus_sum() and self.transfer_on_switch:
                        run.do_transfer_stats(old, best, "second switch", at_wayne)
            return
        self._switch(run, cur, guns, at_wayne)

    def _switch(self, run, cur, guns, at_wayne):
        if not guns:
            return
        if self.fav_kind and cur.kind != self.fav_kind and any(g.kind == self.fav_kind for g in guns):
            margin = 0.0                                          # specialist: always move to the class
        else:
            margin = self.switch_margin
        can_move = self.transfer_on_switch and run.has("donors") and run.tools_available(at_wayne) > 0 and cur.bonus_sum() > 0
        cur_s = self.hyp_score(run, cur)
        best, best_s = cur, cur_s
        for g in guns:
            if g.uid == cur.uid:
                continue
            s = self.hyp_score(run, g, cur.bonus if can_move else None)
            if s > best_s * (margin if g.uid != cur.uid else 1) and s > best_s:
                best, best_s = g, s
        if best.uid != cur.uid and best_s > cur_s * margin:
            run.equip(best, "main")
            if can_move:
                keep_old = self.two_weapon and run.second == cur.uid
                run.do_transfer_stats(cur, best, "switch", at_wayne,
                                      super_tool=keep_old and run.inv.count[T.SUPER_TOOL] > 0)
            run.dirty = True

    # ---- Tools ---------------------------------------------------------------------------------
    def harvest(self, run, at_wayne):
        if not run.has("donors"):
            return
        pool = list(run.inv.gear.values()) + (list(run.inv.stored.values()) if at_wayne else [])
        for it in sorted(pool, key=lambda x: -x.bonus_sum()):
            if it.uid in (run.main, run.armor, run.second) or not it.alive or not it.transferable:
                continue
            if it.bonus_sum() < self.min_donor or it.bonus_sum() == 0:
                continue
            if run.tools_available(at_wayne) <= self.tool_reserve:
                break
            if self.harvest_prob < 1 and run.r_pol.random() > self.harvest_prob:
                continue
            if it.is_gun:
                dst = run.gun
                if self.two_weapon and run.sec and it.kind == 4:
                    dst = run.sec
            else:
                dst = run.worn
                if not self.armor_transfer or it.bonus_sum() < max(3, self.min_donor):
                    continue
            run.do_transfer_stats(it, dst, "donor", at_wayne)

    def buy(self, run):
        n = 0
        while run.inv.held(T.TOOL) < self.buy_tools and n < 3:
            p = min(100, run.price(40 + 10 * run.tools_bought))
            if run.junk - p < self.junk_reserve(run) + 30 or not run.buy_tool():
                break
            n += 1

    # ---- mods ----------------------------------------------------------------------------------
    def target_mods(self, run, item, budget):
        """The effect set to aim for on item: greedy by surrogate ("greedy") or a preference list."""
        side = run.catalog.side(item)
        avail = set(item.effects()) | (run.catalog.unlocked[side] if run.econ["catalog"] else set())
        avail = {c for c in avail if c in T.GUN_FX and T.GUN_FX[c] not in ("Steal", "StealAtk")}
        if run.econ["premium_needs_tool"] and not run.inv.has_kit() and run.tools_available() <= 0:
            avail = {c for c in avail if T.GUN_TIER[c] < 2 or c in item.effects()}
        k = item.slots()
        aya = run.aya.combat()
        key = (self.mods, item.iid, k, tuple(item.base), tuple(item.bonus), tuple(sorted(item.effects())), tuple(sorted(avail)),
               aya["stat22"], aya["offense"], run.defense_ref(), run.crules["name"], SG.TIMING)
        hit = _TARGET_CACHE.get(key)
        if hit is not None:
            return list(hit)
        out = self._target(run, item, avail, k, aya)
        if len(_TARGET_CACHE) > 200000:
            _TARGET_CACHE.clear()
        _TARGET_CACHE[key] = tuple(out)
        return out

    def _target(self, run, item, avail, k, aya):
        if self.mods == "greedy":
            chosen = []
            base = SG.score(cfg_with(item, None, chosen), aya, run.defense_ref(), run.crules)
            for _ in range(k):
                best = None
                for c in avail:
                    if c in chosen or (T.gun_group(c) and any(T.gun_group(x) == T.gun_group(c) for x in chosen)):
                        continue
                    s = SG.score(cfg_with(item, None, chosen + [c]), aya, run.defense_ref(), run.crules)
                    if best is None or s > best[0]:
                        best = (s, c)
                if not best or best[0] <= base * 1.002:
                    break
                chosen.append(best[1]); base = best[0]
            return chosen
        pref = PREF["casual"] if self.mods == "casual" else PREF.get(item.kind, PREF[1])
        chosen = []
        for name in pref:
            c = T.GUN_FX_CODE[name]
            if c in avail and not (T.gun_group(c) and any(T.gun_group(x) == T.gun_group(c) for x in chosen)):
                chosen.append(c)
            if len(chosen) >= k:
                break
        for c in item.effects():           # keep built-ins in the remaining slots
            if len(chosen) < k and c not in chosen and not (T.gun_group(c) and any(T.gun_group(x) == T.gun_group(c) for x in chosen)):
                chosen.append(c)
        return chosen

    def install_mods(self, run):
        if not (run.econ["catalog"] and run.has("catalog")):
            self.vanilla_mods(run)
            return
        for item in [run.gun] + ([run.sec] if run.sec else []):
            target = self.target_mods(run, item, None)
            if set(target) - set(item.effects()):
                aya = run.aya.combat()
                s_cur = SG.score(cfg_with(item), aya, run.defense_ref(), run.crules)
                s_tgt = SG.score(cfg_with(item, None, target), aya, run.defense_ref(), run.crules)
                if s_tgt < s_cur * 1.02:          # not worth the Junk (no flip-flopping)
                    continue
            for c in target:
                if c in item.effects():
                    continue
                price, premium = run.catalog.price(item, c, run.price)
                if run.junk - price < self.junk_reserve(run):
                    continue
                if premium and run.tools_available() <= (0 if self.mods == "greedy" else self.tool_reserve):
                    continue
                slot = run.catalog.install_plan(item, c)
                if slot is None:
                    # make room: remove an effect not in the target (Catalog remove; it stays unlocked)
                    drop = [i for i, m in enumerate(item.mods) if m and m not in target]
                    if not drop:
                        continue
                    run.remove_mod(item, drop[0])
                run.install(item, c)
        if self.econ_mods:
            w = run.worn
            for name in ECON_ORDER:
                code = {"Bargain": 17, "Scavenger": 18, "LuckyFind": 19, "Salvager": 20}[name]
                if name in run.econ_unlocked and code not in w.mods and w.free_slots() > 0:
                    if run.junk - run.price(30) >= self.junk_reserve(run):
                        run.install(w, code)

    def vanilla_mods(self, run):
        """VANILLA: effects move only by Tool from a donor carrying them (donor lost)."""
        if not run.has("donors"):
            return
        main = run.gun
        want = self.target_mods_vanilla(run, main)
        for it in list(run.inv.gear.values()):
            if it.uid in (run.main, run.armor, run.second) or not it.is_gun or not it.alive:
                continue
            for c in it.effects():
                if c in want and c not in main.effects() and run.tools_available() > self.tool_reserve:
                    if run.do_transfer_mod(it, main, c, "vanilla mod"):
                        break

    def target_mods_vanilla(self, run, main):
        pref = PREF.get(main.kind, PREF[1])
        return {T.GUN_FX_CODE[n] for n in pref[:main.slots()]}

    # ---- BP ------------------------------------------------------------------------------------
    def spend_bp(self, run, at_wayne=False):
        if not run.has("bp"):
            return
        if self.bp_mode == "end" and not (run.phase == "Disc2" and run.aya.level >= 33):
            return                                   # the run's own habit: hoard until the last level
        guard = 0
        if getattr(self, "spend_at_wayne_only", False):
            if not at_wayne:
                return
            guard = 200 - max(1, run.ledger.banked // run.ledger.cost // 2)    # half of it per visit
        while run.ledger.can_spend() and guard < 200:
            guard += 1
            if self.spend_prob < 1 and not getattr(self, "spend_at_wayne_only", False) and run.r_pol.random() > self.spend_prob:
                return
            cat, item = self.bp_choice(run)
            if cat is None or not run.spend_bp(cat, item):
                return

    def magazine_need(self, run, item):
        eff = item.cfg()["eff"]
        used, _ = SG.volley_bullets(eff, 2.0)
        return used * eff.get("commands", 1)

    def bp_choice(self, run):
        mode = self.bp_mode
        if mode == "end":
            mode = "marginal"
        if mode == "save":
            if not run.m["wayne_guns"] and run.phase != "Disc2":
                return None, None
            mode = "marginal"
        if mode == "at_first" and run.aya.at_bought < self.at_target:
            return "active_time", None
        if mode == "cap_first" and run.aya.cap_bought < self.cap_target:
            return "capacity", None
        if mode == "armor_first" and run.ledger.spent["armor"] // run.ledger.cost < self.armor_target:
            return "armor", None
        if mode in ("at_first", "cap_first", "armor_first"):
            mode = "marginal"
        if self.two_weapon and run.sec:
            spent_w = sum(run.ledger.spent[c] for c in ("attack", "range", "bullets"))
            sec_pts = sum(v for i in range(3) for (k, u), v in run.sec.prov[i].items() if k == "bp" and u == run.sec.uid)
            if spent_w and sec_pts * 100 < self.second_share * spent_w:
                return ("range" if run.sec.base[1] + run.sec.bonus[1] < 200 else "attack"), run.sec
        if self.bullet_align and run.gun.magazine() < self.magazine_need(run, run.gun) and \
                self.magazine_need(run, run.gun) - run.gun.magazine() <= 6:
            return "bullets", run.gun
        if mode == "weights":
            w = self.bp_weights
            tot = max(1, run.ledger.total_spent)
            cat = max(w, key=lambda c: w[c] - run.ledger.spent[c] / tot)
            return cat, None
        return self.marginal(run)

    def marginal(self, run):
        g = run.gun
        aya = run.aya.combat()
        base = self.hyp_score(run, g)
        best = (0.0, None)
        for cat, idx in (("attack", 0), ("range", 1), ("bullets", 2)):
            for k in ((1,) if idx != 2 else (1, 2, 3, 4, 5, 6)):
                ex = [0, 0, 0]; ex[idx] = k
                gain = (self.hyp_score(run, g, ex) / base - 1) / k
                if gain > best[0]:
                    best = (gain, cat)
        at = dict(aya, stat22=aya["stat22"] + 1)
        gain = self.hyp_score(run, g, None, at) / base - 1
        if gain > best[0]:
            best = (gain, "active_time")
        if run.recent_overflow and run.capacity() < 50 and 0.004 > best[0]:
            best = (0.004, "capacity")
        return best[1], None

    # ---- armor, Wayne, tidy --------------------------------------------------------------------
    def armor(self, run, at_wayne):
        pool = [it for it in run.inv.gear.values() if it.is_armor and it.alive and it.transferable]
        best = max(pool, key=lambda a: (a.base[0] + a.bonus[0] + 6 * a.bag_bonus()), default=None)
        cur = run.worn
        if best and best.uid != cur.uid and best.base[0] + 6 * best.bag_bonus() > cur.base[0] + 6 * cur.bag_bonus() + 4:
            if cur.bag_bonus() > best.bag_bonus() and run.free() < 2:
                return
            run.equip(best, "armor")
            if self.armor_transfer and cur.bonus_sum() >= 3 and run.has("donors") and run.tools_available(at_wayne) > self.tool_reserve:
                run.do_transfer_stats(cur, best, "armor switch", at_wayne)

    def use_boosters(self, run):
        for bid in list(run.inv.boosters):
            tgt, idx, amount, _ = T.booster_info(bid)
            if tgt == "weapon":
                item = run.gun
                if self.two_weapon and run.sec and idx == 1:
                    item = run.sec
                run.use_booster(bid, item)
            else:
                run.use_booster(bid, run.worn)

    def wayne(self, run):
        for _ in range(3):
            if len(run.m["wayne_guns"]) >= self.wayne_guns or run.econ["wayne_junk_cost"] is None:
                break
            if run.junk < run.econ["wayne_junk_cost"] or run.phase not in ("D5", "Disc2"):
                break
            owned = {it.iid for it in run.items.values() if it.alive}
            opts = [i for i in T.WAYNE_GUNS if i not in owned]
            if self.fav_kind and self.fav_kind in WAYNE_BY_KIND:
                opts = [i for i in opts if T.ITEMS[i]["kind"] == self.fav_kind] or opts
            if self.two_weapon and run.m["wayne_guns"]:
                opts = [i for i in opts if T.ITEMS[i]["kind"] == 4] or opts
            if not opts:
                break
            if self.wayne_pick == "best":
                from .equipment import Item
                tmp = {i: Item(i, "probe", run.phase, uid=-1) for i in opts}
                pick = max(opts, key=lambda i: self.hyp_score(run, tmp[i], run.gun.bonus))
            else:
                pick = self.wayne_pick if self.wayne_pick in opts else opts[0]
            run.wayne_gun(pick)
        # Mod Permits: main gun first, then the second gun.
        for item in [run.gun] + ([run.sec] if run.sec else []):
            while run.use_permit(item):
                pass
        # Storage: spare Tools beyond 4 in the bag (they still count as held for the cascade).
        for kind in (T.TOOL, T.SUPER_TOOL, T.MOD_PERMIT):
            keep = 4 if kind == T.TOOL else 1
            while run.inv.count[kind] > keep:
                run.inv.count[kind] -= 1; run.inv.stored_count[kind] += 1
        # ... and donors worth keeping until a Tool turns up.
        for it in list(run.inv.gear.values()):
            if it.uid in (run.main, run.armor, run.second):
                continue
            if it.is_gun and it.bonus_sum() >= self.min_donor and run.tools_available(True) == 0:
                run.inv.gear.pop(it.uid); run.inv.stored[it.uid] = it
                run.tx("store", item=it.describe())

    def tidy(self, run):
        """Dismantle carried gear that has nothing left to give (CURRENT); keep free slots."""
        if not run.econ["catalog"]:
            return
        for it in list(run.inv.gear.values()):
            if it.uid in (run.main, run.armor, run.second) or not it.alive:
                continue
            new = [m for m in it.effects() if m not in run.catalog.unlocked[run.catalog.side(it)]]
            if it.bonus_sum() == 0 or (it.bonus_sum() < self.min_donor and run.free() <= 1) or new:
                if it.is_armor and it.base[0] > run.worn.base[0]:
                    continue
                if it.is_gun and self.hyp_score(run, it) > self.hyp_score(run, run.gun) * 0.98 and not new:
                    continue
                run.dismantle(it)


# ---- the policy set ------------------------------------------------------------------------------
def policy_set():
    P = {}
    P["A"] = Policy("A", "Casual", switch_margin=1.25, transfer_on_switch=True, min_donor=4, harvest_prob=0.4,
                    bp_mode="weights", bp_weights=dict(attack=0.45, range=0.15, bullets=0.1, capacity=0.15, armor=0.15),
                    spend_prob=0.5, bullet_align=False, mods="casual", buy_tools=0, econ_mods=False)
    P["A"].spend_at_wayne_only = True             # spends now and then (at Wayne), half of it at a time
    P["B"] = Policy("B", "Favorite-weapon specialist", fav_kind=1, switch_margin=1.02, min_donor=1, bp_mode="weights",
                    bp_weights=dict(attack=0.6, range=0.15, bullets=0.25), mods="list", buy_tools=3)
    P["C"] = Policy("C", "Weapon optimizer", switch_margin=1.03, min_donor=1, tool_reserve=0, bp_mode="marginal",
                    mods="greedy", buy_tools=3)
    P["D"] = Policy("D", "Two-weapon specialist", two_weapon=True, switch_margin=1.03, bp_mode="marginal", mods="list",
                    buy_tools=3, wayne_guns=2)
    P["E"] = Policy("E", "Flexible experimenter", switch_margin=1.0, min_donor=1, bp_mode="weights",
                    bp_weights=dict(attack=0.5, range=0.25, bullets=0.25), mods="greedy", buy_tools=3, wayne_guns=2)
    P["F"] = Policy("F", "Farmer (optimizer on the farmer profile)", switch_margin=1.03, bp_mode="marginal",
                    mods="greedy", buy_tools=5, wayne_guns=2)
    P["G"] = Policy("G", "ATB-focused", bp_mode="at_first", at_target=15, mods="greedy", buy_tools=3)
    P["H"] = Policy("H", "Inventory-focused", bp_mode="cap_first", cap_target=8, min_donor=0, mods="greedy", buy_tools=3)
    P["I"] = Policy("I", "Balanced", bp_mode="weights", mods="greedy", buy_tools=2,
                    bp_weights=dict(attack=0.3, range=0.15, bullets=0.15, active_time=0.2, capacity=0.1, armor=0.1))
    # BP strategy variants (section 6), on the optimizer's other decisions
    P["S_save"] = P["C"].copy("S_save", label="Saves BP until Wayne's gun", bp_mode="save")
    P["S_def"] = P["C"].copy("S_def", label="Defensive (armor first)", bp_mode="armor_first", armor_target=25)
    P["S_wpn"] = P["C"].copy("S_wpn", label="Weapon stats only", bp_mode="weights",
                             bp_weights=dict(attack=0.6, range=0.2, bullets=0.2))
    P["S_end"] = P["C"].copy("S_end", label="Hoards BP to the end (the logged run's habit)", bp_mode="end")
    P["C_wayne"] = P["C"].copy("C_wayne", label="Optimizer saving Junk for Wayne from Day 2", wayne_save_from="D2-4")
    P["G_wayne"] = P["G"].copy("G_wayne", label="ATB-first saving Junk for Wayne from Day 2", wayne_save_from="D2-4")
    return P


def specialist(kind, base=None):
    b = base or policy_set()["B"]
    return b.copy("B_" + KIND_NAME[kind], label="Specialist " + KIND_NAME[kind], fav_kind=kind)
