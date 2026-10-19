# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.74 (0.75) | 14.21 → 9.50 | 0.28 → 0.10 | 24.5 → 27.6 (1.13, 0.75) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.45 (0.66) | 9.14 → 7.52 | 1.00 → 0.57 | 338.6 → 236.2 (0.70, 0.67) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.81 (0.63) | 10.16 → 7.88 | 0.75 → 0.31 | 4.2 → 9.2 (2.16, -0.04) | 0.00 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.98) | 9.22 → 8.04 | 0.50 → 0.69 | 3.2 → 9.2 (2.83, -0.74) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.56 (0.77) | 13.43 → 7.89 | 0.27 → 0.02 | 29.4 → 38.3 (1.30, 0.58) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.35 (0.99) | 7.97 → 9.38 | 1.40 → 0.40 | 126.2 → 149.3 (1.18, 0.90) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.45 (0.71) | 12.78 → 7.43 | 1.30 → 1.05 | 89.0 → 101.2 (1.14, 0.83) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.22 (0.73) | 14.01 → 12.04 | 1.00 → 0.78 | 86.1 → 94.5 (1.10, 0.50) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.15 (0.37) | 8.40 → 6.67 | 0.13 → 0.01 | 17.5 → 17.4 (0.99, 0.69) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 9.80 (0.41) | 7.40 → 7.24 | 1.00 → 0.45 | 740.7 → 461.3 (0.62, 0.49) | 0.00 |
