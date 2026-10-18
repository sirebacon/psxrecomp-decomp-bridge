# Phase 3 report G: M10B acquisition and reachable capacity

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | milestone | reached | phase counts | mean battle if reached | cumulative bullet BP if reached |
|---|---|---|---|---|---|
| overlap\|S0 | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69 | 0 |
| overlap\|S0 | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69.9 | 0 |
| overlap\|S0 | mag12 | 99/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 99} | 69.7 | 0 |
| overlap\|S0 | mag16 | 98/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 98} | 69.3 | 0 |
| overlap\|S1 | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69 | 336 |
| overlap\|S1 | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 70.4 | 347 |
| overlap\|S1 | mag12 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 71.3 | 355 |
| overlap\|S1 | mag16 | 98/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 98} | 70.8 | 351.0 |
| overlap\|controlled_shotgun | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69 | 622 |
| overlap\|controlled_shotgun | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 70.5 | 639 |
| overlap\|controlled_shotgun | mag12 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 71.4 | 641 |
| overlap\|controlled_shotgun | mag16 | 99/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 99} | 70.9 | 638.4 |
| serial\|S0 | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69 | 0 |
| serial\|S0 | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 70.1 | 0 |
| serial\|S0 | mag12 | 99/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 99} | 70.4 | 0 |
| serial\|S0 | mag16 | 97/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 97} | 69.3 | 0 |
| serial\|S1 | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69.3 | 325 |
| serial\|S1 | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 70.5 | 331 |
| serial\|S1 | mag12 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 71.6 | 343 |
| serial\|S1 | mag16 | 99/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 99} | 71.9 | 346.5 |
| serial\|controlled_shotgun | acquired | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 69 | 512 |
| serial\|controlled_shotgun | mag8 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 70.3 | 525 |
| serial\|controlled_shotgun | mag12 | 100/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 100} | 71.5 | 541 |
| serial\|controlled_shotgun | mag16 | 99/100 | {'D1': 0, 'D2-4': 0, 'D5': 0, 'Disc2': 99} | 71.5 | 533.3 |

Milestones are first observations of a live owned M10B after policy maintenance. An item can gain several points in one maintenance pass, so this is a conservative observation time, not the exact transaction time. Counts are conditional on the modeled acquisition policy and log-derived availability. Cumulative bullet BP includes previous weapons; it is not the direct cost paid on M10B alone. Raw records retain origins and cumulative Tool/Junk spending at each milestone.

A direct Bullet +1 costs 100 spendable BP; a donor route costs one Tool and an available donor with a Bullet bonus, transferring its other bonuses too. A suitable booster adds its tier without a Tool, but its acquisition is random. S0 spends no BP on bullets; compare its milestones with S1 before claiming BP is necessary. None of these routes guarantees an early pickup. The original fixed-capacity grid remains a controlled mechanical experiment, not evidence that every grid build is obtainable in a normal campaign.
