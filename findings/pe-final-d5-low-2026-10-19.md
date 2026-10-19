# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 38.17→36.63 | 50.3→47.7 | 11.6→12.6 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.71→27.13 | 37.6→38.0 | 11.2→13.4 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.983→0.983 (+0.000, [+0.000, +0.000]) | 52.50→48.52 | 66.1→59.8 | 12.1→11.6 | 0.1→0.1 | 0.000→0.000 | 0.00 | 0.26 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 40.54→37.89 | 81.0→77.5 | 12.1→13.1 | 0.1→0.1 | 0.000→0.000 | 0.00 | 0.19 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 32.14→31.93 | 73.3→76.5 | 11.5→13.8 | 0.0→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 51.03→45.33 | 90.7→78.9 | 12.8→12.3 | 0.1→0.1 | 0.000→0.000 | 0.00 | 0.28 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.34→31.75 | 72.9→48.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 56.99→49.29 | 82.1→70.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 22.53→28.30 | 21.6→36.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 42.61→37.25 | 72.5→61.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.66→27.66 | 44.8→44.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 0.958→0.958 | 56.87→56.87 | 58.2→58.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 13.07→26.54 | 7.0→27.9 | 0.0→0.4 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.66→31.66 | 44.4→44.4 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 26.49→26.49 | 50.1→50.1 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 41.22→41.22 | 56.1→56.1 | 0.2→0.2 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 12.78→20.89 | 8.5→29.9 | 0.1→0.3 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 52.45→52.45 | 55.2→55.2 | 0.2→0.2 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.48→28.88 | 94.2→45.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 78.61→64.63 | 83.5→64.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 23.82→20.32 | 31.0→26.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 60.85→48.03 | 79.0→57.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.50→31.50 | 36.9→36.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 55.64→55.64 | 65.2→65.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 21.41→28.93 | 9.1→33.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 48.13→48.13 | 65.1→65.1 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 50.62→37.23 | 130.5→91.8 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 65.55→54.49 | 114.0→93.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 25.90→31.03 | 56.6→70.7 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 44.44→36.74 | 98.2→78.1 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 31.81→31.81 | 73.9→73.9 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 43.07→43.07 | 70.9→70.9 | 0.0→0.0 |
| human_reaction | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 17.45→31.60 | 31.9→75.7 | 0.1→0.5 |
| human_reaction | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 30.49→30.49 | 60.3→60.3 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 33.15→33.15 | 90.0→90.0 | 0.1→0.1 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 46.61→46.61 | 74.3→74.3 | 0.3→0.3 |
| human_reaction | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 17.26→26.63 | 30.3→64.8 | 0.1→0.4 |
| human_reaction | D5 | class_machine_aa/boss | 24 | 1.000→1.000 | 34.96→34.96 | 67.2→67.2 | 0.2→0.2 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 56.93→34.76 | 125.5→85.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 82.03→61.39 | 137.3→95.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 26.21→23.32 | 59.8→54.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/boss | 24 | 1.000→1.000 | 55.72→38.15 | 109.9→74.5 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 36.80→36.80 | 80.6→80.6 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 59.78→59.78 | 88.9→88.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 25.30→32.98 | 54.4→77.7 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 47.62→47.62 | 85.7→85.7 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_grenade_aa, class_machine, class_shotgun_aa, class_grenade, class_shotgun, class_rifle_aa, class_machine_aa, class_handgun, class_rifle
- human_reaction: Spearman vs default 0.15; order class_rifle_aa, class_machine_aa, class_handgun_aa, class_grenade_aa, class_handgun, class_machine, class_shotgun_aa, class_grenade, class_rifle, class_shotgun
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, human_reaction +0.000

