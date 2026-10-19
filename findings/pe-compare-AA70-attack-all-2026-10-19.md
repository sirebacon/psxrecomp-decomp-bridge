# Rule comparison: exp:AA_70 vs baseline — October 18, 2026

Fixed frozen builds, campaign-frequency encounters (logged won battles), matched seeds; 8 seeds x 6 fights per build and stage.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | Disc2 | ALL | 0.995→0.995 (+0.000, [+0.000, +0.000]) | 5.84→6.06 | 29.0→31.2 | 5.1→6.0 | 0.0→0.0 | 0.005→0.005 | 0.00 | 0.24 |
| default | Disc2 | ORDINARY | 0.995→0.995 (+0.000, [+0.000, +0.000]) | 5.55→5.71 | 22.9→24.2 | 4.6→5.4 | 0.0→0.0 | 0.005→0.005 | 0.00 | 0.22 |
| default | Disc2 | BOSS | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 12.49→14.11 | 169.1→191.6 | 15.0→20.5 | 0.0→0.0 | 0.000→0.000 | 0.00 | 0.50 |
| human_reaction | Disc2 | ALL | 0.982→0.979 (-0.003, [-0.008, +0.000]) | 9.94→10.27 | 50.4→53.1 | 5.2→6.1 | 0.0→0.0 | 0.018→0.021 | 0.00 | 0.18 |
| human_reaction | Disc2 | ORDINARY | 0.984→0.984 (+0.000, [+0.000, +0.000]) | 9.58→9.86 | 42.1→43.9 | 4.8→5.6 | 0.0→0.0 | 0.016→0.016 | 0.00 | 0.17 |
| human_reaction | Disc2 | BOSS | 0.938→0.875 (-0.062, [-0.188, +0.000]) | 18.18→19.88 | 242.2→265.0 | 14.2→16.9 | 0.0→0.0 | 0.062→0.125 | 0.00 | 0.42 |
| far_player | Disc2 | ALL | 0.984→0.984 (+0.000, [+0.000, +0.000]) | 6.55→6.86 | 30.9→33.6 | 5.8→7.1 | 0.0→0.0 | 0.016→0.016 | 0.00 | 0.23 |
| far_player | Disc2 | ORDINARY | 0.986→0.986 (+0.000, [+0.000, +0.000]) | 6.21→6.45 | 24.8→26.6 | 5.4→6.5 | 0.0→0.0 | 0.014→0.014 | 0.00 | 0.21 |
| far_player | Disc2 | BOSS | 0.938→0.938 (+0.000, [+0.000, +0.000]) | 14.21→16.17 | 170.3→195.5 | 14.5→19.2 | 0.0→0.0 | 0.062→0.062 | 0.00 | 0.47 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | Disc2 | C/ord | 46 | 0.978→0.978 | 7.76→7.76 | 37.6→37.6 | 0.0→0.0 |
| default | Disc2 | C/boss | 2 | 1.000→1.000 | 10.85→10.85 | 151.0→151.0 | 0.0→0.0 |
| default | Disc2 | D/ord | 46 | 1.000→1.000 | 2.81→3.55 | 4.1→14.2 | 0.0→0.0 |
| default | Disc2 | D/boss | 2 | 1.000→1.000 | 13.09→19.70 | 103.5→212.0 | 0.0→0.0 |
| default | Disc2 | G/ord | 46 | 1.000→1.000 | 6.62→6.62 | 31.4→31.4 | 0.0→0.0 |
| default | Disc2 | G/boss | 2 | 1.000→1.000 | 10.93→10.93 | 174.5→174.5 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/ord | 46 | 1.000→1.000 | 6.09→6.09 | 16.7→16.7 | 0.0→0.0 |
| default | Disc2 | controlled_grenade/boss | 2 | 1.000→1.000 | 16.73→16.73 | 249.0→249.0 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/ord | 46 | 1.000→1.000 | 5.78→5.78 | 27.0→27.0 | 0.0→0.0 |
| default | Disc2 | controlled_handgun/boss | 2 | 1.000→1.000 | 12.47→12.47 | 151.0→151.0 | 0.0→0.0 |
| default | Disc2 | controlled_machine/ord | 46 | 1.000→1.000 | 1.92→2.39 | 1.5→1.6 | 0.0→0.0 |
| default | Disc2 | controlled_machine/boss | 2 | 1.000→1.000 | 9.20→15.53 | 151.0→222.0 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/ord | 46 | 0.978→0.978 | 7.76→7.76 | 37.3→37.3 | 0.0→0.0 |
| default | Disc2 | controlled_rifle/boss | 2 | 1.000→1.000 | 10.85→10.85 | 151.0→151.0 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/ord | 46 | 1.000→1.000 | 5.69→5.69 | 27.8→27.8 | 0.0→0.0 |
| default | Disc2 | controlled_shotgun/boss | 2 | 1.000→1.000 | 15.81→15.81 | 222.0→222.0 | 0.0→0.0 |
| human_reaction | Disc2 | C/ord | 46 | 0.978→0.978 | 11.63→11.63 | 55.2→55.2 | 0.0→0.0 |
| human_reaction | Disc2 | C/boss | 2 | 1.000→1.000 | 14.61→14.61 | 174.5→174.5 | 0.0→0.0 |
| human_reaction | Disc2 | D/ord | 46 | 1.000→1.000 | 5.60→6.62 | 15.7→24.4 | 0.0→0.0 |
| human_reaction | Disc2 | D/boss | 2 | 1.000→0.500 | 21.12→25.99 | 255.5→342.5 | 0.0→0.0 |
| human_reaction | Disc2 | G/ord | 46 | 0.978→0.978 | 10.69→10.69 | 54.8→54.8 | 0.0→0.0 |
| human_reaction | Disc2 | G/boss | 2 | 1.000→1.000 | 15.94→15.94 | 269.5→269.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/ord | 46 | 1.000→1.000 | 10.92→10.92 | 37.3→37.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_grenade/boss | 2 | 1.000→1.000 | 18.48→18.48 | 245.5→245.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/ord | 46 | 0.978→0.978 | 11.05→11.05 | 52.9→52.9 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_handgun/boss | 2 | 0.500→0.500 | 20.65→20.65 | 345.0→345.0 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/ord | 46 | 1.000→1.000 | 4.67→5.85 | 12.9→18.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_machine/boss | 2 | 1.000→1.000 | 17.15→25.86 | 174.5→269.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/ord | 46 | 0.978→0.978 | 11.63→11.63 | 53.6→53.6 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_rifle/boss | 2 | 1.000→1.000 | 14.61→14.61 | 174.5→174.5 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/ord | 46 | 0.957→0.957 | 10.44→10.44 | 54.3→54.3 | 0.0→0.0 |
| human_reaction | Disc2 | controlled_shotgun/boss | 2 | 1.000→1.000 | 22.89→22.89 | 299.0→299.0 | 0.0→0.0 |
| far_player | Disc2 | C/ord | 46 | 0.957→0.957 | 7.97→7.97 | 36.9→36.9 | 0.0→0.0 |
| far_player | Disc2 | C/boss | 2 | 1.000→1.000 | 11.25→11.25 | 151.0→151.0 | 0.0→0.0 |
| far_player | Disc2 | D/ord | 46 | 1.000→1.000 | 3.92→5.22 | 4.5→17.3 | 0.0→0.0 |
| far_player | Disc2 | D/boss | 2 | 1.000→1.000 | 14.51→22.75 | 38.5→169.0 | 0.0→0.0 |
| far_player | Disc2 | G/ord | 46 | 1.000→1.000 | 6.88→6.88 | 32.2→32.2 | 0.0→0.0 |
| far_player | Disc2 | G/boss | 2 | 1.000→1.000 | 13.74→13.74 | 130.5→130.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/ord | 46 | 1.000→1.000 | 7.11→7.11 | 20.5→20.5 | 0.0→0.0 |
| far_player | Disc2 | controlled_grenade/boss | 2 | 1.000→1.000 | 20.37→20.37 | 249.0→249.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/ord | 46 | 0.978→0.978 | 6.63→6.63 | 35.0→35.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_handgun/boss | 2 | 1.000→1.000 | 15.79→15.79 | 151.0→151.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/ord | 46 | 1.000→1.000 | 2.61→3.21 | 5.8→7.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_machine/boss | 2 | 1.000→1.000 | 10.40→17.85 | 151.0→222.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/ord | 46 | 0.957→0.957 | 7.97→7.97 | 36.8→36.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_rifle/boss | 2 | 1.000→1.000 | 11.25→11.25 | 151.0→151.0 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/ord | 46 | 1.000→1.000 | 6.63→6.63 | 26.8→26.8 | 0.0→0.0 |
| far_player | Disc2 | controlled_shotgun/boss | 2 | 0.500→0.500 | 16.36→16.36 | 340.5→340.5 | 0.0→0.0 |

## Build ranking stability across assumption sets

**Disc2**
- default: Spearman vs default 1.00; order controlled_machine, D, controlled_handgun, controlled_shotgun, controlled_grenade, G, C, controlled_rifle
- human_reaction: Spearman vs default 0.33; order controlled_machine, controlled_grenade, D, G, C, controlled_rifle, controlled_shotgun, controlled_handgun
- far_player: Spearman vs default 0.76; order controlled_machine, D, G, controlled_grenade, controlled_handgun, controlled_shotgun, C, controlled_rifle
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction -0.003, far_player +0.000

