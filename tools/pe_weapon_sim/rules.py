"""Rulesets. VANILLA and CURRENT are frozen (MappingProxyType); experiments copy CURRENT.

Every rule carries a validation status in VALIDATION (see weapon-mechanics-validation doc):
  D = decomp-verified (function cited), R = runtime-verified (read from the running game),
  L = log-calibrated (play log), A = assumed (no direct evidence yet).
"""
from types import MappingProxyType

# Per-bullet power by Rate of Fire (Battle_StepEnemyMovement hitCountPercent[]).
HIT_PCT_VANILLA = {1: 100, 2: 60, 3: 41, 5: 25, 7: 18, 10: 13}

_VANILLA = dict(
    name="vanilla",
    hit_pct=HIT_PCT_VANILLA,
    # Heat / Frost: resist /5, weak x1.5, neutral x1; vanilla order Heat, then Frost unless weak.
    elem_resist=20, elem_neutral=100, elem_weak=150, elem_best_of_two=False,
    # Acid / Tranq / Cyanide: resist bits 0 average (rand()&1: 50%), 1 strong (never), 2 weak (always).
    status_avg=50, status_resist=0,
    status_preroll_skips_bosses=False,   # vanilla: bosses just have their own resist bits
    poison_pct=100,
    # Critical: +20 points to the distance crit threshold (Battle_CheckEvasion); the mod's extra
    # is a conversion of normal in-range hits (pe_mod_effects.c), 0 here.
    crit_points=20, crit_convert_pct=0.0,
    quickdraw_bonus=0,
    counter_mult=1.0,
    guard_attack_down=100, guard_slow_at=100,
    # Hit quality (Battle_CheckEvasion, distance per mille of the gun's range).
    graze_mult=0.30, splash_mult=0.10, crit_mult=1.5,
    graze_bands=((1000, 1200, 80), (1200, 1500, 50), (1500, 1800, 25)),
    miss_beyond=1800,
    # Half-bar turns (pe_atb_items.c): off in vanilla.
    half_bar_items=False, half_bar_weapon_switch=False,
    # Experiment switches (inert unless set).
    graze_mult_short=None, graze_mult_boss=None, recovery_scale=1.0, recovery_scale_kinds=(),
    keepaway_threshold_scale=1.0,
)

_CURRENT = dict(_VANILLA,
    name="current",
    hit_pct={1: 100, 2: 60, 3: 41, 5: 25, 7: 20, 10: 15},
    elem_resist=80, elem_neutral=115, elem_weak=150, elem_best_of_two=True,
    status_avg=60, status_resist=20, status_preroll_skips_bosses=True,
    poison_pct=125,
    crit_points=20, crit_convert_pct=(40 - 20) * 100 / 75.0,   # pe_mod_effects.c: (s_crit - 20) * 100 / 75
    quickdraw_bonus=15,
    counter_mult=1.0,                    # boost removed 2026-10-16 (HP-level bug)
    guard_attack_down=75, guard_slow_at=85,
    half_bar_items=True, half_bar_weapon_switch=True,
)

VANILLA = MappingProxyType(_VANILLA)
CURRENT = MappingProxyType(_CURRENT)

SHORT_KINDS = (1, 2, 3, 5)   # handgun, shotgun, machine gun, grenade launcher

EXPERIMENTS = {
    "E1": dict(graze_mult=0.50),                                   # global graze 30 -> 50%
    "E2": dict(graze_mult_short=0.50),                             # short-range classes only
    "E3": dict(graze_mult_boss=0.50),                              # bosses only
    "E4": dict(graze_bands=((1000, 1300, 80), (1300, 1600, 50), (1600, 1800, 25))),  # wider strong-graze band
    "E5": dict(recovery_scale=0.75, recovery_scale_kinds=(2, 4, 5)),   # shotgun/rifle/grenade recover 25% faster
    "E6": dict(keepaway_threshold_scale=0.70),                     # Day 5 keep-away boss part 1: 30% less to deal
}


