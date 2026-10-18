# Extracted animation durations — 2026-10-18

Ordinary uninterrupted queued shots; bank0, nominal59.9/2 updates/s.
Counts include the initial battle call; reload and input time excluded.

| Class | Aim frames | Fire frames | 1 shot updates / seconds | 3 shot updates / seconds |
|---|---:|---:|---:|---:|
| handgun | 15 | 10 | 25 / 0.835 | 57 / 1.903 |
| shotgun | 15 | 30 | 50 / 1.669 | 112 / 3.740 |
| machine | 8 | 3 | 11 / 0.367 | 19 / 0.634 |
| rifle | 15 | 15 | 47 / 1.569 | 93 / 3.105 |
| grenade | 15 | 25 | 40 / 1.336 | 102 / 3.406 |
| rocket | 30 | 10 | 40 / 1.336 | 102 / 3.406 |
| special | 15 | 10 | 25 / 0.835 | 57 / 1.903 |
| club | 15 | 15 | 30 / 1.002 | 62 / 2.070 |

Synthetic frozen-equipment overlap benchmark, 8 matched seeds per encounter:

| Class | Legacy suite score | Asset-queue profile suite score |
|---|---:|---:|
| handgun | 19.388 | 57.335 |
| shotgun | 22.614 | 70.525 |
| machine | 19.247 | 57.335 |
| rifle | 23.126 | 70.525 |
| grenade | 23.034 | 70.525 |
| rocket | 42.047 | 196.402 |
| special | 19.388 | 57.335 |

The benchmark changes both gauge clock/arithmetic and animation timing; it does not
isolate animation-only effects. Suite scores include a 60-second penalty for encounters
with any losses; inspect raw win rates before interpreting them as clear times. It does not
establish policy rankings. The two costumes differ
in grenade/club aiming length. Burst/Random/AttackAll are explicitly rejected by this
profile until their alternate queue branches are reconstructed. Historical defaults
remain available; use decomp_animation.source_rules for this experimental profile.
