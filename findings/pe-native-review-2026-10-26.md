# Native weapon balance review — 2026-10-26

Simulation only. No native game source, balance settings, or binaries changed.

8,952 simulated fights; 2 seeds; native-default attack bonuses and combat rules mapped into the calibrated source model.
Screen: up to 8 ordinary encounters and four bosses per stage, sampled separately with a fixed seed. Built-in-only has zero optional installs, including Disc2. Catalog selects the best native loadout from the tested feasible orders, prioritizing wins and then ordinary time; candidate comparisons keep that same loadout.
Stage availability follows the historical ladder: D5 includes museum-era guns and Wayne rewards. It is not exact pickup chronology.
Boss and ordinary results stay separate; these are not campaign-weighted totals. Candidate intervals resample encounter-level paired differences and describe model variation, not confidence in real gameplay.

## Revisited proposals

candidate_half / candidate_full: M203-3 +10 / +20, M79-2 +10 / +20, M79-3 +5 / +10, PPK +5 / +10 attack. Extended runs also test M79-3 +15 and +20. M10B: +1 or +50% magazine. Existing six native bonuses remain enabled in every case.

| Stage | Gun | Setup | Candidate | Fights | Ordinary seconds | Change | Paired delta interval, s | Win rate |
|---|---|---|---|---:|---|---:|---|---|
| D5 | PPK | builtin / typical | candidate_full | 16 | 29.39 → 24.99 | -15.0% | [-7.6, -1.77] | 1.00 → 1.00 |
| D5 | PPK | builtin / typical | candidate_half | 16 | 29.39 → 24.99 | -15.0% | [-7.6, -1.77] | 1.00 → 1.00 |
| D5 | PPK | catalog / typical | candidate_full | 16 | 28.05 → 26.41 | -5.8% | [-3.18, -0.49] | 1.00 → 1.00 |
| D5 | PPK | catalog / typical | candidate_half | 16 | 28.05 → 26.46 | -5.7% | [-3.06, -0.47] | 1.00 → 1.00 |
| D5 | M10B | builtin / typical | magazine_plus1 | 16 | 22.79 → 22.79 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / typical | magazine_plus50pct | 16 | 22.79 → 22.79 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / typical | magazine_plus1 | 16 | 21.27 → 21.27 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / typical | magazine_plus50pct | 16 | 21.27 → 21.27 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / typical | candidate_full | 16 | 39.50 → 32.71 | -17.2% | [-10.83, -3.78] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / typical | candidate_half | 16 | 39.50 → 36.84 | -6.7% | [-4.25, -1.13] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / typical | candidate_full | 16 | 17.60 → 16.42 | -6.7% | [-2.9, -0.2] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / typical | candidate_half | 16 | 17.60 → 16.75 | -4.9% | [-2.01, -0.1] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / typical | candidate_full | 16 | 41.20 → 33.10 | -19.7% | [-12.0, -4.75] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / typical | candidate_half | 16 | 41.20 → 37.39 | -9.3% | [-6.83, -1.0] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / typical | candidate_full | 16 | 18.91 → 17.02 | -10.0% | [-3.89, -0.6] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / typical | candidate_half | 16 | 18.91 → 17.92 | -5.2% | [-1.93, -0.27] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | candidate_full | 16 | 39.50 → 38.92 | -1.5% | [-1.6, 0.0] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | candidate_half | 16 | 39.50 → 38.92 | -1.5% | [-1.6, 0.0] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | candidate_full | 16 | 24.98 → 24.82 | -0.6% | [-0.37, 0.08] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | candidate_half | 16 | 24.98 → 24.95 | -0.1% | [-0.08, 0.0] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / typical | candidate_full | 16 | 13.26 → 12.75 | -3.8% | [-1.26, -0.05] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / typical | candidate_half | 16 | 13.26 → 13.23 | -0.2% | [-0.2, 0.11] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / typical | candidate_full | 16 | 11.54 → 10.54 | -8.6% | [-2.3, -0.23] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / typical | candidate_half | 16 | 11.54 → 11.41 | -1.1% | [-0.33, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / typical | magazine_plus1 | 16 | 15.33 → 15.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / typical | magazine_plus50pct | 16 | 15.33 → 15.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / typical | magazine_plus1 | 16 | 6.87 → 6.87 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / typical | magazine_plus50pct | 16 | 6.87 → 6.87 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / typical | candidate_full | 16 | 21.82 → 20.81 | -4.6% | [-2.19, -0.13] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / typical | candidate_half | 16 | 21.82 → 21.15 | -3.1% | [-1.55, -0.06] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / typical | candidate_full | 16 | 9.63 → 9.65 | +0.2% | [-0.04, 0.11] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / typical | candidate_half | 16 | 9.63 → 9.61 | -0.2% | [-0.05, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / typical | candidate_full | 16 | 22.11 → 20.94 | -5.3% | [-2.25, -0.3] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / typical | candidate_half | 16 | 22.11 → 21.28 | -3.7% | [-1.71, -0.13] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / typical | candidate_full | 16 | 9.67 → 9.62 | -0.5% | [-0.1, -0.01] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / typical | candidate_half | 16 | 9.67 → 9.67 | +0.0% | [-0.07, 0.1] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | candidate_full | 16 | 17.48 → 17.48 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | candidate_half | 16 | 17.48 → 17.48 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | candidate_full | 16 | 9.56 → 9.56 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | candidate_half | 16 | 9.56 → 9.56 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |

## D2-4 / builtin / typical — median 29.88s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| MINI UZ | 3 | — | 18.16 | 0.61 | 27.10 | 1.00 |
| M10 | 3 | — | 19.96 | 0.67 | 29.55 | 1.00 |
| MICRO UZ | 3 | — | 20.92 | 0.70 | 28.63 | 1.00 |
| G23 | 1 | — | 23.23 | 0.78 | 31.82 | 1.00 |
| M11 | 3 | — | 25.02 | 0.84 | 28.76 | 1.00 |
| MP5K | 3 | — | 25.14 | 0.84 | 33.88 | 1.00 |
| M9 2 | 1 | — | 27.17 | 0.91 | 38.00 | 1.00 |
| G3A3 | 4 | — | 29.05 | 0.97 | 34.24 | 1.00 |
| G19 | 1 | — | 29.50 | 0.99 | 41.65 | 1.00 |
| M203 | 5 | — | 30.26 | 1.01 | 48.61 | 1.00 |
| M16A1 | 4 | — | 30.39 | 1.02 | 39.36 | 1.00 |
| SG550 | 4 | — | 30.50 | 1.02 | 41.38 | 1.00 |
| M92F | 1 | — | 30.94 | 1.04 | 42.75 | 1.00 |
| M79 | 5 | — | 32.87 | 1.10 | 47.63 | 1.00 |
| P220 | 1 | — | 39.58 | 1.32 | 56.52 | 1.00 |
| M9 | 1 | — | 40.17 | 1.34 | 49.23 | 1.00 |
| M1911A1 | 1 | — | 40.67 | 1.36 | 49.49 | 1.00 |
| P8 | 1 | — | 44.64 | 1.49 | 56.15 | 1.00 |

## D2-4 / catalog / typical — median 20.95s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| G19 | 1 | Heat, Random, RoF5 | 16.56 | 0.79 | 16.94 | 1.00 |
| M92F | 1 | Heat, Random, RoF5 | 16.70 | 0.80 | 18.49 | 1.00 |
| MINI UZ | 3 | Heat | 17.44 | 0.83 | 22.49 | 1.00 |
| G3A3 | 4 | Heat, Random, RoF5 | 17.59 | 0.84 | 17.49 | 1.00 |
| M9 | 1 | Heat, Random, RoF5 | 17.90 | 0.85 | 19.58 | 1.00 |
| M10 | 3 | — | 19.96 | 0.95 | 29.55 | 1.00 |
| MP5K | 3 | Heat, RoF5 | 20.31 | 0.97 | 17.52 | 1.00 |
| MICRO UZ | 3 | — | 20.92 | 1.00 | 28.63 | 1.00 |
| M9 2 | 1 | Heat, RoF5 | 20.93 | 1.00 | 17.13 | 1.00 |
| G23 | 1 | Heat, RoF5 | 20.97 | 1.00 | 17.24 | 1.00 |
| P220 | 1 | Heat, RoF5 | 22.19 | 1.06 | 27.55 | 1.00 |
| P8 | 1 | RoF5, Heat | 22.23 | 1.06 | 25.68 | 1.00 |
| M1911A1 | 1 | Heat, RoF5 | 22.24 | 1.06 | 25.65 | 1.00 |
| M203 | 5 | RoF5 | 24.80 | 1.18 | 22.20 | 1.00 |
| M11 | 3 | — | 25.02 | 1.19 | 28.76 | 1.00 |
| M79 | 5 | Heat, RoF5 | 25.17 | 1.20 | 21.65 | 1.00 |
| M16A1 | 4 | Heat, RoF5 | 27.12 | 1.29 | 23.59 | 1.00 |
| SG550 | 4 | Heat, RoF5 | 27.25 | 1.30 | 23.69 | 1.00 |

## D5 / builtin / typical — median 30.64s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| P90 | 3 | — | 19.36 | 0.63 | 18.48 | 1.00 |
| DE50AE7 | 1 | — | 20.77 | 0.68 | 38.66 | 1.00 |
| M8000 | 1 | — | 20.99 | 0.69 | 40.48 | 1.00 |
| USP TU | 1 | — | 22.64 | 0.74 | 36.83 | 1.00 |
| M10B | 2 | — | 22.79 | 0.74 | 44.68 | 1.00 |
| M9 3 | 1 | — | 23.90 | 0.78 | 40.85 | 1.00 |
| HK40 | 5 | — | 25.75 | 0.84 | 52.50 | 1.00 |
| MP5PDW | 3 | — | 27.21 | 0.89 | 36.99 | 1.00 |
| MAG | 4 | — | 27.28 | 0.89 | 50.82 | 1.00 |
| M500 | 2 | — | 27.41 | 0.89 | 54.27 | 1.00 |
| G22 | 1 | — | 27.62 | 0.90 | 48.90 | 1.00 |
| G3A3 | 4 | — | 28.04 | 0.92 | 63.20 | 1.00 |
| M1911A2 | 1 | — | 28.69 | 0.94 | 49.04 | 1.00 |
| G23 | 1 | — | 28.70 | 0.94 | 49.05 | 1.00 |
| P220 2 | 1 | — | 28.72 | 0.94 | 49.42 | 1.00 |
| MINI UZ | 3 | — | 29.15 | 0.95 | 44.34 | 1.00 |
| PPK | 1 | — | 29.39 | 0.96 | 48.81 | 1.00 |
| MP5K | 3 | — | 30.08 | 0.98 | 50.22 | 1.00 |
| M203 4 | 5 | — | 30.21 | 0.99 | 57.10 | 1.00 |
| M10 | 3 | — | 31.07 | 1.01 | 43.39 | 1.00 |
| MICRO UZ | 3 | — | 31.90 | 1.04 | 50.81 | 1.00 |
| AT4 | 6 | — | 33.12 | 1.08 | 55.86 | 1.00 |
| M9 2 | 1 | — | 34.43 | 1.12 | 53.32 | 1.00 |
| M203 | 5 | — | 35.35 | 1.15 | 66.90 | 1.00 |
| M16A1 | 4 | — | 35.81 | 1.17 | 63.52 | 1.00 |
| SG550 | 4 | — | 35.82 | 1.17 | 63.62 | 1.00 |
| M203 2 | 5 | — | 36.21 | 1.18 | 60.10 | 1.00 |
| M11 | 3 | — | 37.55 | 1.23 | 56.05 | 1.00 |
| M203 3 | 5 | — | 39.50 | 1.29 | 62.07 | 1.00 |
| M79 3 | 5 | — | 39.50 | 1.29 | 62.58 | 1.00 |
| G19 | 1 | — | 40.86 | 1.33 | 59.09 | 1.00 |
| M79 2 | 5 | — | 41.20 | 1.34 | 62.43 | 1.00 |
| M92F | 1 | — | 41.37 | 1.35 | 60.59 | 1.00 |
| M79 | 5 | — | 44.88 | 1.46 | 67.80 | 1.00 |
| P220 | 1 | — | 47.68 | 1.56 | 69.57 | 1.00 |
| M1911A1 | 1 | — | 50.20 | 1.64 | 67.30 | 1.00 |
| M9 | 1 | — | 50.78 | 1.66 | 68.20 | 1.00 |
| P8 | 1 | — | 51.67 | 1.69 | 84.18 | 1.00 |

## D5 / catalog / typical — median 20.30s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| DE50AE7 | 1 | Heat, Random, RoF5 | 11.85 | 0.58 | 22.64 | 1.00 |
| HK40 | 5 | Heat, Random, RoF5 | 12.84 | 0.63 | 28.61 | 1.00 |
| MAG | 4 | Heat, Random, RoF5 | 13.56 | 0.67 | 26.52 | 1.00 |
| M203 4 | 5 | Heat, Random, RoF5 | 15.06 | 0.74 | 30.23 | 1.00 |
| M1911A2 | 1 | Heat, Random, RoF5 | 15.15 | 0.75 | 33.82 | 1.00 |
| G23 | 1 | Heat, Random, RoF5 | 15.15 | 0.75 | 33.83 | 1.00 |
| G22 | 1 | Heat, Random, RoF5 | 15.15 | 0.75 | 33.39 | 1.00 |
| P220 2 | 1 | Heat, Random, RoF5 | 15.75 | 0.78 | 33.79 | 1.00 |
| G3A3 | 4 | Heat, Random, RoF5 | 17.43 | 0.86 | 32.80 | 1.00 |
| M203 3 | 5 | Heat, Random, RoF5 | 17.60 | 0.87 | 34.07 | 1.00 |
| M203 2 | 5 | Random, RoF5 | 17.64 | 0.87 | 37.00 | 1.00 |
| M9 2 | 1 | Heat, Random, RoF5 | 17.90 | 0.88 | 35.77 | 1.00 |
| P90 | 3 | Heat | 18.91 | 0.93 | 18.20 | 1.00 |
| M79 2 | 5 | Heat, Random, RoF5 | 18.91 | 0.93 | 34.12 | 1.00 |
| M8000 | 1 | Heat, Random | 19.16 | 0.94 | 33.56 | 1.00 |
| MP5K | 3 | Heat, Random, RoF5 | 19.31 | 0.95 | 35.36 | 1.00 |
| G19 | 1 | Heat, Random, RoF5 | 19.52 | 0.96 | 35.04 | 1.00 |
| M203 | 5 | Random, RoF5 | 19.63 | 0.97 | 39.58 | 1.00 |
| M16A1 | 4 | Heat, Random, RoF5 | 20.06 | 0.99 | 34.90 | 1.00 |
| M92F | 1 | Heat, Random, RoF5 | 20.53 | 1.01 | 36.07 | 1.00 |
| M9 3 | 1 | Heat, RoF5 | 20.86 | 1.03 | 36.09 | 1.00 |
| SG550 | 4 | Heat, Random, RoF5 | 20.87 | 1.03 | 35.16 | 1.00 |
| P8 | 1 | Heat, Random, RoF5 | 21.20 | 1.04 | 39.90 | 1.00 |
| M10B | 2 | Heat, RoF5 | 21.27 | 1.05 | 38.82 | 1.00 |
| M1911A1 | 1 | Heat, Random, RoF5 | 21.55 | 1.06 | 37.87 | 1.00 |
| M9 | 1 | Heat, Random, RoF5 | 21.62 | 1.07 | 39.83 | 1.00 |
| P220 | 1 | Heat, Random, RoF5 | 21.74 | 1.07 | 39.48 | 1.00 |
| M500 | 2 | Heat, RoF5 | 21.89 | 1.08 | 44.82 | 1.00 |
| USP TU | 1 | Heat | 22.05 | 1.09 | 35.55 | 1.00 |
| MP5PDW | 3 | Heat | 23.79 | 1.17 | 32.07 | 1.00 |
| M79 3 | 5 | Heat, RoF5 | 24.98 | 1.23 | 48.62 | 1.00 |
| M79 | 5 | Heat, RoF5 | 25.32 | 1.25 | 47.52 | 1.00 |
| M10 | 3 | Heat | 25.85 | 1.27 | 36.67 | 1.00 |
| MINI UZ | 3 | Heat | 25.87 | 1.27 | 41.05 | 1.00 |
| PPK | 1 | Heat | 28.05 | 1.38 | 41.54 | 1.00 |
| MICRO UZ | 3 | — | 31.90 | 1.57 | 50.81 | 1.00 |
| AT4 | 6 | — | 33.12 | 1.63 | 55.86 | 1.00 |
| M11 | 3 | — | 37.55 | 1.85 | 56.05 | 1.00 |

## Disc2 / builtin / typical — median 16.70s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| MP5PDW | 3 | — | 9.61 | 0.58 | 40.98 | 1.00 |
| M10 | 3 | — | 10.29 | 0.62 | 46.09 | 1.00 |
| MINI UZ | 3 | — | 10.94 | 0.66 | 41.67 | 1.00 |
| M11 | 3 | — | 11.00 | 0.66 | 49.62 | 1.00 |
| MICRO UZ | 3 | — | 11.17 | 0.67 | 46.47 | 1.00 |
| P90 | 3 | — | 11.66 | 0.70 | 21.46 | 1.00 |
| M8000 | 1 | — | 12.72 | 0.76 | 35.10 | 1.00 |
| DE50AE7 | 1 | — | 12.73 | 0.76 | 34.42 | 1.00 |
| PPK | 1 | — | 13.26 | 0.79 | 67.68 | 1.00 |
| M9 3 | 1 | — | 13.30 | 0.80 | 36.62 | 1.00 |
| USP TU | 1 | — | 13.59 | 0.81 | 41.70 | 1.00 |
| MP5K | 3 | — | 15.09 | 0.90 | 55.31 | 1.00 |
| M10B | 2 | — | 15.33 | 0.92 | 52.09 | 1.00 |
| AT4 | 6 | — | 15.68 | 0.94 | 102.63 | 1.00 |
| MAG | 4 | — | 15.93 | 0.95 | 35.89 | 1.00 |
| M1911A2 | 1 | — | 16.09 | 0.96 | 65.98 | 1.00 |
| G23 | 1 | — | 16.09 | 0.96 | 64.47 | 1.00 |
| P220 2 | 1 | — | 16.11 | 0.96 | 64.90 | 1.00 |
| G22 | 1 | — | 16.28 | 0.97 | 56.93 | 1.00 |
| M203 4 | 5 | — | 17.12 | 1.03 | 56.92 | 1.00 |
| M500 | 2 | — | 17.34 | 1.04 | 72.83 | 1.00 |
| M9 2 | 1 | — | 17.47 | 1.05 | 67.82 | 1.00 |
| M79 3 | 5 | — | 17.48 | 1.05 | 64.35 | 1.00 |
| G19 | 1 | — | 17.94 | 1.07 | 71.19 | 1.00 |
| M92F | 1 | — | 18.03 | 1.08 | 77.63 | 1.00 |
| P220 | 1 | — | 18.69 | 1.12 | 83.89 | 1.00 |
| M1911A1 | 1 | — | 19.20 | 1.15 | 89.27 | 1.00 |
| M9 | 1 | — | 19.24 | 1.15 | 88.47 | 1.00 |
| P8 | 1 | — | 19.34 | 1.16 | 95.38 | 1.00 |
| HK40 | 5 | — | 19.64 | 1.18 | 56.49 | 1.00 |
| G3A3 | 4 | — | 19.77 | 1.18 | 66.33 | 1.00 |
| M16A1 | 4 | — | 20.12 | 1.20 | 67.45 | 1.00 |
| SG550 | 4 | — | 20.64 | 1.24 | 70.50 | 1.00 |
| M203 2 | 5 | — | 21.37 | 1.28 | 61.57 | 1.00 |
| M203 3 | 5 | — | 21.82 | 1.31 | 80.78 | 1.00 |
| M79 | 5 | — | 21.94 | 1.31 | 83.98 | 1.00 |
| M79 2 | 5 | — | 22.11 | 1.32 | 83.93 | 1.00 |
| M203 | 5 | — | 24.49 | 1.47 | 76.49 | 1.00 |

## Disc2 / catalog / typical — median 8.62s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| DE50AE7 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 3.34 | 0.39 | 8.35 | 1.00 |
| M9 3 | 1 | Quickdraw, RoF5, Acid, Heat, Random | 3.90 | 0.45 | 11.29 | 1.00 |
| G23 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 4.04 | 0.47 | 11.90 | 1.00 |
| HK40 | 5 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 4.11 | 0.48 | 12.15 | 1.00 |
| M9 2 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 4.23 | 0.49 | 12.06 | 1.00 |
| M92F | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 4.39 | 0.51 | 14.21 | 1.00 |
| M9 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 5.19 | 0.60 | 15.45 | 1.00 |
| M1911A1 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 5.20 | 0.60 | 16.42 | 1.00 |
| P8 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat, Random | 5.20 | 0.60 | 16.19 | 1.00 |
| MP5PDW | 3 | 2Cmd, Heat, Quickdraw, Acid | 5.21 | 0.60 | 16.72 | 1.00 |
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 6.87 | 0.80 | 12.38 | 1.00 |
| M500 | 2 | 2Cmd, Quickdraw, RoF5, Acid | 6.97 | 0.81 | 19.90 | 1.00 |
| MP5K | 3 | RoF5, 2Cmd, Heat, Quickdraw | 7.56 | 0.88 | 13.40 | 1.00 |
| MINI UZ | 3 | 2Cmd | 8.33 | 0.97 | 27.78 | 1.00 |
| P220 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.45 | 0.98 | 18.36 | 1.00 |
| M1911A2 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.55 | 0.99 | 11.77 | 1.00 |
| M8000 | 1 | Quickdraw, RoF5, Acid, Heat | 8.56 | 0.99 | 11.88 | 1.00 |
| G22 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.57 | 0.99 | 12.18 | 1.00 |
| P220 2 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.58 | 1.00 | 11.78 | 1.00 |
| G19 | 1 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.66 | 1.00 | 14.96 | 1.00 |
| M203 4 | 5 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 9.45 | 1.10 | 16.62 | 1.00 |
| M10 | 3 | 2Cmd | 9.55 | 1.11 | 27.30 | 1.00 |
| M79 3 | 5 | 2Cmd, Quickdraw, RoF5 | 9.56 | 1.11 | 19.25 | 1.00 |
| M203 2 | 5 | 2Cmd, Quickdraw, RoF5, Acid | 9.61 | 1.11 | 17.82 | 1.00 |
| M203 3 | 5 | 2Cmd, Quickdraw, RoF5, Heat | 9.63 | 1.12 | 18.29 | 1.00 |
| M79 | 5 | 2Cmd, Quickdraw, RoF5 | 9.64 | 1.12 | 20.97 | 1.00 |
| M79 2 | 5 | 2Cmd, Quickdraw, RoF5 | 9.67 | 1.12 | 22.10 | 1.00 |
| USP TU | 1 | 2Cmd, Heat, Quickdraw, Acid | 9.69 | 1.12 | 22.07 | 1.00 |
| P90 | 3 | 2Cmd, Heat, Quickdraw, Acid | 10.08 | 1.17 | 11.01 | 1.00 |
| M11 | 3 | — | 11.00 | 1.28 | 49.62 | 1.00 |
| MAG | 4 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 11.14 | 1.29 | 13.28 | 1.00 |
| MICRO UZ | 3 | — | 11.17 | 1.30 | 46.47 | 1.00 |
| G3A3 | 4 | 2Cmd, Quickdraw, RoF5, Acid | 11.31 | 1.31 | 21.22 | 1.00 |
| PPK | 1 | 2Cmd, Acid | 11.54 | 1.34 | 49.18 | 1.00 |
| M16A1 | 4 | 2Cmd, Quickdraw, RoF5 | 11.55 | 1.34 | 24.99 | 1.00 |
| SG550 | 4 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 11.59 | 1.34 | 22.12 | 1.00 |
| M203 | 5 | 2Cmd, Quickdraw | 14.83 | 1.72 | 44.08 | 1.00 |
| AT4 | 6 | — | 15.68 | 1.82 | 102.63 | 1.00 |

## Model limits

- Integer per-hit hook arithmetic mapped from native; crowd cap models restored final HP, not delayed engine updates or the native 40-frame reference heuristic.
- One logged campaign; synthetic loadouts, not a new acquisition/economy simulation.
- Catalog best-of tested orders is an optimistic upper bound, not guaranteed player ownership.
- Built-in-only means no optional installs at ALL stages, including Disc2.
- Infinite reserve per isolated battle; rocket results do not establish campaign ammo viability.
- Per-hit integer arithmetic passed 2,000 randomized comparisons against the native C helper compiled unchanged. This does not validate the entire fight model.
- Critical conversion uses the inherited probability 26.67% rather than native integer 26%; random sequences are not native RNG replays. The five disputed weapons have no built-in Critical.
- At the minimum-damage floor, the model may apply a status that native gun damage skips. Treat near-floor status results as approximate.
- Native crowd-cap binary-search granularity and delayed hit processing are approximated by limiting final HP loss. Shot queues and enemy behavior remain a model, not native-game execution.
