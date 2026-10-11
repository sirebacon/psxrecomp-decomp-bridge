# Parasite Eve loot overhaul: drops, scrap, tools, dismantle and shop (design draft, 2026-10-11)

A discussion document for reworking Parasite Eve's loot loop into a "craft what you want,
but earn it" system. It covers how the game works today (decomp + guides), what our mod
toolkit can control, a proposed economy, and the decisions we still need to make. Nothing
here is built yet.

**Status (2026-10-11):** decisions recorded in section 5. Next is the **research pass**
(section 6) before building. Junk keeps its name and becomes a counter; the shop goes in
F1 first, then Wayne's screen; vanilla rewards stay.

**Goals (from the discussion):**

- Craft the gear and mods you actually want, but it costs effort.
- Grinding must never feel **pointless** (every fight pays something useful) or
  **frustrating** (no long dry streaks, no all-or-nothing gambles).
- Old gear shouldn't be dead weight. Today it only matters if it carries mods you can move.
- A clear economy for **Scrap** (dropped by enemies) and **Tools** (spent on mods).

---

## 1. How it works today

### Enemy rewards (decomp, `Battle_StepEntityAnimState.c`, checked live 2026-10-11)

Each enemy's battle record (`EnemyCombatant`) carries its rewards. When it dies:

| Field | Offset | What happens |
|---|---|---|
| `hpMirror` | | added to the battle's **EXP** total |
| `rewardBase`, `rewardFactorA`, `rewardFactorB` | +0x98 / +0x9A / +0x9C | **Bonus points** += `base − A × B`. `B` counts how many times *that enemy* hit Aya (`Menu_MainUpdate.c`), so taking fewer hits earns more BP |
| `rewardSlotId` (drop item) | +0x9E | appended to the battle's **reward list** (10 slots at `0x800A7FF0`, `{u16 item, s16 amount}`) |
| `stealItemId` (steal item) | +0x9F | taken by a melee hit with the **Steal** effect (Club 2): coin flip or always, from `statusFlags2` bits 12–13 (`Battle_ResolveHitOnTimer.c`) |
| `lootItemId` | +0xA0 | items the enemy stole *from* Aya, which come back when it dies |

After the fight the results screen (`Aya_SetTotalExp`) shows the reward list and Aya takes
what fits in her bag. No dice are rolled at death or on the results screen. Every enemy
simply hands over its one `rewardSlotId` item.

**Live example:** the two rat enemies in the slot 4 battle save each have drop item `0x01`
(**AMMO 6**, a 6-round handgun box, not a medicine as first written), steal item `0x01`,
and BP `5 − 2 × hits taken`.

**Still to check:** whether the game rolls a *drop chance* when an enemy spawns, which would
set `rewardSlotId` to 0 most of the time. Guides describe Junk as a common but not
guaranteed drop, which suggests a roll somewhere in the encounter data.

### Junk and Wayne (guides: Almar's Guides)

- **Junk** (item `0x14`, "Broken Item") drops from many enemies and can be stolen from some.
  It takes up bag space ("clogs up your inventory").
- **Wayne**, in the NYPD armory, takes Junk. At **300** he crafts one top-tier gun of your
  choice (DE50AE7, HK40, LAW80, MAG, P90 or M10B). The count carries over into EX Game.
- Farming spots: Police Station on Day 3, Museum on Day 5, Chrysler Building in EX Game.
- **Super Junk** (`0x0B`) and **Duper Junk** (`0x0C`) are **worthless** consolation results:
  choosing "Leave it to Wayne" at 300 Junk can hand you one of these instead of a gun
  (RPGClassics).
