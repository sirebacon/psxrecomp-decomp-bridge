# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.36 (0.62) | 8.22 → 8.20 | 0.20 → 0.03 | 15.6 → 18.9 (1.21, 0.56) | 0.03 |
| default | ALL boss | 12 | 3.50 → 4.17 (0.85) | 2.17 → 12.53 | 0.58 → 0.52 | 17.3 → 25.3 (1.46, 0.23) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.78) | 10.16 → 8.35 | 0.75 → 0.25 | 4.2 → 11.8 (2.79, 0.19) | 0.19 |
| default | D1 boss | 4 | 3.50 → 3.44 (0.98) | 9.22 → 8.49 | 0.50 → 0.62 | 3.2 → 9.2 (2.85, -0.92) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.11 (0.76) | 7.23 → 7.00 | 0.27 → 0.00 | 26.9 → 38.2 (1.42, 0.66) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 120.9 (4.03, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 5.8 (0.32, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.06 (0.86) | 7.92 → 15.25 | 0.75 → 0.94 | 32.2 → 0.9 (0.03, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.11 (0.44) | 7.70 → 6.90 | 0.12 → 0.00 | 13.2 → 14.0 (1.05, 0.50) | 0.02 |
| default | Disc2 boss | 2 | 3.00 → 3.88 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 10.6 (3.54, n/a) | 0.00 |
