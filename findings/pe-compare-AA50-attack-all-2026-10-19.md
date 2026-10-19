# Rule comparison: exp:AA_50 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 8 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.995→0.953 (-0.042, [-0.073, -0.016]) | 6.25→7.86 | 40.3→64.3 | 8.7→15.6 | 0.0→0.0 | 0.005→0.047 | 0.00 | 0.27 |
| default | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 5.55→6.73 | 17.4→25.6 | 6.9→12.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.14 |
| default | Disc2 | BOSS | 0.938→0.438 (-0.500, [-0.750, -0.250]) | 13.96→20.34 | 292.1→490.5 | 29.1→47.2 | 0.0→0.0 | 0.062→0.562 | 0.00 | 0.70 |
| human_reaction | Disc2 | ALL | 0.958→0.927 (-0.031, [-0.057, -0.010]) | 10.67→12.42 | 74.6→97.6 | 8.6→13.9 | 0.0→0.0 | 0.042→0.073 | 0.00 | 0.25 |
| human_reaction | Disc2 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 9.80→11.51 | 33.1→49.2 | 7.1→12.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.14 |
| human_reaction | Disc2 | BOSS | 0.500→0.125 (-0.375, [-0.625, -0.125]) | 20.23→22.39 | 531.3→629.1 | 25.3→29.4 | 0.0→0.0 | 0.500→0.875 | 0.00 | 0.72 |
| far_player | Disc2 | ALL | 0.979→0.938 (-0.042, [-0.073, -0.016]) | 6.92→8.91 | 45.4→72.9 | 10.4→18.6 | 0.0→0.0 | 0.021→0.062 | 0.00 | 0.28 |
| far_player | Disc2 | ORDINARY | 0.994→0.994 (+0.000, [+0.000, +0.000]) | 6.12→7.67 | 21.0→30.4 | 8.4→15.6 | 0.0→0.0 | 0.006→0.006 | 0.00 | 0.17 |
| far_player | Disc2 | BOSS | 0.812→0.312 (-0.500, [-0.750, -0.250]) | 15.74→22.50 | 314.9→540.9 | 32.4→51.6 | 0.0→0.0 | 0.188→0.688 | 0.00 | 0.72 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order controlled_rifle, controlled_handgun, controlled_machine, D
- human_reaction: Spearman vs default 0.20; order controlled_rifle, D, controlled_machine, controlled_handgun
- far_player: Spearman vs default 1.00; order controlled_rifle, controlled_handgun, controlled_machine, D
- win-rate delta (proposal − baseline) by set: default -0.042, human_reaction -0.031, far_player -0.042

