# Rule comparison: exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20 vs baseline — October 18, 2026

Equal-investment class benchmark guns (run_benchmark.CLASS_GUNS; D5 Day-5 investment, Disc2 [30,10,10] + 2Cmd + Quickdraw; Aya = the same seed frozen group-C build), campaign-frequency encounters (logged won battles), matched seeds; 3 seeds x every logged battle.
Coverage labels: fallback hits use estimated damage; untimed strikes use the labelled placeholder timing (assumption sets vary both).

Disc2 boss battles are an incomplete scenario: 188 / 245 / 429 boss identities have no resolved attacks and 256 / 428 / 432 / 350 effects use the untimed placeholder (see fallback / untimed shares).

| Assumptions | Stage | Group | Win base→prop (Δ, 95% CI) | Time s base→prop | Damage taken base→prop | Rounds | Reloads | Deaths | Fallback hit share | Untimed strike share |
|---|---|---|---|---|---|---|---|---|---|---|
| default | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 27.89→24.14 | 47.0→36.5 | 11.5→10.8 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 24.16→20.43 | 50.0→36.3 | 11.0→10.3 | 0.2→0.1 | 0.000→0.000 | 0.00 | 0.00 |
| default | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 32.54→28.78 | 43.2→36.8 | 12.1→11.5 | 0.3→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| default | Disc2 | ALL | 0.957→0.957 (+0.000, [+0.000, +0.000]) | 9.11→9.55 | 53.0→57.1 | 8.2→11.4 | 0.0→0.0 | 0.040→0.040 | 0.01 | 0.33 |
| default | Disc2 | ORDINARY | 0.999→0.999 (+0.000, [+0.000, +0.000]) | 7.68→8.18 | 15.9→20.5 | 5.9→9.4 | 0.0→0.0 | 0.001→0.001 | 0.02 | 0.20 |
| default | Disc2 | BOSS | 0.600→0.600 (+0.000, [+0.000, +0.000]) | 21.07→21.07 | 363.3→363.3 | 27.6→27.6 | 0.2→0.2 | 0.370→0.370 | 0.00 | 0.62 |
| human_reaction | D5 | ALL | 0.981→1.000 (+0.019, [+0.004, +0.033]) | 39.01→34.61 | 74.5→64.1 | 12.0→11.5 | 0.3→0.2 | 0.004→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 35.01→29.87 | 89.5→75.9 | 11.7→11.1 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| human_reaction | D5 | BOSS | 0.958→1.000 (+0.042, [+0.008, +0.083]) | 44.01→40.52 | 55.7→49.5 | 12.4→12.0 | 0.3→0.3 | 0.008→0.000 | 0.00 | 0.00 |
| human_reaction | Disc2 | ALL | 0.936→0.935 (-0.001, [-0.002, +0.000]) | 14.77→15.39 | 73.9→79.0 | 7.9→11.2 | 0.0→0.0 | 0.059→0.060 | 0.02 | 0.27 |
| human_reaction | Disc2 | ORDINARY | 0.991→0.990 (-0.001, [-0.002, +0.000]) | 13.30→13.99 | 34.1→39.8 | 6.0→9.7 | 0.0→0.0 | 0.009→0.010 | 0.02 | 0.17 |
| human_reaction | Disc2 | BOSS | 0.479→0.479 (+0.000, [+0.000, +0.000]) | 27.08→27.08 | 406.9→406.9 | 24.5→24.5 | 0.1→0.1 | 0.473→0.473 | 0.00 | 0.60 |
| far_player | D5 | ALL | 0.996→1.000 (+0.004, [+0.000, +0.011]) | 31.78→27.83 | 46.0→36.6 | 13.8→13.1 | 0.4→0.3 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | ORDINARY | 1.000→1.000 (+0.000, [+0.000, +0.000]) | 26.97→22.63 | 53.4→40.1 | 13.0→12.2 | 0.3→0.2 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | D5 | BOSS | 0.992→1.000 (+0.008, [+0.000, +0.025]) | 37.80→34.32 | 36.8→32.2 | 14.8→14.2 | 0.5→0.5 | 0.000→0.000 | 0.00 | 0.00 |
| far_player | Disc2 | ALL | 0.949→0.949 (+0.000, [+0.000, +0.000]) | 10.12→10.61 | 55.1→59.5 | 9.6→13.3 | 0.0→0.0 | 0.047→0.047 | 0.01 | 0.32 |
| far_player | Disc2 | ORDINARY | 0.999→0.999 (+0.000, [+0.000, +0.000]) | 8.54→9.09 | 16.3→21.3 | 7.0→11.1 | 0.0→0.0 | 0.001→0.001 | 0.02 | 0.19 |
| far_player | Disc2 | BOSS | 0.527→0.527 (+0.000, [+0.000, +0.000]) | 23.31→23.31 | 379.4→379.4 | 31.9→31.9 | 0.2→0.2 | 0.436→0.436 | 0.00 | 0.60 |

