# Parasite Eve: weapon simulation audit (2026-10-17)

Phase 1 of the weapon balance study. Audits the three old simulators (`tools/pe_mod_sim.py`,
`pe_combo_sim.py`, `pe_gun_progression_sim.py`, snapshot = git tag `sims-pre-audit-2026-10-16`)
against the decomp and the play log, and documents the replacement, `tools/pe_weapon_sim/`.
The old scripts are kept unchanged for reproducibility; do not use them for decisions.

Status legend (see [pe-weapon-mechanics-validation-2026-10-17.md](pe-weapon-mechanics-validation-2026-10-17.md)):
D decomp-verified, R read from the running game / a save state, L log-calibrated, A assumed.

## 1. Confirmed implementation errors in the old simulators

| # | Old behaviour | Real mechanic (source) | Effect on results |
|---|---|---|---|
| 1 | **Range treated as linear**: distance / raw range stat (rifle 110 = 2x a handgun 55) | Range in game units = 150 x sqrt(stat) (`Inv_BuildWeaponList`, D): rifle 110 = 1573 vs handgun 1112, **1.41x** | The old "rifles dominate keep-away bosses" result was inflated. Keep-away: rifle 110 in range 80% of the time (old model 95%), handgun 52%, machine gun 40%. |
| 2 | **Status on misses**: `hit()` applied Acid / Tranq / Cyanide even when `shot_damage()` returned 0 | Status and elements only inside `damage > 0` of a landed bullet (`Battle_StepEnemyMovement`, D) | Status effects overrated at long range. Test `test_no_status_on_miss`. |
| 3 | **Attack All ammo**: charged RoF x targets but took only RoF from the magazine | One queue slot per target, RoF bullets each, every bullet 1 round (`Battle_FillActionQueue`, `Battle_FinalizeAttackResult`, D) | Attack All reloads underestimated (~3x too few vs 3 targets). Test `test_attack_all_uses_rof_per_target`. |
| 4 | **Empty magazine = the whole action is a reload** | Remaining bullets click; reload animation at the end of the turn (`Battle_StepCharacterAction` -> mode 0xC, D) | High RoF on small magazines was modelled as a lost turn; now as wasted bullets + a reload. Test `test_empty_magazine_clicks_and_reloads`. |
| 5 | **Burst = 40% chance per other enemy** | Every live enemy inside a ~90 degree cone in front of Aya, each with its own distance roll (`Battle_ResolveHitOnTimer`, D) | Cone membership is geometry; still an assumption (50%) until enemy positions are logged. |
| 6 | **No splash** anywhere; grenade launchers assumed to be area weapons | Splash exists only for **rocket launchers** (actionId 6): the others take the main hit's reaction one step down (crit -> hit -> graze -> x0.1). Grenade launchers are single-target (D/R) | The "grenade = crowd control" hypothesis is **not** supported by the game. |
| 7 | **Critical = +40 points** (proposal value) | The mod keeps the game's +20 and turns 26.7% of the remaining normal in-range hits into crits (`pe_mod_effects.c`, D) | Crit chance 78/56/45% (close/mid/edge) instead of 90/60/45%. Test `test_crit_conversion_only_with_critical`. |
| 8 | **Counter 5x** in the "proposed" rules, base 5% | Boost removed 2026-10-16 (it corrupted the HP level). Vanilla chance after an enemy hit = L/1000 .. L/5000 by rank with L = level x 10 (`Battle_RollEnemySpawn`, D): **6-33% late game** | Vanilla Counter is far better than the old 2-8% assumption (that was level 9). |
| 9 | **"Ammo above 5 shots at 50%"** in the proposed rules | Not implemented in the mod | Proposed RoF 7/10 were overrated on ammo. |
| 10 | **Aya's offense** guessed 35-120 by area | Level table (`AyaLevelStats` at *0x800A803C + 0x800A8028, R): 65 (lv7) .. 200 (lv24) .. 350 (lv33) | Flat per-bullet power was ~half its real size: gun attack differences were exaggerated. |
| 11 | **Aya's stat22** (ATB / Quickdraw) 56-78 | Same table (low byte of row +6): 56 (lv7) .. 73 (lv24) .. 82 (lv33) | Small change. |
| 12 | **Gun stats** from the RPGClassics page | Game item table read from a save state: kind, base / bonus stats, slots, slot cap, built-in effects (R, `findings/data/pe-weapons-game-2026-10-16.csv`) | Several guns differ (M9 17/53/8, slots and built-ins exact). |
| 13 | **Mod slots capped at 3** for every gun | Real slots (M500 8, M203 4 5, M9 3 / MP5PDW 2 with none free) | Slot count turned out to be the largest mid-game differentiator. |
| 14 | **Uniform random distances 15-75** (units unclear) | Absolute distances from the play log (hitq landed hits re-weighted by hit chance + reach rows for out-of-range time, L) | Normal fights mean 703 units, bosses 934, the Day 5 keep-away boss 1188. |
| 15 | **Timing**: `aya_next = t + 1/atb + 0.04 x shots` | ATB gain = stat22 x factor[kind] / 10 per tick, full at 9000 (D, factors R); firing animation from `g_BattleActionAnimRows` (R loops, A frame length) | Class timing structure is now the game's; absolute loop length still assumed (sensitivity run). |
| 16 | **Poison** 4-5% max HP per enemy turn | Every 31 battle ticks hpAlive -= periodicDamage (turn.c, D); periodicDamage ~2-8 normal, ~30 bosses (enemy rows, L) | Acid worth 4-16% (was 2-7%). |
| 17 | **Progression**: only the attack bonus moved by Tool | All three bonuses add to the destination, source zeroed, source item kept (`armor_capacity.c TRANSFER_STAT`, D) | No duplication bug in the old code; range / capacity transfers were missing. Tests `test_transfer_*`. |
| 18 | **Enemy defense** 1.6 x level | 1.6 x level + 3 (least squares over 18 logged enemies, L) | Small. |

