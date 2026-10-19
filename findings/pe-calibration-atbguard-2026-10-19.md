# Incoming damage: the gauge guard, and a corrected calibration reading — October 19, 2026 (Claude)

## Missing source mechanic: incoming damage halves while Aya's gauge is above 0

`Entity_ResolveDropTable` (entity/combat.c:85–88), after defense, armor and critical:

```c
if (!(after_state->stateFlags & 0x200)) {      /* no PE barrier */
    if (after_state->atbGauge > 0) value /= 2;
```

- `source_enemy.enemy_damage` already had the halving (`charged_guard`), but the main
  `source_combat` hit path always passed False. Every non-beam enemy hit did full damage.
- **New opt-in `source_options['atb_guard']`:** halve when `session.gauge > 0` and Aya is not
  mid-action.
  - The gauge is set to 0 at the attack commit.
  - Game flag 0x100 gates gauge gain during the action (`source_timing.step_gauge`), so hits
    landing while she acts do full damage.
  - Counters `atb_guard_halved` / `atb_guard_full`.
  - Test: `test_called_slots.AtbGuardTests`.
- Flags:
  - `calibrate_logged --atb-guard`;
  - `compare_rules --atb-guard`.
- The beam path already used the beam player's own gauge.
- In Disc2 ordinary replays, 77% of hits are halved and 23% land during Aya's action.

## Corrected calibration reading

The October 18 report said incoming damage *per hit* matched and hit *frequency* was about
2× too high. Two corrections:

1. That per-hit check came from one enemy type (0x11).
2. The calibration JSON's `hits` field is summed over the replay's 4 fights, not averaged.

Per fight, against the raw log's `hurt` rows (one per hit Aya takes), same day's model, log-era
Counter, `walk` policy:

| Group | Battles | Hits per battle, log → sim | Damage per hit, log → sim (no guard) | Damage per hit, sim with guard |
|---|---:|---|---|---|
| Day 1–4 ordinary | 34 | 2.03 → 3.29 (1.6×) | 10.6 → 16.8 | **11.8** |
| Day 1–4 boss | 6 | 0.83 → 3.08 | 14.6 → 20.8 | **13.2** |
| Disc2 ordinary | 88 | 0.99 → 1.38 (1.4×) | 14.1 → 23.2 | **18.5** |

Total damage taken, ordinary battles (`pe-calibration-logged-{noguard,atbguard}-2026-10-19`):
15.6 logged → 38.1 without the guard (2.45×) → **29.0 with it (1.86×)**.

## What remains

- **Hit frequency is 1.4–1.6× the log.** Candidates:
  - player movement and dodging (only the `walk` approach is modelled);
  - the enemies' outer state / position gates, which aren't evaluated;
  - the human player's spacing.
- **Disc2 per-hit damage is 1.3× high with the guard.** Candidates:
  - the armor used: the replay takes the last save holding the gun, while the battle row
    logs the armor actually equipped;
  - Disc2 power scales.
- **Day 5 bosses (4 battles) deal almost no damage in the replay** (32 logged vs about 1
  simulated). Their hits resolve to about 0 power. Not investigated yet.

Recommendation: use `--atb-guard` for every new comparison. It is source behaviour, and it
interacts with balance: builds whose actions take longer spend more time at gauge 0 and take
more full-damage hits.

## V80, the shared power scale, is a per-playthrough difficulty setting

Every scaled enemy power is N10 × multiplier >> 16, with N10 = V80 (or 65536 when V80 is 0).
A scan of every room script on both discs finds **exactly one write to V80**: room 5 (the
opening theatre) actor 6, offsets 144468–144780. It is set once from V8:

| V8 | V80 | Scale |
|---|---|---|
| 0 | 65536 | 1.0 |
| 1 | 91750 | 1.4 |
| 2 | 104857 | 1.6 |
| ≥ 3 | 117964 | 1.8 |

- V8 behaves like a completed-playthrough count (New Game+), which isn't confirmed.
- The live read at the final fight (V80 = 65536) shows the logged run was at scale 1.0 for its
  whole length. So `FIRST_RUN_SHARED_CELLS` is right for every logged battle, not just the
  end.
