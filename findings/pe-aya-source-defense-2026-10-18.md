# Aya's source stats and defensive inputs — October 18, 2026

Continuation of the shared-combat priority "join source-earned player defense/armor inputs".
One **read-only** live probe (isolated god-mode session, debug port 4378, final Eve fight):
no input, no writes, no state load. Balance-rerun hold unchanged; no balance runs.

## Source chain (decomp)

| Input | Source | Formula |
|---|---|---|
| defense subtracted (stat20) | `aya/stats.c` Inv_RecalcSlotStats | `AyaLevelStats[defense stat level + g_StatScaleBase[2]].defense`, used as stat20/5 |
| armor first | `aya/stats.c` Inv_BuildArmorList | armor base[0] + bonus[0], cap 999 — action slots 0-2 |
| armor second | same | armor base[1] + bonus[1] (PE defense), cap 999 — slots 3+ |
| critical resist (third) | same | CR evade v (cap 999): v < 85 → isqrt(v·3000)/10, else (v·249/208 + 402)/10, u8 |
| use | `entity/combat.c` Entity_ResolveDropTable | damage = power − stat20/5 − first/second; crit if roll < chance·(100 − third)/100 |
| stat level | `save/game_data.c` Aya_StatQueryLevelAndSubLevel | largest i with growth[kind][i] ≤ value |
| level-ups | live | +10 on every stat value: level L → 10·(L − 1) (level 33 → 320) |

## Live verification (level 33, N Jacket +32/21/12, CR evade 31)

| Field | Predicted | Live |
|---|---|---|
| stat20 | row 32 defense = 362 | 362 |
| armor first / second / third | 66 / 49 / 30 | 66 / 49 / 30 (parameter word 0x01E0C442) |
| offense (stat1E) | 350 | 350 |
| stat22 | AT growth (kind 5) index of 320 = 29 → 79 | 79 |

Data: `data/pe-aya-level-stats-2026-10-18.json` (99 level rows, 7 growth tables, probe provenance),
`data/pe-live-defense-2026-10-18.json` (raw probe). Probe: `tools/pe_weapon_sim/live_defense_probe.py`.

## Correction: Active Time lags Aya's level

Growth kind 5 (Active Time) has uneven early thresholds (0, 20, 28, 36, 48, 72, 84, 96, 105,
120, 129, 140, 150, 160, then +10). Every other track is +10. So at level 33 Aya's AT level is
29 (stat22 79), not 32 (82). Phases 1-3 used `stat22 = 49 + level` (and phase 1's level-21 Aya
used 70; source gives 67), overstating stat22 by about 3 from Day 5 on. An AT purchase moves
the value to the next kind-5 threshold. Example (policy G, seed 1): 15 AT purchases end at
stat22 92 with source tables vs 97 with the linear approximation, so earlier reports overstate
Active Time's late value somewhat. Max HP was not checked: the session's 385/385 comes from
the HP-level-bug save and god mode, so it doesn't test the HP formula.

## Code (opt-in; historical results reproduce unchanged)

- `economy/source_stats.py`: stat queries, `aya_stats`, `armor_inputs`, `player_inputs`.
- `economy/bp.py` `Aya(source=True)`: source offense / stat22 / capacity, BP buys the next
  growth threshold, `combat()` adds `defense`, `armor_first`, `armor_second`, `critical_resist`
  from the worn armor. Enabled per ruleset with `source_level_stats=True`
  (`ER.variant(ER.CURRENT, ..., source_level_stats=True)`); default off.
- `source_combat.py`: explicitly powered ordinary hits now take armor / critical resist from the
  player dict; an explicit per-enemy profile value still overrides (older fixtures unchanged).
- Tests: `tests/test_source_stats.py` (6, pinned to the live values). Full suite 224 passed.

## Next

Use `source_level_stats=True` plus the source power catalog when the hold lifts; check max HP
on a save without the HP-level bug; ordinary-enemy action choice / delivery timing remains the
next highest-payoff item.
