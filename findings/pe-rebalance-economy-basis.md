# Parasite Eve rebalance + economy mod — design basis

**Status:** basis for the rebalance and economy mod, from simulation only. Nothing here has been
built into the mod or tested in the game. Every change is meant to sit behind a Mod Effects
toggle, with the vanilla value one click away.

October 19, 2026. Working notes and the full history are in `pe-rebalance-working-document.md`;
this document is the agreed outcome.

---

## 1. Summary

| ID | Area | Change | Why |
|---|---|---|---|
| **R-A** | Weapons / mods | **Attack All: at most 75% of a target's max HP per turn**, ordinary fights with 2+ enemies alive (bosses exempt) | Attack All is the strongest mod at every stage (−48% fight time at Day 5; the P90 clears Disc2 crowds 2.6× faster than any other class). The cap keeps Attack All guns about 1.2–1.5× faster than without it, at every stage and investment level |
| **R-B** | Weapons | **G3A3 base attack +45** | The slowest class at Day 4–5 (about 1.8× the pack). +45 is the only value that fixes it at low investment and never overshoots at high investment |
| **R-C** | Weapons | **M203 4 base attack +15** | Second slowest at Day 5; +15 crosses the same breakpoint as +20 / +25 |
| **R-E** | Mods | **Installed RoF 5 / 7 / 10 become a real upgrade:** volley 200% of one shot (40 / 29 / 20% per bullet), follow animation at most 4 frames, per-shot hold removed. Installed mods only; built-in RoF and RoF 2 / 3 unchanged | RoF 5 / 7 / 10 currently make almost every gun slower (+8 to +25%), in vanilla and the current mod. Players read "more bullets" as an upgrade |
| PE | Parasite Energy | **Keep the mod's PE changes** (half-bar quick powers and items, heals 15 / 30 / 65% of max HP) | They help (vanilla PE costs Disc2 bosses +6 s and +58 HP per fight). The exact heal percentages are not a balance lever |
| Econ | Economy mod | **Keep the Normal preset numbers.** Keep rockets at 20 Junk. Open item: a late-game Junk sink or Disc2 taper | First Wayne gun lands at Day 5 on Normal (target: Day 4–5). The LAW80 stays ammo-gated. About 1,000 Junk is left unspent at the end on Normal |
| Keep | Mods | The mod's element, status, Critical and Quickdraw changes | Vanilla Heat / Frost slow Day 5 fights by 36% / 107% (resist ÷5); the mod fixes that. Critical goes from marginal to a real boss mod |

