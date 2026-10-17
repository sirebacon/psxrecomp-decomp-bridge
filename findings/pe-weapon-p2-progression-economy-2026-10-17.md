# Weapon balance phase 2 — F. Progression and economy (2026-10-17)

Builds on [pe-weapon-progression-analysis-2026-10-17.md](pe-weapon-progression-analysis-2026-10-17.md).
New: two guns from **one** budget (Day 5: attack boosters 2 x 12, mod picks = Day 5 budget + 1
permit), split 100/0, 75/25, 60/40, 50/50. Each gun's mods greedy within its share; in each
encounter the player uses whichever gun is faster, paying half a bar to switch (current rules).
Geo-mean vs the 100% single gun (negative = the pair is better).

| Primary + secondary | 75/25 | 60/40 | 50/50 | Where the secondary is used |
|---|---|---|---|---|
| DE50AE7 + MAG | +21% | +12% | **-16%** | keep-away first, then nearly everything at 50/50 |
| P90 + MAG | -6% | -8% | **-21%** | keep-away, D5 boss, then everything |
| DE50AE7 + M10B | +28% | +46% | +77% | almost never |
| MAG + M10B | +1% | +2% | +75% | never |

## Reading

1. **A MAG "secondary" isn't a secondary:** given half the budget it becomes the better gun in
   most encounters. Splitting pays only because the MAG is universally strong.
2. **A shotgun secondary never pays** (+28..+77%): there is no encounter where an M10B with a
   quarter to half of the budget beats a fully invested main gun. The economy isn't what stops
   two-gun play; the specialist has no encounter it wins.
3. With the shotgun package (report D) the M10B wins close stationary bosses only against
   non-MAG mains; re-test the split after any shotgun change.
4. Transfers are lossless (decomp), so frequent switching (strategy C) stays cheap; one-gun play
   remains optimal.

## Economy status and ideas (not approved, not built)

The Tool / Mod Catalog / Permit / Rebuild / Junk systems already let a player move everything to
a new gun. What two-gun play lacks is a specialist worth the split, not affordability. Economy
ideas (copying a range bonus, discounted backup upgrades) should wait until a specialist wins
an encounter; otherwise they would only make "MAG + anything" cheaper. No transfer restrictions.
