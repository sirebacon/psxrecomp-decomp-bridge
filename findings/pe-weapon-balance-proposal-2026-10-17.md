# Parasite Eve: weapon balance proposal (2026-10-17)

Status: **proposal, nothing implemented.** Evidence: [audit](pe-weapon-simulation-audit-2026-10-17.md),
[validation table](pe-weapon-mechanics-validation-2026-10-17.md), [class benchmark](pe-weapon-class-benchmark-2026-10-17.md),
[build diversity](pe-weapon-build-diversity-2026-10-17.md), [range / bosses](pe-weapon-range-boss-analysis-2026-10-17.md),
[progression](pe-weapon-progression-analysis-2026-10-17.md). Simulator: `tools/pe_weapon_sim`
(rulesets VANILLA / CURRENT frozen, EXPERIMENTAL = CURRENT + switches E1-E6).

## Answers

1. **Are the classes unbalanced, or was it the simulations?** Both. The old simulators overstated
   the rifle's range edge (range is 150 x sqrt(stat), not linear), let status land on misses,
   miscounted Attack All ammo and halved Aya's offense. Corrected, real differences remain, but
   they come mostly from **individual guns** (slots, magazine, attack) and from **keep-away
   encounters**, not from class rules.
2. **Strongest under realistic conditions:** late game the **MAG rifle** (attack 151, range 185,
   built-in Critical, 21 rounds) with 2 Commands + Quickdraw; mid-game the **many-slot guns**
   (M500 shotgun 8 slots, M203 4 grenade 5) and modded rifles. **2 Commands** is in every top
   build of every class.
3. **Only weak against some encounters?** Yes. Handgun / machine / grenade builds are within
   ~5-15% of the best in normal fights at Day 5, but ~2x slower against keep-away and long bosses,
   and spread modes (Random Fire, Attack All) fall apart in scripted fights with invulnerable
   helpers.
4. **Did the effect rebalance fix things?** It fixed the effect traps (Heat from +12..+86% slower
   to -3..-9% faster; Tranq now cuts damage taken 11-36%; Acid, Critical, Quickdraw better). It
   did not change class balance (not its aim; spreads moved by a few points).
5. **Can a player specialise?** Handgun, machine gun, rifle, grenade launcher: yes for the main
   game; the price is ~2x longer keep-away / long boss fights. Shotgun: viable mid-game thanks to
   slots, clearly behind late (M10B ~2x slower everywhere) because 7 rounds don't feed 2 Commands.
6. **Multiple viable builds?** Mid-game yes (several classes within ~15-30%). Late game they
   converge on Wayne gun + 2 Commands + Quickdraw. One-gun play is optimal; a second gun is too
   expensive to maintain (economy, not weapon stats).
7. **Smallest changes with the biggest gain:** see R1-R4 below.
8. **Validation:** loadout logging + four targeted play tests (section "Validation plan").

## Recommendations

### R1 Day 5 scripted boss (room 156): ~30% less real damage to deal (E6) — medium-high confidence
1. Current: the fight ends after ~450 real damage (enemy HP 1,000,450 placeholder); defense 33;
   3 helpers attack the whole time.
2. Proposed: end it at ~315 (raise the placeholder base by 135 when the fight starts, or scale
   damage to that enemy id in that room; the damage-routine hook already exists).
3. Reason: the one mandatory fight where short guns were in real danger (logged 434 HP lost);
   damage taken there is proportional to time (~15 HP/s).
4. Evidence: E6 -19..-35% time for every class, no effect anywhere else; graze changes only
   -5..-12% there.
5-6. All classes; only that encounter.
7. ~25% less time and damage taken in that fight.
8. Risk: the fight gets shorter for rifles too (fine); scripted HP may be shared with part 2 (check).
9. Validate: replay room 156 with a handgun and a rifle; compare time / HP lost with the 3 logged attempts.
10. Confidence: medium-high (decomp + 3 logged attempts + sim).

### R2 Graze 50% against bosses only (E3) — medium confidence, optional
1. Current 30%. 2. 50% when the target is a boss. 3. Softens keep-away bosses without touching
normal fights. 4. -5..-12% keep-away, 0% normal fights, rifle -2%. 5-6. Short-range classes vs
bosses. 7. Small. 8. Risk: none found; may be too small to notice. 9. Same room 156 test + one
long boss. 10. Medium. **Do not** take E1 (global) or E4 (wider bands, ~0%).

### R3 Keep the effect rebalance and the vanilla Counter — high confidence
Current values verified in source; every effect is now useful somewhere (build diversity report).
Counter needs no boost: vanilla chance is L/1000..L/5000 with L = level x 10 (6-33% late).
If a boost is ever wanted, the safe lever is Aya's **rank byte** in her battle combatant
(`field04.bytes.rank`, battle-only, not saved) raised for the duration of `Battle_RollEnemySpawn`
(entry hook to set, the next frame to restore) — never `stats.levels`. Needs the rank values
mapped first (log them).

### R4 Late shotgun: bigger magazines — experimental
1. Current: M10B 7 rounds (6 + 1), shotgun ATB factor 8.
2. Proposed to test: shotguns +50% magazine (base bullets), optionally ATB factor 10.
3. Reason: 2 Commands empties a 7-round magazine almost every turn (clicks + reload).
4. Evidence: magazine x1.5 alone -25..-30% in every encounter; with ATB 10 the M10B reaches
   1.1 s / 2.2 s in close / groups (handgun DE50AE7: 1.0 / 1.8).
5. Shotguns. 6. All. 7. Shotgun from ~2x behind to ~10-30% behind late.
8. Risk: early shotguns (M870 / M500 with 8+ slots) already lead mid-game; consider applying to the
   Wayne M10B only, or scaling with the stage.
9. Validate: Day 5+ fights with M10B before / after. 10. Experimental (reload time and Burst cone assumed).

### R5 High RoF on small magazines — experimental, information first
The trap is a vanilla mechanic (bullets click when the magazine empties). Before any change,
show it: the F1 Mod Effects page or the Workshop could flag "RoF higher than magazine / commands"
on the selected gun. A mechanical fix (e.g. RoF 7 / 10 refill from the reserve mid-volley) changes
a core rule and needs its own test.

### R6 Economy for a secondary gun — experimental
Strategy B (main + rifle for keep-away) loses because the secondary gets no investment. Test
cheap ways to keep a second gun current (copy, not move, the range bonus; Workshop "match 50% of
the main gun's bonuses" for Junk) against strategy B before building. Do not restrict transfers.

### Leave alone (high confidence)
ATB class factors, graze band widths, hit bands, crit thresholds, Tool transfer rules, rocket /
club rules, Random Fire / Attack All rules (their weakness in scripted fights is informative, not
broken), the 2 Commands mechanic (strong but central to Parasite Eve's combat; nerfing it would
make every build worse).

## Validation plan (live play)

1. **Add loadout logging** (gun id, bonuses, mods, armor, stat22, offense, Haste/Slow active) to
   battle rows — prerequisite for comparing any play test with the model.
2. **Animation timing measurement** per class and RoF (debug server, one battle each) to replace
   the assumed loop length.
3. **Room 156 replays** with a handgun, a machine gun and a rifle, before / after R1 (and R2).
4. **Day 5+ shotgun fights** before / after R4 (if built).
5. Compare each play test's time, HP lost, grazes / misses (hitq), reach rows with the simulator's
   prediction for the logged loadout; investigate any gap > 25% before tuning further.
