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

## 6. Data first

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
