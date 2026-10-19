# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.991→0.994 (+0.003, [+0.000, +0.006]) | 14.83→13.75 | 69.6→69.9 | 6.5→6.1 | 0.0→0.0 | 0.009→0.006 | 0.00 | 0.25 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.62→9.88 | 6.6→4.9 | 4.7→4.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.927→0.949 (+0.022, [+0.000, +0.044]) | 44.65→41.16 | 515.0→529.7 | 19.7→18.3 | 0.0→0.0 | 0.073→0.051 | 0.00 | 0.53 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.67→14.05 | 9.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.897→0.949 | 58.07→52.73 | 727.8→663.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 12.16→11.64 | 7.5→5.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.949→0.974 | 35.44→32.31 | 399.4→391.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.10→4.41 | 1.3→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 0.974→0.974 | 33.33→22.15 | 351.9→186.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.47→14.68 | 8.7→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 0.949→0.974 | 38.72→41.57 | 402.8→546.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 5.98→5.43 | 0.8→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 0.974→0.949 | 26.84→29.95 | 238.8→411.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 7.62→6.28 | 11.4→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 63.95→55.37 | 885.4→885.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.30→12.66 | 6.8→5.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.949→0.949 | 56.23→54.03 | 598.5→623.6 | 0.1→0.1 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_rifle_aa, class_shotgun, class_grenade, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.003

