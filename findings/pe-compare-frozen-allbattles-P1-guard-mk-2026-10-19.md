# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 2 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.67→22.67 | 28.0→28.0 | 9.3→9.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 19.82→19.82 | 32.6→32.6 | 8.9→8.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.23→26.23 | 22.4→22.4 | 9.8→9.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.976→0.976 (+0.000, [+0.000, +0.000]) | 6.67→7.06 | 45.3→48.0 | 6.7→8.8 | 0.0→0.0 | 0.024→0.024 | 0.02 | 0.32 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.52→5.95 | 12.5→15.5 | 4.9→7.2 | 0.0→0.0 | 0.000→0.000 | 0.03 | 0.15 |
| default | Disc2 | BOSS | 0.778→0.778 (+0.000, [+0.000, +0.000]) | 16.32→16.32 | 320.1→320.1 | 21.6→21.6 | 0.0→0.0 | 0.222→0.222 | 0.00 | 0.60 |
| human_reaction | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 33.54→33.54 | 45.9→45.9 | 9.3→9.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 30.42→30.42 | 56.0→56.0 | 9.0→9.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 37.44→37.44 | 33.4→33.4 | 9.6→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.959→0.959 (+0.000, [+0.000, +0.000]) | 10.66→11.22 | 63.4→67.0 | 6.4→8.6 | 0.0→0.0 | 0.039→0.039 | 0.03 | 0.26 |
| human_reaction | Disc2 | ORDINARY | 0.999→0.999 (+0.000, [+0.000, +0.000]) | 9.34→9.97 | 25.2→29.2 | 5.0→7.4 | 0.0→0.0 | 0.001→0.001 | 0.04 | 0.14 |
| human_reaction | Disc2 | BOSS | 0.619→0.619 (+0.000, [+0.000, +0.000]) | 21.72→21.72 | 383.6→383.6 | 18.5→18.5 | 0.0→0.0 | 0.364→0.364 | 0.00 | 0.57 |
| far_player | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.79→26.79 | 32.5→32.5 | 10.9→10.9 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 23.30→23.30 | 41.6→41.6 | 10.5→10.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 31.15→31.15 | 21.2→21.2 | 11.4→11.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.974→0.974 (+0.000, [+0.000, +0.000]) | 7.60→8.03 | 48.1→51.1 | 7.8→10.3 | 0.0→0.0 | 0.025→0.025 | 0.02 | 0.32 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 6.27→6.75 | 14.3→17.6 | 5.8→8.5 | 0.0→0.0 | 0.000→0.000 | 0.04 | 0.16 |
| far_player | Disc2 | BOSS | 0.756→0.756 (+0.000, [+0.000, +0.000]) | 18.71→18.71 | 330.7→330.7 | 25.0→25.0 | 0.1→0.1 | 0.239→0.239 | 0.00 | 0.60 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | C/ord | 20 | 1.000→1.000 | 19.89→19.89 | 27.8→27.8 | 0.0→0.0 |
| default | D5 | C/boss | 16 | 1.000→1.000 | 27.09→27.09 | 19.8→19.8 | 0.0→0.0 |
| default | D5 | D/ord | 20 | 1.000→1.000 | 20.04→20.04 | 27.5→27.5 | 0.0→0.0 |
| default | D5 | D/boss | 16 | 1.000→1.000 | 31.58→31.58 | 32.4→32.4 | 0.0→0.0 |
| default | D5 | G/ord | 20 | 1.000→1.000 | 16.11→16.11 | 30.4→30.4 | 0.0→0.0 |
| default | D5 | G/boss | 16 | 1.000→1.000 | 19.15→19.15 | 19.4→19.4 | 0.0→0.0 |
| default | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 19.89→19.89 | 27.8→27.8 | 0.0→0.0 |
| default | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 27.09→27.09 | 19.8→19.8 | 0.0→0.0 |
| default | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 19.49→19.49 | 37.1→37.1 | 0.0→0.0 |
| default | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 23.91→23.91 | 18.5→18.5 | 0.0→0.0 |
| default | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 20.06→20.06 | 32.2→32.2 | 0.0→0.0 |
| default | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 26.47→26.47 | 19.4→19.4 | 0.0→0.0 |
| default | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 23.18→23.18 | 50.0→50.0 | 0.0→0.0 |
| default | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 27.49→27.49 | 30.2→30.2 | 0.0→0.0 |
| default | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 19.89→19.89 | 27.8→27.8 | 0.0→0.0 |
| default | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 27.09→27.09 | 19.8→19.8 | 0.0→0.0 |
| default | Disc2 | C/ord | 184 | 1.000→1.000 | 7.38→7.38 | 19.7→19.7 | 0.0→0.0 |
| default | Disc2 | C/boss | 22 | 0.818→0.818 | 15.45→15.45 | 340.0→340.0 | 0.0→0.0 |
| default | Disc2 | D/ord | 184 | 1.000→1.000 | 3.12→5.16 | 3.0→18.7 | 0.0→0.0 |
| default | Disc2 | D/boss | 22 | 0.818→0.818 | 13.29→13.29 | 267.1→267.1 | 0.0→0.0 |
| default | Disc2 | G/ord | 184 | 1.000→1.000 | 6.80→6.80 | 17.3→17.3 | 0.0→0.0 |
| default | Disc2 | G/boss | 22 | 0.864→0.864 | 15.82→15.82 | 337.7→337.7 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 5.87→5.87 | 14.0→14.0 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/boss | 22 | 0.682→0.682 | 21.49→21.49 | 362.3→362.3 | 0.1→0.1 |
| default | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 5.65→5.65 | 12.0→12.0 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/boss | 22 | 0.727→0.727 | 19.11→19.11 | 353.2→353.2 | 0.0→0.0 |
| default | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 1.97→3.35 | 0.4→8.8 | 0.0→0.0 |
| default | Disc2 | controlled_machine/boss | 22 | 0.864→0.864 | 8.58→8.58 | 213.1→213.1 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.38→7.38 | 19.1→19.1 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/boss | 22 | 0.818→0.818 | 15.56→15.56 | 339.8→339.8 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 6.00→6.00 | 14.4→14.4 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/boss | 22 | 0.636→0.636 | 21.30→21.30 | 347.7→347.7 | 0.1→0.1 |
| human_reaction | D5 | C/ord | 20 | 1.000→1.000 | 31.31→31.31 | 48.8→48.8 | 0.0→0.0 |
| human_reaction | D5 | C/boss | 16 | 1.000→1.000 | 40.16→40.16 | 29.9→29.9 | 0.0→0.0 |
| human_reaction | D5 | D/ord | 20 | 1.000→1.000 | 32.32→32.32 | 54.2→54.2 | 0.0→0.0 |
| human_reaction | D5 | D/boss | 16 | 1.000→1.000 | 43.95→43.95 | 38.3→38.3 | 0.0→0.0 |
| human_reaction | D5 | G/ord | 20 | 1.000→1.000 | 27.27→27.27 | 57.4→57.4 | 0.0→0.0 |
| human_reaction | D5 | G/boss | 16 | 1.000→1.000 | 27.99→27.99 | 28.2→28.2 | 0.0→0.0 |
| human_reaction | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 31.31→31.31 | 48.8→48.8 | 0.0→0.0 |
| human_reaction | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 40.16→40.16 | 29.9→29.9 | 0.0→0.0 |
| human_reaction | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 27.22→27.22 | 63.2→63.2 | 0.0→0.0 |
| human_reaction | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 30.27→30.27 | 31.6→31.6 | 0.0→0.0 |
| human_reaction | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 31.01→31.01 | 56.8→56.8 | 0.0→0.0 |
| human_reaction | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 38.67→38.67 | 35.3→35.3 | 0.0→0.0 |
| human_reaction | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 31.62→31.62 | 69.8→69.8 | 0.0→0.0 |
| human_reaction | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 38.16→38.16 | 43.6→43.6 | 0.0→0.0 |
| human_reaction | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 31.31→31.31 | 48.8→48.8 | 0.0→0.0 |
| human_reaction | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 40.16→40.16 | 29.9→29.9 | 0.0→0.0 |
| human_reaction | Disc2 | C/ord | 184 | 1.000→1.000 | 10.84→10.84 | 32.5→32.5 | 0.0→0.0 |
| human_reaction | Disc2 | C/boss | 22 | 0.727→0.727 | 20.36→20.36 | 351.2→351.2 | 0.0→0.0 |
| human_reaction | Disc2 | D/ord | 184 | 1.000→1.000 | 6.00→8.67 | 14.1→31.9 | 0.0→0.0 |
| human_reaction | Disc2 | D/boss | 22 | 0.682→0.682 | 18.77→18.77 | 363.0→363.0 | 0.0→0.0 |
| human_reaction | Disc2 | G/ord | 184 | 1.000→1.000 | 10.29→10.29 | 33.1→33.1 | 0.0→0.0 |
| human_reaction | Disc2 | G/boss | 22 | 0.636→0.636 | 20.07→20.07 | 381.6→381.6 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 9.67→9.67 | 30.0→30.0 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/boss | 22 | 0.500→0.500 | 22.43→22.43 | 447.7→447.7 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 11.11→11.11 | 25.6→25.6 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/boss | 22 | 0.545→0.545 | 27.07→27.07 | 411.0→411.0 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 4.66→7.04 | 10.0→24.2 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/boss | 22 | 0.773→0.773 | 15.72→15.72 | 317.3→317.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 10.86→10.86 | 30.9→30.9 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/boss | 22 | 0.727→0.727 | 20.76→20.76 | 359.5→359.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/ord | 184 | 0.995→0.995 | 11.26→11.26 | 24.9→24.9 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/boss | 22 | 0.364→0.364 | 28.57→28.57 | 437.4→437.4 | 0.1→0.1 |
| far_player | D5 | C/ord | 20 | 1.000→1.000 | 22.65→22.65 | 36.2→36.2 | 0.0→0.0 |
| far_player | D5 | C/boss | 16 | 1.000→1.000 | 32.39→32.39 | 18.3→18.3 | 0.0→0.0 |
| far_player | D5 | D/ord | 20 | 1.000→1.000 | 22.33→22.33 | 33.9→33.9 | 0.0→0.0 |
| far_player | D5 | D/boss | 16 | 1.000→1.000 | 36.56→36.56 | 32.0→32.0 | 0.1→0.1 |
| far_player | D5 | G/ord | 20 | 1.000→1.000 | 19.23→19.23 | 36.1→36.1 | 0.0→0.0 |
| far_player | D5 | G/boss | 16 | 1.000→1.000 | 24.24→24.24 | 16.1→16.1 | 0.1→0.1 |
| far_player | D5 | controlled_grenade/ord | 20 | 1.000→1.000 | 22.65→22.65 | 36.2→36.2 | 0.0→0.0 |
| far_player | D5 | controlled_grenade/boss | 16 | 1.000→1.000 | 32.39→32.39 | 18.3→18.3 | 0.0→0.0 |
| far_player | D5 | controlled_handgun/ord | 20 | 1.000→1.000 | 25.09→25.09 | 50.8→50.8 | 0.0→0.0 |
| far_player | D5 | controlled_handgun/boss | 16 | 1.000→1.000 | 27.97→27.97 | 20.6→20.6 | 0.0→0.0 |
| far_player | D5 | controlled_machine/ord | 20 | 1.000→1.000 | 22.60→22.60 | 41.5→41.5 | 0.0→0.0 |
| far_player | D5 | controlled_machine/boss | 16 | 1.000→1.000 | 31.49→31.49 | 21.8→21.8 | 0.0→0.0 |
| far_player | D5 | controlled_rifle/ord | 20 | 1.000→1.000 | 29.21→29.21 | 61.7→61.7 | 0.0→0.0 |
| far_player | D5 | controlled_rifle/boss | 16 | 1.000→1.000 | 31.76→31.76 | 24.1→24.1 | 0.0→0.0 |
| far_player | D5 | controlled_shotgun/ord | 20 | 1.000→1.000 | 22.65→22.65 | 36.2→36.2 | 0.0→0.0 |
| far_player | D5 | controlled_shotgun/boss | 16 | 1.000→1.000 | 32.39→32.39 | 18.3→18.3 | 0.0→0.0 |
| far_player | Disc2 | C/ord | 184 | 1.000→1.000 | 7.77→7.77 | 20.3→20.3 | 0.0→0.0 |
| far_player | Disc2 | C/boss | 22 | 0.773→0.773 | 16.69→16.69 | 309.9→309.9 | 0.0→0.0 |
| far_player | Disc2 | D/ord | 184 | 1.000→1.000 | 4.21→6.46 | 6.0→22.7 | 0.0→0.0 |
| far_player | Disc2 | D/boss | 22 | 0.773→0.773 | 16.33→16.33 | 329.4→329.4 | 0.1→0.1 |
| far_player | Disc2 | G/ord | 184 | 1.000→1.000 | 7.02→7.02 | 18.6→18.6 | 0.0→0.0 |
| far_player | Disc2 | G/boss | 22 | 0.818→0.818 | 16.81→16.81 | 331.5→331.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/ord | 184 | 1.000→1.000 | 6.95→6.95 | 18.1→18.1 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/boss | 22 | 0.682→0.682 | 25.88→25.88 | 403.6→403.6 | 0.1→0.1 |
| far_player | Disc2 | controlled_handgun/ord | 184 | 1.000→1.000 | 6.34→6.34 | 12.3→12.3 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/boss | 22 | 0.727→0.727 | 22.02→22.02 | 345.8→345.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/ord | 184 | 1.000→1.000 | 2.88→4.50 | 2.5→12.3 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/boss | 22 | 0.818→0.818 | 11.20→11.20 | 226.0→226.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/ord | 184 | 1.000→1.000 | 7.77→7.77 | 19.5→19.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/boss | 22 | 0.727→0.727 | 16.71→16.71 | 319.3→319.3 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/ord | 184 | 1.000→1.000 | 7.19→7.19 | 17.1→17.1 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/boss | 22 | 0.727→0.727 | 24.03→24.03 | 380.0→380.0 | 0.2→0.2 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order G, controlled_handgun, controlled_machine, C, controlled_grenade, controlled_shotgun, controlled_rifle, D
- human_reaction: Spearman vs default 0.86; order G, controlled_handgun, controlled_machine, controlled_rifle, C, controlled_grenade, controlled_shotgun, D
- far_player: Spearman vs default 0.98; order G, controlled_handgun, controlled_machine, C, controlled_grenade, controlled_shotgun, D, controlled_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, G, D, C, controlled_rifle, controlled_handgun, controlled_grenade, controlled_shotgun
- human_reaction: Spearman vs default 0.79; order controlled_machine, C, controlled_rifle, D, G, controlled_handgun, controlled_grenade, controlled_shotgun
- far_player: Spearman vs default 0.95; order controlled_machine, G, D, C, controlled_handgun, controlled_rifle, controlled_shotgun, controlled_grenade
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

