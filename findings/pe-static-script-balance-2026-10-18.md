# Counter and enemy-charge balance rerun — 2026-10-18

12816 fights; 8 matched frozen campaign seeds per group, 6 fights per encounter.
Uses historically earned equipment; campaigns were not reoptimized. Enemy script policies
use static declarations where matched and charge-step60/90/120 fallback elsewhere; action selection remains assumed.
HP385 and reserve budgets999 per pool are controlled inputs.

Disc2 baseline results (lower score is better; read win fraction first):

| Charge step | Group | Score ± 95% Monte Carlo interval | Win fraction |
|---|---|---:|---:|
| 60 | C | 10.932 ± 2.207 | 0.953 |
| 60 | G | 9.903 ± 1.978 | 0.958 |
| 60 | D | 7.674 ± 1.114 | 0.979 |
| 60 | controlled_handgun | 12.733 ± 3.113 | 0.911 |
| 60 | controlled_shotgun | 14.534 ± 3.218 | 0.911 |
| 60 | controlled_machine | 5.191 ± 0.647 | 0.995 |
| 60 | controlled_rifle | 10.954 ± 2.223 | 0.953 |
| 60 | controlled_grenade | 16.019 ± 4.199 | 0.870 |
| 90 | C | 11.371 ± 2.284 | 0.938 |
| 90 | G | 10.353 ± 2.351 | 0.943 |
| 90 | D | 8.314 ± 1.054 | 0.958 |
| 90 | controlled_handgun | 13.641 ± 3.074 | 0.885 |
| 90 | controlled_shotgun | 15.825 ± 2.063 | 0.870 |
| 90 | controlled_machine | 5.423 ± 0.835 | 0.990 |
| 90 | controlled_rifle | 11.396 ± 2.303 | 0.938 |
| 90 | controlled_grenade | 17.533 ± 5.167 | 0.839 |
| 120 | C | 12.619 ± 2.599 | 0.896 |
| 120 | G | 11.374 ± 2.554 | 0.911 |
| 120 | D | 9.631 ± 1.692 | 0.927 |
| 120 | controlled_handgun | 15.464 ± 5.038 | 0.849 |
| 120 | controlled_shotgun | 17.186 ± 3.703 | 0.828 |
| 120 | controlled_machine | 5.573 ± 0.897 | 0.984 |
| 120 | controlled_rifle | 12.647 ± 2.621 | 0.896 |
| 120 | controlled_grenade | 18.434 ± 6.015 | 0.818 |

Equal-slot intervention: replace an existing Quickdraw with Counter (negative score delta favors Counter):

| Charge step | Phase | Eligible seed-loadouts | Mean score delta | Mean win delta | Successful counters |
|---|---|---:|---:|---:|---:|
| 60 | Disc2 | 50 | 5.632 | -0.043 | 235 |
| 90 | Disc2 | 50 | 6.376 | -0.057 | 304 |
| 120 | Disc2 | 50 | 6.764 | -0.066 | 342 |

Static declaration scenario: 18138/23838 enemy instances matched by exact map + rank/kind.
Matched charge/rank/poison literals override sensitivity defaults. Action selection and windup/recovery remain assumed.
Static declarations are not a control-flow or runtime execution proof. Conflicting and missing identities fall back.

Score is the geometric mean of encounter mean time +60*(1-win fraction).
Intervals measure Monte Carlo variation under the assumptions, not certainty about retail balance.
Counter eligibility/roll/one-command/gauge cost follow source. Idle reaction settling and
enemy-specific AI/action parameters remain approximations. Rank and HP-level fallbacks are
explicitly documented in pe-counter-enemy-derivation-2026-10-18.md.
No gameplay changes or new global balance recommendation are made from this sensitivity rerun.
