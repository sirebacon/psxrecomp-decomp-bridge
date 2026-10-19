# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.67→22.67 | 31.7→31.7 | 9.3→9.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 19.82→19.82 | 36.1→36.1 | 8.9→8.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.23→26.23 | 26.1→26.1 | 9.8→9.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.965→0.965 (+0.000, [+0.000, +0.000]) | 6.36→6.74 | 52.9→55.6 | 6.4→8.4 | 0.0→0.0 | 0.035→0.035 | 0.25 | 0.28 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.52→5.95 | 15.7→18.7 | 4.9→7.2 | 0.0→0.0 | 0.000→0.000 | 0.03 | 0.15 |
| default | Disc2 | BOSS | 0.676→0.676 (+0.000, [+0.000, +0.000]) | 13.37→13.37 | 364.5→364.5 | 18.5→18.5 | 0.0→0.0 | 0.324→0.324 | 0.52 | 0.64 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 33.54→33.54 | 54.3→54.3 | 9.3→9.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 30.42→30.42 | 62.9→62.9 | 9.0→9.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 37.44→37.44 | 43.5→43.5 | 9.6→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.941→0.941 (+0.000, [+0.000, +0.000]) | 10.27→10.84 | 75.6→79.6 | 6.2→8.3 | 0.0→0.0 | 0.059→0.059 | 0.20 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 9.29→9.92 | 31.0→35.5 | 5.0→7.4 | 0.0→0.0 | 0.006→0.006 | 0.04 | 0.13 |
| human_reaction | Disc2 | BOSS | 0.500→0.500 (+0.000, [+0.000, +0.000]) | 18.49→18.49 | 448.1→448.1 | 16.0→16.0 | 0.0→0.0 | 0.500→0.500 | 0.52 | 0.59 |
| far_player | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.79→26.79 | 35.7→35.7 | 10.9→10.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 23.30→23.30 | 44.5→44.5 | 10.5→10.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 31.15→31.15 | 24.7→24.7 | 11.4→11.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.961→0.961 (+0.000, [+0.000, +0.000]) | 7.21→7.64 | 57.5→60.3 | 7.3→9.8 | 0.0→0.0 | 0.039→0.039 | 0.27 | 0.28 |
| far_player | Disc2 | ORDINARY | 0.999→0.999 (+0.000, [+0.000, +0.000]) | 6.27→6.75 | 17.8→20.9 | 5.8→8.5 | 0.0→0.0 | 0.001→0.001 | 0.04 | 0.16 |
| far_player | Disc2 | BOSS | 0.636→0.636 (+0.000, [+0.000, +0.000]) | 15.12→15.12 | 389.7→389.7 | 20.4→20.4 | 0.0→0.0 | 0.364→0.364 | 0.51 | 0.64 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | C/ord | 20 | 1.000→1.000 | 19.89→19.89 | 30.9→30.9 | 0.0→0.0 |
| default | D5 | C/boss | 16 | 1.000→1.000 | 27.09→27.09 | 22.6→22.6 | 0.0→0.0 |
| default | D5 | D/ord | 20 | 1.000→1.000 | 20.04→20.04 | 31.5→31.5 | 0.0→0.0 |
| default | D5 | D/boss | 16 | 1.000→1.000 | 31.58→31.58 | 38.4→38.4 | 0.0→0.0 |
| default | D5 | G/ord | 20 | 1.000→1.000 | 16.11→16.11 | 31.4→31.4 | 0.0→0.0 |
| default | D5 | G/boss | 16 | 1.000→1.000 | 19.15→19.15 | 21.8→21.8 | 0.0→0.0 |
| default | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 19.89→19.89 | 30.9→30.9 | 0.0→0.0 |
| default | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 27.09→27.09 | 22.6→22.6 | 0.0→0.0 |
| default | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 19.49→19.49 | 41.6→41.6 | 0.0→0.0 |
| default | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 23.91→23.91 | 20.2→20.2 | 0.0→0.0 |
| default | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 20.06→20.06 | 38.0→38.0 | 0.0→0.0 |
| default | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 26.47→26.47 | 26.8→26.8 | 0.0→0.0 |
| default | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 23.18→23.18 | 53.8→53.8 | 0.0→0.0 |
| default | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 27.49→27.49 | 34.2→34.2 | 0.0→0.0 |
| default | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 19.89→19.89 | 30.9→30.9 | 0.0→0.0 |
| default | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 27.09→27.09 | 22.6→22.6 | 0.0→0.0 |
| default | Disc2 | C/ord | 184 | 1.000→1.000 | 7.38→7.38 | 25.4→25.4 | 0.0→0.0 |
| default | Disc2 | C/boss | 22 | 0.682→0.682 | 12.31→12.31 | 364.9→364.9 | 0.0→0.0 |
| default | Disc2 | D/ord | 184 | 1.000→1.000 | 3.12→5.16 | 4.1→19.7 | 0.0→0.0 |
| default | Disc2 | D/boss | 22 | 0.727→0.727 | 12.55→12.55 | 350.0→350.0 | 0.0→0.0 |
| default | Disc2 | G/ord | 184 | 1.000→1.000 | 6.80→6.80 | 21.6→21.6 | 0.0→0.0 |
| default | Disc2 | G/boss | 22 | 0.682→0.682 | 12.66→12.66 | 368.3→368.3 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 5.87→5.87 | 15.5→15.5 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/boss | 22 | 0.591→0.591 | 15.97→15.97 | 384.7→384.7 | 0.1→0.1 |
| default | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 5.65→5.65 | 17.8→17.8 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/boss | 22 | 0.545→0.545 | 14.91→14.91 | 413.4→413.4 | 0.0→0.0 |
| default | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 1.97→3.35 | 0.6→9.0 | 0.0→0.0 |
| default | Disc2 | controlled_machine/boss | 22 | 0.864→0.864 | 8.86→8.86 | 271.0→271.0 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.38→7.38 | 24.7→24.7 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/boss | 22 | 0.682→0.682 | 12.62→12.62 | 371.4→371.4 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 6.00→6.00 | 15.7→15.7 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/boss | 22 | 0.636→0.636 | 17.09→17.09 | 392.6→392.6 | 0.1→0.1 |
| human_reaction | D5 | C/ord | 20 | 1.000→1.000 | 31.31→31.31 | 54.9→54.9 | 0.0→0.0 |
| human_reaction | D5 | C/boss | 16 | 1.000→1.000 | 40.16→40.16 | 37.9→37.9 | 0.0→0.0 |
| human_reaction | D5 | D/ord | 20 | 1.000→1.000 | 32.32→32.32 | 60.7→60.7 | 0.0→0.0 |
| human_reaction | D5 | D/boss | 16 | 1.000→1.000 | 43.95→43.95 | 52.2→52.2 | 0.0→0.0 |
| human_reaction | D5 | G/ord | 20 | 1.000→1.000 | 27.27→27.27 | 64.3→64.3 | 0.0→0.0 |
| human_reaction | D5 | G/boss | 16 | 1.000→1.000 | 27.99→27.99 | 36.3→36.3 | 0.0→0.0 |
| human_reaction | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 31.31→31.31 | 54.9→54.9 | 0.0→0.0 |
| human_reaction | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 40.16→40.16 | 37.9→37.9 | 0.0→0.0 |
| human_reaction | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 27.22→27.22 | 68.0→68.0 | 0.0→0.0 |
| human_reaction | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 30.27→30.27 | 41.9→41.9 | 0.0→0.0 |
| human_reaction | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 31.01→31.01 | 67.3→67.3 | 0.0→0.0 |
| human_reaction | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 38.67→38.67 | 50.3→50.3 | 0.0→0.0 |
| human_reaction | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 31.62→31.62 | 78.1→78.1 | 0.0→0.0 |
| human_reaction | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 38.16→38.16 | 53.6→53.6 | 0.0→0.0 |
| human_reaction | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 31.31→31.31 | 54.9→54.9 | 0.0→0.0 |
| human_reaction | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 40.16→40.16 | 37.9→37.9 | 0.0→0.0 |
| human_reaction | Disc2 | C/ord | 184 | 0.989→0.989 | 10.77→10.77 | 42.3→42.3 | 0.0→0.0 |
| human_reaction | Disc2 | C/boss | 22 | 0.545→0.545 | 16.64→16.64 | 409.9→409.9 | 0.0→0.0 |
| human_reaction | Disc2 | D/ord | 184 | 1.000→1.000 | 6.00→8.67 | 15.4→35.5 | 0.0→0.0 |
| human_reaction | Disc2 | D/boss | 22 | 0.455→0.455 | 16.46→16.46 | 457.0→457.0 | 0.0→0.0 |
| human_reaction | Disc2 | G/ord | 184 | 0.989→0.989 | 10.23→10.23 | 38.9→38.9 | 0.0→0.0 |
| human_reaction | Disc2 | G/boss | 22 | 0.591→0.591 | 16.79→16.79 | 417.1→417.1 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/ord | 184 | 0.995→0.995 | 9.61→9.61 | 34.3→34.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/boss | 22 | 0.500→0.500 | 20.17→20.17 | 478.4→478.4 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/ord | 184 | 0.995→0.995 | 11.06→11.06 | 36.1→36.1 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/boss | 22 | 0.409→0.409 | 22.78→22.78 | 485.2→485.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 4.66→7.04 | 10.6→26.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/boss | 22 | 0.591→0.591 | 15.71→15.71 | 413.3→413.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/ord | 184 | 0.989→0.989 | 10.78→10.78 | 40.5→40.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/boss | 22 | 0.545→0.545 | 17.07→17.07 | 416.5→416.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/ord | 184 | 0.995→0.995 | 11.19→11.19 | 29.9→29.9 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/boss | 22 | 0.364→0.364 | 22.31→22.31 | 507.4→507.4 | 0.1→0.1 |
| far_player | D5 | C/ord | 20 | 1.000→1.000 | 22.65→22.65 | 38.7→38.7 | 0.0→0.0 |
| far_player | D5 | C/boss | 16 | 1.000→1.000 | 32.39→32.39 | 22.2→22.2 | 0.0→0.0 |
| far_player | D5 | D/ord | 20 | 1.000→1.000 | 22.33→22.33 | 36.6→36.6 | 0.0→0.0 |
| far_player | D5 | D/boss | 16 | 1.000→1.000 | 36.56→36.56 | 35.2→35.2 | 0.1→0.1 |
| far_player | D5 | G/ord | 20 | 1.000→1.000 | 19.23→19.23 | 37.5→37.5 | 0.0→0.0 |
| far_player | D5 | G/boss | 16 | 1.000→1.000 | 24.24→24.24 | 18.8→18.8 | 0.1→0.1 |
| far_player | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 22.65→22.65 | 38.7→38.7 | 0.0→0.0 |
| far_player | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 32.39→32.39 | 22.2→22.2 | 0.0→0.0 |
| far_player | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 25.09→25.09 | 53.9→53.9 | 0.0→0.0 |
| far_player | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 27.97→27.97 | 22.7→22.7 | 0.0→0.0 |
| far_player | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 22.60→22.60 | 45.0→45.0 | 0.0→0.0 |
| far_player | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 31.49→31.49 | 27.6→27.6 | 0.0→0.0 |
| far_player | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 29.21→29.21 | 66.5→66.5 | 0.0→0.0 |
| far_player | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 31.76→31.76 | 26.9→26.9 | 0.0→0.0 |
| far_player | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 22.65→22.65 | 38.7→38.7 | 0.0→0.0 |
| far_player | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 32.39→32.39 | 22.2→22.2 | 0.0→0.0 |
| far_player | Disc2 | C/ord | 184 | 1.000→1.000 | 7.77→7.77 | 25.6→25.6 | 0.0→0.0 |
| far_player | Disc2 | C/boss | 22 | 0.636→0.636 | 13.17→13.17 | 376.7→376.7 | 0.0→0.0 |
| far_player | Disc2 | D/ord | 184 | 1.000→1.000 | 4.21→6.46 | 7.7→24.1 | 0.0→0.0 |
| far_player | Disc2 | D/boss | 22 | 0.682→0.682 | 13.73→13.73 | 385.9→385.9 | 0.0→0.0 |
| far_player | Disc2 | G/ord | 184 | 1.000→1.000 | 7.02→7.02 | 23.0→23.0 | 0.0→0.0 |
| far_player | Disc2 | G/boss | 22 | 0.636→0.636 | 13.61→13.61 | 374.1→374.1 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 6.95→6.95 | 19.7→19.7 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/boss | 22 | 0.545→0.545 | 19.51→19.51 | 447.0→447.0 | 0.1→0.1 |
| far_player | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 6.34→6.34 | 18.6→18.6 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/boss | 22 | 0.545→0.545 | 17.13→17.13 | 425.6→425.6 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 2.88→4.50 | 3.9→12.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/boss | 22 | 0.818→0.818 | 11.34→11.34 | 293.6→293.6 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.77→7.77 | 24.8→24.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/boss | 22 | 0.636→0.636 | 13.20→13.20 | 376.4→376.4 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/ord | 184 | 0.995→0.995 | 7.17→7.17 | 18.9→18.9 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/boss | 22 | 0.591→0.591 | 19.24→19.24 | 438.3→438.3 | 0.1→0.1 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order G, controlled_handgun, controlled_machine, C, controlled_grenade, controlled_shotgun, controlled_rifle, D
- human_reaction: Spearman vs default 0.86; order G, controlled_handgun, controlled_machine, controlled_rifle, C, controlled_grenade, controlled_shotgun, D
- far_player: Spearman vs default 0.98; order G, controlled_handgun, controlled_machine, C, controlled_grenade, controlled_shotgun, D, controlled_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, D, G, C, controlled_rifle, controlled_shotgun, controlled_grenade, controlled_handgun
- human_reaction: Spearman vs default 0.79; order controlled_machine, G, D, controlled_grenade, C, controlled_rifle, controlled_handgun, controlled_shotgun
- far_player: Spearman vs default 0.90; order controlled_machine, D, G, C, controlled_rifle, controlled_handgun, controlled_grenade, controlled_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

