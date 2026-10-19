# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 0.998→0.999 (+0.001, [+0.000, +0.003]) | 28.20→28.40 | 69.5→64.2 | 9.6→10.5 | 0.1→0.2 | 0.001→0.001 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 0.997→0.999 (+0.001, [+0.000, +0.004]) | 22.47→23.71 | 30.2→29.6 | 8.2→9.2 | 0.1→0.1 | 0.001→0.001 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 66.03→59.32 | 328.7→292.9 | 19.2→18.6 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 1.000→1.000 | 29.81→29.81 | 38.4→38.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 84.37→84.37 | 435.0→435.0 | 0.6→0.6 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 17.66→24.98 | 14.9→17.8 | 0.1→0.2 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 67.01→67.01 | 324.2→324.2 | 0.9→0.9 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 24.13→24.13 | 36.4→36.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 64.06→64.06 | 313.5→313.5 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 13.62→19.55 | 16.9→24.4 | 0.1→0.2 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 38.29→38.29 | 168.5→168.5 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 0.990→0.990 | 26.30→26.30 | 41.1→41.1 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 69.74→69.74 | 321.1→321.1 | 0.9→0.9 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 16.24→19.95 | 23.5→29.9 | 0.2→0.3 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 52.77→52.77 | 247.9→247.9 | 0.9→0.9 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 0.990→1.000 | 34.62→25.20 | 50.6→29.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 92.28→58.84 | 485.8→308.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 17.38→19.76 | 19.9→19.5 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 59.73→39.50 | 333.6→224.7 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_rifle_aa, class_machine_aa, class_handgun, class_rifle, class_grenade_aa, class_grenade, class_machine
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.001

