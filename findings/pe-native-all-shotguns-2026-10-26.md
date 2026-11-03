# All shotgun review against current native balance — 2026-10-26

**Simulation only. No native game code, balance settings, or executable changes.**

Baseline: 12,168 fights; all seven shotgun records plus six comparison weapons, four seeds, built-in effects only. Candidate experiments: 3,744 fights.
Current means the native Rebalanced defaults, including the approved M79-2 +20, M203-3 +20, and M79-3 +18. Other existing bonuses remain enabled. Both native defaults and source hashes were checked before and after each batch.
All seven shotgun combat stat records were also verified against the original resident item pack read by the native loader; see `data/pe-shotgun-item-audit-2026-10-26.json`.

## Coverage and investment

M870 (also MA10) and M870-2 (MA10-2) were missed by the old name-based availability join. This pass enumerates every kind-2 weapon record. Chrysler weapons tested in story scenarios are counterfactual same-investment comparisons, not claims that they can be acquired then.
Stock: no player investment. attack_only: typical attack/range investment (+18/+12 for D5; +50/+18 for Disc2/EX), zero extra magazine rounds. mag2: the same attack/range with only two additional magazine rounds. Intrinsic starting bonuses are retained.
Campaign tests use the sampled logged Aya/armor/PE/bag. Chrysler stress tests use twelve extracted regular enemy stat blocks spanning the tower, including the highest defense (200), each alone and as a constructed group of three. EX33/EX50 use level 33/50 with logged endgame armor and no PE/items. They are not recorded tower fights, and they exclude scripted Chrysler bosses and True Eve.
Every fight starts with a full magazine and a 999-round reserve. Groups use the existing modeled angular spread for Burst. Fight geometry, EX action fallbacks, player levels, and armor assumptions affect absolute times.

## Weapon records

| Weapon | Attack including intrinsic bonus | Range | Stock rounds | Built-in effects |
|---|---:|---:|---:|---|
| M870 | 49 | 60 | 7 | RoF2, Burst |
| M870 2 | 63 | 64 | 5 | Burst |
| M500 | 59 | 63 | 7 | Burst, RoF2 |
| M500 2 | 76 | 67 | 6 | RoF3, Burst |
| MAVERICK | 82 | 71 | 7 | Burst |
| S12 | 98 | 72 | 9 | Burst |
| M10B | 121 | 70 | 7 | RoF3, Burst |

## D5 / attack_only: current balance

| Weapon | campaign_ordinary seconds / win rate | campaign_boss seconds / win rate |
|---|---:|---:|
| M870 | 29.58 / 100% | 53.53 / 100% |
| M870 2 | 37.06 / 100% | 48.89 / 100% |
| M500 | 29.00 / 100% | 50.23 / 100% |
| M500 2 | 27.41 / 100% | 48.09 / 100% |
| MAVERICK | 27.57 / 100% | 42.68 / 100% |
| S12 | 20.22 / 100% | 39.51 / 100% |
| M10B | 23.62 / 100% | 40.89 / 100% |
| M9 3 | 23.83 / 100% | 33.43 / 100% |
| DE50AE7 | 20.57 / 100% | 32.23 / 100% |
| P90 | 20.07 / 100% | 19.10 / 100% |
| MAG | 26.80 / 100% | 40.97 / 100% |
| M203 4 | 30.41 / 100% | 48.47 / 100% |
| M79 3 | 30.69 / 100% | 48.45 / 100% |

## Disc2 / attack_only: current balance

| Weapon | campaign_ordinary seconds / win rate | campaign_boss seconds / win rate |
|---|---:|---:|
| M870 | 18.40 / 100% | 101.92 / 100% |
| M870 2 | 17.56 / 100% | 98.40 / 100% |
| M500 | 17.32 / 100% | 92.80 / 100% |
| M500 2 | 18.05 / 100% | 87.76 / 100% |
| MAVERICK | 16.97 / 100% | 81.95 / 100% |
| S12 | 16.68 / 100% | 75.14 / 100% |
| M10B | 15.49 / 100% | 67.74 / 100% |
| M9 3 | 13.43 / 100% | 56.76 / 100% |
| DE50AE7 | 13.07 / 100% | 53.69 / 100% |
| P90 | 12.71 / 100% | 29.75 / 100% |
| MAG | 16.71 / 100% | 54.07 / 100% |
| M203 4 | 17.20 / 100% | 87.31 / 100% |
| M79 3 | 17.20 / 100% | 88.61 / 100% |

