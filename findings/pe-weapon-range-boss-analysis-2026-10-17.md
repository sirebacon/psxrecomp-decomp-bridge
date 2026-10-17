# Parasite Eve: range and keep-away bosses (2026-10-17)

Phase 6. Follows [pe-range-keepaway-bosses-2026-10-15.md](pe-range-keepaway-bosses-2026-10-15.md)
(options 1-4) with the corrected simulator. Realistic Day 5 loadouts chosen under CURRENT rules so
only the rule changes between experiments. 300 fights a cell. Simulator results.

## 1. What the data says about distance

| Context | Mean distance | MG 45 in range | Handgun 55 | Rifle 110 | Rifle 158 |
|---|---|---|---|---|---|
| normal fights | 703 units | 77% | 83% | 93% | 95% |
| bosses | 934 | 65% | 73% | 87% | 90% |
| keep-away (room 156) | 1188 | **40%** | **52%** | **80%** | 93% |

(range in game units = 150 x sqrt(stat): MG 1006, handgun 1112, rifle 1573 / 1885; distance
profiles from hitq + reach rows.) Range is the deciding stat only in keep-away fights.

## 2. Experiments (policy "stand": Aya never steps into range)

Mean clear time vs E0 (current rules unchanged):

| Exp | Change | Keep-away boss | Day 5 scripted boss | Normal fights | Rifle |
|---|---|---|---|---|---|
| E1 | graze 30 -> 50% everywhere | -5..-12% (MG most) | -5..-10% | -1..-4% | -1..-2% |
| E2 | graze 50% for short-range classes | same as E1 | same | -1..-4% | 0% |
| E3 | graze 50% vs bosses only | -5..-12% | -5..-10% | **0%** | -2% |
| E4 | wider strong-graze band (to 130%) | -1% | -1..-2% | 0% | 0% |
| E5 | shotgun / rifle / grenade recover 25% faster | -0..-4% | -1..-4% | -1..-3% | -0..-4% |
| E6 | Day 5 scripted boss: 30% less real HP to deal | 0% | **-19..-35%** | 0% | -35% |
| E3+E6 | both | -5..-12% | **-32..-36%** | 0% | |

Class spread in the keep-away fight (slowest / fastest class): E0 2.24 -> E1 2.08 -> E1+E4 2.06.
No graze rule closes the gap much: the short-range classes lose most of their time to bullets that
**miss outright** beyond 150% of range, not to grazes.

## 3. The player's position matters more than any rule

Same loadouts, policy "approach" (Aya spends 0.6 s to step into range when her target is beyond it):

| Class | Keep-away, stand | Keep-away, approach |
|---|---|---|
| handgun (M9 3) | 62.9 s | 44.1 s (-30%) |
| machine (MP5PDW) | 76.1 s | 44.1 s (-42%) |
| grenade (M203 4) | 39.3 s | 28.7 s (-27%) |
| shotgun (M500) | 33.9 s | 22.8 s (-33%) |
| rifle (G3A3) | 57.0 s | 51.6 s (-9%) |

With approach the graze experiments do nothing (no grazes left). The logged attempts agree: the
fastest one (M9, 8 s) closed the distance and used Haste.

## 4. Recommendation

1. **E6 (high confidence for the scripted fight, medium overall):** lower the real HP threshold of
   the Day 5 boss part 1 (room 156) by ~30% (450 -> ~315). It is a scripted fight that ends on
   damage dealt, the one place where short guns were in real danger; every class gains 19-35%,
   nothing else changes. Implementation: raise the boss's placeholder HP base by the difference or
   scale damage to it in that room (needs a room/enemy check, entry hook already present on the
   damage routine).
2. **E3 (medium):** graze 50% against bosses only, as a softer general aid. Small effect (-5..-12%)
   and no effect on normal fights or on rifles' identity.
3. **Do not** widen graze bands (E4: ~0%) or change global graze (E1 changes normal fights too).
4. **Teach the mechanic:** a short in-game hint (or the F1 page) that stepping toward a boss that
   keeps away removes grazes and misses; it is the biggest lever and costs no balance.
5. Leave rifles' range advantage as is: in keep-away fights the best rifle (MAG) is ~2x faster
   than the best handgun / machine gun at Day 5 (8 s vs 16-17 s); a weak rifle platform (G3A3, no
   RoF) gains only ~10%. That is the class identity the game supports.
