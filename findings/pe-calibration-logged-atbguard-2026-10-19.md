# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 0 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.40 (0.63) | 8.22 → 5.55 | 0.20 → 0.03 | 15.6 → 29.0 (1.86, 0.49) | 0.04 |
| default | ALL boss | 12 | 3.50 → 4.27 (0.87) | 2.17 → 9.04 | 0.58 → 0.56 | 17.3 → 23.4 (1.35, 0.20) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.83) | 10.16 → 5.89 | 0.75 → 0.28 | 4.2 → 12.2 (2.87, 0.28) | 0.24 |
| default | D1 boss | 4 | 3.50 → 3.62 (0.97) | 9.22 → 6.44 | 0.50 → 0.69 | 3.2 → 9.6 (2.94, -0.53) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.13 (0.76) | 7.23 → 5.06 | 0.27 → 0.00 | 26.9 → 47.1 (1.75, 0.73) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 103.4 (3.45, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.19 (0.98) | 7.92 → 14.28 | 0.75 → 1.00 | 32.2 → 1.2 (0.04, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.15 (0.46) | 7.70 → 3.65 | 0.12 → 0.00 | 13.2 → 25.5 (1.92, 0.42) | 0.05 |
| default | Disc2 boss | 2 | 3.00 → 4.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 15.2 (5.08, n/a) | 0.00 |