## EX33 / attack_only: current balance

| Weapon | ex_solo seconds / win rate | ex_triple seconds / win rate |
|---|---:|---:|
| M870 | 28.73 / 75% | 28.56 / 52% |
| M870 2 | 26.34 / 73% | 27.19 / 50% |
| M500 | 27.47 / 75% | 28.01 / 52% |
| M500 2 | 28.07 / 85% | 28.22 / 58% |
| MAVERICK | 24.48 / 75% | 26.45 / 56% |
| S12 | 23.40 / 75% | 25.96 / 56% |
| M10B | 22.90 / 96% | 25.59 / 58% |
| M9 3 | 20.51 / 92% | 26.67 / 58% |
| DE50AE7 | 14.27 / 100% | 21.35 / 58% |
| P90 | 11.10 / 100% | 20.55 / 75% |
| MAG | 14.31 / 100% | 23.17 / 60% |
| M203 4 | 21.66 / 75% | 25.33 / 58% |
| M79 3 | 21.63 / 75% | 25.23 / 58% |

## EX50 / attack_only: current balance

| Weapon | ex_solo seconds / win rate | ex_triple seconds / win rate |
|---|---:|---:|
| M870 | 22.20 / 98% | 28.01 / 65% |
| M870 2 | 22.80 / 90% | 25.13 / 65% |
| M500 | 20.57 / 100% | 28.04 / 65% |
| M500 2 | 19.29 / 100% | 29.06 / 65% |
| MAVERICK | 20.58 / 96% | 24.36 / 65% |
| S12 | 18.39 / 100% | 24.31 / 67% |
| M10B | 15.48 / 100% | 27.87 / 69% |
| M9 3 | 10.90 / 100% | 27.56 / 79% |
| DE50AE7 | 9.72 / 100% | 21.73 / 67% |
| P90 | 7.58 / 100% | 17.48 / 100% |
| MAG | 10.47 / 100% | 24.70 / 71% |
| M203 4 | 16.30 / 100% | 24.31 / 67% |
| M79 3 | 16.68 / 98% | 24.45 / 67% |

## D5 / stock: current balance

| Weapon | campaign_ordinary seconds / win rate | campaign_boss seconds / win rate |
|---|---:|---:|
| M870 | 45.92 / 98% | 62.91 / 100% |
| M870 2 | 38.93 / 100% | 53.68 / 100% |
| M500 | 37.51 / 100% | 58.00 / 100% |
| M500 2 | 32.65 / 100% | 54.92 / 100% |
| MAVERICK | 35.23 / 100% | 44.94 / 100% |
| S12 | 27.86 / 100% | 43.13 / 100% |
| M10B | 25.21 / 100% | 43.23 / 100% |
| M9 3 | 26.19 / 100% | 37.81 / 100% |
| DE50AE7 | 21.14 / 100% | 35.31 / 100% |
| P90 | 21.54 / 100% | 20.17 / 100% |
| MAG | 26.87 / 100% | 41.92 / 100% |
| M203 4 | 40.30 / 100% | 56.77 / 100% |
| M79 3 | 41.10 / 100% | 57.45 / 100% |

## Disc2 / stock: current balance

| Weapon | campaign_ordinary seconds / win rate | campaign_boss seconds / win rate |
|---|---:|---:|
| M870 | 22.75 / 100% | 181.49 / 81% |
| M870 2 | 20.98 / 100% | 179.52 / 81% |
| M500 | 20.77 / 100% | 164.68 / 94% |
| M500 2 | 21.80 / 100% | 143.41 / 100% |
| MAVERICK | 19.45 / 100% | 136.00 / 100% |
| S12 | 18.13 / 100% | 113.90 / 100% |
| M10B | 18.20 / 100% | 96.54 / 100% |
| M9 3 | 15.79 / 100% | 103.47 / 100% |
| DE50AE7 | 14.34 / 100% | 75.26 / 100% |
| P90 | 13.25 / 100% | 43.78 / 100% |
| MAG | 18.11 / 100% | 69.70 / 100% |
| M203 4 | 20.10 / 100% | 139.81 / 100% |
| M79 3 | 20.13 / 100% | 142.97 / 100% |

## EX33 / stock: current balance

