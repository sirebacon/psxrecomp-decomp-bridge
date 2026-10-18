# Phase 3 report E: Donor equipment and transfer costs

Generated from `data/pe-weapon-p3-completion-2026-10-17.json` using corrected checkpoint snapshots and timing-separated surrogate scores. Original Phase 3 tables and the first continuation remain historical artifacts; their checkpoint combat results are superseded here.

Each group: 100 matched campaign seeds; first 40 seeds benchmarked at D5 and Disc2, ten fights per encounter. CIs describe Monte Carlo variation under the model, not confidence in actual game mechanics. Overlap and serial are alternative ATB assumptions. Fixed pickup timing and exploration profiles remain assumptions derived from one logged campaign. No gameplay changes were implemented.

| group | gear pickups offered | stat transfers | extracted atk | extracted range | extracted bullets | BP bonus points moved | Tools left | unused gun bonuses |
|---|---|---|---|---|---|---|---|---|
| overlap\|A | 26.59 | 8.33 | 41.10 | 19.30 | 20.42 | 4.44 | 9.08 | 8.60 |
| overlap\|C | 26.59 | 18.58 | 91.98 | 43.89 | 70.14 | 32.40 | 5.66 | 0 |
| overlap\|G | 26.59 | 18.54 | 75.37 | 45.31 | 56.91 | 0.01 | 5.76 | 0 |
| overlap\|H | 26.59 | 18.52 | 74.86 | 43.43 | 59.80 | 7.59 | 5.69 | 0 |
| overlap\|I | 26.59 | 18.55 | 80.20 | 48.36 | 59.34 | 18.61 | 5.53 | 0 |

| group | Tools field | Tools drops | Tools rare | Tools bought | Tools spent | boosters field | boosters rare | overflow events |
|---|---|---|---|---|---|---|---|---|
| overlap\|A | 14 | 2 | 2.41 | 0 | 9.33 | 33 | 5.81 | 0 |
| overlap\|C | 14 | 2 | 3.02 | 6.22 | 19.58 | 33 | 5.92 | 0 |
| overlap\|G | 14 | 2 | 3.09 | 6.21 | 19.54 | 33 | 5.75 | 0 |
| overlap\|H | 14 | 2 | 3.11 | 6.10 | 19.52 | 33 | 5.78 | 0 |
| overlap\|I | 14 | 2 | 3.17 | 5.91 | 19.55 | 33 | 5.75 | 0 |

The existing metric named donors_got counts offered guns **and armor**, including gear that can overflow; it is not a count of useful donor guns. Transfer totals count actions, including switching and armor transfers, rather than distinct harvested weapons. A plain Tool transfers all three bonus axes and deletes the donor; a Super Tool preserves it with bonuses removed. Base stats do not transfer. BP-derived bonuses retain provenance and transfer exactly like other bonuses. Switching preserves investment if a Tool is available, but consumes the prior weapon under an ordinary Tool. This is not costless switching. Inventory-focused results describe this inventory policy; consumable reserves are coarse and armor defense is omitted, so a small simulated capacity benefit is not evidence that capacity is useless in play.
