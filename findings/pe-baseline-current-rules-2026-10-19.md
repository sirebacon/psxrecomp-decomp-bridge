# Rule comparison: baseline vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 8 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.74→22.74 | 48.4→48.4 | 10.0→10.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 20.92→20.92 | 52.6→52.6 | 9.5→9.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.56→24.56 | 44.1→44.1 | 10.6→10.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.977→0.977 (+0.000, [+0.000, +0.000]) | 6.30→6.30 | 45.5→45.5 | 5.6→5.6 | 0.0→0.0 | 0.023→0.023 | 0.04 | 0.28 |
| default | Disc2 | ORDINARY | 0.989→0.989 (+0.000, [+0.000, +0.000]) | 5.66→5.66 | 17.5→17.5 | 4.6→4.6 | 0.0→0.0 | 0.011→0.011 | 0.06 | 0.12 |
| default | Disc2 | BOSS | 0.844→0.844 (+0.000, [+0.000, +0.000]) | 13.33→13.33 | 353.1→353.1 | 16.5→16.5 | 0.0→0.0 | 0.156→0.156 | 0.00 | 0.75 |
| late | D5 | ALL | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.66→22.66 | 47.7→47.7 | 10.0→10.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| late | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 20.86→20.86 | 52.1→52.1 | 9.4→9.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| late | D5 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.45→24.45 | 43.3→43.3 | 10.5→10.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| late | Disc2 | ALL | 0.977→0.977 (+0.000, [+0.000, +0.000]) | 6.30→6.30 | 44.3→44.3 | 5.7→5.7 | 0.0→0.0 | 0.023→0.023 | 0.05 | 0.31 |
| late | Disc2 | ORDINARY | 0.989→0.989 (+0.000, [+0.000, +0.000]) | 5.68→5.68 | 16.4→16.4 | 4.7→4.7 | 0.0→0.0 | 0.011→0.011 | 0.07 | 0.13 |
| late | Disc2 | BOSS | 0.844→0.844 (+0.000, [+0.000, +0.000]) | 13.17→13.17 | 351.2→351.2 | 16.3→16.3 | 0.0→0.0 | 0.156→0.156 | 0.00 | 0.79 |
| human_reaction | D5 | ALL | 0.992→0.992 (+0.000, [+0.000, +0.000]) | 33.22→33.22 | 86.2→86.2 | 10.0→10.0 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 31.22→31.22 | 95.3→95.3 | 9.8→9.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.984→0.984 (+0.000, [+0.000, +0.000]) | 35.21→35.21 | 77.0→77.0 | 10.3→10.3 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.948→0.948 (+0.000, [+0.000, +0.000]) | 9.98→9.98 | 64.1→64.1 | 5.3→5.3 | 0.0→0.0 | 0.052→0.052 | 0.05 | 0.22 |
| human_reaction | Disc2 | ORDINARY | 0.986→0.986 (+0.000, [+0.000, +0.000]) | 9.32→9.32 | 26.4→26.4 | 4.5→4.5 | 0.0→0.0 | 0.014→0.014 | 0.06 | 0.10 |
| human_reaction | Disc2 | BOSS | 0.531→0.531 (+0.000, [+0.000, +0.000]) | 17.22→17.22 | 478.8→478.8 | 13.4→13.4 | 0.0→0.0 | 0.469→0.469 | 0.00 | 0.66 |
| far_player | D5 | ALL | 0.997→0.997 (+0.000, [+0.000, +0.000]) | 25.36→25.36 | 51.5→51.5 | 11.1→11.1 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.05→22.05 | 50.2→50.2 | 10.5→10.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.995→0.995 (+0.000, [+0.000, +0.000]) | 28.67→28.67 | 52.9→52.9 | 11.8→11.8 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.961→0.961 (+0.000, [+0.000, +0.000]) | 6.99→6.99 | 51.1→51.1 | 6.4→6.4 | 0.0→0.0 | 0.039→0.039 | 0.05 | 0.28 |
| far_player | Disc2 | ORDINARY | 0.989→0.989 (+0.000, [+0.000, +0.000]) | 6.26→6.26 | 18.3→18.3 | 5.3→5.3 | 0.0→0.0 | 0.011→0.011 | 0.08 | 0.11 |
| far_player | Disc2 | BOSS | 0.656→0.656 (+0.000, [+0.000, +0.000]) | 14.98→14.98 | 412.4→412.4 | 17.8→17.8 | 0.0→0.0 | 0.344→0.344 | 0.00 | 0.72 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order G, controlled_handgun, C, controlled_shotgun, controlled_machine, controlled_rifle, controlled_grenade, D
- late: Spearman vs default 1.00; order G, controlled_handgun, C, controlled_shotgun, controlled_machine, controlled_rifle, controlled_grenade, D
- human_reaction: Spearman vs default 0.48; order G, C, controlled_shotgun, controlled_grenade, D, controlled_handgun, controlled_machine, controlled_rifle
- far_player: Spearman vs default 0.43; order G, C, controlled_shotgun, controlled_rifle, controlled_grenade, controlled_machine, D, controlled_handgun
- win-rate delta (proposal − baseline) by set: default +0.000, late +0.000, human_reaction +0.000, far_player +0.000

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, D, G, controlled_rifle, C, controlled_shotgun, controlled_handgun, controlled_grenade
- late: Spearman vs default 1.00; order controlled_machine, D, G, controlled_rifle, C, controlled_shotgun, controlled_handgun, controlled_grenade
- human_reaction: Spearman vs default 0.81; order G, controlled_machine, C, controlled_rifle, D, controlled_shotgun, controlled_handgun, controlled_grenade
- far_player: Spearman vs default 1.00; order controlled_machine, D, G, C, controlled_rifle, controlled_shotgun, controlled_handgun, controlled_grenade
- win-rate delta (proposal − baseline) by set: default +0.000, late +0.000, human_reaction +0.000, far_player +0.000