| Weapon | ex_solo seconds / win rate | ex_triple seconds / win rate |
|---|---:|---:|
| M870 | 38.15 / 58% | 32.36 / 38% |
| M870 2 | 34.76 / 58% | 30.20 / 35% |
| M500 | 36.12 / 65% | 31.72 / 38% |
| M500 2 | 36.20 / 71% | 34.04 / 46% |
| MAVERICK | 30.91 / 67% | 29.62 / 38% |
| S12 | 27.59 / 69% | 27.82 / 44% |
| M10B | 29.59 / 83% | 28.62 / 58% |
| M9 3 | 31.25 / 75% | 32.25 / 50% |
| DE50AE7 | 19.73 / 85% | 23.87 / 58% |
| P90 | 15.23 / 94% | 22.77 / 69% |
| MAG | 19.85 / 94% | 24.61 / 58% |
| M203 4 | 27.65 / 67% | 31.17 / 46% |
| M79 3 | 27.82 / 67% | 31.75 / 44% |

## EX50 / stock: current balance

| Weapon | ex_solo seconds / win rate | ex_triple seconds / win rate |
|---|---:|---:|
| M870 | 30.84 / 83% | 31.69 / 56% |
| M870 2 | 29.10 / 77% | 28.88 / 56% |
| M500 | 29.06 / 85% | 30.67 / 58% |
| M500 2 | 28.41 / 90% | 32.77 / 54% |
| MAVERICK | 26.97 / 88% | 28.89 / 58% |
| S12 | 25.14 / 88% | 28.73 / 60% |
| M10B | 21.51 / 100% | 30.83 / 65% |
| M9 3 | 20.36 / 92% | 29.59 / 69% |
| DE50AE7 | 13.19 / 100% | 23.04 / 67% |
| P90 | 9.94 / 100% | 20.93 / 92% |
| MAG | 12.92 / 100% | 26.02 / 65% |
| M203 4 | 22.80 / 92% | 27.08 / 62% |
| M79 3 | 22.91 / 92% | 27.18 / 62% |

## Two-round magazine investment

