# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player | D5 | ALL | 0.978→0.996 (+0.019, [+0.004, +0.037]) | 37.69→32.75 | 48.5→41.3 | 11.9→11.3 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.34→29.40 | 59.5→49.9 | 12.0→11.2 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player | D5 | BOSS | 0.950→0.992 (+0.042, [+0.008, +0.083]) | 40.63→36.94 | 34.9→30.6 | 11.9→11.5 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| logged_player | Disc2 | ALL | 0.968→0.968 (+0.000, [+0.000, +0.000]) | 15.20→15.76 | 40.7→42.9 | 8.4→11.4 | 0.0→0.0 | 0.027→0.027 | 0.01 | 0.25 |
| logged_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 13.14→13.77 | 9.9→12.3 | 5.9→9.3 | 0.0→0.0 | 0.000→0.000 | 0.01 | 0.10 |
| logged_player | Disc2 | BOSS | 0.703→0.703 (+0.000, [+0.000, +0.000]) | 32.42→32.42 | 298.4→298.4 | 29.1→29.1 | 0.2→0.2 | 0.248→0.248 | 0.00 | 0.62 |
| default | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 27.52→23.86 | 46.6→35.5 | 11.5→10.9 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.16→20.43 | 50.0→36.3 | 11.0→10.3 | 0.2→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 31.72→28.14 | 42.3→34.5 | 12.1→11.5 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.957→0.957 (+0.000, [+0.000, +0.000]) | 9.08→9.54 | 48.5→51.7 | 8.2→11.4 | 0.0→0.0 | 0.039→0.039 | 0.01 | 0.28 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 7.63→8.14 | 11.5→15.1 | 5.9→9.5 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.10 |
| default | Disc2 | BOSS | 0.600→0.600 (+0.000, [+0.000, +0.000]) | 21.18→21.18 | 357.9→357.9 | 27.9→27.9 | 0.2→0.2 | 0.370→0.370 | 0.00 | 0.63 |
| far_player | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 31.31→27.27 | 45.0→35.4 | 13.8→13.0 | 0.4→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.97→22.63 | 53.4→40.1 | 13.0→12.2 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 36.74→33.06 | 34.4→29.7 | 14.7→14.1 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.950→0.950 (+0.000, [+0.000, +0.000]) | 10.14→10.64 | 51.4→54.9 | 9.7→13.4 | 0.0→0.0 | 0.047→0.047 | 0.01 | 0.28 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 8.50→9.06 | 12.9→16.8 | 6.9→11.1 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.11 |
| far_player | Disc2 | BOSS | 0.527→0.527 (+0.000, [+0.000, +0.000]) | 23.90→23.90 | 373.3→373.3 | 32.7→32.7 | 0.2→0.2 | 0.436→0.436 | 0.00 | 0.61 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 41.61→31.32 | 71.3→57.2 | 0.5→0.1 |
| logged_player | D5 | class_grenade/boss | 24 | 0.875→1.000 | 43.86→37.72 | 42.1→31.8 | 0.2→0.1 |
| logged_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 27.01→27.01 | 41.0→41.0 | 0.1→0.1 |
| logged_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 33.39→33.39 | 25.8→25.8 | 0.3→0.3 |
| logged_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 29.59→29.59 | 55.3→55.3 | 0.5→0.5 |
| logged_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 28.58→28.58 | 27.5→27.5 | 0.5→0.5 |
| logged_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 48.81→29.40 | 84.2→50.6 | 0.0→0.0 |
| logged_player | D5 | class_rifle/boss | 24 | 0.875→0.958 | 56.12→43.82 | 46.3→35.0 | 0.0→0.0 |
| logged_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 29.69→29.69 | 45.5→45.5 | 0.2→0.2 |
| logged_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 41.20→41.20 | 32.8→32.8 | 0.3→0.3 |
| logged_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 15.74→15.74 | 10.6→10.6 | 0.0→0.0 |
| logged_player | Disc2 | class_grenade/boss | 33 | 0.606→0.606 | 39.71→39.71 | 346.1→346.1 | 0.1→0.1 |
| logged_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 13.98→13.98 | 10.0→10.0 | 0.0→0.0 |
| logged_player | Disc2 | class_handgun/boss | 33 | 0.697→0.697 | 32.27→32.27 | 259.6→259.6 | 0.1→0.1 |
| logged_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.89→9.02 | 3.5→15.5 | 0.0→0.0 |
| logged_player | Disc2 | class_machine/boss | 33 | 0.818→0.818 | 22.35→22.35 | 267.1→267.1 | 0.1→0.1 |
| logged_player | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.94→15.94 | 12.3→12.3 | 0.0→0.0 |
| logged_player | Disc2 | class_rifle/boss | 33 | 0.758→0.758 | 29.80→29.80 | 270.2→270.2 | 0.1→0.1 |
| logged_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 14.15→14.15 | 13.3→13.3 | 0.0→0.0 |
| logged_player | Disc2 | class_shotgun/boss | 33 | 0.636→0.636 | 37.95→37.95 | 348.8→348.8 | 0.7→0.7 |
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 28.10→22.50 | 63.6→38.6 | 0.4→0.0 |
| default | D5 | class_grenade/boss | 24 | 1.000→1.000 | 35.17→29.60 | 51.3→40.4 | 0.2→0.1 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 18.67→18.67 | 33.5→33.5 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 22.19→22.19 | 26.9→26.9 | 0.3→0.3 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 16.72→16.72 | 39.2→39.2 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 21.83→21.83 | 23.0→23.0 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 34.72→21.66 | 81.7→38.3 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.958→1.000 | 47.20→34.91 | 64.8→36.5 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 22.61→22.61 | 31.9→31.9 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 32.19→32.19 | 45.6→45.6 | 0.4→0.4 |
| default | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 9.35→9.35 | 12.8→12.8 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 33 | 0.485→0.485 | 27.76→27.76 | 389.4→389.4 | 0.1→0.1 |
| default | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 7.66→7.66 | 12.0→12.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.697→0.697 | 20.10→20.10 | 322.0→322.0 | 0.2→0.2 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.22→5.77 | 2.7→21.0 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 33 | 0.788→0.788 | 13.72→13.72 | 275.2→275.2 | 0.1→0.1 |
| default | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 9.59→9.59 | 15.2→15.2 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.606→0.606 | 19.40→19.40 | 368.1→368.1 | 0.1→0.1 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 8.36→8.36 | 14.8→14.8 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.424→0.424 | 24.91→24.91 | 434.5→434.5 | 0.6→0.6 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.02→23.55 | 63.3→39.6 | 0.5→0.0 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 40.29→34.08 | 36.7→32.3 | 0.3→0.2 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 20.02→20.02 | 36.4→36.4 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 27.39→27.39 | 24.3→24.3 | 0.6→0.6 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 22.35→22.35 | 53.6→53.6 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 30.02→30.02 | 25.4→25.4 | 0.8→0.8 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 37.05→22.83 | 79.5→36.5 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 0.958→1.000 | 47.82→35.62 | 47.5→28.0 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 24.42→24.42 | 34.2→34.2 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 38.19→38.19 | 38.3→38.3 | 0.6→0.6 |
| far_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 9.95→9.95 | 15.2→15.2 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.424→0.424 | 28.82→28.82 | 382.4→382.4 | 0.1→0.1 |
| far_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 8.68→8.68 | 12.4→12.4 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.576→0.576 | 23.85→23.85 | 351.4→351.4 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.41→7.22 | 4.2→23.4 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 33 | 0.727→0.727 | 18.76→18.76 | 325.8→325.8 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 9.72→9.72 | 15.9→15.9 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.606→0.606 | 20.50→20.50 | 349.2→349.2 | 0.1→0.1 |
| far_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 9.71→9.71 | 17.1→17.1 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 27.56→27.56 | 457.9→457.9 | 0.6→0.6 |

## Build ranking stability across assumption sets

**D5**
- logged_player: Spearman vs default 1.00; order class_machine, class_handgun, class_grenade, class_shotgun, class_rifle
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_grenade, class_shotgun, class_rifle
- far_player: Spearman vs default 0.80; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- win-rate delta (proposal − baseline) by set: logged_player +0.019, default +0.004, far_player +0.004

**Disc2**
- logged_player: Spearman vs default 0.80; order class_machine, class_rifle, class_handgun, class_shotgun, class_grenade
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_grenade, class_shotgun
- far_player: Spearman vs default 0.90; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: logged_player +0.000, default +0.000, far_player +0.000