- **Wayne's 300-Junk guns** (RPGClassics). Ask for a type:

  | Type | Gun | Attack / range / bullets / slots / effects |
  |---|---|---|
  | Pistol | DE50AE7 | 123+2 / 55+1 / 15+2 / 10 / ROF×2 |
  | Shotgun | M10B | 120+1 / 70 / 6+1 / 4 / Burst, ROF×3 |
  | Machine gun | P90 | 122 / 51+2 / 200+1 / 5 / ROF×10, Attack All |
  | Rifle | MAG | 151+1 / 185 / 20+1 / 4 / ROF×2, Critical Up |
  | Grenade launcher | HK40 | 115+1 / 70 / 8+1 / 8 |
  | Rocket launcher | LAW80 | 200+20 / 210 / 1 / 8 |

  "Leave it to Wayne" rolls AK-47, PPsh41, SP1C, USP-TU, or Super/Duper Junk.
- **Best Junk sources:** birds in Central Park and Chrysler floors 2–10 (high drop rate, in
  packs), slimes on Chrysler 61+ (tougher). Frogs (Chinatown sewers) and lizards (Museum) drop
  it too rarely to farm.
- **Trading cards** (corrected; RPGClassics):
  - a **Trading Card** pays for a weapon **tune-up** with Wayne (an extra mod slot), with 2
    in the game (NYPD Day 3, Hospital);
  - a **Rare Trading Card** (the named GSP/P38/… cards, 14 in the Chrysler Building) pays
    for a tune-up worth **two** extra slots;
  - showing Wayne 10 rare cards earns the **Tool Kit** (unlimited Tools), 14 earn the
    **Super Tool Kit** (unlimited Super Tools).

### Tools and modding (decomp `Inv_TransferItemBetweenLists`, guides)

- Guns and armor have **base** stats plus a **+N bonus**, and up to N **mod slots** (effects
  such as burst fire or steal; one per exclusivity group).
- A **Tool** moves either *all* of a donor's +N bonuses (added together, capped at 999) or
  **one mod** (replacing a same-group mod or filling an empty slot) onto another item.
  - With a Tool the donor is destroyed.
  - A **Super Tool** can move more than one attribute, and the donor survives at +0.
- **Tool Kit / Super Tool Kit** are the unlimited versions (count 999 in the game's table).
- The **Mod Permit** (2 from Baker on Day 2) is needed to ask Torres or Wayne for a tune-up.
- **Vanilla Tool supply** (RPGClassics item list):

  | Item | Total | Where |
  |---|---|---|
  | Tool | **48** | 31 in the Chrysler Building (post-game), so **about 17 in the main story**: Hospital 4, Museum 4, Warehouse 2, 1 each in NYPD Day 2, NYPD Day 3, Central Park, Soho Gun Store, Soho Pharmacy, Chinatown Sewers, Subway |
  | Super Tool | **8** | 6 in Chrysler, 1 Subway, 1 Museum |

  Tools also **drop** from the Yellow Rat (NYPD) and can be **stolen** from several bosses
  and big enemies (Worm, Giant Slime/Spider, Alligator, Centipede head, Triceratops,
  Tyrannosaur). A Super Tool can be stolen from the final boss's third form.
- **Stat boosters** (Offense / Range / Bullet Cap / Defense / CR Evade / PE, +1 to +4) are
  mostly in Chrysler. A few are in story areas; Monkey, Dogman and Centipede tail drop some,
  and several bosses can be stolen from.

So in the main story a player gets **about 17 Tools and 2 Super Tools for the whole game**,
which is why people hoard them. The overhaul's Tool pacing should be set against that number.

### What players find frustrating

- Junk clutters the bag, and the 300-Junk payoff is one big cliff with nothing along the way.
- Tools are finite, so you hoard them and never use them.
- Old weapons are useless unless they carry a mod worth moving.
- Most drops are low-value consumables. There is no shop, so no way to target what you want.

---

## 2. What our toolkit can control (verified levers)

| Lever | Status | Used for |
|---|---|---|
| Enemy records in RAM at battle start (`+0x98..0xA2`) | data write ✅ | our own **loot tables**: drop item, steal item, BP formula |
| Battle reward list (10 slots) | data write ✅ | add extra drops (Scrap bundles, Tools) at battle end |
| Aya's bag, Wayne's storage, equipment records | data write ✅ (give-item, Item Editor) | dismantle, crafting results, a Scrap counter |
| Item names / descriptions (string tables) | data ✅ | relabel Junk as Scrap, describe new uses |
| Build-time hooks + pointer redirects | ✅ (tests A/B, Weapon power, Half-bar ATB) | new rows and actions **inside the game's own menus** (Wayne's armory, item menu) |
| F1 mod menu | ✅ | fast prototype UI for shop and dismantle before the in-game UI exists |
| Turn-gauge / battle state | ✅ | optional: reward speed or few hits taken |

