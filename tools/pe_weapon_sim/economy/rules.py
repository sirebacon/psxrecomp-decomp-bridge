"""Economy rulesets. VANILLA and CURRENT are frozen; experiments and ablations copy them.

`systems` switches whole progression systems off for ablations (a disabled system yields
nothing; its resources are never conjured elsewhere). `combat` names the combat ruleset
(pe_weapon_sim.rules) used at checkpoints.
"""
from types import MappingProxyType

ALL_SYSTEMS = ("bp", "catalog", "donors", "junk", "rare")

_VANILLA = dict(
    name="vanilla", combat="vanilla",
    bp_cost=100, bp_bank_on_levelup=True, bp_bank_cap=99999, bonus_cap=999,
    rare_cascade=False, junk_economy=False, catalog=False, salvage=False, requisition=False,
    permits=False, wayne_junk_cost=300,           # 300 vanilla Junk items (the run dropped ~111)
    tool_kits_infinite=True, premium_needs_tool=False,
    preset=1, systems=ALL_SYSTEMS,
)
_CURRENT = dict(_VANILLA,
    name="current", combat="current",
    rare_cascade=True, junk_economy=True, catalog=True, salvage=True, requisition=True,
    permits=True, wayne_junk_cost=300, premium_needs_tool=True,
)
VANILLA = MappingProxyType(_VANILLA)
CURRENT = MappingProxyType(_CURRENT)


def variant(base, name=None, **over):
    r = dict(base); r.update(over)
    r["name"] = name or (base["name"] + "+" + "+".join("%s=%s" % kv for kv in sorted(over.items())))
    return r


def ablation(code):
    """Phase 3 ablations A1-A8 (A0 is the phase 1/2 fixed budget, run separately)."""
    sets = {"A1": ("bp",), "A2": ("donors",), "A3": ("rare",), "A4": ("bp", "donors"), "A5": ("donors", "rare"),
            "A6": ("bp", "rare"), "A7": ALL_SYSTEMS, "A8": ALL_SYSTEMS}
    # The CURRENT base (fixed pickups incl. field boosters / Tools, Junk, Requisition, Mod Catalog
    # installs, switching to found guns) stays on in every model; the switches remove BP spending
    # ("bp"), Tool transfers of stats and mods ("donors"), and rare-cascade rewards ("rare").
    keep = tuple(sorted(set(sets[code]) | {"catalog", "junk"}))
    r = variant(CURRENT, "abl:" + code, systems=keep)
    if code == "A8":
        r["combat"] = "exp:C1s_40"
    return r


# Validation status of each economy rule (D decomp, R runtime/RAM, L log, A assumed).
VALIDATION = [
    ("BP per enemy = max(0, rewardBase - rewardFactorA x hits that enemy landed on Aya)", "D",
     "battle/enemy_movement.c ~388; rewardFactorB counted in menu/main_update.c ~496; logged as bp=base/A/B"),
    ("Battle BP goes to a pool, banked into spendable BP only when Aya levels up (cap 99999)", "D",
     "menu/main_menu.c Aya_SetTotalExp; L: save rows stay at 1326 BP across 5,000 EXP without a level-up"),
    ("BP comes only from battles", "L", "log: kept battles' BP = banked + pending pool at the end"),
    ("100 BP = +1 weapon attack / range / bullets or armor axis (bonusStats, cap 999)", "D",
     "menu/item_actions.c Menu_SpendBonusPoints"),
    ("100 BP = +1 stat level of Active Time (stat22 +1) or item capacity (next table step)", "D/R",
     "Menu_SpendBonusPoints + level-stat table 0x63c0 (R)"),
    ("BP bonuses are ordinary bonusStats: transferable by Tool", "D", "TRANSFER_STAT reads bonusStats only"),
    ("Tool transfer: all 3 bonuses add to the target (sum capped 999, excess lost), source zeroed", "D",
     "item/armor_capacity.c Inv_TransferItemBetweenLists"),
    ("Plain Tool deletes the donor (its ammo returns to the pool); Super Tool keeps it", "D",
     "armor_capacity.c: !(flags & 1) -> DeleteSlot(source); cost item kind 12 vs 13"),
    ("A mod transfer moves one mod (same group overwrites, else first empty slot)", "D", "armor_capacity.c"),
    ("A mod transfer that finds no room still consumes the Tool and the donor", "D (not runtime-checked)",
     "armor_capacity.c: the failure branch only shows a dialog; policies never attempt it"),
    ("Tool Kit / Super Tool Kit make transfers free (count 999)", "D", "menu/inventory.c g_StatBaseTable"),
    ("Items with flags & 0x40 (Maeda's guns, Dress) can't take part", "D", "item_actions.c ~1072"),
    ("CURRENT: a plain-Tool donor is salvaged (Catalog unlock, dismantle Junk, Rebuild list)", "D",
     "pe_loot_catalog.c pe_on_tool_transfer (decision 42)"),
    ("CURRENT: rare cascade, soft pity 4% +1%/dry battle, certain at 25 (Normal preset)", "D", "pe_loot.c pe_roll_rare"),
    ("CURRENT: Lucky Find doubles pity progress per dry battle (not the chance table)", "D", "pe_loot.c pe_pity_step"),
    ("CURRENT: Tool rare chance 85/65/40/20/10% by Tools held (bag + storage), skipped at 5+", "D",
     "pe_loot.c pe_cascade_skip"),
    ("CURRENT: booster tier by battle EXP (<20, <60, <150, else +4)", "D", "pe_loot.c pe_pick_rare"),
    ("CURRENT: battle Junk = min(cap, 1 + EXP/8) (+25% x (4-hits)/4 if hits<4), cap 12 / boss 25", "D",
     "pe_loot.c pe_on_set_total_exp"),
    ("CURRENT: Requisition Tool price 40 +10 per Tool bought, max 100 Junk", "D", "pe_loot_shop.c"),
    ("CURRENT: Mod Catalog install 10 / 30 / 80 Junk; premium (RoF10, Atk All, Cyanide, 2/3 Cmd) + a Tool", "D",
     "pe_loot_catalog.c s_gun_tier"),
    ("CURRENT: dismantle pays 5 + 2/bonus + 3/mod + 2/already-unlocked mod (x1.5 Salvager, cap 150)", "D",
     "pe_loot_catalog.c pe_salvage_payout; L: 24 dismantle rows match"),
    ("CURRENT: Mod Permit = +1 slot up to the item's slot cap (max 10), at Wayne", "D", "pe_wayne_menu.c pe_at_max"),
    ("Wayne crafts a chosen 300-Junk gun (DE50AE7, HK40, LAW80, MAG, P90, M10B) from Day 4", "D/L",
     "pe_loot.c (before Day 4 his menu only stores Junk); loot design doc; log"),
    ("VANILLA: 300 Junk items; the run's battles dropped 111 (loot rows' vanilla count)", "L", "campaign script"),
    ("Fixed gear locations by area", "A (wiki table)", "pe-gear-locations-2026-10-11.csv"),
    ("Field Tools / boosters / permits per phase", "L", "campaign script (one real run)"),
    ("Hits landed on Aya scale with fight length (surrogate)", "A", "surrogate.py; validated vs engine at checkpoints"),
]
