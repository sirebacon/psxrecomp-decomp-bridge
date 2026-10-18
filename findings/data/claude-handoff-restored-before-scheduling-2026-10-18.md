# Claude / Codex simulation handoff

Last updated: October 18, 2026, by Codex.

## Start here

**Current user instruction: hold balance reruns until projectile geometry and linked beam
handling are coherent. Continue offline extraction/implementation and focused checks.**
Read `pe-beam-cleanup-combat-integration-2026-10-18.md` first, then
`pe-joint-beam-integration-2026-10-18.md`, then
`pe-projectile-geometry-linked-beams-2026-10-18.md`. New geometry/delivery
primitives now have an opt-in full combat beam adapter; previous balance results have not been regenerated with them.


Latest offline pass: read `pe-enemy-projectile-timing-2026-10-18.md` first.
Then read `pe-enemy-action-timing-2026-10-18.md`.
Then read `pe-enemy-script-extraction-2026-10-18.md` and
`pe-static-script-balance-2026-10-18.md` first. The raw room-script inventory is
`data/pe-enemy-scripts-2026-10-18.json`; rerun data is
`data/pe-static-script-balance-2026-10-18.json`. This adds static enemy declarations,
not a complete AI interpreter. The older behavior rerun remains the no-catalog comparison.


Read `pe-weapon-p3-targeted-followups-2026-10-17.md` and
`pe-weapon-p3-runtime-validation-plan.md` first for the latest validation work.
Then read `pe-weapon-p3-L-conclusions-2026-10-17.md` and
`pe-weapon-p3-K-validation-2026-10-17.md`. Reports C–L and the completion JSON
supersede checkpoint combat results in the original tables and first continuation.
The first continuation remains the historical record of the earlier run.

Repository: `D:\Recomp Games\psxrecomp-decomp-bridge`.
Simulation package: `tools/pe_weapon_sim`.
Original task scope: `findings/SimulationPrompt.txt`.

## Work log

1. Retrieved referenced conversation `6ad2d556-9cb4-83e9-beb5-98ee5a8e8ba2`; located its three
   attachments and matching local reports. Earlier assistant prose was unavailable through
   the reader, which supplied content-reference markers.
2. Checked repository state. Claude's Phase 3 package, test, data, and reports were already
   untracked; they are pre-existing work and must not be removed or attributed to Codex.
3. Inspected simulation code and project requirements. No AGENTS.md was found in this bridge
   repository by the initial hidden-file search.
4. Ran existing tests: 56 passed. Default Python alias failed to launch; used bundled runtime.
5. Corrected timing cache isolation in economy/surrogate.py; added a targeted regression test
   to tests/test_economy.py. Full suite: 57 passed.
6. Added economy/run_continuation.py. Ran 80 matched seeds for C/G/B_shotgun under overlap and
   serial timing, benchmarked first 40 seeds at D5 and Disc2. Run finished successfully in
   21.58 seconds. Saved raw records and source hashes in the new continuation JSON.
7. Wrote focused findings and this handoff. Original simulation outputs remain unchanged.
8. On the user's request to continue, found checkpoint Item references were mutable. Later
   upgrades and donor transfers could change equipment used to benchmark earlier checkpoints.
   Fixed playthrough.checkpoint to deep-copy gun, secondary and armor. This supersedes previous
   checkpoint combat findings, including the first continuation; resource summaries were already
   compact snapshots and did not have that reference bug.
9. Fixed evaluation.spearman to average tied ranks and correlate those ranks. Added snapshot
   isolation and tied-rank regression tests. Full suite passed 59 tests before new experiments.
10. Added run_completion.py: 51 experiment groups, 100 matched seeds per group, first 40
    benchmarked at D5/Disc2, ten fights per encounter. Includes C-derived preferred classes,
    BP strategies, exploration profiles, S0–S4 under both timing assumptions, and resource
    ablations. M10B ownership/capacity milestones record cumulative spending and bonus origins.
11. Added report_completion.py to generate reproducible reports C–L from the separate completion
    JSON. Reports explicitly distinguish measured model outputs from unvalidated game behavior,
    and identify original questions that require further targeted experiments or runtime data.
12. Completed all 51 groups: 5,100 invariant-checked campaigns and 2,040 benchmarked campaigns
    at two checkpoints. Generated C–L successfully. Corrected surrogate rank agreement is
    0.937 (D2–4), 0.969 (D5), 0.789 (Disc2), on 30 loadouts per checkpoint.
    The 59-test suite also passed after implementation. Remaining questions are listed in L.
