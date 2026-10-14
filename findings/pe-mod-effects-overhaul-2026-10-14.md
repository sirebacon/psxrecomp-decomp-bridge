# Parasite Eve: weapon and armor effect overhaul (design draft, 2026-10-14)

Status: **draft for discussion**, nothing built. Goal: every vanilla add-on effect is a real
choice for a run, so no effect is a trap that quietly makes Aya weaker. Prompted by a
playtest: Heat Rounds on the gun made ordinary fights a struggle.

Companion docs: [`pe-loot-overhaul-design-2026-10-11.md`](pe-loot-overhaul-design-2026-10-11.md)
(Mod Catalog, prices), [`pe-loot-cascade-design-2026-10-14.md`](pe-loot-cascade-design-2026-10-14.md).

Sources: the decomp (cited by function), and community knowledge from a guide video on
Parasite Eve's equipment (2026-10-14, summarised in our own words in section 2; not quoted).

---

## 1. How the game computes a gun hit (decomp)

`Battle_StepEnemyMovement` (src/main/battle/enemy_movement.c; legacy name: it is the
damage routine for Aya's attacks on an enemy). For a normal gun shot:

1. **Per-shot power:** `attack = (stat1E / 5 + weapon power bonus) x hit% / 100`, with hit%
   by the weapon's Rate of Fire (shots per turn):

   | Shots | 1 | 2 | 3 | 5 | 7 | 10 |
   |---|---|---|---|---|---|---|
   | Per-shot % | 100 | 60 | 41 | 25 | 18 | 13 |
   | Turn total % | 100 | 120 | 123 | 125 | 126 | 130 |

2. **Defense:** each shot subtracts `enemy defense / shots`, so a whole turn subtracts the
   defense once whatever the Rate of Fire.
3. **Enemy hit reaction** (enemy core flags & 0x38000): 0x8000 → x0.3, 0x18000 → x1.5,
   0x20000 → x0.1 (armoured / weak-point types).
4. **Status rounds** (unless the enemy is immune, class 2): Cyanide (turn flag 0x400), Acid
   (0x800), Tranquilizer (0x1000). Each enemy has 2 bits per status: 0 → 50% chance, 2 →
   always, 1 or 3 → never. Cyanide sets the instant-death flag.
5. **Elements:** Heat (0x100) reads the enemy's 2 bits at status-flags-2 >> 14, Frost
   (0x200) at >> 16. Value **1 = resists → damage / 5**, **2 = weak → damage x 1.5**,
   0 = neutral → **no change**. Frost is only checked when Heat didn't already find a
   weakness, and a neutral Frost result does **not** clear a Heat resistance.
6. Minimum damage 1 (2 against x1.5 hit-reaction enemies).

Weapon effect bits (BattleCmd decode, commands.c): 1–5 Rate of Fire, 6–8 spread mode
(Random / Burst / Attack All), 9 Heat, 10 Frost, 11 Cyanide, 12 Acid, 13 Tranquilizer,
14 Counter, 15 Quickdraw, 16–17 Steal / Steal on Attack (Steal alone halves the attack),
18 Critical, 19–20 two / three commands.

**Why Heat hurt:** against a neutral enemy it adds nothing; against a resistant one every
shot loses 80%; only weak enemies gain 50%. It is a pure downside except for a few
matchups, and the game never tells you which enemies resist. Heat plus Frost doesn't fix
it: an enemy that resists Heat and is neutral to Frost still takes the 80% cut.

## 2. Community view (guide video, our summary)

- **Rate of Fire:** higher totals deal a bit more damage per turn but cost far more ammo and
  lock Aya in place until every shot is fired; 3 or 5 is the sweet spot. (The table above
  agrees: 10 shots give 130% vs 125% for 5, for twice the ammo.)
- **Spread modes (one at a time):** Burst is the favourite; Random Fire gives 1.5x shots but
  no target choice; Attack All drains ammo fast.
- **Heat / Frost:** avoid; a resistant enemy cuts damage to single digits, and some late
  enemies resist both.
- **Acid:** harmless extra damage over time. **Tranquilizer:** strong in the hospital,
  weaker later. **Cyanide:** only found in the Chrysler Building.
- **Counter** (50% to strike back when hit): rarely useful. **Quickdraw** (Aya's ATB starts
  full): easy to recommend. **Critical:** always good. **2 / 3 Commands:** best for bosses;
  3 Commands only in the Chrysler Building.
- **Armor:** the resist mods are fine niche picks; **Auto Medicine** (the guide's "auto
  heal") is a must-have; Auto Cure is optional; bag Capacity is very valuable; Max HP Up and
  Attack Up are strong; PE Burden Down is good (guides wrongly call it a debuff); **Slow
  Active Time** and **Attack Down** are pure negatives to strip off.
- **Slots:** late weapons have 7–9; the M92F has 10 but weak base stats.

## 3. Problems to fix

| Effect | Problem |
|---|---|
| Heat, Frost | No gain vs neutral, -80% vs resistant, no in-game hint; a trap |
| Heat + Frost | Doesn't take the better of the two (a resistance survives) |
| Rate of Fire 7 / 10 | +1–5% damage for 1.4–2x the ammo of 5, and longer lock-in |
| Attack All | Same total power spread over every enemy, at full ammo cost |
| Counter | 50% on being hit; low impact |
| Steal (club) | Halves club damage; Steal on Attack strictly better |
| Slow Active Time, Attack Down | Pure negatives; armor carrying them is worse than none |
| Tranquilizer, Acid | Fine early; fall off late (fine, but note) |
| Cyanide, 3 Commands, Attack Up, PE Burden Down | Chrysler-only in vanilla (sources, not balance) |

## 4. Proposals (for discussion)

### 4.1 Elements (priority: this is the one that hurts a run)

Make Heat and Frost a modest, reliable upgrade instead of a gamble:

| Enemy | Vanilla | Proposed |
|---|---|---|
| Neutral | x1.0 | **x1.15** |
| Weak | x1.5 | x1.5 |
| Resists | **x0.2** | **x0.7** |

- Heat + Frost: use whichever element is better for that enemy (resistance cleared when the
  other element is neutral or weak).
- Optional feedback: the first hit on an enemy prints "Resists Heat" / "Weak to Frost" in
  the battle message, so the player learns matchups.

### 4.2 Rate of Fire

Keep the shape (more shots = slightly more damage), but make high fire rates worth their
ammo: per-shot % for 7 → 20 (140% total), 10 → 15 (150%). Ammo cost unchanged. Or leave
damage and halve the extra ammo above 5 shots.

### 4.3 Spread modes

- Attack All: each target takes the full per-shot damage (vanilla) but ammo is charged as
  if it were Burst, so it isn't an ammo trap. Or keep ammo and give +20% damage.
- Random Fire, Burst: unchanged (Burst is already the community favourite).

### 4.4 Status rounds

- Tranquilizer, Acid, Cyanide: keep the 50% roll; add a small late-game lift, e.g. +10%
  chance per weapon slot above 6, or a guaranteed proc on the first shot of a turn. Low
  priority.

### 4.5 Counter, Steal

- Counter: 50% → 75%, and the counter shot ignores the 50% defense split (full shot).
- Steal (club only): stop halving damage, so Steal and Steal on Attack differ only in steal
  chance (Steal higher). Or merge into one effect.

### 4.6 Negative armor effects: give them a trade-off

| Effect | Vanilla | Proposed |
|---|---|---|
| Slow Active Time | ATB slower | ATB 15% slower, **damage taken -20%** ("heavy armor") |
| Attack Down | Damage dealt down | Damage dealt -15%, **critical evasion +25% / PE defense +15%** |

So armor that comes with them stays usable, and a tank build is possible. (The Mod Catalog
already removes any effect for free; this is about making them worth keeping sometimes.)

### 4.7 Not changing

Quickdraw, Critical, 2 / 3 Commands, Auto Medicine, Auto Cure, Capacity, Max HP Up, Attack
Up, PE Burden Down, the resist mods: already good or a fair niche.

## 5. How it could be built

Function-entry hooks can only rewrite arguments at a function's start, not change a
result in the middle, so there are two routes:

- **No new hook (data rewrite):** at battle start and while an enemy is alive, rewrite its
  element bits (resist → neutral where the new rule says so) and give Aya's weapon action a
  power bonus while Heat or Frost is installed (the x1.15 neutral bonus). Fast and safe, but
  the resist case becomes x1.15 (neutral), not x0.7; the proposed table can only be matched
  roughly.
- **New entry hook on the damage routine** (`Battle_StepEnemyMovement`, a0 = target entity):
  before each hit, set that enemy's element bits and the action's power bonus for exactly
  this hit (e.g. resist → neutral plus a -30% power bonus = x0.7), restored after. Matches
  the table exactly. Cost: a `game.toml` hook change (new overlay cache folder; copy the
  movie player DLL, see the FMV gotcha) and careful per-hit restore.

Other proposals (Rate of Fire %, Counter, armor trade-offs) need their own hooks or table
patches (the hit% table is a local array in the damage routine; the action's turn word and
power bonus are per action), to be scoped once the direction is agreed.

## 6. Enemy data

**Wiki extract (2026-10-14):** [data/pe-enemies-wiki-2026-10-14.csv](data/pe-enemies-wiki-2026-10-14.csv),
80 stat blocks (37 creatures, one row per location variant): level, HP, EXP, BP, the five
rounds (Cyanide, Acid, Tranquilizer, Heat, Freeze) and Confuse / Steal / Scan / Slow /
Escape, each Strong / Average / Weak, plus drops, steals and location. Source: the Parasite
Eve Wiki (parasiteeve.fandom.com, Category:Parasite Eve creatures), CC-BY-SA; pulled through
the wiki's API. Strong is read as the game's "resists / immune" value, Weak as "weak / always",
Average as neutral / 50%; to be confirmed against the game (below). No defense or hit-reaction
type on the wiki: those come from the game (the play log's enemy row already logs defense).

Main game only (46 variants, Chrysler Building excluded):

| Round | Strong | Average | Weak |
|---|---|---|---|
| Heat | 12 | 22 | 11 |
| Freeze | 6 | 27 | 12 |
| Cyanide | 31 | 9 | 5 |
| Acid | 25 | 18 | 2 |
| Tranquilizer | 35 | 7 | 3 |

What it means under the vanilla rules:

- **Heat is a net loss:** a quarter of enemies resist it (x0.2) and a quarter are weak (x1.5),
  so the average multiplier is ~0.90, and the resisted fights take five times as long. Heat-
  resistant enemies include the Day 2 snakes, the Carnegie / Central Park and Liberty Island
  Eve fights, Chinatown cats and snakes, hospital Flymen, and the museum's armadillos,
  chameleons and troodons.
- **Freeze is slightly positive** (~1.03): few resist it, a quarter are weak.
- **Heat + Freeze** still takes the x0.2 cut on 4 main-game variants (resist Heat, Freeze not
  weak).
- **Status rounds are mostly dead:** Tranquilizer works on 10 of 45 (35 immune), Cyanide on 14,
  Acid on 20. The video's praise for Tranquilizer in the hospital fits: Bacteria are weak to it
  and Flymen / Mixedmen average.

**Confirm in the game:** log every enemy's Heat / Freeze bits and status bits on the play
log's enemy row (status flags 2 at enemy +0xCC: Heat >> 14, Freeze >> 16, Cyanide & 3, Acid
>> 2, Tranquilizer >> 4) and check a few against the wiki rows; then use the game values where
they differ.

## 6b. Data first

Before tuning, log every enemy's Heat / Frost bits and status bits on the play log's
`enemy` row (status flags 2 at enemy +0xCC: Heat >> 14, Frost >> 16, Cyanide & 3, Acid >> 2,
Tranquilizer >> 4). One playthrough then shows how many enemies resist each element by
area, and the elemental numbers above can be set from real data.

## 7. Open questions

1. Elements: is x1.15 / x1.5 / x0.7 the right feel, or should resistance be milder still
   (x0.85)?
2. Show matchups in battle ("Resists Heat")?
3. Rate of Fire: more damage at 7 / 10, or less ammo?
4. Negative armor effects: trade-offs as in 4.6, or leave them as negatives?
5. Exact build (new damage hook) or the quick data rewrite first?

## 8. Simulation (2026-10-14)

Tool: [	ools/pe_mod_sim.py](../tools/pe_mod_sim.py) (`python tools/pe_mod_sim.py --fights 2000`).
Monte Carlo fights against the wiki roster, main game only (45 variants), 2,000 fights per area
per effect: groups of 1–3 regular enemies per area, bosses alone. Baseline: a Rate of Fire 3 gun
with no other effect; each row adds one effect. Numbers are change vs the baseline in **time
to clear / ammo used / enemy attacks taken** (lower is better).

**Correction from the decomp (setup.c `Battle_CheckEvasion`):** the x0.3 / x1.5 / x0.1
multipliers in section 1 are **hit quality**, not armor: distance over the gun's range picks
miss (> 180%), graze x0.3 (100–180%, 80% / 50% / 25% of the time by band), or a hit (≤ 100%)
that is a **critical x1.5** 5% (80–100%), 20% (50–80%) or 50% (< 50%) of the time; the
**Critical effect adds 20 points**. x0.1 is the splash on secondary targets.

Main-game results, averaged over Days 1–5 (bosses where they differ):

| Effect | Vanilla | Proposed (tuned) | Verdict |
|---|---|---|---|
| RoF 1 / 2 | +38% / +2% time, -51% / -30% ammo | same | fine: the ammo-saver |
| RoF 5 | ~+1% time, +60% ammo | same | sidegrade (vanilla ok) |
| RoF 7 / 10 | **+6% / +9% slower, +120% / +200% ammo** | -9% / -11% time, +65% / +90% ammo | was a trap; now a speed-for-ammo choice |
| Random Fire | -44% time, -9% ammo | same | very strong *if* A2 holds (to verify) |
| Burst | -17% all three | same | good (multi-enemy only) |
| Attack All | -38% time but +5% ammo | -38% time, -38% ammo | proposal makes it a clear upgrade; maybe too good |
| **Heat** | **+16% to +106% slower** (+39% bosses) | -8% to -19% (Day 1 +5%) | trap → modest upgrade |
| Frost | -22% … **+135%** (hospital) | -6% to -27% | gamble → upgrade |
| Heat + Frost | -30% … +34% bosses | -11% to -30% | best-of-two fixes it |
| Cyanide | -11% to -49% (A6) | -27% to -51% | strong early; check A6 |
| Acid | -2% to -7% | -11% to -15% | weak → useful |
| Tranquilizer | ~0% time, -2% to -18% hits | **-33% to -39% hits taken** | dead → the safety pick |
| Counter | -1% to -8% | -6% to -12% | weak → small but real |
| Quickdraw | -18% time, -23% hits | same | good as is |
| Critical | -2% to -7% | -5% to -12% (bosses -12%) | weak → solid |
| 2 / 3 Commands | -43% / -57% | same | dominant *if* commands are free (verify) |

Tuned proposed values: elements x1.15 neutral / x1.5 weak / **x0.8** resist, best of Heat and
Frost; RoF 7 → 20%, 10 → 15% per shot and shots past the 5th cost half a round; Attack All
charges one target's ammo; status rounds Strong 20% / Average 60% / Weak always (bosses stay
immune), poison 6% max HP a turn; Counter 75% for a half-power shot; Critical +40 points.
(First pass had Counter at full power: -34%, too strong.)

**Assumptions to verify before building** (marked in the tool):
A1 defense = 1.6 x enemy level and Aya's attack scaled so a plain shot kills an average foe
in ~2.5 hits; A2 Random Fire = 1.5x shots at the same per-shot %; A3 fight distance 30–125% of
range; A4 poison tick 4% max HP; A5 ATB 1.0 per turn plus firing time, enemies every 1.0–1.4;
A6 a Cyanide proc kills 1 in 4 times; A7 Tranquilizer skips 2 enemy turns; A8 Burst hits each
other enemy 40% of the time; A9 75% of enemy attacks land; Commands assumed to add full extra
actions per ATB bar.

Next: read Random Fire, the command effects, Cyanide, poison and Stop in the decomp, re-run, then
pick final numbers. Armor effects aren't in this sim (they act on Aya's survival and the bag);
Slow Active Time and Attack Down trade-offs need an enemy-damage model.

