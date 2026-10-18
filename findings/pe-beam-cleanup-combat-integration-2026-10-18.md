# Linked beam cleanup and full combat integration — October 18, 2026

This pass stayed entirely outside the game. No balance suite was rerun and no historical balance output was replaced. The full source combat backend now accepts explicit linked beam schedules and delivers their damage/status during ordinary combat updates. This is an opt-in integration, not a completed boss AI model.

## Source timing and cleanup

`src/main/fieldfx/geometry.c:2174`, `FieldFx_UpdateTasks`, runs the task script before callbacks. Opcode 0 checks the live controller count; zero releases the owner, clears its held bits, and changes its action state to 4. A controller returning 1 loses its slot immediately, even if its visual callback pool remains active. Returning 2 instead asks for callback-list completion. Visual lifetime must not be added to the uninterrupted beam's damage-owner lifetime.

`src/overlays/room_lib/spark_attacks.c:662`, `RoomEffect_BeamSparkController`, supplies six approach updates, six expansion updates, duration active updates, and 32 fade updates. With the extracted script spawning at effect update 47, contacts first become possible at 59. A duration-60 controller returns 1 at 150 and the owner releases at 151; duration 300 gives 390/391. These counts assume uninterrupted execution and an in-floor target.

At the sixth approach callback the source checks the target against the floor polygon and returns 1 if outside. The adapter checks the extracted map-156 polygon. An outside target loses its controller at 52, cannot contact, and releases at the script's stop gate at 55. Owner deletion and external interruption remain separate unresolved paths.

## Full simulation wiring

Use `source_behavior_rules` and supply `source_options.linked_beams` plus `beam_player`. Each schedule explicitly supplies a unique owner, start_update (zero means begin with this encounter), target_x, target_z, duration, interval, and shared Q16 scale. Optional effect_chance defaults to the extracted 50; optional counter_target must be an explicit foe index. Owner list order is the supplied actor scan order. Schedules are encounter-local and are not carried into another encounter.

`beam_player` requires integer source max_hp, defense, armor_second, status_step, pe_gauge, x and z. Optional armor_first, critical_resist, effect_flags, flags, max_atk, barrier_energy, stiffness_timer, contact_timer, motion, mode and base_mode expose the component's remaining state. Barrier requires max_atk and barrier_energy. Finite integer starting HP below 32768 is required. The PE gauge is distinct from the weapon action gauge; filling the latter never grants PE damage reduction.

The battle pass gains action gauge, drains pending beam contacts, and decrements player status timers. The later effect pass checks geometry and latches contacts for the next battle pass. Menu/stream pauses freeze this adapter's active update clock. Simultaneous owners deliver sequentially, so the first stiffness hit removes Haste before the next damage calculation. New stiffness timers decrement on their delivery update. Stiffness changes subsequent gauge gain and prevents modeled approach movement; it does not globally disable shooting. Weapon changes select the currently equipped model's extracted cylinder radius.

Nonbarrier beam damage contributes to survival damage and HP; barrier damage reduces PE energy and still applies stiffness. Beam flags, barrier energy, stiffness/contact timers and mode are carried in `_source_state.beam_player`. Geometry contacts, deliveries and cleanups appear in the optional event trace, with summary counters and `_beam_state` diagnostics. There is no invented parent target for Counter: missing helper-to-foe mapping clears the pending counter and increments beam_counter_unresolved. Existing 21-update Counter reaction settling remains an approximation.

For mixed encounters, explicit enemy power attacks use the adapter's defensive stats and current PE/flag state. Active barrier routes their damage to energy. Fractional legacy incoming damage is rejected in beam encounters rather than silently truncating HP; provide integer source power profiles. Nonbeam enemy status and full reaction/animation processing are still the existing approximations, not a newly decoded implementation.

## Validation

Run `PYTHONPATH=tools python -m pe_weapon_sim.validate_beam_combat` from the bridge workspace. This intentionally excludes the encounter benchmark test and all balance runners. The latest run passed **67 focused tests**. The machine-readable artifact is `data/pe-beam-combat-validation-2026-10-18.json`, including source/implementation hashes and test counts.

Coverage includes controller return 1 versus 2, exact short/long release, outside-polygon cancellation, contact/delivery pass order, same-update timer decrement, status expiration, menu pause, weapon radius boundary, separate PE guard and barrier paths, simultaneous-owner Haste removal, original-instruction joint rotation checks, and existing combat/ammo/switch regressions. A deterministic full-engine encounter gives contacts at update 59, deliveries at 60, damage 74/60/60, HP 500→306, three cleanups at 151, and zero ammo imbalance. These are fixtures, not balance findings.

## Remaining hold and next steps

Rerun readiness remains false. Resolve actual beam owner scheduling, target-cell selection, shared scale changes and actor ordering from enemy scripts. The current geometry uses explicitly fixed player/target XZ coordinates; legacy sampled enemy distance and approach movement do not reconstruct a moving world-space trajectory. Do not use this adapter to claim measured moving-player contact rates. Actual launch pose/heading, orb lifetime/cleanup, owner interruption/deletion, reaction gates and angles, Counter helper mapping, cures and encounter reset policy still need work. The earlier joint reconstruction validation remains valid but does not establish all launch poses.

Next: trace owner trigger/target/scale writes, then effect interruption and orb callback cleanup. Add focused fixtures for those before any weapon ranking or balance rerun. Keep legacy outputs labeled as historical and the new beam mode explicitly opt-in.
