# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.994→0.998 (+0.004, [+0.000, +0.009]) | 35.75→34.60 | 48.4→46.2 | 11.0→12.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 25.33→25.97 | 35.7→36.1 | 10.6→12.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.996 (+0.008, [+0.000, +0.021]) | 48.78→45.38 | 64.3→58.7 | 11.6→11.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.26 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 38.48→36.42 | 76.7→74.9 | 11.5→12.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.18 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 30.47→30.66 | 69.3→73.6 | 10.9→13.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 48.49→43.62 | 86.0→76.4 | 12.3→11.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.27 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.45→31.44 | 73.0→48.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.52→49.46 | 83.9→72.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 22.45→27.70 | 21.3→34.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 40.23→36.41 | 71.0→60.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.00→26.00 | 40.2→40.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.78→41.78 | 57.2→57.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.64→24.92 | 5.8→23.3 | 0.0→0.2 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.03→31.03 | 44.0→44.0 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 25.53→25.53 | 47.5→47.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 39.40→39.40 | 50.6→50.6 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 12.32→20.99 | 7.7→30.1 | 0.0→0.2 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 51.74→51.74 | 52.2→52.2 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 47.68→28.87 | 91.9→45.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→1.000 | 75.09→62.88 | 79.2→63.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 23.23→20.31 | 29.5→26.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→1.000 | 56.98→45.11 | 73.2→55.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.61→26.61 | 33.1→33.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 51.43→51.43 | 65.8→65.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 17.37→27.31 | 7.1→32.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 44.61→44.61 | 65.5→65.5 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 50.09→36.71 | 129.6→90.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 63.59→54.36 | 110.8→93.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 25.81→30.93 | 56.5→70.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 40.80→35.75 | 90.2→76.6 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 30.81→30.81 | 68.0→68.0 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 40.93→40.93 | 65.7→65.7 | 0.0→0.0 |
| human_reaction | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 16.59→29.97 | 29.8→73.5 | 0.0→0.2 |
| human_reaction | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 28.38→28.38 | 54.4→54.4 | 0.1→0.1 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 32.03→32.03 | 85.5→85.5 | 0.0→0.0 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 44.13→44.13 | 73.0→73.0 | 0.1→0.1 |
| human_reaction | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 16.24→26.13 | 28.3→62.9 | 0.0→0.3 |
| human_reaction | D5 | class_machine_aa/boss | 24 | 1.000→1.000 | 34.86→34.86 | 66.4→66.4 | 0.2→0.2 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 56.91→34.74 | 125.4→85.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 76.34→58.21 | 125.5→91.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 25.20→23.31 | 56.6→54.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/boss | 24 | 1.000→1.000 | 50.51→34.25 | 100.0→69.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 30.57→30.57 | 71.1→71.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 58.27→58.27 | 87.4→87.4 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 20.49→31.35 | 42.4→74.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 47.05→47.05 | 86.2→86.2 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_rifle_aa, class_grenade_aa, class_machine, class_handgun, class_shotgun_aa, class_shotgun, class_grenade, class_rifle, class_machine_aa
- human_reaction: Spearman vs default 0.64; order class_rifle_aa, class_handgun_aa, class_machine_aa, class_grenade_aa, class_handgun, class_machine, class_shotgun_aa, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.004, human_reaction +0.000