# Phase 2 (2026-10-17): close-combat and identity experiments. Distances are absolute game
# units (not % of range), so range upgrades don't widen a proximity zone.
M10B = 0x6E
EXPERIMENTS.update({
    # C1 shotgun proximity damage: +bonus within r_full; "s" variants fade linearly to r_zero.
    **{"C1_%d" % b: dict(prox=dict(kinds=(2,), bonus=b / 100.0, r_full=400, r_zero=400)) for b in (15, 25, 30, 40, 50)},
    **{"C1s_%d" % b: dict(prox=dict(kinds=(2,), bonus=b / 100.0, r_full=400, r_zero=650, smooth=True)) for b in (15, 25, 30, 40, 50)},
    # C2 magazine: the late shotgun only (M10B), or every shotgun.
    **{"C2_m10b_%d" % p: dict(mag_scale={M10B: 1 + p / 100.0}) for p in (25, 50, 75, 100)},
    "C2_all_50": dict(mag_scale={2: 1.5}),
    # C4 faster shotgun recovery (firing commitment).
    "C4_25": dict(recovery_scale=0.75, recovery_scale_kinds=(2,)),
    "C4_50": dict(recovery_scale=0.50, recovery_scale_kinds=(2,)),
    # C5 shotgun stagger: per command volley, delays the target's next action; cooldown; bosses resist.
    "C5": dict(stagger=dict(kinds=(2,), chance=0.35, delay=0.8, cooldown=3.0, boss_mult=0.3)),
    # Handgun responsiveness: recovery -25%.
    "H1": dict(recovery_scale=0.75, recovery_scale_kinds=(1,)),
    # Machine-gun suppression (stress test only: per volley, cooldown, bosses resist).
    "M1": dict(stagger=dict(kinds=(3,), chance=0.25, delay=0.5, cooldown=3.0, boss_mult=0.3)),
    # R1 smart reload: reload at the turn's end when the rounds left won't cover the next turn.
    "R1": dict(smart_reload=True),
    # Analysis only (mechanism tests, not proposals):
    "X_crit600": dict(crit_zone_abs=(600, 960)),       # 50% crit zone capped at 600 units, 20% zone at 960
    "X_cmd25": dict(cmd_fill_scale=0.25),              # each extra command makes the bar fill 25% slower
    "X_cmd50": dict(cmd_fill_scale=0.50),
    "X_all1": dict(all_first_cmd_only=True),            # Attack All only on the first command of a turn
})

# Phase 4 (2026-10-19, source backend): Attack All per-bullet power (P90 Attack All dominates
# Disc2 group fights in the source model). Applied in engine.bullet for eff mode 'all'.
EXPERIMENTS.update({"AA_%d" % p: dict(all_mode_power_pct=p) for p in (50, 60, 70, 80)})
# AAm: the cut applies only while two or more enemies are alive (single targets keep full power).
EXPERIMENTS.update({"AAm_%d" % p: dict(all_mode_power_pct=p, all_mode_multi_only=True) for p in (30, 40, 50, 60, 70)})
# AAo: as AAm, but never in a battle that contains a boss (boss fights with adds keep full Attack All).
# RoFT_<T>: every RoF level's volley totals T% of one shot's power (per bullet T/n %), the general-upgrade sweep
# (R-E, 2026-10-19). Current: RoF2 120, RoF3 123, RoF5 125, RoF7 140, RoF10 150.
EXPERIMENTS.update({"RoFT_%d" % t: dict(hit_pct={1: 100, **{n: round(t / n) for n in (2, 3, 5, 7, 10)}}) for t in (150, 175, 200, 225)})
# AAd_<p>: Attack All damage x p% AFTER defense (2+ enemies alive, no boss). In the mod's pe_on_damage hook this is
# scaling both the attack term and the target's defense by p. AAo_* scales attack only, which floors weak guns at 1.
EXPERIMENTS.update({"AAd_%d" % p: dict(all_mode_damage_pct=p, all_mode_multi_only=True, all_mode_ordinary_only=True) for p in (30, 40, 50, 60, 70)})
# RoFS_<k>: installed RoF 5 / 7 / 10 mods fire k x faster (Aya's animation step scaled during the volley); RoFST_<k>_<t>
# adds volley power t% (hit_pct as RoFT). R-E general-upgrade sweep.
# RoFC_<n>[_<t>]: installed RoF 5 / 7 / 10 volleys play the follow loop in at most n frames (mod: Aya's animation step x
# follow / n during the volley), optionally with volley power t%.
for _n in (6, 8, 10):
    EXPERIMENTS["RoFC_%d" % _n] = dict(rof_fire_cadence={5: _n, 7: _n, 10: _n})
    for _t in (175, 200):
        EXPERIMENTS["RoFC_%d_%d" % (_n, _t)] = dict(rof_fire_cadence={5: _n, 7: _n, 10: _n}, hit_pct={1: 100, **{n: round(_t / n) for n in (2, 3, 5, 7, 10)}})
