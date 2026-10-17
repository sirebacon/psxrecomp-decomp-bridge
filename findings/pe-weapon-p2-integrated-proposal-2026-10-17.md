# Weapon balance phase 2 — H. Integrated proposal (2026-10-17)

Status: **proposal; nothing implemented.** Reports: [A corrections](pe-weapon-p2-simulator-corrections-2026-10-17.md),
[B modifications](pe-weapon-p2-modification-balance-2026-10-17.md), [C archetypes](pe-weapon-p2-build-archetypes-2026-10-17.md),
[D close combat](pe-weapon-p2-close-combat-2026-10-17.md), [E P90 / MAG](pe-weapon-p2-p90-mag-stress-2026-10-17.md),
[F economy](pe-weapon-p2-progression-economy-2026-10-17.md), [G encounters](pe-weapon-p2-encounter-balance-2026-10-17.md).
Supersedes phase 1's R1 (boss threshold) and R4 (shotgun magazine +50%). Simulator results,
not gameplay facts; open measurements listed at the end.

## Answers

1. **Does the effect rebalance hold up across the roster?** Yes. No effect is a trap anymore
   except high RoF on small magazines (a magazine mechanic, not a damage value).
2. **Too weak / too strong / too universal?** Too universal: 2 Commands and Quickdraw (in every
   optimized build), Frost to a lesser degree (best third slot). Weak-looking but situational by
   design: Acid, Heat, Tranquilizer, Counter. Nothing needs a number change now.
3. **Are 2 Commands and Quickdraw crowding out other builds?** Yes. Without Commands every gun is
   +52..+242% slower (M10B +13%: its magazine can't feed two volleys); every non-core archetype
   is +50..+670% behind. Diversity today lives in slots 3-5.
4. **Can RoF 7/10 work on more weapons without the P90 running away?** Magazine-based help
   ("+50% magazine with RoF 7/10") lifts other guns 20-25% and the P90 0%, but RoF 7/10 still
   trail. Whether they're good on the P90 depends on the unmeasured per-bullet firing time
   (0.05 s: RoF 7 wins; 0.10 s: RoF 3 wins). Measure before changing anything.
5. **Is the P90 too powerful?** No: best non-MAG gun in crowds and endurance, ~2x slower than the
   MAG at keep-away, not dominant on bosses. Appropriately specialised; no experiment boosted it.
6. **Is the MAG too universally strong?** It is the best gun in every encounter. Its range-relative
   crit zone (-9%) and Attack All on every command (-9%) explain little; it is mainly the platform
   (attack 151, range 185, built-in Critical, 21 rounds). It is one of five Wayne guns; better
   reasons to pick the others are more useful than weakening it.
7. **Would shotgun close-combat bonuses improve the game?** Yes, as a targeted niche: +40%
   damage within 400 units fading to 650 makes shotguns 12-25% faster (more when played close),
   touches no other class, and gives the M10B a real case (close stationary bosses).
8. **Magazine, damage, recovery or a combination?** Proximity damage + a magazine sized to the
   volley (M10B 7 -> 8). Recovery (-2..-7%) and stagger (~0%) aren't worth building. A blanket
   +50% magazine is worse than nothing on the M10B (10 rounds leave 2-bullet turns).
9. **Could close-combat bonuses make a new dominant weapon?** Not with the tested values: the
   package leaves the best shotgun slower than the P90 and MAG everywhere; M500 midgame gains
   12-22% (check Day 3-4 shotgun play).
10. **Can classes support distinct builds throughout the game?** Partly: each class has an
    encounter it does well, but builds converge on the Commands + Quickdraw core and the MAG
    leads late. The shotgun package adds one genuine niche.
11. **Does the economy make multiple weapons too expensive?** Not the main problem: transfers are
    lossless; a specialist secondary doesn't pay because it wins no encounter (an M10B secondary
    +28..+77%; a MAG "secondary" just takes over).
12. **Should the Day 5 keep-away boss change?** Not now. The logged attempts were at level 21 with
    correct HP; walking at the measured speed removes the range problem; it is a damage race.
    Boss-only graze does ~0% once Aya walks; a lower threshold eases it for everyone. Teach the
    fight, play-test with logging, keep the threshold change as a fallback.
