# Boss beam choice and launch integration — October 18, 2026

This pass stayed entirely offline. No game/emulator, live scan, balance runner or encounter benchmark ran. The initialized boss chooser now connects source charge readiness, state gates, facing turns, region/layout selection and generated targets to the validated normal formation launch timing. It resolves one supported static-world decision; it is not a full repeating boss AI or a new weapon ranking.

## What the boss chooses

Actor3's actual attack-selection fragment begins at root+4752, after earlier state gates and facing setup. Distance comes from Entity_GetDistanceComponents (`script/actor_opcodes.c:108`): it adds the absolute fixed16 X, Y and Z differences. This is three-axis Manhattan distance, not Euclidean or XZ-only distance. Vertical differences can change both branch selection and target projection.

For an admitted decision:

| Distance in source units | Decision |
|---|---|
| Below1300 | Melee action0 |
| 1300 through1700 inclusive | Orb action4 |
| Above1700 through2000 inclusive | Draw Script_Random[0,3); result0 selects orb;1/2 can select beams |
| Above2000 | Beams can be selected without this action-choice RNG call |

Both beam-capable cases also require shared trigger cells18/19/20 all equal0 and Aya field21 unequal2. `Battle_GetContextField(21)` is `(stateFlags>>6)&3`; value2 means stiffness lock. A busy owner or stiffness-locked Aya redirects to orb. The action-choice RNG is still consumed in the middle interval even when these later eligibility tests will reject beams. Other stiffness pair values, including immunity3, do not trigger that lock exclusion.

This table applies only after the outer gate admits an attack decision. It is not an unconditional distance AI or a measured action frequency. RNG outcomes remain explicit inputs; no source branch counts are used as probabilities.

## The outer gate and persistent local state

The main loop at root+3388 yields one update, then checks these conditions in order at+3412:

1. If local22 bit0 is set, clear it. While local3==1, wait; otherwise go to decision setup. This can bypass the normal charge check.
2. If bit6 is set, wait at the main loop.
3. If bit2 is set and either distance<1200 or local1==0, go to decision setup.
4. If local44==1 (the completed-beam path), clear it. If bit2 is clear and local1==1, enter movement setup; otherwise enter decision setup.
5. If local35==0, wait.
6. Otherwise, distance>2000 with bit2 clear and local1==1 enters movement setup. Other cases enter decision setup.

The movement boundary is root+4248 and decision setup is+4472. The new code reports movement instead of inventing a travel duration. Local1 is the position-polygon child's result, not a generic distance band. The initialized script sets local32=1 and uses the four-vertex table at root+20488; the other encoded path selectors are retained as explicit inputs rather than assumed live routes.

Local35 is a sticky ready latch. Its child at+3156 checks field43>=9000 and sets local35=1; it does not clear it just because charge later decreases. The shared post-action path at+16348 resets charge and+16364 clears the latch. Using only current charge for every decision would lose source behavior. The caller must supply initialized script bits/latches; full startup/cutscene and previous action replay are not inferred.

## Node order and readiness latency

The original main node creates ordinary children at+1888,+1900,+1912,+1940,+1968,+1980. Script_SpawnChildNode inserts each after the same current node, producing this scan order after the root exits:

position/polygon child+2080 → movement child+17792 → main chooser+3388 → death-monitor child+20816 → region child+3252 → charge-poll child+3156.

This order is validated against freshly decoded room bytecode and the source insertion/interpreter semantics. Main runs before its charge poll. Battle_UpdateEnemy runs after actor scripts. Under the supported initialized, normal path, if charge first crosses9000 in battle update U, the poll latches ready in actor update U+1, and the normal charge-dependent main decision can occur in U+2. A ready latch already set or an earlier event/state gate can change that timing; do not apply the two-update latency as a universal delay.

The bounded charge replay uses EnemyClock's u16 charge rules and slow reduction. With charge0, step70 and the supplied main-loop start at1, a normal ready-based decision is reached at131; slow reduces the increment to42 and gives217. Poisoned/incapacitated/dead actor paths are rejected because they need movement/death/node-eligibility replay. These are source counter fixtures, not seconds measured from encounter entry.

## Joining choice to targets and launch timing

Decision setup clears motion, resets the relevant node/movement bookkeeping, sets animation step2.0 and turns toward Aya using local10=128. Despite its name, Render_CameraSnapToEntity changes the current actor's yaw and yields until aligned; it is not a separate camera delay. The new join reuses the validated retail atan/turn implementation for static boss/Aya inputs.

