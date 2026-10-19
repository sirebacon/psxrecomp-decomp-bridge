# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Parasite Energy and items are simulated (parasite_energy.py), replaying the logged casts. Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 142 | 2.63 → 2.69 (0.77) | 14.23 → 9.51 | 0.27 → 0.09 | 24.5 → 25.8 (1.05, 0.77) | 0.00 |
| default | ALL boss | 31 | 8.16 → 6.62 (0.74) | 9.34 → 7.71 | 0.94 → 0.52 | 313.5 → 206.5 (0.66, 0.82) | 0.00 |
| default | D1 normal | 7 | 2.57 → 2.75 (0.83) | 7.44 → 7.98 | 0.71 → 0.29 | 1.6 → 9.8 (6.20, 0.75) | 0.00 |
| default | D1 boss | 5 | 3.60 → 3.40 (0.91) | 9.60 → 8.80 | 0.60 → 0.65 | 7.2 → 6.8 (0.95, -0.17) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.45 (0.74) | 13.43 → 7.69 | 0.27 → 0.03 | 29.4 → 32.9 (1.12, 0.56) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.70 (0.99) | 7.97 → 9.48 | 1.40 → 0.40 | 126.2 → 151.9 (1.20, 0.89) | 0.00 |
| default | D5 normal | 10 | 6.80 → 5.38 (0.75) | 12.78 → 7.09 | 1.30 → 0.95 | 89.0 → 99.0 (1.11, 0.88) | 0.00 |
| default | D5 boss | 8 | 5.88 → 6.00 (0.70) | 14.01 → 10.87 | 1.00 → 0.78 | 86.1 → 78.2 (0.91, 0.50) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.47) | 8.40 → 6.94 | 0.13 → 0.00 | 17.5 → 16.5 (0.94, 0.68) | 0.00 |
| default | Disc2 boss | 13 | 10.85 → 7.83 (0.64) | 8.43 → 7.42 | 0.85 → 0.37 | 643.2 → 383.3 (0.60, 0.77) | 0.00 |
