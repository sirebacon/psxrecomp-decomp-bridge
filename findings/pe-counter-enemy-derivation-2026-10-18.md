# Counterattacks and enemy behavior from decomp — 2026-10-18

Entirely offline: read C, extracted metadata from the existing PST, implemented and tested
state transitions, then reran frozen-loadout combat. No game launch, input, live read or
save loading. Historical defaults/results are preserved.

## Counter source and implementation

Paths below are relative to Parasite Eve Project/parasite-eve-decomp/src/main.

- `entity/combat.c:88`: Entity_ResolveDropTable records a pending attacker after processing
  an eligible hit/reaction on a surviving Aya. The global stores one attacker; later hits
  replace it. Positive HP loss is not itself required by that assignment.
- `battle/encounter.c:429`: the counter roll is attempted at an idle animation boundary,
  with assets ready, no action queue, battle phase0, the Counter effect set, and a pending
  attacker. The pending pointer is cleared after the attempt. This is not an extra volley
  immediately after every successful enemy damage roll.
- `battle/context.c:576`: Battle_RollEnemySpawn rejects dead attackers and branches on the
  signed8-bit player-rank minus enemy-rank difference. It compares an integer rand()%100
  roll times10/50/100 against HP-level or3*HP-level. `aya/stats.c:184` returns the value
  called g_AyaStatAgility; the current mod explains it is actually stats.levels[0], HP-level.
- `battle/turn.c:167`: Battle_SetupEntityTarget queues one counter command against that
  attacker, dispatches it and marks action commitment. It does not call FinishAction or
  empty the gauge. Ordinary/Burst counters queue RoF slots; Random queues one slot and
  Attack All one repeated-shot target slot. Commands2/3 does not multiply a counter.

`source_enemy.counter_probability` counts successful integer outcomes, rather than using
the old continuous approximation. At HP-level210, probabilities for rank differences
positive/zero/-1/below-1 are21%/13%/7%/5%. These include rounding at integer thresholds.
The current runtime mod disables its old Counter boost; CURRENT counter_mult remains1.

BattleSession now supports counter=True attacks that preserve gauge and do not wait for
a full bar. Gauge continues refilling during their animation; ammo and reloads are real.
The combat adapter retains one pending attacker and defers execution while a player
action/menu/switch is active. It checks attacker life and optional counter_eligible, rolls
once, then uses the normal timed damage callback. An idle hook allows a counter during
refill without re-entering an already executing queue. Random counter construction does
not draw random targets or multiply its ammo use.

Timing boundary: idle settling defaults to21 updates from the extracted20-frame base
reaction clip. The adapter deliberately prioritizes settling a pending Counter before
its next ordinary attack. Exact hit-reaction save/restore of an interrupted gun pose,
holding flags and player input priority are not fully emulated. That default and enemy
eligibility are scenario inputs, not claimed retail-perfect interrupt timing.

The model accepts counter_hp_level/player_rank overrides or aya.hp_level/aya.rank. If
absent, HP-level defaults to level*10 and rank to level. The balance rerun explicitly uses
level*10; it does not recreate the user's HP bug. Enemy rank falls back to the encounter
model's inferred level when an explicit rank is missing. This uncertainty matters to Counter.

## Common enemy mechanics versus script policy

`battle/turn.c:930` Battle_UpdateEnemy supplies shared mechanics:

- Charge at core+0x0C is a u16 gauge, not enemy life; life is core+0x10.
- Unpaused charge grows by chargeStep at+0x8E. Slow subtracts floor(step*2/5). Overshoot
  is narrowed to16bits, then capped at9000 on the following update. Actor flag0x1000
  resets a full gauge to0.
- Stiff/confusion-style cycle bits and Tranq bits decrement when charge is0. They are
  gauge-cycle counts, not a fixed number of enemy attacks skipped.
- Poison ticks its5-bit counter on every eligible battle update and damages on the31st,
  then resets. It is not accumulated only when the enemy happens to attack.

`source_enemy.EnemyClock` implements this ordering and gates. Source-backed status weapon
hits feed its flags. CURRENT poison_pct is applied once, with integer truncation, when
initializing periodic damage; periodic_damage_is_current avoids double scaling already
modified snapshot values. A regression test caught the missing modifier in the first
development run; the final balance artifact was regenerated after that correction.

