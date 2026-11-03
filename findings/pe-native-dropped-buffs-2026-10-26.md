# Native weapon balance review — 2026-10-26

Simulation only. No native game source, balance settings, or binaries changed.

20,208 simulated fights; 4 seeds; native-default attack bonuses and combat rules mapped into the calibrated source model.
Screen: up to 12 ordinary encounters and four bosses per stage, sampled separately with a fixed seed. Built-in-only has zero optional installs, including Disc2. Catalog selects the best native loadout from the tested feasible orders, prioritizing wins and then ordinary time; candidate comparisons keep that same loadout.
Stage availability follows the historical ladder: D5 includes museum-era guns and Wayne rewards. It is not exact pickup chronology.
Boss and ordinary results stay separate; these are not campaign-weighted totals. Candidate intervals resample encounter-level paired differences and describe model variation, not confidence in real gameplay.

## Revisited proposals

candidate_half / candidate_full: M203-3 +10 / +20, M79-2 +10 / +20, M79-3 +5 / +10, PPK +5 / +10 attack. Extended runs also test M79-3 +15 and +20. M10B: +1 or +50% magazine. Existing six native bonuses remain enabled in every case.

| Stage | Gun | Setup | Candidate | Fights | Ordinary seconds | Change | Paired delta interval, s | Win rate |
|---|---|---|---|---:|---|---:|---|---|
| D5 | PPK | builtin / high | candidate_full | 40 | 25.01 → 21.97 | -12.2% | [-4.52, -1.63] | 1.00 → 1.00 |
| D5 | PPK | builtin / high | candidate_half | 40 | 25.01 → 23.48 | -6.1% | [-2.8, -0.37] | 1.00 → 1.00 |
| D5 | PPK | builtin / low | candidate_full | 40 | 33.89 → 26.61 | -21.5% | [-9.07, -5.4] | 1.00 → 1.00 |
| D5 | PPK | builtin / low | candidate_half | 40 | 33.89 → 29.36 | -13.4% | [-6.24, -2.97] | 1.00 → 1.00 |
| D5 | PPK | builtin / typical | candidate_full | 40 | 28.40 → 25.09 | -11.6% | [-5.03, -1.83] | 1.00 → 1.00 |
| D5 | PPK | builtin / typical | candidate_half | 40 | 28.40 → 25.09 | -11.6% | [-5.03, -1.83] | 1.00 → 1.00 |
| D5 | PPK | catalog / high | candidate_full | 40 | 24.84 → 23.22 | -6.5% | [-2.73, -0.65] | 1.00 → 1.00 |
| D5 | PPK | catalog / high | candidate_half | 40 | 24.84 → 24.33 | -2.0% | [-1.06, -0.14] | 1.00 → 1.00 |
| D5 | PPK | catalog / low | candidate_full | 40 | 27.05 → 25.38 | -6.2% | [-2.5, -1.04] | 1.00 → 1.00 |
| D5 | PPK | catalog / low | candidate_half | 40 | 27.05 → 26.71 | -1.3% | [-0.58, -0.16] | 1.00 → 1.00 |
| D5 | PPK | catalog / typical | candidate_full | 40 | 26.39 → 24.66 | -6.6% | [-2.42, -1.11] | 1.00 → 1.00 |
| D5 | PPK | catalog / typical | candidate_half | 40 | 26.39 → 24.90 | -5.6% | [-2.13, -0.84] | 1.00 → 1.00 |
| D5 | M10B | builtin / high | magazine_plus1 | 40 | 23.81 → 23.81 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / high | magazine_plus50pct | 40 | 23.81 → 23.81 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / low | magazine_plus1 | 40 | 23.42 → 23.42 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / low | magazine_plus50pct | 40 | 23.42 → 23.42 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / typical | magazine_plus1 | 40 | 23.62 → 23.62 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / typical | magazine_plus50pct | 40 | 23.62 → 23.62 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / high | magazine_plus1 | 40 | 21.33 → 21.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / high | magazine_plus50pct | 40 | 21.33 → 21.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / low | magazine_plus1 | 40 | 21.39 → 21.39 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / low | magazine_plus50pct | 40 | 21.39 → 21.39 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / typical | magazine_plus1 | 40 | 21.35 → 21.35 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / typical | magazine_plus50pct | 40 | 21.35 → 21.35 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / high | candidate_full | 40 | 36.02 → 31.53 | -12.5% | [-6.54, -2.61] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / high | candidate_half | 40 | 36.02 → 31.96 | -11.3% | [-6.12, -2.19] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / low | candidate_full | 40 | 40.26 → 32.43 | -19.5% | [-10.58, -5.31] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / low | candidate_half | 40 | 40.26 → 37.36 | -7.2% | [-4.07, -1.76] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / typical | candidate_full | 40 | 38.51 → 31.57 | -18.0% | [-9.98, -4.4] | 1.00 → 1.00 |
| D5 | M203 3 | builtin / typical | candidate_half | 40 | 38.51 → 35.45 | -7.9% | [-4.59, -1.76] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / high | candidate_full | 40 | 18.80 → 17.40 | -7.5% | [-2.63, -0.28] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / high | candidate_half | 40 | 18.80 → 18.30 | -2.7% | [-1.37, 0.43] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / low | candidate_full | 40 | 20.19 → 19.07 | -5.6% | [-2.18, 0.01] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / low | candidate_half | 40 | 20.19 → 19.31 | -4.4% | [-1.66, -0.27] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / typical | candidate_full | 40 | 19.25 → 18.29 | -5.0% | [-2.11, 0.2] | 1.00 → 1.00 |
| D5 | M203 3 | catalog / typical | candidate_half | 40 | 19.25 → 18.54 | -3.7% | [-1.29, -0.17] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / high | candidate_full | 40 | 37.31 → 31.57 | -15.4% | [-8.14, -3.64] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / high | candidate_half | 40 | 37.31 → 32.37 | -13.3% | [-7.18, -2.92] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / low | candidate_full | 40 | 41.30 → 36.06 | -12.7% | [-6.39, -4.23] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / low | candidate_half | 40 | 41.30 → 38.73 | -6.2% | [-3.62, -1.45] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / typical | candidate_full | 40 | 39.65 → 32.16 | -18.9% | [-10.48, -4.8] | 1.00 → 1.00 |
| D5 | M79 2 | builtin / typical | candidate_half | 40 | 39.65 → 36.41 | -8.2% | [-4.99, -1.66] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / high | candidate_full | 40 | 19.17 → 18.11 | -5.5% | [-2.17, -0.1] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / high | candidate_half | 40 | 19.17 → 18.84 | -1.7% | [-1.02, 0.6] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / low | candidate_full | 40 | 20.44 → 18.84 | -7.8% | [-2.66, -0.65] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / low | candidate_half | 40 | 20.44 → 19.54 | -4.4% | [-1.57, -0.32] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / typical | candidate_full | 40 | 19.92 → 18.77 | -5.8% | [-2.37, 0.06] | 1.00 → 1.00 |
| D5 | M79 2 | catalog / typical | candidate_half | 40 | 19.92 → 19.22 | -3.5% | [-1.47, -0.18] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / high | attack_plus15 | 40 | 39.61 → 30.36 | -23.3% | [-12.51, -5.75] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / high | attack_plus20 | 40 | 39.61 → 30.36 | -23.3% | [-12.51, -5.75] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / high | candidate_full | 40 | 39.61 → 30.91 | -22.0% | [-12.26, -5.07] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / high | candidate_half | 40 | 39.61 → 30.91 | -22.0% | [-12.26, -5.07] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / low | attack_plus15 | 40 | 40.27 → 39.84 | -1.1% | [-1.05, -0.04] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / low | attack_plus20 | 40 | 40.27 → 30.97 | -23.1% | [-12.46, -5.99] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / low | candidate_full | 40 | 40.27 → 39.84 | -1.1% | [-1.05, -0.04] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / low | candidate_half | 40 | 40.27 → 40.27 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | attack_plus15 | 40 | 40.17 → 30.93 | -23.0% | [-12.33, -5.97] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | attack_plus20 | 40 | 40.17 → 30.39 | -24.3% | [-12.54, -6.66] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | candidate_full | 40 | 40.17 → 38.63 | -3.8% | [-3.87, -0.02] | 1.00 → 1.00 |
| D5 | M79 3 | builtin / typical | candidate_half | 40 | 40.17 → 39.81 | -0.9% | [-0.92, 0.01] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / high | attack_plus15 | 40 | 24.50 → 24.44 | -0.2% | [-0.12, 0.01] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / high | attack_plus20 | 40 | 24.50 → 24.44 | -0.2% | [-0.12, 0.01] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / high | candidate_full | 40 | 24.50 → 24.44 | -0.2% | [-0.12, 0.01] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / high | candidate_half | 40 | 24.50 → 24.44 | -0.2% | [-0.12, 0.01] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / low | attack_plus15 | 40 | 24.69 → 24.40 | -1.2% | [-0.48, -0.13] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / low | attack_plus20 | 40 | 24.69 → 24.39 | -1.2% | [-0.48, -0.13] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / low | candidate_full | 40 | 24.69 → 24.55 | -0.6% | [-0.32, -0.03] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / low | candidate_half | 40 | 24.69 → 24.69 | -0.0% | [-0.01, 0.0] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | attack_plus15 | 40 | 24.54 → 24.36 | -0.7% | [-0.29, -0.05] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | attack_plus20 | 40 | 24.54 → 24.36 | -0.7% | [-0.29, -0.05] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | candidate_full | 40 | 24.54 → 24.36 | -0.7% | [-0.29, -0.05] | 1.00 → 1.00 |
| D5 | M79 3 | catalog / typical | candidate_half | 40 | 24.54 → 24.52 | -0.1% | [-0.07, 0.0] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / high | candidate_full | 48 | 12.09 → 11.76 | -2.7% | [-0.82, -0.02] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / high | candidate_half | 48 | 12.09 → 11.78 | -2.6% | [-0.8, -0.02] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / low | candidate_full | 48 | 14.19 → 13.71 | -3.4% | [-0.93, -0.13] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / low | candidate_half | 48 | 14.19 → 13.97 | -1.5% | [-0.49, -0.02] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / typical | candidate_full | 48 | 12.80 → 12.23 | -4.5% | [-1.24, -0.18] | 1.00 → 1.00 |
| Disc2 | PPK | builtin / typical | candidate_half | 48 | 12.80 → 12.74 | -0.5% | [-0.18, 0.0] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / high | candidate_full | 48 | 10.87 → 10.97 | +0.9% | [-0.15, 0.47] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / high | candidate_half | 48 | 10.87 → 11.02 | +1.4% | [-0.04, 0.5] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / low | candidate_full | 48 | 12.01 → 11.79 | -1.8% | [-0.54, -0.02] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / low | candidate_half | 48 | 12.01 → 11.82 | -1.6% | [-0.45, -0.02] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / typical | candidate_full | 48 | 11.41 → 10.91 | -4.4% | [-0.95, -0.19] | 1.00 → 1.00 |
| Disc2 | PPK | catalog / typical | candidate_half | 48 | 11.41 → 11.33 | -0.7% | [-0.2, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / high | magazine_plus1 | 48 | 15.48 → 15.48 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / high | magazine_plus50pct | 48 | 15.48 → 15.48 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / low | magazine_plus1 | 48 | 16.22 → 16.22 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / low | magazine_plus50pct | 48 | 16.22 → 16.22 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / typical | magazine_plus1 | 48 | 15.49 → 15.49 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / typical | magazine_plus50pct | 48 | 15.49 → 15.49 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / high | magazine_plus1 | 48 | 8.27 → 8.27 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / high | magazine_plus50pct | 48 | 8.27 → 8.27 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / low | magazine_plus1 | 48 | 8.33 → 8.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / low | magazine_plus50pct | 48 | 8.33 → 8.33 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / typical | magazine_plus1 | 48 | 8.32 → 8.32 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / typical | magazine_plus50pct | 48 | 8.32 → 8.32 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / high | candidate_full | 48 | 19.44 → 18.59 | -4.4% | [-2.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / high | candidate_half | 48 | 19.44 → 18.78 | -3.4% | [-1.54, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / low | candidate_full | 48 | 21.30 → 19.79 | -7.1% | [-2.92, -0.63] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / low | candidate_half | 48 | 21.30 → 20.58 | -3.4% | [-1.12, -0.39] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / typical | candidate_full | 48 | 20.08 → 19.45 | -3.1% | [-1.4, -0.06] | 1.00 → 1.00 |
| Disc2 | M203 3 | builtin / typical | candidate_half | 48 | 20.08 → 19.69 | -1.9% | [-0.9, -0.02] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / high | candidate_full | 48 | 10.55 → 10.55 | +0.1% | [-0.03, 0.05] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / high | candidate_half | 48 | 10.55 → 10.56 | +0.1% | [0.0, 0.04] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / low | candidate_full | 48 | 10.66 → 10.60 | -0.6% | [-0.14, -0.01] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / low | candidate_half | 48 | 10.66 → 10.65 | -0.2% | [-0.04, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / typical | candidate_full | 48 | 10.61 → 10.56 | -0.4% | [-0.11, 0.0] | 1.00 → 1.00 |
| Disc2 | M203 3 | catalog / typical | candidate_half | 48 | 10.61 → 10.59 | -0.2% | [-0.04, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / high | candidate_full | 48 | 19.54 → 18.65 | -4.6% | [-2.04, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / high | candidate_half | 48 | 19.54 → 19.16 | -2.0% | [-1.01, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / low | candidate_full | 48 | 21.66 → 20.23 | -6.6% | [-2.99, -0.49] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / low | candidate_half | 48 | 21.66 → 21.24 | -1.9% | [-1.07, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / typical | candidate_full | 48 | 20.58 → 19.53 | -5.1% | [-2.46, -0.17] | 1.00 → 1.00 |
| Disc2 | M79 2 | builtin / typical | candidate_half | 48 | 20.58 → 19.79 | -3.9% | [-1.84, -0.1] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / high | candidate_full | 48 | 10.57 → 10.49 | -0.7% | [-0.19, -0.01] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / high | candidate_half | 48 | 10.57 → 10.54 | -0.3% | [-0.06, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / low | candidate_full | 48 | 10.70 → 10.59 | -1.1% | [-0.19, -0.03] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / low | candidate_half | 48 | 10.70 → 10.60 | -1.0% | [-0.17, -0.03] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / typical | candidate_full | 48 | 10.58 → 10.55 | -0.3% | [-0.07, -0.01] | 1.00 → 1.00 |
| Disc2 | M79 2 | catalog / typical | candidate_half | 48 | 10.58 → 10.57 | -0.1% | [-0.04, 0.02] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / high | attack_plus15 | 48 | 17.20 → 16.51 | -4.0% | [-1.48, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / high | attack_plus20 | 48 | 17.20 → 16.51 | -4.0% | [-1.48, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / high | candidate_full | 48 | 17.20 → 16.51 | -4.0% | [-1.48, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / high | candidate_half | 48 | 17.20 → 17.04 | -0.9% | [-0.47, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / low | attack_plus15 | 48 | 18.44 → 17.91 | -2.9% | [-1.37, -0.04] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / low | attack_plus20 | 48 | 18.44 → 17.91 | -2.9% | [-1.37, -0.04] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / low | candidate_full | 48 | 18.44 → 17.91 | -2.9% | [-1.37, -0.04] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / low | candidate_half | 48 | 18.44 → 18.40 | -0.2% | [-0.13, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | attack_plus15 | 48 | 17.88 → 17.20 | -3.8% | [-2.05, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | attack_plus20 | 48 | 17.88 → 17.20 | -3.8% | [-2.05, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | candidate_full | 48 | 17.88 → 17.88 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | builtin / typical | candidate_half | 48 | 17.88 → 17.88 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / high | attack_plus15 | 48 | 10.48 → 10.45 | -0.3% | [-0.09, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / high | attack_plus20 | 48 | 10.48 → 10.44 | -0.4% | [-0.1, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / high | candidate_full | 48 | 10.48 → 10.45 | -0.3% | [-0.09, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / high | candidate_half | 48 | 10.48 → 10.48 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / low | attack_plus15 | 48 | 10.53 → 10.52 | -0.2% | [-0.03, -0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / low | attack_plus20 | 48 | 10.53 → 10.52 | -0.2% | [-0.03, -0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / low | candidate_full | 48 | 10.53 → 10.52 | -0.2% | [-0.03, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / low | candidate_half | 48 | 10.53 → 10.52 | -0.1% | [-0.03, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | attack_plus15 | 48 | 10.50 → 10.48 | -0.2% | [-0.04, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | attack_plus20 | 48 | 10.50 → 10.48 | -0.2% | [-0.04, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | candidate_full | 48 | 10.50 → 10.50 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M79 3 | catalog / typical | candidate_half | 48 | 10.50 → 10.50 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |

## D5 / builtin / low — median 40.26s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 23.42 | 0.58 | 41.09 | 1.00 |
| PPK | 1 | — | 33.89 | 0.84 | 49.68 | 1.00 |
| M203 3 | 5 | — | 40.26 | 1.00 | 57.56 | 1.00 |
| M79 3 | 5 | — | 40.27 | 1.00 | 57.75 | 1.00 |
| M79 2 | 5 | — | 41.30 | 1.03 | 58.58 | 1.00 |

## D5 / builtin / typical — median 38.51s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 23.62 | 0.61 | 40.43 | 1.00 |
| PPK | 1 | — | 28.40 | 0.74 | 42.43 | 1.00 |
| M203 3 | 5 | — | 38.51 | 1.00 | 55.91 | 1.00 |
| M79 2 | 5 | — | 39.65 | 1.03 | 56.46 | 1.00 |
| M79 3 | 5 | — | 40.17 | 1.04 | 56.38 | 1.00 |

## D5 / builtin / high — median 36.02s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 23.81 | 0.66 | 40.35 | 1.00 |
| PPK | 1 | — | 25.01 | 0.69 | 40.98 | 1.00 |
| M203 3 | 5 | — | 36.02 | 1.00 | 54.51 | 1.00 |
| M79 2 | 5 | — | 37.31 | 1.04 | 55.36 | 1.00 |
| M79 3 | 5 | — | 39.61 | 1.10 | 55.41 | 1.00 |

## D5 / catalog / low — median 21.39s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M203 3 | 5 | Heat, Random, RoF5 | 20.19 | 0.94 | 29.64 | 1.00 |
| M79 2 | 5 | Heat, Random, RoF5 | 20.44 | 0.96 | 30.46 | 1.00 |
| M10B | 2 | Heat, RoF5 | 21.39 | 1.00 | 31.95 | 1.00 |
| M79 3 | 5 | Heat, RoF5 | 24.69 | 1.15 | 38.49 | 1.00 |
| PPK | 1 | Heat | 27.05 | 1.26 | 40.52 | 1.00 |

## D5 / catalog / typical — median 21.35s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M203 3 | 5 | Heat, Random, RoF5 | 19.25 | 0.90 | 29.60 | 1.00 |
| M79 2 | 5 | Heat, Random, RoF5 | 19.92 | 0.93 | 29.79 | 1.00 |
| M10B | 2 | Heat, RoF5 | 21.35 | 1.00 | 31.93 | 1.00 |
| M79 3 | 5 | Heat, RoF5 | 24.54 | 1.15 | 38.44 | 1.00 |
| PPK | 1 | Heat | 26.39 | 1.24 | 36.29 | 1.00 |

## D5 / catalog / high — median 21.33s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M203 3 | 5 | Heat, Random, RoF5 | 18.80 | 0.88 | 29.17 | 1.00 |
| M79 2 | 5 | Heat, Random, RoF5 | 19.17 | 0.90 | 29.18 | 1.00 |
| M10B | 2 | Heat, RoF5 | 21.33 | 1.00 | 31.89 | 1.00 |
| M79 3 | 5 | Heat, RoF5 | 24.50 | 1.15 | 39.37 | 1.00 |
| PPK | 1 | Heat | 24.84 | 1.16 | 35.05 | 1.00 |

## Disc2 / builtin / low — median 18.44s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| PPK | 1 | — | 14.19 | 0.77 | 124.86 | 1.00 |
| M10B | 2 | — | 16.22 | 0.88 | 72.00 | 1.00 |
| M79 3 | 5 | — | 18.44 | 1.00 | 113.13 | 1.00 |
| M203 3 | 5 | — | 21.30 | 1.16 | 123.68 | 1.00 |
| M79 2 | 5 | — | 21.66 | 1.17 | 131.35 | 1.00 |

## Disc2 / builtin / typical — median 17.88s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| PPK | 1 | — | 12.80 | 0.72 | 110.99 | 1.00 |
| M10B | 2 | — | 15.49 | 0.87 | 65.08 | 1.00 |
| M79 3 | 5 | — | 17.88 | 1.00 | 99.64 | 1.00 |
| M203 3 | 5 | — | 20.08 | 1.12 | 108.47 | 1.00 |
| M79 2 | 5 | — | 20.58 | 1.15 | 109.14 | 1.00 |

## Disc2 / builtin / high — median 17.20s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| PPK | 1 | — | 12.09 | 0.70 | 94.33 | 1.00 |
| M10B | 2 | — | 15.48 | 0.90 | 58.69 | 1.00 |
| M79 3 | 5 | — | 17.20 | 1.00 | 86.57 | 1.00 |
| M203 3 | 5 | — | 19.44 | 1.13 | 94.82 | 1.00 |
| M79 2 | 5 | — | 19.54 | 1.14 | 96.07 | 1.00 |

## Disc2 / catalog / low — median 10.66s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.33 | 0.78 | 15.39 | 1.00 |
| M79 3 | 5 | 2Cmd, Quickdraw, RoF5 | 10.53 | 0.99 | 28.40 | 1.00 |
| M203 3 | 5 | 2Cmd, Quickdraw, RoF5, Heat | 10.66 | 1.00 | 29.12 | 1.00 |
| M79 2 | 5 | 2Cmd, Quickdraw, RoF5 | 10.70 | 1.00 | 34.57 | 1.00 |
| PPK | 1 | 2Cmd, Acid | 12.01 | 1.13 | 77.34 | 1.00 |

## Disc2 / catalog / typical — median 10.58s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.32 | 0.79 | 15.24 | 1.00 |
| M79 3 | 5 | 2Cmd, Quickdraw, RoF5 | 10.50 | 0.99 | 27.03 | 1.00 |
| M79 2 | 5 | 2Cmd, Quickdraw, RoF5 | 10.58 | 1.00 | 29.97 | 1.00 |
| M203 3 | 5 | 2Cmd, Quickdraw, RoF5, Heat | 10.61 | 1.00 | 26.02 | 1.00 |
| PPK | 1 | 2Cmd, Acid | 11.41 | 1.08 | 68.18 | 1.00 |

## Disc2 / catalog / high — median 10.55s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.27 | 0.78 | 14.34 | 1.00 |
| M79 3 | 5 | 2Cmd, Quickdraw, RoF5 | 10.48 | 0.99 | 24.37 | 1.00 |
| M203 3 | 5 | 2Cmd, Quickdraw, RoF5, Heat | 10.55 | 1.00 | 21.93 | 1.00 |
| M79 2 | 5 | 2Cmd, Quickdraw, RoF5 | 10.57 | 1.00 | 26.03 | 1.00 |
| PPK | 1 | 2Cmd, Acid | 10.87 | 1.03 | 56.00 | 1.00 |

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
