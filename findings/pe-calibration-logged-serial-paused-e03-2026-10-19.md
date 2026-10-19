# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.56 (0.64) | 8.22 → 7.58 | 0.20 → 0.03 | 15.6 → 10.2 (0.65, 0.52) | 0.02 |
| default | ALL boss | 12 | 3.50 → 4.08 (0.79) | 2.17 → 10.88 | 0.58 → 0.48 | 17.3 → 10.5 (0.60, 0.21) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.75 (0.73) | 10.16 → 8.26 | 0.75 → 0.34 | 4.2 → 7.2 (1.70, 0.03) | 0.10 |
| default | D1 boss | 4 | 3.50 → 3.31 (0.94) | 9.22 → 8.89 | 0.50 → 0.50 | 3.2 → 7.1 (2.19, -0.55) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.11 (0.78) | 7.23 → 7.37 | 0.27 → 0.00 | 26.9 → 26.2 (0.97, 0.60) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 46.4 (1.55, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.06 (0.83) | 7.92 → 15.47 | 0.75 → 0.94 | 32.2 → 1.1 (0.03, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.38 (0.51) | 7.70 → 5.90 | 0.12 → 0.00 | 13.2 → 5.7 (0.43, 0.47) | 0.01 |
| default | Disc2 boss | 2 | 3.00 → 3.62 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 0.0 (0.00, n/a) | 0.00 |
