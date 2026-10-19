# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 25.74→26.47 | 60.8→57.9 | 8.7→9.6 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 20.71→22.40 | 26.8→27.6 | 7.4→8.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 58.97→53.35 | 284.9→257.7 | 17.5→16.9 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 1.000→1.000 | 28.10→28.10 | 34.5→34.5 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 77.39→77.39 | 399.4→399.4 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 16.21→23.92 | 12.4→17.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 54.20→54.20 | 244.3→244.3 | 0.3→0.3 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 22.74→22.74 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 56.03→56.03 | 247.7→247.7 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 12.34→18.67 | 12.3→23.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 36.29→36.29 | 170.5→170.5 | 0.3→0.3 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 1.000→1.000 | 22.29→22.29 | 36.3→36.3 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 63.40→63.40 | 306.6→306.6 | 0.6→0.6 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 14.78→18.50 | 22.4→28.1 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 41.28→41.28 | 160.7→160.7 | 0.7→0.7 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 1.000→1.000 | 32.74→25.19 | 45.7→29.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 88.59→58.83 | 455.1→308.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 16.48→19.76 | 18.4→19.5 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 54.57→39.41 | 294.6→224.3 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine_aa, class_rifle_aa, class_handgun, class_machine, class_grenade_aa, class_rifle, class_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

