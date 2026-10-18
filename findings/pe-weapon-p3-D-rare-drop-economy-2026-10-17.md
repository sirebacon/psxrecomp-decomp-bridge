# Phase 3 report D: Rare rewards and Tool feedback

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | Tools field | Tools drops | Tools rare | Tools bought | Tools spent | boosters field | boosters rare | overflow events |
|---|---|---|---|---|---|---|---|---|
| overlap\|A | 14 | 2 | 2.41 | 0 | 9.33 | 33 | 5.81 | 0 |
| overlap\|C | 14 | 2 | 3.02 | 6.22 | 19.58 | 33 | 5.92 | 0 |
| overlap\|G | 14 | 2 | 3.09 | 6.21 | 19.54 | 33 | 5.75 | 0 |
| overlap\|H | 14 | 2 | 3.11 | 6.10 | 19.52 | 33 | 5.78 | 0 |
| overlap\|I | 14 | 2 | 3.17 | 5.91 | 19.55 | 33 | 5.75 | 0 |

| group | mean rare rewards per campaign |
|---|---|
| overlap\|A | booster: 5.81, TOOL: 2.41, MOD PERMIT: 2.36, Salvager: 0.81, Bargain: 0.79, SUPER TOOL: 0.75, LuckyFind: 0.7, SUPER JUNK: 0.7, Scavenger: 0.5, DUPER JUNK: 0.27 |
| overlap\|C | booster: 5.92, TOOL: 3.02, MOD PERMIT: 2.54, Salvager: 0.86, Bargain: 0.83, SUPER TOOL: 0.79, SUPER JUNK: 0.73, LuckyFind: 0.69, Scavenger: 0.56, DUPER JUNK: 0.3 |
| overlap\|G | booster: 5.75, TOOL: 3.09, MOD PERMIT: 2.54, Salvager: 0.87, Bargain: 0.83, SUPER TOOL: 0.81, SUPER JUNK: 0.72, LuckyFind: 0.69, Scavenger: 0.54, DUPER JUNK: 0.3 |
| overlap\|H | booster: 5.78, TOOL: 3.11, MOD PERMIT: 2.56, Salvager: 0.87, Bargain: 0.83, SUPER TOOL: 0.79, SUPER JUNK: 0.72, LuckyFind: 0.69, Scavenger: 0.56, DUPER JUNK: 0.32 |
| overlap\|I | booster: 5.75, TOOL: 3.17, MOD PERMIT: 2.52, Salvager: 0.87, Bargain: 0.82, SUPER TOOL: 0.8, SUPER JUNK: 0.74, LuckyFind: 0.68, Scavenger: 0.53, DUPER JUNK: 0.3 |

Normal pity starts at 4%, gains one percentage point per dry battle, and guarantees a rare when dry+1 reaches 25. Lucky Find adds two dry steps on failure, not a new reward table. Within a rare cascade, the Tool branch rolls at 85/65/40/20/10% for 0/1/2/3/4 Tools held and skips at 5+ or with a kit. Earlier cascade branches can win first, so those numbers are conditional branch chances, not per-battle Tool probabilities. Spending Tools raises later Tool eligibility; hoarding suppresses Tool rewards and allows more later-branch boosters. Observed differences also include policies buying Tools and wearing economy mods. The model does not establish that players should waste Tools to manipulate drops.
