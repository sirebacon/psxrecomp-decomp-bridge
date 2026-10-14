"""Parasite Eve weapon-effect simulator: vanilla rules vs proposed rebalance.

Monte Carlo fights against the real enemy roster (findings/data/pe-enemies-wiki-2026-10-14.csv),
area by area, for a baseline gun (Rate of Fire 3, no other effects) plus each effect in turn.
Reports, relative to the baseline: time to clear a fight, ammo used, enemy attacks taken.

Decomp-backed (pe-mod-effects-overhaul-2026-10-14.md section 1):
  per-shot % by shots (100/60/41/25/18/13), defense split per shot, hit quality by distance
  (graze x0.3 / hit / critical x1.5; crit 5/20/50% by distance, +20 points with Critical),
  Heat/Frost (resist /5, weak x1.5, neutral x1; Frost only checked if Heat found no weakness),
  status rounds (resist bits: Average 50%, Weak always, Strong never).
Assumptions (marked A1..A9 in the report) where the decomp hasn't been read yet.

Usage: python pe_mod_sim.py [--fights N] [--csv path]
"""
import argparse, csv, os, random, re, statistics

HIT_PCT = {1: 100, 2: 60, 3: 41, 5: 25, 7: 18, 10: 13}

# ---- guesses (G1..G4): replace with values read from the game -----------------------
# G1 Aya's speed stat (stat22) by area: it is the Quickdraw chance in % and sets her ATB.
STAT22_BY_AREA = {"Day 1 Theater": 20, "Day 2 Central Park": 30, "Day 3 NYPD": 35,
                  "Day 4 Hospital": 40, "Day 5 Chinatown-Museum": 50, "Bosses (main game)": 45}
# G2 Attack Up / Down = offense read 2 levels higher / lower: about +/-5% gun damage.
ATTACK_LEVELS_PCT = 5
# G3 Slow Active Time = stat22 read 2 levels lower: ATB ~10% slower, Quickdraw -4 points.
SLOW_ATB, SLOW_QUICKDRAW = 0.90, 4
# G4 Counter: chance from agility and rank (decomp); ~30% vs a same-rank enemy, a full attack.

# ---- rules ----------------------------------------------------------------------
VANILLA = dict(
    name="vanilla",
    hit_pct=dict(HIT_PCT),
    elem={"Strong": 0.2, "Average": 1.0, "Weak": 1.5},
    elem_best_of_two=False,
    status_chance={"Strong": 0.0, "Average": 0.5, "Weak": 1.0},
    boss_status_immune=True,
    acid_tick=0.04,            # A4: fraction of max HP per enemy turn while poisoned
    counter_chance=0.30, counter_power=1.0,   # G4
    quickdraw_sure=False,                    # vanilla: chance = stat22 %
    attack_down_guard=1.0, slow_at_guard=1.0,  # damage taken with those armor effects
    attack_all_ammo_per_target=True,
    crit_bonus=20,
    ammo_above_5=1.0,          # ammo per shot beyond the 5th (RoF 7 / 10)
)
PROPOSED = dict(VANILLA,
    name="proposed",
    hit_pct={1: 100, 2: 60, 3: 41, 5: 25, 7: 20, 10: 15},
    elem={"Strong": 0.8, "Average": 1.15, "Weak": 1.5},
    elem_best_of_two=True,
    status_chance={"Strong": 0.2, "Average": 0.6, "Weak": 1.0},
    acid_tick=0.06,
    counter_chance=0.40, counter_power=1.0,
    quickdraw_sure=True,
    attack_down_guard=0.85, slow_at_guard=0.80,
    attack_all_ammo_per_target=False,
    crit_bonus=40,
    ammo_above_5=0.5,
)

# ---- effects (one at a time on the baseline gun) -----------------------------------
BASE = dict(rof=3)
EFFECTS = [
    ("baseline (RoF 3)", {}),
    ("RoF 1", dict(rof=1)), ("RoF 2", dict(rof=2)), ("RoF 5", dict(rof=5)),
    ("RoF 7", dict(rof=7)), ("RoF 10", dict(rof=10)),
    ("Random Fire", dict(mode="random")), ("Burst", dict(mode="burst")), ("Attack All", dict(mode="all")),
    ("Heat", dict(heat=True)), ("Frost", dict(frost=True)), ("Heat + Frost", dict(heat=True, frost=True)),
    ("Cyanide", dict(cyanide=True)), ("Acid", dict(acid=True)), ("Tranquilizer", dict(tranq=True)),
    ("Counter", dict(counter=True)), ("Quickdraw", dict(quickdraw=True)), ("Critical", dict(critical=True)),
    ("2 Commands", dict(commands=2)), ("3 Commands", dict(commands=3)),
    # armor
    ("Max HP Up", dict(maxhp=1.15)), ("Attack Up", dict(attack_levels=+1)),
    ("Attack Down", dict(attack_levels=-1)), ("Slow Active Time", dict(slow_at=True)),
]

