# Phase 3 report A: progression mechanics audit (2026-10-17)

Source-of-truth table for every resource the phase 3 economy simulator uses. Tags:
**D** decomp (function cited), **R** read from game RAM / item table, **L** play log
(`pe_play_log.csv`, one complete first playthrough, 2026-10-13..16), **A** assumed.
CURRENT = the Recomp mods as built today (`parasite-eve-recomp/src/mods`), VANILLA = the original game.
Code: `tools/pe_weapon_sim/economy/rules.py` keeps the same list as `VALIDATION`.

## A. Bonus Points

| Rule | Vanilla | CURRENT | Source | Tag |
|---|---|---|---|---|
| Earned per defeated enemy | max(0, rewardBase − rewardFactorA × hits that enemy landed on Aya) | same | `battle/enemy_movement.c` ~388; hit counter `menu/main_update.c` ~496 | D |
| Logged per enemy | `bp=base/A/hits` on enemy rows | same | play log | L |
| Battle total → where | added to a **pending pool** | same | `menu/main_menu.c` Aya_SetTotalExp | D |
| When the pool becomes spendable | **only when that battle's EXP makes Aya level up**; then pool → spendable, total capped at 99,999 | same | Aya_SetTotalExp (`bonus <= 0x1869F`) | D |
| Evidence | save rows stay at 1,326 BP across 5,000 EXP of farming with no level-up; the end-of-run gap (4,406 earned vs 4,029 banked) is the unbanked pool | | log | L |
| Other BP sources | none found (no level-up bonus, no story award) | the BP-floor mod exists but is **off by default** since 2026-10-13 | log: kept battles' BP = banked + pool | L |
| Carries forward | yes, spendable BP persists in the save | same | save rows | L |
| EX game | the log's next new game starts with 3,029 BP (carried or an EX bonus; not investigated) | same | log | L |
| Repeatable | yes: every battle, so farming earns BP (but only banks at the next level-up) | same | | D |
| Damage taken affects BP | **yes**: each hit an enemy lands costs rewardFactorA of that enemy's BP | same | | D |

Spending (`menu/item_actions.c` Menu_SpendBonusPoints, D):

| Target | Cost | Gain | Cap | Notes |
|---|---|---|---|---|
| Weapon attack / range / bullets | 100 BP | +1 bonusStats | 999 | becomes an ordinary bonus: **transferable by Tool** (TRANSFER_STAT reads only bonusStats) |
| Armor defense / PE / CR evade | 100 BP | +1 bonusStats | 999 | same |
| Active Time (stat22) | 100 BP | +1 stat level = stat22 +1 (table 50, 51, ...) | table | permanent, every weapon benefits |
| Item capacity | 100 BP | +1 stat level (capacity table: 10..20, then +1 every 1-3 levels) | 50 slots | permanent |
| Refund | only back to the value when the menu opened | | | |
| Cost increase | none (flat 100) | | | |

ATB: gain per tick = stat22 × class factor / 10, full at 9000 (D, phase 1). +1 stat22 is +1.2-2.0%
faster filling at levels 21-33. Whether the bar refills during the firing animation is **not
measured** (phase 1 "overlap" assumption, A); it decides how much Active Time is worth (report C, K).

## B. Weapons and donor equipment

| Rule | Value | Source | Tag |
|---|---|---|---|
| Base stats, built-in bonuses, slots, slot caps, effects | item table read from RAM | `findings/data/pe-items-baseline-2026-10-11.csv`, `pe-weapons-game-2026-10-16.csv` | R |
| Every gun / armor carries a small built-in bonus | +0..+2 per stat (USP TU +1/1/6, MAG +1/0/1, M10B +1/0/1, AT4-1 +0/30/0, LAW80 +20/0/0) | item table | R |
| Fixed locations (first playthrough) | Carnegie Hall / sewer (Day 1), Central Park, Soho, 17th Precinct, Hospital (Days 2-4), Chinatown, sewer, Warehouse, Subway, Museum (disc 2) | `pe-gear-locations-2026-10-11.csv` (wiki) mapped by the run's own pickups | A/L |
| **Chrysler Building gear** | EX game only (77-floor bonus dungeon) — excluded from a first run | game structure | A |
| Fixed pickups repeatable | no (one each) | | D/L |
| Enemy weapon drops | rare: the run got G23 ×2, AT4, M8000 from boss drops | log rewards | L |
| Wayne's 300-Junk guns | VANILLA: 300 Junk *items*; the run saw 9 vanilla Junk drops all game → not reachable in a first run | log | L/A |
| | CURRENT: hand in 300 Junk (the economy counter) at Wayne, from Day 5; the run built USP TU (end of Day 5) and P90 (disc 2) | `pe_loot.c` PE_WAYNE_CRAFT_COST; log `wayne` rows | D/L |
| Non-transferable | Maeda's guns, Dress (flags & 0x40) | `item_actions.c` ~1072 | D |
| The run's donors | 28 gear items picked up in the field; 23 dismantled (plus Tool salvages) | log | L |

