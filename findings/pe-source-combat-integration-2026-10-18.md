# Source backend combat integration and Attack All audit — 2026-10-18

Entirely offline. No emulator connection, controller input, save loading, or live scan.
Historical reports and default engine behavior remain reproducible.

## Combat integration

`engine.fight` now dispatches to `source_combat.run` when the rules carry
combat_backend='source'. Create that profile with
`decomp_animation.source_combat_rules(CURRENT or VANILLA)`. The older source_rules()
profile remains the aggregate animation experiment; it is not this combat backend.

The adapter shares the existing engine's damage, range/graze/critical, elemental,
Cyanide/Acid/Tranq, proximity and rocket-splash calculations. Source shot events consume
ammo immediately, and hit callbacks apply damage at the hit trigger. Target death is
visible to subsequent queue steps. This replaces turn-start aggregate damage for this
backend. Encounter/script thresholds stop the action when achieved, not at animation end.

BattleSession gained update and stop hooks. The adapter runs the inherited enemy action
periods, movement, damage rolls, poison and stop effects during player refill, shooting,
reload and switch execution. Menu updates pause the modeled enemy clock. Optional finite
Aya HP stops play on defeat; the encounter horizon can stop a queue or pending switch.
Source slow-gauge arithmetic is applied using the old armor SlowAT assumption.

Optional source_options supports multiple weapon configs and a weapon_policy callback.
That callback receives equipped weapon, gauge, turn count, enemy states, loaded magazines
and reserve pools. Legal switch turns then incur CURRENT/retail gauge costs, menu time,
supplied stream waits and the extracted switch clip, all with carried ammo and gauge.
The hit resolver uses the active weapon's power, range, effects and RoF after switching.

Results retain the standard Stats fields for the encounter benchmark suite, plus
ammo_balance (must be zero) and a private _source_state for continuation. Trace mode adds
_source_events. `economy/evaluation.py` now carries loaded ammo, reserve pools, equipped gun,
gauge and remaining HP across linked endurance fights and excludes private dictionaries
from numeric totals. Historical aggregate fights continue through their original path.

Example:

    profile = source_combat_rules(CURRENT)
    result = engine.fight(profile, primary_cfg, aya, foes, distance_profile, rng,
        source_options={
            'hp': 300, 'reserve_ammo': {0: 120},
            'weapons': {'rifle': rifle_cfg},
            'weapon_policy': choose_owned_weapon,
            'menu_updates': 6, 'stream_updates': 20, 'trace': True})

## Attack All counter: source and original executable agree

The earlier concern was not just a naming artifact in the decomp. The relevant path is:

1. `battle/attack.c:158`: mode0xC0 repeats within the same queue slot while remaining!=1.
   Each repeat decrements remaining, then finalizes another shot.
2. `battle/attack.c:240`: empty ammo during repetition calls CommitAmmoAndUpdate. A
   positive transfer changes actionMode to12 and returns without advancing that target slot.
3. `battle/commands.c:388`: the helper synchronizes ammo, transfers a bounded amount from
   reserves, and rebuilds the action from the gun's modifiers. RoF remains the gun's RoF.
4. `battle/player_turn.c:87`: reload mode12 waits for the previous-frame end boundary,
   selects a fresh aiming animation, and does not restore the pre-reload remaining count.
5. `battle/attack.c:133`: aiming's ready path assigns remaining=action.turnWord.actions
   before finalizing the next shot. That resets the per-target count to full RoF.

`audit_attack_all.py` additionally read the original US PS-X EXE backup, not the patched
runtime or a live process. It verified14 exact instruction signatures. The key ones are:

- 0x80023288/0x80023290 load Combatant.action then BattleAction.turnWord.
- 0x80023294 jumps to0x800235A8, with delay-slot ANDI15 at0x80023298.
- 0x800235A8 stores the low4-bit count to g_BattleRemainingActions, then calls FinalizeAttackResult.
- 0x800235BC calls CommitAmmoAndUpdate in the repeated-shot reload path; nonzero transfer
  calls Entity_SetActionMode with argument12 at0x800235D4/0x800235D8.
- 0x80022184/0x8002218C check reload's previous-frame boundary; 0x800221EC/0x800221F0
  select the target-angle aiming mode and call Entity_SetActionMode again.

Executable SHA256, actual/expected words and addresses are recorded in
`data/pe-attack-all-retail-audit-2026-10-18.json`. This is instruction-level static evidence,
not a claim that an entire retail battle was emulated or measured.

A regression case with one durable target, handgun RoF5, capacity5, initially loaded2
and reserve5 fires7 total rounds: two before reload plus a fresh five after reload. Both
the player-state model and integrated combat reproduce this with exact ammo conservation.
In an actual modeled fight, a target dying earlier stops/skips repetitions. Keep the reset;
do not replace it with a presumed five-shot cap. Very short magazines may keep resetting
until reserves run out, so target HP and reserve limits matter to any balance conclusion.

## Validation

Full suite:99 tests passing (9 additional combat-integration tests). Tests cover timed
lethal hits and queue termination, finite reloads and conservation, Attack All7-shot reset,
HP defeat, horizon stops, switching damage/config state, special modes, encounter-suite
integration, endurance resource carry, and preventing a switch committing after timeout.

`run_source_combat.py` completed944 benchmark calls: 7 firearm classes x4 firing modes
x4 encounter profiles x8 seeds, plus 3 switching policies x2 stream waits x8 seeds.
Endurance calls contain3 linked segments, making1392 underlying fight invocations.
All results passed ammo conservation. Raw results are
`data/pe-source-combat-2026-10-18.json`; report is `pe-source-combat-validation-2026-10-18.md`.

The controlled equipment is synthetic (power100/range1500/magazine5/RoF3), not an earned
campaign loadout. HP300 and reserve budgets are explicit. Several encounters have poor
survival under the inherited enemy model: reported mean times include defeats and timeouts,
and must be read with win fractions. No new campaign ranking or recommended switch policy
is established by these checks.

With PYTHONPATH=tools:

    python -m unittest discover -s tools/pe_weapon_sim/tests -q
    python -m pe_weapon_sim.audit_attack_all "D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/disc/SLUS_006.62.original-backup" --out findings/data/pe-attack-all-retail-audit-2026-10-18.json
    python -m pe_weapon_sim.run_source_combat

## Explicit remaining limits

Enemy AI periods/movement and damage, status durations and armor effects remain inherited
model assumptions. Angles default to seeded uniform headings if source_options.enemy_angles
is absent; range movement changes distance without reconstructing full3D positions. Burst
uses the source predicate, but occupancy therefore depends on supplied or modeled geometry.
Walking uses an adapter policy rather than exact controller/animation movement.

Counterattack scheduling is explicitly rejected in this backend until its interruption
and queue semantics are integrated. Serial timing is rejected for this source profile;
ordinary source shooting uses overlap. The economy surrogate explicitly rejects source
combat scoring, so whole-policy campaigns cannot silently mix this backend with an
uncalibrated aggregate loadout score. The encounter evaluator can run it directly.

Seconds use nominal59.9/2 updates/s; external asset readiness delays must be supplied.
Mode13 uses the previously extracted base actor clip. Mid-animation enemy reactions,
PM asynchronous effect readiness and broader special-action interruptions are not full
retail instruction-level emulation. Remaining work is to refine those paths and calibrate
an economy scorer against the integrated encounter backend before recomputing phase3 rankings.
