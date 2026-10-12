# Parasite Eve loot overhaul: drops, Junk, tools, dismantle and shop (design draft, 2026-10-11)

A discussion document for reworking Parasite Eve's loot loop into a "craft what you want,
but earn it" system. It covers how the game works today (decomp + guides), what our mod
toolkit can control, a proposed economy, and the decisions we still need to make. Nothing
here is built yet.

**Status (2026-10-11):** design complete: decisions 1–41 in section 5 (custom items in
their own doc). Build order in section 4, progress in
[`pe-loot-overhaul-checklist.md`](pe-loot-overhaul-checklist.md). Section 3 is the early
draft and is superseded where the decisions differ.

**Goals (from the discussion):**

- Craft the gear and mods you actually want, but it costs effort.
- Grinding must never feel **pointless** (every fight pays something useful) or
  **frustrating** (no long dry streaks, no all-or-nothing gambles).
- Old gear shouldn't be dead weight. Today it only matters if it carries mods you can move.
- A clear economy for **Junk** (dropped by enemies) and **Tools** (spent on mods).

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

**Resolved (6.1a):** each enemy's battle script picks its drop from a **per-room random
pool** when the battle starts, and some pools include "nothing". Death itself rolls nothing.

### Junk and Wayne (guides: Almar's Guides)

- **Junk** (item `0x14`, "Broken Item") drops from many enemies and can be stolen from some.
  It takes up bag space ("clogs up your inventory").
- **Wayne**, in the NYPD armory, takes Junk. At **300** he crafts one top-tier gun of your
  choice (DE50AE7, HK40, LAW80, MAG, P90 or M10B). The count carries over into EX Game.
- Farming spots: Police Station on Day 3, Museum on Day 5, Chrysler Building in EX Game.
- **Super Junk** (`0x0B`) and **Duper Junk** (`0x0C`) are called **worthless** consolation results by the guides, but the decomp disagrees: using them restores **1/4** and **1/2 of max Parasite Energy** (`Battle_ApplyDamage`). They are PE recovery items, not junk:
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
  - **Confirmed in the decomp** (`Inv_TransferItemBetweenLists`, the `!(flags & 1)` branch):
    a plain **Tool deletes the donor item** (its loaded rounds go back to the ammo pool). A
    **Super Tool keeps the donor**, which only loses what was moved.
  - Each use spends one Tool (kind 12) or Super Tool (kind 13), taken from the bag or from
    Wayne's storage.
  - Because a same-group mod on the target is **overwritten**, a Super Tool doubles as
    "remove a mod": move the unwanted mod onto a throwaway gun and the main gun keeps an
    empty slot. A forum answer describes exactly this for removing ROF×10 from a P90.
- **Where it happens:** in Aya's own menu ("Tune Up Weapon/Armor"), not at Wayne's. Wayne
  only **adds slots** (trading-card tune-ups). Players find this confusing: Wayne talks about
  upgrades, his "Slot is full" message reads like a bug, and nothing in the game explains
  Tools, Super Tools or why ROF×10 lowers damage per shot (our damage formula: shot% 13 at
  10 shots).

**UX lessons for the overhaul** (from forum complaints): every action should say in plain
words what it costs and what it destroys; show the effect of a mod (for example damage per
turn, as Weapon power does) before applying it; give "remove a mod" its own clear action
instead of a Super Tool trick; and have Wayne's screen explain what he does and doesn't do.
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

### Encounters and the steal-and-flee exploit (community, r/ParasiteEve guide by GF_Eden, 2024)

- **Encounter rate per trigger spot** (from the official Japanese guide): 100% the first time,
  then 45%, 20%, and 10% after that. **Winning** a fight lowers the rate; **fleeing** leaves
  it "unresolved", so a first-time fight stays at 100%.
- **The exploit:** steal Junk from crows with Club 2, flee, step back on the trigger, repeat.
  The Day 3 precinct corridor fight near Wayne's stairs makes an infinite Junk tap (one crow
  in a first playthrough, two in EX Game). Players get the AK at the start of Day 4 in
  **2–6 hours** and call it "game-breaking"; without it, the grind takes "real days" and many
  never get a Wayne gun.
- **Wayne crafts only from Day 4**, after he takes over Torres's job; Junk handed in earlier
  counts, and the next hand-in from Day 4 triggers the craft (matches our live tests).
- For the overhaul: normal-route battles get scarcer as fights are won, which bounds Junk
  from EXP; and any Junk paid during a battle must not survive a flee (decision 35).

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
| Battle reward list (10 slots) | data write ✅ | add extra drops (Junk bundles, Tools) at battle end |
| Aya's bag, Wayne's storage, equipment records | data write ✅ (give-item, Item Editor) | dismantle, crafting results, a Junk counter |
| Item names / descriptions (string tables) | data ✅ | relabel Junk as Junk, describe new uses |
| Build-time hooks + pointer redirects | ✅ (tests A/B, Weapon power, Half-bar ATB) | new rows and actions **inside the game's own menus** (Wayne's armory, item menu) |
| F1 mod menu | ✅ | fast prototype UI for shop and dismantle before the in-game UI exists |
| Turn-gauge / battle state | ✅ | optional: reward speed or few hits taken |

So the whole loop can be built without patching game code: the game's own reward plumbing
delivers our drops, and the menus can host our shop.

---

## 3. Proposed economy (early draft, superseded where the decisions differ)

> **Read section 5 first.** Differences from this draft: no "mod chips" items or
> blueprints (the Mod Codex replaced them); **Wayne's 300 gun stays vanilla** (no 100/200
> milestone track); Junk per battle uses the battle's EXP plus a floor (16, 17); the
> "skill bonus" Junk and "+1 stat for Junk" offers below were **never decided**; the pity
> timer covers a rare table, not just Tools (18).

### 3.1 Currencies

| Currency | Source | Spent on |
|---|---|---|
| **Junk** (Junk renamed, or kept as "Junk") | every enemy, more from stronger ones; dismantling | crafting, upgrades, buying Tools |
| **Tools** | rare drops, crafting from Junk, dismantling modded gear | moving or installing mods, +N transfers |
| **Mod chips** (new, virtual) | dismantling an item that has mods; rare drops | installing that mod on any compatible item at the workshop |
| **Blueprints** (optional) | trading cards, story progress, bosses | unlock crafting a specific weapon or armor |

**Junk doesn't take bag slots** (decided: keep the name "Junk", make it a counter). The mod
keeps a count, and picked-up Junk goes straight into it. That fixes the clutter complaint
and lets numbers grow without inventory pain. In this doc "Junk" just means Junk.

### 3.2 Drops: never pointless, never frustrating

- **Guaranteed base Junk per kill**, scaled by enemy strength (the enemy's EXP value makes
  a natural yardstick).
- **Skill bonus:** extra Junk for taking few hits, reusing the game's own BP rule
  (`base − A × hits`).
