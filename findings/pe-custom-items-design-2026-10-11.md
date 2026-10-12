# Parasite Eve: custom items and mods for the loot overhaul (design)

**Date: 2026-10-11. Status: decisions recorded, nothing built. Companion to
[`pe-loot-overhaul-design-2026-10-11.md`](pe-loot-overhaul-design-2026-10-11.md), whose
decisions 1–24 this builds on (Junk counter, Mod Codex, rare loot table, shop).**

## Why

Three gaps in vanilla PE that the overhaul exposes:

- **Nothing ties your build to the economy.** In Diablo-style games, gear choice changes
  how well you farm; in PE it doesn't.
- **No guaranteed escape.** Fleeing is random, so a farming run at low HP or out of ammo
  can end on a bad roll.
- **No way to lean into the rare table** other than grinding more.

## Where new things can live (from the decomp and the live item dump)

| Space | What it is | Limits |
|---|---|---|
| **5 unused mod effects** | The game's mod-name table (text table 3) has 35 real effects (guns 1–20 = entries 0–19, armor 1–15 = entries 20–34) and **5 entries named "dummy"** (35–39), right after the armor effects | Names shown through the `Draw_PrintRawText` hook (as Weapon power does); effects done by our hooks; must confirm the game ignores these numbers safely |
| **2 unused items** | `ITEM24` / `ITEM25` (ids `0x18` / `0x19`): kind 10, Tools and Junk, "Helps Item", flags 0x03, no case in `Battle_ApplyDamage` | Only two. Names relabelled at draw time; effects by a hook on item use |

## Decisions (user, 2026-10-11)

| # | Decision |
|---|---|
| C1 | **New armor mod "Scavenger":** +50% Junk from battles |
| C2 | **New armor mod "Lucky Find":** the rare-drop soft pity builds up faster |
| C3 | **New armor mod "Salvager":** +25% Junk from dismantling |
| C4 | **New armor mod "Bargain":** shop prices −15%; the user's price caps (Tools ≤ 100, buy-back ≤ 150) still apply on top |
| C5 | **The four new mods are economy-only:** they make farming better, never make Aya stronger in combat. They live in the 4 of the 5 "dummy" effect slots and are obtained **only** through the rare loot table or Wayne, never from the shop. Once found, they go into the Codex like any other effect (dismantle to unlock, install for Junk) |
| C6 | **New item "Smoke Grenade"** (`ITEM24`): used in battle, a **guaranteed escape**. Sold in the shop at a mid price. Escaping still gives no rewards, as in vanilla |
| C7 | **New item "Lucky Charm"** (`ITEM25`): for the next 10 won battles, the rare roll counts **double** toward pity. Found as a rare-table entry |
| C8 | **Not adding:** anything that skips Wayne's 300 (gun vouchers); more healing items (PE already has plenty); new gun or armor pieces (they'd need new models and stats) |
| C9 | **New armor mod "Recycler"** (the 5th "dummy" slot): when the "items found" screen holds more than the bag can take, the leftovers become **Junk instead of being discarded**. Economy-only like C1–C4, and obtained the same way (rare table or Wayne) |
| C10 | **Medicine fusion** (Workshop recipe, no new item ids): **2× Medicine 1 → Medicine 2, 2× Medicine 2 → Medicine 3, 2× Medicine 3 → Medicine 4**. Free or 1 Junk. Heals are 45 / 90 / 180 / 400 HP (`Battle_ApplyDamage`), so 2-for-1 is even in HP (a small gain at the top). The point is one bag slot and **one battle turn instead of two**, and auto-medicine armor uses the best medicine first |
| C11 | **Dropped: stat booster fusion.** Boosters are consumed and add a permanent +N (Offense 1 = +1, Offense 2 = +2), so three Offense 1s already give +3; fusing them into one Offense 2 would lose value, and boosters are used outside battle, so no turn is saved |

**All 5 dummy mod slots are now used** (C1–C4, C9), and both spare item ids (C6, C7).

## How they fit the existing decisions

- **Rare loot table (loot decision 18):** gains two entries, the new armor mods (on a
  carrier armor or straight into the Codex; to settle when building) and the Lucky Charm.
  Shares get re-tuned in the balance pass.
- **Shop (loot decision 14):** adds the Smoke Grenade. Price tuned under the existing caps.
- **Codex (loot decisions 9–11):** the four mods behave like any other effect. Price band:
  mid, since they're strong for farming but don't affect combat.
- **Saved state:** the Lucky Charm's battles-left counter lives in the loot mod's
  save-state block and save tail, like the pity counter.

## Research before building

1. **Safe dummy effects:** confirm the armor-list builder (`Inv_BuildArmorList`,
   `tailData & 31`) and the damage and battle code ignore effect numbers 16–20 for armor
   (entries 35–39) without side effects. Also check which exclusivity group bits they
   should carry.
2. **Relabels:** confirm the "dummy" names and the `ITEM24/25` names and descriptions can
   be swapped through the existing `Draw_PrintRawText` hook in every menu that shows them
   (bag, equip screen, Codex, items-found screen).
3. **Smoke Grenade:** find where battle escape is decided (the escape command,
   0x199+ in the battle queue) and how to force success; and how a kind-10 item becomes
   usable in battle (the `Battle_UseItem` → `Battle_ApplyDamage` path).
4. **Lucky Charm:** whether it should be used from the bag (field use path) or work just
   by being carried; field item use goes through `Inv_BuildEquipSlotDisplay`'s item types.
5. **Recycler:** find how the "items found" screen handles a full bag (the discard step
   after `Inv_LoadWayneItemsAsOverride`), so leftovers can become Junk at that point.
6. **Medicine fusion:** a Workshop action only. It removes two bag entries and adds one
   (bag writes, as the give-item and Item Editor rows already do). No game code needed.
7. **Effects:** Scavenger and Salvager hook the same places as the Junk rules (the
   `Aya_SetTotalExp` hook and the dismantle action); Bargain hooks the shop prices; Lucky
   Find hooks the soft-pity step. All read the equipped armor's mod bytes.

## Sources

Decomp: `include/pe1/item_ids.h`, `Battle_ApplyDamage.c`, `Inv_BuildArmorList.c`,
`Inv_ItemActions.c`; live item table dump
[`data/pe-items-baseline-2026-10-11.csv`](data/pe-items-baseline-2026-10-11.csv);
mod-name table decoded live (loot doc section 6.1b).
