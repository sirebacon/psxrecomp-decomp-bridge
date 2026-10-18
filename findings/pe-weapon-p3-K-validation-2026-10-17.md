# Phase 3 report K: Corrections, sensitivity, and validation

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

## Corrections

Checkpoint equipment is now deep-copied. Earlier checkpoints previously referenced live Item objects that could gain later upgrades or be zeroed/deleted by a transfer. This contaminated combat benchmarks while compact checkpoint summaries retained the old values. Timing is part of the surrogate cache key. Spearman now uses average ranks for ties and Pearson correlation of ranks; constant vectors return undefined.

| phase | corrected Spearman | loadouts |
|---|---|---|
| D2-4 | 0.937 | 30 |
| D5 | 0.969 | 30 |
| Disc2 | 0.789 | 30 |

## Resource ablations

| group | suite seconds ±95% CI | BP earned | BP spent | pending BP | AT bought | capacity | main gun |
|---|---|---|---|---|---|---|---|
| overlap\|C | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |
| overlap\|A1 | 4.12 ± 0.29 | 5282.44 | 4172 | 1059.79 | 4.69 | 28 | MAG 76%, P90 24% |
| overlap\|A2 | 3.75 ± 0.11 | 5216.30 | 0 | 1043.99 | 0 | 28.02 | MAG 97%, P90 3% |
| overlap\|A3 | 3.81 ± 0.46 | 5227.79 | 0 | 1027.36 | 0 | 28 | MAG 79%, P90 21% |
| overlap\|A4 | 3.16 ± 0.06 | 5351.35 | 4218 | 1086.35 | 1.59 | 28.02 | MAG 93%, P90 7% |
| overlap\|A5 | 2.67 ± 0.29 | 5319.81 | 0 | 1078.27 | 0 | 28.01 | MAG 100% |
| overlap\|A6 | 3.17 ± 0.36 | 5406.23 | 4281 | 1075.74 | 5.82 | 28 | MAG 73%, P90 27% |
| overlap\|A7 | 2.40 ± 0.25 | 5443.03 | 4293 | 1100.90 | 1.87 | 28.01 | MAG 99%, P90 1% |

A1 BP only; A2 donors only; A3 rare only; A4 BP+donors; A5 donors+rare; A6 BP+rare; A7 all three. Catalog/Junk and fixed pickups remain enabled in these ablations, so “only” describes the three switched progression systems, not all resources. These tests include policy adaptation and feedback; they are not additive decompositions.

All new campaign runs check accounting and inventory invariants. Unit tests cover snapshot isolation, mixed-timing caching, tied ranks, transfers, loot and ledger behavior. Combat uses fitted enemy damage, simplified movement, and no armor-defense mitigation. The random stream is seeded by campaign, but different state-dependent cascade paths consume different draws. This matches seeds and encounter opportunities, not identical rewards across policies. Priority runtime measurements: refill while firing, animation time per shot, real shotgun distance/risk, armor mitigation, and acquisition timing.