| Stage / scenario | Shotgun | No extra rounds → +2 rounds, seconds | Win rate | Reloads |
|---|---|---|---|---|
| D5 / campaign_boss | M10B | 40.89 → 40.54 | 100% → 100% | 0.19 → 0.06 |
| D5 / campaign_ordinary | M10B | 23.62 → 23.62 | 100% → 100% | 0.00 → 0.00 |
| D5 / campaign_boss | M500 | 50.23 → 50.01 | 100% → 100% | 0.38 → 0.06 |
| D5 / campaign_ordinary | M500 | 29.00 → 28.82 | 100% → 100% | 0.15 → 0.00 |
| D5 / campaign_boss | M500 2 | 48.09 → 49.03 | 100% → 100% | 0.94 → 0.62 |
| D5 / campaign_ordinary | M500 2 | 27.41 → 27.16 | 100% → 100% | 0.55 → 0.23 |
| D5 / campaign_boss | M870 | 53.53 → 52.87 | 100% → 100% | 0.62 → 0.12 |
| D5 / campaign_ordinary | M870 | 29.58 → 29.41 | 100% → 100% | 0.15 → 0.00 |
| D5 / campaign_boss | M870 2 | 48.89 → 48.89 | 100% → 100% | 0.38 → 0.06 |
| D5 / campaign_ordinary | M870 2 | 37.06 → 37.06 | 100% → 100% | 0.30 → 0.03 |
| D5 / campaign_boss | MAVERICK | 42.68 → 42.68 | 100% → 100% | 0.00 → 0.00 |
| D5 / campaign_ordinary | MAVERICK | 27.57 → 27.57 | 100% → 100% | 0.00 → 0.00 |
| D5 / campaign_boss | S12 | 39.51 → 39.51 | 100% → 100% | 0.00 → 0.00 |
| D5 / campaign_ordinary | S12 | 20.22 → 20.22 | 100% → 100% | 0.00 → 0.00 |
| Disc2 / campaign_boss | M10B | 67.74 → 65.19 | 100% → 100% | 2.38 → 1.75 |
| Disc2 / campaign_ordinary | M10B | 15.49 → 15.49 | 100% → 100% | 0.00 → 0.00 |
| Disc2 / campaign_boss | M500 | 92.80 → 92.55 | 100% → 100% | 2.44 → 1.88 |
| Disc2 / campaign_ordinary | M500 | 17.32 → 17.32 | 100% → 100% | 0.02 → 0.02 |
| Disc2 / campaign_boss | M500 2 | 87.76 → 89.64 | 100% → 100% | 3.75 → 2.69 |
| Disc2 / campaign_ordinary | M500 2 | 18.05 → 17.98 | 100% → 100% | 0.15 → 0.08 |
| Disc2 / campaign_boss | M870 | 101.92 → 100.77 | 100% → 100% | 2.62 → 1.94 |
| Disc2 / campaign_ordinary | M870 | 18.40 → 18.29 | 100% → 100% | 0.08 → 0.02 |
| Disc2 / campaign_boss | M870 2 | 98.40 → 98.40 | 100% → 100% | 2.12 → 1.50 |
| Disc2 / campaign_ordinary | M870 2 | 17.56 → 17.56 | 100% → 100% | 0.04 → 0.00 |
| Disc2 / campaign_boss | MAVERICK | 81.95 → 81.95 | 100% → 100% | 1.19 → 0.81 |
| Disc2 / campaign_ordinary | MAVERICK | 16.97 → 16.97 | 100% → 100% | 0.00 → 0.00 |
| Disc2 / campaign_boss | S12 | 75.14 → 75.14 | 100% → 100% | 0.69 → 0.56 |
| Disc2 / campaign_ordinary | S12 | 16.68 → 16.68 | 100% → 100% | 0.00 → 0.00 |
| EX33 / ex_solo | M10B | 22.90 → 21.83 | 96% → 96% | 0.60 → 0.33 |
| EX33 / ex_triple | M10B | 25.59 → 25.54 | 58% → 58% | 0.40 → 0.31 |
| EX33 / ex_solo | M500 | 27.47 → 27.25 | 75% → 75% | 0.46 → 0.33 |
| EX33 / ex_triple | M500 | 28.01 → 27.97 | 52% → 54% | 0.33 → 0.25 |
| EX33 / ex_solo | M500 2 | 28.07 → 29.25 | 85% → 85% | 0.98 → 0.67 |
| EX33 / ex_triple | M500 2 | 28.22 → 28.46 | 58% → 58% | 0.58 → 0.46 |
| EX33 / ex_solo | M870 | 28.73 → 28.66 | 75% → 75% | 0.48 → 0.44 |
| EX33 / ex_triple | M870 | 28.56 → 28.38 | 52% → 54% | 0.31 → 0.25 |
| EX33 / ex_solo | M870 2 | 26.34 → 26.34 | 73% → 73% | 0.38 → 0.10 |
| EX33 / ex_triple | M870 2 | 27.19 → 27.19 | 50% → 50% | 0.27 → 0.10 |
| EX33 / ex_solo | MAVERICK | 24.48 → 24.48 | 75% → 75% | 0.06 → 0.00 |
| EX33 / ex_triple | MAVERICK | 26.45 → 26.45 | 56% → 56% | 0.08 → 0.08 |
| EX33 / ex_solo | S12 | 23.40 → 23.40 | 75% → 75% | 0.00 → 0.00 |
| EX33 / ex_triple | S12 | 25.96 → 25.96 | 56% → 56% | 0.06 → 0.02 |
| EX50 / ex_solo | M10B | 15.48 → 14.93 | 100% → 100% | 0.31 → 0.21 |
| EX50 / ex_triple | M10B | 27.87 → 27.28 | 69% → 69% | 0.71 → 0.46 |
| EX50 / ex_solo | M500 | 20.57 → 20.39 | 100% → 100% | 0.40 → 0.21 |
| EX50 / ex_triple | M500 | 28.04 → 27.58 | 65% → 65% | 0.56 → 0.25 |
| EX50 / ex_solo | M500 2 | 19.29 → 20.03 | 100% → 100% | 0.67 → 0.42 |
| EX50 / ex_triple | M500 2 | 29.06 → 29.52 | 65% → 65% | 1.00 → 0.73 |
| EX50 / ex_solo | M870 | 22.20 → 22.02 | 98% → 98% | 0.42 → 0.25 |
| EX50 / ex_triple | M870 | 28.01 → 27.60 | 65% → 65% | 0.56 → 0.25 |
| EX50 / ex_solo | M870 2 | 22.80 → 22.80 | 90% → 90% | 0.35 → 0.21 |
| EX50 / ex_triple | M870 2 | 25.13 → 25.13 | 65% → 65% | 0.25 → 0.12 |
| EX50 / ex_solo | MAVERICK | 20.58 → 20.58 | 96% → 96% | 0.17 → 0.06 |
| EX50 / ex_triple | MAVERICK | 24.36 → 24.36 | 65% → 65% | 0.10 → 0.02 |
| EX50 / ex_solo | S12 | 18.39 → 18.39 | 100% → 100% | 0.00 → 0.00 |
| EX50 / ex_triple | S12 | 24.31 → 24.31 | 67% → 67% | 0.02 → 0.00 |

