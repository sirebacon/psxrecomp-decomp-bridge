"""Weapon balance phase 2: python -m pe_weapon_sim.run_phase2 [--fights N] [--only parts]

Parts: endurance, movement, crit, builds (stress weapons x builds x archetypes), matrix
(experiments x stress weapons x encounters x policies), regret (effect opportunity cost), rof,
split (two-weapon investment), boss (Day 5 keep-away with movement).
Writes findings/data/pe-weapon-phase2-<date>.json; the 2026-10-17 benchmark file is left as is.
"""
import argparse, datetime, json, math, os, random, statistics, sys

from . import data as D, engine as E, rules as R, encounters as N
from .progression import Gun
from .run_benchmark import run_encounter, summarize, score, W, ENEMIES, PROF, STAGE_INVEST, group_of

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "findings", "data", "pe-weapon-phase2-%s.json" % datetime.date.today().isoformat())
ENCS = list(N.ENCOUNTERS.keys())
STRESS = {"P90": 0x78, "MAG": 0x82, "DE50AE7": 0x66, "M10B": 0x6E, "M500": 0x6A, "HK40": 0x8F}
POOL = D.MOD_POOL["Day5"]
STAGE = "Day5"
PERMITS = 1          # one Mod Permit slot by the end of Day 5 (current economy)


def aya_for(enc):
    return D.AYA_LEVEL21 if enc == "scripted_day5" else D.AYA[STAGE]


def evaluate(rules, cfg, n, encs=ENCS, **kw):
    return {e: summarize(run_encounter(rules, cfg, aya_for(e), e, STAGE, n, **kw)) for e in encs}


def make_gun(wid, invest=None):
    g = Gun(W[wid]); g.invested[0] = STAGE_INVEST[STAGE] if invest is None else invest; g.slots_bought = PERMITS
    return g


def cfg_of(g, mods):
    h = Gun(g.w); h.invested = list(g.invested); h.slots_bought = g.slots_bought; h.mods = list(mods)
    return h.config()


def k_slots(g):
    return min(max(0, g.free_slots()), D.MOD_BUDGET[STAGE] + PERMITS)


def greedy(rules, g, pool, k, n=30, encs=("close_normal", "groups", "keepaway_boss", "stationary_boss"), **kw):
    chosen = []
    def sc(mods):
        logs = []
        for e in encs:
            s = run_encounter(rules, cfg_of(g, mods), aya_for(e), e, STAGE, n, seed=11, **kw)
            logs.append(math.log(max(0.1, statistics.mean(x["time"] for x in s))))
        return math.exp(sum(logs) / len(logs))
    base = sc(chosen)
    for _ in range(k):
        best = None
        for m in pool:
            if m in chosen or any(group_of(m) == group_of(c) for c in chosen): continue
            s = sc(chosen + [m])
            if best is None or s < best[0]: best = (s, m)
        if not best or best[0] >= base * 0.995: break
        chosen.append(best[1]); base = best[0]
    return chosen, base


ARCHETYPES = {   # preferred order; truncated to the gun's free slots
    "general": None,                                        # greedy optimum
    "burst": ["2Cmd", "Critical", "Quickdraw", "Frost"],
    "status": ["Acid", "Tranq", "Burst", "AttackAll"],
    "critical": ["Critical", "Frost", "Heat", "Quickdraw"],
    "sustained": ["RoF7", "Acid", "AttackAll", "Frost"],
    "close": ["Burst", "Critical", "Tranq", "Quickdraw"],    # played with policy close_in
    "efficient": ["Frost"],                                 # one cheap mod, fewest rounds
    "defensive": ["Tranq", "Quickdraw", "Counter"],          # + Attack Down armor
}


