# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.41 (0.58) | 8.22 → 8.17 | 0.20 → 0.03 | 15.6 → 24.2 (1.55, 0.55) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.19 (0.80) | 2.17 → 10.82 | 0.58 → 0.56 | 17.3 → 21.6 (1.24, 0.22) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.78 (0.69) | 10.16 → 7.69 | 0.75 → 0.28 | 4.2 → 7.9 (1.86, -0.16) | 0.11 |
| default | D1 boss | 4 | 3.50 → 3.31 (0.99) | 9.22 → 9.11 | 0.50 → 0.62 | 3.2 → 3.8 (1.17, -0.69) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.22 (0.76) | 7.23 → 7.35 | 0.27 → 0.00 | 26.9 → 43.3 (1.61, 0.68) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 3.88 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 100.9 (3.36, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 6.0 (0.33, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.38 (0.92) | 7.92 → 16.46 | 0.75 → 1.06 | 32.2 → 1.5 (0.05, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.13 (0.34) | 7.70 → 6.71 | 0.12 → 0.01 | 13.2 → 20.3 (1.53, 0.47) | 0.04 |
| default | Disc2 boss | 2 | 3.00 → 3.88 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 17.9 (5.96, n/a) | 0.00 |