Rejected along the way: Attack All power cuts of any strength (they floor weak guns at 1 damage
from Day 2–5), post-defense or crowd-scaled cuts (they don't bite the overkilling Disc2 P90),
R-C at +20, the shotgun proximity bonus, and power-only RoF fixes (even 225% volleys don't make
RoF 7 / 10 worth taking).

---

## 2. How the numbers were produced

**Simulator.** Combat rebuilt from the decompiled game (`tools/pe_weapon_sim`):
- Aya's offense, defense, statuses, Parasite Energy and items all come from game code.
- Every enemy in the logged playthrough resolves to its own room-script attacks.
- Body-contact damage, scripted boss HP and untargetable boss cores are modelled.

**Calibration against the logged playthrough** (every won battle replayed):
- Ordinary-fight damage: 1.05× of the log (correlation 0.77).
- Bosses: 0.66× (correlation 0.82).
- Aya's damage per turn matches the log in every group.
- Energy Shot and Liberate match live casts exactly.

**Comparisons are paired:** vanilla, current mod and proposal fight the same battles with the
same seeds and builds.

**Coverage, start to finish:**

| Stage | Battles | Builds |
|---|---|---|
| Day 1 | 13 logged | Calibration only (handguns, tiny damage) |
| Day 2–4 | 38 logged | Each battle's own logged Aya (level, armor) with the Day 4 class guns |
| Day 5 | 18 | Class benchmark |
| Disc2 | 105 (92 ordinary, 13 boss) | Class benchmark, including the LAW80 rocket launcher and a catalog Attack All MAG |

Every class is also tested with a catalog-installed Attack All.

**Investment profiles.** Economy simulator, 40 playthroughs per economy preset × player type;
BP anchored to the logged hits. Sweeps run at the low / typical / high attack bonus players
actually reach:

| Stage | Low | Typical | High |
|---|---|---|---|
| Day 2–4 attack bonus | +9 | +15 | +20 |
| Day 5 attack bonus | +12 | +18 | +25 |
| Disc2 attack bonus | +35 | +50 | +68 |

**Player assumptions.** Calibrated player (1 s paused menu per turn); the slow-menu and
keep-distance alternatives were checked for the key results.

**Confidence:**
- High: the ordering of classes and mods, and the direction and size of each change in
  ordinary fights at every stage.
- Medium: absolute fight lengths (one player's log).
- Directional only: Disc2 boss absolutes (the logged player used the club and held fire in four
  boss fights).

---

## 3. Weapons

### R-A — Attack All per-turn HP cap (75%)

- **Rule:** in an ordinary fight with 2+ live enemies, Attack All can't take more than 75% of a
  target's max HP within one turn. Boss fights, and fights down to one enemy, are unaffected.
- **Effect:** a crowd needs at least two Attack All turns, while single-target guns need a turn
  per enemy.

Ordinary fight time, current mod → with R-A (single-target gun shown for reference), typical
investment:

| Stage | Gun | Without Attack All | With Attack All, now | With Attack All + R-A |
|---|---|---|---|---|
| Day 2–4 | Handgun | 22.7 s | 12.3 s | **18.7 s** |
| Day 2–4 | Machine gun | 22.3 s | 14.8 s | **18.5 s** |
| Day 2–4 | Rifle (with R-B) | 25.2 s | 16.5 s | **19.8 s** |
| Day 2–4 | Grenade | 28.1 s | 16.2 s | **23.9 s** |
| Day 5 | Handgun (M9 3) | 26.0 s | 12.6 s | **24.9 s** |
| Day 5 | Machine gun (MP5PDW) | 25.5 s | 12.3 s | **21.0 s** |
| Day 5 | Rifle (G3A3, with R-B) | 28.9 s | 23.2 s | **20.3 s** |
| Day 5 | Shotgun (M500) | 26.6 s | 17.4 s | **27.3 s** (gives up its Burst) |
| Day 5 | Grenade (M203 4, with R-C) | 31.4 s | 22.5 s | **27.7 s** |
| Disc2 | P90 (built-in Attack All) | — | 4.5 s | **7.6 s** |
| Disc2 | MAG + catalog Attack All | 14.7 s (plain MAG) | 5.5 s | **7.9 s** |
| Disc2 | Single-target guns | 11.7–14.7 s | | |

- Low and high investment give the same picture.
- Boss fights are unchanged (Attack All keeps its advantage against bosses with adds).
- Attack All guns take more damage than now, but still no more than single-target guns.

**Why a cap instead of a power cut:**
- A flat attack cut (the earlier R-A at 40%) is subtracted before defense. At Day 2–5 that drops
  weak guns' bullets to the 1-damage floor: Day 5 Attack All guns became 1.5–3.5× slower than
  without it, and the rifle hit the time cap.
- Post-defense and crowd-scaled cuts fix Day 5 but don't bite in Disc2, where the P90 overkills
  every enemy in one volley.
- The cap targets overkill directly and behaves the same at every stage.

**Mod implementation sketch** (to verify live; it is the only part needing new mod logic):
- Location: the existing `pe_on_damage` hook at `Battle_StepEnemyMovement` (0x80028574) already
  sees each hit's target and Attack All (`(turn & 0xC0) == 0xC0`).
- Per action, record each target's HP when the action starts.
- At each hit, if the target has already lost 75% of its max HP this action (and 2+ enemies are
  alive, no boss bit 0x40000), restore the HP above that line. Equivalently, lower `atk_pm` so
  the hit can't cross it.
- The last hit of a volley needs a check on the next battle update (the existing `Battle_Update`
  hook).
- Menu row: "Attack All crowd cap %", default 75, vanilla 100 (off).

### R-B — G3A3 base attack +45 · R-C — M203 4 base attack +15

Single weapon-table edits; no other gun changes.

**Rifle G3A3:**

| | Low | Typical | High |
|---|---|---|---|
| Day 2–4 | 34.6 → 25.2 s | 32.7 → 25.2 s | 30.5 → 25.2 s |
| Day 5 ordinary | 48.5 → 28.9 s | 47.7 → 28.9 s | 45.7 → 27.5 s |
| Day 5 bosses | 78.6 → 64.6 s | 75.1 → 62.9 s (loss gone) | 73.1 → 60.6 s (loss gone) |

The Day 2–4 boss fights go from 83–92 s to 54–59 s.

**Grenade M203 4, Day 5 ordinary:** 39 → 31.4–31.8 s at low / typical investment. At high
investment it's already fine (31.7 → 30.9 s).

**Day 5 pack after R-B / R-C:**

| | Low | Typical | High |
|---|---|---|---|
| All classes | 26.5–31.8 s | 25.5–31.4 s | 24.2–30.9 s |
| Range before (rifle slowest) | 26.5–48.5 s | 25.5–47.7 s | 24.2–45.7 s |

**Why these numbers:** damage moves in breakpoints (hits per kill).
- Rifle: +35 / +40 leave the G3A3 at 34 s, still the slowest, at low investment. Only +45 works
  at every level.
- Grenade: +15 / +20 / +25 give identical results.

### Rocket launchers (no change)

- The LAW80 (Wayne) and AT4 (Disc2 Warehouse) are the second-fastest crowd guns (6.3 s, splash)
  and the weakest boss guns (87% boss wins).
- **Ammo-gated:**
  - a LAW80 main gun needs about 190 rockets over Disc2;
  - the game gives 9 for free;
  - rockets cost 20 Junk each in the shop, enough for about a third of Disc2 fights on Normal.
- Keep the rocket price. Re-check if rockets get cheaper or start dropping.

---

## 4. Mods

### Value of each mod on its own (current mod, typical investment)

Change in fight time vs no mod (negative = faster), mean over classes:

| Mod | Day 5 ordinary | Day 5 bosses | Disc2 ordinary | Disc2 bosses |
|---|---|---|---|---|
| Attack All | −48% (R-A caps it) | −8% | −27% | −16% |
| Quickdraw | −16% | −10% | **−35%** | −10% |
| 2 Commands | −17% | −16% | −7% | **−37%** |
| 3 Commands | −17% | −23% | −6% | **−48%** |
| Cyanide | −15% | −5% | −5% | 0% (immune) |
| Burst | −14% | +6% | −1% | −1% |
| Heat | −10% (vanilla +36%) | −9% | +1% | −11% |
| Critical | −6% | −12% | −7% | −12% |
| Counter | −6% | −3% | −10% | −15% |
| Frost | +7% (vanilla +107%) | −4% | −5% | −12% |
| RoF 5 / 7 / 10 now | +8 / +8 / +25% | +17 / +4 / +12% | +13 / +15 / +25% | +3 / +3 / +9% |
| **RoF 5 / 7 / 10 with R-E** | **−11 / −14 / −5%** | +14 (\*) / **−11 / +3%** | +2 / +1 / +6% | **−14 / −19 / −16%** |

\* Installing RoF 5 over the MP5PDW's built-in RoF 7 is a downgrade; that single case drives
the figure.

**Healthy roles:** Commands are boss mods, Quickdraw is the crowd mod, Critical and Counter are
boss support, elements are now worth taking. The mod's element, status and Critical changes
(element resist 80%, neutral ×1.15, status 60%, critical conversion) are confirmed.

### R-E — installed RoF 5 / 7 / 10 as a general upgrade

**The problem.** Each extra bullet replays the "follow" animation, and its length depends on
the gun type:

| Gun type | Follow frames per extra bullet |
|---|---|
| Shotgun | 30 |
| Grenade | 25 |
| Rifle | 15 |
| Handgun | 10 (+5 hold) |
| Rocket | 10 (+20 hold) |
| Machine gun | 3 |

So high RoF only works on machine guns. More power alone can't fix it (a 225% volley still
leaves RoF 7 / 10 slower).

**The rule, for installed RoF 5 / 7 / 10 mods only:**
- volley power 200% of one shot: 40 / 29 / 20% per bullet (now 25 / 20 / 15%);
- the follow animation plays in at most 4 frames (never shorter than the hit frame);
- the per-shot hold is removed.

Built-in RoF (P90, MP5PDW, …) and RoF 2 / 3 are unchanged, so the class balance above is
unaffected.

**Mod implementation sketch** (verify live):
- Power: the existing `pe_on_damage` per-hit `atk_pm` scaling, applied when the equipped gun's
  installed mods include the RoF effect.
- Speed: scale Aya's animation step during the volley (the mechanism the battle-start speed
  feature already uses), with factor = the kind's follow frames ÷ 4.
