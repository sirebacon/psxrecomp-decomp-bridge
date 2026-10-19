# Enemy melee reach from hit-sphere geometry — October 18, 2026 (Claude)

Follows `pe-melee-contact-window-2026-10-18.md`. That pass established that a slot 0–2 hit
needs 3D sphere contact between a listed enemy part and Aya. This pass computes whether
contact can happen, and from how far.

## Source rules ported (`enemy_reach.py`)

- **Model layout** (`render/object.c` Render_SetupEntityPrims), in order: a 0x1C header,
  parts (12 bytes each), vertices, colours, primitive descriptors, two section vectors, part
  bounds pairs, the projection origin, then the matrix commands.
  - A part with `visible == 1` and `bounds[2i+1].pad >= 0` owns a hit sphere: centre
    `bounds[2i].xyz`, radius `bounds[2i].pad`, part id `i`.
- **Model and animation location**: models are room directory field 0x0C records
  (slot = actor type, `entity/frame_update.c`). Animations are field 0x10 (group = actor
  type, slot = mode).
- **Animation decode** (`anim/bone_rotations.c`): three root translation channels, then per
  bone three YXZ angles. Angles are byte samples × 16 or u16 values; each channel is either
  constant or per-frame.
- **Bone hierarchy** (Render_TransformVertices): matrix command −1 pushes, −2 pops.
  - Bone matrix = parent × the bone's own rotation.
  - The root takes the animation translation; every other bone takes (0, 0, its part
    `translation_z`).
  - Sphere centre = bone matrix × bounds vertex.
- **Scale**: `move_speed` = the Script_SetEntityMoveSpeed literal >> 4 (default 4096). It
  scales positions (model matrix) and radii (the sphere test in `entity/allocation.c`).

## Validation (read-only, live game)

These were read from the running Eve fight (port 4378) with one atomic read per sample, with
no writes or input. Eve's model and animation were decoded straight from RAM with this port:

- Over 12 samples, every one fits best with YXZ order and standard signs.
- In 11 of 12, all 9 sphere centres land within 7 units of the game's values.
- The remaining sample was taken at an animation switch.
- The game's sphere entries lag its frame counter by 1–2 frames.
- Summary: `data/pe-hit-sphere-validation-2026-10-18.json`.

Structural checks:

- The farming enemy's model has exactly four spheres, on parts 3, 10, 11 and 12, which are
  its bite's contact ids.
- 151 of 198 attacks list only parts that exist on the model. The other 47 share a script
  with a different species' model; each still keeps at least one real contact part.

## Reach

Scenario: both on the same floor, facing each other along local −Z (confirmed live for Eve
and Aya). Aya stands in her captured idle pose (`data/pe-aya-hit-spheres-2026-10-18.json`:
15 spheres, about 470 units tall). Reach is the largest origin distance at which any
contact-part sphere overlaps any Aya sphere on some exit-clip frame inside the window.

- 187 of 198 melee actions have a reach. 7 have a non-literal move speed; 4 never overlap
  Aya's idle pose.
- Deciles run from 201 to 1150. The longest are large sweeping limbs or tails, e.g. map 243's
  whip at 1569 and map 34's tail at 1897.
- Independent check against the scripts' attack-decision distances (Manhattan guards):

| Enemy (ID) | Decides to attack at | Reach |
|---|---|---|
| 0x0F | d < 330 | 407 |
| 0x11 | d < 350 | 373 / 422 |
| 0x10 | d < 700 | 714 |
| 0x14 | d < 300 | 402 |
| Farming enemy, 0x0A (45 logged appearances) | d < 630 | 576 (miss band 576–630) |
| Maps 162/163, 0x17 slot 1 | d < 1000 | 633 |

  For the 0x0F, 0x11, 0x10 and 0x14 enemies the guard sits just inside the reach, so the
  designers tuned attack distance to reach. Two exceptions:
  - The farming enemy has a small miss band, from 576 to 630.
  - Maps 162/163 ID 0x17 decides at up to 1000 but reaches only 633. Possibly forward motion
    during the attack that isn't in the animation; open.
- Data: `data/pe-enemy-reach-2026-10-18.json` (`python -m pe_weapon_sim.enemy_reach`).

## Code (opt-in)

- `source_options['melee_reach'] = True`, together with `enemy_choice` and/or `melee_window`.
- A melee strike with a reach lands if the distance at the strike is within the reach,
  otherwise it misses (the window closes with no contact). This replaces `hit_probability`
  for those strikes.
- Counters: `melee_reach_strikes`, `melee_reach_misses`.
- `reach_rows(foe, cells)` returns the reach per slot for an identity whose actors agree
  (within 1 unit).

## Tests

`tests/test_enemy_reach.py` (9 tests):

- the model's spheres equal the contact parts;
- frame decode and hierarchy, and that the rotation order matters;
- the live validation record;
- the pair-reach math;
- move-speed literals;
- the catalog and the designer guards;
- in combat: hits in reach, misses past it on both paths, and the option requirement.

Full suite: 284 passed.

## Limits

- Aya is held in one pose and facing is exact (no lateral offset).
- No vertical offset between the floors the two stand on, so flying enemies are approximate.
- Motion during the attack driven by script movement rather than the animation isn't
  included.
- The guard's Manhattan distance is compared with Euclidean reach.
- The 4 actions that never overlap Aya's idle pose may need other Aya poses (crouch, dodge).