Checked and found correct: per-bullet % by RoF (100/60/41/25/18/13), defense split by RoF (also for
Random Fire), graze x0.3 / crit x1.5, hit bands 80/50/25%, crit 5/20/50% +20, Heat/Frost vanilla
order, status 50% / never / always, ATB class factors (handgun/machine 1.0, rifle/shotgun/grenade 0.8).

## 2. Unverified assumptions (remaining)

| Assumption | Value used | How to resolve |
|---|---|---|
| Animation loop length | 1 frame @30 fps per loop; 3 frames a bullet; 6 frames a turn | Debug-server watch of Aya's actionMode per frame for each class (one battle each) |
| ATB does not depend on firing (overlap mode) | turn interval = max(fill, commit) | Same instrumentation; "serial" mode run as sensitivity |
| Reload time | 0.8 s | Same; sensitivity 0.3-1.5 s changes results by < 5% except the shotgun (+17% at 1.5 s) |
| Burst cone membership | 50% of the other enemies | Log enemies hit per Burst bullet |
| Enemy attack rhythm / damage | every 1.0-1.4 s, 75% land, 1.6 x level per hit (Day 5 boss: 15 HP/s, fitted) | hurt rows per enemy slot (add slot to the hurt row) |
| Counter rank difference | equal rank | Log Aya's and the enemy's rank byte on each Counter roll |
| Player movement | "stand" or "approach" (0.6 s to step into range) | Not observable; both reported |
| Mod pool and investment by story stage | tables in `data.py` / `run_benchmark.py` | Loadout logging (see 4) |

## 3. Validation against the play log

Day 5 boss part 1 (room 156, scripted: ~450 real HP, defense 33, three attacking helpers):

| | Log | Model (current rules) |
|---|---|---|
| M79, attempt 1 / 2 | 12 s, 153 HP lost / 27 s, 434 HP | RoF 5, attack 66 (the only loadout that gives the logged 19 per bullet): 17.9 s mean, p10-p90 12-23 s, 263 HP |
| M9 (upgraded) | 8 s, 131 HP | RoF 3, attack 40 (20 per bullet), 2 Commands, stepping into range: 10.2 s, 151 HP |

The logged attempts also used Haste (2-4 casts) and Slow, which the model leaves out, and the
loadouts (bonuses, mods) are not in the log. Within those limits the model lands inside the
logged spread; the M79's logged per-bullet damage rules out RoF 2.

Per-bullet damage check (Day 1, level 1, M84F attack 12, RoF 2, defense 9): formula 6.3 -> log 6
(crit 9). Test `test_damage_day1_log`.

## 4. Recommended instrumentation (cheap, high value)

1. **Loadout per battle**: gun id, attack / range / bullet bonuses, mods, armor id and mods,
   Aya's stat22 and offense, in the battle row. Without it no live result can be checked exactly.
2. **Enemy slot on hurt rows** and **enemies hit per bullet** (Burst / rocket splash).
3. **Animation timing**: frames from command to control return per class and RoF (debug server).
4. **Counter**: roll, rank bytes, result.

## 5. Tests

`python -m unittest discover -s tools/pe_weapon_sim/tests` (17 tests): range formula, Day 1
damage vs log, Counter formula, ATB factors, no status on misses, weak status lands, rockets
apply no status, Attack All ammo, empty magazine clicks + reload, graze band and E1, club has no
graze band, crit conversion, baselines frozen / experiments separate, Counter not boosted,
scripted threshold, Tool transfer sums / zeroes, repeated transfers conserve bonuses.
