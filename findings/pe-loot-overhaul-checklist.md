# Parasite Eve loot overhaul: build checklist

Tick items off as they land. Design and decision numbers:
[loot overhaul design](pe-loot-overhaul-design-2026-10-11.md) (decisions 1–30) and
[custom items](pe-custom-items-design-2026-10-11.md) (C1–C11). Started 2026-10-11.

## Done before the build

- [x] Design discussion complete: decisions 1–30, C1–C11
- [x] Save-state API for plugin data (`psx_mod_register_state`, psxrecomp `6cb1d104`), first
      user Half-bar ATB (PE `fe00ce3`), verified live
- [x] Research: drop flow, Wayne's counter and crafting (live: crafts on a hand-in that
      reaches 300, subtracts 300), hook points (`Aya_SetTotalExp`, `Inv_DispatchCommand`,
      `Inv_AddItem`), save tail, mod effects, spare item ids and mod slots
- [x] Wayne junk refund written (`src/mods/pe_wayne_refund.c`, decision 8), compiles

## Phase 0: prep (one build, game closed)

- [ ] Build with `pe_wayne_refund.c`
- [ ] Test the refund on save state slot 6 (Day 4 at Wayne): counter 299 → 300, put a
      Super Junk in the bag, drop the counter by 300 → expect 300 back and the item kept
- [ ] Commit the refund mod
- [ ] Temporary hook on `Inv_DispatchCommand` (0x8005D2B4): log command/value during a
      "Discard junk" hand-in; confirm the 1102 (count) / 1112 (remove) loop
- [ ] Loot logger: session marker per launch
- [ ] Loot logger: skip identity-0 rows (and the 1-frame "battle" after a load)
- [ ] Loot logger: steal logging (what was stolen, empty steals)
- [ ] User plays a normal stretch with the logger on (baseline data for phase 7)

## Phase 1: Junk counter (decisions 2, 13, 16, 17, 20, 21, 22, 24, 28, 30)

- [ ] New `game.toml` hooks: `Aya_SetTotalExp` 0x8004B70C, `Inv_DispatchCommand`
      0x8005D2B4, `Inv_AddItem` 0x80053D2C, save build/load (`Save_SerializeTail` and the
      load path)
- [ ] Loot mod skeleton: master switch, on by default (28), F1 → PE Enhancements →
      Workshop page
- [ ] Junk counter storage: save-state block (`pe.loot`) + save-tail block (magic,
      version) written on save and read on load; absent → start at 0
- [ ] Battle end: move vanilla Junk entries out of the reward list into the counter,
      keep the list contiguous
- [ ] Battle end: floor of 1 + EXP-scaled Junk, with a per-battle cap (16, 17)
- [ ] Toast after every won battle: "+N Junk · total" (21, 24)
- [ ] Chest / story Junk → counter (20), through `Inv_AddItem` or a per-frame sweep
- [ ] Wayne hand-in: on count-Junk (1102) with no Junk in the bag, place one Junk from
      the counter (needs one free slot); sweep back any unused placed Junk
- [ ] Junk total row on the Workshop page (22)
- [ ] Debug → Loot tuning page: Junk per EXP, floor, per-battle cap (30)
- [ ] Live test: battles, a chest, a full Wayne hand-in that crafts, F7 save/load, a
      memory-card save/load, a vanilla save without the block
- [ ] Verify the EX Game save carries the save-tail block (15)

## Phase 2: rare drops (decisions 18, 23)

- [ ] Rare roll with soft pity (only won battles count; enemy drops reset it)
- [ ] Rare table: Tool 40, stat booster 35 (tier by area), Super/Duper Junk 15, Mod
      Permit 7, Super Tool 3
- [ ] Add the drop to the reward list ("items found" screen); carry it over if the list
      is full
- [ ] Pity counter in the save-state block and save tail
- [ ] "Rare drop guaranteed within N battles" row on the Workshop page (23)
- [ ] Tuning rows: base chance, step, guarantee, table shares
- [ ] Live test, including a save/load mid-streak

## Phase 3: Codex (decisions 9–12, 26)

- [ ] Codex storage: unlocked effects (save-state block + save tail)
- [ ] Dismantle (F1 row for now): item → its effects into the Codex, item → Junk
      (scaled by tier and +bonus, max 150); duplicates → extra Junk
- [ ] Codex list on the Workshop page: unlocked effects, greyed "dismantle to unlock" for
      effects on carried gear, names from the game's mod text
- [ ] Install: pick item + free slot + effect; price by value ranking; premium effects
      (Command ×2/×3, Attack All, maybe ROF ×10) also cost a Tool (9); game group rules
- [ ] Remove / replace installed effects freely
- [ ] Buy-back list (~30 entries): item id, +bonuses, slot count; returns with empty mod
      slots; price = min(payout × 1.5, 150) (12)
- [ ] Every cost shown before confirming; no random failure
- [ ] Tuning rows: install price bands, dismantle payouts, buy-back markup
- [ ] Live test

## Phase 4: shop (decision 14)

- [ ] F1 shop page: consumables, ammo, Tools
- [ ] Tool price 40, +10 per purchase, capped at 100; purchase count saved
- [ ] Not sold: Super Tools, guns, armor
- [ ] Tuning rows: shop prices
- [ ] Live test (full bag, ammo pools at cap)

## Phase 5: native menus (decisions 21, 22, 25, 27, C10)

- [ ] Research: how selecting an item opens its action list
      (`Menu_OpenItemActionSubmenu` → `Menu_CreateUsableItemActionView`)
- [ ] Aya's item menu: "Dismantle" action on a gun/armor, with confirm (25); remove the
      F1 Dismantle row
- [ ] Aya's item menu: "Combine" on Medicine 1–3 when you hold two (2× → next tier) (C10)
- [ ] Aya's item menu title: Junk total (22)
- [ ] Research: which code draws Wayne's choice list and the "Discard junk" string
- [ ] Wayne's menu: "Discard junk (N)" (22)
- [ ] Wayne's menu: Shop and Buy-back rows; remove them from F1 (27)
- [ ] Later: native "items found" line for Junk ("Junk ×3") (21)
- [ ] Live test

## Phase 6: custom content (C1–C7, decision 19)

- [ ] Research: the game ignores the "dummy" effect numbers safely; group bits
- [ ] Research: relabel "dummy" and `ITEM24/25` names everywhere they're shown
- [ ] Scavenger (+50% battle Junk) (C1)
- [ ] Lucky Find (faster soft pity) (C2)
- [ ] Salvager (+25% dismantle Junk) (C3)
- [ ] Bargain (shop −15%, caps still apply) (C4)
- [ ] The four mods come only from the rare table or Wayne (C5)
- [ ] Research: where battle escape is decided; Smoke Grenade = guaranteed escape,
      sold in the shop (C6)
- [ ] Lucky Charm: double pity progress for 10 won battles, a rare-table entry (C7)
- [ ] Research: where Aya's steal resolves; empty steal → a little Junk (19)
- [ ] Live test

## Phase 7: balance (decisions 5, 7)

- [ ] Fit Junk per EXP and the floor to the logged pace; leave a Wayne gun reachable at
      a normal pace (13)
- [ ] Set pity chance, step and guarantee
- [ ] Set install bands, dismantle payouts, buy-back markup, shop prices under the caps
      (buy-back ≤ 150, Tools ≤ 100)
- [ ] Make the tuned values the code defaults
- [ ] Decide on difficulty presets (Relaxed / Normal / Grind) (7)
- [ ] Full playthrough check, into EX Game
