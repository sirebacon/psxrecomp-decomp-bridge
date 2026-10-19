# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 0 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.35 (0.66) | 8.22 → 5.70 | 0.20 → 0.03 | 15.6 → 35.7 (2.29, 0.47) | 0.15 |
| default | ALL boss | 12 | 3.50 → 4.17 (0.79) | 2.17 → 10.31 | 0.58 → 0.58 | 17.3 → 68.2 (3.94, 0.03) | 0.05 |
| default | D1 normal | 8 | 2.75 → 2.62 (0.88) | 10.16 → 6.43 | 0.75 → 0.28 | 4.2 → 16.6 (3.90, -0.06) | 0.19 |
| default | D1 boss | 4 | 3.50 → 3.62 (1.00) | 9.22 → 6.58 | 0.50 → 0.75 | 3.2 → 20.7 (6.37, -0.07) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.14 (0.75) | 7.23 → 5.12 | 0.27 → 0.02 | 26.9 → 72.3 (2.68, 0.76) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.50 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 208.4 (6.95, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 22.5 (1.25, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.12 (0.82) | 7.92 → 14.51 | 0.75 → 1.00 | 32.2 → 0.0 (0.00, n/a) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.08 (0.53) | 7.70 → 3.03 | 0.12 → 0.00 | 13.2 → 26.8 (2.02, 0.29) | 0.26 |
| default | Disc2 boss | 2 | 3.00 → 3.00 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 159.7 (53.23, n/a) | 0.74 |
