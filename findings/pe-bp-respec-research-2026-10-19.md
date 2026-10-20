# BP respec — research notes, October 19, 2026

Idea (user liked it): pay Junk to take back spent Bonus Points (BP) and spend them again. A no-power
Junk sink (BP total never grows). **Nothing is built** (mod-change hold). Decomp references below.

## How BP spending works

- Screen: `Menu_SpendBonusPoints` (`src/main/menu/item_actions.c:1477`). Stats 0-2 = the selected
  weapon's or armor's three bonuses (weapon: Attack / Range / Bullets; armor: Defense / P.Energy /
  Critical); stats 5-6 = two of Aya's own stats.
- **Flat price: 100 BP per step** for every stat. Items: +1 to `bonusStats[i]` per step (cap 999).
  Aya stats: + the distance to the next sub-level (`Aya_StatQueryDistanceAndSubLevel`) per step.
- Inside the screen the game already lets you take back steps, but only down to the value the stat
  had when the screen opened (`item->bonusStats[i]` / `g_BonusPointStatDeltas[stat]`).
- Commit: items write the edited record back at once (`item_actions.c:1578-1588`); Aya's stats and
  the BP total are written when the screen closes (`Menu_ExitBonusPointAllocation`,
  `item_actions.c:871`: `g_AyaStatAgility[0..6]` and `g_AyaBonusPoints`), then `Inv_RecalcSlotStats`.
- BP total: `g_AyaBonusPoints` `0x800C0E10` (persistent, game clamp 99,999).

## Aya's stat table (`0x800C0E28`, 7 x u16, `aya/stats.c:98-136`)

| Entry | Drives | Raised by BP? |
|---:|---|---|
| 0 | HP level -> max HP | no |
| 1 | offense | no |
| 2 | defense | no |
| 3 | active time (gauge rate / step) | no |
| 4 | status timing | no |
| 5 | battle stat 22 (first BP-screen Aya stat) | yes |
| 6 | item capacity | yes |

- New game: each entry starts at its growth table's first value (`Inv_InitNewGameInventory`,
  `save/game_data.c:777-781`).
- Every level-up adds **+10 to all seven entries** (`main_menu.c:416-423`, applied at `main_menu.c:736-743`).
- So Aya's BP share of entries 5 and 6 is computable from the save alone:
  `current - (start + 10 x level)`; the BP count follows by replaying the sub-level steps.
- **Standing rule:** never write Aya's stat table (it caused the HP-level bug, entry 0). A respec of
  entries 5-6 would write that table: needs the user's explicit exception, limited to entries 5 and 6.

## Weapon and armor BP

- BP and Tools / mod transfers both write `bonusStats` (`ItemDataRecord +0x0E`), so the game cannot
  tell how much of a bonus came from BP.
- No spare room in the record to keep it: `+0x02` holds a copy of the item id, `+0x03` is the only
  zero byte (one byte), and the 11th mod byte holds stale data in 86 of 719 records checked
  (all saves on disk, `g_InvItemSlotArray 0x800C0EAC`, 128 x 32 bytes).
- So item respec needs **our own record**, started by a hook on the screen's confirm: for each record,
  BP steps per stat (1 byte each), kept in the save tail (`g_MemCardFileBuffer + 0x1C90..`, about 224
  bytes free; shared with the Bestiary ~92 and model swap ~32). A list of (record index, 3 counts) =
  4 bytes per item: 24-32 items fit if the Bestiary and skins also go there.
- Tools / mod transfers move bonuses between records, so the record must follow them (hook the
  transfer too) or a respec only refunds what is still on the item (capped at its current bonus).
- BP spent before the mod is installed is unknown for items (Aya's stats are always computable).

## Options

| Option | Refunds | Writes | Effort |
|---|---|---|---|
| A. Aya stats only | BP in entries 5-6, exact from the save | stat table entries 5-6 (rule exception) | small |
| B. Items, tracked | BP spent on weapons / armor since the mod was installed | item bonuses; save-tail record | medium (spend + transfer hooks) |
| C. A + B | everything tracked | both | medium |

Junk price ideas (to tune with the economy model): a flat fee per respec, or Junk per 100 BP
refunded (e.g. 5 Junk per 100 BP, capped), cheaper early, so it soaks the Disc 2 surplus.
