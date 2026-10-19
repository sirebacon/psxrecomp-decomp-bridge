# Rule comparison: VANILLA → CURRENT (mod) (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 37.61→35.09 | 48.1→46.7 | 10.0→9.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.12 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 33.05→29.06 | 40.6→39.7 | 10.6→8.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 43.32→42.62 | 57.5→55.4 | 9.3→9.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | Disc2 | ALL | 0.995→0.998 (+0.004, [+0.001, +0.007]) | 17.27→11.02 | 54.9→38.0 | 9.9→6.7 | 0.0→0.0 | 0.005→0.002 | 0.00 | 0.17 |
| logged_player_serial | Disc2 | ORDINARY | 0.999→1.000 (+0.001, [+0.000, +0.003]) | 14.04→8.32 | 7.9→2.4 | 8.0→4.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.962→0.986 (+0.024, [+0.005, +0.048]) | 40.13→30.14 | 387.2→289.4 | 23.2→19.2 | 0.1→0.0 | 0.038→0.014 | 0.00 | 0.50 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | C/ord | 20 | 1.000→1.000 | 39.28→28.62 | 35.4→33.0 | 0.1→0.0 |
| logged_player_serial | D5 | C/boss | 16 | 1.000→1.000 | 41.41→39.86 | 65.1→60.0 | 0.0→0.0 |
| logged_player_serial | D5 | D/ord | 20 | 1.000→1.000 | 29.45→29.45 | 35.0→35.0 | 0.0→0.0 |
| logged_player_serial | D5 | D/boss | 16 | 1.000→1.000 | 51.59→51.59 | 57.0→57.0 | 0.0→0.0 |
| logged_player_serial | D5 | G/ord | 20 | 1.000→1.000 | 26.15→26.15 | 40.6→40.6 | 0.0→0.0 |
| logged_player_serial | D5 | G/boss | 16 | 1.000→1.000 | 30.20→30.20 | 51.6→51.6 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 39.28→28.62 | 35.4→33.0 | 0.1→0.0 |
| logged_player_serial | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 41.41→39.86 | 65.1→60.0 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 29.42→29.42 | 46.8→46.8 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 44.13→44.13 | 52.2→52.2 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 26.76→26.76 | 36.9→36.9 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 40.90→40.90 | 43.3→43.3 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 34.80→34.80 | 59.1→59.1 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 55.47→54.59 | 60.9→58.8 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 39.28→28.62 | 35.4→33.0 | 0.1→0.0 |
| logged_player_serial | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 41.41→39.86 | 65.1→60.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | C/ord | 184 | 1.000→1.000 | 15.70→9.91 | 9.7→3.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | C/boss | 26 | 0.962→1.000 | 32.19→27.72 | 280.1→268.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | D/ord | 184 | 1.000→1.000 | 5.47→4.73 | 1.6→0.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | D/boss | 26 | 1.000→1.000 | 34.03→25.68 | 295.0→197.7 | 0.1→0.0 |
| logged_player_serial | Disc2 | G/ord | 184 | 1.000→1.000 | 14.64→9.37 | 8.3→3.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | G/boss | 26 | 0.962→1.000 | 35.67→28.93 | 333.1→320.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_grenade/ord | 184 | 0.995→1.000 | 18.46→9.59 | 9.3→2.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_grenade/boss | 26 | 0.962→0.962 | 57.17→43.52 | 546.8→460.2 | 0.2→0.1 |
| logged_player_serial | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 17.34→9.40 | 17.5→4.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_handgun/boss | 26 | 0.923→0.962 | 59.04→35.27 | 764.8→383.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 6.49→3.33 | 1.9→0.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_machine/boss | 26 | 0.962→1.000 | 24.82→18.26 | 242.2→196.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 15.77→9.91 | 8.5→3.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_rifle/boss | 26 | 0.962→1.000 | 32.85→28.28 | 286.0→266.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 18.48→10.30 | 6.8→2.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_shotgun/boss | 26 | 0.962→0.962 | 45.25→33.46 | 349.3→223.0 | 0.1→0.1 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order G, controlled_machine, C, controlled_grenade, controlled_shotgun, controlled_handgun, D, controlled_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order controlled_machine, D, G, C, controlled_rifle, controlled_handgun, controlled_shotgun, controlled_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.004