## Per build group (ordinary and boss separate)

| Assumptions | Stage | Group | n | Win base→prop | Time s base→prop | Damage taken base→prop | Reloads base→prop |
|---|---|---|---|---|---|---|---|
| default | D5 | class_grenade/ord | 30 | 1.000→1.000 | 28.10→22.50 | 63.6→38.6 | 0.4→0.0 |
| default | D5 | class_grenade/boss | 24 | 1.000→1.000 | 36.95→29.83 | 52.5→43.0 | 0.2→0.1 |
| default | D5 | class_handgun/ord | 30 | 1.000→1.000 | 18.67→18.67 | 33.5→33.5 | 0.2→0.2 |
| default | D5 | class_handgun/boss | 24 | 1.000→1.000 | 23.70→23.70 | 28.9→28.9 | 0.2→0.2 |
| default | D5 | class_machine/ord | 30 | 1.000→1.000 | 16.72→16.72 | 39.2→39.2 | 0.3→0.3 |
| default | D5 | class_machine/boss | 24 | 1.000→1.000 | 21.34→21.34 | 25.8→25.8 | 0.6→0.6 |
| default | D5 | class_rifle/ord | 30 | 1.000→1.000 | 34.72→21.66 | 81.7→38.3 | 0.0→0.0 |
| default | D5 | class_rifle/boss | 24 | 0.958→1.000 | 47.71→36.01 | 64.2→41.5 | 0.0→0.0 |
| default | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 22.61→22.61 | 31.9→31.9 | 0.2→0.2 |
| default | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 33.01→33.01 | 44.8→44.8 | 0.4→0.4 |
| default | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 9.41→9.41 | 17.5→17.5 | 0.0→0.0 |
| default | Disc2 | class_grenade/boss | 33 | 0.515→0.515 | 27.65→27.65 | 384.9→384.9 | 0.1→0.1 |
| default | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 7.74→7.74 | 17.1→17.1 | 0.0→0.0 |
| default | Disc2 | class_handgun/boss | 33 | 0.727→0.727 | 19.93→19.93 | 317.4→317.4 | 0.2→0.2 |
| default | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 3.23→5.70 | 3.8→27.0 | 0.0→0.0 |
| default | Disc2 | class_machine/boss | 33 | 0.788→0.788 | 13.82→13.82 | 288.5→288.5 | 0.1→0.1 |
| default | Disc2 | class_rifle/ord | 276 | 0.996→0.996 | 9.59→9.59 | 19.1→19.1 | 0.0→0.0 |
| default | Disc2 | class_rifle/boss | 33 | 0.636→0.636 | 20.36→20.36 | 379.9→379.9 | 0.1→0.1 |
| default | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 8.45→8.45 | 22.0→22.0 | 0.0→0.0 |
| default | Disc2 | class_shotgun/boss | 33 | 0.333→0.333 | 23.59→23.59 | 445.9→445.9 | 0.6→0.6 |
| human_reaction | D5 | class_grenade/ord | 30 | 1.000→1.000 | 40.38→31.64 | 107.9→80.3 | 0.5→0.1 |
| human_reaction | D5 | class_grenade/boss | 24 | 0.958→1.000 | 47.60→40.80 | 65.6→57.2 | 0.2→0.2 |
| human_reaction | D5 | class_handgun/ord | 30 | 1.000→1.000 | 26.98→26.98 | 64.0→64.0 | 0.1→0.1 |
| human_reaction | D5 | class_handgun/boss | 24 | 1.000→1.000 | 32.82→32.82 | 37.0→37.0 | 0.2→0.2 |
| human_reaction | D5 | class_machine/ord | 30 | 1.000→1.000 | 28.47→28.47 | 84.3→84.3 | 0.5→0.5 |
| human_reaction | D5 | class_machine/boss | 24 | 1.000→1.000 | 32.86→32.86 | 40.9→40.9 | 0.7→0.7 |
| human_reaction | D5 | class_rifle/ord | 30 | 1.000→1.000 | 47.67→30.71 | 116.2→75.9 | 0.0→0.0 |
| human_reaction | D5 | class_rifle/boss | 24 | 0.833→1.000 | 60.65→50.00 | 76.6→53.8 | 0.0→0.0 |
| human_reaction | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 31.57→31.57 | 74.8→74.8 | 0.2→0.2 |
| human_reaction | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 46.13→46.13 | 58.5→58.5 | 0.4→0.4 |
| human_reaction | Disc2 | class_grenade/ord | 276 | 0.982→0.982 | 16.06→16.06 | 40.3→40.3 | 0.0→0.0 |
| human_reaction | Disc2 | class_grenade/boss | 33 | 0.333→0.333 | 32.06→32.06 | 421.8→421.8 | 0.1→0.1 |
| human_reaction | Disc2 | class_handgun/ord | 276 | 0.996→0.996 | 14.26→14.26 | 29.5→29.5 | 0.0→0.0 |
| human_reaction | Disc2 | class_handgun/boss | 33 | 0.485→0.485 | 28.00→28.00 | 407.0→407.0 | 0.1→0.1 |
| human_reaction | Disc2 | class_machine/ord | 276 | 1.000→0.996 | 6.03→9.47 | 15.7→44.2 | 0.0→0.0 |
| human_reaction | Disc2 | class_machine/boss | 33 | 0.697→0.697 | 20.11→20.11 | 360.0→360.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/ord | 276 | 0.989→0.989 | 16.11→16.11 | 41.0→41.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_rifle/boss | 33 | 0.606→0.606 | 27.31→27.31 | 395.2→395.2 | 0.1→0.1 |
| human_reaction | Disc2 | class_shotgun/ord | 276 | 0.986→0.986 | 14.04→14.04 | 44.0→44.0 | 0.0→0.0 |
| human_reaction | Disc2 | class_shotgun/boss | 33 | 0.273→0.273 | 27.93→27.93 | 450.8→450.8 | 0.4→0.4 |
| far_player | D5 | class_grenade/ord | 30 | 1.000→1.000 | 31.02→23.55 | 63.3→39.6 | 0.5→0.0 |
| far_player | D5 | class_grenade/boss | 24 | 1.000→1.000 | 41.00→35.82 | 42.9→36.5 | 0.3→0.2 |
| far_player | D5 | class_handgun/ord | 30 | 1.000→1.000 | 20.02→20.02 | 36.4→36.4 | 0.2→0.2 |
| far_player | D5 | class_handgun/boss | 24 | 1.000→1.000 | 27.11→27.11 | 29.0→29.0 | 0.5→0.5 |
| far_player | D5 | class_machine/ord | 30 | 1.000→1.000 | 22.35→22.35 | 53.6→53.6 | 0.7→0.7 |
| far_player | D5 | class_machine/boss | 24 | 1.000→1.000 | 29.96→29.96 | 25.2→25.2 | 0.9→0.9 |
| far_player | D5 | class_rifle/ord | 30 | 1.000→1.000 | 37.05→22.83 | 79.5→36.5 | 0.0→0.0 |
| far_player | D5 | class_rifle/boss | 24 | 0.958→1.000 | 49.28→37.04 | 45.7→29.1 | 0.0→0.0 |
| far_player | D5 | class_shotgun/ord | 30 | 1.000→1.000 | 24.42→24.42 | 34.2→34.2 | 0.3→0.3 |
| far_player | D5 | class_shotgun/boss | 24 | 1.000→1.000 | 41.66→41.66 | 41.1→41.1 | 0.8→0.8 |
| far_player | Disc2 | class_grenade/ord | 276 | 1.000→1.000 | 10.04→10.04 | 17.1→17.1 | 0.0→0.0 |
| far_player | Disc2 | class_grenade/boss | 33 | 0.424→0.424 | 27.95→27.95 | 390.4→390.4 | 0.1→0.1 |
| far_player | Disc2 | class_handgun/ord | 276 | 1.000→1.000 | 8.66→8.66 | 16.6→16.6 | 0.0→0.0 |
| far_player | Disc2 | class_handgun/boss | 33 | 0.576→0.576 | 23.01→23.01 | 352.2→352.2 | 0.2→0.2 |
| far_player | Disc2 | class_machine/ord | 276 | 1.000→1.000 | 4.43→7.18 | 6.0→30.9 | 0.0→0.0 |
| far_player | Disc2 | class_machine/boss | 33 | 0.727→0.727 | 17.79→17.79 | 338.5→338.5 | 0.1→0.1 |
| far_player | Disc2 | class_rifle/ord | 276 | 0.996→0.996 | 9.71→9.71 | 18.9→18.9 | 0.0→0.0 |
| far_player | Disc2 | class_rifle/boss | 33 | 0.606→0.606 | 21.15→21.15 | 358.6→358.6 | 0.1→0.1 |
| far_player | Disc2 | class_shotgun/ord | 276 | 1.000→1.000 | 9.87→9.87 | 23.1→23.1 | 0.0→0.0 |
| far_player | Disc2 | class_shotgun/boss | 33 | 0.303→0.303 | 26.66→26.66 | 457.1→457.1 | 0.6→0.6 |

## Build ranking stability across assumption sets

**D5**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_grenade, class_shotgun, class_rifle
- human_reaction: Spearman vs default 0.90; order class_handgun, class_machine, class_grenade, class_shotgun, class_rifle
- far_player: Spearman vs default 0.80; order class_handgun, class_machine, class_grenade, class_rifle, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.004, human_reaction +0.019, far_player +0.004

**Disc2**
- default: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_grenade, class_shotgun
- human_reaction: Spearman vs default 0.90; order class_machine, class_rifle, class_handgun, class_grenade, class_shotgun
- far_player: Spearman vs default 1.00; order class_machine, class_handgun, class_rifle, class_grenade, class_shotgun
- win-rate delta (proposal − baseline) by set: default +0.000, human_reaction -0.001, far_player +0.000