## Individual candidate experiments

These edits exist only in simulator configurations. Paired intervals resample encounters, grouping the repeated seeds per encounter; they measure model variation, not real-game confidence. Delta uses the fight horizon as a penalty for losses so early deaths are not rewarded as faster clears.

| Stage / scenario | Weapon | Setup | Candidate | Current → candidate seconds | Win rate | Penalized delta interval |
|---|---|---|---|---|---|---|
| D5 / campaign_boss | M870 2 | attack_only | attack5 | 48.89 → 44.68 | 100% → 100% | [-11.35, 0.00] |
| D5 / campaign_ordinary | M870 2 | attack_only | attack5 | 37.06 → 27.81 | 100% → 100% | [-13.04, -5.49] |
| Disc2 / campaign_boss | M870 2 | attack_only | attack5 | 98.40 → 93.57 | 100% → 100% | [-8.63, -1.65] |
| Disc2 / campaign_ordinary | M870 2 | attack_only | attack5 | 17.56 → 17.56 | 100% → 100% | [0.00, 0.00] |
| EX33 / ex_solo | M870 2 | attack_only | attack5 | 26.34 → 25.80 | 73% → 73% | [-1.34, 0.00] |
| EX33 / ex_triple | M870 2 | attack_only | attack5 | 27.19 → 27.19 | 50% → 50% | [0.00, 0.00] |
| EX50 / ex_solo | M870 2 | attack_only | attack5 | 22.80 → 22.51 | 90% → 92% | [-0.78, 0.00] |
| EX50 / ex_triple | M870 2 | attack_only | attack5 | 25.13 → 25.01 | 65% → 65% | [-0.34, 0.00] |
| D5 / campaign_boss | M870 2 | attack_only | attack10 | 48.89 → 44.68 | 100% → 100% | [-11.35, 0.00] |
| D5 / campaign_ordinary | M870 2 | attack_only | attack10 | 37.06 → 27.81 | 100% → 100% | [-13.04, -5.49] |
| Disc2 / campaign_boss | M870 2 | attack_only | attack10 | 98.40 → 87.37 | 100% → 100% | [-20.89, -1.65] |
| Disc2 / campaign_ordinary | M870 2 | attack_only | attack10 | 17.56 → 16.98 | 100% → 100% | [-1.44, 0.00] |
| EX33 / ex_solo | M870 2 | attack_only | attack10 | 26.34 → 25.36 | 73% → 73% | [-1.97, 0.00] |
| EX33 / ex_triple | M870 2 | attack_only | attack10 | 27.19 → 26.46 | 50% → 54% | [-2.04, 0.00] |
| EX50 / ex_solo | M870 2 | attack_only | attack10 | 22.80 → 21.57 | 90% → 92% | [-2.22, -0.43] |
| EX50 / ex_triple | M870 2 | attack_only | attack10 | 25.13 → 24.90 | 65% → 65% | [-0.87, 0.00] |
| D5 / campaign_boss | M870 2 | attack_only | attack15 | 48.89 → 43.31 | 100% → 100% | [-11.77, -0.84] |
| D5 / campaign_ordinary | M870 2 | attack_only | attack15 | 37.06 → 27.81 | 100% → 100% | [-13.04, -5.49] |
| Disc2 / campaign_boss | M870 2 | attack_only | attack15 | 98.40 → 85.17 | 100% → 100% | [-24.81, -1.65] |
| Disc2 / campaign_ordinary | M870 2 | attack_only | attack15 | 17.56 → 16.98 | 100% → 100% | [-1.44, 0.00] |
| EX33 / ex_solo | M870 2 | attack_only | attack15 | 26.34 → 24.55 | 73% → 73% | [-3.17, -0.40] |
| EX33 / ex_triple | M870 2 | attack_only | attack15 | 27.19 → 26.35 | 50% → 56% | [-4.25, 0.00] |
| EX50 / ex_solo | M870 2 | attack_only | attack15 | 22.80 → 20.90 | 90% → 94% | [-5.29, -0.71] |
| EX50 / ex_triple | M870 2 | attack_only | attack15 | 25.13 → 24.90 | 65% → 65% | [-0.87, 0.00] |
| D5 / campaign_boss | M870 2 | attack_only | mag2 | 48.89 → 48.89 | 100% → 100% | [0.00, 0.00] |
| D5 / campaign_ordinary | M870 2 | attack_only | mag2 | 37.06 → 37.06 | 100% → 100% | [0.00, 0.00] |
| Disc2 / campaign_boss | M870 2 | attack_only | mag2 | 98.40 → 98.40 | 100% → 100% | [0.00, 0.00] |
| Disc2 / campaign_ordinary | M870 2 | attack_only | mag2 | 17.56 → 17.56 | 100% → 100% | [0.00, 0.00] |
| EX33 / ex_solo | M870 2 | attack_only | mag2 | 26.34 → 26.34 | 73% → 73% | [0.00, 0.00] |
| EX33 / ex_triple | M870 2 | attack_only | mag2 | 27.19 → 27.19 | 50% → 50% | [0.00, 0.00] |
| EX50 / ex_solo | M870 2 | attack_only | mag2 | 22.80 → 22.80 | 90% → 90% | [0.00, 0.00] |
| EX50 / ex_triple | M870 2 | attack_only | mag2 | 25.13 → 25.13 | 65% → 65% | [0.00, 0.00] |
| D5 / campaign_boss | M870 2 | attack_only | mag50pct | 48.89 → 48.89 | 100% → 100% | [0.00, 0.00] |
| D5 / campaign_ordinary | M870 2 | attack_only | mag50pct | 37.06 → 37.06 | 100% → 100% | [0.00, 0.00] |
| Disc2 / campaign_boss | M870 2 | attack_only | mag50pct | 98.40 → 98.40 | 100% → 100% | [0.00, 0.00] |
| Disc2 / campaign_ordinary | M870 2 | attack_only | mag50pct | 17.56 → 17.56 | 100% → 100% | [0.00, 0.00] |
| EX33 / ex_solo | M870 2 | attack_only | mag50pct | 26.34 → 26.34 | 73% → 73% | [0.00, 0.00] |
| EX33 / ex_triple | M870 2 | attack_only | mag50pct | 27.19 → 27.19 | 50% → 50% | [0.00, 0.00] |
| EX50 / ex_solo | M870 2 | attack_only | mag50pct | 22.80 → 22.80 | 90% → 90% | [0.00, 0.00] |
| EX50 / ex_triple | M870 2 | attack_only | mag50pct | 25.13 → 25.13 | 65% → 65% | [0.00, 0.00] |