- Hold: temporarily zero the kind's `per` byte in `g_BattleActionAnimRows` (0x800106A4) during
  the volley.
- Menu row: "RoF mods: fast volleys", default on.

### Watch list (no change proposed)

- 3 Commands barely beats 2 Commands, except against Disc2 bosses.
- Frost is still slightly negative at Day 5 (frost-resistant enemies).
- Random fire hurts the shotgun (+35%).

---

## 5. Parasite Energy

**Mod changes kept:** half-bar quick powers and items; Heal 1 / 2 / 3 restore 15 / 30 / 65% of
max HP (never less than vanilla).

| Isolated test (mod combat rules) | Day 2–4 | Day 5 | Disc2 bosses |
|---|---|---|---|
| Vanilla PE instead of the mod's | +1 s, +2 HP per ordinary fight, 0.8% deaths; bosses +5 s, +37 HP | no change | +6 s, +58 HP per fight |
| Heal % variants (10–20 / 25–40 / 50–65) | no change | no change | within noise |

- The heal percentages rarely matter: at Day 2–4 max HP (150–250) they land close to vanilla's
  flat heals, and the generic player heals only below half HP.
- Keep 15 / 30 / 65.

**Design note (source rule, not a change):** Haste cuts Aya's defense term to 30% while active.
It trades speed for damage taken, and it matters for boss fights.

