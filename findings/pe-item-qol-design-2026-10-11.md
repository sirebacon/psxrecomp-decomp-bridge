# Parasite Eve: item quality-of-life improvements (design)

**Date: 2026-10-11. Status: decisions recorded, nothing built. Separate from the
[loot overhaul](pe-loot-overhaul-design-2026-10-11.md) and its build phases, though Q4
pairs naturally with it.**

## Why

Forum and guide complaints about PE's items are mostly about **clarity**: Tools, Super
Tools and some mods are described in ways that don't say what they do, and the game never
shows whether a new gun is actually better. The other common pain is losing items to a
full bag.

## Decisions (user, 2026-10-11)

| # | Improvement | What it does |
|---|---|---|
| Q1 | **Better descriptions** | Rewrite confusing item and mod descriptions at draw time. Tool: "Moves one mod or all + bonuses to another item. The donor is destroyed." Super Tool: "... The donor is kept." Mods with hidden downsides get a plain note, e.g. Rate of Fire ×10: "10 shots, each weaker" (shot% 13 at 10 shots). The fixes come from the forum complaints in the loot doc (section 1, "UX lessons") |
| Q2 | **Compare before equipping** | Extend Weapon power's "PWR n" to the equip screen as a change: **"PWR 120 → 150"** for guns (including Enter 2/3 Commands, see below), and the defense change for armor |
| Q3 | **Trading-card progress** | Show **"Rare T Card collection (8/14)"** so players see how close the Tool Kit (10 rare cards) and Super Tool Kit (14) are. On Wayne's "Rare T Card collection" row, and as a line on the Workshop page when the loot overhaul is on |
| Q4 | **Overflow to storage** | When the battle "items found" screen or a chest offers more than the bag holds, the extra goes to **Wayne's storage** (100 slots) instead of being discarded. The item is kept (unlike the dropped Recycler idea). **Optional F1 toggle**, default to settle when building (suggest on); if storage is also full, the vanilla discard happens |

**Not adding (for now):** Sort bag (needs menu research; reconsider later), storage
anywhere (too generous), quick-use battle buttons (changes the controls), more bag slots
(the Storage mod is parked; the loot overhaul's Junk counter frees slots).

## How each maps onto the game

- **Q1:** the existing `Draw_PrintRawText` hook (0x8005F27C), the trick Weapon power uses:
  match the description string (item text tables / mod text table 3) and the calling menu
  (`ra` range), then swap `a0` for our text in guest memory. Text must use PE's font glyphs
  (same check as loot decision 37). Research: which call draws item and mod descriptions
  (the menu help bar is `Menu_DrawContextHelpText`, already used by Weapon power).
- **Q2:** Weapon power already computes per-gun power. **Fix first:** it ignores Enter 2 /
  3 Commands (effects 19/20, ×2 / ×3 per turn; loot doc 6.1b). Research: which screen draws
  the equip comparison and where the currently equipped gun is read (`D_800C0E20` weapon
  slot).
- **Q3:** count the rare trading cards Aya holds or has shown Wayne. Research: where the
  game stores "cards shown to Wayne" (likely a script variable near his Junk counter
  `0x800A78B0`, found the same way: snapshot, hand over a card, diff).
- **Q4:** battle overflow happens after `Inv_LoadWayneItemsAsOverride` builds the items-found
  list; chest pickups go through `Inv_AddItem` (0x80053D2C), the hook point the loot
  overhaul also uses. Research: where the game decides "bag full" and asks to discard, so
  the extra can be written into Wayne's storage (`0x800C1EB8`, 100 × u16) instead.

## Build checklist

- [ ] Q2 prerequisite: Weapon power multiplies by commands per turn (Enter 2/3 Commands)
- [ ] Q1: research the description draw calls; relabel Tool, Super Tool, and the mods with
      hidden downsides; font check
- [ ] Q2: research the equip screen; show "PWR old → new" for guns, defense change for armor
- [ ] Q3: find where "rare cards shown to Wayne" is stored (snapshot + diff); show "(n/14)" on
      Wayne's row and on the Workshop page
- [ ] Q4: research the bag-full discard path for battle rewards and chests; send the extra to
      Wayne's storage; F1 toggle; storage-full fallback = vanilla discard
- [ ] Live test each, including a save-state load in the middle of a full-bag pickup
