# Weapon balance phase 2 — B. Weapon modification balance (2026-10-17)

CURRENT rules (as implemented). Stress weapons at Day 5 with that stage's boosters and one Mod
Permit slot: P90, MAG, DE50AE7, M10B, M500, HK40. Optimized build = greedy over the Day 5 mod
pool by mixed clear time (close / groups / keep-away / stationary boss). Single-effect results
from phase 1 (`pe-weapon-build-diversity-2026-10-17.md`) still apply. Simulator results.

## Opportunity cost (regret): an effect in place of one slot of an optimized build

Median over the six weapons and slots (mixed clear time; 0% = what the optimizer picks):

| Effect | Median regret | Best case | Worst case | Reading |
|---|---|---|---|---|
| 2 Commands | 0% | 0% | 0% | always chosen (except M10B: +7-13% without it) |
| Quickdraw | 0% | 0% | 0% | always chosen |
| Frost | +12% | -8% | +136% | best "third slot"; near-automatic on many-slot guns |
| Attack All | +23% | -8% | +96% | excellent on high-power, big-magazine guns (MAG, HK40) |
| Burst | +24% | 0% | +131% | fine |
| Counter | +28% | +5% | +150% | decent (vanilla chance grows with level) |
| Random Fire | +36% | 0% | +118% | mixed; wastes bullets on helpers |
| Critical | +38% | -3% | +179% | situational, strong with built-in RoF |
| (empty slot) | +38% | +9% | +179% | reference |
| Tranquilizer | +39% | +5% | +179% | defensive value not in clear time (see below) |
| Heat | +48% | 0% | +172% | no longer a trap; coverage pick |
| Acid | +50% | 0% | +175% | long fights only |
| RoF 3 / 5 / 7 | +68 / +136 / +172% | | | replacing a built-in RoF or wasting magazine (see below) |

## Effect by effect

- **Heat / Frost.** Frost is the most universally attractive non-core effect (neutral 115% applies
  to every enemy without a match). The optimizer rarely takes Heat + Frost together; it prefers
  Frost + Critical / Acid. Not dominant enough to act on; watch in play data (`modfx` element rows).
- **Acid.** 4-16% faster alone (decomp poison tick, phase 1); strongest on many-bullet guns and
  long fights. Healthy.
- **Tranquilizer.** No clear-time gain, but -11..-36% damage taken (phase 1); the most on the
  machine gun (many bullets). The stop lasts 3 enemy turns and **every landed bullet that procs
  refreshes it** (the game ORs the stop bits again; the sim refreshes to 3), so many-bullet guns
  can keep a non-resistant enemy stopped most of the time. Resistant enemies (20%) and bosses
  (vanilla odds, mostly Strong) limit it. Healthy today; it is the effect to watch if machine-gun
  bullets or Tranq odds are ever raised (any MG suppression idea would stack with it).
- **Critical.** +20 points then 26.7% of normal hits become crits. The MAG gets 72% crits in close
  fights vs 26-33% for the other stress guns (range-relative crit zone + built-in Critical);
  capping the zone at 600 units (analysis) slows the MAG only 9%.
- **Quickdraw.** In every optimized build; removing it costs 23-195% (most on the MAG: one-turn
  kills). Strong but reasonable: it's a first-turn effect, worth most in short fights.
- **Counter.** Vanilla (boost stays off). Regret +28%: a real option at level 24+.
- **RoF 7 / 10.** Still a trap on small magazines (DE50AE7 RoF 10: 3.1 vs 1.3 s close). On the
  P90 the verdict flips with the unmeasured per-bullet time (see report A). "+50% magazine with
  RoF 7/10" helps the others 20-25% and the P90 0% (200 rounds), but RoF 7/10 still trail.
- **Attack All.** Uses RoF bullets per target from the magazine (decomp; no free ammo). Removing
  it costs the MAG 107%. Restricting it to the first command (analysis) slows the MAG only 9%.
- **Burst.** Cone share assumed (50%); good in groups. Needs geometry data.
- **Random Fire.** Picks random targets including invulnerable helpers: the M10B's optimized build
  (2Cmd + Quickdraw + Random) takes 13 s in the Day 5 scripted fight vs 3-5 s for the others.
- **Multiple Commands.** See archetypes report: removing Commands costs 52-242% (M10B 7-13%);
  making each extra command cost 50% more ATB (analysis) compresses the field from 2.6-5.8x to
  1.6-3.6x of the best, but slows every weapon. Commands is the convergence point.
- **Cyanide** (EX only): -6..-12%; bosses resist; premium price justified.
- **Armor: Attack Down / Slow AT.** The defensive archetype (Attack Down armor + Tranq + Quickdraw
  + Counter) takes *more* total damage than the optimized build on every stress gun (e.g. MAG
  keep-away 404 vs 273) because fights last longer: damage reduction doesn't pay for slower
  kills in this model. Their value is in fights you can't speed up.

## Verdict

The effect rebalance holds across the roster: no effect is a trap except high RoF on small
magazines. Too universally attractive: **2 Commands, Quickdraw**, and to a lesser degree
**Frost**. Too weak: none outright; **Acid, Heat, Tranquilizer** are situational by design.
