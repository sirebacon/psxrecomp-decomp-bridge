# Balance recommendations from the source-backed combat model — October 19, 2026 (Claude)

These recommendations come from the improved outside-the-game simulator: called-slot enemy
attacks, effect timelines, melee reach, source Aya stats and the `walk` policy. Nothing here
has been built into the mod or tested in the game.

## How much to trust these numbers

- Comparisons are **relative**: the same enemies, seeds and assumptions under two rule sets.
  - The play-log check (`pe-calibration-logged-2026-10-18.md`) matches turns per battle and
    damage per hit.
  - Incoming hit frequency is about 2× the log, so absolute survival rates are pessimistic.
- Every result is reported under three assumption sets:
  - `default`;
  - `human_reaction` (+75 updates per turn for menu time);
  - `far_player` (enemy distances × 1.4).
- **Ordinary battles and boss battles are reported separately.** Disc2 boss battles are an
  incomplete scenario:
  - boss identities 188 / 245 / 429 have unresolved attacks;
  - room 256 / 428 / 432 / 350 effects use placeholder timing (fallback share about 0.5 and
    untimed share about 0.65 in boss rows).
  - So no recommendation below depends on Disc2 boss numbers, and each one is checked for
    collateral damage on bosses.
- **Exhaustive battle mode** (`--all-battles`): every build fights every logged campaign
  battle. Without it, Disc2 results moved by ±1–2 s between battle samples. This is how
  the secondary-test MAG measured 7.2 s while the comparison MAG measured 9.2 s.

## Robustness check: newer source fixes (gauge guard, boss identities)

Re-run with `--atb-guard --multi-kind`; see `pe-calibration-atbguard-2026-10-19.md` and
`pe-boss-identity-multikind-2026-10-19.md`. Files: `pe-compare-class-allbattles-P1-guard-mk` and
`pe-compare-frozen-allbattles-P1-guard-mk`.

- Every recommendation's effect is unchanged:
  - P90 ordinary 3.23 → 5.70 s;
  - G3A3 34.7 → 21.7 s;
  - M203 4 28.1 → 22.5 s;
  - boss rows identical between base and proposal.
- What moves is the absolute level:
  - damage taken falls about 20–30%;
  - Disc2 boss win rates rise: class benchmark 0.47 → 0.60, frozen builds 0.68 → 0.78;
  - D5 rifle boss wins rise from 0.958 to 1.000 under the proposal.
- New comparisons should use both flags.

## Calibrated absolute check (`logged_player`)

Setup: `--atb-guard --logged-charge --multi-kind`, assumption set `logged_player` (reaction 75,
evade 0.55). This reproduces the log's ordinary-battle damage (1.05×) and time per turn. File:
`pe-compare-class-allbattles-P1-calibrated-2026-10-19`.

| Stage | Class | Ordinary s, base → P1 | Damage taken, base → P1 | Boss win, base → P1 |
|---|---|---|---|---|
| D5 | handgun (M9 3) | 27.0 | 41.0 | 1.000 |
| D5 | machine (MP5PDW) | 29.6 | 55.3 | 1.000 |
| D5 | shotgun (M500) | 29.7 | 45.5 | 1.000 |
| D5 | grenade (M203 4) | 41.6 → **31.3** | 71.3 → 57.2 | 0.875 → **1.000** |
| D5 | rifle (G3A3) | 48.8 → **29.4** | 84.2 → 50.6 | 0.875 → **0.958** |
| Disc2 | handgun / shotgun / grenade / rifle | 14.0 / 14.2 / 15.7 / 15.9 | 10–13 | — |
| Disc2 | machine (P90) | 5.89 → **9.02** | 3.5 → 15.5 | 0.818 (unchanged) |

- With R-B and R-C, every Day 5 class clears ordinary battles in 27–31 s.
- With R-A, the P90 is still the fastest crowd gun (about 1.6×), but it now takes slightly
  more damage than the others. That's a trade-off rather than a free win.
- **AAo_30 overshoots** (`pe-compare-class-ord-AAo30-calibrated-2026-10-19`):
  - the P90 reaches 12.6 s but takes 28.6 damage, against 10–13 for the other classes;
  - under `default` it starts losing fights (0.989).
- So keep 40%.

## Build sources

1. **Frozen builds:** campaign-earned loadouts.
   - At D5, every frozen build carries a G23, so D5 frozen results don't distinguish classes.
2. **Class benchmark (new):** `--builds class`.
   - Each class uses its representative gun from `run_benchmark.CLASS_GUNS` with equal
     investment:
     - D5: Day-5 attack investment and built-in effects only. Guns: M9 3 / MP5PDW / G3A3 /
       M500 / M203 4.
     - Disc2: [30, 10, 10] plus 2 Commands + Quickdraw. Guns: DE50AE7 / P90 / MAG / M10B /
       HK40.
   - Aya (level, armor, stats) is the same seed's frozen group-C build, so only the gun
     differs.
   - An earlier run without armor and at a lower level is kept as
     `pe-compare-class-noarmor-AA70-2026-10-19`. It overstated losses and is superseded.