13. User authorized continued validation and targeted follow-ups. Inspected decompiled
    Menu_MainUpdate, Battle_AdvancePhase, FinishAction and rate setup, plus CURRENT half-bar
    switching and combat logger. Found action flag 0x100 gates gauge gain, favoring serial-style
    pause behavior. This is source evidence, not a runtime timing capture. The 94-Hz aggregate
    calibration and exact shot/reload duration remain unverified. Wrote a frame-level capture
    protocol with source references and existing debug addresses.
14. Corrected the inherited mod-target cache to include timing and item base stats; added a
    regression test. Prior completion groups used separate pools, so those outputs are not
    invalidated by this fix.
15. Added run_followups.py and report_followups.py. Completed 320 campaign replays: 40 matched
    seeds for C, G, C-derived shotgun and D under both timings, with D5/Disc2 benchmarks using
    20 fights per encounter. Ran paired Commands/Quickdraw/both removal, frozen-loadout clock
    sensitivity at 94 vs 59.9 Hz, and two-weapon optimistic portfolio screening with a scalar
    half-fill switch-cost alternative. Saved separate raw JSON and generated a report.
16. Added ablation-copy and portfolio-delay tests. Full suite: **62 tests passed**. Raw results
    and report distinguish whole-policy campaigns, frozen-loadout interventions, and optimistic
    switching bounds. No dynamic switching or live timing capture was claimed.

## Decomp-first continuation — 2026-10-18

COUNTER/ENEMY CONTINUATION COMPLETED OFFLINE: see `pe-counter-enemy-derivation-2026-10-18.md`.
New source_enemy.py models exact discrete Counter roll outcomes, common u16 enemy charge,
slow, status-cycle and31-update poison timers, plus descriptor-driven integer enemy damage.
ScriptedEnemy separates a supplied charge/windup/recovery policy from verified common timers.
source_behavior_rules() enables this scenario; older source_combat_rules() keeps random-period
enemies for reproducibility. Missing enemy-specific policy/data are labeled assumptions.

Counter is no longer rejected. Source Battle_SetupEntityTarget queues one command at the
pending attacker without spending gauge; Random counter fires1, Attack All repeatsRoF,
ordinary/Burst queuesRoF. CounterHP-level integer rolls and rank differences follow source.
Latest eligible attacker overwrites a single pending record; an idle hook executes a counter
during refill without recursively interrupting an executing queue. Exact reaction pose
save/restore/input priority remains approximate: default settling21 updates, Counter priority.
CURRENT does not boost the HP-level value (the runtime mod disabled that HP-bug mechanism).

Offline existing-PST extraction saved `data/pe-enemy-state-extract-2026-10-18.json`: Aya
rank33/HP-level320; Eve controller step120 and linked parts step0. Not universal enemy AI.
Balance missing ranks use inferred encounter level; HP-level uses explicit level*10 fallback.

Reran12,816 fights on8 matched frozen earned seeds/group at D5/Disc2,4 encounters and3
charge-step scenarios60/90/120;150 equal-slot Quickdraw→Counter replacements. Corrected
CURRENT poison scaling and regenerated final output. All fights conserved ammo;108 tests
passed. Raw `data/pe-behavior-balance-2026-10-18.json`; report `pe-behavior-balance-2026-10-18.md`.
controlled_machine has lowest Disc2 mean score in these scenarios; Counter replacements
worsen pooled mean loss-penalized score by4.123/6.172/6.784 across the3 rates. Conditional
results only: old campaign acquisition decisions were frozen, not reoptimized. D is its
earned primary here, not a newly optimized two-gun policy. No universal ranking claim.

Important: enemy room-script AI, action-specific parameters, reaction interrupts and3D
movement are not fully decoded. The new common clocks are not permission to invent a
retail attack schedule. Benchmark policies/HP385/reserve999 are explicit sensitivities;
missing action power retains old level-based damage fallback. Optional actual profiles can
use source damage params; selected action slot chooses armor parameter, not category byte.
Next extract room scripts/data and calibrate the economy scorer before full progression
reoptimization. No emulator connection, gameplay, live scan or save load in this pass.

FULL-COMBAT ADAPTER CONTINUATION (offline): read `pe-source-combat-integration-2026-10-18.md`.
engine.fight now accepts decomp_animation.source_combat_rules(CURRENT/VANILLA), dispatching
to source_combat.py. Source events apply the existing damage/status/critical/range/splash
formulas at hit time while modeled enemies act during refill, shooting, reload and switch
execution. Target death, encounter thresholds, HP defeat and time caps stop the action.
source_options provides HP/reserves, secondary configs, a weapon-policy callback and
explicit menu/stream waits. _source_state carries magazines, pools, gauge, equipped gun
and remaining HP through linked endurance segments; _source_events is optional trace.

