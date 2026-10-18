"""Campaign script from the play log: the ordered battles and field acquisitions of one real
main-game playthrough (2026-10-13..16), used as the "typical" exploration profile.

Save-state and memory-card loads branch the log. The final timeline is recovered backwards: from
the last row of the first playthrough, a load row jumps back to the latest earlier row whose
progress clock (cumulative EXP, play_s) is not above the loaded state's, so every event of an
abandoned branch (including a state loaded and immediately undone) is skipped and each fight
counts once. Phases follow the story-day field and Aya's level: D1 (Day 1), D2-4 (Days 2-4),
D5 (the day field at 5: Day 5 on disc 1), Disc2 (the field reads 1 again with Aya at level 24+:
disc 2, Chinatown / Warehouse / Subway / Museum to the final bosses; the run's pickups there match
those areas in the gear table).

python -m pe_weapon_sim.campaign [--log path]  -> findings/data/pe-campaign-2026-10-17.json
"""
import argparse, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "findings", "data", "pe-campaign-2026-10-17.json")
LOG = r"D:\Recomp Games\Parasite Eve Project\parasite-eve-recomp\build-release\pe_play_log.csv"


RESIST = {"0": "Average", "1": "Strong", "2": "Weak"}


def kv(s):
    return dict(re.findall(r"(\w+)=([^ ]+)", s))


def phase_of(day, level):
    if day == "1" and level <= 8: return "D1"
    if day in ("2", "3", "4"): return "D2-4"
    if day == "5": return "D5"
    return "Disc2" if level >= 24 else "D5"      # disc 2 continues Day 5 with the day field at 1


def _key(r):
    """Progress clock (cumulative EXP, play_s): EXP only grows within one timeline, while play_s
    is not monotonic across memory-card loads (disc swaps)."""
    try: return (int(r[7]), int(r[5]))
    except ValueError: return (-1, -1)


def _level(r):
    return int(r[6]) if r[6].lstrip("-").isdigit() else 0


def final_timeline(rows):
    """Rows of the final timeline of the first playthrough, in order (see module doc)."""
    end, late = len(rows), False
    for i, r in enumerate(rows):                       # cut the second playthrough
        if _level(r) >= 20: late = True
        if late and (r[0] == "newgame" or (0 < _level(r) <= 2 and _key(r)[1] > 200)):
            end = i; break
    real = lambda r: r[0] not in ("session", "stateload", "cardload") and r[2] != "-1" and _key(r)[1] > 200
    loads = {}
    for i in range(end):                               # restored clock of every load row
        if rows[i][0] == "stateload":
            loads[i] = _key(rows[i])
        elif rows[i][0] == "cardload":
            j = next((j for j in range(i + 1, end) if real(rows[j])), None)
            if j is not None: loads[i] = _key(rows[j])
    kept, i = [], end - 1
    while i >= 0:
        if i in loads:
            # Resume at the row with the highest clock not above the loaded state's (the latest
            # such row on ties): rows between it and the load belong to an abandoned branch.
            k = loads[i]
            best = max((j for j in range(i) if real(rows[j]) and _key(rows[j]) <= k),
                       key=lambda j: (_key(rows[j]), j), default=-1)
            i = best
            continue
        if real(rows[i]) or rows[i][0] in ("enemy", "loot", "rare_take", "rare_left", "econ_unlock", "econ_left"):
            kept.append(rows[i])
        i -= 1
    kept.reverse()
    return kept


