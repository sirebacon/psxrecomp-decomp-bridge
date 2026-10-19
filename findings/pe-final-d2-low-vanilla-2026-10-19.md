# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.990→0.994 (+0.004, [+0.001, +0.007]) | 15.68→14.43 | 75.5→73.9 | 7.3→6.8 | 0.0→0.0 | 0.010→0.006 | 0.00 | 0.27 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.89→10.12 | 6.9→5.2 | 5.1→4.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.919→0.952 (+0.033, [+0.011, +0.059]) | 49.55→44.95 | 560.8→559.7 | 22.8→21.0 | 0.1→0.1 | 0.081→0.048 | 0.00 | 0.54 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 15.19→14.58 | 10.9→9.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.897→0.949 | 70.70→60.16 | 894.6→772.2 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 12.31→11.79 | 7.9→5.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.923→0.949 | 37.66→33.08 | 382.3→331.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.59→4.79 | 1.3→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 1.000→1.000 | 37.11→26.48 | 386.3→227.0 | 0.2→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.55→14.73 | 8.9→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 0.923→1.000 | 41.08→46.40 | 439.0→645.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 6.05→5.49 | 0.8→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 0.974→0.974 | 29.32→35.33 | 249.6→486.1 | 0.1→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 7.83→6.36 | 11.5→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 67.99→55.85 | 894.4→814.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.71→13.07 | 7.3→5.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 62.96→57.36 | 679.0→640.7 | 0.4→0.4 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_rifle_aa, class_handgun, class_grenade, class_shotgun, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.004

