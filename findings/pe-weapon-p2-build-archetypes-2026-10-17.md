# Weapon balance phase 2 — C. Build archetypes (2026-10-17)

Each stress weapon (Day 5 boosters, 1 Mod Permit slot) with: original (built-ins only), optimized,
optimized without Commands, without Quickdraw, and seven archetypes (preferred effects truncated
to the gun's free slots). CURRENT rules, 200 fights a cell, all eight encounters.
Regret = geo-mean clear time vs the same weapon's optimized build. Close-combat archetype played
with `close_in` (350 units, close risk +25%); defensive with Attack Down armor.

| Archetype (effects) | P90 | MAG | DE50AE7 | M10B | M500 | HK40 |
|---|---|---|---|---|---|---|
| optimized | 2Cmd+RoF3+QD+Frost (0%) | 2Cmd+QD+AttackAll (0%) | 2Cmd+QD+Burst+Crit+Heat (0%) | 2Cmd+QD+Random (0%) | 2Cmd+QD+Frost+Crit+Acid (0%) | 2Cmd+AttackAll+QD+Frost+Crit (0%) |
| no Commands | +72% | +194% | +53% | +13% | +73% | +68% |
| no Quickdraw | +43% | +195% | +43% | +23% | +29% | +51% |
| burst (2Cmd, Crit, QD, Frost) | +52% | +70% | **+9%** | **-13%** | **+5%** | +32% |
| critical (Crit, Frost, Heat, QD) | +85% | +440% | +95% | +49% | +97% | +156% |
| status (Acid, Tranq, Burst, AttackAll) | +203% | +439% | +199% | +92% | +170% | +225% |
| sustained (RoF7, Acid, AttackAll, Frost) | +139% | +432% | +292% | +99% | +170% | +283% |
| close (Burst, Crit, Tranq, QD) | +183% | +667% | +210% | +104% | +204% | +256% |
| efficient (Frost only) | +177% | +450% | +190% | +71% | +172% | +265% |
| defensive (Tranq, QD, Counter + Attack Down) | +124% | +310% | +165% | +54% | +161% | +236% |

(M10B "burst" beats its greedy optimum: the greedy pick of Random Fire wastes bullets on helpers
in the scripted fight; 2Cmd + Critical + Quickdraw is the better M10B build.)

## What this shows

1. **Every viable archetype contains 2 Commands + Quickdraw.** Archetypes without them are
   +50% to +670% slower than the same gun's best build. The "burst" archetype is the only real
   alternative and it is the same core with a different third slot.
2. **Status, sustained-fire, close-combat and defensive archetypes reduce damage taken per
   second but lose more to the longer fight.** In this model (enemy pressure is time-based) they
   are dominated; their niche would be fights that can't be shortened (scripted timers,
   escorts), which the benchmark doesn't contain.
3. **The M10B depends least on Commands** (+13% without): its 7 rounds can't feed two volleys.
   That is the shotgun's structural problem (see report D), not its damage.
4. **Pareto view** (mixed time, damage taken, rounds used, mods used): the optimized builds plus
   "original", "efficient" and "defensive" survive for most guns only because they use fewer
   mods / rounds; none survives on time and damage taken together. So the alternatives are
   cheaper, not competitive.

## Implication

Build diversity today is diversity of the **third to fifth slot** around a fixed core. Breaking
that would need either a cost on Commands (analysis: +50% ATB per extra command compresses the
weapon spread from 2.6-5.8x to 1.6-3.6x but slows every build) or archetypes with a payoff that
time-based pressure doesn't erase. Neither is recommended without play data (see proposal).
