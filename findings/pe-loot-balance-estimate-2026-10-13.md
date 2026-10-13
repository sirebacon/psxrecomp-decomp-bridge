# Parasite Eve loot overhaul: balance estimate (phase 7 groundwork, 2026-10-13)

An estimate of how much Junk and how many rare drops a normal playthrough produces under
the overhaul's current numbers, built before a full logged playthrough exists. It combines
the code's formulas, the loot logger's real battles (Days 1–3), **26 downloaded saves that
follow one player from Day 1 to Day 6**, the game's level table and facts from the
walkthroughs. The aim is to find the numbers that matter most, so the logged playthrough
can confirm them instead of starting from nothing.

Round 1 (the same day) estimated battle counts from the walkthroughs alone; round 2
calibrated them against the saves' EXP and play time, which made Day 4 and Day 5 bigger
than first thought. The numbers below are round 2.

Design and decisions: [`pe-loot-overhaul-design-2026-10-11.md`](pe-loot-overhaul-design-2026-10-11.md)
(targets in 6.3, decision 34 for Wayne's pace). The model is a small Python script; its
inputs are all listed below, so any of them can be swapped for logger data and re-run.

---

## 1. Summary

- **A normal run has about 130–200 battles** (best guess ~160, bosses included), over
  about 10 hours to the final day. Not every room has a fight, and each trigger spot fires
  100% the first time, then 45%, 20%, 10%.
- **Day 5 is half the game.** In the saves it takes ~4 hours and ~60 fights at roughly
  950 EXP each, and earns 95% of the run's EXP.
- **Junk is back-loaded.** Junk per battle is `1 + EXP / 8`, capped at 30. Days 1–3 pay
  1–7 a fight, Day 4 about 13, and from Day 5 every fight hits the 30 cap. With today's
  numbers **Day 5 alone pays ~2,300 Junk**, about 2.5× Days 1–4 together (~970) and enough
  for seven Wayne guns. A run pays **~3,650** (2,980–4,470), against ~1,700 a player who
  uses every system would spend.
- **Days 1–3 look about right.** ~490 Junk by the end of Day 3, before spending: the first
  Wayne gun is affordable at the start of Day 4 for a light spender, later for someone
  buying Tools and premium installs. Day 4 already pays fast (~13 a fight).
- **The rare-drop presets don't do anything yet.** Soft pity (4% +1% a dry battle) almost
  always hits before the guarantee, so Relaxed, Normal and Grind all give **one rare per
  ~9.5–9.8 battles** (~16 rares in a run, ~6 of them Tools on top of vanilla's ~17 chest
  Tools).
- **Recommendation:** lower the per-battle cap from 30 to **12**, let **bosses use a cap of
  25**, and make the presets scale the pity **base chance and step**. Days 1–3 stay as they
  are, Day 4 barely changes, Day 5 halves, the run pays **~2,200** (1,880–2,630), and the
  presets become real (one rare per ~7.6 / 9.8 / 13.8 battles).
- **EX Game and Chrysler (section 10, estimate only):** every Chrysler fight pays the cap.
  A full video playthrough puts the climb at ~3 hours, ~110 fights. Today an EX run earns
  ~9,000 Junk against ~4,000 a completionist can spend; at cap 12 it's ~5,200. Two Chrysler-only fixes are proposed: Tool rolls turn into stat boosters
  once the Tool Kit is held, and the dismantle bonus for repeated effects shrinks.

---

## 2. Inputs

### 2.1 The overhaul's current numbers (code defaults)

| What | Value | Where |
|---|---|---|
| Junk per won battle | `floor (1) + EXP / 8`, capped at **30** | `pe_loot.c`, Debug → Loot tuning |
| No-hit bonus | up to **+25%**, less per hit taken (4+ hits: none) | decision 32 |
| Presets | Relaxed / Normal / Grind: Junk ×1.5 / ×1 / ×0.75, pity guarantee ×0.7 / ×1 / ×1.3, prices −25% / 0 / +25% | decision 39 |
| Scavenger (armor) | battle Junk +50% | C1 |
| Rare drop | 4% base, +1% per dry battle, certain at 25 | decision 18 |
| Rare table (weights, sum 111) | Tool 40, stat booster 35, Super Junk 10, Duper Junk 5, Mod Permit 7, Super Tool 3, economy mod 6, Lucky Charm 5 | `s_rare_table` |
| Empty steal | 2 Junk, paid on a win | decision 19 |
| Dismantle payout | `5 + 2 × (sum of +bonuses) + 3 per mod + 5 per already-unlocked mod`, Salvager +25%, cap 150 | `pe_salvage_payout` |
| Mod Catalog installs | common **10**, mid **30**, premium **80 + a Tool** | `s_price` |
| Rebuild | payout × 1.5, never below the payout, cap 150 | decision 12 |
| Requisition | Medicine 1–4: 6 / 12 / 25 / 50; cures 5; Full Cure 15; Bullets ×15 / ×30: 5 / 9; Rocket 20; Smoke Grenade 15; Tool 40, +10 per Tool bought, cap 100 | decision 43 |
| Wayne's gun | 300 Junk, crafts from Day 4 | vanilla |

### 2.2 When fights happen (game rules, design doc section 1)

- Fights come from **trigger spots** in some rooms, not every room.
- A spot fires **100%** the first time, then **45%, 20%, 10%** once won. Fleeing doesn't
  lower it.
- So most battles are **first passes** through an area; backtracking adds a few, and
  grinding one spot gets slow quickly. Optional grinding means hopping between spots:
  roughly **1.5–2 minutes per extra fight**, walking included (the logger's fights last
  20–65 seconds each).

### 2.3 Real battles (loot logger, `pe_loot_log.csv`, your Day 1–3 sessions)

| Area | EXP per battle | Junk per battle today | Vanilla Junk drops |
|---|---|---|---|
| Day 1, Carnegie Hall (rats) | 1–5 | 1 | none |
| Day 2, Central Park (birds, monkeys, bears) | 14–30 | 2–4 | ~1 in 3 enemies; one room ~80% |
| Day 2–3, NYPD (dog-men, mixed) | 20–78 | 3–10 | rare |

### 2.4 Level table and walkthrough anchors

EXP to reach a level (resident data pack, `Aya_GetLevelExpTable`):

| Level | 10 | 15 | 20 | 25 | 30 | 33 | 35 | 38 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| Total EXP | 184 | 868 | 3,744 | 17,216 | 73,151 | 168,061 | 299,579 | 725,158 | 734,158 |

Above level 38 the curve goes nearly flat (+4,500 a level), which is the "level 38 cap"
the guides mention.

From Shotgunnova's walkthrough (private copy; facts only): Aya is around **level 20 at
Black Widow**; boss EXP Sheeva 1,000, Black Widow 6,500, Crustacean 2,510, Triceratops
50,000.

### 2.5 What the 26 saves show (one player, Day 1 to Day 6)

Read from each save's 8 KB block (`g_SaveRuntimeState`, RAM 0x800C0DE0, is stored at card
+0x100: play time at +0x108, total EXP at +0x120, level at +0x12A; bag, gear records and
the trunk follow; Wayne's counter is script variable +0xC0 at card +0x14A4). The field the
decomp calls `playTimeMinutes` holds seconds.

| Save | Play time | Level | Total EXP |
|---|---|---|---|
| Day 1, Alligator | 0:44 | 6 | 51 |
| Day 2, start | 0:52 | 7 | 81 |
| Day 2, Amphitheater | 2:10 | 11 | 283 |
| Day 2, Giant Worms | 2:25 | 13 | 439 |
| Day 2, end (Flaming Horse) | 2:38 | 14 | 759 |
| Day 3, NYPD | 3:32 | 14 | 791 |
| Day 3, 2nd floor | 4:18 | 16 | 1,438 |
| Day 4, start (after Sheeva) | 4:31 | 18 | 2,705 |
| Day 4, Lobby revisit | 5:12 | 20 | 3,925 |
| Day 4, Sperm bank (before Black Widow) | 5:39 | 21 | 5,273 |
| Day 5, start (after Black Widow) | 5:55 | 24 | 11,793 |
| Day 5, Chinatown | 6:25 | 24 | 17,155 |
| Day 5, Sewers | 7:04 | 26 | 25,162 |
| Day 5, Museum | 7:26 | 27 | 36,688 |
| Day 5, Security room (after Triceratops) | 8:15 | 31 | 104,394 |
| Day 5, T-Rex defeated | 9:06 | 33 | 214,670 |
| Day 6, start | 9:51 | 34 | 225,172 |

What follows from it:

- **Black Widow at level 21** (5,273 → 11,793 is her 6,500 EXP), as the walkthrough says.
  The T-Rex fight is worth about **100,000 EXP** (108,656 → 214,670 across it).
- **EXP from regular fights per day** (bosses taken out): Day 1 ~40, Day 2 ~520, Day 3
  ~950, Day 4 ~2,150, **Day 5 ~55,000**.
- **Play time per day**: 0:44 / 1:54 / 1:53 / 1:24 / **3:56**. Day 5 is the longest day by
  far.
- **No battle counter** in the save: the only fields that rise steadily are stats, HP
  levels and a story-progress value. Battle counts come from EXP ÷ EXP per fight.
- This player **never collected Junk or visited Wayne** (0–2 Junk in the bag, Wayne's
  counter 0) and used every Tool they found, so the saves can't measure vanilla Junk or
  Tool pickups. They carried 4–12 guns and armor at a time.

Gear supply for dismantling (from
[`data/pe-gear-locations-2026-10-11.csv`](data/pe-gear-locations-2026-10-11.csv)): **57
guns and armor in the main story**: Carnegie Hall and starting gear 7, Central Park 5, NYPD
8, Soho 4, Hospital 8, **Day 5 areas 24** (Museum 11, Warehouse 5, Chinatown and sewers 6,
Subway 2), Maeda 1.

---

### 2.6 A full video playthrough (time per day and per Chrysler block)

A complete first playthrough, EX Game and Chrysler Building on YouTube
([playlist](https://www.youtube.com/playlist?list=PL510D0B396E327AC5), 112 parts, titled
by day and floor). Video time is edited, but it matches the saves closely, so the per-day
weights hold:

| Segment | Video | Saves |
|---|---|---|
| Day 1 | 55 min | 44 min |
| Day 2 | 102 min | 114 min |
| Day 3 | 92 min | 113 min |
| Day 4 | 68 min | 84 min |
| Days 5 + 6 | 233 min | 236 min (Day 5 alone) |
| EX Game, Days 1–5 | 346 min | |
| **Chrysler Building, floors 2–77** | **190 min** | |

Chrysler by block: floors 2–10 38 min, 11–20 / 21–30 / 31–40 20 min each, 41–50 22, 51–60
27, 61–70 29, 71–77 and the ending 14. That's **about 2–3 minutes a floor**, armory,
walking and the block boss included, which leaves room for only **~1–2.5 fights a floor**
with EX gear.

## 3. Battles per day (calibrated against the saves)

| Day | Areas | Play time (save) | Regular EXP (save) | EXP per fight | Low | **Mid** | High |
|---|---|---|---|---|---|---|---|
| 1 | Carnegie Hall | 0:44 | ~40 | 4 (logger) | 8 | **10** | 12 |
| 2 | Central Park, NYPD | 1:54 | ~520 | 20 (logger) | 20 | **25** | 30 |
| 3 | NYPD, Soho | 1:53 | ~950 | 55 (logger) | 14 | **17** | 22 |
| 4 | St. Francis Hospital | 1:24 | ~2,150 | ~100 (guess) | 20 | **25** | 32 |
| 5 | Chinatown, Warehouse, Sewer, Subway, Museum | 3:56 | ~55,000 | ~950 (guess) | 45 | **60** | 75 |
| 6 | Final dungeon | ? | ? | 1,500+ | 8 | **10** | 15 |
| | **Total** | **~10 h** | | | **115** | **147** | **186** |

Plus about **14 bosses**. Day 5's count also fits its play time: at Day 4's pace (a fight
every ~3.4 minutes) its 3:56 holds ~70 fights. For Day 5 and Day 6 the exact EXP per fight
doesn't matter for Junk: anything above 232 EXP (today) or 88 EXP (with a cap of 12) pays
the cap.

Other income the model counts (per day, mid): vanilla Junk drops (0.8 a fight on Day 2,
falling to 0.2–0.4 later), the no-hit bonus (+8% on average), and dismantling about 60% of
the gear found (30 / 40 / 90 / 60 / 190 / 0 Junk on Days 1–6, ~410 in all, at 10–25 Junk a
piece). Steals and empty steals are left out: they need a steal club (Day 3) and are
optional.

---

## 4. Junk income with today's numbers (Normal, mid)

| Day | Junk per fight | Fights | Bosses | Vanilla drops | Dismantles | **Day total** | **By end of day** |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 11 | 8 | 0 | 30 | **49** | **49** |
| 2 | 3 | 81 | 41 | 20 | 40 | **182** | **231** |
| 3 | 7 | 129 | 30 | 7 | 90 | **255** | **486** |
| 4 | 13 | 351 | 60 | 8 | 60 | **478** | **965** |
| 5 | 30 | 1,944 | 180 | 18 | 190 | **2,332** | **3,297** |
| 6 | 30 | 324 | 30 | 2 | 0 | **356** | **3,653** |

Low battle counts: ~2,980 for the run; high: ~4,470. In Junk per hour of play: about
100–130 on Days 2–3, ~340 on Day 4, **~600 on Day 5**.

---

## 5. Where the Junk goes

A plausible spend for a player who uses every system over the main story:

| Sink | Example | Junk |
|---|---|---|
| Wayne's guns | 2 guns | 600 |
| Mod Catalog | 6 common, 7 mid, 2 premium installs | 60 + 210 + 160 |
| Tools from Requisition | 4 Tools (40, 50, 60, 70) | 220 |
| Requisition consumables | medicine, cures, ammo, a few Smoke Grenades | ~250 |
| Rebuild | 2 old guns back | ~200 |
| **Total** | | **~1,700** |

By the start of Day 4 a light spender (a few installs and medicines) has spent about
**150**; a heavy one (Tools, premium installs) about **300**. The Chrysler Building (EX
Game) keeps paying after the story, so ending the story with a few hundred spare is fine;
ending with ~2,000 spare is not.

---

## 6. Wayne's first gun (decision 34)

Target: affordable around **Day 4–5**, with **about 1–2 hours of optional fighting**;
vanilla's Day 4 gate is the ceiling.

With today's numbers (mid), the player has earned ~490 Junk by the end of Day 3:

- **Light spender (~150 spent):** ~340 left; the gun is affordable right at the start of
  Day 4 with no extra fighting.
- **Heavy spender (~300 spent):** ~190 left; Day 4's own fights get there in its first
  third, or ~10 extra fights (~20 minutes) at its start.

So the first gun lands at the start of Day 4 for nearly everyone; the "1–2 hours of
optional fighting" in decision 34 no longer applies, because on Day 4 an hour of extra
fighting is worth 300+ Junk by itself. Whether that's fine is a design call (question 3
in section 9). The bigger problem is after: on Day 5 every player can afford **seven more
Wayne guns**, Rebuild and premium installs stop being decisions, and Junk stops mattering
for the last half of the play time (against design rule "never pointless", 6.3).

---

## 7. Rare drops and the presets

Expected battles per rare drop (soft pity, computed exactly):

| Setting | Base / step / guarantee | One rare per |
|---|---|---|
| Today, Relaxed | 4% / +1% / 18 | 9.5 battles |
| Today, Normal | 4% / +1% / 25 | 9.8 battles |
| Today, Grind | 4% / +1% / 33 | 9.8 battles |
| Lucky Find or Lucky Charm (pity counts double) | | 7.1 battles |

The chance passes 50% within about 10 dry battles, so the guarantee almost never fires,
and scaling it changes nothing. Over a mid run (~160 battles) that's **~16 rares**: ~6
Tools, ~5 stat boosters, ~2 Super/Duper Junk, ~1 Mod Permit, ~1 economy mod, ~1 Lucky Charm
and a ~45% chance of a Super Tool. Six extra Tools on vanilla's ~17 seems right alongside
the shop's capped Tools. Because Day 5 has ~40% of the fights, it also gets ~40% of the
rares; that's fine.

**Fix:** let the presets scale the base chance and step too:

| Preset | Base / step / guarantee | One rare per |
|---|---|---|
| Relaxed | 6% / +1.5% / 18 | 7.6 battles |
| Normal | 4% / +1% / 25 | 9.8 battles |
| Grind | 2% / +0.6% / 33 | 13.8 battles |

---

## 8. Options compared

Cumulative Junk by the end of each day (Normal preset, mid battle counts) and the run
total's low–high range. Options C, E and F let bosses use a cap of 25 (same formula:
Day 1 bosses pay 2–6, Day 2 bosses ~20, Sheeva onwards 25).