When beams are selected, root+5592 explicitly yields one update. The next resume sets step1.0 and faces Aya again at128; with the same stationary target this second turn is already aligned. The region child runs after the chooser, so it refreshes its sample before that next resume on the supported path. The actual four-vertex region at+3316 selects shared27=0 outside or2 inside. Mode1 still is not produced by this normal entry.

Mode0 computes the central1100-unit projection, waits for the turn at+10384, then forms its1200-unit lateral targets. Mode2 consumes its separate explicit layout RNG[0,3) and computes the three previously decoded target samples/offsets. Its layout RNG is distinct from the middle-range attack-choice RNG. The join then calls formation_launch at the common tail, including its final turn, polygon admission, fixed16-to-integer conversion, helper6/5/4 ordering, and exact conditional effect/delivery/cleanup schedule.

One fixture supplies initialized main resume1, charge8990, step70, ready latch0, static boss(0,-1873,-6000), Aya(3000,-1873,-6000), yaw0, no local event bits, and free/ready helpers. The position path result is0. It derives:

- main readiness/decision admission at3;
- facing complete and attack chosen at10;
- formation mode0 and trigger update11;
- earliest contact opportunity69 and earliest delivery70;
- normal long-effect release401.

The input does not supply a formation entry or trigger timestamp. The full-engine regression preserves those derived values and uses the same Aya position for choice and beam contact. Its stationary Aya remains outside the target circles, so it receives no beam damage; all three effects clean up and ammo imbalance remains0. This is intentionally not an assumption that every beam targets Aya's current location.

## Implementation and validation

New `boss_beam_choice.py` implements chooser_gate, choose_action, source_distance, first_choice_update, and boss_choice_to_launch. The source engine accepts opt-in `source_options.boss_beam_choice` as an alternative to beam_formation or linked_beams, and returns `_boss_beam_choice` plus `_beam_launch_timing` diagnostics. It does not automatically repeat the chooser. The same-boss generic enemy attack model must not also be counted as an independent replay of that boss; focused tests disable its generic charge.

Inputs include initialized main resume update, fixed16 XYZ positions, yaw, local script bits/local3/local44/local35, initial charge and source charge step, path selector, Aya flags, helper trigger cells/readiness, shared scale, PM capacity, boss core flags and actor flags. Explicit action/layout random outcomes are required only where the script consumes them. Unsupported movement ends the join with action=move. A beam decision checks that full-engine beam_player XZ and stiffness pair match the static chooser snapshot; inconsistent states are rejected. Boss slow is supported; poison/incapacity/dead or busy-helper execution needs fuller scheduler replay.

`script_decisions.probe` now supports source bit operations, explicit bounded RNG outcomes, cross-player field reads and known stopping boundaries. New tests compare360 attack-selection combinations at1300/1700/2000 boundaries and500 outer-gate snapshots against freshly decoded bytecode. They also check actual child spawn order, readiness delay, slow, sticky/event readiness, mode/layout RNG separation, movement boundary, stiffness/helper exclusions and consistent full-engine integration.

Latest focused validation: **114 tests pass**, including12 new chooser tests. No encounter benchmark or balance runner is included. Reproduce with PYTHONPATH=tools and bundled Python:

- `python -m pe_weapon_sim.extract_boss_beam_choice`
- `python -m pe_weapon_sim.validate_beam_combat`

Artifacts: `data/pe-boss-beam-choice-2026-10-18.json` contains raw selected commands, room/source hashes, path/region polygons, branch-boundary table and seven conditional fixtures. `data/pe-beam-combat-validation-2026-10-18.json` contains the focused test result and implementation/source hashes.

## Remaining hold and next work

Rerun readiness remains false. The admitted initialized chooser now determines one beam volley and its launch timing without a manually chosen entry timestamp. Remaining encounter work is replaying the movement/position-node path that establishes those inputs, updating world positions/Aya status during turns, replaying the parent post-action state and repeated choices, and integrating interrupts/death/busy helpers/PM exhaustion. Actual source-earned stats/shared scale and launch-pose trajectories still need a coherent encounter join. Orb cleanup, full reactions/Counter helper mapping, cures and encounter resets remain outstanding. Historical balance outputs have not been replaced.
