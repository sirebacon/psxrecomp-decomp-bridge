# Joint reconstruction and beam damage/status component — October 18, 2026

The user's hold on balance reruns remains active. This pass ran offline asset/math checks
and focused component tests only. No weapon-balance or encounter benchmarks were rerun,
and no game was launched, controlled, or scanned live. Historical balance outputs remain
unchanged. The new components are staged outside the existing full combat runner.

## Joint math is now source-derived and checked

`joint_reconstruction.py` ports the decompiled LIBGTE `RotMatrixYXZ` routine from
`src/main/psyq/libgte/fgo_02.c`. It uses the original packed4096-entry sine/cosine table,
signed16 angles, the retail low32 multiply/arithmetic-shift order, and signed16 stores.
It does not substitute floating-point rotations.

`rotation_oracle.py` independently executes only the original656-byte RotMatrixYXZ math
routine (0x80079754..0x800799E4) from the executable. It supports just the instruction
subset used there, restricts instruction fetch to that routine and data access to the
sine table plus angle/output buffers, and stops on unsupported access/instructions.
This is an isolated arithmetic oracle, not a game/emulator session.

One thousand deterministic signed-angle triples matched the original instruction result
exactly. Focused tests also cover axes, negative angles and additional independent random
triples. The output records executable, routine, source and component hashes.

The hierarchy port follows `Render_TransformVertices`: push/pop parent matrices,
source bone rotations, root XYZ translation, non-root part Z translation, Q12 matrix
column composition, IR saturation for rotation-column stores, and MAC translation.
It rejects unimplemented44-bit overflow rather than silently returning an invented pose.
Both additive and replacement per-bone rotation overrides are supported.

For an independent saved-state check, the existing Disc2 PST supplies the model, original
animation channels, world model matrix, rotation overrides and cached rendered matrices.
Rebuilding the previous rendered frame2 matches **all29 joint rotations and translations**,
with zero mismatches. The actor's next animation frame is3, consistent with render-before-
animation-advance order. No pose parameters were fitted to the saved joint matrices.

The47-part hospital boss model also reconstructs all168 extracted frames for modes8/9/10/11.
The validation artifact saves each frame's orb joint7 point and beam joint31 point, with
the source offsets applied, relative to an identity actor world matrix.

Some useful source-pose ranges (Y relative to actor origin):

| Animation mode | Orb launch joint/offset Y range |
|---|---:|
| 8 | -638 to -354 |
| 9 | -914 to -441 |
| 10 | -666 to -646 |
| 11 | -656 to -380 |

These are decoded poses, not a measured encounter trajectory. In mode9, frames0..4 give
Y=-441,-506,-592,-692,-800. Which cached pose the effect sees at launch still depends on
actor/effect/render pass ordering. A single arbitrary height320 or640 is not a validated
replacement for that scheduling. Actual actor world rotation, scale, source-copy modes
and joint overrides must be supplied when replaying the boss encounter.

## Beam geometry, delivery and status now compose

`beam_delivery.py` adds a staged component that connects supplied world-space beam targets
to contact latches, actor-ordered HP/barrier damage and incoming stiffness.

`BeamEmitter.update_effect` implements the extracted warmup and active window, strict
XZ contact against600+the supplied weapon-model cylinder radius, per-emitter interval,
held counter25/rearm and event-state transition. A contact schedules a pending owner hit;
it does not immediately subtract HP. The caller explicitly orders effect updates against
the separate battle delivery pass. Actual pool completion must call `finish_tasks`; fade
length alone does not silently finish a process.

The same-pass scan preserves separate owners and consumes the established
`drain_action_contacts` behavior. Per-owner power uses signed32 multiplication/shift then
u16 storage from shared scale *90. Record slot3 selects the second armor parameter.
The damage component applies defense scaling, the owner's critical chance/resistance,
charged guard, HP writes and the barrier-energy path. HP storage follows the source's
16-bit field; no new death/clamping policy is invented.

