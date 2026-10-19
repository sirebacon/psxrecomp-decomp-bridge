# Rule comparison: exp:AAm_60 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 8 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.958→0.958 (+0.000, [+0.000, +0.000]) | 5.80→6.16 | 53.7→55.4 | 7.8→9.9 | 0.0→0.0 | 0.042→0.042 | 0.07 | 0.23 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.19→5.54 | 12.3→14.1 | 6.2→8.3 | 0.0→0.0 | 0.000→0.000 | 0.02 | 0.13 |
| default | Disc2 | BOSS | 0.667→0.667 (+0.000, [+0.000, +0.000]) | 10.09→10.53 | 344.0→344.8 | 18.9→21.3 | 0.0→0.0 | 0.333→0.333 | 0.15 | 0.49 |
| human_reaction | Disc2 | ALL | 0.938→0.938 (+0.000, [+0.000, +0.000]) | 9.84→10.44 | 65.8→70.6 | 7.7→10.1 | 0.0→0.0 | 0.062→0.062 | 0.05 | 0.15 |
| human_reaction | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.26→9.82 | 19.1→24.1 | 6.7→9.1 | 0.0→0.0 | 0.000→0.000 | 0.03 | 0.07 |
| human_reaction | Disc2 | BOSS | 0.500→0.500 (+0.000, [+0.000, +0.000]) | 13.91→14.75 | 392.8→396.6 | 14.6→17.0 | 0.0→0.0 | 0.500→0.500 | 0.10 | 0.41 |
| far_player | Disc2 | ALL | 0.958→0.958 (+0.000, [+0.000, +0.000]) | 6.84→7.19 | 56.5→57.7 | 9.6→11.7 | 0.0→0.0 | 0.042→0.042 | 0.08 | 0.22 |
| far_player | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.98→6.28 | 14.0→15.3 | 8.1→10.0 | 0.0→0.0 | 0.000→0.000 | 0.05 | 0.12 |
| far_player | Disc2 | BOSS | 0.667→0.667 (+0.000, [+0.000, +0.000]) | 12.87→13.55 | 354.5→354.5 | 20.2→23.8 | 0.0→0.0 | 0.333→0.333 | 0.14 | 0.45 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, D, controlled_rifle, controlled_handgun
- human_reaction: Spearman vs default 0.40; order controlled_machine, controlled_rifle, controlled_handgun, D
- far_player: Spearman vs default 0.40; order controlled_rifle, controlled_machine, D, controlled_handgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction +0.000, far_player +0.000

