# Enemy room scripts and action records — October 18, 2026

All work was offline: read existing PST RAM metadata and raw disc assets; no game connection or control.

## Extraction

`extract_enemy_scripts.py` reads 103 campaign battle maps from both US discs (206 reads,
zero asset-read errors). Every corresponding room blob has the same SHA-256 on both discs.
Counts below deduplicate the discs, but do not claim distinct enemy species or actions:

- 2,970 room animation headers, including frame counts and raw header bytes.
- 248 `Script_SetEntityAnim12Args` declarations, 156 five-argument declarations,
  and 47 action-entry step declarations.
- 8,465 self-field setters, 237 setters targeting another actor, 821 callback-offset setters.
- 135 map + rank/kind catalog keys with consistent literal rank, kind and charge settings.
  Literal charge values range from 40 to 125.

Room provenance includes sector address/count, room hash, script root/boundary, instruction
byte offset, opcode/handler, and every operand's addressing mode. The JSON also records
snapshot and source hashes. `Scene_LoadRoom` indexes the map sector table at map minus one.
The relocated taskBlock roots select actor-type scripts; bankRows group selects actor type
and its slot selects animation mode. Instruction length is 8 + 4*argument_count; the sixth
argument starts using modes from the second header word. Nonzero modes remain unresolved.

This is a bounded **linear static inventory**, not a control-flow graph or executed trace.
Decoding stops at an unknown opcode, invalid argument mode, or script boundary. Bytes after
unconditional jumps are not proved reachable. Callback targets, actor switches, variable
assignments, conditions and loops require further analysis before a faithful AI interpreter.
Animation frame counts alone do not establish time until an attack hits or completes.

## Identity matching and integration

The logger reads the enemy ID from core +4: low byte rank, high byte kind. This is not
actor type/subtype. `enemy_catalog.py` joins exact map + rank/kind from literal setters,
requires one consistent charge value, and rejects conflicting catalog candidates. Matching
is still a static-declaration scenario: no proof the declaration executes for every spawn.
It does not resolve indirect identity/charge setters or apply cross-actor setters.

Opt in with source option `static_enemy_catalog=True`. Matching charge, rank and signed
poison tick values override sensitivity defaults; explicit per-enemy profiles override the
catalog. Missing and ambiguous matches retain defaults. Existing simulations are unchanged
unless enabled. Coverage counters are returned with each fight.

Frozen pool coverage: D5 normal 3/3, bosses 4/5; Disc2 normal 14/23, bosses 7/15.
The pool already deduplicates repeated identity/HP/defense records and retains one location;
this rerun preserves that historical pool definition. It is not a per-room campaign replay.

## Concrete action record: map 156, actor type 3

Core declarations give rank22/kind2 (logged ID0x0216), charge70, poison tick29.
At room byte209272, opcode112 declares action slot0, effect type0, enter mode6, exit mode7,
category3, hit frame20. Power is **mode3 operand-table entry1**, not literal damage1.
At byte209540, opcode176 sets slot0 enter step131072 (2.0), exit step98304 (1.5).
Bank headers give mode6 42 frames and mode7 30 frames. Slots3 and4 also declare attacks,
with modes10/11 and8/9, respectively; their powers likewise depend on operand-table entry1.
The new balance scenario therefore uses charge70 and poison29 for this match, but does not
invent power, action-selection probabilities, or windup/recovery from these declarations.

## Rerun and validation

`run_behavior_balance --static-catalog`: 12,816 fights, eight frozen campaign seeds,
six fights per encounter, four encounters at D5 and Disc2, eight build groups, and 150
matched Counter-for-Quickdraw seed/loadouts. 18,138/23,838 enemy instances matched (76.1%).
All ammo-conservation assertions passed. Full suite: 111 tests passed.

Controlled machine remains the lowest Disc2 score across the three fallback rates:
5.191 / 5.423 / 5.573; win fractions .995 / .990 / .984. Mean Counter replacement score
changes are +5.632 / +6.376 / +6.764 (worse); win deltas -.043 / -.057 / -.066.
These remain conditional results: generic action scheduling, hit chance/geometry, damage
fallbacks, reaction settling and historical acquisition decisions have not been replaced.
Campaign progression was not reoptimized. No global rebalance recommendation follows.

## Next targeted work for Claude

1. Build reachable control flow from roots and callback offsets; track actor changes and
   literal assignments, including operand-table entry1 in the map156 example.
2. Decode enemy action chooser conditions and animation-event wait/yield behavior before
   replacing the generic consume-charge / windup10 / recovery10 policy.
3. Expand matching with verified cross-actor and indirect identity setters. Preserve all
   room occurrences rather than the historical pool's single retained location.
4. Then integrate action power, hit frame, entry/exit steps and clip frame counts into a
   per-action event schedule, compare against the generic policy, and rerun the same seeds.

Reproduce with bundled Python and PYTHONPATH=tools:

    python -m pe_weapon_sim.extract_enemy_scripts --out findings/data/pe-enemy-scripts-2026-10-18.json
    python -m pe_weapon_sim.run_behavior_balance --static-catalog
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

Outputs: `data/pe-enemy-scripts-2026-10-18.json`,
`data/pe-static-script-balance-2026-10-18.json`, `pe-static-script-balance-2026-10-18.md`.