Attack All RESET CONFIRMED BY STATIC RETAIL INSTRUCTIONS as well as decomp callers:
ready loads turnWord&15 and jumps to shared remaining-counter store/fire tail; successful
repeated-shot reload enters mode12; its caller restarts aim without restoring the old count.
New audit_attack_all.py verified14 exact signatures in the original US EXE backup. Artifact
`data/pe-attack-all-retail-audit-2026-10-18.json` records executable hash and instruction words.
Regression: RoF5/capacity5/loaded2/reserve5 against durable target fires7, both in standalone
state model and integrated fight; stops early if target dies. This supersedes the earlier
"unconfirmed decompiled inference" status, but is static evidence, not a live execution trace.

Validation:99 tests pass. run_source_combat.py completed944 encounter benchmark calls
(1392 underlying fights including chained endurance), with ammo conservation in every result.
Raw `data/pe-source-combat-2026-10-18.json`; report `pe-source-combat-validation-2026-10-18.md`.
Synthetic frozen equipment/explicit HP300 and reserves, not new earned-loadout rankings.
Poor-survival cases must be read with win rates; short defeat times are not clear times.

Limits: inherited enemy AI/movement/status/armor assumptions; supplied or seeded geometry;
external PM/asset latency still modeled/supplied. Counterattack scheduling and serial timing
explicitly reject rather than silently mis-model. Economy surrogate rejects combat_backend
source until calibrated; direct encounter benchmarks are integrated. Historical defaults
and reports remain reproducible. No game process, input, save load or live scans this pass.

STATEFUL RELOAD/MODE/SWITCH CONTINUATION COMPLETED OFFLINE: see
`pe-source-battle-derivation-2026-10-18.md` and `pe-source-battle-validation-2026-10-18.md`.
New source_battle.py models finite shared reserves, per-gun loaded ammo, dispatch and
mid-queue transfers, extracted reload clips, Random queue construction, Burst's signed
angle predicate, Attack All repeated hits, timed hit callbacks, dead-target skips,
CURRENT/retail switch gauge costs and carried state across multiple weapons. Switch menu
and stream waits are explicit inputs; the destination gauge refills during the modeled
post-commit stream/clip interval. No unconditional0.8s reload in this backend.

Entry point: engine.source_sequence(guns,reserves,equipped,actions,**state), or BattleSession
for hit/death callbacks. This new backend is separate from the historical aggregate fight
and surrogate; do not claim that their reload/mode approximation was replaced wholesale.
Do not route source_rules/asset_queue special-mode configs to old fight: it still rejects
those modes. Next connect the event backend to damage/status, enemy AI and acquired loadouts.

Ran192 attack cases and168 carried-state multi-weapon sequences, saved raw events under
`data/pe-source-battle-2026-10-18.json`. Every firearm attack case asserts ammo conservation.
Fourteen new tests; full suite90 passed. No game process, input, save load or runtime scan.

Important qualification: Attack All's reload path appears to reset the per-target shot
counter in the decompiled ready branch, producing extra repetitions with short magazines.
Preserved as an explicit source-path inference pending independent retail code checking.
Normal switch mode13 assumes the extracted16-frame base clip and17-call normalized path;
bank streaming latency is supplied, not predicted. Burst requires real caller angles,
not a50% cone guess; Python RNG is reproducible but not retail rand()-identical. Grid
results validate transition cases, not completed combat rankings or secondary superiority.

ANIMATION EXTRACTION COMPLETED (offline): see `pe-animation-derivation-2026-10-18.md`.
extract_animations.py reads the existing isolated slot9 PST RAM and Disc2 BIN using the
source-defined sector/bank/header formats. Extracted142 headers across16 weapon banks,
all8 classes in2 variants; output `data/pe-animation-extract-2026-10-18.json` includes
snapshot SHA256, per-bank payload hashes, offsets, sector ranges and raw headers. No game
input, save load, launch or new live scan. Loaded handgun headers agree with disc bank.

Added decomp_animation.py ordinary queued-shot timeline and source_rules() experimental
profile; engine and economy surrogate both use extracted commitment and exact refill
at nominal59.9/2 updates/s. Historical defaults remain reproducible. Profile rejects
Burst/Random/AttackAll until alternate branches are reconstructed. Six new tests; full
suite76 passed. Generated64 duration cases and14 controlled frozen-equipment benchmark
groups: `pe-animation-durations-2026-10-18.md`, raw `data/pe-animation-validation-2026-10-18.json`.
Results combine a clock correction with animation changes, not animation-only sensitivity.

