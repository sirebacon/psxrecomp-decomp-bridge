# Parasite Eve: weapon class benchmark (2026-10-17)

Phases 2-4 and 8 (vanilla vs current). Simulator `tools/pe_weapon_sim` (audit and validation:
[pe-weapon-simulation-audit-2026-10-17.md](pe-weapon-simulation-audit-2026-10-17.md),
[pe-weapon-mechanics-validation-2026-10-17.md](pe-weapon-mechanics-validation-2026-10-17.md)).
Raw results: `findings/data/pe-weapon-benchmark-2026-10-17.json`; tables:
`python -m pe_weapon_sim.report_tables <json> classes`. 300 fights per cell, common random numbers
(every loadout meets the same enemies and seeds), 95% CI of the mean clear time ~ +/-3-6%.

These are simulator results, not gameplay facts. Absolute seconds depend on assumed animation
and enemy timing; class *ratios* were checked against those assumptions (section 5).

## 1. Encounters

| Encounter | What it tests | Data |
|---|---|---|
| close normal | 1-3 area enemies | log distance profile "normal" (mean 703 units) |
| medium mobile | 1-2 enemies that move every action | "boss" profile (934) |
| groups | 3-4 enemies | "normal" |
| keep-away boss | the area's biggest boss at room-156 distances | "keepaway" (1188) |
| stationary boss | same boss close (normal x0.8) | |
| 6 s window | damage dealt in a 6 s opening | "boss" |
| Day 5 scripted boss | 450 real HP, defense 33, 3 attacking helpers, keep-away | fitted to the 3 logged attempts |
| endurance | 3 fights of 2, magazine carried over | |

Metrics per cell: clear time (mean, median, p10, p90, CI), damage taken, hits taken, rounds,
reloads, crit / graze / miss shares, turns out of range, status applications, overkill.
In this model damage taken tracks clear time almost 1:1 (enemy pressure is time-based), so
"slower" means "takes proportionally more damage"; the Pareto set therefore reduces to clear time
vs ammo vs investment (see build diversity report).

## 2. Results by stage (current rules; +x% = slower than the best class; geo-mean over encounters)

**Day 3, best gun per class (realistic: Day 3 boosters, mods from the Day 3 pool):**

| Class | Gun + mods | close | groups | keep-away | stat. boss | geo-mean |
|---|---|---|---|---|---|---|
| handgun | G19 Frost+Burst | 3.5 s (best) | 4.9 (best) | +49% | +23% | **+17%** |
| rifle | SG550 Frost | +21% | +52% | 10.9 s (best) | +8% | **+13%** |
| machine | M11 | +19% | +49% | +68% | 8.0 s (best) | **+53%** |

**Day 4, best gun per class:**

| Class | Gun + mods | close | groups | keep-away | stat. boss | Day 5 boss | geo-mean |
|---|---|---|---|---|---|---|---|
| rifle | G3A3 RoF3+Random+Quickdraw | 3.7 s | 7.2 | 9.3 | 7.1 | 37.4 | **0%** |
| handgun | G23 Random | +31% | +17% | +47% | +12% | +34% | **+29%** |
| grenade | M79 Random | +59% | +42% | +55% | +35% | +43% | **+52%** |
| machine | M11 | +63% | +44% | +128% | +32% | +99% | **+71%** |

**Day 5, a fixed non-Wayne gun per class (M9 3, MP5PDW, G3A3, M500, M203 4; realistic):**

| Class | Mods added | close | groups | keep-away | geo-mean |
|---|---|---|---|---|---|
| shotgun M500 (8 slots) | 2Cmd+Quickdraw+Frost+Critical | 2.3 s | 3.7 | 33.9 | **0%** |
| grenade M203 4 (5 slots) | 2Cmd+Quickdraw+Burst | +11% | +13% | +16% | **+12%** |
| rifle G3A3 | 2Cmd+AttackAll+Quickdraw | +64% | +40% | +68% | **+73%** |
| handgun M9 3 (no free slot) | - | +177% | +216% | +85% | **+130%** |
| machine MP5PDW (no free slot) | - | +208% | +238% | +124% | **+207%** |

