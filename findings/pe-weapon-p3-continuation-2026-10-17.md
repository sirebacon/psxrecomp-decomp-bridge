# Phase 3 continuation: timing robustness and paired policy comparisons

Date: October 17, 2026 (America/New_York). Author: Codex.

## What was done

Recovered the referenced ChatGPT conversation and its three report attachments, then located
Claude's implementation in this repository. Read the mechanics audit, architecture, experiment
driver, evaluator, surrogate, policies, prior integrated proposal, and original SimulationPrompt.
The conversation reader returned reference markers instead of the earlier assistant prose;
the local source and reports supplied the working context.

The original suite passed **56 tests**. Fixed a timing-sensitive memoization bug in
`tools/pe_weapon_sim/economy/surrogate.py`: `_score` used the global TIMING but omitted it from
the cache key. A process that scored a loadout under overlap could return the same cached score
under serial timing. The fix keys and explicitly passes the selected timing. Added a regression
test comparing warm-cache and cold-cache results across timing switches. **57 tests now pass.**

This does not prove Claude's multiprocessing results were affected: those experiments usually
created separate pools. It does establish that mixed-timing runs in the same process were unsafe.
Original outputs remain historical evidence and have not been overwritten.

Added `tools/pe_weapon_sim/economy/run_continuation.py` and ran six groups: policies C (marginal
optimizer), G (ATB-first), and B_shotgun (favorite-class specialist), each under overlap and serial
timing. Each group uses typical exploration and matched campaign seeds 1–80. Seeds 1–40 receive
full combat benchmarks at D5 and Disc2, with ten fights per encounter. That is 480 campaign runs
and 240 benchmarked campaigns, each benchmarked at two checkpoints. Raw per-seed records,
summaries, paired differences, and hashes of the driver/evaluator/surrogate files are preserved.

## Results

Times below are means of the engine's geometric-mean encounter clear-time score, in seconds.
These are model outputs, not measured gameplay times. Lower is better.

| ATB assumption | Policy | D5 time | Disc2 time | Disc2 main gun across 80 campaigns | AT levels bought at end |
|---|---|---:|---:|---|---:|
| Overlap | C | 5.735 | 2.396 | MAG 79, P90 1 | 1.89 |
| Overlap | G | 4.495 | 2.230 | MAG 77, P90 3 | 15.41 |
| Overlap | B_shotgun | 6.724 | 3.597 | M10B 80 | 0 |
| Serial | C | 8.434 | 4.194 | P90 80 | 19.70 |
| Serial | G | 8.197 | 4.002 | P90 80 | 21.32 |
| Serial | B_shotgun | 10.870 | 6.103 | M10B 80 | 0 |

Paired differences compare the same seed's policy outcomes. Positive means slower than C.
Intervals use the existing runner's approximate normal 95% CI; they cover simulation variation
across campaign seeds, not uncertainty about actual game mechanics or encounter design.

| ATB assumption | Comparison | D5 difference | Disc2 difference |
|---|---|---:|---:|
| Overlap | G minus C | -1.241 ± 0.223 | -0.165 ± 0.176 |
| Overlap | B_shotgun minus C | +0.988 ± 0.224 | +1.201 ± 0.246 |
| Serial | G minus C | -0.237 ± 0.289 | -0.192 ± 0.058 |
| Serial | B_shotgun minus C | +2.436 ± 0.408 | +1.909 ± 0.240 |

G's late overlap advantage is unresolved by this interval. Its late serial advantage is small
but consistent in this sample. These are comparisons of whole policies, including differences
in gear and feedback-driven BP earnings, not a controlled causal estimate of one BP purchase.
G beating C also shows the surrogate's marginal optimizer is not a globally optimal policy.

The favorite-shotgun policy is **not using a shotgun at D5**: overlap has G23 in 66/80 and M11
in 14/80 campaigns; serial has G23 in 65/80 and M11 in 15/80. Do not interpret its D5 results as
an M10B test. At Disc2 it does use M10B in every run, with mean magazine about 33 in both timing
models. That supports the narrower claim that this policy can upgrade well beyond seven rounds;
it does not establish early availability or that casual players choose the same upgrades.

## Current recommendations

1. Measure ATB refill during firing before recommending a P90 or MAG nerf. Their selection flips
   under the two plausible timing assumptions even after earned progression is modeled.
2. Keep the proposed M10B base-magazine increase unimplemented. The specialist already reaches
   substantial capacity through the existing economy; early acquisition and opportunity cost
   still require targeted analysis.
3. Shotgun viability remains worth investigating: its late specialist policy is slower under
   both timing models. This is not an equal-investment weapon-only comparison, because the
   specialist uses weighted BP and listed mods while C uses marginal BP and greedy mods.
4. Retain proximity damage as an experiment only. This continuation did not rerun S0–S4 and
   does not establish a new proximity coefficient or balance recommendation.

## Reproduction

Working directory: `D:\Recomp Games\psxrecomp-decomp-bridge\tools`.
Use the bundled Python below; this machine's ordinary `python` command points to an unusable
Windows Store alias.

```powershell
$simPython = 'C:\Users\maver\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $simPython -m unittest discover -s pe_weapon_sim/tests
& $simPython -m pe_weapon_sim.economy.run_continuation --n 80 --bench 40 --workers 4
```

New output: `findings/data/pe-weapon-p3-continuation-2026-10-17.json`.
Original `pe-weapon-p3-results-2026-10-17.json`, tables, campaign, and traces are untouched.
No game source, compiled mods, saves, or balance values were changed. No commits were made.

## Next work for Claude

- Read this report and the handoff file first; preserve original Phase 3 artifacts.
- Add a same-policy controlled class comparison: same acquisition/budget logic with different
  favorite classes, plus an adaptive ATB strategy for the shotgun specialist.
- Record first M10B acquisition and first reachable 8/12/16-round capacity by seed and profile.
  Show resources spent and what was deferred, not just final magazine sizes.
- Run S0–S4 under both timing assumptions with paired differences. Existing S2/S4 alter checkpoint
  benchmark rules only; their progression feedback remains CURRENT. Label that limitation or
  propagate experimental combat consistently before calling them full experimental campaigns.
- Complete the remaining original requested reports C–L. This continuation adds one focused
  report; it does not claim those deliverables are complete.
- Validate actual refill/firing timing, incoming armor damage, and pickup timing before treating
  simulation intervals as confidence in real-world weapon balance. Current hit feedback is
  calibrated surrogate/Poisson behavior, not a full model of enemy attacks and armor defense.
- Audit Spearman tie handling in `evaluation.spearman`: it currently assigns distinct ranks to
  equal values. Existing rank-agreement figures should be treated as approximate until corrected.
