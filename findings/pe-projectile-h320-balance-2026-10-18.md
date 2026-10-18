# Counter and enemy-charge balance rerun — 2026-10-18

12816 fights; 8 matched frozen campaign seeds per group, 6 fights per encounter.
Uses historically earned equipment; campaigns were not reoptimized. Enemy script policies
use static declarations where matched and charge-step60/90/120 fallback elsewhere; action selection remains assumed.
HP385 and reserve budgets999 per pool are controlled inputs.

Disc2 baseline results (lower score is better; read win fraction first):

| Charge step | Group | Score ± 95% Monte Carlo interval | Win fraction |
|---|---|---:|---:|
| 60 | C | 11.104 ± 2.222 | 0.948 |
| 60 | G | 9.868 ± 1.890 | 0.958 |
| 60 | D | 7.718 ± 1.118 | 0.979 |
| 60 | controlled_handgun | 12.746 ± 3.103 | 0.911 |
| 60 | controlled_shotgun | 14.273 ± 2.479 | 0.906 |
| 60 | controlled_machine | 5.178 ± 0.648 | 0.995 |
| 60 | controlled_rifle | 11.132 ± 2.241 | 0.948 |
| 60 | controlled_grenade | 16.533 ± 4.253 | 0.859 |
| 90 | C | 11.501 ± 2.343 | 0.932 |
| 90 | G | 10.284 ± 2.389 | 0.943 |
| 90 | D | 8.090 ± 1.008 | 0.969 |
| 90 | controlled_handgun | 13.773 ± 3.002 | 0.880 |
| 90 | controlled_shotgun | 16.101 ± 2.100 | 0.859 |
| 90 | controlled_machine | 5.379 ± 0.820 | 0.990 |
| 90 | controlled_rifle | 11.531 ± 2.371 | 0.932 |
| 90 | controlled_grenade | 17.569 ± 5.184 | 0.839 |
| 120 | C | 12.632 ± 2.514 | 0.896 |
| 120 | G | 11.231 ± 2.549 | 0.917 |
| 120 | D | 9.715 ± 1.686 | 0.927 |
| 120 | controlled_handgun | 15.557 ± 4.964 | 0.844 |
| 120 | controlled_shotgun | 17.486 ± 3.704 | 0.818 |
| 120 | controlled_machine | 5.535 ± 0.872 | 0.984 |
| 120 | controlled_rifle | 12.666 ± 2.548 | 0.896 |
| 120 | controlled_grenade | 18.578 ± 5.945 | 0.812 |

Equal-slot intervention: replace an existing Quickdraw with Counter (negative score delta favors Counter):

| Charge step | Phase | Eligible seed-loadouts | Mean score delta | Mean win delta | Successful counters |
|---|---|---:|---:|---:|---:|
| 60 | Disc2 | 50 | 5.474 | -0.039 | 229 |
| 90 | Disc2 | 50 | 6.024 | -0.051 | 303 |
| 120 | Disc2 | 50 | 6.482 | -0.061 | 351 |

Static declaration scenario: 18138/23838 enemy instances matched by exact map + rank/kind.
Matched charge/rank/poison literals override sensitivity defaults. Action selection and windup/recovery remain assumed.
Static declarations are not a control-flow or runtime execution proof. Conflicting and missing identities fall back.

Action timing scenario: fast; matched 3579/23838 enemy instances.
Chooses shortest/longest complete extracted melee action per matching identity; this is not decoded retail choice probability.
Verified straight post-command zero-charge setters enable reset at completion; other reset behavior retains the generic assumption.
Unresolved actions, parent animation sharing, interruptions, movement and hit delivery remain assumptions.

Projectile scenario: map156 ID0x0216, launch height320; 432 matched enemy instances, 942 orbs launched, 426 geometry contacts.
Outer chooser gates assumed entered; close distance<1300 selects melee, far path forces slot4. Flat floor, stationary point player, aligned heading; projectile jitter ranges follow source.
Visual tail completion uses an explicit 24-update bound; full effect pool traversal and process ordering remain unresolved.

Score is the geometric mean of encounter mean time +60*(1-win fraction).
Intervals measure Monte Carlo variation under the assumptions, not certainty about retail balance.
Counter eligibility/roll/one-command/gauge cost follow source. Idle reaction settling and
enemy-specific AI/action parameters remain approximations. Rank and HP-level fallbacks are
explicitly documented in pe-counter-enemy-derivation-2026-10-18.md.
No gameplay changes or new global balance recommendation are made from this sensitivity rerun.