# AAn_<c>: Attack All total output = c/10 x one volley: each target takes min(1, c / (10 N)) of the damage after defense, N =
# live enemies, 2+ enemies, no boss. Crowd-scaled R-A (2026-10-19).
EXPERIMENTS.update({"AAn_%d" % c: dict(all_mode_crowd_c=c / 10, all_mode_multi_only=True, all_mode_ordinary_only=True) for c in (12, 15, 20)})
# PE study: PEv = vanilla Parasite Energy (vanilla heals, no half-bar powers / items) under the mod's combat rules;
# PEh_<a>_<b>_<c> = mod PE with Heal 1/2/3 at a/b/c % of max HP (mod CURRENT: 15/30/65).
EXPERIMENTS['PEv'] = dict(pe_mode='vanilla')
# CTR_<k>: counter roll's HP level x k/10 (the removed 'Counter chance %' boost; the logged run used x5).
EXPERIMENTS.update({'CTR_%d' % k: dict(counter_level_mult=k / 10) for k in (25, 50)})
# RoFE: final R-E candidate. Installed RoF 5 / 7 / 10 mods only: volley 200% (40 / 29 / 20% per bullet), follow loop
# at most 4 frames (never below the hit frame), per-shot hold removed. Built-in RoF and RoF 2 / 3 unchanged.
EXPERIMENTS['RoFE'] = dict(rof_fire_cadence={5: 4, 7: 4, 10: 4}, rof_no_hold=True, rof_mod_hit_pct={5: 40, 7: 29, 10: 20})
# RoFCH_<n>_<t>: RoFC_<n>_<t> plus the per-shot hold (anim row 'per': handgun / grenade 5, rocket 20) removed.
for _n, _t in ((6, 200), (6, 225), (4, 200), (4, 225)):
    EXPERIMENTS['RoFCH_%d_%d' % (_n, _t)] = dict(rof_fire_cadence={5: _n, 7: _n, 10: _n}, rof_no_hold=True, hit_pct={1: 100, **{k: round(_t / k) for k in (2, 3, 5, 7, 10)}})
# AAc_<p>: Attack All deals at most p% of a target's max HP per turn (2+ enemies, no boss): crowds need 2+ turns.
EXPERIMENTS.update({'AAc_%d' % p: dict(all_mode_hp_cap=p / 100) for p in (40, 50, 60, 75)})
EXPERIMENTS['AAc_50n'] = dict(all_mode_hp_cap=0.5, all_mode_crowd_c=2.0, all_mode_multi_only=True, all_mode_ordinary_only=True)
for _h in ((10, 25, 50), (15, 30, 50), (20, 40, 65)):
    EXPERIMENTS['PEh_%d_%d_%d' % _h] = dict(pe_heal_pct=dict(zip(('Heal1', 'Heal2', 'Heal3'), _h)))
for _k in (15, 20, 30):
    EXPERIMENTS["RoFS_%d" % _k] = dict(rof_fire_speed={5: _k / 10, 7: _k / 10, 10: _k / 10})
    for _t in (175, 200):
        EXPERIMENTS["RoFST_%d_%d" % (_k, _t)] = dict(rof_fire_speed={5: _k / 10, 7: _k / 10, 10: _k / 10}, hit_pct={1: 100, **{n: round(_t / n) for n in (2, 3, 5, 7, 10)}})
EXPERIMENTS.update({"AAo_%d" % p: dict(all_mode_power_pct=p, all_mode_multi_only=True, all_mode_ordinary_only=True) for p in (30, 35, 40, 45, 50, 60)})