| Option | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Run (Day 6) | Run range |
|---|---|---|---|---|---|---|---|
| **A. Today:** `1 + EXP/8`, cap 30 | 49 | 231 | 486 | 965 | 3,297 | **3,653** | 2,980–4,470 |
| **C. Cap 12, bosses cap 25** | 49 | 231 | 481 | 923 | 2,058 | **2,215** | 1,880–2,630 |
| **E. Cap 12, `1 + EXP/12`, bosses cap 25** | 49 | 204 | 417 | 778 | 1,914 | **2,070** | 1,760–2,450 |
| **F. Cap 10, bosses cap 25** | 49 | 231 | 481 | 869 | 1,875 | **2,010** | 1,720–2,370 |

- **C** keeps Days 1–3 as they are and Day 4 nearly so (13 → 12 a fight), halves Day 5,
  and lands the run ~500 above what the sinks absorb, which the EX Game can soak up.
  Bosses still feel like a payday: 25 is two regular Day 5 fights.
- **F** is C a notch tighter (Day 4 at 10 a fight); the run lands at ~2,000.
- **E** also slows Days 2–4 by ~15–20%, which pushes the first Wayne gun to around
  mid-Day 4 for a light spender: closer to decision 34's "optional fighting", at the cost
  of Days 2–3 paying only 2–5 Junk a fight.

