# Aya's incoming status effects — October 18, 2026 (Claude)

Next shared mechanic after effect-driven actions. Offline; no balance runs (hold respected).

## Why

Of the attack slots resolved for the run's logged ordinary enemies, 118 of 571 carry a status
effect type: 63 poison (1), 27 stiffness slow (6), 21 darkness (4), 7 defense-down (7). Until
now every one was counted as `incoming_status_unmodeled`.

## Source rules

- **Apply** (`battle/enemy_actions.c` Battle_ApplyEnemyAttack), called by
  `entity/combat.c` Entity_ResolveDropTable after every resolved hit whose effectType ≠ 0 —
  there is no separate status roll; it also runs at zero damage and under Barrier. Per ailment
  pair: already afflicted → nothing; armor resist bit → resisted when rand % 100 < 70 (poison,
  slow) / 60 (confusion, darkness) / 50 (lock); both bits set (a cure taken while healthy) →
  the immunity is consumed; else afflicted with timer 9000.
  - 1 poison: step = enemy field 0x43 (effect_level), period = field 0x44 (effect_duration).
  - 4 darkness: hit evaluation and targeting use range **200** instead of the weapon's
    (`battle/setup.c`, `battle/turn.c`).
  - 5 / 6 stiffness lock / slow: clears Haste; slows ATB gain (lock also stops movement).
  - 7: flag 0x1000, which cuts the defense term stat20/5 to 3/10 and has **no timer**.
  - 8 / 9 / 16: HP halved / to 1 / to 3/4 (8 and 16 blocked by Barrier); 2 clears buffs.
  - 3 confusion and 10-13 steals: tracked, effect not modelled.
- **Tick** (`entity/combat.c` Entity_UpdateTimers, once per battle update): poison via
  Battle_SubActionStep (damage when the counter reaches the period; reset to 0 then ++ in the
  same tick, so every `period` updates), its timer − statusStep3E; confusion, darkness,
  stiffness timers − statusStep3C.
- **Inputs**: Aya's statusStep3C / 3E from level-table track 4 (level 33: 28 / 10 → poison lasts
  900 updates ≈ 30 s, darkness / stiffness 322 ≈ 10.7 s); enemy effect_level / duration from
  init-script literals (`Entity_WriteFieldByCmd` 0x43 / 0x44; e.g. the farming-room enemy:
  3 HP every 78 updates; map 126 ID 0x12: 3 HP every 30); armor resist bits from tail effects 1-5
  (bit 1 << (k − 1)).
- Naming note: the code tests bit 0x2 for confusion and 0x8 for stiffness, but the in-game
  mod names call armor effect 2 "Resist Stiffness" and 5 "Resist Confusion". The model uses the
  bits as the code does; a live check would settle which label is right.

## Code (opt-in)

- `player_status.py`: `PlayerStatus` (apply / tick / dark / stiff / locked), `armor_effect_flags`.
- `source_stats.player_inputs` now also returns `status_step3c`, `status_step3e`,
  `armor_effect_flags`; the static catalog adds `status_level` / `status_period`.
- `source_options['player_status'] = True` (non-beam encounters; needs the status steps in the
  aya dict): poison ticks add damage (`player_poison`), stiffness sets the session's slow ATB,
  lock stops modelled approach movement, darkness forces range 200 for hits and targeting,
  defense-down feeds the damage formula, HP-fraction effects adjust HP. Counters:
  `status_poison`, `status_already`, `status_resisted`, … ; confusion / steals still count as
  `incoming_status_unmodeled`.

Example: map 126 ID 0x12 (effect-122 flare, poison 3/30) vs a level-21 Aya at 800 units over
30 s: 207 → 267 damage taken (60 from poison; later hits find her already poisoned).

## Validation

`tests/test_player_status.py` (10): apply rules (already, resist bits, immunity, Haste removal,
lock vs slow, HP fractions, untimed 0x1000), poison cadence (indices 78, 156, …; 11 ticks in 900),
darkness duration by level step, inputs, combat integration and the missing-input error.
Full suite 257 passed; focused beam/combat checks pass.

## Limits

No cure-item use (auto-cure armor, manual cures), confusion movement, or status on the beam
path beyond its own stiffness model; the run's armor mods must be supplied to get resist bits.
