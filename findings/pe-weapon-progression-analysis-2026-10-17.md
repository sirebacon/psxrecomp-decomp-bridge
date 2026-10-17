# Parasite Eve: progression and the customization economy (2026-10-17)

Phase 7. Strategies over Days 1-5 under CURRENT rules (60 fights a cell; `part_progression`).
Each day: the strategy's main gun gets twice the stage's boosters (everything invested in it,
bonuses follow by Tool as `TRANSFER_STAT` does), mods greedily from the stage's pool within its
free slots. Times = mean clear time close / groups / keep-away boss / stationary boss.

| Strategy | Day 2 | Day 3 | Day 4 | Day 5 |
|---|---|---|---|---|
| A handgun | M9 5.8 / 9.8 / 10.2 / 5.4 | G19 3.4 / 4.6 / 15.4 / 9.2 | G23 4.4 / 7.7 / 11.9 / 7.2 | DE50AE7 1.0 / 1.6 / 15.7 / 8.9 |
| A machine | (M9) | MP5K 4.4 / 7.6 / 20.0 / 8.8 | MP5K 6.0 / 10.1 / 22.1 / 9.9 | P90 1.1 / 1.6 / 15.2 / 8.4 |
| A rifle | M16A1 5.2 / 8.7 / 4.7 / 4.1 | SG550 4.0 / 5.5 / 11.2 / 9.1 | G3A3 3.3 / 6.6 / 8.0 / 5.9 | MAG 0.9 / 2.1 / 7.6 / 6.9 |
| A grenade | (G19) | (G19) | M79 5.3 / 9.1 / 12.8 / 8.3 | HK40 1.2 / 1.9 / 20.2 / 12.8 |
| B handgun + rifle | as A | 13.8 keep-away | 21.5 keep-away | 21.0 keep-away |
| B machine + rifle | as A | 13.8 keep-away | 21.5 keep-away | 21.0 keep-away |
| C best of any class | M16A1 | M11 | G23 | MAG |

(Grenade launchers start on Day 4, machine guns on Day 3: earlier days use a handgun.)

## Findings

1. **One upgraded gun of your favourite class finishes the main game.** In normal fights the
   Day 5 Wayne guns of handgun / machine gun / rifle / grenade launcher are within 0.9-1.2 s of
   each other. The cost of not picking a rifle shows in keep-away bosses (15-20 s vs 7.6 s) and
   long boss fights (8.4-12.8 s vs 6.9 s): about 2x the time and so about 2x the damage taken
   there. Shotguns: not modelled as a strategy (only from Day 5); best-in-class benchmark puts
   the M10B ~2x behind in every encounter.
2. **Two guns (B) is worse than one** in this economy: a rifle kept as a secondary without
   investment is slower in keep-away fights than the invested main gun (21 s vs 15.7 s at Day 5),
   even with the half-bar weapon switch. This is an economy problem: boosters, mods and Tools
   all flow into one gun, and a secondary gets nothing.
3. **Switching often (C) works** because transfers are lossless (all three bonuses move, the
   source keeps its item): C follows the best base gun each day and ends on the MAG.
4. Mid-game the rifle line is strong early (M16A1 Day 2: keep-away 4.7 s) and the machine guns
   are the weakest line on Days 3-4 (MP5K, M11: low power, short range, Random Fire wastes bullets).

## Customization economy status (from the mod's code)

| System | Status | Effect on weapon balance |
|---|---|---|
| Tool / Super Tool transfers | vanilla, lossless | favours one-gun play |
| Mod Permit (+1 slot, cap 2 held) | implemented (Wayne / Warner menu) | helps slot-poor guns; MAG gains most |
| Mod Catalog (install for Junk) | implemented | makes 2 Commands / Quickdraw reachable for everyone |
| Rebuild (dismantled gear, keeps bought slots) | implemented | lowers the cost of switching |
| Junk economy, rare drops cascade | implemented | sets when Commands / Permits arrive (not simulated per drop) |
| Half-bar weapon switch | implemented | cheap switching; doesn't fix the secondary's lack of investment |

## Suggestions (experimental, need the economy model and play data)

- **Make a secondary affordable rather than restricting transfers:** e.g. Tools that copy (not
  move) the *range* bonus, or a Workshop service that raises a stored gun's bonuses to a fraction
  of the main gun's. Test against strategy B before building anything.
- **Do not restrict transfers by class:** the simulation (and the 2026-10-15 run) shows transfer
  rules barely change outcomes; restrictions would only punish experimenting.
