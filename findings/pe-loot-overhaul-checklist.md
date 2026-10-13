# Parasite Eve loot overhaul: build checklist

Tick items off as they land. Design and decision numbers:
[loot overhaul design](pe-loot-overhaul-design-2026-10-11.md) (decisions 1–41) and
[custom items](pe-custom-items-design-2026-10-11.md) (C1–C11). Started 2026-10-11.

## Done before the build

- [x] Design discussion complete: decisions 1–40, C1–C12 (review 2026-10-11 added 31–40)
- [x] Save-state API for plugin data (`psx_mod_register_state`, psxrecomp `6cb1d104`), first
      user Half-bar ATB (PE `fe00ce3`), verified live
- [x] Research: drop flow, Wayne's counter and crafting (live: crafts on a hand-in that
      reaches 300, subtracts 300), hook points (`Aya_SetTotalExp`, `Inv_DispatchCommand`,
      `Inv_AddItem`), save tail, mod effects, spare item ids and mod slots
- [x] Wayne junk refund written (`src/mods/pe_wayne_refund.c`, decision 8), compiles

## Phase 0: prep (one build, game closed)

- [x] Build with `pe_wayne_refund.c` (PE `b833f6f`)
- [x] Test the refund on save state slot 6 (Day 4 at Wayne; debug slot 5): counter → 300,
      Super Junk in the bag, counter −300 → 300 back, item kept, toast shown; a normal craft
      is not refunded (verified 2026-10-11)
- [x] Refund toast wording: "Wayne refunds 300 Junk" (37)
- [x] Commit the refund mod (PE `b833f6f`)
- [x] Hook on `Inv_DispatchCommand` (0x8005D2B4), logged during a "Discard junk" hand-in
      (kept, gated by the logger). **Result:** removal is 1112 (value Junk); the count is
      NOT 1102 but the script's own count opcode `Task_CountItemsByValue` (0x800194F8) →
      `Inv_CountByValue` (0x80053E6C). Phase 1's "place one Junk" hook moves there
- [x] Loot logger: session marker per launch (verified)
- [x] Loot logger: skip identity-0 rows (and the 1-frame "battle" after a load) (coded;
      shows up in the play session)
- [x] Loot logger: steal logging (what was stolen, empty steals = item 0x00) and "add"
      rows for other `Inv_AddItem` calls (add verified with Wayne's gun; steals show up in
      the play session)
- [ ] User plays a normal stretch with the logger on (baseline data for phase 7)

## Phase 1: Junk counter (decisions 2, 13, 16, 17, 20, 21, 22, 24, 28, 30)

- [x] New `game.toml` hooks: `Aya_SetTotalExp` 0x8004B70C, `Inv_DispatchCommand`
      0x8005D2B4, `Inv_AddItem` 0x80053D2C, `Save_SerializeTail` 0x8003F800,
      `Save_DeserializeTail` 0x8003FBD8 (PE `b833f6f`)
- [x] Loot mod skeleton `src/mods/pe_loot.c`: master switch "Junk economy", on by default
      (28), F1 → PE Enhancements → Workshop page (PE `c0060dc`)
- [x] Junk counter storage: save-state block (`pe.loot`) **verified** (F7 save at 35, load
      → 35); save-tail block ("PELT", version, junk, check) **coded, memory-card test
      pending**; absent → start at 0
- [ ] Battle end: move vanilla Junk entries out of the reward list into the counter,
      keep the list contiguous (coded; needs a battle that drops Junk, e.g. Day 3 precinct)
- [x] Battle end: floor of 1 + EXP-scaled Junk, with a per-battle cap (16, 17) (1 + EXP/8,
      cap 30; verified in play 2026-10-12: a toast after every won battle)
- [ ] Skill bonus: up to +25% battle Junk for a no-hit battle, from the enemies' "hits on
      Aya" counts (`+0x9C`), tracked during the battle (32) (coded; battle test pending)
- [x] ~~Toast after every won battle~~ → replaced 2026-10-13 by the items-found "Junk xN"
      line (phase 5; user: in-game messages only)
