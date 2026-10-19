# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.06 (0.60) | 8.22 → 7.97 | 0.20 → 0.03 | 15.6 → 36.3 (2.33, 0.56) | 0.04 |
| default | ALL boss | 12 | 3.50 → 4.21 (0.82) | 2.17 → 11.50 | 0.58 → 0.62 | 17.3 → 47.5 (2.74, 0.20) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.66) | 10.16 → 7.50 | 0.75 → 0.22 | 4.2 → 15.4 (3.61, 0.28) | 0.18 |
| default | D1 boss | 4 | 3.50 → 3.44 (0.98) | 9.22 → 9.14 | 0.50 → 0.62 | 3.2 → 16.3 (5.02, -0.57) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.10 (0.80) | 7.23 → 7.30 | 0.27 → 0.00 | 26.9 → 66.4 (2.46, 0.77) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.62 (n/a) | n/a → n/a | 0.50 → 0.12 | 30.0 → 209.4 (6.98, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.19 (0.77) | 7.92 → 14.96 | 0.75 → 1.19 | 32.2 → 1.3 (0.04, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 1.69 (0.33) | 7.70 → 6.11 | 0.12 → 0.01 | 13.2 → 29.7 (2.24, 0.45) | 0.04 |
| default | Disc2 boss | 2 | 3.00 → 3.38 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 40.6 (13.54, n/a) | 0.00 |