## Burst alignment sensitivity

Additional 1,248 current-balance fights: same EX50 stats, seeds, investment, and built-in effects, but the constructed triples are within the native Burst angular predicate. This is an ideal line-up sensitivity, not measured player behavior. Non-Burst controls retain identical outcomes.

| Weapon | Scattered triples: seconds / win rate | Lined-up triples: seconds / win rate | Penalized time, scattered → lined-up |
|---|---:|---:|---:|
| DE50AE7 | 21.73 / 66.7% | 21.73 / 66.7% | 42.39 → 42.39 |
| M10B | 27.87 / 68.8% | 20.93 / 87.5% | 45.54 → 27.66 |
| M203 4 | 24.31 / 66.7% | 24.31 / 66.7% | 45.80 → 45.80 |
| M500 | 28.04 / 64.6% | 20.01 / 68.8% | 49.28 → 39.75 |
| M500 2 | 29.06 / 64.6% | 21.07 / 72.9% | 49.20 → 36.80 |
| M79 3 | 24.45 / 66.7% | 24.45 / 66.7% | 45.94 → 45.94 |
| M870 | 28.01 / 64.6% | 20.53 / 66.7% | 49.48 → 41.28 |
| M870 2 | 25.13 / 64.6% | 18.16 / 66.7% | 48.33 → 40.68 |
| M9 3 | 27.56 / 79.2% | 27.56 / 79.2% | 37.94 → 37.94 |
| MAG | 24.70 / 70.8% | 24.70 / 70.8% | 42.45 → 42.45 |
| MAVERICK | 24.36 / 64.6% | 17.37 / 68.8% | 47.46 → 38.60 |
| P90 | 17.48 / 100.0% | 17.48 / 100.0% | 17.48 → 17.48 |
| S12 | 24.31 / 66.7% | 16.87 / 68.8% | 46.41 → 38.11 |

