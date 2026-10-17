# Weapon balance phase 2 — G. Encounter balance: keep-away and the Day 5 damage race (2026-10-17)

Revisits R1 of the phase 1 proposal (lower the Day 5 boss part 1 threshold 450 -> 315).

## 1. Corrected player stats

- The HP-level bug (Counter boost wiping level-up HP) is fixed (PE c7dc04f) and old saves repair
  themselves (39594f5).
- **The logged room-156 attempts were at level 21, where HP was correct** (296, matching the
  chart): the bug started at level 24. The difficulty logged there was real, not the bug.

## 2. Logged loadouts with realistic movement (level 21, current rules, 300 fights)

| Loadout (fit to logged per-bullet damage) | Policy | Time (p10-p90) | HP lost | Out-of-range turns |
|---|---|---|---|---|
| M79 RoF 5, attack 66 | stand | 17.7 s (12.4-23.0) | 260 | 32% |
| | walk 440 | 14.7 s (12.4-17.9) | 218 | 0% |
| | walk 300 | 16.0 s (12.4-20.9) | 236 | 1% |
| M9 RoF 3, attack 40 | stand | 17.8 s (13.5-22.9) | 263 | 43% |
| | walk 440 | 15.5 s (11.7-19.4) | 228 | 1% |
| Boss-only graze 50% (E3) | stand | -6% | -6% | |
| | walk | 0% | 0% | |
| Log | | 8 s (M9), 12 s / 27 s (M79) | 131 / 153 / 434 | grazes 12-33% of hits |

(The logged attempts used Haste 2-4 times; the model doesn't.)

## 3. With Day 5 Wayne gear (optimized, walk 440)

P90 3.8 s, DE50AE7 0.9 s, HK40 3.0 s, M500 3.4 s, MAG 0.4 s; M10B 11.3 s because its greedy build
uses Random Fire, which wastes bullets on the three invulnerable helpers (with 2Cmd + Critical
+ Quickdraw it takes ~3 s).

## 4. Reading

1. **It is a damage race, not a range wall.** Walking at the measured speed removes the
   out-of-range turns for every class; what remains is damage per second at level 21 against
   ~15 HP/s of pressure. Short guns are not "nearly unusable" there.
2. **Boss-only graze (E3) does almost nothing once Aya walks** (0%); it only helps a player who
   stands still (-6%).
3. **E6 (threshold -30%) would make the fight easier for everyone**, which is what you were
   worried about; the data doesn't show a weapon-viability problem it would fix.
4. The real traps in this fight are **Random Fire and Attack All** (bullets on helpers) and
   standing still. Both are information problems.

## 5. Recommendation

- **Don't change the boss now.** Withdraw phase 1's R1 as a default; keep it as a fallback if
  play tests with correct HP still end near death on average (> ~70% HP lost).
- **Teach the fight:** a one-line hint (F1 page or a toast on that fight) that the boss keeps its
  distance and that walking toward it while the bar fills, and single-target fire, work best.
- **Play test:** 3-5 attempts each with a handgun, a machine gun / grenade launcher and a rifle,
  same level and loadout, with loadout logging on; compare time, HP lost and grazes with the
  table above.
