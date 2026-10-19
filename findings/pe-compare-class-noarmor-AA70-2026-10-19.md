# Rule comparison: exp:AA_70 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 6 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.472→0.472 (+0.000, [+0.000, +0.000]) | 18.68→18.68 | 229.5→229.5 | 8.4→8.4 | 0.1→0.1 | 0.528→0.528 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 0.565→0.565 (+0.000, [+0.000, +0.000]) | 20.26→20.26 | 213.4→213.4 | 9.0→9.0 | 0.1→0.1 | 0.435→0.435 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.308→0.308 (+0.000, [+0.000, +0.000]) | 15.88→15.88 | 257.9→257.9 | 7.2→7.2 | 0.1→0.1 | 0.692→0.692 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.856→0.839 (-0.017, [-0.039, +0.000]) | 9.29→9.51 | 142.9→153.7 | 7.2→8.7 | 0.0→0.0 | 0.144→0.161 | 0.00 | 0.23 |
| default | Disc2 | ORDINARY | 0.927→0.909 (-0.018, [-0.042, +0.000]) | 9.05→9.26 | 97.2→109.0 | 6.2→7.6 | 0.0→0.0 | 0.073→0.091 | 0.00 | 0.16 |
| default | Disc2 | BOSS | 0.067→0.067 (+0.000, [+0.000, +0.000]) | 11.88→12.25 | 645.1→645.1 | 19.1→21.0 | 0.1→0.1 | 0.933→0.933 | 0.00 | 0.70 |
| human_reaction | D5 | ALL | 0.289→0.289 (+0.000, [+0.000, +0.000]) | 20.40→20.40 | 266.1→266.1 | 6.3→6.3 | 0.1→0.1 | 0.711→0.711 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 0.313→0.313 (+0.000, [+0.000, +0.000]) | 22.06→22.06 | 260.1→260.1 | 6.7→6.7 | 0.0→0.0 | 0.687→0.687 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.246→0.246 (+0.000, [+0.000, +0.000]) | 17.48→17.48 | 276.7→276.7 | 5.4→5.4 | 0.1→0.1 | 0.754→0.754 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.806→0.789 (-0.017, [-0.039, +0.000]) | 13.95→14.08 | 192.0→199.8 | 6.7→7.7 | 0.0→0.0 | 0.194→0.211 | 0.00 | 0.17 |
| human_reaction | Disc2 | ORDINARY | 0.879→0.861 (-0.018, [-0.042, +0.000]) | 14.05→14.19 | 151.0→159.6 | 6.2→7.3 | 0.0→0.0 | 0.121→0.139 | 0.00 | 0.11 |
| human_reaction | Disc2 | BOSS | 0.000→0.000 (+0.000, [+0.000, +0.000]) | 12.86→12.86 | 642.7→642.7 | 12.6→12.6 | 0.0→0.0 | 1.000→1.000 | 0.00 | 0.71 |
| far_player | D5 | ALL | 0.500→0.500 (+0.000, [+0.000, +0.000]) | 21.28→21.28 | 210.9→210.9 | 9.6→9.6 | 0.2→0.2 | 0.500→0.500 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 0.617→0.617 (+0.000, [+0.000, +0.000]) | 23.30→23.30 | 183.7→183.7 | 10.5→10.5 | 0.2→0.2 | 0.383→0.383 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.292→0.292 (+0.000, [+0.000, +0.000]) | 17.72→17.72 | 258.9→258.9 | 8.1→8.1 | 0.2→0.2 | 0.708→0.708 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.850→0.833 (-0.017, [-0.039, +0.000]) | 10.12→10.32 | 135.2→144.4 | 8.6→10.4 | 0.0→0.0 | 0.150→0.167 | 0.00 | 0.23 |
| far_player | Disc2 | ORDINARY | 0.921→0.909 (-0.012, [-0.030, +0.000]) | 9.91→10.10 | 88.8→98.2 | 7.7→9.4 | 0.0→0.0 | 0.079→0.091 | 0.00 | 0.16 |
| far_player | Disc2 | BOSS | 0.067→0.000 (-0.067, [-0.200, +0.000]) | 12.35→12.75 | 645.9→653.2 | 19.3→20.8 | 0.1→0.1 | 0.933→1.000 | 0.00 | 0.71 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 23 | 0.478→0.478 | 22.49→22.49 | 238.6→238.6 | 0.1→0.1 |
| default | D5 | class_grenade/boss | 13 | 0.231→0.231 | 16.75→16.75 | 270.1→270.1 | 0.0→0.0 |
| default | D5 | class_handgun/ord | 23 | 0.739→0.739 | 19.15→19.15 | 174.8→174.8 | 0.1→0.1 |
| default | D5 | class_handgun/boss | 13 | 0.538→0.538 | 14.26→14.26 | 219.5→219.5 | 0.2→0.2 |
| default | D5 | class_machine/ord | 23 | 0.565→0.565 | 17.48→17.48 | 231.9→231.9 | 0.2→0.2 |
| default | D5 | class_machine/boss | 13 | 0.462→0.462 | 14.46→14.46 | 234.5→234.5 | 0.2→0.2 |
| default | D5 | class_rifle/ord | 23 | 0.217→0.217 | 20.99→20.99 | 268.1→268.1 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 13 | 0.154→0.154 | 17.23→17.23 | 286.3→286.3 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 23 | 0.826→0.826 | 21.18→21.18 | 153.8→153.8 | 0.0→0.0 |
| default | D5 | class_shotgun/boss | 13 | 0.154→0.154 | 16.71→16.71 | 279.2→279.2 | 0.1→0.1 |
| default | Disc2 | class_grenade/ord | 33 | 0.909→0.909 | 11.68→11.68 | 114.8→114.8 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 3 | 0.000→0.000 | 12.45→12.45 | 686.0→686.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/ord | 33 | 0.879→0.879 | 9.43→9.43 | 108.5→108.5 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 3 | 0.000→0.000 | 10.86→10.86 | 650.3→650.3 | 0.0→0.0 |
| default | Disc2 | class_machine/ord | 33 | 1.000→0.909 | 3.42→4.49 | 35.8→94.8 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 3 | 0.333→0.333 | 12.29→14.11 | 604.0→604.0 | 0.0→0.0 |
| default | Disc2 | class_rifle/ord | 33 | 0.939→0.939 | 11.81→11.81 | 117.3→117.3 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 3 | 0.000→0.000 | 10.86→10.86 | 660.3→660.3 | 0.0→0.0 |
| default | Disc2 | class_shotgun/ord | 33 | 0.909→0.909 | 8.90→8.90 | 109.8→109.8 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 3 | 0.000→0.000 | 12.94→12.94 | 625.0→625.0 | 0.3→0.3 |
| human_reaction | D5 | class_grenade/ord | 23 | 0.304→0.304 | 23.77→23.77 | 267.4→267.4 | 0.0→0.0 |
| human_reaction | D5 | class_grenade/boss | 13 | 0.231→0.231 | 18.62→18.62 | 282.6→282.6 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/ord | 23 | 0.435→0.435 | 20.70→20.70 | 224.0→224.0 | 0.0→0.0 |
| human_reaction | D5 | class_handgun/boss | 13 | 0.385→0.385 | 16.24→16.24 | 244.5→244.5 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 23 | 0.217→0.217 | 20.07→20.07 | 281.2→281.2 | 0.2→0.2 |
| human_reaction | D5 | class_machine/boss | 13 | 0.308→0.308 | 15.45→15.45 | 260.5→260.5 | 0.1→0.1 |
| human_reaction | D5 | class_rifle/ord | 23 | 0.174→0.174 | 22.13→22.13 | 285.3→285.3 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 13 | 0.077→0.077 | 18.14→18.14 | 309.5→309.5 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 23 | 0.435→0.435 | 23.63→23.63 | 242.7→242.7 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/boss | 13 | 0.231→0.231 | 18.93→18.93 | 286.4→286.4 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/ord | 33 | 0.848→0.848 | 17.38→17.38 | 169.6→169.6 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 3 | 0.000→0.000 | 10.19→10.19 | 613.0→613.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/ord | 33 | 0.909→0.909 | 15.91→15.91 | 150.5→150.5 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 3 | 0.000→0.000 | 16.38→16.38 | 660.3→660.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/ord | 33 | 0.970→0.879 | 6.76→7.43 | 96.4→139.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 3 | 0.000→0.000 | 10.86→10.86 | 644.0→644.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/ord | 33 | 0.848→0.848 | 16.73→16.73 | 164.8→164.8 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 3 | 0.000→0.000 | 12.99→12.99 | 678.0→678.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/ord | 33 | 0.818→0.818 | 13.49→13.49 | 173.9→173.9 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 3 | 0.000→0.000 | 13.87→13.87 | 618.3→618.3 | 0.0→0.0 |
| far_player | D5 | class_grenade/ord | 23 | 0.522→0.522 | 25.26→25.26 | 194.5→194.5 | 0.2→0.2 |
| far_player | D5 | class_grenade/boss | 13 | 0.231→0.231 | 17.93→17.93 | 275.4→275.4 | 0.0→0.0 |
| far_player | D5 | class_handgun/ord | 23 | 0.870→0.870 | 20.04→20.04 | 138.2→138.2 | 0.1→0.1 |
| far_player | D5 | class_handgun/boss | 13 | 0.462→0.462 | 15.50→15.50 | 226.6→226.6 | 0.2→0.2 |
| far_player | D5 | class_machine/ord | 23 | 0.435→0.435 | 18.99→18.99 | 222.0→222.0 | 0.5→0.5 |
| far_player | D5 | class_machine/boss | 13 | 0.462→0.462 | 16.31→16.31 | 238.8→238.8 | 0.4→0.4 |
| far_player | D5 | class_rifle/ord | 23 | 0.478→0.478 | 26.76→26.76 | 226.9→226.9 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 13 | 0.231→0.231 | 20.76→20.76 | 269.5→269.5 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 23 | 0.783→0.783 | 25.42→25.42 | 137.0→137.0 | 0.1→0.1 |
| far_player | D5 | class_shotgun/boss | 13 | 0.077→0.077 | 18.10→18.10 | 284.0→284.0 | 0.2→0.2 |
| far_player | Disc2 | class_grenade/ord | 33 | 0.909→0.909 | 12.28→12.28 | 101.5→101.5 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 3 | 0.000→0.000 | 12.45→12.45 | 686.0→686.0 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/ord | 33 | 0.879→0.879 | 10.63→10.63 | 90.4→90.4 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 3 | 0.000→0.000 | 11.86→11.86 | 694.3→694.3 | 0.0→0.0 |
| far_player | Disc2 | class_machine/ord | 33 | 0.970→0.909 | 4.78→5.70 | 52.6→99.6 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 3 | 0.333→0.000 | 11.35→13.38 | 592.0→628.7 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/ord | 33 | 0.939→0.939 | 11.30→11.30 | 95.6→95.6 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 3 | 0.000→0.000 | 11.86→11.86 | 650.3→650.3 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/ord | 33 | 0.909→0.909 | 10.57→10.57 | 103.8→103.8 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 3 | 0.000→0.000 | 14.20→14.20 | 606.7→606.7 | 0.3→0.3 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_handgun, class_shotgun, class_machine, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_shotgun, class_grenade, class_machine, class_rifle
- far_player: Spearman vs default 1.00; order class_handgun, class_shotgun, class_machine, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_rifle, class_shotgun, class_grenade, class_handgun
- human_reaction: Spearman vs default -0.10; order class_handgun, class_machine, class_rifle, class_grenade, class_shotgun
- far_player: Spearman vs default 0.90; order class_rifle, class_machine, class_shotgun, class_grenade, class_handgun
- win-rate delta (proposal − baseline) by set: default -0.017, human_reaction -0.017, far_player -0.017

