# Enemy action selection and attack timing — October 18, 2026

This pass reads the existing disc assets, original executable and decompiled sources.
No game was launched, controlled, or scanned live.

## What is now decoded

`decode_enemy_actions.py` follows possible control flow from actor script roots:
conditional and unconditional halfword-relative jumps, child-script entries, and registered
callback offsets. It stops at node termination and records invalid/out-of-bounds targets.
Literal branch conditions prune impossible edges. Unknown conditions retain both edges.
The output contains 191 actor scripts with 412 attack-command sites, 14,780 conditional
branch nodes, and 63 attack declarations with enough data for conditional timing.

This is an overapproximation of possible control flow. Registered callbacks and child nodes
are not guaranteed to execute; their scheduler, flags, geometry, external variables and
opaque handlers are not interpreted. Handler names can mislead: `Entity_CallAction` is a
polygon containment query, not an attack dispatcher. The actual animation attack wrapper
is `Script_RunEntityCommand`.

A small fragment evaluator (`script_decisions.py`) executes supported integer expressions,
assignments, supplied field/distance reads and branches offline. Unknown inputs or handlers
stop it. It is deliberately an isolated decision evaluator, not a full enemy AI emulator.
The raw output records concrete probe inputs, instruction traces, exit offsets and cells.

## Verified map 156 example

Actor type3 has rank22/kind2, giving campaign ID0x0216. Its script root is room byte208280.

- At root+4752, a decision fragment sets local3=1, reads distance to Aya into local5,
  and compares it with 85,196,800 (1300 in 16.16 units). At distance1299, the fragment
  branches to root+16264, then calls action slot0 at root+16280. At distance1300,
  it exits to root+4852 for further decisions. These probes assume the outer state,
  charge and position gates already allowed entry. They do not prove a global near/far AI.
- A separate child loop at root+3156 reads charge field0x2B, compares it with9000,
  and sets local35=1 once ready. Other state-bit and polygon tests gate the main chooser.
- Another reachable command calls slot4 at root+16140. It follows process-manager
  setup, and its effect lifetime is polled afterward. Its projectile timing is unresolved.
- Slot0 enters mode6 (42 frames) at step2.0, exits in mode7 (30 frames) at step1.5,
  category3, hit frame20. The original executable's initial enemy record template gives
  default steps1.0 for all six slots; explicit script step declarations override these.
- `Entity_AdvanceAnim` stores the previous fixed-point frame, adds the step, and wraps.
  `Entity_TriggerAnimEvent` changes to the exit clip after the enter clip wraps. It marks
  the hit when the exit clip's whole frame is strictly greater than20 and the previous
  whole frame is at most20. Thus enter takes21 updates, exit hit takes14 more, and
  exit completion takes20: windup35, recovery6, total41 animation advances.
  Nominally this is about1.17s to hit and another0.20s recovery at29.95 updates/s.
  It assumes no pauses, holds, interruptions, parent-animation substitution or actor skips.
  The damage application pass can follow the animation event; exact delivery latency remains open.
- After slot0 returns, root+16348 writes charge field0x2B=0. Charge is reset on completion,
  rather than consumed on entry. A straight post-command path proves this for49 of the63
  timed declarations. Other cases retain the generic reset assumption in the scenario.
- Slot0 power is indirect operand-table entry1. The setup computes it from
  `(node-active-flags[10] * 115) >> 16`; that external scale is not universally fixed.
  The timing scenario therefore retains the earlier damage fallback rather than substituting
  either operand index1 or an unproved constant115 as actual attack power.

## Combat integration and reruns

`enemy_catalog.py` joins action declarations through map + actor type to the existing static
map + rank/kind catalog. It rejects conflicting candidate timing lists. There are46 matched
identity keys with usable timing. Source combat opt-in `enemy_action_timing='fast'|'slow'`
selects the shortest/longest complete extracted slot0–2 animation sequence and applies its
windup, recovery, and verified completion-reset behavior. Explicit per-enemy profiles still
have final precedence. This choice is a scenario, not a recovered retail action probability.
It is not an envelope over missing projectile, movement or other unresolved actions.

Final reruns: 12,816 fights each, eight frozen campaign seeds/group, six fights/encounter,
D5/Disc2, eight build groups, fallback charge steps60/90/120, and150 paired
Counter-for-Quickdraw seed/loadouts per run. All ammo-conservation assertions passed.
Attack timing matched3,579/23,838 enemy instances (15.0%) in each run; static charge/rank/poison
matched18,138/23,838 (76.1%). Frozen pool timing coverage: D5 normal0/3, bosses2/5;
Disc2 normal4/23, bosses2/15. Unmatched enemies retain the previous generic timing.

The fast and slow runs produced identical combat records for the sampled enemies. Their
available extracted action timings therefore did not distinguish these choices. This is
not evidence that retail action selection has no effect.

| Fallback charge | Best Disc2 group | Score | Win fraction | Counter replacement score delta | Win delta |
|---|---|---:|---:|---:|---:|
| 60 | controlled_machine | 5.178 | .995 | +5.474 | -.039 |
| 90 | controlled_machine | 5.379 | .990 | +6.024 | -.051 |
| 120 | controlled_machine | 5.535 | .984 | +6.482 | -.061 |

Lower score is better; score is the geometric mean of encounter mean time +60*(1-win).
Counter deltas pool eligible Disc2 loadouts. There are no eligible D5 replacements.
Machine remains best in these conditional comparisons; Counter does not beat Quickdraw on
average. These are frozen earned equipment comparisons, not reoptimized progression or a
new global balance recommendation.

## Validation and outputs

Full suite:119 tests passed. New checks cover halfword jump targets, pruning literal
branches, child entry reachability, fractional step/strict frame crossing, rejecting
unproved wrap hits, exact map156 timing lookup, completion charge reset, and the isolated
1299/1300 distance decision. Existing combat, status, counter and ammo tests still pass.

Data: `data/pe-enemy-actions-2026-10-18.json`,
`data/pe-action-fast-balance-2026-10-18.json`, `data/pe-action-slow-balance-2026-10-18.json`.
Readable comparisons: `pe-action-fast-balance-2026-10-18.md` and
`pe-action-slow-balance-2026-10-18.md`. Data includes source/executable/asset hashes.
Selection probes were appended after the combat runs without changing action timing fields;
rerun metadata preserves the original input hash and identifies that annotation-only change.

Reproduce with bundled Python and PYTHONPATH=tools:

    python -m pe_weapon_sim.decode_enemy_actions --out findings/data/pe-enemy-actions-2026-10-18.json
    python -m pe_weapon_sim.run_behavior_balance --action-timing fast
    python -m pe_weapon_sim.run_behavior_balance --action-timing slow
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

## Next targeted steps

1. Interpret the chooser's concurrent charge/state latches and polygon tests, starting with
   map156. Extend the isolated fragment evaluator with verified handlers and explicit inputs.
2. Trace slot4 process-manager effect129, send-command arguments, and core field0x52 lifetime
   to recover projectile spawn/hit/completion timing. Five-argument declarations lack enough
   direct hit-frame metadata for the current melee path.
3. Resolve external scaling and dynamic attack power; preserve rank/kind identity and room
   occurrence matching rather than copying one enemy's values to all rooms.
4. Trace parent-linked animation selection, interruption/counter interactions and the pass
   that delivers state3 damage. Then replace the remaining generic scheduler and rerun
   identical seeds with per-action choices; report coverage separately from fallback results.
