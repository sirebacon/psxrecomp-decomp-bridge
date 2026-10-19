# Rule comparison: exp:AAo_40 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle (boss only).
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.491→0.491 (+0.000, [+0.000, +0.000]) | 16.77→16.77 | 443.5→443.5 | 23.6→23.6 | 0.1→0.1 | 0.509→0.509 | 0.19 | 0.61 |
| default | Disc2 | BOSS | 0.491→0.491 (+0.000, [+0.000, +0.000]) | 16.77→16.77 | 443.5→443.5 | 23.6→23.6 | 0.1→0.1 | 0.509→0.509 | 0.19 | 0.61 |
| human_reaction | Disc2 | ALL | 0.370→0.370 (+0.000, [+0.000, +0.000]) | 19.92→19.92 | 484.9→484.9 | 18.6→18.6 | 0.0→0.0 | 0.630→0.630 | 0.14 | 0.63 |
| human_reaction | Disc2 | BOSS | 0.370→0.370 (+0.000, [+0.000, +0.000]) | 19.92→19.92 | 484.9→484.9 | 18.6→18.6 | 0.0→0.0 | 0.630→0.630 | 0.14 | 0.63 |
| far_player | Disc2 | ALL | 0.491→0.491 (+0.000, [+0.000, +0.000]) | 18.68→18.68 | 442.2→442.2 | 26.6→26.6 | 0.1→0.1 | 0.509→0.509 | 0.18 | 0.61 |
| far_player | Disc2 | BOSS | 0.491→0.491 (+0.000, [+0.000, +0.000]) | 18.68→18.68 | 442.2→442.2 | 26.6→26.6 | 0.1→0.1 | 0.509→0.509 | 0.18 | 0.61 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | Disc2 | class_grenade/boss | 33 | 0.333→0.333 | 18.85→18.85 | 493.3→493.3 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.545→0.545 | 16.16→16.16 | 429.8→429.8 | 0.1→0.1 |
| default | Disc2 | class_machine/boss | 33 | 0.667→0.667 | 12.63→12.63 | 387.3→387.3 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.606→0.606 | 16.82→16.82 | 412.9→412.9 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 19.40→19.40 | 494.3→494.3 | 0.3→0.3 |
| human_reaction | Disc2 | class_grenade/boss | 33 | 0.273→0.273 | 20.95→20.95 | 514.0→514.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 33 | 0.364→0.364 | 20.66→20.66 | 477.6→477.6 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 33 | 0.515→0.515 | 15.77→15.77 | 442.5→442.5 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 33 | 0.424→0.424 | 20.87→20.87 | 477.3→477.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 33 | 0.273→0.273 | 21.33→21.33 | 513.1→513.1 | 0.2→0.2 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.333→0.333 | 20.52→20.52 | 497.4→497.4 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.606→0.606 | 18.50→18.50 | 403.7→403.7 | 0.1→0.1 |
| far_player | Disc2 | class_machine/boss | 33 | 0.636→0.636 | 15.14→15.14 | 405.1→405.1 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.545→0.545 | 17.41→17.41 | 417.6→417.6 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.333→0.333 | 21.83→21.83 | 487.3→487.3 | 0.4→0.4 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- human_reaction: Spearman vs default 1.00; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 0.90; order class_machine, class_handgun, class_rifle, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

