"""Gun x effect-combination x enemy simulator (vanilla vs proposed rules).

For each area of the main game it takes the guns a player has there (stats from the RPGClassics
Parasite Eve shrine weapons page, 2026-10-14; to be checked against the game's item table), every
legal combination of effects that fits the gun's slots (one per group: Rate of Fire, spread mode,
commands; the rest on/off), and simulates fights against that area's real enemies
(findings/data/pe-enemies-wiki-2026-10-14.csv). Rules, decomp-backed formulas and guesses come
from pe_mod_sim.py.

Reports per area: the best builds, how close the best build with each effect gets to the overall
best (is every effect worth a slot somewhere?), and builds far ahead of the rest (broken combos).

Usage: python pe_combo_sim.py [--fights N] [--max-mods K] [--procs P]
"""
import argparse, itertools, multiprocessing as mp, os, random, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe_mod_sim as M

# ---- guns: name, type, attack (base+bonus), range, magazine, slots, built-in effects ------
# ATB factor by type (decomp scale table 10/8/10/8/8/4/10/20; mapping by gun type: guess G5).
ATB = {"handgun": 1.0, "machine": 1.0, "rifle": 0.8, "shotgun": 0.8, "grenade": 0.8, "club": 2.0}
GUNS = {  # area -> guns (main game, where found)
    "Day 1 Theater": [("P220", "handgun", 15, 55, 5, 1), ("M1911A1", "handgun", 17, 60, 6, 2)],
    "Day 2 Central Park": [("M9", "handgun", 17, 54, 9, 3), ("M16A1", "rifle", 35, 112, 16, 1)],
    "Day 3 NYPD": [("M92F", "handgun", 29, 51, 11, 3), ("G19", "handgun", 32, 58, 10, 3),
                   ("MP5K", "machine", 36, 43, 24, 1), ("M11", "machine", 33, 42, 21, 2)],
    "Day 4 Hospital": [("G23", "handgun", 48, 60, 10, 2), ("SG550", "rifle", 40, 110, 21, 2),
                       ("G3A3", "rifle", 44, 123, 19, 3), ("M79", "grenade", 45, 67, 5, 3)],
    "Day 5 Chinatown-Museum": [("M9-3", "handgun", 55, 58, 13, 3), ("M8000", "handgun", 57, 58, 12, 3),
                               ("PPK", "handgun", 47, 49, 12, 2), ("MP5PDW", "machine", 53, 46, 25, 2),
                               ("M500", "shotgun", 59, 63, 7, 10), ("M203-4", "grenade", 58, 67, 8, 5)],
}
# G6 Aya's offense by area (stat1E; per-shot power = offense / 5 + gun attack).
OFFENSE = {"Day 1 Theater": 35, "Day 2 Central Park": 55, "Day 3 NYPD": 70,
           "Day 4 Hospital": 90, "Day 5 Chinatown-Museum": 120}

# ---- effects: groups ----------------------------------------------------------------------
ROF = [None, 1, 2, 3, 5, 7, 10]          # None = the gun's plain single shot (RoF 1, no slot)
SPREAD = [None, "random", "burst", "all"]
COMMANDS = [None, 2, 3]
FLAGS = ["heat", "frost", "cyanide", "acid", "tranq", "counter", "quickdraw", "critical"]

# Main-game pool: Cyanide and 3 Commands are only found in the Chrysler Building (EX Game).
EXCLUDED = set()

def builds(slots, max_mods):
    k = min(slots, max_mods)
    out = []
    flags = [f for f in FLAGS if f not in EXCLUDED]
    for rof in ROF:
        for sp in SPREAD:
            for cm in COMMANDS:
                if cm == 3 and "3cmd" in EXCLUDED:
                    continue
                used = (rof is not None) + (sp is not None) + (cm is not None)
                if used > k:
                    continue
                for n in range(0, k - used + 1):
                    for fl in itertools.combinations(flags, n):
                        eff = {"rof": rof or 1}
                        if sp: eff["mode"] = sp
                        if cm: eff["commands"] = cm
                        for f in fl: eff[f] = True
                        out.append(eff)
    return out

def label(eff):
    parts = ["RoF%d" % eff["rof"]]
    if "mode" in eff: parts.append({"random": "Random", "burst": "Burst", "all": "AtkAll"}[eff["mode"]])
    if "commands" in eff: parts.append("%dCmd" % eff["commands"])
    parts += [f.capitalize() for f in FLAGS if eff.get(f)]
    return "+".join(parts)

