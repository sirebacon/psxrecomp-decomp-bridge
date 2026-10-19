# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.985→1.000 (+0.015, [+0.004, +0.030]) | 27.76→24.14 | 56.0→43.2 | 11.5→10.8 | 0.3→0.2 | 0.015→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.16→20.43 | 58.8→43.1 | 11.0→10.3 | 0.2→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.967→1.000 (+0.033, [+0.008, +0.067]) | 32.25→28.78 | 52.4→43.3 | 12.0→11.5 | 0.3→0.3 | 0.033→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.943→0.943 (+0.000, [+0.000, +0.000]) | 8.74→9.18 | 68.2→72.3 | 7.9→11.0 | 0.0→0.0 | 0.057→0.057 | 0.24 | 0.30 |
| default | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 7.65→8.14 | 23.0→27.7 | 5.9→9.4 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.20 |
| default | Disc2 | BOSS | 0.521→0.521 (+0.000, [+0.000, +0.000]) | 17.85→17.85 | 445.7→445.7 | 24.5→24.5 | 0.1→0.1 | 0.479→0.479 | 0.55 | 0.70 |
| human_reaction | D5 | ALL | 0.970→0.989 (+0.019, [+0.004, +0.037]) | 38.85→34.42 | 88.7→76.4 | 12.0→11.5 | 0.3→0.2 | 0.015→0.011 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 0.993→1.000 (+0.007, [+0.000, +0.020]) | 34.98→29.87 | 102.0→86.1 | 11.7→11.1 | 0.3→0.2 | 0.007→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.942→0.975 (+0.033, [+0.008, +0.067]) | 43.68→40.10 | 72.0→64.3 | 12.4→11.9 | 0.3→0.3 | 0.025→0.025 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.913→0.912 (-0.001, [-0.002, +0.000]) | 13.95→14.56 | 90.2→95.9 | 7.4→10.7 | 0.0→0.0 | 0.087→0.087 | 0.18 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.977→0.976 (-0.001, [-0.002, +0.000]) | 13.05→13.73 | 41.6→48.0 | 5.9→9.6 | 0.0→0.0 | 0.023→0.024 | 0.03 | 0.15 |
| human_reaction | Disc2 | BOSS | 0.376→0.376 (+0.000, [+0.000, +0.000]) | 21.49→21.49 | 496.6→496.6 | 19.9→19.9 | 0.1→0.1 | 0.618→0.618 | 0.55 | 0.65 |
| far_player | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 31.78→27.83 | 53.3→42.3 | 13.8→13.1 | 0.4→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.97→22.63 | 60.7→45.6 | 13.0→12.2 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 37.80→34.32 | 44.0→38.2 | 14.8→14.2 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.936→0.936 (+0.000, [+0.000, +0.000]) | 9.64→10.13 | 69.9→74.3 | 9.0→12.7 | 0.0→0.0 | 0.063→0.063 | 0.27 | 0.30 |
| far_player | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 8.51→9.06 | 23.3→28.3 | 7.0→11.1 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.19 |
| far_player | Disc2 | BOSS | 0.455→0.455 (+0.000, [+0.000, +0.000]) | 19.05→19.05 | 459.2→459.2 | 26.0→26.0 | 0.2→0.2 | 0.539→0.539 | 0.54 | 0.71 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 28.10→22.50 | 77.6→48.2 | 0.4→0.0 |
| default | D5 | class_grenade/boss | 24 | 0.958→1.000 | 36.74→29.83 | 63.5→51.2 | 0.2→0.1 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 18.67→18.67 | 38.0→38.0 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 23.70→23.70 | 32.0→32.0 | 0.2→0.2 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 16.72→16.72 | 42.2→42.2 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 21.34→21.34 | 30.5→30.5 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 34.72→21.66 | 97.1→48.1 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.875→1.000 | 46.48→36.01 | 84.7→51.7 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 22.61→22.61 | 39.1→39.1 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 33.01→33.01 | 51.3→51.3 | 0.4→0.4 |
| default | Disc2 | class_grenade/ord | 276 | 0.986→0.986 | 9.34→9.34 | 28.5→28.5 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 33 | 0.424→0.424 | 20.47→20.47 | 490.4→490.4 | 0.1→0.1 |
| default | Disc2 | class_handgun/ord | 276 | 0.993→0.993 | 7.72→7.72 | 25.0→25.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.606→0.606 | 17.05→17.05 | 420.1→420.1 | 0.1→0.1 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.23→5.70 | 4.7→28.0 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 33 | 0.727→0.727 | 13.13→13.13 | 353.8→353.8 | 0.0→0.0 |
| default | Disc2 | class_rifle/ord | 276 | 0.989→0.989 | 9.50→9.50 | 28.8→28.8 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.515→0.515 | 17.20→17.20 | 456.7→456.7 | 0.1→0.1 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 8.45→8.45 | 28.1→28.1 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.333→0.333 | 21.42→21.42 | 507.6→507.6 | 0.5→0.5 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.38→31.64 | 125.6→92.3 | 0.5→0.1 |
| human_reaction | D5 | class_grenade/boss | 24 | 0.917→0.958 | 46.88→40.08 | 85.4→76.2 | 0.2→0.1 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.98→26.98 | 71.1→71.1 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 32.82→32.82 | 45.7→45.7 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 93.3→93.3 | 0.5→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 32.86→32.86 | 50.3→50.3 | 0.7→0.7 |
| human_reaction | D5 | class_rifle/ord | 30 | 0.967→1.000 | 47.49→30.71 | 135.7→89.6 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 0.833→0.958 | 59.86→48.73 | 100.6→71.3 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.57→31.57 | 84.3→84.3 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 0.958→0.958 | 45.99→45.99 | 78.0→78.0 | 0.4→0.4 |
| human_reaction | Disc2 | class_grenade/ord | 276 | 0.971→0.971 | 15.70→15.70 | 49.3→49.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 33 | 0.303→0.303 | 23.36→23.36 | 503.8→503.8 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/ord | 276 | 0.975→0.975 | 13.98→13.98 | 42.2→42.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 33 | 0.364→0.364 | 21.08→21.08 | 500.4→500.4 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/ord | 276 | 1.000→0.996 | 6.03→9.46 | 17.1→48.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 33 | 0.515→0.515 | 18.32→18.32 | 442.4→442.4 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/ord | 276 | 0.971→0.971 | 15.72→15.72 | 49.3→49.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 33 | 0.424→0.424 | 21.69→21.69 | 500.8→500.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/ord | 276 | 0.967→0.967 | 13.80→13.80 | 50.2→50.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 33 | 0.273→0.273 | 22.97→22.97 | 535.8→535.8 | 0.2→0.2 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.02→23.55 | 74.6→47.5 | 0.5→0.0 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 41.00→35.82 | 50.8→43.2 | 0.3→0.2 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 20.02→20.02 | 39.6→39.6 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 27.11→27.11 | 32.3→32.3 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 22.35→22.35 | 56.7→56.7 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 29.96→29.96 | 31.4→31.4 | 0.9→0.9 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 37.05→22.83 | 92.8→44.6 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 0.958→1.000 | 49.28→37.04 | 58.0→36.2 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 24.42→24.42 | 39.6→39.6 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 41.66→41.66 | 47.6→47.6 | 0.8→0.8 |
| far_player | Disc2 | class_grenade/ord | 276 | 0.993→0.993 | 10.00→10.00 | 28.2→28.2 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.394→0.394 | 22.29→22.29 | 488.9→488.9 | 0.1→0.1 |
| far_player | Disc2 | class_handgun/ord | 276 | 0.993→0.993 | 8.64→8.64 | 24.7→24.7 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.455→0.455 | 18.97→18.97 | 443.3→443.3 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.43→7.18 | 6.8→31.8 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 33 | 0.576→0.576 | 15.44→15.44 | 419.6→419.6 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/ord | 276 | 0.986→0.986 | 9.62→9.62 | 27.9→27.9 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.545→0.545 | 16.52→16.52 | 429.9→429.9 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/ord | 276 | 0.996→0.996 | 9.87→9.87 | 29.0→29.0 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 22.03→22.03 | 514.4→514.4 | 0.4→0.4 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_grenade, class_shotgun, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_grenade, class_shotgun, class_rifle
- far_player: Spearman vs default 0.80; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.015, human_reaction +0.019, far_player +0.004

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_shotgun, class_grenade
- human_reaction: Spearman vs default 0.80; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 0.80; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction -0.001, far_player +0.000

