# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.49 (0.66) | 8.22 → 7.58 | 0.20 → 0.03 | 15.6 → 12.1 (0.78, 0.56) | 0.02 |
| default | ALL boss | 12 | 3.50 → 4.12 (0.85) | 2.17 → 11.20 | 0.58 → 0.56 | 17.3 → 15.1 (0.87, 0.21) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.66 (0.79) | 10.16 → 8.36 | 0.75 → 0.28 | 4.2 → 8.8 (2.07, 0.14) | 0.15 |
| default | D1 boss | 4 | 3.50 → 3.56 (0.99) | 9.22 → 8.88 | 0.50 → 0.69 | 3.2 → 9.4 (2.88, -0.48) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.08 (0.77) | 7.23 → 7.35 | 0.27 → 0.00 | 26.9 → 31.0 (1.15, 0.59) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 69.9 (2.33, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 4.94 (0.90) | 7.92 → 15.55 | 0.75 → 1.00 | 32.2 → 0.9 (0.03, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.29 (0.53) | 7.70 → 5.93 | 0.12 → 0.00 | 13.2 → 7.0 (0.52, 0.53) | 0.01 |
| default | Disc2 boss | 2 | 3.00 → 3.62 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 0.0 (0.00, n/a) | 0.00 |
