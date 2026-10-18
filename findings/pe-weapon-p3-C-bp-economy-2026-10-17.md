# Phase 3 report C: BP economy and opportunity costs

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|A | 2.69 ± 0.09 | 5538.02 | 4017 | 1074.83 | 0 | 32.01 | P90 100% |
| overlap\|C | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |
| overlap\|G | 2.23 ± 0.21 | 5471.55 | 4362 | 1059.37 | 15.33 | 28.01 | MAG 97%, P90 3% |
| overlap\|H | 2.38 ± 0.26 | 5402.29 | 4252 | 1099.61 | 1.20 | 32.01 | MAG 100% |
| overlap\|I | 2.35 ± 0.25 | 5395.26 | 4278 | 1070.40 | 8.88 | 31.02 | MAG 98%, P90 2% |
| overlap\|S_def | 2.50 ± 0.27 | 5373.32 | 4226 | 1096.58 | 0 | 28.02 | MAG 100% |
| overlap\|S_save | 2.38 ± 0.26 | 5422.85 | 4273 | 1101.55 | 2.01 | 28.01 | MAG 100% |
| overlap\|S_wpn | 2.46 ± 0.27 | 5407.35 | 4264 | 1089.94 | 0 | 28.01 | MAG 100% |
| serial\|A | 4.90 ± 0.10 | 5484.80 | 3958 | 1075.63 | 0 | 32.01 | P90 100% |
| serial\|C | 4.19 ± 0.12 | 5610.83 | 4441 | 1122 | 19.69 | 28.01 | P90 100% |
| serial\|G | 4.00 ± 0.10 | 5646.91 | 4456 | 1134.39 | 21.24 | 28.01 | P90 100% |
| serial\|H | 4.32 ± 0.10 | 5566.25 | 4399 | 1121.08 | 18.43 | 32.01 | P90 100% |
| serial\|I | 4.42 ± 0.12 | 5568.66 | 4406 | 1116.12 | 8.99 | 31.02 | P90 100% |
| serial\|S_def | 4.58 ± 0.11 | 5519.55 | 4357 | 1117.68 | 14.80 | 28.02 | P90 100% |
| serial\|S_save | 4.04 ± 0.10 | 5606.44 | 4429 | 1129.85 | 21.13 | 28.01 | P90 100% |
| serial\|S_wpn | 4.48 ± 0.11 | 5584.93 | 4418 | 1118.86 | 0 | 28.01 | P90 100% |

| group | attack BP | range BP | bullets BP | AT BP | capacity BP | armor BP | unspent incl. pool |
|---|---|---|---|---|---|---|---|
| overlap\|A | 1807 | 609 | 400 | 0 | 604 | 597 | 1521.02 |
| overlap\|C | 2908 | 2 | 1196 | 187 | 0 | 0 | 1150.03 |
| overlap\|G | 2467 | 4 | 358 | 1533 | 0 | 0 | 1109.55 |
| overlap\|H | 2427 | 0 | 905 | 120 | 800 | 0 | 1150.29 |
| overlap\|I | 1297 | 660 | 624 | 888 | 409 | 400 | 1117.26 |
| overlap\|S_def | 1319 | 0 | 407 | 0 | 0 | 2500 | 1147.32 |
| overlap\|S_save | 3374 | 0 | 698 | 201 | 0 | 0 | 1149.85 |
| overlap\|S_wpn | 2526 | 887 | 851 | 0 | 0 | 0 | 1143.35 |
| serial\|A | 1766 | 605 | 400 | 0 | 601 | 586 | 1526.80 |
| serial\|C | 1802 | 158 | 512 | 1969 | 0 | 0 | 1169.83 |
| serial\|G | 2161 | 171 | 0 | 2124 | 0 | 0 | 1190.91 |
| serial\|H | 1334 | 121 | 301 | 1843 | 800 | 0 | 1167.25 |
| serial\|I | 1309 | 693 | 666 | 899 | 438 | 401 | 1162.66 |
| serial\|S_def | 306 | 71 | 0 | 1480 | 0 | 2500 | 1162.55 |
| serial\|S_save | 2111 | 205 | 0 | 2113 | 0 | 0 | 1177.44 |
| serial\|S_wpn | 2621 | 900 | 897 | 0 | 0 | 0 | 1166.93 |

| comparison group | D5 difference seconds | Disc2 difference seconds |
|---|---|---|
| overlap\|G | -0.79 ± 0.13 | -0.17 ± 0.18 |
| serial\|G | -0.05 ± 0.14 | -0.19 ± 0.06 |

Differences above are relative to optimizer C within the same timing model; negative is faster. These are whole-policy comparisons with combat-feedback earnings, not isolated returns on one BP point. One weapon stat point costs 100 BP; buying it defers one AT stat level or one capacity stat level. Capacity stat levels need not grant an inventory slot at every step. Armor defense currently does not reduce simulated incoming damage, so this model cannot fairly value defense-first investment. BP after the final level-up remains pending and cannot be spent. Do not convert earned totals directly into affordable upgrades. The optimizer is a surrogate-guided heuristic, not a proven optimum.
