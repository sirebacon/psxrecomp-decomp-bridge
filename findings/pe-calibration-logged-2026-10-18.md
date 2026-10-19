# Independent check against the play log — October 18, 2026 (Claude)

> **Correction (October 19):** finding 4 below is superseded by
> `pe-calibration-atbguard-2026-10-19.md`. Counted per fight against the log's `hurt` rows, per-hit
> damage was 1.5–1.8× too high. The cause was a missing source rule: incoming damage halves while
> Aya's gauge is above 0. Hit frequency is 1.4–1.6× high, not 2×.

`calibrate_logged.py` replays every logged won battle from the campaign log:

- 171 battles; 135 remain once battles with PE casts are excluded, since PE abilities aren't
  simulated.
- Each battle uses the gun and armor of the last save holding that gun, Aya's source stats at
  the logged level, and the battle's own enemies.
- The results are compared with the raw log (`build-release/pe_play_log.csv`, aligned 175/175
  on map, secs and EXP).

## Findings

1. **The logger's `secs` field is seconds ÷ 10.** `pe_loot_logger.c` computes
   `pe_secs = (frames*10/599 + 5)/10`. Real time is frames / 59.9; for example, frames 2778 is
   46 s but logs as `secs=5`.
   - Every earlier use of logged `secs` as seconds was off by 10×. That includes the Phase-1
     tick-rate calibration, which the source timing model has since replaced.
   - Real ordinary battles: about 12–13 s of fixed overhead (intro, results) plus about
     7.6–8.2 s per turn.
2. **The logged run had the old Counter boost.** Mod Effects "Counter chance %" was 500 by
   default (REBALANCED) until it was removed in c7dc04f. The HP-level bug froze the boosted
   level at level 24.
   - The log shows counters after almost every hit Aya takes.
   - Replaying with `--log-era` (counter HP level × 5, capped at 240) brings turns per battle
     into line.
3. **Player time per turn:** 8.2 s logged vs 5.7 s simulated. The difference is human
   reaction / menu time, about 75 updates, now the `human_reaction` assumption set.
4. **Incoming damage per hit matches.** 0x11 logged hurts are 20–61; the simulator gives about
   38.
   - The overall damage-taken ratio of 2.0–2.7× comes from hit frequency.
   - Part of it is the remaining placeholders: Disc2 normal battles still have a 26% fallback
     share.
   - The rest is player movement / spacing, which the log can't resolve per battle. That's
     bracketed by `far_player` (distance profile × 1.4).
5. **Darkness is source-correct** (range 200 in `Battle_CheckEvasion`). A standing Aya then
   misses everything, so the comparison now uses the `walk` policy: Aya approaches into range.

## Results (log-era Counter, `walk` policy, 4 fights per battle)

| Group | n | Turns logged → sim (r) | Damage taken logged → sim (ratio, r) | Fallback share |
|---|---:|---|---|---:|
| All ordinary | 123 | 2.13 → 2.35 (0.66) | 15.6 → 35.7 (2.29, 0.47) | 0.15 |
| Disc2 ordinary | 88 | 1.91 → 2.08 (0.53) | 13.2 → 26.8 (2.02, 0.29) | 0.26 |
| D2-4 ordinary | 26 | 2.65 → 3.14 (0.75) | 26.9 → 72.3 (2.68, 0.76) | 0.00 |
| All bosses | 12 | 3.50 → 4.17 (0.79) | 17.3 → 68.2 (3.94) | 0.05 |

Before these fixes (CURRENT counters, `stand` policy): turns 2.83 and damage 2.56× for ordinary
battles.

Interpretation:

- Turns per battle and the player's damage output are now credible (r ≈ 0.66 per battle).
- Incoming damage is about 2× too high in absolute terms. The model supports **relative**
  comparisons (same enemies, same assumptions, two rule sets) much better than absolute
  survival numbers.
- Comparisons report results under `far_player` as well, so conclusions that depend on the
  absolute incoming level stay visible.

## Files

- Data: `data/pe-calibration-logged-2026-10-18.json` (stand policy, CURRENT counters).
- Data: `data/pe-calibration-logged-walk-2026-10-18.json`.
- Data: `data/pe-calibration-logged-logera-2026-10-18.json`.
- Reproduce:
  `PYTHONPATH=tools python -m pe_weapon_sim.calibrate_logged --fights 4 --policy walk --log-era --out pe-calibration-logged-logera-2026-10-18`
