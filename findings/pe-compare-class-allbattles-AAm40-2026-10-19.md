# Rule comparison: exp:AAm_40 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.985→0.985 (+0.000, [+0.000, +0.000]) | 27.76→27.76 | 56.0→56.0 | 11.5→11.5 | 0.3→0.3 | 0.015→0.015 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.16→24.16 | 58.8→58.8 | 11.0→11.0 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.967→0.967 (+0.000, [+0.000, +0.000]) | 32.25→32.25 | 52.4→52.4 | 12.0→12.0 | 0.3→0.3 | 0.033→0.033 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.943→0.938 (-0.005, [-0.009, -0.002]) | 8.74→9.30 | 68.2→74.4 | 7.9→12.0 | 0.0→0.0 | 0.057→0.062 | 0.24 | 0.30 |
| default | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 7.65→8.14 | 23.0→27.7 | 5.9→9.4 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.20 |
| default | Disc2 | BOSS | 0.521→0.473 (-0.048, [-0.085, -0.018]) | 17.85→19.04 | 445.7→464.7 | 24.5→33.9 | 0.1→0.2 | 0.479→0.527 | 0.55 | 0.70 |
| human_reaction | D5 | ALL | 0.970→0.970 (+0.000, [+0.000, +0.000]) | 38.85→38.85 | 88.7→88.7 | 12.0→12.0 | 0.3→0.3 | 0.015→0.015 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 34.98→34.98 | 102.0→102.0 | 11.7→11.7 | 0.3→0.3 | 0.007→0.007 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.942→0.942 (+0.000, [+0.000, +0.000]) | 43.68→43.68 | 72.0→72.0 | 12.4→12.4 | 0.3→0.3 | 0.025→0.025 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.913→0.909 (-0.004, [-0.007, -0.001]) | 13.95→14.68 | 90.2→97.1 | 7.4→11.4 | 0.0→0.0 | 0.087→0.091 | 0.18 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.977→0.976 (-0.001, [-0.002, +0.000]) | 13.05→13.73 | 41.6→48.0 | 5.9→9.6 | 0.0→0.0 | 0.023→0.024 | 0.03 | 0.15 |
| human_reaction | Disc2 | BOSS | 0.376→0.345 (-0.030, [-0.061, -0.006]) | 21.49→22.62 | 496.6→508.4 | 19.9→26.6 | 0.1→0.1 | 0.618→0.648 | 0.55 | 0.65 |
| far_player | D5 | ALL | 0.996→0.996 (+0.000, [+0.000, +0.000]) | 31.78→31.78 | 53.3→53.3 | 13.8→13.8 | 0.4→0.4 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.97→26.97 | 60.7→60.7 | 13.0→13.0 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.992→0.992 (+0.000, [+0.000, +0.000]) | 37.80→37.80 | 44.0→44.0 | 14.8→14.8 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.936→0.933 (-0.003, [-0.006, -0.001]) | 9.64→10.28 | 69.9→75.5 | 9.0→13.7 | 0.0→0.0 | 0.063→0.067 | 0.27 | 0.30 |
| far_player | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 8.51→9.06 | 23.3→28.3 | 7.0→11.1 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.19 |
| far_player | Disc2 | BOSS | 0.455→0.424 (-0.030, [-0.061, -0.006]) | 19.05→20.43 | 459.2→469.8 | 26.0→35.8 | 0.2→0.2 | 0.539→0.570 | 0.54 | 0.71 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 28.10→28.10 | 77.6→77.6 | 0.4→0.4 |
| default | D5 | class_grenade/boss | 24 | 0.958→0.958 | 36.74→36.74 | 63.5→63.5 | 0.2→0.2 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 18.67→18.67 | 38.0→38.0 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 23.70→23.70 | 32.0→32.0 | 0.2→0.2 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 16.72→16.72 | 42.2→42.2 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 21.34→21.34 | 30.5→30.5 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 34.72→34.72 | 97.1→97.1 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.875→0.875 | 46.48→46.48 | 84.7→84.7 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 22.61→22.61 | 39.1→39.1 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 33.01→33.01 | 51.3→51.3 | 0.4→0.4 |
| default | Disc2 | class_grenade/ord | 276 | 0.986→0.986 | 9.34→9.34 | 28.5→28.5 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 33 | 0.424→0.424 | 20.47→20.47 | 490.4→490.4 | 0.1→0.1 |
| default | Disc2 | class_handgun/ord | 276 | 0.993→0.993 | 7.72→7.72 | 25.0→25.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.606→0.606 | 17.05→17.05 | 420.1→420.1 | 0.1→0.1 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.23→5.70 | 4.7→28.0 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 33 | 0.727→0.485 | 13.13→19.04 | 353.8→449.0 | 0.0→0.2 |
| default | Disc2 | class_rifle/ord | 276 | 0.989→0.989 | 9.50→9.50 | 28.8→28.8 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.515→0.515 | 17.20→17.20 | 456.7→456.7 | 0.1→0.1 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 8.45→8.45 | 28.1→28.1 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.333→0.333 | 21.42→21.42 | 507.6→507.6 | 0.5→0.5 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.38→40.38 | 125.6→125.6 | 0.5→0.5 |
| human_reaction | D5 | class_grenade/boss | 24 | 0.917→0.917 | 46.88→46.88 | 85.4→85.4 | 0.2→0.2 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.98→26.98 | 71.1→71.1 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 32.82→32.82 | 45.7→45.7 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 93.3→93.3 | 0.5→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 32.86→32.86 | 50.3→50.3 | 0.7→0.7 |
| human_reaction | D5 | class_rifle/ord | 30 | 0.967→0.967 | 47.49→47.49 | 135.7→135.7 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 0.833→0.833 | 59.86→59.86 | 100.6→100.6 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.57→31.57 | 84.3→84.3 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 0.958→0.958 | 45.99→45.99 | 78.0→78.0 | 0.4→0.4 |
| human_reaction | Disc2 | class_grenade/ord | 276 | 0.971→0.971 | 15.70→15.70 | 49.3→49.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 33 | 0.303→0.303 | 23.36→23.36 | 503.8→503.8 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/ord | 276 | 0.975→0.975 | 13.98→13.98 | 42.2→42.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 33 | 0.364→0.364 | 21.08→21.08 | 500.4→500.4 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/ord | 276 | 1.000→0.996 | 6.03→9.46 | 17.1→48.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 33 | 0.515→0.364 | 18.32→24.01 | 442.4→501.1 | 0.0→0.1 |
| human_reaction | Disc2 | class_rifle/ord | 276 | 0.971→0.971 | 15.72→15.72 | 49.3→49.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 33 | 0.424→0.424 | 21.69→21.69 | 500.8→500.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/ord | 276 | 0.967→0.967 | 13.80→13.80 | 50.2→50.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 33 | 0.273→0.273 | 22.97→22.97 | 535.8→535.8 | 0.2→0.2 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.02→31.02 | 74.6→74.6 | 0.5→0.5 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 41.00→41.00 | 50.8→50.8 | 0.3→0.3 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 20.02→20.02 | 39.6→39.6 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 27.11→27.11 | 32.3→32.3 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 22.35→22.35 | 56.7→56.7 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 29.96→29.96 | 31.4→31.4 | 0.9→0.9 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 37.05→37.05 | 92.8→92.8 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 0.958→0.958 | 49.28→49.28 | 58.0→58.0 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 24.42→24.42 | 39.6→39.6 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 41.66→41.66 | 47.6→47.6 | 0.8→0.8 |
| far_player | Disc2 | class_grenade/ord | 276 | 0.993→0.993 | 10.00→10.00 | 28.2→28.2 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.394→0.394 | 22.29→22.29 | 488.9→488.9 | 0.1→0.1 |
| far_player | Disc2 | class_handgun/ord | 276 | 0.993→0.993 | 8.64→8.64 | 24.7→24.7 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.455→0.455 | 18.97→18.97 | 443.3→443.3 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.43→7.18 | 6.8→31.8 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 33 | 0.576→0.424 | 15.44→22.33 | 419.6→472.7 | 0.1→0.3 |
| far_player | Disc2 | class_rifle/ord | 276 | 0.986→0.986 | 9.62→9.62 | 27.9→27.9 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.545→0.545 | 16.52→16.52 | 429.9→429.9 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/ord | 276 | 0.996→0.996 | 9.87→9.87 | 29.0→29.0 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 22.03→22.03 | 514.4→514.4 | 0.4→0.4 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- far_player: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order class_handgun, class_machine, class_rifle, class_shotgun, class_grenade
- human_reaction: Spearman vs default 0.60; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 0.60; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default -0.005, human_reaction -0.004, far_player -0.003

