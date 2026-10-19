# Parasite Eve weapon rebalance — working document

**Status: DRAFT. Simulations are still running; nothing here is decided, built into the mod, or
tested in the game.**

Last updated: October 19, 2026. Keep this file current as results come in: it is the single place
that says what we're leaning toward and why.

## Candidate changes

| ID | Change | Current lean | Evidence so far | Still needed before deciding |
|---|---|---|---|---|
| R-A | Attack All per-bullet power cut to **40%** when 2+ enemies are alive and no boss is present | **Yes at 40%** (sweep done) | At every investment level, Attack All guns stay 1.4–1.7× faster than the handgun: P90 4.5 → 7.0–8.1 s, catalog Attack All MAG 5.5 → 8.3–9.0 s. Bosses are untouched. 35% = alternative for damage parity; 45% still near 2×; 30% overshoots | Day 2–4 Attack All guns; try in game |
| R-B | G3A3 base attack **+45** | **Yes at +45** (sweep done) | The only value that works at low investment (+35 / +40 leave it at 34 s, still slowest). +45 gives 27.5–28.9 s at every level, no overshoot (pack 24–31.5 s); the Day 5 boss loss disappears at typical / high investment | The G3A3's Day 4 use (Day 2–4 benchmark) |
| R-C | M203 4 base attack **+15** (revised from +20) | **Yes at +15** (sweep done) | +15, +20 and +25 give the same result (39 → 31.4–31.8 s; boss 57 → 49 s): +15 already crosses the breakpoint. At high investment the M203 4 is in the pack even without a buff | Frost-resistant rooms separately; Day 2–4 |
| R-D | Weapon switching cost | No change for now | Switching is a convenience while one gun covers both roles | Revisit after Disc2 bosses are reliable and if two-gun loadouts matter |

Rejected so far:
- **R-C at +20:** +15 gives the same effect with a smaller change.
- **AAo_30** (Attack All at 30%): overshoots on the calibrated model.
- **Global Attack All cuts** (any strength, always on): wreck single-target and boss use.
- **S1 shotgun proximity bonus**: no measurable effect on campaign battles.

## What the simulations have established

Three-way comparison (vanilla / current mod / mod + proposals) on the calibrated model. Report page:
<https://claude.ai/artifact/StkGFVGtDGe4dtxnE1hYUp> (private; local copy
`findings/reports/pe-weapon-rebalance-2026-10-19.html`).

### Vanilla vs the current mod
- **The mod already fixes the Day 5 grenade launcher.** The M203 4 fires frost rounds. Vanilla cuts
  elemental damage to a fifth against resistant enemies, so 60% of its Day 5 ordinary fights run
  out the clock. The mod's 80% resist makes it viable.
- **The P90's crowd dominance predates the mod.** Vanilla: 5.8 s vs 12.5–15.7 s for the other
  Disc2 classes. The mod's RoF 10 boost sharpens it to 4.9 s.
- **Disc2 got easier under the mod:** ordinary fights about 5% shorter, 10–30% less damage taken,
  more boss fights won.
- **The MAG's longer boss time in the mod is not a slowdown.** Vanilla loses 3 of 39 boss fights
  with it, and losses end early.

### Day 5 class spread (ordinary fights, calibrated player)

| Class (gun) | Vanilla | Current mod | Mod + proposals |
|---|---|---|---|
| Handgun (M9 3) | 27.4 s | 27.4 s | 27.4 s |
| Machine gun (MP5PDW) | 32.2 s | 28.5 s | 28.5 s |
| Shotgun (M500) | 32.8 s | 32.8 s | 32.8 s |
| Rifle (G3A3) | 48.7 s | 48.5 s | **28.7 s** |
| Grenade (M203 4) | 78.1 s (40% won) | 40.2 s | **31.8 s** |

### Disc2 class spread (ordinary fights, calibrated player)

| Class (gun) | Vanilla | Current mod | Mod + AA 40% | Mod + AA 30% |
|---|---|---|---|---|
| Handgun (DE50AE7) | 12.5 s | 11.9 s | 11.9 s | 11.9 s |
| Machine gun (P90) | 5.8 s | 4.9 s | **8.6 s** | 12.6 s |
| Shotgun (M10B) | 14.0 s | 13.3 s | 13.3 s | 13.3 s |
| Rifle (MAG) | 15.7 s | 14.9 s | 14.9 s | 14.9 s |
| Grenade (HK40) | 15.2 s | 14.6 s | 14.6 s | 14.6 s |

Robustness:
- The same ordering holds under the slow-menu (+75 updates per turn) and keep-distance (×1.4)
  assumption sets.
- Under slow menus, 30% gets worse (P90 15.0 s, 21.9 damage).

## How far to trust the model