- [ ] Chest / story Junk → counter (20): `Inv_AddItem(Junk)` rewritten to `Inv_AddItem(0)`
      and counted (coded; the add-item hook sees every chest pickup (14 logged on Day 4),
      but no Junk chest found yet)
- [ ] Stolen Junk (an `Inv_AddItem` call from `Battle_ResolveHitOnTimer`, ra 0x800236E8–
      0x80023E14): don't put it in the bag; bank it and pay it at battle end only on a win
      (41); test steal-and-flee adds nothing (coded; steal test pending)
- [x] Add the `Task_CountItemsByValue` hook (0x800194F8) to `game.toml` (PE `c0060dc`)
- [x] Wayne hand-in (PE `c0060dc`, **verified**: 50 Junk, Wayne at 280 → 20 handed, gun,
      30 left). The script counts ONCE then removes that many: the count reads a scratch
      list of N Junk, each 1112 removal gets one Junk placed just in time (needs one free
      slot inside the bag limit); the hand-in stays open across his dialogue, since his
      script adds even for failed removals. Workshop choice "Wayne hand-in": Next gun
      (default) / All Junk
- [x] Junk found in the bag or Wayne's storage moves into the counter in free movement,
      with a toast (a sweep, not one-time; verified with 50 Junk in storage)
- [x] Master switch off/on mid-playthrough (decision 45, built 2026-10-12): off = vanilla
      (Junk in the bag, Wayne counts it, Tools vanilla, Workshop refuses; "Take out Junk"
      moves the counter into bag/trunk); on = the sweep takes Junk back (test pending)
- [x] Wayne hand-in with a full bag: his row reads "Discard junk 147, 120/300 bag full"
      (was a toast; 2026-10-13, test pending)
- [x] Junk total row on the Workshop page (22) (verified)
- [x] Debug → Loot tuning page: floor, EXP per Junk, per-battle cap, no-hit bonus %, Set Junk
      (30)
- [ ] Live test: battles, a chest, a full Wayne hand-in that crafts, F7 save/load, a
      memory-card save/load, a vanilla save without the block
- [ ] Verify the EX Game save carries the save-tail block (15)

## Phase 2: rare drops (decisions 18, 23)

- [x] Rare roll with soft pity (only won battles count; enemy drops reset it)
- [x] Rare table: Tool 40, stat booster 35 (tier by battle EXP), Super Junk 10, Duper Junk
      5, Mod Permit 7, Super Tool 3; phase 6 added economy mod 6 and Lucky Charm 5
- [x] Add the drop to the reward list ("items found" screen, name in gold); carry it over
      if the list is full
- [x] Pity counter and carried drop in the save-state block and save tail
- [x] "Rare drop guaranteed within N battles" row on the Workshop page (23)
- [x] Tuning rows: base chance, step, guarantee
- [ ] Live test, including a save/load mid-streak

## Phase 3: Codex / Mod Catalog (decisions 9–12, 26) — done (PE `f3ebb08`, `90e011f`, `a375eed`)

- [x] Codex storage: unlocked effects (save-state block + save tail)
- [x] Dismantle (F1 row for now): item → its effects into the Codex, item → Junk
      (scaled by tier and +bonus, max 150); duplicates → extra Junk
- [x] Dismantle guards: never the equipped gun or armor; armor with bag-capacity mods only
      when the bag would still fit its items (the Item Editor's existing check)
- [x] Dismantle guard: never the last Club (36); warn before dismantling the last gun for
      an ammo type you carry (36)
- [x] Codex list on the Workshop page: unlocked effects, greyed "dismantle to unlock" for
      effects on carried gear, names from the game's mod text
- [x] Install: pick item + free slot + effect; price by value ranking; premium effects
      (Command ×2/×3, Attack All, maybe ROF ×10) also cost a Tool (9); game group rules
- [x] Remove / replace installed effects freely
- [x] Buy-back list (~30 entries): item id, +bonuses, slot count; returns with empty mod
      slots; price = min(payout × 1.5, 150) (12)
- [x] Every cost shown before confirming; no random failure
- [x] Tuning rows: install price bands and rebuild markup (dismantle payout formula is fixed
      for now: 5 + 2/+bonus + 3/mod + 5/duplicate, max 150)
- [x] Shop-style live rows: Your Junk, Pays, New effects, Cost; Item row names the
      equipped gear
- [x] Debug: Give 100/1000 Junk, Unlock all effects, Clear catalog, fixed test gun/armor
- [x] Live test (2026-10-12, user: works; F1 pausing makes it a bit janky)
- [x] Tool salvage (42): a plain Tool's donor unlocks its remaining effects, pays
      dismantle Junk for what's left and goes on the Rebuild list (hook on
      `Inv_TransferItemBetweenLists` 0x8005A318); Super Tool keeps the donor; a target mod overwritten by a same-group move
      unlocks in the Catalog (any Tool)