### 8.1 Mechanics verified in the decomp (2026-10-14, second pass)

| Mechanic | Finding | Source |
|---|---|---|
| Random Fire | Rate of Fire x 3 / 2 shots, each at a random target, at the base per-shot %; defense still split by the base Rate of Fire | turn.c `Battle_FillActionQueue` (mode 0x40) |
| Attack All | one queue entry per target | same (mode 0xC0) |
| 2 / 3 Commands | 2 or 3 actions entered and run on one ATB bar (turn slots, turn word >> 4) | turn.c `Battle_StepEnemyTurn`, setup.c |
| Cyanide | a proc sets the instant-death flag; the enemy's HP is set to -1 at its next update: **every proc kills**; each shot rolls (50% vs Average, always vs Weak, never vs Strong) | turn.c `Battle_UpdateEnemy`, enemy_movement.c |
| Acid (poison) | every 30 ticks the enemy loses its own fixed `periodicDamage` (enemy +0x96) | turn.c `Battle_UpdateEnemy` |
| Tranquilizer (Stop) | a counter of **3**, counted down each time the enemy's turn comes round; the enemy skips its actions meanwhile | turn.c `Battle_UpdateEnemy` |
| Enemy ATB | charge per tick `chargeStep` (enemy +0x8E), turn at 9000; Slow takes 40% off | turn.c |
| Critical | +20 points on the distance-based critical chance (critical = x1.5) | setup.c `Battle_CheckEvasion` |

