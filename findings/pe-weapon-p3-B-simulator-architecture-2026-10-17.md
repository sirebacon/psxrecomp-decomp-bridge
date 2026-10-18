# Phase 3 report B: simulator architecture (2026-10-17)

Package `tools/pe_weapon_sim/economy` sits on top of the phase 1/2 combat simulator, which it
imports and never modifies (`engine.py`, `rules.py`, `data.py`, `encounters.py`, `run_benchmark.py`,
`run_phase2.py` unchanged; phase 1/2 outputs reproduce as before).

## Modules

| Module | Role |
|---|---|
| `campaign.py` (pe_weapon_sim) | Builds the campaign script from the play log: the final timeline of the first playthrough (save-state / card-load branches removed by walking the log backwards on the progress clock *cumulative EXP, play time*), every won battle with its enemies (EXP, BP base / factor / hits on Aya, resist bits, drops), vanilla reward items, field pickups, save rows (the logged loadout over time). Output `findings/data/pe-campaign-2026-10-17.json`. |
| `economy/tables.py` | Game tables: levelExp, offense, Active Time and capacity by stat level, booster ids, effect codes and groups, Catalog price tiers, item table, gear locations → phases. |
| `economy/rules.py` | Economy rulesets VANILLA / CURRENT (frozen `MappingProxyType`), `variant()` for experiments and sensitivity, `ablation()` A1-A8, `VALIDATION` (every rule with its tag and source). |
| `economy/bp.py` | `Ledger` (earned, pending pool, banked, spent by category, lost to hits, capped; `check()` proves no BP is created or lost), `Aya` (EXP → level, stat22 and capacity with bought stat levels). |
| `economy/loot.py` | 1:1 port of `pe_loot.c`: battle Junk, soft pity, the rare cascade with skip checks and guarantees, prices. State read at roll time through `LootView` (Tools held, permits held, kits, unlocked economy mods, Lucky Find, Scavenger). |
| `economy/equipment.py` | `Item` instances (unique uid, base stats, bonuses with **per-point provenance**, mod slots, history), `transfer_stats` / `transfer_mod` exactly as `Inv_TransferItemBetweenLists`, boosters, Mod Permits, dismantle payout, `Catalog` (unlocks, prices, group rule). |
| `economy/inventory.py` | Bag (gear, Tools, Super Tools, permits, kits, boosters, a consumable reserve that grows by phase) and Wayne's storage. |
| `economy/acquisition.py` | Event stream per exploration profile from the campaign script; gear from the location table; Wayne visits. |
| `economy/surrogate.py` | Fast loadout score (expected damage per second from the engine's own formulas; memoised) for routine decisions and the combat-feedback loop. |
| `economy/policies.py` | Player policies A-I and BP-strategy variants; every decision is a call to a `Run` transaction. |
| `economy/playthrough.py` | `Run`: the persistent state, all transactions (gain, transfer, install, dismantle, spend BP, buy Tool, permit, Wayne gun, equip), the battle step, checkpoints, the transaction log; `play()`. |
| `economy/evaluation.py` | Checkpoint benchmarks through `engine.fight` on encounters built from the enemies the run met in each phase; cache; surrogate validation. |
| `economy/run_phase3.py` | Experiments, statistics, traces → `findings/data/pe-weapon-p3-results-2026-10-17.json`. |
| `economy/reporting.py` | Markdown tables from the results file (`pe-weapon-p3-tables-2026-10-17.md`). |

## State model

Run state = Aya (EXP, bought Active Time / capacity levels) + BP ledger + Junk (+ Tools bought) +
loot state (dry counter, guarantee counters, history) + Mod Catalog (unlocked effects, Rebuild list)
+ inventory (bag, storage) + every Item ever owned (alive or not, with history) + the equipped gun,
armor and (two-weapon players) second gun + metrics. Every change is a transaction method on
`Run`; with tracing on, each appends a log line (`findings/data/pe-weapon-p3-trace-*.txt`).

Invariants checked after every event (tests): ledger balance (banked + pool + spent + capped =
earned), bonus provenance sums equal bonuses, bonuses within 0..999, no negative stacks or Junk,
equipped items alive, deleted donors never reused.

## Resource flows

```
battles --EXP--> level-ups --bank--> spendable BP --100--> weapon / armor bonus | Active Time | capacity
   |  \--BP (base - A x hits)--> pending pool --------^
   |--Junk--> Requisition Tools / Catalog installs / Wayne gun (300) / Rebuild
   |--vanilla drops (gear, Tools, boosters)
   '--rare cascade (Tools by Tools held, permits, Super Tools, boosters, Junk bundles, economy mods)
field pickups --> gear (donors) / Tools / boosters / permits
gear --Tool--> all 3 bonuses to the target, donor deleted (salvaged: Junk + Catalog unlocks)
     --Super Tool--> same, donor kept
     --dismantle--> Junk + Catalog unlocks
boosters --> +1..+4 on a chosen item's bonus
```

## Combat feedback

Each battle replays the logged enemies. Hits an enemy lands on Aya are drawn Poisson with mean =
logged hits × (logged loadout's surrogate DPS / the player's DPS): a stronger loadout ends fights
sooner and takes fewer hits, so it keeps more BP (base − A × hits) and more no-hit Junk. The logged
loadout per battle comes from the save rows. Calibration: with the ratio forced to 1 the run's own
BP is reproduced (results: `policies.S_end|calib`).

## Random streams and matching

Run seed → independent streams `enc` (profile transformations, gear timing), `loot` (cascade),
`hits` (feedback), `policy` (casual randomness), `sens` (sensitivity scaling). Policies are compared
on matched seeds 1..N: identical encounters and gear, and the same loot stream (the cascade's draws
still depend on the player's state where the game's do — that is the Tool feedback loop). Policies
read only the current state.

## Approximations (where and why)

| Where | Approximation | Check |
|---|---|---|
| Routine battles | surrogate DPS instead of a full fight | Spearman rank agreement with the engine suite: report K |
| Checkpoints | full engine, 10 fights per encounter for 40 runs per group | CI in tables |
| Gear timing | a uniform battle within the gear's phase | profiles |
| Consumables | a bag reserve of 4 / 6 / 7 / 8 slots | run's save rows |
| Armor defense | not in the combat model | report K |
| Profiles | minimal / completionist / farmer transformations of the one real run | report K |

## Reproduction

```
cd tools
python -m pe_weapon_sim.campaign                       # campaign script from the play log
python -m unittest discover -s pe_weapon_sim/tests     # 55 tests (24 phase 1/2 + 31 phase 3)
python -m pe_weapon_sim.economy.run_phase3 --n 150 --bench 40 --workers 7
python -m pe_weapon_sim.economy.reporting              # tables markdown
```
