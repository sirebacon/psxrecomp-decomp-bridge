# Parasite Eve loot: cascading rare drops (design, 2026-10-14)

Status: **agreed with the user 2026-10-14, not built yet.** Replaces the weighted rare table
of the loot overhaul (phase 2, decision 18) and settles the open checklist item "Economy
mods, final source". Companion docs: [`pe-loot-overhaul-design-2026-10-11.md`](pe-loot-overhaul-design-2026-10-11.md),
[`pe-loot-balance-estimate-2026-10-13.md`](pe-loot-balance-estimate-2026-10-13.md),
[`pe-loot-overhaul-checklist.md`](pe-loot-overhaul-checklist.md).

## 1. Why

The weighted table (Tool 40, stat booster 35, Super Junk 4, Duper Junk 2, Mod Permit 7,
Super Tool 3, economy mod 6, Lucky Charm 5) can't tell when an item has stopped being
useful, and its small weights starve the items that matter most:

- an average run finds **about 1 of the 4 economy mods**; only **2%** find all four;
- **Mod Permits** come about once a run (1 in ~140 battles), although they now buy mod
  slots at Wayne's and Warner's;
- nothing in it can grow with custom drops.

## 2. Shape

1. **Pacing gate (unchanged):** each won battle rolls today's soft pity (Normal: 4% + 1% a
   dry battle, certain at 25; presets scale base, step and guarantee). Lucky Find and an
   active Lucky Charm still double pity progress. About one rare per 10 battles on Normal.
   **At most one rare per battle.**
2. **Cascade (new):** when the gate passes, walk an ordered list from the top. Each entry
   has a chance, a **skip check** ("is this still useful?") and optionally its own
   **guarantee** (certain after N rares without it). A skipped entry is treated as absent:
   its share falls through to the entries below. The first entry that passes its check
   and its roll is the drop. The last entry always hits.
3. **Data-driven:** an entry is `{item, chance, skip check, guarantee}`. New custom drops are
   one entry each; boss or area lists (e.g. Chrysler) can reuse the same machinery later.

Rarest and most valuable first, so they get a fair roll and aren't crowded out by common
items.

## 3. The list

| # | Entry | Chance | Skipped when | Guarantee |
|---|---|---|---|---|
| 1 | Economy mod (tiered, section 5) | 15% | all four unlocked | after 8 rares without one |
| 2 | Super Tool | 6% | Super Tool Kit carried | — |
| 3 | Mod Permit | 15% | **2 or more held** | after 8 rares without one |
| 4 | Lucky Charm | 8% | one carried or active | — |
| 5 | Duper Junk | 4% | — | — |
| 6 | Super Junk | 8% | — | — |
| 7 | Tool | by Tools held (section 4) | Tool Kit carried, or 5+ held | — |
| 8 | Stat booster (tier by battle EXP, as today) | always | — | — |

"Held" counts the bag and Wayne's storage. Guarantees count rares, not battles, and only
while the entry isn't skipped.

Per-rare odds (economy mods still missing → all found; Tool at the 40% middle value):

| Entry | Missing | All found |
|---|---|---|
| Economy mod | 15% | — |
| Super Tool | 5.1% | 6.0% |
| Mod Permit | 12.0% | 14.1% |
| Lucky Charm | 5.4% | 6.4% |
| Duper / Super Junk | 2.5% / 4.8% | 2.9% / 5.7% |
| Tool | 22.1% | 26.0% |
| Stat booster | 33.1% | 39.0% |

## 4. Tools follow need

Tools are worth the most early and pile up late, so the Tool chance depends on how many the
player holds instead of on the story day:

| Tools held | 0 | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|
| Tool chance | 85% | 65% | 40% | 20% | 10% | skipped |

