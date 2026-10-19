# Calibration: PE powers pause enemies, the logged casts and boss controllers — October 19, 2026 (Claude)

This pass continues `pe-aya-pe-items-2026-10-19.md`. Every change is opt-in, so the earlier
calibration files reproduce.

## Source rules added (decomp)

| Rule | Where | Model |
|---|---|---|
| Haste weakens defense | `entity/combat.c` `Entity_ResolveDropTable`: state flag 0x100 (AYA_HASTE) cuts the defense term `stat20/5` to 3/10 | PE Haste now sets 0x100 on the player status (`enemy_damage` `player_flags`); stiffness cure on cast |
| Barrier | `Battle_ApplySpellEffect` (cost maxPE/3); `Entity_ResolveDropTable` (with 0x200: no gauge halving, PE −= damage × (4·maxPE / maxHP), HP untouched); `Entity_UpdateTimers` (ends at PE ≤ 1) | `PE.barrier_hit`; HP-share effects blocked (player_status already checks 0x200) |
| Detox | `Battle_ApplySpellEffect` | Clears poison unless the immunity pair is set |
| Slow | `Battle_ApplySpellEffect` (enemy coreFlags bit 1); `Battle_UpdateEnemy` (charge step × 3/5) | Clock flag 1 on the lowest-HP targetable foe |
| Confuse | `Battle_ApplySpellEffect` (coreFlags bits 1–3 = 3–5, entity flag 0x1000) | Enemy skips 3–5 charge cycles (EnemyClock incapacitated path) |

Slow and Confuse land with certainty when the target's status pair reads 2, and on a coin flip
at 0. The catalog has no `statusFlags2`, so the coin flip is used (labelled).

## Behaviour and log-derived rules (labelled)

- **PE powers pause the enemies** for the whole cast and can't be interrupted (user observation).
  Items stay a committed action.
- **`--logged-casts`:** replays each battle's logged casts (Heal1–3, Detox, Haste, Barrier, Slow,
  Confuse) in place of the generic policy:
  - heals below half HP;
  - Detox only while poisoned;
  - buffs while absent;
  - Slow and Confuse early.

  Items still follow the policy. Liberate, Scan, Gene Heal and Preraise are dropped (no effect
  modelled).
- **`--controllers`:** boss cores logged at 10 HP are untargetable and the battle ends without
  them:
  - room 123 0x0312: HP 1000010; never hit by Aya; one scripted hit for 1000010 at the end;
  - room 273 0x0325: never hit; `died=0`.

  The other +1000000 HP values (rooms 188, 245, 273 parts, 350, 429) are scripted phase offsets.
  Aya hits those foes normally, so their stripped HP stays the damageable amount.
- **`--multi-kind`** is now available in the calibration (the identity fixes and silent parts).
- **`--boss-cap 400`:** six logged boss fights run 125–282 s, past the old 90 s sim cap, which
  truncated their damage.
- Fixed: `sim_rounds` had been swallowed into a comment, and the run header claimed PE battles
  were excluded under `--pe`.

## Results

All runs use `--serial --pe --evade-melee-early 0.6 --atb-guard --logged-charge --log-era`,
reaction 30 paused, 4 fights per battle. Damage taken, log → sim ratio (r):

| Group | n | PE pause | + logged casts | + multi-kind | + boss cap 400 | + controllers (current best) |
|---|---:|---|---|---|---|---|
| All ordinary | 143 | 0.93 (0.67) | 1.04 (0.75) | 1.04 | 1.04 | **1.04 (0.75)** |
| Day 2–4 ordinary | 33 | 1.05 | 1.10 | 1.10 | 1.10 | 1.10 (0.56) |
| Day 5 ordinary | 10 | 0.64 | 1.06 (0.87) | 1.06 | 1.06 | 1.06 (0.87) |
| Disc2 ordinary | 92 | 1.00 | 0.97 | 0.97 | 0.97 | 0.97 (0.65) |
| All bosses | 28 | 0.83 | 0.85 | 0.71 | 0.78 | **0.84 (0.57)** |
| Day 2–4 bosses | 5 | 1.95 | 1.01 | 0.57 | 0.57 | 1.25 (0.89) |
| Day 5 bosses | 8 | 0.56 | 0.96 | 0.96 | 0.98 | 0.98 (0.60) |
| Disc2 bosses | 11 | 0.76 | 0.83 | 0.69 | 0.77 | 0.80 (0.38) |
| Boss fallback share | | 0.28 | 0.27 | 0.00 | 0.00 | 0.00 |

