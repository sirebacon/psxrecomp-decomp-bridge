# Rule comparison: cfg:4.rof+1 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.985→0.993 (+0.007, [+0.000, +0.019]) | 27.76→26.86 | 56.0→52.8 | 11.5→12.1 | 0.3→0.3 | 0.015→0.007 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.16→23.51 | 58.8→55.9 | 11.0→11.5 | 0.2→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.967→0.983 (+0.017, [+0.000, +0.042]) | 32.25→31.04 | 52.4→49.0 | 12.0→12.8 | 0.3→0.3 | 0.033→0.017 | 0.00 | 0.00 |
| human_reaction | D5 | ALL | 0.970→0.974 (+0.004, [+0.000, +0.011]) | 38.85→38.05 | 88.7→87.3 | 12.0→12.7 | 0.3→0.3 | 0.015→0.015 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 0.993→0.993 (+0.000, [+0.000, +0.000]) | 34.98→34.26 | 102.0→101.1 | 11.7→12.3 | 0.3→0.3 | 0.007→0.007 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.942→0.950 (+0.008, [+0.000, +0.025]) | 43.68→42.78 | 72.0→69.9 | 12.4→13.1 | 0.3→0.3 | 0.025→0.025 | 0.00 | 0.00 |
| far_player | D5 | ALL | 0.996→0.993 (-0.004, [-0.011, +0.000]) | 31.78→30.99 | 53.3→51.5 | 13.8→14.4 | 0.4→0.4 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.97→26.16 | 60.7→56.8 | 13.0→13.5 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.992→0.983 (-0.008, [-0.025, +0.000]) | 37.80→37.04 | 44.0→44.9 | 14.8→15.6 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 28.10→28.10 | 77.6→77.6 | 0.4→0.4 |
| default | D5 | class_grenade/boss | 24 | 0.958→0.958 | 36.74→36.74 | 63.5→63.5 | 0.2→0.2 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 18.67→18.67 | 38.0→38.0 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 23.70→23.70 | 32.0→32.0 | 0.2→0.2 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 16.72→16.72 | 42.2→42.2 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 21.34→21.34 | 30.5→30.5 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 34.72→31.42 | 97.1→82.5 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.875→0.958 | 46.48→40.43 | 84.7→67.8 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 22.61→22.61 | 39.1→39.1 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 33.01→33.01 | 51.3→51.3 | 0.4→0.4 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.38→40.38 | 125.6→125.6 | 0.5→0.5 |
| human_reaction | D5 | class_grenade/boss | 24 | 0.917→0.917 | 46.88→46.88 | 85.4→85.4 | 0.2→0.2 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.98→26.98 | 71.1→71.1 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 32.82→32.82 | 45.7→45.7 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 93.3→93.3 | 0.5→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 32.86→32.86 | 50.3→50.3 | 0.7→0.7 |
| human_reaction | D5 | class_rifle/ord | 30 | 0.967→0.967 | 47.49→43.88 | 135.7→131.3 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 0.833→0.875 | 59.86→55.37 | 100.6→90.1 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.57→31.57 | 84.3→84.3 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 0.958→0.958 | 45.99→45.99 | 78.0→78.0 | 0.4→0.4 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.02→31.02 | 74.6→74.6 | 0.5→0.5 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 41.00→41.00 | 50.8→50.8 | 0.3→0.3 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 20.02→20.02 | 39.6→39.6 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 27.11→27.11 | 32.3→32.3 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 22.35→22.35 | 56.7→56.7 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 29.96→29.96 | 31.4→31.4 | 0.9→0.9 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 37.05→32.99 | 92.8→73.6 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 0.958→0.917 | 49.28→45.47 | 58.0→62.0 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 24.42→24.42 | 39.6→39.6 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 41.66→41.66 | 47.6→47.6 | 0.8→0.8 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_shotgun, class_grenade, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- far_player: Spearman vs default 0.90; order class_handgun, class_machine, class_shotgun, class_grenade, class_rifle
- win-rate delta (proposal − baseline) by set: default +0.007, human_reaction +0.004, far_player -0.004

