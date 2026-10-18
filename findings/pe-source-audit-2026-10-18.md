# Decomp-driven simulation development — 2026-10-18

User direction: develop from source; use the running game only when a specific scan is
needed. No game input, state load, launch or runtime scan was performed in this pass.

## Implemented

Added `tools/pe_weapon_sim/source_timing.py`: integer per-update gauge gains, slow/haste
precedence, update gates, ceiling refill counts, and switch-to-next-attack transitions.
`run_source_timing.py` generated 512 deterministic transitions across eight source and
destination classes, four entry gauges and retail/CURRENT costs. Outputs are separate
from historical campaign results. The table is `pe-source-timing-2026-10-18.md` and raw
cases are `data/pe-source-timing-2026-10-18.json`.

`engine.fill_seconds(..., source_steps=True)` now supports exact integer gauge arithmetic;
`engine.fight` opts in with rules['source_gauge']=True. Default legacy behavior is preserved
for historical reproduction. The existing economy surrogate does not implement this option:
do not enable it in whole-policy campaigns until surrogate scoring/cache identity also match.
TICK_HZ remains an explicit legacy assumption (94), not validated by the new source work.

Six new source-state tests passed; full suite is 70 tests. Reproduce with PYTHONPATH=tools:

    python -m pe_weapon_sim.run_source_timing
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

## Source evidence

Paths below are relative to `D:/Recomp Games/Parasite Eve Project`.

- `parasite-eve-decomp/src/main/battle/enemy_actions.c:267`:
  Battle_SetupEnemyAnims assigns rate = stat22 * scale[actionId] / 10 using integer math.
- `parasite-eve-decomp/src/main/menu/main_update.c:99`:
  Menu_MainUpdate advances only with nonzero low byte of menuMode and without game flag
  0x100. Slow subtracts floor(rate*2/5); otherwise haste adds floor(rate/2). Slow wins.
- `parasite-eve-decomp/src/main/battle/encounter.c:253`:
  menuMode begins at 1; opening a turn sets 0; other execution paths set 2. Ready-state
  handling clamps gauge at 9000. Therefore VBlank rate alone does not establish gauge rate.
- `parasite-eve-decomp/src/main/battle/turn.c:224`:
  FinishAction resets the gauge; `battle/phase.c:302` sets the action-block flag and later
  paths clear it. These support pausing during execution but do not prove an entire turn
  is one uniform blocked interval. Preserve both timing scenarios until event scheduling
  is reconstructed. Menu-mode and action-flag gates are separate.
- `parasite-eve-recomp/src/mods/pe_atb_items.c:295` onward:
  CURRENT tracks the menu turn and queued action. Allowed weapon changes from a borrowed
  gauge restore savedGauge-4500; full-bar allowed changes leave4500. Borrowed cancellation
  refunds the saved gauge. Attack takes precedence when classifying mixed queues.
  Default settings enable half-bar items, quick PE and weapon changes, but live settings
  can override defaults. The switch helper assumes enabled/allowed, one isolated switch,
  no gauge accrual during menu/execution, and the destination action's established rate.

## Important correction to live evidence

`battle/attack.c:38` Battle_FinalizeAttackResult decrements the active BattleAction
attackWord low10 bits. `battle/commands.c:228` BattleCmd_SyncActiveAmmo and other commit
paths copy those bits to the inventory record separately. Thus unchanged inventory ammo
does NOT demonstrate that no bullets fired. Earlier attack captures did not snapshot
the active action, so firing is unverified rather than disproven. The observed absence
of pause flag remains an independent observation. Historical data is preserved.

The future capture helper defaults to passive scan with no state load and records active
action ammo; the analyzer ignores ammo comparisons if the core's action pointer differs
from the sampled record. No new live scan was necessary in this pass.

`item/actions.c:814` Inv_DrawSlotItemIcon is misleadingly named: it transfers ammo from
a reserve pool into the tracked weapon, bounded by magazine capacity (max999) and reserve.
`battle/commands.c:388` synchronizes current ammo, calls that transfer and rebuilds the
weapon record. The existing simulation's unlimited-reserve/end-of-turn-only reload policy
and fixed0.8s duration are still assumptions; the transfer routine alone does not settle
when every reload path executes. Do not replace timing with a guessed duration.

## Next phase

1. Reconstruct reload call sites and shot/command progression, including when an empty
   magazine interrupts queued commands; add finite reserve pools and ammo carry between guns.
2. Trace action animation end conditions and event timers; loop counts are animation loops,
   not automatically frames. Preserve uncertain seconds as explicit parameters.
3. Connect stateful switching to encounter simulation and the economy surrogate together;
   benchmark legal switching policies with carried ammo, gauge and enemy state. The new
   512-case table is transition validation, not a dynamic damage/portfolio simulation.
4. Use targeted passive RAM scans only for residual clock/animation questions. Record the
   active action's ammo, equipped slots, gauge gates and callbacks before claiming timings.