- **Calibration:** replaying every logged battle, ordinary damage is 1.05× of the log
  (correlation 0.77), bosses 0.66× (0.82).
  - Aya's damage per turn matches the log in every group.
  - Energy Shot and Liberate match live casts exactly.
- **High confidence:**
  - Day 5 class ordering and the effect of R-B / R-C;
  - R-A's effect on crowds;
  - R-A doesn't touch boss fights;
  - the vanilla → mod differences in ordinary fights.
- **Medium:** absolute fight lengths. Calibrated to one player's log; real menus and movement vary.
- **Directional only:**
  - Disc2 boss numbers (the logged player used the club and held fire in four of those fights);
  - Day 2–4 weapons (not in the benchmark yet);
  - anything about which guns players buy.

## Investment: BP and the Junk economy

The class benchmark gives each gun one fixed investment:
- Day 5: +12 attack;
- Disc2: 30 / 10 / 10 bonuses plus 2 Commands and Quickdraw.

Real investment depends on BP and on the Junk economy, and both interact with the proposals.

**BP (bonus points):**
- Earned per battle as base − factor × hits taken (fewer hits, more BP); banked and paid at
  level-up; BP after the final level-up is wasted.
- One weapon stat point = 100 BP.
- The phase-3 economy runs earned about 5,400 BP per campaign and spent about 4,200. 1,300–3,400 of
  that went to attack (+13 to +34); the rest went to Active Time, capacity, range, bullets and
  armor.

**Junk economy:**
- The Mod Catalog lets any gun get Attack All or 2 / 3 Commands after a dismantle.
- Rare Tool drops, the Requisition shop and salvage raise attack investment.
- Tool transfers carry bought bonuses between guns.

**How investment touches each proposal:**
- **R-A:** applies to every Attack All volley, including catalog Attack All on non-P90 guns, which
  may out-hit the P90. Slowing the P90 also means more hits taken and so less BP: a campaign-level
  feedback the fixed benchmark can't see.
- **R-B / R-C:** base-power buffs weigh less when a lot of bought attack sits on top. The right
  size depends on the BP-attack range at Day 4–5.
- **BP floor mod** (`pe_bonus_points_floor.c`, refills unspent BP to 999 every frame): a
  Quality-of-Life convenience / cheat, **off by default** (`default_enabled = false` in its
  manifest). It's not a balance target: balance is tuned for normal BP. "BP floor on" stays at
  most as a sanity-check profile (does anything break with unlimited BP?).

**Investment profiles to sweep across** (per stage: Day 4, Day 5, Disc2):

| Profile | BP | Junk economy |
|---|---|---|
| Vanilla | earned normally, floor off | off |
| Mod, Normal | earned normally; attack-first and spread spenders | on, Normal preset |
| Mod, heavy | earned normally, attack-first | Grind preset |
| BP floor on (optional sanity check) | effectively maxed | any |

**Method:**
1. Get BP and Junk per stage from playthrough runs (the economy simulator's BP ledger and
   spending policies), re-run on the calibrated combat model so earnings reflect real hits taken.
   The logged playthrough is the anchor: its endgame gun was 0x64 with +32 attack.
2. Run the strength sweeps across all profiles, plus a catalog Attack All loadout on a non-P90 gun.
3. One playthrough-level check per proposal for the BP feedback loop.
4. A change passes if it holds across the non-floor profiles. A change that only balances at one
   investment level points to the economy knob to adjust (BP payout, Tool price, catalog access);
   record those here for the economy balancing (phase 7).

### Investment profiles: results (`pe-investment-profiles-2026-10-19`)

40 playthroughs per economy setting × player policy:
- BP anchored to the logged hits and scaled by gun strength;
- Junk economy, rare drops, Tools and the Mod Catalog;
- the BP floor is off (confirmed disabled in the user's config too).

Attack bonus on the gun carried at the end of each stage, mean (p10–p90):

| Player | Vanilla D5 | Mod Normal D5 | Vanilla Disc2 | Mod Normal Disc2 |
|---|---|---|---|---|
| Casual (A) | 17 (16–19) | 16 (15–18) | 40 | 40 (36–45) |
| Balanced (I) | 17 | 20 (15–25) | 27 | 40 (34–46) |
| Optimizer (C) | 21 | 22 (16–28) | 50 | 56 (48–65) |
| Weapon stats only | 20 | 23 (19–28) | 43 | 53 (46–58) |
| BP hoarder (logged habit) | 12 | 16 (12–20) | 36 | 66 (60–72), after a final spend |
| Farmer | 21 | 22 | 60 | 67 (62–74) |

- **Logged run (anchor):** +12 at Day 5 and +32 in Disc2, then +54 after the final spend.
- **Calibration (logged route, the run's own hits, hoarder):** +16 at Day 5 and +69 at the end,
  so the simulator overstates attack investment by about +4 and +15. The logged player also put
  part of the final 4,000 BP into other stats.
- **Relaxed vs Grind preset:** shifts attack by only ±1–3. BP dominates attack investment; the
  Junk economy mostly changes Tools, Junk and effects.
- **Strong effects:** 2 Commands is on almost every Disc2 gun (78–100%) and on none at Day 5.
  Attack All, on the other hand, ends up on many casual players' guns in the mod economy (88–98%
  of casual runs at Day 5 and Disc2, 0% in vanilla), via the catalog and found guns.
  **R-A will affect far more players than just P90 users.**
- **What this means for the sweeps:** the class benchmark's fixed investment (+12 at Day 5, +30
  in Disc2) sits at the low end of real play. Sweeps run at three levels per stage:

