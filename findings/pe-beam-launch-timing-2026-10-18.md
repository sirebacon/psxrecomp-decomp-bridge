# Beam navigation, animation waits and launch timing — October 18, 2026

This pass stayed entirely offline. No game or emulator was launched, no live scan was performed, and no balance or encounter benchmark suite ran. A new opt-in formation timing path now produces beam launch schedules for the full combat simulation from source rules. It is exact for the explicitly supported uninterrupted formation path, with entry update, world inputs, helper readiness and PM capacity supplied. It is not a complete boss AI reconstruction.

## Navigation is an immediate polygon test

`src/main/script/system_opcodes.c:1593`, Entity_CallAction, calls Geo_PointInPoly and returns1. The argument9 is vertex count, and10372 is a halfword-relative polygon offset. It is not an action dispatch, pathfinding call or navigation wait. Earlier handoff entries describing an unresolved navigation wait are superseded by this result.

Fresh extraction verifies actor3 root208280 +20744 =229024 points to the same nine-vertex polygon later installed as the beam floor polygon. After the turn at root+14416 completes, the common path performs three polygon checks, accepted target conversions and trigger writes without yielding before the first animation wait. All accepted triggers are written in the same actor update. Failure skips that trigger; if none is active, parent animations10/11 are skipped.

There are two distinct geometry checks: navigation reads the fixed16 target with integer-floor extraction, while the helper receives target coordinates after signed integer division by65536 (truncation toward zero). A point at fixed16 (262078465,-298188799) passes the first check but becomes (3999,-4549), outside the helper's floor test. The model preserves this: no active contact window, effect release at T+54 rather than T+390. This boundary case is covered by both the schedule metadata and component execution.

## Helper creation and update order

Actor7's callback at root+5052,5092,5132 creates helpers4/5/6 through Script_DispatchScriptCmd2500, then+5172 creates boss3 through Script_SpawnEntityAt. Both call Scene_LoadMap with the current actor as insertion anchor. Scene_LoadMap inserts each new actor immediately after that same anchor, giving the list fragment7→3→6→5→4. Each helper starts without an attached parent. Startup/intro scripts must have completed before claiming helper readiness.

Entity_FrameUpdate traverses frame callbacks in linked-list order. Actor types3/4/5/6 all bind Entity_IntegratePositionConditional, which dispatches the actor's three script buckets in order. Script_RunQueue consumes a node's active counter before interpreting it; an active1 node runs that update and continues through handlers returning1 until a handler yields. Ordinary child nodes are inserted after the current node; children of flag1/2 nodes go to the actor's bucket2 head. Do not sort child scripts by numeric address or assume children always start the next update.

The boss therefore writes triggers before the ready helpers6/5/4 poll them. They allocate their beam effect processes in that same update. The helper actor scan order is also the order used for action-contact delivery, subject to normal source eligibility gates. This replaces an arbitrary owner4/5/6 ordering for the recovered room path; manually supplied linked_beams lists still retain their supplied order.

## Original process passes resolve effect timing

The original frame routine calls0x80069660 before actor rendering and Pm_RunPrimary0x80069594 after rendering. Isolated bounded instruction execution establishes that0x80069660 draws/executes secondary slots11..21; it does not execute command130. Command130 is allocated in primary slots0..10 and executes in the later pass. Primary slot draws precede primary execution.

Normal pass order is actor scripts → Battle_Update/delivery → secondary PM → movement/parent position → render/joint construction → primary PM draw/execute → animation advance. Thus newly allocated beam PMs begin on the same update as the helper's trigger handling, and a new effect contact cannot deliver in the earlier battle pass until the next eligible update. The beam controller's mode1 joint query uses matrices rebuilt in that update's render pass on this normal path. Earlier uncertainty about whether the beam mode1 query necessarily used the previous rendered frame is superseded; actual actor pose/heading/overrides still have to be supplied.

The PM instruction oracle also verifies pause gates: without scene flag0x80 neither pass runs; flag4 prevents execution; under flag0x100 primary execution admits only commands85..114, excluding beam130, while secondary execution stops. This does not imply all script nodes universally stop: Script_RunQueue separately honors its flag80 exceptions. The new schedule is defined in normal, unpaused active combat updates, not wall-clock frames or guaranteed seconds.

## Real waits and exact conditional timeline

Script_TurnTowardPointStep caches target coordinates and step, recomputes yaw from actor-to-target position, steps toward it and yields only while not aligned. Alignment on the last step continues the script in that same update. The model ports its wrap/half-turn branches and uses the retail atan table. The ratan2 port matched1005 cases against the original bounded372-byte routine. Stationary actor/target inputs are required for this schedule; a coincident target is rejected because the source's early return retains node flag20 and needs a fuller node-state replay.

