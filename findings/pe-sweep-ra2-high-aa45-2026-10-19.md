# Rule comparison: CURRENT → exp:AAo_45 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 33.61→41.13 | 43.4→61.6 | 10.1→14.9 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 23.33→36.85 | 30.3→62.9 | 9.6→18.3 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.988 (+0.000, [+0.000, +0.000]) | 46.47→46.47 | 59.9→59.9 | 10.7→10.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.25 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.66→31.66 | 47.7→47.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 50.64→50.64 | 68.8→68.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 17.18→51.90 | 7.1→95.1 | 0.0→0.2 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 36.53→36.53 | 60.8→60.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.45→25.45 | 39.3→39.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.61→41.61 | 54.5→54.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.13→27.69 | 5.8→29.2 | 0.0→0.2 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 30.04→30.04 | 42.2→42.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 24.17→24.17 | 40.0→40.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 35.36→35.36 | 48.0→48.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 11.92→28.33 | 6.9→49.5 | 0.0→0.7 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 50.78→50.78 | 49.5→49.5 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.68→45.68 | 90.2→90.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 73.08→73.08 | 76.1→76.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 22.02→59.57 | 25.9→123.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 54.31→54.31 | 70.1→70.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.43→26.43 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 50.23→50.23 | 64.8→64.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 16.66→47.67 | 7.0→82.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 42.10→42.10 | 64.1→64.1 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine, class_handgun, class_shotgun, class_grenade, class_grenade_aa, class_shotgun_aa, class_machine_aa, class_rifle_aa, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