CORRECTION: ANIM row bytes are pose-hold update counters, not complete animation loops;
counter3 is a retarget hold rather than mandatory post-turn recovery. Aim/fire asset lengths
vary by class (machine8/3, handgun15/10, shotgun15/30, rifle15/15). Variant1 grenade/club
aiming is30 rather than15. Normal loop calls Battle_Update before advancing animation and
Draw_RenderFrame normally VSync(2). Ordinary shot dispatch does not set game flag0x100:
earlier serial preference came from PE/non-shot paths. Normal ordinary shots support
overlap; special actions/pauses are distinct. No-stall nominal clock is29.95Hz, not94Hz.

Scope: timeline covers uninterrupted ordinary queued shots, with explicit target-change
indices available. Fight engine still aggregates volley damage at turn time and does not
pass actual target-change events to this timing helper. Reload scheduling/0.8s remains
legacy; source shows conditional mid-queue reload and mode12. Mode13 switch clip is16
frames in snapshot but not a complete streaming/menu switch duration. Next implement
event-level damage/hit triggers, mid-queue reload, alternate modes and carried-state switches.

Animation follow-up: source DOES implement duration mechanics. field/actor_collision.c
Entity_SetActionMode loads animLastFrame = animation header.frame_count-1;
Entity_AdvanceAnim advances a signed16.16 animStep with hold/stop/wrap handling.
battle/context.c modifies step at action event boundaries. entity/frame_update.c calls
the animator. Next extract action headers/model mapping and trace update cadence/event
ordering; do not assume gameplay timing measurements are required to derive durations.

User requests source-driven development, avoiding gameplay except targeted scans. Follow
that direction. No gameplay or live scan in this pass. Read the source findings in
`pe-source-audit-2026-10-18.md` before continuing.

Added source_timing.py, run_source_timing.py and six tests; full suite: 70 passing. Generated
512 switch/gauge transitions and `pe-source-timing-2026-10-18.md` with separate raw JSON.
Source timing handles integer rate, status precedence, gauge gates, borrowed-menu refunds
and CURRENT half-cost vs retail full-cost switch transitions. Units are eligible gauge
updates, not seconds. Menu/animation time remains excluded. engine.fight can opt into exact
gauge arithmetic using rules['source_gauge']; economy surrogate must be updated before
whole-policy campaigns use that option. Historical defaults/results remain reproducible.

CORRECTION: unchanged INVENTORY ammo in earlier live captures cannot exclude firing.
Battle_FinalizeAttackResult subtracts from active BattleAction.attackWord &0x3FF; separate
commit/sync functions copy it to inventory. Earlier captures did not record active action.
Their firing status is unverified. Future capture defaults to passive scan/no state load,
records active-action ammo and rejects comparisons when the action pointer changes.
This source evidence supersedes the earlier inference that lack of inventory changes
proved nonexecuted/canceled attacks. Observed refill and pause-flag data remain as recorded.

Next source tasks: reconstruct reload scheduling, finite reserve pools and animation event
timing; then connect carried gauge/ammo switching to encounter simulation and surrogate.
Do not describe deterministic switch transitions as a completed dynamic portfolio model.

## Live session update — 2026-10-18

See `pe-weapon-live-timing-2026-10-18.md` for setup, evidence and exclusions.
Isolated executable/save/cache copy is in `live-timing-session`; current normal frontend
is on debug port 4378. User activated native god mode; current HP is 385/385. Preserve
this session when possible. Disc 2 slot 1 reaches Eve after moving forward and skipping
the event; isolated slot 9 captures combat start. Original saves were not edited.

Verified refill only: attack03/04 each take 230 guest VBlanks from gauge 0 to 9000 at
rate 79, approximately 3.840 s at nominal 59.9 VBlanks/s. These samples did NOT consume
ammo. No completed weapon change has been recorded. Do not treat attack/switch filenames
as proof of successful actions, and do not replace model firing/switch costs yet.
The pointer at 0x8009D254 is BattleEntity; dereference its first word for Combatant core.

Added live_probe.py, live_timing_capture.py, analyze_live_timing.py and two analyzer tests
(64 tests passed in full suite). Debug request log, raw captures and PNGs are under the
isolated session. Passive captures with --load -1 now release overrides for the user's
controller. Most recent capture attempt is god-passive-attack01; inspect its ammo changes
before making any firing claim. That capture completed: 873 contiguous VBlanks, HP385 and
gauge9000 throughout, ammo10->48 only at frame20194, no ammo decrease or pause flag. It
does not establish firing duration or reload duration. Existing inventory has USP-TU/M8000/Club3/Maeda's Gun,
so direct validation of MAG/P90/M10B secondary niches still needs appropriate loadouts.

## Latest findings and priorities

- Source supports serial pause more strongly than unconditional overlap; keep duration and
  clock calibration open until frame-level samples exist. Existing detail timestamps are
  whole seconds and do not resolve refill versus firing boundaries.