## C. Rare drops (CURRENT `pe_loot.c`; VANILLA has none)

| Rule | Value | Tag |
|---|---|---|
| Roll | once per won battle, at Aya_SetTotalExp | D |
| Soft pity (Normal preset) | chance = 4% + 1% per dry battle; certain at 25 dry; Relaxed / Grind scale base, step and guarantee (150/150/72%, 50/60/132%) | D |
| Reset | dry counter → 0 on any rare | D |
| **Lucky Find** (worn armor) | a dry battle adds **2** to the counter instead of 1 (pity progresses twice as fast); it does not change the cascade or the item odds | D (`pe_pity_step`) |
| Cascade order (first to pass its check and roll) | Economy mod 15% (guarantee every 8 rares while one is locked) → Super Tool 6% (skipped with a Super Tool Kit) → Mod Permit 15% (skipped with 2+ held; guarantee 8) → Lucky Charm (removed: always skipped) → Duper Junk 4% (150 Junk) → Super Junk 8% (75 Junk) → **Tool 85 / 65 / 40 / 20 / 10% by Tools held (bag + storage), skipped at 5+ or with a kit** → stat booster (always) | D |
| Booster | one of 6 stats at random; tier by the battle's EXP: <20 +1, <60 +2, <150 +3, else +4 | D |
| Guarantee counters | count rares only while the entry isn't skipped | D |
| Run's result | 140 loot rolls, 14 rares: 5 Tools, 2 Super Junk, 2 Permits, 1 Super Tool, 4 boosters, 3 economy mods | L |

## D. Tools and Super Tools