- [x] Live test Tool salvage (2026-10-12, user: "it all seems to work well")
- [x] F1 Mod Catalog as an effect board (grid rows added to recomp-ui 9f09f0a and psxrecomp
      c80e0189; PE cb5f51d): blue unlocked, grey seen, "?" unknown, gold premium, mark =
      on the equipped item; auto slot; accept twice installs; Selected / Replaces / Result
      rows. Live-tested 2026-10-12 (user: works well)

## Phase 4: shop (decision 14)

- [x] F1 shop page (Workshop > Requisition, `pe_loot_shop.c`): goods board with medicine,
      cures, bullets, rockets, Tools; list and prices in decision 43
- [x] Tool price 40, +10 per purchase, capped at 100; purchase count saved (save-state
      block "pe.loot.shop" + save tail "PESH" at 0x1C90 + 0x1C0)
- [x] Not sold: Super Tools, guns, armor (and Revive, Full Recover, Maeda's, boosters: 43)
- [x] Soft-lock rescue (36): detect "can't attack" (no melee weapon, no gun with loaded
      rounds or spare ammo of its type); then offer a free Club 1 on the Workshop page, make
      the basic handgun ammo box cost 0 Junk until she has ammo, and show a toast
- [ ] Soft-lock test: dismantle every gun but the equipped one, empty all ammo, discard
      the Club → rescue appears; repeat from a save state saved mid-battle
- [x] Tuning rows: Shop price %, Tool price start / step / cap, Tools bought
- [ ] Live test (full bag, ammo pools at cap)

## Phase 5: native menus (decisions 21, 22, 25, 27, C10) — partly built (PE `e052f22`, decision 44)

- [x] Research: punctuation in the text-box font: '.' 0x2F, ',' 0x4B, ':' 0x4A, '!' 0x2B,
      ''' 0x2E, '/' 0x4C; no "·" or "(" found, so Wayne's label is "147, 120/300"
- [x] Research: how selecting an item opens its action list
      (`Menu_OpenItemActionSubmenu` → `Menu_CreateUsableItemActionView`)
- [x] Aya's item menu: Dismantle on a gun/armor, with confirm (25) — via Discard (44); the F1
      Dismantle row stays for now
- [x] Aya's item menu: Combine on Medicine 1–3 when you hold two (2× → next tier) (C10) — via
      Discard (44)
- [ ] Aya's item menu title: Junk total (22)
- [x] Research: Wayne's choice list is a script text box (FB 09 n), drawn by
      Menu_DrawTextboxEntries (pe_wayne_menu.c)
- [x] Wayne's menu: "Discard junk 147, 120/300", plus "bag full" / "Day 4" (22, 31)
- [x] Wayne's menu: Workshop row → Requisition and Rebuild screens in his own box (27, 47);
      the F1 pages stay as backup/debug (decision 47)
- [x] Native "items found" line for Junk ("Junk ×3") (21), built 2026-10-13 (PE `d907732`,
      test pending): one Junk entry at the top of the list, its name relabelled "Junk xN";
      the player's choice as with vanilla drops (user): taken, all N go to the counter and the bag item goes straight back out; left behind, lost; a full bag can't take it; no room in the list, credited directly. **Toasts dropped** for battle,
      chest, sweep and dismantle Junk (user: in-game messages only; replaces 24's toasts)
- [x] In-play toasts moved in game or dropped (2026-10-13, test pending): Wayne "can't
      build yet" → his row "Day 4"; full-bag hand-in → "bag full"; Wayne refund, Lucky Charm
      used, Tool salvage and the Smoke Grenade's "escaped" dropped (each is visible in
      game); the Smoke Grenade is greyed out in battles it can't escape (no use-and-refund)
- [x] Economy mod found by the rare table: an items-found line, a Mod Permit entry named
      "<mod> mod" in gold; taken = unlocked, left = lost (2026-10-13, test pending)
- [ ] Rescue hint ("Aya can't attack: Wayne's Workshop has a spare Club"): kept as the one
      toast (soft-lock lifeline); in-game home to decide
- [ ] Live test

## Phase 6: custom content (C1–C7, decision 19) — built (PE `a3a57f2`), not live-tested

- [x] Research: the game ignores the "dummy" effect numbers safely; group bits (C13: armor
      17–20, no group; 16 avoided for its icon)
- [x] Research: relabel "dummy" and `ITEM24/25` names everywhere they're shown (text tables
      +0x08 / +0x0C / +0x10 swapped in the `Draw_PrintRawText` hook, `pe_custom.c`; glyph
      codes A=0x10, a=0x30, 0=0x00, space 0x0F, end 0xFF)
- [x] Scavenger (+50% battle Junk) (C1)
- [x] Lucky Find (faster soft pity) (C2)
- [x] Salvager (+25% dismantle Junk) (C3)
- [x] Bargain (shop −15%, caps still apply) (C4)
- [x] The four mods come only from the rare table (straight into the Catalog, C13); Wayne
      source not built (his 300-Junk roll is the game's script)
- [x] Research: where battle escape is decided; Smoke Grenade = guaranteed escape,
      sold in the shop (C6, C15)
- [x] Lucky Charm: double pity progress for 10 won battles, a rare-table entry (C7, C14)
- [x] Research: where Aya's steal resolves; empty steal → a little Junk (19), **banked and
      paid at the battle-end hook only on a win** (35); test steal-and-flee gives nothing
- [ ] Live test (the new mods' badges: text badges Barg / Scav / Luck / Salv, PE `b73be3b`)
## Phase 7: balance (decisions 5, 7)

- [x] First pass from the balance estimate (saves, video, guides; 2026-10-13): Junk
      formula kept (1 + EXP/8), cap 12, boss cap 25; pity base/step per preset; prices and
      payouts checked (decision 34 now: first Wayne gun around the start of Day 4)
- [ ] Second pass from logged play (Days 4–6 especially): re-check fights per day, EXP per
      fight, Junk per hour, and adjust the tuning rows
- [x] Economy mods for sale at Wayne's Requisition, 150 Junk each (tunable "Economy mod
      price"), listed until unlocked (stopgap, 2026-10-13): the rare drop alone gave ~1 of 4
      a run
- [ ] Economy mods, final source: proposed a guaranteed one for each of the first four
      boss wins (the rare roll stays); decide, then keep or drop the shop listing
- [x] Recommended changes from the balance estimate, **built 2026-10-13 (PE `e565a36`,
      playtest pending)**
      ([`pe-loot-balance-estimate-2026-10-13.md`](pe-loot-balance-estimate-2026-10-13.md)
      section 9): cap 30 → 12; bosses cap 25 (if a clean boss test
      exists); keep EXP/8 and floor 1; presets scale pity base/step; Tool Kit turns Tool
      rolls into boosters and hides shop Tools; Medicine 4 50 → 80, Medicine 3 25 → 35;
      repeat-effect dismantle bonus +5 → +2; Wayne's guns and top Chrysler gear rebuild at
      150; Wayne's 300 stays (escalating repeat guns held in reserve)
- [x] Make the tuned values the code defaults (first pass, PE `e565a36`)
- [x] Difficulty presets Relaxed / Normal / Grind on the Workshop page, switchable any
      time, default Normal; scale Junk, pity length and prices; caps fixed (39, 40) — built
      early (PE `a3a57f2`): Junk x1.5/x1/x0.75, guarantee x0.7/x1/x1.3, prices -25%/0/+25%
- [ ] Full playthrough check, into EX Game
