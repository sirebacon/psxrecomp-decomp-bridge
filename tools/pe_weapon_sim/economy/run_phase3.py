"""Phase 3 experiments: python -m pe_weapon_sim.economy.run_phase3 [--n N] [--only parts] [--workers W]

Parts: policies (A-I, specialists, BP strategies; typical), profiles, ablations (A0-A8), magazine
(M10B capacity x firing configuration grid), shotgun (S0-S4), sensitivity, validation (surrogate vs
engine), traces (representative transaction logs). Matched seeds 1..N across policies.
Writes findings/data/pe-weapon-p3-results-2026-10-17.json and pe-weapon-p3-trace-*.txt.
"""
import argparse, json, math, multiprocessing as mp, os, random, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "..", "..", "findings", "data")
OUT = os.path.join(OUT_DIR, "pe-weapon-p3-results-2026-10-17.json")
PHASES = ("D1", "D2-4", "D5", "Disc2")
M10B = 0x6E


# ---- specs (picklable) -----------------------------------------------------------------------------
def econ_from(spec):
    from . import rules as ER
    if spec == "current": return ER.CURRENT
    if spec == "vanilla": return ER.VANILLA
    if spec.startswith("abl:"): return ER.ablation(spec[4:])
    if spec.startswith("cur:"):                # cur:key=json;key=json (sensitivity / experiments)
        over = {}
        for kv in spec[4:].split(";"):
            k, v = kv.split("=", 1)
            over[k] = json.loads(v)
        if "base_delta" in over:
            over["base_delta"] = {int(k, 0): tuple(v) for k, v in over["base_delta"].items()}
        return ER.variant(ER.CURRENT, spec, **over)
    raise ValueError(spec)


def policy_from(spec):
    from . import policies as PO
    name, over = spec
    P = PO.policy_set()
    if name.startswith("B_"):
        kind = {v: k for k, v in PO.KIND_NAME.items()}[name[2:]]
        p = PO.specialist(kind)
    else:
        p = P[name]
    if over:
        p = p.copy(p.name + "*", **over)
    return p


def compact(snap):
    return {k: v for k, v in snap.items() if not k.startswith("_") and k != "metrics"}


def run_one(task):
    """task: dict(econ, policy, profile, seed, bench(bool), timing, bench_rules, sg_timing)."""
    from . import acquisition as AQ, evaluation as EV, playthrough as PT, surrogate as SG
    from .. import engine as E
    SG.TIMING = task.get("sg_timing", "overlap")
    camp = _camp()
    econ = econ_from(task["econ"]); pol = policy_from(task["policy"])
    run = PT.play(econ, pol, task["profile"], task["seed"], camp, check=False)
    rec = dict(econ=task["econ"], policy=pol.name, profile=task["profile"], seed=task["seed"],
               cps={p: compact(run.checkpoints[p]) for p in PHASES if p in run.checkpoints},
               m=run.checkpoints["Disc2"]["metrics"], bench={})
    if task.get("bench"):
        crules = PT.combat_rules(task.get("bench_rules") or econ["combat"])
        for p in task.get("bench_phases", PHASES):
            s = run.checkpoints[p]
            res = EV.benchmark(crules, s["_gun"].cfg(), s["_aya"], p, armor=EV.armor_of(s["_armor"]),
                               n=task.get("fights", 10), timing=task.get("timing", "overlap"))
            rec["bench"][p] = slim(res)
            if s["_second"] is not None:
                r2 = EV.benchmark(crules, s["_second"].cfg(), s["_aya"], p, armor=EV.armor_of(s["_armor"]),
                                  n=task.get("fights", 10), timing=task.get("timing", "overlap"))
                rec["bench"][p + "_second"] = slim(r2)
    return rec


def slim(res):
    out = dict(suite_time=res["suite_time"], window_damage=res.get("window_damage"))
    for k, v in res.items():
        if isinstance(v, dict):
            out[k] = dict(t=v["time_mean"], win=v["win"], taken=v["taken"], rounds=v["rounds"],
                          reloads=v["reloads"], clicks=v.get("clicks", 0), dmg=v["damage"])
    return out


_CAMP = None


