# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.48 (0.62) | 8.22 → 7.91 | 0.20 → 0.03 | 15.6 → 21.4 (1.37, 0.57) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.19 (0.84) | 2.17 → 11.31 | 0.58 → 0.50 | 17.3 → 23.3 (1.34, 0.23) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.62 (0.72) | 10.16 → 8.08 | 0.75 → 0.28 | 4.2 → 10.6 (2.49, 0.11) | 0.16 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.94) | 9.22 → 8.92 | 0.50 → 0.56 | 3.2 → 8.7 (2.67, -0.37) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.12 (0.79) | 7.23 → 7.39 | 0.27 → 0.00 | 26.9 → 40.7 (1.51, 0.73) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 103.4 (3.45, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.12 (0.89) | 7.92 → 15.31 | 0.75 → 0.94 | 32.2 → 2.3 (0.07, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.26 (0.44) | 7.70 → 6.28 | 0.12 → 0.00 | 13.2 → 16.8 (1.27, 0.48) | 0.03 |
| default | Disc2 boss | 2 | 3.00 → 3.75 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 14.5 (4.83, n/a) | 0.00 |
