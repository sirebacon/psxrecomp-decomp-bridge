# Reloads, special firing and weapon changes from source — 2026-10-18

This pass was entirely offline: source reads, simulation changes and deterministic runs.
No emulator connection, game input, save loading or new scans. Existing extracted asset
metadata is reused. The code is `tools/pe_weapon_sim/source_battle.py`, exposed through
`engine.source_sequence`. This is a new stateful player-action backend, separate from
the historical aggregate `engine.fight` and economy surrogate.

## Reload semantics

`parasite-eve-decomp/src/main/item/actions.c:814` (Inv_DrawSlotItemIcon) transfers
min(capacity-loaded, reserve) into the tracked gun, with capacity capped at999. Its pool
selection for kinds1..5 is pool0, kind6 pool1, kind7 pool2; clubs consume no rounds in
Battle_FinalizeAttackResult. This follows the C mapping, rather than assigning a fresh
reserve to each weapon. The simulation retains loaded ammo separately for each gun.

`battle/commands.c:388` synchronizes active action ammo, performs this transfer, then
rebuilds the action record. `battle/setup.c:242` calls that path before dispatch when
the gun is empty. No unconditional reload-animation delay is added at that point.

`battle/attack.c:209,240` calls it when ammo runs out during the queue. A positive
transfer enters actionMode12. `battle/player_turn.c:87` waits for animPrev==lastFrame
before restarting aim. The new backend advances the extracted35/40/45-frame reload
clip, then resumes the appropriate queue branch. Transfer0 does not invent rounds.
There is no automatic end-of-turn magazine refill. The old fixed0.8s reload estimate
is not used in this backend; historical aggregate fight behavior remains unchanged.

For example, a bank0 handgun with one loaded round, capacity2, reserve2 and RoF3 fires
three rounds total and finishes empty. It reloads once during the queue. The reload-start
to reload-ready interval is35 updates; the return-to-aim path adds its own animation time.

## Firing mode queues and hits

`battle/commands.c:459` maps effect6/7/8 to packed modes1/2/3. The queue builder in
`battle/turn.c:335` distinguishes:

- Ordinary/Burst: RoF individual selected-target slots per command.
- Random (0x40): floor(RoF*3/2) target draws per command, chosen during queue creation.
- Attack All (0xC0): one slot per eligible target per command, with RoF repetitions
  inside each slot's follow-through branch (`battle/attack.c:158,217`).

The new queue enforces the45-entry storage bound. Python RNG makes scenarios reproducible;
it is not a bit-exact replacement for the game's rand() generator/modulo distribution.

Burst (0x80) is not a random50% chance of hitting each other enemy. At hit time,
`battle/attack.c:375` applies signed16-bit angular bounds to every eligible target.
`burst_contains` implements that predicate directly. Callers must provide target angles;
there is no guessed cone occupancy or unconditional extra primary hit. Caller facing
must use the source coordinate convention, which is not assumed identical to the
target-vector angle. Distance/evasion/damage remain the responsibility of the hit resolver.

Each firearm fire event consumes one round; club attack events do not consume ammo.
Hit events occur at fireUpdate+hitTrigger-1 because the hit timer is incremented later
in the same Battle_Update call. `on_hit(event)` and `target_alive(id)` let a caller change
enemy health and skip dead queued targets. The model reproduces the source's double
queue-index advancement when the next ordinary target is already dead. No enemy attacks,
movement or status effects are invented by this backend.

One edge case is deliberately retained and flagged: after a reload in an Attack All
repetition, the ready branch reloads g_BattleRemainingActions from RoF. With short magazines,
this can extend repetitions beyond the original count until reserves run out. This is a
literal decompiled-path inference, not independently verified retail behavior and not a
balance recommendation. A bounded update guard catches nonterminating translations.

## Carried-state weapon changes

`battle/turn.c:416` copies the new action, sets up its rate and animations, sets mode13,
and consumes the remaining turn slots. `battle/commands.c:422` builds the action from
the newly equipped item's loaded ammo. Switching therefore changes the active rate and
loaded count without granting a free reload or resetting another gun's magazine.

The CURRENT cost comes from `parasite-eve-recomp/src/mods/pe_atb_items.c:306`: borrowed
allowed changes restore entryGauge-4500, full-bar allowed changes leave4500. The new
session implements enabled/allowed weapon switching and borrowed cancellation refunds.
Retail changes require9000 and leave0. It does not mix attacks into a switch turn.

`battle/setup.c:583` stages the equipment command and holds mode13. In
`battle/encounter.c:448`, the hold is released when g_DiscChangeFlags&1 clears; the previous
frame boundary completes the switch. The existing snapshot's mode13 clip has16frames,
so the normalized no-stall path uses17 battle calls including its initial call.

Menu duration and stream readiness are explicit caller inputs. Menu updates pause the
gauge; after commit the destination rate can refill it while stream readiness holds the
pose. The backend advances both waits and clip time alongside refill, rather than adding
them twice to the next attack. It does not predict disk latency or model alternate base
actor clips/costumes whose mode13 headers have not been extracted. CURRENT settings may
disable the half-bar feature; half_bar=False is an explicit scenario, not live detection.

## Validation and reproduction

`run_source_battle.py` generates192 attack cases (8 kinds x2 banks x4 modes x3 ammo setups)
and168 attack–switch–attack–switch–attack sequences (42 directed firearm pairs x2 costs
x2 stream waits). Every firearm attack case asserts conservation of initial loaded plus
reserve equals fired plus final loaded plus reserve. Raw event timelines and carried
state are in `data/pe-source-battle-2026-10-18.json`; the report is
`pe-source-battle-validation-2026-10-18.md`.

Fourteen new tests cover prior ordinary timing agreement, finite transfer, mid-queue clip
time, empty reserves, random queue construction, all-target repetitions, burst hit timing,
target-death callbacks, magazine/pool carry, destination refill, cancellation, melee ammo,
shared-reserve depletion and the sequence entry point. Full suite:90 passing tests.

With PYTHONPATH=tools and the bundled Python, run:

    python -m pe_weapon_sim.run_source_battle
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

Example API (gun definitions are copied, so callers retain their inputs):

    from pe_weapon_sim.engine import source_sequence
    from pe_weapon_sim.source_battle import Gun
    result = source_sequence(
        {'pistol': Gun(1, 10, 3), 'rifle': Gun(4, 10, 7)},
        {0: 40}, 'pistol',
        [{'op': 'attack', 'rof': 3},
         {'op': 'switch', 'destination': 'rifle', 'half_bar': True,
          'menu_updates': 6, 'stream_updates': 20},
         {'op': 'attack', 'rof': 3}], gauge=9000)

## Boundaries for future work

The new backend models player transitions, not a complete combat/economy replacement.
The old aggregate fight and surrogate still reject special modes under asset_queue, and
their old reload behavior is intentionally not relabeled as source-accurate. Use
engine.source_sequence/BattleSession for these new cases. Next connect its timed hit
callbacks to the existing damage/status formulas, enemy AI, movement and action effects;
then score acquired loadouts and switching policies against common encounters. No new
campaign ranking or assertion of secondary-weapon superiority is justified by this grid.
Cross-check unusual Attack All and switch entry/cleanup timing against retail code offline
before treating their exact counts as final. Seconds use nominal59.9/2 updates per second;
update counts and supplied waits remain the primary auditable units.