| Stage | Low | Typical | High |
|---|---|---|---|
| Day 5 attack bonus | +12 | +18 | +25 |
| Disc2 attack bonus | +35 | +50 | +68 |

Day 2–4: about +11 to +20.

### Rocket launchers (added 2026-10-19)

The class benchmark had no rocket class. Rockets exist only in Disc2: the AT4 (Warehouse pickup)
and the LAW80 (one of Wayne's six 300-Junk guns). The LAW80 is now an opt-in Disc2 class
(`compare_rules --classes rocket`). Results, calibrated player:

| LAW80 | Vanilla | Current mod |
|---|---|---|
| Ordinary time | 7.9 s | 6.6 s |
| Ordinary damage | 11.6 | 7.7 |
| Boss win | 0.795 | 0.872 |
| Boss time | 68 s | 56 s |

- It is the **second-fastest crowd gun** after the P90 (splash) and the **weakest boss gun**.
- **Interaction with R-A:** at 40%, the P90 drops to 8.6 s and the LAW80 (6.6 s) becomes the
  fastest crowd gun. R-A has to be judged together with rockets.
- **Ammo:** rockets come from a separate, scarce pool. A per-fight supply limit (20) changed
  nothing because supply resets each fight. Rocket balance hinges on rockets available per
  campaign (finds plus Requisition rocket purchases), which needs a campaign-level check.

### Rocket supply per campaign (done)

| | Rockets |
|---|---|
| **Demand:** LAW80 as main gun, per ordinary Disc2 fight | 1.45 |
| **Demand:** per boss fight | 4.2–4.6 |
| **Demand:** over the logged run's 105 Disc2 battles | about 190 |
| **Free supply in the logged run** (a one-time 9 rockets around room 333 in Disc2; no rocket drops, the pool was 0 before Disc2) | 9 |
| **Bought supply:** Requisition sells rockets at 20 Junk each (`pe_loot_shop.c`); an optimizer ends Disc2 on Normal with about 980 Junk to spare | at most ~50 |

**Verdict:** the LAW80 is ammo-gated.
- Mod economy: enough rockets for roughly a third of Disc2 fights, if every spare Junk goes to
  rockets.
- Vanilla: about 6 fights' worth.

It is a strong special-purpose weapon, not a main crowd gun, so its crowd speed doesn't undercut
R-A. Re-check if rocket prices drop (the Relaxed preset prices at 75%) or rockets get added to
drops.

### Strength sweeps (done, 2026-10-19)

Calibrated model; class benchmark at low / typical / high investment (Day 5 attack +12 / +18 / +25;
Disc2 +35 / +50 / +68); every logged battle, 3 seeds; Day 5 also under slow menus. Data:
`pe-sweep-{d5,d2}-*-2026-10-19`, tabulated by `report_sweeps.py` into `pe-sweeps-2026-10-19.json`.

**Damage moves in breakpoints** (hits needed per kill), so results step instead of sliding.

Day 5 ordinary fights (mod now → swept G3A3 / M203 4 buffs):

| Class | Low | Typical | High |
|---|---|---|---|
| Rifle G3A3: now | 48.5 s | 47.7 s | 45.7 s |
| Rifle: +35 / +40 / +45 | 34.0 / 34.0 / **28.9** | 34.0 / 28.9 / **28.9** | 28.9 / 28.9 / **27.5** |
| Grenade M203 4: now | 39.3 s | 39.4 s | 31.7 s |
| Grenade: +15 / +20 / +25 | **31.8** / 31.8 / 31.8 | **31.4** / 31.4 / 31.4 | **30.9** / 30.9 / 29.8 |
| Rest of the pack (handgun, machine, shotgun) | 26.5–31.5 | 25.5–26.6 | 24.2–26.4 |

Disc2 ordinary fights (Attack All strength):

| Class | Mod now | 35% | 40% | 45% |
|---|---|---|---|---|
| P90 | 4.4–4.8 s | 7.9–9.5 | **7.0–8.1** | 6.1–7.5 |
| MAG + catalog Attack All | 5.4–5.5 s | 9.1–10.7 | **8.3–9.0** | 7.4–8.4 |
| Single-target guns (unchanged) | 11.6–14.7 s | | | |
| LAW80 (ammo-gated) | 6.3–6.4 s | | | |
| Attack All guns' damage taken | 0.4 | 3.6–7.6 | **3.0–5.1** | 1.9–4.3 |
| Single-target guns' damage taken | 5.1–9.2 | | | |

- Single-target Disc2 guns barely respond to investment (plateau).
- Catalog Attack All on the MAG is as strong as the P90, which confirms R-A has to apply to every
  Attack All gun.
- Bosses are unchanged by R-A at every strength.
## Simulations still to run

Ordered by how much they could change the decisions.

0. ~~Investment profiles~~ **done** (see above). Sweeps run at low / typical / high attack
   investment per stage.
0b. ~~Rocket supply per campaign~~ **done:** the LAW80 is ammo-gated (see above).
1. ~~Strength sweeps~~ **done** (see above). Kept for reference:
   - R-A at 35 / 40 / 45%;
   - R-B at +35 / +40 / +45;
   - R-C at +15 / +20 / +25;
   - on the class benchmark (now including the LAW80) and the campaign-earned builds, all three
     assumption sets, at low / typical / high investment;
   - plus catalog Attack All on a non-P90 gun.
2. **Day 2–4 class benchmark.** The benchmark has Day 4 guns (`CLASS_GUNS['Day4']`) but no Day 2–4
   builds. Needs an Aya build per stage from the log, then the same three-way run. The G3A3 and
   the Attack All guns are used before Day 5.
3. **Disc2 bosses replaying the logged weapon turns** (club turns, weapon swaps, held fire), so boss
   balance can be judged. Also room 350's arena distances (the boss sits in the graze band a third
   of the time).