- Commands and Quickdraw removal materially slows many final builds. At D5 neither effect
  was present in these sampled loadouts, making the removal a no-op there. Empty-slot ablations
  do not prove mandatory effects: next test legal replacement effects at equal slot/resources.
- D's secondary has no modeled D5 niche. At Disc2 all 40 overlap portfolios and all 38 serial
  portfolios that own a secondary have at least one encounter niche after the assumed half-fill
  scalar delay. Mean within-D optimistic suite gains are 0.47s and 0.60s, respectively. This is
  not evidence of beating C, and it is not a validated dynamic switch simulation.
- 59.9 versus 94 Hz changes frozen-loadout clear times materially; never reinterpret logger
  frame frequency as a verified gauge-update frequency. Next measure idle refill separately.
- First M10B observation in the earlier runs is policy-conditioned; the policy restricts
  crafting to D5/Disc2 and play() adds final Wayne maintenance. Verify actual first accessible
  Wayne visit with 300 Junk before making claims about earliest legal acquisition.

## Cache correction status

run_completion created a fresh process pool per group, isolating timing, base-stat variants
and policy caches. Its historical missing-key caveat is now resolved: policies._TARGET_CACHE
includes SG.TIMING and tuple(item.base). The standalone surrogate score cache also separates
timing. Keep future engine-global sensitivity changes isolated and clear evaluation caches;
the follow-up driver clears them when changing TICK_HZ and restores globals in a finally block.

## State and boundaries

Live testing uses isolated copied saves/settings and a new isolated combat snapshot;
the user enabled god mode in that running test session. Original saves were not edited.
No commits, staging, deletion, or messages sent to
another chat or service. The user requested continuation and documentation for cooperation
with Claude; this file is the durable handoff, not evidence of a live Claude connection.

Codex edits: economy/surrogate.py, economy/playthrough.py, economy/evaluation.py,
and tests/test_economy.py.
Codex additions: economy/run_continuation.py, findings/data/pe-weapon-p3-continuation-2026-10-17.json,
findings/pe-weapon-p3-continuation-2026-10-17.md, and this file.
Further additions: economy/run_completion.py, economy/report_completion.py,
findings/data/pe-weapon-p3-completion-2026-10-17.json, and generated reports C–L.
Latest additions: economy/run_followups.py, economy/report_followups.py,
findings/data/pe-weapon-p3-followups-2026-10-17.json,
findings/pe-weapon-p3-targeted-followups-2026-10-17.md, and
findings/pe-weapon-p3-runtime-validation-plan.md. Further edit: economy/policies.py.

The original runner can overwrite original results, even on a partial run. Use the separate
continuation driver to reproduce this work. Keep VANILLA, CURRENT, and experimental results
separate. Update this handoff with actions, commands, validation, and caveats after future work.


## October 18 — enemy-specific room/script extraction and catalog scenario

- Continued entirely offline; no emulator launch, game control, or live memory access.
- Added `tools/pe_weapon_sim/extract_enemy_scripts.py`: 103 campaign battle maps on
  both discs, 206 asset reads, zero errors, all corresponding room hashes equal.
  Records opcode/operand addressing modes, root/byte offsets, room and source hashes.
  Disc-deduplicated inventory: 2,970 animation headers, 404 action declarations,
  47 action-step declarations, 8,465 self setters and 237 cross-actor setters.
- Important identity correction: logged enemy ID is core rank/kind, not actor type/subtype.
  Added `enemy_catalog.py`: 135 consistent map + rank/kind declaration keys. Opt-in
  `static_enemy_catalog=True` overrides charge/rank/poison only; explicit profiles take
  precedence. Missing/ambiguous matches retain defaults. Returned coverage counters
  make partial extraction visible. This is a static scenario, not executed AI proof.
- Example map156 actor3 / ID0x0216: charge70, poison29; action0 modes6/7,
  category3, hit frame20, enter2.0/exit1.5 steps, clip counts42/30. Power is an
  indirect mode3 operand-table entry1. Do not use the operand index as damage.
- Reran 12,816 fights with eight frozen seeds/group and six fights/encounter, including
  150 paired Counter-for-Quickdraw loadouts. Matched18,138/23,838 enemy instances
  (76.1%). Source ammo-balance checks all passed. Disc2 controlled machine scores
  5.191/5.423/5.573 with win .995/.990/.984 across fallback steps60/90/120.
  Counter replacement mean score worsens +5.632/+6.376/+6.764; win changes
  -.043/-.057/-.066. This does not establish a new retail balance recommendation.
- Tests: 111 passing, including argument-mode boundary decoding, truncation rejection,
  exact identity mapping and known room declaration checks.
