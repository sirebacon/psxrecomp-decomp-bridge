# Phase 3 report H: Controlled class-policy comparisons

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|controlled_handgun | 3.60 ± 0.11 | 5207.18 | 4152 | 1007.69 | 0.74 | 28.01 | USP TU 100% |
| overlap\|controlled_shotgun | 2.73 ± 0.15 | 5344.83 | 4193 | 1100.27 | 26.44 | 28.01 | M10B 100% |
| overlap\|controlled_machine | 2.38 ± 0.08 | 5584.06 | 4406 | 1134.16 | 15.83 | 28.01 | P90 100% |
| overlap\|controlled_rifle | 2.41 ± 0.25 | 5427.82 | 4276 | 1103.71 | 1.78 | 28.01 | MAG 100% |
| overlap\|controlled_grenade | 3.85 ± 0.38 | 5047.43 | 4032 | 965.35 | 0.93 | 28.01 | HK40 77%, M8000 23% |
| serial\|controlled_handgun | 5.79 ± 0.17 | 5257.81 | 4206 | 1002.34 | 9.86 | 28.01 | USP TU 100% |
| serial\|controlled_shotgun | 5.29 ± 0.17 | 5358.02 | 4230 | 1083.54 | 22.27 | 28.01 | M10B 100% |
| serial\|controlled_machine | 4.24 ± 0.12 | 5598.35 | 4430 | 1122.80 | 19.20 | 28.01 | P90 100% |
| serial\|controlled_rifle | 3.25 ± 0.22 | 5432.41 | 4290 | 1090.72 | 18.35 | 28.01 | MAG 100% |
| serial\|controlled_grenade | 5.28 ± 0.22 | 5107.73 | 4057 | 1001.77 | 10.93 | 28.01 | HK40 100% |

## Paired differences from unrestricted C

| comparison group | D5 difference seconds | Disc2 difference seconds |
|---|---|---|
| overlap\|controlled_handgun | -0.22 ± 0.14 | 1.21 ± 0.24 |
| overlap\|controlled_shotgun | 0.00 ± 0.00 | 0.33 ± 0.25 |
| overlap\|controlled_machine | 0.33 ± 0.12 | -0.01 ± 0.25 |
| overlap\|controlled_rifle | 0.07 ± 0.10 | 0.01 ± 0.02 |
| overlap\|controlled_grenade | 0.21 ± 0.16 | 1.46 ± 0.44 |
| serial\|controlled_handgun | -0.40 ± 0.16 | 1.60 ± 0.18 |
| serial\|controlled_shotgun | 0.00 ± 0.00 | 1.09 ± 0.10 |
| serial\|controlled_machine | 0.15 ± 0.19 | 0.04 ± 0.05 |
| serial\|controlled_rifle | 0.05 ± 0.07 | -0.95 ± 0.22 |
| serial\|controlled_grenade | 0.24 ± 0.19 | 1.08 ± 0.15 |

All controlled class policies inherit C’s BP, mod, donor, purchasing, and switching decision settings; only preferred class changes. This controls decision logic, not identical realized earnings, gear, or resource spending. Gear must be acquired through the economy. The preferred class can be unavailable earlier; inspect checkpoint gun shares before calling any row a class-specific benchmark. These results cover policies and their chosen guns, not every individual named gun at equal investment. M500 versus M10B and earlier individual weapons still need targeted fixed-loadout comparisons if decisions depend on them. P90/MAG dominance must be conditioned on timing assumptions; no nerf follows from a single model.
