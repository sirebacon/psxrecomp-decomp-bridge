# Phase 3 targeted validation follow-ups

320 new invariant-checked campaign replays; 40 matched seeds per policy/timing group. Each D5 and Disc2 checkpoint uses 20 fights per encounter. Original historical JSON and reports C–L are preserved. No live gameplay or save changes.

## Timing source audit

Local decompiled action processing sets game flag 0x100, and Aya’s gauge update is gated by that flag. This favors serial-style pause behavior; it does not calibrate every animation or establish a new real-time clock. See `pe-weapon-p3-runtime-validation-plan.md` for verified source locations, caveats and a concrete frame-level capture protocol. No new runtime capture was performed. Both timing hypotheses remain explicitly tested.

## Matched mod-removal experiments

Positive differences mean slower than the identical baseline checkpoint. Removing Commands sets the command count to one; removing Quickdraw disables its effect. Other stats and effects remain fixed. Slots are left empty, no replacement effect is added, and progression is not rerun with the weakened gun. C = optimizer, G = ATB-first, controlled_shotgun = C’s decision rules with a shotgun preference, D = two-weapon policy main gun.

| group | phase | Commands present | Quickdraw present | baseline seconds | remove Commands Δs | remove Quickdraw Δs | remove both Δs |
|---|---|---|---|---|---|---|---|
| overlap\|C | D5 | 0/40 | 0/40 | 4.44 ± 0.12 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| overlap\|C | Disc2 | 40/40 | 14/40 | 2.24 ± 0.25 | 1.29 ± 0.06 | 0.57 ± 0.24 | 1.84 ± 0.25 |
| overlap\|G | D5 | 0/40 | 0/40 | 3.59 ± 0.09 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| overlap\|G | Disc2 | 40/40 | 24/40 | 2.00 ± 0.20 | 1.57 ± 0.17 | 0.92 ± 0.23 | 2.47 ± 0.36 |
| overlap\|controlled_shotgun | D5 | 0/40 | 0/40 | 4.44 ± 0.12 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| overlap\|controlled_shotgun | Disc2 | 40/40 | 36/40 | 2.38 ± 0.14 | 2.64 ± 0.04 | 1.20 ± 0.13 | 3.68 ± 0.12 |
| overlap\|D | D5 | 0/40 | 0/40 | 5.15 ± 0.09 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| overlap\|D | Disc2 | 40/40 | 38/40 | 4.19 ± 0.17 | 1.40 ± 0.18 | 1.44 ± 0.11 | 2.66 ± 0.22 |
| serial\|C | D5 | 0/40 | 0/40 | 6.62 ± 0.13 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| serial\|C | Disc2 | 40/40 | 38/40 | 3.49 ± 0.11 | 3.27 ± 0.08 | 1.24 ± 0.09 | 4.22 ± 0.10 |
| serial\|G | D5 | 0/40 | 0/40 | 6.40 ± 0.14 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| serial\|G | Disc2 | 40/40 | 38/40 | 3.33 ± 0.10 | 3.06 ± 0.05 | 1.23 ± 0.09 | 4.09 ± 0.09 |
| serial\|controlled_shotgun | D5 | 0/40 | 0/40 | 6.62 ± 0.13 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| serial\|controlled_shotgun | Disc2 | 40/40 | 36/40 | 4.40 ± 0.17 | 4.14 ± 0.07 | 1.23 ± 0.13 | 5.58 ± 0.14 |
| serial\|D | D5 | 0/40 | 0/40 | 8.71 ± 0.14 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| serial\|D | Disc2 | 40/40 | 38/40 | 6.00 ± 0.18 | 2.86 ± 0.13 | 1.32 ± 0.11 | 4.28 ± 0.22 |

Intervals are the inherited normal approximation over paired campaign-seed differences. They do not include model error. If an effect is absent, its removal is a no-op; presence counts give the relevant denominator. This quantifies the cost of removal in the tested loadouts, not whether the effect is mandatory after legal replacement/reinvestment.

