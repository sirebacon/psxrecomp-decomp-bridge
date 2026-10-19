# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 14.40→15.12 | 72.9→73.9 | 6.8→8.8 | 0.0→0.0 | 0.006→0.006 | 0.00 | 0.28 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.12→10.91 | 5.2→5.6 | 4.8→7.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.952→0.952 (+0.000, [+0.000, +0.000]) | 44.69→44.92 | 551.6→557.9 | 20.9→21.0 | 0.1→0.1 | 0.048→0.048 | 0.00 | 0.58 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.58→14.58 | 9.2→9.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.949→0.949 | 60.16→60.16 | 772.2→772.2 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 11.79→11.79 | 5.8→5.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.949→0.949 | 33.08→33.08 | 331.6→331.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.79→7.75 | 0.4→1.6 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 1.000→1.000 | 26.48→26.48 | 227.0→227.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 14.73→14.73 | 7.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 1.000→1.000 | 46.14→46.14 | 633.5→633.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 5.49→8.07 | 0.4→1.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 0.974→0.974 | 34.81→35.33 | 475.2→486.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 6.36→6.36 | 7.5→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.872→0.872 | 55.85→55.85 | 814.3→814.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.07→13.07 | 5.5→5.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 56.27→57.36 | 607.3→640.7 | 0.4→0.4 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_rifle_aa, class_handgun, class_grenade, class_shotgun, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

