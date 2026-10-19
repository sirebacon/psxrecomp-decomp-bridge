# Rule comparison: CURRENT → cfg:@G3A3.power+35,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.996→0.996 (+0.000, [+0.000, +0.000]) | 41.76→37.93 | 61.7→52.0 | 10.6→10.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 33.05→28.71 | 57.2→43.7 | 10.3→9.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.992→0.992 (+0.000, [+0.000, +0.000]) | 52.64→49.46 | 67.3→62.4 | 10.9→10.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.21 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 47.45→42.18 | 94.4→82.1 | 10.9→10.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.14 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 40.08→34.42 | 95.9→81.3 | 10.5→10.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 56.65→51.89 | 92.5→83.2 | 11.4→11.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.22 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.45→31.44 | 73.0→48.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.52→49.46 | 83.9→72.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.00→26.00 | 40.2→40.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.78→41.78 | 57.2→57.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 25.53→25.53 | 47.5→47.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 39.40→39.40 | 50.6→50.6 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 47.68→33.97 | 91.9→49.4 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 75.09→65.23 | 79.2→65.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.61→26.61 | 33.1→33.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 51.43→51.43 | 65.8→65.8 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 50.09→36.71 | 129.6→90.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 63.59→54.36 | 110.8→93.6 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 30.81→30.81 | 68.0→68.0 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 40.93→40.93 | 65.7→65.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 32.03→32.03 | 85.5→85.5 | 0.0→0.0 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 44.13→44.13 | 73.0→73.0 | 0.1→0.1 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 56.91→41.95 | 125.4→91.3 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 76.34→61.76 | 125.5→96.0 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 30.57→30.57 | 71.1→71.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 58.27→58.27 | 87.4→87.4 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, human_reaction +0.000

