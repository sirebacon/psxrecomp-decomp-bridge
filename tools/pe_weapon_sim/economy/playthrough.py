"""One continuous playthrough: explicit state transitions with a transaction log.

Random streams (independent, seeded from the run seed): enc (profile transformations, gear
timing), loot (rare cascade), hits (combat feedback), policy (casual randomness). Matched
seeds give every policy the same encounters and the same loot stream (the loot stream's
draws still depend on the player's state where the game's cascade does).
"""
import bisect, random, copy

from .. import rules as CR
from . import acquisition as AQ, bp as BP, equipment as EQ, inventory as INV, loot as LT, source_stats as SS, surrogate as SG, tables as T

GEAR_MIN, GEAR_MAX = 0x3F, 0xC7


def combat_rules(name):
    if name == "vanilla": return CR.VANILLA
    if name == "current": return CR.CURRENT
    if name.startswith("exp:"): return CR.experimental(*[x for x in name[4:].split("+") if x and x != "none"])
    raise ValueError(name)


class Run:
    def __init__(self, econ, policy, profile, seed, camp, trace=False):
        self.econ, self.policy, self.profile, self.seed = econ, policy, profile, seed
        self.crules = combat_rules(econ["combat"])
        self.sys = set(econ["systems"])
        mk = lambda tag: random.Random("%s|%s" % (seed, tag))
        self.r_enc, self.r_loot, self.r_hits, self.r_pol, self.r_sens = mk("enc"), mk("loot"), mk("hits"), mk("policy"), mk("sens")
        self.camp = camp
        self.aya = BP.Aya(source=econ.get("source_level_stats", False))
        self.ledger = BP.Ledger(econ["bp_cost"], econ["bp_bank_cap"])
        self.loot = LT.LootState(self.r_loot, econ["preset"])
        self.catalog = EQ.Catalog()
        self.inv = INV.Inventory()
        self.junk = 0
        self.tools_bought = 0
        self.econ_unlocked = set()
        self.phase = "D1"
        self.battle_no = 0
        self.trace_on = trace
        self.log = []
        self.items = {}                       # uid -> Item, every item ever owned
        self.m = dict(tools_got={}, tools_spent={}, super_got=0, super_spent=0, boosters_got={}, booster_points=[0, 0, 0],
                      donors_got=0, donors_harvested=0, extracted=[0, 0, 0], extracted_bp=0, lost_cap=[0, 0, 0],
                      permits_got=0, permits_used=0, mods_installed=0, junk_earned=0, junk_spent={}, overflow=0,
                      switches=0, wayne_guns=[], hits=0, bp_lost=0, battles=0, farm_battles=0, rare={}, dismantled=0,
                      premium_tools=0, effect_first={})
        self.checkpoints = {}
        self.recent_overflow = 0
        self.wayne_open = False               # Wayne crafts from Day 4
        self._logged = AQ.logged_loadouts_t(camp)
        self._logged_keys = [x[0] for x in self._logged]
        g = self.new_item(T.STARTING["gun"], "start"); a = self.new_item(T.STARTING["armor"], "start")
        self.inv.gear[g.uid] = g; self.inv.gear[a.uid] = a
        self.main, self.armor, self.second = g.uid, a.uid, None
        self.aya.armor = a

    # ---- bookkeeping -----------------------------------------------------------------------------
    def tx(self, kind, **kw):
        if self.trace_on:
            self.log.append(dict(b=self.battle_no, phase=self.phase, kind=kind, **kw))

    def new_item(self, iid, source):
        it = EQ.Item(iid, source, self.phase)
        d = self.econ.get("base_delta", {}).get(iid)
        if d:                                 # EXPERIMENTAL base-stat change (e.g. S3: M10B +1 bullet)
            it.base = [it.base[i] + d[i] for i in range(3)]
        self.items[it.uid] = it
        if it.is_gun or it.is_armor:
            for code in it.effects():
                self.m["effect_first"].setdefault(T.GUN_FX.get(code, "?") if it.is_gun else T.ARMOR_FX.get(code, "?"),
                                                   (self.phase, self.battle_no))
        return it

    @property
    def gun(self): return self.items[self.main]

    @property
    def worn(self): return self.items[self.armor]

    @property
    def sec(self): return self.items[self.second] if self.second else None

    def capacity(self):
        return self.aya.capacity(self.worn.bag_bonus())

    def free(self):
        return self.inv.free(self.capacity(), self.phase)

    def defense_ref(self):
        return {"D1": 8, "D2-4": 20, "D5": 32, "Disc2": 48}[self.phase]

    def score(self, item, aya=None):
        return SG.score(item.cfg(), aya or self.aya.combat(), self.defense_ref(), self.crules)

    def has(self, sysname): return sysname in self.sys

    def price(self, base):
        return self.loot.price(base, bargain="Bargain" in self.worn_effects())

    def worn_effects(self): return self.worn.effect_names()

    def loot_view(self):
        return LT.LootView(tools_held=self.inv.held(T.TOOL), permits_held=self.inv.held(T.MOD_PERMIT),
                           tool_kit=self.inv.held(T.TOOL_KIT) > 0, super_tool_kit=self.inv.held(T.SUPER_TOOL_KIT) > 0,
                           econ_unlocked=self.econ_unlocked, lucky_find="LuckyFind" in self.worn_effects(),
                           scavenger="Scavenger" in self.worn_effects())

    # ---- acquisitions --------------------------------------------------------------------------
    def gain_gear(self, iid, source):
        it = self.new_item(iid, source)
        if it.is_gun or it.is_armor:
            self.m["donors_got"] += 1
        if self.free() <= 0 and not self.policy.make_room(self, it):
            self.inv.overflow += 1; self.m["overflow"] += 1; self.recent_overflow = 20
            it.alive = False
            self.tx("overflow", item=it.describe())
            return None
        self.inv.gear[it.uid] = it
        self.tx("gain", src=source, item=it.describe())
        return it

    def gain_stack(self, kind, source):
        if kind in (T.TOOL, T.SUPER_TOOL):
            key = "tools_got" if kind == T.TOOL else None
            if key: self.m[key][source] = self.m[key].get(source, 0) + 1
            else: self.m["super_got"] += 1
        if kind == T.MOD_PERMIT: self.m["permits_got"] += 1
        self.inv.count[kind] += 1
        self.tx("gain", src=source, item=T.item_name(kind))

    def gain_booster(self, bid, source):
        self.m["boosters_got"][source] = self.m["boosters_got"].get(source, 0) + 1
        self.inv.boosters.append(bid)
        self.tx("gain", src=source, item="booster %s +%d" % (T.booster_info(bid)[3], T.booster_info(bid)[2]))

    def gain_item(self, iid, source):
        if GEAR_MIN <= iid <= GEAR_MAX and iid in T.ITEMS:
            return self.gain_gear(iid, source)
        if T.booster_info(iid):
            return self.gain_booster(iid, source)
        if iid in INV.STACKED:
            return self.gain_stack(iid, source)
        if iid in LT.BUNDLE_VALUE and self.econ["junk_economy"] and self.has("junk"):
            self.add_junk(LT.BUNDLE_VALUE[iid], "bundle")

    def add_junk(self, n, why):
        self.junk = min(99999, self.junk + n); self.m["junk_earned"] += n

    def spend_junk(self, n, why):
        assert self.junk >= n
        self.junk -= n; self.m["junk_spent"][why] = self.m["junk_spent"].get(why, 0) + n

    # ---- player actions (transactions) -----------------------------------------------------------
    def take_tool(self, super_tool, at_wayne=False):
        kind = T.SUPER_TOOL if super_tool else T.TOOL
        kit = T.SUPER_TOOL_KIT if super_tool else T.TOOL_KIT
        if self.econ["tool_kits_infinite"] and self.inv.held(kit):
            return "kit"
        if self.inv.count[kind] > 0:
            self.inv.count[kind] -= 1; return "bag"
        if at_wayne and self.inv.stored_count[kind] > 0:
            self.inv.stored_count[kind] -= 1; return "storage"
        return None

    def tools_available(self, at_wayne=False):
        n = self.inv.count[T.TOOL] + (self.inv.stored_count[T.TOOL] if at_wayne else 0)
        return 999 if self.inv.held(T.TOOL_KIT) else n

    def do_transfer_stats(self, src, dst, why, at_wayne=False, super_tool=False):
        if not self.has("donors"):
            return False
        if self.take_tool(super_tool, at_wayne) is None:
            return False
        bp_moved = sum(v for i in range(3) for (k, _), v in src.prov[i].items() if k == "bp")
        before = [src.bonus[i] for i in range(3)]
        res = EQ.transfer_stats(src, dst, super_tool)
        for i in range(3):
            self.m["extracted"][i] += res["moved"][i]; self.m["lost_cap"][i] += res["lost"][i]
        self.m["extracted_bp"] += bp_moved
        self.m["donors_harvested"] += 1
        sp = "super" if super_tool else "stat"
        self.m["tools_spent"][sp] = self.m["tools_spent"].get(sp, 0) + 1
        self.tx("tool_stats", tool="Super Tool" if super_tool else "Tool", src=src.describe(), dst=dst.describe(),
                moved=res["moved"], before=before, why=why)
        if res["deleted"]:
            self.retire(src, "tool")
        return True

    def do_transfer_mod(self, src, dst, code, why, at_wayne=False):
        if not self.has("donors") or dst.free_slots() == 0 and not any(
                T.gun_group(m) and T.gun_group(m) == T.gun_group(code) for m in dst.effects()):
            return False
        if self.take_tool(False, at_wayne) is None:
            return False
        EQ.transfer_mod(src, dst, code, False)
        self.m["tools_spent"]["mod"] = self.m["tools_spent"].get("mod", 0) + 1
        self.tx("tool_mod", src=src.describe(), dst=dst.describe(), mod=T.GUN_FX.get(code), why=why)
        self.retire(src, "tool")
        return True

    def retire(self, item, how):
        """An item leaves play: Tool donor (CURRENT salvage), dismantle, or discard."""
        item.alive = False
        self.inv.gear.pop(item.uid, None); self.inv.stored.pop(item.uid, None)
        if self.second == item.uid: self.second = None
        if (how == "tool" and self.econ["salvage"]) or how == "dismantle":
            pay = EQ.salvage_payout(item, self.catalog.unlocked[self.catalog.side(item)],
                                    "Salvager" in self.worn_effects())
            new = self.catalog.unlock_from(item)
            if self.has("junk"): self.add_junk(pay, "salvage")
            self.m["dismantled"] += how == "dismantle"
            self.tx("salvage" if how == "tool" else "dismantle", item=item.describe(), junk=pay,
                    unlocked=[T.GUN_FX.get(c) if item.is_gun else T.ARMOR_FX.get(c) for c in new])

    def dismantle(self, item):
        if not self.econ["catalog"] or item.uid in (self.main, self.armor):
            return False
        self.retire(item, "dismantle")
        return True

    def spend_bp(self, category, item=None, detail=""):
        if not self.has("bp") or not self.ledger.can_spend():
            return False
        if category in BP.STAT_INDEX:
            item = item or self.gun
            i = BP.STAT_INDEX[category]
            if item.bonus[i] >= 999: return False
            self.ledger.spend(category, self.battle_no, "%s#%d" % (item.name, item.uid))
            item.add_bonus(i, 1, ("bp", item.uid))
        elif category == "armor":
            item = item or self.worn
            if item.bonus[0] >= 999: return False
            self.ledger.spend(category, self.battle_no, "%s#%d defense" % (item.name, item.uid))
            item.add_bonus(0, 1, ("bp", item.uid))
        elif category == "active_time":
            self.ledger.spend(category, self.battle_no); self.aya.buy_active_time()
        elif category == "capacity":
            self.ledger.spend(category, self.battle_no); self.aya.buy_capacity()
        self.tx("bp", cat=category, item=item.describe() if item else "", banked=self.ledger.banked)
        return True

    def use_booster(self, bid, item):
        n = EQ.apply_booster(item, bid)
        info = T.booster_info(bid)
        if info[0] == "weapon":
            self.m["booster_points"][info[1]] += n
        self.inv.boosters.remove(bid)
        self.tx("booster", booster="%s +%d" % (info[3], info[2]), item=item.describe())

    def install(self, item, code):
        """Mod Catalog install (CURRENT): Junk, and a Tool for premium effects."""
        if not (self.econ["catalog"] and self.has("catalog")):
            return False
        slot = self.catalog.install_plan(item, code)
        if slot is None or code not in self.catalog.unlocked[self.catalog.side(item)]:
            return False
        price, premium = self.catalog.price(item, code, self.price)
        if self.junk < price:
            return False
        if premium and self.econ["premium_needs_tool"] and not self.inv.has_kit():
            if self.inv.count[T.TOOL] <= 0:
                return False
            self.inv.count[T.TOOL] -= 1
            self.m["tools_spent"]["premium"] = self.m["tools_spent"].get("premium", 0) + 1
        self.spend_junk(price, "mods")
        old = self.catalog.install(item, code, slot)
        self.m["mods_installed"] += 1
        tbl = T.GUN_FX if item.is_gun else T.ARMOR_FX
        self.tx("install", item=item.describe(), mod=tbl.get(code), replaced=tbl.get(old) if old else None, junk=price)
        return True

    def remove_mod(self, item, slot):
        """Mod Catalog remove (CURRENT): the effect leaves the slot and stays unlocked; free."""
        code = item.mods[slot]
        if not code or (item.is_armor and code in T.BAG_FX) or not self.econ["catalog"]:
            return False
        self.catalog.unlocked[self.catalog.side(item)].add(code)
        item.mods[slot] = 0
        self.tx("remove_mod", item=item.describe(), mod=(T.GUN_FX if item.is_gun else T.ARMOR_FX).get(code))
        return True

    def buy_tool(self):
        if not (self.econ["requisition"] and self.has("junk")) or self.inv.has_kit():
            return False
        p = min(100, self.price(40 + 10 * self.tools_bought))
        if self.junk < p or self.free() <= 0:
            return False
        self.spend_junk(p, "tools"); self.tools_bought += 1
        self.gain_stack(T.TOOL, "bought")
        return True

    def use_permit(self, item):
        """At Wayne: the bag's first permit, else storage (pe_wayne_menu.c pe_take_permit)."""
        if self.inv.held(T.MOD_PERMIT) <= 0 or not self.econ["permits"]:
            return False
        if not EQ.permit_slot(item):
            return False
        if self.inv.count[T.MOD_PERMIT] > 0: self.inv.count[T.MOD_PERMIT] -= 1
        else: self.inv.stored_count[T.MOD_PERMIT] -= 1
        self.m["permits_used"] += 1
        self.tx("permit", item=item.describe())
        return True

    def wayne_gun(self, iid):
        """Wayne crafts a chosen 300-Junk gun from Day 4 (decomp script; pe_loot.c: before Day 4
        his menu only stores Junk). VANILLA counts Junk items, CURRENT the economy counter."""
        cost = self.econ["wayne_junk_cost"]
        if cost is None or self.junk < cost or not self.wayne_open:
            return None
        self.spend_junk(cost, "wayne")
        it = self.new_item(iid, "wayne")
        self.inv.gear[it.uid] = it
        self.m["wayne_guns"].append(it.name)
        self.tx("wayne_gun", item=it.describe(), junk=cost)
        return it

    def equip(self, item, slot="main"):
        if slot == "main" and item.uid != self.main:
            self.m["switches"] += 1
            self.tx("equip", item=item.describe(), was=self.gun.describe())
            if self.second == item.uid: self.second = None
            self.main = item.uid
        elif slot == "armor":
            self.armor = item.uid
            self.aya.armor = item
        elif slot == "second":
            self.second = item.uid

    # ---- the battle ----------------------------------------------------------------------------
    def logged_cfg(self, t):
        i = bisect.bisect_right(self._logged_keys, tuple(t)) - 1
        if i < 0:
            return self._logged_item(dict(id=T.STARTING["gun"], bonus=[2, 0, 0], mods=[1]))
        return self._logged_item(self._logged[i][1])

    _lcache = {}

    def _logged_item(self, g):
        key = (g["id"], tuple(g["bonus"]), tuple(g["mods"]))
        if key not in Run._lcache:
            it = EQ.Item(g["id"], "logged", "", uid=0)
            it.bonus = list(g["bonus"]); it.prov = [{("intrinsic", 0): b} for b in it.bonus]
            it.mods = list(g["mods"])
            Run._lcache[key] = it.cfg()
        return Run._lcache[key]

    def battle(self, b):
        self.battle_no += 1
        self.m["battles"] += 1; self.m["farm_battles"] += bool(b.get("farm"))
        enemies = [e for e in b["enemies"] if e.get("died", True)] or b["enemies"]
        defense = sum(e["defense"] for e in enemies) / max(1, len(enemies))
        aya = self.aya.combat()
        cfg = self.gun.cfg()
        mine = SG.dps(cfg, aya, defense, rules=self.crules)
        ref_aya = dict(aya, stat22=(SS.aya_stats(self.aya.level)["stat22"] if self.aya.source else T.stat22_of(self.aya.level)))
        ref = SG.dps(self.logged_cfg(b["t"]), ref_aya, defense, rules=CR.CURRENT)
        ratio = min(5.0, max(0.2, ref / max(1e-6, mine)))
        if self.econ.get("hits_logged"):
            ratio = 1.0                        # calibration: the run's own hits
        bp_total = lost = hits_total = 0
        for e in enemies:
            mean = e["bp_hits"] * ratio ** self.econ.get("hits_exp", 1.0)
            h = _poisson(self.r_hits, mean) if mean > 0 else 0
            hits_total += h
            got = BP.enemy_bp(e["bp_base"], e["bp_factor"], h)
            lost += BP.enemy_bp(e["bp_base"], e["bp_factor"], 0) - got
            bp_total += got
        self.m["hits"] += hits_total; self.m["bp_lost"] += lost
        lv0 = self.aya.level
        self.aya.exp += b["exp"]
        self.ledger.award(bp_total, lost, self.battle_no)
        if self.aya.level > lv0:
            self.ledger.level_up(self.battle_no)
            self.tx("level", level=self.aya.level, banked=self.ledger.banked)
        self.tx("battle", map=b["map"], exp=b["exp"], bp=bp_total, hits=hits_total, ratio=round(ratio, 2))
        # Vanilla Junk items this battle dropped (the loot row's `vanilla` count: the mod takes them
        # off the reward list into the counter; with the economy off they are Wayne's Junk items).
        vj = sum(int(r.get("vanilla", 0)) for r in b.get("rare", []) if r.get("kind") == "loot")
        if self.econ["junk_economy"] and self.has("junk"):
            j = self.loot.battle_junk(b["exp"], hits_total, b["boss"], self.loot_view())
            self.add_junk(j + vj, "battle")
        elif not self.econ["junk_economy"]:
            self.add_junk(vj, "vanilla junk")
        for r in b["rewards"]:
            if r and int(r, 16) != T.JUNK:
                self.gain_item(int(r, 16), "drop")
        if self.econ["rare_cascade"] and self.has("rare"):
            res = self.loot.roll(b["exp"], self.loot_view())
            if res:
                kind, val = res
                key = val if kind == "econ" else ("booster" if T.booster_info(val) else T.item_name(val))
                self.m["rare"][key] = self.m["rare"].get(key, 0) + 1
                self.tx("rare", got=key)
                if kind == "econ":
                    self.econ_unlocked.add(val)
                    code = {n: c for n, c, _ in LT.ECON_MODS}[val]
                    self.catalog.unlocked["armor"].add(code)
                else:
                    self.gain_item(val, "rare")
        self.recent_overflow = max(0, self.recent_overflow - 1)
        self.policy.after_battle(self)

    def checkpoint(self, phase):
        g = self.gun
        snap = dict(level=self.aya.level, stat22=self.aya.stat22, at_bought=self.aya.at_bought,
                    cap_bought=self.aya.cap_bought, capacity=self.capacity(),
                    bp_earned=self.ledger.earned, bp_banked=self.ledger.banked, bp_pool=self.ledger.pool,
                    bp_spent=dict(self.ledger.spent), bp_lost=self.ledger.lost_to_hits,
                    gun=g.name, gun_id=g.iid, gun_kind=g.kind, bonus=list(g.bonus), magazine=g.magazine(),
                    mods=g.effect_names(), slots=g.slots(),
                    origins=[g.origin_totals(i) for i in range(3)],
                    second=self.sec.describe() if self.sec else None,
                    second_bonus=list(self.sec.bonus) if self.sec else None,
                    second_kind=self.sec.kind if self.sec else None,
                    armor=self.worn.describe(), armor_bonus=list(self.worn.bonus), armor_mods=self.worn.effect_names(),
                    tools=self.inv.held(T.TOOL), super_tools=self.inv.held(T.SUPER_TOOL), junk=self.junk,
                    unused_donor_bonus=sum(it.bonus_sum() for it in list(self.inv.gear.values()) + list(self.inv.stored.values())
                                           if it.uid not in (self.main, self.armor, self.second) and it.is_gun),
                    cfg_sig=g.signature(), score=round(self.score(g), 2),
                    metrics={k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v) for k, v in self.m.items()})
        # Checkpoints must not acquire upgrades made later in the campaign.
        snap["_gun"] = copy.deepcopy(g)
        snap["_second"] = copy.deepcopy(self.sec)
        snap["_armor"] = copy.deepcopy(self.worn)
        snap["_aya"] = self.aya.combat()
        self.checkpoints[phase] = snap
        self.tx("checkpoint", gun=g.describe(), score=snap["score"])

    def check(self):
        self.ledger.check(); self.inv.check()
        assert self.junk >= 0
        assert self.gun.alive and self.worn.alive


