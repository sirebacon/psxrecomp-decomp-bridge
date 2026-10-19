# Rule comparison: CURRENT → exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15 on CURRENT (calibrated model)

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Calibrated model (pe-calibration-logged-v7-2026-10-19): every logged foe resolved from source data, contact damage, Parasite Energy and items with the generic policy; Disc2 boss absolute levels are pessimistic for the player (the log player used clubs / held fire), comparisons are paired.

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.994→0.998 (+0.004, [+0.000, +0.009]) | 33.61→33.48 | 43.4→43.7 | 10.1→11.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.18 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 23.33→25.27 | 30.3→34.5 | 9.6→12.2 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.988→0.996 (+0.008, [+0.000, +0.021]) | 46.47→43.75 | 59.9→55.2 | 10.7→10.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.25 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.55→35.23 | 69.6→72.2 | 10.6→11.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.17 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 28.09→30.10 | 62.1→72.0 | 9.9→12.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 44.88→41.64 | 79.0→72.4 | 11.4→11.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.26 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.66→30.88 | 47.7→47.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 1.000→1.000 | 50.64→47.65 | 68.8→58.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 17.18→27.69 | 7.1→34.6 | 0.0→0.0 |
| logged_player_serial | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 36.53→34.52 | 60.8→51.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 25.45→25.45 | 39.3→39.3 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 41.61→41.61 | 54.5→54.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 12.13→23.70 | 5.8→22.6 | 0.0→0.1 |
| logged_player_serial | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 30.04→30.04 | 42.2→42.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 24.17→24.17 | 40.0→40.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 35.36→35.36 | 48.0→48.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 11.92→20.65 | 6.9→28.7 | 0.0→0.1 |
| logged_player_serial | D5 | class_machine_aa/boss | 24 | 0.958→0.958 | 50.78→50.78 | 49.5→49.5 | 0.1→0.1 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 45.68→27.52 | 90.2→44.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.958→1.000 | 73.08→60.59 | 76.1→63.5 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 22.02→20.26 | 25.9→26.0 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle_aa/boss | 24 | 0.958→1.000 | 54.31→44.65 | 70.1→55.2 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 26.43→26.43 | 32.7→32.7 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 50.23→50.23 | 64.8→64.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 16.66→25.94 | 7.0→29.8 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 42.10→42.10 | 64.1→64.1 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 37.74→36.35 | 92.5→90.6 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 24 | 1.000→1.000 | 55.06→52.24 | 93.6→87.5 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/ord | 30 | 1.000→1.000 | 22.03→30.60 | 44.0→70.5 | 0.0→0.0 |
| human_reaction | D5 | class_grenade_aa/boss | 24 | 1.000→1.000 | 35.79→33.55 | 76.6→70.5 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 30.10→30.10 | 67.4→67.4 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 40.76→40.76 | 65.7→65.7 | 0.0→0.0 |
| human_reaction | D5 | class_handgun_aa/ord | 30 | 1.000→1.000 | 16.03→29.09 | 28.8→72.5 | 0.0→0.1 |
| human_reaction | D5 | class_handgun_aa/boss | 24 | 1.000→1.000 | 28.14→28.14 | 54.4→54.4 | 0.0→0.0 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 30.03→30.03 | 78.7→78.7 | 0.0→0.0 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 41.35→41.35 | 63.8→63.8 | 0.1→0.1 |
| human_reaction | D5 | class_machine_aa/ord | 30 | 1.000→1.000 | 14.39→25.39 | 20.7→60.7 | 0.0→0.1 |
| human_reaction | D5 | class_machine_aa/boss | 24 | 1.000→1.000 | 33.36→33.36 | 64.2→64.2 | 0.1→0.1 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 54.27→32.85 | 124.0→82.8 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 1.000→1.000 | 72.25→57.75 | 120.0→91.1 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/ord | 30 | 1.000→1.000 | 24.29→22.94 | 53.3→53.0 | 0.0→0.0 |
| human_reaction | D5 | class_rifle_aa/boss | 24 | 1.000→1.000 | 46.60→33.80 | 94.6→69.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.66→31.66 | 72.9→72.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 53.52→53.52 | 78.9→78.9 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/ord | 30 | 1.000→1.000 | 20.32→32.00 | 38.7→71.2 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun_aa/boss | 24 | 1.000→1.000 | 41.91→41.91 | 78.3→78.3 | 0.0→0.0 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun_aa, class_machine, class_grenade_aa, class_rifle_aa, class_handgun, class_shotgun_aa, class_shotgun, class_grenade, class_rifle, class_machine_aa
- human_reaction: Spearman vs default 0.52; order class_rifle_aa, class_handgun_aa, class_machine_aa, class_grenade_aa, class_handgun, class_machine, class_shotgun_aa, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.004, human_reaction +0.000