**Day 5, best gun per class (that class's Wayne gun wins every class):**

| Class | Gun + mods | close | groups | keep-away | stat. boss | Day 5 boss | geo-mean |
|---|---|---|---|---|---|---|---|
| rifle | MAG 2Cmd+Quickdraw | 1.0 s | +34% | 8.1 | 6.9 | 0.3 | **+4%** |
| handgun | DE50AE7 2Cmd+Quickdraw+Burst+Critical | +8% | 1.8 (+8%) | +110% | +42% | +515% | **+69%** |
| machine | P90 2Cmd+RoF3+Quickdraw | +5% | 1.7 (best) | +105% | +32% | +1462% | **+80%** |
| grenade | HK40 2Cmd+AttackAll+Quickdraw+Frost | +11% | +8% | +177% | +109% | +1315% | **+113%** |
| shotgun | M10B 2Cmd+Quickdraw | +99% | +102% | +253% | +168% | +1106% | **+202%** |

With one Mod Permit slot the MAG pulls further ahead (+130..+371% for the rest), because
2 Commands + Quickdraw + Attack All on attack 151 / range 185 / 21 rounds has no counterpart.

## 3. Vanilla vs current

The current rules change effects, not classes, and the class spread barely moved:

| Stage / model | Spread vanilla (geo-mean of the worst class) | Spread current |
|---|---|---|
| Day 4 best-in-class | machine +63% | machine +71% |
| Day 5 fixed guns, realistic | machine +186% | machine +207% |
| Day 5 best-in-class (Wayne) | shotgun +156% | shotgun +202% |

Slightly wider under current rules: the effect boosts (Frost / Heat, Critical, Quickdraw) help
whatever already fires the most bullets with the most power. The rebalance did what it set out to
do (no effect is a trap, see the build diversity report) and was never aimed at class balance.

## 4. What decides the class results (from the decomp, not the sim)

1. **Mod slots.** Day 5's shotguns (M500 8, M870 6-7) and grenade launchers (M203 4 5) carry
   2 Commands + Quickdraw + more; the Day 5 handgun M9 3 and machine gun MP5PDW have no free slot.
   This is gun data, not a class rule.
2. **2 / 3 Commands** is the single strongest effect (-40..-63% clear time where not built in).
   It doubles the volleys per ATB bar. It is in every top build of every class.
3. **Magazine x Commands.** A volley that outruns the magazine clicks and reloads: high RoF on
   12-round handguns and 2 Commands on 7-round shotguns waste bullets every turn (M8000 RoF 10 is
   ~2x slower than RoF 3 under every animation assumption).
4. **Range** matters a lot only at keep-away distances: rifle 110 in range 80% of the time,
   handgun 52%, machine gun 40%. In normal fights every class is in range 77-95% of the time.
5. **ATB factor** (rifle / shotgun / grenade 0.8 of handgun / machine) costs those classes ~20%
   per turn, which rifles win back with power and range, shotguns and grenades with slots.
6. **Random Fire / Attack All** waste bullets on invulnerable helpers in scripted boss fights
   (Day 5 boss: P90 5.3 s vs MAG 0.3 s).
7. The **Wayne gun** of Day 5 outclasses every found gun; the MAG is the strongest platform
   in the game (attack 151, range 185, built-in Critical, 21 rounds).

## 5. Robustness

- **Animation loop length x0.5 / x1 / x2:** best-in-class times change 0-50% but the order
  (MAG, P90/DE50AE7, HK40, M10B) is the same in all three.
- **Timing mode serial vs overlap and distance x0.8 / x1.25:** class order of plain guns unchanged
  in normal fights; keep-away gaps grow with distance (x1.25: machine 122 s vs rifle 135 s vs
  handgun 99 s for plain Day 5 guns, where the plain rifle G3A3 has no RoF).
- **Reload 0.3 / 0.8 / 1.5 s:** < 5% change except the shotgun (+17% at 1.5 s).
- Not covered: Haste / Slow (strong in the logged boss attempts), armor choice, PE.
