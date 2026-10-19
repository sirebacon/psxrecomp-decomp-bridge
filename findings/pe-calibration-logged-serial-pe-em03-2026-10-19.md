# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.66 (0.64) | 14.21 → 9.71 | 0.28 → 0.09 | 24.5 → 22.2 (0.91, 0.63) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.02 (0.59) | 9.14 → 5.53 | 1.00 → 0.47 | 338.6 → 263.2 (0.78, 0.46) | 0.27 |
| default | D1 normal | 8 | 2.75 → 2.75 (0.63) | 10.16 → 8.09 | 0.75 → 0.31 | 4.2 → 9.0 (2.11, 0.11) | 0.13 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.79 | 0.50 → 0.62 | 3.2 → 8.7 (2.67, -0.90) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.38 (0.68) | 13.43 → 7.72 | 0.27 → 0.02 | 29.4 → 37.1 (1.26, 0.58) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 8.40 (0.71) | 7.97 → 5.85 | 1.40 → 0.20 | 126.2 → 310.3 (2.46, 0.16) | 0.40 |
| default | D5 normal | 10 | 6.80 → 4.12 (0.54) | 12.78 → 12.46 | 1.30 → 0.97 | 89.0 → 57.0 (0.64, 0.62) | 0.00 |
| default | D5 boss | 8 | 5.88 → 5.62 (0.43) | 14.01 → 12.37 | 1.00 → 0.78 | 86.1 → 44.6 (0.52, 0.16) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.24 (0.43) | 8.40 → 6.57 | 0.13 → 0.00 | 17.5 → 14.3 (0.82, 0.62) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 8.66 (0.40) | 7.40 → 4.95 | 1.00 → 0.32 | 740.7 → 493.4 (0.67, 0.28) | 0.45 |