# Experiment keys the source backend honours (others were built for the earlier abstract engine).
SOURCE_BACKEND_KEYS = {'counter_level_mult', 'all_mode_hp_cap', 'rof_no_hold', 'rof_mod_hit_pct', 'prox', 'mag_scale', 'all_mode_power_pct', 'all_mode_damage_pct', 'all_mode_crowd_c', 'pe_mode', 'pe_heal_pct', 'rof_fire_speed', 'rof_fire_cadence', 'all_mode_multi_only', 'all_mode_ordinary_only', 'graze_mult', 'graze_mult_short', 'graze_mult_boss',
                       'graze_bands', 'keepaway_threshold_scale', 'counter_mult', 'hit_pct', 'crit_points', 'crit_convert_pct',
                       'elem_resist', 'elem_neutral', 'elem_weak', 'quickdraw_bonus', 'poison_pct', 'status_avg', 'status_resist'}


def combine(*names):
    """CURRENT + several experiments; the mag_scale / stagger dicts of later ones replace earlier ones."""
    return experimental(*names)


def experimental(*names, **overrides):
    """CURRENT plus the named experiments (and any explicit overrides); returns a new dict."""
    r = dict(_CURRENT)
    tag = []
    for n in names:
        r.update(EXPERIMENTS[n]); tag.append(n)
    r.update(overrides)
    if overrides: tag.append("custom")
    r["name"] = "exp:" + ("+".join(tag) if tag else "none")
    return r


def graze_mult_for(rules, kind, boss):
    m = rules["graze_mult"]
    if rules.get("graze_mult_short") is not None and kind in SHORT_KINDS:
        m = max(m, rules["graze_mult_short"])
    if rules.get("graze_mult_boss") is not None and boss:
        m = max(m, rules["graze_mult_boss"])
    return m


