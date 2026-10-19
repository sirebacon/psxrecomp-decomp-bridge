# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.54 (0.57) | 8.22 → 7.89 | 0.20 → 0.03 | 15.6 → 19.8 (1.27, 0.53) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.23 (0.84) | 2.17 → 11.58 | 0.58 → 0.52 | 17.3 → 21.6 (1.25, 0.22) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.62 (0.72) | 10.16 → 8.15 | 0.75 → 0.28 | 4.2 → 9.8 (2.32, 0.02) | 0.11 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.94) | 9.22 → 9.13 | 0.50 → 0.56 | 3.2 → 7.7 (2.37, -0.47) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.15 (0.77) | 7.23 → 7.39 | 0.27 → 0.00 | 26.9 → 33.3 (1.24, 0.67) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 96.8 (3.23, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 4.2 (0.24, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.25 (0.87) | 7.92 → 15.01 | 0.75 → 1.00 | 32.2 → 1.5 (0.05, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.34 (0.37) | 7.70 → 6.39 | 0.12 → 0.00 | 13.2 → 16.9 (1.28, 0.46) | 0.03 |
| default | Disc2 boss | 2 | 3.00 → 3.75 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 14.5 (4.83, n/a) | 0.00 |
