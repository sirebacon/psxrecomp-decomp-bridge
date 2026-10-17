"""Calibration data for the weapon simulator, from the play log (pe_play_log.csv).

Writes findings/data/pe-calibration-<date>.json with:
  - reach: share of Aya's ready time with the nearest live enemy in range / graze band /
    far band / out of reach, per gun kind, split normal vs boss fights (reach rows; only rows
    after the target-test fix carry data);
  - hit_distance: landed hits by distance band (as % of the gun's range) per gun kind, normal vs
    boss (hitq rows), and the crit / graze shares per band;
  - enemy_defense: real defense and HP per enemy id (enemy rows), with the wiki level when known,
    and a least-squares defense-per-level fit;
  - turn_timing: battle seconds per Aya turn (battle rows: secs / turns) per gun kind;
  - day5_boss: the recorded attempts at boss part 1 (room 156) and part 2 (room 380).

Usage: python pe_log_calibration.py [--log path] [--out path]
"""
import argparse, collections, csv, datetime, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG = r"D:\Recomp Games\Parasite Eve Project\parasite-eve-recomp\build-release\pe_play_log.csv"
COLS = ["kind", "battle", "day", "map", "scene", "play_s", "level", "exp", "hp", "max_hp", "junk", "wayne", "detail"]
KIND_NAMES = {1: "handgun", 2: "shotgun", 3: "machine", 4: "rifle", 5: "grenade", 6: "rocket", 7: "special", 8: "club"}
BANDS = ["lt50", "50_80", "80_100", "100_120", "120_150", "gt150"]


def kv(detail):
    return dict(m.groups() for m in re.finditer(r"(\w+)=([^ ]+)", detail))


def weapon_kinds():
    path = os.path.join(HERE, "..", "findings", "data", "pe-weapons-game-2026-10-16.csv")
    return {int(r["id"], 16): int(r["kind"]) for r in csv.DictReader(open(path))}


