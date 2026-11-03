# Remaining Chrysler weapons versus current native balance — 2026-10-26

**No native game balance, code, saved settings, or executable changes.**

35,200 simulated fights: 22,528 baseline and 12,672 candidate experiments. All 31 remaining Chrysler weapon records are included, plus 13 current-balance reference weapons. Four matched seeds per configuration. Previously reviewed Chrysler shotguns are not repeated as targets.
Current baseline includes PPK +5, M870-2 +10, M79-2 +20, M203-3 +20, M79-3 +18, and all earlier native bonuses. Both native settings defaults and source hashes were checked before and after each run. Combat stats for all 44 records were verified against the resident item pack used by the native loader (`data/pe-chrysler-items-audit-2026-10-26.json`).

## Method and coverage

Built-in effects only. Stock uses intrinsic bonuses and no player investment. attack_only adds the same late-game +50 attack/+18 range to every weapon, with zero magazine investment. Built-in RoF never receives installed-RoF power/animation changes.
Disc2 uses sampled logged campaign enemies, Aya, armor, spells, and bags. EX33/EX50 use twelve extracted Chrysler regular enemy stat blocks (including defense 200) as singles and constructed triples, fixed level 33/50 with logged endgame armor and no spells/items. EX tests are stress scenarios, not actual tower fights. There is no scripted Chrysler boss or True Eve validation, pickup-floor chronology, or complete EX economy replay.
AM444 is mapped to native AM44. Clubs 4–5 are included for damage, Counter, and Quickdraw; stealing/loot utility is not modeled. Rocket benchmarks have 999 reserve rockets and do not establish campaign ammo affordability.
A status-floor simulator correction was made before these runs: Cyanide/Acid/Tranq cannot activate when the native pre-quality damage term is non-positive. Native integer damage checks and the dedicated Cyanide regression pass. Earlier reports remain historical; these new results should be compared within this matched batch.
Times include deaths/timeouts; read the win rates. Full CSV/JSON also include successful-clear times, failure-penalized durations, ammunition, empty clicks and reloads. No weak early pickup is required to match a top Wayne gun at the upper tower.

## Weapon records

| Weapon | Class | Base + intrinsic attack | Native attack bonus | Range | Stock rounds | Built-in effects |
|---|---|---:|---:|---:|---:|---|
| CLUB 4 | Clubs — damage only | 80 | 0 | 10 | 0 | Steal, Counter, Critical |
| CLUB 5 | Clubs — damage only | 102 | 0 | 10 | 0 | Steal, Quickdraw |
| M96 | Handguns | 77 | 0 | 59 | 16 | None |
| M96R | Handguns | 89 | 0 | 59 | 20 | RoF2, 3Cmd |
| P228 | Handguns | 59 | 0 | 56 | 13 | None |
| P226 | Handguns | 63 | 0 | 57 | 12 | RoF2 |
| P229 | Handguns | 71 | 0 | 56 | 13 | RoF3 |
| M1911A3 | Handguns | 50 | 0 | 62 | 9 | RoF5 |
| M1911A4 | Handguns | 68 | 0 | 63 | 9 | None |
| M1911A5 | Handguns | 86 | 0 | 63 | 11 | None |
| USP | Handguns | 52 | 0 | 56 | 10 | RoF3 |
| USP 2 | Handguns | 58 | 0 | 59 | 11 | None |
| USP 3 | Handguns | 76 | 0 | 58 | 13 | RoF2, Quickdraw |
| MARK 23 | Handguns | 82 | 0 | 61 | 13 | RoF3, Quickdraw |
| G20 | Handguns | 65 | 0 | 62 | 14 | Counter |
| M712 | Handguns | 87 | 0 | 64 | 11 | Counter |
| AM44 | Handguns | 78 | 0 | 58 | 13 | None |
| MP5A5 | Machine guns | 68 | 0 | 48 | 29 | RoF2, AttackAll |
| MP5SD6 | Machine guns | 89 | 0 | 52 | 32 | RoF3, AttackAll |
| FULL UZ | Machine guns | 68 | 0 | 50 | 43 | RoF10, Random |
| M16A2 | Rifles | 55 | 0 | 124 | 19 | RoF3 |
| SAR | Rifles | 86 | 0 | 136 | 16 | None |
| XM177E2 | Rifles | 99 | 0 | 159 | 17 | Critical |
| PSG 1 | Rifles | 75 | 0 | 120 | 19 | RoF2 |
| FA MAS | Rifles | 119 | 0 | 169 | 26 | RoF3 |
| M203 5 | Grenade launchers | 68 | 0 | 65 | 7 | None |
| M203 6 | Grenade launchers | 81 | 0 | 68 | 8 | Cyanide |
| M79 4 | Grenade launchers | 61 | 0 | 65 | 10 | None |
| M79 5 | Grenade launchers | 75 | 0 | 69 | 8 | None |
| M79 6 | Grenade launchers | 94 | 0 | 69 | 11 | None |
| AT4 1 | Rocket launchers | 186 | 0 | 235 | 1 | None |

