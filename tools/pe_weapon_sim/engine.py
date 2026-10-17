"""One fight, decomp formulas per bullet. Time in seconds.

Timing (rules.VALIDATION marks the assumptions):
  ATB: gain per tick = stat22 * ATB_FACTOR[kind] / 10, full at 9000 (D/R); TICK_HZ ticks a second
  (L: calibrated so a level-21 handgun turn is ~1.4 s). Two modes: "overlap" (the bar refills
  while Aya fires; turn interval = max(fill, commit)) and "serial" (fill + commit).
  Commit (firing animation): ANIM loops (R) x LOOP_S, plus PER_SHOT_S a bullet and TURN_S a turn (A).
Distance: each enemy has an absolute distance redrawn from the encounter's profile whenever it acts
  (L); bands as % of the gun's range (D). Player policy "stand" never moves; "approach" spends
  MOVE_S to step into range when the target is beyond it (A).
"""
import math
from .data import ATB_FACTOR, ANIM
from .rules import graze_mult_for

TICK_HZ = 94.0      # L: 9000 / (stat22 70 x 10 / 10) / 1.37 s median handgun turn (battle rows)
LOOP_S = 1.0 / 30
PER_SHOT_S = 3.0 / 30
TURN_S = 6.0 / 30
RELOAD_S = 0.8
MOVE_S = 0.6
ENEMY_PERIOD = (1.0, 1.4)
ENEMY_HIT = 0.75


ANIM_SCALE = 1.0       # sensitivity knob: multiplies every animation loop (loop length not measured)


def commit_seconds(kind, shots, rules):
    w0, w1, per, rec, _ = ANIM.get(kind, (0, 0, 0, 10, 2))
    w0, w1, per, rec = (x * ANIM_SCALE for x in (w0, w1, per, rec))
    if rules.get("recovery_scale", 1.0) != 1.0 and kind in rules.get("recovery_scale_kinds", ()):
        rec = rec * rules["recovery_scale"]
    return TURN_S + LOOP_S * (w0 + w1 + rec) + shots * PER_SHOT_S + max(0, shots - 1) * per * LOOP_S


def fill_seconds(stat22, kind, slow=False, haste=False):
    gain = stat22 * ATB_FACTOR.get(kind, 10) / 10.0
    if slow: gain -= gain * 2 / 5
    if haste: gain += gain / 2
    return 9000.0 / max(1e-6, gain) / TICK_HZ


class Stats(dict):
    def add(self, k, v=1):
        self[k] = self.get(k, 0) + v


def counter_chance(level, rank_diff=0):
    """Battle_RollEnemySpawn: L = HP level = level * 10 (stats.levels[0])."""
    L = level * 10
    if rank_diff > 0: return L / 1000.0
    if rank_diff == 0: return 3 * L / 5000.0
    if rank_diff == -1: return 3 * L / 10000.0
    return L / 5000.0