Action selection is not encoded solely in this shared function. Enemy room/entity scripts
write chargeStep and request animation-event records. `battle/context.c:15,59` initializes
those descriptors; Entity_TriggerAnimEvent uses entry/exit modes, fixed-point speeds and
hit-frame crossings. `entity/frame_update.c:577` resumes waiting script nodes. The common
charge gauge reaching9000 is not itself proof that every enemy must attack immediately.

`ScriptedEnemy` therefore supplies an explicitly assumed policy on top of the verified
clock: consume full charge, use supplied windup/strike/recovery update counts, then repeat.
Source_behavior_rules() enables this charge-aware scenario; source_combat_rules() retains
the earlier random-period enemy scenario for reproduction. Optional enemy_profiles by
target index and enemy_defaults provide actual extracted values where available.

Enemy action damage is also available as a source component: Entity_ResolveDropTable
subtracts floor(stat20/5) and an armor parameter chosen by selected action-record slot
(coreFlags>>21 &7), NOT by the descriptor's category byte. It then applies critical,
guard and effectType10 integer reductions. The adapter uses this when profile power is
provided. Missing power/defense/armor data retain the old explicit level-based damage
fallback; spatial hit chance and distance sampling remain assumptions.

## Offline snapshot evidence

`extract_enemy_state.py` read the existing isolated Disc2slot9 PST and saved
`data/pe-enemy-state-extract-2026-10-18.json`, including its SHA256. Aya rank is33 but stored
HP-level is320. One Eve controller has chargeStep120, power177, critical chance40 and
selected action slot5; three linked parts have chargeStep0. This does not establish a
universal120-step attack rate. These boss/helper records are not substituted for the
normal enemies in the balance suite.

## Balance rerun

`run_behavior_balance.py` rebenchmarked8 frozen campaign seeds each for C, G, D, and the
handgun/shotgun/machine/rifle/grenade controlled groups at D5 and Disc2. It reconstructed
the exact saved weapon id, bonuses and effect codes from cfg_sig and checked magazines.
It ran6 matched fights in each of4 encounter profiles under charge-step60/90/120,
windup10/recovery10 script-policy sensitivities. HP385 and999 reserve rounds per pool
are controlled budgets. Where Quickdraw was present, a paired equal-slot intervention
replaced it with Counter; no free extra effect slot was added.

Final artifact:12,816 fights,150 eligible paired seed-loadout replacements. Every result
passed ammo conservation. Original campaign JSON is hashed in the metadata. Raw output:
`data/pe-behavior-balance-2026-10-18.json`; report `pe-behavior-balance-2026-10-18.md`.
The first poison-unadjusted development output was overwritten by the corrected rerun.

Within these scenarios, controlled_machine has the lowest Disc2 mean loss-penalized score
at all3 charge rates. Replacing Quickdraw with Counter worsens the pooled mean score at
all3 rates (deltas+4.123/+6.172/+6.784), with pooled win changes-0.017/-0.062/-0.074.
These are conditional frozen-loadout findings, not evidence that Counter is universally
bad, P90 universally wins, or the former whole-policy rankings remain correct. Scores
combine time and losses; short defeats are not successful clear times.

The old campaign decisions were made with the historical economy surrogate. This pass
does not silently rerun those decisions with that uncalibrated scorer. D denotes its
earned primary here, not a newly optimized within-fight secondary policy. Full progression
reoptimization needs a surrogate calibrated to this event backend and enemy-specific AI data.

## Validation and reproduction

9 new tests; full suite108 passing. Tests cover discrete Counter probabilities, one-command
counter queues, no random draws for Random counters, preserved gauge/ammo, refill-time
counter execution, enemy charge overshoot/hold reset, status cycles,31-update poison,
integer damage and once-only CURRENT poison scaling.

With PYTHONPATH=tools:

    python -m pe_weapon_sim.extract_enemy_state findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst --out findings/data/pe-enemy-state-extract-2026-10-18.json
    python -m unittest discover -s tools/pe_weapon_sim/tests -q
    python -m pe_weapon_sim.run_behavior_balance --seeds 8 --fights 6

Next source work: extract room-script action policies and per-enemy charge/descriptor data;
reconstruct hit-reaction interruption/restoration, body contact and exact movement/geometry;
then calibrate the economy scorer before new end-to-end progression-policy comparisons.