- **Rare drops** (Tools, mod chips, ammo, consumables) on **tiered tables by area/day**, so
  late areas drop late-game value.
- **Pity timer:** each rare drop gets more likely with every kill that misses, and resets
  when it lands. You never go 200 fights without a Tool.
- **No failure chances in crafting.** Costs are shown up front, so grinding is a known
  distance, not a gamble.

### 3.3 Dismantle (old gear always has value)

Break down any unequipped gun or armor at the workshop for:

- Junk, based on the item's tier and its +N bonus;
- a **mod chip** for each mod it carries, so you no longer need to find the right donor and
  target pairing at that moment;
- a chance at a Tool for heavily modded items.

Rule: never the equipped item. Bag-capacity mods are guarded, like the Item Editor's check.

### 3.4 Shop / workshop (Wayne, plus an F1 prototype)

| Offer | Cost idea |
|---|---|
| Buy a Tool | flat Junk price, rising slowly with each purchase |
| Install a mod chip on an item | 1 Tool (or Junk at a higher rate) |
| +1 to a stat on an item | Junk, rising with the current +N (soft cap so it stays a sink) |
| Craft a weapon or armor from a blueprint | Junk + Tools, tiered by item |
| Wayne's 300-Junk reward | kept as a **milestone track** with smaller rewards along the way (100, 200, 300) |

Escalating costs keep Junk meaningful all game. Milestones turn the 300-Junk cliff into steps.

### 3.5 Example numbers (placeholders only, to tune by playtest)

- Kill: 1–3 Junk early, 5–10 late; +50% for taking no hits.
- Tool: 40 Junk.
- +1 attack: 10 × (current +N + 1) Junk.
- Dismantle: 5 + 2 × (total +N) Junk, plus chips.
- Pity timer for a Tool drop: guaranteed by about 25 kills.

---

## 4. Build plan (decided 2026-10-11, decisions 29–30)

Progress is tracked in [`pe-loot-overhaul-checklist.md`](pe-loot-overhaul-checklist.md).

The earlier draft plan is replaced by this order. The research it listed is done (sections
6.1–6.7): drops come from per-room random pools picked at battle start, Super/Duper Junk
restore PE, Wayne's counter is `0x800A78B0`, and the Tool donor rule.

Each phase is playable on its own; numbers are placeholders until phase 7.

| Phase | What gets built | Playable result | Needs first |
|---|---|---|---|
| **0. Prep** | Test the Wayne refund (`pe_wayne_refund.c`). Temporary log of `Inv_DispatchCommand` during a hand-in. Logger fixes: session marker, skip identity-0 rows, steal logging | Refund verified, Junk-counter hook confirmed, clean data | One build with the game closed |
| **1. Junk counter** | Master switch, on by default (28). Junk counter saved in the save tail and a save-state block (6.4). `Aya_SetTotalExp` hook: vanilla Junk + floor + EXP-scaled Junk, toast (16, 17, 21, 24). Chest Junk → counter (20). Wayne hand-in through `Inv_DispatchCommand` (6.5). F1 Workshop page with the Junk total. **Debug → Loot tuning page** (30) | Junk never takes bag space; Wayne's 300 gun works from the counter | New `game.toml` hooks: 0x8004B70C, 0x8005D2B4, 0x80053D2C, save/load |
| **2. Rare drops** | Rare roll with soft pity, rare table on the "items found" screen, pity in F1 (18, 23) | Lucky drops | Phase 1 |
| **3. Codex** | Dismantle (F1 row first), Codex with greyed previews, installs priced in Junk/Tools, buy-back with the 150 cap (9–12, 26) | Craft what you want | Phase 1 |
| **4. Shop** | F1 shop: consumables, ammo, Tools 40 → 100 cap (14) | Junk always has a use | Phase 1 |
| **5. Native menus** | Aya's item menu: Dismantle + Combine actions, Junk in the title (25, C10, 22). Wayne: "Discard junk (N)", Shop and Buy-back rows (22, 27). Later the native "items found" Junk line (21) | Feels part of the game | Menu research: item action list, Wayne's choice list |
| **6. Custom content** | Scavenger, Lucky Find, Salvager, Bargain; Smoke Grenade; Lucky Charm (custom items doc); empty-steal Junk (19) | The extras | Research: dummy effects, escape, steals |
| **7. Balance** | All numbers from logger data, set as defaults; difficulty presets if wanted (7) | Tuned pace | A logged play session |

**Debug → Loot tuning (decision 30):** number rows for Junk per EXP, the floor, the
per-battle cap, pity base chance, step and guarantee, rare table shares, and prices. They
can be changed live during playtests (F1 pauses the game). The settled values become the
code defaults in phase 7.
---

## 5. Decisions (answered 2026-10-11)

