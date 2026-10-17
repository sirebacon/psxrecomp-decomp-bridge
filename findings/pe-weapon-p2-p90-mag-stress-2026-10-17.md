# Weapon balance phase 2 — E. P90 and MAG stress tests (2026-10-17)

Reference weapons: P90, MAG, DE50AE7, M10B, M500, HK40 at Day 5 (+1 Mod Permit). CURRENT rules.
Mixed time = geometric mean of clear times over seven encounters (6 s window excluded).

## Where each stands (current rules)

| Weapon | Optimized build | Mixed time | x best | close / groups / keep-away / stat. boss (s) |
|---|---|---|---|---|
| MAG | 2Cmd + Quickdraw + Attack All | 1.08 s | 1.00 | 0.3 / 0.3 / 8.1 / 7.0 |
| P90 | 2Cmd + RoF3 + Quickdraw + Frost | 2.83 | 2.61 | 0.9 / 1.4 / 14.2 / 7.8 |
| HK40 | 2Cmd + Quickdraw + Attack All + Frost + Critical | 3.29 | 3.04 | 0.9 / 1.5 / 19.4 / 12.8 |
| DE50AE7 | 2Cmd + Quickdraw + Frost + Random + Critical | 3.77 | 3.49 | 1.1 / 1.7 / 14.5 / 8.5 |
| M10B | 2Cmd + Quickdraw + Random | 5.97 | 5.52 | 1.9 / 4.2 / 19.1 / 12.2 |
| M500 | 2Cmd + Quickdraw + Frost + Critical + Acid | 6.31 | 5.84 | 2.1 / 3.3 / 34.0 / 21.6 |

## Is the P90 too strong?

No. It is the best non-MAG weapon in groups and close fights and has no ammo problem (200 rounds),
but it is ~2x slower than the MAG in keep-away fights and doesn't dominate stationary bosses
(7.8 s vs DE50AE7 8.5, MAG 7.0). Its RoF 10 is not its best mode (RoF 3 is) at the assumed
per-bullet time; with a faster per-bullet time RoF 7 would edge ahead (measure first).
**No phase 2 experiment strengthened it** (all shotgun / handgun rules: 0%; machine-gun
suppression M1: +1%, i.e. nothing; magazine rules: 0% because of its 200 rounds).
It is appropriately specialised: sustained fire, crowds, no reloads.

## Is the MAG too strong?

It is the strongest weapon in every encounter, so this is more than specialisation:

| Source of the MAG's lead | How much (analysis experiments) |
|---|---|
| Range-relative crit zone (50% crits within 1020 units) + built-in Critical | capping the zone at 600 units: MAG 9% slower |
| Attack All repeated on every command | Attack All on the first command only: MAG 9% slower |
| Commands in general | extra commands +50% ATB: MAG 122% slower (1.1 -> 2.4 s), everyone slower |
| Raw stats: attack 151 (P90 122, DE50AE7 123), range 185, 21 rounds, Quickdraw one-turn kills | the remainder |

Its lead is mostly the platform. But the MAG is one of five Wayne guns and the player gets one;
the useful question is whether the other Wayne guns have a reason to exist. With the shotgun
package (report D) the M10B gets one (close stationary bosses); the DE50AE7's 8 slots make it
the most customizable; the P90 has crowds and endurance; the HK40 trails.

## Anti-runaway check (every experiment)

| Experiment | P90 | MAG | Gap best-other vs P90/MAG |
|---|---|---|---|
| C1 / C1s proximity (all sizes) | 0% | 0% | unchanged |
| C2 magazine (M10B, all shotguns) | 0% | 0% | unchanged |
| C4 recovery, C5 stagger | 0% | 0% | unchanged |
| H1 handgun recovery | 0% | 0% | DE50AE7 -5% |
| M1 machine-gun suppression | +1% | 0% | unchanged; not worth it, stacks with Tranq refresh |
| E3 boss-only graze | -2% | -1% | -3 points |
| R1 smart reload | 0% | -1% | unchanged |
| "+50% magazine with RoF 7/10" | 0% | helps MAG RoF 7/10 builds | MAG still prefers RoF 2 + Attack All |

None of the proposed shotgun / handgun rules widens the gap; none makes a new dominant weapon.

## Recommendation

Leave the P90 and the MAG as they are. If the MAG's universality bothers players in practice,
the narrowest lever found is its built-in Critical / crit zone (-9%), not its damage; it is not
recommended without play data.