A per-day or per-level cap (e.g. 6 / 10 / 14 rising through the story) was considered but
needs a story-day read the mod doesn't have yet; the EXP formula already scales with
progress, so a single cap does most of the work.

---

## 9. Proposed decisions (for the user)

1. **Per-battle cap: 30 → 12** (option C), or **10** (F) for a tighter run.
2. **Bosses use a cap of 25** with the same formula. Needs a reliable "this is a boss
   fight" test: the game's own no-escape flag on boss battles is the likely candidate (to
   confirm in the decomp before building).
3. **Early pace: keep `EXP / 8`** (C), or **slow it to `EXP / 12`** (E) if the first Wayne
   gun should take some real optional fighting on Day 4.
4. **Presets scale pity base and step** as in section 7, not only the guarantee.
5. **Keep** the floor (1), the no-hit bonus (25%), the rare table shares, dismantle
   payouts and all prices for now; revisit after the logged run.

---

## 10. EX Game and the Chrysler Building (low confidence: no saves or logs; video timing)

The EX Game replays the story with the cleared save's leftovers (the equipped gun and
armor, Wayne's storage and his Junk count, unused bonus points; enemy groups are often
larger) and opens the **Chrysler Building**: 77 floors, the overhaul's Junk counter,
Mod Catalog and Rebuild list carried in (decision 15). Facts from Shotgunnova's
walkthrough (private copy) and the gear table:

