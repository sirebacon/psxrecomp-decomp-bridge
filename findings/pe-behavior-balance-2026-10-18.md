# Counter and enemy-charge balance rerun — 2026-10-18

12816 fights; 8 matched frozen campaign seeds per group, 6 fights per encounter.
Uses historically earned equipment; campaigns were not reoptimized. Enemy script policies
are explicit charge-step60/90/120 sensitivity scenarios, not extracted enemy-specific AI.
HP385 and reserve budgets999 per pool are controlled inputs.

Disc2 baseline results (lower score is better; read win fraction first):

| Charge step | Group | Score ± 95% Monte Carlo interval | Win fraction |
|---|---|---:|---:|
| 60 | C | 10.140 ± 1.755 | 0.974 |
| 60 | G | 9.365 ± 1.911 | 0.969 |
| 60 | D | 7.998 ± 1.587 | 0.984 |
| 60 | controlled_handgun | 11.314 ± 2.144 | 0.953 |
| 60 | controlled_shotgun | 12.506 ± 2.100 | 0.964 |
| 60 | controlled_machine | 5.150 ± 0.752 | 1.000 |
| 60 | controlled_rifle | 10.145 ± 1.754 | 0.974 |
| 60 | controlled_grenade | 14.193 ± 3.936 | 0.927 |
| 90 | C | 11.661 ± 2.403 | 0.922 |
| 90 | G | 10.415 ± 2.552 | 0.938 |
| 90 | D | 8.605 ± 1.439 | 0.964 |
| 90 | controlled_handgun | 12.263 ± 1.997 | 0.911 |
| 90 | controlled_shotgun | 16.687 ± 1.945 | 0.859 |
| 90 | controlled_machine | 5.318 ± 0.884 | 0.995 |
| 90 | controlled_rifle | 11.655 ± 2.406 | 0.922 |
| 90 | controlled_grenade | 17.853 ± 6.006 | 0.833 |
| 120 | C | 14.083 ± 2.912 | 0.865 |
| 120 | G | 11.933 ± 2.905 | 0.880 |
| 120 | D | 10.099 ± 2.354 | 0.911 |
| 120 | controlled_handgun | 18.001 ± 5.398 | 0.802 |
| 120 | controlled_shotgun | 19.015 ± 4.756 | 0.797 |
| 120 | controlled_machine | 5.714 ± 1.205 | 0.974 |
| 120 | controlled_rifle | 14.132 ± 2.912 | 0.865 |
| 120 | controlled_grenade | 20.371 ± 6.736 | 0.760 |

Equal-slot intervention: replace an existing Quickdraw with Counter (negative score delta favors Counter):

| Charge step | Phase | Eligible seed-loadouts | Mean score delta | Mean win delta | Successful counters |
|---|---|---:|---:|---:|---:|
| 60 | Disc2 | 50 | 4.123 | -0.017 | 200 |
| 90 | Disc2 | 50 | 6.172 | -0.062 | 345 |
| 120 | Disc2 | 50 | 6.784 | -0.074 | 456 |

Score is the geometric mean of encounter mean time +60*(1-win fraction).
Intervals measure Monte Carlo variation under the assumptions, not certainty about retail balance.
Counter eligibility/roll/one-command/gauge cost follow source. Idle reaction settling and
enemy-specific AI/action parameters remain approximations. Rank and HP-level fallbacks are
explicitly documented in pe-counter-enemy-derivation-2026-10-18.md.
No gameplay changes or new global balance recommendation are made from this sensitivity rerun.
