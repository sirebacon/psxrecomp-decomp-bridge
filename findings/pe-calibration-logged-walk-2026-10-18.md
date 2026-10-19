# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 0 updates). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.62 (0.63) | 8.22 → 5.54 | 0.20 → 0.03 | 15.6 → 38.3 (2.46, 0.45) | 0.16 |
| default | ALL boss | 12 | 3.50 → 4.25 (0.81) | 2.17 → 10.17 | 0.58 → 0.58 | 17.3 → 68.5 (3.95, 0.05) | 0.04 |
| default | D1 normal | 8 | 2.75 → 2.62 (0.88) | 10.16 → 6.43 | 0.75 → 0.28 | 4.2 → 16.6 (3.90, -0.06) | 0.19 |
| default | D1 boss | 4 | 3.50 → 3.62 (1.00) | 9.22 → 6.58 | 0.50 → 0.75 | 3.2 → 20.7 (6.37, -0.07) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.12 (0.76) | 7.23 → 5.12 | 0.27 → 0.02 | 26.9 → 62.3 (2.31, 0.68) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.62 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 218.6 (7.29, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 22.5 (1.25, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.12 (0.82) | 7.92 → 14.51 | 0.75 → 1.00 | 32.2 → 0.0 (0.00, n/a) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.47 (0.52) | 7.70 → 4.21 | 0.12 → 0.00 | 13.2 → 33.3 (2.52, 0.35) | 0.24 |
| default | Disc2 boss | 2 | 3.00 → 3.38 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 151.3 (50.43, n/a) | 0.73 |
