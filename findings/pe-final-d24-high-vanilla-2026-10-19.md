# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | ALL | 0.997→1.000 (+0.003, [+0.000, +0.008]) | 25.55→24.65 | 64.3→58.7 | 8.2→8.2 | 0.0→0.0 | 0.003→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | ORDINARY | 0.996→1.000 (+0.004, [+0.000, +0.009]) | 20.32→19.90 | 27.1→25.5 | 6.9→6.9 | 0.0→0.0 | 0.004→0.000 | 0.00 | 0.00 |
| logged_player_serial | D2-4 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 60.07→55.99 | 309.5→277.6 | 16.5→16.3 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D2-4 | class_grenade/ord | 99 | 0.980→1.000 | 28.64→27.94 | 39.8→35.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade/boss | 15 | 1.000→1.000 | 77.47→72.35 | 401.0→385.2 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/ord | 99 | 1.000→1.000 | 15.74→15.96 | 12.8→12.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_grenade_aa/boss | 15 | 1.000→1.000 | 50.51→53.15 | 225.1→246.1 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_handgun/ord | 99 | 1.000→1.000 | 22.89→22.71 | 32.6→32.8 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun/boss | 15 | 1.000→1.000 | 63.94→55.51 | 335.9→256.3 | 0.1→0.1 |
| logged_player_serial | D2-4 | class_handgun_aa/ord | 99 | 1.000→1.000 | 12.22→12.22 | 12.3→12.3 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_handgun_aa/boss | 15 | 1.000→1.000 | 36.88→33.80 | 187.7→165.8 | 0.2→0.2 |
| logged_player_serial | D2-4 | class_machine/ord | 99 | 1.000→1.000 | 21.94→21.08 | 36.6→34.4 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine/boss | 15 | 1.000→1.000 | 66.93→60.61 | 351.3→298.0 | 0.4→0.4 |
| logged_player_serial | D2-4 | class_machine_aa/ord | 99 | 1.000→1.000 | 13.64→13.52 | 20.2→18.7 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_machine_aa/boss | 15 | 1.000→1.000 | 48.16→39.27 | 234.9→158.3 | 0.5→0.5 |
| logged_player_serial | D2-4 | class_rifle/ord | 99 | 0.990→1.000 | 32.21→30.53 | 46.2→41.6 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle/boss | 15 | 1.000→1.000 | 84.21→82.91 | 451.9→435.0 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/ord | 99 | 1.000→1.000 | 15.30→15.27 | 16.7→16.6 | 0.0→0.0 |
| logged_player_serial | D2-4 | class_rifle_aa/boss | 15 | 1.000→1.000 | 52.43→50.30 | 288.2→276.3 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D2-4**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine_aa, class_rifle_aa, class_grenade_aa, class_machine, class_handgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.003