So the whole loop can be built without patching game code: the game's own reward plumbing
delivers our drops, and the menus can host our shop.

---

## 3. Proposed economy (draft for discussion)

### 3.1 Currencies

| Currency | Source | Spent on |
|---|---|---|
| **Scrap** (Junk renamed, or kept as "Junk") | every enemy, more from stronger ones; dismantling | crafting, upgrades, buying Tools |
| **Tools** | rare drops, crafting from Scrap, dismantling modded gear | moving or installing mods, +N transfers |
| **Mod chips** (new, virtual) | dismantling an item that has mods; rare drops | installing that mod on any compatible item at the workshop |
| **Blueprints** (optional) | trading cards, story progress, bosses | unlock crafting a specific weapon or armor |

**Junk doesn't take bag slots** (decided: keep the name "Junk", make it a counter). The mod
keeps a count, and picked-up Junk goes straight into it. That fixes the clutter complaint
and lets numbers grow without inventory pain. In this doc "Scrap" just means Junk.

### 3.2 Drops: never pointless, never frustrating

- **Guaranteed base Scrap per kill**, scaled by enemy strength (the enemy's EXP value makes
  a natural yardstick).
- **Skill bonus:** extra Scrap for taking few hits, reusing the game's own BP rule
  (`base − A × hits`).
- **Rare drops** (Tools, mod chips, ammo, consumables) on **tiered tables by area/day**, so
  late areas drop late-game value.
- **Pity timer:** each rare drop gets more likely with every kill that misses, and resets
  when it lands. You never go 200 fights without a Tool.
- **No failure chances in crafting.** Costs are shown up front, so grinding is a known
  distance, not a gamble.

### 3.3 Dismantle (old gear always has value)

Break down any unequipped gun or armor at the workshop for:

- Scrap, based on the item's tier and its +N bonus;
- a **mod chip** for each mod it carries, so you no longer need to find the right donor and
  target pairing at that moment;
- a chance at a Tool for heavily modded items.

Rule: never the equipped item. Bag-capacity mods are guarded, like the Item Editor's check.

### 3.4 Shop / workshop (Wayne, plus an F1 prototype)

| Offer | Cost idea |
|---|---|
| Buy a Tool | flat Scrap price, rising slowly with each purchase |
| Install a mod chip on an item | 1 Tool (or Scrap at a higher rate) |
| +1 to a stat on an item | Scrap, rising with the current +N (soft cap so it stays a sink) |
| Craft a weapon or armor from a blueprint | Scrap + Tools, tiered by item |
| Wayne's 300-Junk reward | kept as a **milestone track** with smaller rewards along the way (100, 200, 300) |

Escalating costs keep Scrap meaningful all game. Milestones turn the 300-Junk cliff into steps.

### 3.5 Example numbers (placeholders only, to tune by playtest)

- Kill: 1–3 Scrap early, 5–10 late; +50% for taking no hits.
- Tool: 40 Scrap.
- +1 attack: 10 × (current +N + 1) Scrap.
- Dismantle: 5 + 2 × (total +N) Scrap, plus chips.
- Pity timer for a Tool drop: guaranteed by about 25 kills.

---

## 4. Build plan (phased)

1. **Research pass (small):**
   - check whether a drop chance is rolled at spawn;
   - find what Super/Duper Junk do;
   - find where Wayne's Junk count and trading-card progress are stored;
   - confirm the donor rule for Tool vs Super Tool (`Inv_TransferItemBetweenLists`, rest of
     the function).
2. **Loot tables + Scrap counter** (data only, battle-start hook): our drop and steal items
   per enemy and area, base Scrap per kill, pity timers, Junk auto-converted to the counter.
   F1 shows Scrap.