| Rule | Value | Source | Tag |
|---|---|---|---|
| Stat transfer | **all three** bonuses of the source add to the target (`src + dst < 1000 ? sum : 999`, the excess is lost); source bonuses → 0 | `item/armor_capacity.c` Inv_TransferItemBetweenLists | D |
| Mod transfer | one mod: same group on the target → overwritten, else the first empty slot | same | D |
| **Plain Tool** | consumed; **the donor is deleted** (its loaded ammo goes back to the pool) | same: `!(flags & 1)` → DeleteSlot(source) | D |
| **Super Tool** | consumed; the donor **survives** with zeroed bonuses (or minus the moved mod) | same: cost item kind 13 | D |
| Stat and mod transfers | separate actions, one Tool each | menu flow | D |
| No room for a mod | dialog "no room" — and the code still consumes the Tool and deletes the donor (no early return; not runtime-tested; the simulator's players never try) | armor_capacity.c | D |
| Tool Kit / Super Tool Kit | transfers free (count shown as 999) | `menu/inventory.c` | D |
| Transfers from Wayne's storage | allowed at Wayne (flags & 2 consumes a stored Tool) | armor_capacity.c | D |
| CURRENT salvage | a plain-Tool donor counts as dismantled: Catalog unlock, dismantle Junk, Rebuild list | `pe_loot_catalog.c` pe_on_tool_transfer | D |
| Sources | field pickups (the run: 14 outside battle), boss / enemy drops (~2), rare cascade (5), Requisition (CURRENT: 40 Junk, +10 per Tool bought, max 100) | log, `pe_loot_shop.c` | L/D |
| Premium Mod Catalog installs | also cost a Tool (CURRENT) | `pe_loot_catalog.c` | D |

## E. Stat boosters

| Rule | Value | Tag |
|---|---|---|
| Items | OFFENSE 0x1D-0x20, RANGE 0x21-0x24, BULLET CAP 0x25-0x28, DEFENSE 0x29-0x2C, CR EVADE 0x2D-0x30, PE 0x31-0x34 | R |
| Amount | +1 / +2 / +3 / +4 by tier | R |
| Use | applied from the menu to a chosen item's bonusStats (cap 999), consumed | D (`item_actions.c` ~1127) |
| Transferable after | yes (ordinary bonusStats) | D |
| Sources | field (the run: 33 outside battle, mostly OFFENSE +1 and DEFENSE +1), vanilla drops, rare cascade | L |

## F. Customization (CURRENT; VANILLA has only Tool mod transfers and Torres' random tune-up)

| System | Rule | Source | Tag |
|---|---|---|---|
| Dismantle | any carried, unequipped gun / armor: its effects unlock in the Mod Catalog; pays 5 + 2 × bonus sum + 3 per mod + 2 per already-unlocked mod (×1.5 Salvager, cap 150); goes on the Rebuild list | `pe_loot_catalog.c` pe_salvage_payout (24 logged dismantles match) | D/L |
| Mod Catalog | install an unlocked effect into a slot of the equipped gun / armor: 10 (common) / 30 (mid) / 80 Junk (premium: RoF 10, Attack All, Cyanide, 2 / 3 Commands; + a Tool unless a kit is carried); group rule; removal free (stays unlocked); bag mods never removed | same | D |
| Mod Permit | +1 slot on a bag item, at Wayne, while slots < min(slot cap, 10) | `pe_wayne_menu.c` pe_at_max | D |
| Rebuild | buy a dismantled item back at payout × 1.5 (cap 150) with its bonuses, empty slots | `pe_loot_catalog.c` | D |
| Junk | battle: min(cap, 1 + EXP/8) (+25% × (4 − hits)/4 if hits < 4), cap 12 / boss 25, × preset (Normal 100%), +50% Scavenger; vanilla Junk drops; Super / Duper Junk = 75 / 150 | `pe_loot.c` | D |
| Requisition | goods, Tools (above), economy mods (Bargain 125, Scavenger 300, Lucky Find 225, Salvager 75 until unlocked) | `pe_loot_shop.c` | D |
| Effects by availability | RoF 2/3/5, Random, Burst, Heat, Frost, Acid, Tranq, Counter, Quickdraw, Critical, 2 Commands on first-run gear; RoF 7 (M10, MP5PDW); RoF 10 and Attack All only on P90 (a Wayne gun) or EX guns; **3 Commands and Cyanide are EX-only** | item table + locations | R/A |

## G. Other progression resources

| Resource | Rule | Tag |
|---|---|---|
| EXP / level | levelExp table (R): level 7 at Day 1's end, 18 by Day 4, 24 at Day 5's end, 33 at the end (L) | R/L |
| Level-up | +1 stat level on every track (offense, Active Time, capacity, HP ...) | R |
| Offense | level table at 7/12/16/19/21/24/27/33 (R), linear between (A) | R/A |
| Capacity | capacity table by stat level (R); armor bag mods +1/+2/+4 | R |
| Storage | Wayne's trunk, 100 slots, at Wayne only | D |
| Money | none in PE; Junk is the CURRENT economy | |

## Corrections to earlier phases found in this audit

1. **BP is banked only at level-ups.** Phase 1/2 used fixed budgets; a real run leaves the BP of
   every battle after the last level-up unspendable (the run: 377 BP; simulated players up to ~1,100).
2. **A plain Tool deletes the donor.** `progression.py` (phase 1/2) says "the source item stays"; that
   is Super Tool behaviour. Phase 1/2 results are unaffected (they never reused a donor), and phase 1/2
   code is left unchanged; the phase 3 model follows the decomp.
3. **Lucky Find speeds up pity; it doesn't change drop tables.**
4. **"Chrysler Building" gear is EX-game**, so 3 Commands and Cyanide are not first-run effects (as phase 1 said).
5. The play log's late "Day 1" rows are disc 2 (Day 5 night to the end); phase 3 calls that phase **Disc2**.

## Open items (bounded by sensitivity runs, report K)

- ATB refill during the firing animation (overlap vs serial) — decides Active Time's value.
- Per-bullet firing time (phase 2's open item) — flips P90 RoF 7 / 10.
- Armor defense in the enemy damage formula (not in the combat model).
- Optional pickups a minimal or completionist player skips / finds (profiles are bounded assumptions).
- Vanilla enemy drop chances (Entity_ResolveDropTable): the logged drops are replayed, not modelled.
