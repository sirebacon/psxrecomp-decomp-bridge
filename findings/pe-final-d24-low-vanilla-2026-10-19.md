# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 0.996→0.998 (+0.002, [-0.002, +0.007]) | 29.32→28.20 | 75.1→69.5 | 9.7→9.6 | 0.1→0.1 | 0.004→0.001 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 0.995→0.997 (+0.003, [-0.003, +0.008]) | 23.05→22.47 | 32.8→30.2 | 8.2→8.2 | 0.1→0.1 | 0.005→0.001 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 70.71→66.03 | 354.2→328.7 | 19.5→19.2 | 0.6→0.5 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 0.980→1.000 | 31.27→29.81 | 45.2→38.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 88.63→84.37 | 425.7→435.0 | 0.6→0.6 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 17.35→17.66 | 15.3→14.9 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 65.02→67.01 | 301.4→324.2 | 0.8→0.9 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 24.57→24.13 | 37.2→36.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 72.94→64.06 | 369.3→313.5 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 13.64→13.62 | 17.7→16.9 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 44.43→38.29 | 226.2→168.5 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 0.990→0.990 | 27.10→26.30 | 44.2→41.1 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 75.51→69.74 | 371.5→321.1 | 0.9→0.9 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 16.28→16.24 | 25.0→23.5 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 61.24→52.77 | 323.5→247.9 | 1.1→0.9 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 0.990→0.990 | 36.78→34.62 | 57.7→50.6 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 97.18→92.28 | 492.3→485.8 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 17.40→17.38 | 19.9→19.9 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 60.72→59.73 | 323.9→333.6 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine_aa, class_rifle_aa, class_grenade_aa, class_handgun, class_grenade, class_machine, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.002

