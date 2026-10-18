"""Markdown tables from the phase 3 results: python -m pe_weapon_sim.economy.reporting"""
import json, os

from .run_phase3 import OUT, OUT_DIR

TABLES = os.path.join(OUT_DIR, "..", "pe-weapon-p3-tables-2026-10-17.md")


def m(s, k="mean", nd=1):
    if not s: return "-"
    v = s.get(k)
    return "-" if v is None else ("%.*f" % (nd, v) if isinstance(v, float) else str(v))


def mci(s, nd=2):
    if not s: return "-"
    return "%.*f ± %.*f" % (nd, s["mean"], nd, s["ci95"])


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def top(d, n=3):
    tot = sum(d.values()) or 1
    return ", ".join("%s %d%%" % (k, round(100 * v / tot)) for k, v in list(d.items())[:n])


def policies_overview(res, keys, phase="Disc2"):
    rows = []
    for k in keys:
        g = res.get(k)
        if not g: continue
        s, f = g["summary"][phase], g["summary"]["final"]
        rows.append([k, m(s["bp_earned"], nd=0), m(s["bp_spent"], nd=0), m(s["bp_pool"], nd=0), m(s["at_bought"]),
                     m(s["capacity"]), "%s/%s/%s" % (m(s["bonus_attack"], nd=0), m(s["bonus_range"], nd=0), m(s["bonus_bullets"], nd=0)),
                     m(s["magazine"], nd=0), top(s["guns"]), mci(s.get("suite_time")),
                     m(s.get("window_damage"), nd=0), "%s/%s" % (m(f["tools_got_total"]), m(f["tools_spent_total"])),
                     "%s/%s" % (m(f["donors_got"]), m(f["donors_harvested"]))])
    return table(["group", "BP earned", "BP spent", "BP pool", "AT lv bought", "capacity", "bonus atk/rng/bul",
                  "magazine", "final gun", "suite s", "6 s window dmg", "Tools got/spent", "donors got/harvested"], rows)


def bp_categories(res, keys, phase="Disc2"):
    rows = []
    for k in keys:
        g = res.get(k)
        if not g: continue
        s = g["summary"][phase]
        rows.append([k] + [m(s["bp_" + c], nd=0) for c in ("attack", "range", "bullets", "active_time", "capacity", "armor")]
                    + [m(s["bp_unspent"], nd=0)])
    return table(["group", "attack", "range", "bullets", "Active Time", "capacity", "armor", "unspent (banked + pool)"], rows)


def origins(res, keys, phase="Disc2"):
    rows = []
    for k in keys:
        g = res.get(k)
        if not g: continue
        s, f = g["summary"][phase], g["summary"]["final"]
        cell = []
        for st in ("attack", "range", "bullets"):
            cell.append("%s / %s / %s" % (m(s["bonus_%s_intrinsic" % st], nd=0), m(s["bonus_%s_bp" % st], nd=0),
                                          m(s["bonus_%s_booster" % st], nd=0)))
        rows.append([k] + cell + [m(f["extracted_bp"], nd=0)])
    return table(["group", "attack: item-born / BP / booster", "range", "bullets", "BP points moved by Tool"], rows)


def phases_table(res, key):
    g = res.get(key)
    if not g: return ""
    rows = []
    for p in ("D1", "D2-4", "D5", "Disc2"):
        s = g["summary"].get(p)
        if not s: continue
        rows.append([p, m(s["bp_earned"], nd=0), m(s["bp_spent"], nd=0), m(s["bp_unspent"], nd=0),
                     "%s/%s/%s" % (m(s["bonus_attack"], nd=0), m(s["bonus_range"], nd=0), m(s["bonus_bullets"], nd=0)),
                     m(s["magazine"], nd=0), top(s["guns"], 2), top({k: v for k, v in s["mods_share"].items()}, 4)
                     if False else ", ".join("%s %d%%" % (k, round(100 * v)) for k, v in list(s["mods_share"].items())[:4]),
                     mci(s.get("suite_time")), m(s["tools_left"])])
    return table(["phase", "BP earned", "spent", "unspent", "bonus atk/rng/bul", "mag", "gun", "mods (share of runs)",
                  "suite s", "Tools left"], rows)


def resources(res, keys):
    rows = []
    for k in keys:
        g = res.get(k)
        if not g: continue
        f = g["summary"]["final"]
        rows.append([k] + [m(f["tools_got_" + s]) for s in ("field", "drop", "rare", "bought")] +
                    [m(f["tools_spent_" + s]) for s in ("stat", "premium", "mod")] +
                    [m(f["boosters_got_" + s]) for s in ("field", "drop", "rare")] +
                    [m(f["booster_points_attack"]), m(f["extracted_attack"]), m(f["permits_used"]), m(f["junk_earned"], nd=0),
                     m(f["overflow"])])
    return table(["group", "Tools field", "drop", "rare", "bought", "spent: stats", "premium mod", "mod move",
                  "boosters field", "drop", "rare", "booster atk pts", "extracted atk", "permits used", "Junk earned", "overflow"], rows)


