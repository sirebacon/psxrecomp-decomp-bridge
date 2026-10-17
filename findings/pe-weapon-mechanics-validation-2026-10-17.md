# Parasite Eve: weapon mechanics validation table (2026-10-17)

What the simulator (`tools/pe_weapon_sim`) implements, and how sure we are.
D decomp-verified, R read from the game (save-state RAM / running game), L log-calibrated,
A assumed. Decomp paths are `parasite-eve-decomp/src/main/...`.

## Combat formulas

| Mechanic | Status | Source |
|---|---|---|
| Per-bullet power = (offense / 5 + gun attack) x hit%[RoF] / 100; hit% 100/60/41/25/18/13 | D | `battle/enemy_movement.c` Battle_StepEnemyMovement (legacy name: the damage routine) |
| Damage = power - defense / RoF (club: full defense); <= 0 -> 1 (2 on a crit) | D | same |
| Graze x0.3, crit x1.5, splash x0.1 (by the hit reaction) | D | same |
| Heat / Frost: resist /5, weak x1.5; Frost read only if Heat is not "weak" | D | same (`resistanceMode`) |
| Acid / Tranq / Cyanide: average 50% (`rand()&1`), strong never, weak always; only on a bullet with damage > 0; a Cyanide proc skips the others | D | same |
| Rocket launchers (category 2): no status, no elements | D | same (`attackClass`) + `battle/commands.c` Inv_BuildWeaponList |
| Maeda's gun 93 (category 3): sets the scripted finisher flag | D | same |
| Gun attack used as is (halved by "Steal, halves attack") | D | `battle/commands.c` Inv_BuildWeaponList |
| Day 1 check: 6 per bullet, 9 per crit, as logged | L | play log hit rows; test `test_damage_day1_log` |

## Hit resolution

| Mechanic | Status | Source |
|---|---|---|
| Distance per mille of range: <=1000 hit; 1001-1200 80% graze; 1201-1500 50%; 1501-1800 25%; >1800 miss | D | `battle/setup.c` Battle_CheckEvasion |
| Crit threshold 5 / 20 / 50% (>800, 501-800, <=500 per mille) + 20 with Critical | D | same |
| Club (actionId 8): no graze band, beyond range = miss; steal roll | D | same + `battle/attack.c` Battle_ResolveHitOnTimer |
| Rocket splash (actionId 6): if the main bullet lands, every other live enemy is hit one step down | D | Battle_ResolveHitOnTimer + Battle_CheckEvasion(attackType) |
| Burst: every live enemy in a ~90 degree cone, own distance roll | D (cone share A) | Battle_ResolveHitOnTimer |
| Range in game units = isqrt(stat x 22500) = 150 x sqrt(stat) | D | Inv_BuildWeaponList |

## Turns, ammo, timing

| Mechanic | Status | Source |
|---|---|---|
| Attack All: one queue slot per live target, RoF bullets each | D | `battle/turn.c` Battle_FillActionQueue (mode 0xC0) |
| Random Fire: RoF x 3 / 2 bullets at random targets (helpers included) | D | same (mode 0x40) |
| Each bullet uses 1 round; an empty magazine clicks; reload at the turn's end | D | `battle/attack.c` Battle_FinalizeAttackResult, Battle_StepCharacterAction |
| ATB gain per tick = stat22 x factor / 10, full at 9000; Slow -40%, Haste +50% | D | `battle/enemy_actions.c` Battle_SetupEnemyAnims; `menu/main_update.c` |
| ATB factor by kind: handgun 10, shotgun 8, machine 10, rifle 8, grenade 8, rocket 4, Maeda 10, club 20 | R | `g_BattleActionOffenseScale` 0x800106D4 |
| Animation loops by kind (windup, extra, per extra shot, recovery, hit frame) | R (frame length A) | `g_BattleActionAnimRows` 0x800106A4 |
| Ticks per second 94 (handgun turn ~1.37 s) | L | battle rows secs / turns |
| Reload 0.8 s, turn overhead, bullet time | A | sensitivity runs |
| Quickdraw: stat22 % chance of a full bar at battle start (mod: up to stat22 + 15, max 90) | D | `battle/context.c` Battle_CheckDropChance; `pe_mod_effects.c` |
| Counter: after an enemy hit lands, chance L/1000 (Aya higher rank), 3L/5000 (equal), 3L/10000 (one lower), L/5000 (lower); L = stats.levels[0] = HP level = level x 10 | D | `battle/context.c` Battle_RollEnemySpawn (legacy name), `aya/stats.c` Battle_GetAgilityBonus |
| Poison: every 31 ticks hpAlive -= periodicDamage | D | `battle/turn.c` |
| periodicDamage ~2-8 (normal), ~30 (bosses) | L | enemy rows `poison=` |

## Aya and equipment data

| Data | Status | Source |
|---|---|---|
| Weapon base / bonus stats, kind, slots, slot cap, built-in effects (ids 0x3F-0x94) | R | item table from a save state -> `findings/data/pe-weapons-game-2026-10-16.csv` |
| Aya by level: HP, offense, defense, stat22, inventory capacity | R | `AyaLevelStats` table |
| Tool transfer: bonuses add (cap 999), source zeroed, source kept; mods move into a free slot | D | `item/armor_capacity.c` TRANSFER_STAT |
| Enemy defense 1.6 x level + 3 | L | enemy rows (18 matched) |
| Enemy HP / level / resistances | wiki (CC-BY-SA), game confirms Strong=1 / Weak=2 | `findings/data/pe-enemies-wiki-2026-10-14.csv` |

## Current mod rules (CURRENT ruleset), from source

| Rule | Vanilla | Current | Source |
|---|---|---|---|
| Heat/Frost neutral / weak / resist | 100 / 150 / 20 | 115 / 150 / 80 (whole hit scaled) | `pe_mod_effects.c` rows |
| Heat + Frost | Heat first | best of the two | same |
| RoF 7 / 10 per bullet | 18 / 13 | 20 / 15 | same |
| Acid / Tranq chance (not bosses) | 50 / 0 resist | 60 / 20 resist | same |
| Poison strength | 100% | 125% | same |
| Critical | +20 | +20 then 26.7% of normal in-range hits | same |
| Quickdraw | stat22 % | up to stat22 + 15 (max 90) | same |
| Counter | vanilla | vanilla (boost removed 2026-10-16) | same |
| Attack Down / Slow AT damage taken | 100 / 100 | 75 / 85 | same |
| Half-bar items / weapon switch | full bar | half bar | `pe_atb_items.c`, `pe_pe_balance.c` |

## Assumed (no direct evidence yet)

Enemy attack interval (1.0-1.4 s) and damage per hit (1.6 x level; Day 5 boss fitted to 15 HP/s),
75% of enemy attacks land, Burst cone share 50%, Counter at equal rank, player reposition time
0.6 s, animation loop length, reload time, mod availability and stat investment by story stage.
