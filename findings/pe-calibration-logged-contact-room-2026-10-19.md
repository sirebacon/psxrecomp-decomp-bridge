# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.68 (0.75) | 14.21 → 9.68 | 0.28 → 0.09 | 24.5 → 26.2 (1.07, 0.76) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.49 (0.67) | 9.14 → 7.48 | 1.00 → 0.59 | 338.6 → 234.3 (0.69, 0.68) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.66 (0.86) | 10.16 → 7.97 | 0.75 → 0.28 | 4.2 → 6.7 (1.58, -0.16) | 0.00 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.98) | 9.22 → 8.00 | 0.50 → 0.69 | 3.2 → 9.6 (2.96, -0.77) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.49 (0.73) | 13.43 → 7.80 | 0.27 → 0.02 | 29.4 → 34.9 (1.19, 0.59) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.35 (0.99) | 7.97 → 9.37 | 1.40 → 0.40 | 126.2 → 144.2 (1.14, 0.90) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.28 (0.72) | 12.78 → 8.00 | 1.30 → 1.00 | 89.0 → 95.9 (1.08, 0.85) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.19 (0.73) | 14.01 → 12.05 | 1.00 → 0.84 | 86.1 → 90.8 (1.05, 0.44) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.11 (0.39) | 8.40 → 7.04 | 0.13 → 0.01 | 17.5 → 17.2 (0.99, 0.69) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 9.93 (0.42) | 7.40 → 7.22 | 1.00 → 0.45 | 740.7 → 461.4 (0.62, 0.51) | 0.00 |