VALIDATION = [
    # (mechanic, status, source)
    ("Per-bullet power = (offense/5 + gun attack) x hit%[RoF] / 100", "D", "Battle_StepEnemyMovement (battle/enemy_movement.c)"),
    ("Defense split by RoF (club: full defense)", "D", "Battle_StepEnemyMovement: defense / (turnWord & 0xF); actionId 8"),
    ("Damage <= 0 -> 1 (2 on a crit)", "D", "Battle_StepEnemyMovement"),
    ("Graze x0.3, crit x1.5, splash x0.1", "D", "Battle_StepEnemyMovement hit reaction"),
    ("Hit bands: in range hit; 100-120% 80% graze; 120-150% 50%; 150-180% 25%; beyond miss", "D", "Battle_CheckEvasion (battle/setup.c)"),
    ("Crit chance 5/20/50% by distance (>80%, 50-80%, <50%) +20 with Critical", "D", "Battle_CheckEvasion"),
    ("Club (actionId 8): no graze band, out of range = miss", "D", "Battle_CheckEvasion actionId 8"),
    ("Rocket splash (actionId 6): others hit if main hit; crit->hit, hit->graze, graze->splash", "D", "Battle_ResolveHitOnTimer + Battle_CheckEvasion attackType"),
    ("Burst: every live enemy in a ~90 degree cone, own distance roll", "D", "Battle_ResolveHitOnTimer turnWord&0xC0==0x80"),
    ("Attack All: one queue slot per target, each fires RoF bullets", "D", "Battle_FillActionQueue mode 0xC0 + Battle_StepCharacterAction"),
    ("Random Fire: RoF*3/2 bullets at random targets, defense split by RoF", "D", "Battle_FillActionQueue mode 0x40"),
    ("Every bullet uses 1 round; empty magazine = shot clicks, reload at turn end", "D", "Battle_FinalizeAttackResult; Battle_StepCharacterAction -> CommitAmmo -> mode 0xC"),
    ("Status/elements only on a hit with damage > 0; Cyanide proc blocks the rest", "D", "Battle_StepEnemyMovement (inside damage > 0)"),
    ("Rocket launchers: no status, no elements (category 2)", "D", "Battle_StepEnemyMovement attackClass; Inv_BuildWeaponList category"),
    ("Heat/Frost: resist /5, weak x1.5; Frost only if Heat not weak", "D", "Battle_StepEnemyMovement resistanceMode"),
    ("Status chance: average 50%, strong never, weak always", "D", "Battle_StepEnemyMovement rand()&1"),
    ("Range in game units = 150 * sqrt(range stat + bonus)", "D", "Inv_BuildWeaponList (battle/commands.c)"),
    ("ATB gain per tick = stat22 * factor[kind] / 10; full 9000; Slow -40%, Haste +50%", "D", "Battle_SetupEnemyAnims g_BattleActionOffenseScale; Battle main update"),
    ("ATB factor by kind: hg 10, sg 8, mg 10, rifle 8, gl 8, rocket 4, Maeda 10, club 20", "R", "g_BattleActionOffenseScale 0x800106D4 (save-state RAM)"),
    ("Animation loops by kind (windup, per-shot, recovery, hit frame)", "D", "g_BattleActionAnimRows 0x800106A4 + weapon-bank frame counts (findings/data/pe-animation-extract-2026-10-18.json), stepped by source_battle.attack (source backend)"),
    ("Quickdraw: stat22 % chance of a full bar at battle start", "D", "Battle_CheckDropChance (battle/context.c)"),
    ("Counter: after an enemy hit, chance L/1000 .. L/5000 by rank (L = HP level = level*10)", "D", "Battle_RollEnemySpawn; Battle_GetAgilityBonus reads stats.levels[0]"),
    ("Tool transfer: bonuses add to destination (cap 999), source zeroed", "D", "armor_capacity.c TRANSFER_STAT"),
    ("Weapon stats, slots, built-in effects", "R", "item table read from a save state (findings/data/pe-weapons-game-2026-10-16.csv)"),
    ("Enemy defense = 1.6 x level + 3", "L", "enemy rows (18 matched enemies)"),
    ("Enemy distance profiles (normal / boss / keep-away)", "L", "hitq + reach rows"),
    ("Seconds per tick / animation frame scale", "L", "battle rows secs/turns (handgun ~1.4 s per turn)"),
    ("Enemy attack interval and damage", "A", "1.0-1.4 s; damage from hurt rows only for the Day 5 boss"),
    ("Aya ATB does not fill while she is acting", "D", "menu/main_update.c Menu_MainUpdate: no gauge gain while game flag 0x100 (committed action, player_turn.c / turn.c)"),
    ("Counter rank difference", "D", "context.c Battle_RollEnemySpawn: s8(Aya rank = level - enemy identity low byte); opt-in identity_rank (default: enemy level)"),
    ("PE regen, costs, heals, Haste/Barrier/Detox/Medic/Slow/Confuse/Gene Heal/Preraise/Full Recover", "D", "Menu_MainUpdate; Battle_ApplySpellEffect; Entity_UpdateTimers (parasite_energy.py, opt-in pe)"),
    ("Haste cuts the defense term to 3/10; Barrier drains PE instead of HP", "D", "Entity_ResolveDropTable (entity/combat.c)"),
    ("Energy Shot power (PE-scaled, full defense, all PE spent)", "D", "Battle_ResolveHit state 0x100000; phase.c. Live cast 2026-10-19: 572 logged = formula with base 219 (full defense, integer level factor); save inputs give 566"),
    ("Preraise / Revive: HP maxHP/2, PE/4, gauge 0, ailments cleared", "D", "encounter.c phase 3; Battle_StepVictory case 7; Battle_ResetEnemyStats"),
    ("Items: Medicine 45/90/180/400, Full Recover, cures (cure or one-use immunity); armor auto-medicine / auto-cure", "D", "Battle_ApplyDamage; Entity_UpdateTimers effect 0x4000 / 0x8000"),
    ("Enemy steals (item / ammo) only with armor bit 0x10, 40%", "D", "Battle_ApplyEnemyAttack (literal; opt-in steals)"),
    ("PE powers pause the enemies and can't be interrupted; items are a committed action", "L", "user observation 2026-10-19 (consistent with Pm_StopLowerHalf / flag 0x100)"),
    ("Player reaction, melee dodge, cast / item choices", "L", "play-log calibration (reaction 30 paused, melee dodge 0.6 Days 1-4, --logged-casts / --logged-items)"),
    ("Player repositioning time", "R", "walk 440 units/s measured live (scene/player_movement.c: 5.0 x moveFactor x moveSpeed per update); when to walk is a policy parameter"),
]
