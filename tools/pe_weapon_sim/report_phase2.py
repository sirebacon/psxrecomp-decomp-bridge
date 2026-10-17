"""Tables from the phase 2 JSON: python -m pe_weapon_sim.report_phase2 <json> [part]"""
import json, math, statistics, sys
from collections import defaultdict

ENCS = ["close_normal", "medium_mobile", "groups", "keepaway_boss", "stationary_boss", "short_window", "scripted_day5", "endurance"]
SH = {"close_normal": "close", "medium_mobile": "mobile", "groups": "groups", "keepaway_boss": "keep-away",
      "stationary_boss": "stat.boss", "short_window": "6s dmg", "scripted_day5": "D5 boss", "endurance": "endur."}


def t_of(s, e):
    return s["damage"] if e == "short_window" else s.get("time_mean", s.get("time"))


def rel(a, b, e):
    """+ = worse than b."""
    if e == "short_window":
        return b / max(1e-9, a) - 1
    return max(a, 0.05) / max(b, 0.05) - 1          # a Quickdraw kill can end a fight at t = 0


def geo(rels):
    return math.exp(statistics.mean(math.log(1 + max(-0.95, r)) for r in rels)) - 1


def endurance(d):
    print("\n#### endurance: magazine carried over (fixed) vs 2026-10-17")
    print("| stage | class | gun | old time | new time | old reloads | new reloads |")
    print("|---|---|---|---|---|---|---|")
    for r in d["endurance"]:
        print("| %s | %s | %s | %.1f | %.1f | %.2f | %.2f |" % (r["stage"], r["cls"], r["gun"], r["old_time"], r["new_time"], r["old_reloads"], r["new_reloads"]))


def builds(d):
    rows = d["builds"]
    best = {e: (max if e == "short_window" else min)(t_of(r["enc"][e], e) for r in rows if r["build"] == "optimized") for e in ENCS}
    print("\n#### builds (current rules, Day 5 + 1 permit): time per encounter; [x] = vs the best optimized weapon; regret = geo-mean vs the same weapon's optimized build")
    print("| weapon | build | mods | " + " | ".join(SH[e] for e in ENCS) + " | vs best | regret | taken (keep-away) | rounds (endur.) |")
    print("|---" * (len(ENCS) + 7) + "|")
    for w in sorted({r["weapon"] for r in rows}, key=lambda x: [r["weapon"] for r in rows].index(x)):
        wr = [r for r in rows if r["weapon"] == w]
        opt = next(r for r in wr if r["build"] == "optimized")
        for r in wr:
            cells = []
            for e in ENCS:
                v = t_of(r["enc"][e], e)
                cells.append(("%.0f" if e == "short_window" else "%.1f") % v)
            vs = geo([rel(t_of(r["enc"][e], e), best[e], e) for e in ENCS])
            rg = geo([rel(t_of(r["enc"][e], e), t_of(opt["enc"][e], e), e) for e in ENCS])
            print("| %s | %s | %s | %s | %+.0f%% | %+.0f%% | %.0f | %.0f |" % (w, r["build"], "+".join(r["mods"]) or "-", " | ".join(cells),
                  100 * vs, 100 * rg, r["enc"]["keepaway_boss"]["taken"], r["enc"]["endurance"]["rounds"]))
    # Pareto per weapon over (mixed time, keep-away taken, endurance rounds, mods used)
    print("\nPareto-efficient builds per weapon (mixed time, taken, rounds, mods used):")
    for w in sorted({r["weapon"] for r in rows}):
        wr = [r for r in rows if r["weapon"] == w]
        pts = []
        for r in wr:
            mt = geo([t_of(r["enc"][e], e) / 10.0 - 1 for e in ENCS if e != "short_window"])
            pts.append((r["build"], mt, statistics.mean(r["enc"][e]["taken"] for e in ENCS), r["enc"]["endurance"]["rounds"], len(r["mods"])))
        eff = [p for p in pts if not any(all(q[i] <= p[i] for i in range(1, 5)) and any(q[i] < p[i] for i in range(1, 5)) for q in pts)]
        print("  %s: %s" % (w, ", ".join(p[0] for p in eff)))