| # | Question | Decision |
|---|---|---|
| 1 | Rename Scrap to Junk? | **No, keep "Junk".** It's the game's own name. "Junk" elsewhere in this doc means Junk |
| 2 | Junk as a counter or bag items? | **Counter.** Picked-up Junk becomes a count, which frees bag space |
| 3 | Mod chips virtual or real items? | **Resolved: virtual, the "Mod Codex"** (option A, section 6.2a), shaped by decisions 9–12 and 26 |
| 4 | Where does the shop live first? | **F1 first**, then move to Wayne's screen |
| 5 | How hard is the curve? | **Set in phase 7 from logger data** (section 6.3), under the user's caps (buy-back ≤ 150, Tools ≤ 100) |
| 6 | Keep vanilla chest Tools and trading-card rewards? | **Yes, keep vanilla**, so it stays true to the game. The overhaul adds to them and replaces nothing |
| 7 | Difficulty presets on the Workshop page? | **Possible feature**, noted in section 7. **Superseded by decision 39: presets are in** |
| 8 | What if "Leave it to Wayne" rolls Super/Duper Junk? | **Refund the 300 Junk** so the player can try again, and **keep** the Super/Duper Junk (it restores 1/4 / 1/2 PE). Built as its own toggle, "Wayne junk refund" (PE `pe_wayne_refund.c`, on by default), 2026-10-11 |
| 9 | What do vanilla Tools become? | **Keep their vanilla job** (moving an effect or a stat bonus; the Codex covers effects only, so stat bonuses still need Tools, and Super Tools keep their "donor survives" niche). **Premium Codex installs** (Command ×2/×3, Attack All, maybe ROF ×10) cost Junk **plus one Tool**; all other installs cost Junk only |
| 10 | How does the Codex fill? | **Dismantling only**, so "keep the gun or bank its effect" stays a real choice. Effects on gear you carry show **greyed out** in the Codex ("dismantle to unlock"), so nothing is a surprise |
| 11 | Where do Codex installs work? | **Anywhere** (Aya's menu / F1), like vanilla tune-ups; Days 5–6 and the Chrysler Building keep you away from the precinct for long stretches. **Wayne stays the gunsmith:** Junk hand-ins, 300-Junk guns, trading-card slot tune-ups, later a Workshop front end in his menu |
| 12 | Can a dismantled gun be bought back? | **Yes, for Junk** (user's request, 2026-10-11). Rules proposed in 6.2b: the gun returns with its stats and +bonuses but **empty mod slots** (its effects already sit in the Codex, and reinstalling costs the normal price), and the buy-back price is above what dismantling paid, so dismantle-and-buy-back is never a profit loop. **Capped at 150 Junk** (user) so buying back always stays worth it |
| 13 | One Junk counter or two? | **One shared counter** (user, 2026-10-11). The mod's counter is the only spending pool. Junk reaches Wayne only when you hand it in ("Discard junk", through the hand-in hook in 6.5), so every Junk is either progress toward his 300 gun or Codex/shop spending, like vanilla where handed-in Junk is gone |
| 14 | What does the F1 shop sell? | **Consumables + ammo + Tools** (user). Tools at a steep, rising price (start around 40 Junk, more each purchase), so premium installs are never hard-capped before the trading-card Tool Kit. **Tool price is capped** (user, 2026-10-11): proposed 40 Junk, +10 per purchase, **never above 100 Junk** (a third of a Wayne gun), so a premium install stays at roughly 200 Junk or less, all in. Numbers tuned in 6.3. **Not sold:** Super Tools (the Super Tool Kit stays special), guns and armor (finds and Wayne) |
| 15 | What carries into EX Game? | **Everything** (user): the Junk counter, the Codex and the buy-back list, as vanilla carries Wayne's count and storage. To verify in testing: the EX Game save goes through `Save_BuildCardFile`, so the save-tail data rides along |
| 16 | A Junk floor per battle? | **Yes: every won battle gives at least 1 Junk** (user, 2026-10-11), plus the amount from decision 17. Fleeing gives nothing, as in vanilla |
| 17 | What decides how much Junk? | **The enemies' EXP** (user). Tougher and later enemies already give more EXP, so Junk scales by area and toughness with no per-species table; bosses pay a big chunk. Formula and divisor tuned in 6.3 |
| 18 | Can enemies drop Tools? | **Yes, rarely, with a pity timer** (user): a small chance per won battle, guaranteed after N battles without one. **Soft pity** (user, 2026-10-11): the chance creeps up each dry battle until the guarantee. Only won battles count; only enemy drops reset it (chest and shop Tools don't). **The roll draws from a "rare" table** (accepted by the user "for now", 2026-10-11; no extra Tool guarantee, since the capped shop covers dry spells): Tool ~40%, stat booster ~35% (6 kinds, tier 1–4 by area via the EXP scale), Super/Duper Junk ~15%, Mod Permit ~7%, Super Tool ~3%. Excluded: trading cards, guns/armor, Tool Kits, key items, medicine. Shares and chances tuned in 6.3 |
| 19 | What does an empty steal give? | **A little Junk** (user). Vanilla steal items stay; when the enemy has nothing to steal, a steal gives a small Junk amount so steal builds are never wasted |
| 20 | Junk from chests and story pickups? | **Straight into the counter** (follows from decision 2) |
| 21 | How is Junk earned in battle shown? | **An engine toast first** ("+3 Junk · 147"), **later a native line** on the game's "items found" screen (one Junk entry relabelled "Junk ×3", picked up into the counter) as polish (user, 2026-10-11) |
| 22 | Where is the Junk total shown? | **All three** (user): a "Junk" row at the top of the F1 Workshop page; Wayne's menu relabels "Discard junk" as **"Discard junk (147)"**; and Aya's item menu title bar shows the total |
| 23 | Is Tool pity progress visible? | **Yes, on the F1 Workshop page** ("Tool guaranteed within N battles") (user) |
| 24 | How often do Junk toasts appear? | **After every won battle**, plus Tool drops and steal Junk (user) |
| 25 | Where does Dismantle live? | **Aya's item menu**: a "Dismantle" action on a selected gun or armor, with a confirm prompt (user, 2026-10-11). Fits the character: an NYPD officer field-strips guns, and vanilla already has Aya do her own tune-ups with Tools in her menu. F1 row until the menu action exists |
| 26 | Where does the Codex live? | **The F1 Workshop page** (user). F1's list rows handle 35+ effects, greyed previews and prices, and work anywhere (decision 11). No new game screen |
| 27 | Final home for the shop and buy-back? | **Both move to Wayne's menu** (user), after starting in F1 (decision 4) |
| 28 | Is the overhaul on by default? | **On by default for a new playthrough** (user), with one master switch on the Workshop page. Switching mid-playthrough is not encouraged (Junk counter conversion), so the choice is made at the start |
| 29 | Build order? | **Phases 0–7 as in section 4** (user, 2026-10-11): prep, Junk counter, rare drops, Codex, shop, native menus, custom content, balance |
| 30 | Live tuning? | **Yes: a Debug → Loot tuning page from phase 1** (user), so playtests can change the numbers without rebuilding |
| 31 | What does Wayne's label show? | **Both numbers** (user, review 2026-10-11): **"Discard junk (147 · 120/300)"**, your Junk and Wayne's progress toward his next gun. Refines decision 22 |
| 32 | A skill bonus for taking few hits? | **Yes, small** (user): e.g. +25% battle Junk for a no-hit battle, scaled down with hits taken. Reuses the game's own "hits that enemy landed on Aya" count (`+0x9C`, the bonus-point rule), summed over the battle's enemies |
| 33 | Can Junk buy +1 stat upgrades? | **No** (user). Stat bonuses stay with stat boosters (rare table, vanilla) and Tools moving +N, so both stay valuable |
| 34 | Pace target for Wayne's guns? | **Vanilla's Day 4 gate stays the ceiling** (Wayne can't craft before he takes over Torres's job: live test, Day 3 never crafts). On the **normal route, without exploits**, the first Wayne gun should be affordable **around Day 4–5 with roughly 1–2 hours of optional fighting** (user). Today it takes 2–6 hours even with the steal-and-flee exploit, and "real days" without it |
| 35 | Steal Junk vs steal-and-flee? | **Banked, paid only on a win** (user). Empty-steal Junk (decision 19) is held during the battle and added at the battle-end hook; fleeing forfeits it, consistent with "fleeing gives nothing". Vanilla steal items are unchanged (decision 6). Closes an infinite-Junk loop (see 1, "Encounters and the steal-and-flee exploit") |
| 36 | How do we prevent soft-locks (no ammo, everything dismantled)? | **Guards plus a rescue** (user, 2026-10-11). **Dismantle guards:** never the equipped gun or armor; never the **last Club** (melee, needs no ammo); a warning (not a block) before dismantling the last gun for an ammo type you carry. **Rescue:** when Aya can't attack (no melee weapon, and no gun with loaded rounds or spare ammo of its type), the Workshop offers a **free Club 1** ("NYPD service baton") and the shop's **basic handgun ammo box costs 0 Junk** until she has ammo again, with a toast pointing to it. Breaks the no ammo → no wins → no Junk → no ammo loop, including vanilla routes into it (e.g. a discarded Club) |
| 37 | Names and wording? | **As in section 6.8** (user, 2026-10-11): the Codex is the **Mod Catalog**, buy-back is **Rebuild**, the shop is **Requisition**, and the custom mods use **PE-style descriptions** in game. The working names (Codex, buy-back, shop) stay in these docs |
| 38 | The Item Editor with the overhaul on? | **Unchanged, a debug tool** (user, 2026-10-11). It can install mods for free, around the Mod Catalog; no note, no hiding. The other cheats (Infinite ammo, God mode, No random battles) also stay as they are |
| 39 | Difficulty presets? | **Yes: Relaxed / Normal / Grind** (user), one row on the Workshop page, **switchable at any time**: the player decides how they want to play, e.g. Normal but harder or easier for a stretch. Presets only scale numbers (Junk per battle, rare-drop pity length, Requisition / Mod Catalog / Rebuild prices), so switching converts nothing. **Not touched:** Wayne's 300, vanilla drops and chests. Default **Normal**. No Custom preset (the Debug tuning page covers that). Example values in 6.3, set in phase 7. Replaces decision 7's "possible feature" |
| 41 | Stolen Junk with the counter? | **Banked until a win** (user, 2026-10-11, found while building phase 0). A steal adds its item mid-battle through `Inv_AddItem` (from `Battle_ResolveHitOnTimer`). Stolen **Junk** is held and added to the counter at the battle-end hook only on a win; fleeing forfeits it. Other stolen items stay vanilla. Without this, the counter would remove the bag limit that slows vanilla's steal-and-flee loop |
| 40 | Do the price caps change with the preset? | **No: fixed on every preset** (user). Tools ≤ 100 and Rebuild ≤ 150 everywhere, so Grind can't get crazy; Relaxed can go below them |

**Resulting layout:**

- **Aya's item menu:** Combine (C10), Dismantle (25), Junk total in the title bar (22).
- **Wayne's menu:** "Discard junk (147)" (22), Shop and Buy-back rows (27, after F1).
- **F1 → PE Enhancements → Workshop:**
  - the master switch (28);
  - Junk total and Tool pity (22, 23);
  - **Codex** (26);
  - **Shop** and **Buy-back** until they move to Wayne (27);
  - the Dismantle row until the Aya's menu action exists (25).

Overall direction: build in the phase order of section 4, with placeholder numbers that are
tuned live (decision 30) and settled in phase 7.

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

**Gear progression and enemy names** (GameFAQs guide by mysticcat, tables extracted
2026-10-11). [data/pe-gear-locations-2026-10-11.csv](data/pe-gear-locations-2026-10-11.csv)
lists every gun and armor with its stats, special effect and **where it's found**. A few
cells the guide garbled are marked `?`. In story order, the best base attack Aya can find:

| Area (day) | Notable finds | Best attack so far |
|---|---|---|
| Start / Carnegie Hall (1) | M84F 12, P220 15, M1911A1 17; N Protector, Kv Vest 1 | ~17 |
| Central Park (2) | M9 17, P8 19, M203 27; Sp/Sv Vest 1 | ~27 |
| NYPD (2–3) | M92F 29, M9-2 39, M16A1 35, SG550 40, MP5K 36; N Jacket, Cm Vest 1/2 | ~40 |
| Soho (3) | G19 32, M11 33, **Club 2 (Steal)**; Cr Vest 1 | ~40 |
| Hospital (4) | G23 48, G3A3 44, M10/Micro/Mini UZ 38–49, M79 45; B Vest 1, Sp Jacket | ~49 |
| Day 5 (Chinatown, Warehouse, Sewer, Subway, Museum) | M1911A2 48, PPK 47, MA10 49, M500 59, M8000 57, M9-3 55, MP5PDW 53, **AT4 128**; N Suit, Sv/Cr/B armors | ~59 (128 rocket) |
| Wayne, 300 Junk | DE50AE7 125, M10B 121, P90 122, MAG 152, HK40 115, LAW80 220 | 115–220 |
| Chrysler (EX Game) | most guns and armor at 60–120 | ~120 |

So Wayne's 300-Junk guns are worth about **2× anything the main story hands out**. That's
why the 300-Junk grind matters, and why the overhaul's crafting must not let early grinding
skip that curve.

**Enemy names for the logger's species ids**, matched by HP to the guide's monster list:

| Id | Enemy | Notes |
|---|---|---|
| 0x02 | Red Rat | 12–21 HP, Carnegie Hall |
| 0x08 | Bird | 35–62 HP, Central Park / NYPD; the Junk droppers |
| 0x0A | Monkey | 57–102 HP, Central Park |
| 0x0C | Bear | 75–134 HP, Central Park |
| 0x11 | Dog-Men | 98–176 HP, NYPD |

The guide gives each monster's HP range, weaknesses and locations for all 29 regular
enemies. The same species shows different HP in different rooms, which matches the logger.

**Resolved from guides:** Super/Duper Junk are the consolation "Leave it to Wayne" results (the decomp shows they restore 1/4 / 1/2 PE, so not truly worthless); vanilla
Tool supply is about 17 in the main story (48 total); trading cards pay for mod-slot tune-ups
(section 1).

**Still to find:**

- chest Tool locations and counts per day (guides);
- battles per area (the logger will give this).

### 6.1b Mod effects in numbers (decomp, 2026-10-11)

Names are the game's own (mod string table: entries 0–19 = gun effects 1–20, entries 20–34 =
armor effects 1–15, 35–39 "dummy"). Numbers come from `Inv_BuildWeaponList`, `Battle_Init`,
the damage code (`Battle_StepEnemyMovement.c`) and `BattleCmd_LoadWeaponModifiers`.

**Gun effects**

| # | Name | What it does (numbers) |
|---|---|---|
| 1–5 | Rate of Fire 2 / 3 / 5 / 7 / 10 | Shots per command 2/3/5/7/10 at 60/41/25/18/13% each, so **×1.20 / ×1.23 / ×1.25 / ×1.26 / ×1.30 raw damage per turn**. Uses that many bullets. Enemy defense ÷ shots comes off each shot, so about one full defense per volley |
| 6 | Random Rate of Fire 1–5 | Volley of shots×1.5 hits on **random** targets |
| 7 | Burst: spray multiple targets | Cone of hits on nearby targets |
| 8 | Attack All Enemies w/ ROF | One hit on **every** target; defense isn't divided |
| 9 / 10 | Heat / Frost | Element: **×1.5** on weak enemies, **÷5** on resistant ones |
| 11 / 12 / 13 | Cyanide / Acid / Tranquilizer | Status on hit: **50%** on normal enemies, 100% on vulnerable ones, 0 on immune ones |
| 14 | Counterattack | after an enemy hits Aya, a **chance of a free counter-shot** at it (`Battle_Update` → `Battle_RollEnemySpawn`, misnamed). The chance scales with her agility bonus and drops against higher-rank enemies |
| 15 | Quickdraw | at battle start, a chance (Aya's stat +0x22, in percent) that her **bar starts full** (gauge 9000; `Battle_CheckDropChance`, misnamed) |
| 16 | Steal Items, but halves attack | Steal on hit; **attack ÷2** |
| 17 | Steal During Attack | Steal on hit, no attack penalty |
| 18 | Critical Percentage Increases | in range, crit chance is 50% / 20% / 5% (near / mid / far); this adds **+20 points** to each, so 70 / 40 / 25 (`Battle_CheckEvasion`, misnamed) |
| 19 / 20 | Enter 2 / 3 Commands | **2 / 3 full volleys per turn** (`Battle_Init`: commands = effect bits 4–5), so **×2 / ×3 damage and ammo per turn**, the strongest effects |

**Armor effects**

| # | Name | Numbers |
|---|---|---|
| 1–4 | Resist Poison / Stiffness / Darkness / Confusion | a **chance** to ignore the attack, not immunity: poison 70%, stiffness 50% (lock) / 70% (slow), darkness 60%, confusion 60% (decomp `battle_ailment.h`, added 2026-10-11) |
| 5 | Decreases Items Stolen | 60% chance an enemy steal fails |
| 6 / 7 | Uses Medicine when HP low / Use Cures to remove status | automatic item use (flags 0x4000 / 0x8000). Medicine fires below **20% of max HP**, best first (Full Recover, Medicine 4 → 1), repeating until HP is back above 20% (`Entity_UpdateTimers`) |
| 8 / 9 / 10 | Item Capacity +1 / +2 / +4 | bag slots |
| 11 | Increases Max HP | ×23/20, i.e. **+15% max HP** |
| 12 | Increases Attack Power | **+2 offense levels** |
| 13 | Active Time Recharges Slower | **−2 Active Time levels** |
| 14 | PE Light | Parasite Energy costs **2/3** (`Inv_GetSlotHighlightState`) |
| 15 | Decreases Attack Power | **−2 offense levels** |

**Value ranking for pricing:** Command ×3 > Command ×2 > Attack All > ROF and element
mods > status mods > utility flags. Pricing ideas for chips or upgrades should follow that
order. Also, **the Weapon power (PWR) feature must multiply by commands per turn**: it
currently ignores effects 19/20 (to fix).

### 6.4 Saving the mod's own data (decomp + the 26 downloaded saves, 2026-10-11)

**Save layout** (one 8 KB memory-card block, `Save_BuildCardFile` /
`Save_LoadCardFileIntoRuntime`):

| Offset | Contents |
|---|---|
| `0x0000` | card header: title, icon (0x100) |
| `0x0100` | `g_SaveRuntimeState` (0x12E4): Aya, bag, equipment records, Wayne's storage, … |
| `0x13E4` | script variables (0x800), including Wayne's Junk counter at +0xC0 |
| `…` | small state blocks (about 0x9C) |
| `0x1C8C` | **CRC-16** (CCITT, init 0xFFFF, inverted) over the whole 0x2000 block with this field zeroed |
| `0x1C90–0x1FFF` | **880 bytes: always zero in all 26 saves (Day 1 to Day 6)** |

**Plan: keep the mod's data in that free tail.**

- **Save:** a build-time hook on `Save_SerializeTail` runs after the game has zeroed the
  save buffer (`D_8009EED0`) and before it computes the CRC. The mod writes its block (magic
  + version + data) at `+0x1C90`, and the game's own CRC then covers it, so the save stays
  valid.
- **Load:** the game reads the whole block into `g_MemCardFileBuffer` and checks the CRC
  over all of it. A hook on the load path (`Save_LoadCardFileIntoRuntime` /
  `Save_DeserializeTail`) copies the mod block back out. No magic → no mod data (a vanilla
  save) → start fresh.
- **Properties:**
  - travels with each save, including copied memory cards;
  - carries into EX Game, because that save is built the same way;
  - the vanilla game ignores it, and a vanilla re-save clears it;
  - 880 bytes is plenty: Junk counter, pity timers, a 40-entry chip library, purchase
    counts and room to spare.
- **Save states (F7): fixed (psxrecomp `6cb1d104`, PE `fe00ce3`, 2026-10-11).** Plugins
  register a static block by id and version (`psx_mod_register_state`); every snapshot
  (F7, rewind, netplay rollback, fast boot) stores it in a new optional section 0x12.
  On load each block is restored, reported absent (the mod resets) or reported as a
  version mismatch (old bytes passed for migration). Blocks of a mod that isn't
  running are kept and written into the next snapshot. Half-bar ATB is the first user,
  verified live with a state saved mid-borrow. The loot mod's Junk counter will
  register the same way, and also write the save's free tail for memory-card saves.
  - Rule for mods: keep data that must follow the game in a registered block, and
    reset short-lived state in `psx_mod_register_restore_callback`.
  - Known leftover: No random battles writes the game's own saved bit, so it persists
    in a save even with the mod removed.

This also answers part of decision 3: **option A (virtual chip library) is technically
sound**. Its data can live in the save's free tail.

### 6.5 Handing Junk to Wayne, and where to override drops (decomp, 2026-10-11)

**How Wayne takes Junk today.** No game code mentions Junk. Wayne's room script does it
with generic field-script opcodes (`Task_LoadWaitAndItemOps.c`):

| Opcode handler | Does |
|---|---|
| `Task_CountItemsByValue` (0x800194F8) | count an item id in the bag, into a script variable |
| `Task_GiveItem` (0x800194B0) | add an item to the bag |
| `Entity_InitWithTimeout` (0x80019540) | open the **"pick an item from your bag"** menu (`Menu_OpenEquipSlotSwap`) and wait; returns the choice, or −1 on cancel |

In that menu (`Menu_InventoryInputHandler`, mode `D_8009CF00`), confirming removes the
chosen item (`Inv_RemoveActiveListItem`). If the script passed an item id, it is handed
back in exchange. The script then does its own bookkeeping: Wayne's counter
`0x800A78B0` +1 per Junk.

- Precedent: `Inv_CountByValue` already treats three item ids as **counters, not bag
  slots** (the ammo pools, `g_InvCategoryItemTable[].count`). A Junk counter follows a
  pattern the game itself uses.
- `Inv_FindItemById` is misnamed: it **removes** the first bag slot holding an id. Only
  battle code calls it (auto-medicine, auto-cure, enemy item steals), never scripts.

**What a Junk counter means for Wayne.** With Junk in a counter there is nothing in the
bag for his menu to pick. Two ways to connect them:

| Option | How | Notes |
|---|---|---|
| **W1. Deposit action** (recommended) | An F1 Workshop row "Give Junk to Wayne" moves N from the mod's counter into `0x800A78B0` | His script reads the variable, so his 300 milestone should keep working untouched. Junk you spend in the shop never reaches Wayne, so the player chooses between shop and milestone |
| **W2. One counter** | The mod's counter *is* `0x800A78B0`: every pickup goes straight to Wayne | Simplest, and the game saves it for free. But shop spending would lower Wayne's progress, so the 300 milestone and the shop fight over one number |

- **Live test, Day 3 NYPD (precinct under attack), 2026-10-11:**
  - Wayne's menu is Store equipment / Store item / **Discard junk** / Cancel.
  - "Discard junk" has **no pick menu**. The counter goes up first, then the Junk leaves
    the bag (299 → 300 with 1 Junk; 300 → 301 with 1 more).
  - **No craft offer**: not at 300, not past it, not on later talks, not after leaving
    and re-entering the room. On this day the counter only accumulates.
- **Live test, Day 4 NYPD (Day 4 Beginning save), 2026-10-11, answered:**
  - Full menu: Tune up weapon / Store equipment / Store item / Discard junk / Rare T
    Card collection / Cancel.
  - Talking at 300 does nothing. **The craft fires only inside "Discard junk", when the
    hand-in takes the counter to 300 or more.** The script adds 1 and removes one Junk per
    step, then Wayne makes a gun.
  - **He subtracts 300:** 299 + 1 Junk → 300 → gun → **0**, and 299 + 2 Junk → 301 →
    gun (AK-47) → **1**. So Wayne's Junk is a **currency at 300 per gun**, and the excess
    carries over. Matches the guides' "every 300".
  - Day 3 (attack) never crafts, even past 300: that version of his menu only stores
    Junk.
- **Design consequences:**
  - A counter written straight into `0x800A78B0` does **not** craft by itself. The craft
    needs a hand-in that crosses 300 while the player is at Wayne on a full-menu day.
  - **W1 refined (recommended):** when the player picks "Discard junk", the mod puts Junk
    from its counter into the bag (up to the free slots), so Wayne's vanilla script
    counts, removes and crafts exactly as it does today.
  - **Hook point found (decomp):** script inventory actions go through
    `Task_RunInvCommand` (0x80015C7C) → **`Inv_DispatchCommand(command, value, other)`
    (0x8005D2B4)**. Command **1102** counts an item (`INV_CMD_COUNT_ITEM`), **1112**
    removes one (`INV_CMD_REMOVE_ITEM`, through `Inv_RemoveActiveListItem`). "Discard
    junk" is a script loop of count Junk → remove one → Wayne +1.
  - Plan: a build-time hook on `Inv_DispatchCommand` sees `a0 = 1102, a1 = 0x14`. If the
    bag has no Junk and the mod's counter is above 0, it puts **one** Junk into a free bag
    slot and takes 1 off the counter. The loop removes it, adds 1 to Wayne, counts again,
    and the hook refills, until the counter is empty. **Needs only one free bag slot.**
    Wayne's crafting at 300 and his gun choices stay vanilla.
  - Guard: other scripts may count Junk too. The per-frame sweep that pulls bag Junk into
    the counter puts back any Junk the hook placed that wasn't taken.
  - Live check still to do (one build): log `Inv_DispatchCommand` calls during a
    hand-in to confirm the 1102/1112 sequence.
  - **Alternative:** the F1 Workshop does Wayne's craft itself (spend 300 from the
    counter, give one of his six guns or a "leave it to Wayne" roll). Simpler to build,
    but it copies his gun table instead of reusing his script.

**Where to override drops.**
- **Spawn:** each enemy's battle script writes its drop (`rewardSlotId` +0x9E) from a
  per-room random pool when the battle starts.
- **Each death:** `Battle_StepEntityAnimState` case 3 appends +0x9E, then any item that
  enemy stole from Aya (+0xA0), to the reward list `0x800A7FF0` (10 × {u16 id, s16 extra}).
- **Battle end, recommended:** `Battle_StepLevelUp` calls **`Aya_SetTotalExp(exp, bp,
  list)` (0x8004B70C) once**, after every death. It passes the list to
  `Inv_LoadWayneItemsAsOverride`, which builds the "items found" screen.
  - A build-time hook on `Aya_SetTotalExp` (like Half-bar's on `Battle_Update`) sees
    the final list in `a2`, plus EXP in `a0` and BP in `a1`. It can strip Junk into the
    counter, add crafted materials, or scale EXP/BP for difficulty presets, all once,
    before anything is shown or added to the bag.
  - List rules: entries are read until the first id 0, at most 10. Ammo ids (the three
    pool ids) carry their amount in `extra`; other items ignore it. The hook must keep
    the list contiguous and within 10.
  - Per-enemy decisions (for example "Junk from this species") need the loot mod to
    track enemies during the battle, as the loot logger already does. Slots are freed
    by the time the hook runs.
  - Fleeing never calls `Aya_SetTotalExp`, so there are no rewards, matching vanilla.
- **Field pickups** (chests, story gifts) come through `Task_GiveItem` → `Inv_AddItem`,
  not the reward list. A Junk counter needs a second path for them: hook `Inv_AddItem`,
  or sweep Junk out of the bag each frame while Wayne's pick menu isn't open.

### 6.6 Drop table structure (decisions 16–20): how it maps onto the game

- **One hook does most of it:** `Aya_SetTotalExp(exp, bp, list)` (0x8004B70C, 6.5) runs
  once per won battle with the **battle's total EXP in `a0`**.
  - **Junk** = max(1, f(total EXP)). Per-enemy tracking isn't needed, since the total
    already sums every enemy, bosses included. A per-battle cap may be needed so one boss
    doesn't skip a whole area's economy (6.3).
  - **Junk entries** already in the vanilla list are also moved into the counter, so the
    vanilla rate stays on top (decision 6).
  - **Tool drop:** roll the chance and advance the pity counter. On a hit, add a Tool
    (`0x16`) to the reward list, so it shows on the game's own "items found" screen. If
    the list is full (10 entries), carry the Tool over to the next battle rather than lose
    it.
- **Chests and story pickups:** the `Inv_AddItem` (0x80053D2C) hook or the per-frame sweep
  moves Junk into the counter (decision 20).
- **Empty steals (decision 19):** research needed. Find where Aya's steal resolves (Club 2
  / gun Steal effects 16–17 read the enemy's `+0x9F`), so that an empty steal can add Junk
  to the counter. The loot logger's planned steal logging will show how often steals come
  up empty.
- **Saved state:** the pity counter and a carried-over Tool live in the loot mod's
  state block (F7) and the save tail (memory card), like the Junk counter.
- **Logger:** already records per-battle EXP and the reward list, which is enough to fit
  f(EXP) against today's Junk pace. Steal logging is still to add.

### 6.7 Junk feedback (decisions 21–24): how it maps onto the game

- **Toasts:** `psx_mod_osd_message`, already used by the Wayne refund. The text is plain ASCII
  in the engine's font. One toast per battle end comes from the `Aya_SetTotalExp` hook
  (6.6), plus one for a steal.
- **"Discard junk (147)" and Aya's item-menu title:** draw-time relabels through the
  existing `Draw_PrintRawText` hook (0x8005F27C), the trick Weapon power uses: match the
  string and the calling menu (`ra` range), then swap `a0` for a guest buffer.
  - Research: which function draws Wayne's choice list (the `ra` range) and the exact
    "Discard junk" string, and which call draws Aya's item-menu title.
- **Native "items found" line (later):** leave one Junk entry in the reward list, relabel
  it at draw time, and let the sweep move it into the counter when it's picked up.
  Research: how `Inv_LoadWayneItemsAsOverride` and the pickup screen draw entries, and
  what happens if the player leaves the entry behind.
- **F1 Workshop page:** live rows (`psx_mod_menu_add_live_int` / read-only actions) for
  the Junk total and the Tool pity progress.

### 6.8 Names and wording (decision 37)

**Rules:** text inside the game's own menus (Aya's actions, Wayne's label, item and mod
names) must use glyphs in PE's font: letters, digits and space are safe; punctuation such
as "·", "/" or "(" must be checked before phase 5. F1 rows and toasts use the engine's
plain ASCII. F1 descriptions stay under ~38 characters. Tone: NYPD and gunsmith, not
fantasy; actions are single words like the game's own.

| Thing | In game | Notes |
|---|---|---|
| F1 page | **Workshop** | |
| Codex | **Mod Catalog** | user pick |
| Buy-back | **Rebuild** | user pick; Wayne keeps your stripped parts and rebuilds the gun |
| Shop | **Requisition** | user pick; NYPD flavour |
| Aya's action on gun/armor | **Dismantle** | |
| Aya's action on medicine | **Combine** | |
| Master switch | **Junk economy** — "Junk counter, Mod Catalog and shop." | |
| Pity row | **Rare drop within N battles** | |
| Wayne's label | **Discard junk (147 · 120/300)** | decision 31; punctuation adapted to the font check |
| Battle toast | **+3 Junk (total 147)** | ASCII-safe; replaces "·" |
| Steal toast | **+1 Junk from steal** | paid at battle end (decision 35) |
| Refund toast | **Wayne refunds 300 Junk** | replaces the current text in `pe_wayne_refund.c` |
| Rescue toast | **Spare Club issued at the Workshop** | decision 36; gives Club 1 |
| Custom mods | **Increases Junk found** (Scavenger), **Finds rare items more often** (Lucky Find), **More Junk from dismantling** (Salvager), **Lowers shop prices** (Bargain) | user pick: PE-style descriptions; short names only in docs |
| Custom items | **Smoke Grenade**, **Lucky Charm** | descriptions in PE's style, to write in phase 6 |

### 6.2 Mod chips: UX options to compare (decision 3)

| Option | How it plays | Pros | Cons |
|---|---|---|---|
| **A. Virtual chip library** (stored by the mod, shown on the Workshop page) | Dismantling files the mod into a library; install it later on any compatible item | No bag clutter, easy to browse, matches the counter approach for Junk | Invisible outside F1 until the Wayne UI exists; needs save-file handling (see below) |
| **B. Real bag items** (reuse spare item IDs such as `ITEM24/25`) | A chip is an item you carry and use, like a Tool | Feels native, lives in the game's own save, visible in the bag | Takes bag slots (the clutter we're removing); limited spare IDs; needs names and icons |
| **C. No chips: keep vanilla's donor → target transfer, made cheaper** | Dismantle gives Junk only; moving mods still needs a donor, but Tools are easier to get | Closest to vanilla, least new UI | Doesn't fix "old gear is useless"; the donor pairing stays fiddly |
| **D. Hybrid: chips stored in Wayne's storage as items** | Chips are items, but they go straight to storage instead of the bag | Native and saved, no bag clutter | Depends on Wayne's storage capacity; only usable at Wayne's |

Research questions:

- **Where would A's data persist?** Answered in 6.4: the save's free 880-byte tail for
  memory-card saves, plus a registered state block for F7 save states (built).
- **Are `ITEM24/25` really unused?** They exist as placeholders: ids `0x18` / `0x19`, named
  literally "ITEM24" / "ITEM25", kind 10, category Tools and Junk, description "Helps
  Item", flags 0x03 (Junk/Tool have 0x00), and no use case in `Battle_ApplyDamage`. So
  option B has exactly **two** spare ids: enough for "a chip" and "a super chip", not one
  per effect. Each chip's effect would have to live in mod data (which keeps option B close
  to option A). Names can be swapped at draw time with the `Draw_PrintRawText` hook, as
  Weapon power does.