3. **F1 Workshop page** (prototype): dismantle, buy Tool, install chip, +N upgrade, craft.
   Same building blocks as the Item Editor, now with costs.
4. **In-game UI:** move the Workshop into the game's own menus (Wayne's armory screen or an
   item-menu "Dismantle" action) using the hook + pointer levers.
5. **Tuning + EX Game:** numbers from playtests; decide what carries over.

---

## 5. Decisions (answered 2026-10-11)

| # | Question | Decision |
|---|---|---|
| 1 | Rename Junk to Scrap? | **No, keep "Junk".** It's the game's own name. "Scrap" elsewhere in this doc means Junk |
| 2 | Junk as a counter or bag items? | **Counter.** Picked-up Junk becomes a count, which frees bag space |
| 3 | Mod chips virtual or real items? | **Open: needs UX research** (section 6) |
| 4 | Where does the shop live first? | **F1 first**, then move to Wayne's screen |
| 5 | How hard is the curve? | **Open: needs balance research** (section 6) |
| 6 | Keep vanilla chest Tools and trading-card rewards? | **Yes, keep vanilla**, so it stays true to the game. The overhaul adds to them and replaces nothing |
| 7 | Difficulty presets on the Workshop page? | **Possible feature**, noted in section 7 |

Overall direction: **research the loot economy before building** any of the economy
features. The Junk counter and the F1 shop shell can come later, once the numbers are
grounded.

---

## 6. Research plan (before building)

### 6.1 Vanilla baseline: what the game gives a player today

Balance needs a baseline, so measure vanilla first.

| Question | How |
|---|---|
| Does an enemy roll a drop chance at spawn, or always drop its item? | Decomp: where enemy records are filled at battle start. Live: watch `+0x9E` across many fresh encounters, not save-state reloads |
| What does each enemy drop and carry for Steal, and what EXP/BP does it give? | Read the enemy records in each area live; check if the decomp/disc has an enemy table to dump in one go |
| How much Junk does a normal playthrough produce? How many Tools and Super Tools (chests), and trading cards? | Chest and pickup lists (guides + room data); Junk per fight × fights per area |
| How many battles per area or day? What are the encounter rates? | Encounter data + guides; a live count on one route |
| What do Super Junk and Duper Junk do? | Decomp: item handlers for `0x0B` / `0x0C` |
| Where is Wayne's Junk count (carries into EX Game) and trading-card progress stored? | Decomp: Wayne's script/menu; the save data |
| Tool vs Super Tool: exact donor and slot rules | Decomp: the rest of `Inv_TransferItemBetweenLists` and its callers |
| How strong are guns per day: base stats, +N, mod slots? | The item base table (already readable) |

The output is a **baseline sheet**: per day or area, the Junk, Tools, cards and gear power
available in vanilla. Every new number is then set relative to it, for example "about 1.5×
vanilla Junk, with a Tool every N fights".

### 6.1a Baseline results so far (2026-10-11)

**Confirmed (decomp, plus live checks in the slot 4 battle save):**

- **Who sets an enemy's rewards:** each enemy's **battle script**, through the "write
  field" command (`Entity_SetField` → `Entity_WriteFieldByCmd`):

  | Command | Field |
  |---|---|
  | `0x28` | EXP value (+0x0E) |
  | `0x5A` | BP base (+0x98) |
  | `0x5B` | BP factor (+0x9A) |
  | `0x5C` | **drop item** (+0x9E) |
  | `0x5D` | **steal item** (+0x9F) |
  | `0x7B`/`0x7C` | loot id / amount |

  Every enemy starts from a blank template (`Entity_AllocSlot`). So drops are **defined per
  enemy by script**, and any drop chance would live in those scripts. The decomp's symbol
  list names `g_DropItem1/2 = 0x800A5DFA / 0x800A5ED6` (slot 0/1 drop fields) with the tag
  "rando": **the PE randomizer already rewrites drops this way**, which is the same lever
  we'd use.
