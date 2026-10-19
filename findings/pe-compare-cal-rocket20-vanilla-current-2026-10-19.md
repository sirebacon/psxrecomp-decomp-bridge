# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.975→0.984 (+0.010, [+0.000, +0.022]) | 15.38→12.63 | 120.9→107.0 | 1.8→1.8 | 0.0→0.0 | 0.025→0.016 | 0.00 | 0.24 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 7.93→6.55 | 11.6→7.7 | 1.5→1.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.795→0.872 (+0.077, [+0.000, +0.154]) | 68.12→55.63 | 894.4→809.6 | 4.2→4.6 | 0.1→0.1 | 0.205→0.128 | 0.00 | 0.39 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 7.93→6.55 | 11.6→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 68.12→55.63 | 894.4→809.6 | 0.1→0.1 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default n/a; order class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.010

