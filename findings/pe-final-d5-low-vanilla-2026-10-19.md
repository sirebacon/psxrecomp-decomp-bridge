# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.944→0.993 (+0.048, [+0.030, +0.067]) | 47.53→38.17 | 79.1→50.3 | 14.1→11.6 | 0.1→0.0 | 0.007→0.000 | 0.00 | 0.15 |
| logged_player_serial | D5 | ORDINARY | 0.913→1.000 (+0.087, [+0.057, +0.120]) | 35.61→26.71 | 59.1→37.6 | 14.1→11.2 | 0.1→0.0 | 0.013→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.983→0.983 (+0.000, [+0.000, +0.000]) | 62.44→52.50 | 104.2→66.1 | 14.1→12.1 | 0.1→0.1 | 0.000→0.000 | 0.00 | 0.23 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 0.400→1.000 | 77.69→39.34 | 173.9→72.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 104.46→56.99 | 254.7→82.1 | 0.2→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 0.733→1.000 | 66.78→22.53 | 123.1→21.6 | 0.7→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 83.20→42.61 | 248.2→72.5 | 0.4→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.66→27.66 | 44.8→44.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 0.958→0.958 | 57.51→56.87 | 59.3→58.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 13.07→13.07 | 7.0→7.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 31.66→31.66 | 44.4→44.4 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 29.55→26.49 | 60.0→50.1 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 45.23→41.22 | 63.6→56.1 | 0.2→0.2 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 15.94→12.78 | 10.2→8.5 | 0.1→0.1 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 55.20→52.45 | 64.7→55.2 | 0.3→0.2 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.66→48.48 | 94.5→94.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→0.958 | 80.65→78.61 | 90.8→83.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 23.82→23.82 | 31.0→31.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→0.958 | 62.71→60.85 | 86.0→79.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.50→31.50 | 36.9→36.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 55.64→55.64 | 65.2→65.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 21.41→21.41 | 9.1→9.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 48.13→48.13 | 65.1→65.1 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_grenade_aa, class_machine, class_shotgun_aa, class_shotgun, class_grenade, class_machine_aa, class_rifle_aa, class_handgun, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.048

