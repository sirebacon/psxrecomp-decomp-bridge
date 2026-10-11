# Parasite Eve loot overhaul: drops, scrap, tools, dismantle and shop (design draft, 2026-10-11)

A discussion document for reworking Parasite Eve's loot loop into a "craft what you want,
but earn it" system. It covers how the game works today (decomp + guides), what our mod
toolkit can control, a proposed economy, and the decisions we still need to make. Nothing
here is built yet.

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
(a medicine), steal item `0x01`, and BP `5 − 2 × hits taken`.

**Still to check:** whether the game rolls a *drop chance* when an enemy spawns, which would
set `rewardSlotId` to 0 most of the time. Guides describe Junk as a common but not
guaranteed drop, which suggests a roll somewhere in the encounter data.

### Junk and Wayne (guides: Almar's Guides)

- **Junk** (item `0x14`, "Broken Item") drops from many enemies and can be stolen from some.
  It takes up bag space ("clogs up your inventory").
- **Wayne**, in the NYPD armory, takes Junk. At **300** he crafts one top-tier gun of your
  choice (DE50AE7, HK40, LAW80, MAG, P90 or M10B). The count carries over into EX Game.
- Farming spots: Police Station on Day 3, Museum on Day 5, Chrysler Building in EX Game.
- The item list also has **Super Junk** (`0x0B`) and **Duper Junk** (`0x0C`), "Helps Item".
  What they do in vanilla is unknown (to check).
- **Trading cards:** each named card (GSP, P38, BHAWK…, 14 in all) gets a specific gun from
  Wayne. All 14 earn the **Super Tool Box**, an unlimited Super Tool.

### Tools and modding (decomp `Inv_TransferItemBetweenLists`, guides)

- Guns and armor have **base** stats plus a **+N bonus**, and up to N **mod slots** (effects
  such as burst fire or steal; one per exclusivity group).
- A **Tool** moves either *all* of a donor's +N bonuses (added together, capped at 999) or
  **one mod** (replacing a same-group mod or filling an empty slot) onto another item.
  - With a Tool the donor is destroyed.
  - A **Super Tool** can move more than one attribute, and the donor survives at +0.
- **Tool Kit / Super Tool Kit** are the unlimited versions (count 999 in the game's table).
- The **Mod Permit** (from Baker on Day 2) unlocks modding.
- Tools come from **chests**, a fixed supply. Enemies don't drop them.

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

**Scrap doesn't take bag slots.** The mod keeps it as a counter: picked-up Junk is turned
straight into the counter. That fixes the clutter complaint and lets numbers grow without
inventory pain.

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

## 5. Decisions needed

1. Keep the name "Junk", or rename it to "Scrap" in the game's text?
2. Should Scrap live **only as a counter** (no bag item), or as stackable bag items?
3. Should mod chips be **virtual** (stored by the mod), or real bag items we invent?
4. Where does the shop live first: **F1 only**, or straight into Wayne's armory?
5. How hard should the curve be? Pick one target, for example "one Tool every ~2 areas"
   or "a top-tier gun by Day 5 with focused grinding".
6. Keep vanilla's fixed chest Tools and trading-card rewards alongside the new economy?
7. Separate difficulty presets (Relaxed / Normal / Grind) on the Workshop page?

Sources: decomp `Battle_StepEntityAnimState.c`, `Battle_ResolveHitOnTimer.c`,
`Menu_MainUpdate.c`, `Menu_LevelUpFlow.c`, `Inv_ItemActions.c`, `Inv_ArmorCapacity.c`,
`include/pe1/item_ids.h`; guides:
[Almar's Guides — Weapons from Junk](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/weaponsfromjunk/),
[Almar's Guides — Day 3](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/day3/),
[Almar's Guides — EX Game](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/exgame/),
[Parasite Eve Wiki — Weapons](https://parasiteeve.fandom.com/wiki/Parasite_Eve_Weapons).
