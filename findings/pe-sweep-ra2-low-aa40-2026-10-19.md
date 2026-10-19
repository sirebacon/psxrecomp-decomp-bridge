# Rule comparison: CURRENT → exp:AAo_40 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.993→0.907 (-0.085, [-0.109, -0.063]) | 38.17→50.97 | 50.3→81.0 | 11.6→20.2 | 0.0→0.3 | 0.000→0.009 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→0.847 (-0.153, [-0.193, -0.110]) | 26.71→49.75 | 37.6→92.8 | 11.2→26.7 | 0.0→0.6 | 0.000→0.017 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.983→0.983 (+0.000, [+0.000, +0.000]) | 52.50→52.50 | 66.1→66.1 | 12.1→12.1 | 0.1→0.1 | 0.000→0.000 | 0.00 | 0.26 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.34→39.34 | 72.9→72.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 56.99→56.99 | 82.1→82.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→0.667 | 22.53→72.53 | 21.6→145.4 | 0.0→1.1 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 42.61→42.61 | 72.5→72.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.66→27.66 | 44.8→44.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 0.958→0.958 | 56.87→56.87 | 58.2→58.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 13.07→44.46 | 7.0→67.3 | 0.0→1.4 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.66→31.66 | 44.4→44.4 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 26.49→26.49 | 50.1→50.1 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 41.22→41.22 | 56.1→56.1 | 0.2→0.2 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 12.78→44.26 | 8.5→86.8 | 0.1→1.9 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 52.45→52.45 | 55.2→55.2 | 0.2→0.2 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.48→48.48 | 94.2→94.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 78.61→78.61 | 83.5→83.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→0.000 | 23.82→90.00 | 31.0→197.4 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 60.85→60.85 | 79.0→79.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.50→31.50 | 36.9→36.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 55.64→55.64 | 65.2→65.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→0.800 | 21.41→72.80 | 9.1→132.5 | 0.0→1.2 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 48.13→48.13 | 65.1→65.1 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun_aa, class_shotgun, class_grenade, class_handgun, class_machine_aa, class_rifle, class_shotgun_aa, class_grenade_aa, class_rifle_aa
- win-rate delta (proposal − baseline) by set: logged_player_serial -0.085

