# Aya's side: Parasite Energy and in-battle items — October 19, 2026 (Claude)

Module `parasite_energy.py`, opt-in `source_options['pe']`, calibration flag `--pe`.

## Source (decomp)

| Mechanic | Where | Model |
|---|---|---|
| PE regeneration | `menu/main_update.c` `Menu_MainUpdate` | While no action is committed (flag 0x100), the menu isn't paused and PE < max: rate −= 3 (min 1); step −= maxPE / (rate × 100) (min 0x1999, i.e. 0.1 PE); PE += step |
| PE start values | `aya/stats.c` track 3; level-table rows `max_atk` / `atb_rate` / `atb_step` | Level 20: max 502 PE, step 0.61 → decays |
| Spell effects and costs | `battle/attack.c` `Battle_ApplySpellEffect` | Heal 1 / 2 / 3: +30 / 60 / 280 HP, cost 60 / 120 / 500; Detox 100; Medic 600; Barrier max/3; Scan 50; Slow 90; Haste 200 (timer 0x1C2); Confuse 150; Gene Heal 400; Preraise 1000; Full Recover 1300; PE Light armor (effect 0x200) cuts costs by a third |
| Haste | `Menu_MainUpdate`, `entity/combat.c` `Entity_UpdateTimers` | Gauge fill + scaledOffense/2; timer −1 per update |
| Items | `battle/attack.c` `Battle_ApplyDamage` | Medicine 1–4 (ids 6–9): +45 / 90 / 180 / 400 HP; Full Recover (0x0A) to max |
| Mod rules (CURRENT) | `pe_pe_balance.c`, `pe_atb_items.c` | Heals 15 / 30 / 65% of max HP (never below vanilla). Quick powers (Heal 1/2, Detox, Medic, Scan, Slow, Confuse) and items work from a half bar for half a bar; other powers cost a full bar. Menu / targeting (battle phase 1) is paused |

Validation against the log:
- Logged heals match the vanilla amounts exactly: Heal1 ≤ 30, Heal2 ≤ 60, Heal3 ≤ 280, Gene
  Heal 1 per tick. The logged run predates the percentage heals.
- Regen happens only outside actions, which roughly matches the logged ~60–80 PE per turn.

## Not source (labelled options)

- **Cast and item duration:** `cast_updates`, default 60 battle updates.
  - **PE powers pause the enemies** for the whole cast, and the cast can't be interrupted (user
    observation, 2026-10-19; consistent with `Pm_StopLowerHalf` at the start of the power
    command). Modelled as a paused advance: no enemy charge, no strikes, no PE regen. Counted as
    `pe_pause_s`.
  - **Items** stay a committed action (serial rule): attacks already in progress can still land.
- **Player policy:**
  - heal below `heal_below` (0.5) of max HP with the best affordable known heal;
  - otherwise the smallest medicine that fits, Full Recover below 25%;
  - Haste on the first turn of a boss battle.
- **Not modelled:** Energy Shot (3 logged casts), Liberate (2), Barrier / Slow / Confuse / Detox
  as policy choices.

## Calibration with PE and items

`--serial --pe --atb-guard --logged-charge`, reaction 30 paused. Each battle gets its logged
starting PE, the spells known by then, its starting bag (end bag + used) and vanilla heals. The
36 battles with casts are now included.

| Group | Battles | Damage, log → sim (ratio) |
|---|---:|---|
| All ordinary | 143 | 24.5 → 26.1 (1.07) |
| All bosses | 28 | 338.6 → 316.5 (0.93) |
| Disc2 ordinary | 92 | 17.5 → 17.4 (1.00) |
| Disc2 bosses | 11 | 740.7 → 606.2 (0.82) |

- Casts per battle: 0.50 logged vs 0.39 simulated. Items: 0.05 simulated vs about 0.23 logged
  (the policy prefers PE heals).
- Calibration runs use an unbounded HP cap, so HP-share statuses (e.g. "hp to 3/4") now act on
  Aya's real max HP (`player_max_hp`). That had blown up two newly included boss battles.

Files: `pe-calibration-logged-serial-pe-items-2026-10-19`. Tests: `test_parasite_energy.py`.

## Ordinary enemies: early melee dodging, and the 0x0100 identity

