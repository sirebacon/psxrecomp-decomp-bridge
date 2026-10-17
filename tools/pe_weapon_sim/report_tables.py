"""Print markdown tables from a benchmark JSON: python -m pe_weapon_sim.report_tables <json> [part]"""
import json, math, statistics, sys

ENCS = ["close_normal", "medium_mobile", "groups", "keepaway_boss", "stationary_boss", "short_window", "scripted_day5", "endurance"]
SHORT = {"close_normal": "close", "medium_mobile": "mobile", "groups": "groups", "keepaway_boss": "keep-away",
         "stationary_boss": "stat.boss", "short_window": "6s window dmg", "scripted_day5": "Day5 boss", "endurance": "endur."}


def classes(d):
    rows = d["classes"]
    keys = sorted({(r["stage"], r["model"]) for r in rows}, key=lambda k: (["Day3", "Day4", "Day5", "Day5+permit", "Wayne"].index(k[0]), k[1]))
    for stage, model in keys:
        for rn in ("vanilla", "current"):
            sel = [r for r in rows if r["stage"] == stage and r["model"] == model and r["rules"] == rn]
            if not sel: continue
            print("\n#### %s / %s / %s (mean clear time s; window = damage in 6 s; [x] = +%% vs best class)" % (stage, model, rn))
            print("| class | gun | mods | " + " | ".join(SHORT[e] for e in ENCS) + " | geo-mean rel |")
            print("|---" * (len(ENCS) + 4) + "|")
            best = {}
            for e in ENCS:
                if e == "short_window":
                    best[e] = max(r["enc"][e]["damage"] for r in sel)
                else:
                    best[e] = min(r["enc"][e]["time_mean"] for r in sel)
            for r in sel:
                cells, logs = [], []
                for e in ENCS:
                    s = r["enc"][e]
                    if e == "short_window":
                        rel = best[e] / max(1e-9, s["damage"]) - 1
                        cells.append("%.0f [%+.0f%%]" % (s["damage"], -100 * (1 - s["damage"] / best[e])))
                    else:
                        rel = s["time_mean"] / best[e] - 1
                        cells.append("%.1f [%+.0f%%]" % (s["time_mean"], 100 * rel))
                    logs.append(math.log(1 + max(0, rel)))
                gm = math.exp(sum(logs) / len(logs)) - 1
                print("| %s | %s | %s | %s | %+.0f%% |" % (r["cls"], r["gun"], "+".join(r["mods"]) or "-", " | ".join(cells), 100 * gm))


def mods(d):
    rows = d["mods"]
    encs = ["close_normal", "groups", "keepaway_boss", "stationary_boss", "endurance"]
    for rn in ("vanilla", "current"):
        print("\n#### single effects, %s rules: clear time vs the plain Day 5 gun (negative = faster), avg of 5 encounters; [taken]" % rn)
        clss = sorted({r["cls"] for r in rows})
        print("| effect | " + " | ".join(clss) + " |")
        print("|---" * (len(clss) + 1) + "|")
        for m in sorted({r["mod"] for r in rows}, key=lambda x: [r["mod"] for r in rows].index(x)):
            cells = []
            for c in clss:
                r = next((x for x in rows if x["rules"] == rn and x["cls"] == c and x["mod"] == m), None)
                if not r: cells.append("-"); continue
                t = statistics.mean(r["enc"][e]["time_vs_base"] for e in encs)
                k = statistics.mean(r["enc"][e]["taken_vs_base"] for e in encs)
                cells.append("%+.0f%% [%+.0f%%]" % (100 * t, 100 * k))
            print("| %s | %s |" % (m, " | ".join(cells)))


def rng(d):
    rows = d["range"]
    encs = ["keepaway_boss", "scripted_day5", "medium_mobile", "close_normal", "groups"]
    for pol in ("stand", "approach"):
        print("\n#### range experiments, policy %s: mean time (s) [%% vs E0]" % pol)
        clss = sorted({r["cls"] for r in rows})
        for e in encs:
            print("\n%s" % e)
            print("| exp | " + " | ".join(clss) + " | spread (max/min) |")
            print("|---" * (len(clss) + 2) + "|")
            base = {c: next(r for r in rows if r["exp"] == "E0" and r["cls"] == c and r["policy"] == pol)["enc"][e]["time_mean"] for c in clss}
            for ex in sorted({r["exp"] for r in rows}, key=lambda x: [r["exp"] for r in rows].index(x)):
                vals = {}
                for c in clss:
                    r = next(x for x in rows if x["exp"] == ex and x["cls"] == c and x["policy"] == pol)
                    vals[c] = r["enc"][e]["time_mean"]
                cells = ["%.1f [%+.0f%%]" % (vals[c], 100 * (vals[c] / base[c] - 1)) for c in clss]
                print("| %s | %s | %.2f |" % (ex, " | ".join(cells), max(vals.values()) / min(vals.values())))


def prog(d):
    print("\n#### progression strategies (current rules): mean time per day, close / groups / keep-away / stat.boss")
    print("| strategy | " + " | ".join(["Day%d" % i for i in range(1, 6)]) + " |")
    print("|---" * 6 + "|")
    for r in d["progression"]:
        cells = []
        for st in ["Day1", "Day2", "Day3", "Day4", "Day5"]:
            dd = r["days"][st]["enc"]
            cells.append("%s: %.1f/%.1f/%.1f/%.1f" % (r["days"][st]["main"], dd["close_normal"]["time"], dd["groups"]["time"],
                                                      dd["keepaway_boss"]["time"], dd["stationary_boss"]["time"]))
        print("| %s | %s |" % (r["strategy"], " | ".join(cells)))


def sens(d):
    print("\n#### sensitivity: Day 5 plain guns, mean time close / keep-away / stat.boss")
    for r in d["sensitivity"]:
        print("%s scale %.2f %-8s %s" % (r["timing"], r["scale"], r["cls"], " / ".join("%.1f" % r["enc"][e] for e in ("close_normal", "keepaway_boss", "stationary_boss"))))


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    part = sys.argv[2] if len(sys.argv) > 2 else "all"
    for name, fn in (("classes", classes), ("mods", mods), ("range", rng), ("progression", prog), ("sensitivity", sens)):
        if part in ("all", name) and name in d:
            fn(d)
