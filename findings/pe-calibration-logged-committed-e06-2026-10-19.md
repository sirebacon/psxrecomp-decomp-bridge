# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.37 (0.60) | 8.22 → 8.24 | 0.20 → 0.03 | 15.6 → 24.9 (1.60, 0.56) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.29 (0.82) | 2.17 → 11.03 | 0.58 → 0.58 | 17.3 → 26.0 (1.50, 0.19) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.81 (0.78) | 10.16 → 7.74 | 0.75 → 0.34 | 4.2 → 10.1 (2.37, -0.24) | 0.10 |
| default | D1 boss | 4 | 3.50 → 3.50 (0.99) | 9.22 → 9.17 | 0.50 → 0.75 | 3.2 → 5.9 (1.81, -0.55) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.20 (0.76) | 7.23 → 7.38 | 0.27 → 0.00 | 26.9 → 46.4 (1.73, 0.67) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 118.9 (3.96, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 6.0 (0.33, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.44 (0.90) | 7.92 → 15.96 | 0.75 → 1.00 | 32.2 → 1.5 (0.05, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.07 (0.38) | 7.70 → 6.71 | 0.12 → 0.01 | 13.2 → 20.2 (1.52, 0.48) | 0.04 |
| default | Disc2 boss | 2 | 3.00 → 3.75 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 22.2 (7.42, n/a) | 0.00 |
