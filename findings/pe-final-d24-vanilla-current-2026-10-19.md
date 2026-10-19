# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 0.997→1.000 (+0.003, [+0.000, +0.008]) | 26.64→25.74 | 66.3→60.8 | 8.7→8.7 | 0.0→0.0 | 0.003→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 0.996→1.000 (+0.004, [+0.000, +0.009]) | 21.17→20.71 | 28.6→26.8 | 7.4→7.4 | 0.0→0.0 | 0.004→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 62.70→58.97 | 315.0→284.9 | 17.4→17.5 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D2-4 | ALL | 0.974→0.989 (+0.015, [+0.008, +0.024]) | 32.42→30.68 | 100.4→91.2 | 8.5→8.6 | 0.0→0.0 | 0.021→0.005 | 0.00 | 0.00 |
| human_reaction | D2-4 | ORDINARY | 0.972→0.989 (+0.016, [+0.009, +0.025]) | 26.26→25.06 | 50.5→45.6 | 7.2→7.3 | 0.0→0.0 | 0.021→0.005 | 0.00 | 0.00 |
| human_reaction | D2-4 | BOSS | 0.983→0.992 (+0.008, [+0.000, +0.025]) | 73.08→67.78 | 429.7→392.2 | 17.1→17.3 | 0.3→0.3 | 0.017→0.008 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 0.980→1.000 | 29.03→28.10 | 39.8→34.5 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 81.49→77.39 | 404.6→399.4 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 15.97→16.21 | 13.0→12.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 51.56→54.20 | 228.9→244.3 | 0.3→0.3 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 22.98→22.74 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 66.19→56.03 | 332.6→247.7 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 12.34→12.34 | 12.3→12.3 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 39.21→36.29 | 193.5→170.5 | 0.3→0.3 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 1.000→1.000 | 23.22→22.29 | 38.7→36.3 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 67.22→63.40 | 336.7→306.6 | 0.5→0.6 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 14.73→14.78 | 23.2→22.4 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 49.15→41.28 | 239.1→160.7 | 0.7→0.7 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 0.990→1.000 | 34.59→32.74 | 50.7→45.7 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 91.00→88.59 | 478.4→455.1 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 16.51→16.48 | 18.5→18.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 55.73→54.57 | 306.1→294.6 | 0.0→0.0 |
| human_reaction | D2-4 | class_grenade/ord | 99 | 0.939→0.990 | 37.15→34.58 | 76.5→61.9 | 0.0→0.0 |
| human_reaction | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 88.13→83.72 | 496.4→502.9 | 0.2→0.2 |
| human_reaction | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 19.00→19.32 | 32.8→30.6 | 0.0→0.0 |
| human_reaction | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 67.36→68.68 | 366.3→400.9 | 0.3→0.3 |
| human_reaction | D2-4 | class_handgun/ord | 99 | 0.980→1.000 | 28.32→27.01 | 45.3→42.6 | 0.0→0.0 |
| human_reaction | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 73.16→61.71 | 428.3→336.6 | 0.2→0.2 |
| human_reaction | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 14.53→14.51 | 18.6→18.6 | 0.0→0.0 |
| human_reaction | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 48.31→42.20 | 306.9→232.8 | 0.3→0.3 |
| human_reaction | D2-4 | class_machine/ord | 99 | 0.980→1.000 | 29.65→27.50 | 58.3→53.0 | 0.0→0.0 |
| human_reaction | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 85.10→70.50 | 539.5→377.7 | 0.6→0.6 |
| human_reaction | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 16.95→16.71 | 31.1→30.1 | 0.1→0.1 |
| human_reaction | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 64.23→51.60 | 405.7→311.5 | 0.6→0.6 |
| human_reaction | D2-4 | class_rifle/ord | 99 | 0.879→0.919 | 43.81→40.80 | 96.0→86.1 | 0.0→0.0 |
| human_reaction | D2-4 | class_rifle/boss | 15 | 0.867→0.933 | 98.71→101.15 | 537.6→587.2 | 0.0→0.0 |
| human_reaction | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 20.71→20.04 | 45.3→42.5 | 0.0→0.0 |
| human_reaction | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 59.66→62.66 | 356.8→388.1 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine_aa, class_grenade_aa, class_rifle_aa, class_handgun, class_machine, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.98; order class_handgun_aa, class_machine_aa, class_rifle_aa, class_grenade_aa, class_handgun, class_machine, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.003, human_reaction +0.015

