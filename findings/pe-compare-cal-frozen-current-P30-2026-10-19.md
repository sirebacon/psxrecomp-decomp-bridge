# Rule comparison: CURRENT → exp:AAo_30|cfg:@G3A3.power+45,@M203_4.power+20 on CURRENT (calibrated model)

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.09→35.09 | 46.7→46.7 | 9.0→9.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.12 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 29.06→29.06 | 39.7→39.7 | 8.9→8.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 42.62→42.62 | 55.4→55.4 | 9.1→9.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | Disc2 | ALL | 0.998→0.998 (+0.000, [+0.000, +0.000]) | 11.02→12.35 | 37.9→39.6 | 6.7→10.6 | 0.0→0.0 | 0.002→0.002 | 0.00 | 0.25 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 8.32→9.83 | 2.4→4.3 | 4.9→9.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.986→0.986 (+0.000, [+0.000, +0.000]) | 30.13→30.17 | 288.8→289.0 | 19.2→19.2 | 0.0→0.0 | 0.014→0.014 | 0.00 | 0.54 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | C/ord | 20 | 1.000→1.000 | 28.62→28.62 | 33.0→33.0 | 0.0→0.0 |
| logged_player_serial | D5 | C/boss | 16 | 1.000→1.000 | 39.86→39.86 | 60.0→60.0 | 0.0→0.0 |
| logged_player_serial | D5 | D/ord | 20 | 1.000→1.000 | 29.45→29.45 | 35.0→35.0 | 0.0→0.0 |
| logged_player_serial | D5 | D/boss | 16 | 1.000→1.000 | 51.59→51.59 | 57.0→57.0 | 0.0→0.0 |
| logged_player_serial | D5 | G/ord | 20 | 1.000→1.000 | 26.15→26.15 | 40.6→40.6 | 0.0→0.0 |
| logged_player_serial | D5 | G/boss | 16 | 1.000→1.000 | 30.20→30.20 | 51.6→51.6 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 28.62→28.62 | 33.0→33.0 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 39.86→39.86 | 60.0→60.0 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 29.42→29.42 | 46.8→46.8 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 44.13→44.13 | 52.2→52.2 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 26.76→26.76 | 36.9→36.9 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 40.90→40.90 | 43.3→43.3 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 34.80→34.80 | 59.1→59.1 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 54.59→54.59 | 58.8→58.8 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 28.62→28.62 | 33.0→33.0 | 0.0→0.0 |
| logged_player_serial | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 39.86→39.86 | 60.0→60.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | C/ord | 184 | 1.000→1.000 | 9.91→9.91 | 3.7→3.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | C/boss | 26 | 1.000→1.000 | 27.72→27.72 | 268.2→268.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | D/ord | 184 | 1.000→1.000 | 4.73→10.78 | 0.5→7.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | D/boss | 26 | 1.000→1.000 | 25.68→25.68 | 197.7→197.7 | 0.0→0.0 |
| logged_player_serial | Disc2 | G/ord | 184 | 1.000→1.000 | 9.37→9.37 | 3.4→3.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | G/boss | 26 | 1.000→1.000 | 28.84→28.84 | 316.8→316.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 9.59→9.59 | 2.1→2.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_grenade/boss | 26 | 0.962→0.962 | 43.52→43.52 | 460.2→460.2 | 0.1→0.1 |
| logged_player_serial | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 9.40→9.40 | 4.3→4.3 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_handgun/boss | 26 | 0.962→0.962 | 35.27→35.27 | 381.8→381.8 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 3.33→9.41 | 0.0→8.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_machine/boss | 26 | 1.000→1.000 | 18.26→18.58 | 196.0→197.6 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 9.91→9.91 | 3.5→3.5 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_rifle/boss | 26 | 1.000→1.000 | 28.28→28.28 | 266.9→266.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 10.30→10.30 | 2.0→2.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | controlled_shotgun/boss | 26 | 0.962→0.962 | 33.46→33.46 | 223.0→223.0 | 0.1→0.1 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order G, controlled_machine, C, controlled_grenade, controlled_shotgun, controlled_handgun, D, controlled_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order controlled_machine, G, C, controlled_rifle, D, controlled_handgun, controlled_shotgun, controlled_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000

