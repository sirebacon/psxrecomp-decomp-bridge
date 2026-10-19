# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.45 (0.55) | 8.22 → 8.17 | 0.20 → 0.03 | 15.6 → 21.6 (1.39, 0.55) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.21 (0.79) | 2.17 → 10.65 | 0.58 → 0.56 | 17.3 → 20.8 (1.20, 0.21) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.75 (0.63) | 10.16 → 7.66 | 0.75 → 0.28 | 4.2 → 6.6 (1.55, -0.08) | 0.12 |
| default | D1 boss | 4 | 3.50 → 3.38 (1.00) | 9.22 → 9.22 | 0.50 → 0.69 | 3.2 → 4.2 (1.31, -0.46) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.14 (0.78) | 7.23 → 7.41 | 0.27 → 0.00 | 26.9 → 35.2 (1.31, 0.68) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 95.2 (3.17, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 6.0 (0.33, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.31 (0.86) | 7.92 → 15.88 | 0.75 → 1.00 | 32.2 → 1.5 (0.05, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.20 (0.29) | 7.70 → 6.76 | 0.12 → 0.00 | 13.2 → 19.2 (1.45, 0.47) | 0.04 |
| default | Disc2 boss | 2 | 3.00 → 3.88 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 17.9 (5.96, n/a) | 0.00 |
