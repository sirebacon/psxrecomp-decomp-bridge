# Ordinary-enemy identity, power and timing coverage — October 18, 2026 (Claude)

Next shared-combat priority after the defense join: ordinary-enemy actions. Offline except
for read-only memory reads of the running isolated session (port 4378, final Eve fight). No
balance runs (the hold stays). Audit: `python -m pe_weapon_sim.audit_enemy_coverage` →
`data/pe-enemy-coverage-2026-10-18.json`.

## 1. Scaled ranks: the farming room's enemy was invisible

The most frequent logged ordinary enemy (map 358, ID 0x000C, 78 of 383 appearances, the run's
farming room) matched nothing: its script (actor 6) sets rank 8 literally, then on a
progress-gated branch (V74 ≥ 272) adds `(N10 × 4) >> 16` through operand-table cells. Ten
scripts use this exact five-instruction idiom (all cell 10 × 4). N10 is initialised from
story variable V80 (N10 = V80, or 65536 when V80 is 0).

Live read (read-only): **V80 = 65536, N10 = 65536, V74 = 720** at the end of a first
playthrough, so the shared scale is 1.0 (rank 8 + 4 = 12, as logged). The same cell 10
drives 364 of the 365 scaled attack-power expressions. `enemy_identity.FIRST_RUN_SHARED_CELLS
= {10: 65536}` records this with provenance. Snapshot of both variable banks:
`data/pe-script-state-endgame-2026-10-18.json`.

`enemy_identity.py` resolves literal identities plus the scaled-branch alternate. The static,
timing and power catalogs accept optional `cells`; without them results are unchanged.

## 2. Power held in locals, per path

The same enemies compute slot-0 power into a local before the declaration, so the existing
multiply/shift matcher rejected it. `local_power.py` evaluates forward from the latest
unsupported instruction (trying the earliest workable start) with taint tracking: unknown
locals and cells spread as unknown and only drop a path if they reach a branch, the
rank/kind fields or the power operand. Story variables read on a path branch over {snapshot,
0}. Each path is keyed by the identity it writes; conflicting paths are rejected. Result
(scale 1.0): rank 8 → power 47 (V74 < 272), rank 12 → power 82 (V74 ≥ 272), critical chance
15, in all ten rooms. Used by `power_profile(..., scaled_identities=True)` as a fallback.

## 3. Category-2 timing bounds

`battle/context.c` Entity_TriggerAnimEvent: in slots 0-2 the exit-clip wrap completes the
action whatever its category, but only categories 1 / 3 hit at the frame crossing.
Category 2 is delivered on contact (`entity/combat.c` Entity_ResolveDropTable marks state 3).
So completion is proven (enter + exit updates) and the hit is not. `contact_timing.py` gives
a labelled bounds scenario: contact inside the action's own clips, `early` (windup = enter,
recovery = exit) or `late` (windup = enter + exit − 1, recovery 1). Charge reset on completion
is proven per call path, as in decode_enemy_actions. Contacts after the animation (slow
projectiles) fall outside the bound. Slot 3+ actions are excluded: their hit and completion
are script-driven.

## Coverage of the 383 logged ordinary-enemy appearances

| Resolved | Before | With first-run cells | + contact bounds |
|---|---:|---:|---:|
| static charge/rank | 244 | 331 | 331 |
| timing | 109 | 196 | 262 (bounded) |
| power, any slot | 271 | 374 | 374 |
| all three | 78 | 180 | 237 |

Bosses: unchanged except +7 timing via contact bounds (9 → 16 of 70). Still uncovered mostly
slot-3 (script-driven) actions, e.g. map 126 / 147 ID 0x12, map 333 / 265 ID 0x1A.

## Use (all opt-in)

`source_options`: `shared_cells=FIRST_RUN_SHARED_CELLS` (scaled identities in every catalog
and the default power scale; an explicit `source_shared_cells` wins), `contact_timing='early'
|'late'` (only where no animation-proven timing exists; slot must match the power slot).

## Validation

New tests: `test_enemy_identity.py` (8), `test_contact_timing.py` (5). Full suite 237 passed;
`validate_beam_combat` focused checks pass. Historical outputs unchanged.

## Limits / next

Coverage means a declaration is resolved, not that the AI selects it (no chooser model for
these enemies yet). V80 was read at the end of the run; earlier it is 65536 or 0 (both give
N10 = 65536 on the paths above), but EX-game scales differ. Next: script-driven slot-3
completion/hit decoding (the largest remaining gap), per-enemy action choice for the top
identities, then rerun matched seeds when the hold lifts.