## Findings (class benchmark, exhaustive battles, default set; other sets agree unless noted)

| Stage | Class (gun) | Ordinary time s | Ordinary win | Boss time s | Boss win |
|---|---|---:|---:|---:|---:|
| D5 | machine (MP5PDW) | 16.7 | 1.000 | 21.3 | 1.000 |
| D5 | handgun (M9 3) | 18.7 | 1.000 | 23.7 | 1.000 |
| D5 | shotgun (M500) | 22.6 | 1.000 | 33.0 | 1.000 |
| D5 | grenade (M203 4) | 28.1 | 1.000 | 36.7 | 0.958 |
| D5 | **rifle (G3A3)** | **34.7** | 1.000 | **46.5** | **0.875** |
| Disc2 | **machine (P90)** | **3.2** | 1.000 | 13.1 | 0.727 |
| Disc2 | handgun (DE50AE7) | 7.7 | 0.993 | 17.1 | 0.606 |
| Disc2 | shotgun (M10B) | 8.5 | 1.000 | 21.4 | 0.333 |
| Disc2 | grenade (HK40) | 9.3 | 0.986 | 20.5 | 0.424 |
| Disc2 | rifle (MAG) | 9.5 | 0.989 | 17.2 | 0.515 |

- Sample sizes: D5 30 ordinary / 24 boss fights per class. Disc2 276 ordinary / 33 boss
  fights per class.
- The class ranking is stable across assumption sets for D5 (Spearman 0.9–1.0). For Disc2 it
  is less stable (0.6–1.0).

## Recommendations

### R-A. Attack All: 40% per-bullet power, only with 2+ enemies alive, never in boss battles (`AAo_40`)

**Problem:** the P90 with Attack All clears Disc2 ordinary battles 2.4–2.9× faster than any
other class, taking almost no damage.

| Variant | Disc2 ordinary P90 time | Disc2 boss P90 win | Verdict |
|---|---|---|---|
| CURRENT | 3.23 s | 0.727 | dominant |
| AA_70 (always 70%) | +0.5 s | unchanged | too weak |
| AA_50 (always 50%) | 5.9 s | 0.94 → 0.44 (frozen) | wrecks single-target and boss use |
| AAm_60 (multi-only 60%) | +0.5 s | unchanged | too weak |
| AAm_40 (multi-only 40%) | 5.70 s | **0.727 → 0.485** | boss fights with adds collapse |
| **AAo_40 (multi-only, no boss)** | **5.70 s** | **0.727 (unchanged)** | **recommended** |

- Under AAo_40 the P90 stays the fastest ordinary-battle gun: 5.7 s against 7.7–9.5 s for the
  other classes. It keeps its identity as the crowd specialist without making the others
  pointless.
- Frozen controlled P90: 1.97 → 3.35 s, vs handgun 5.65 s and shotgun 6.00 s.
- Win rates don't change; damage taken rises from 4.7 to 28.0, in line with the other
  classes (25–29).
- Same direction under `human_reaction` (6.0 → 9.5 s) and `far_player` (4.4 → 7.2 s).
- **Mod implementation** (it fits the existing per-hit hook, nothing new to find):
  - Location: `pe_mod_effects.c` `pe_on_damage`, the entry of `Battle_StepEnemyMovement`
    (0x80028574). It already scales the attack term per hit through `atk_pm`.
  - Condition: `(turn & 0xC0u) == 0xC0u`. That's Attack All (`Battle_FillActionQueue` mode
    0xC0, as in the simulator's source table).
  - Also require at least 2 active enemy slots with HP > 0. Enemy slots are at
    `PE_ENEMY_SLOT_BASE`: 7 × 0xDC, active byte at +0, combatant at +4, enemy HP s32 at slot +4 +0x10.
  - Also require that no active slot has status2 (slot +4 +0xCC) bit 0x40000. That's the "can't
    escape" boss bit `pe_loot.c` / `pe_loot_logger.c` already use, and the logged `boss` label
    the simulator's encounters come from.
  - Then set `atk_pm = atk_pm * 400 / 1000`. This multiplies with the existing RoF 7 / 10
    boost, matching the simulator: power × hit% × 40%, before defense.
  - Add a Mod Effects menu row "Attack All power % (crowds)", default 40, with vanilla = 100.

### R-B. G3A3 base power +45 (56 → 101)

**Problem:** at Day 5 the rifle is the worst class by a wide margin. It takes 1.9× the
handgun's ordinary time and has the lowest boss win rate (0.875; 0.833 under
`human_reaction`).

