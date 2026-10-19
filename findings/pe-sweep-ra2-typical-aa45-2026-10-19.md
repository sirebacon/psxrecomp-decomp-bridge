# Rule comparison: CURRENT → exp:AAo_45 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.994→0.985 (-0.009, [-0.019, -0.002]) | 35.75→44.88 | 48.4→70.8 | 11.0→16.9 | 0.0→0.2 | 0.000→0.002 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→0.983 (-0.017, [-0.033, -0.003]) | 25.33→41.76 | 35.7→76.0 | 10.6→21.1 | 0.0→0.2 | 0.000→0.003 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.988 (+0.000, [+0.000, +0.000]) | 48.78→48.78 | 64.3→64.3 | 11.6→11.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.26 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.45→39.45 | 73.0→73.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.52→55.52 | 83.9→83.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→0.967 | 22.45→56.28 | 21.3→107.4 | 0.0→0.4 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 40.23→40.23 | 71.0→71.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.00→26.00 | 40.2→40.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.78→41.78 | 57.2→57.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.64→32.60 | 5.8→44.9 | 0.0→0.6 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.03→31.03 | 44.0→44.0 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 25.53→25.53 | 47.5→47.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 39.40→39.40 | 50.6→50.6 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 12.32→34.68 | 7.7→65.4 | 0.0→1.0 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 51.74→51.74 | 52.2→52.2 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 47.68→47.68 | 91.9→91.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 75.09→75.09 | 79.2→79.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→0.867 | 23.23→74.95 | 29.5→158.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 56.98→56.98 | 73.2→73.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.61→26.61 | 33.1→33.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 51.43→51.43 | 65.8→65.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 17.37→53.83 | 7.1→98.8 | 0.0→0.4 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 44.61→44.61 | 65.5→65.5 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun_aa, class_handgun, class_shotgun, class_grenade, class_shotgun_aa, class_machine_aa, class_grenade_aa, class_rifle, class_rifle_aa
- win-rate delta (proposal − baseline) by set: logged_player_serial -0.009

