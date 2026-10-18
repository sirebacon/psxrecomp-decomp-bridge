"""Equipment instances with bonus provenance, Tool transfers, boosters, Mod Permits, Mod Catalog.

Every bonus point carries its origin: ("intrinsic", uid) for the bonus an item came with,
("bp", uid) for BP bought on item uid, ("booster", uid) for a stat booster used on uid. A Tool
transfer moves the origin labels with the points, so a final weapon shows exactly where each
point came from. The game treats all bonusStats alike; provenance never restricts anything.
"""
import itertools

from .. import data as D
from . import tables as T

_uid = itertools.count(1)


class Item:
    def __init__(self, iid, source, phase, uid=None):
        r = T.ITEMS[iid]
        self.uid = next(_uid) if uid is None else uid
        self.iid, self.name, self.kind, self.flags = iid, r["name"], r["kind"], r["flags"]
        if 1 <= self.kind <= 8 and iid in T.WEAPONS:
            w = T.WEAPONS[iid]            # the phase 1/2 weapon table (same game table, 2026-10-16)
            self.base = [w.attack, w.range_stat, w.bullets]
            self.bonus = [w.bonus_attack, w.bonus_range, w.bonus_bullets]
            self.slot_cap = w.slot_cap
            self.mods = [T.GUN_FX_CODE.get(e, 0) for e in (w.builtin + ["m00"] * (w.slots - len(w.builtin)))]
        else:
            self.base = list(r["base"]); self.bonus = list(r["bonus"]); self.slot_cap = r["slot_cap"]
            self.mods = [m & 0x1F for m in r["mods"]]
        self.prov = [{("intrinsic", self.uid): b} if b else {} for b in self.bonus]
        self.source, self.phase, self.alive, self.history = source, phase, True, []
        self.permit_slots = 0

    # ---- views ---------------------------------------------------------------------------------
    @property
    def is_gun(self): return 1 <= self.kind <= 8

    @property
    def is_armor(self): return self.kind == 9

    @property
    def transferable(self): return not (self.flags & 0x40)

    def slots(self): return len(self.mods)

    def free_slots(self): return sum(1 for m in self.mods if m == 0)

    def effects(self): return [m for m in self.mods if m]

    def effect_names(self):
        tbl = T.GUN_FX if self.is_gun else T.ARMOR_FX
        return [tbl.get(m, "?%d" % m) for m in self.effects()]

    def magazine(self): return max(1, self.base[2] + self.bonus[2])

    def bag_bonus(self):
        return sum(T.BAG_FX.get(m, 0) for m in self.effects()) if self.is_armor else 0

    def bonus_sum(self): return sum(max(0, b) for b in self.bonus)

    def origin_totals(self, i):
        """Bonus i split by origin kind: {'intrinsic': n, 'bp': n, 'booster': n, 'lost': n}."""
        out = {}
        for (k, _), v in self.prov[i].items():
            out[k] = out.get(k, 0) + v
        return out

    def check(self):
        for i in range(3):
            assert sum(self.prov[i].values()) == self.bonus[i], (self.name, i, self.prov[i], self.bonus[i])
            assert 0 <= self.bonus[i] <= 999

    def cfg(self):
        """A data.Weapon.config()-shaped loadout for engine.fight from this instance's mods."""
        eff = {"rof": 1}
        for m in self.effects():
            name = T.GUN_FX.get(m)
            if name in D.MODS:
                k, v = D.MODS[name]; eff[k] = v
            elif name in D.FLAGS:
                eff[name.lower()] = True
        return dict(weapon=T.WEAPONS.get(self.iid), kind=self.kind, power=self.base[0] + self.bonus[0],
                    range=D.range_units(self.base[1] + self.bonus[1]), magazine=self.magazine(), eff=eff)

    def signature(self):
        return (self.iid, tuple(self.bonus), tuple(sorted(self.effects())))

    def describe(self):
        return "%s#%d +%d/%d/%d [%s]" % (self.name, self.uid, *self.bonus, ",".join(self.effect_names()))

    # ---- stat changes --------------------------------------------------------------------------
    def add_bonus(self, i, n, origin):
        """+n to bonusStats[i] from origin, capped at 999 (what doesn't fit is not added)."""
        room = 999 - self.bonus[i]
        n = max(0, min(n, room))
        if n:
            self.bonus[i] += n
            self.prov[i][origin] = self.prov[i].get(origin, 0) + n
        return n


class TransferError(Exception):
    pass


