# Rule comparison: CURRENT → cfg:@G3A3.power+45,@M203_4.power+25 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 39.35→35.68 | 55.5→47.9 | 9.7→9.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 30.68→26.67 | 50.0→40.1 | 9.5→8.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 50.18→46.93 | 62.5→57.7 | 9.9→9.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.20 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 43.80→39.55 | 85.9→77.2 | 9.9→9.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 36.76→31.97 | 87.1→77.2 | 9.5→8.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 52.59→49.03 | 84.4→77.2 | 10.5→10.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.21 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.66→29.78 | 47.7→44.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 50.64→46.88 | 68.8→57.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.45→25.45 | 39.3→39.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.61→41.61 | 54.5→54.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 24.17→24.17 | 40.0→40.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 35.36→35.36 | 48.0→48.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.68→27.52 | 90.2→44.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→1.000 | 73.08→60.59 | 76.1→63.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.43→26.43 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 50.23→50.23 | 64.8→64.8 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 37.74→35.20 | 92.5→84.3 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.06→51.78 | 93.6→86.5 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 30.10→30.10 | 67.4→67.4 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 40.76→40.76 | 65.7→65.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 30.03→30.03 | 78.7→78.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 41.35→41.35 | 63.8→63.8 | 0.1→0.1 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 54.27→32.85 | 124.0→82.8 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 72.25→57.75 | 120.0→91.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.66→31.66 | 72.9→72.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 53.52→53.52 | 78.9→78.9 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.004, human_reaction +0.000

