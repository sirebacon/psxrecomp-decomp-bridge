# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.975→0.984 (+0.010, [+0.000, +0.022]) | 15.38→12.63 | 120.9→107.0 | 1.8→1.8 | 0.0→0.0 | 0.025→0.016 | 0.00 | 0.24 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 7.93→6.55 | 11.6→7.7 | 1.5→1.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.795→0.872 (+0.077, [+0.000, +0.154]) | 68.12→55.63 | 894.4→809.6 | 4.2→4.6 | 0.1→0.1 | 0.205→0.128 | 0.00 | 0.39 |
| human_reaction | Disc2 | ALL | 0.959→0.981 (+0.022, [+0.006, +0.038]) | 18.15→16.26 | 144.7→148.2 | 1.7→1.8 | 0.0→0.0 | 0.041→0.019 | 0.00 | 0.23 |
| human_reaction | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.11→8.79 | 15.1→11.1 | 1.5→1.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | BOSS | 0.667→0.846 (+0.179, [+0.077, +0.308]) | 75.05→69.13 | 1062.0→1117.9 | 3.5→4.3 | 0.0→0.0 | 0.333→0.154 | 0.00 | 0.38 |
| far_player | Disc2 | ALL | 0.975→0.984 (+0.010, [+0.000, +0.022]) | 13.02→11.19 | 105.4→106.3 | 1.8→1.9 | 0.0→0.0 | 0.025→0.016 | 0.00 | 0.26 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 6.89→5.60 | 11.1→7.4 | 1.5→1.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | BOSS | 0.795→0.872 (+0.077, [+0.000, +0.154]) | 56.45→50.76 | 772.7→806.3 | 4.3→4.8 | 0.1→0.1 | 0.205→0.128 | 0.00 | 0.44 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 7.93→6.55 | 11.6→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 68.12→55.63 | 894.4→809.6 | 0.1→0.1 |
| human_reaction | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 10.11→8.79 | 15.1→11.1 | 0.0→0.0 |
| human_reaction | Disc2 | class_rocket/boss | 39 | 0.667→0.846 | 75.05→69.13 | 1062.0→1117.9 | 0.0→0.0 |
| far_player | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 6.89→5.60 | 11.1→7.4 | 0.0→0.0 |
| far_player | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 56.45→50.76 | 772.7→806.3 | 0.1→0.1 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default n/a; order class_rocket
- human_reaction: Spearman vs default n/a; order class_rocket
- far_player: Spearman vs default n/a; order class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.010, human_reaction +0.022, far_player +0.010