Notes on the columns:
- Without multi-kind, the boss figures relied on fallback damage, about 27% of boss hits.
  "+ multi-kind" is the first all-source boss column.
- The Day 5 gap was the logged player's own casts. Each cast costs a gauge fill (more enemy
  time), and Haste cuts Aya's defense term. It was not missing enemy power.

Files: `pe-calibration-logged-serial-pe-pause-`, `-serial-pe-casts-`, `-serial-pe-casts-mk-`,
`-serial-pe-casts-mk-cap-`, `-serial-pe-casts-mk-ctl-2026-10-19` (md + data json).

## Scripted boss HP, read from the per-slot hit log (`--controllers`)

The log reader now keeps each enemy's hit list (`raw_battles`). The `+1000000` marker means the
room script watches for HP < 1,000,000.

| Case | Evidence | Model |
|---|---|---|
| Threshold ends the fight | Every marked boss except 188: the next hit is a scripted kill for the rest | Stripped HP = the real HP (unchanged) |
| Second phase | Room 188 0x021A: the reset hit `dmg=999660 left=300`; actor 5 `Entity_SetField` 44 / 45 = 300 | `phase2_hp` = 300, refilled once (`engine`) |
| Untargetable controller | Rooms 123 / 273: 10-HP cores never hit by Aya | `controller`: not targeted, not needed for victory |
| Never engaged | One hit for the whole HP when the boss dies (room 269 slots 3–6, a room 245 0x0421, a room 159 0x0016) | Dropped from the battle |

Room 269 goes from 2635 sim vs 960 logged to **1067 vs 960** (13.75 vs 14 turns). Before, four
0x021B parts attacked; in the log only two ever engaged.

## Aya's offense is validated

Damage dealt per turn, log vs sim, from the new `logged_dealt` / `sim_dealt` columns (marked
bosses excluded):

| Group | Logged | Sim |
|---|---:|---:|
| Day 1 | 14.5 | 13.6 |
| Day 2–4 ordinary | 49.8 | 44.9 |
| Day 2–4 bosses | 61.7 | 54.3 |
| Day 5 bosses | 68.8 | 57.9 |
| Disc2 ordinary | 145.6 | 140.5 |
| Disc2 bosses | 246.4 | 242.3 |

## Current best (`pe-calibration-logged-best-2026-10-19`)

All flags above plus `--controllers`. Damage taken, log → sim:

| Group | n | Ratio (r) |
|---|---:|---|
| All ordinary | 143 | **1.04 (0.75)** |
| Day 2–4 ordinary | 33 | 1.10 |
| Day 5 ordinary | 10 | 1.06 (0.87) |
| Disc2 ordinary | 92 | 0.97 |
| All bosses | 28 | **0.67 (0.71)** |
| Day 2–4 bosses | 5 | 1.25 (0.89) |
| Day 5 bosses | 8 | 0.94 |
| Disc2 bosses | 11 | 0.60 (0.55) |

The boss ratio fell when room 269's double count was removed, while the correlation rose. What's
left is a shortfall concentrated in a few long Disc2 fights.

## Remaining boss gaps

- **Out-of-reach turns (188, 245, 256, 350):** the logged player spent only 1.2–2.4 rounds per
  turn, against 3.5–5.5 in 273 and 429. Shots ≈ hits, so these are turns without firing, where
  the boss was out of reach. Damage dealt per turn there is 80–150 vs 205–305 in the sim, so the
  sim fights are 2–3× shorter in turns and take less damage. This is arena and boss movement,
  not modelled; the walk policy always closes in. Treat these as a known calibration limit.
- **273:** 1264 vs 239. The controller 0x0325 is the attacker and is not ported.
- **350 / 428 / 432:** see `pe-effect-ports-2026-10-19.md`.
- **Day 1:** 1.8× on a 4 HP average (small sample).

## Balance relevance

Haste's defense cut is a real source rule. A hasted Aya takes noticeably more damage per hit
(defense term × 0.3), which trades against faster turns. The rebalance runs don't cast Haste
outside bosses, and their boss policy casts it once.
