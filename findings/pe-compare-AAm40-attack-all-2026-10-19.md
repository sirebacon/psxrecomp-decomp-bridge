# Rule comparison: exp:AAm_40 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 8 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.990→0.984 (-0.005, [-0.013, +0.000]) | 7.38→8.13 | 49.5→56.8 | 6.9→10.8 | 0.0→0.0 | 0.010→0.016 | 0.00 | 0.23 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 6.70→7.48 | 23.5→29.2 | 5.6→9.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.13 |
| default | Disc2 | BOSS | 0.875→0.812 (-0.062, [-0.156, +0.000]) | 14.83→15.24 | 336.1→360.6 | 21.3→23.2 | 0.0→0.0 | 0.125→0.188 | 0.00 | 0.71 |
| human_reaction | Disc2 | ALL | 0.951→0.945 (-0.005, [-0.013, +0.000]) | 12.13→13.05 | 84.1→93.7 | 6.8→10.3 | 0.0→0.0 | 0.049→0.055 | 0.00 | 0.21 |
| human_reaction | Disc2 | ORDINARY | 0.997→0.994 (-0.003, [-0.009, +0.000]) | 11.41→12.43 | 42.6→52.0 | 5.8→9.6 | 0.0→0.0 | 0.003→0.006 | 0.00 | 0.13 |
| human_reaction | Disc2 | BOSS | 0.438→0.406 (-0.031, [-0.094, +0.000]) | 20.04→19.91 | 541.4→552.2 | 18.4→18.5 | 0.0→0.0 | 0.562→0.594 | 0.00 | 0.73 |
| far_player | Disc2 | ALL | 0.971→0.966 (-0.005, [-0.013, +0.000]) | 8.22→9.06 | 55.4→62.9 | 8.0→12.3 | 0.0→0.0 | 0.029→0.034 | 0.00 | 0.25 |
| far_player | Disc2 | ORDINARY | 0.997→0.997 (+0.000, [+0.000, +0.000]) | 7.38→8.28 | 25.5→31.4 | 6.6→11.2 | 0.0→0.0 | 0.003→0.003 | 0.00 | 0.14 |
| far_player | Disc2 | BOSS | 0.688→0.625 (-0.062, [-0.156, +0.000]) | 17.38→17.63 | 384.8→409.8 | 23.8→24.8 | 0.0→0.0 | 0.312→0.375 | 0.00 | 0.72 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | Disc2 | C/ord | 44 | 1.000→1.000 | 9.19→9.19 | 34.2→34.2 | 0.0→0.0 |
| default | Disc2 | C/boss | 4 | 1.000→1.000 | 11.45→11.45 | 255.0→255.0 | 0.0→0.0 |
| default | Disc2 | D/ord | 44 | 1.000→1.000 | 3.28→6.93 | 10.0→37.8 | 0.0→0.0 |
| default | Disc2 | D/boss | 4 | 1.000→0.750 | 14.75→15.86 | 436.5→478.5 | 0.0→0.0 |
| default | Disc2 | G/ord | 44 | 1.000→1.000 | 8.31→8.31 | 26.9→26.9 | 0.0→0.0 |
| default | Disc2 | G/boss | 4 | 1.000→1.000 | 11.28→11.28 | 332.5→332.5 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/ord | 44 | 1.000→1.000 | 7.70→7.70 | 36.6→36.6 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/boss | 4 | 0.500→0.500 | 18.91→18.91 | 470.0→470.0 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/ord | 44 | 1.000→1.000 | 7.48→7.48 | 23.4→23.4 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/boss | 4 | 0.750→0.750 | 18.86→18.86 | 353.2→353.2 | 0.0→0.0 |
| default | Disc2 | controlled_machine/ord | 44 | 1.000→1.000 | 2.27→4.86 | 3.7→21.5 | 0.0→0.0 |
| default | Disc2 | controlled_machine/boss | 4 | 1.000→0.750 | 10.58→12.78 | 125.8→279.8 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/ord | 44 | 1.000→1.000 | 9.19→9.19 | 32.6→32.6 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/boss | 4 | 1.000→1.000 | 11.64→11.64 | 253.0→253.0 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/ord | 44 | 1.000→1.000 | 6.20→6.20 | 20.2→20.2 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/boss | 4 | 0.750→0.750 | 21.15→21.15 | 462.8→462.8 | 0.0→0.0 |
| human_reaction | Disc2 | C/ord | 44 | 1.000→1.000 | 13.11→13.11 | 55.9→55.9 | 0.0→0.0 |
| human_reaction | Disc2 | C/boss | 4 | 0.500→0.500 | 16.16→16.16 | 505.5→505.5 | 0.0→0.0 |
| human_reaction | Disc2 | D/ord | 44 | 1.000→0.977 | 6.29→10.50 | 16.3→61.0 | 0.0→0.0 |
| human_reaction | Disc2 | D/boss | 4 | 0.500→0.500 | 21.43→20.68 | 546.5→545.0 | 0.0→0.0 |
| human_reaction | Disc2 | G/ord | 44 | 1.000→1.000 | 12.68→12.68 | 51.4→51.4 | 0.0→0.0 |
| human_reaction | Disc2 | G/boss | 4 | 0.500→0.500 | 14.97→14.97 | 470.2→470.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/ord | 44 | 1.000→1.000 | 13.11→13.11 | 50.5→50.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/boss | 4 | 0.500→0.500 | 22.05→22.05 | 559.2→559.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/ord | 44 | 1.000→1.000 | 14.53→14.53 | 44.6→44.6 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/boss | 4 | 0.000→0.000 | 21.19→21.19 | 659.2→659.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/ord | 44 | 1.000→1.000 | 5.28→9.22 | 17.6→48.1 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/boss | 4 | 1.000→0.750 | 22.14→21.82 | 418.5→506.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/ord | 44 | 1.000→1.000 | 13.11→13.11 | 53.8→53.8 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/boss | 4 | 0.500→0.500 | 16.16→16.16 | 501.0→501.0 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/ord | 44 | 0.977→0.977 | 13.16→13.16 | 50.5→50.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/boss | 4 | 0.000→0.000 | 26.26→26.26 | 670.8→670.8 | 0.0→0.0 |
| far_player | Disc2 | C/ord | 44 | 1.000→1.000 | 9.34→9.34 | 33.1→33.1 | 0.0→0.0 |
| far_player | Disc2 | C/boss | 4 | 0.750→0.750 | 14.13→14.13 | 359.0→359.0 | 0.0→0.0 |
| far_player | Disc2 | D/ord | 44 | 1.000→1.000 | 4.06→8.57 | 7.9→44.4 | 0.0→0.0 |
| far_player | Disc2 | D/boss | 4 | 1.000→0.750 | 16.36→16.91 | 355.0→397.0 | 0.0→0.0 |
| far_player | Disc2 | G/ord | 44 | 1.000→1.000 | 8.74→8.74 | 30.2→30.2 | 0.0→0.0 |
| far_player | Disc2 | G/boss | 4 | 0.750→0.750 | 13.96→13.96 | 378.5→378.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/ord | 44 | 1.000→1.000 | 8.77→8.77 | 37.7→37.7 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/boss | 4 | 0.250→0.250 | 21.59→21.59 | 554.8→554.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/ord | 44 | 0.977→0.977 | 7.90→7.90 | 31.9→31.9 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/boss | 4 | 0.500→0.500 | 20.37→20.37 | 423.0→423.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/ord | 44 | 1.000→1.000 | 3.17→5.83 | 12.5→23.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/boss | 4 | 1.000→0.750 | 12.11→13.56 | 125.8→283.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/ord | 44 | 1.000→1.000 | 9.34→9.34 | 31.5→31.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/boss | 4 | 0.750→0.750 | 14.13→14.13 | 355.8→355.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/ord | 44 | 1.000→1.000 | 7.75→7.75 | 19.0→19.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/boss | 4 | 0.500→0.500 | 26.34→26.34 | 526.8→526.8 | 0.2→0.2 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order G, C, controlled_rifle, controlled_machine, controlled_shotgun, D, controlled_handgun, controlled_grenade
- human_reaction: Spearman vs default 0.62; order controlled_machine, G, C, controlled_rifle, controlled_grenade, D, controlled_handgun, controlled_shotgun
- far_player: Spearman vs default 0.64; order controlled_machine, G, D, C, controlled_rifle, controlled_shotgun, controlled_handgun, controlled_grenade
- win-rate delta (proposal − baseline) by set: default -0.005, human_reaction -0.005, far_player -0.005