**Melee dodging (player behaviour, confirmed by the user).** "I did a lot of dodges of melee
hits... in the beginning."
- Opt-in `player_evade_melee`: the share of melee strikes avoided by stepping back. It never
  applies while Aya is committed, and effects / projectiles are unaffected.
- Calibration flags: `--evade-melee` (all phases) and `--evade-melee-early` (Days 1–4 only).
- A global melee dodge doesn't fit: at 0.5, Day 2–4 drops to 1.15× but Disc2 drops to 0.75×.
- Days 1–4 only, at 0.6:

| Group | Damage, log → sim (ratio) |
|---|---|
| Day 2–4 ordinary | 29.4 → 31.4 (1.07) |
| Disc2 ordinary | 1.00 (unchanged) |
| All ordinary (143) | 0.93 (r 0.67) |
| Day 1 | 1.8× (8 battles, average 4 HP logged) |

- Files: `pe-calibration-logged-serial-pe-eme{04,06}-2026-10-19`.

**0x0100 (rooms 34 / 123).**
- Room 34 actor 4 and room 123 actors 2–4 write kind 1 and never write a rank. The template
  keeps 0, giving 0x0100 (`enemy_identity.rank_default_identities`, under the `MULTI_KIND`
  identity-fix opt-in).
- Their flows have no commands, effects or PM sends, so they are **silent parts**. The logged
  hits in those battles come from the other actors.

## Aya's side, completion pass (later on October 19)

Everything below is from the decomp and opt-in through `pe` / options, unless marked labelled.

| Mechanic | Source | Model |
|---|---|---|
| Preraise / Revive | `battle/encounter.c`: at death, Preraise (0x800) first, else a Revive item (0x12); `Battle_StepVictory` case 7: HP = maxHP/2, PE >>= 2; `Battle_ResetEnemyStats`: gauge 0, every ailment and buff cleared | `dead()` in source_combat. The 90-update enemy hold timer (`g_BattleEnemyHoldTimer`) is not modelled |
| Gene Heal | `Entity_UpdateTimers`: +1 HP per update; PE −= maxPE / (level × 30) (`fieldId04` = level, aya/stats.c); ends at PE ≤ 1 | `upkeep()`. Labelled: the draw-slot gate is taken as open every update (the log shows 1 HP per tick) |
| Energy Shot | `Battle_ResolveHit` (enemy_movement.c) with state 0x100000: base = stat1E/5 + gun power bonus; power = base × ⌊(7·level+120)/160⌋ × PE/maxPE + base; damage = power − full defense, at least 1; no hit quality, elements or status. phase.c spends all PE and the ammo | `energy_shot_damage`. **Live check 2026-10-19** (room 273, level 33, PE 1420/1420, 0x0125 defense 85): **572** logged, which is the formula exactly with base 219. My save-derived inputs give base 217 (566); the 2 points are the gun / offense stat of that save state, which aren't on disk. Alternatives are ruled out: defense split by RoF gives 634, a fractional level factor gives 607 |
| Armor auto-medicine (effect 0x4000) | `Entity_UpdateTimers`: below maxHP/5, uses Full Recover, then Medicine 4 → 1, repeating | From the battle bag |
| Armor auto-cure (0x8000) | `Entity_UpdateTimers`: Cure-P / C / D / M or Full Cure for each active ailment; Full Cure for flag 0x1000 | From the battle bag |
| Enemy buff clear (effects 2 / 9) | `Battle_ApplyEnemyAttack` | Also drops Gene Heal and Preraise |
| Counter rank | `Battle_RollEnemySpawn`: s8(Aya rank − enemy rank); Aya rank = level (`fieldId04` = level+1, low byte), enemy rank = identity low byte | Opt-in `identity_rank` (`--identity-rank` on `calibrate_logged` / `compare_rules`) |
| Confusion on Aya | `scene/player_movement.c`: controls rotated by 180° + k·90° and mirrored; no damage or targeting effect | Labelled: no melee dodge while confused |

Liberate's power formula is also in `Battle_ResolveHit` (state 0x80000):
(stat1E − 25 + level) × 6 × (1 + 0.1·(targets − 1)) / 7. It is the final-boss transformation, so
it's not simulated.

**Rule table (`rules.VALIDATION`) updated:**
- "ATB doesn't fill while acting" A → D (flag 0x100).
- "Counter rank difference" A → D.
- "Animation loops" R → D (weapon-bank frame counts, stepped by `source_battle.attack`).
- "Player repositioning" A → R (440 units/s live, with the movement formula cited).