- **EXP vs BP (checked live):**
  - **EXP** per battle = the sum of each enemy's +0x0E value. In the rat fight: 2 + 2 → Aya
    2 → 6 EXP, reaching level 1.
  - **BP** = Σ (`base − factor × hits that enemy landed`), here 3 + 3 = 6. It's **banked**
    (`pe_bonus_pool`, save +0x1E) and paid into bonus points **only on level-up**: 999 + 5
    already banked + 6 = 1010.

  The results screen's "EXP" line shows Aya's new total, not the gain.
- **The results screen** lists the reward list (up to 10 drops) and has ALL / SEL / END for
  taking items. Ammo drops go into the ammo pool (6 + 2×6 = 18 rounds).
- **Item kinds** (from the dumped item table):

  | Kind | Items |
  |---|---|
  | 10 | consumables: medicine, Junk, Super/Duper Junk, trading cards, Mod Permit |
  | 12 | Tool |
  | 13 | Super Tool |
  | 14 | Tool Kit |
  | 15 | Super Tool Kit |
  | 16–18 | ammo |
  | 1–8 | guns / melee |
  | 9 | armor |

  Tool transfers consume kind 12 or 13 from the bag or from Wayne's storage (100 slots at
  `0x800C1EB8`). The kits count as 999 (unlimited).
- **Gear power range** (base attack): handguns up to 123 (DE50AE7), machine guns 122 (P90),
  rifles 34–155 (AK 47), shotguns 48–120 (M10B), grenade launchers 25–115 (HK40), rockets
  128–200 (LAW80), melee 9–100 (Club 1–5). Four of Wayne's 300-Junk guns (DE50AE7, P90, M10B,
  HK40) are their class's strongest by base attack; LAW80 has the highest base attack of
  anything.
- **Full item table:** [data/pe-items-baseline-2026-10-11.csv](data/pe-items-baseline-2026-10-11.csv)
  lists all 235 items with base stats, built-in +N, mod-slot count (`mod_count`) and the mods
  they ship with.

**Loot logger (research tool, PE build):** `Mods > PE Enhancements > Debug > Loot logger`.
When on, it appends to `pe_loot_log.csv` next to the game exe:

- one **enemy** row per enemy: room, identity, start HP, defense, EXP, BP fields, hits it
  landed, drop, steal, whether it died;
- one **battle** row per fight: room, length, EXP and BP totals, rewards;
- **pickup** rows when Aya's count of Junk, Tools, kits, trading cards or the Mod Permit
  changes in the field.

Tested on the rat fight. **Playing normally with it on builds the vanilla baseline sheet**,
and it will show whether the same enemy sometimes drops nothing (the "drop chance" question).

**Wayne's Junk counter (found live 2026-10-11):** script variable **`0x800A78B0`**
(`g_EntityWorkBuffer + 0xC0`, a halfword). Handing Wayne 1 Junk in the Day 3 NYPD save took
it from 0 to 1. Nothing else changed apart from the bag slot. It lives in the saved
script-variable area, which fits it carrying over into EX Game. The mod can read Wayne's
progress toward 300 from it (Workshop display, milestone rewards).

**Logger data so far** (your play sessions, about 17 battles, 40+ real enemies):

- **Every enemy has a drop, picked at random from a per-room pool.** The same 5-enemy fight
  in room 0x80C8 dropped Junk ×5 once and Junk ×3 + Medicine 1 ×2 the next time. **"Nothing"
  is in some pools**: 1 rat out of about 40 enemies dropped nothing.
- **Overall drops:** AMMO 6 about 40%, Junk about 35%, Medicine 1 about 15%, AMMO 15 about
  8%. One room (0x80C8) gives about 80% Junk. **Steal pools are a step up** (Medicine 2,
  Cure P, Junk).
- **Per-enemy values:** about 1–12 EXP for early enemies, 39 for the police-station brute
  (species 0x11, 98 HP, BP 15 − 10 per hit).
- **Junk pace:** about 1 per 3 kills overall, about 1 per kill in the best room, so Wayne's
  300 is roughly 300–900 kills.