## Shortlist for discussion — no changes applied

These are conservative starting points for playtesting, not proven unique optima. M1911A3 and M16A2 are the clearest weak gun candidates; consider the three non-elemental grenades together to preserve their relative stats. The boss comparisons contain four sampled boss encounters × four seeds, so absolute times and exact bonus choices remain provisional.

| Weapon | Candidate flat attack bonus | Attack including intrinsic bonuses, current → proposed | Disc2 boss seconds, current → proposed | EX50 solo wins, current → proposed |
|---|---:|---:|---:|---:|
| M1911A3 | +15 | 50 → 65 | 113.27 → 99.18 | 100.0% → 100.0% |
| M16A2 | +20 | 55 → 75 | 117.70 → 101.18 | 100.0% → 100.0% |
| M203 5 | +15 | 68 → 83 | 113.36 → 100.24 | 91.7% → 95.8% |
| M79 4 | +15 | 61 → 76 | 122.87 → 104.86 | 89.6% → 93.8% |
| M79 5 | +10 | 75 → 85 | 107.93 → 99.23 | 91.7% → 95.8% |

**M1911A3 +15:** preserves its attack below M1911A4 (65 versus 68) while improving its weak built-in RoF5 performance. It still trails the single-shot M1911A4 on bosses (99.18 versus 87.90s); this is a modest repair, not proof that the built-in high-RoF tradeoff is fully solved.
**M16A2 +20:** raises intrinsic attack from 55 to 75, matching PSG-1’s nominal attack but retaining different RoF. It remains a little slower than current G3A3 and PSG-1 on sampled bosses (101.18 versus 96.74 and 92.07s). It does not obsolete either anchor.
**Grenades +15 / +15 / +10:** M79-4 reaches 76 attack with ten stock rounds; M203-5 reaches 83 with seven; M79-5 reaches 85 with eight and more range. M79-6 stays at 94 with eleven rounds, while M203-6 retains Cyanide utility. These choices avoid flattening the whole non-elemental line. They remain slower on the sampled bosses than current M203-4 / M79-3, so elemental launchers retain a role.
Ordinary-fight gains are smaller than boss gains, and larger +20 alternatives exist in the experiment tables. M203-5 and M79-5 boss intervals reach zero because some sampled bosses do not benefit; their recommendations are less strongly supported than the M1911A3/M16A2/M79-4 cases. Exact pickup-floor data and live tests are still needed before treating this as a finished Chrysler progression.
A separate stock-only grenade pass confirms the direction without any player attack/range investment: proposed EX50 solo win rates rise from 79.2% to 87.5% (M203-5), 77.1% to 85.4% (M79-4), and 85.4% to 87.5% (M79-5). Completely uninvested Disc2 boss wins remain 75% for these guns; the proposed bonuses do not turn them into universal boss or tower-clearing weapons.
Adding two magazine rounds has very little benefit for the five tested candidates. There is no evidence here for a general capacity or class-wide attack increase.
**Keep the other 26 targets for now:** the SMGs, M96R, Mark 23, USP-3, stronger rifles, M203-6, M79-6, AT4-1, and Clubs 4–5 have useful damage or built-in-effect roles. Lower-tier single-shot handguns such as P228 and USP-2 are slower, but that alone does not establish a buff when acquisition floors and ammo/utility choices are unresolved. This is a watch list, not a claim that every unmodified gun is equally strong.
Clubs already show strong offensive results; their unmodeled stealing value is additional utility. AT4-1 fits below LAW80 in this ammo-unlimited comparison, but rocket economy and splash geometry need separate validation. No nerfs or balance edits are proposed from these cases.