def _camp():
    global _CAMP
    if _CAMP is None:
        from . import acquisition as AQ
        _CAMP = AQ.load_campaign()
    return _CAMP


def run_many(tasks, workers):
    if workers <= 1:
        return [run_one(t) for t in tasks]
    with mp.Pool(workers) as pool:
        return pool.map(run_one, tasks, chunksize=4)


# ---- statistics ----------------------------------------------------------------------------------
def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    s = sorted(xs); n = len(s)
    mean = statistics.mean(s); sd = statistics.pstdev(s) if n > 1 else 0.0
    return dict(n=n, mean=round(mean, 3), median=s[n // 2], p10=s[n // 10], p90=s[min(n - 1, (9 * n) // 10)],
                ci95=round(1.96 * sd / math.sqrt(n), 3))


def prob(flags):
    flags = list(flags)
    if not flags: return None
    p = sum(flags) / len(flags)
    return dict(p=round(p, 3), ci95=round(1.96 * math.sqrt(max(p * (1 - p), 1e-9) / len(flags)), 3), n=len(flags))


def summarize_group(recs):
    """Distribution summary of a group of runs (same econ / policy / profile)."""
    out = {}
    for p in PHASES:
        cp = [r["cps"][p] for r in recs if p in r["cps"]]
        if not cp: continue
        o = {}
        o["bp_earned"] = stats([c["bp_earned"] for c in cp])
        o["bp_spent"] = stats([sum(c["bp_spent"].values()) for c in cp])
        o["bp_unspent"] = stats([c["bp_banked"] + c["bp_pool"] for c in cp])
        o["bp_pool"] = stats([c["bp_pool"] for c in cp])
        for cat in ("attack", "range", "bullets", "armor", "active_time", "capacity"):
            o["bp_" + cat] = stats([c["bp_spent"][cat] for c in cp])
        o["at_bought"] = stats([c["at_bought"] for c in cp]); o["capacity"] = stats([c["capacity"] for c in cp])
        for i, k in enumerate(("attack", "range", "bullets")):
            o["bonus_" + k] = stats([c["bonus"][i] for c in cp])
            for src in ("intrinsic", "bp", "booster"):
                o["bonus_%s_%s" % (k, src)] = stats([c["origins"][i].get(src, 0) for c in cp])
        o["armor_bonus"] = stats([sum(c["armor_bonus"]) for c in cp])
        o["magazine"] = stats([c["magazine"] for c in cp])
        o["tools_left"] = stats([c["tools"] for c in cp]); o["junk"] = stats([c["junk"] for c in cp])
        o["unused_donor_bonus"] = stats([c["unused_donor_bonus"] for c in cp])
        o["score"] = stats([c["score"] for c in cp])
        guns = {}
        for c in cp: guns[c["gun"]] = guns.get(c["gun"], 0) + 1
        o["guns"] = dict(sorted(guns.items(), key=lambda kv: -kv[1]))
        kinds = {}
        for c in cp: kinds[c["gun_kind"]] = kinds.get(c["gun_kind"], 0) + 1
        o["gun_kinds"] = kinds
        mods = {}
        for c in cp:
            for mname in c["mods"]: mods[mname] = mods.get(mname, 0) + 1
        o["mods_share"] = {k: round(v / len(cp), 3) for k, v in sorted(mods.items(), key=lambda kv: -kv[1])}
        bench = [r["bench"].get(p) for r in recs if r["bench"].get(p)]
        if bench:
            o["suite_time"] = stats([b["suite_time"] for b in bench])
            o["window_damage"] = stats([b["window_damage"] for b in bench])
            for enc in ("close_normal", "groups", "medium_mobile", "keepaway_boss", "stationary_boss", "endurance",
                        "scripted_day5"):
                if enc in bench[0]:
                    o["t_" + enc] = stats([b[enc]["t"] for b in bench])
                    o["win_" + enc] = stats([b[enc]["win"] for b in bench])
                    o["taken_" + enc] = stats([b[enc]["taken"] for b in bench])
            o["reloads_endurance"] = stats([b["endurance"]["reloads"] for b in bench])
            o["clicks_endurance"] = stats([b["endurance"]["clicks"] for b in bench])
        b2 = [r["bench"].get(p + "_second") for r in recs if r["bench"].get(p + "_second")]
        if b2:
            o["second_suite_time"] = stats([b["suite_time"] for b in b2])
            o["second_t_keepaway"] = stats([b["keepaway_boss"]["t"] for b in b2])
        out[p] = o
    ms = [r["m"] for r in recs]
    f = {}
    for k in ("donors_got", "donors_harvested", "extracted_bp", "permits_got", "permits_used", "mods_installed",
              "junk_earned", "overflow", "switches", "hits", "bp_lost", "dismantled", "battles", "farm_battles"):
        f[k] = stats([m[k] for m in ms])
    f["tools_got_total"] = stats([sum(m["tools_got"].values()) for m in ms])
    for src in ("field", "rare", "drop", "bought"):
        f["tools_got_" + src] = stats([m["tools_got"].get(src, 0) for m in ms])
    f["tools_spent_total"] = stats([sum(m["tools_spent"].values()) for m in ms])
    for k in ("stat", "mod", "premium", "super"):
        f["tools_spent_" + k] = stats([m["tools_spent"].get(k, 0) for m in ms])
    f["super_got"] = stats([m["super_got"] for m in ms])
    f["boosters_got"] = stats([sum(m["boosters_got"].values()) for m in ms])
    for src in ("field", "rare", "drop"):
        f["boosters_got_" + src] = stats([m["boosters_got"].get(src, 0) for m in ms])
    for i, k in enumerate(("attack", "range", "bullets")):
        f["extracted_" + k] = stats([m["extracted"][i] for m in ms])
        f["booster_points_" + k] = stats([m["booster_points"][i] for m in ms])
    rare = {}
    for m in ms:
        for k, v in m["rare"].items(): rare[k] = rare.get(k, 0) + v
    f["rare_per_run"] = {k: round(v / len(ms), 3) for k, v in sorted(rare.items(), key=lambda kv: -kv[1])}
    wg = {}
    for m in ms:
        for g in m["wayne_guns"]: wg[g] = wg.get(g, 0) + 1
    f["wayne_guns"] = wg
    first = {}
    for m in ms:
        for eff, (ph, b) in m["effect_first"].items():
            first.setdefault(eff, []).append(b)
    f["effect_first_battle"] = {k: stats(v) for k, v in first.items()}
    out["final"] = f
    return out


def probabilities(recs):
    """Breakpoint probabilities for a group."""
    def cp(r, p): return r["cps"].get(p, {})
    out = {}
    fin = [cp(r, "Disc2") for r in recs]
    out["bp_mostly_active_time"] = prob(c["bp_spent"]["active_time"] > sum(c["bp_spent"].values()) / 2 for c in fin)
    out["any_bp_on_bullets"] = prob(c["bp_spent"]["bullets"] > 0 for c in fin)
    out["tools_limiting"] = prob(c["tools"] == 0 and c["unused_donor_bonus"] > 0 for c in fin)
    out["second_underdeveloped"] = prob(c["second_bonus"] is not None and sum(c["second_bonus"]) < 0.25 * sum(c["bonus"])
                                        for c in fin if c["second"] is not None) if any(c["second"] for c in fin) else None
    for p in ("D5", "Disc2"):
        cs = [cp(r, p) for r in recs]
        out["2cmd_by_" + p] = prob("2Cmd" in c["mods"] for c in cs)
        out["quickdraw_by_" + p] = prob("Quickdraw" in c["mods"] for c in cs)
        out["attack30_by_" + p] = prob(c["bonus"][0] >= 30 for c in cs)
        out["range10_by_" + p] = prob(c["bonus"][1] >= 10 for c in cs)
    return out


# ---- parts ---------------------------------------------------------------------------------------
def tasks_for(econ, policy, profile, n, bench_n, **kw):
    return [dict(econ=econ, policy=policy, profile=profile, seed=s, bench=(s <= bench_n), **kw) for s in range(1, n + 1)]


def part_policies(n, workers, bench_n):
    groups = {}
    names = ["A", "B", "C", "D", "E", "G", "H", "I", "S_save", "S_def", "S_wpn", "S_end", "C_wayne", "G_wayne"]
    specs = [(x, None) for x in names] + [("B_" + k, None) for k in ("shotgun", "machine", "rifle", "grenade")]
    tasks = []
    for sp in specs:
        tasks += tasks_for("current", sp, "typical", n, bench_n)
    tasks += tasks_for("current", ("F", None), "farmer", n, bench_n)
    # calibration: the run's own hits on Aya (ratio 1) -> BP earned should match the log
    tasks += tasks_for("cur:hits_logged=true", ("S_end", None), "logged", 20, 0)
    recs = run_many(tasks, workers)
    for r in recs:
        tag = "calib" if r["econ"].startswith("cur:hits_logged") else r["profile"]
        groups.setdefault("%s|%s" % (r["policy"], tag), []).append(r)
    return {k: dict(summary=summarize_group(v), prob=probabilities(v)) for k, v in groups.items()}, recs


def part_profiles(n, workers, bench_n):
    tasks = []
    for prof in ("minimal", "typical", "completionist", "farmer"):
        for pol in ("A", "C", "I"):
            tasks += tasks_for("current", (pol, None), prof, n, bench_n)
    recs = run_many(tasks, workers)
    groups = {}
    for r in recs:
        groups.setdefault("%s|%s" % (r["policy"], r["profile"]), []).append(r)
    return {k: dict(summary=summarize_group(v), prob=probabilities(v)) for k, v in groups.items()}


def part_ablations(n, workers, bench_n):
    tasks = []
    for code in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
        for pol in ("C", "B_shotgun"):
            tasks += tasks_for("abl:" + code, (pol, None), "typical", n, bench_n)
    tasks += tasks_for("vanilla", ("C", None), "typical", n, bench_n)
    recs = run_many(tasks, workers)
    groups = {}
    for r in recs:
        groups.setdefault("%s|%s" % (r["econ"], r["policy"]), []).append(r)
    res = {k: dict(summary=summarize_group(v)) for k, v in groups.items()}
    res["A0"] = part_a0()
    return res


def part_a0():
    """A0: the phase 1/2 fixed-budget loadouts (Day 5: +12 attack, greedy mods within the stage
    budget + 1 permit) evaluated on the phase 3 checkpoint encounters for comparison."""
    from .. import data as D, rules as CR
    from ..run_phase2 import make_gun, k_slots, greedy, POOL
    from . import evaluation as EV, tables as T
    out = {}
    aya = dict(level=24, stat22=73, offense=200)
    for name, wid in (("MAG", 0x82), ("P90", 0x78), ("M10B", 0x6E), ("DE50AE7", 0x66), ("HK40", 0x8F), ("M500", 0x6A)):
        g = make_gun(wid)
        mods, _ = greedy(CR.CURRENT, g, POOL, k_slots(g), n=12)
        g.mods = mods
        cfg = g.config()
        out[name] = dict(mods=mods, power=cfg["power"], magazine=cfg["magazine"],
                         D5=slim(EV.benchmark(CR.CURRENT, cfg, aya, "D5", n=12)),
                         Disc2=slim(EV.benchmark(CR.CURRENT, cfg, dict(level=33, stat22=82, offense=350), "Disc2", n=12)))
    return out


def part_magazine():
    """M10B capacity x firing configuration on Day 5 and disc-2 encounters (engine)."""
    from .. import data as D, rules as CR
    from . import evaluation as EV, equipment as EQ, tables as T
    configs = {
        "stock (RoF3+Burst)": ["RoF3", "Burst"], "RoF1+Burst": ["Burst"], "RoF2+Burst": ["RoF2", "Burst"],
        "RoF5+Burst": ["RoF5", "Burst"], "RoF7+Burst": ["RoF7", "Burst"], "RoF10+Burst": ["RoF10", "Burst"],
        "RoF3+Burst+2Cmd": ["RoF3", "Burst", "2Cmd"], "RoF2+Burst+2Cmd": ["RoF2", "Burst", "2Cmd"],
        "RoF5+Burst+2Cmd": ["RoF5", "Burst", "2Cmd"], "RoF3+Burst+3Cmd": ["RoF3", "Burst", "3Cmd"],
        "RoF3+Random": ["RoF3", "Random"], "RoF3+Random+2Cmd": ["RoF3", "Random", "2Cmd"],
        "RoF3+AttackAll": ["RoF3", "AttackAll"], "RoF3+AttackAll+2Cmd": ["RoF3", "AttackAll", "2Cmd"],
        "RoF3+Burst+2Cmd+QD+Crit": ["RoF3", "Burst", "2Cmd", "Quickdraw", "Critical"],
    }
    legal = {"3Cmd": "EX game only (M96R, Chrysler)", "RoF10": "P90 (Wayne) / EX guns: a Wayne gun dismantled",
             "RoF7": "M10 / MP5PDW (Hospital, Museum)", "AttackAll": "P90 (Wayne) / MP5A5, MP5SD6 (EX)"}
    out = dict(legal=legal, grid=[])
    stages = (("D5", dict(level=24, stat22=73, offense=200), 12), ("Disc2", dict(level=30, stat22=79, offense=316), 30))
    for cname, mods in configs.items():
        for cap in (7, 8, 9, 10, 12, 14):
            for phase, aya, atk in stages:
                g = EQ.Item(M10B, "grid", phase)
                g.mods = [T.GUN_FX_CODE[m] for m in mods]
                g.bonus = [atk, 0, cap - g.base[2]]
                g.prov = [{("grid", 0): b} for b in g.bonus]
                cfg = g.cfg()
                res = EV.benchmark(CR.CURRENT, cfg, aya, phase, n=24,
                                   suite=("close_normal", "groups", "stationary_boss", "endurance", "keepaway_boss"))
                demand = _demand(cfg)
                out["grid"].append(dict(config=cname, magazine=cap, phase=phase, demand=demand,
                                        suite=res["suite_time"], **{e: dict(t=res[e]["time_mean"], rounds=res[e]["rounds"],
                                        reloads=res[e]["reloads"], clicks=res[e]["clicks"], win=res[e]["win"])
                                        for e in ("close_normal", "groups", "stationary_boss", "endurance", "keepaway_boss")}))
    return out


def _demand(cfg):
    from . import surrogate as SG
    used, _ = SG.volley_bullets(cfg["eff"], 2.0)
    return used * cfg["eff"].get("commands", 1)


NO_BULLETS = dict(bullet_align=False, bp_weights=dict(attack=0.75, range=0.25))


def part_shotgun(n, workers, bench_n):
    """S0-S4 on shotgun specialists (B_shotgun), checkpoint benchmarks with stand and close-in play.
    S0 / S3 put no BP into bullets (bullets come only from transfers and boosters)."""
    variants = {
        "S0": dict(econ="current", policy=("B_shotgun", NO_BULLETS), bench_rules="current"),
        "S1": dict(econ="current", policy=("B_shotgun", None), bench_rules="current"),
        "S2": dict(econ="current", policy=("B_shotgun", None), bench_rules="exp:C1s_40"),
        "S3": dict(econ='cur:base_delta={"0x6E":[0,0,1]}', policy=("B_shotgun", NO_BULLETS), bench_rules="current"),
        "S4": dict(econ='cur:base_delta={"0x6E":[0,0,1]}', policy=("B_shotgun", None), bench_rules="exp:C1s_40"),
    }
    out = {}
    for name, v in variants.items():
        tasks = [dict(econ=v["econ"], policy=v["policy"], profile="typical", seed=s, bench=(s <= bench_n),
                      bench_rules=v["bench_rules"], bench_phases=("D5", "Disc2")) for s in range(1, n + 1)]
        recs = run_many(tasks, workers)
        out[name] = dict(summary=summarize_group(recs), prob=probabilities(recs))
        out[name]["close_in"] = close_in_bench(recs[:bench_n], v["bench_rules"])
    return out


def close_in_bench(recs, rules_name):
    """Final loadouts replayed with close-in movement (phase 2 policy: stop at 350 units, +30%
    risk of being hit while close) to see whether the proximity zone is reachable."""
    from .. import rules as CR
    from . import evaluation as EV, playthrough as PT
    crules = PT.combat_rules(rules_name)
    rows = []
    for r in recs:
        c = r["cps"]["Disc2"]
        g = _rebuild(c)
        aya = dict(level=c["level"], stat22=c["stat22"], offense=_off(c["level"]))
        res = EV.benchmark(crules, g, aya, "Disc2", n=10, policy="close_in",
                           suite=("close_normal", "groups", "stationary_boss", "keepaway_boss"))
        rows.append(dict(suite=res["suite_time"], taken=sum(res[e]["taken"] for e in ("close_normal", "groups", "stationary_boss"))))
    return dict(suite=stats([x["suite"] for x in rows]), taken=stats([x["taken"] for x in rows]))


def _off(level):
    from . import tables as T
    return T.offense_of(level)


def _rebuild(c):
    from . import equipment as EQ, tables as T
    g = EQ.Item(c["gun_id"], "rebuild", "Disc2")
    g.bonus = list(c["bonus"]); g.prov = [{("r", 0): b} for b in g.bonus]
    g.mods = [T.GUN_FX_CODE[m] for m in c["mods"] if m in T.GUN_FX_CODE] + [0] * max(0, c["slots"] - len(c["mods"]))
    if c["magazine"] != g.magazine():                 # experimental base change
        g.base = [g.base[0], g.base[1], g.base[2] + (c["magazine"] - g.magazine())]
    return g.cfg()


def part_sensitivity(n, workers, bench_n):
    cases = {
        "base": dict(econ="current"),
        "serial_timing": dict(econ="current", sg_timing="serial", timing="serial"),
        "hits_exp_0.5": dict(econ="cur:hits_exp=0.5"),
        "field_tools_x0.5": dict(econ="cur:field_tool_scale=0.5"),
        "field_tools_x1.5": dict(econ="cur:field_tool_scale=1.5"),
        "preset_relaxed": dict(econ="cur:preset=0"),
        "preset_grind": dict(econ="cur:preset=2"),
    }
    out = {}
    for name, c in cases.items():
        for pol in ("C", "G", "B_shotgun"):
            tasks = [dict(econ=c["econ"], policy=(pol, None), profile="typical", seed=s, bench=(s <= bench_n),
                          sg_timing=c.get("sg_timing", "overlap"), timing=c.get("timing", "overlap"),
                          bench_phases=("D5", "Disc2")) for s in range(1, n + 1)]
            recs = run_many(tasks, workers)
            out["%s|%s" % (name, pol)] = dict(summary=summarize_group(recs), prob=probabilities(recs))
    out["anim_scale"] = anim_sensitivity()
    return out


def anim_sensitivity():
    """P90 RoF10 vs RoF7 vs RoF3 and M10B configs under animation scale 0.7 / 1.0 / 1.3."""
    from .. import engine as E, rules as CR
    from . import evaluation as EV, equipment as EQ, tables as T
    rows = []
    aya = dict(level=30, stat22=79, offense=316)
    for scale in (0.7, 1.0, 1.3):
        E.ANIM_SCALE = scale
        EV._CACHE.clear()
        for gname, wid, variants in (("P90", 0x78, (["RoF10", "AttackAll", "2Cmd"], ["RoF7", "AttackAll", "2Cmd"],
                                                    ["RoF3", "AttackAll", "2Cmd"], ["RoF10", "2Cmd", "Quickdraw"])),
                                     ("M10B", M10B, (["RoF3", "Burst", "2Cmd"], ["RoF2", "Burst", "2Cmd"], ["RoF5", "Burst"]))):
            for mods in variants:
                g = EQ.Item(wid, "s", "Disc2"); g.mods = [T.GUN_FX_CODE[m] for m in mods]
                g.bonus = [30, 5, 10 if wid == M10B else 0]; g.prov = [{("s", 0): b} for b in g.bonus]
                res = EV.benchmark(CR.CURRENT, g.cfg(), aya, "Disc2", n=20)
                rows.append(dict(scale=scale, gun=gname, mods="+".join(mods), suite=res["suite_time"]))
    E.ANIM_SCALE = 1.0
    EV._CACHE.clear()
    return rows


def part_validation():
    """Surrogate score vs engine suite time on loadouts drawn from simulated runs."""
    from .. import rules as CR
    from . import evaluation as EV, playthrough as PT, policies as PO, rules as ER
    camp = _camp()
    out = {}
    P = PO.policy_set()
    for phase in ("D2-4", "D5", "Disc2"):
        loads = []
        for pol in ("A", "B", "C", "D", "E", "I"):
            for seed in range(1, 6):
                run = PT.play(ER.CURRENT, P[pol] if pol != "B" else PO.specialist(2), "typical", seed, camp, check=False)
                s = run.checkpoints[phase]
                loads.append((s["_gun"].cfg(), s["_aya"]))
        rho, pairs = EV.validate_surrogate(CR.CURRENT, loads, phase, n=12)
        out[phase] = dict(spearman=round(rho, 3), n=len(pairs))
    return out


def part_routes(policy_groups):
    """M10B bullet +1 routes from the shotgun specialist runs (typical, CURRENT)."""
    g = policy_groups.get("B_shotgun|typical", {}).get("summary", {})
    return dict(note="see report G / H; numbers from B_shotgun|typical", summary=g.get("final", {}))


def part_traces():
    from . import playthrough as PT, policies as PO, rules as ER
    camp = _camp()
    P = PO.policy_set()
    files = []
    for tag, pol in (("optimizer-C", P["C"]), ("shotgun-specialist", PO.specialist(2)), ("casual-A", P["A"]),
                     ("two-weapon-D", P["D"])):
        run = PT.play(ER.CURRENT, pol, "typical", 1, camp, trace=True)
        path = os.path.join(OUT_DIR, "pe-weapon-p3-trace-%s-2026-10-17.txt" % tag)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# Phase 3 trace: policy %s (%s), profile typical, seed 1, CURRENT economy\n" % (pol.name, pol.label))
            fh.write("# b = battle number; every line is one state transition (simulated values)\n")
            for x in run.log:
                if x["kind"] == "battle" and not (x.get("bp") or 0) and x["b"] % 10:
                    continue
                d = {k: v for k, v in x.items() if k not in ("b", "phase", "kind")}
                fh.write("b%03d %-5s %-11s %s\n" % (x["b"], x["phase"], x["kind"], " ".join("%s=%s" % kv for kv in d.items())))
            for ph, s in run.checkpoints.items():
                fh.write("CHECKPOINT %s level %d %s +%s mag %d mods %s AT+%d cap+%d BP earned %d spent %s pool %d origins %s\n" % (
                    ph, s["level"], s["gun"], s["bonus"], s["magazine"], s["mods"], s["at_bought"], s["cap_bought"],
                    s["bp_earned"], {k: v for k, v in s["bp_spent"].items() if v}, s["bp_pool"], s["origins"]))
        files.append(os.path.basename(path))
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--bench", type=int, default=40)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    res = {}
    if os.path.exists(OUT):
        with open(OUT) as fh:
            res = json.load(fh)
    t0 = time.time()

    def want(p): return only is None or p in only

    if want("policies"):
        res["policies"], recs = part_policies(a.n, a.workers, a.bench)
        res["routes"] = part_routes(res["policies"])
        print("policies %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("profiles"):
        res["profiles"] = part_profiles(max(40, a.n // 2), a.workers, a.bench // 2)
        print("profiles %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("ablations"):
        res["ablations"] = part_ablations(max(40, a.n // 2), a.workers, a.bench // 2)
        print("ablations %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("magazine"):
        res["magazine"] = part_magazine()
        print("magazine %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("shotgun"):
        res["shotgun"] = part_shotgun(max(40, a.n // 2), a.workers, a.bench // 2)
        print("shotgun %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("sensitivity"):
        res["sensitivity"] = part_sensitivity(max(40, a.n // 3), a.workers, a.bench // 2)
        print("sensitivity %.0fs" % (time.time() - t0)); sys.stdout.flush()
    if want("validation"):
        res["validation"] = part_validation()
    if want("traces"):
        res["traces"] = part_traces()
    res["meta"] = dict(n=a.n, bench=a.bench, seconds=round(time.time() - t0), date="2026-10-17")
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print("wrote", OUT, "%.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
