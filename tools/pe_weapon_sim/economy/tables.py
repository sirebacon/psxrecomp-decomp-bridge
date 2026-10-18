"""Game tables for the progression economy (sources in each comment).

Tags as in rules.VALIDATION: D decomp, R read from game RAM, L play log, A assumed."""
import bisect, csv, os, re

from .. import data as D

FIND = D.FIND
ITEMS_CSV = os.path.join(FIND, "pe-items-baseline-2026-10-11.csv")
GEAR_CSV = os.path.join(FIND, "pe-gear-locations-2026-10-11.csv")
CAMPAIGN_JSON = os.path.join(FIND, "pe-campaign-2026-10-17.json")

# ---- Aya ---------------------------------------------------------------------------------------
# levelExp (resident pack 0x800A8028, R): total EXP at which each level starts (index = level - 1).
LEVEL_EXP = [0, 3, 8, 19, 28, 41, 68, 104, 142, 184, 240, 325, 428, 568, 868, 1120, 1460, 1920, 2906,
             3744, 4875, 6403, 8465, 11248, 17216, 22289, 29137, 43820, 56301, 73151, 95897, 126605,
             168061, 224026, 299579]


def level_of(total_exp):
    """Aya_StatBinarySearch over levelExp (D main_menu.c)."""
    return max(1, bisect.bisect_right(LEVEL_EXP, total_exp))


# Offense by level (level-stat table offset 0x63c0, R at these levels; linear in between, A).
_OFFENSE = [(1, 40), (7, 65), (12, 90), (16, 135), (19, 170), (21, 180), (24, 200), (27, 300), (33, 350), (40, 400)]


def offense_of(level):
    for (l0, o0), (l1, o1) in zip(_OFFENSE, _OFFENSE[1:]):
        if l0 <= level <= l1:
            return round(o0 + (o1 - o0) * (level - l0) / (l1 - l0))
    return _OFFENSE[-1][1]


def stat22_of(stat_level):
    """Active Time stat (stat22) by stat level: 50, 51, ... (R). Level-ups add one stat level."""
    return 49 + stat_level


# Item capacity by stat level (level-stat table, R): index = stat level - 1.
CAPACITY = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 21, 21, 21, 22, 22, 23, 23, 23, 24, 24, 25, 25,
            25, 26, 26, 27, 27, 27, 27, 28, 28, 29, 29, 30, 31, 31, 32, 32, 32, 33, 33, 34, 34]


def capacity_of(stat_level):
    return CAPACITY[min(len(CAPACITY), max(1, stat_level)) - 1]


# ---- items -------------------------------------------------------------------------------------
TOOL, SUPER_TOOL, TOOL_KIT, SUPER_TOOL_KIT, MOD_PERMIT = 0x16, 0x17, 0x35, 0x36, 0x37
SUPER_JUNK, DUPER_JUNK, JUNK = 0x0B, 0x0C, 0x14
# Stat boosters (item kind 10, R): tier 1 id per stat, +1..+4 by tier (reserveAmmo field, R);
# Menu applies one to a chosen item's bonusStats[stat] (cap 999) and consumes it (D item_actions.c).
BOOSTER_BASE = {0x1D: ("weapon", 0, "OFFENSE"), 0x21: ("weapon", 1, "RANGE"), 0x25: ("weapon", 2, "BULLET CAP"),
                0x29: ("armor", 0, "DEFENSE"), 0x2D: ("armor", 2, "CR EVADE"), 0x31: ("armor", 1, "PE")}


def booster_info(iid):
    """(target 'weapon'/'armor', bonus index, amount, name) or None."""
    for base, (tgt, idx, name) in BOOSTER_BASE.items():
        if base <= iid < base + 4:
            return tgt, idx, iid - base + 1, name
    return None


# Effect codes: low 5 bits of a mod byte; the high 3 bits are the group (D armor_capacity.c).
GUN_FX = {1: "RoF2", 2: "RoF3", 3: "RoF5", 4: "RoF7", 5: "RoF10", 6: "Random", 7: "Burst", 8: "AttackAll",
          9: "Heat", 10: "Frost", 11: "Cyanide", 12: "Acid", 13: "Tranq", 14: "Counter", 15: "Quickdraw",
          16: "Steal", 17: "StealAtk", 18: "Critical", 19: "2Cmd", 20: "3Cmd"}
