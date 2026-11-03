# Native weapon balance: proposals to discuss — 2026-10-26

**No game balance changes made.** The native checkout, saved settings, and game executable were not modified. Only the separate bridge simulator, regression tests, and reports changed.

31,656 simulated fights in three completed batches. The screening covers 38 distinct main-campaign guns (18 available in the early-stage pool), at D2–4, museum-era D5, and Disc2. Chrysler-only weapons, clubs, and other special weapons are outside this ladder.
The disputed five weapons were repeated at four seeds and low / typical / high investment, with up to twelve ordinary encounters plus four bosses per stage. M10B also received stock and attack-only investment checks.

## What changes the earlier conclusion

The earlier decision to drop buffs relied on each gun receiving favorable Catalog installs. That establishes upgraded potential; it does not establish that the pickup is satisfying with its built-in effects alone. These runs keep those questions separate.
A simulator bug was corrected: the source combat callback reset installed RoF damage to the built-in percentage at each hit. Historical reports remain untouched, but their precise values should not be treated as equivalent to these corrected runs.
The review additionally maps native integer attack scaling, element scaling, defense division, and hit-quality rounding. 2,000 randomized cases matched the native C damage helper compiled unchanged. Twenty focused regression tests passed. Whole-fight behavior remains a model, not execution of the native game.

## Attack proposals worth discussing

D5 ordinary fights, typical investment, built-in effects only. Negative time change means faster. These are separate alternatives, not installed changes.

| Weapon | Candidate | Native setup → candidate | Time change | Catalog time change, same baseline loadout |
|---|---|---|---:|---:|
| M79 2 | +20 attack | 39.65s → 32.16s | -18.9% | -5.8% |
| M203 3 | +20 attack | 38.51s → 31.57s | -18.0% | -5.0% |
| M79 3 | +20 attack | 40.17s → 30.39s | -24.3% | -0.7% |
| PPK | +5 attack | 28.40s → 25.09s | -11.6% | -5.6% |

**M79-2 +20 and M203-3 +20:** reopen these proposals if pickups should stand on their own. The benefit persists across all three investment levels; the Catalog versions are already competitive, so stronger optimized builds are the tradeoff.
**M79-3:** the old +10 is not robust at low investment. +20 crosses the useful breakpoint at all three tested investment levels; +15 misses it at low investment. Discuss it alongside the other two grenades, and compare with M203-4 before approving a package.
**PPK:** +5 is the conservative candidate; do not automatically take +10. The baseline is already near the overall D5 median and has built-in Quickdraw. A buff helps comfort, but it is a lower priority than the grenade progression.

## Magazine proposals

The historical low / typical / high profiles already add 10 / 15 / 20 magazine rounds at D5. Their lack of response to a magazine buff cannot establish that the stock M10B is comfortable.
The dedicated checks below remove magazine investment: stock = zero investment in any stat; attack_only = typical attack and range investment but zero magazine investment.

| Stage | Setup | Investment | Candidate | Ordinary seconds | Boss seconds |
|---|---|---|---|---|---|
| D5 | builtin | attack_only | magazine_plus1 | 23.62 → 23.62 | 40.89 → 40.43 |
| D5 | builtin | attack_only | magazine_plus50pct | 23.62 → 23.62 | 40.89 → 40.43 |
| D5 | builtin | stock | magazine_plus1 | 25.21 → 25.04 | 43.23 → 42.90 |
| D5 | builtin | stock | magazine_plus50pct | 25.21 → 24.95 | 43.23 → 42.56 |
| D5 | catalog | attack_only | magazine_plus1 | 21.35 → 21.35 | 31.93 → 31.93 |
| D5 | catalog | attack_only | magazine_plus50pct | 21.35 → 21.35 | 31.93 → 31.93 |
| D5 | catalog | stock | magazine_plus1 | 22.45 → 22.27 | 33.57 → 33.35 |
| D5 | catalog | stock | magazine_plus50pct | 22.45 → 22.23 | 33.57 → 33.35 |
| Disc2 | builtin | attack_only | magazine_plus1 | 15.49 → 15.49 | 67.74 → 67.07 |
| Disc2 | builtin | attack_only | magazine_plus50pct | 15.49 → 15.49 | 67.74 → 66.85 |
| Disc2 | builtin | stock | magazine_plus1 | 18.20 → 18.31 | 96.54 → 95.66 |
| Disc2 | builtin | stock | magazine_plus50pct | 18.20 → 18.09 | 96.54 → 94.77 |
| Disc2 | catalog | attack_only | magazine_plus1 | 8.57 → 8.46 | 17.75 → 17.73 |
| Disc2 | catalog | attack_only | magazine_plus50pct | 8.57 → 8.32 | 17.75 → 15.47 |
| Disc2 | catalog | stock | magazine_plus1 | 8.73 → 8.73 | 23.80 → 24.08 |
| Disc2 | catalog | stock | magazine_plus50pct | 8.73 → 8.58 | 23.80 → 20.13 |