13. **Smallest, safest diversity improvements:** shotgun proximity + M10B magazine 8 (S1), and
    information about magazine / volley mismatches (S2). Everything else waits for measurements.
14. **Leave untouched:** see the list below.

## Ranked proposals

| # | Change | Current -> proposed | Benefit (sim) | Complexity | Confidence | Risk | Diversity | Effect on P90 / MAG |
|---|---|---|---|---|---|---|---|---|
| S1 | Shotgun proximity damage | none -> **+40% within 400 units, linear fade to 0 at 650** (absolute; shotguns only) | M10B -12% stand / -21% close; M500 -13 / -23% | low-medium (damage hook + Aya/enemy positions already read for `reach`) | medium (needs distance data) | low | + shotgun niche | 0% / 0% |
| S1b | M10B magazine sized to its volley | 7 (6+1) -> **8** | with S1: M10B -19% stand / -26% close (close / stat. boss / keep-away 2.3 / 9.7 / 18.1 s) | low (item data or reload rule) | medium | low (M10B only) | + | 0% / 0% |
| S2 | Show magazine / volley mismatch | none -> F1 / Workshop note when bullets per turn > magazine (or leave a short turn) | removes the RoF 7/10 and Commands-on-shotgun traps by information | low | high | none | + (players avoid traps) | 0 |
| S3 | Keep-away hint for the Day 5 fight | none -> one-line hint: walk in while the bar fills, prefer single-target fire | -13..-17% time when followed (walking), and avoids Random / Attack All on helpers | low | medium | none | + short guns | 0 |
| S4 | Smart reload (optional) | reload only when empty -> also when the rounds left can't cover the next turn | -1..-4%, mostly endurance | medium (reload hook) | medium | low | small | 0 / -1% |

Rejected or parked, with the evidence:

| Idea | Result | Why not now |
|---|---|---|
| Boss threshold 450 -> 315 (E6) | -19..-35% for everyone | eases the fight for all; no viability problem found once Aya walks |
| Boss-only graze 50% (E3) | -6% standing, 0% walking | little effect where it matters |
| Shotgun recovery -25 / -50% (C4) | -2..-7% | weak |
| Shotgun stagger (C5) | ~0% | complexity for nothing in clear time |
| Machine-gun suppression (M1) | 0-1% | nothing gained; would stack with Tranquilizer's refreshing stop |
| Handgun recovery -25% (H1) | DE50AE7 -5% | small; revisit after the timing measurement |
| Commands ATB cost +50% (analysis) | spread 2.6-5.8x -> 1.6-3.6x | slows every weapon; a universal nerf |
| MAG crit-zone cap (analysis) | MAG -9% | small, and it is a core vanilla mechanic |
| Global magazine +50% for shotguns | M10B worse (+2..+7%) | volley misalignment |

## Mechanics to leave unchanged

Damage formula, hit and graze bands, range = 150 x sqrt(stat), range-relative crit zones, ATB
class factors, Commands, Quickdraw (as implemented), the effect rebalance values, Counter at
vanilla strength (never touch Aya's stat-level table), Attack All / Random Fire rules, Tool
transfers and the customization economy, the P90 and the MAG, the Day 5 boss (for now).

## Gameplay validation (smallest set that separates the explanations)

1. **Loadout logging** in battle rows (gun id, bonuses, mods, armor, stat22, offense, Haste/Slow)
   — prerequisite for everything below.
2. **Timing measurement** (debug server): command -> control return for P90 RoF 3 / 10, DE50AE7
   RoF 3 / 7, M10B with 2 Commands. Settles RoF 7/10 and the per-bullet assumption.
3. **Shotgun distance log**: absolute distance per bullet for a few M10B / M500 fights; how often
   400 / 650 units is reachable and what it costs in hits taken.
4. **M10B magazine test** (after S1b): same encounter and loadout, 7 vs 8 rounds: turns, bullets,
   clicks, reloads, damage, time, HP lost.
5. **P90 and MAG check**: one optimized fight each before / after S1 to confirm no change.
6. **Day 5 boss replays**: 3-5 attempts per class, same level and loadout, walking vs standing.
