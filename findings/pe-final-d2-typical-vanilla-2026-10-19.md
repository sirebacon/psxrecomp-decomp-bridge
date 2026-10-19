# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 0.992→0.995 (+0.002, [+0.000, +0.005]) | 15.32→14.07 | 72.8→71.1 | 7.0→6.5 | 0.0→0.0 | 0.008→0.005 | 0.00 | 0.26 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 10.73→9.97 | 6.7→5.0 | 4.9→4.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.938→0.956 (+0.018, [-0.004, +0.040]) | 47.79→43.10 | 540.5→538.9 | 21.8→19.9 | 0.0→0.0 | 0.062→0.044 | 0.00 | 0.54 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.86→14.24 | 10.2→8.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 39 | 0.949→0.923 | 65.67→55.18 | 793.5→695.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 12.25→11.73 | 7.7→5.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 39 | 0.974→0.974 | 39.36→35.38 | 440.2→418.9 | 0.1→0.0 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.36→4.55 | 1.1→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 39 | 1.000→1.000 | 35.60→26.06 | 379.2→255.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.54→14.72 | 8.8→7.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 39 | 0.949→1.000 | 41.16→43.54 | 434.3→556.6 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/ord | 276 | 1.000→1.000 | 6.04→5.48 | 0.8→0.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle_aa/boss | 39 | 0.974→1.000 | 27.88→33.45 | 233.7→434.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/ord | 276 | 1.000→1.000 | 7.62→6.28 | 11.4→7.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rocket/boss | 39 | 0.795→0.872 | 66.09→54.17 | 888.7→809.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.41→12.78 | 7.1→5.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 39 | 0.923→0.923 | 58.79→53.93 | 613.7→602.5 | 0.2→0.2 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle_aa, class_rifle, class_handgun, class_shotgun, class_grenade, class_rocket
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.002