- A replay scenario can set `{10: 91750}` and so on to model later playthroughs.
- The Day 5 boss gap is not a scale effect. At scale 1.0, room 332's 0x0015 slot-3 power
  (N10 × 78) can't get through Aya's Day 5 defense term (44) plus armor (41). Yet the log has
  3 hits for 44 HP in that battle. That remains open.
  - Lead: the log splits room 332's 0x0015 into one large form (HP 170, EXP 114) and four
    small ones (HP 45, charge 40). Every logged hit there is 7–8 HP. With the gauge halving,
    that implies power of about 100 for a slot ≥3 attack.
  - Only actor 6's declaration (78) is extracted; actor 7 shares the id. The hit likely comes
    from an attack or power the extractor doesn't resolve.

## Charge-step fallback and player evasion: ordinary battles now match the log

**1. Logged charge steps** (`logged_charge.py`, data
`pe-logged-enemy-charge-2026-10-19.json`, opt-in `logged_charge`, flag `--logged-charge`).
- The logger's `enemy` rows record each enemy's runtime charge step.
- For all 105 identities where the script catalog has a literal field 0x3E, the two agree
  exactly. The other 29 fell back to the placeholder 90, while the log shows 40–81 (0x0015,
  0x0200, 0x001A, 0x001D, 0x001E and others). Those enemies acted up to twice as often.
- The fallback fills only identities with no catalog value. It is keyed by (map, id, HP) so
  variants stay separate.

**2. Human timing and evasion** (behaviour, not source).
- With `--reaction 75`, time per turn matches (7.97 vs 8.22 s). Damage per hit then matches
  closely: Day 1–4 ordinary 11.5 vs 10.6, Disc2 ordinary 14.2 vs 14.1.
- The simulator still lands 2.1–2.4× the logged strikes per turn. A human moves during the
  gauge wait.
- New opt-in `player_evade`: the share of strikes avoided. Flag `--evade`, assumption set
  `logged_player` in `compare_rules`.
- Fitted value: 0.55 (Day 1–4 alone gives 0.52, Disc2 alone 0.58).

**Full calibration** (`pe-calibration-logged-full-2026-10-19`: walk, reaction 75, log-era
Counter, `--atb-guard --logged-charge --evade 0.55`):

| Group | Turns, log → sim (r) | Time s/turn, log → sim | Damage taken, log → sim (ratio, r) |
|---|---|---|---|
| All ordinary (123) | 2.13 → 2.43 (0.66) | 8.22 → 8.20 | 15.6 → 16.4 (1.05, 0.55) |
| Day 2–4 ordinary (26) | 2.65 → 3.17 (0.80) | 7.23 → 7.44 | 26.9 → 31.0 (1.15, 0.65) |
| Disc2 ordinary (88) | 1.91 → 2.18 (0.50) | 7.70 → 6.40 | 13.2 → 13.0 (0.98, 0.48) |
| All bosses (12) | 3.50 → 4.15 (0.84) | — | 17.3 → 12.3 (0.71) |

Notes:
- Evasion is one parameter fitted to these battles. Two eras landing at 1.15 and 0.98 with a
  single value is consistent with a real behaviour, not over-fitting. It's still a fit, so it
  belongs in an assumption set, not in source mechanics.
- **Bosses:** Day 5 (4 battles) is near zero; see the room 332 lead above.
- **Absolute survival** for ordinary battles is now usable under `logged_player`. Boss
  absolute numbers are not.

### Room 332 follow-up (still open)

- Actor 6 is the large form (charge 65). It calls slot 3 (power N10 × 78, effect type 6) with
  effects 187 and 75.
- Actor 7 is the small form (charge 40). It never runs a command and loads PM effect 79.
- Its action records are the template's, which carry power 0 (`g_EnemyCombatantInitial`
  slot records read from the retail executable).
- So neither path explains the steady 7–8 HP hits at Day 5 defense (term 44, armor_second 41).
- Candidates:
  - effect 79 or 187 supplying its own power;
  - a different defense term for these hits;
  - the logged run's Aya stats differing from the source level table.
- It affects only the 4 Day 5 boss battles.
