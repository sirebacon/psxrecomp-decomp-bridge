# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.926→0.993 (+0.067, [+0.041, +0.100]) | 55.30→45.36 | 96.9→64.3 | 13.5→11.4 | 0.5→0.3 | 0.011→0.000 | 0.00 | 0.11 |
| logged_player_serial | D5 | ORDINARY | 0.880→1.000 (+0.120, [+0.067, +0.180]) | 43.82→35.47 | 83.4→60.9 | 13.2→11.2 | 0.5→0.2 | 0.020→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.983→0.983 (+0.000, [+0.000, +0.000]) | 69.64→57.72 | 113.8→68.5 | 13.9→11.6 | 0.5→0.3 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | Disc2 | ALL | 0.990→0.996 (+0.006, [+0.003, +0.010]) | 17.42→16.17 | 77.7→71.4 | 9.3→8.6 | 0.0→0.0 | 0.010→0.004 | 0.00 | 0.28 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 12.64→11.94 | 7.5→6.0 | 6.5→6.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.923→0.969 (+0.046, [+0.021, +0.077]) | 51.26→46.11 | 574.0→534.6 | 29.3→27.1 | 0.2→0.2 | 0.077→0.031 | 0.00 | 0.62 |
| human_reaction | D5 | ALL | 0.915→1.000 (+0.085, [+0.056, +0.122]) | 62.86→50.57 | 143.7→100.6 | 13.8→11.9 | 0.4→0.3 | 0.030→0.000 | 0.00 | 0.13 |
| human_reaction | D5 | ORDINARY | 0.853→1.000 (+0.147, [+0.093, +0.207]) | 51.59→43.26 | 128.8→103.7 | 13.4→11.7 | 0.4→0.3 | 0.047→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 76.95→59.72 | 162.4→96.6 | 14.3→12.2 | 0.5→0.3 | 0.008→0.000 | 0.00 | 0.21 |
| human_reaction | Disc2 | ALL | 0.984→0.994 (+0.010, [+0.006, +0.016]) | 22.14→21.27 | 119.1→123.7 | 8.8→8.5 | 0.0→0.0 | 0.016→0.006 | 0.00 | 0.25 |
| human_reaction | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 16.00→15.29 | 16.6→14.5 | 6.3→5.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | BOSS | 0.872→0.954 (+0.082, [+0.046, +0.123]) | 65.61→63.59 | 844.4→896.8 | 26.0→27.1 | 0.2→0.3 | 0.128→0.046 | 0.00 | 0.56 |
| far_player | D5 | ALL | 0.933→1.000 (+0.067, [+0.041, +0.100]) | 50.19→41.32 | 92.8→66.4 | 15.7→13.5 | 0.6→0.4 | 0.004→0.000 | 0.00 | 0.14 |
| far_player | D5 | ORDINARY | 0.880→1.000 (+0.120, [+0.067, +0.180]) | 43.17→34.80 | 86.8→64.6 | 15.7→13.0 | 0.6→0.4 | 0.007→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 58.97→49.48 | 100.3→68.8 | 15.7→14.1 | 0.6→0.4 | 0.000→0.000 | 0.00 | 0.22 |
| far_player | Disc2 | ALL | 0.990→0.994 (+0.004, [+0.001, +0.008]) | 15.99→14.93 | 77.2→78.1 | 10.7→10.1 | 0.0→0.0 | 0.010→0.006 | 0.00 | 0.27 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 11.36→10.71 | 7.9→6.5 | 7.6→7.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | BOSS | 0.918→0.954 (+0.036, [+0.010, +0.067]) | 48.77→44.84 | 568.0→585.2 | 32.0→31.4 | 0.3→0.3 | 0.082→0.046 | 0.00 | 0.60 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 0.400→1.000 | 78.13→40.24 | 173.9→74.1 | 1.4→0.5 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 110.59→59.44 | 289.8→81.6 | 0.9→0.2 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.35→27.35 | 42.5→42.5 | 0.2→0.2 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 43.96→43.88 | 56.5→55.9 | 0.2→0.2 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 32.15→28.47 | 67.3→55.1 | 0.7→0.3 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 48.83→42.49 | 67.0→56.4 | 0.9→0.6 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.71→48.54 | 94.0→93.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 81.36→79.32 | 91.0→83.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 32.77→32.77 | 39.2→39.2 | 0.2→0.2 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 0.958→0.958 | 63.46→63.46 | 64.9→64.9 | 0.4→0.4 |
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 15.21→14.60 | 10.9→9.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.897→0.949 | 73.99→61.14 | 940.4→796.9 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 12.48→11.94 | 8.5→6.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.923→0.974 | 39.58→36.26 | 403.5→380.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.84→4.94 | 1.3→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 0.974→1.000 | 37.74→26.77 | 421.5→199.8 | 0.2→0.1 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.71→14.91 | 8.9→7.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 0.923→1.000 | 40.26→47.30 | 411.2→662.1 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.96→13.33 | 8.1→6.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.897→0.923 | 64.74→59.10 | 693.3→633.6 | 0.8→0.9 |
| human_reaction | D5 | class_grenade/ord | 30 | 0.367→1.000 | 83.00→51.39 | 226.5→131.6 | 0.9→0.5 |
| human_reaction | D5 | class_grenade/boss | 24 | 0.958→1.000 | 125.29→65.52 | 367.7→114.7 | 0.9→0.2 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 31.97→31.83 | 73.5→73.5 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 44.77→43.55 | 73.2→72.1 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 0.967→1.000 | 46.50→38.50 | 130.4→104.4 | 0.8→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 55.00→47.63 | 77.2→69.1 | 0.8→0.8 |
| human_reaction | D5 | class_rifle/ord | 30 | 0.933→1.000 | 58.54→56.65 | 130.2→125.9 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 95.88→82.27 | 194.5→140.4 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 37.91→37.91 | 83.2→83.2 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 63.79→59.62 | 99.3→86.9 | 0.4→0.4 |
| human_reaction | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 19.12→18.53 | 21.4→20.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 39 | 0.846→0.923 | 86.93→78.72 | 1168.2→1159.7 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 16.30→15.85 | 17.3→15.4 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 39 | 0.872→0.923 | 60.73→60.35 | 843.9→895.7 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 7.37→6.49 | 5.2→2.7 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 39 | 0.897→0.974 | 44.06→39.50 | 609.7→575.0 | 0.1→0.1 |
| human_reaction | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 19.77→18.87 | 21.0→18.9 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 39 | 0.872→0.974 | 58.49→56.58 | 769.4→813.9 | 0.1→0.1 |
| human_reaction | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 17.41→16.69 | 17.8→15.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 39 | 0.872→0.974 | 77.82→82.78 | 830.9→1039.8 | 0.7→0.9 |
| far_player | D5 | class_grenade/ord | 30 | 0.400→1.000 | 75.58→39.21 | 172.2→72.3 | 1.5→0.5 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 91.54→50.48 | 216.4→76.9 | 1.1→0.2 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.57→25.57 | 46.3→46.3 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 37.69→36.90 | 52.5→52.8 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 37.84→32.88 | 81.9→71.5 | 1.0→0.8 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 49.21→46.45 | 70.6→64.3 | 1.0→1.0 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.88→45.37 | 90.8→90.0 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 1.000→1.000 | 63.83→61.32 | 95.1→83.0 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 30.98→30.98 | 42.8→42.8 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 52.58→52.24 | 66.8→66.8 | 0.6→0.6 |
| far_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 13.07→12.58 | 11.4→10.1 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 39 | 0.872→0.923 | 60.93→60.27 | 809.9→896.4 | 0.1→0.2 |
| far_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 10.55→10.09 | 8.6→7.2 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 39 | 0.949→0.974 | 47.22→38.02 | 613.8→531.0 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 6.68→5.83 | 3.0→1.7 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 39 | 0.949→0.974 | 36.95→30.02 | 397.8→334.7 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 13.20→12.47 | 8.7→7.2 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 39 | 0.949→0.974 | 41.19→37.33 | 467.4→551.8 | 0.1→0.1 |
| far_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.30→12.54 | 7.6→6.1 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 39 | 0.872→0.923 | 57.54→58.54 | 550.9→612.3 | 0.8→0.9 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_shotgun, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- far_player: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.067, human_reaction +0.085, far_player +0.067

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- human_reaction: Spearman vs default 0.70; order class_machine, class_rifle, class_shotgun, class_handgun, class_grenade
- far_player: Spearman vs default 0.80; order class_machine, class_handgun, class_rifle, class_shotgun, class_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.006, human_reaction +0.010, far_player +0.004