## Handguns / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M1911A3 | Yes | 16.73 / 100.0% | 113.27 / 100.0% | 19.69 / 100.0% | 31.40 / 66.7% |
| USP | Yes | 15.51 / 100.0% | 90.49 / 100.0% | 16.24 / 100.0% | 25.86 / 64.6% |
| USP 2 | Yes | 15.26 / 100.0% | 94.27 / 100.0% | 16.60 / 91.7% | 20.93 / 60.4% |
| P228 | Yes | 15.27 / 100.0% | 96.41 / 100.0% | 17.16 / 91.7% | 20.93 / 60.4% |
| P226 | Yes | 14.16 / 100.0% | 78.39 / 100.0% | 13.34 / 100.0% | 23.31 / 66.7% |
| G20 | Yes | 14.70 / 100.0% | 86.97 / 100.0% | 15.15 / 91.7% | 19.70 / 64.6% |
| M1911A4 | Yes | 14.84 / 100.0% | 87.90 / 100.0% | 16.26 / 91.7% | 20.93 / 60.4% |
| P229 | Yes | 14.76 / 100.0% | 77.49 / 100.0% | 14.24 / 100.0% | 24.79 / 66.7% |
| USP 3 | Yes | 10.80 / 100.0% | 67.72 / 100.0% | 9.21 / 100.0% | 20.78 / 66.7% |
| M96 | Yes | 14.55 / 100.0% | 82.13 / 100.0% | 15.26 / 95.8% | 20.88 / 62.5% |
| AM44 | Yes | 14.55 / 100.0% | 81.86 / 100.0% | 15.27 / 95.8% | 20.88 / 62.5% |
| MARK 23 | Yes | 10.93 / 100.0% | 68.33 / 100.0% | 9.76 / 100.0% | 23.28 / 66.7% |
| M1911A5 | Yes | 14.53 / 100.0% | 77.78 / 100.0% | 14.53 / 100.0% | 20.76 / 62.5% |
| M712 | Yes | 14.03 / 100.0% | 73.62 / 100.0% | 13.49 / 97.9% | 19.68 / 64.6% |
| M96R | Yes | 12.97 / 100.0% | 31.53 / 100.0% | 7.08 / 100.0% | 21.09 / 97.9% |
| PPK | Reference | 12.86 / 100.0% | 106.41 / 100.0% | 16.02 / 100.0% | 30.33 / 66.7% |
| M9 3 | Reference | 13.43 / 100.0% | 56.76 / 100.0% | 10.90 / 100.0% | 27.56 / 79.2% |
| DE50AE7 | Reference | 13.07 / 100.0% | 53.69 / 100.0% | 9.72 / 100.0% | 21.73 / 66.7% |

## Shotgun reference / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M10B | Reference | 15.49 / 100.0% | 67.74 / 100.0% | 15.48 / 100.0% | 27.87 / 68.8% |

## Machine guns / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| FULL UZ | Yes | 9.91 / 100.0% | 64.88 / 100.0% | 8.67 / 100.0% | 27.00 / 66.7% |
| MP5A5 | Yes | 10.90 / 100.0% | 41.78 / 100.0% | 11.16 / 100.0% | 17.04 / 81.2% |
| MP5SD6 | Yes | 11.04 / 100.0% | 38.62 / 100.0% | 9.90 / 100.0% | 16.92 / 89.6% |
| MP5PDW | Reference | 10.04 / 100.0% | 68.42 / 100.0% | 9.92 / 100.0% | 25.66 / 66.7% |
| P90 | Reference | 12.71 / 100.0% | 29.75 / 100.0% | 7.58 / 100.0% | 17.48 / 100.0% |

## Rifles / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M16A2 | Yes | 20.45 / 100.0% | 117.70 / 100.0% | 21.06 / 100.0% | 30.12 / 60.4% |
| PSG 1 | Yes | 20.26 / 100.0% | 92.07 / 100.0% | 16.77 / 100.0% | 28.13 / 62.5% |
| SAR | Yes | 19.72 / 100.0% | 98.91 / 100.0% | 20.03 / 95.8% | 25.62 / 58.3% |
| XM177E2 | Yes | 18.69 / 100.0% | 83.28 / 100.0% | 16.28 / 100.0% | 24.81 / 60.4% |
| FA MAS | Yes | 18.05 / 100.0% | 75.99 / 100.0% | 14.30 / 100.0% | 28.05 / 66.7% |
| G3A3 | Reference | 19.75 / 100.0% | 96.74 / 100.0% | 19.48 / 100.0% | 25.63 / 58.3% |
| MAG | Reference | 16.71 / 100.0% | 54.07 / 100.0% | 10.47 / 100.0% | 24.70 / 70.8% |

## Grenade launchers / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M79 4 | Yes | 19.94 / 100.0% | 122.87 / 100.0% | 21.60 / 89.6% | 24.42 / 58.3% |
| M203 5 | Yes | 19.27 / 100.0% | 113.36 / 100.0% | 21.23 / 91.7% | 24.42 / 58.3% |
| M79 5 | Yes | 18.72 / 100.0% | 107.93 / 100.0% | 20.00 / 91.7% | 24.42 / 58.3% |
| M203 6 | Yes | 17.75 / 100.0% | 101.80 / 100.0% | 13.17 / 95.8% | 21.25 / 68.8% |
| M79 6 | Yes | 18.45 / 100.0% | 93.03 / 100.0% | 17.79 / 100.0% | 24.27 / 60.4% |
| M79 3 | Reference | 17.20 / 100.0% | 88.61 / 100.0% | 16.68 / 97.9% | 24.45 / 66.7% |
| M203 4 | Reference | 17.20 / 100.0% | 87.31 / 100.0% | 16.30 / 100.0% | 24.31 / 66.7% |
| HK40 | Reference | 18.45 / 100.0% | 82.83 / 100.0% | 15.54 / 100.0% | 23.82 / 60.4% |

## Rocket launchers / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| AT4 1 | Yes | 13.76 / 100.0% | 76.84 / 100.0% | 20.21 / 97.9% | 20.60 / 62.5% |
| LAW80 | Reference | 12.82 / 100.0% | 67.93 / 100.0% | 17.35 / 100.0% | 18.64 / 66.7% |