## Gauge-clock sensitivity on frozen final loadouts

Only the engine’s fill-time conversion changes. The 94-Hz value is the historical aggregate-turn calibration; 59.9 is an alternative suggested by the logger frame conversion, not a newly measured gauge tick rate. Earned equipment, BP strategy and encounter samples stay fixed. A full campaign under a different clock can make different investment choices.

| group | 94-Hz suite seconds | 59.9-Hz suite seconds | paired Δs |
|---|---|---|---|
| overlap\|C | 2.24 ± 0.25 | 3.23 ± 0.37 | 0.99 ± 0.12 |
| overlap\|G | 2.00 ± 0.20 | 2.65 ± 0.31 | 0.65 ± 0.11 |
| overlap\|controlled_shotgun | 2.38 ± 0.14 | 3.54 ± 0.21 | 1.16 ± 0.07 |
| overlap\|D | 4.19 ± 0.17 | 4.50 ± 0.18 | 0.31 ± 0.12 |
| serial\|C | 3.49 ± 0.11 | 4.33 ± 0.16 | 0.85 ± 0.05 |
| serial\|G | 3.33 ± 0.10 | 4.15 ± 0.14 | 0.82 ± 0.04 |
| serial\|controlled_shotgun | 4.40 ± 0.17 | 5.71 ± 0.24 | 1.32 ± 0.08 |
| serial\|D | 6.00 ± 0.18 | 6.82 ± 0.21 | 0.82 ± 0.08 |

## Two-weapon screening

For each encounter, the optimistic envelope picks the faster of the two separately benchmarked weapons. A second version adds half of the secondary weapon’s fill time when choosing it. Both assume advance knowledge of the encounter and start each component fight independently. They do not simulate enemy actions during a switch, within-fight switching, shared ammo, menu/animation time or carried ATB. The half-fill delay is an assumed scalar cost screen informed by the CURRENT half-bar switch, not a validated switch-duration model. Negative deltas are optimistic improvements versus the main gun.

| group | phase | secondary owned | both suites win | free-choice Δs | half-fill-cost Δs | runs with any secondary niche after delay |
|---|---|---|---|---|---|---|
| overlap\|D | D5 | 40/40 | 40/40 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 |
| overlap\|D | Disc2 | 40/40 | 40/40 | -1.10 ± 0.10 | -0.47 ± 0.06 | 40 |
| serial\|D | D5 | 40/40 | 40/40 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 |
| serial\|D | Disc2 | 38/40 | 38/38 | -0.98 ± 0.06 | -0.60 ± 0.03 | 38 |

The envelope analysis excludes runs with any component encounter win rate below 99.9%. It compares D’s two components, not D against an equally funded single-gun policy. A benefit here is only a candidate niche to test dynamically; a lack of benefit does not rule out movement, status or tactical benefits absent from the encounter model.

## What remains

- Measure guest-frame gauge increments, firing/reload duration and the half-bar weapon change using the capture protocol. Source evidence is stronger than before, but runtime duration remains unmeasured.
- For any high-cost mod removal, test a legal alternative effect with the same slot and resource budget before calling it mandatory.
- Verify actual early Wayne access and 300-Junk timing. The simulated first M10B observation reflects policy behavior, not the earliest legal acquisition.
- Build a dynamic switching model only around an observed secondary niche and validate its gauge/ammo/animation transitions against captured gameplay.

## Reproduce

From `D:/Recomp Games/psxrecomp-decomp-bridge/tools`, use the bundled Python:

```powershell
$simPython = 'C:\Users\maver\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $simPython -m unittest discover -s pe_weapon_sim/tests
& $simPython -m pe_weapon_sim.economy.run_followups --n 40
& $simPython -m pe_weapon_sim.economy.report_followups
```

Raw output: `data/pe-weapon-p3-followups-2026-10-17.json`. It includes paired seed-level benchmarks, portfolio component win rates, clock alternatives, parameters and source hashes.
