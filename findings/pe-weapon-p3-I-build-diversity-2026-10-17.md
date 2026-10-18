# Phase 3 report I: Build diversity and two-weapon investment

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | final mod frequency | secondary suite seconds |
|---|---|---|
| overlap\|controlled_handgun | 2Cmd: 100%, Heat: 100%, Quickdraw: 93%, Random: 63%, RoF2: 13% | - |
| overlap\|controlled_shotgun | RoF2: 100%, Burst: 100%, Heat: 100%, 2Cmd: 100%, Quickdraw: 92% | - |
| overlap\|controlled_machine | RoF2: 100%, AttackAll: 100%, Heat: 100%, 2Cmd: 100%, Quickdraw: 95% | - |
| overlap\|controlled_rifle | RoF2: 100%, Random: 100%, Heat: 100%, 2Cmd: 100%, Critical: 96%, Quickdraw: 49% | - |
| overlap\|controlled_grenade | Heat: 100%, 2Cmd: 100%, Quickdraw: 94%, RoF2: 77%, Random: 77% | - |
| serial\|controlled_handgun | 2Cmd: 100%, Heat: 100%, Quickdraw: 93%, Random: 64%, RoF2: 13% | - |
| serial\|controlled_shotgun | Burst: 100%, Heat: 100%, 2Cmd: 100%, RoF2: 99%, Quickdraw: 92%, RoF3: 1% | - |
| serial\|controlled_machine | RoF2: 100%, AttackAll: 100%, Heat: 100%, 2Cmd: 100%, Quickdraw: 95% | - |
| serial\|controlled_rifle | Heat: 100%, 2Cmd: 100%, RoF2: 99%, Random: 99%, Critical: 97%, Quickdraw: 47%, RoF3: 1% | - |
| serial\|controlled_grenade | Heat: 100%, RoF2: 100%, Random: 100%, 2Cmd: 100%, Quickdraw: 89% | - |
| overlap\|D | 2Cmd: 100%, Quickdraw: 95%, RoF10: 83%, AttackAll: 83%, Acid: 61%, RoF3: 17%, Burst: 17% | 3.54 ± 0.10 |
| serial\|D | 2Cmd: 100%, Quickdraw: 95%, RoF10: 90%, AttackAll: 90%, Acid: 67%, RoF3: 10%, Critical: 10% | 6.08 ± 0.12 |

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|C | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |
| overlap\|D | 4.77 ± 0.19 | 4753.64 | 3809 | 895.61 | 3.21 | 28.01 | P90 83%, M10B 17% |
| serial\|C | 4.19 ± 0.12 | 5610.83 | 4441 | 1122 | 19.69 | 28.01 | P90 100% |
| serial\|D | 6.81 ± 0.21 | 5049.57 | 4023 | 974.74 | 0.26 | 28.01 | P90 90%, MAG 10% |

Frequent Commands or Quickdraw selections show these policies favor them; they do not prove either effect is mandatory. Establishing that requires matched mod-removal experiments at the same legal slot budget. Secondary scores benchmark each gun separately; the model does not simulate a dynamic two-gun encounter policy with switch time and shared ammunition. Do not treat the better of the two scores as an achievable free-switch result. Transferable BP lowers sunk equipment cost, but maintaining two simultaneous bonus pools still competes for donors and Tools.
