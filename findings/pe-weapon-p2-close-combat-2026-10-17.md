# Weapon balance phase 2 — D. Close-combat experiments (2026-10-17)

Builds fixed at each weapon's current optimum so only the rule changes. Shotguns played both
`stand` and `close_in` (walk to 350 units, enemies next to Aya hit 25% more often). Proximity uses
**absolute** distance (not % of range), so range upgrades don't widen the zone.
Geo-mean clear-time change vs E0 over all eight encounters. 200 fights a cell.

## Critical distance first

The game's 50%-crit zone is half the gun's own range: within **1020 units** for the MAG, 546-627
for the P90 / DE50AE7 / shotguns / HK40. With built-in Critical the MAG crits 72% of its bullets
in ordinary close fights; the others 26-33%. A shotgun must stand within ~600 units to get what
the MAG gets at 1000. Capping the zone at 600 units (analysis only) slows the MAG 9%: real, but a
small part of its lead. Keep the mechanic.

## Results (shotguns; P90 / MAG / DE50AE7 / HK40 unchanged by every C experiment: 0%)

| Exp | Change | M10B stand | M10B close-in | M500 stand | M500 close-in | M10B close / stat.boss / keep-away (s, close-in) |
|---|---|---|---|---|---|---|
| C0 | none | 0% | 0% | 0% | 0% | 2.9 / 15.2 / 28.2 |
| C1 +15% | within 400 | -3% | -9% | -4% | -9% | 2.8 / 12.6 / 24.8 |
| C1 +25% | | -6% | -13% | -6% | -14% | 2.8 / 12.3 / 23.5 |
| C1 +30% | | -7% | -15% | -7% | -16% | 2.7 / 11.9 / 22.9 |
| C1 +40% | | -9% | -20% | -10% | -22% | 2.6 / 10.1 / 21.1 |
| C1 +50% | | -11% | -24% | -11% | -27% | 2.6 / 9.5 / 20.0 |
| C1s +25% | 400, fading to 650 | -9% | -14% | -8% | -14% | 2.7 / 12.3 / 23.4 |
| **C1s +40%** | 400, fading to 650 | -12% | -21% | -13% | -23% | 2.6 / 10.1 / 21.0 |
| C1s +50% | | -14% | -25% | -15% | -28% | 2.5 / 9.5 / 19.9 |
| C2 +25% magazine (M10B 7 -> 8) | | -7% | -11% | 0% | 0% | 2.7 / 12.8 / 23.6 |
| C2 +50% (7 -> 10) | | **+2%** | **+7%** | 0% | 0% | 3.1 / 16.1 / 32.2 |
| C2 +75% (7 -> 12) | | -9% | -5% | 0% | 0% | 2.7 / 14.9 / 28.1 |
| C2 +100% (7 -> 14) | | -18% | -14% | 0% | 0% | 2.5 / 13.0 / 25.1 |
| C2 all shotguns +50% | | +2% | +7% | -3% | -5% | |
| C4 recovery -25% / -50% | | -3 / -7% | -2 / -4% | -2 / -4% | -2 / -4% | 2.9 / 14.9 / 27.4 |
| C5 stagger (35% / volley, 0.8 s, 3 s cooldown, bosses x0.3) | | 0% | 0% | 0% | -2% | 2.9 / 15.2 / 27.1 |
| R1 smart reload | | -4% | -2% | -3% | +4% | |
| **C1s +40% + C2 M10B +25%** | | **-19%** | **-26%** | -12% | -22% | **2.3 / 9.7 / 18.1** |
| C1s +40% + C2 +25% + R1 | | -22% | -29% | -15% | -19% | 2.3 / 9.7 / 18.1 |
| C1s +40% + C2 +50% | | -10% | -17% | -13% | -23% | 2.5 / 10.7 / 23.6 |
| C1s +40% + C2 +50% + C4 -25% | | -12% | -18% | -15% | -24% | 2.5 / 10.4 / 23.2 |

Reference (current optimum, close-in not used): P90 0.9 / 7.8 / 14.2, MAG 0.3 / 7.0 / 8.1,
DE50AE7 1.1 / 8.5 / 14.5 (close / stationary boss / keep-away, s).

## Reading

- **Magazine is about alignment, not size.** The M10B fires 8 bullets a turn with 2 Commands +
  Random (6 with 2 Commands alone). The game reloads only when empty, so 8 rounds fits, 10
  leaves a 2-bullet turn and is worse than 7. Any magazine change must be checked against the
  shotgun's real volley sizes.
- **Proximity damage is the clean lever:** it only touches shotguns, more when the player
  actually closes in (the intended play), and nothing else moves. A fade (400 -> 650) works as
  well as a hard edge and is kinder to the player.
- **Recovery and stagger are not worth implementing:** small effects (stagger only reduces damage
  taken, which time-based pressure dwarfs).
- **Best package: C1s +40% + M10B magazine 7 -> 8.** M10B close-in 26% faster; at a stationary close
  boss 9.7 s vs P90 7.8, DE50AE7 8.5, MAG 7.0: a shotgun becomes a reasonable pick against nearby
  high-HP enemies without beating the P90 or MAG anywhere.
- **No runaway:** the package changes no other weapon; the best shotgun remains slower than the
  P90 and MAG in every encounter. Midgame M500 gains 12-22% (it already leads Day 5 non-Wayne
  shotguns; check Day 3-4 shotgun play before shipping).

## Open questions before building

1. How often can a player keep a target within 400-650 units? Log absolute distance per bullet
   (hitq has bands only) in a few shotgun fights.
2. Does the danger of standing close (enemy attacks, contact damage) cost more than +25%
   hit chance? Hurt rows with distance would tell.