GUN_FX_CODE = {v: k for k, v in GUN_FX.items()}
GUN_FX_CODE.update({"StealHalf": 16})
ARMOR_FX = {1: "ResPoison", 2: "ResStiff", 3: "ResDark", 4: "LessStolen", 5: "ResConfuse", 6: "AutoMed",
            7: "AutoCure", 8: "Bag+1", 9: "Bag+2", 10: "Bag+4", 11: "MaxHP", 12: "AttackUp", 13: "SlowAT",
            14: "PEBurdenDown", 15: "AttackDown", 17: "Bargain", 18: "Scavenger", 19: "LuckyFind", 20: "Salvager"}
BAG_FX = {8: 1, 9: 2, 10: 4}


def gun_group(code):
    """pe_mod_group (pe_loot_catalog.c) == the mod byte's high bits (D)."""
    if 1 <= code <= 5: return 1
    if 6 <= code <= 8: return 2
    if code in (19, 20): return 3
    if code in (16, 17): return 4
    return 0


def armor_group(code):
    return 5 if code in BAG_FX else 0


# Mod Catalog install price tier (pe_loot_catalog.c s_gun_tier / s_armor_tier; prices 10/30/80,
# premium also costs a Tool unless a Tool Kit is carried) (D, CURRENT only).
GUN_TIER = [0, 0, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1, 2, 2]
ARMOR_TIER = [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1]
TIER_PRICE = (10, 30, 80)


def load_items():
    """Item baseline (item table read from RAM 2026-10-11, R): id -> row dict."""
    out = {}
    with open(ITEMS_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            iid = int(r["id"], 16)
            mods = [int(x, 16) for x in r["mods"].split()] if r["mods"].strip() else []
            out[iid] = dict(id=iid, name=r["name"], kind=int(r["kind"]), flags=int(r["flags"], 16),
                            base=[int(r["base_atk"]), int(r["base_rng"]), int(r["base_cap"])],
                            bonus=[int(r["bonus_atk"]), int(r["bonus_rng"]), int(r["bonus_cap"])],
                            slot_cap=int(r["mod_slots"]), mods=mods)
    return out


ITEMS = load_items()
WEAPONS = D.load_weapons()


def item_name(iid):
    r = ITEMS.get(iid)
    return r["name"] if r else "0x%02X" % iid


# ---- where gear is found (gear-locations table, wiki, A for timing within a phase) ---------------
AREA_PHASE = {"Initial": "D1", "Carnegie Hall": "D1", "Carnegie Hall Sewer": "D1", "Central Park": "D2-4",
              "Soho": "D2-4", "NYPD 17th Precinct": "D2-4", "Hospital": "D2-4", "Chinatown": "Disc2",
              "Chinatown Sewer": "Disc2", "Warehouse": "Disc2", "Subway": "Disc2", "Museum": "Disc2"}
# "Chrysler Building" gear is EX-game only (the 77-floor bonus dungeon): not in a first run.
PHASES = ["D1", "D2-4", "D5", "Disc2"]


def _norm(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def load_gear_locations():
    """[(item id, phase, area)] for main-game gear with a fixed location; Wayne / Maeda rows
    are excluded (they come through their own events)."""
    names = {}
    for iid, r in ITEMS.items():
        if 1 <= r["kind"] <= 9:
            names.setdefault(_norm(r["name"]), iid)
    alias = {"AM444": "AM44", "KVPROTECTOR": "KVPROTECTOR1", "KVJACKET": "KVJACKET1"}
    out = []
    with open(GEAR_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            phase = AREA_PHASE.get(r["location"])
            if not phase or r["location"] == "Initial":
                continue
            n = _norm(r["name"]); n = alias.get(n, n)
            iid = names.get(n)
            if iid is not None:
                out.append((iid, phase, r["location"]))
    return out


GEAR_LOCATIONS = load_gear_locations()
# Wayne's 300-Junk guns as used in phases 1/2 (data.WAYNE_DAY5; L: the run got USP TU and P90).
WAYNE_GUNS = sorted(D.WAYNE_DAY5 | {0x64})
STARTING = dict(gun=0x44, armor=0x96)         # M84F, N Vest (save row at level 1, L)