def _poisson(rng, lam):
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, lam ** 0.5))))
    import math
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L: return k
        k += 1


def play(econ, policy, profile, seed, camp, trace=False, check=True):
    run = Run(econ, policy, profile, seed, camp, trace)
    events = AQ.build(profile, camp, run.r_enc)
    phase = "D1"
    for e in events:
        ph = e.get("phase", phase)
        if ph != phase and ph in T.PHASES and T.PHASES.index(ph) > T.PHASES.index(phase):
            policy.maintain(run, at_wayne=False)
            run.checkpoint(phase)
            phase = ph
        run.phase = phase
        t = e["type"]
        if t == "battle":
            run.battle(e)
        elif t == "gear":
            run.gain_gear(e["item"], "field")
            policy.maintain(run, at_wayne=False)
        elif t == "pickup":
            k = econ.get("field_tool_scale", 1.0) if e["item"] == T.TOOL else 1.0
            n = int(k) + (1 if run.r_sens.random() < k - int(k) else 0)
            for _ in range(n):
                run.gain_item(e["item"], "field")
        elif t == "wayne":
            if e.get("why") == "Day 4" or phase in ("D5", "Disc2"):
                run.wayne_open = True
            policy.at_wayne(run)
        if check:
            run.check()
    policy.at_wayne(run)
    policy.maintain(run, at_wayne=True)
    run.checkpoint(phase)
    return run