The only Aya-side rows still marked L or A are behaviour: reaction time, melee dodge, cast policy,
when to walk.

**Final pass (Aya's side closed):**
- **Medic / Full Recover powers:** cure every ailment pair unless it reads immune, plus flag
  0x1000; Full Recover also heals to max. Scan has no combat effect: it's a cast with a pause
  only.
- **Cure items** (Battle_ApplyDamage 0x0D–0x11): an active ailment is cleared; with none, the
  one-use immunity is set. Full Cure clears all of them.
- **Steals** (opt-in `steals`, `--steals`), literal source:
  - Battle_ApplyEnemyAttack steals only when Aya's armor has effect bit 0x10, and then when
    rand()%100 ≥ 60.
  - Item: one random item from the battle bag.
  - Ammo: pool index `(count · RandomByte) >> 8` among the first `count` slots; amount =
    stock × RandomByte / 256 (Inv_RollRandomItemType).
  - The "only with the bit" reading is what the code says. Worth a live check if steals ever
    matter for balance.
- **`--logged-items`:** replays each battle's logged item use: medicine when low, cures while
  their ailment is active. Revive 0x12 is automatic at death.
- **The revive "hold timer"** (`g_BattleEnemyHoldTimer` / escape flag) is the battle-intro
  active-state flag, not an enemy pause. Revive simply restarts Aya's gauge at 0, which is
  modelled.
- **Liberate:** power formula documented above. It's the final-boss transformation only, so it
  is deliberately not simulated.

Final Aya-side calibration (`pe-calibration-logged-aya-final-2026-10-19`, every flag), damage taken:

| Group | Ratio (r) |
|---|---|
| Ordinary | **1.04 (0.75)** |
| Day 5 ordinary | 1.06 |
| Disc2 ordinary | 0.98 |
| Bosses | 0.64 (0.73) |
| Day 2–4 bosses | 1.20 (0.89) |
| Day 5 bosses | 0.94 |
| Disc2 bosses | 0.57 |

The Disc2 boss figure moves ±0.1 between runs: 11 battles × 4 fights, and the steal rolls shift
the random stream. The gap is the enemy-side items listed in `pe-calibration-casts-2026-10-19.md`
(out-of-reach turns, room 273), not Aya's side.

**Status of Aya's side: complete.** Every mechanic is cited to the decomp or measured live, except:
- Energy Shot, now checked against one live cast (structure confirmed; within 1% of the inputs on disk);
- the labelled player behaviour: reaction time, melee dodge, cast and item choices.

Calibration with all of this plus `--identity-rank` (`pe-calibration-logged-best-rank-2026-10-19`):

| Group | Ratio (r) |
|---|---|
| Ordinary | 1.04 (0.75) |
| Bosses | 0.73 (0.68) |
| Day 5 bosses | 0.94 |
| Disc2 bosses | 0.67 |

## Calibrated setup with the PE pause (current best)

`--serial --pe --evade-melee-early 0.6 --atb-guard --logged-charge`, reaction 30 paused, PE powers
pausing the enemies. File: `pe-calibration-logged-serial-pe-pause-2026-10-19`.

| Group | Battles | Damage, log → sim (ratio, r) |
|---|---:|---|
| All ordinary | 143 | 24.5 → 22.8 (0.93, 0.67) |
| Day 2–4 ordinary | 33 | 29.4 → 31.0 (1.05) |
| Day 5 ordinary | 10 | 89.0 → 57.4 (0.64) |
| Disc2 ordinary | 92 | 17.5 → 17.4 (1.00) |
| All bosses | 28 | 338.6 → 279.5 (0.83) |
| Day 5 bosses | 8 | 86.1 → 48.4 (0.56) |
| Disc2 bosses | 11 | 740.7 → 561.9 (0.76) |

The pause barely moves the ordinary figures (fewer than 1 cast per battle). Bosses drop about
5–10%, because hits that used to land during heals are gone. The Day 5 gap (ordinary and bosses)
is now the largest remaining error.

**Still unexplained:** 0x001E in rooms 217 / 226. The scripts set rank 29 (0x1D) and nothing in
the room scripts rewrites it.
