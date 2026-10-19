# Rule comparison: CURRENT → exp:AAo_40 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 13.74→14.42 | 69.3→70.2 | 6.1→7.9 | 0.0→0.0 | 0.006→0.006 | 0.00 | 0.27 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.88→10.66 | 4.9→5.8 | 4.4→6.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.949→0.949 (+0.000, [+0.000, +0.000]) | 41.10→41.06 | 525.4→525.9 | 18.3→18.3 | 0.0→0.0 | 0.051→0.051 | 0.00 | 0.57 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.05→14.05 | 7.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.949→0.949 | 52.73→52.73 | 663.2→663.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 11.64→11.64 | 5.5→5.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.974→0.974 | 32.31→32.31 | 391.0→391.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.41→7.00 | 0.4→3.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 0.974→0.974 | 22.48→22.15 | 188.7→186.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 14.68→14.68 | 7.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 0.974→0.974 | 41.29→41.29 | 534.9→534.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 5.43→8.31 | 0.4→4.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 0.949→0.949 | 29.86→29.95 | 405.9→411.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 6.28→6.28 | 7.5→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.872→0.872 | 55.37→55.37 | 885.7→885.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 12.66→12.66 | 5.1→5.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.949→0.949 | 53.64→53.64 | 608.6→608.6 | 0.1→0.1 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_rifle_aa, class_shotgun, class_grenade, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

