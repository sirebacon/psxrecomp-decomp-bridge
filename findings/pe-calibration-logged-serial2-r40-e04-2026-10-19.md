# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 40 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.50 (0.60) | 8.22 → 8.39 | 0.20 → 0.03 | 15.6 → 14.4 (0.92, 0.51) | 0.02 |
| default | ALL boss | 12 | 3.50 → 4.10 (0.81) | 2.17 → 12.51 | 0.58 → 0.44 | 17.3 → 13.1 (0.75, 0.03) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.72 (0.67) | 10.16 → 8.46 | 0.75 → 0.31 | 4.2 → 8.9 (2.09, 0.10) | 0.14 |
| default | D1 boss | 4 | 3.50 → 3.44 (0.93) | 9.22 → 9.13 | 0.50 → 0.50 | 3.2 → 9.2 (2.85, -0.11) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.12 (0.77) | 7.23 → 7.06 | 0.27 → 0.00 | 26.9 → 31.1 (1.15, 0.64) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 38.5 (1.28, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 8.2 (0.46, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.00 (0.87) | 7.92 → 15.18 | 0.75 → 0.81 | 32.2 → 1.3 (0.04, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.30 (0.41) | 7.70 → 7.37 | 0.12 → 0.01 | 13.2 → 10.1 (0.76, 0.43) | 0.01 |
| default | Disc2 boss | 2 | 3.00 → 3.62 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 18.9 (6.29, n/a) | 0.00 |