Script_SetEntityActionAndWait first sets the animation, resets current/previous frames, clears animation hold flag0x100, and yields. Subsequent resumes check forward/reverse frame wrap. The source field named FieldActor.action at+0x0F is actually the last-frame byte in the BattleEntity view; zero means a one-frame clip, not action mode0. An isolated original opcode oracle checks54 combinations of clip lengths, step sign, frame relationship and initial node flag. This prevents a misleading field name from introducing an extra/missing wait.

For normal step1.0, parent mode10 has42 frames and mode11 has45. If the trigger is written at T, mode10 starts at T, wraps at the end of T+41, and the script sees completion at T+42 and starts mode11 immediately. It completes the second wait at T+87. These waits overlap the helper effect startup; they do not delay the beam process allocation.

For an accepted target that also passes the helper's integer-coordinate floor check:

| Event | Active combat update |
|---|---:|
| Boss writes accepted trigger(s); helpers6/5/4 observe them | T |
| Beam effect first executes | T |
| Beam controller spawns | T+46 |
| First possible geometry contact | T+58 |
| First possible battle delivery | T+59 |
| Parent finishes animations10 and11 | T+87 |
| Long beam effect releases action record/held bits | T+390 |
| Helpers4/5 finish command and clear trigger | T+391 |
| Helper6 clears trigger after its explicit additional yield | T+392 |

Contact/delivery times are opportunities, not guaranteed hits: player geometry and the battle reaction/action gate still apply. Long helper4 uses interval300; helpers5/6 use140. No short-beam frequency is invented. A separate actor/action/effect replay follows helper action3 through enter clip10, exit clip11, effect state2 and opcode0 release, confirming the command does not complete merely because clip11 wraps.

## Integration and reproduction

New `beam_launch_timing.py` supplies formation_launch, AnimationClock/AnimationWait, HelperActionClock and a focused helper replay. New bounded instruction checks are pm_pass_oracle.py, ratan_oracle.py and animation_wait_oracle.py. They only execute approved small math/runner/opcode instruction windows with explicit buffers and intercepted calls. They never run the game, renderer, audio or IO.

The full source engine accepts `source_options.beam_formation` as an alternative to linked_beams. Supply entry_update (first eligible actor update at the common turn opcode, starting at1), three targets_fixed XZ pairs, current_yaw, scale, helpers_idle=True and verified pm_free_slots. Supply boss_position to derive target yaw or an explicit retail target_yaw, but not both. Optional step and animation_step allow controlled fixtures; normal script values are128 and65536. Continue supplying beam_player with matching source stats. Unknown/busy helpers, missing PM capacity and coincident derived turns are rejected. This input represents one formation volley; it does not automatically repeat or run the outer chooser.

The generated schedules retain helper6/5/4 order and map a trigger at active update T to the adapter's start_update=T−1. `_beam_launch_timing` returns the conditional proof metadata. BeamCombat active updates exclude menu/stream pauses; event trace session update numbers additionally count those paused updates. Do not mix those two counters. Targets and initial pose remain explicit; legacy sampled range/movement is not a reconstructed moving world trajectory.

Reproduce from the bridge with bundled Python and PYTHONPATH=tools:

- `python -m pe_weapon_sim.extract_beam_launch_timing`
- `python -m pe_weapon_sim.validate_beam_combat`

Outputs: `data/pe-beam-launch-timing-2026-10-18.json` contains raw spawn commands, polygon equality, frame direct-call addresses, original instruction/table hashes, source hashes, a conditional fixture and three helper lifetime replays. `data/pe-beam-combat-validation-2026-10-18.json` reports **102 focused tests passing**, including16 launch-timing tests. No encounter benchmark test or balance runner is included.

A deliberately overlapping full-engine control with T=5 gives first deliveries at64 in helper6/5/4 order, damage74/60/60, all three cleanups at395 and zero ammo imbalance. Its coincident beam targets are a delivery-order fixture, not a recovered boss formation layout or a balance result.

## Remaining hold

Rerun readiness remains false. The normal formation-tail timing is now resolved conditionally. Remaining work is placing entry T from the outer chooser/charge/region/turn path, using source-earned player/scale inputs, reconstructing actual moving world pose and launch-joint trajectories, and handling interrupted/busy helper or PM-exhaustion paths. The sequential short-mode branch is not newly made reachable. Preserve the other holds on orb cleanup, complete reactions/Counter helper targeting, cures and encounter resets. No balance rankings have changed from this pass.
