# Enemy decisions: distance-gated attack choice — October 18, 2026 (Claude)

Offline; no balance runs (hold respected). Follows `pe-player-status-2026-10-18.md`.

## Why

Until now every source-modelled enemy used one fixed attack slot (`source_action_slot`) or a
fast/slow timing policy. In the room scripts, many enemies pick the attack from Aya's distance:
the farming-room enemy (map 358 ID 0x0A, 31 of the logged ordinary appearances) bites at close
range and uses a slot-3 move at long range, and doesn't attack at all in between.

## Source rules

- Distance: `Entity_GetDistanceComponents #0 #0` writes the Manhattan distance (16.16) to a
  local; a `Script_CondBranch` on that local (literal threshold) guards the code below it. The
  getter must be the last writer of the local within 200 instructions.
- `_walk` follows the graph from the script root to each `Script_RunEntityCommand` attack call
  and collects the guards on the way:
  - through child entries, to their single spawn site;
  - through local diamonds (both arms rejoin);
  - through state dispatch: `CondBranch equal` on a state local, mapped back to the
    "assign k, then overwrite if distance …" idiom. For example, map 333 actor 5 sets L18 = 4
    (slot 1) when d ≤ 800 and 5 (slot 3) when d > 800.
- Map 358 actor 4 (root+0x21ac): slot 0 when d < 630; slot 3 when d > 1000. From 630 to 1500
  the enemy approaches, then waits Random 30..59 and decides again.
- An identity counts as gated only when every attack call of every actor resolving to it has a
  guard, and those guards agree.

## Code (opt-in)

- `enemy_choice.py`:
  - `catalog(cells)` / `choice_profile(foe, cells)` give the slot intervals per identity.
  - `slot_plans(foe, cells, contact)` gives each slot its timing: `anim` (decoded action
    timing), `contact` (category-2 bound), `effect` (room-library effect), or `untimed`
    (a labelled 10/10 fallback). Each slot also gets its source power.
  - `GatedEnemy`: at full charge it picks the slot whose guard holds the current distance.
    Overlapping guards: `ambiguous='first'` (lowest slot) or `'uniform'`. If no guard holds,
    it keeps the charge and waits 30–59 updates.
- `source_options['enemy_choice'] = True` or `dict(contact='early'|'late',
  ambiguous='first'|'uniform', scenario=...)`. While on, it replaces the single-slot timing,
  contact and effect assignment for gated foes; non-gated foes keep the old path.
  - At each strike the chosen slot's power is merged in; explicit `enemy_profiles` still win.
  - Counters: `choice_matches`, `choice_strikes_slot<N>`, `choice_waits`.
  - Approximation: the enemy's approach movement isn't modelled. While it waits, the
    distance is resampled from the encounter profile.
- `audit_enemy_coverage.py` adds `choice_gated`, `choice_multislot`,
  `choice_all_slots_timed` and `choice_all_slots_powered`.

Example: farming-room enemy against a level-33 Aya over 30 s:

| Distance | Slot used | Damage taken |
|---|---|---|
| 400 | slot 0 | 243 |
| 800 | none (16 waits) | 0 |
| 1400 | slot 3 | 192 |
| 400, fixed slot 0 (old path) | slot 0 | 216 |

## Coverage (first-run cells)

- Attack calls: 93 of 412 are guarded (25 of them through state dispatch).
- 23 identities are fully gated.
- Ordinary appearances: 83 of 383 are gated, and all 83 have power for every slot.
  - 65 have more than one slot.
  - 65 have a dead band, a distance range where no slot is allowed.
  - 60 have at least one slot with source timing; none have timing for every slot.
- Bosses: 4 of 70 are gated.
- Slot timing across the gated identities:

  | Slot | anim | contact | effect | untimed |
  |---|---|---|---|---|
  | 0 | 6 | – | – | 15 |
  | 1 | 3 | 2 | – | 1 |
  | 3 | – | – | 4 | 13 |

  The 15 untimed slot-0 identities (maps 100–159 and 328, e.g. 115/113/120 ID 0x0F, d < 330)
  have the attack call decoded but no action record in `pe-enemy-actions`. That gap belongs to
  the decoder's timing capture, not to the choice logic.

## Validation

`tests/test_enemy_choice.py` (10 tests):

- the farming enemy's guard boundaries and slot plans;
- an unresolved identity gives no plans;
- GatedEnemy picks the slot by distance, strikes at the windup, holds in the dead band and
  keeps its charge, and follows the ambiguity rule;
- in combat: close range uses slot 0, far range uses slot 3, the dead band takes no damage,
  and the feature is opt-in.

Full suite: 267 passed. `validate_beam_combat` passed.

## Limits / next

- Not modelled: movement (approach and retreat), non-distance gates (HP, state timers,
  Random), or identities whose actors disagree, such as map 333 ID 0x1A actors 4/5/6.
- Next: timing for the untimed gated slots: slot 0 in the decoder, and slot 3 for the
  room-library effects not yet ported (10, 11, 40, 75 …).
