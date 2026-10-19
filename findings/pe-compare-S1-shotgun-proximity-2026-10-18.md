# Rule comparison: exp:C1s_40 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 4 seeds x 4 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

| Assumptions | Stage | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|
| default | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 21.63→21.63 | 28.1→28.1 | 9.5→9.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | 0.945→0.945 (+0.000, [+0.000, +0.000]) | 8.39→8.39 | 64.4→65.7 | 9.4→9.4 | 0.0→0.0 | 0.055→0.055 | 0.59 | 0.45 |
| late | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 21.42→21.42 | 27.0→27.0 | 9.4→9.4 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| late | Disc2 | 0.969→0.969 (+0.000, [+0.000, +0.000]) | 8.49→8.43 | 60.0→60.2 | 9.6→9.5 | 0.0→0.0 | 0.031→0.031 | 0.60 | 0.51 |
| untimed_long | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 21.63→21.63 | 28.1→28.1 | 9.5→9.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| untimed_long | Disc2 | 0.984→0.984 (+0.000, [+0.000, +0.000]) | 8.99→8.92 | 47.8→48.3 | 10.1→10.0 | 0.0→0.0 | 0.016→0.016 | 0.49 | 0.38 |
| human_reaction | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 31.76→31.76 | 62.5→62.5 | 9.6→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | 0.898→0.898 (+0.000, [+0.000, +0.000]) | 12.71→12.70 | 97.8→97.3 | 8.9→8.9 | 0.0→0.0 | 0.102→0.102 | 0.57 | 0.31 |
| far_player | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 25.16→25.16 | 37.1→37.1 | 10.7→10.7 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | 0.930→0.930 (+0.000, [+0.000, +0.000]) | 9.15→9.20 | 66.7→67.2 | 10.8→10.8 | 0.0→0.0 | 0.070→0.070 | 0.58 | 0.47 |
| geometry_upper | D5 | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 22.09→22.09 | 48.0→48.0 | 9.6→9.6 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.00 |
| geometry_upper | Disc2 | 0.945→0.945 (+0.000, [+0.000, +0.000]) | 8.39→8.39 | 64.4→65.7 | 9.4→9.4 | 0.0→0.0 | 0.055→0.055 | 0.59 | 0.45 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order G, controlled_handgun, C, controlled_shotgun, controlled_rifle, controlled_machine, controlled_grenade, D
- late: Spearman vs default 0.98; order G, controlled_handgun, C, controlled_shotgun, controlled_machine, controlled_rifle, controlled_grenade, D
- untimed_long: Spearman vs default 1.00; order G, controlled_handgun, C, controlled_shotgun, controlled_rifle, controlled_machine, controlled_grenade, D
- human_reaction: Spearman vs default 1.00; order G, controlled_handgun, C, controlled_shotgun, controlled_rifle, controlled_machine, controlled_grenade, D
- far_player: Spearman vs default 0.98; order G, controlled_handgun, C, controlled_shotgun, controlled_machine, controlled_rifle, controlled_grenade, D
- geometry_upper: Spearman vs default 0.98; order G, controlled_handgun, C, controlled_shotgun, controlled_machine, controlled_rifle, controlled_grenade, D
- win-rate delta (proposal − baseline) by set: default +0.000, late +0.000, untimed_long +0.000, human_reaction +0.000, far_player +0.000, geometry_upper +0.000

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, G, D, controlled_shotgun, controlled_handgun, C, controlled_rifle, controlled_grenade
- late: Spearman vs default 0.79; order controlled_machine, D, G, C, controlled_rifle, controlled_shotgun, controlled_handgun, controlled_grenade
- untimed_long: Spearman vs default 0.90; order controlled_machine, D, G, controlled_shotgun, controlled_handgun, controlled_grenade, controlled_rifle, C
- human_reaction: Spearman vs default 0.55; order controlled_machine, D, G, controlled_grenade, C, controlled_rifle, controlled_shotgun, controlled_handgun
- far_player: Spearman vs default 0.76; order controlled_machine, G, D, C, controlled_rifle, controlled_handgun, controlled_shotgun, controlled_grenade
- geometry_upper: Spearman vs default 1.00; order controlled_machine, G, D, controlled_shotgun, controlled_handgun, C, controlled_rifle, controlled_grenade
- win-rate delta (proposal − baseline) by set: default +0.000, late +0.000, untimed_long +0.000, human_reaction +0.000, far_player +0.000, geometry_upper +0.000

