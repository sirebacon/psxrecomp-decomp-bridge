# Rule comparison: CURRENT → cfg:@G3A3.power+35,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.996→0.996 (+0.000, [+0.000, +0.000]) | 39.35→36.24 | 55.5→48.5 | 9.7→9.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 30.68→27.16 | 50.0→40.9 | 9.5→9.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.992→0.992 (+0.000, [+0.000, +0.000]) | 50.18→47.60 | 62.5→58.1 | 9.9→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.20 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 43.80→40.08 | 85.9→78.7 | 9.9→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 36.76→32.57 | 87.1→79.0 | 9.5→9.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 52.59→49.46 | 84.4→78.2 | 10.5→10.2 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.21 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.66→30.88 | 47.7→47.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 50.64→47.65 | 68.8→58.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.45→25.45 | 39.3→39.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.61→41.61 | 54.5→54.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 24.17→24.17 | 40.0→40.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 35.36→35.36 | 48.0→48.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.68→28.85 | 90.2→45.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 73.08→63.14 | 76.1→64.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.43→26.43 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 50.23→50.23 | 64.8→64.8 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 37.74→36.35 | 92.5→90.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.06→52.24 | 93.6→87.5 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 30.10→30.10 | 67.4→67.4 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 40.76→40.76 | 65.7→65.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 30.03→30.03 | 78.7→78.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 41.35→41.35 | 63.8→63.8 | 0.1→0.1 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 54.27→34.72 | 124.0→85.6 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 72.25→59.43 | 120.0→95.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.66→31.66 | 72.9→72.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 53.52→53.52 | 78.9→78.9 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, human_reaction +0.000