- **What does a good loop look like?** Look at how other games handle "salvage → reusable
  upgrade": FF7 materia, FF8 refine/junction, Resident Evil 4 upgrades, Borderlands/Diablo
  salvage. The target feel: one action to dismantle, one action to install, always shown
  in the game's own words.

### 6.2a How other games handle salvage → upgrades (2026-10-11)

| Game | Salvage | What you get / how you upgrade | Lesson for PE |
|---|---|---|---|
| **Diablo 4** (Codex of Power, since Season 4 "Loot Reborn") | Salvaging a legendary **unlocks its aspect permanently** in a codex. A duplicate only counts if its roll is better | Imprint any unlocked aspect onto gear, for gold plus salvage materials | The closest model to option A. Find once, reuse forever; each application costs common currency, so grinding stays useful. Discovery stays meaningful because you can only use what you've found |
| **Destiny 2** | Older one-use mod items, later replaced by a mod collection | Mods became unlocks you socket freely, limited by an energy budget | Players disliked consumable mods that vanish when moved. A collection plus a slot budget replaced them |
| **Warframe** | Duplicate mods and junk become **Endo** (currency) | Mods live in their own inventory; Endo ranks them up; slots are limited by capacity | Duplicates are never wasted, and mods never take normal inventory space |
| **Final Fantasy VII** (materia) | None | Materia moves freely between slotted gear | Moving an effect should be free and painless; spend the effort on getting it |
| **Mass Effect 1** | Excess items become omni-gel | Weapon and armor mods were bag items | A known UX failure: endless mod items clogged the inventory, and ME2 dropped the system. The case against option B |
| **Fallout 4** | Junk breaks into components **automatically, when a recipe needs them** | Weapon mods are crafted at a workbench, and swapped-out mods go to storage | Junk shouldn't need managing: count it only when it's spent. That's our Junk counter |
| **Resident Evil 4** | None (money from treasure) | Pay the merchant to upgrade a gun's stats in steps | One clear place and price per upgrade; the game's own menu shows the next step's cost |
| **Final Fantasy VIII** (refine/junction) | Refine items into magic and abilities | Junction magic onto stats | Powerful but opaque: players miss it. Keep each step one obvious action |

