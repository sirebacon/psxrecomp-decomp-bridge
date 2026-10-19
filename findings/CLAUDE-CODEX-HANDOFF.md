# Claude / Codex simulation handoff

Last updated: October 19, 2026, by Claude.

## Start here

**Latest (Codex, Oct 18): user authorized a current-model rerun after Claude's work.**
The former rerun hold is superseded by that explicit request. Completed **6,144 fights**
outside the game with the latest ordinary-enemy options enabled. Read
`pe-current-model-balance-2026-10-18.md`; raw records, options, and SHA256 provenance are in
`data/pe-current-model-balance-2026-10-18.json`. Reproduce with
`PYTHONPATH=tools python -m pe_weapon_sim.run_current_model`.

- Full discovery: **284 tests passed**. Separate beam validation: **125 tests passed**.
- Eight frozen earned campaign seeds per group; D5/Disc2; four encounter types;
  six repetitions; early/late melee contact bounds. Recomputed source Aya stats and
  armor, replaying historical AT purchase counts. Enabled shared-cell identities,
  source power, distance choices, melee windows/reach, contact/effect actions, and
  incoming player status. No campaign reoptimization or gameplay interaction.
- Disc2 controlled_machine (P90): **99.48-100% wins**, **5.90-5.96 s** mean fight time.
  Controlled handgun (USP TU): 89.06-90.10%, 9.80-9.94 s; shotgun (M10B):
  88.54-90.10%, 11.21-11.26 s; rifle (MAG): 89.06-89.58%, 9.02 s;
  grenade policy (HK40 on six seeds, M8000 on two): 84.38-86.46%, 10.86-10.97 s.
  Policy labels describe frozen campaigns; do not present grenade policy as a pure
  HK40 benchmark. D5 and Disc2 rankings differ.
- **7,124 explicit-power hits / 9,123 fallback-damage hits** (43.85% source power).
  9,296/11,424 enemy appearances matched static declarations; 2,640 choice matches.
  1,760/4,933 reach-tested melee strikes missed. Status: 663 poison applications,
  119 stiffness-slow applications. Feature match counters overlap, not additive coverage.
- Controlled HP385 and ample reserves999; step90/windup10/recovery10 fallback;
  slot0 fallback power selection; overlapping choice guards use lowest slot.
  Source geometry is same-floor/facing/idle-pose, not continuous navigation.
  Full repeated boss AI/beam formations remain incomplete and are not enabled in
  this balance suite. Source maximum HP remains unverified against a clean save.
- Input fingerprint comparison found **no simulation source or consumed data changes**
  during the run. The only changed fingerprint was the beam-validation JSON rewritten
  by the independent validation command; it is an output, not a combat input.
- Best next payoff: resolve the remaining fallback power/action identities and inspect
  which encounters drive losses before proposing balance edits. These results measure
  current frozen loadouts under explicit scenarios, not final retail balance.


**Latest (Claude, Oct 19, step 5): class benchmark, exhaustive battles, balance recommendations.**
Read `pe-balance-recommendations-2026-10-19.md`. New in `compare_rules`:
- `--builds class`: equal-investment class guns (`run_benchmark.CLASS_GUNS`). Aya is the same
  seed's frozen group-C build, so only the gun differs.
- `--all-battles`: every logged battle once per build. Random battle sampling moved Disc2
  results by ±1–2 s.
- `--encounters ordinary|boss`.
- Per-group ordinary / boss table in reports; `resummarize(stem)` rebuilds a report from
  saved rows.
- Weapon-table proposals: `cfg:@G3A3.power+45,5.rof+1`, combinable as `exp:X|cfg:...`.

Other changes:
- New experiments `AAo_30..60` (`all_mode_ordinary_only`: no Attack All cut in boss battles).
- `secondary_test --proposal`.
- Tests: `test_compare_rules.py`. Full suite 311 + 5 OK.

Recommendations, not built into the mod:
- **R-A `AAo_40`:**
  - Disc2 ordinary P90 3.2 → 5.7 s (others 7.7–9.5); bosses unchanged.
  - `AAm_40` without the boss exemption drops P90 boss wins 0.73 → 0.49.
- **R-B G3A3 +45 power:** D5 rifle 34.7 → 21.7 s.
- **R-C M203 4 +20 power:** 28.1 → 22.5 s.
- **R-D:** switch-cost change is low priority.

