# Committed actions freeze enemies: the source "serial" rule — October 19, 2026 (Claude)

## Starting point: what the user observed

You cannot cancel out of a committed firing (or a counter attack), so Aya can be hit while she
fires: she is a sitting duck. The first change made `player_evade` (the fitted dodge share) not
apply while an attack or counter is committed (`strikes_while_committed`).

With that change alone, evasion could no longer fit the log:
- evade 0.7 still left ordinary damage at 1.55×;
- 77% of simulated hits landed during Aya's committed action, because enemies were allowed to
  charge and start new attacks during it.

## Source: game flag 0x100

`battle/player_turn.c:123` and `turn.c:227` (FinishAction) set `g_GameStateFlags |= 0x100`
while Aya's queued action command (3..406) runs with `actionMode >= 4`. The flag is cleared when
the queue ends (`phase.c`, `player_turn.c:142`). While it is set:

| Code | Effect |
|---|---|
| `battle/turn.c:968` `Battle_UpdateEnemy` | skips enemy charge and status-timer updates |
| `script/flow_opcodes.c:307` | skips every script node of entities other than Aya (unless the node has flag 0x80), so enemy AI makes no new decisions |
| `menu/main_update.c:100` | no gauge gain for Aya: her gauge stays 0 through her own action |
| `asset/tim_textures.c:128` | PM effects run only for commands 0x55..0x72 |

What still runs: entity animation and actor collision, and the FieldFx task effects (ids 85+).
So **an attack already under way still lands** — the sitting duck — **but no enemy starts a
new attack while Aya is committed.**

## Model (opt-in `serial_action`; `calibrate_logged --serial`, `compare_rules --serial`)

- An enemy in its charge phase is frozen while `session.action_busy`: no charge, no status
  ticks, no decisions (`serial_frozen_updates`).
- An enemy mid-action keeps animating; its strike can land, with charge and status frozen.
- Aya's gauge does not fill during her action (`source_battle` `step_gauge(game_flags=0x100)`).
- Also tested, as player behaviour: `reaction_paused`, the per-turn menu time spent in the
  paused command menu.

## Calibration

Walk policy, log-era Counter, `--atb-guard --logged-charge`, ordinary battles:

| Setup | Damage taken, log 15.6 → sim | s/turn, log 8.22 → sim | D2–4 ratio | Disc2 ratio |
|---|---|---|---|---|
| No serial, reaction 75 live, evade 0.55 (earlier fit) | 16.4 (1.05) | 8.20 | 1.15 | 0.98 |
| Sitting-duck evasion only, evade 0.7 | 24.2 (1.55) | 8.17 | 1.61 | 1.53 |
| Paused reaction, evade 0.5, no serial | 19.8 (1.27) | 7.89 | 1.24 | 1.28 |
| **Serial, reaction 40 paused, no evasion** | **18.0 (1.15)** | **8.57** | 1.43 | **0.95** |
| Serial, reaction 40 paused, evade 0.4 | 14.4 (0.92) | 8.39 | 1.15 | 0.76 |

- **The source rule alone, with no fitted evasion, reproduces the log** almost as well as the
  0.55 evasion fit did. The correlation per battle is a little higher (0.58 vs 0.55).
- With a paused reaction, damage doesn't depend on the reaction time: 18.0 at 0, 40 and 75
  updates. Time per turn does, so 30 updates matches the log (about 8.2 s).
- New assumption set **`logged_player_serial`**: reaction 30, paused, no evasion. Use it with
  `--serial --atb-guard --logged-charge --multi-kind`.
- The earlier `logged_player` (evade 0.55) is kept for reproducing earlier runs. Its evasion
  value was standing in for this source rule.
- Remaining:
  - Day 2–4 ordinary is 1.43× high, which a little real player spacing could explain;
  - Day 5 bosses are still near zero (room 332 lead);
  - Day 1 is small and noisy (8 battles).

Files: `pe-calibration-logged-serial2-r{0,40,75}-e00-2026-10-19`,
`pe-calibration-logged-serial2-r{0,40}-e04-2026-10-19`,
`pe-calibration-logged-committed-e{06,07}-2026-10-19` and
`pe-calibration-logged-paused-e{00,03,05}-2026-10-19`. Test: `test_room_m256.SerialActionTests`.
