# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.58 (0.65) | 14.21 → 9.82 | 0.28 → 0.09 | 24.5 → 22.8 (0.93, 0.67) | 0.01 |
| default | ALL boss | 28 | 8.61 → 6.90 (0.64) | 9.14 → 6.01 | 1.00 → 0.46 | 338.6 → 279.5 (0.83, 0.51) | 0.28 |
| default | D1 normal | 8 | 2.75 → 2.72 (0.62) | 10.16 → 7.95 | 0.75 → 0.31 | 4.2 → 7.8 (1.83, -0.01) | 0.06 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.79 | 0.50 → 0.62 | 3.2 → 6.2 (1.90, -0.78) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.36 (0.67) | 13.43 → 7.76 | 0.27 → 0.03 | 29.4 → 31.0 (1.05, 0.60) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 7.90 (0.74) | 7.97 → 6.83 | 1.40 → 0.20 | 126.2 → 246.5 (1.95, 0.01) | 0.33 |
| default | D5 normal | 10 | 6.80 → 4.12 (0.54) | 12.78 → 12.53 | 1.30 → 0.97 | 89.0 → 57.4 (0.64, 0.62) | 0.00 |
| default | D5 boss | 8 | 5.88 → 5.59 (0.42) | 14.01 → 12.27 | 1.00 → 0.84 | 86.1 → 48.4 (0.56, 0.16) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.47) | 8.40 → 6.84 | 0.13 → 0.00 | 17.5 → 17.4 (1.00, 0.67) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 8.61 (0.51) | 7.40 → 5.66 | 1.00 → 0.25 | 740.7 → 561.9 (0.76, 0.28) | 0.50 |