---

## 6. Economy mod

**BP (bonus points):**
- They drive attack investment: 1,300–3,400 BP per campaign goes to attack, about +13 to +34
  levels.
- The Junk presets move attack by only ±1–3.
- Balance is tuned for normal BP. The BP floor (refill to 999) is a convenience cheat, off by
  default and off in the user's config.

**Junk left at the end of each stage** (weapon optimizer; casual players hoard more):

| Preset | Day 2–4 | Day 5 | Disc2 | First Wayne gun (300 Junk) |
|---|---|---|---|---|
| Relaxed | ~130 (casual 500) | ~520 | ~1,800 | Day 4–5 (casual hoarders Day 4) |
| **Normal** | ~70 (casual 380) | ~340 | ~1,000 | **Day 5** (design target Day 4–5) |
| Grind | ~50 | ~275 | ~500 | mostly Disc2 |
| Vanilla | — | — | — | needs 300 vanilla Junk (the logged run found about 111) |

**Tools held:** Normal about 1.5 at Day 2–5 and 5.5 in Disc2; Relaxed 2–3 / 7; Grind 0.5–1 / 4.

**Catalog effects:**
- Attack All reaches 88–98% of casual players' guns from Day 5 on; R-A covers it.
- 2 Commands is on almost every Disc2 gun.

**Decisions:**
- Keep the Normal preset as default.
- Keep the Tool price cap (40 + 10 per purchase, max 100) and the rocket price (20).
- **Open:**
  - late-game Junk surplus (about 1,000 on Normal, 1,800 on Relaxed). Options: a Disc2-only Junk
    taper, or a late sink (e.g. Super Tool or premium Codex installs). Needs one economy run
    once a direction is picked.
  - the simulated players buy Tools but few consumables, so real surplus will be somewhat lower.

**Interaction with the rebalance:**
- R-A makes Attack All players take a little more damage, so slightly fewer BP (BP = base − hits
  taken). The effect is small next to the level-up BP flow.
- R-B / R-C make two weak guns viable buys.
- R-E makes RoF mods worth spending Codex installs and Tools on.

---

## 7. Start-to-finish check

| Stage | What was verified |
|---|---|
| Day 1 | Calibration only: tiny damage, handguns. Nothing in the package changes Day 1 guns except catalog Attack All (none at Day 1) |
| Day 2–4 | Rifle and Attack All fixed at every investment level; wins unchanged or better; bosses not worse |
| Day 5 | Every class at 24–32 s in ordinary fights at every investment level; rifle boss loss gone; Attack All 1.0–1.5× |
| Disc2 | Attack All guns about 1.5× single-target; bosses unchanged; LAW80 ammo-gated; RoF mods now a boss upgrade |
| Economy | First Wayne gun on target (Day 5, Normal); BP normal; BP floor off |

**Remaining risks:**
- Disc2 boss absolutes (directional).
- The three implementation sketches (R-A cap, R-E speed / hold) need live verification.
- Economy-model players are simplified.
- One logged playthrough anchors behaviour.

---

## 8. Next steps (when the user decides to build)

1. Build R-B and R-C (table edits), then R-A, then R-E, each behind a Mod Effects row
   (vanilla = off).
2. In-game check per change using the matching save states:
   - Day 4 / Day 5 rifle and grenade fights;
   - a Disc2 crowd with the P90 / MAG Attack All;
   - a Day 5 crowd with a catalog Attack All gun;
   - a RoF 7 install on a handgun / rifle.

   Compare fight length with the predictions above.
3. Decide the late-game Junk sink, then run the economy check.
4. Re-run `calibrate_logged` and the class benchmarks after any change to the simulator.

---

## 9. Reproduce

All from the bridge repo with `PYTHONPATH=tools`:

- **Final package:** `compare_rules --builds class|classlog --calibrated --invest low|typical|high
  --base current --proposal "exp:AAc_75+RoFE|cfg:@G3A3.power+45,@M203_4.power+15"`.
  Outputs `pe-final-{d24,d5,d2}-{low,typical,high}`.
- **Vanilla → mod:** `--base vanilla --proposal baseline` (`pe-compare-cal-*`, `pe-final-d24-vanilla-current`).
- **Mod values:** `mod_values --stage D5|Disc2 --rules current|vanilla|exp:RoFE`.
- **Sweeps:** `pe-sweep-*` (R-A power / post-defense / crowd / cap variants, R-B / R-C strengths),
  `pe-mod-values-*-rof*` (R-E variants).
- **PE study:** `pe-pestudy-*`.
- **Investment profiles:** `economy.run_profiles`.
- **Report page** (earlier package, vanilla / mod / proposal charts):
  `findings/reports/pe-weapon-rebalance-2026-10-19.html`.
