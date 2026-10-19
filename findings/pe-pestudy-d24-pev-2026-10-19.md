# Rule comparison: CURRENT → exp:PEv on CURRENT (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 1.000→0.993 (-0.007, [-0.016, +0.000]) | 32.20→33.69 | 76.9→83.8 | 8.3→8.3 | 0.0→0.0 | 0.000→0.007 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 1.000→0.992 (-0.008, [-0.019, +0.000]) | 26.45→27.41 | 37.2→39.5 | 7.0→7.0 | 0.0→0.0 | 0.000→0.008 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 70.19→75.20 | 339.2→376.2 | 16.3→16.5 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 66 | 1.000→0.985 | 28.35→28.87 | 34.8→36.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 10 | 1.000→1.000 | 76.65→81.82 | 364.6→395.6 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_handgun/ord | 66 | 1.000→1.000 | 23.02→23.31 | 33.6→33.8 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 10 | 1.000→1.000 | 55.34→62.64 | 239.6→309.8 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine/ord | 66 | 1.000→1.000 | 21.99→23.01 | 35.7→38.1 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine/boss | 10 | 1.000→1.000 | 60.81→67.32 | 297.4→328.9 | 0.6→0.5 |
| logged_player_serial | D2-4 | class_rifle/ord | 66 | 1.000→0.985 | 32.44→34.43 | 44.8→50.3 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 10 | 1.000→1.000 | 87.94→89.01 | 455.1→470.4 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial -0.007

