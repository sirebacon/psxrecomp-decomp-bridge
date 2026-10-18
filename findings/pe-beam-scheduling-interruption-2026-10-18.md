# Beam scheduling, targets and interruption — October 18, 2026

This continuation stayed offline. No game was launched and no balance rerun occurred. The new components resolve bounded source decisions and lifecycle rules; they do not replace the full combat adapter's explicit launch schedule with autonomous boss AI.

## Reproducible evidence

`python -m pe_weapon_sim.extract_beam_scheduling` freshly decodes map156 from Disc1, verifies its room hash against the inventory, and saves `data/pe-beam-scheduling-extract-2026-10-18.json`. Actor3 has1099 reachable decoded nodes, actor4/5 have79 each, actor6 has88, with zero decoder boundary errors. Each node retains absolute and actor-relative offsets. This is control-flow reachability, not proof of live branch frequencies.

The extractor also reads the existing saved RAM file, without launching it, to resolve PM handler85: execute=FieldFx_UpdateTasks (0x800D413C), stop=FieldFx_CloseTaskOwner (0x800D4850), through handler table0x80094188 and record0x800E13D4. Snapshot and source hashes are retained. Math_IntSqrt is lifted from the original executable's isolated60-byte routine0x8005186C..0x800518A8; its code hash is saved. It uses signed comparisons, gives floor sqrt on nonnegative inputs, and returns0 for negative signed inputs.

## Scheduling and owner handshake

Actors4/5/6 independently poll shared trigger cells18/19/20 for exactly1. They copy the actor of type3/sub31's position, configure effect130 parameter slots0/1/2, sample target cells21/22,23/24,25/26, and request action record3. Source `Script_RunEntityCommand` yields and retries until `Entity_TriggerAnimEvent` returns nonzero; its call is not a fire-and-forget launch.

Actors4/5 then wait for field82==0 before clearing their trigger. Actor6 first waits until field48 is0 or4, explicitly yields one update, then waits for field82==0. `Battle_GetEnemyContextField` proves field48 is the selected record's state and field82 is `(coreFlags>>24)&63`, the held counter. This handshake prevents automatic retrigger while an owner is busy. `BeamOwnerPoll` models resume boundaries with caller-supplied completion/state/held inputs; no actor ordering or animation duration is invented.

At actor3 root+5940, local cell46 selects shared cell27=0 when zero and2 otherwise. The following mode1 comparison cannot be true on that uninterrupted entry path. The short-duration branch remains encoded in each helper, but this entry does not produce it. Do not assign short-beam probability or claim global unreachability without auditing other entry paths/interleavings.

The sequential mode1 branch samples Aya separately for each target, projects200 units toward the boss when distance>=200, validates the navigation call, converts accepted fixed16 target cells to integer using truncation toward zero, and writes the matching trigger. It waits for animations10 and11 after accepted launches and explicitly waits30 updates before later player samples. Do not trigger all three simultaneously by default.

The common formation path instead validates and triggers the three targets in sequence, then waits for animations10 and11 if any trigger is set. Success/failure of the navigation calls controls which trigger writes execute. Trigger writes at root+14700/14980/15260 are ordered bytecode operations, not established absolute launch timestamps or established helper scan order.

## Target geometry and retail quirks

`projected_target` preserves every signed32 subtract, divide, multiply and truncation step. The source divides axis deltas and distance to integer units before calculating offsets; floating-point normalized vectors differ, especially for negative/fractional coordinates.

Mode0 uses a single Aya sample and a center up to1100 units toward the boss. After the turn wait at+10384, two lateral offsets of1200 are computed using the resulting heading. Mode2 draws an explicit outcome in[0,3): its first target moves away from the boss by1100 for outcome0 or900 for outcomes1/2, with an additional lateral500 offset for outcomes1/2. Later targets each resample Aya, project1100 toward the boss when sufficiently far, and use lateral750 offsets. `formation_targets` accepts the sample positions/distances, choice and relevant heading explicitly; those inputs are not synthesized by the combat backend.

The sequential second-target gate at+7752 checks whether the first owner is active, then tests sqrt(dx²+0)>1000. The Z term is literally cell24-cell24 at+7864, followed by multiplication by cell24-cell22. It must not be repaired into Euclidean spacing. The third-target gate at+8964, when either previous trigger is1, checks distance to both previous targets, even if just one owner is active. Both comparisons are strict `>1000`. Signed32 overflow and the retail sqrt's negative-input behavior are preserved.

## Interruption behavior

`EffectProcess` follows `Pm_Exec`, `Pm_Stop`, and `FieldFx_UpdateTasks` as a separately tested lifecycle component. A live process can be marked state4 by the actor gate when the action state is0 and either (held>0 and command_value<=0) or coreFlags&0x180E. Held is the value after that update's counter decay. With action state0 and actor_mode<2, the callback pass is skipped. A nonzero action state bypasses these actor-specific interruption gates.

Marking state4 does not itself return early when actor_mode>=2: the same update can still invoke the beam callback and latch a contact. On later PM executions state4→5→0 without further effect callbacks. An explicit Pm_Stop requires a matching owner unless forced; handler85's stop callback writes PM state4, then Pm_Stop immediately clears the PM slot. Crucially, that stop callback does not clear the actor's held counter, selected action record, or pending hit. Do not reuse normal opcode0 cleanup (which clears held bits and writes action state4) for these interruptions.

These lifecycle predicates are not automatically applied to the full combat adapter: it does not yet supply the actual helper actor states/HP/flags and PM/actor scheduling. Automatically clearing pending contacts or releasing triggers on every process stop would assert behavior absent from the stop callback. Connecting them requires source-backed owner state trajectories and caller ordering.

## Validation and remaining hold

`PYTHONPATH=tools python -m pe_weapon_sim.validate_beam_combat` passed86 focused tests. This includes11 scheduling tests, existing action-decision checks, beam/full-combat integration, geometry/joints, ammo and switching regressions. No encounter benchmark or balance runner was executed. The artifact `data/pe-beam-combat-validation-2026-10-18.json` includes counts and implementation/source hashes.

The new checks compare100 projection cases against freshly decoded raw arithmetic; test30 formation combinations across modes/choices/headings (mode0 explicitly splits at its turn wait); preserve the X-only second-target bug and the third gate's inactive-owner comparison; exercise owner handshake/yield and process interruption/ownership rules; and check sqrt positive/negative/boundary behavior. Polar operations use the original sine table with the decoded source formula, not a separate instruction-level polar oracle.

Rerun readiness remains false. Next resolve navigation action9 at root+10372*2, animation10/11 waits in the parent, helper creation/update order, and parent/helper state changes during damage/death. Then replay owner events into the full backend with validated timestamps. Also retain the earlier holds on moving world geometry, launch pose/heading, orb cleanup, cures and full reaction/Counter targeting. Existing full combat mode remains opt-in with explicit schedules; these new bounded decisions are available for that next integration without guessing schedules.
