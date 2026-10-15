"""Gun progression simulator: how Tool transfer rules shape a playthrough (main game, Days 1-5).

Guns arrive day by day (RPGClassics weapons page, 2026-10-14: base attack, range, magazine, slots,
built-in effects, own +bonus), +N boosters and Tools arrive per day, and the player keeps one gun
whose +bonus grows. When a better gun turns up, the bonus moves over with a Tool under one of four
rules:
  A  vanilla: any gun to any gun, 1 Tool
  B  same type only (other types: the bonus stays behind)
  C  other types get half the bonus
  D  other types cost 2 Tools
Two players: "best" (switches whenever a gun is faster with the bonus it would get) and "loyal"
(picks one type on Day 2 and only switches within it; the Wayne gun on Day 5 is of that type).
Gun strength = time to clear the area's fights (pe_combo_sim.fight, proposed Mod Effects rules,
the gun's built-in effects). Only the attack bonus is modelled (range / bullet bonuses are small).

Usage: python pe_gun_progression_sim.py [--runs N] [--fights N]
"""
import argparse, os, random, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe_mod_sim as M
import pe_combo_sim as C

# name, type, base attack, own +bonus, range, magazine, slots, built-in effects, day found
GUNS = [
    ("P220", "handgun", 14, 1, 55, 5, 1, {"rof": 2}, 1),
    ("M1911A1", "handgun", 15, 2, 60, 6, 2, {"rof": 3}, 1),
    ("M9", "handgun", 17, 0, 54, 9, 3, {"rof": 3}, 2),
    ("M16A1", "rifle", 34, 1, 112, 16, 1, {"rof": 2}, 2),
    ("M92F", "handgun", 28, 1, 51, 11, 3, {"rof": 3}, 3),
    ("G19", "handgun", 30, 2, 58, 10, 3, {"rof": 3}, 3),
    ("MP5K", "machine", 35, 1, 43, 24, 1, {"rof": 3}, 3),
    ("M11", "machine", 32, 1, 42, 21, 2, {"rof": 5, "mode": "random"}, 3),
    ("SG550", "rifle", 40, 0, 110, 21, 2, {"rof": 2}, 3),
    ("G23", "handgun", 47, 1, 60, 10, 2, {"rof": 3}, 4),
    ("G3A3", "rifle", 43, 1, 123, 19, 3, {"rof": 1}, 4),
    ("M79", "grenade", 44, 1, 67, 5, 3, {"rof": 2, "tranq": True}, 4),
    ("PPK", "handgun", 45, 2, 49, 12, 2, {"rof": 5, "quickdraw": True}, 5),
    ("M9-3", "handgun", 53, 2, 58, 13, 3, {"rof": 3, "commands": 2}, 5),
    ("M8000", "handgun", 57, 0, 58, 12, 3, {"rof": 1, "commands": 2}, 5),
    ("MP5PDW", "machine", 52, 1, 46, 25, 2, {"rof": 7, "mode": "random"}, 5),
    ("M870", "shotgun", 48, 1, 60, 7, 6, {"rof": 2, "mode": "burst"}, 5),
    ("M500", "shotgun", 57, 2, 63, 7, 10, {"rof": 2, "mode": "burst"}, 5),
    ("M203-4", "grenade", 57, 1, 67, 8, 5, {"rof": 2, "frost": True}, 5),
]
WAYNE = {  # one Wayne gun at the start of Day 5 (300 Junk), of the player's choice
    "handgun": ("DE50AE7", "handgun", 123, 2, 56, 17, 10, {"rof": 2}, 5),
    "shotgun": ("M10B", "shotgun", 120, 1, 70, 7, 4, {"rof": 3, "mode": "burst"}, 5),
    "machine": ("P90", "machine", 122, 1, 53, 201, 5, {"rof": 10, "mode": "all"}, 5),
    "rifle": ("MAG", "rifle", 151, 1, 185, 21, 4, {"rof": 2, "critical": True}, 5),
    "grenade": ("HK40", "grenade", 115, 1, 70, 9, 8, {"rof": 1}, 5),
}
AREA = {1: "Day 1 Theater", 2: "Day 2 Central Park", 3: "Day 3 NYPD", 4: "Day 4 Hospital",
        5: "Day 5 Chinatown-Museum"}
# Per day: attack boosters found (fixed Offense +N finds and gun-stat rare drops) and Tools.
BOOSTERS = {1: [1], 2: [1, 1], 3: [1, 2], 4: [2, 2], 5: [2, 3, 3]}
EXTRA_BOOSTER_P = {1: 0.0, 2: 0.3, 3: 0.4, 4: 0.5, 5: 1.0}   # chance of one more (rare drop)
TOOLS = {1: 1, 2: 3, 3: 4, 4: 3, 5: 6}

SYSTEMS = {
    "A vanilla": lambda same: (1.0, 1),
    "B same type only": lambda same: (1.0, 1) if same else (0.0, 0),
    "C half across types": lambda same: (1.0, 1) if same else (0.5, 1),
    "D 2 Tools across types": lambda same: (1.0, 1) if same else (1.0, 2),
}