def crit(d):
    print("\n#### crit by distance (plain Day 5 guns): 50%-crit zone = within half the range")
    print("| weapon | range | 50% crit within | 20% within | crit close | crit mobile | crit keep-away | graze keep-away | miss keep-away |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in d["crit"]:
        e = r["enc"]
        print("| %s | %d | %d | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% |" % (r["weapon"], r["range"], r["crit50_within"], r["crit20_within"],
              100 * e["close_normal"]["crit"], 100 * e["medium_mobile"]["crit"], 100 * e["keepaway_boss"]["crit"],
              100 * e["keepaway_boss"]["graze"], 100 * e["keepaway_boss"]["miss"]))


def movement(d):
    print("\n#### movement policies (optimized builds): time (s) / out-of-range turns")
    encs = ["close_normal", "medium_mobile", "keepaway_boss", "scripted_day5"]
    print("| weapon | policy | " + " | ".join(SH[e] for e in encs) + " |")
    print("|---" * (len(encs) + 2) + "|")
    for r in d["movement"]:
        print("| %s | %s | %s |" % (r["weapon"], r["policy"], " | ".join("%.1f / %.0f%%" % (r["enc"][e]["time"], 100 * r["enc"][e]["oor"]) for e in encs)))


def matrix(d):
    rows = d["matrix"]
    base = {(r["weapon"], r["policy"]): r for r in rows if r["exp"] == "E0"}
    print("\n#### experiment matrix (builds fixed): geo-mean time change vs E0 per weapon [M10B close / stat.boss / keep-away]; gap = best non-P90/MAG weapon vs best of P90/MAG")
    ws = sorted({(r["weapon"], r["policy"]) for r in rows}, key=lambda x: (x[0], x[1]))
    print("| exp | " + " | ".join("%s%s" % (w, "" if p == "stand" else " (close-in)") for w, p in ws) + " | gap stand | M10B close / stat.boss / keep-away |")
    print("|---" * (len(ws) + 3) + "|")
    for ex in [x for x in dict.fromkeys(r["exp"] for r in rows)]:
        cells = []
        er = {(r["weapon"], r["policy"]): r for r in rows if r["exp"] == ex}
        for k in ws:
            r, b = er[k], base[k]
            cells.append("%+.0f%%" % (100 * geo([rel(t_of(r["enc"][e], e) if e != "short_window" else r["enc"][e]["damage"],
                                                     t_of(b["enc"][e], e) if e != "short_window" else b["enc"][e]["damage"], e) for e in ENCS])))
        # gap: per encounter best time among {P90, MAG} vs the best of the others (stand)
        gaps = []
        for e in ENCS:
            if e == "short_window": continue
            top = min(er[(w, "stand")]["enc"][e]["time"] for w in ("P90", "MAG"))
            oth = min(er[(w, "stand")]["enc"][e]["time"] for w, p in ws if p == "stand" and w not in ("P90", "MAG"))
            gaps.append(max(oth, 0.05) / max(top, 0.05) - 1)
        m = er[("M10B", "close_in")] if ("M10B", "close_in") in er else er[("M10B", "stand")]
        print("| %s | %s | %+.0f%% | %.1f / %.1f / %.1f |" % (ex, " | ".join(cells), 100 * geo(gaps),
              m["enc"]["close_normal"]["time"], m["enc"]["stationary_boss"]["time"], m["enc"]["keepaway_boss"]["time"]))


def regret(d):
    rows = d["regret"]
    by = defaultdict(list)
    for r in rows:
        by[r["alt"]].append(r["regret"])
    print("\n#### effect opportunity cost: mixed-time regret when the effect replaces one slot of an optimized build (median over weapons and slots; lower = closer to optimal)")
    print("| effect | median regret | best case | worst case | n |")
    print("|---|---|---|---|---|")
    for alt, v in sorted(by.items(), key=lambda kv: statistics.median(kv[1])):
        print("| %s | %+.0f%% | %+.0f%% | %+.0f%% | %d |" % (alt, 100 * statistics.median(v), 100 * min(v), 100 * max(v), len(v)))
    print("\nslot removed -> cost of an empty slot instead (per weapon):")
    for r in rows:
        if r["alt"] == "(empty)":
            print("  %s: drop %s -> %+.0f%%" % (r["weapon"], r["slot_of"], 100 * r["regret"]))


def rof(d):
    print("\n#### RoF on each stress gun (optimized build, RoF replaced): time close / groups / stat.boss / endurance; reloads endurance")
    for r in d["rof"]:
        e = r["enc"]
        print("%-8s %-9s %-9s %s | reloads %.1f" % (r["weapon"], r["rof"], r["rules"], " / ".join("%.1f" % e[k]["time"] for k in ("close_normal", "groups", "stationary_boss", "endurance")), e["endurance"]["reloads"]))


def split(d):
    print("\n#### two guns from one budget: best-of-two time per encounter (secondary used where faster, +half-bar switch)")
    print("| primary + secondary | share | " + " | ".join(SH[e] for e in ENCS) + " | geo vs 100% |")
    print("|---" * (len(ENCS) + 3) + "|")
    base = {}
    for r in d["split"]:
        key = (r["primary"], r["secondary"])
        if r["share"] == 1.0: base[key] = r
    for r in d["split"]:
        b = base[(r["primary"], r["secondary"])]
        g = geo([max(0.05, r["enc"][e]["time"]) / max(0.05, b["enc"][e]["time"]) - 1 for e in ENCS if e != "short_window"])
        cells = ["%.1f%s" % (r["enc"][e]["time"], "*" if r["enc"][e]["used"] == "secondary" else "") for e in ENCS]
        print("| %s + %s | %.0f%% | %s | %+.0f%% |" % (r["primary"], r["secondary"], 100 * r["share"], " | ".join(cells), 100 * g))
    print("(* = the secondary was the better gun there)")


def boss(d):
    print("\n#### Day 5 boss part 1 (scripted) and keep-away boss: time / taken / out-of-range turns")
    print("| exp | weapon | policy | scripted time (p90) | scripted taken | keep-away time | keep-away oor | miss |")
    print("|---|---|---|---|---|---|---|---|")
    for r in d["boss"]:
        s, k = r["scripted"], r["keepaway"]
        print("| %s | %s | %s | %.1f (%.1f) | %.0f | %.1f | %.0f%% | %.0f%% |" % (r["exp"], r["weapon"], r["policy"], s["time"], s["p90"], s["taken"], k["time"], 100 * k["oor"], 100 * k["miss"]))


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    part = sys.argv[2] if len(sys.argv) > 2 else "all"
    for name, fn in (("endurance", endurance), ("builds", builds), ("crit", crit), ("movement", movement), ("matrix", matrix),
                     ("regret", regret), ("rof", rof), ("split", split), ("boss", boss)):
        if part in ("all", name) and name in d:
            fn(d)
