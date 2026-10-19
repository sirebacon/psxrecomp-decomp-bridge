# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 75 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 123 | 2.13 → 2.43 (0.66) | 8.22 → 8.20 | 0.20 → 0.03 | 15.6 → 16.4 (1.05, 0.55) | 0.04 |
| default | ALL boss | 12 | 3.50 → 4.15 (0.84) | 2.17 → 10.86 | 0.58 → 0.52 | 17.3 → 12.3 (0.71, 0.23) | 0.00 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.78) | 10.16 → 7.45 | 0.75 → 0.31 | 4.2 → 7.3 (1.72, 0.15) | 0.15 |
| default | D1 boss | 4 | 3.50 → 3.44 (0.98) | 9.22 → 9.05 | 0.50 → 0.62 | 3.2 → 4.0 (1.23, -0.05) | 0.00 |
| default | D2-4 normal | 26 | 2.65 → 3.17 (0.80) | 7.23 → 7.44 | 0.27 → 0.00 | 26.9 → 31.0 (1.15, 0.65) | 0.00 |
| default | D2-4 boss | 2 | 3.00 → 4.12 (n/a) | n/a → n/a | 0.50 → 0.00 | 30.0 → 56.6 (1.89, n/a) | 0.00 |
| default | D5 normal | 1 | 3.00 → 3.00 (n/a) | n/a → n/a | 1.00 → 1.00 | 18.0 → 6.0 (0.33, n/a) | 0.00 |
| default | D5 boss | 4 | 4.00 → 5.06 (0.86) | 7.92 → 15.10 | 0.75 → 0.94 | 32.2 → 0.5 (0.02, -0.09) | 0.00 |
| default | Disc2 normal | 88 | 1.91 → 2.18 (0.50) | 7.70 → 6.40 | 0.12 → 0.01 | 13.2 → 13.0 (0.98, 0.48) | 0.04 |
| default | Disc2 boss | 2 | 3.00 → 3.75 (n/a) | n/a → n/a | 0.50 → 0.00 | 3.0 → 8.1 (2.71, n/a) | 0.00 |