Incoming effect5 stiffness follows source ordering:

1. Already active lock returns without refreshing its timer or drawing a resistance roll.
2. Resistance armor gets its50% prevention roll before one-time immunity is consumed.
3. One-time stiffness immunity clears itself and prevents that application.
4. Otherwise Haste clears, stiffness becomes lock, and its timer becomes9000 status units.

Status ticking subtracts the supplied level-derived statusStep3C with u16 storage/signed
expiry semantics. Non-expired lock zeros motion; expiry restores the base action mode
when the actor is in lock mode17. Pauses freeze this component's status tick. Cures and
full frame ordering remain caller responsibilities.

The per-owner ordering matters even within one pass. With HP500, defense100, second armor
parameter10, Haste initially active, scale1.0 and noncritical rolls, three overlapping
beams deliver **74,60,60** damage: the first lock removes Haste before the later defense
calculations. HP ends306. Only the first application sets the9000-unit lock timer.
Removing Haste here increases the defense deduction, so later damage is lower.

The controlled geometry fixture places three beam targets at(1000,-2000) and Aya at
(1600,-2000), radius23. All three schedule contact on active update59, HP remains unchanged
until delivery, then the same ordered damage/status results occur. A separate boundary
fixture at640 units misses radius23 but hits radius63, confirming that weapon-model
collision size can affect beam contact under identical positions.

Other validated cases include PE-barrier energy loss without HP subtraction, stiffness
through the barrier, guard halving, armor-second selection, reaction-state changes without
rechecking the outer gate mid-pass, zero-HP-damage status application, immunity/resistance
ordering, and status expiry in supplied units. Relative-angle reaction animation and
Counter priority are surfaced as reaction requests/hooks rather than invented outcomes.

## Validation completed, reruns still held

- 1000 original-instruction rotation comparisons passed.
- All29 saved joint matrices matched exactly.
- 168 boss pose frames were reconstructed and recorded.
- 15 focused joint/beam integration tests and11 earlier geometry/delivery checks passed.
- No full test-suite count is claimed for this pass; no combat benchmark was run.

Files:

- `tools/pe_weapon_sim/joint_reconstruction.py`
- `tools/pe_weapon_sim/rotation_oracle.py`
- `tools/pe_weapon_sim/beam_delivery.py`
- `tools/pe_weapon_sim/validate_joint_reconstruction.py`
- `tools/pe_weapon_sim/tests/test_joint_beam_integration.py`
- `data/pe-joint-reconstruction-validation-2026-10-18.json`

Reproduce these offline validations only with bundled Python and PYTHONPATH=tools:

    python -m pe_weapon_sim.validate_joint_reconstruction
    python -m unittest discover -s tools/pe_weapon_sim/tests -p test_joint_beam_integration.py -v
    python -m unittest discover -s tools/pe_weapon_sim/tests -p test_projectile_geometry.py -v

## What remains before another balance run

The main joint math and isolated beam damage/status component now have meaningful checks.
The remaining work is joining them to the actual encounter timeline:

1. Resolve the cached render frame, actual actor world pose/heading and relevant render-copy
   modes when each orb/beam effect starts. The saved pose check validates reconstruction,
   not the hospital encounter's launch-frame choice.
2. Replay shared beam target strategies and trigger concurrency; order effect contacts,
   battle delivery and status ticking using the source scheduler. Do not map every target
   to Aya's current position or assign arbitrary chooser probabilities.
3. Replace the visual-drain surrogate with actual callback-pool lifecycle/stop ordering.
4. Wire reaction requests, stiffness action/AT behavior, inventory cures and barrier expiry
   into the full combat backend. Shared scaling, Aya defense/status stats and armor fields
   must come from the matching earned state rather than test defaults.
5. Run focused timeline and geometry controls. Judge readiness then; keep the user's hold
   on broad balance reruns until these joins are validated.