The play log now records each enemy's resist bits, `periodicDamage` and `chargeStep` on its
`enemy` row (PE `5d76fdf`), so poison strength and enemy speed can replace A4 / A5 after a
session.

Re-run with these (A2, A6, A7 replaced by the real rules):

- **Random Fire** is -20 to -24% time at about the same ammo: good as is (the first pass
  overstated it).
- **Cyanide** is the strongest effect early: -79% time on Day 1, -56% Day 2, -33% Day 4, -17%
  Day 5, nothing on bosses. It must **keep vanilla chances** (Strong stays immune); the
  status-round boost applies to Acid and Tranquilizer only. In vanilla it only exists in the
  Chrysler Building; if the Mod Catalog ever offers it earlier, it needs a price to match.
- 2 / 3 Commands confirmed as extra actions on one bar: -43% / -57%, the best effects; fine for
  late, rare unlocks.

### 8.2 Recommended changes (current)

| Effect | Change | Simulated result (Days 1–5) |
|---|---|---|
| Heat, Frost | x1.15 neutral / x1.5 weak / x0.8 resist; Heat + Frost takes the better | Heat -8 to -19% time (Day 1 +5%), Frost -6 to -27%, both -11 to -30% |
| RoF 7 / 10 | per shot 20% / 15%; shots past the 5th cost half a round | -6 to -12% time for +60–90% ammo (was slower) |
| Attack All | ammo charged as for one target | -38% time and ammo (watch: maybe too good; alternative +20% damage instead) |
| Acid | Strong 20% / Average 60%; poison 1.5x | -11 to -15% (was -2 to -7%) |
| Tranquilizer | Strong 20% / Average 60% | -33 to -41% hits taken (was ~0) |
| Counter | 75% chance, half-power return shot | -6 to -12% (was -1 to -8%) |
| Critical | +40 points | -5 to -12%, bosses -12% (was -2 to -7%) |
| Random Fire, Burst, Quickdraw, Cyanide, 2 / 3 Commands, RoF 1–5 | unchanged | already useful |

