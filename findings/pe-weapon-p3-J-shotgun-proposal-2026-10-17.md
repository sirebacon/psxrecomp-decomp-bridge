# Phase 3 report J: Revised shotgun experiments S0–S4

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|S0 | 3.58 ± 0.15 | 5130.86 | 4033 | 1054.17 | 0 | 28.01 | M10B 100% |
| overlap\|S1 | 3.60 ± 0.16 | 5110.32 | 3994 | 1058.93 | 0 | 28.01 | M10B 100% |
| overlap\|S2 | 3.05 ± 0.15 | 5110.32 | 3994 | 1058.93 | 0 | 28.01 | M10B 100% |
| overlap\|S3 | 3.52 ± 0.14 | 5132.98 | 4016 | 1062.84 | 0 | 28.01 | M10B 100% |
| overlap\|S4 | 3.04 ± 0.15 | 5110.05 | 4002 | 1055.87 | 0 | 28.01 | M10B 100% |
| serial\|S0 | 6.19 ± 0.24 | 5083.63 | 4013 | 1019.36 | 0 | 28.01 | M10B 100% |
| serial\|S1 | 6.10 ± 0.27 | 5078.32 | 4001 | 1026.60 | 0 | 28.01 | M10B 100% |
| serial\|S2 | 5.43 ± 0.22 | 5078.32 | 4001 | 1026.60 | 0 | 28.01 | M10B 100% |
| serial\|S3 | 6.12 ± 0.22 | 5093.20 | 4005 | 1034.18 | 0 | 28.01 | M10B 100% |
| serial\|S4 | 5.39 ± 0.19 | 5087.89 | 4007 | 1036.51 | 0 | 28.01 | M10B 100% |

## Paired differences

| comparison group | D5 difference seconds | Disc2 difference seconds |
|---|---|---|
| overlap\|S0 | -0.11 ± 0.03 | -0.02 ± 0.10 |
| overlap\|S2 | 0.00 ± 0.00 | -0.55 ± 0.02 |
| overlap\|S3 | -0.11 ± 0.03 | -0.08 ± 0.09 |
| overlap\|S4 | 0.00 ± 0.00 | -0.56 ± 0.03 |
| serial\|S0 | -0.20 ± 0.05 | 0.09 ± 0.22 |
| serial\|S2 | 0.00 ± 0.00 | -0.68 ± 0.06 |
| serial\|S3 | -0.20 ± 0.05 | 0.01 ± 0.22 |
| serial\|S4 | 0.00 ± 0.00 | -0.72 ± 0.11 |

S0/S2/S3/S4 differences use S1 as the matched reference. S1 rows elsewhere use C. S0: no BP bullets; S1: normal specialist; S2: proximity benchmark; S3: base Bullet +1 without BP bullets; S4: base Bullet +1 plus proximity benchmark.

| group | Disc2 close-in suite seconds | close-normal damage taken |
|---|---|---|
| overlap\|S0 | 3.43 ± 0.15 | 84.76 ± 6.68 |
| overlap\|S1 | 3.47 ± 0.16 | 90.00 ± 7.89 |
| overlap\|S2 | 2.95 ± 0.15 | 76.29 ± 4.66 |
| overlap\|S3 | 3.38 ± 0.14 | 84.45 ± 7.29 |
| overlap\|S4 | 2.93 ± 0.15 | 77.28 ± 5.28 |
| serial\|S0 | 5.69 ± 0.22 | 157.39 ± 9.60 |
| serial\|S1 | 5.63 ± 0.24 | 157.35 ± 11.57 |
| serial\|S2 | 4.96 ± 0.20 | 116.92 ± 12.68 |
| serial\|S3 | 5.60 ± 0.20 | 155.51 ± 9.25 |
| serial\|S4 | 4.92 ± 0.17 | 117.21 ± 12.97 |

Proximity in S2/S4 is a checkpoint-only combat experiment (+40% within 400 units, fading to zero at 650). Campaign hit feedback and policy scoring remain CURRENT, so this does not measure a full-campaign proximity economy. Close-in policy assumes a 350-unit stopping distance and increased hit risk; real reachability is unmeasured.

Recommendation: retain stock magazine and CURRENT damage pending runtime measurements. Progression can solve capacity, while the remaining shotgun clear-time gap warrants testing an optional proximity mechanic. Avoid treating a faster benchmark as proof that the proposed coefficient is balanced or needed throughout the campaign.
