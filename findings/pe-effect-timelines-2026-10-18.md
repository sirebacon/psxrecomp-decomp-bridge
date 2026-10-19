# Enemy effect attacks: source timelines replace the placeholder — October 18, 2026 (Claude)

Accuracy plan, step 2. Follows `pe-fallback-hit-audit-2026-10-18.md`. Offline, except one
read-only live read of the PM handler table.

## How effect ids resolve (source)

- `scene/room_load.c` reads room directory field 0x04 records:
  - slot 8–84 → `g_PmCmdHandlerTable[slot]`;
  - slot 85+ → `g_FieldFxTaskPrograms[slot − 85]`;
  - `u.handler` is an absolute address in the room overlay.
- The room blob *is* the overlay image: offset 0 = the overlay's vram base. This was verified
  on room 146: its command-40 class lists its RoomLib methods at base 0.
- `room_handlers.py` reads the records and names the functions from the splat symbol maps.
- Ids below 85 can therefore be room-module classes (seven methods: no-op, PlantScript,
  Spawn6, register, start, close, no-op), not only resident PM programs.
  - A read-only live read of the handler table in the Eve fight showed only 73/75 loaded, both
    pointing into the room overlay.

## Ported engines and controllers

| Code | Engine | Rooms / enemies | Timing source |
|---|---|---|---|
| `room_modules.ModuleObject` | FieldFx object script (`fieldfx/object_script.c`): commands, 0x40 slots, free/close rules | room modules | exact |
| falling sprite burst (`falling_sprite_burst.c`) | module | 0x13 in rooms 146/147/324/327 | exact; Aya stationary |
| three particles (`three_particles.c`) | module | 0x0B in rooms 65/85/87 | exact; field-D branch → uniform (labelled); debris direction (see limits) |
| timed spawn (`timed_spawn.c`) | task (`room_effects.TaskEffect`) | 0x15 rooms 152/153/154/332 | exact; unavoidable scene flash at update 55 |
| burst orb (`spark_attacks.c`, via Codex's `BurstOrb`) | task | 0x216 room 156, 0x217 room 380 | launch exact; completion = Codex bound |
| sound burst (`sound_burst.c`) | task | 0x20 rooms 205/231/234/243 | exact; steps from the script's `SetArgs3`; hand matrix 9 |
| spark ring + burst sparks (`spark_ring_burst.c`) | task | 0x1F in 10 rooms | exact; ring hits Aya's captured position (stationary Aya = hit) |
| homing projectile + ground eruption (`homing_projectile.c`, `ground_eruption.c`) | task + eruption | 0x14 rooms 146/153/154/328 | exact flight on open floor; Aya's lateral offset is a scenario |

Common rules ported:

- **Re-arm timers** (`room_rearm_timer.h`).
- **One hit per effect** where a controller rewrites the owner's 0x3F000000 bits after a hit
  (0x21 / 0x19).
- **Contact tests:** X/Z, `FieldFx_IsPlayerWithinRadius` (radius + Aya's cylinder radius).
- **Engine forward vector** `D_800C2258` = (0, 0, −16384) (retail EXE).

Each action plan now carries kind `module` / `task` / `homing`, with its own contacts and
release from the source timeline. `GatedEnemy` uses them for both distance-gated and
called-slot enemies.

## Effect (same audit cases, early bound, `called_slots`)

| | Before ports | After ports |
|---|---|---|
| Executed strikes on the untimed 10/10 placeholder | 8,556 of 12,427 (69%) | 1,372 of 6,720 (20%) |
| Landed hits | 10,058 | 6,410 |

Hits drop because effect actions really take 100–350 updates; the placeholder was 20.

The fallback-damage share rises to 17.5% because the denominator shrank. The absolute fallback
count is about the same (1,119), and nearly all of it is overlay-driven boss parts plus the 0x1A
variants. Data: `data/pe-fallback-hit-audit-effects-2026-10-18.json`, with per-strike
attribution under `strikes`.

## Remaining untimed (largest first)

- **Ordinary enemies:**
  - 429 0x26 slots 3/4/5: effect 147; room 429 has no overlay symbol map yet.
  - 350 0x225 slot 5: room 350 hand sparks; the room is decompiled, port pending.
  - 0x17 (rooms 163/186): flash sprite + handler D/E classes; module 11 is the twelve-effect
    class.
  - 0x0A slot 3: no effect, so its completion comes from another script node; unresolved.
- **Bosses:** 256 / 432 / 428 0x223 and 0x225; 269 0x220.

## Assumptions (all labelled; the comparison varies them)

- **Aya is stationary during an effect.** Dodging needs player movement, which isn't modelled
  yet. The spark ring always hits a stationary Aya.
- **Floor polygons are open:** no reflection or out-of-bounds cut-offs.
- **The homing throw passes 145 units to the side of the facing line.**
  - Default lateral offset 0: a miss.
  - Assumption set `geometry_upper`: Aya on the throw line, a hit.
- **Three-particle debris leaves behind the actor** under the source seed and engine forward
  vector, unless the view matrix carries an extra half turn. `geometry_upper` flips it.

## Tests

- `test_room_modules.py`: room data, the script engine, falling burst, all task runners.
- `test_homing_throw.py`.
- `test_called_slots.py`, updated.

Full suite: 308 passed.

## Reproduce

```
PYTHONPATH=tools python -m unittest discover -s tools/pe_weapon_sim/tests
PYTHONPATH=tools python -m pe_weapon_sim.audit_fallback_hits --bound early --extra "{\"called_slots\": {\"contact\": \"BOUND\"}}"
```
