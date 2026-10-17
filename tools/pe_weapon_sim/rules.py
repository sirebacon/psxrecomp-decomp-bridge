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
    ("Animation loops by kind (windup, per-shot, recovery, hit frame)", "R", "g_BattleActionAnimRows 0x800106A4; absolute frames not measured"),
    ("Quickdraw: stat22 % chance of a full bar at battle start", "D", "Battle_CheckDropChance (battle/context.c)"),
    ("Counter: after an enemy hit, chance L/1000 .. L/5000 by rank (L = HP level = level*10)", "D", "Battle_RollEnemySpawn; Battle_GetAgilityBonus reads stats.levels[0]"),
    ("Tool transfer: bonuses add to destination (cap 999), source zeroed", "D", "armor_capacity.c TRANSFER_STAT"),
    ("Weapon stats, slots, built-in effects", "R", "item table read from a save state (findings/data/pe-weapons-game-2026-10-16.csv)"),
    ("Enemy defense = 1.6 x level + 3", "L", "enemy rows (18 matched enemies)"),
    ("Enemy distance profiles (normal / boss / keep-away)", "L", "hitq + reach rows"),
    ("Seconds per tick / animation frame scale", "L", "battle rows secs/turns (handgun ~1.4 s per turn)"),
    ("Enemy attack interval and damage", "A", "1.0-1.4 s; damage from hurt rows only for the Day 5 boss"),
    ("Aya ATB does not fill while she is acting", "A", "Battle update skips the fill on state 0x2600 (not mapped)"),
    ("Counter rank difference", "A", "ranks not mapped; equal rank assumed"),
    ("Player repositioning time", "A", "policy parameter (stand / approach)"),
]
