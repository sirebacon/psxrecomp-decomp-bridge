# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.69 (0.77) | 14.21 → 9.47 | 0.28 → 0.10 | 24.5 → 26.3 (1.07, 0.76) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.74 (0.63) | 9.14 → 7.25 | 1.00 → 0.58 | 338.6 → 250.6 (0.74, 0.81) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.78 (0.74) | 10.16 → 8.05 | 0.75 → 0.38 | 4.2 → 8.5 (2.01, -0.07) | 0.00 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.79 | 0.50 → 0.62 | 3.2 → 6.4 (1.98, -0.77) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.45 (0.74) | 13.43 → 7.69 | 0.27 → 0.03 | 29.4 → 32.9 (1.12, 0.56) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.70 (0.99) | 7.97 → 9.48 | 1.40 → 0.40 | 126.2 → 151.9 (1.20, 0.89) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.38 (0.75) | 12.78 → 7.09 | 1.30 → 0.95 | 89.0 → 99.0 (1.11, 0.88) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.12 (0.75) | 14.01 → 12.03 | 1.00 → 0.78 | 86.1 → 87.6 (1.02, 0.60) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.46) | 8.40 → 6.80 | 0.13 → 0.00 | 17.5 → 17.5 (1.00, 0.65) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 10.45 (0.40) | 7.40 → 6.82 | 1.00 → 0.50 | 740.7 → 502.8 (0.68, 0.70) | 0.00 |
