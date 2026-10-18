# Phase 3 report F: Integrated progression across the story

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | phase | BP earned | gun | bonus atk/rng/bul | magazine | suite seconds |
|---|---|---|---|---|---|---|
| overlap\|A | D1 | 115.19 | M84F 100% | 5.01/0.02/0.01 | 6.01 | - |
| overlap\|A | D2-4 | 971.45 | SG550 41%, G19 18%, M9 2 13% | 12.90/7.23/8.89 | 25.08 | - |
| overlap\|A | D5 | 1485.12 | P90 98%, G23 1%, SG550 1% | 15.56/9.55/12.21 | 208.51 | 2.45 ± 0.10 |
| overlap\|A | Disc2 | 5538.02 | P90 100% | 39.56/16.96/17.04 | 217.04 | 2.69 ± 0.09 |
| overlap\|C | D1 | 115.19 | M84F 100% | 6/0.02/0.02 | 6.02 | - |
| overlap\|C | D2-4 | 998.31 | SG550 40%, M9 2 27%, G19 20% | 18.29/9.64/15.72 | 30.62 | - |
| overlap\|C | D5 | 1421.95 | G23 91%, M9 2 5%, SG550 2% | 21.88/11.68/19.47 | 29.75 | 4.21 ± 0.10 |
| overlap\|C | Disc2 | 5443.03 | MAG 99%, P90 1% | 56.37/14.88/29.50 | 51.30 | 2.40 ± 0.25 |
| overlap\|I | D1 | 115.19 | M84F 100% | 6.01/0.02/0.01 | 6.01 | - |
| overlap\|I | D2-4 | 994.75 | SG550 40%, M9 2 24%, M11 22% | 15.99/10.87/13.05 | 28.97 | - |
| overlap\|I | D5 | 1406.73 | G23 92%, M9 2 4%, SG550 2% | 19.53/13.73/15.21 | 27.41 | 4.12 ± 0.12 |
| overlap\|I | Disc2 | 5395.26 | MAG 98%, P90 2% | 40.17/21.50/23.97 | 47.57 | 2.35 ± 0.25 |
| serial\|A | D1 | 115.19 | M84F 100% | 5.01/0.02/0.01 | 6.01 | - |
| serial\|A | D2-4 | 974.14 | M11 29%, MP5K 28%, SG550 25% | 12.78/6.80/8.58 | 27.84 | - |
| serial\|A | D5 | 1491.39 | P90 100% | 15.45/9.19/11.90 | 211.90 | 2.89 ± 0.02 |
| serial\|A | Disc2 | 5484.80 | P90 100% | 39.14/16.53/16.80 | 216.80 | 4.90 ± 0.10 |
| serial\|C | D1 | 115.19 | M84F 100% | 6.01/0.02/0.01 | 6.01 | - |
| serial\|C | D2-4 | 1027.58 | M11 51%, M9 2 21%, G19 20% | 19.42/9.65/15.21 | 30.68 | - |
| serial\|C | D5 | 1454.48 | G23 65%, G19 18%, M9 2 8% | 24.26/11.75/18.47 | 29.10 | 6.09 ± 0.14 |
| serial\|C | Disc2 | 5610.83 | P90 100% | 43.92/18.46/22.48 | 222.48 | 4.19 ± 0.12 |
| serial\|I | D1 | 115.19 | M84F 100% | 6.01/0.02/0.01 | 6.01 | - |
| serial\|I | D2-4 | 1017.62 | M11 50%, M9 2 22%, G19 17% | 16.03/11.06/13.17 | 28.75 | - |
| serial\|I | D5 | 1442.82 | G23 54%, M11 24%, G19 11% | 19.51/13.77/15.38 | 28.09 | 6.35 ± 0.07 |
| serial\|I | Disc2 | 5568.66 | P90 100% | 38.36/23.38/23.85 | 223.85 | 4.42 ± 0.12 |

## Exploration sensitivity

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|C | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |
| overlap\|C_minimal | 3.41 ± 0.19 | 4069.28 | 3059 | 964.10 | 10.28 | 28.01 | P90 77%, MAG 23% |
| overlap\|C_completionist | 1.94 ± 0.25 | 6432.10 | 5289 | 1096.52 | 3.72 | 29.01 | MAG 100% |
| overlap\|C_farmer | 1.47 ± 0.19 | 6647.76 | 5391 | 1206.27 | 1.89 | 28.01 | MAG 99%, P90 1% |
| serial\|C | 4.19 ± 0.12 | 5610.83 | 4441 | 1122 | 19.69 | 28.01 | P90 100% |
| serial\|C_minimal | 6.04 ± 0.21 | 4114.26 | 3102 | 964.70 | 13.83 | 28 | P90 100% |
| serial\|C_completionist | 3.34 ± 0.20 | 6589.40 | 5426 | 1113.04 | 19.77 | 29.01 | P90 100% |
| serial\|C_farmer | 3.89 ± 0.12 | 6816.26 | 5518 | 1247.88 | 22.57 | 28.01 | P90 100% |

D1 and D2–4 resource states are recorded but not combat-benchmarked in this experiment. A dash is not a zero clear time. Farmers add modeled repeat encounters; this is not a validated farming route or an estimate of real hours required. Completionist gear and uniform within-phase pickup timing can bring items earlier than a real route would.
