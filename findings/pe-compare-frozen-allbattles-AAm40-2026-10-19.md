# Rule comparison: exp:AAm_40 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.965→0.959 (-0.006, [-0.010, -0.002]) | 6.36→6.88 | 52.9→58.5 | 6.4→9.2 | 0.0→0.0 | 0.035→0.041 | 0.25 | 0.28 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.52→5.95 | 15.7→18.7 | 4.9→7.2 | 0.0→0.0 | 0.000→0.000 | 0.03 | 0.15 |
| default | Disc2 | BOSS | 0.676→0.619 (-0.057, [-0.097, -0.023]) | 13.37→14.73 | 364.5→392.0 | 18.5→25.9 | 0.0→0.0 | 0.324→0.381 | 0.52 | 0.64 |
| human_reaction | Disc2 | ALL | 0.941→0.936 (-0.005, [-0.008, -0.002]) | 10.27→10.98 | 75.6→81.0 | 6.2→8.8 | 0.0→0.0 | 0.059→0.062 | 0.20 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 9.29→9.92 | 31.0→35.5 | 5.0→7.4 | 0.0→0.0 | 0.006→0.006 | 0.04 | 0.13 |
| human_reaction | Disc2 | BOSS | 0.500→0.455 (-0.045, [-0.080, -0.017]) | 18.49→19.83 | 448.1→461.7 | 16.0→20.7 | 0.0→0.0 | 0.500→0.534 | 0.52 | 0.59 |
| far_player | Disc2 | ALL | 0.961→0.954 (-0.006, [-0.010, -0.002]) | 7.21→7.82 | 57.5→62.6 | 7.3→10.6 | 0.0→0.0 | 0.039→0.046 | 0.27 | 0.28 |
| far_player | Disc2 | ORDINARY | 0.999→0.999 (+0.000, [+0.000, +0.000]) | 6.27→6.75 | 17.8→20.9 | 5.8→8.5 | 0.0→0.0 | 0.001→0.001 | 0.04 | 0.16 |
| far_player | Disc2 | BOSS | 0.636→0.580 (-0.057, [-0.091, -0.023]) | 15.12→16.79 | 389.7→411.5 | 20.4→27.9 | 0.0→0.0 | 0.364→0.420 | 0.51 | 0.64 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | Disc2 | C/ord | 184 | 1.000→1.000 | 7.38→7.38 | 25.4→25.4 | 0.0→0.0 |
| default | Disc2 | C/boss | 22 | 0.682→0.682 | 12.31→12.31 | 364.9→364.9 | 0.0→0.0 |
| default | Disc2 | D/ord | 184 | 1.000→1.000 | 3.12→5.16 | 4.1→19.7 | 0.0→0.0 |
| default | Disc2 | D/boss | 22 | 0.727→0.500 | 12.55→17.67 | 350.0→455.7 | 0.0→0.1 |
| default | Disc2 | G/ord | 184 | 1.000→1.000 | 6.80→6.80 | 21.6→21.6 | 0.0→0.0 |
| default | Disc2 | G/boss | 22 | 0.682→0.682 | 12.66→12.66 | 368.3→368.3 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 5.87→5.87 | 15.5→15.5 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/boss | 22 | 0.591→0.591 | 15.97→15.97 | 384.7→384.7 | 0.1→0.1 |
| default | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 5.65→5.65 | 17.8→17.8 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/boss | 22 | 0.545→0.545 | 14.91→14.91 | 413.4→413.4 | 0.0→0.0 |
| default | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 1.97→3.35 | 0.6→9.0 | 0.0→0.0 |
| default | Disc2 | controlled_machine/boss | 22 | 0.864→0.636 | 8.86→14.58 | 271.0→385.0 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.38→7.38 | 24.7→24.7 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/boss | 22 | 0.682→0.682 | 12.62→12.62 | 371.4→371.4 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 6.00→6.00 | 15.7→15.7 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/boss | 22 | 0.636→0.636 | 17.09→17.09 | 392.6→392.6 | 0.1→0.1 |
| human_reaction | Disc2 | C/ord | 184 | 0.989→0.989 | 10.77→10.77 | 42.3→42.3 | 0.0→0.0 |
| human_reaction | Disc2 | C/boss | 22 | 0.545→0.545 | 16.64→16.64 | 409.9→409.9 | 0.0→0.0 |
| human_reaction | Disc2 | D/ord | 184 | 1.000→1.000 | 6.00→8.67 | 15.4→35.5 | 0.0→0.0 |
| human_reaction | Disc2 | D/boss | 22 | 0.455→0.273 | 16.46→21.22 | 457.0→517.4 | 0.0→0.1 |
| human_reaction | Disc2 | G/ord | 184 | 0.989→0.989 | 10.23→10.23 | 38.9→38.9 | 0.0→0.0 |
| human_reaction | Disc2 | G/boss | 22 | 0.591→0.591 | 16.79→16.79 | 417.1→417.1 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/ord | 184 | 0.995→0.995 | 9.61→9.61 | 34.3→34.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/boss | 22 | 0.500→0.500 | 20.17→20.17 | 478.4→478.4 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/ord | 184 | 0.995→0.995 | 11.06→11.06 | 36.1→36.1 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/boss | 22 | 0.409→0.409 | 22.78→22.78 | 485.2→485.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 4.66→7.04 | 10.6→26.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/boss | 22 | 0.591→0.409 | 15.71→21.65 | 413.3→461.6 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/ord | 184 | 0.989→0.989 | 10.78→10.78 | 40.5→40.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/boss | 22 | 0.545→0.545 | 17.07→17.07 | 416.5→416.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/ord | 184 | 0.995→0.995 | 11.19→11.19 | 29.9→29.9 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/boss | 22 | 0.364→0.364 | 22.31→22.31 | 507.4→507.4 | 0.1→0.1 |
| far_player | Disc2 | C/ord | 184 | 1.000→1.000 | 7.77→7.77 | 25.6→25.6 | 0.0→0.0 |
| far_player | Disc2 | C/boss | 22 | 0.636→0.636 | 13.17→13.17 | 376.7→376.7 | 0.0→0.0 |
| far_player | Disc2 | D/ord | 184 | 1.000→1.000 | 4.21→6.46 | 7.7→24.1 | 0.0→0.0 |
| far_player | Disc2 | D/boss | 22 | 0.682→0.545 | 13.73→19.39 | 385.9→444.3 | 0.0→0.2 |
| far_player | Disc2 | G/ord | 184 | 1.000→1.000 | 7.02→7.02 | 23.0→23.0 | 0.0→0.0 |
| far_player | Disc2 | G/boss | 22 | 0.636→0.636 | 13.61→13.61 | 374.1→374.1 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 6.95→6.95 | 19.7→19.7 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/boss | 22 | 0.545→0.545 | 19.51→19.51 | 447.0→447.0 | 0.1→0.1 |
| far_player | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 6.34→6.34 | 18.6→18.6 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/boss | 22 | 0.545→0.545 | 17.13→17.13 | 425.6→425.6 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 2.88→4.50 | 3.9→12.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/boss | 22 | 0.818→0.500 | 11.34→19.04 | 293.6→409.3 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.77→7.77 | 24.8→24.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/boss | 22 | 0.636→0.636 | 13.20→13.20 | 376.4→376.4 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/ord | 184 | 0.995→0.995 | 7.17→7.17 | 18.9→18.9 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/boss | 22 | 0.591→0.591 | 19.24→19.24 | 438.3→438.3 | 0.1→0.1 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order G, C, controlled_rifle, controlled_machine, controlled_shotgun, controlled_grenade, controlled_handgun, D
- human_reaction: Spearman vs default 0.71; order G, controlled_grenade, C, controlled_rifle, controlled_machine, controlled_handgun, controlled_shotgun, D
- far_player: Spearman vs default 0.55; order G, C, controlled_rifle, controlled_handgun, D, controlled_grenade, controlled_shotgun, controlled_machine
- win-rate delta (proposal − baseline) by set: default -0.006, human_reaction -0.005, far_player -0.006