- Remaining limits: linear decoding has no reachability proof; actor switches, callback
  execution, indirect setters, action chooser conditions, and animation-event timing
  are unresolved. Generic windup10/recovery10, old hit/geometry/damage fallbacks,
  reaction settling, and historical acquisition choices remain. No campaign reoptimization.
- Next: reachable control flow plus actor/operand-table tracking; map156 action-power
  dependency is a concrete starting point. Then derive per-action hit/completion events,
  expand verified catalog joins, preserve repeated room occurrences and rerun matched seeds.
- Reproduce: set PYTHONPATH=tools, use the bundled Python runtime, run
  `-m pe_weapon_sim.extract_enemy_scripts --out findings/data/pe-enemy-scripts-2026-10-18.json`,
  then `-m pe_weapon_sim.run_behavior_balance --static-catalog`, then
  `-m unittest discover -s tools/pe_weapon_sim/tests -q`.


## October 18 — action choice control flow and attack timing continuation

- Stayed entirely offline. Added `decode_enemy_actions.py` and `script_decisions.py`.
  Possible control flow includes literal-pruned jumps, child entries and callback targets:
  191 actor scripts with412 attack-command sites and63 conditional timed attack records.
  These are possible paths, not complete AI execution/probabilities. Opaque handlers remain
  unevaluated. `Entity_CallAction` is actually a polygon query; don't treat it as an attack.
- Original executable enemy template establishes default enter/exit steps1.0. Script steps
  override them. Positive fixed-point animation crossing gives hit/completion times for
  supported slots0–2; unproved wrap hits and incomplete descriptors are excluded.
- Map156 / ID0x0216 slot0: enter42 frames at2.0, exit30 at1.5, strict hit-frame20
  crossing =>windup35/recovery6 updates. Core charge is explicitly zeroed after command
  completion (root+16348). Added opt-in completion reset to `ScriptedEnemy`;49/63 extracted
  actions have a straight post-command path proving the zero setter.
- Isolated chooser probe: entering map156 root+4752 with distance1299 follows slot0
  entry root+16264; distance1300 continues at root+4852. Outer state/charge/polygon gates
  are not evaluated. The actual chooser uses a charge-ready latch plus state/position checks.
  Reachable slot4/process-manager projectile remains unresolved; its timing is not invented.
- Action catalog has46 map/rank/kind keys. `enemy_action_timing=fast|slow` selects shortest/
  longest complete extracted melee sequence and applies timing/reset behavior. Explicit
  per-enemy profiles override it. This is a partial-action scenario, not full AI replacement.
- Final corrected reruns:25,632 fights total (12,816 each), all ammo assertions passed.
  Timing matched3,579/23,838 enemy instances per run (15.0%); charge/rank/poison76.1%.
  Both scenarios produced identical records for sampled enemies; unresolved action choices
  are not thereby validated. Disc2 machine scores5.178/5.379/5.535 and wins.995/.990/.984;
  pooled Counter replacement deltas+5.474/+6.024/+6.482, win-.039/-.051/-.061.
- Full suite:119 tests passed. No campaign reoptimization or new global balance proposal.
- Read `pe-enemy-action-timing-2026-10-18.md` for exact source reasoning, assumptions,
  reproduction commands and next steps. Raw output `data/pe-enemy-actions-2026-10-18.json`;
  comparisons `data/pe-action-fast-balance-2026-10-18.json` and slow counterpart.
  Decision probes were added after runs without changing timing/reset fields; metadata
  preserves the original input hash and annotation-only provenance note.
- Next: concurrent chooser latches/geometry, slot4 effect129 process-manager lifecycle,
  indirect power scaling, linked-parent animation and state3 damage-delivery ordering.


## October 18 — projectile timing and chooser inventory continuation

- Stayed offline. Added `extract_projectiles.py`, `source_projectile.py`, and
  `run_projectile_targeted.py`. Raw output `data/pe-projectile-extract-2026-10-18.json`.
- Bound effect129/130 task programs in map156 and380 (four registrations). Correct
  overlay mapping: virtual0x8018EFE8 corresponds to room byte0, not payload8.
  Effect129 waits46 effect updates, starts controller on47, emits orb at age1/update48.
  Contact is XZ-only with cylinder radius added,150 flight/400 burst, burst timer1..8;
  held25 counter rearms after24 updates. Flight adds speed plus jitter[-16,15] per axis.
- Distance chooser is Manhattan XYZ, not Euclidean. Strict speed bands:
  >3500:250, >3000:200, >2000:150, >1500:120, >1000:100, else80.
  Indexed273 immediate distance comparisons,1,583 random-assignment sites,1,982 state
  branch sites across possible CFGs. Setup/random sites are not action probabilities.