Still open: armor effects (need an enemy-damage model), poison and enemy speed from the new
log fields, and the build route (section 5).

### 8.3 More mechanics from the decomp (third pass)

| Effect | How it really works | Source |
|---|---|---|
| Quickdraw | at battle start, Aya's ATB starts full with a chance of `stat22` % (her speed stat) | battle/context.c (turn word 0x10000) |
| Aya's ATB | charge per tick = `stat22` x weapon factor / 10 (factors 10 / 8 / 10 / 8 / 8 / 4 / 10 / 20 by action type), full at 9000 | battle/enemy_actions.c `scaledOffense` |
| Counter | when an enemy hits Aya, a counter-attack fires with a chance set by Aya's agility (`g_AyaStatAgility`, A) and her rank vs the attacker's: higher rank A/1000, same rank 3A/5000, one below 3A/10000, lower A/5000. **Not a flat 50%**, as guides say | battle/context.c (misnamed `Battle_RollEnemySpawn`), entity/combat.c |
| Burst | hits every enemy inside a ~90° cone ahead of Aya (angle window of 0x400 out of 0x1000) | battle/attack.c `Battle_ResolveHitOnTimer` |
| Max HP Up | max HP x 23 / 20 (+15%) | battle/commands.c `BattleCmd_LoadWeaponModifiers`, aya/stats.c |
| Attack Up / Attack Down | Aya's offense read from her level table **2 levels higher / lower** | same |
| Slow Active Time | `stat22` read **2 levels lower**: slower ATB **and** a lower Quickdraw chance | same |
| Capacity +1 / +2 / +4 | bag bonus slots | same |

So Slow Active Time and Attack Down are "two levels of speed / offense", and their real size,
like Counter's chance, comes from Aya's level table (`*(u32*)0x800A803C + 0x800A8028`, 0x18 a
level: HP, offense, defense, `stat22`, ...) and `g_AyaStatAgility`. Next: read those from the
running game, then model Counter, Quickdraw, Slow Active Time and the Attack mods with real
numbers. Per-enemy `periodicDamage` (poison) and `chargeStep` (speed) live in the game's enemy
data files, not in code: the new play-log fields capture them.
