# Rule comparison: exp:AAo_30 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle (ordinary only).
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player | Disc2 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 13.09→14.43 | 10.4→15.4 | 5.9→13.0 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.10 |
| logged_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 13.09→14.43 | 10.4→15.4 | 5.9→13.0 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.10 |
| default | Disc2 | ALL | 1.000→0.998 (-0.002, [-0.005, +0.000]) | 7.65→8.64 | 11.2→18.4 | 5.9→13.1 | 0.0→0.0 | 0.000→0.002 | 0.02 | 0.10 |
| default | Disc2 | ORDINARY | 1.000→0.998 (-0.002, [-0.005, +0.000]) | 7.65→8.64 | 11.2→18.4 | 5.9→13.1 | 0.0→0.0 | 0.000→0.002 | 0.02 | 0.10 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 15.72→15.72 | 11.3→11.3 | 0.0→0.0 |
| logged_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 13.96→13.96 | 9.4→9.4 | 0.0→0.0 |
| logged_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 5.82→12.56 | 3.6→28.6 | 0.0→0.0 |
| logged_player | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 15.96→15.96 | 12.7→12.7 | 0.0→0.0 |
| logged_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.97→13.97 | 15.0→15.0 | 0.0→0.0 |
| default | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 9.38→9.38 | 11.8→11.8 | 0.0→0.0 |
| default | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 7.71→7.71 | 9.6→9.6 | 0.0→0.0 |
| default | Disc2 | class_machine/ord | 276 | 1.000→0.989 | 3.24→8.18 | 3.5→39.5 | 0.0→0.0 |
| default | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 9.57→9.57 | 16.6→16.6 | 0.0→0.0 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 8.38→8.38 | 14.7→14.7 | 0.0→0.0 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player: Spearman vs default 0.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- default: Spearman vs default 1.00; order class_handgun, class_shotgun, class_grenade, class_rifle, class_machine
- win-rate delta (proposal − baseline) by set: logged_player +0.000, default -0.002