Disc2 boss numbers remain an incomplete scenario and drive no recommendation. R-A has a
concrete mod spec:
- hook `pe_on_damage`;
- condition: Attack All (`turn & 0xC0 == 0xC0`), at least 2 live enemy slots, and no slot with
  status2 bit 0x40000;
- the boss bit is the same one the logger's `boss` label uses.

**Step 5b, boss identities** (`pe-boss-identity-multikind-2026-10-19.md`):
- Bosses 188 / 245 / 269 / 429 write several literal kinds (field 42: 2 then 4), so
  `literal_identities` skipped them.
- New opt-in: `MULTI_KIND` sentinel cell, `enemy_identity.multi_kind_identities`, and
  `compare_rules --multi-kind`.
- Same opt-in: silent actors (`enemy_choice.silent_identity`). Their flow has no command,
  effect or PM send: 269 0x041B and 273 0x0125.
- Disc2 boss fallback share 0.52 → **0.00**. The untimed share (0.60) is now the main boss
  gap.
- Untimed task-effect controllers:
  - 245: SeekingTrail.
  - 269: GroundSweep / OrbitTrailBurst / RisingSpray.
  - 256 131 / 132, 428, 429, 432: unnamed.
- All room overlays load at 0x8018EFE8.

**Step 5c, gauge guard** (`pe-calibration-atbguard-2026-10-19.md`):
- `Entity_ResolveDropTable` halves incoming damage while Aya's `atbGauge` is above 0 and no
  barrier is up. The main `source_combat` hit path never applied this.
- New opt-in `atb_guard`: halved unless Aya is mid-action. Flags `--atb-guard` on
  `calibrate_logged` and `compare_rules`.
- Corrected calibration reading: the per-hit damage overshoot was the real issue.
  - Day 1–4 ordinary per hit is now 11.8 vs 10.6 logged.
  - Total damage ratio 2.45 → 1.86.
  - Hit frequency remains 1.4–1.6× high.
- Use `--atb-guard --multi-kind` for new comparisons.

**Step 9, rebalance re-run** (`pe-balance-recommendations-2026-10-19.md`, last section; report `findings/reports/pe-weapon-rebalance-2026-10-19.html`):
- `compare_rules --calibrated --base vanilla` runs the three-way comparison.
- R-A is back to AAo_40 (AAo_30 overshoots on the calibrated model); R-B and R-C are confirmed.
- Vanilla's ÷5 elemental resist breaks the Day 5 M203 4.

