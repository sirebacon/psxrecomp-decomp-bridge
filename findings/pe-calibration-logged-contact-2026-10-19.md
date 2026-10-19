# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.67 (0.75) | 14.21 → 9.68 | 0.28 → 0.10 | 24.5 → 26.2 (1.07, 0.76) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.58 (0.66) | 9.14 → 7.49 | 1.00 → 0.60 | 338.6 → 239.1 (0.71, 0.67) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.66 (0.86) | 10.16 → 8.07 | 0.75 → 0.28 | 4.2 → 7.3 (1.71, -0.20) | 0.00 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.98) | 9.22 → 8.00 | 0.50 → 0.69 | 3.2 → 9.0 (2.77, -0.80) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.46 (0.73) | 13.43 → 7.70 | 0.27 → 0.02 | 29.4 → 34.9 (1.19, 0.60) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.45 (1.00) | 7.97 → 9.39 | 1.40 → 0.40 | 126.2 → 143.8 (1.14, 0.90) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.25 (0.70) | 12.78 → 8.11 | 1.30 → 1.05 | 89.0 → 95.6 (1.07, 0.84) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.25 (0.74) | 14.01 → 12.16 | 1.00 → 0.88 | 86.1 → 92.9 (1.08, 0.46) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.11 (0.39) | 8.40 → 7.01 | 0.13 → 0.01 | 17.5 → 17.1 (0.98, 0.67) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 10.07 (0.40) | 7.40 → 7.26 | 1.00 → 0.45 | 740.7 → 472.6 (0.64, 0.49) | 0.00 |
