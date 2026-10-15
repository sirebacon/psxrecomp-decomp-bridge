# Parasite Eve: short-range guns vs keep-away bosses (2026-10-15)

Status: **parked**. Problem confirmed by play; options listed; to pick after more data.

## Problem

Short-range guns (handguns, machine guns, shotguns) are fine in most rooms: rooms are small to
medium and normal enemies come close. One keep-away boss turns range into everything. Player
report (Day 5): "the first time I was considering I am really dead if I don't play really
smart. A regular player might have a massive struggle here."

## Evidence (play log, Day 5, gun 0x89, range 1281, level 21-24, max HP 296)

| Fight | Time | HP lost | Shots | Grazes / hits |
|---|---|---|---|---|
| Boss part 1, room 156 (0x0216 + three 0x0200) | 27 s | 434 | 38 | 10 / 30 (33%) |
| same, earlier attempt | 12 s | 153 | 15 | - |
| Boss part 2, room 380 (0x0217 + three 0x0200) | 10 s | 149 | 8 | 3 / 22 (14%) |
| same, earlier attempt | 11 s | 193 | 7 | - |

- Part 1 is a scripted fight: the boss survives (enemies carry about 1,000,000 HP and the script
  ends the fight). A third of the hits that landed were grazes (100-150% of the gun's range);
  shots beyond 180% miss outright and the hit rows never see them, so the real out-of-range
  share is higher.
- Part 2 plays like a normal fight (hits mostly at 50-80% of range).
- Normal fights: about three quarters of hits land under 50% of range (`hitq` rows, Days 3-5).
- Side finding: the ~1,000,000 HP placeholder explains the absurd `dealt` totals on scripted
  boss fights (1,001,410 / 4,010,576); filter those enemies out of damage stats.

Mechanics (decomp, `Battle_CheckEvasion`): distance as a share of the gun's range; beyond 180%
miss, 150-180% 25% graze, 120-150% 50%, 100-120% 80%; a graze deals 30% damage.

## Options

1. **Stronger grazes** (all guns): 30% -> ~50-60%. Progress against a boss that backs off; a
   rifle still wins inside its range. One new Mod Effects row, switchable. **Leaning this way.**
2. **Stronger grazes for short-range types only**: narrows the gap without buffing rifles.
3. **Wider graze band against bosses** (e.g. 100-180%): turns sure misses into grazes; the most
   direct fix for "can't reach it", boss fights only.
4. **Backup rifle** (already possible: weapon switch costs half a bar under Items & Parasite
   Energy rules): costs a bag slot and players won't know to do it; a tip, not a fix.

Goal for any option: a short-range gun clears boss part 1 with clearly less than ~434 HP taken,
without making normal fights easier.

## Data still to collect

- `reach` rows (PE `148540d`, target test fixed in `f9b5fd2`): Aya's ready time by the nearest
  live enemy's distance vs the gun's range (in / graze / far / out). Replay boss part 1 (room 156)
  with the current gun and with a rifle (Debug > Give item) and compare.
- Then simulate boss part 1 per option (`tools/pe_combo_sim.py`, `DIST` per fight type: normal
  close, keep-away from the `reach` rows) and pick.

Related: `pe-mod-effects-overhaul-2026-10-14.md` (Mod Effects rules), `tools/pe_gun_progression_sim.py`
(rifle dominance depended on the distance assumption: close favours machine guns, far favours
rifles).