| Variant | Ordinary s | Boss s | Boss win |
|---|---:|---:|---:|
| CURRENT | 34.7 | 46.5 | 0.875 |
| +30 power | 25.0 | 38.4 | 1.000 |
| +1 shot per command | 31.4 | 40.4 | 0.958 |
| +30 power and +1 shot | 21.7 | 35.6 | 1.000 |
| **+45 power** | **21.7** | **36.0** | **1.000** |

- With +45 power the G3A3 sits between the shotgun and the handgun.
  - Ordinary: 21.7 s, against 22.6 (shotgun) and 18.7 (handgun).
  - Boss: 36.0 s, against 33.0 / 36.7.
- A single table edit. Weapon-specific (the MAG is fine at Disc2).

### R-C. M203 4 base power +20 (70 → 90)

**Problem:** the D5 grenade launcher is the second-slowest class.

- Change: ordinary 28.1 → 22.5 s; boss 36.7 → 29.8 s; boss win 0.958 → 1.000.
- Under `human_reaction`: ordinary 40.4 → 31.6 s.
- Reloads per fight fall from 0.4 to 0.0.
- Weapon-specific; the HK40 is unchanged.

### R-D. Weapon switching: no change recommended yet (low priority)

- Under CURRENT's half-bar switch, switching mid-fight from MAG to P90 is slower than either
  gun alone. With AAo_40 applied:
  - crowd_switch 8.65 s vs mag_only 7.20 and p90_only 3.73.
- Free switching (no gauge cost):
  - removes the penalty (7.28 s);
  - lifts boss wins 0.875 → 1.000, but on 8 boss fights only, which is an incomplete
    scenario.
- Conclusion: switching is a convenience, not a balance lever, while one gun covers both
  roles.
- Reconsider once Disc2 bosses are complete, and after R-A, if testers want two-gun loadouts.

### Rejected

- **S1 shotgun proximity bonus:** no measurable effect on campaign battles (every CI spans 0).
- **Global Attack All cuts** (AA_50..80): see R-A.

## Not yet supported by the model (keep visible)

- **Disc2 boss balance:** the shotgun's 0.33 boss win rate stands out. But boss AI and effects
  are incomplete, so no boss-specific change is recommended.
- **Day 2–4 weapons:** the class benchmark covers only D5 and Disc2.
- **Campaign economy:** the effect of these changes on which guns players buy is not modelled.
  The economy surrogate is uncalibrated.
- **Player movement and dodging:** only the `walk` approach policy is modelled. Absolute
  incoming damage runs about 2× the log.

## Reproduce

All results use `PYTHONPATH=tools`, `--seeds 3` (class) or `--seeds 2` (frozen), and the sets
`default,human_reaction,far_player`.

- `python -m pe_weapon_sim.compare_rules --builds class --all-battles --proposal exp:AAo_40 --stages Disc2 --out pe-compare-class-allbattles-AAo40-2026-10-19`
- `python -m pe_weapon_sim.compare_rules --builds class --all-battles --proposal "exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20" --stages D5 Disc2 --out pe-compare-class-allbattles-P1-2026-10-19`
- `python -m pe_weapon_sim.compare_rules --all-battles --proposal "exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20" --stages D5 Disc2 --out pe-compare-frozen-allbattles-P1-2026-10-19`
- `python -m pe_weapon_sim.secondary_test --proposal exp:AAo_40 [--free-switch]`

Supporting runs, all kept:

- `pe-compare-class-allbattles-AAm40`, `pe-compare-frozen-allbattles-AAm40`,
  `pe-compare-class-AAm40`, `pe-compare-AAm40-attack-all`.
- `pe-compare-class-D5-{4powerp30,4powerp45,4rofp1,4powerp30_4rofp1,5powerp20}`.
- `pe-secondary-test-{AAm40,AAo40}[-freeswitch]` (all 2026-10-19).

## Update: under the serial rule, AAo_30 instead of AAo_40

The source rule from `pe-calibration-serial-2026-10-19.md`: enemies can't start attacks while
Aya's action is committed. This makes long Attack All volleys protective.

| Setup | P90 time s | Other guns time s | P90 damage | Other guns damage |
|---|---|---|---|---|
| Serial model, `logged_player_serial`, AAo_40 | 4.94 → 8.60 | 11.9–15.0 | 4.1 | 6.6–11.0 |
| Serial model, `logged_player_serial`, AAo_30 | 12.35 | 12.0–15.0 | 12.4 | 6.3–11.0 |

- With AAo_40, the P90 stays both the fastest and the safest gun, and its Disc2 boss win rate
  (0.91) is the highest.
- With AAo_30, it lands among the other classes, trading slightly more damage taken for crowd
  clearing.
- **Revised R-A: 30% per-bullet power with 2+ enemies alive, no boss battles.**
- The Day 5 buffs (R-B, R-C) are unchanged: every class takes 27–33 s.

Files: `pe-compare-class-allbattles-P1-serial-2026-10-19` and
`pe-compare-class-ord-AAo30-serial-2026-10-19`.
