# Phase 3 report L: Integrated conclusions and next decisions

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|A | 2.69 ± 0.09 | 5538.02 | 4017 | 1074.83 | 0 | 32.01 | P90 100% |
| overlap\|C | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |
| overlap\|G | 2.23 ± 0.21 | 5471.55 | 4362 | 1059.37 | 15.33 | 28.01 | MAG 97%, P90 3% |
| overlap\|controlled_shotgun | 2.73 ± 0.15 | 5344.83 | 4193 | 1100.27 | 26.44 | 28.01 | M10B 100% |
| serial\|C | 4.19 ± 0.12 | 5610.83 | 4441 | 1122 | 19.69 | 28.01 | P90 100% |
| serial\|G | 4.00 ± 0.10 | 5646.91 | 4456 | 1134.39 | 21.24 | 28.01 | P90 100% |
| serial\|controlled_shotgun | 5.29 ± 0.17 | 5358.02 | 4230 | 1083.54 | 22.27 | 28.01 | M10B 100% |

The corrected optimizer selects MAG in 99/100 overlap campaigns and P90 in all 100 serial campaigns. With the optimizer’s decision rules, the shotgun preference finishes at 2.73 versus 2.40 seconds under overlap and 5.29 versus 4.19 under serial (benchmark means over 40 seeds). Its gap is smaller than the older weighted-BP shotgun specialist’s, so player decision rules explain part of the apparent class deficit. These comparisons retain differences in earned resources and available gear.

The no-BP-bullets specialist reaches at least eight M10B rounds in 100/100 seeds under each timing model, and at least twelve in 99/100. All first M10B observations are in Disc2 in this acquisition model. This supports later customization availability but cannot establish early comfort or an early-game need for an extra built-in round. Conditional checkpoint proximity improves that specialist’s late benchmark by 0.55 ± 0.02 seconds under overlap and 0.68 ± 0.06 under serial, while its progression feedback remains unchanged.



## Decisions supported now

- Use these corrected checkpoint results in place of the original combat tables.
- Preserve the BP, donor, Tool and rare systems; they provide distinct resource routes.
- Defer a permanent M10B Bullet +1 until acquisition and opportunity-cost findings are checked against actual play. Final specialist capacity is not evidence of early comfort.
- Defer P90/MAG changes until timing is measured. Their rankings depend on that assumption.
- Keep shotgun proximity experimental and measure risk and distance before selecting values.

## Coverage and unresolved questions

Reports C–G quantify modeled BP availability, spending competition, capacity behavior, gear/Tool flows, rare feedback, provenance, and magazine milestones. Reports H–J compare class preferences, two-weapon components, mod frequency, and S0–S4. Report K documents correctness checks, ablations and uncertainty.

The following original questions remain only partially answered: exact useful donor-gun counts (the inherited counter includes armor/offered gear), mandatory Commands/Quickdraw (no matched removal experiment), a true two-weapon battle strategy, direct defense/capacity utility in real play, all individual named-gun rankings, and full-campaign proximity effects. Simulation does not establish whether rare rewards make experimentation feel affordable to humans or whether farming is enjoyable. Those require controlled follow-ups and playtests.

## Reproduce

From the repository tools directory, run:

```powershell
$simPython = 'C:\Users\maver\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $simPython -m unittest discover -s pe_weapon_sim/tests
& $simPython -m pe_weapon_sim.economy.run_completion --n 100 --bench 40 --workers 4
& $simPython -m pe_weapon_sim.economy.report_completion
```

Raw JSON stores seed-level checkpoint states, benchmarks, milestone provenance, paired differences, experiment specifications and source hashes. Original results are preserved. No live game source, binaries or saves were changed.
