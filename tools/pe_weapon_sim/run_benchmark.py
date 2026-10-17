"""Weapon benchmark: python -m pe_weapon_sim.run_benchmark [--fights N] [--out path] [--only part]

Parts: validate (Day 5 boss vs the log), classes (weapon classes x investment x encounters,
vanilla vs current), mods (single effects), range (E0-E6 on keep-away + normal fights),
progression (strategies A/B/C), sensitivity (timing / distance assumptions).
Common random numbers: every loadout meets the same enemy draws and the same fight seeds.
"""
import argparse, datetime, itertools, json, math, os, random, statistics, sys

from . import data as D, engine as E, rules as R, encounters as N
from .progression import Gun, transfer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DEFAULT = os.path.join(HERE, "..", "..", "findings", "data", "pe-weapon-benchmark-%s.json" % datetime.date.today().isoformat())

W = D.load_weapons()
ENEMIES = D.load_enemies()
PROF = D.load_profiles()


# ---- running -------------------------------------------------------------------------------
def run_encounter(rules, cfg, aya, enc, stage, n, seed=7, policy="stand", timing="overlap", armor=None, scale=1.0):
    desc, builder = N.ENCOUNTERS[enc]
    out = []
    for i in range(n):
        kw = builder(stage, ENEMIES, PROF, random.Random(seed * 100003 + i))
        window = kw.pop("window", False)
        chain = kw.pop("chain", False)
        foes, prof = kw.pop("foes"), kw.pop("profile")
        if "threshold" in kw and rules.get("keepaway_threshold_scale", 1.0) != 1.0:   # E6
            kw["threshold"] = {k: v * rules["keepaway_threshold_scale"] for k, v in kw["threshold"].items()}
        if scale != 1.0:
            prof = N.Scaled(prof, scale)
        rng = random.Random(seed * 7919 + i)
        if chain:                                    # three fights of two, magazine carried over
            tot = E.Stats(); loaded = cfg["magazine"]
            for j in range(3):
                c2 = dict(cfg)
                st = E.fight(rules, c2, aya, foes[2 * j:2 * j + 2], prof, rng, policy=policy, timing=timing, armor=armor, **kw)
                for k, v in st.items(): tot.add(k, v)
            tot["won"] = int(tot["won"] == 3)
            out.append(tot)
        else:
            st = E.fight(rules, cfg, aya, foes, prof, rng, policy=policy, timing=timing, armor=armor, **kw)
            st["window"] = int(window)
            out.append(st)
    return out