## Clubs — damage only / attack_only: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| CLUB 4 | Yes | 9.21 / 100.0% | 47.73 / 100.0% | 10.08 / 100.0% | 18.88 / 79.2% |
| CLUB 5 | Yes | 7.63 / 100.0% | 42.90 / 100.0% | 7.74 / 100.0% | 18.96 / 79.2% |
| CLUB 3 | Reference | 8.59 / 100.0% | 74.51 / 100.0% | 15.42 / 91.7% | 20.76 / 66.7% |

## Handguns / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M1911A3 | Yes | 20.55 / 100.0% | 173.00 / 75.0% | 30.89 / 91.7% | 34.77 / 56.2% |
| USP | Yes | 19.03 / 100.0% | 162.26 / 75.0% | 25.07 / 89.6% | 29.64 / 58.3% |
| USP 2 | Yes | 17.55 / 100.0% | 167.09 / 75.0% | 25.18 / 83.3% | 24.83 / 58.3% |
| P228 | Yes | 17.58 / 100.0% | 165.55 / 75.0% | 24.57 / 83.3% | 24.23 / 58.3% |
| P226 | Yes | 17.10 / 100.0% | 134.46 / 100.0% | 21.32 / 91.7% | 24.26 / 58.3% |
| G20 | Yes | 16.53 / 100.0% | 157.16 / 81.2% | 20.24 / 85.4% | 22.05 / 58.3% |
| M1911A4 | Yes | 17.33 / 100.0% | 153.89 / 93.8% | 22.98 / 89.6% | 24.10 / 58.3% |
| P229 | Yes | 17.10 / 100.0% | 128.56 / 100.0% | 21.92 / 89.6% | 27.37 / 58.3% |
| USP 3 | Yes | 13.18 / 100.0% | 112.43 / 100.0% | 16.82 / 91.7% | 23.22 / 60.4% |
| M96 | Yes | 16.75 / 100.0% | 140.71 / 100.0% | 21.58 / 89.6% | 23.28 / 58.3% |
| AM44 | Yes | 16.36 / 100.0% | 135.30 / 100.0% | 21.76 / 89.6% | 23.29 / 58.3% |
| MARK 23 | Yes | 12.34 / 100.0% | 109.74 / 100.0% | 16.58 / 100.0% | 25.91 / 62.5% |
| M1911A5 | Yes | 16.13 / 100.0% | 123.02 / 100.0% | 20.08 / 91.7% | 22.73 / 58.3% |
| M712 | Yes | 15.69 / 100.0% | 119.49 / 100.0% | 17.50 / 91.7% | 21.39 / 60.4% |
| M96R | Yes | 13.24 / 100.0% | 47.88 / 100.0% | 10.10 / 100.0% | 23.34 / 83.3% |
| PPK | Reference | 17.18 / 100.0% | 171.99 / 75.0% | 27.24 / 91.7% | 34.55 / 60.4% |
| M9 3 | Reference | 15.79 / 100.0% | 103.47 / 100.0% | 20.36 / 91.7% | 29.59 / 68.8% |
| DE50AE7 | Reference | 14.34 / 100.0% | 75.26 / 100.0% | 13.19 / 100.0% | 23.04 / 66.7% |

## Shotgun reference / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M10B | Reference | 18.20 / 100.0% | 96.54 / 100.0% | 21.51 / 100.0% | 30.83 / 64.6% |

## Machine guns / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| FULL UZ | Yes | 13.52 / 100.0% | 110.19 / 100.0% | 11.98 / 100.0% | 32.34 / 62.5% |
| MP5A5 | Yes | 12.72 / 100.0% | 73.38 / 100.0% | 17.36 / 91.7% | 19.47 / 66.7% |
| MP5SD6 | Yes | 11.84 / 100.0% | 56.83 / 100.0% | 14.26 / 97.9% | 18.90 / 68.8% |
| MP5PDW | Reference | 13.71 / 100.0% | 128.72 / 100.0% | 15.98 / 100.0% | 30.58 / 58.3% |
| P90 | Reference | 13.25 / 100.0% | 43.78 / 100.0% | 9.94 / 100.0% | 20.93 / 91.7% |

## Rifles / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M16A2 | Yes | 25.07 / 100.0% | 172.77 / 75.0% | 30.05 / 87.5% | 33.20 / 54.2% |
| PSG 1 | Yes | 22.31 / 100.0% | 147.60 / 100.0% | 24.04 / 89.6% | 29.91 / 58.3% |
| SAR | Yes | 22.27 / 100.0% | 158.13 / 75.0% | 25.28 / 87.5% | 29.22 / 58.3% |
| XM177E2 | Yes | 19.98 / 100.0% | 124.94 / 100.0% | 21.48 / 91.7% | 26.23 / 58.3% |
| FA MAS | Yes | 20.17 / 100.0% | 102.80 / 100.0% | 18.49 / 100.0% | 30.16 / 62.5% |
| G3A3 | Reference | 22.00 / 100.0% | 156.57 / 81.2% | 24.86 / 87.5% | 29.36 / 58.3% |
| MAG | Reference | 18.11 / 100.0% | 69.70 / 100.0% | 12.92 / 100.0% | 26.02 / 64.6% |

