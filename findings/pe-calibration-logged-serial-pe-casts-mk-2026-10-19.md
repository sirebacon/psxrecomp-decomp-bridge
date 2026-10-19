# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.69 (0.77) | 14.21 → 9.48 | 0.28 → 0.10 | 24.5 → 25.4 (1.04, 0.75) | 0.01 |
| default | ALL boss | 28 | 8.61 → 6.68 (0.72) | 9.14 → 6.90 | 1.00 → 0.51 | 338.6 → 239.2 (0.71, 0.53) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.78 (0.74) | 10.16 → 8.05 | 0.75 → 0.38 | 4.2 → 7.5 (1.76, -0.10) | 0.00 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.79 | 0.50 → 0.62 | 3.2 → 6.2 (1.90, -0.78) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.45 (0.74) | 13.43 → 7.69 | 0.27 → 0.03 | 29.4 → 32.2 (1.10, 0.56) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 6.45 (0.90) | 7.97 → 11.00 | 1.40 → 0.20 | 126.2 → 71.5 (0.57, -0.60) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.35 (0.76) | 12.78 → 7.01 | 1.30 → 0.95 | 89.0 → 94.2 (1.06, 0.87) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.00 (0.67) | 14.01 → 13.10 | 1.00 → 0.78 | 86.1 → 82.6 (0.96, 0.64) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.46) | 8.40 → 6.85 | 0.13 → 0.00 | 17.5 → 17.0 (0.97, 0.65) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 8.41 (0.61) | 7.40 → 6.69 | 1.00 → 0.41 | 740.7 → 514.2 (0.69, 0.34) | 0.00 |
