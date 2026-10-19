# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | ALL | 0.981→1.000 (+0.019, [+0.004, +0.037]) | 38.25→33.31 | 53.5→42.0 | 11.4→10.8 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.41→29.82 | 60.2→45.3 | 11.2→10.5 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | D5 | BOSS | 0.958→1.000 (+0.042, [+0.008, +0.083]) | 41.80→37.68 | 45.0→37.8 | 11.7→11.2 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player_serial | Disc2 | ALL | 0.970→0.970 (+0.000, [+0.000, +0.000]) | 14.64→15.30 | 35.4→36.0 | 8.8→11.7 | 0.0→0.0 | 0.022→0.022 | 0.01 | 0.13 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 11.96→12.69 | 7.0→7.7 | 6.0→9.2 | 0.0→0.0 | 0.000→0.000 | 0.01 | 0.00 |
| logged_player_serial | Disc2 | BOSS | 0.715→0.715 (+0.000, [+0.000, +0.000]) | 37.13→37.15 | 273.0→273.0 | 32.0→32.0 | 0.2→0.2 | 0.206→0.206 | 0.00 | 0.40 |
| default | D5 | ALL | 0.989→1.000 (+0.011, [+0.000, +0.026]) | 34.04→29.56 | 53.5→42.0 | 11.5→10.8 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 31.22→26.32 | 60.2→45.3 | 11.2→10.5 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.975→1.000 (+0.025, [+0.000, +0.058]) | 37.57→33.61 | 45.0→37.8 | 11.8→11.2 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.973→0.973 (+0.000, [+0.000, +0.000]) | 12.23→12.83 | 35.4→36.1 | 8.8→11.7 | 0.0→0.0 | 0.022→0.022 | 0.01 | 0.13 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.73→10.40 | 7.0→7.7 | 6.0→9.2 | 0.0→0.0 | 0.000→0.000 | 0.01 | 0.00 |
| default | Disc2 | BOSS | 0.745→0.745 (+0.000, [+0.000, +0.000]) | 33.07→33.08 | 273.5→273.5 | 32.3→32.3 | 0.2→0.2 | 0.206→0.206 | 0.00 | 0.40 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.30→31.82 | 73.9→47.6 | 0.5→0.0 |
| logged_player_serial | D5 | class_grenade/boss | 24 | 0.917→1.000 | 44.90→37.81 | 56.0→43.0 | 0.2→0.1 |
| logged_player_serial | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.35→27.35 | 41.8→41.8 | 0.2→0.2 |
| logged_player_serial | D5 | class_handgun/boss | 24 | 1.000→1.000 | 30.27→30.27 | 24.8→24.8 | 0.3→0.3 |
| logged_player_serial | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 54.6→54.6 | 0.3→0.3 |
| logged_player_serial | D5 | class_machine/boss | 24 | 1.000→1.000 | 31.97→31.97 | 29.9→29.9 | 0.6→0.6 |
| logged_player_serial | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.15→28.66 | 92.2→44.1 | 0.0→0.0 |
| logged_player_serial | D5 | class_rifle/boss | 24 | 0.875→1.000 | 58.56→45.06 | 66.2→42.9 | 0.0→0.0 |
| logged_player_serial | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 32.77→32.77 | 38.7→38.7 | 0.2→0.2 |
| logged_player_serial | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 43.30→43.30 | 48.2→48.2 | 0.3→0.3 |
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.65→14.65 | 11.0→11.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_grenade/boss | 33 | 0.576→0.576 | 40.51→40.59 | 354.7→354.6 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 11.93→11.93 | 7.2→7.2 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/boss | 33 | 0.697→0.697 | 34.26→34.26 | 269.1→269.1 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.94→8.60 | 0.4→4.1 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/boss | 33 | 0.909→0.909 | 27.38→27.38 | 183.7→183.7 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.01→15.01 | 9.6→9.6 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/boss | 33 | 0.727→0.727 | 34.93→34.93 | 259.8→259.8 | 0.1→0.1 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.25→13.25 | 6.6→6.6 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/boss | 33 | 0.667→0.667 | 48.58→48.58 | 297.6→297.6 | 0.8→0.8 |
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 35.70→28.25 | 73.9→47.6 | 0.5→0.0 |
| default | D5 | class_grenade/boss | 24 | 1.000→1.000 | 40.57→33.81 | 56.0→43.0 | 0.2→0.1 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 23.85→23.85 | 41.8→41.8 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 26.72→26.72 | 24.8→24.8 | 0.3→0.3 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 25.10→25.10 | 54.6→54.6 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 28.42→28.42 | 29.9→29.9 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 42.28→25.19 | 92.2→44.1 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.875→1.000 | 53.22→40.17 | 66.3→42.9 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 29.19→29.19 | 38.7→38.7 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 38.92→38.92 | 48.2→48.2 | 0.3→0.3 |
| default | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 12.00→12.00 | 11.0→11.0 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 33 | 0.576→0.576 | 36.11→36.16 | 354.7→354.6 | 0.1→0.1 |
| default | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 9.34→9.34 | 7.2→7.2 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.727→0.727 | 30.00→30.00 | 269.1→269.1 | 0.1→0.1 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.81→7.17 | 0.4→4.1 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 33 | 0.909→0.909 | 24.01→24.01 | 183.7→183.7 | 0.1→0.1 |
| default | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 12.43→12.43 | 9.6→9.6 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.818→0.818 | 30.96→30.96 | 259.8→259.8 | 0.1→0.1 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 11.09→11.09 | 6.6→6.6 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.697→0.697 | 44.25→44.25 | 300.1→300.1 | 0.8→0.8 |

## Build ranking stability across assumption sets

**D5**
- logged_player_serial: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- default: Spearman vs default 1.00; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.019, default +0.011

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_shotgun, class_grenade
- default: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_shotgun, class_grenade
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, default +0.000

