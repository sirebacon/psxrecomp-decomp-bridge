# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.65→25.84 | 58.7→57.3 | 8.2→9.2 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 19.90→22.05 | 25.5→27.3 | 6.9→8.2 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 55.99→50.81 | 277.6→255.4 | 16.3→15.7 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 1.000→1.000 | 27.94→27.94 | 35.0→35.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 72.35→72.35 | 385.2→385.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 15.96→23.79 | 12.4→17.6 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 53.15→53.15 | 246.1→246.1 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 22.71→22.71 | 32.8→32.8 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 55.51→55.51 | 256.3→256.3 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 12.22→18.46 | 12.3→23.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 33.80→33.80 | 165.8→165.8 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 1.000→1.000 | 21.08→21.08 | 34.4→34.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 60.61→60.61 | 298.0→298.0 | 0.4→0.4 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 13.52→17.50 | 18.7→26.1 | 0.0→0.1 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 39.27→39.27 | 158.3→158.3 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 1.000→1.000 | 30.53→25.19 | 41.6→29.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 82.91→53.68 | 435.0→302.8 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 15.27→19.76 | 16.6→19.5 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 50.30→38.11 | 276.3→230.5 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_machine_aa, class_handgun_aa, class_rifle_aa, class_machine, class_handgun, class_grenade_aa, class_rifle, class_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

