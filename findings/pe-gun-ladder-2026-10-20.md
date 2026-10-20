# Gun ladder (rebalanced rules, typical investment), October 20, 2026

Question (user): do the lesser / progression guns need updates so guns around them are close enough?
The rebalance (R-A..R-E) only benchmarked one representative gun per class per stage. This runs every
gun the player can hold at each stage. Recommendation and candidate check at the end
(**R-F, awaiting the user's decision; nothing built**).

Reading the tables: x median below 1 = faster than the typical gun at that stage. "Found" is the
earliest pickup (economy GEAR_LOCATIONS; Wayne's crafts from Day 5). The D5 stage uses the museum-era
pool, so guns labelled Disc2 (Museum, Warehouse, Chinatown, Subway) appear there. Disc2 investment is high,
so base attack matters less there and all guns bunch together. Base attack is shown before bonuses (the
G3A3 has R-B's +45 and the M203 4 has R-C's +15 in every run). D2-4 has no boss samples.

Every gun the player can hold at each stage, same investment (`compare_rules` INVEST typical; Disc2 with
2 Commands + Quickdraw), calibrated model, 4 seeds x 4 fights. Ordinary = mean fight time of ordinary
battles; x median = the gun against the stage median. Produced by `run_gun_ladder`.

## D2-4 (median 27.6 s)

| Gun | Kind | Found | Base atk / range / bullets | Ordinary s | x median | Boss s | Boss wins |
|---|---|---|---|---:|---:|---:|---:|
| MINI UZ | machine | D2-4 (Hospital) | 48/45/19 | 18.3 | 0.66 | - | - |
| M10 | machine | D2-4 (Hospital) | 37/45/22 | 21.2 | 0.77 | - | - |
| G23 | handgun | D2-4 (Hospital) | 47/58/10 | 21.9 | 0.80 | - | - |
| MP5K | machine | D2-4 (NYPD 17th Precinct) | 35/43/23 | 23.3 | 0.84 | - | - |
| MICRO UZ | machine | D2-4 (Hospital) | 38/43/18 | 23.7 | 0.86 | - | - |
| M11 | machine | D2-4 (Soho) | 32/42/20 | 24.5 | 0.89 | - | - |
| G3A3 | rifle | D2-4 (Hospital) | 43/121/18 | 24.8 | 0.90 | - | - |
| M9 2 | handgun | D2-4 (NYPD 17th Precinct) | 38/54/10 | 25.3 | 0.92 | - | - |
| M79 | grenade | D2-4 (Hospital) | 44/65/4 | 27.2 | 0.99 | - | - |
| G19 | handgun | D2-4 (Soho) | 30/57/8 | 27.9 | 1.01 | - | - |
| M92F | handgun | D2-4 (NYPD 17th Precinct) | 28/50/8 | 29.4 | 1.07 | - | - |
| SG550 | rifle | D2-4 (NYPD 17th Precinct) | 40/108/20 | 30.7 | 1.11 | - | - |
| P220 | handgun | D1 (Carnegie Hall) | 14/55/5 | 34.8 | 1.26 | - | - |
| M16A1 | rifle | D2-4 (NYPD 17th Precinct) | 34/110/15 | 34.9 | 1.27 | - | - |
| M203 | grenade | D2-4 (Central Park) | 25/59/5 | 35.3 | 1.28 | - | - |
| M9 | handgun | D2-4 (Central Park) | 17/53/8 | 36.1 | 1.31 | - | - |
| M1911A1 | handgun | D1 (Carnegie Hall Sewer) | 15/60/5 | 36.2 | 1.31 | - | - |
| P8 | handgun | D2-4 (Central Park) | 18/54/7 | 36.6 | 1.33 | - | - |

## D5 (median 33.7 s)

| Gun | Kind | Found | Base atk / range / bullets | Ordinary s | x median | Boss s | Boss wins |
|---|---|---|---|---:|---:|---:|---:|
| P90 | machine | D5 (Wayne) | 122/51/200 | 17.5 | 0.52 | 19.1 | 1.00 |
| DE50AE7 | handgun | D5 (Wayne) | 123/55/15 | 21.5 | 0.64 | 32.8 | 1.00 |
| M8000 | handgun | Disc2 (Museum) | 57/58/12 | 21.8 | 0.65 | 34.4 | 1.00 |
| M10B | shotgun | D5 (Wayne) | 120/70/6 | 22.3 | 0.66 | 37.1 | 1.00 |
| USP TU | handgun | D5 (Wayne) | 115/87/25 | 23.2 | 0.69 | 30.0 | 1.00 |
| HK40 | grenade | D5 (Wayne) | 115/70/8 | 25.4 | 0.75 | 47.8 | 1.00 |
| M9 3 | handgun | Disc2 (Museum) | 53/58/13 | 26.6 | 0.79 | 34.1 | 1.00 |
| MAG | rifle | D5 (Wayne) | 151/185/20 | 26.9 | 0.80 | 39.7 | 1.00 |
| G3A3 | rifle | D2-4 (Hospital) | 43/121/18 | 27.1 | 0.80 | 56.7 | 1.00 |
| MP5PDW | machine | Disc2 (Museum) | 52/46/23 | 28.0 | 0.83 | 34.6 | 1.00 |
| PPK | handgun | Disc2 (Warehouse) | 45/48/12 | 28.3 | 0.84 | 40.3 | 1.00 |
| M500 | shotgun | Disc2 (Museum) | 57/61/5 | 28.5 | 0.84 | 44.3 | 1.00 |
| G22 | handgun | Disc2 (Museum) | 49/60/10 | 29.4 | 0.87 | 42.1 | 1.00 |
| M203 4 | grenade | Disc2 (Museum) | 57/67/7 | 29.8 | 0.88 | 49.1 | 1.00 |
| M1911A2 | handgun | Disc2 (Chinatown) | 48/61/8 | 31.7 | 0.94 | 42.0 | 1.00 |
| G23 | handgun | D2-4 (Hospital) | 47/58/10 | 31.7 | 0.94 | 42.1 | 1.00 |
| P220 2 | handgun | Disc2 (Museum) | 47/55/11 | 31.8 | 0.94 | 42.1 | 1.00 |
| MINI UZ | machine | D2-4 (Hospital) | 48/45/19 | 32.1 | 0.95 | 36.9 | 1.00 |
| MP5K | machine | D2-4 (NYPD 17th Precinct) | 35/43/23 | 33.5 | 1.00 | 43.1 | 1.00 |
| M10 | machine | D2-4 (Hospital) | 37/45/22 | 33.8 | 1.00 | 38.6 | 1.00 |
| AT4 | rocket | Disc2 (Warehouse) | 128/202/1 | 35.4 | 1.05 | 43.0 | 1.00 |
| MICRO UZ | machine | D2-4 (Hospital) | 38/43/18 | 35.4 | 1.05 | 41.1 | 1.00 |
| M79 3 | grenade | Disc2 (Subway) | 52/68/5 | 37.4 | 1.11 | 54.6 | 1.00 |
| M203 2 | grenade | Disc2 (Warehouse) | 48/65/6 | 37.6 | 1.12 | 52.7 | 1.00 |
| M11 | machine | D2-4 (Soho) | 32/42/20 | 38.6 | 1.15 | 44.5 | 1.00 |
| M9 2 | handgun | D2-4 (NYPD 17th Precinct) | 38/54/10 | 39.3 | 1.17 | 50.4 | 1.00 |
| M92F | handgun | D2-4 (NYPD 17th Precinct) | 28/50/8 | 41.9 | 1.24 | 51.8 | 1.00 |
| G19 | handgun | D2-4 (Soho) | 30/57/8 | 42.2 | 1.25 | 51.8 | 1.00 |
| M203 3 | grenade | Disc2 (Chinatown Sewer) | 49/71/5 | 42.4 | 1.26 | 55.6 | 1.00 |
| M79 | grenade | D2-4 (Hospital) | 44/65/4 | 42.7 | 1.27 | 57.8 | 1.00 |
| M79 2 | grenade | Disc2 (Chinatown) | 45/68/4 | 42.8 | 1.27 | 57.3 | 1.00 |
| SG550 | rifle | D2-4 (NYPD 17th Precinct) | 40/108/20 | 46.3 | 1.37 | 60.8 | 1.00 |
| M16A1 | rifle | D2-4 (NYPD 17th Precinct) | 34/110/15 | 46.4 | 1.38 | 65.4 | 1.00 |
| M1911A1 | handgun | D1 (Carnegie Hall Sewer) | 15/60/5 | 51.9 | 1.54 | 64.6 | 1.00 |
| P220 | handgun | D1 (Carnegie Hall) | 14/55/5 | 52.1 | 1.55 | 64.9 | 1.00 |
| M9 | handgun | D2-4 (Central Park) | 17/53/8 | 52.4 | 1.56 | 64.5 | 1.00 |
| P8 | handgun | D2-4 (Central Park) | 18/54/7 | 53.3 | 1.58 | 81.1 | 1.00 |
| M203 | grenade | D2-4 (Central Park) | 25/59/5 | 58.9 | 1.75 | 72.5 | 1.00 |

## Disc2 (median 14.8 s)

| Gun | Kind | Found | Base atk / range / bullets | Ordinary s | x median | Boss s | Boss wins |
|---|---|---|---|---:|---:|---:|---:|
| P90 | machine | D5 (Wayne) | 122/51/200 | 6.4 | 0.44 | 20.4 | 1.00 |
| MP5PDW | machine | Disc2 (Museum) | 52/46/23 | 8.7 | 0.59 | 28.5 | 1.00 |
| MINI UZ | machine | D2-4 (Hospital) | 48/45/19 | 9.0 | 0.61 | 30.7 | 1.00 |
| M10 | machine | D2-4 (Hospital) | 37/45/22 | 10.0 | 0.68 | 36.9 | 1.00 |
| M500 | shotgun | Disc2 (Museum) | 57/61/5 | 10.3 | 0.69 | 78.7 | 1.00 |
| MICRO UZ | machine | D2-4 (Hospital) | 38/43/18 | 10.5 | 0.71 | 31.7 | 1.00 |
| AT4 | rocket | Disc2 (Warehouse) | 128/202/1 | 10.5 | 0.71 | 79.3 | 1.00 |
| M10B | shotgun | D5 (Wayne) | 120/70/6 | 10.7 | 0.72 | 49.8 | 1.00 |
| M11 | machine | D2-4 (Soho) | 32/42/20 | 11.2 | 0.76 | 38.6 | 1.00 |
| DE50AE7 | handgun | D5 (Wayne) | 123/55/15 | 11.7 | 0.79 | 25.6 | 1.00 |
| MP5K | machine | D2-4 (NYPD 17th Precinct) | 35/43/23 | 11.9 | 0.81 | 48.3 | 1.00 |
| USP TU | handgun | D5 (Wayne) | 115/87/25 | 13.5 | 0.91 | 40.6 | 1.00 |
| G22 | handgun | Disc2 (Museum) | 49/60/10 | 13.5 | 0.92 | 46.9 | 1.00 |
| M1911A2 | handgun | Disc2 (Chinatown) | 48/61/8 | 13.5 | 0.92 | 53.3 | 1.00 |
| G23 | handgun | D2-4 (Hospital) | 47/58/10 | 13.5 | 0.92 | 53.3 | 1.00 |
| P220 2 | handgun | Disc2 (Museum) | 47/55/11 | 13.6 | 0.92 | 51.9 | 1.00 |
| M9 3 | handgun | Disc2 (Museum) | 53/58/13 | 13.6 | 0.92 | 51.7 | 1.00 |
| M8000 | handgun | Disc2 (Museum) | 57/58/12 | 14.0 | 0.95 | 57.5 | 1.00 |
| HK40 | grenade | D5 (Wayne) | 115/70/8 | 14.6 | 0.99 | 43.9 | 1.00 |
| M9 2 | handgun | D2-4 (NYPD 17th Precinct) | 38/54/10 | 14.9 | 1.01 | 64.0 | 1.00 |
| G19 | handgun | D2-4 (Soho) | 30/57/8 | 15.3 | 1.04 | 70.8 | 1.00 |
| MAG | rifle | D5 (Wayne) | 151/185/20 | 15.4 | 1.04 | 29.1 | 1.00 |
| M92F | handgun | D2-4 (NYPD 17th Precinct) | 28/50/8 | 15.4 | 1.05 | 71.8 | 1.00 |
| M203 4 | grenade | Disc2 (Museum) | 57/67/7 | 16.0 | 1.08 | 55.3 | 1.00 |
| M1911A1 | handgun | D1 (Carnegie Hall Sewer) | 15/60/5 | 16.2 | 1.10 | 87.3 | 1.00 |
| M79 3 | grenade | Disc2 (Subway) | 52/68/5 | 16.2 | 1.10 | 71.3 | 1.00 |
| M9 | handgun | D2-4 (Central Park) | 17/53/8 | 16.3 | 1.10 | 88.7 | 1.00 |
| G3A3 | rifle | D2-4 (Hospital) | 43/121/18 | 16.4 | 1.11 | 51.2 | 1.00 |
| P220 | handgun | D1 (Carnegie Hall) | 14/55/5 | 16.8 | 1.14 | 81.6 | 1.00 |
| PPK | handgun | Disc2 (Warehouse) | 45/48/12 | 17.4 | 1.18 | 71.3 | 1.00 |
| M79 | grenade | D2-4 (Hospital) | 44/65/4 | 17.6 | 1.19 | 91.3 | 1.00 |
| P8 | handgun | D2-4 (Central Park) | 18/54/7 | 17.9 | 1.21 | 101.3 | 1.00 |
| SG550 | rifle | D2-4 (NYPD 17th Precinct) | 40/108/20 | 17.9 | 1.21 | 86.7 | 1.00 |
| M203 2 | grenade | Disc2 (Warehouse) | 48/65/6 | 19.3 | 1.31 | 73.4 | 1.00 |
| M203 3 | grenade | Disc2 (Chinatown Sewer) | 49/71/5 | 19.6 | 1.33 | 92.9 | 1.00 |
| M79 2 | grenade | Disc2 (Chinatown) | 45/68/4 | 19.7 | 1.33 | 100.1 | 1.00 |
| M203 | grenade | D2-4 (Central Park) | 25/59/5 | 20.8 | 1.41 | 103.9 | 1.00 |
| M16A1 | rifle | D2-4 (NYPD 17th Precinct) | 34/110/15 | 21.3 | 1.45 | 94.6 | 1.00 |

## Findings

- **Rifles before the G3A3 are duds.** M16A1 (NYPD) is the slowest gun of its stage at every stage
  (1.27 / 1.38 / 1.45 x median); SG550 1.11 / 1.37 / 1.21. Even with a Day-2-4 attack investment they lose to
  the starting handgun tier.
- **The grenade line between M79 and HK40 barely moves.** M203 (Central Park) 1.28 on D2-4 vs M79 0.99;
  the museum-era M203 2 / M203 3 / M79 2 (1.12 / 1.26 / 1.27 on D5) are no better than the Day-2-4 M79
  (1.27), so picking them up is not progress. M79 3 is 1.11. (M203 4 with R-C is 0.88.)
- **PPK (Warehouse)** is fine at D5 (0.84) but the weakest museum-era handgun on Disc2 (1.18, range 48).
- **Handguns are a healthy ladder.** Day 1 (P220, M1911A1) and Central Park (M9, P8) guns are about
  1.3 on D2-4, and G19 / M92F / M9 2 / G23 overtake them in order (1.01 down to 0.80). Museum handguns
  (M9 3, M8000, G22, M1911A2, P220 2) sit at 0.65-0.94 at D5 and bunch at 0.92-0.95 on Disc2. No change.
- **Machine guns lead every stage** (MINI UZ 0.66 on D2-4, P90 0.44 on Disc2). That's the vanilla identity
  (spray, poor range), and boss times are ordinary. No nerf proposed.
- **Wayne's guns top D5** (P90, DE50AE7, M10B, USP TU 0.52-0.69) as intended. MAG 0.80 / 1.04 is a boss gun
  (Disc2 boss 29.1 s, second only to the P90).

## R-F proposal: progression attack bonuses (same mechanism as R-B / R-C)

Candidate set A, checked with `--extra` (4 seeds x 4 fights; x median against the full-ladder medians
above; data `findings/pe-gun-ladder-cand-A.md`):

| Gun | Bonus | D2-4 | D5 | Disc2 |
|---|---:|---|---|---|
| M16A1 | +30 (suggest **+25**) | 1.27 -> 0.93 | 1.38 -> 0.87 | 1.45 -> 1.14 |
| SG550 | +15 | 1.11 -> 0.96 | 1.37 -> 1.07 | 1.21 -> 1.14 |
| M203 | +25 (suggest **+20**) | 1.28 -> 0.92 | 1.75 -> 1.09 | 1.41 -> 1.28 |
| M203 2 | +15 | - | 1.12 -> 1.03 | 1.31 -> 1.18 |
| M203 3 | +20 | - | 1.26 -> 0.97 | 1.33 -> 1.34 (noise) |
| M79 2 | +15 (suggest **+20**) | - | 1.27 -> 1.13 | 1.33 -> 1.36 (noise) |
| M79 3 | +10 | - | 1.11 -> 1.00 | 1.10 -> 1.07 |
| PPK | +10 (optional) | - | 0.84 -> 0.75 | 1.18 -> 1.10 |

With the suggested values, each pickup beats the gun of its class you had before it, and nothing passes the
G3A3 / Wayne tier. Grenade Disc2 times stay above the median (grenades have the widest spread between runs, and
their value is elements and range). In the mod this would be one row, "Progression gun bonuses" (OFF
vanilla, ON rebalanced), driving a small per-item table in `pe_fx_attack_bonus` beside R-B / R-C, so the
DPS line picks it up for free.

## Rerun with Mod Catalog installs (user request, October 20, 2026)

`run_gun_ladder --catalog` (tables: `findings/pe-gun-ladder-catalog-2026-10-20.md`) gives each gun the
Catalog installs a player could really have at that stage, and keeps the gun's best loadout:

- **Unlocked effects by stage**, from 60 economy playthroughs (current rules, Normal preset, policies A / C / I,
  20 seeds each):
  - Day 2-4 / Day 5: Heat and RoF3 always, Random 85-98%, RoF5 65-68% (so an RoF3 loadout is tried too).
  - Disc 2 adds 2 Commands (100%), Quickdraw (95%) and Acid (85%).
  - Critical (15%) and Attack All (3%) are left out.
- **Slots:** the larger of the gun's own and the carried gun's typical total at the end of the stage
  (2 / 3 / 6, base + Mod Permits), capped at the gun's slot limit.
- **Install rules:** a better RoF replaces the built-in RoF in its slot; built-in Burst / Attack All / Commands
  are never replaced; installed RoF gets R-E's fast volleys.

What changed (x median, before -> with installs):

- **Museum-era grenades are fixed by installs:** M79 3 1.11 -> 0.83, M203 3 1.26 -> 0.86, M79 2 1.27 -> 0.93 on D5.
  Their buffs are dropped.
- **PPK** is fine where it's found (D5 0.91); its Disc2 lag is shared by every pre-Wayne gun. Buff dropped.
- **Still duds where they're found:** M16A1 (D2-4 1.25, D5 1.22), SG550 (1.18, 1.08), M203 (1.26, 1.46) and
  M203 2 (D5 1.16).

Candidate check with installs (`--extra`, data `findings/pe-gun-ladder-catalog-cand-B.md`; x median against the
catalog-ladder medians):

| Gun | Bonus | D2-4 | D5 | Disc2 |
|---|---:|---|---|---|
| M16A1 | +25 | 1.25 -> 1.08 | 1.22 -> 0.95 | 1.58 -> 1.38 |
| SG550 | +15 (suggest **+20**) | 1.18 -> 1.12 | 1.08 -> 0.98 | 1.47 -> 1.39 |
| M203 | +20 | 1.26 -> 1.01 | 1.46 -> 1.17 | 1.70 -> 1.52 |
| M203 2 | +15 | - | 1.16 -> 0.99 | 1.26 -> 1.21 |

**Revised R-F: M16A1 +25, SG550 +20, M203 +20, M203 2 +15.** Day 3 guns still trail on Disc 2, which is
expected (Wayne and museum guns replace them).

Separate observation (not progression): on Disc 2, ordinary fights favour fast guns with 2 Commands (machine
guns, handguns). Rifles and grenade launchers sit at 1.2-1.3 even for the G3A3 / MAG / M203 4, but rifles
lead on bosses (MAG 25.6 s, G3A3 42.7 s vs handguns 30-48 s). No change proposed.
