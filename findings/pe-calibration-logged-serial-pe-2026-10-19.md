# Logged-battle calibration — October 18, 2026

Independent check: every logged won battle replayed with its logged gun/armor/level and enemies (4 fights each; player policy walk, reaction 30 updates, log-era Counter boost True). HP unbounded; damage is not truncated.

Battles with PE casts are excluded (PE abilities are not simulated). Logged real time = frames / 59.9 (the logger secs field is seconds / 10) and includes intro/results overhead; compare turns and the per-turn time slope.

| Assumptions | Group | n | Turns logged → sim (r) | Time s/turn logged → sim | Reloads logged → sim | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---|---|---|---|---|---|---|
| default | ALL normal | 143 | 2.64 → 2.55 (0.65) | 14.21 → 10.40 | 0.28 → 0.09 | 24.5 → 26.1 (1.07, 0.64) | 0.02 |
| default | ALL boss | 28 | 8.61 → 4.66 (0.48) | 9.14 → 8.06 | 1.00 → 0.47 | 338.6 → 305.1 (0.90, 0.51) | 0.32 |
| default | D1 normal | 8 | 2.75 → 2.69 (0.78) | 10.16 → 8.35 | 0.75 → 0.25 | 4.2 → 11.8 (2.79, 0.19) | 0.19 |
| default | D1 boss | 4 | 3.50 → 3.44 (0.98) | 9.22 → 8.49 | 0.50 → 0.62 | 3.2 → 9.2 (2.85, -0.92) | 0.00 |
| default | D2-4 normal | 33 | 3.09 → 3.24 (0.64) | 13.43 → 8.62 | 0.27 → 0.02 | 29.4 → 44.5 (1.51, 0.59) | 0.00 |
| default | D2-4 boss | 5 | 9.40 → 4.65 (0.39) | 7.97 → 7.04 | 1.40 → 0.20 | 126.2 → 275.9 (2.19, 0.79) | 0.50 |
| default | D5 normal | 10 | 6.80 → 4.10 (0.54) | 12.78 → 12.91 | 1.30 → 0.97 | 89.0 → 57.4 (0.64, 0.62) | 0.00 |
| default | D5 boss | 8 | 5.88 → 4.75 (0.26) | 14.01 → 16.01 | 1.00 → 0.88 | 86.1 → 48.8 (0.57, 0.22) | 0.00 |
| default | Disc2 normal | 92 | 2.01 → 2.12 (0.47) | 8.40 → 6.84 | 0.13 → 0.00 | 17.5 → 17.4 (1.00, 0.67) | 0.01 |
| default | Disc2 boss | 11 | 12.09 → 5.05 (0.50) | 7.40 → 5.47 | 1.00 → 0.25 | 740.7 → 612.5 (0.83, 0.27) | 0.48 |
