# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 40 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.37 (0.63) | 8.22 → 8.57 | 0.20 → 0.03 | 15.6 → 18.0 (1.15, 0.58) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.17 (0.86) | 2.17 → 12.99 | 0.58 → 0.54 | 17.3 → 19.3 (1.12, 0.20) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.78) | 10.16 → 8.69 | 0.75 → 0.25 | 4.2 → 11.8 (2.79, 0.19) | 0.19 |
| default | D1 boss | 4 | 3.50 → 3.50 (0.99) | 9.22 → 9.03 | 0.50 → 0.69 | 3.2 → 10.2 (3.13, -0.25) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.11 (0.76) | 7.23 → 7.33 | 0.27 → 0.00 | 26.9 → 38.5 (1.43, 0.66) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 83.1 (2.77, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.00 (0.88) | 7.92 → 17.03 | 0.75 → 0.94 | 32.2 → 0.9 (0.03, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.12 (0.46) | 7.70 → 7.31 | 0.12 → 0.00 | 13.2 → 12.6 (0.95, 0.52) | 0.02 |
| default | Disc2 boss | 2 | 3.00 → 3.88 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 10.6 (3.54, n/a) | 0.00 |
