# Enemy and boss effect ports from decompiled source — October 19, 2026 (Claude)

These ports turn "untimed" attacks (placeholder 10 / 10 timing) into source timelines. All are
from decompiled C: `room_lib/*.c`, `room_m256_museum/m256.c`, `m256_class.c`.

Shared conventions:
- Actor frame faces −Z; Aya stands at (0, 0, −distance); floor y = 0.
- Contacts need the owner's action bits at 0x01, and most rewrite them (one hit per action).
- Labelled simplifications: the floor polygon is not tested; `rand()` is Python's.

## Ports

| Identity (room) | Slot | Effect → controller | Source behaviour (summary) | Result |
|---|---|---|---|---|
| 0x0223 (256) | 3 | 132 → `RoomM256_TrailEmitter` / `TrailCallback` | two homing trail heads (index 0 and 2); speed 8–15, +6 per update to 50, moving speed²/16; turn weight rsin(turn) × turnScale; hits near the floor within 100 + radius, impact 180 + radius | turnScale 800–820 facing Aya (default 810); contact is sensitive (grazes); hits about update 72–78 when it connects |
| 0x0223 (256) | 4 | 131 → `RoomM256_ScatterDropEmitter`, swung by class 76 | drops every odd age < 110 from hand joint 4, aimed by the swing's bone-3 Y override (branches by facing: (−1100, 700) / (−1600, 50) / (1200, −450)); every other drop hazardous; 410 / 620 + radius | contact at update 53 (600 units) … 87 (2000) |
| 0x001A (263 / 265 / 333) | 1 | melee | per-species window: the species pick now also takes that actor's melee window | window-timed |
| 0x001A species 5 | 3 | 115 → `RoomEffect_OrbitFlareController` | three flares rise 52 frames from matrix 25, fly 55 per update at −256 / 0 / +256 + facing; hit within 57 + radius | contact at 56 / 65 / 76 for 700 / 1200 / 1800 units |
| 0x001A species 6 | 3 | 136 → `RoomEffect_LineBurstController` | glow at the target point after 12 updates, hits within 260 + radius for `duration` (300) | ported; the target point is script-computed (labelled: Aya's position); that species is rarely picked |
| 0x021A (188) | 3 | 124 → `RoomEffect_PhasedSparkController` | six sparks from hand joint 6, rise 16 frames, fall at Aya ± 600 (random); hit falling (110 + radius, near the floor) or landing (200 + radius) | about 3 / 4 runs hit, update 80–92 |
| 0x021A (188) | 4 | 125 → `RoomEffect_WaveSparkController` | particles only draw; no contact anywhere | **harmless** (the HandlerC lunge is slot ≥ 3, so no melee contact either) |
| 0x021B (269) | 4 | 137 → `RoomEffect_GroundSweepController` | ground ribbon from hand joint 4, 8 sweeps (12 out + 4 steering toward Aya), step 24–48 (`GrabSetSlot` 48); hit within 50 + radius | contact at 35–70 |
| 0x0220 (269) | 3 | 139 → `RoomEffect_RisingSprayController` | spark stream ages 16–60, facing ± spread/2 (1024) at 39–54 per update; hit within 100 + radius | contact at 21–52 by distance |
| 0x0220 (269) | 5 | 138 OrbitTrailBurst (visual) + class 77 Grab | grab only if Aya is within 256 of the hand (matrix 6) at animation frames 8–14 | misses at normal ranges; held repeat hits labelled as one |
| 0x0421 (245) | 3 | 140 / 141 → Seeking / ScatterTrail | trail from matrix 7 / 5 × (0, 0, −250), eases toward Aya by 1/8 with wander, speed 32 → 60 (speed²/16); any of the last 24 points within 104 / 100 + radius; stops at age 32 | contact at 47–67, sometimes misses at range |
| 0x000C (75 / 80 / 82) | 3 | 12 → MotionParticles module (eruption strip) | two 10-link floor strips from matrices 9 / 13, 300 per link, ±400 wide, links 2–5 turn toward Aya, one link lit per update (`FieldFx_UpdateStripCollision`); re-arm 30 | contact at 48 (600) … 57 (3200) |

## Plumbing

- `room_m256.py` and `room_lib_effects.py` register their controllers in `TASK_RUNNERS` /
  `SCENE_RUNNERS`.
- The motion-particle module is registered in `room_modules.MODULES` and gets all joints
  through `scene['joints']`.
- `task_actions`:
  - when the last loaded effect is a motion class (Handler C / D / E, PM < 85), it uses the
    latest task program loaded in the same block;
  - room 256 slot 4 looks behind the swing class.
- `task_plan(..., actor=)` and the species pick in `called_plans` take the picked actor's own
  task effect and melee window.
- Joint access no longer depends on joint 9 existing. Runners fall back to a labelled static
  pose when a clip is unresolved.

Tests: `test_room_m256.py`, `test_room_lib_effects.py`.

## Still untimed after this pass (inventory, all logged identities)

- **350 0x0225** (2 appearances): HandSweepTrap (quad trap from animation 11 frame 8; corner
  data in the overlay), Orb, AreaZone, Drop, RushFlare. All decompiled, not yet ported.
- **Decompiled room bosses:** 5 `RoomM005_Orbiter`, 23 `RoomM023_ScatterEmitter`,
  89 `RoomM089_SpiralTrail`, 123 `RoomM123_JointTriangleEmitter` / `PulseRing`, 273 (Liberty
  emitters), 348 DropField.
- **No symbols and no signature match** among 491 named functions: 428 / 429 / 432 (end-game
  bosses). They need disassembly.
- **Unresolved identities:**
  - 86 0x020D slots 0 / 1: no plan;
  - 0x0100 (34, 123) and 0x001E (217, 226): no called slots.

## Second pass

| Identity (room) | Slot | Source | Result |
|---|---|---|---|
| 0x0201 (5) | 3 | 117 table, controller 2 `RoomM005_JointBeacon`: beam from matrix 0x14 along the facing, +0x200 per update for 5, band 100, owner → 0x11 | contact 47 / 49 / 51 at 600 / 1500 / 2600 |
| 0x0204 (23) | 3 | 118, two `RoomM023_JointBeacon` (joints 8 / 0x10), +0x19A per update, band 0x50, 61 updates | contact 50 / 52; misses beyond reach (2050) |
| 0x020E (89) | 3 | 119, controller 2 `RoomM089_ModelPulse`: within 0xF0 of the anchor for ages < 0x28 (anchor from `RoomM089_SetAnchor`; labelled: Aya's position) | contact 30 |
| 0x0312 (123) | 3 | 128, controller 2 `RoomM123_JointBeacon`: fixed 0x7D0 beam from matrix 0x17, band 0x140 | contact 34 |
| 0x0312 (123) | 4 | 143 `RoomM123_PulseRing`: unconditional at age 32 (owner → 0x21), a room-wide flash | contact 48 |
| 0x020D (86) | 0 / 1 / 3 | four phase blocks of declarations: power N10 × 52–66 (slot 0) and 65–74 (slot 1); the timing is identical in every block | labelled phase pick (`enemy_choice.phase_powers`); the melee windows now accept repeated declarations whose timing agrees |

Room 350 (0x0225), investigated but not ported. The geometry depends on runtime configuration
the static image doesn't hold:

| Effect | Behaviour | Blocker |
|---|---|---|
| 155 HandSweepTrap | two traps at animation 11 frame 8 from hand matrices 11 / 15; a strip 256 wide from the beam's floor point (`g_RoomM350HandSweepTrapCorners`) | — |
| 156 Orb | spawns at animation 13 frame 15, homes with a weave, hit within 128, lives 48 | `g_RoomM350OrbSpawnPoint` is set at run time |
| 158 AreaZone | 256–320 × 4096 beam (`g_RoomM350AreaCorners`) turning toward Aya for about 90 updates | the yaw and tracking come from `RoomM350_AreaConfigure` at run time (0 in the image) |
| 159 Drop, 160 RushFlare | contact code found (`RoomM350_TestDropPlayerHit`, `m350_callbacks.c:666`) | not ported |

Still unresolved:
- **0x001E in rooms 217 / 226:** the scripts set rank 29 (0x1D) with no later change, but the
  log says 0x1E. A spawn-time adjustment outside these scripts, not proved.
- **0x0100 in rooms 34 / 123:** no script sets that kind and rank.
- **Room 348 DropField and room 273 Liberty:** decompiled, not yet ported.
- **428 / 429 / 432:** no symbols.