**What PE already has that fits.** Its 35 effects come in natural tiers (Rate of Fire
×2 → ×10, capacity +1 / +2 / +4, 2 / 3 commands), belong to exclusivity groups that
overwrite each other, and fill a limited number of mod slots per item (tune-ups add
slots). That is the same shape as Destiny's or Warframe's "collection plus slot budget".

**Recommendation: option A as a "Mod Codex", built on Diablo 4's loop.**
1. **Dismantle** (Workshop): the item's effects are added to the Codex (each tier kept
   separately, since a lower tier is cheaper and can still be useful), and the item turns
   into Junk scaled by its tier and +bonus.
2. **Duplicates** of an effect you already have give extra Junk instead, so every dismantle
   pays something (Warframe).
3. **Install** any unlocked effect into a free slot of any compatible item, priced by the
   value ranking in 6.1b (Command ×3 most expensive). The game's group rules still apply.
4. **Remove or replace** installed effects freely, since they stay in the Codex (FF7).
5. **No random failure** anywhere, and every cost is shown before you confirm (RE4).
6. **Words and place:** effect names come from the game's own mod text (table 3). It's a
   page in F1 first, then a Wayne menu row.
7. **Saved** in the save's free tail and in a save-state block (6.4).

Why not the others: B gets only two spare item ids and brings back the clutter (Mass
Effect 1). C doesn't fix "old gear is useless". D ties chips to Wayne's 100 shared
storage slots and to his room.