4. **Boss-specific checks:**
   - the Day 5 rifle boss loss (1 in 24, under every rule set): which fight, and is it a gun
     problem?
   - the Disc2 shotgun's 0.92 boss win rate.
5. **Two-gun loadouts and switching (R-D)** once Disc2 bosses are reliable.
6. **Economy:** whether the changes shift which guns players buy (the economy model is
   uncalibrated).
7. **In-game test** of whatever survives the sweeps: build the changes behind Mod Effects menu
   rows, play the matching fights, and compare with the predictions.

## Implementation notes (for when a change is decided)

- **R-A:**
  - Location: `pe_mod_effects.c` `pe_on_damage`, at the entry of `Battle_StepEnemyMovement`
    (0x80028574).
  - Conditions: `(turn & 0xC0) == 0xC0`; 2+ active enemy slots with HP > 0; no active slot with
    status2 bit 0x40000 (boss).
  - Effect: `atk_pm = atk_pm * 400 / 1000`.
  - Menu row: "Attack All power % (crowds)", default 40, vanilla 100.
- **R-B / R-C:** single weapon-table edits (G3A3 base attack +45, M203 4 base attack +15).
- **Reproduce the comparisons:**
  ```
  PYTHONPATH=tools python -m pe_weapon_sim.compare_rules --builds class --all-battles \
    --stages D5 Disc2 --seeds 3 --calibrated \
    --assumptions logged_player_serial,human_reaction,far_player \
    --base vanilla --proposal baseline --out pe-compare-cal-vanilla-current-2026-10-19
  ... --base current --proposal "exp:AAo_40|cfg:@G3A3.power+45,@M203_4.power+20"
  ```
  The three-way summary comes from `tools/pe_weapon_sim/report_rebalance.py`.

## Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-19 | R-A strength revised 40% → 30% | Serial-action model made long volleys protective |
| 2026-10-19 | R-A revised back to 40% | Calibrated model (contact damage, Parasite Energy, full enemy roster): 30% overshoots |
| 2026-10-19 | R-B, R-C kept | Confirmed on the calibrated model |
| 2026-10-19 | R-A 40% and R-B +45 confirmed; R-C reduced to +15 | Strength sweeps across investment levels |
| — | Nothing built or tested in game yet | Waiting on the sweeps and the Day 2–4 benchmark |

## Related files

- `findings/pe-balance-recommendations-2026-10-19.md`: full history of the recommendations.
- `findings/pe-calibration-casts-2026-10-19.md`, `findings/pe-contact-damage-2026-10-19.md`,
  `findings/pe-aya-pe-items-2026-10-19.md`: model and calibration.
- `findings/CLAUDE-CODEX-HANDOFF.md`: step-by-step log.
