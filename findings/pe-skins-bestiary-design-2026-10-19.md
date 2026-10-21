# Skins and Bestiary — economy and in-game design, October 19, 2026

Two Junk sinks that never make Aya stronger: **skins** (play as another character or outfit) and
the **Bestiary** (enemy information). Both are bought with Junk at any time and **stay unlocked
for every game afterwards** (new games, other saves, the EX Game). Research behind it:
`pe-model-swap-research-2026-10-19.md`, `pe-model-catalog-2026-10-19.md`,
`pe-bestiary-design-2026-10-19.md`, `pe-enemy-model-catalog-2026-10-19.md`.

## 1. The Junk they compete for

Economy model (`economy/playthrough.py`, Normal preset, typical investment, 20 seeds):

| Point in the story | Junk earned so far | Junk spare |
|---|---:|---:|
| End of Days 2-4 | ~450 | ~70-90 (tight: Tools, mods) |
| End of Day 5 | ~750 | ~340 |
| End of Disc 2 | ~1,870 | ~930 (unused today) |

The EX Game carries Junk over and adds more. Because unlocks are permanent, prices can be set
against several runs' surplus, not one.

## 2. Bestiary prices (from the Bestiary design, now permanent)

- Per creature: basics free on first kill; **weaknesses** by Scan, 5 kills or Junk; **loot** by 15
  kills or Junk. Prices rise by story section (Day 1: 2 / 3 Junk ... Day 6: 12 / 24 Junk);
  buying the whole story Bestiary outright costs ~717 Junk; with kills and Scan a player spends
  ~360-400. Chrysler section: 12 / 24 Junk per creature (provisional).
- **Permanent:** kills, Scan unlocks and purchases carry into later games, so the Bestiary fills in
  over a player's history, not per save. A second run's Bestiary spending is therefore small: the
  repeatable sink is the skins.
- "Whenever": any entry can be bought at any time, also for a creature not met yet (its name
  shows as "???" until met; buying reveals the tier anyway).

## 3. Skin catalogue and prices

Ordered by value: the main cast and showpiece models cost most; Aya's own outfits are cheapest
(they need no conversion). Ben, the police dog and monsters are excluded.

| Tier | Price | Skins | Notes |
|---|---:|---|---|
| Free | 0 | Aya (jacket and jeans) | the default |
| Outfit | 100 | Aya: black evening dress, T-shirt and jeans, long dress | Aya's own bundles, ready now |
| Premium | 400 | Aya's transformed form, Melissa, Eve (Day 1 form) | showpieces; Eve only if the conversion works (49 parts) |
| Main cast | 250 | Daniel, Maeda, Maya | retarget fixed (2026-10-19) |
| Supporting | 150 | Chief Baker?, Daniel (gun drawn), Maeda (backpack) | variants count as separate skins |
| Extras | 50 | Aya's date, policewoman (vest), policewoman (cap), police officer (moustache), police officer (cap), NYPD man (brown jacket), NYPD man (holster), opera actress, opera performer (doublet), robed king, knight, harlequin, usher, crew | 14 skins |

Totals: Outfit 300 + Premium 1,200 + Main cast 750 + Supporting 450 + Extras 700 = **3,400 Junk**.

| Collection pace (Normal, typical) | Junk for skins |
|---|---|
| First run (after ~400 on the Bestiary) | ~500: the three outfits and a main-cast skin, or several extras |
| Each later run | ~900 |
| EX Game | extra |

So a full collection takes about four runs, a main-cast skin is affordable within the first run,
and the cheapest extras from Day 3-4 onward. All prices are knobs in one table.

**Price curve, 2026-10-21 (user: "fun to unlock things early on the first playthrough"; the full
collection is for repeat runs or grinding).** 34 buyable skins after the cast additions (Wayne, Torres,
Warner, Cathy, Eddie, Nix, Scientist, Klamp, Ben, Nurse, Guard, Soldier, Cameraman, Admiral,
Captain):

| Tier | Price | Skins | Total |
|---|---:|---:|---:|
| Extras | 25 | 12 | 300 |
| Aya's outfits | 50 | 2 (long dress / transformed still "soon") | 100 |
| Supporting | 100 | 13 | 1,300 |
| Main cast | 250 | Daniel, Maeda, Maya, Klamp | 1,000 |
| Showpiece | 400 | Melissa | 400 |
| **All** | | | **3,100** |