## Grenade launchers / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| M79 4 | Yes | 23.33 / 100.0% | 184.72 / 75.0% | 27.42 / 77.1% | 29.15 / 58.3% |
| M203 5 | Yes | 22.57 / 100.0% | 173.70 / 75.0% | 26.95 / 79.2% | 29.15 / 58.3% |
| M79 5 | Yes | 22.42 / 100.0% | 167.30 / 75.0% | 25.66 / 85.4% | 28.40 / 58.3% |
| M203 6 | Yes | 19.45 / 100.0% | 160.71 / 75.0% | 15.32 / 91.7% | 22.55 / 68.8% |
| M79 6 | Yes | 20.23 / 100.0% | 147.12 / 100.0% | 24.06 / 87.5% | 27.87 / 58.3% |
| M79 3 | Reference | 20.13 / 100.0% | 142.97 / 100.0% | 22.91 / 91.7% | 27.18 / 62.5% |
| M203 4 | Reference | 20.10 / 100.0% | 139.81 / 100.0% | 22.80 / 91.7% | 27.08 / 62.5% |
| HK40 | Reference | 19.29 / 100.0% | 119.98 / 100.0% | 21.50 / 89.6% | 24.66 / 58.3% |

## Rocket launchers / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| AT4 1 | Yes | 14.48 / 100.0% | 97.44 / 100.0% | 22.61 / 93.8% | 21.29 / 60.4% |
| LAW80 | Reference | 14.01 / 100.0% | 80.71 / 100.0% | 20.81 / 97.9% | 20.88 / 60.4% |

## Clubs — damage only / stock: current balance

| Weapon | Chrysler | Disc2 ordinary: s / wins | Disc2 bosses: s / wins | EX50 single: s / wins | EX50 triple: s / wins |
|---|---|---:|---:|---:|---:|
| CLUB 4 | Yes | 11.35 / 100.0% | 87.39 / 100.0% | 18.99 / 91.7% | 21.99 / 66.7% |
| CLUB 5 | Yes | 10.13 / 100.0% | 77.89 / 100.0% | 15.76 / 93.8% | 20.53 / 66.7% |
| CLUB 3 | Reference | 13.95 / 100.0% | 179.28 / 75.0% | 25.25 / 81.2% | 25.29 / 58.3% |

## Candidate experiments against current balance

These changes exist only in simulator configurations. Paired intervals resample encounter-level differences, grouping repeated seeds per encounter. Losses receive the 90/400-second scenario horizon as a penalty; short failed fights are not rewarded. Intervals describe model variation, not real-game confidence. Stock-profile results remain in the full CSV.