_cache = {}
def strength(gun, bonus, day, fights, groups):
    """Mean time to clear the area's fights with this gun and attack bonus (lower is better)."""
    key = (gun[0], int(bonus), day)
    if key in _cache: return _cache[key]
    name, kind, atk, own, rng_r, mag, slots, eff, _ = gun
    g = (name, kind, atk + bonus, rng_r, mag, slots)
    r = random.Random(17)
    area = AREA[day]
    t = statistics.mean(C.fight(M.PROPOSED, eff, g, C.OFFENSE[area], grp, r, M.STAT22_BY_AREA[area])[0]
                        for grp in groups[day][:fights])
    _cache[key] = t
    return t

def play(system, policy, loyal_type, seed, fights, groups):
    rng = random.Random(seed)
    rule = SYSTEMS[system]
    gun, bonus, tools = GUNS[0], float(GUNS[0][3]), 0
    lost, switches, type_changes, by_day = 0.0, 0, 0, {}
    for day in range(1, 6):
        tools += TOOLS[day]
        found = [g for g in GUNS if g[8] == day]
        if day == 5:
            want = loyal_type if policy == "loyal" else min(
                WAYNE, key=lambda k: strength(WAYNE[k], WAYNE[k][3] + bonus * rule(WAYNE[k][1] == gun[1])[0], 5, fights, groups))
            found = found + [WAYNE[want]]
        for b in BOOSTERS[day] + ([rng.choice((1, 2, 3))] if rng.random() < EXTRA_BOOSTER_P[day] else []):
            bonus += b                                  # boosters go on the gun in hand
        for cand in found:
            if policy == "loyal" and day >= 2 and cand[1] != loyal_type:
                continue
            same = cand[1] == gun[1]
            share, cost = rule(same)
            moved = bonus * share if tools >= cost and cost > 0 else 0.0
            new_bonus = cand[3] + moved
            if policy == "loyal" and gun[1] != loyal_type and day >= 2:
                better = True                           # move onto the chosen type as soon as possible
            else:
                better = strength(cand, new_bonus, day, fights, groups) < 0.97 * strength(gun, bonus, day, fights, groups)
            if better:
                if moved: tools -= cost
                lost += bonus - moved
                type_changes += not same
                switches += 1
                gun, bonus = cand, new_bonus
        by_day[day] = strength(gun, bonus, day, fights, groups)
    return by_day, lost, switches, type_changes, gun[0], gun[1], bonus

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=60)
    ap.add_argument("--fights", type=int, default=120)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    enemies = M.load_enemies(os.path.join(here, "..", "findings", "data", "pe-enemies-wiki-2026-10-14.csv"))
    r = random.Random(3)
    groups = {}
    for day, area in AREA.items():
        pool = M.area_groups(enemies, dict(M.AREAS)[area])
        groups[day] = [[r.choice(pool) for _ in range(r.choice((1, 2, 2, 3)))] for _ in range(a.fights)]
    base = None
    print("Gun progression, %d runs per system; fight time = mean seconds to clear an area fight" % a.runs)
    for system in SYSTEMS:
        res = [play(system, "best", None, s, a.fights, groups) for s in range(a.runs)]
        days = {d: statistics.mean(x[0][d] for x in res) for d in range(1, 6)}
        if base is None: base = days
        ends = {}
        for x in res: ends[x[5]] = ends.get(x[5], 0) + 1
        print("\n== %s ==" % system)
        print("  'best' player: fight time by day " + "  ".join("D%d %.2f (%+.0f%%)" % (d, days[d], 100 * (days[d] / base[d] - 1)) for d in range(1, 6)))
        print("    bonus lost to switching %.1f, switches %.1f, type changes %.1f, final bonus +%.1f, ends with %s" % (
            statistics.mean(x[1] for x in res), statistics.mean(x[2] for x in res), statistics.mean(x[3] for x in res),
            statistics.mean(x[6] for x in res), ", ".join("%s %d%%" % (k, 100 * v // a.runs) for k, v in sorted(ends.items(), key=lambda kv: -kv[1]))))
        loyal = {}
        for t in ("handgun", "rifle", "machine", "shotgun", "grenade"):
            lr = [play(system, "loyal", t, s, a.fights, groups) for s in range(max(10, a.runs // 3))]
            loyal[t] = (statistics.mean(x[0][4] for x in lr), statistics.mean(x[0][5] for x in lr))
        best4 = min(v[0] for v in loyal.values()); best5 = min(v[1] for v in loyal.values())
        print("  'loyal' player by type (Day 4 / Day 5 fight time, vs the best type):")
        print("    " + "  ".join("%s %.2f/%.2f (%+.0f%%/%+.0f%%)" % (t, v[0], v[1], 100 * (v[0] / best4 - 1), 100 * (v[1] / best5 - 1)) for t, v in loyal.items()))

if __name__ == "__main__":
    main()
