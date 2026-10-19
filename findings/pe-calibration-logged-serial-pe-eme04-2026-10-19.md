# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.59 (0.65) | 14.21 → 9.69 | 0.28 → 0.09 | 24.5 → 24.1 (0.98, 0.66) | 0.01 |
| default | ALL boss | 28 | 8.61 → 7.03 (0.61) | 9.14 → 5.76 | 1.00 → 0.47 | 338.6 → 305.0 (0.90, 0.49) | 0.27 |
| default | D1 normal | 8 | 2.75 → 2.75 (0.63) | 10.16 → 8.00 | 0.75 → 0.31 | 4.2 → 8.1 (1.92, 0.16) | 0.14 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.76 | 0.50 → 0.62 | 3.2 → 9.5 (2.92, -0.92) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.41 (0.68) | 13.43 → 7.68 | 0.27 → 0.02 | 29.4 → 36.5 (1.24, 0.57) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 8.25 (0.63) | 7.97 → 6.66 | 1.40 → 0.20 | 126.2 → 288.7 (2.29, 0.00) | 0.32 |
| default | D5 normal | 10 | 6.80 → 4.12 (0.54) | 12.78 → 12.53 | 1.30 → 0.97 | 89.0 → 57.4 (0.64, 0.62) | 0.00 |
| default | D5 boss | 8 | 5.88 → 5.66 (0.39) | 14.01 → 12.43 | 1.00 → 0.88 | 86.1 → 48.8 (0.57, 0.22) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.47) | 8.40 → 6.84 | 0.13 → 0.00 | 17.5 → 17.4 (1.00, 0.67) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 8.73 (0.48) | 7.40 → 5.28 | 1.00 → 0.25 | 740.7 → 606.2 (0.82, 0.27) | 0.47 |