def fight(rules, cfg, aya, foes_in, profile, rng, policy="stand", timing="overlap",
          armor=None, threshold=None, target_first=None, enemy_dmg=None, time_cap=240.0, max_turns=None):
    """cfg: data.Weapon.config(); aya: dict(level, stat22, offense); foes_in: enemy dicts.
    threshold: scripted fight (dict enemy index -> real HP to deal) ends when reached.
    Returns Stats."""
    armor = armor or {}
    eff = cfg["eff"]
    kind = cfg["kind"]
    rof = eff.get("rof", 1)
    mode = eff.get("mode")
    commands = eff.get("commands", 1)
    hitp = rules["hit_pct"].get(rof, 100)
    slow = bool(armor.get("slow_at"))
    stat22 = aya["stat22"] - (4 if slow else 0)              # Slow AT reads stat22 two levels lower (~-2/level, A)
    offense = aya["offense"] * (1 + 0.08 * armor.get("attack_levels", 0))
    guard = 1.0
    if armor.get("attack_levels", 0) < 0: guard *= rules["guard_attack_down"] / 100.0
    if slow: guard *= rules["guard_slow_at"] / 100.0
    st = Stats()
    foes = []
    for i, e in enumerate(foes_in):
        foes.append(dict(e, i=i, cur=float(e["hp"]), dealt=0.0, poisoned=False, stopped=0,
                         t_next=rng.uniform(0.4, 1.2), dist=profile.sample(rng)))
    loaded = cfg["magazine"]
    rng_units = cfg["range"]
    t = 0.0
    qd = 0.0
    if eff.get("quickdraw"):
        # Battle_CheckDropChance rolls stat22 %; the mod tops it up to stat22 + bonus (max 90).
        qd = max(stat22, min(90, stat22 + rules["quickdraw_bonus"])) / 100.0
    aya_next = 0.0 if rng.random() < qd else fill_seconds(stat22, kind, slow)
    st["quickdraw"] = int(aya_next == 0.0)

    def alive():
        return [f for f in foes if f["cur"] > 0]

    def done():
        if threshold:
            return any(foes[i]["dealt"] >= hp for i, hp in threshold.items())
        return not alive()

    def element_pct(f):
        if not (eff.get("heat") or eff.get("frost")) or kind == 6:
            return 100
        tbl = {"Strong": rules["elem_resist"], "Weak": rules["elem_weak"]}
        h = f["heat"] if eff.get("heat") else None
        fr = f["frost"] if eff.get("frost") else None
        if rules["elem_best_of_two"]:
            return max(tbl.get(x, rules["elem_neutral"]) for x in (h, fr) if x)
        state = h if h in ("Strong", "Weak") else None
        if state != "Weak" and fr in ("Strong", "Weak"):
            state = fr
        return tbl.get(state, rules["elem_neutral"]) if state else rules["elem_neutral"]

    def status_lands(f, key, vanilla_roll=False):
        """Resist bits: Weak always; vanilla Average 50% (rand()&1), Strong never; the mod
        pre-rolls Acid/Tranq with its own chances (not Cyanide, not bosses)."""
        v = f[key]
        if v == "Weak": return True
        if vanilla_roll:
            return v != "Strong" and rng.random() < 0.5
        return rng.random() * 100 < (rules["status_resist"] if v == "Strong" else rules["status_avg"])

    def reaction(f):
        """Battle_CheckEvasion: None (miss), 'graze', 'hit', 'crit'."""
        d = f["dist"] * 1000.0 / rng_units
        roll = rng.random() * 100
        if kind == 8:                                   # club: no graze band
            if d >= 1001: return None
        else:
            if d >= rules["miss_beyond"] + 1: return None
            for lo, hi, p in reversed(rules["graze_bands"]):
                if d >= lo + 1:
                    return "graze" if roll < p else None
        thr = (rules["crit_points"] if eff.get("critical") else 0) + (5 if d >= 801 else 20 if d >= 501 else 50)
        if roll < thr: return "crit"
        if eff.get("critical") and rules["crit_convert_pct"] and rng.random() * 100 < rules["crit_convert_pct"]:
            return "crit"
        return "hit"

    def bullet(f, react, split):
        """Battle_StepEnemyMovement for one landed bullet."""
        if react is None:
            st.add("miss"); return
        st.add(react)
        power = (offense / 5.0 + cfg["power"]) * hitp / 100.0
        dmg = power - f["defense"] / (1 if kind == 8 else split)
        landed_positive = dmg > 0
        if landed_positive:
            dmg *= {"graze": graze_mult_for(rules, kind, f["boss"]), "crit": rules["crit_mult"],
                    "splash": rules["splash_mult"]}.get(react, 1.0)
            if kind != 6:
                cyan = False
                if eff.get("cyanide") and status_lands(f, "cyanide", vanilla_roll=True):
                    cyan = True; st.add("cyanide")
                if not cyan:
                    vr = bool(f["boss"] and rules["status_preroll_skips_bosses"]) or rules["name"] == "vanilla"
                    if eff.get("acid") and not f["poisoned"] and status_lands(f, "acid", vr):
                        f["poisoned"] = True; f["ptime"] = t; st.add("acid")
                    if eff.get("tranq") and status_lands(f, "tranq", vr):
                        f["stopped"] = max(f["stopped"], 3); st.add("tranq")
                    dmg = dmg * element_pct(f) / 100.0
                if cyan and not f["boss"] and not threshold:
                    st.add("overkill", max(0.0, f["cur"]))
                    f["dealt"] += f["cur"]; f["cur"] = 0; return
        dmg = int(dmg) if dmg > 0 else (2 if react == "crit" else 1)
        st.add("overkill", max(0.0, dmg - f["cur"]))
        st.add("damage", min(dmg, max(0.0, f["cur"])))
        f["cur"] -= dmg; f["dealt"] += dmg

    def volley(tgt):
        """One command: returns bullets fired (rounds used)."""
        nonlocal loaded
        fired = 0
        def shoot():
            nonlocal loaded, fired
            if loaded <= 0:
                st.add("click"); return False
            loaded -= 1; fired += 1; st.add("rounds"); return True
        if mode == "all":
            for f in list(alive()):
                for _ in range(rof):
                    if f["cur"] <= 0: break
                    if not shoot(): continue            # empty: the rest of the bullets click
                    bullet(f, reaction(f), rof)
        elif mode == "random":
            for _ in range(rof * 3 // 2):
                a = alive()
                if not a: break
                if not shoot(): continue
                f = rng.choice(a); bullet(f, reaction(f), rof)
        else:
            for _ in range(rof):
                a = alive()
                if not a: break
                if not shoot(): continue
                f = tgt if tgt["cur"] > 0 else min(a, key=lambda x: x["cur"])
                r = reaction(f)
                bullet(f, r, rof)
                if mode == "burst":                     # ~90 degree cone: 50% of the others are inside (A)
                    for o in alive():
                        if o is not f and rng.random() < 0.5:
                            bullet(o, reaction(o), rof)
                if kind == 6 and r is not None:          # rocket splash on everyone else
                    for o in alive():
                        if o is not f:
                            bullet(o, {"crit": "hit", "hit": "graze", "graze": "splash"}[r], rof)
        return fired

    taken = 0.0
    guard_n = 0
    while not done() and t < time_cap and guard_n < 5000 and not (max_turns and st.get("turns", 0) >= max_turns):
        guard_n += 1
        a = alive()
        if not a:
            break
        nxt = min(f["t_next"] for f in a)
        if aya_next <= nxt:
            t = aya_next
            st.add("turns")
            if target_first is not None and foes[target_first]["cur"] > 0:
                tgt = foes[target_first]
            else:
                inr = [f for f in a if f["dist"] <= rng_units]
                tgt = min(inr or a, key=lambda f: f["cur"])
            moved = 0.0
            if policy == "approach" and tgt["dist"] > rng_units:
                tgt["dist"] = rng.uniform(0.6, 0.95) * rng_units
                moved = MOVE_S; st.add("move_s", MOVE_S)
            if tgt["dist"] > rng_units:
                st.add("turns_out_of_range")
            shots = 0
            for _ in range(commands):
                if done() or not alive(): break
                shots += volley(tgt)
            commit = commit_seconds(kind, shots, rules) + moved
            if loaded <= 0:
                loaded = cfg["magazine"]; st.add("reloads"); commit += RELOAD_S
            st.add("commit_s", commit)
            fill = fill_seconds(stat22, kind, slow)
            aya_next = t + (max(fill, commit) if timing == "overlap" else fill + commit)
        else:
            f = min(a, key=lambda x: x["t_next"])
            t = f["t_next"]
            f["t_next"] = t + rng.uniform(*ENEMY_PERIOD)
            f["dist"] = profile.sample(rng)            # it moves
            if f["poisoned"]:
                # turn.c: every 31 battle ticks hpAlive -= periodicDamage (D); periodicDamage from
                # enemy rows: ~2-8 for normal enemies by level, ~30 for bosses (L). Applied for the
                # time since the last tick here.
                pd = 30 if f["boss"] else 2 + f["level"] // 8
                pd = pd * rules["poison_pct"] / 100.0
                since = t - f.get("ptime", t)
                tick = pd * since * TICK_HZ / 31.0
                f["ptime"] = t
                f["cur"] -= tick; f["dealt"] += tick; st.add("poison", tick)
                if f["cur"] <= 0: continue
            if f["stopped"] > 0:
                f["stopped"] -= 1; continue
            if rng.random() < ENEMY_HIT:
                st.add("hits_taken")
                hurt = (enemy_dmg or (lambda e: 1.6 * e["level"]))(f) * guard
                taken += hurt
                if eff.get("counter") and rng.random() < counter_chance(aya["level"]) * rules["counter_mult"]:
                    st.add("counters")
                    volley(f)
    st["time"] = t
    st["damage_taken"] = taken
    st["won"] = int(done())
    return st