- **Layout:** floors 1–70 in seven blocks of ten, a boss on every 10th floor (plus Maya on
  77), random hallway layouts each visit, an armory on every floor, no save points
  inside. Fights only in corridor screens (never in junctions, dead ends, elevator or
  stair screens, rarely in armories); beating a block's boss clears its remaining
  enemies. Floors 71–76 are single screens.
- **Enemies:** weak on floors 1–10 (the story's Day 5 gear one-shots them), 500+ HP from
  41, 600+ from 51, 800+ from 61; floors 61–70 give **4,000+ EXP for a pair of wolves**.
  Every Chrysler fight is far above the EXP that hits any cap (232 today, 88 at cap 12).
- **Vanilla Junk:** bluebirds on floors 1–10, slimes on 61–70.
- **Gear:** **60 guns and armor** in its armories, with bigger +bonuses and more mod
  slots than the story's (Cr Armor 2 has 10).
- **Tools:** 31 in chests plus 6 Super Tools; Wayne gives the **Tool Kit** at 10 rare
  cards (around floors 41–50) and the **Super Tool Kit** at all 14 (after floor 70).

**Estimate** (floors 1–70: 63 regular floors at ~1–2.5 fights each, from the video's 2–3
minutes a floor):

| | Today (cap 30) | Cap 12, bosses cap 25 |
|---|---|---|
| Regular fights (80 / **110** / 150) | 2,590 / **3,560** / 4,860 | 1,040 / **1,430** / 1,940 |
| 8 bosses | 240 | 200 |
| Vanilla Junk drops | ~50 | ~50 |
| Dismantles (60% of 60 pieces at ~35 each) | ~1,260 | ~1,260 |
| **Chrysler total** | 4,140 / **5,110** / 6,410 | 2,550 / **2,940** / 3,450 |
| EX story replay (larger groups) | ~4,000 | ~2,300 |

What can be spent there: all six Wayne guns (1,800), ~25 installs on endgame gear
(~1,000; no Tools once the Tool Kit is in), some Rebuilds (~300), and medicine for long
climbs without saves (~800): **~4,000 for a completionist**. With today's numbers an EX
run earns ~9,000 plus whatever the story run left over, so Junk means little there; at a
cap of 12 it's ~5,200, close to the sinks once the story's leftovers are counted, and the
Grind preset (×0.75) tightens it further for players who want it.

**Chrysler-specific points to decide:**

1. **Every Chrysler fight pays the cap**, so the cap is the only Junk knob there; the
   cap-12 decision (section 9, question 1) covers it.
2. **Dismantling becomes ~40% of Chrysler's income** (at cap 12), mostly from the +5 a repeated
   effect pays (by then nearly every effect is unlocked). Option: drop the repeat bonus to
   +2, or to 0 once the Catalog is complete.
3. **Tool Kit makes Tools pointless:** a Tool from the rare table or Requisition is wasted
   once the kit is held. Proposal: with the Tool Kit, a rare **Tool roll becomes a stat
   booster** (the Super Tool roll likewise with the Super Tool Kit), and Requisition hides
   Tools.
4. **Rares:** ~12 in a mid Chrysler climb, nearly all tier-4 stat boosters by the EXP
   scale, which is the Chrysler reward players want; no change needed.

To firm this up: log a few Chrysler floors (fights per floor, EXP, drops) once an EX Game
save exists.

---

## 11. Confirming it with a logged playthrough

The loot logger already records every battle (room, EXP, drops, steals) and pickup. To
turn this estimate into measured numbers:

- Play with **Debug → Loot logger** on, at least a stretch of **Day 4 and Day 5** (no data
  yet; they decide most of the balance).
- Note the in-game day when a session starts (or a day column can be added to the log).
- From the log: battles per area, EXP per battle, vanilla Junk drops, and time per battle;
  these replace the guessed Day 4–5 EXP per fight in section 3, and the options table is
  re-run.

**Biggest uncertainties, in order:** Day 5's battle count (45–75), Day 4's EXP per fight
(sets whether a cap of 10–12 bites there), and dismantle income (depends on how much found
gear a player breaks down). The cap recommendation holds across the whole low–high range;
the early-pace choice (question 3) is the one most sensitive to the real counts.
