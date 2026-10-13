# Parasite Eve loot overhaul: balance estimate (phase 7 groundwork, 2026-10-13)

An estimate of how much Junk and how many rare drops a normal playthrough produces under
the overhaul's current numbers, built before a full logged playthrough exists. It combines
the code's formulas, the loot logger's real battles (Days 1–3), the game's level table and
facts from the walkthroughs. The aim is to find the numbers that matter most, so the
logged playthrough can confirm them instead of starting from nothing.

Design and decisions: [`pe-loot-overhaul-design-2026-10-11.md`](pe-loot-overhaul-design-2026-10-11.md)
(targets in 6.3, decision 34 for Wayne's pace). The model is a small Python script; its
inputs are all listed below, so any of them can be swapped for logger data and re-run.

---

## 1. Summary

- **A normal run has roughly 90–180 battles** (best guess ~145, bosses included). Not every
  room has a fight, and each trigger spot fires 100% the first time, then 45%, 20%, 10%.
- **Junk is back-loaded.** Junk per battle is `1 + EXP / 8`, capped at 30. Days 1–4 enemies
  give 4–70 EXP a fight (1–9 Junk); from Day 5 almost every fight hits the 30 cap. With
  today's numbers **Day 5 alone pays ~1,800 Junk**, more than Days 1–4 together (~760)
  and enough for six Wayne guns.
- **Days 1–4 look about right.** About 440 Junk by the end of Day 3 and 760 by the end of
  Day 4, before spending, which puts the first Wayne gun at the start of Day 4 for a light
  spender and mid-Day 4 or later for someone buying installs and Tools.
- **The rare-drop presets don't do anything yet.** Soft pity (4% +1% a dry battle) almost
  always hits before the guarantee, so Relaxed, Normal and Grind all give **one rare per
  ~9.5–9.8 battles** (~15 rares in a run, ~5 of them Tools on top of vanilla's ~17 chest
  Tools).
- **Recommendation:** lower the per-battle cap from 30 to **12**, pay bosses a flat **25**,
  and make the presets scale the pity **base chance and step** instead of the guarantee.
  That leaves Days 1–4 unchanged, roughly halves the late game (~1,800 Junk for the whole
  main story instead of ~2,950), and makes the presets real (one rare per ~7.6 / 9.8 / 13.8
  battles).

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

### 2.4 Levels and bosses (decomp level table, walkthroughs)

EXP to reach a level (resident data pack, `Aya_GetLevelExpTable`):

| Level | 10 | 15 | 20 | 25 | 30 | 33 | 35 | 38 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| Total EXP | 184 | 868 | 3,744 | 17,216 | 73,151 | 168,061 | 299,579 | 725,158 | 734,158 |

Above level 38 the curve goes nearly flat (+4,500 a level), which is the "level 38 cap"
the guides mention.

Anchors from Shotgunnova's walkthrough (private copy; facts only):

- Aya is **around level 20** when she reaches Black Widow (end of Day 4).
- Boss EXP: Sheeva 1,000 (Day 3), Black Widow 6,500 (Day 4), Crustacean 2,510 (Day 5),
  Triceratops 50,000 (Day 5). The other bosses' EXP isn't listed; the model guesses them
  (section 3). Under today's cap every boss from Day 3 on pays the 30 maximum anyway.

From these, Days 2–3 run about 20–45 EXP a regular fight and Day 4 about 70 (3,744 EXP by
Black Widow minus roughly 2,700 by the end of Day 3, over ~15–20 fights). Day 5 and Day 6
enemies give hundreds of EXP each; the exact figure barely matters, because anything above
232 EXP (today) or 88 EXP (with a cap of 12) pays the cap.

---

## 3. Battles per day (estimate)

Regular fights on a normal route, no deliberate grinding:

| Day | Areas | Low | **Mid** | High | EXP per fight (mid) |
|---|---|---|---|---|---|
| 1 | Carnegie Hall | 6 | **10** | 15 | 4 |
| 2 | Central Park, NYPD | 15 | **22** | 30 | 20 |
| 3 | NYPD, Soho | 15 | **22** | 30 | 45 |
| 4 | St. Francis Hospital | 14 | **20** | 28 | 70 |
| 5 | Chinatown, Warehouse, Sewer, Subway, Museum | 30 | **45** | 60 | 300+ |
| 6 | Final dungeon | 6 | **10** | 15 | 600+ |
| | **Total** | **86** | **129** | **178** | |

Plus about **14 bosses** (Day 1: 2, Day 2: 2, Day 3: 1, Day 4: 2, Day 5: 6, Day 6: 1).

Other income the model counts (per day, mid): vanilla Junk drops (0.8 a fight on Day 2,
falling to 0.2–0.4 later), the no-hit bonus (+8% on average), and dismantling the gear
you find (10 / 40 / 50 / 60 / 150 / 30 Junk on Days 1–6, ~340 in all, from ~25 dismantles
at 10–25 Junk each). Steals and empty steals are left out: they need a steal club
(Day 3) and are optional.

---

## 4. Junk income with today's numbers (Normal, mid battle counts)

| Day | Junk per fight | Fights | Bosses | Vanilla drops | Dismantles | **Day total** | **By end of day** |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 11 | 10 | 0 | 10 | **31** | **31** |
| 2 | 3 | 71 | 49 | 18 | 40 | **178** | **209** |
| 3 | 6 | 143 | 30 | 9 | 50 | **231** | **440** |
| 4 | 9 | 194 | 60 | 6 | 60 | **320** | **760** |
| 5 | 30 | 1,458 | 180 | 14 | 150 | **1,802** | **2,562** |
| 6 | 30 | 324 | 30 | 2 | 30 | **386** | **2,948** |

With low battle counts the run ends near 2,190; with high, near 3,770. Either way Day 5
dwarfs everything before it: going from 9 Junk a fight to the 30 cap overnight.

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
**150**; a heavy one (Tools, premium installs) about **300**.

---

## 6. Wayne's first gun (decision 34)

Target: affordable around **Day 4–5**, with **about 1–2 hours of optional fighting**;
vanilla's Day 4 gate is the ceiling.

With today's numbers (mid), the player has earned ~440 Junk by the end of Day 3:

- **Light spender (~150 spent):** ~290 left; the gun is affordable right at the start of
  Day 4 with no extra fighting. Slightly faster than the target.
- **Heavy spender (~300 spent):** ~140 left; Day 4's own fights (~230 Junk) get there
  mid-Day 4, or ~20 extra fights (~30–40 minutes) at its start.

So the early pace is close to the target, a little generous. The real problem is after:
on Day 5 every player can afford **five or six more Wayne guns**, Rebuild and premium
installs stop being decisions, and Junk stops mattering for the last third of the game
(against design rule "never pointless", 6.3).

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
and scaling it changes nothing. Over a mid run (~143 battles) that's **~15 rares**:
~5 Tools, ~5 stat boosters, ~2 Super/Duper Junk, ~1 Mod Permit, ~1 economy mod, ~1 Lucky
Charm and a 40% chance of a Super Tool. Five extra Tools on vanilla's ~17 seems right
alongside the shop's capped Tools.

**Fix:** let the presets scale the base chance and step too:

| Preset | Base / step / guarantee | One rare per |
|---|---|---|
| Relaxed | 6% / +1.5% / 18 | 7.6 battles |
| Normal | 4% / +1% / 25 | 9.8 battles |
| Grind | 2% / +0.6% / 33 | 13.8 battles |

---

## 8. Options compared

Cumulative Junk by the end of each day (Normal preset, mid battle counts; low–high range
for the run total):

| Option | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 (run) | Run range |
|---|---|---|---|---|---|---|---|
| **A. Today:** `1 + EXP/8`, cap 30 | 31 | 209 | 440 | 760 | 2,562 | **2,948** | 2,190–3,770 |
| **C. Cap 12, bosses a flat 25** | 31 | 184 | 410 | 707 | 1,604 | **1,791** | 1,400–2,230 |
| **E. Cap 12, `1 + EXP/12`, bosses 25** | 28 | 157 | 336 | 568 | 1,465 | **1,652** | 1,300–2,040 |
| **D. `1 + √EXP / 2`, cap 20** | 38 | 182 | 352 | 557 | 1,278 | **1,471** | |

- **C** keeps Days 1–4 as they are (the cap only bites from Day 5), halves the late game,
  and brings the run total in line with what the sinks can absorb (~1,700, section 5).
  Bosses still feel like a payday: 25 is over two regular Day 5 fights.
- **E** also slows Days 2–4 by ~20%, which moves the first Wayne gun to mid/late Day 4 for
  a light spender: closer to decision 34's "1–2 hours of optional fighting", but Days 2–3
  would pay only 2–4 Junk a fight.
- **D** flattens the whole curve but makes early fights feel worth the same as late ones
  and needs a new formula row in Debug → Loot tuning; C and E are just two existing rows
  and one new boss rule.

---

## 9. Proposed decisions (for the user)

1. **Per-battle cap: 30 → 12** (option C). Days 1–4 unchanged; Day 5–6 fights pay 12.
2. **Boss pay: a flat 25** for any battle worth ≥ 1,000 EXP (Sheeva onwards), instead of the
   cap. Early bosses (Days 1–2) keep the normal formula.
3. **Early pace: keep `EXP / 8`** (C) or **slow it to `EXP / 12`** (E) if the first Wayne
   gun should need real optional fighting on Day 4.
4. **Presets scale pity base and step** as in section 7, not only the guarantee.
5. **Keep** the floor (1), the no-hit bonus (25%), the rare table shares, dismantle
   payouts and all prices for now; revisit after the logged run.

---

## 10. Confirming it with a logged playthrough

The loot logger already records every battle (room, EXP, drops, steals) and pickup. To
turn this estimate into numbers:

- Play with **Debug → Loot logger** on. A short session per day is enough; Days 4–6 matter
  most (no data yet).
- Note the in-game day when a session starts (or a day column can be added to the log).
- From the log: battles per day, EXP per battle per area, vanilla Junk drops, and time per
  battle; these replace the "mid" columns in sections 3–4, and the options table is
  re-run.

**Biggest uncertainties, in order:** Day 5 battle count (30–60), how many fights players
take on backtracking, and the dismantle income (depends on how much found gear a player
breaks down). The cap recommendation holds across the whole low–high range; the early-pace
choice (3) is the one most sensitive to the real battle counts.
