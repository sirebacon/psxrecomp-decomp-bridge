# Parasite Eve: effects and build diversity (2026-10-17)

Phase 5. Each effect added alone to each class's Day 5 gun (built-ins kept, Day 5 boosters), mean
change in clear time over close / groups / keep-away / stationary boss / endurance; [ ] = change in
damage taken. Negative = better. 150 fights per cell, common random numbers. Simulator results.

| Effect | Vanilla (range over the 5 classes) | Current | Verdict |
|---|---|---|---|
| Heat | **+12..+86% slower** [+13..+82%] | -3..-9% | Vanilla trap confirmed (Day 5 enemies resist Heat); fixed |
| Frost | 0..-6% | **-14..-18%** | Now the best single damage effect; keep an eye on it |
| Acid | -4..-10% | -7..-16% | Useful, strongest on many-bullet guns |
| Tranquilizer | 0% time, -2..-6% taken | 0% time, **-11..-36% taken** | Became a real defensive pick (stops enemies) |
| Cyanide (EX only) | -7..-12% | -6..-12% | Premium price is right; not dominant in fights with bosses |
| Critical | -7% | -10..-12% | Fine |
| Quickdraw | -4..-8% | -5..-11% | Fine; in almost every top build because it is cheap |
| Counter | -7..-15% | same (no boost) | Vanilla Counter is already decent at level 24+ (chance 6-33% by rank); no boost needed |
| Burst | -4..-15% (groups) | same | Fine; cone share assumed |
| Attack All | rifle -25%, others -2..+4% | same | Good on high-power, big-magazine guns; ammo-hungry |
| Random Fire | -22..+2% (more damage taken: wasted bullets) | same | Mixed; bad in fights with helpers |
| RoF 3 / 5 (rifle) | -27% | -27% | Good on rifles (power high, magazine 18+) |
| RoF 5-10 on handgun / grenade / shotgun | **+19..+159% slower** | +19..+106% | **Trap: magazine 5-13 runs dry, bullets click, reload every turn** |
| RoF 7 / 10 on rifle | -15 / -6% | -30 / -27% | The mod's 20 / 15% made them worthwhile on rifles |
| 2 Commands | -12..-47% | same | **The core of every top build** |
| 3 Commands (EX) | -7..-63% | same | Even more so |

## Combinations

- Top builds of every class at every stage contain **2 Commands + Quickdraw**, then whatever the
  remaining slots allow (Frost / Critical / Burst / Attack All). Commands and Quickdraw both act on
  turn count, so they stack with everything.
- **High RoF + status:** more bullets mean more status rolls, but only landed bullets with damage
  > 0 roll; on small magazines the clicks cancel it out.
- **Attack All + Commands:** strong on the MAG (21 rounds); on small magazines it empties them.
- **Attack All / Random + Acid:** applies poison to many targets; worthwhile in groups.
- **Burst + shotgun:** shotguns already carry Burst; adding more bullets runs into the 5-8 round magazines.
- **Critical + rifles:** no special synergy (crit is per bullet, rifles fire few).
- **Heat + Frost:** best-of-two under current rules makes the pair strictly better than either.
- **Defensive armor + long fights:** Attack Down (-25% damage taken) and Slow AT (-15%) now pay off
  in long fights; not part of the weapon ranking.

## Is anything dominant because of a mechanic or because of the simulator?

- **2 / 3 Commands:** a mechanic (two or three full volleys per ATB bar, `Battle_StepEnemyTurn`
  queues a slot per command). Not a simulator artifact.
- **High-RoF trap:** a mechanic (each bullet 1 round, clicks when empty). Its size depends on the
  assumed per-bullet animation time, but it holds at half and double that time.
- **Frost after the rebalance:** partly from the neutral bonus (115%) applying to every enemy
  without a Frost match; the size depends on the area's resistances (wiki data).
- **Tranq's defensive value:** depends on the assumed enemy attack rhythm; direction is robust.

## Diversity verdict

- Mid-game (Day 3-4) several builds of different classes are within ~15-30% of each other in
  normal fights; the spread comes from slots and the stage's guns.
- Late game converges on **Wayne gun + 2 Commands + Quickdraw**, and on the **MAG** in particular.
- No effect is a trap any more except **high RoF on small magazines**, which the rebalance made
  less bad (+19..+106% instead of +19..+159%) but did not remove.