M10B +1 round has little impact here. A +50% magazine helps the Catalog-equipped Disc2 boss cases with no magazine investment (23.80s → 20.13s stock; 17.75s → 15.47s with attack/range investment), but ordinary-fight gains are small and the effect disappears with the historical magazine investments. This supports a conditional comfort discussion, not a blanket shotgun damage buff.

## Other guns

Keep the existing six attack bonuses as the baseline. The broad screen does not justify a blanket buff to older guns simply because Wayne or later pickups beat them. M79 is reasonably close to the early-stage median; its late-game lag is an expected replacement curve. M203-2 already receives +15 and should remain a comparison point when adjusting the later grenades.
Machine guns, rifles, shotguns, and rockets retain different crowd, boss, range, and ammo roles. This screen does not establish a new P90/MAG adjustment. Rocket campaign viability is not tested by unlimited-reserve isolated battles.

## Limits and discussion

Results use one historical logged campaign and modeled movement, enemy behavior, and shot scheduling. Boss absolutes are less reliable than paired comparisons. The sample is stratified, so ordinary and boss averages must not be added into an unweighted campaign score. Catalog is an optimistic best-of-tested-loadouts estimate, not guaranteed player ownership.
Native crowd-cap binary-search granularity, delayed hit processing, status-at-minimum-damage behavior, and RNG replay are not reproduced exactly. Critical conversion retains the inherited 26.67% model chance versus native integer 26%. The disputed five weapons have no built-in Critical.
Recommendation for the discussion: decide whether an unmodified pickup should be a useful upgrade, then consider the three grenade +20 proposals together. Treat PPK +5 as optional and discuss M10B capacity separately. Do not install any balance changes from this report automatically.

## Detailed evidence

- [native-review-2026-10-26](pe-native-review-2026-10-26.md): full tables; paired boss/ordinary data and intervals in `data/pe-native-review-2026-10-26-candidates.csv`.
- [native-dropped-buffs-2026-10-26](pe-native-dropped-buffs-2026-10-26.md): full tables; paired boss/ordinary data and intervals in `data/pe-native-dropped-buffs-2026-10-26-candidates.csv`.
- [native-shotgun-capacity-2026-10-26](pe-native-shotgun-capacity-2026-10-26.md): full tables; paired boss/ordinary data and intervals in `data/pe-native-shotgun-capacity-2026-10-26-candidates.csv`.

## Reproduce

From the bridge repository, set PYTHONPATH to tools and run:

```text
python -m unittest pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat pe_weapon_sim.tests.test_compare_rules
python -m pe_weapon_sim.run_native_review --seeds 2 --workers 4
python -m pe_weapon_sim.run_native_review --only "M79 2" "M203 3" "M79 3" PPK M10B --stages D5 Disc2 --invest low typical high --seeds 4 --battle-limit 12 --extended --tag native-dropped-buffs-2026-10-26
python -m pe_weapon_sim.run_native_review --only M10B --stages D5 Disc2 --invest stock attack_only --seeds 4 --battle-limit 12 --workers 2 --tag native-shotgun-capacity-2026-10-26
python -m pe_weapon_sim.report_native_review native-review-2026-10-26
python -m pe_weapon_sim.report_native_review native-dropped-buffs-2026-10-26
python -m pe_weapon_sim.report_native_review native-shotgun-capacity-2026-10-26
python -m pe_weapon_sim.report_native_discussion
```

Native defaults and source hashes are recorded in `data/pe-native-defaults-audit-2026-10-26.json`; follow-up batches also embed that audit. Historical result files were preserved.
