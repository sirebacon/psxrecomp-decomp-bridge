"""Phase 2b: smart reload (R1) and combinations, high RoF with R1, and Commands dependency under R1.
python -m pe_weapon_sim.run_phase2b [--fights N]; appends "phase2b" to the phase 2 JSON."""
import argparse, json, math, os, statistics, sys
from . import rules as R
from .run_phase2 import (OUT, STRESS, POOL, ENCS, make_gun, cfg_of, k_slots, greedy, evaluate, rules_for)
from .run_benchmark import W, group_of


def geo(xs):
    return math.exp(statistics.mean(math.log(max(0.05, x)) for x in xs))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fights", type=int, default=200); a = ap.parse_args()
    d = json.load(open(OUT))
    choices = d["build_choices"]
    n = a.fights
    exps = {"E0": R.CURRENT, "R1": R.experimental("R1"), "R1+C1s_40": R.experimental("R1", "C1s_40"),
            "R1+C2_m10b_25": R.experimental("R1", "C2_m10b_25"), "R1+C1s_40+C2_m10b_25": R.experimental("R1", "C1s_40", "C2_m10b_25"),
            "C1s_40+C2_m10b_25": R.experimental("C1s_40", "C2_m10b_25")}
    out = dict(matrix=[], rof=[], cmd=[])
    for ex, rules in exps.items():
        for name, wid in STRESS.items():
            g = make_gun(wid)
            pols = [("stand", {})] + ([("close_in", dict(policy="close_in", close_d=350, close_risk=0.25))] if W[wid].kind == 2 else [])
            for pn, kw in pols:
                ev = evaluate(rules, cfg_of(g, choices[name]["opt"]), n, **kw)
                out["matrix"].append(dict(exp=ex, weapon=name, policy=pn, enc={e: dict(time=s["time_mean"], taken=s["taken"], reloads=s["reloads"],
                                                                                       rounds=s["rounds"], damage=s["damage"]) for e, s in ev.items()}))
        print("2b matrix", ex, file=sys.stderr)
    # High RoF with and without R1 on handguns / shotgun / P90 (built-in RoF replaced)
    for name in ("DE50AE7", "M10B", "P90", "MAG", "HK40"):
        g = make_gun(STRESS[name])
        for rof in ("RoF3", "RoF5", "RoF7", "RoF10"):
            mods = [m for m in choices[name]["opt"] if group_of(m) != "rof"] + [rof]
            for ex in ("E0", "R1"):
                ev = evaluate(exps[ex], cfg_of(g, mods), n, encs=("close_normal", "groups", "stationary_boss", "endurance"))
                out["rof"].append(dict(weapon=name, rof=rof, exp=ex, mods=mods, enc={e: dict(time=s["time_mean"], reloads=s["reloads"], rounds=s["rounds"]) for e, s in ev.items()}))
        print("2b rof", name, file=sys.stderr)
    # Commands dependency under R1: reoptimize without Commands
    for name, wid in STRESS.items():
        g = make_gun(wid)
        for ex in ("E0", "R1"):
            k = k_slots(g)
            opt, _ = greedy(exps[ex], g, POOL, k)
            nocmd, _ = greedy(exps[ex], g, [m for m in POOL if m not in ("2Cmd", "3Cmd")], k)
            e_opt = evaluate(exps[ex], cfg_of(g, opt), n)
            e_no = evaluate(exps[ex], cfg_of(g, nocmd), n)
            reg = geo([max(0.05, e_no[e]["time_mean"]) / max(0.05, e_opt[e]["time_mean"]) for e in ENCS if e != "short_window"]) - 1
            out["cmd"].append(dict(weapon=name, exp=ex, opt=opt, nocmd=nocmd, nocmd_regret=round(reg, 3)))
        print("2b cmd", name, file=sys.stderr)
    d["phase2b"] = out
    json.dump(d, open(OUT, "w"), indent=1, default=str)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