| Weapon | Scenario | Candidate | Current → candidate seconds | Current → candidate wins | Penalized delta interval, s |
|---|---|---|---|---|---|
| M16A2 | Disc2 / campaign_boss | attack5 | 117.70 → 112.76 | 100.0% → 100.0% | [-9.08, -0.93] |
| M16A2 | Disc2 / campaign_ordinary | attack5 | 20.45 → 20.39 | 100.0% → 100.0% | [-0.16, 0.00] |
| M1911A3 | Disc2 / campaign_boss | attack5 | 113.27 → 109.40 | 100.0% → 100.0% | [-7.67, -0.20] |
| M1911A3 | Disc2 / campaign_ordinary | attack5 | 16.73 → 16.45 | 100.0% → 100.0% | [-0.55, -0.09] |
| M16A2 | EX50 / ex_solo | attack5 | 21.06 → 20.20 | 100.0% → 100.0% | [-1.88, -0.20] |
| M16A2 | EX50 / ex_triple | attack5 | 30.12 → 30.60 | 60.4% → 60.4% | [-0.29, 0.07] |
| M1911A3 | EX50 / ex_solo | attack5 | 19.69 → 18.74 | 100.0% → 100.0% | [-1.97, -0.26] |
| M1911A3 | EX50 / ex_triple | attack5 | 31.40 → 30.46 | 66.7% → 66.7% | [-2.46, -0.20] |
| M16A2 | Disc2 / campaign_boss | attack10 | 117.70 → 110.56 | 100.0% → 100.0% | [-13.36, -0.93] |
| M16A2 | Disc2 / campaign_ordinary | attack10 | 20.45 → 20.25 | 100.0% → 100.0% | [-0.48, 0.00] |
| M1911A3 | Disc2 / campaign_boss | attack10 | 113.27 → 102.65 | 100.0% → 100.0% | [-21.03, -0.20] |
| M1911A3 | Disc2 / campaign_ordinary | attack10 | 16.73 → 16.21 | 100.0% → 100.0% | [-0.94, -0.20] |
| M16A2 | EX50 / ex_solo | attack10 | 21.06 → 19.83 | 100.0% → 100.0% | [-2.73, -0.32] |
| M16A2 | EX50 / ex_triple | attack10 | 30.12 → 30.54 | 60.4% → 60.4% | [-0.38, 0.04] |
| M1911A3 | EX50 / ex_solo | attack10 | 19.69 → 18.05 | 100.0% → 100.0% | [-2.99, -0.69] |
| M1911A3 | EX50 / ex_triple | attack10 | 31.40 → 30.16 | 66.7% → 66.7% | [-3.03, -0.32] |
| M16A2 | Disc2 / campaign_boss | attack15 | 117.70 → 103.78 | 100.0% → 100.0% | [-28.60, -1.12] |
| M16A2 | Disc2 / campaign_ordinary | attack15 | 20.45 → 20.25 | 100.0% → 100.0% | [-0.48, 0.00] |
| M1911A3 | Disc2 / campaign_boss | attack15 | 113.27 → 99.18 | 100.0% → 100.0% | [-29.32, -0.20] |
| M1911A3 | Disc2 / campaign_ordinary | attack15 | 16.73 → 16.03 | 100.0% → 100.0% | [-1.20, -0.29] |
| M16A2 | EX50 / ex_solo | attack15 | 21.06 → 18.72 | 100.0% → 100.0% | [-4.56, -0.80] |
| M16A2 | EX50 / ex_triple | attack15 | 30.12 → 30.35 | 60.4% → 62.5% | [-2.27, 0.06] |
| M1911A3 | EX50 / ex_solo | attack15 | 19.69 → 17.32 | 100.0% → 100.0% | [-4.51, -0.97] |
| M1911A3 | EX50 / ex_triple | attack15 | 31.40 → 29.61 | 66.7% → 66.7% | [-4.08, -0.46] |
| M16A2 | Disc2 / campaign_boss | attack20 | 117.70 → 101.18 | 100.0% → 100.0% | [-34.15, -1.12] |
| M16A2 | Disc2 / campaign_ordinary | attack20 | 20.45 → 20.25 | 100.0% → 100.0% | [-0.48, 0.00] |
| M1911A3 | Disc2 / campaign_boss | attack20 | 113.27 → 95.46 | 100.0% → 100.0% | [-36.54, -0.84] |
| M1911A3 | Disc2 / campaign_ordinary | attack20 | 16.73 → 15.68 | 100.0% → 100.0% | [-2.07, -0.33] |
| M16A2 | EX50 / ex_solo | attack20 | 21.06 → 17.95 | 100.0% → 100.0% | [-5.64, -1.22] |
| M16A2 | EX50 / ex_triple | attack20 | 30.12 → 30.02 | 60.4% → 62.5% | [-2.94, -0.09] |
| M1911A3 | EX50 / ex_solo | attack20 | 19.69 → 16.70 | 100.0% → 100.0% | [-5.51, -1.26] |
| M1911A3 | EX50 / ex_triple | attack20 | 31.40 → 29.47 | 66.7% → 66.7% | [-4.38, -0.37] |
| M16A2 | Disc2 / campaign_boss | mag2 | 117.70 → 115.82 | 100.0% → 100.0% | [-3.76, 0.00] |
| M16A2 | Disc2 / campaign_ordinary | mag2 | 20.45 → 20.45 | 100.0% → 100.0% | [0.00, 0.00] |
| M1911A3 | Disc2 / campaign_boss | mag2 | 113.27 → 113.20 | 100.0% → 100.0% | [-2.93, 2.65] |
| M1911A3 | Disc2 / campaign_ordinary | mag2 | 16.73 → 16.61 | 100.0% → 100.0% | [-0.30, 0.00] |
| M16A2 | EX50 / ex_solo | mag2 | 21.06 → 20.91 | 100.0% → 100.0% | [-0.44, 0.00] |
| M16A2 | EX50 / ex_triple | mag2 | 30.12 → 30.08 | 60.4% → 60.4% | [-0.11, 0.00] |
| M1911A3 | EX50 / ex_solo | mag2 | 19.69 → 19.36 | 100.0% → 100.0% | [-0.60, -0.09] |
| M1911A3 | EX50 / ex_triple | mag2 | 31.40 → 30.18 | 66.7% → 66.7% | [-2.47, -0.24] |
| M203 5 | Disc2 / campaign_boss | attack5 | 113.36 → 108.01 | 100.0% → 100.0% | [-11.45, 0.00] |
| M203 5 | Disc2 / campaign_ordinary | attack5 | 19.27 → 18.73 | 100.0% → 100.0% | [-1.37, 0.00] |
| M79 4 | Disc2 / campaign_boss | attack5 | 122.87 → 115.24 | 100.0% → 100.0% | [-16.50, -1.57] |
| M79 4 | Disc2 / campaign_ordinary | attack5 | 19.94 → 19.27 | 100.0% → 100.0% | [-2.01, 0.00] |
| M79 5 | Disc2 / campaign_boss | attack5 | 107.93 → 102.09 | 100.0% → 100.0% | [-12.10, 0.00] |
| M79 5 | Disc2 / campaign_ordinary | attack5 | 18.72 → 18.72 | 100.0% → 100.0% | [0.00, 0.00] |
| M203 5 | EX50 / ex_solo | attack5 | 21.23 → 20.34 | 91.7% → 91.7% | [-1.88, -0.11] |
| M203 5 | EX50 / ex_triple | attack5 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 4 | EX50 / ex_solo | attack5 | 21.60 → 21.49 | 89.6% → 89.6% | [-0.33, 0.00] |
| M79 4 | EX50 / ex_triple | attack5 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 5 | EX50 / ex_solo | attack5 | 20.00 → 19.68 | 91.7% → 93.8% | [-1.78, 0.00] |
| M79 5 | EX50 / ex_triple | attack5 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M203 5 | Disc2 / campaign_boss | attack10 | 113.36 → 103.71 | 100.0% → 100.0% | [-19.29, 0.00] |
| M203 5 | Disc2 / campaign_ordinary | attack10 | 19.27 → 18.73 | 100.0% → 100.0% | [-1.37, 0.00] |
| M79 4 | Disc2 / campaign_boss | attack10 | 122.87 → 108.78 | 100.0% → 100.0% | [-29.17, -1.57] |
| M79 4 | Disc2 / campaign_ordinary | attack10 | 19.94 → 19.27 | 100.0% → 100.0% | [-2.01, 0.00] |
| M79 5 | Disc2 / campaign_boss | attack10 | 107.93 → 99.23 | 100.0% → 100.0% | [-17.39, 0.00] |
| M79 5 | Disc2 / campaign_ordinary | attack10 | 18.72 → 18.72 | 100.0% → 100.0% | [0.00, 0.00] |
| M203 5 | EX50 / ex_solo | attack10 | 21.23 → 19.71 | 91.7% → 93.8% | [-5.08, -0.55] |
| M203 5 | EX50 / ex_triple | attack10 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 4 | EX50 / ex_solo | attack10 | 21.60 → 20.45 | 89.6% → 91.7% | [-2.34, -0.29] |
| M79 4 | EX50 / ex_triple | attack10 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 5 | EX50 / ex_solo | attack10 | 20.00 → 19.10 | 91.7% → 95.8% | [-5.35, -0.11] |
| M79 5 | EX50 / ex_triple | attack10 | 24.42 → 23.90 | 58.3% → 58.3% | [-1.56, 0.00] |
| M203 5 | Disc2 / campaign_boss | attack15 | 113.36 → 100.24 | 100.0% → 100.0% | [-28.23, 0.00] |
| M203 5 | Disc2 / campaign_ordinary | attack15 | 19.27 → 18.73 | 100.0% → 100.0% | [-1.37, 0.00] |
| M79 4 | Disc2 / campaign_boss | attack15 | 122.87 → 104.86 | 100.0% → 100.0% | [-35.52, -1.57] |
| M79 4 | Disc2 / campaign_ordinary | attack15 | 19.94 → 18.73 | 100.0% → 100.0% | [-2.69, 0.00] |
| M79 5 | Disc2 / campaign_boss | attack15 | 107.93 → 95.00 | 100.0% → 100.0% | [-28.77, 0.00] |
| M79 5 | Disc2 / campaign_ordinary | attack15 | 18.72 → 18.72 | 100.0% → 100.0% | [0.00, 0.00] |
| M203 5 | EX50 / ex_solo | attack15 | 21.23 → 19.34 | 91.7% → 95.8% | [-6.99, -0.77] |
| M203 5 | EX50 / ex_triple | attack15 | 24.42 → 23.90 | 58.3% → 58.3% | [-1.57, 0.00] |
| M79 4 | EX50 / ex_solo | attack15 | 21.60 → 20.05 | 89.6% → 93.8% | [-5.47, -0.55] |
| M79 4 | EX50 / ex_triple | attack15 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 5 | EX50 / ex_solo | attack15 | 20.00 → 18.68 | 91.7% → 97.9% | [-8.04, -0.11] |
| M79 5 | EX50 / ex_triple | attack15 | 24.42 → 23.90 | 58.3% → 58.3% | [-1.56, 0.00] |
| M203 5 | Disc2 / campaign_boss | attack20 | 113.36 → 98.68 | 100.0% → 100.0% | [-29.46, 0.00] |
| M203 5 | Disc2 / campaign_ordinary | attack20 | 19.27 → 18.73 | 100.0% → 100.0% | [-1.37, 0.00] |
| M79 4 | Disc2 / campaign_boss | attack20 | 122.87 → 101.88 | 100.0% → 100.0% | [-42.17, -1.57] |
| M79 4 | Disc2 / campaign_ordinary | attack20 | 19.94 → 18.73 | 100.0% → 100.0% | [-2.69, 0.00] |
| M79 5 | Disc2 / campaign_boss | attack20 | 107.93 → 93.03 | 100.0% → 100.0% | [-31.25, 0.00] |
| M79 5 | Disc2 / campaign_ordinary | attack20 | 18.72 → 18.45 | 100.0% → 100.0% | [-0.82, 0.00] |
| M203 5 | EX50 / ex_solo | attack20 | 21.23 → 18.70 | 91.7% → 97.9% | [-10.08, -1.00] |
| M203 5 | EX50 / ex_triple | attack20 | 24.42 → 23.90 | 58.3% → 58.3% | [-1.57, 0.00] |
| M79 4 | EX50 / ex_solo | attack20 | 21.60 → 19.57 | 89.6% → 95.8% | [-7.49, -0.88] |
| M79 4 | EX50 / ex_triple | attack20 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 5 | EX50 / ex_solo | attack20 | 20.00 → 17.79 | 91.7% → 100.0% | [-12.37, -0.55] |
| M79 5 | EX50 / ex_triple | attack20 | 24.42 → 24.27 | 58.3% → 60.4% | [-3.10, 0.00] |
| M203 5 | Disc2 / campaign_boss | mag2 | 113.36 → 113.36 | 100.0% → 100.0% | [0.00, 0.00] |
| M203 5 | Disc2 / campaign_ordinary | mag2 | 19.27 → 19.27 | 100.0% → 100.0% | [0.00, 0.00] |
| M79 4 | Disc2 / campaign_boss | mag2 | 122.87 → 122.87 | 100.0% → 100.0% | [0.00, 0.00] |
| M79 4 | Disc2 / campaign_ordinary | mag2 | 19.94 → 19.94 | 100.0% → 100.0% | [0.00, 0.00] |
| M79 5 | Disc2 / campaign_boss | mag2 | 107.93 → 107.93 | 100.0% → 100.0% | [0.00, 0.00] |
| M79 5 | Disc2 / campaign_ordinary | mag2 | 18.72 → 18.72 | 100.0% → 100.0% | [0.00, 0.00] |
| M203 5 | EX50 / ex_solo | mag2 | 21.23 → 21.23 | 91.7% → 91.7% | [0.00, 0.00] |
| M203 5 | EX50 / ex_triple | mag2 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 4 | EX50 / ex_solo | mag2 | 21.60 → 21.60 | 89.6% → 89.6% | [0.00, 0.00] |
| M79 4 | EX50 / ex_triple | mag2 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |
| M79 5 | EX50 / ex_solo | mag2 | 20.00 → 20.00 | 91.7% → 91.7% | [0.00, 0.00] |
| M79 5 | EX50 / ex_triple | mag2 | 24.42 → 24.42 | 58.3% → 58.3% | [0.00, 0.00] |