**Resolved from guides:** Super/Duper Junk are worthless "Leave it to Wayne" results; vanilla
Tool supply is about 17 in the main story (48 total); trading cards pay for mod-slot tune-ups
(section 1).

**Still to find:**

- the exact donor rule for Tool vs Super Tool (rest of `Inv_TransferItemBetweenLists`);
- chest Tool locations and counts per day (guides);
- battles per area (the logger will give this).

### 6.2 Mod chips: UX options to compare (decision 3)

| Option | How it plays | Pros | Cons |
|---|---|---|---|
| **A. Virtual chip library** (stored by the mod, shown on the Workshop page) | Dismantling files the mod into a library; install it later on any compatible item | No bag clutter, easy to browse, matches the counter approach for Junk | Invisible outside F1 until the Wayne UI exists; needs save-file handling (see below) |
| **B. Real bag items** (reuse spare item IDs such as `ITEM24/25`) | A chip is an item you carry and use, like a Tool | Feels native, lives in the game's own save, visible in the bag | Takes bag slots (the clutter we're removing); limited spare IDs; needs names and icons |
| **C. No chips: keep vanilla's donor → target transfer, made cheaper** | Dismantle gives Junk only; moving mods still needs a donor, but Tools are easier to get | Closest to vanilla, least new UI | Doesn't fix "old gear is useless"; the donor pairing stays fiddly |
| **D. Hybrid: chips stored in Wayne's storage as items** | Chips are items, but they go straight to storage instead of the bag | Native and saved, no bag clutter | Depends on Wayne's storage capacity; only usable at Wayne's |

Research questions:

- **Where would A's data persist?** Plugin memory isn't saved with the game. It would need
  a small save area of its own, or spare bytes in the game's save that we can verify are
  unused.
- **Are `ITEM24/25` really unused?** Can chip names be drawn from the mod table, as Weapon
  power does?
- **What does a good loop look like?** Look at how other games handle "salvage → reusable
  upgrade": FF7 materia, FF8 refine/junction, Resident Evil 4 upgrades, Borderlands/Diablo
  salvage. The target feel: one action to dismantle, one action to install, always shown
  in the game's own words.

### 6.3 Balance targets (decision 5)

Settle these after the baseline:

- **Pace:** how many fights per Tool, per +1 upgrade, and per crafted top-tier gun, at each
  stage of the game.
- **Never pointless:** every fight should give at least some Junk. The test: no fight in a
  normal route gives zero progress.
- **Never frustrating:** the longest dry streak for a rare drop is capped (pity timer); no
  random failure in crafting.
- **No trivialising:** escalating costs and per-area drop tiers, so early grinding can't
  buy late-game power.
- **True to vanilla:** vanilla chest Tools, trading cards and the 300-Junk gun stay as they
  are, and the new economy adds on top (decision 6). Junk spent at the workshop shouldn't
  undercut Wayne's 300 milestone. One question to settle: is there a separate workshop
  balance, or do both draw from one Junk count?

---

## 7. Possible features (not committed)

- **Difficulty presets on the Workshop page** (decision 7): *Relaxed / Normal / Grind*.
  Each scales Junk per kill, rare-drop chance, pity length and workshop prices together, so
  players pick a pace without touching individual numbers.

Sources: decomp `Battle_StepEntityAnimState.c`, `Battle_ResolveHitOnTimer.c`,
`Menu_MainUpdate.c`, `Menu_LevelUpFlow.c`, `Inv_ItemActions.c`, `Inv_ArmorCapacity.c`,
`include/pe1/item_ids.h`; guides:
[RPGClassics — Junk](https://shrines.rpgclassics.com/psx/pe/junk.shtml),
[RPGClassics — Items](https://shrines.rpgclassics.com/psx/pe/items.shtml),
[Almar's Guides — Weapons from Junk](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/weaponsfromjunk/),
[Almar's Guides — Day 3](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/day3/),
[Almar's Guides — EX Game](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/exgame/),
[Parasite Eve Wiki — Weapons](https://parasiteeve.fandom.com/wiki/Parasite_Eve_Weapons).
