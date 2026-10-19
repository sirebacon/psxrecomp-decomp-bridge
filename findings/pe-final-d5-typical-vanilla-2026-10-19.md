# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.946→0.994 (+0.048, [+0.030, +0.067]) | 44.77→35.75 | 76.5→48.4 | 13.2→11.0 | 0.1→0.0 | 0.007→0.000 | 0.00 | 0.14 |
| logged_player_serial | D5 | ORDINARY | 0.913→1.000 (+0.087, [+0.057, +0.120]) | 34.09→25.33 | 56.7→35.7 | 13.2→10.6 | 0.1→0.0 | 0.013→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.988 (+0.000, [+0.000, +0.000]) | 58.13→48.78 | 101.2→64.3 | 13.1→11.6 | 0.1→0.0 | 0.000→0.000 | 0.00 | 0.22 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 0.400→1.000 | 77.51→39.45 | 172.8→73.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 101.73→55.52 | 259.2→83.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 0.733→1.000 | 66.67→22.45 | 122.9→21.3 | 0.6→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 81.55→40.23 | 243.4→71.0 | 0.1→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.00→26.00 | 40.2→40.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 42.41→41.78 | 58.3→57.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.64→12.64 | 5.8→5.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.03→31.03 | 44.0→44.0 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 27.91→25.53 | 53.9→47.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 40.32→39.40 | 51.3→50.6 | 0.2→0.1 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 15.07→12.32 | 9.6→7.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 52.56→51.74 | 58.7→52.2 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 47.86→47.68 | 92.2→91.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 77.00→75.09 | 86.2→79.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 23.23→23.23 | 29.5→29.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 58.70→56.98 | 79.8→73.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.61→26.61 | 33.1→33.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 51.43→51.43 | 65.8→65.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 17.37→17.37 | 7.1→7.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 44.61→44.61 | 65.5→65.5 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_shotgun_aa, class_grenade_aa, class_machine, class_handgun, class_shotgun, class_grenade, class_machine_aa, class_rifle_aa, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.048

