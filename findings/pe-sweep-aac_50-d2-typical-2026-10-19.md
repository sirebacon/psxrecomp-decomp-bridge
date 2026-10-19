# Rule comparison: CURRENT → exp:AAc_50 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.995→0.995 (+0.000, [+0.000, +0.000]) | 14.04→16.47 | 70.2→71.8 | 6.5→11.6 | 0.0→0.0 | 0.005→0.005 | 0.00 | 0.28 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.97→12.71 | 5.0→6.0 | 4.6→10.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.956→0.956 (+0.000, [+0.000, +0.000]) | 42.87→43.06 | 531.6→537.2 | 19.8→19.9 | 0.0→0.0 | 0.044→0.044 | 0.00 | 0.58 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.24→14.24 | 8.1→8.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.923→0.923 | 55.18→55.18 | 695.3→695.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 11.73→11.73 | 5.7→5.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.974→0.974 | 35.38→35.38 | 418.9→418.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.55→11.44 | 0.4→2.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 1.000→1.000 | 26.06→26.06 | 255.5→255.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 14.72→14.72 | 7.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 1.000→1.000 | 43.26→43.26 | 544.2→544.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 5.48→17.79 | 0.4→4.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 1.000→1.000 | 33.36→33.45 | 428.7→434.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 6.28→6.28 | 7.5→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.872→0.872 | 54.17→54.17 | 809.5→809.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 12.78→12.78 | 5.3→5.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 52.65→53.93 | 569.0→602.5 | 0.2→0.2 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_rifle_aa, class_handgun, class_shotgun, class_grenade, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