def load(path):
    rows = []
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split(",", 12)
            if len(parts) < 13 or parts[0] == "kind":
                continue
            rows.append(dict(zip(COLS, parts)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "findings", "data",
                                                  "pe-calibration-%s.json" % datetime.date.today().isoformat()))
    a = ap.parse_args()
    kinds = weapon_kinds()
    rows = load(a.log)

    # Battle rows close a battle; the reach / hitq / enemy rows of that battle come just before.
    reach = collections.defaultdict(lambda: [0, 0, 0, 0])
    hitd = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
    timing = collections.defaultdict(list)
    pending_reach, pending_hitq, pending_enemies = [], [], []
    enemies = {}
    day5 = []
    for r in rows:
        d = kv(r["detail"])
        k = r["kind"]
        if k == "reach":
            pending_reach.append(d)
        elif k == "hitq":
            pending_hitq.append((d, r["detail"]))
        elif k == "enemy":
            pending_enemies.append(d)
            eid = d.get("id")
            if eid and d.get("boss") == "0":
                e = enemies.setdefault(eid, dict(hp=set(), defense=set()))
                e["hp"].add(int(d.get("hp", 0))); e["defense"].add(int(d.get("def", 0)))
        elif k == "battle":
            boss = d.get("boss") == "1"
            tag = "boss" if boss else "normal"
            gun = int(d.get("gun", "0x0"), 16)
            kind = KIND_NAMES.get(kinds.get(gun, 0), "?")
            for rd in pending_reach:
                if int(rd.get("ready", 0)) and int(rd.get("in", 0)) + int(rd.get("graze", 0)) + int(rd.get("far", 0)) + int(rd.get("out", 0)):
                    v = reach[(kind, tag)]
                    for i, key in enumerate(("in", "graze", "far", "out")):
                        v[i] += int(rd.get(key, 0))
            for hd, raw in pending_hitq:
                for band in BANDS:
                    m = re.search(r"\b%s=(\d+)/(\d+)/(\d+)/(\d+)" % band, raw)
                    if m:
                        v = hitd[(kind, tag)][band]
                        for i in range(4):
                            v[i] += int(m.group(i + 1))
            turns, secs = int(d.get("turns", 0)), float(d.get("secs", 0))
            if turns and secs and d.get("outcome") == "win" and not boss:
                timing[kind].append(secs / turns)
            if r["day"] == "5" and r["map"] in ("156", "380") or (r["map"] in ("156", "380") and boss):
                day5.append(dict(map=r["map"], gun="0x%02X" % gun, kind=kind, secs=secs, turns=turns,
                                 shots=int(d.get("shots", 0)), dealt=int(d.get("dealt", 0)),
                                 taken=int(d.get("taken", 0)), hp=d.get("hp"), casts=d.get("casts", ""),
                                 hitq=[raw for _, raw in pending_hitq]))
            pending_reach, pending_hitq, pending_enemies = [], [], []

    # Enemy defense against the wiki level (by HP match where the id is shared by variants).
    wiki = list(csv.DictReader(open(os.path.join(HERE, "..", "findings", "data", "pe-enemies-wiki-2026-10-14.csv"), encoding="utf-8")))
    def num(s):
        m = re.search(r"[\d,]+", s or ""); return int(m.group(0).replace(",", "")) if m else None
    by_hp = collections.defaultdict(list)
    for w in wiki:
        hp, lvl = num(w["hp"]), num(w["level"])
        if hp and lvl: by_hp[hp].append(lvl)
    pairs = []
    enemy_out = {}
    for eid, e in enemies.items():
        hp = max(e["hp"]); df = max(e["defense"])
        lvl = by_hp.get(hp, [None])[0]
        enemy_out[eid] = dict(hp=sorted(e["hp"]), defense=sorted(e["defense"]), wiki_level=lvl)
        if lvl: pairs.append((lvl, df))
    fit = None
    if len(pairs) >= 3:
        xs, ys = zip(*pairs)
        mx, my = statistics.mean(xs), statistics.mean(ys)
        slope = sum((x - mx) * (y - my) for x, y in pairs) / max(1e-9, sum((x - mx) ** 2 for x in xs))
        fit = dict(slope=round(slope, 3), intercept=round(my - slope * mx, 2), n=len(pairs),
                   ratio_mean=round(statistics.mean(y / x for x, y in pairs), 3))

    # Absolute distance profiles (game units) from hitq rows: each band's hits spread over
    # [lo, hi) x the battle's gun range, weighted by 1 / P(hit lands) to turn landed hits into
    # time spent there (in range 1, 100-120% 0.8, 120-150% 0.5, >150% 0.25).
    edges = {"lt50": (0.0, 0.5, 1.0), "50_80": (0.5, 0.8, 1.0), "80_100": (0.8, 1.0, 1.0),
             "100_120": (1.0, 1.2, 0.8), "120_150": (1.2, 1.5, 0.5), "gt150": (1.5, 1.8, 0.25)}
    profiles = collections.defaultdict(list)
    battle_ctx = None
    pend = []
    for r in rows:
        if r["kind"] == "hitq":
            pend.append(r)
        elif r["kind"] == "battle":
            d = kv(r["detail"])
            ctx = "keepaway" if r["map"] == "156" and d.get("boss") == "1" else ("boss" if d.get("boss") == "1" else "normal")
            for hr in pend:
                hd = kv(hr["detail"]); rng = int(hd.get("range", 0))
                if not rng: continue
                for band, (lo, hi, p) in edges.items():
                    m = re.search(r"\b%s=(\d+)/(\d+)/(\d+)/(\d+)" % band, hr["detail"])
                    if m:
                        n = sum(int(m.group(i)) for i in range(1, 5))
                        if n: profiles[ctx].append([round(lo * rng), round(hi * rng), round(n / p, 2)])
            pend = []
    # Reach tail (ready time beyond full range), per context, as a share to add.
    tails = {}
    for ctx, key in (("normal", "handgun/normal"), ("boss", "handgun/boss")):
        v = reach.get(tuple(key.split("/")))
        if v and sum(v):
            tails[ctx] = dict(graze=v[1] / sum(v), far=v[2] / sum(v), out=v[3] / sum(v), ref_range=1492)
    tails.setdefault("keepaway", dict(tails.get("boss", dict(graze=0.12, far=0.03, out=0.03, ref_range=1492))))

    out = dict(
        source=os.path.basename(a.log), rows=len(rows),
        abs_distance=dict(profiles), reach_tail=tails,
        reach={"%s/%s" % key: dict(zip(("in", "graze", "far", "out"), v), total=sum(v),
                                    share=dict(zip(("in", "graze", "far", "out"), [round(x / max(1, sum(v)), 3) for x in v])))
               for key, v in reach.items()},
        hit_distance={"%s/%s" % key: {b: dict(zip(("hit", "graze", "crit", "splash"), v)) for b, v in bands.items()}
                      for key, bands in hitd.items()},
        enemy_defense=dict(fit=fit, enemies=enemy_out),
        turn_timing={k: dict(n=len(v), median_s=round(statistics.median(v), 2), mean_s=round(statistics.mean(v), 2))
                     for k, v in timing.items() if v},
        day5_boss=day5,
    )
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", a.out)
    print(json.dumps(dict(reach=out["reach"], turn_timing=out["turn_timing"], defense_fit=fit), indent=1))
    for k, bands in out["hit_distance"].items():
        tot = {b: sum(v.values()) for b, v in bands.items()}
        allh = sum(tot.values())
        print(k, "hits", allh, " ".join("%s %.0f%%" % (b, 100 * tot.get(b, 0) / max(1, allh)) for b in BANDS))


if __name__ == "__main__":
    main()