def part_endurance(n):
    """Endurance with the magazine really carried over (bug fixed), vs the 2026-10-17 numbers."""
    old = json.load(open(os.path.join(HERE, "..", "..", "findings", "data", "pe-weapon-benchmark-2026-10-17.json")))
    res = []
    for row in old["bestclass"]:
        if row["stage"] not in ("Day5", "Day3") or row["rules"] != "current": continue
        wid = next(w for w, x in W.items() if x.name == row["gun"])
        stage = row["stage"]
        g = Gun(W[wid]); g.invested[0] = STAGE_INVEST[stage]; g.mods = list(row["mods"])
        s = summarize(run_encounter(R.CURRENT, g.config(), D.AYA[stage], "endurance", stage, n))
        res.append(dict(stage=stage, cls=row["cls"], gun=row["gun"], mods=row["mods"],
                        old_time=row["enc"]["endurance"]["time_mean"], new_time=s["time_mean"],
                        old_reloads=row["enc"]["endurance"]["reloads"], new_reloads=s["reloads"]))
    return res


def part_movement(n, builds):
    res = []
    pols = [("stand", {}), ("approach_0.6s", dict(policy="approach")),
            ("walk_300", dict(policy="walk", walk_speed=300)), ("walk_440", dict(policy="walk", walk_speed=440)),
            ("walk_800", dict(policy="walk", walk_speed=800)),
            ("walk_440_risk25", dict(policy="walk", walk_speed=440, close_risk=0.25))]
    for name, wid in STRESS.items():
        cfg = cfg_of(builds[name]["gun"], builds[name]["opt"])
        for pn, kw in pols:
            ev = evaluate(R.CURRENT, cfg, n, encs=("close_normal", "medium_mobile", "keepaway_boss", "scripted_day5"), **kw)
            res.append(dict(weapon=name, policy=pn, enc={e: dict(time=s["time_mean"], taken=s["taken"], oor=s["out_of_range_turns"],
                                                                miss=s["miss_share"], graze=s["graze_share"]) for e, s in ev.items()}))
        print("movement", name, file=sys.stderr)
    return res


