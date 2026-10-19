# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.950→0.994 (+0.044, [+0.028, +0.065]) | 43.06→33.61 | 73.4→43.4 | 12.4→10.1 | 0.0→0.0 | 0.006→0.000 | 0.00 | 0.14 |
| logged_player_serial | D5 | ORDINARY | 0.920→1.000 (+0.080, [+0.050, +0.110]) | 32.73→23.33 | 54.6→30.3 | 12.3→9.6 | 0.0→0.0 | 0.010→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.988 (+0.000, [+0.000, +0.000]) | 55.98→46.47 | 96.9→59.9 | 12.4→10.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.22 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 0.400→1.000 | 76.86→31.66 | 171.9→47.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 96.40→50.64 | 248.3→68.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 0.800→1.000 | 63.82→17.18 | 116.6→7.1 | 0.3→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 75.93→36.53 | 229.7→60.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.45→25.45 | 39.3→39.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 42.24→41.61 | 55.6→54.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.13→12.13 | 5.8→5.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 30.04→30.04 | 42.2→42.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 26.19→24.17 | 49.4→40.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 39.81→35.36 | 50.6→48.0 | 0.1→0.0 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 11.88→11.92 | 7.0→6.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 52.67→50.78 | 55.5→49.5 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.85→45.68 | 90.4→90.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 74.64→73.08 | 82.1→76.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 22.02→22.02 | 25.9→25.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 55.69→54.31 | 75.7→70.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.43→26.43 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 50.23→50.23 | 64.8→64.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 16.66→16.66 | 7.0→7.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 42.10→42.10 | 64.1→64.1 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_grenade_aa, class_shotgun_aa, class_machine, class_handgun, class_shotgun, class_grenade, class_machine_aa, class_rifle_aa, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.044

