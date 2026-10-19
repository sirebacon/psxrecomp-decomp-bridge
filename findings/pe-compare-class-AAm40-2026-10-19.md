# Rule comparison: exp:AAm_40 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 6 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 28.11→28.11 | 63.5→63.5 | 11.7→11.7 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 25.12→25.12 | 67.2→67.2 | 11.2→11.2 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.985→0.985 (+0.000, [+0.000, +0.000]) | 33.40→33.40 | 57.0→57.0 | 12.6→12.6 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.956→0.950 (-0.006, [-0.017, +0.000]) | 9.56→10.32 | 76.6→85.9 | 7.7→13.0 | 0.0→0.0 | 0.044→0.050 | 0.00 | 0.34 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 8.83→9.63 | 35.9→43.0 | 6.1→11.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.25 |
| default | Disc2 | BOSS | 0.467→0.400 (-0.067, [-0.200, +0.000]) | 17.61→17.88 | 524.6→558.5 | 25.3→27.3 | 0.1→0.1 | 0.533→0.600 | 0.00 | 0.70 |
| human_reaction | D5 | ALL | 0.967→0.967 (+0.000, [+0.000, +0.000]) | 38.74→38.74 | 99.7→99.7 | 12.0→12.0 | 0.3→0.3 | 0.006→0.006 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 0.991→0.991 (+0.000, [+0.000, +0.000]) | 36.16→36.16 | 113.5→113.5 | 11.9→11.9 | 0.3→0.3 | 0.009→0.009 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.923→0.923 (+0.000, [+0.000, +0.000]) | 43.30→43.30 | 75.3→75.3 | 12.2→12.2 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.906→0.906 (+0.000, [+0.000, +0.000]) | 15.37→16.25 | 106.2→114.8 | 7.4→11.9 | 0.0→0.0 | 0.094→0.094 | 0.00 | 0.27 |
| human_reaction | Disc2 | ORDINARY | 0.976→0.976 (+0.000, [+0.000, +0.000]) | 14.83→15.80 | 56.8→66.1 | 6.3→11.2 | 0.0→0.0 | 0.024→0.024 | 0.00 | 0.19 |
| human_reaction | Disc2 | BOSS | 0.133→0.133 (+0.000, [+0.000, +0.000]) | 21.23→21.23 | 649.7→650.7 | 19.7→19.8 | 0.1→0.1 | 0.867→0.867 | 0.00 | 0.73 |
| far_player | D5 | ALL | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 31.62→31.62 | 64.5→64.5 | 13.6→13.6 | 0.4→0.4 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 27.83→27.83 | 64.8→64.8 | 13.2→13.2 | 0.4→0.4 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.985→0.985 (+0.000, [+0.000, +0.000]) | 38.33→38.33 | 63.9→63.9 | 14.4→14.4 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.944→0.939 (-0.006, [-0.017, +0.000]) | 10.47→11.39 | 81.3→90.8 | 9.1→15.3 | 0.0→0.0 | 0.056→0.061 | 0.00 | 0.33 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.76→10.76 | 35.8→43.0 | 7.6→14.2 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.24 |
| far_player | Disc2 | BOSS | 0.333→0.267 (-0.067, [-0.200, +0.000]) | 18.25→18.35 | 581.7→615.5 | 25.9→27.3 | 0.2→0.2 | 0.667→0.733 | 0.00 | 0.72 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 23 | 1.000→1.000 | 29.77→29.77 | 82.3→82.3 | 0.5→0.5 |
| default | D5 | class_grenade/boss | 13 | 1.000→1.000 | 36.14→36.14 | 72.2→72.2 | 0.2→0.2 |
| default | D5 | class_handgun/ord | 23 | 1.000→1.000 | 18.78→18.78 | 37.7→37.7 | 0.1→0.1 |
| default | D5 | class_handgun/boss | 13 | 1.000→1.000 | 24.28→24.28 | 30.7→30.7 | 0.3→0.3 |
| default | D5 | class_machine/ord | 23 | 1.000→1.000 | 19.06→19.06 | 55.4→55.4 | 0.4→0.4 |
| default | D5 | class_machine/boss | 13 | 1.000→1.000 | 22.15→22.15 | 35.7→35.7 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 23 | 1.000→1.000 | 36.22→36.22 | 116.3→116.3 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 13 | 0.923→0.923 | 48.39→48.39 | 83.7→83.7 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 23 | 1.000→1.000 | 21.79→21.79 | 44.0→44.0 | 0.1→0.1 |
| default | D5 | class_shotgun/boss | 13 | 1.000→1.000 | 36.05→36.05 | 62.8→62.8 | 0.5→0.5 |
| default | Disc2 | class_grenade/ord | 33 | 1.000→1.000 | 11.57→11.57 | 46.3→46.3 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 3 | 0.333→0.333 | 22.42→22.42 | 674.0→674.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/ord | 33 | 1.000→1.000 | 9.32→9.32 | 38.9→38.9 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 3 | 0.667→0.667 | 19.02→19.02 | 500.0→500.0 | 0.0→0.0 |
| default | Disc2 | class_machine/ord | 33 | 1.000→1.000 | 3.20→7.22 | 12.8→48.2 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 3 | 0.667→0.333 | 12.60→13.93 | 411.0→580.3 | 0.0→0.0 |
| default | Disc2 | class_rifle/ord | 33 | 1.000→1.000 | 11.41→11.41 | 43.8→43.8 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 3 | 0.333→0.333 | 14.35→14.35 | 493.0→493.0 | 0.0→0.0 |
| default | Disc2 | class_shotgun/ord | 33 | 1.000→1.000 | 8.65→8.65 | 37.7→37.7 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 3 | 0.333→0.333 | 19.68→19.68 | 545.0→545.0 | 0.3→0.3 |
| human_reaction | D5 | class_grenade/ord | 23 | 1.000→1.000 | 40.43→40.43 | 130.1→130.1 | 0.5→0.5 |
| human_reaction | D5 | class_grenade/boss | 13 | 0.846→0.846 | 45.42→45.42 | 77.5→77.5 | 0.2→0.2 |
| human_reaction | D5 | class_handgun/ord | 23 | 1.000→1.000 | 28.44→28.44 | 77.7→77.7 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 13 | 1.000→1.000 | 33.36→33.36 | 48.5→48.5 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 23 | 1.000→1.000 | 30.80→30.80 | 107.6→107.6 | 0.6→0.6 |
| human_reaction | D5 | class_machine/boss | 13 | 1.000→1.000 | 33.15→33.15 | 55.7→55.7 | 0.6→0.6 |
| human_reaction | D5 | class_rifle/ord | 23 | 0.957→0.957 | 48.76→48.76 | 153.6→153.6 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 13 | 0.846→0.846 | 59.77→59.77 | 112.5→112.5 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 23 | 1.000→1.000 | 32.36→32.36 | 98.3→98.3 | 0.3→0.3 |
| human_reaction | D5 | class_shotgun/boss | 13 | 0.923→0.923 | 44.80→44.80 | 82.5→82.5 | 0.5→0.5 |
| human_reaction | Disc2 | class_grenade/ord | 33 | 0.970→0.970 | 17.98→17.98 | 60.0→60.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 3 | 0.000→0.000 | 18.13→18.13 | 676.7→676.7 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/ord | 33 | 0.970→0.970 | 16.11→16.11 | 54.8→54.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 3 | 0.333→0.333 | 27.21→27.21 | 625.7→625.7 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/ord | 33 | 1.000→1.000 | 5.86→10.68 | 21.6→67.9 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 3 | 0.000→0.000 | 16.87→16.87 | 657.7→663.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/ord | 33 | 0.970→0.970 | 18.17→18.17 | 72.1→72.1 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 3 | 0.333→0.333 | 21.07→21.07 | 609.0→609.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/ord | 33 | 0.970→0.970 | 16.05→16.05 | 75.5→75.5 | 0.1→0.1 |
| human_reaction | Disc2 | class_shotgun/boss | 3 | 0.000→0.000 | 22.88→22.88 | 679.3→679.3 | 0.3→0.3 |
| far_player | D5 | class_grenade/ord | 23 | 1.000→1.000 | 30.99→30.99 | 77.5→77.5 | 0.5→0.5 |
| far_player | D5 | class_grenade/boss | 13 | 1.000→1.000 | 40.93→40.93 | 67.1→67.1 | 0.3→0.3 |
| far_player | D5 | class_handgun/ord | 23 | 1.000→1.000 | 20.14→20.14 | 35.7→35.7 | 0.3→0.3 |
| far_player | D5 | class_handgun/boss | 13 | 1.000→1.000 | 29.49→29.49 | 42.6→42.6 | 0.7→0.7 |
| far_player | D5 | class_machine/ord | 23 | 1.000→1.000 | 24.55→24.55 | 65.1→65.1 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 13 | 1.000→1.000 | 25.12→25.12 | 40.0→40.0 | 0.5→0.5 |
| far_player | D5 | class_rifle/ord | 23 | 1.000→1.000 | 36.17→36.17 | 98.2→98.2 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 13 | 0.923→0.923 | 49.69→49.69 | 84.2→84.2 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 23 | 1.000→1.000 | 27.30→27.30 | 47.7→47.7 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 13 | 1.000→1.000 | 46.40→46.40 | 85.8→85.8 | 0.8→0.8 |
| far_player | Disc2 | class_grenade/ord | 33 | 1.000→1.000 | 12.00→12.00 | 42.9→42.9 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 3 | 0.000→0.000 | 23.65→23.65 | 685.7→685.7 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/ord | 33 | 1.000→1.000 | 10.25→10.25 | 35.0→35.0 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 3 | 0.333→0.333 | 16.74→16.74 | 674.7→674.7 | 0.3→0.3 |
| far_player | Disc2 | class_machine/ord | 33 | 1.000→1.000 | 4.37→9.36 | 19.3→55.5 | 0.0→0.1 |
| far_player | Disc2 | class_machine/boss | 3 | 0.667→0.333 | 12.92→13.38 | 411.0→580.3 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/ord | 33 | 1.000→1.000 | 11.56→11.56 | 42.3→42.3 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 3 | 0.333→0.333 | 15.40→15.40 | 529.3→529.3 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/ord | 33 | 1.000→1.000 | 10.61→10.61 | 39.5→39.5 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 3 | 0.333→0.333 | 22.56→22.56 | 607.7→607.7 | 0.7→0.7 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- far_player: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order class_handgun, class_machine, class_shotgun, class_rifle, class_grenade
- human_reaction: Spearman vs default 0.80; order class_machine, class_handgun, class_rifle, class_shotgun, class_grenade
- far_player: Spearman vs default 0.90; order class_machine, class_handgun, class_shotgun, class_rifle, class_grenade
- win-rate delta (proposal − baseline) by set: default -0.006, human_reaction +0.000, far_player -0.006