## Findings for discussion

**M870-2 (MA10-2): +10 attack is the strongest conservative individual candidate.** At attack/range-only investment, current D5 ordinary fights take 37.06s; +5/+10/+15 all cross the same breakpoint to 27.81s. On Disc2 bosses, current 98.40s falls to 93.57s at +5, 87.37s at +10, and 85.17s at +15. +10 takes its intrinsic attack total from 63 to 73, below M500-2 76 and Maverick 82. It preserves the five-round magazine and single-shot identity. It does not make this lower-power tower pickup an upper-floor endgame replacement.
In EX50 single-enemy stress cases, the same M870-2 +10 raises wins from 89.6% to 91.7%; +15 reaches 93.8%. These are limited constructed stress samples, not proof of tower clear rates. Both +2 and +50% magazine candidates leave its results unchanged across the tested profiles. Its main weakness here is damage/breakpoints, not capacity.
**M870: keep.** It is the lower-power main-game shotgun (called MA10 in the old gear list), not a weapon that should be raised to Wayne/S12 power. **M500: keep.** It improves on that early model without needing Catalog installs.
**M500-2: keep.** The modest Disc2 ordinary-fight regression versus M500 (18.05 vs 17.32s at no magazine investment) is offset by better bosses (87.76 vs 92.80s), higher EX33 solo wins (85.4% vs 75%), and improved EX50 aligned-triple wins (72.9% vs M500 68.8%). Its RoF3 and six-round magazine trade ammo cost and firing commitment for damage against tougher targets.
**Maverick: keep.** It provides a useful single-shot, larger-magazine step above M870-2; S12 is a stronger later-tier stat option. Exact Chrysler pickup floors were not established by the available item-location table. **S12: keep.** Strong ordinary performance and ammunition economy; it needs no buff from this evidence.
**M10B: keep.** Best shotgun in the Disc2 boss benchmark (67.74s versus S12 75.14s) and EX50 solo benchmark (15.48s versus S12 18.39s) at zero magazine investment. Its EX50 constructed-triple win rate improves from 68.8% scattered to 87.5% when lined up. Two extra rounds provide a small Disc2 boss improvement (67.74 → 65.20s), not evidence of a broad capacity defect.
A +10 M870-2 change is a proposal only. No weapon attack, magazine, firing speed, native settings, or game executable was modified in this review.

## Limits

Table times include losses/timeouts; always read win rates alongside them. Successful-clear means and penalized durations are available in the CSV/JSON. Stage averages weight the chosen encounters equally, not by campaign frequency. Source-extracted EX stats do not verify its complete AI, room formations, encounter frequency, pickup floors, or progression economy.
Old early-game shotguns need not match Wayne/S12 on upper tower floors. A Chrysler weapon being tested does not establish where it should rank without its actual acquisition-floor data. No class-wide attack, firing-speed, proximity, or reload change is applied.
The built-in RoF is preserved; installed-RoF bonuses and acceleration never apply to these shotguns. Native hit arithmetic is mirrored, but native RNG sequences, status-floor edge cases, delayed hits, and integer crowd-cap search retain earlier model limitations. Critical conversion now uses native integer 26%, rather than the earlier 26.67% approximation.
Other current-balance comparison weapons can specialize: P90 has Attack All, MAG Critical, M9-3 Commands, and grenade elements. Their results provide context, not a requirement that every shotgun beat every class.

## Reproduce

Use the configured Python runtime from the bridge root with PYTHONPATH=tools.

```text
python -m unittest pe_weapon_sim.tests.test_shotgun_review pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat
python -m pe_weapon_sim.run_shotgun_review
python -m pe_weapon_sim.run_shotgun_review --only "M870 2" --no-anchors --profiles stock attack_only --variants current attack5 attack10 attack15 mag2 mag50pct --workers 2 --tag native-shotgun-m8702-candidates-2026-10-26
python -m pe_weapon_sim.run_shotgun_review --stages EX50 --profiles attack_only --geometry clustered --workers 2 --tag native-shotgun-burst-alignment-2026-10-26
python -m pe_weapon_sim.report_shotgun_review --candidate native-shotgun-m8702-candidates-2026-10-26
```
