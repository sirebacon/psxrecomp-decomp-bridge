# Broad combat priorities: attack power and shared damage — October 18, 2026

The user asked for the highest payoff areas. This pass prioritized mechanics and data reusable across ordinary enemies and bosses, rather than extending the hospital boss's choreography. Everything stayed offline. No game/emulator/live scan, encounter benchmark, balance sweep or campaign optimization ran. The balance-rerun hold remains active.

## Why these areas came first

The existing source combat backend could use exact weapon events and common enemy charge, but most incoming attacks still used an explicit level-based damage fallback unless an enemy profile supplied power. Inspection showed that most decoded attack declarations compute power through the same adjacent multiply/shift pair. Resolving those operands has wider coverage than another boss-only script branch. The other immediate priority was a real barrier integration bug in source_combat, found during the shared-damage audit.

The next priorities after this pass should remain ordinary-enemy action choice/delivery timing and source-earned player defense/armor/status inputs, followed by generic incoming status/reaction behavior. Further hospital-specific movement choreography stays deferred unless it exposes another reusable primitive.

## Conservative attack-power extraction

New `enemy_power.py` accepts either a literal power or an exact adjacent expression chain:

`u16(s32(shared_cell * multiplier) >> 16)`

It verifies that the multiply, shift and declaration are contiguous, that operand destinations match, and that each consumer has a unique CFG predecessor. It rejects ambiguous merges, unsupported producer patterns and alternate declarations for the same actor/slot when constructing the usable catalog. It preserves signed32 wrap before shifting and u16 storage afterward. An indirect operand index is never substituted for the computed value.

The extractor resolves **381 of393 declarations (96.9%)** in the existing191 decoded action-bearing scripts:365 shared-scale expressions and16 literals;12 remain unresolved. This is not a claim that every game script or runtime action is decoded.

Joining with conservative map + rank/kind identities, unique slot declarations, compatible effect types and a consistent literal critical chance yields **284 map/enemy/action-slot keys across141 enemy identities**. The catalog preserves original declaration/proof offsets and does not select actions or infer their runtime probabilities. Shared scales are required inputs for computed power; no universal scale1.0 is silently assumed.

Coverage against the existing saved campaign log, without replaying fights:

| Logged appearances | Any supported action record | Supported slot0 |
|---|---:|---:|
| Ordinary enemies:387 |275 (71.1%) |147 |
| Boss enemies:70 |44 |21 |
| All enemies:457 |319 (69.8%) |168 |

These denominators describe the saved log, not all possible encounters. Having a supported record does not mean the AI selects that record, nor that its current scale or animation timing is known. In particular, do not treat the any-slot figure as complete combat coverage or automatically force slot0.

## Opt-in full-combat use

An explicit enemy profile can now provide `source_action_slot` and `source_shared_cells` (for example cell10's actual Q16 scale). The engine resolves power, selected slot, effect type and source critical chance through the catalog. Missing identity/slot matches retain the earlier fallback and expose power_catalog_matches/power_catalog_foes; a known computed expression with a missing scale raises rather than guessing. Existing explicit profile overrides retain precedence.

When enemy_action_timing is also enabled, a conflicting selected timing slot is rejected. This prevents applying power from one source action to the timing of another. The change does not infer a new chooser or silently broaden the timing catalog. Profiles must still supply or validate the action policy, hit geometry and remaining player/armor inputs.

A controlled ordinary-enemy regression for map5 / identity0x0201 / slot0 / scale1.0 extracts power15, effect0 and critical chance10. With explicit no-critical defense inputs it delivers15 in the full engine; the old level5 fallback would have used8. This illustrates replacement of an assumption, not a balance finding.

New hit counters `explicit_power_hits` and `legacy_damage_hits` expose which damage route actually ran. `incoming_status_unmodeled` records nonzero source effects that the adapter does not fully apply, rather than letting the presence of an effect type imply completed status integration.

## Shared HP/barrier reducer and bug fix

New `incoming_damage.resolve_incoming` follows the common branch of `entity/combat.c:Entity_ResolveDropTable`: defense and selected armor parameter, one crit roll, PE-gauge guard only in the HP branch, integer effect10 reduction, u16 HP storage, signed-HP reaction eligibility and signed32 barrier energy. Status application stays with the caller; this helper does not invent cures, item stealing or reaction animations.

Beam delivery and explicitly powered ordinary incoming attacks in beam encounters now use the same reducer. This prevents drifting copies of barrier math. The generic nonbeam damage component continues using the same underlying source integer damage helper; it does not silently acquire a new player-status state model.

The audit found that the beam event loop contained a duplicated generic barrier branch. With a live barrier it attempted to use the enemy-loop variable before that loop had assigned it, causing a crash; it also bypassed the correct beam event accounting. That duplicated branch is removed. A full-engine barrier-beam regression now shows one beam hit, zero HP loss, correct single energy deduction100000→99520, preserved stiffness behavior, and no generic enemy_barrier_hit event. A separate mixed ordinary-attack case verifies that normal hits route to barrier energy without HP loss or duplicated subtraction.

Unsupported fractional legacy incoming damage in an explicit beam/player-state encounter is now rejected before it can be used. Source-player HP/barrier handling also rejects the old aggregate guard multiplier when guard!=1, rather than mixing an unproved armor approximation into integer source state.

Limits remain: ordinary nonbeam incoming status/reaction behavior is incomplete, and the generic assumed enemy strike loop is not a newly decoded Menu_MainUpdate delivery scheduler. The stiffness component can be used with explicit powered beam-context hits, but that does not prove exact ordinary-enemy status timer phase. Player defense, armor, PE and critical-resistance data must still match the earned state. Do not promote this pass into a full common combat validation claim.

## Validation and reproducibility

**125 focused tests pass**, including11 new broad-combat checks. They compare all365 accepted arithmetic chains at four scale values against the decoded expression evaluator, including signed overflow; reject an artificial CFG merge; check identity/scale handling; exercise HP/PE/barrier/zero-damage/type10 integer behavior; and cover the barrier crash regression, mixed incoming hits and ordinary-enemy full integration. Existing weapon/ammo, beam, chooser, geometry and source-counter checks remain passing. The runner excludes the encounter benchmark test and all balance runners.

Run from the bridge with bundled Python and PYTHONPATH=tools:

- `python -m pe_weapon_sim.audit_shared_combat`
- `python -m pe_weapon_sim.validate_beam_combat`

`data/pe-shared-combat-coverage-2026-10-18.json` contains declaration records, catalog/proof offsets, conditional scale1.0 examples, logged-appearance coverage and source/input hashes. Scale1.0 examples are labeled controls, not runtime defaults. `data/pe-beam-combat-validation-2026-10-18.json` records125 passing focused checks and implementation/source hashes. Historical balance outputs remain unchanged.

Rerun readiness remains false. Highest payoff next: validate selected actions and delivery timing for the most frequently logged ordinary enemies, and join source-earned defensive inputs before broad balance conclusions. Preserve the outstanding work on generic status/reactions/Counter/cures/resets and interrupted/moving enemy behavior.