def probs(res, keys):
    rows = []
    for k in keys:
        g = res.get(k)
        if not g or "prob" not in g: continue
        p = g["prob"]
        f = lambda x: "-" if not p.get(x) else "%.0f%%" % (100 * p[x]["p"])
        rows.append([k, f("2cmd_by_D5"), f("2cmd_by_Disc2"), f("quickdraw_by_Disc2"), f("attack30_by_D5"), f("attack30_by_Disc2"),
                     f("range10_by_Disc2"), f("any_bp_on_bullets"), f("bp_mostly_active_time"), f("tools_limiting"),
                     f("second_underdeveloped")])
    return table(["group", "2 Cmd by D5", "2 Cmd end", "Quickdraw end", "atk +30 by D5", "atk +30 end", "range +10 end",
                  "any BP on bullets", "BP mostly AT", "Tools limiting", "2nd gun underdeveloped"], rows)


def magazine(res):
    g = res.get("magazine")
    if not g: return ""
    out = []
    for phase in ("D5", "Disc2"):
        rows = {}
        caps = sorted({r["magazine"] for r in g["grid"]})
        for r in g["grid"]:
            if r["phase"] != phase: continue
            rows.setdefault((r["config"], r["demand"]), {})[r["magazine"]] = r
        head = ["config", "rounds/turn"] + ["mag %d" % c for c in caps]
        body = []
        for (cfg, dem), byc in rows.items():
            body.append([cfg, dem] + ["%.2f (%s)" % (byc[c]["suite"], byc[c]["endurance"]["reloads"]) if c in byc else "-" for c in caps])
        out.append("**%s** — suite time s (endurance reloads)\n\n" % phase + table(head, body))
    return "\n\n".join(out)


def generic(res, part, keys=None, phase="Disc2"):
    g = res.get(part)
    if not g: return ""
    keys = keys or [k for k in g if isinstance(g[k], dict) and "summary" in g[k]]
    return policies_overview(g, keys, phase)


def main():
    with open(OUT) as fh:
        res = json.load(fh)
    P = res.get("policies", {})
    pk = [k for k in P]
    parts = ["# Phase 3 tables (generated %s)\n" % res.get("meta", {}).get("date", ""),
             "Means over matched seeds; ± is the 95% CI of the mean. `suite s` = engine geometric-mean clear time over "
             "close / groups / medium-mobile / keep-away boss / stationary boss / endurance at that checkpoint.\n",
             "## Policies at the end (Disc2)\n", policies_overview(P, pk),
             "\n## Policies at the end of Day 5 (D5)\n", policies_overview(P, pk, "D5"),
             "\n## BP by category (end)\n", bp_categories(P, pk),
             "\n## Where the main gun's bonuses came from (end)\n", origins(P, pk),
             "\n## Resources\n", resources(P, pk),
             "\n## Breakpoint probabilities\n", probs(P, pk)]
    for key in ("C|typical", "A|typical", "B_shotgun|typical", "D|typical"):
        parts += ["\n## By phase: %s\n" % key, phases_table(P, key)]
    if "profiles" in res:
        parts += ["\n## Exploration profiles (end)\n", generic(res, "profiles"),
                  "\n### Profiles: BP by category\n", bp_categories(res["profiles"], list(res["profiles"]))]
    if "ablations" in res:
        ab = res["ablations"]
        keys = [k for k in ab if k != "A0"]
        parts += ["\n## Ablations (end)\n", policies_overview(ab, keys), "\n### Ablations at D5\n", policies_overview(ab, keys, "D5")]
        a0 = ab.get("A0", {})
        rows = [[k, "+".join(v["mods"]), v["power"], v["magazine"], v["D5"]["suite_time"], v["Disc2"]["suite_time"]] for k, v in a0.items()]
        parts += ["\n### A0: phase 1/2 fixed-budget loadouts (+12 attack, stage mods + 1 permit)\n",
                  table(["gun", "mods", "power", "magazine", "D5 suite s", "Disc2 suite s"], rows)]
    if "magazine" in res:
        parts += ["\n## Magazine breakpoints (M10B)\n", magazine(res)]
    if "shotgun" in res:
        sg = res["shotgun"]
        parts += ["\n## Shotgun experiments S0-S4 (B_shotgun)\n", policies_overview(sg, list(sg)),
                  "\n### S0-S4 at D5\n", policies_overview(sg, list(sg), "D5")]
        rows = [[k, mci(v["close_in"]["suite"]), mci(v["close_in"]["taken"], 0)] for k, v in sg.items()]
        parts += ["\n### Close-in play (stop at 350 units, +30% hit risk while close)\n", table(["variant", "suite s", "damage taken"], rows)]
    if "sensitivity" in res:
        se = res["sensitivity"]
        keys = [k for k in se if k != "anim_scale"]
        parts += ["\n## Sensitivity (end)\n", policies_overview(se, keys), "\n### Sensitivity: BP by category\n", bp_categories(se, keys)]
        rows = [[r["scale"], r["gun"], r["mods"], r["suite"]] for r in se.get("anim_scale", [])]
        parts += ["\n### Animation scale\n", table(["scale", "gun", "mods", "suite s"], rows)]
    if "validation" in res:
        rows = [[k, v["spearman"], v["n"]] for k, v in res["validation"].items()]
        parts += ["\n## Surrogate vs engine (Spearman of score vs 1 / suite time)\n", table(["phase", "rho", "loadouts"], rows)]
    with open(TABLES, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")
    print("wrote", os.path.normpath(TABLES))


if __name__ == "__main__":
    main()