**Step 8c, enemy coverage complete:**
- Shared identities resolved by HP (y_hp).
- --borrow covers 0x001E in rooms 217 / 226 (agreed plans from 16 rooms).
- Defense ≥ 200 / 0x0200 parts are kept as controllers (room 34's attacker 0x0307).
- No unresolved foe left in the log; fallback 0.00.
- Calibration v7: ordinary 1.05× (r 0.77), bosses 0.66× (r 0.82), Day 1 bosses 0.95×.

**Step 8b, room 273 and Liberate:**
- Counters no longer hit untargetable controllers: room 273 goes 239 → 1091 (logged 1264).
- Liberate is from source: 7 hits of power − full defense, matching rooms 273 / 432 exactly; room 432 goes 340 → 83 (logged 79).
- Bosses now 0.68× (r 0.82).
- The rest of the Disc2 boss gap is player behaviour (club turns, 245 / 256; few volleys, 188; 350 open).

**Step 8, enemy body-contact damage** (`pe-contact-damage-2026-10-19.md`):
- Source (Menu_MainUpdate):
  - flat contactDamage (script field 65) on hit-cylinder overlap;
  - 90-update window (strikes open it too), Barrier blocks it;
  - post-revive 0x800000 = 90 updates of immunity (now modelled as `hold`).
- `enemy_choice.unarmed_actor`: a shared identity's actor resolved by HP; unarmed actors don't
  strike (room 332's small 0x0015).
- The contact rate is log-measured per room (`logged_contact.py`), with strike-matching hurts and
  poison ticks excluded.
- Calibration `pe-calibration-logged-contact-v3`: ordinary 1.07× (r 0.76); Day 5 bosses 1.02×.
- Commit 1eee061 holds everything before this step. 358 tests OK.

**Step 7f, Energy Shot live check:**
- The user cast it in room 273: 572 damage, PE 1420/1420, level 33, defense 85.
- energy_shot_damage reproduces it exactly with base 219; save inputs give 566.
- Full defense and the integer level factor are confirmed.

**Step 7e, Aya's side closed:**
- Medic, Full Recover and Scan powers.
- Cure items (cure, or immunity when not afflicted).
- Literal source steals (opt-in `--steals`).
- `--logged-items` replay.
- `rules.VALIDATION` has rows for PE, items, revive and steals.
- Final calibration `pe-calibration-logged-aya-final-2026-10-19`: ordinary 1.04× (r 0.75);
  bosses 0.64× (Disc2 noisy).
- From here on, work is enemy-side: room 273, out-of-reach boss turns, 350 / 428 / 432,
  room 332, 0x001E.
- Use the full flag set for rebalance re-runs. 354 tests OK.

**Step 7d, Aya's side completed** (`pe-aya-pe-items-2026-10-19.md`, "completion pass"):
- Source:
  - Preraise / Revive (half HP, PE / 4);
  - Gene Heal (tick + drain);
  - Energy Shot formula (not in the log, unvalidated);
  - armor auto-medicine and auto-cure;
  - counter rank = identity low byte (opt-in `--identity-rank`).
- Labelled: confusion disables the melee dodge.
- `rules.VALIDATION`: four rows promoted. What's left as A / L on Aya's side is player behaviour
  only.
- Best calibration `pe-calibration-logged-best-rank-2026-10-19`: ordinary 1.04×, bosses 0.73×.
- 352 tests OK.

**Step 7c, logged casts, spell effects, controllers** (`pe-calibration-casts-2026-10-19.md`):
- Source: Haste sets 0x100 (defense term × 3/10); Barrier drains PE instead of HP; Detox; Slow
  (charge × 3/5); Confuse (3–5 skipped cycles).
- Calibration flags: `--logged-casts`, `--multi-kind`, `--boss-cap 400`, `--controllers`.
  - 10-HP boss cores in rooms 123 and 273 are untargetable; the other +1000000 values are phase
    offsets.
- Current best (all flags): ordinary 1.04× (r 0.75), bosses 0.84× (r 0.57), fallback 0.
  - Day 5 ordinary 1.06× and bosses 0.98×: that gap was the player's casts.
- Scripted boss HP from the per-slot hit log:
  - room 188 second phase 300 (script `Entity_SetField` 44 / 45);
  - parts removed unengaged dropped (room 269: 2635 → 1067 vs 960 logged);
  - controllers untargetable.
- Aya's dealt per turn matches the log in every group.
- Best run `pe-calibration-logged-best-2026-10-19`: ordinary 1.04× (r 0.75); bosses 0.67×
  (r 0.71).
  - Remaining boss gap: out-of-reach turns in 188 / 245 / 256 / 350 (1.2–2.4 rounds per turn;
    arena movement not modelled) and 273 (0x0325 not ported).
- 349 tests OK.

**Step 7b, PE powers pause enemies** (user observation): PE casts are a paused advance (no
strikes, no regen; `pe_pause_s`). Items stay committed. Current best calibration is
`--serial --pe --evade-melee-early 0.6 --atb-guard --logged-charge --reaction 30 --reaction-paused`
(`pe-calibration-logged-serial-pe-pause-2026-10-19`):
- ordinary 0.93× (Day 2–4 1.05, Disc2 1.00, Day 5 0.64);
- bosses 0.83× (Day 5 0.56, Disc2 0.76).

Next up is the Day 5 gap. 343 tests OK.

**Step 7, Aya's side** (`pe-aya-pe-items-2026-10-19.md`):
- PE regen, spells and items from source; mod half-bar rules; opt-in `pe` and `--pe`.
- The calibration now includes PE battles: ordinary 1.07×, bosses 0.93×.
- `player_max_hp` for HP-share statuses.
- Ordinary enemies: early melee dodge 0.6 (--evade-melee-early, user-confirmed behaviour) gives ordinary 0.93× and Day 2–4 1.07×. 0x0100 = template-rank silent parts. Open: 0x001E (217 / 226), Day 1 (small sample).

**Step 6c:**
- Beacons and pulses for bosses 5, 23, 89 and 123.
- Room 86 phase pick (`phase_powers`); `melee_window` accepts repeated declarations with
  identical timing.
- 350 investigated: geometry needs runtime configuration. Details in
  `pe-effect-ports-2026-10-19.md` (second pass).

**Step 6b, effect ports** (`pe-effect-ports-2026-10-19.md`):
- Timelines from decompiled source for:
  - 0x001A (melee per species, OrbitFlare, LineBurst);
  - boss 188 (PhasedSpark; WaveSpark is visual, so slot 4 is harmless);
  - boss 269 (GroundSweep, RisingSpray, grab);
  - boss 245 (Seeking / Scatter trails);
  - 0x000C (MotionParticles eruption strip).
- Remaining untimed: 350, 5, 23, 89, 123, 273, 348; 428 / 429 / 432 have no symbols.

**Step 6, serial rule and room 256 ports** (`pe-calibration-serial-2026-10-19.md`).
- Game flag 0x100 is set during Aya's committed action:
  - enemy charge and status (`Battle_UpdateEnemy`) and enemy script nodes freeze, so no new
    attacks start;
  - attacks already animating still land (the user's "sitting duck");
  - Aya's gauge doesn't fill.
- Opt-in `serial_action` / `--serial`; `reaction_paused`; `player_evade` no longer applies
  while committed.
- New set `logged_player_serial` (reaction 30 paused, no evasion): ordinary damage 1.15×,
  time per turn matched. It replaces the fitted 0.55 evasion.
- `room_m256.py` ports the 256 boss trail (132, slot 3) and the swing + scatter drops
  (131 + class 76, slot 4).
  - `task_actions` now looks behind the swing class for a RoomM256 program.
  - The trail's contact is sensitive to its turn scale (810, source range 800–820 when facing
    Aya).
- Species picks also take the picked actor's melee window: 0x1A slot 1 is now window-timed.

**Step 5d, charge fallback and player evasion.**
- `logged_charge.py`: the play log's runtime charge step, used as a fallback for 29
  identities that otherwise got the placeholder 90. The 105 catalogued identities match the
  log exactly. Opt-in `logged_charge` / `--logged-charge`.
- `player_evade`: player behaviour, fitted value 0.55. `compare_rules` assumption set
  `logged_player` = reaction 75 + evade 0.55.
- Full calibration, ordinary battles: damage 15.6 logged vs 16.4 simulated (1.05×);
  8.20 vs 8.22 s per turn.
- Recommended for absolute numbers:
  `--atb-guard --logged-charge --multi-kind --assumptions logged_player,...`
- Day 5 bosses remain near zero damage (room 332 0x0015 power lead).

**Claude, Oct 19, step 4: baseline balance on the improved model + first rebalance tests.**
Read `pe-baseline-current-rules-2026-10-19.md` (CURRENT rules; 8 seeds × 6 campaign battles
per build/stage; sets default / late / human_reaction / far_player). Comparisons now use the
source level table's max HP (level 33 = 621) instead of the HP-bugged 385. Disc2 ordinary
fallback share is 5–8% (was 60%), helped by:
- per-room scale cells (`enemy_power.room_v80_cells`: room 210 uses N11 = V80);
- labelled species picks for 0x1A / 0x1D (`called_slots` variants).

Findings:
- D5 is mostly a G23 comparison; every build wins.
- **Disc2 ordinary: the P90 with Attack All dominates** (1.8 s, 0 damage vs MAG 8.2 s), stable
  across assumption sets.
- Disc2 bosses remain an incomplete scenario: 188 / 245 / 429 unresolved; 256 / 428 / 432 / 350
  effects untimed.
- S1 shotgun proximity: no measurable effect on campaign battles. D5 "shotgun" builds hold a
  G23; Disc2 M10B −0.04..−0.57 s, every CI spans 0.

New experiments `AA_50..80` (Attack All per-bullet power). `rules.SOURCE_BACKEND_KEYS` lists
the keys the source backend honours, and `compare_rules` refuses proposals using others.

**Claude, Oct 18, accuracy plan step 3: play-log calibration.** Read
`pe-calibration-logged-2026-10-18.md`. The logger's `secs` is seconds/10 (use frames/59.9).
The logged run had the old Counter boost ×5 (replay with `--log-era`). With that and the
`walk` policy, turns per battle match (2.35 vs 2.13, r 0.66). Incoming damage per hit matches,
but frequency is about 2× high: the remaining placeholders plus player spacing. Also new:
- More effect ports: homing flash (0x17 rooms 162/163), twelve elements (0x17 rooms
  167–173/186), paired glow (0x11), three particles.
- A `noeffect` plan kind: slot 3+ with no effect object can't damage (e.g. 0x0A slot 3).
- An option for timing/power slot realignment in `called_slots` mode.
- An opt-in `reaction_updates` player policy.
- Comparison assumption sets `human_reaction` and `far_player`.
Relative comparisons are supported; absolute survival is not yet.

**Claude, Oct 18, accuracy plan step 2: effect attacks get source timelines.** Read
`pe-effect-timelines-2026-10-18.md`. `room_handlers.py` resolves effect id → room overlay
program; `room_modules.py` ports the FieldFx object engine plus falling burst, three particles,
timed spawn, burst orb, sound burst, spark ring and burst sparks; `homing_throw.py` ports the
thrown projectile and ground eruption. Untimed strikes 69% → 20% (early audit). Remaining
untimed: 429 0x26 (no symbols), room 350 hand sparks, 0x17, bosses 256/432/428/269.
`compare_rules.py` is the comparison workflow (matched seeds, campaign battles, assumption
sets incl. `geometry_upper`). 308 tests. Next: the remaining effects, player movement during
effects, then calibration against the 175 logged battles.

**Claude, Oct 18, accuracy plan step 1: fallback-hit audit + called slots.** Read
`pe-fallback-hit-audit-2026-10-18.md`. Audit replay reproduces the published run exactly
(9,123/16,247 fallback). The cause was the slot-0 default on enemies that never call slot 0
(146 0x13 alone 42.7%). Opt-in `source_options['called_slots']` uses each identity's called
slots with per-slot timing+power, plus the template critical chance 0 (retail EXE
g_EnemyCombatantInitial). Fallback 56.15% → 11.12% (ordinary 8.2%, bosses 19.9%), and what
remains is labelled. **New largest gap: 69% of executed strikes use the untimed 10/10
placeholder** (slot 3+ effects; PM programs 0–84 aren't decompiled). Next: rebalance
comparison workflow with sensitivity to that placeholder, then the player-loop and
progression validation.
Reproduce: `python -m pe_weapon_sim.audit_fallback_hits --bound both [--extra ...]`;
`python -m unittest pe_weapon_sim.tests.test_called_slots`.

**Claude, Oct 18, seventh pass: melee reach from hit-sphere geometry.** Read
`pe-melee-reach-2026-10-18.md`. `enemy_reach.py` ports the model layout, animation decode
and bone hierarchy; validated read-only against live Eve sphere entries (11/12 samples within
7 units, YXZ). Reach for 187/198 melee actions (`data/pe-enemy-reach-2026-10-18.json`);
script attack distances sit just inside reach (330/407, 350/373, 700/714, 300/402), with
exceptions the farming enemy (630 vs 576) and 0x17 slot 1 (1000 vs 633). Opt-in
`source_options['melee_reach']` (already used by Codex's rerun above). 284 tests.

**Latest (Claude, Oct 18, sixth pass): melee contact windows — correction.** Read
`pe-melee-contact-window-2026-10-18.md`. A slot 0-2 hit needs 3D sphere contact with the
record's contact ids while the record is in state 1 (Entity_CheckActionIdMatch); the category
1/3 frame crossing *closes* that window (state 3) and is not the hit. `decode_enemy_actions`
timing = window close + 1 and assumes a hit always lands. `melee_window.py` gives windows for
all 198 melee actions (cat 0/2/3); opt-in `source_options['melee_window']`; enemy_choice uses
it. Ordinary timing 322 → 348/383. Next: reach (sphere geometry). 275 tests. Hold respected.

**Latest (Claude, Oct 18, fifth pass): enemy decisions (distance-gated attack choice).** Read
`pe-enemy-choice-2026-10-18.md`. `enemy_choice.py` derives each attack call's distance guard
from the room scripts (Entity_GetDistanceComponents comparisons, state dispatch, diamonds);
`GatedEnemy` picks the slot by current distance at full charge, else holds 30-59 updates.
Opt-in `source_options['enemy_choice']`. 83/383 ordinary appearances gated (65 multi-slot,
65 with a dead band); 60 have at least one timed slot, none all. 267 tests pass. Hold respected.

**Latest (Claude, Oct 18, fourth pass): Aya's incoming status.** Read
`pe-player-status-2026-10-18.md`. `player_status.py` ports Battle_ApplyEnemyAttack and Aya's
Entity_UpdateTimers (poison / darkness range 200 / stiffness / 0x1000 defense-down / HP
fractions); enemy effect_level/duration from fields 0x43/0x44; status steps from the level
table. Opt-in `source_options['player_status']` (non-beam). 257 tests pass. Hold respected.

**Latest (Claude, Oct 18, third pass): effect-driven slot-3 actions.** Read
`pe-effect-driven-actions-2026-10-18.md`. Slot 3+ actions complete when FieldFx_UpdateTasks
releases the owner; effects 115/122/136 are decompiled room-library controllers (orbit flare,
dropped flare, line burst) with identical task scripts per room. `room_effects.py` ports the
task engine + controllers exactly (scenario geometry); `effect_actions.py` catalogs 28 actions
and `EffectEnemy`; opt-in `source_options['effect_actions']`. Ordinary timing coverage 262 →
322/383, all three 237 → 297. 247 tests pass. Hold respected.

**Latest (Claude, Oct 18, second pass): ordinary-enemy coverage.** Read
`pe-ordinary-enemy-coverage-2026-10-18.md`. Scaled-rank identity idiom (10 scripts incl. the
farming-room enemy, 78/383 logged appearances); live read-only V80 = N10 = 65536 →
`enemy_identity.FIRST_RUN_SHARED_CELLS`; `local_power.py` resolves locals-held power per
identity-keyed path (taint tracking); `contact_timing.py` bounds category-2 hits (completion
proven, hit inside own clips, early/late). Opt-in `source_options` keys `shared_cells`,
`contact_timing`. Ordinary all-three coverage 78 → 237 of 383. 237 tests pass. Hold respected.

**Latest (Claude, Oct 18): source-earned defense joined.** Read
`pe-aya-source-defense-2026-10-18.md`. One read-only live probe (port 4378, Eve fight, no
input/writes/loads) verified stat20 362, armor 66/49/30, offense 350, stat22 79 at level 33.
Correction: Active Time uses growth kind 5, so stat22 lags level (79, not the linear 82).
Opt-in `source_level_stats=True` in economy rulesets; source_combat reads player armor from
the aya dict (profile override kept). New source_stats.py, live_defense_probe.py,
test_source_stats.py; 224 tests pass. Hold on balance reruns still respected.

**Current user instruction: hold balance reruns until projectile geometry and linked beam
handling are coherent. Continue offline extraction/implementation and focused checks.**
Read `pe-shared-combat-priorities-2026-10-18.md` first, then
`pe-boss-beam-choice-2026-10-18.md`, then
`pe-beam-launch-timing-2026-10-18.md`, then
`pe-beam-scheduling-interruption-2026-10-18.md`, then
`pe-beam-cleanup-combat-integration-2026-10-18.md`, then
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


## Latest continuation: owner scheduling, targets and interruption

Read `pe-beam-scheduling-interruption-2026-10-18.md`. Fresh raw extraction is `data/pe-beam-scheduling-extract-2026-10-18.json`; new bounded components are `beam_scheduling.py` with tests in `test_beam_scheduling.py`. Target projection and both formation layouts are decoded, including the second-target X-only spacing bug and third-target comparison against both earlier targets. Parent entry+5940 selects cell27=0/2, not short mode1. Helpers sample target cells once, retry action3, wait held counter zero, and actor6 has an extra selected-record-state wait and explicit update yield.

PM handler85 was resolved from the existing snapshot to prove its stop callback. Actor interruption can mark closure and still allow a callback that update; later PM states4→5→0 prevent more callbacks. Explicit Pm_Stop checks ownership and clears the PM slot. Neither stop path automatically releases the actor held bits/action state/pending contact as normal opcode0 cleanup does. These new source lifecycle components are staged: full combat still requires explicit launch schedules and does not guess helper state trajectories.

Validation now passes86 focused checks, including11 new scheduling checks and decoded-script comparisons. Run `PYTHONPATH=tools python -m pe_weapon_sim.validate_beam_combat`. No game, encounter benchmark, balance sweep, or historical balance output replacement occurred.

Continue hold on reruns. Next: navigation action9/callback at actor3 root+20744, parent animation10/11 waits, helper creation/update ordering, parent/helper HP/status/death paths. Use those to place source-derived target/trigger events on actual combat updates before wiring interruption automatically. Moving-player geometry, actual launch pose, orb cleanup and full reaction/Counter/cure behavior remain outstanding. Do not use static branch counts as attack probabilities.


## Latest continuation: navigation, animation waits and exact conditional launch timing

Read `pe-beam-launch-timing-2026-10-18.md`. New artifact: `data/pe-beam-launch-timing-2026-10-18.json`. New code: beam_launch_timing.py plus isolated original PM/ratan2/animation-wait instruction oracles. The normal formation tail now generates source-derived beam schedules through full engine source_options.beam_formation; manual linked_beams remains available. Entry update, targets, pose/retail yaw, scale, initialized idle helpers and verified free PM capacity remain explicit. No autonomous chooser or repeating volley is claimed.

Corrections to earlier next-step entries: Entity_CallAction is an immediate polygon check (9 vertices at root+20744), not a navigation wait. Actor7 creates4/5/6 then3 after the same insertion anchor, proving callback order3/6/5/4. Accepted formation triggers are written together before the parent animation wait; idle helpers allocate PM130 in that same update. PM130 runs in the PRIMARY pass after actor rendering, not the earlier secondary pass. Its mode1 joint query sees that update's rebuilt joints on the normal path. Source FieldActor.action at0x0F means last-frame index; animation wait's zero shortcut means a one-frame clip.

If accepted triggers are written at T: PM starts at T, controller at T+46, earliest contact at T+58, earliest delivery at T+59. Parent waits42+45 advances and finishes at T+87. Long effect releases at T+390; helpers4/5 clear trigger at T+391 and helper6 at T+392. Actor/action/FX replay confirms helper command completion waits for effect release, not merely animation wrap. Polygon acceptance before integer conversion can still lead to helper-floor cancellation at T+54; covered by a concrete boundary fixture.

Validation:102 focused tests pass, including16 timing checks;1005 ratan cases match original instructions;54 animation-wait predicate/first-entry cases match the original opcode; both PM runners and pause gates are checked with original bounded instructions. Full engine fixture T=5 delivers at64 in helper6/5/4 order, then cleans up at395, ammo imbalance0. No game/emulator, live scan, encounter benchmark or balance rerun occurred. Run PYTHONPATH=tools python -m pe_weapon_sim.extract_beam_launch_timing, then -m pe_weapon_sim.validate_beam_combat.

Hold on balance reruns remains active. Next: derive formation entry T from outer chooser/charge/region gates, then connect actual moving pose/launch joints and helper interruptions/busy state/PM exhaustion. Coincident turn-target flag20 behavior is explicitly rejected until full node replay. Full source-earned stats/scales, orb cleanup, complete reaction/Counter targeting, cures and encounter reset behavior remain outstanding. Conditional timing is now implemented; complete encounter timing is not yet claimed.


## Latest continuation: when the boss selects beams, joined to launch timing

Read `pe-boss-beam-choice-2026-10-18.md`; artifact `data/pe-boss-beam-choice-2026-10-18.json`. Added boss_beam_choice.py and full-engine opt-in source_options.boss_beam_choice. It derives an admitted initialized chooser decision, turns, region/layout targets and beam launch timing without an explicit formation timestamp. This is one static-world volley, not an autonomous repeating boss AI. Movement boundaries are surfaced, not assigned a guessed duration.

After the earlier outer gate admits a decision: distance<1300 selects melee;1300..1700 orb;1700<distance<=2000 draws explicit[0,3),0 orb and1/2 beam-capable;distance>2000 is beam-capable without that draw. Beams also require all three trigger cells0 and Aya stiffness pair!=2; otherwise orb. Distance is the absolute fixed16 XYZ sum (Manhattan). The separate region2 layout RNG is not the same draw. The main gate can instead wait/move, based on local22 event/movement bits, local3, completed-beam local44, path local1 and sticky ready latch local35. The report records exact priority and boundaries.

Actual initial child order is position+2080, movement+17792, chooser+3388, death+20816, region+3252, charge poll+3156. The chooser precedes the charge poll, both before Battle_UpdateEnemy. A charge crossing in battle updateU ordinarily reaches a charge-based decision in actor updateU+2; prior ready/event gates can bypass that latency. Sticky ready latch is cleared by the post-action path. Source slow is modeled; poisoned/incapacitated/dead actor replay is rejected pending fuller scheduler support.

Conditional fixture: initialized main resume1, charge8990/step70/latch0, boss(0,-1873,-6000), Aya(3000,-1873,-6000), yaw0, free/ready helpers. Main admits decision3, facing completes10, region0 formation triggers11, earliest contact69/delivery70, release401. Full engine uses consistent chooser/contact positions; this stationary Aya receives no beam damage because generated targets are elsewhere. All three effects clean up and ammo imbalance0. No direct hit chance is inferred from target selection.

Validation now114 focused tests pass, including12 new chooser checks:360 attack-boundary cases and500 outer-gate snapshots compared against fresh bytecode, child order, readiness/slow/latch behavior, movement boundary, separate RNG and full integration. Run PYTHONPATH=tools python -m pe_weapon_sim.extract_boss_beam_choice, then -m pe_weapon_sim.validate_beam_combat. No game, emulator, live scan, encounter benchmark or balance rerun occurred.

Continue holding balance reruns. Next: replay movement/position node outcomes and moving/static status changes through turns; post-action state and repeated choices; actual launch pose and earned inputs; helper interrupts/death/busy/PM failure paths. The one-volley overlay must not double-count the same boss's generic enemy attacks. Orb cleanup, full reactions/Counter targeting, cures and resets remain unresolved. Earlier entries saying chooser selection is entirely unknown are superseded by these bounded decoded gates, not by a claim of full encounter reconstruction.


## Latest continuation: prioritize broad combat payoff over further boss-only work

The user asked for best bang for the buck. Prioritize shared mechanics/data and frequent ordinary enemies. This pass added enemy_power.py and incoming_damage.py, improved source_combat integration and fixed a live-barrier beam-hit crash. Read `pe-shared-combat-priorities-2026-10-18.md`. Audit artifact: `data/pe-shared-combat-coverage-2026-10-18.json`.

Conservative extraction resolves381/393 decoded attack declarations (365 scale expressions,16 literals), yielding284 action-slot keys over141 map/enemy identities. In the saved campaign log, any supported slot covers275/387 ordinary-enemy appearances and319/457 total appearances. This is static record coverage, NOT action selection or complete combat coverage. No new balance run was done. Unknown/ambiguous producers and alternate declarations are rejected; real shared scales and selected action slots remain explicit.

Enemy profiles now accept source_action_slot/source_shared_cells to resolve power/effect/chance. Existing explicit overrides win; missing scales for known computed power raise. Timing/power slot mismatch is rejected. power_catalog_matches/power_catalog_foes plus explicit_power_hits/legacy_damage_hits make actual fallback use visible. incoming_status_unmodeled exposes unresolved nonzero effects. Ordinary map5/0x0201 slot0 scale1.0 yields power15 instead of the old level5 fallback8 in a controlled regression; this is not a balance result.

The shared HP/barrier reducer preserves source integer defense/crit/PE/armor selection and reaction requests. Beam and powered mixed normal incoming hits reuse it. Removed an accidentally duplicated generic barrier branch inside the beam loop which referenced an unassigned enemy variable and could crash on barrier beam delivery. Full-engine regression now gives one beam hit, HP unchanged, energy100000->99520, no duplicate/generic event. Mixed normal barrier and ordinary-enemy source-power regressions pass. Fractional legacy hits and old aggregate guard multipliers are rejected in source player/beam-state encounters instead of silently mixed into integer state.

Validation:125 focused checks pass, including11 new broad-combat tests and all365 extracted chains checked at four scales against decoded arithmetic. Run PYTHONPATH=tools python -m pe_weapon_sim.audit_shared_combat, then -m pe_weapon_sim.validate_beam_combat. No game/emulator/live scan, encounter benchmark, balance sweep or historical balance output replacement occurred. Balance hold remains active.

Next highest payoff: ordinary-enemy action choice/delivery timing for frequent logged identities; source-earned Aya defense/armor/PE/resistance joins; generic incoming status/reaction/Counter/cure/reset handling. Further hospital choreography is lower priority. Existing generic timing/hit chance and ordinary status phase are still scenario assumptions; do not interpret the new catalog as a completed enemy AI. Beam chooser and normal-path timing work remains available for later interrupted/moving encounter integration.
