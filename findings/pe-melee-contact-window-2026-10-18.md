# Enemy melee: contact windows, not frame hits — October 18, 2026 (Claude)

Offline; no balance runs (hold respected). Follows `pe-enemy-choice-2026-10-18.md`.

## Correction

`decode_enemy_actions.timing` (and the `enemy_action_timing` option built on it) treats a
category 1 / 3 record's frame crossing as **the hit**. The source says otherwise:

- `field/actor_collision.c` Entity_CheckActionIdMatch is Aya's contact callback. It runs for
  each overlapping pair of hit spheres (`entity/allocation.c` Scene_UpdateEntityPositions;
  3D sphere test on animated part centres). It registers a hit only when:
  - the enemy's active record is in **state 1**, and
  - the touching enemy sphere's part id is one of the record's **contact ids**
    (Script_SetObjAnimEntry12 parameters 0–3; -1 ends the list).
- `battle/context.c` Entity_TriggerAnimEvent:
  - State 1 begins when the enter clip wraps into the exit clip.
  - For categories 1 / 3, the frame crossing sets **state 3, which closes the window**.
  - A frame at or past the clip's last frame never crosses (the decoder rejected these).
  - The exit clip's wrap completes the action.
- `entity/combat.c` Entity_ResolveDropTable, called from `menu/main_update.c` on a registered
  contact:
  - category 0 → state 4: the action ends on the hit;
  - categories 2 / 3 → state 3: one hit;
  - category 1 → state unchanged.

So a melee hit lands at the first sphere contact inside [open, close]. If the enemy's listed
parts never touch Aya in that window, it misses. The old frame-crossing time is exactly one
update after the window closes; that holds for every action where both exist (tested).
Historical results using `enemy_action_timing` are therefore a late bound + 1 and assume the
hit always lands. They are kept as they were for reproducibility.

## Code (opt-in)

- `melee_window.py`:
  - `window()` / `bounds()`: open = enter updates. Close = the frame crossing − 1 (categories
    1 / 3 with the frame inside the clip), otherwise completion − 1. Category 0 recovers one
    update after its hit.
  - `actions()` / `catalog(cells)` / `melee_rows(foe, cells)` cover every slot 0–2 record with
    a call: 198 actions (category 2: 96, category 3: 87 of which 24 never close by frame,
    category 0: 15; no category 1 in the game). Rows carry the contact ids.
- `source_options['melee_window'] = 'early' | 'late'` (fixed-slot path): uses the window for
  the foe's `source_action_slot`, or the shortest / longest action if none is set. It replaces
  `enemy_action_timing` / `contact_timing` / `effect_actions` for the foes it resolves.
  Counter: `melee_window_matches`.
- `enemy_choice.slot_plans` now uses the window first (kind `'window'`, bound = `contact`).
  The farming enemy's slot 0 is early 9 / 18 and late 21 / 6 (the decoder said 22 / 5).

## Coverage (ordinary appearances, first-run cells)

| Measure | Before | After |
|---|---|---|
| Timing of any kind | 322 / 383 | 348 / 383 |
| Stats, timing and power (all three) | 297 / 383 | 322 / 383 |
| Gated appearances with every slot timed | 0 / 83 | 22 / 83 |

- Bosses with any timing: 19 → 24 / 70.
- Slots still untimed among gated identities: 13 slot-3 actions using room effects that
  aren't ported yet.

## Validation

- `tests/test_melee_window.py` (8 tests):
  - window rules: frame close, frame past the clip, category 0, category 2 matching
    `contact_timing`;
  - every category covered;
  - decoder agreement (decoder hit = close + 1);
  - a previously untimed close attack;
  - the combat option.
- `test_enemy_choice` updated for the window plan.

Full suite 275 passed; `validate_beam_combat` passed.

## Next: reach (does the hit land?)

Whether contact happens needs the enemy's per-frame sphere centres: bone matrices from the
animation × per-bone bounds vertices (`render/object.c` Render_SetupBoneTransforms) and
sphere radii × move_speed / 4096. Two routes:

- offline: decode model headers and animation frames from the room data;
- live: a read-only probe of an enemy's `animation_entries` during its attacks. This needs the
  game in a room with that enemy; the current session is at the Eve fight.

Until then, `hit_probability` stays the stand-in for whether a melee attack connects.