## Limits

- All weapons keep built-in effects; no Catalog installs or installed-RoF acceleration.
- Stock means no player investment; attack_only adds typical late attack/range (+50/+18), no magazine bonus. Profiles retain intrinsic bonuses.
- EX33/EX50 use twelve extracted regular Chrysler enemy stat blocks, solo and synthetic triples, fixed level 33/50 with logged endgame armor, no PE/items.
- Campaign battles retain logged Aya/armor/PE/bag. EX stress cases are not actual tower encounters, pickup-floor progression, or a full EX playthrough.
- No scripted Chrysler boss or True Eve validation. Enemy behavior, geometry, fallback attacks, and shot scheduling remain modeled.
- Clubs include melee damage, Counter and Quickdraw; Steal/loot utility is not modeled, and gun-style clear times alone cannot value them.
- Rocket tests start with 999 reserve rockets; ammo cost/availability and friendly splash are not an economy validation.
- Native damage-floor status gating corrected before this run; damage arithmetic checked against native C. No native RNG replay or exact delayed hit/crowd-cap replication.

## Reproduce

From the bridge root with the configured Python runtime and PYTHONPATH=tools:

```text
python -m unittest pe_weapon_sim.tests.test_chrysler_review pe_weapon_sim.tests.test_native_damage pe_weapon_sim.tests.test_native_c_oracle pe_weapon_sim.tests.test_source_combat
python -m pe_weapon_sim.run_chrysler_review
python -m pe_weapon_sim.run_chrysler_review --only M1911A3 M16A2 --no-anchors --profiles stock attack_only --variants current attack5 attack10 attack15 attack20 mag2 --workers 2 --tag native-chrysler-candidates-a-2026-10-26
python -m pe_weapon_sim.run_chrysler_review --only "M203 5" "M79 4" "M79 5" --no-anchors --profiles attack_only --variants current attack5 attack10 attack15 attack20 mag2 --workers 2 --tag native-chrysler-candidates-b-2026-10-26
python -m pe_weapon_sim.run_chrysler_review --only "M203 5" "M79 4" "M79 5" --no-anchors --stages Disc2 EX50 --profiles stock --variants current attack10 attack15 attack20 --workers 4 --tag native-chrysler-candidates-stock-2026-10-26
python -m pe_weapon_sim.report_chrysler_review --candidate native-chrysler-candidates-a-2026-10-26 native-chrysler-candidates-b-2026-10-26 native-chrysler-candidates-stock-2026-10-26
```
