# Rule comparison: exp:AAo_40 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.943→0.943 (+0.000, [+0.000, +0.000]) | 8.74→9.18 | 68.2→72.3 | 7.9→11.0 | 0.0→0.0 | 0.057→0.057 | 0.24 | 0.30 |
| default | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 7.65→8.14 | 23.0→27.7 | 5.9→9.4 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.20 |
| default | Disc2 | BOSS | 0.521→0.521 (+0.000, [+0.000, +0.000]) | 17.85→17.85 | 445.7→445.7 | 24.5→24.5 | 0.1→0.1 | 0.479→0.479 | 0.55 | 0.70 |
| human_reaction | Disc2 | ALL | 0.913→0.912 (-0.001, [-0.002, +0.000]) | 13.95→14.56 | 90.2→95.9 | 7.4→10.7 | 0.0→0.0 | 0.087→0.087 | 0.18 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.977→0.976 (-0.001, [-0.002, +0.000]) | 13.05→13.73 | 41.6→48.0 | 5.9→9.6 | 0.0→0.0 | 0.023→0.024 | 0.03 | 0.15 |
| human_reaction | Disc2 | BOSS | 0.376→0.376 (+0.000, [+0.000, +0.000]) | 21.49→21.49 | 496.6→496.6 | 19.9→19.9 | 0.1→0.1 | 0.618→0.618 | 0.55 | 0.65 |
| far_player | Disc2 | ALL | 0.936→0.936 (+0.000, [+0.000, +0.000]) | 9.64→10.13 | 69.9→74.3 | 9.0→12.7 | 0.0→0.0 | 0.063→0.063 | 0.27 | 0.30 |
| far_player | Disc2 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 8.51→9.06 | 23.3→28.3 | 7.0→11.1 | 0.0→0.0 | 0.007→0.007 | 0.02 | 0.19 |
| far_player | Disc2 | BOSS | 0.455→0.455 (+0.000, [+0.000, +0.000]) | 19.05→19.05 | 459.2→459.2 | 26.0→26.0 | 0.2→0.2 | 0.539→0.539 | 0.54 | 0.71 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
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

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_shotgun, class_grenade
- human_reaction: Spearman vs default 0.80; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 0.80; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction -0.001, far_player +0.000