**Open questions for the user:**
- **What do vanilla Tools become?** Either (a) they keep their vanilla job and the Codex
  costs Junk only, or (b) they also become the price of premium installs (Command ×2/×3,
  Attack All), which keeps the ~17 story Tools valuable.
- **Does the Codex fill only from dismantling,** or also from mods on gear you own?
  Dismantle-only keeps the choice meaningful (Diablo 4).
- **Codex reach:** should installs need Wayne's room once his menu has a Workshop row, or
  work anywhere from F1?

### 6.2b Buy-back of dismantled gear (decision 12)

**Why:** dismantling is meant to be a choice, not a trap. If a later fight calls for a gun
you broke down, you can get it back by spending Junk.

**Proposed rules:**
- **What comes back:** the same base item, with its stat +bonuses (attack, range,
  capacity) and its tune-up slot count, but **no installed effects**. Its effects stayed in
  the Codex when you dismantled it, and putting them back costs the normal install price.
  Otherwise dismantle + buy back would hand you the effect twice for free.
- **Price:** the Junk that dismantling paid out, plus a markup (start at ×1.5, tune in 6.3).
  It's never cheaper than what you got, so there's no Junk loop. The price is shown before
  you confirm.
- **Price cap (user, 2026-10-11): buy-back never costs more than 150 Junk**, half of one of
  Wayne's 300-Junk guns. Price = min(payout × 1.5, 150). Getting an old gun back is always
  clearly cheaper than crafting a new top-tier one, so it stays worth doing. To keep the
  no-loop rule, **no dismantle pays out more than 150 Junk**, so even a capped price is at
  least what you got. Exact numbers are tuned in 6.3.
