# Effect-driven enemy actions (slot 3+) — October 18, 2026 (Claude)

Continues `pe-ordinary-enemy-coverage-2026-10-18.md`. Offline; no game access this pass. No
balance runs (hold respected).

## How slot 3+ actions work (source)

- `script/system_opcodes.c` Script_RunEntityCommand repeats each update until
  Entity_TriggerAnimEvent returns non-zero, i.e. until the action record's state is 4.
- `battle/context.c`: for slots 3+ neither the hit (state 3) nor the completion (state 4)
  comes from the animation.
- The script loads an effect (`Script_GetEntityEffect #id` → Scene_LoadRoomAssets) and sends its
  arguments (`Pm_ScriptSendCommand0` → the program's initializer, which returns the effect's
  argument block). `fieldfx/geometry.c` FieldFx_UpdateTasks releases the owner (action state
  4) at the task script's stop opcode once no controller is live. Hits are controller contacts
  (player flag 0x4000) delivered by the battle pass.

The effects the run's ordinary enemies use most are shared room-library code, already
decompiled, with identical task scripts in every room:

| Effect | Controller (src/overlays/room_lib) | Task script | Arguments (initializer) |
|---|---|---|---|
| 136 | RoomEffect_LineBurstController (line_burst.c) | held, var6=51, wait 29, spawn | RoomLib_SlotSet: duration, countdown; target X/Z (cells N25..N28) |
| 115 | RoomEffect_OrbitFlareController (orbit_flare.c) | held, var6=30, spawn ×3 (phase 0/1/2), wait 2 | RoomLib_SetArgs3: radius, angle, attached |
| 122 | RoomEffect_DroppedFlareEmitter (dropped_flare.c) | held, var6=37, wait 66, var0=1, spawn | RoomEffect_DroppedFlareSetArgs: speed, lift |

## Exact timelines (`room_effects.py`)

A port of FieldFx_UpdateTasks (script before callbacks; spawn counts immediately; return 1
frees the slot; return 2 frees it only when its particle list had no active entry that pass)
and of the three controllers, with retail rsin/rcos from the original executable. Geometry is
an explicit scenario: Aya stationary, X/Z contact (FieldFx_IsPlayerWithinRadius: model
cylinder radius + extra).

- **136 line burst:** 6 sweep + 6 ring updates, then a glow of `duration` updates that tags Aya
  within 260 + radius of the target point (re-armed every `countdown`), then a 32-update fade.
  With the scripts' 300/300: contact at effect update 42, release at 374 (the caster is busy
  ~12.5 s). Target outside the floor: released at 36, no contact.
- **115 orbit flare:** three controllers rise 52 updates, then travel `radius` units/update
  (straight, at −angle / 0 / +angle) until they touch Aya (57 + radius) or leave the walkable
  area, then 16 updates. Middle flare at 800 units: contact 74.
- **122 dropped flare:** the emitter (aimed at Aya, pitch 0x180) drops a flare at age 1 with the
  script's random speed 32-63; it hits within lift·50/4096 + radius while falling, else lands;
  scatter children (24 updates each) and a spark keep the effect alive until the list drains.
  At 500 units: hit ~77, release ~102; at 2500 it lands short (no hit).

Action mapping: windup = contact effect update (delivered next pass), total = release.

## Simulation (opt-in)

`effect_actions.py` catalogs 28 effect actions (11 × 115, 9 × 136, 8 × 122) with literal
arguments (122's speed range from its Script_Random); 22 identities with first-run cells.
`source_options['effect_actions'] = True` (or a scenario dict: height 480, floor_exit 3000,
target_offset 0 by default) gives such enemies an `EffectEnemy` when no animation-proven or
contact-bounded timing exists: at command start it takes the current distance, strikes on
contacts (geometric, no hit roll) and completes at release. Aya's radius follows her weapon
model (23-63). The effect's slot drives power resolution unless an explicit profile sets one.
Example: map 126 ID 0x12, slot-3 power 90, Aya defense 220 → 46 per hit at 500-1000 units,
no hits at 2500.

## Coverage of the 383 logged ordinary-enemy appearances (first-run cells)

| | Animation timing | + contact bounds | + effect actions |
|---|---:|---:|---:|
| timing resolved | 196 | 262 | 322 |
| stats + timing + power | 180 | 237 | 297 |

Bosses: timing 19 of 70.

## Limits

Stationary Aya and a fixed distance per action; 136's target offset is a scenario (cells
N25..N28 are written by another actor); 115's walkable area is a circle; 122's emitter height
is assumed; effect status (122 effect_type 1) is still counted as incoming_status_unmodeled;
Pm_ScriptStopCurrentEntity interruption paths and action choice between an enemy's melee and
effect actions are not modelled (effect actions are used only where nothing else resolved).

## Validation

`tests/test_room_effects.py` (10): retail trig, task semantics (same-pass spawn/stop, return-2
drain), each timeline incl. strict radius, floor cancel and re-arm, catalog, combat
integration. Full suite 247 passed; focused beam/combat checks pass.