- Linked beam actor4/5/6 parameters branch on node-active-flags[27]==1:
  short60/60 all; otherwise300/300 for actor4 and300/140 for actors5/6.
  Beam task starts47, warms6+6, first active opportunity59, fades32 after duration.
  Long140 opportunities59/199/339; callback ends390. Beam extraction/tests are complete
  for these conditional parameters; beam damage is not injected pending actor coupling,
  shared-target cell21..26 semantics, parent animation and overlapping damage flags.
- Opt-in `projectile_height=320|640` applies only map156 ID0x0216. Outer chooser gates
  assumed entered; near<1300 uses prior melee35+6, far forces later slot4 path.
  Geometry is stationary aligned1D point player, flat floor, inside polygon, assumed
  launch height. Exact joint pose/heading, visual callback drain and damage delivery are
  unresolved. Completion uses minimum63 updates/25 after impact, an explicit surrogate.
  Separate deterministic jitter RNG preserves close melee combat random stream.
- Final reruns:27,936 combat fights (12,816 each height +2,304 focused control fights).
  All ammo checks passed. Each full run matches432/23,838 enemy instances (1.8%) for
  new projectiles; old timing15.0%, static stats76.1%. Height320 launched942/contact426;
  height640 launched483/contact483. Contacts are model geometry events, not retail hits.
  Disc2 results unchanged: machine remains lowest score; this boss is in D5.
  D5 fallback90 groupG scores12.435(win.995)/11.347(win1.000) for320/640.
- Focused fixed-distance1000 control exactly matches old melee baseline across heights.
  At distance1300 wins.880/.885/.896 for baseline/320/640. At2000/4000 most loadouts
  cannot reach the boss; treat those as pressure/horizon tests, not weapon-rank evidence.
- Full suite132 tests passed. No campaign reoptimization or new global balance proposal.
  Read `pe-enemy-projectile-timing-2026-10-18.md` for results, derivations, limitations,
  reproduction commands and next targets. Full data `pe-projectile-h320-balance-2026-10-18.json`
  and h640 counterpart; focused `pe-projectile-targeted-2026-10-18.json` under data/.
- Next: extracted joint7/floor/cylinder/heading geometry, actual visual pool drain,
  contact-to-damage ordering, shared beam state27/targets21..26 and chooser concurrency;
  then indirect power scaling and identical-seed reruns.


## October 18 — geometry / linked-beam delivery, reruns held

- User explicitly asked to resolve geometry/linked damage and hold rerunning until ready;
  later “continue” preserves that instruction. No full or targeted balance runs this pass.
  Offline extraction and11 focused unit checks only. Do not launch a rerun just to update scores.
- New `extract_projectile_geometry.py`, `projectile_geometry.py`, focused tests and
  `data/pe-projectile-geometry-2026-10-18.json`. Read
  `pe-projectile-geometry-linked-beams-2026-10-18.md` for full reasoning.
- Map156 source floor=-1873; actor7 registers nine actual effect-boundary vertices.
  Extracted47-part model, bounds/translations/67-byte hierarchy commands and168 full
  animation frames for modes8/9/10/11. World pose/PSX fixed-point hierarchy remains pending.
- Important radius correction: Aya model setup radii vary by weapon class; both costumes
  agree: handgun23, shotgun35, machine41, rifle63, grenade37, rocket53, special23, club27.
  All16 banks read offline; saved runtime radius63 matches its model. Do not copy63 to all
  weapons or retain the old point-player assumption in the next validated backend.
- Orb local offset(0,-70,-100), joint7; beam(0,0,-100), joint31. These must be transformed
  through animated world matrices, not interpreted as world positions or fixed heights.
- Owner linkage resolved on analyzed path: independent actor4/5/6 combat records wait on
  cells18/19/20, copy type3/sub31 position, use slots0/1/2 and target cells21..26, execute
  own action record3, wait for held0x52 to clear, then clear trigger. Sub-ID31 in actor query
  is not joint31. An actual C parent pointer is not required by this path.
- Delivery correction: Menu_MainUpdate evaluates reaction/action gate once, then scans
  actor order. Multiple pending state1/2 beam owners can deliver in one admitted pass.
  Each pending bit clears on delivery; global player0x4000 clears at end even if gated.
  90-update0x01000000 immunity belongs to separate body-contact gate, not this action-hit test.
  Staged drain helper has tests for simultaneous owners, gated/persistent flags and ordering.