First run (Normal): 2-3 extras by Day 4 (~70-90 spare), outfits and a couple of supporting skins by
Day 5 (~340), one or two main-cast skins by the end (~930 more). Everything plus the Bestiary
(~400-700) is ~3,500-3,800 Junk: 3-4 runs, or a run plus grinding. The Wardrobe groups by price
(main 250+, supporting 100+, extras below).

## 4. How to buy

Two places, same catalogue and prices:

1. **F1 > PE Enhancements > Collection** (any time outside battle, also on Day 1):
   - `Your Junk` (live), then two pages:
   - **Wardrobe:** every skin with its price; owned skins show OWNED; a locked skin shows its tier
     and price, and confirm buys it (Junk taken from the current game's Junk counter).
   - **Bestiary:** creatures by story section; each row shows what is known (name / ???, HP,
     weaknesses, loot) and the price of the next tier; confirm buys it.
2. **Wayne's Workshop** (NYPD, and Warner on Day 4): a **Wardrobe** row beside Requisition, the same
   list in the game's own text box (5 per page, dimmed when too expensive). The Bestiary stays in
   the F1 menu (it is a reference you read, not a counter purchase).

Junk is spent from the running game; the unlock is written at once to the profile (section 6), so it
survives even if that game is never saved.

## 5. How to activate

- **Skins:** F1 > Collection > Wardrobe > **Wear**: pick any owned skin (or Aya). It applies at the
  next room load (door, battle start or end, loading a save), when the game reloads the player
  bundle anyway (`Scene_LoadEntityTexture` step 6 and `Scene_LoadEntityTextures` step 6 take our
  bundle and rows instead of the disc's). Wayne's Wardrobe also offers Wear.
- The choice is remembered in the profile, so every game starts in the chosen skin. "Story outfits"
  mode (default ON for Aya's outfits): while wearing an Aya outfit, the game's own outfit changes
  (Day 1 dress, Disc 2 T-shirt) still happen; a character skin stays as chosen.
- Cutscenes that use Aya's separate cutscene models are not affected (only the field / battle
  player model is swapped).
- **Bestiary:** F1 > Collection > Bestiary (read any time); a new entry or tier shows a short
  on-screen line ("Bestiary: Green Snake - weaknesses").
- **Scan** (done, 2026-10-19): Scan now shows one line with the target's weaknesses and
  resistances; with the Bestiary built, casting it also unlocks that creature's weaknesses tier.

## 6. Where unlocks live (permanent)

- A profile file beside the game, `pe_collection.dat` (written with `fopen` like the play log):
  magic / version / checksum; skin bitmask (64 bits), worn skin id, "story outfits" flag; per
  creature one byte (2 tier bits, kill count capped at 31; ~90 creatures with Chrysler).
- Read at start-up, written at every unlock / kill-tier change / Wear. Not in the memory-card save
  and not in save states, so loading an older save never takes an unlock away. (The save tail stays
  free for per-game data such as the BP respec record.)
- A "Reset collection" action under Debug for testing.

## 7. Building a skin (offline tool, then a data file)

For each skin, `tools/pe_assets` produces a bundle the mod loads instead of the disc's:

1. Mesh: the character's model from its room (catalog location), unchanged.
2. Animations: Aya's 29-bone player rows (outfit bundle rows 0-3, 13-23, 28 and the per-day rows
   4-12) retargeted with `retarget.py` (semantic chains, world-orientation matching, shoulder
   rest correction), re-encoded in the game's animation format (constant / per-frame channels).
3. Texture: the character's TIMs from its room's scratch / texture blobs, repacked into the
   player's texture slot (one 4-bit page at x=960, y=256; palettes rows 448-449), faces' page /
   palette rewritten (the player's raw page 31, so `Render_InitPrimBlock` leaves it alone).
4. Header: anchor (`anchor_y`, `anchor_matrix_index`), shadow and hit-cylinder values checked
   against Aya's so the camera, shadow and hits line up.

Per skin, test in game: walk / run / aim / fire / dodge / item use / door and ladder actions /
battle start and end / a cutscene; check the gun sits in the hand (the gun is a separate model
attached to a hand part: map it to the character's hand).

## 8. Order of work

1. Profile file + Collection page (Bestiary reading, Wardrobe list) — no model work needed.
2. Aya's outfits as the first skins (native bundles: pick the image entry).
3. Bestiary unlocks: kill hook (the logger's enemy-slot tracking), Scan hook (`0x80024250`, spell 7),
   creature table generated from `pe-bestiary-draft-2026-10-19.json`.
4. Bundle builder: animation encoder, texture repack; Daniel first, then Maeda and Maya.
5. Wayne's Wardrobe row; the remaining skins in tier order; Eve last (feasibility).
