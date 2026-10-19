# Rule comparison: exp:AAo_40 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle (boss only).
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.552→0.552 (+0.000, [+0.000, +0.000]) | 21.36→21.36 | 386.1→386.1 | 29.0→29.0 | 0.2→0.2 | 0.418→0.418 | 0.00 | 0.60 |
| default | Disc2 | BOSS | 0.552→0.552 (+0.000, [+0.000, +0.000]) | 21.36→21.36 | 386.1→386.1 | 29.0→29.0 | 0.2→0.2 | 0.418→0.418 | 0.00 | 0.60 |
| human_reaction | Disc2 | ALL | 0.406→0.406 (+0.000, [+0.000, +0.000]) | 25.95→25.95 | 430.6→430.6 | 24.2→24.2 | 0.2→0.2 | 0.539→0.539 | 0.00 | 0.62 |
| human_reaction | Disc2 | BOSS | 0.406→0.406 (+0.000, [+0.000, +0.000]) | 25.95→25.95 | 430.6→430.6 | 24.2→24.2 | 0.2→0.2 | 0.539→0.539 | 0.00 | 0.62 |
| far_player | Disc2 | ALL | 0.545→0.545 (+0.000, [+0.000, +0.000]) | 23.86→23.86 | 385.4→385.4 | 33.7→33.7 | 0.2→0.2 | 0.418→0.418 | 0.00 | 0.61 |
| far_player | Disc2 | BOSS | 0.545→0.545 (+0.000, [+0.000, +0.000]) | 23.86→23.86 | 385.4→385.4 | 33.7→33.7 | 0.2→0.2 | 0.418→0.418 | 0.00 | 0.61 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | Disc2 | class_grenade/boss | 33 | 0.364→0.364 | 25.49→25.49 | 434.5→434.5 | 0.1→0.1 |
| default | Disc2 | class_handgun/boss | 33 | 0.636→0.636 | 20.08→20.08 | 370.7→370.7 | 0.2→0.2 |
| default | Disc2 | class_machine/boss | 33 | 0.758→0.758 | 14.47→14.47 | 331.5→331.5 | 0.1→0.1 |
| default | Disc2 | class_rifle/boss | 33 | 0.697→0.697 | 20.06→20.06 | 353.6→353.6 | 0.1→0.1 |
| default | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 26.69→26.69 | 440.2→440.2 | 0.7→0.7 |
| human_reaction | Disc2 | class_grenade/boss | 33 | 0.273→0.273 | 28.06→28.06 | 458.3→458.3 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/boss | 33 | 0.364→0.364 | 27.92→27.92 | 423.8→423.8 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/boss | 33 | 0.606→0.606 | 18.48→18.48 | 384.0→384.0 | 0.1→0.1 |
| human_reaction | Disc2 | class_rifle/boss | 33 | 0.515→0.515 | 26.88→26.88 | 427.4→427.4 | 0.1→0.1 |
| human_reaction | Disc2 | class_shotgun/boss | 33 | 0.273→0.273 | 28.40→28.40 | 459.6→459.6 | 0.4→0.4 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.333→0.333 | 27.28→27.28 | 439.2→439.2 | 0.1→0.1 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.697→0.697 | 23.14→23.14 | 347.5→347.5 | 0.2→0.2 |
| far_player | Disc2 | class_machine/boss | 33 | 0.727→0.727 | 18.07→18.07 | 349.8→349.8 | 0.2→0.2 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.636→0.636 | 21.55→21.55 | 357.8→357.8 | 0.1→0.1 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.333→0.333 | 29.28→29.28 | 432.6→432.6 | 0.7→0.7 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- human_reaction: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 0.90; order class_machine, class_handgun, class_rifle, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