# ---- enemies --------------------------------------------------------------------
AREAS = [  # (label, location keywords)
    ("Day 1 Theater", ["Theater", "Carnegie"]),
    ("Day 2 Central Park", ["Central Park"]),
    ("Day 3 NYPD", ["NYPD", "N.Y.P.D"]),
    ("Day 4 Hospital", ["Hospital"]),
    ("Day 5 Chinatown-Museum", ["Chinatown", "Sewer", "Subway", "Museum", "Warehouse"]),
]

def num(s):
    m = re.search(r"[\d,]+", s or "")
    return int(m.group(0).replace(",", "")) if m else None

def load_enemies(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out = []
    for r in rows:
        if "Chrysler" in r["location"] or not r["location"]:
            continue
        hp, lvl = num(r["hp"]), num(r["level"])
        if not hp or not lvl or r["Heat"] == "?":
            continue
        out.append(dict(name=r["variant"], loc=r["location"], hp=hp, level=lvl,
                        boss=r["o_Escape"] == "No",
                        heat=r["Heat"], frost=r["Freeze"], cyanide=r["Cyanide"],
                        acid=r["Acid"], tranq=r["Tranq"]))
    return out

def defense_of(e):
    return max(4, round(1.6 * e["level"]))          # A1: logged Day 1 ~4-6, Day 2 18

# ---- one fight ----------------------------------------------------------------------
def fight(rules, eff, group, attack, rng, stat22=35):
    """Returns (time, ammo, enemy attacks landed, HP lost in units of max HP)."""
    attack *= 1 + eff.get("attack_levels", 0) * ATTACK_LEVELS_PCT / 100.0
    atb = SLOW_ATB if eff.get("slow_at") else 1.0
    guard_mult = (rules["attack_down_guard"] if eff.get("attack_levels", 0) < 0 else 1.0) * \
                 (rules["slow_at_guard"] if eff.get("slow_at") else 1.0)
    rof = eff.get("rof", BASE["rof"])
    shots = rof
    pct = rules["hit_pct"][rof]
    mode = eff.get("mode")
    if mode == "random":
        shots = rof * 3 // 2                            # decomp (Battle_FillActionQueue): RoF x 3 / 2 random targets
    commands = eff.get("commands", 1)
    foes = [dict(e, cur=e["hp"], poisoned=False, stopped=0, d=defense_of(e),
                 t_next=rng.uniform(0.4, 1.2)) for e in group]
    dist = rng.uniform(0.3, 1.25)                       # A3: distance / range per fight
    t, ammo, taken = 0.0, 0, 0
    qd = 0.0
    if eff.get("quickdraw"):                            # decomp: chance = stat22 %
        qd = 1.0 if rules["quickdraw_sure"] else (stat22 - (SLOW_QUICKDRAW if eff.get("slow_at") else 0)) / 100.0
    aya_next = 0.0 if rng.random() < qd else 1.0 / atb
    def crit_chance():
        base = 5 if dist > 0.8 else 20 if dist > 0.5 else 50
        return base + (rules["crit_bonus"] if eff.get("critical") else 0)
    def shot_damage(f, per_shot_attack, n_shots):
        if dist > 1.2 and rng.random() < 0.2: return 0.0   # rare miss at the edge
        dmg = per_shot_attack - f["d"] / n_shots
        if dmg <= 0: return 1.0
        q = 1.0
        if dist > 1.0: q = 0.3 if rng.random() < 0.8 else 1.0      # graze band
        elif rng.random() * 100 < crit_chance(): q = 1.5
        dmg *= q
        m = 1.0
        if eff.get("heat") or eff.get("frost"):
            h = f["heat"] if eff.get("heat") else None
            fr = f["frost"] if eff.get("frost") else None
            if rules["elem_best_of_two"]:
                m = max(rules["elem"][x] for x in (h, fr) if x)
            else:                                        # vanilla: Heat first, Frost only if no weakness
                state = None
                if h: state = {"Strong": "r", "Weak": "w"}.get(h)
                if state != "w" and fr:
                    s2 = {"Strong": "r", "Weak": "w"}.get(fr)
                    if s2: state = s2
                m = {"r": rules["elem"]["Strong"], "w": rules["elem"]["Weak"]}.get(state, 1.0)
        return max(1.0, dmg * m)
    def status(f, key):
        if f["boss"] and rules["boss_status_immune"]: return False
        table = VANILLA["status_chance"] if key == "cyanide" else rules["status_chance"]   # Cyanide kills: keep vanilla
        return rng.random() < table[f[key]]
    def hit(f, per_shot_attack, n_shots):
        f["cur"] -= shot_damage(f, per_shot_attack, n_shots)
        if f["cur"] > 0 and eff.get("cyanide") and status(f, "cyanide"):
            f["cur"] = 0                                 # decomp: a Cyanide proc sets HP to -1 (turn.c)
        if eff.get("acid") and not f["poisoned"] and status(f, "acid"): f["poisoned"] = True
        if eff.get("tranq") and status(f, "tranq"): f["stopped"] = max(f["stopped"], 3)   # decomp: Stop counts 3 enemy turns
    per_shot = attack * pct / 100.0
    guard = 0
    while any(f["cur"] > 0 for f in foes) and guard < 400:
        guard += 1
        alive = [f for f in foes if f["cur"] > 0]
        nxt = min(f["t_next"] for f in alive)
        if aya_next <= nxt:                              # Aya acts
            t = aya_next
            for _ in range(commands):
                alive = [f for f in foes if f["cur"] > 0]
                if not alive: break
                tgt = min(alive, key=lambda f: f["cur"])
                if mode == "all":
                    for f in alive:
                        for _ in range(shots): hit(f, per_shot, shots)
                    ammo += shots * (len(alive) if rules["attack_all_ammo_per_target"] else 1)
                else:
                    for _ in range(shots):
                        alive = [f for f in foes if f["cur"] > 0]
                        if not alive: break
                        f = rng.choice(alive) if mode == "random" else (tgt if tgt["cur"] > 0 else min(alive, key=lambda x: x["cur"]))
                        hit(f, per_shot, rof)        # decomp: defense split by the base RoF, even for Random Fire
                        if mode == "burst":              # A8: each other foe in the cone is hit 40% of the time
                            for o in alive:
                                if o is not f and o["cur"] > 0 and rng.random() < 0.4: hit(o, per_shot, rof)
                    ammo += min(shots, 5) + max(0, shots - 5) * rules["ammo_above_5"]
            aya_next = t + 1.0 / atb + 0.04 * shots * commands     # A5: firing time locks Aya per shot
        else:                                            # an enemy acts
            f = min(alive, key=lambda x: x["t_next"])
            t = f["t_next"]
            f["t_next"] = t + rng.uniform(1.0, 1.4)      # A5: enemy turn every 1.0-1.4
            if f["poisoned"]: f["cur"] -= f["hp"] * rules["acid_tick"]
            if f["cur"] <= 0: continue
            if f["stopped"] > 0: f["stopped"] -= 1; continue
            if rng.random() < 0.75:                      # A9: 75% of enemy attacks land
                taken += 1
                if eff.get("counter") and rng.random() < rules["counter_chance"]:
                    f["cur"] -= shot_damage(f, attack * rules["counter_power"], 1)
    return t, ammo, taken, taken * guard_mult / eff.get("maxhp", 1.0)

# ---- runs ------------------------------------------------------------------------------
def area_groups(enemies, kws):
    pool = [e for e in enemies if any(k in e["loc"] for k in kws) and not e["boss"]]
    return pool

def stage_attack(pool):
    """A1: Aya's attack per turn for the area so a plain RoF 1 shot kills an average foe in ~2.5."""
    hp = statistics.mean(e["hp"] for e in pool)
    d = statistics.mean(defense_of(e) for e in pool)
    return d + hp / 2.5

def run(rules, enemies, fights, seed):
    rng = random.Random(seed)
    table = {}
    areas = AREAS + [("Bosses (main game)", None)]
    for label, kws in areas:
        if kws is None:
            pool = [e for e in enemies if e["boss"]]
            attack = statistics.mean(stage_attack(area_groups(enemies, k)) for _, k in AREAS[3:])
        else:
            pool = area_groups(enemies, kws)
            if not pool: continue
            attack = stage_attack(pool)
        groups = []
        for _ in range(fights):
            if kws is None: groups.append([rng.choice(pool)])
            else: groups.append([rng.choice(pool) for _ in range(rng.choice((1, 2, 2, 3)))])
        for name, eff in EFFECTS:
            r2 = random.Random(seed + 1)
            res = [fight(rules, eff, g, attack, r2, STAT22_BY_AREA.get(label, 35)) for g in groups]
            table[(label, name)] = tuple(statistics.mean(x[i] for x in res) for i in range(4))
    return table, [a for a, _ in areas]

def report(tables, areas):
    lines = []
    for rules_name, table in tables:
        lines.append("\n=== %s rules: change vs baseline (time / ammo / hits taken / HP lost; lower is better) ===" % rules_name)
        hdr = "%-18s" % "effect" + "".join("%-30s" % a[:28] for a in areas if (a, EFFECTS[0][0]) in table)
        lines.append(hdr)
        for name, _ in EFFECTS[1:]:
            row = "%-18s" % name
            for a in areas:
                if (a, EFFECTS[0][0]) not in table: continue
                b = table[(a, EFFECTS[0][0])]; v = table[(a, name)]
                row += "%-30s" % ("%+4.0f%% %+4.0f%% %+4.0f%% %+4.0f%%" % tuple(100 * (v[i] / b[i] - 1) if b[i] else 0 for i in range(4)))
            lines.append(row)
    return "\n".join(lines)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--csv", default=os.path.join(here, "..", "findings", "data", "pe-enemies-wiki-2026-10-14.csv"))
    ap.add_argument("--fights", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    enemies = load_enemies(a.csv)
    tv, areas = run(VANILLA, enemies, a.fights, a.seed)
    tp, _ = run(PROPOSED, enemies, a.fights, a.seed)
    print("enemies:", len(enemies), "| fights per area per effect:", a.fights)
    print(report([("VANILLA", tv), ("PROPOSED", tp)], areas))