def part_crit(n):
    """Crit share by absolute distance: the 50% zone is half the gun's range."""
    res = []
    for name, wid in STRESS.items():
        cfg = W[wid].config([], bonus_attack=W[wid].bonus_attack + STAGE_INVEST[STAGE])
        row = dict(weapon=name, range=cfg["range"], crit50_within=cfg["range"] // 2, crit20_within=int(cfg["range"] * 0.8), enc={})
        for e in ("close_normal", "medium_mobile", "keepaway_boss"):
            s = summarize(run_encounter(R.CURRENT, cfg, aya_for(e), e, STAGE, n))
            row["enc"][e] = dict(crit=s["crit_share"], graze=s["graze_share"], miss=s["miss_share"])
        res.append(row)
    return res


def part_builds(n):
    """Per stress weapon: original, optimized, no-Commands, no-Quickdraw, archetypes (current rules)."""
    builds, res = {}, []
    for name, wid in STRESS.items():
        g = make_gun(wid)
        k = k_slots(g)
        opt, _ = greedy(R.CURRENT, g, POOL, k)
        nocmd, _ = greedy(R.CURRENT, g, [m for m in POOL if m not in ("2Cmd", "3Cmd")], k)
        noqd, _ = greedy(R.CURRENT, g, [m for m in POOL if m != "Quickdraw"], k)
        builds[name] = dict(gun=g, opt=opt, nocmd=nocmd, noqd=noqd, k=k)
        variants = [("original", []), ("optimized", opt), ("no_commands", nocmd), ("no_quickdraw", noqd)]
        for arch, mods in ARCHETYPES.items():
            if mods is None: continue
            have = [m for m in mods if m in POOL][:k]
            variants.append(("arch_" + arch, have))
        for vn, mods in variants:
            kw = {}
            armor = None
            if vn == "arch_close": kw = dict(policy="close_in", close_d=350, close_risk=0.25)
            if vn == "arch_defensive": armor = dict(attack_levels=-1)
            ev = {e: summarize(run_encounter(R.CURRENT, cfg_of(g, mods), aya_for(e), e, STAGE, n, armor=armor, **kw)) for e in ENCS}
            res.append(dict(weapon=name, build=vn, mods=mods, slots_free=k, enc=ev))
        print("builds", name, opt, "| nocmd", nocmd, "| noqd", noqd, file=sys.stderr)
    return builds, res


MATRIX = ["E0", "C1_15", "C1_25", "C1_30", "C1_40", "C1_50", "C1s_25", "C1s_40", "C1s_50",
          "C2_m10b_25", "C2_m10b_50", "C2_m10b_75", "C2_m10b_100", "C2_all_50", "C4_25", "C4_50", "C5",
          "H1", "M1", "E3", "C3_s40_m50", "C3_s40_m50_c4", "C3_25_m50"]


def rules_for(name):
    if name == "E0": return R.CURRENT
    if name == "C3_s40_m50": return R.experimental("C1s_40", "C2_m10b_50")
    if name == "C3_s40_m50_c4": return R.experimental("C1s_40", "C2_m10b_50", "C4_25")
    if name == "C3_25_m50": return R.experimental("C1_25", "C2_m10b_50")
    return R.experimental(name)


def part_matrix(n, builds):
    """Builds fixed (current optimum) so only the rule changes. Shotguns also played close_in."""
    res = []
    for ex in MATRIX:
        rules = rules_for(ex)
        for name, b in builds.items():
            pols = [("stand", {})]
            if W[STRESS[name]].kind == 2:
                pols.append(("close_in", dict(policy="close_in", close_d=350, close_risk=0.25)))
            for pn, kw in pols:
                ev = evaluate(rules, cfg_of(b["gun"], b["opt"]), n, **kw)
                res.append(dict(exp=ex, weapon=name, policy=pn, enc={e: dict(time=s["time_mean"], taken=s["taken"],
                    damage=s["damage"], rounds=s["rounds"], reloads=s["reloads"]) for e, s in ev.items()}))
        print("matrix", ex, file=sys.stderr)
    return res


def part_regret(n, builds):
    """Opportunity cost: replace each mod of the optimized build by every alternative (same slot)."""
    res = []
    encs = ("close_normal", "groups", "keepaway_boss", "stationary_boss")
    def mixed(cfg):
        logs = [math.log(statistics.mean(x["time"] for x in run_encounter(R.CURRENT, cfg, aya_for(e), e, STAGE, n, seed=19))) for e in encs]
        return math.exp(sum(logs) / len(logs))
    for name, b in builds.items():
        g, opt = b["gun"], b["opt"]
        base = mixed(cfg_of(g, opt))
        for i, m in enumerate(opt):
            rest = opt[:i] + opt[i + 1:]
            for alt in POOL + [None]:
                if alt in rest or (alt and any(group_of(alt) == group_of(c) for c in rest)): continue
                mods = rest + ([alt] if alt else [])
                res.append(dict(weapon=name, slot_of=m, alt=alt or "(empty)", regret=round(mixed(cfg_of(g, mods)) / base - 1, 3)))
        print("regret", name, file=sys.stderr)
    return res


def part_rof(n, builds):
    """RoF 7 / 10 on every stress gun (optimized build, RoF replaced), current rules and a
    'magazine +50% with RoF 7 / 10' experiment, to see whether the P90 runs away."""
    res = []
    exp = R.experimental()
    for name, b in builds.items():
        g = b["gun"]
        for rof in (None, "RoF3", "RoF5", "RoF7", "RoF10"):
            mods = [m for m in b["opt"] if group_of(m) != "rof"] + ([rof] if rof else [])
            cfg = cfg_of(g, mods)
            for rn, rules in (("current", R.CURRENT), ("rof_mag50", dict(R.CURRENT, mag_scale={k: 1.5 for k in range(1, 9)}) if rof in ("RoF7", "RoF10") else R.CURRENT)):
                ev = evaluate(rules, cfg, n, encs=("close_normal", "groups", "stationary_boss", "endurance"))
                res.append(dict(weapon=name, rof=rof or "built-in", rules=rn, mods=mods,
                                enc={e: dict(time=s["time_mean"], rounds=s["rounds"], reloads=s["reloads"]) for e, s in ev.items()}))
        print("rof", name, file=sys.stderr)
    return res


def part_split(n):
    """Two guns from one budget (attack boosters 2 x the stage's, mod picks), vs one gun.
    The player uses whichever gun is better per encounter; switching costs half a bar (current)."""
    res = []
    total_attack = 2 * STAGE_INVEST[STAGE]
    total_mods = D.MOD_BUDGET[STAGE] + PERMITS
    pairs = [("DE50AE7", "MAG"), ("P90", "MAG"), ("DE50AE7", "M10B"), ("MAG", "M10B")]
    encs = ENCS
    for prim, sec in pairs:
        for share in (1.0, 0.75, 0.6, 0.5):
            gp = make_gun(STRESS[prim], invest=round(total_attack * share))
            gs = make_gun(STRESS[sec], invest=round(total_attack * (1 - share)))
            kp = min(k_slots(gp), max(0, round(total_mods * share)))
            ks = min(k_slots(gs), total_mods - kp)
            mp, _ = greedy(R.CURRENT, gp, POOL, kp, n=20)
            ms, _ = greedy(R.CURRENT, gs, POOL, ks, n=20) if share < 1.0 else ([], 0)
            evp = evaluate(R.CURRENT, cfg_of(gp, mp), n, encs=encs)
            evs = evaluate(R.CURRENT, cfg_of(gs, ms), n, encs=encs) if share < 1.0 else None
            switch = E.fill_seconds(D.AYA[STAGE]["stat22"], W[STRESS[prim]].kind) / 2
            row = dict(primary=prim, secondary=sec, share=share, mods_primary=mp, mods_secondary=ms, enc={})
            for e in encs:
                tp = evp[e]["time_mean"]
                ts = (evs[e]["time_mean"] + switch) if evs else float("inf")
                row["enc"][e] = dict(time=round(min(tp, ts), 2), used="secondary" if ts < tp else "primary")
            res.append(row)
        print("split", prim, sec, file=sys.stderr)
    return res


def part_boss(n, builds):
    """Day 5 boss part 1 (level 21: HP 296 is correct there, the HP-level bug began at level 24)."""
    res = []
    exps = ["E0", "E3", "E6", "C1s_40", "C2_m10b_50", "C3_s40_m50"]
    pols = [("stand", {}), ("walk_440", dict(policy="walk", walk_speed=440)), ("walk_300", dict(policy="walk", walk_speed=300))]
    for ex in exps:
        rules = rules_for(ex)
        for name, b in builds.items():
            for pn, kw in pols:
                s = summarize(run_encounter(rules, cfg_of(b["gun"], b["opt"]), D.AYA_LEVEL21, "scripted_day5", STAGE, n, **kw))
                k = summarize(run_encounter(rules, cfg_of(b["gun"], b["opt"]), D.AYA[STAGE], "keepaway_boss", STAGE, n, **kw))
                res.append(dict(exp=ex, weapon=name, policy=pn, scripted=dict(time=s["time_mean"], p90=s["time_p90"], taken=s["taken"], oor=s["out_of_range_turns"], miss=s["miss_share"]),
                                keepaway=dict(time=k["time_mean"], taken=k["taken"], oor=k["out_of_range_turns"], miss=k["miss_share"])))
        print("boss", ex, file=sys.stderr)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=200)
    ap.add_argument("--only", default="endurance,builds,crit,movement,matrix,regret,rof,split,boss")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    parts = a.only.split(",")
    out = {}
    if os.path.exists(a.out):
        out = json.load(open(a.out))
    out.update(date=datetime.date.today().isoformat(), fights=a.fights)
    builds = None
    if "endurance" in parts: out["endurance"] = part_endurance(a.fights)
    if any(p in parts for p in ("builds", "movement", "matrix", "regret", "rof", "boss")):
        builds, out["builds"] = part_builds(a.fights)
        out["build_choices"] = {k: dict(opt=v["opt"], nocmd=v["nocmd"], noqd=v["noqd"], free_slots=v["k"]) for k, v in builds.items()}
    if "crit" in parts: out["crit"] = part_crit(a.fights)
    if "movement" in parts: out["movement"] = part_movement(a.fights, builds)
    if "matrix" in parts: out["matrix"] = part_matrix(a.fights, builds)
    if "regret" in parts: out["regret"] = part_regret(max(60, a.fights // 3), builds)
    if "rof" in parts: out["rof"] = part_rof(a.fights, builds)
    if "split" in parts: out["split"] = part_split(max(100, a.fights // 2))
    if "boss" in parts: out["boss"] = part_boss(a.fights, builds)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
