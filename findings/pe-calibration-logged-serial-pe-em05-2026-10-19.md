# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.73 (0.62) | 14.21 → 9.77 | 0.28 → 0.09 | 24.5 → 20.6 (0.84, 0.63) | 0.01 |
| default | ALL boss | 28 | 8.61 → 6.96 (0.59) | 9.14 → 5.98 | 1.00 → 0.45 | 338.6 → 222.1 (0.66, 0.40) | 0.21 |
| default | D1 normal | 8 | 2.75 → 2.75 (0.63) | 10.16 → 7.98 | 0.75 → 0.31 | 4.2 → 7.8 (1.82, 0.07) | 0.09 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.75 | 0.50 → 0.62 | 3.2 → 7.8 (2.40, -0.85) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.39 (0.68) | 13.43 → 7.80 | 0.27 → 0.03 | 29.4 → 34.0 (1.15, 0.58) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 8.25 (0.65) | 7.97 → 6.41 | 1.40 → 0.20 | 126.2 → 285.3 (2.26, -0.03) | 0.31 |
| default | D5 normal | 10 | 6.80 → 4.12 (0.54) | 12.78 → 12.68 | 1.30 → 0.97 | 89.0 → 56.1 (0.63, 0.63) | 0.00 |
| default | D5 boss | 8 | 5.88 → 5.62 (0.43) | 14.01 → 12.40 | 1.00 → 0.78 | 86.1 → 44.1 (0.51, 0.15) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.34 (0.42) | 8.40 → 6.86 | 0.13 → 0.00 | 17.5 → 13.1 (0.75, 0.59) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 8.57 (0.43) | 7.40 → 5.66 | 1.00 → 0.25 | 740.7 → 400.8 (0.54, 0.25) | 0.40 |