- **List:** the Workshop keeps a buy-back list of dismantled gear, newest first. It stores
  item id, +bonuses and slot count (about 8 bytes each), so the save's free tail holds
  ~30 entries easily. When it's full, the oldest entry drops off (or the list is capped and
  shown; to settle in the UI pass).
- **Vanilla-only items** (Maeda's Gun, story weapons) follow the same rule. Wayne's
  300-Junk guns can also be bought back this way, at their dismantle price plus the
  markup, not 300 again (to settle in balance).
- **Where:** same as installs (decision 11): anywhere, from the Workshop page.

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
  undercut Wayne's 300 milestone. Settled by decision 13: both draw from **one** Junk
  count, so prices must leave a Wayne gun reachable at a normal pace.
- **Price caps already fixed by the user:** buy-back ≤ 150 Junk (decision 12), Tools ≤ 100
  Junk (decision 14). Everything else is tuned under them.
- **Difficulty presets (decisions 39, 40):** starting multipliers to tune: Relaxed = Junk
  ×1.5, pity ×0.7, prices −25%; Normal = ×1 (the target above); Grind = Junk ×0.75,
  pity ×1.3, prices +25%. Caps stay fixed on every preset.
- **Wayne pace target (decision 34):** first gun affordable around Day 4–5 on the normal
  route with ~1–2 hours of optional fighting; vanilla's Day 4 gate is the hard ceiling.
  Measure: Junk earned per hour on the normal route (logger), minus typical Codex/shop
  spending.

---

**Custom items and mods** (Scavenger, Lucky Find, Salvager, Bargain, Smoke Grenade,
Lucky Charm) have their own decisions document:
[`pe-custom-items-design-2026-10-11.md`](pe-custom-items-design-2026-10-11.md).

## 7. Possible features (not committed)

- *(Difficulty presets moved into the plan: decisions 39 and 40.)*

Sources: decomp `Battle_StepEntityAnimState.c`, `Battle_ResolveHitOnTimer.c`,
`Menu_MainUpdate.c`, `Menu_LevelUpFlow.c`, `Inv_ItemActions.c`, `Inv_ArmorCapacity.c`,
`include/pe1/item_ids.h`; guides:
[GameFAQs — Guide and Walkthrough by mysticcat](https://gamefaqs.gamespot.com/ps/198265-parasite-eve/faqs/13947),
[GameFAQs — Walkthrough by _Young-Gamer_](https://gamefaqs.gamespot.com/ps/198265-parasite-eve/faqs/80267),
[RPGClassics — Junk](https://shrines.rpgclassics.com/psx/pe/junk.shtml),
[RPGClassics — Items](https://shrines.rpgclassics.com/psx/pe/items.shtml),
[Almar's Guides — Weapons from Junk](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/weaponsfromjunk/),
[Icy Veins — Diablo 4 Codex of Power](https://www.icy-veins.com/d4/guides/legendary-aspects-codex-of-power-guide/),
[Icy Veins — Aspects extract directly to the Codex (Season 4)](https://www.icy-veins.com/d4/news/all-legendary-aspects-extract-directly-to-codex-in-diablo-4-season-4/),
[PCGamesN — Destiny 2 armor mods unlocked](https://www.pcgamesn.com/destiny-2/armor-mods-unlocked),
[Almar's Guides — Day 3](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/day3/),
[Almar's Guides — EX Game](https://almarsguides.com/retro/walkthroughs/ps1/games/parasiteeve/fullplaythrough/exgame/),
[Parasite Eve Wiki — Weapons](https://parasiteeve.fandom.com/wiki/Parasite_Eve_Weapons).
