# Rule comparison: CURRENT → exp:AAo_30|cfg:@G3A3.power+45,@M203_4.power+20 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 45.36→40.29 | 64.3→53.3 | 11.4→10.8 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.14 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.47→29.82 | 60.9→45.9 | 11.2→10.5 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.983→0.983 (+0.000, [+0.000, +0.000]) | 57.72→53.37 | 68.5→62.4 | 11.6→11.1 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.21 |
| logged_player_serial | Disc2 | ALL | 0.996→0.996 (+0.000, [+0.000, +0.000]) | 16.18→17.52 | 71.6→73.5 | 8.6→14.5 | 0.0→0.0 | 0.004→0.004 | 0.00 | 0.27 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 11.94→13.47 | 6.0→8.1 | 6.0→12.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.969→0.969 (+0.000, [+0.000, +0.000]) | 46.16→46.20 | 536.0→535.7 | 27.1→27.1 | 0.2→0.2 | 0.031→0.031 | 0.00 | 0.62 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 50.57→43.85 | 100.6→86.0 | 11.9→11.3 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.14 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 43.26→36.11 | 103.7→88.0 | 11.7→11.1 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 59.72→53.52 | 96.6→83.6 | 12.2→11.6 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.22 |
| human_reaction | Disc2 | ALL | 0.994→0.994 (-0.001, [-0.002, +0.000]) | 21.30→22.72 | 123.9→126.7 | 8.5→14.3 | 0.0→0.0 | 0.006→0.006 | 0.00 | 0.26 |
| human_reaction | Disc2 | ORDINARY | 1.000→0.999 (-0.001, [-0.002, +0.000]) | 15.29→16.98 | 14.5→18.3 | 5.9→12.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | BOSS | 0.954→0.954 (+0.000, [+0.000, +0.000]) | 63.86→63.32 | 898.3→893.8 | 27.2→27.1 | 0.3→0.3 | 0.046→0.046 | 0.00 | 0.57 |
| far_player | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 41.32→36.13 | 66.4→54.7 | 13.5→12.8 | 0.4→0.3 | 0.000→0.000 | 0.00 | 0.17 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 34.80→28.99 | 64.6→50.4 | 13.0→12.2 | 0.4→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 49.48→45.05 | 68.8→60.2 | 14.1→13.6 | 0.4→0.4 | 0.000→0.000 | 0.00 | 0.24 |
| far_player | Disc2 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 14.93→16.34 | 78.4→80.0 | 10.1→16.9 | 0.0→0.0 | 0.006→0.006 | 0.00 | 0.28 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.71→12.30 | 6.5→8.6 | 7.1→14.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | BOSS | 0.954→0.954 (+0.000, [+0.000, +0.000]) | 44.87→44.89 | 587.6→585.4 | 31.2→31.4 | 0.3→0.3 | 0.046→0.046 | 0.00 | 0.61 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.24→31.82 | 74.1→48.3 | 0.5→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 59.44→51.97 | 81.6→70.5 | 0.2→0.1 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.35→27.35 | 42.5→42.5 | 0.2→0.2 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 43.88→43.88 | 55.9→55.9 | 0.2→0.2 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 55.1→55.1 | 0.3→0.3 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 42.49→42.49 | 56.4→56.4 | 0.6→0.6 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.54→28.66 | 93.7→44.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 79.32→65.06 | 83.6→64.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 32.77→32.77 | 39.2→39.2 | 0.2→0.2 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 0.958→0.958 | 63.46→63.46 | 64.9→64.9 | 0.4→0.4 |
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.60→14.60 | 9.2→9.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.949→0.949 | 61.27→61.14 | 804.2→796.9 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 11.94→11.94 | 6.1→6.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.974→0.974 | 35.94→36.26 | 374.7→380.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.94→12.57 | 0.4→11.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 1.000→1.000 | 26.77→26.77 | 199.8→199.8 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 14.91→14.91 | 7.8→7.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 1.000→1.000 | 47.04→47.04 | 649.6→649.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.33→13.33 | 6.4→6.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 59.77→59.77 | 651.6→651.6 | 0.9→0.9 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 51.39→37.52 | 131.6→93.6 | 0.5→0.1 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 65.52→55.37 | 114.7→94.7 | 0.2→0.1 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 31.83→31.83 | 73.5→73.5 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 43.55→43.55 | 72.1→72.1 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 38.50→38.50 | 104.4→104.4 | 0.5→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 47.63→47.63 | 69.1→69.1 | 0.8→0.8 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 56.65→34.79 | 125.9→85.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 82.27→61.44 | 140.4→95.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 37.91→37.91 | 83.2→83.2 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 59.62→59.62 | 86.9→86.9 | 0.4→0.4 |
| human_reaction | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 18.53→18.53 | 20.3→20.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 39 | 0.923→0.923 | 78.72→78.72 | 1159.7→1159.7 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 15.85→15.85 | 15.4→15.4 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 39 | 0.923→0.923 | 60.35→60.36 | 895.7→904.1 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/ord | 276 | 1.000→0.996 | 6.49→14.95 | 2.7→21.9 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 39 | 0.974→0.974 | 39.34→39.50 | 563.7→575.0 | 0.1→0.1 |
| human_reaction | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 18.87→18.87 | 18.9→18.9 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 39 | 0.974→0.974 | 56.58→56.58 | 813.9→813.9 | 0.1→0.1 |
| human_reaction | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 16.69→16.69 | 15.2→15.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 39 | 0.974→0.974 | 84.29→81.44 | 1058.4→1016.2 | 0.9→0.9 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 39.21→29.09 | 72.3→48.6 | 0.5→0.0 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 50.48→42.13 | 76.9→55.4 | 0.2→0.1 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.57→25.57 | 46.3→46.3 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 36.90→36.90 | 52.8→52.8 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 32.88→32.88 | 71.5→71.5 | 0.8→0.8 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 46.45→46.45 | 64.3→64.3 | 1.0→1.0 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.37→26.45 | 90.0→42.6 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 1.000→1.000 | 61.32→47.51 | 83.0→61.6 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 30.98→30.98 | 42.8→42.8 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 52.24→52.24 | 66.8→66.8 | 0.6→0.6 |
| far_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 12.58→12.58 | 10.1→10.1 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 39 | 0.923→0.923 | 60.27→60.20 | 896.4→892.2 | 0.2→0.2 |
| far_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 10.09→10.09 | 7.2→7.2 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 39 | 0.974→0.974 | 38.07→37.81 | 538.3→521.3 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.83→13.82 | 1.7→12.3 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 39 | 0.974→0.974 | 29.54→30.02 | 324.4→334.7 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 12.47→12.47 | 7.2→7.2 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 39 | 0.974→0.974 | 37.33→37.33 | 551.8→551.8 | 0.1→0.1 |
| far_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 12.54→12.54 | 6.1→6.1 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 59.11→59.11 | 627.2→627.2 | 0.9→0.9 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- human_reaction: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- far_player: Spearman vs default 0.70; order class_handgun, class_grenade, class_rifle, class_machine, class_shotgun
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- human_reaction: Spearman vs default 0.20; order class_rifle, class_shotgun, class_machine, class_handgun, class_grenade
- far_player: Spearman vs default 0.50; order class_handgun, class_rifle, class_machine, class_shotgun, class_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, human_reaction -0.001, far_player +0.000

