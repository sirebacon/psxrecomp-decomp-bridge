# Incoming-damage fallback audit and called-slot fix — October 18, 2026 (Claude)

Task step 1 of the accuracy plan: audit the fallback hits in `pe-current-model-balance-2026-10-18`,
then fix the largest contributors. Offline; no game input.

## Method

`audit_fallback_hits.py` replays `run_current_model`'s exact cases (8 groups × 8 frozen seeds × D5/Disc2
× 4 encounters × 6 fights × early/late) with the opt-in `hit_trace`. That attributes every landed hit
to (map, enemy id, boss flag, power source, action slot), plus the static reason power was missing
(`power_gaps.py`).

**Independent check:** the baseline replay reproduces the published run exactly: 16,247 hits, of
which 9,123 are fallback (56.15%), the same counters as `pe-current-model-balance-2026-10-18.json`.
`test_called_slots.test_audit_files_reproduce_published_run` pins this.

## Finding: the slot-0 default caused most fallback hits

The run gave every non-gated enemy the default `source_action_slot=0`. Many enemies never call
slot 0; their scripts attack only with slots 1–5, which do have source power. Top baseline
contributors:

| Identity | Group | Fallback hits | Share | Cause |
|---|---|---:|---:|---|
| 146 0x13 | normal (D5) | 3,896 | 42.7% | calls only slot 3 (power 98) |
| 273 0x125 | normal (Disc2) | 960 | 10.5% | no attack calls: Statue of Liberty boss room, overlay-driven (logged as non-boss) |
| 154 0x15 | boss (D5) | 578 | 6.3% | calls only slot 3 (power 78) |
| 429 0x26 | normal | 485 | 5.3% | slots 3/4/5 are status-only (power 0) and no critical-chance write |
| 256 0x223 | boss | 408 | 4.5% | slots 1/3/4 resolved; slot 0 never called |
| 245 0x421, 429 0x426 | boss | 740 | 8.1% | no identity resolves (overlay-driven or non-literal rank/kind) |

## Fix (opt-in, new runs only)

- **`source_options['called_slots'] = dict(contact=...)`** (`enemy_choice.called_slots` /
  `called_plans`): a non-gated foe uses the slots its identity's scripts actually call.
  - Each slot carries its own timing (window / anim / contact / effect / untimed) and its own
    power, effect type and critical chance from the same declaration. So selection, timing,
    damage and status refer to the same attack.
  - One called slot: deterministic. Several unguarded slots: a uniform choice, labelled with
    the counter `called_slot_unguarded_multi`.
  - Slots without source power are dropped. Distance-gated foes (`enemy_choice`) keep their
    guards.
- **Template critical chance** (`enemy_power`, `default_critical=True`, used by `called_plans`
  only): `battle/enemy_slots.c` Entity_AllocSlot copies `g_EnemyCombatantInitial`. Its byte 0x90
  (effectChance) is 0 in the retail EXE (tested). So a script that never writes field 0x3F
  attacks with critical chance 0. Such profiles are labelled `critical_source='template default 0'`.
  - This resolves 429 0x26's status-only attacks (power 0: buff clear / confusion / poison).
- New counters: `called_slot_matches`, `called_slot_foes`, `called_slot_unguarded_multi`, and
  `strike_timing_<kind>` per executed strike (gated or called).
- `hit_trace` (audit only): underscore keys, excluded from campaign aggregates.

## Result (same cases, both bounds)

| | Hits | Fallback | Share |
|---|---:|---:|---:|
| Baseline (published options) | 16,247 | 9,123 | 56.15% |
| + `called_slots` | 19,954 | 2,218 | 11.12% |
| Ordinary only | 15,006 | 1,232 | 8.2% |
| Bosses only | 4,948 | 986 | 19.9% |

Hit counts rise because the affected enemies now attack with source power and per-slot plans
instead of the generic profile.

Remaining fallback, all labelled:

- **273 0x125:** 1,013 hits. Overlay-driven Liberty boss parts.
- **Boss identities that don't resolve:** 245 0x421 (376), 429 0x426 (364), 269 0x41B (108),
  188 0x21A (100).
- **0x1A in rooms 333 and 263:** 219 hits. Two species share the ID and their declarations
  differ (multipliers 176/182 with critical 32, vs 178/190 with critical 28 and stiffness);
  the logged HP/defense pairs don't map to either literally.
- **210 0x1D:** 38 hits. Shared scale cell 11 is unknown.

## New largest gap: untimed effect attacks

On the early bound with `called_slots`, 8,556 of 12,427 executed strikes (69%) use the labelled
`untimed` 10/10 timing. They're mostly slot 3+ effect attacks; 146 0x13's slot 3 loads effect 40.

- Effects 0–84 are PM overlay programs loaded on demand (`pm/process.c`). They aren't
  decompiled, so their release timing can't yet be ported.
  - A read-only live read of the handler table confirmed it: only 73 and 75 were loaded in the
    Eve fight.
- Effects 85+ are room task programs. 115/122/136 are ported; others (116, 129, 137–139, 142,
  147, 150–158, 166, 180, 187) still need their controllers.
- Until these are resolved, results must be tested for sensitivity to this placeholder (next
  steps).

## Reproduce

```
PYTHONPATH=tools python -m pe_weapon_sim.audit_fallback_hits --bound both --out findings/data/pe-fallback-hit-audit-baseline-2026-10-18.json
PYTHONPATH=tools python -m pe_weapon_sim.audit_fallback_hits --bound both --extra "{\"called_slots\": {\"contact\": \"BOUND\"}}" --out findings/data/pe-fallback-hit-audit-called-slots-2026-10-18.json
PYTHONPATH=tools python -m unittest pe_weapon_sim.tests.test_called_slots
```