def build(log=LOG):
    with open(log, encoding="utf-8", errors="replace") as fh:
        rows = [l.rstrip("\n").split(",", 12) for l in fh if l.count(",") >= 12]
    rows = final_timeline([r for r in rows if r[0] != "kind"])
    events = []
    enemies, rares = [], []
    last_battle = None
    for r in rows:
        k, d = r[0], kv(r[12])
        t = _key(r)
        if k == "enemy":
            bp = d.get("bp", "0/0/0").split("/")
            enemies.append(dict(id=d.get("id"), hp=int(d.get("hp", 0)), defense=int(d.get("def", 0)), exp=int(d.get("exp", 0)),
                                level=int(d.get("lv", 0) or 0),
                                bp_base=int(bp[0]), bp_factor=int(bp[1]), bp_hits=int(bp[2]),
                                drop=d.get("drop"), steal=d.get("steal"), boss=d.get("boss") == "1", died=d.get("died") == "1",
                                # resist bits (D: 0 average, 1 strong, 2 weak)
                                **{k: RESIST.get(d.get(k), "Average") for k in ("heat", "frost", "cyanide", "acid", "tranq")}))
        elif k in ("rare_take", "rare_left", "econ_unlock", "econ_left", "loot"):
            rares.append(dict(kind=k, **d))
        elif k == "battle":
            lv = int(r[6]) if r[6].lstrip("-").isdigit() else 1
            last_battle = (t, r[3])
            events.append(dict(type="battle", t=t, phase=phase_of(r[2], lv), level=lv, map=r[3], boss=d.get("boss") == "1",
                               outcome=d.get("outcome"), secs=float(d.get("secs", 0)), exp=int(d.get("exp", 0)), bp=int(d.get("bp", 0)),
                               gun=d.get("gun"), hits_taken=int(d.get("hits", 0)) if "hits" in d else None,
                               taken=int(d.get("taken", 0)), rewards=(d.get("rewards") or "").split(" ") if d.get("rewards") else [],
                               enemies=enemies, rare=rares))
            enemies, rares = [], []
        elif k == "add" and r[1] == "":
            item = int(d.get("item", "0x0"), 16)
            lv = int(r[6]) if r[6].lstrip("-").isdigit() else 1
            if r[3] not in ("0",) and lv >= 1:
                post = bool(last_battle) and last_battle[1] == r[3] and 0 <= t[1] - last_battle[0][1] <= 30
                events.append(dict(type="field", t=t, phase=phase_of(r[2], lv), map=r[3], item=item, post_battle=post))
        elif k == "pickup":
            item = int(d.get("item", "0x0"), 16); delta = int(d.get("delta", 0))
            if delta > 0:
                lv = int(r[6]) if r[6].lstrip("-").isdigit() else 1
                events.append(dict(type="pickup", t=t, phase=phase_of(r[2], lv), item=item, delta=delta))
        elif k == "wayne":
            events.append(dict(type="wayne", t=t, frm=int(d.get("from", 0)), to=int(d.get("to", 0))))
        elif k == "save":
            m = re.search(r"gun=0x([0-9A-Fa-f]+)\+(-?\d+)/(-?\d+)/(-?\d+) mods=([\d/]*)", r[12])
            a = re.search(r"armor=0x([0-9A-Fa-f]+)\+(-?\d+)/(-?\d+)/(-?\d+) mods=([\d/]*)", r[12])
            lv = int(r[6]) if r[6].lstrip("-").isdigit() else 1
            ev = dict(type="save", t=t, phase=phase_of(r[2], lv), level=lv, bp=int(d.get("bp", 0)), bag=d.get("bag"))
            for key, mm in (("gun", m), ("armor", a)):
                if mm:
                    ev[key] = dict(id=int(mm.group(1), 16), bonus=[int(mm.group(i)) for i in (2, 3, 4)],
                                   mods=[int(x) for x in mm.group(5).split("/") if x])
            events.append(ev)
        elif k in ("dismantle", "install", "buy", "permit_slot"):
            events.append(dict(type=k, t=t, detail=r[12]))
    return events


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--log", default=LOG); ap.add_argument("--out", default=OUT); a = ap.parse_args()
    ev = build(a.log)
    b = [e for e in ev if e["type"] == "battle" and e["outcome"] == "win"]
    summary = {}
    for e in b:
        s = summary.setdefault(e["phase"], dict(battles=0, bosses=0, bp=0, exp=0))
        s["battles"] += 1; s["bosses"] += e["boss"]; s["bp"] += e["bp"]; s["exp"] += e["exp"]
    json.dump(dict(source=os.path.basename(a.log), summary=summary, events=ev), open(a.out, "w"), indent=0)
    print("wrote", a.out, len(ev), "events"); print(json.dumps(summary, indent=1))
    gear = [e for e in ev if e["type"] == "field" and 0x3F <= e["item"] <= 0xC7]
    print("field gear:", [(e["phase"], hex(e["item"])) for e in gear])


if __name__ == "__main__":
    main()
