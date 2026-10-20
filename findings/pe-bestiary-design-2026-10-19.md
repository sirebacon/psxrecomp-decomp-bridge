# Bestiary design (Junk sink) — October 19, 2026

Design decisions for a Bestiary that the player fills in by fighting, scanning or spending Junk.
It is a **no-power** Junk sink for the rebalance + economy mod: it shows information, it never makes
Aya stronger. **Nothing is built yet** (the "no mod changes" hold still applies).

Data behind it: `findings/pe-bestiary-draft-2026-10-19.md` (every enemy stat block, names, drops /
steals with odds, mid-fight values, disc locations). Junk figures: economy simulator, Normal preset,
typical investment, 20 seeds per policy (`economy/playthrough.py`).

## Decisions (user, 2026-10-19)

1. **Per creature, three tiers.**
2. **Three ways to unlock a tier: Scan, kills or Junk.** Junk is the shortcut, never the only way.
3. **A full story Bestiary costs about 700 Junk** if everything is bought outright.
4. **The Chrysler Building (EX Game) gets its own section.**

## Tiers

| Tier | Shows | Unlocked by |
|---|---|---|
| 0 — Basics | name, area(s), HP | first kill (bosses: on defeat) |
| 1 — Weaknesses | defense, weak / strong elements (heat, frost, cyanide, acid, tranq) | casting **Scan** on it, or **5 kills**, or Junk; bosses: Scan, defeat, or Junk |
| 2 — Loot | drop and steal items with their odds | **15 kills**, or Junk; bosses: Junk only |

- Scan (Parasite Energy 7, 30 PE with the PE mod, vanilla 50) gets a lasting purpose: one cast fills
  in a creature's weaknesses for good.
- Bosses are fought once, so their loot tier (what you can steal, once) is the main boss Junk buy.
- A creature is one entry even when the game uses several stat blocks (the Sheeva heads, the Crab
  claws, the Centipede segments and phases, tougher copies later in the story). The entry shows the
  first block met and lists the later ones as they are met.

## Prices (story)

Prices rise with story progress, so the tight early Junk (Days 2-4 end with about 70-90 Junk spare)
is barely touched and most of the cost lands on Disc 2, where about 930 Junk is left unused today.

| Section | Creatures (bosses) | Tier 1 / Tier 2 | Buy everything |
|---|---|---|---:|
| Day 1 (theater, sewer) | 6 (2) | 2 / 3 J | 30 |
| Day 2 (Central Park) | 7 (1) | 3 / 6 J | 63 |
| Day 3 (NYPD, hospital) | 11 (4) | 4 / 8 J | 132 |
| Day 4 (Chinatown, sewer, subway) | 5 (1) | 8 / 16 J | 120 |
| Days 4-5 (museum, warehouse) | 10 (3) | 10 / 20 J | 300 |
| Day 6 (Statue of Liberty Eve, Ultimate Being) | 2 (2) | 12 / 24 J | 72 |
| **Total** | **41 (13)** | | **~717** |

- Disc 1 (Days 1-3): about 225 J. Disc 2 (Days 4-6): about 490 J, roughly half the Disc 2 surplus.

### What a player actually spends

Unlocks by kills and Scan mean nobody pays the full 717. Using the logged playthrough's kill counts:

| Player | Junk spent on the story Bestiary |
|---|---:|
| Buys every tier outright | ~717 |
| Buys only what kills (5 / 15) did not unlock | ~400 |
| Also casts Scan on every creature once | ~360 |

Kills alone unlocked weaknesses for 19 of the 28 regular creatures and loot for 8 (Blackbird was
killed 107 times, Bear, Cat and Grey Rat 3 or fewer). So Junk mostly buys the rare enemies and the
bosses, which is where the information is hardest to get by playing. Expected spend (360-400 J)
takes about 40% of the Disc 2 surplus; the rest stays for rockets, Wayne crafts and the EX Game.

If a stronger sink is wanted later: raise the loot threshold (for example 25 kills) or drop Scan's
unlock to "Scan shows HP only". Both are tuning knobs, not structural changes.

## Chrysler Building (EX Game) section

- 35 creatures (14 bosses) with their own entries; Chrysler stats are written directly (they match
  the shrine EX HP), so the entries need no scaling.
- Story entries also show **EX HP** once the EX Game starts: story enemies are scaled by about 1.397x
  in the EX Game (derived from the shrine's EX HP; to confirm from an EX save, story variable V80).
- Prices are **provisional**: Tier 1 / Tier 2 = 12 / 24 J (late Disc 2 level), about 1,260 J to buy
  everything, less with kills and Scan. Junk carries into the EX Game, but EX Junk income has not been
  simulated yet; set the final prices after an EX economy run.

## Open questions (for implementation, later)

1. **Where the unlock state lives.** Per creature: tier flags and a kill counter (small). It must
   survive saves without touching the game's save format; candidates are the mod's own save-state
   storage or spare bytes the game already saves. To decide when building.
2. **Menu.** Needs the mod menu groundwork (`findings/pe-mod-menu-groundwork-2026-10-10.md`) or a
   new screen. Entries show the game's own item names for drops / steals.
3. **Recognising a creature in battle** (for kills and Scan): by map + enemy ID, using the draft's
   identity table (the same ID can mean different creatures in different areas).
4. **Bosses with a computed HP** (Worm growth, damage carried over) show their starting HP and the
   growth values from the mid-fight table.
