# Native weapon balance review — 2026-10-26

Simulation only. No native game source, balance settings, or binaries changed.

2,496 simulated fights; 4 seeds; native-default attack bonuses and combat rules mapped into the calibrated source model.
Screen: up to 12 ordinary encounters and four bosses per stage, sampled separately with a fixed seed. Built-in-only has zero optional installs, including Disc2. Catalog selects the best native loadout from the tested feasible orders, prioritizing wins and then ordinary time; candidate comparisons keep that same loadout.
Stage availability follows the historical ladder: D5 includes museum-era guns and Wayne rewards. It is not exact pickup chronology.
Boss and ordinary results stay separate; these are not campaign-weighted totals. Candidate intervals resample encounter-level paired differences and describe model variation, not confidence in real gameplay.

## Revisited proposals

candidate_half / candidate_full: M203-3 +10 / +20, M79-2 +10 / +20, M79-3 +5 / +10, PPK +5 / +10 attack. Extended runs also test M79-3 +15 and +20. M10B: +1 or +50% magazine. Existing six native bonuses remain enabled in every case.

| Stage | Gun | Setup | Candidate | Fights | Ordinary seconds | Change | Paired delta interval, s | Win rate |
|---|---|---|---|---:|---|---:|---|---|
| D5 | M10B | builtin / attack_only | magazine_plus1 | 40 | 23.62 → 23.62 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / attack_only | magazine_plus50pct | 40 | 23.62 → 23.62 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / stock | magazine_plus1 | 40 | 25.21 → 25.04 | -0.7% | [-0.35, 0.0] | 1.00 → 1.00 |
| D5 | M10B | builtin / stock | magazine_plus50pct | 40 | 25.21 → 24.95 | -1.1% | [-0.49, -0.09] | 1.00 → 1.00 |
| D5 | M10B | catalog / attack_only | magazine_plus1 | 40 | 21.35 → 21.35 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / attack_only | magazine_plus50pct | 40 | 21.35 → 21.35 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / stock | magazine_plus1 | 40 | 22.45 → 22.27 | -0.8% | [-0.4, 0.0] | 1.00 → 1.00 |
| D5 | M10B | catalog / stock | magazine_plus50pct | 40 | 22.45 → 22.23 | -1.0% | [-0.49, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / attack_only | magazine_plus1 | 48 | 15.49 → 15.49 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / attack_only | magazine_plus50pct | 48 | 15.49 → 15.49 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / stock | magazine_plus1 | 48 | 18.20 → 18.31 | +0.6% | [0.0, 0.29] | 1.00 → 1.00 |
| Disc2 | M10B | builtin / stock | magazine_plus50pct | 48 | 18.20 → 18.09 | -0.6% | [-0.29, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / attack_only | magazine_plus1 | 48 | 8.57 → 8.46 | -1.3% | [-0.29, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / attack_only | magazine_plus50pct | 48 | 8.57 → 8.32 | -3.0% | [-0.63, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / stock | magazine_plus1 | 48 | 8.73 → 8.73 | +0.0% | [0.0, 0.0] | 1.00 → 1.00 |
| Disc2 | M10B | catalog / stock | magazine_plus50pct | 48 | 8.73 → 8.58 | -1.7% | [-0.44, 0.0] | 1.00 → 1.00 |

## D5 / builtin / stock — median 25.21s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 25.21 | 1.00 | 43.23 | 1.00 |

## D5 / builtin / attack_only — median 23.62s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 23.62 | 1.00 | 40.89 | 1.00 |

## D5 / catalog / stock — median 22.45s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | Heat, RoF5 | 22.45 | 1.00 | 33.57 | 1.00 |

## D5 / catalog / attack_only — median 21.35s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | Heat, RoF5 | 21.35 | 1.00 | 31.93 | 1.00 |

## Disc2 / builtin / stock — median 18.20s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 18.20 | 1.00 | 96.54 | 1.00 |

## Disc2 / builtin / attack_only — median 15.49s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | — | 15.49 | 1.00 | 67.74 | 1.00 |

## Disc2 / catalog / stock — median 8.73s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.73 | 1.00 | 23.80 | 1.00 |

## Disc2 / catalog / attack_only — median 8.57s

| Gun | Kind | Installs | Ordinary s | × median | Boss s | Boss wins |
|---|---|---|---:|---:|---:|---:|
| M10B | 2 | 2Cmd, Quickdraw, RoF5, Acid, Heat | 8.57 | 1.00 | 17.75 | 1.00 |

## Model limits

- Integer per-hit hook arithmetic mapped from native; crowd cap models restored final HP, not delayed engine updates or the native 40-frame reference heuristic.
- One logged campaign; synthetic loadouts, not a new acquisition/economy simulation.
- Catalog best-of tested orders is an optimistic upper bound, not guaranteed player ownership.
- Built-in-only means no optional installs at ALL stages, including Disc2.
- Infinite reserve per isolated battle; rocket results do not establish campaign ammo viability.
- Per-hit integer arithmetic passed 2,000 randomized comparisons against the native C helper compiled unchanged. This does not validate the entire fight model.
- Critical conversion uses the inherited probability 26.67% rather than native integer 26%; random sequences are not native RNG replays. The five disputed weapons have no built-in Critical.
- At the minimum-damage floor, the model may apply a status that native gun damage skips. Treat near-floor status results as approximate.
- Native crowd-cap binary-search granularity and delayed hit processing are approximated by limiting final HP loss. Shot queues and enemy behavior remain a model, not native-game execution.