- Beam record3 power is u16((sharedCell10*90)>>16), with script scale source/fallback still
  requiring encounter-state resolution. Armor second parameter applies to slot3.
  Effect type5 adds stiffness lock: can clear Haste, timer9000 status units decays by
  statusStep3C, resistance armor can prevent with50% roll. Do not model beams as pure HP
  subtraction or infer duration from raw9000. Incoming status/cures/reactions remain to wire.
- Validation:11 new focused checks passed; previous132-test suite not rerun this pass.
  Previous balance JSON/Markdown were not changed. New JSON explicitly records ready=false.
- Continue with fixed-point joint/world pose validation, actual shared target strategies,
  FX pool drain/order, incoming stiffness and actor-ordered delivered damage. Run small
  focused validation before judging readiness; only then resume matched balance runs.


## October 18 — validated joint reconstruction and staged beam damage/status

- User authorized joint reconstruction and beam damage/status integration, keeping work
  offline and holding balance reruns until validated. Hold remains active. No balance or
  targeted encounter benchmarks this pass; only isolated math/component validation.
- New `joint_reconstruction.py` ports LIBGTE FGO_02 RotMatrixYXZ exactly with retail sine
  table, signed low32 multiply/shift order and halfword storage. `rotation_oracle.py`
  executes only original bounded656-byte math routine, not game code outside that function.
  1000 signed-angle cases matched. Source file is src/main/psyq/libgte/fgo_02.c.
- Source hierarchy push/pop/part-Z/root-XYZ composition and rotation overrides implemented.
  Existing Disc2 PST check reconstructs rendered frame2 from raw channels/world input;
  all29 saved joint rotations/translations match, zero mismatches. Actor next frame3.
- Reconstructed168 hospital boss frames. Orb point relative Y mode8:-638..-354,
  mode9:-914..-441; mode9 frame0..4:-441,-506,-592,-692,-800. Do not choose an encounter
  launch height until actual cached-pose and process/render timing is established.
- New `beam_delivery.py` stages world-target emitter contacts -> per-owner pending latch
  -> actor-order HP/barrier damage -> stiffness. Separate effect and delivery passes, no
  auto-completion from fade alone. Real pool drain must call explicit finish_tasks.
- Source damage power scale signed32>>16/u16; slot3 armor second; defense/critical/guard/
  barrier path implemented. Stiffness lock ordering includes already-locked no-refresh,
  50% armor resist before one-time-immunity consumption, Haste removal, timer9000 status
  units, u16/signed expiry, motion freeze and mode17 base-mode restore. Cures/whole-frame
  order remain external. Reaction requests/hooks avoid inventing angle or Counter priority.
- Three-owner fixture with Haste, defense100, armor-second10, power90 delivers74/60/60,
  HP500->306, timer set once. Removing Haste increases defense deduction here, reducing
  later damage. Geometry fixture connects overlapping targets and radius23 into this
  sequence. Boundary640 misses radius23 but hits radius63.
- Validation15 focused new joint/beam tests +11 existing geometry checks passed; no full
  suite claim this pass. No edits to historical balance outputs or full combat runner.
- Read `pe-joint-beam-integration-2026-10-18.md`. Data:
  `data/pe-joint-reconstruction-validation-2026-10-18.json`, containing oracle hashes,
  saved-pose proof,168 pose samples, controlled beam fixture and ready=false.
- Next: actual cached-frame/world-pose scheduling; shared target strategy/concurrency;
  FX pool drain; full-backend reaction/stiffness/cure/barrier integration with matching
  earned stats. Run focused timeline controls before deciding to lift the balance-rerun hold.


## Latest continuation: beam cleanup and full combat integration

Read `pe-beam-cleanup-combat-integration-2026-10-18.md` for the complete contract and limitations. Added `effect_cleanup.py`, `beam_combat.py`, and the source-combat hook. The uninterrupted beam releases at effect update 151/391; live visual particles do not delay controller return-1 cleanup. Outside-floor target cancellation releases at 55. Contacts occur in the later effect pass and deliver next combat update. Beam HP/barrier/stiffness now affect the full simulation, including slow gain, movement lock, equipped model radius, explicit Counter mapping and persistent player status state.

Validation: `PYTHONPATH=tools python -m pe_weapon_sim.validate_beam_combat` passed 67 focused checks. Artifact: `data/pe-beam-combat-validation-2026-10-18.json`. No gameplay, balance runners, benchmark sweeps, or historical output replacement occurred.

Still hold reruns. Explicit beam schedules, target XZ, scale and player source stats are required; static world coordinates do not establish moving contact rates. Remaining: owner chooser/target writes/scale/order, actual launch poses, orb cleanup, interruptions/deletion, full reaction gates and Counter helper mapping/cures/reset policy. Fractional legacy incoming damage is rejected in beam mode; supply integer source power profiles. This is validated component integration, not complete boss reconstruction.