def transfer_stats(src, dst, super_tool):
    """Inv_TransferItemBetweenLists with modifier < 0 (D): every bonus of src adds to dst
    (src + dst < 1000 ? sum : 999, the excess is lost), src's bonuses become 0. A plain Tool
    then deletes src; a Super Tool keeps it. Returns dict(moved, lost, deleted)."""
    if src is dst or not (src.alive and dst.alive):
        raise TransferError("source and target must be two live items")
    if not (src.transferable and dst.transferable):
        raise TransferError("item can't take part (flags & 0x40)")
    if src.is_gun != dst.is_gun:
        raise TransferError("guns transfer to guns, armor to armor")
    moved, lost = [0, 0, 0], [0, 0, 0]
    for i in range(3):
        total = src.bonus[i] + dst.bonus[i]
        new = total if total < 1000 else 999
        kept = new - dst.bonus[i]
        moved[i], lost[i] = kept, src.bonus[i] - kept
        # Origins move with the points; when capped, keep them in order and drop the rest.
        left = kept
        for origin, v in sorted(src.prov[i].items(), key=lambda kv: str(kv[0])):
            take = min(v, left); left -= take
            if take:
                dst.prov[i][origin] = dst.prov[i].get(origin, 0) + take
        dst.bonus[i] = new
        src.bonus[i] = 0; src.prov[i] = {}
    src.history.append(("donated_stats", dst.uid, moved))
    dst.history.append(("received_stats", src.uid, moved, lost))
    if not super_tool:
        src.alive = False
    return dict(moved=moved, lost=lost, deleted=not super_tool)


def transfer_mod(src, dst, code, super_tool):
    """One mod (D): same group on dst -> overwritten, else the first empty slot. Returns the code
    it overwrote (0 if none). Raises when there is no room (the game would still consume the Tool
    and the donor; policies never try)."""
    if src is dst or not (src.alive and dst.alive) or not (src.transferable and dst.transferable):
        raise TransferError("bad items")
    if code not in src.mods:
        raise TransferError("source lacks that mod")
    group = T.gun_group if dst.is_gun else T.armor_group
    g = group(code)
    slot = None
    if g:
        slot = next((i for i, m in enumerate(dst.mods) if m and group(m) == g), None)
    if slot is None:
        slot = next((i for i, m in enumerate(dst.mods) if m == 0), None)
    if slot is None:
        raise TransferError("no room")
    old = dst.mods[slot]
    dst.mods[slot] = code
    src.mods[src.mods.index(code)] = 0
    src.history.append(("donated_mod", dst.uid, code)); dst.history.append(("received_mod", src.uid, code, old))
    if not super_tool:
        src.alive = False
    return old


def apply_booster(item, booster_iid):
    """Menu use of a stat booster on item (D item_actions.c ~1127): +amount to bonusStats[idx]."""
    info = T.booster_info(booster_iid)
    if not info:
        raise TransferError("not a booster")
    tgt, idx, amount, _ = info
    if (tgt == "weapon") != item.is_gun:
        raise TransferError("booster for the other item kind")
    return item.add_bonus(idx, amount, ("booster", item.uid))


def permit_slot(item):
    """Mod Permit (CURRENT, pe_wayne_menu.c): +1 empty slot while slots < min(slot cap, 10)."""
    if item.slots() >= min(item.slot_cap, 10):
        return False
    item.mods.append(0); item.permit_slots += 1
    return True


def salvage_payout(item, unlocked, salvager=False):
    """pe_salvage_payout (D): 5 + 2 x bonus sum + 3 per mod + 2 per mod already unlocked."""
    p = 5 + 2 * item.bonus_sum()
    for m in item.effects():
        p += 3 + (2 if m in unlocked else 0)
    if salvager: p += p // 2
    return min(150, p)


class Catalog:
    """Mod Catalog (CURRENT): effects unlocked by dismantling / Tool salvage; installs for Junk."""

    def __init__(self):
        self.unlocked = {"gun": set(), "armor": set()}
        self.rebuild = []

    def side(self, item): return "gun" if item.is_gun else "armor"

    def unlock_from(self, item):
        new = [m for m in item.effects() if m not in self.unlocked[self.side(item)]]
        self.unlocked[self.side(item)].update(item.effects())
        return new

    def price(self, item, code, price_fn):
        tier = (T.GUN_TIER if item.is_gun else T.ARMOR_TIER)[code]
        return price_fn(T.TIER_PRICE[tier]), tier == 2

    def install_plan(self, item, code):
        """Slot index an install of code would use (group rule), or None."""
        group = T.gun_group if item.is_gun else T.armor_group
        g = group(code)
        if code in item.mods:
            return None
        if g:
            s = next((i for i, m in enumerate(item.mods) if m and group(m) == g), None)
            if s is not None:
                return s
        return next((i for i, m in enumerate(item.mods) if m == 0), None)

    def install(self, item, code, slot):
        if code not in self.unlocked[self.side(item)]:
            raise TransferError("effect not unlocked")
        old = item.mods[slot]
        if old and item.is_armor and old in T.BAG_FX:
            raise TransferError("bag mods are never replaced")
        item.mods[slot] = code
        item.history.append(("catalog_install", code, old))
        return old