# ---- one fight with a real gun -----------------------------------------------------------------
def fight(rules, eff, gun, offense, group, rng, stat22):
    name, kind, atk, rng_range, mag, slots = gun
    rof = eff.get("rof", 1)
    shots = rof * 3 // 2 if eff.get("mode") == "random" else rof
    pct = rules["hit_pct"][rof]
    commands = eff.get("commands", 1)
    attack = offense / 5.0 + atk
    per_shot = attack * pct / 100.0
    atb = ATB[kind]
    foes = [dict(e, cur=e["hp"], poisoned=False, stopped=0, d=M.defense_of(e),
                 t_next=rng.uniform(0.4, 1.2), dist=rng.uniform(15, 75) / rng_range) for e in group]
    t, ammo, taken, loaded = 0.0, 0.0, 0, mag
    qd = 0.0
    if eff.get("quickdraw"):
        qd = min(0.9, (stat22 + rules["quickdraw_bonus"]) / 100.0)
    aya_next = 0.0 if rng.random() < qd else 1.0 / atb

    def shot_damage(f, power, split):
        d = f["dist"]
        if d > 1.8: return 0.0
        q = 1.0
        if d > 1.0:
            p_hit = 0.25 if d > 1.5 else 0.5 if d > 1.2 else 0.8
            if rng.random() >= p_hit: return 0.0
            q = 0.3
        else:
            base = 5 if d > 0.8 else 20 if d > 0.5 else 50
            if rng.random() * 100 < base + (rules["crit_bonus"] if eff.get("critical") else 0): q = 1.5
        dmg = power - f["d"] / split
        if dmg <= 0: return 1.0
        dmg *= q
        m = 1.0
        if eff.get("heat") or eff.get("frost"):
            h = f["heat"] if eff.get("heat") else None
            fr = f["frost"] if eff.get("frost") else None
            if rules["elem_best_of_two"]:
                m = max(rules["elem"][x] for x in (h, fr) if x)
            else:
                state = {"Strong": "r", "Weak": "w"}.get(h) if h else None
                if state != "w" and fr:
                    s2 = {"Strong": "r", "Weak": "w"}.get(fr)
                    if s2: state = s2
                m = {"r": rules["elem"]["Strong"], "w": rules["elem"]["Weak"]}.get(state, 1.0)
        return max(1.0, dmg * m)

    def status(f, key):
        if f["boss"] and rules["boss_status_immune"]: return False
        table = M.VANILLA["status_chance"] if key == "cyanide" else rules["status_chance"]
        return rng.random() < table[f[key]]

    def hit(f, power):
        f["cur"] -= shot_damage(f, power, rof)
        if f["cur"] > 0 and eff.get("cyanide") and status(f, "cyanide"): f["cur"] = 0
        if eff.get("acid") and not f["poisoned"] and status(f, "acid"): f["poisoned"] = True
        if eff.get("tranq") and status(f, "tranq"): f["stopped"] = max(f["stopped"], 3)

    guard = 0
    while any(f["cur"] > 0 for f in foes) and guard < 500:
        guard += 1
        alive = [f for f in foes if f["cur"] > 0]
        nxt = min(f["t_next"] for f in alive)
        if aya_next <= nxt:
            t = aya_next
            fired = 0
            for _ in range(commands):
                alive = [f for f in foes if f["cur"] > 0]
                if not alive: break
                if loaded <= 0:                         # G7: an empty magazine costs this action to reload
                    loaded = mag
                    continue
                n = min(shots, loaded)
                tgt = min(alive, key=lambda f: f["cur"])
                if eff.get("mode") == "all":
                    for f in alive:
                        for _ in range(n): hit(f, per_shot)
                    cost = n * (len(alive) if rules["attack_all_ammo_per_target"] else 1)
                else:
                    for _ in range(n):
                        alive = [f for f in foes if f["cur"] > 0]
                        if not alive: break
                        f = rng.choice(alive) if eff.get("mode") == "random" else (
                            tgt if tgt["cur"] > 0 else min(alive, key=lambda x: x["cur"]))
                        hit(f, per_shot)
                        if eff.get("mode") == "burst":   # ~90 degree cone: A8, 40% per other foe
                            for o in alive:
                                if o is not f and o["cur"] > 0 and rng.random() < 0.4: hit(o, per_shot)
                    cost = min(n, 5) + max(0, n - 5) * rules["ammo_above_5"]
                loaded -= min(loaded, n)
                ammo += cost
                fired += n
            aya_next = t + 1.0 / atb + 0.04 * fired
        else:
            f = min(alive, key=lambda x: x["t_next"])
            t = f["t_next"]
            f["t_next"] = t + rng.uniform(1.0, 1.4)
            if f["poisoned"]: f["cur"] -= f["hp"] * rules["acid_tick"]
            if f["cur"] <= 0: continue
            if f["stopped"] > 0: f["stopped"] -= 1; continue
            if rng.random() < 0.75:
                taken += 1
                if eff.get("counter") and rng.random() < rules["counter_chance"]:
                    f["cur"] -= shot_damage(f, attack * rules["counter_power"], 1)
    return t, ammo, taken

