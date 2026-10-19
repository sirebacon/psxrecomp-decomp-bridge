# Current-model simulation — October 18, 2026

Disc2 P90 controlled loadouts led this sample: 99.48–100% wins and 5.90–5.96 seconds
mean fight time across the timing bounds. This is conditional on frozen earned equipment
and the assumptions below. Group labels describe historical campaign policies; the grenade
group includes HK40 on six seeds and M8000 on two, rather than a uniform weapon.

Validation: 284 full-suite tests and 125 separate beam-validation tests passed. All 6,144
fights passed ammunition conservation checks. No simulation source or consumed data changed
during the run; the reported beam-validation JSON fingerprint change is an independent
validation output rewritten during execution, not a combat input.

Source power covered 7,124 incoming hits; 9,123 hits used fallback damage (56.15%). Static
declarations matched 9,296/11,424 appearances. The reach model rejected 1,760/4,933 tested
melee strikes. These are overlapping feature counters, not complete-enemy coverage rates.

6,144 fights using 8 frozen campaign seeds, 6 fights per encounter, D5 and Disc2, and early/late contact bounds.
User authorized this rerun after Claude’s latest additions. No game interaction. Equipment and BP purchase counts are frozen; source stat tables recalculate Aya’s stats.

| Contact | Phase | Group | Win % | Mean seconds | Mean damage taken | Mean rounds |
|---|---|---|---:|---:|---:|---:|
| early | D5 | C | 99.0 | 14.46 | 90.0 | 7.9 |
| early | D5 | G | 99.5 | 12.19 | 69.1 | 7.9 |
| early | D5 | D | 97.9 | 17.33 | 102.2 | 11.6 |
| early | D5 | controlled_handgun | 98.4 | 13.93 | 88.9 | 7.5 |
| early | D5 | controlled_shotgun | 99.0 | 14.46 | 90.0 | 7.9 |
| early | D5 | controlled_machine | 97.9 | 15.77 | 100.6 | 9.3 |
| early | D5 | controlled_rifle | 95.8 | 15.43 | 106.3 | 7.3 |
| early | D5 | controlled_grenade | 97.4 | 15.81 | 98.5 | 8.1 |
| early | Disc2 | C | 89.1 | 9.02 | 124.1 | 5.6 |
| early | Disc2 | G | 90.1 | 8.45 | 114.8 | 5.7 |
| early | Disc2 | D | 95.8 | 8.04 | 95.5 | 43.0 |
| early | Disc2 | controlled_handgun | 90.1 | 9.80 | 130.2 | 5.5 |
| early | Disc2 | controlled_shotgun | 88.5 | 11.21 | 139.0 | 8.8 |
| early | Disc2 | controlled_machine | 100.0 | 5.96 | 58.4 | 10.7 |
| early | Disc2 | controlled_rifle | 89.1 | 9.02 | 123.9 | 5.6 |
| early | Disc2 | controlled_grenade | 84.4 | 10.86 | 143.8 | 8.1 |
| late | D5 | C | 97.9 | 14.77 | 89.8 | 8.1 |
| late | D5 | G | 99.5 | 12.05 | 68.4 | 7.8 |
| late | D5 | D | 97.4 | 17.04 | 101.6 | 11.2 |
| late | D5 | controlled_handgun | 98.4 | 14.02 | 87.7 | 7.6 |
| late | D5 | controlled_shotgun | 97.9 | 14.77 | 89.8 | 8.1 |
| late | D5 | controlled_machine | 95.8 | 16.40 | 100.6 | 9.8 |
| late | D5 | controlled_rifle | 94.8 | 15.48 | 103.7 | 7.3 |
| late | D5 | controlled_grenade | 96.9 | 16.05 | 98.9 | 8.2 |
| late | Disc2 | C | 89.6 | 9.01 | 115.4 | 5.6 |
| late | Disc2 | G | 91.7 | 8.56 | 106.6 | 5.8 |
| late | Disc2 | D | 96.4 | 8.16 | 85.8 | 43.3 |
| late | Disc2 | controlled_handgun | 89.1 | 9.94 | 124.9 | 5.5 |
| late | Disc2 | controlled_shotgun | 90.1 | 11.26 | 134.6 | 8.8 |
| late | Disc2 | controlled_machine | 99.5 | 5.90 | 55.6 | 10.6 |
| late | Disc2 | controlled_rifle | 89.6 | 9.02 | 115.0 | 5.6 |
| late | Disc2 | controlled_grenade | 86.5 | 10.97 | 137.6 | 8.2 |

## Interpretation limits

These are scenario results, not a final retail balance verdict. HP385 and effectively ample ammunition are controlled inputs. Source max HP is not used because the prior save had an HP bug.
Distance profiles are sampled encounter scenarios, not continuous world navigation. Melee reach uses facing actors on a common floor and captured idle Aya geometry. Early/late timing bounds do not reconstruct per-frame player movement.
Overlapping choice guards select the lowest slot; unknown actions retain approximations. Slot0 is the explicit fallback power selection, not a claim that retail enemies always choose it. Missing source charge/timing uses step90 and windup/recovery10.
Boss encounters retain incomplete generic behavior; the validated beam volley adapter is not a complete boss AI and is not enabled here. Frozen equipment was optimized under earlier rules, so this run does not establish newly optimal campaign policies.

Inputs changed during run: ['findings\\data\\pe-beam-combat-validation-2026-10-18.json'].

## Feature counters

```json
{
  "catalog_matches": 9296,
  "catalog_foes": 11424,
  "choice_matches": 2640,
  "power_catalog_foes": 11424,
  "power_catalog_matches": 5120,
  "choice_strikes_slot0": 2197,
  "melee_reach_strikes": 4933,
  "explicit_power_hits": 7124,
  "choice_strikes_slot3": 3625,
  "action_timing_matches": 1616,
  "melee_window_matches": 1616,
  "contact_timing_matches": 2000,
  "effect_action_matches": 1136,
  "legacy_damage_hits": 9123,
  "melee_reach_misses": 1760,
  "choice_waits": 826,
  "status_poison": 663,
  "status_already": 588,
  "choice_strikes_slot1": 111,
  "status_stiffness_slow": 119
}
```