Early, about 6 of every 10 rares that reach the Tool row are Tools; late, the share drops on
its own and those rolls fall through to stat boosters. With the Tool Kit the row is skipped
(today's "Tool roll becomes a booster" rule, generalised).

## 5. Economy mods are not equal: tiers

Worth over a mid run (balance estimate: ~2,200 Junk earned, ~410 from dismantling, ~16
rares):

| Mod | Effect | Worth over a run |
|---|---|---|
| Scavenger | battle Junk +50% | ~+850 Junk (nearly 3 Wayne guns) |
| Lucky Find | pity builds twice as fast | ~+6 rares (16 → ~22) |
| Bargain | prices −15% | ~+150–250 Junk, by spending |
| Salvager | dismantle Junk +25% → **+50%** (change) | ~+100 → ~+200 Junk |

- **Drop weights within the economy-mod entry:** Salvager 4, Bargain 3, Lucky Find 2,
  Scavenger 1, over the mods still missing. The guarantee picks the same way.
- **Requisition prices by tier** (were 150 each): Salvager **75**, Bargain **125**, Lucky Find
  **225**, Scavenger **300**. Preset and Bargain modifiers apply as for every price. The
  shop listing stays (it is the way to buy the one you want).
- **Salvager** raised from +25% to +50% dismantle Junk so it is worth an armor slot; the
  other three unchanged.

## 6. Mod Permits

- Vanilla: Baker gives two on Day 2; showing Torres one adds a mod slot to an item. In the
  mod, Wayne's and Warner's boxes have a **Mod Permit** option (built 2026-10-14, PE
  `33b368c`): pick a gun or armor, Yes / No, the permit is only spent on Yes; the game's own
  per-item maximum (record +0x01, at most 10) applies.
- **No refunds.** A spent permit stays spent, so permits stay scarce and building up a gun
  is a choice.
- **Built-up items are never lost:** Rebuild already remembers a destroyed item's slot
  count (Dismantle, Discard-dismantle and plain-Tool donors all record it), so a rebuilt
  item comes back with the slots bought for it (installed mods are reinstalled from the
  Catalog, as today).
- **Rebuild-list protection (change):** the list holds 30 and drops the oldest when full.
  It now drops the oldest **ordinary** entry first and never one with permit-added slots
  (slot count above the base item's default). Raising the cap instead doesn't fit: the game
  has 86 weapons and 51 armor, and the save's free tail is ~880 bytes. Rebuild rows show
  built-up items, e.g. "M16A1 +2 slots".
- **No Junk loop (Salvager + Rebuild):** a rebuilt item comes back with its +bonuses and
  slots but no installed mods, so dismantling it again pays `5 + 2 x bonuses` (+Salvager).
  Rebuild costs payout x 1.5, after preset and Bargain, floored at the payout and capped at
  150. That already loops today on Relaxed + Bargain + Salvager +25% (floor x1.0 < x1.25),
  would loop on Normal + Bargain + Salvager +50% (x1.275 < x1.5), and loops on top-tier guns
  whose payout reaches the 150 cap (rebuild 127 with Bargain). **Rule:** the rebuild price is
  at least `(5 + 2 x bonuses) x 1.5 + 1` (what the rebuilt item could pay back with the
  strongest Salvager, before any cap), applied after every discount and above the 150 cap
  when needed. Independent of history, preset, Bargain and Salvager; ordinary prices are
  unchanged (the markup on the original payout, mods included, is already higher).
- **Drop rule:** skipped while 2 or more are held, so drops pause for a hoarder and resume
  once one is spent. Permits are always useful otherwise (no story-day fading, no slot-room
  check: gun churn doesn't waste them because Rebuild keeps the slots).

## 7. Simulation (20,000 runs, Normal)

Run model: balance estimate section 3, mid (10 / 25 / 17 / 25 / 60 / 10 fights on Days 1–6
plus ~14 bosses, 161 won battles; EXP per fight 4 / 20 / 55 / 100 / 950 / 1,500). Player
model: Baker's second permit held from Day 2; a held permit is spent 12 battles after it
arrives; vanilla chests give ~17 Tools spread over the run and a Tool is used every 8
battles; a Lucky Charm is used at the next win; no Tool Kit in the main story; Lucky Find
worn once found (tier report only). Script: `loot_sim.py` (session scratchpad; rerun with
`python loot_sim.py 15 8 40 "85,65,40,20,10"`).

Mean per run (rares per run unchanged at **16.4**):

| Item | Today (weighted) | Cascade (final) |
|---|---|---|
| Economy mods (of 4) | 0.95 | **2.95** |
| Mod Permit | 1.1 | **2.6** |
| Super Tool | 0.5 | 0.8 |
| Lucky Charm | 0.8 | 0.8 |
| Duper / Super Junk | 0.3 / 0.6 | 0.4 / 0.7 |
| Tool | 6.5 | **4.5** |
| Stat booster | 5.7 | **3.7** |

Tools by day (Days 1–3 / 4 / 5 / 6): today 2.4 / 1.1 / 2.6 / 0.5; cascade 2.1 / 0.7 / 1.5 / 0.2.

- All four economy mods found in 34% of runs (2% today); one by the end of Day 3 in 64%
  (29% today).
- Permit drops were paused by the cap on ~2 of 161 battles (only a hoarder hits it).

Economy mods by tier:

| Mod | Found in a run | By end of Day 4 | Median day |
|---|---|---|---|
| Salvager | 90% | 56% | 4 |
| Bargain | 86% | 48% | 4 |
| Lucky Find | 72% | 34% | 5 |
| Scavenger | 65% | 22% | 5 |

Iterations: a first cascade (economy 20% / guarantee 6, flat Tool 50%) gave 3.6 economy
mods (all four in 68%), 3.8 Tools and 3.9 boosters; economy was too fast and early Tools too
few (1.3 on Days 1–3). 15% / guarantee 8 and need-based Tools fixed both.

## 8. Build notes

- `pe_loot.c`: replace `s_rare_table` / `pe_pick_rare` with the cascade table and walker;
  keep `pe_roll_rare` (the gate) as is. Per-entry guarantee counters go in the save-state
  block `pe.loot` and the save tail (bump versions; old saves start the counters at 0).
- Economy-mod pick: weighted 4/3/2/1 over missing mods (`pe_econ_missing`).
- `pe_loot_shop.c`: per-mod prices 75 / 125 / 225 / 300 (the "Economy mod price" tuning row
  becomes a scale, or four rows).
- `pe_loot_catalog.c`: Salvager +50%; rebuild price floor `(5 + 2 x bonuses) x 1.5 + 1`
  (section 6, no Junk loop); Rebuild list drops the oldest entry without bought
  slots; Rebuild rows mark "+N slots".
- F1 tuning: keep Rare base / step / guarantee; add the economy and permit guarantees.
- Play log: the `loot` row gains the cascade path (entries skipped, entry hit) so drops can
  be checked against this doc.
- Then rerun this simulation against logged Days 4–6.