# ---- runs -----------------------------------------------------------------------------------------
def eval_job(args):
    rules_name, area, gun, eff, groups, seed = args
    rules = M.VANILLA if rules_name == "vanilla" else M.PROPOSED
    rng = random.Random(seed)
    stat22 = M.STAT22_BY_AREA.get(area, 35)
    res = [fight(rules, eff, gun, OFFENSE[area], g, rng, stat22) for g in groups]
    return (rules_name, area, gun[0], label(eff), eff,
            statistics.mean(r[0] for r in res), statistics.mean(r[1] for r in res),
            statistics.mean(r[2] for r in res))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=150)
    ap.add_argument("--max-mods", type=int, default=3)
    ap.add_argument("--procs", type=int, default=max(1, mp.cpu_count() - 1))
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--pool", choices=("main", "all"), default="main")
    a = ap.parse_args()
    if a.pool == "main":
        EXCLUDED.update({"cyanide", "3cmd"})
    print("effect pool:", "main game (no Cyanide, no 3 Commands)" if a.pool == "main" else "everything (EX Game)")
    here = os.path.dirname(os.path.abspath(__file__))
    enemies = M.load_enemies(os.path.join(here, "..", "findings", "data", "pe-enemies-wiki-2026-10-14.csv"))
    rng = random.Random(a.seed)
    jobs = []
    for area, guns in GUNS.items():
        kws = dict(M.AREAS)[area]
        pool = M.area_groups(enemies, kws)
        groups = [[rng.choice(pool) for _ in range(rng.choice((1, 2, 2, 3)))] for _ in range(a.fights)]
        for gun in guns:
            for eff in builds(gun[5], a.max_mods):
                for rn in ("vanilla", "proposed"):
                    jobs.append((rn, area, gun, eff, groups, a.seed + 1))
    print("jobs:", len(jobs), "fights each:", a.fights, file=sys.stderr)
    with mp.Pool(a.procs) as p:
        results = p.map(eval_job, jobs, chunksize=64)
    report(results)

def report(results):
    for rn in ("vanilla", "proposed"):
        print("\n" + "=" * 100 + "\n%s rules" % rn.upper())
        for area in GUNS:
            rows = [r for r in results if r[0] == rn and r[1] == area]
            best = min(rows, key=lambda r: r[5])
            print("\n-- %s: best %s %s  time %.2f ammo %.1f hits %.2f" % (area, best[2], best[3], best[5], best[6], best[7]))
            top = sorted(rows, key=lambda r: r[5])[:6]
            for r in top:
                print("   %-8s %-40s time %5.2f (%+4.0f%%)  ammo %5.1f  hits %4.2f" % (
                    r[2], r[3], r[5], 100 * (r[5] / best[5] - 1), r[6], r[7]))
            plain = min((r for r in rows if r[4] == {"rof": 1}), key=lambda r: r[5])
            print("   effect viability (best build containing it, vs best overall; plain gun %+.0f%%):" % (100 * (plain[5] / best[5] - 1)))
            line = []
            for key, test in [("RoF2", lambda e: e["rof"] == 2), ("RoF3", lambda e: e["rof"] == 3),
                              ("RoF5", lambda e: e["rof"] == 5), ("RoF7", lambda e: e["rof"] == 7),
                              ("RoF10", lambda e: e["rof"] == 10), ("Random", lambda e: e.get("mode") == "random"),
                              ("Burst", lambda e: e.get("mode") == "burst"), ("AtkAll", lambda e: e.get("mode") == "all"),
                              ("2Cmd", lambda e: e.get("commands") == 2), ("3Cmd", lambda e: e.get("commands") == 3)] + \
                             [(f.capitalize(), (lambda f: lambda e: e.get(f))(f)) for f in FLAGS]:
                cand = [r for r in rows if test(r[4])]
                if cand:
                    b = min(cand, key=lambda r: r[5])
                    line.append("%s %+.0f%%" % (key, 100 * (b[5] / best[5] - 1)))
            print("     " + ", ".join(line))
            second = sorted(rows, key=lambda r: r[5])
            gap = 100 * (second[min(10, len(second) - 1)][5] / best[5] - 1)
            print("   top-1 vs 10th best: %.0f%% gap" % gap)

if __name__ == "__main__":
    main()