def summarize(sts):
    def col(k): return [s.get(k, 0) for s in sts]
    t = sorted(col("time"))
    n = len(t)
    mean = statistics.mean(t); sd = statistics.pstdev(t)
    bullets = sum(col("hit")) + sum(col("crit")) + sum(col("graze")) + sum(col("miss")) + sum(col("splash"))
    turns = max(1, sum(col("turns")))
    return dict(
        n=n, time_mean=round(mean, 2), time_median=round(t[n // 2], 2), time_p10=round(t[n // 10], 2),
        time_p90=round(t[(9 * n) // 10], 2), time_ci95=round(1.96 * sd / math.sqrt(n), 2),
        win=round(statistics.mean(col("won")), 3),
        damage=round(statistics.mean(col("damage")), 1),
        taken=round(statistics.mean(col("damage_taken")), 1), hits_taken=round(statistics.mean(col("hits_taken")), 2),
        rounds=round(statistics.mean(col("rounds")), 1), reloads=round(statistics.mean(col("reloads")), 2),
        crit_share=round(sum(col("crit")) / max(1, bullets), 3), graze_share=round(sum(col("graze")) / max(1, bullets), 3),
        miss_share=round(sum(col("miss")) / max(1, bullets), 3),
        out_of_range_turns=round(sum(col("turns_out_of_range")) / turns, 3),
        status=round(statistics.mean([s.get("acid", 0) + s.get("tranq", 0) + s.get("cyanide", 0) for s in sts]), 2),
        overkill=round(statistics.mean(col("overkill")), 1),
        commit_share=round(sum(col("commit_s")) / max(1e-9, sum(col("time"))), 3),
    )


def score(rules, cfg, aya, stage, n=40, encs=("close_normal", "groups", "keepaway_boss", "stationary_boss")):
    """Geometric mean of mean clear time over a mixed suite (lower is better)."""
    logs = []
    for enc in encs:
        sts = run_encounter(rules, cfg, aya, enc, stage, n, seed=11)
        logs.append(math.log(max(0.1, statistics.mean(s["time"] for s in sts) + (0 if all(s["won"] for s in sts) else 60))))
    return math.exp(sum(logs) / len(logs))


# ---- loadouts ------------------------------------------------------------------------------
STAGE_INVEST = {"Day1": 0, "Day2": 2, "Day3": 4, "Day4": 8, "Day5": 12}   # attack boosters + bonus points by stage (A)
GROUPS = {"rof": {"RoF2", "RoF3", "RoF5", "RoF7", "RoF10"}, "mode": {"Random", "Burst", "AttackAll"}, "cmd": {"2Cmd", "3Cmd"}}


def group_of(m):
    for g, s in GROUPS.items():
        if m in s: return g
    return m


def greedy_mods(rules, gun, stage, k, aya):
    """Pick up to k extra effects from the stage's pool, one at a time, by the mixed suite score."""
    chosen = []
    pool = list(D.MOD_POOL[stage])
    base = score(rules, gun_cfg(gun, chosen), aya, stage)
    for _ in range(k):
        best = None
        for m in pool:
            if m in chosen or any(group_of(m) == group_of(c) for c in chosen):
                continue
            s = score(rules, gun_cfg(gun, chosen + [m]), aya, stage)
            if best is None or s < best[0]:
                best = (s, m)
        if not best or best[0] >= base * 0.995:
            break
        chosen.append(best[1]); base = best[0]
    return chosen


def gun_cfg(gun, mods):
    g = Gun(gun.w); g.invested = list(gun.invested); g.received = list(gun.received); g.mods = list(mods)
    return g.config()


def loadout(rules, wid, stage, model, aya):
    g = Gun(W[wid])
    if model == "original":
        return g, []
    if model in ("realistic", "equal_slots"):
        g.invested[0] = STAGE_INVEST[stage]
        k = 2 if model == "equal_slots" else min(max(0, g.free_slots()), D.MOD_BUDGET[stage])
        return g, greedy_mods(rules, g, stage, k, aya)
    if model == "endgame":                              # Day 5 Wayne-tier: +30 attack, +10 range, slots to 5 extra
        g.invested = [30, 10, 10]
        return g, greedy_mods(rules, g, "Day5", 5, aya)
    raise ValueError(model)


CLASS_GUNS = {   # representative guns per class and stage (main game; Wayne guns Day 5)
    "Day4": {"handgun": 0x5B, "machine": 0x6F, "rifle": 0x7D, "grenade": 0x89},
    "Day5": {"handgun": 0x47, "machine": 0x72, "rifle": 0x7D, "shotgun": 0x6A, "grenade": 0x86},
    "Wayne": {"handgun": 0x66, "machine": 0x78, "rifle": 0x82, "shotgun": 0x6E, "grenade": 0x8F},
}
ALL_ENCS = list(N.ENCOUNTERS.keys())


def part_classes(n, rulesets):
    res = []
    plans = [("Day4", "original"), ("Day4", "realistic"), ("Day5", "original"), ("Day5", "realistic"),
             ("Day5", "equal_slots"), ("Wayne", "original"), ("Wayne", "endgame")]
    for stage_key, model in plans:
        stage = "Day5" if stage_key == "Wayne" else stage_key
        aya = D.AYA[stage]
        for cls, wid in CLASS_GUNS[stage_key].items():
            for rn, rules in rulesets.items():
                g, mods = loadout(rules, wid, stage, model, aya)
                cfg = gun_cfg(g, mods)
                row = dict(stage=stage_key, model=model, cls=cls, gun=W[wid].name, rules=rn, mods=mods,
                           power=cfg["power"], range=cfg["range"], magazine=cfg["magazine"], eff=cfg["eff"], enc={})
                for enc in ALL_ENCS:
                    row["enc"][enc] = summarize(run_encounter(rules, cfg, aya, enc, stage, n))
                res.append(row)
                print("classes", stage_key, model, cls, rn, mods, file=sys.stderr)
    return res


SINGLE = ["RoF3", "RoF5", "RoF7", "RoF10", "Random", "Burst", "AttackAll", "Heat", "Frost", "Acid", "Tranq",
          "Cyanide", "Critical", "Quickdraw", "Counter", "2Cmd", "3Cmd"]


def part_mods(n, rulesets):
    """One effect at a time on each class's Day 5 gun (built-ins kept), vs the plain loadout."""
    res = []
    for cls, wid in CLASS_GUNS["Day5"].items():
        for rn, rules in rulesets.items():
            base_cfg = W[wid].config([], bonus_attack=W[wid].bonus_attack + STAGE_INVEST["Day5"])
            encs = ("close_normal", "groups", "keepaway_boss", "stationary_boss", "endurance")
            base = {e: summarize(run_encounter(rules, base_cfg, D.AYA["Day5"], e, "Day5", n)) for e in encs}
            for m in SINGLE:
                cfg = W[wid].config([m], bonus_attack=W[wid].bonus_attack + STAGE_INVEST["Day5"])
                row = dict(cls=cls, gun=W[wid].name, rules=rn, mod=m, enc={})
                for e in encs:
                    s = summarize(run_encounter(rules, cfg, D.AYA["Day5"], e, "Day5", n))
                    row["enc"][e] = dict(time_vs_base=round(s["time_mean"] / base[e]["time_mean"] - 1, 3),
                                         taken_vs_base=round(s["taken"] / max(1e-9, base[e]["taken"]) - 1, 3),
                                         rounds_vs_base=round(s["rounds"] / max(1e-9, base[e]["rounds"]) - 1, 3))
                res.append(row)
            print("mods", cls, rn, file=sys.stderr)
    return res


def part_range(n):
    """E0..E6 on realistic Day 5 loadouts (chosen under CURRENT so only the rule changes)."""
    res = []
    loads = {}
    for cls, wid in CLASS_GUNS["Day5"].items():
        g, mods = loadout(R.CURRENT, wid, "Day5", "realistic", D.AYA["Day5"])
        loads[cls] = gun_cfg(g, mods)
    exps = [("E0", R.CURRENT)] + [(e, R.experimental(e)) for e in ("E1", "E2", "E3", "E4", "E5", "E6")] + \
           [("E1+E4", R.experimental("E1", "E4")), ("E2+E4", R.experimental("E2", "E4")), ("E3+E6", R.experimental("E3", "E6"))]
    encs = ("keepaway_boss", "scripted_day5", "close_normal", "medium_mobile", "groups")
    for name, rules in exps:
        for cls, cfg in loads.items():
            for policy in ("stand", "approach"):
                row = dict(exp=name, cls=cls, policy=policy, enc={})
                for e in encs:
                    kw_aya = D.AYA_LEVEL21 if e == "scripted_day5" else D.AYA["Day5"]
                    sts = run_encounter(rules, cfg, kw_aya, e, "Day5", n, policy=policy)
                    if e == "scripted_day5" and rules.get("keepaway_threshold_scale", 1.0) != 1.0:
                        pass  # threshold scaled inside below
                    row["enc"][e] = summarize(sts)
                res.append(row)
        print("range", name, file=sys.stderr)
    return res, {c: dict(eff=v["eff"], power=v["power"], range=v["range"]) for c, v in loads.items()}


def part_validate(n):
    """Day 5 boss part 1 vs the three logged attempts (time / bullets / HP lost)."""
    logged = [dict(gun="M79 (0x89)", range=1281, secs=12, shots=15, taken=153),
              dict(gun="M79 (0x89)", range=1281, secs=27, shots=38, taken=434),
              dict(gun="M9 upgraded (0x45)", range=1171, secs=8, shots=9, taken=131)]
    aya = D.AYA_LEVEL21
    out = dict(logged=logged, model=[])
    # Per-bullet damage vs def 33 was 19 (M79) and 20 (M9) in the log; the loadouts are not logged, so two
    # hypotheses for the M79 (RoF 2 with an implied low power, RoF 5 with attack 66) and the M9 at RoF 3, attack 40.
    cases = [("M79 RoF2 (power fit to 19/bullet)", 0x89, ["RoF2"], 23, 1281),
             ("M79 RoF5 (attack 66 fits 19/bullet)", 0x89, ["RoF5"], 66, 1281),
             ("M9 RoF3 (attack 40 fits 20/bullet)", 0x45, ["RoF3"], 40, 1171)]
    for label, wid, mods, power, rng_u in cases:
        cfg = W[wid].config(mods)
        cfg = dict(cfg, power=power, range=rng_u)
        for rn, rules in (("current", R.CURRENT),):
            sts = run_encounter(rules, cfg, aya, "scripted_day5", "Day5", n)
            s = summarize(sts)
            out["model"].append(dict(case=label, rules=rn, **{k: s[k] for k in ("time_mean", "time_median", "time_p10", "time_p90", "taken", "rounds", "graze_share", "miss_share", "out_of_range_turns")}))
    return out


def part_progression(n):
    """Strategies over Days 1-5 (current rules): A one class, transfers within it; B = A plus a
    rifle kept for keep-away/boss fights (weapon switch costs half a bar); C always the best new
    gun of any class (bonuses follow by Tool)."""
    res = []
    stages = D.STAGES
    for strat in ("A:handgun", "A:machine", "A:rifle", "A:grenade", "B:handgun+rifle", "B:machine+rifle", "C:best"):
        row = dict(strategy=strat, days={})
        for st in stages:
            aya = D.AYA[st]
            avail = [w for s in stages[:stages.index(st) + 1] for w in D.AVAILABLE[s]]
            avail = [w for w in avail if (st == "Day5" or w not in D.WAYNE_DAY5)]
            def best_of(kinds):
                cands = [w for w in avail if D.KIND[W[w].kind] in kinds]
                if not cands: return None
                return max(cands, key=lambda w: W[w].attack + W[w].bonus_attack + (5 if W[w].free_slots() > 1 else 0))
            if strat.startswith("C"):
                cands = avail
                prim = min(cands, key=lambda w: score(R.CURRENT, Gun(W[w]).config(), aya, st, n=15))
            else:
                prim = best_of({strat.split(":")[1].split("+")[0]}) or best_of({"handgun"})
            g = Gun(W[prim]); g.invested[0] = STAGE_INVEST[st] * 2   # everything invested in the main gun
            k = min(max(0, g.free_slots()), D.MOD_BUDGET[st])
            g.mods = greedy_mods(R.CURRENT, g, st, k, aya) if k else []
            cfg = g.config()
            sec_cfg = None
            if strat.startswith("B"):
                sec = best_of({"rifle"})
                if sec: sec_cfg = Gun(W[sec]).config()
            day = {}
            for e in ("close_normal", "groups", "keepaway_boss", "stationary_boss"):
                use = cfg
                if sec_cfg and e in ("keepaway_boss",):
                    use = sec_cfg                         # switch at the start: half a bar (current)
                s = summarize(run_encounter(R.CURRENT, use, aya, e, st, n))
                if use is sec_cfg:
                    s["time_mean"] = round(s["time_mean"] + E.fill_seconds(aya["stat22"], W[prim].kind) / 2, 2)
                day[e] = dict(gun=(W[prim].name if use is cfg else "rifle"), time=s["time_mean"], taken=s["taken"])
            row["days"][st] = dict(main=W[prim].name, mods=g.mods, enc=day)
        res.append(row)
        print("progression", strat, file=sys.stderr)
    return res


def part_sensitivity(n):
    """Do class rankings survive the timing and distance assumptions?"""
    res = []
    for timing in ("overlap", "serial"):
        for scale in (0.8, 1.0, 1.25):
            for cls, wid in CLASS_GUNS["Day5"].items():
                cfg = W[wid].config([], bonus_attack=W[wid].bonus_attack + STAGE_INVEST["Day5"])
                row = dict(timing=timing, scale=scale, cls=cls, enc={})
                for e in ("close_normal", "keepaway_boss", "stationary_boss"):
                    s = summarize(run_encounter(R.CURRENT, cfg, D.AYA["Day5"], e, "Day5", n, timing=timing, scale=scale))
                    row["enc"][e] = s["time_mean"]
                res.append(row)
    return res


def best_class_loadouts(stage, rules, permits=0):
    """For each class: the best gun available by `stage` (realistic loadout, greedy mods, +permits slots)."""
    aya = D.AYA[stage]
    avail = [w for s in D.STAGES[:D.STAGES.index(stage) + 1] for w in D.AVAILABLE[s]]
    out = {}
    for cls in ("handgun", "machine", "rifle", "shotgun", "grenade"):
        cands = [w for w in avail if D.KIND[W[w].kind] == cls]
        best = None
        for w in cands:
            g = Gun(W[w]); g.invested[0] = STAGE_INVEST[stage]; g.slots_bought = permits
            k = min(max(0, g.free_slots()), D.MOD_BUDGET[stage] + permits)
            mods = greedy_mods(rules, g, stage, k, aya)
            s = score(rules, gun_cfg(g, mods) if True else None, aya, stage)
            if best is None or s < best[0]:
                best = (s, w, g, mods)
        if best:
            out[cls] = best
    return out


def part_bestclass(n, rulesets):
    res = []
    for stage, permits in (("Day3", 0), ("Day4", 0), ("Day5", 0), ("Day5", 1)):
        aya = D.AYA[stage]
        for rn, rules in rulesets.items():
            for cls, (sc, w, g, mods) in best_class_loadouts(stage, rules, permits).items():
                cfg = gun_cfg(g, mods)
                row = dict(stage=stage + ("+permit" if permits else ""), model="best-in-class", cls=cls, gun=W[w].name,
                           rules=rn, mods=mods, power=cfg["power"], range=cfg["range"], eff=cfg["eff"], enc={})
                for enc in ALL_ENCS:
                    row["enc"][enc] = summarize(run_encounter(rules, cfg, aya, enc, stage, n))
                res.append(row)
                print("bestclass", stage, permits, rn, cls, W[w].name, mods, file=sys.stderr)
    return res


def part_anim(n):
    """Animation loop length x0.5 / x1 / x2 on the Day 5 best-in-class loadouts (current rules)."""
    res = []
    loads = best_class_loadouts("Day5", R.CURRENT)
    for scale in (0.5, 1.0, 2.0):
        E.ANIM_SCALE = scale
        for cls, (sc, w, g, mods) in loads.items():
            cfg = gun_cfg(g, mods)
            row = dict(anim_scale=scale, cls=cls, gun=W[w].name, mods=mods, enc={})
            for e in ("close_normal", "groups", "keepaway_boss", "stationary_boss"):
                row["enc"][e] = summarize(run_encounter(R.CURRENT, cfg, D.AYA["Day5"], e, "Day5", n))["time_mean"]
            res.append(row)
        # RoF ladder on the M8000 handgun (built-in 2 Commands) under each animation scale
        for m in ("RoF3", "RoF5", "RoF7", "RoF10"):
            cfg = W[0x48].config([m], bonus_attack=W[0x48].bonus_attack + STAGE_INVEST["Day5"])
            row = dict(anim_scale=scale, cls="handgun-rof", gun="M8000", mods=[m], enc={})
            for e in ("close_normal", "stationary_boss"):
                row["enc"][e] = summarize(run_encounter(R.CURRENT, cfg, D.AYA["Day5"], e, "Day5", n))["time_mean"]
            res.append(row)
    E.ANIM_SCALE = 1.0
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=300)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only", default="validate,classes,mods,range,progression,sensitivity")
    a = ap.parse_args()
    parts = a.only.split(",")
    out = dict(date=datetime.date.today().isoformat(), fights=a.fights, tick_hz=E.TICK_HZ,
               validation=[dict(mechanic=m, status=s, source=src) for m, s, src in R.VALIDATION])
    if os.path.exists(a.out):
        try: out.update({k: v for k, v in json.load(open(a.out)).items() if k not in out})
        except Exception: pass
    rs = {"vanilla": R.VANILLA, "current": R.CURRENT}
    if "validate" in parts: out["validate"] = part_validate(a.fights)
    if "classes" in parts: out["classes"] = part_classes(a.fights, rs)
    if "mods" in parts: out["mods"] = part_mods(max(100, a.fights // 2), rs)
    if "range" in parts: out["range"], out["range_loadouts"] = part_range(a.fights)
    if "progression" in parts: out["progression"] = part_progression(max(60, a.fights // 4))
    if "sensitivity" in parts: out["sensitivity"] = part_sensitivity(max(100, a.fights // 2))
    if "bestclass" in parts: out["bestclass"] = part_bestclass(a.fights, rs)
    if "anim" in parts: out["anim"] = part_anim(max(100, a.fights // 2))
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
