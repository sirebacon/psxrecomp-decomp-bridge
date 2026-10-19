# Rule comparison: exp:AAo_30 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle (ordinary only).
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 11.89→13.39 | 7.0→9.3 | 5.9→12.6 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.00 |
| logged_player_serial | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 11.89→13.39 | 7.0→9.3 | 5.9→12.6 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.00 |
| default | Disc2 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.67→11.04 | 7.0→9.3 | 5.9→12.6 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.00 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.67→11.04 | 7.0→9.3 | 5.9→12.6 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| logged_player_serial | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 14.57→14.57 | 11.0→11.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 12.00→12.00 | 6.9→6.9 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.87→12.35 | 0.8→12.4 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 14.99→14.99 | 10.0→10.0 | 0.0→0.0 |
| logged_player_serial | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 13.02→13.02 | 6.3→6.3 | 0.0→0.0 |
| default | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 11.92→11.92 | 11.0→11.0 | 0.0→0.0 |
| default | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 9.39→9.39 | 6.9→6.9 | 0.0→0.0 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.75→10.59 | 0.8→12.4 | 0.0→0.0 |
| default | Disc2 | class_rifle/ord | 276 | 1.000→1.000 | 12.41→12.41 | 10.0→10.0 | 0.0→0.0 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 10.89→10.89 | 6.3→6.3 | 0.0→0.0 |

## Build ranking stability across assumption sets

**Disc2**
- logged_player_serial: Spearman vs default 1.00; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- default: Spearman vs default 1.00; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: logged_player_serial +0.000, default +0.000

