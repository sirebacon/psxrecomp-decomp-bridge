# Bestiary draft (extraction) — October 19, 2026

Groundwork for a Junk-bought Bestiary. Every enemy stat block the room scripts set up, read
offline from both US discs (`extract_bestiary`, then `report_bestiary`). **No mod changes.**

## How it was extracted

- All 414 rooms of the room sector table (maps 1-440) on both discs; every room with enemies is
  byte-identical on the two discs.
- Each actor script's setup code is evaluated up to its last stat write. Common enemies compute
  HP and defense as `(scale x base) >> 16` (the scale is 1.0 on a first playthrough; the EX Game
  scale differs and is not applied here) and roll drop / steal with the script `Random`, so drop
  and steal are listed with their odds.
- Story-progress checks are split over the end-of-run value and 0; a stat block seen only on the
  0 side is marked *progress branch*. Scripted bosses store HP + 1,000,000 (the script ends the
  fight); the table shows HP without the offset and marks them.
- Resistances: weak / strong per element (heat, frost, cyanide, acid, tranq); unlisted = average.

## Check against the logged playthrough

- 145 logged (room, enemy) pairs; 132 found in the extraction, 129 with matching HP, defense and EXP.
- Drops, steals and BP matched on every found pair; resistances match every log row that recorded them
  (the first 42 enemy rows predate resistance logging and read as average).
- Not found (13): m5 0x0201, m23 0x0204, m86 0x020D, m89 0x020E, m123 0x0312, m188 0x021A, m217 0x001E, m226 0x001E, m273 0x0325, m350 0x0225, m428 0x0225, m430 0x0226, m432 0x0223. Mostly bosses whose identity is set by another actor or computed.
- Scripts the evaluator could not finish: 9.

## Coverage

| | Regular | Bosses / forced | Helpers (0 EXP, 0 BP) |
|---|---:|---:|---:|
| first seen Day 1 | 5 | 3 | 1 |
| first seen Day 2 | 7 | 0 | 1 |
| first seen Day 3 | 12 | 9 | 5 |
| first seen Day 4 | 6 | 4 | 0 |
| first seen Days 4-5 | 8 | 11 | 1 |
| first seen Day 6 | 0 | 0 | 3 |
| first seen late addition | 0 | 2 | 0 |
| first seen special scene | 0 | 0 | 3 |
| first seen Chrysler (EX) | 23 | 27 | 7 |
| **total distinct stat blocks** | **61** | **56** | **21** |

Bosses / forced = the can't-escape flag with a reward. Helpers are boss parts, props and scripted
actors with no EXP or BP; they would not get Bestiary entries.

A distinct stat block is not always a distinct creature: the same monster can appear with a
tougher block later in the story. Naming pass will merge those.

## Regular enemies

| ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| 0x0002 | Day 1 | sewer, theater (12, 14, 27, 28) | 12 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| 0x0002 | Day 1 | theater (13) | 17 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| 0x0002 | Day 1 | theater (14) | 10 | 4 | 1 | 2/1 | frost, cyanide, acid | heat, tranq | Medicine 1 90%, nothing 10% | Ammo 6 80%, nothing 20% |  |
| 0x0004 | Day 1 | sewer (28, 32) | 34 | 6 | 4 | 8/3 | frost | heat, acid, tranq | Ammo 6 90%, Medicine 1 10% | Ammo 6 80%, nothing 20% |  |
| 0x0002 | Day 1 | sewer (30) | 14 | 4 | 3 | 5/2 | heat, cyanide | frost | Revive 90%, Medicine 1 10% | Medicine 2 80%, nothing 20% |  |
| 0x0007 | Day 2 | central_park (59, 62, 78) | 32 | 18 | 6 | 5/3 | - | heat | Medicine 1 90%, nothing 10% | Cure P 80%, Medicine 1 20% |  |
| 0x0008 | Day 2 | central_park (59, 66, 67, 78, 82) | 44 | 18 | 8 | 7/3 | - | heat, cyanide, acid | Ammo 6 90%, Cure P 10% | Cure P 80%, Medicine 2 20% |  |
| 0x0008 | Day 2 | central_park, nypd (61, 67, 80, 81, 87, 100 +2) | 35 | 18 | 6 | 6/3 | cyanide | - | Junk 90%, Medicine 1 10% | Junk 90%, Medicine 2 10% | progress branch (V74 = 0); progress branch (V74, V80 = 0) |
| 0x000C | Day 2 | central_park, nypd (61, 67, 80, 81, 87, 100 +5) | 35 | 22 | 6 | 6/3 | cyanide | - | Junk 90%, Medicine 1 10% | Junk 90%, Medicine 2 10% |  |
| 0x000A | Day 2 | central_park (63, 83, 358) | 57 | 18 | 10 | 9/3 | - | tranq | Ammo 6 99%, Offense 1 1% | Medicine 1 99%, Offense 2 1% |  |
| 0x000B | Day 2 | central_park (65, 85, 87) | 60 | 18 | 10 | 9/4 | heat | cyanide, acid, tranq | Ammo 6 90%, Cure P 10% | Ammo 6 80%, Cure P 20% |  |
| 0x000C | Day 2 | central_park (75, 80, 82) | 75 | 18 | 12 | 16/5 | heat | tranq | Ammo 15 90%, Medicine 1 10% | Ammo 6 50%, Ammo 15 50% |  |
| 0x0010 | Day 3 | nypd (100, 110, 113, 121) | 70 | 15 | 26 | 11/5 | heat, cyanide, tranq | frost | Medicine 1 90%, nothing 10% | Ammo 6 |  |
| 0x000F | Day 3 | nypd (104, 113, 115, 116, 122) | 78 | 18 | 20 | 13/6 | frost | cyanide, tranq | Ammo 15 90%, Cure M 10% | Ammo 6 50%, Ammo 15 50% |  |
| 0x000F | Day 3 | nypd (104, 113, 115, 116, 120, 122) | 72 | 20 | 0 | 0/6 | frost | cyanide, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x000C | Day 3 | nypd (107) | 35 | 22 | 6 | 6/3 | cyanide | - | Offense 1 | Junk 90%, Medicine 2 10% | progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| 0x0011 | Day 3 | nypd (107, 111, 122) | 98 | 20 | 39 | 15/10 | - | tranq | Medicine 2 90%, Junk 10% | Medicine 1 90%, Medicine 3 10% |  |
| 0x0008 | Day 3 | nypd (120) | 35 | 18 | 6 | 6/3 | cyanide | - | Full Cure | Junk 90%, Medicine 2 10% | progress branch (V74 = 0); progress branch (V74, V80 = 0) |
| 0x000C | Day 3 | nypd (120) | 35 | 22 | 6 | 6/3 | cyanide | - | Full Cure | Junk 90%, Medicine 2 10% |  |
| 0x000F | Day 3 | nypd (120) | 78 | 18 | 20 | 13/6 | frost | cyanide, tranq | Medicine 3 | Ammo 6 50%, Ammo 15 50% |  |
| 0x000C | Day 3 | nypd (121) | 35 | 22 | 6 | 6/3 | cyanide | - | Tool | Junk 90%, Medicine 2 10% | progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| 0x0012 | Day 3 | hospital (126, 129, 137, 139, 140, 141 +6) | 88 | 30 | 48 | 6/3 | heat, acid, tranq | frost | Ammo 6 90%, Cure P 10% | Ammo 6 50%, Medicine 1 50% |  |
| 0x0013 | Day 3 | hospital (137, 140, 146, 147, 324, 327) | 110 | 30 | 86 | 9/5 | frost | heat, cyanide, acid | Medicine 2 90%, Cure M 10% | Ammo 6 50%, Cure M 50% |  |
| 0x0014 | Day 3 | hospital (141, 146, 153, 154, 328) | 120 | 30 | 92 | 11/6 | heat, cyanide | frost, tranq | Medicine 2 66%, nothing 34% | Ammo 6 50%, Medicine 2 50% |  |
| 0x0016 | Day 4 | chinatown, sewer2 (162, 163, 167) | 99 | 34 | 287 | 8/6 | frost | heat, cyanide, acid, tranq | Ammo 6 90%, nothing 10% | Cure P |  |
| 0x0017 | Day 4 | chinatown (162, 163) | 135 | 34 | 361 | 21/8 | frost | heat, tranq | Ammo 6 90%, Ammo 15 10% | Ammo 15 90%, Medicine 2 10% |  |
| 0x0017 | Day 4 | sewer2, subway (167, 168, 169, 173, 178, 186) | 112 | 36 | 301 | 10/4 | heat | - | Cure D 90%, Ammo 6 10% | Medicine 2 80%, Cure D 20% |  |
| 0x0018 | Day 4 | sewer2 (168, 169) | 153 | 36 | 425 | 12/8 | heat | cyanide, acid, tranq | Medicine 2 80%, Junk 20% | Junk |  |
| 0x0019 | Day 4 | sewer2 (174) | 215 | 50 | 522 | 26/8 | heat | cyanide, tranq | Range 1 50%, Cr Evade 1 50% | Junk 80%, Tool 20% |  |
| 0x0019 | Day 4 | subway (186, 187) | 161 | 40 | 462 | 15/8 | heat, frost | cyanide, acid, tranq | Cure P 90%, Ammo 6 10% | nothing 99%, Offense 1 1% |  |
| 0x001D | Days 4-5 | museum (197, 198, 199, 201, 206, 207 +8) | 200 | 40 | 896 | 16/4 | cyanide | heat, tranq | Junk 66%, Medicine 2 34% | nothing 90%, Ammo 30 10% |  |
| 0x001D | Days 4-5 | museum (197, 198, 199, 203, 206, 207 +10) | 240 | 71 | 1202 | 12/5 | frost | heat | Ammo 15 90%, Medicine 3 10% | nothing 80%, Ammo 15 20% |  |
| 0x001E | Days 4-5 | museum (197, 198, 199, 203, 206, 207 +11) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% |  |
| 0x001F | Days 4-5 | museum (203, 223, 224, 229, 231, 233 +3) | 320 | 50 | 1829 | 32/10 | - | cyanide, acid, tranq | Medicine 3 90%, Ammo 30 10% | Cure D 50%, Ammo 15 50% |  |
| 0x0020 | Days 4-5 | museum (205) | 430 | 78 | 3652 | 24/9 | - | cyanide, tranq | Medicine 3 90%, Range 2 10% | nothing 80%, Range 2 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0020 | Days 4-5 | museum (231, 234, 243) | 390 | 78 | 2036 | 24/9 | - | cyanide, tranq | Cure P 90%, Ammo 30 10% | Cure P 90%, Medicine 4 10% |  |
| 0x001A | Days 4-5 | warehouse (263, 265, 333) | 215 | 40 | 135 | 40/5 | - | tranq | Ammo 30 | Ammo 30 |  |
| 0x001A | Days 4-5 | warehouse (263, 265, 333) | 242 | 40 | 185 | 32/9 | heat | cyanide, acid, tranq | Ammo 30 | Cure M |  |
| 0x000A | Chrysler (EX) | chrysler (298, 308, 311) | 74 | 40 | 2 | 6/1 | cyanide | - | Junk 90%, Medicine 2 10% | Junk 80%, Medicine 3 20% |  |
| 0x000B | Chrysler (EX) | chrysler (298, 308, 311) | 85 | 42 | 2 | 8/2 | heat, cyanide, tranq | frost, acid | nothing 90%, Cure M 10% | nothing 80%, Medicine 2 20% |  |
| 0x000F | Chrysler (EX) | chrysler (299, 309, 310) | 106 | 49 | 4 | 9/3 | - | heat, cyanide, tranq | Ammo 6 90%, Medicine 1 10% | nothing 95%, Revive 5% |  |
| 0x0011 | Chrysler (EX) | chrysler (299, 309, 310, 385, 388, 389) | 98 | 45 | 3 | 8/1 | - | - | Medicine 1 90%, Cure D 10% | Cure D 95%, Medicine 3 5% |  |
| 0x0014 | Chrysler (EX) | chrysler (384, 386, 387, 391, 392, 393 +3) | 120 | 48 | 5 | 8/2 | - | heat, cyanide, acid, tranq | Ammo 6 90%, Medicine 1 10% | nothing 50%, Cure P 50% |  |
| 0x0015 | Chrysler (EX) | chrysler (384, 387) | 158 | 62 | 9 | 10/2 | - | tranq | nothing 99%, Revive 1% | nothing 80%, Medicine 2 20% |  |
| 0x0013 | Chrysler (EX) | chrysler (385, 388, 389) | 144 | 52 | 7 | 12/4 | heat, frost | cyanide, acid, tranq | Medicine 2 90%, Ammo 15 10% | Medicine 2 95%, Revive 5% |  |
| 0x0015 | Chrysler (EX) | chrysler (391, 393, 394, 395, 396, 399 +2) | 280 | 65 | 27 | 15/5 | heat | cyanide, acid, tranq | Medicine 2 90%, Cure P 10% | nothing 80%, Medicine 3 20% |  |
| 0x0017 | Chrysler (EX) | chrysler (391, 392, 394, 395) | 205 | 68 | 23 | 15/3 | frost | cyanide, acid, tranq | nothing 80%, Ammo 30 20% | Cure M 95%, Revive 5% |  |
| 0x0016 | Chrysler (EX) | chrysler (392, 393, 396, 401) | 240 | 60 | 15 | 12/4 | frost | heat, cyanide, acid | Cure M 90%, Medicine 3 10% | nothing 95%, Medicine 3 5% |  |
| 0x001A | Chrysler (EX) | chrysler (398, 400, 403) | 315 | 70 | 40 | 15/3 | - | heat, tranq | Medicine 3 90%, Cure M 10% | Ammo 15 50%, Ammo 30 50% |  |
| 0x0020 | Chrysler (EX) | chrysler (398, 400, 403) | 375 | 74 | 52 | 15/3 | - | tranq | Ammo 6 90%, Ammo 30 10% | nothing 95%, Medicine 3 5% |  |
| 0x001E | Chrysler (EX) | chrysler (405, 407, 408, 409, 410) | 460 | 88 | 133 | 20/4 | frost | heat, acid, tranq | nothing 80%, Ammo 15 20% | Medicine 3 95%, Revive 5% |  |
| 0x001F | Chrysler (EX) | chrysler (405, 406, 407, 408, 409) | 420 | 85 | 115 | 18/3 | frost, cyanide, acid | heat, tranq | Medicine 2 90%, Medicine 4 10% | nothing 80%, Medicine 4 20% |  |
| 0x0026 | Chrysler (EX) | chrysler (405, 408, 409, 413, 416, 417) | 410 | 92 | 144 | 20/5 | - | cyanide | nothing 80%, Medicine 3 20% | nothing 95%, Medicine 4 5% |  |
| 0x0023 | Chrysler (EX) | chrysler (406, 410) | 580 | 98 | 160 | 24/4 | frost | heat, cyanide, tranq | Ammo 6 90%, Ammo 30 10% | Medicine 4 80%, Revive 20% |  |
| 0x0028 | Chrysler (EX) | - (412, 414, 415, 421, 422, 423 +1) | 590 | 95 | 327 | 25/5 | heat, cyanide, tranq | frost | nothing 90%, Revive 10% | Medicine 4 80%, Ammo 30 20% |  |
| 0x002D | Chrysler (EX) | - (412, 414, 415) | 715 | 104 | 364 | 28/7 | cyanide | frost, tranq | Ammo 15 90%, Ammo 30 10% | nothing 95%, Revive 5% |  |
| 0x0030 | Chrysler (EX) | - (412) | 790 | 150 | 562 | 32/8 | heat, cyanide, tranq | frost | Medicine 3 90%, Medicine 4 10% | nothing 80%, Rocket 20% |  |
| 0x002E | Chrysler (EX) | - (419, 420) | 780 | 98 | 804 | 28/6 | - | heat, cyanide, acid | nothing 66%, Medicine 4 34% | nothing 80%, Medicine 4 20% |  |
| 0x0031 | Chrysler (EX) | - (419, 420, 421, 422, 423) | 880 | 112 | 855 | 35/7 | acid, tranq | frost | Junk 90%, Medicine 4 10% | Ammo 30 80%, Medicine 4 20% |  |
| 0x0035 | Chrysler (EX) | - (419, 420) | 1000 | 128 | 894 | 35/7 | heat | tranq | nothing 80%, Medicine 4 20% | nothing 95%, Revive 5% |  |
| 0x0034 | Chrysler (EX) | - (421, 422, 423, 424) | 980 | 120 | 920 | 44/11 | - | - | Ammo 30 90%, Revive 10% | nothing 80%, Medicine 4 20% |  |

## Bosses and forced fights

| ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| 0x0002 | Day 1 | theater (16) | 12 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| 0x0002 | Day 1 | theater (22) | 10 | 4 | 1 | 2/1 | frost, cyanide, acid | heat, tranq | Medicine 1 90%, nothing 10% | Ammo 6 80%, nothing 20% |  |
| 0x0307 | Day 1 | sewer (34) | 120 | 200 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0011 | Day 3 | nypd (114) | 98 | 20 | 39 | 15/10 | - | tranq | Medicine 2 90%, Junk 10% | Medicine 1 90%, Medicine 3 10% |  |
| 0x0012 | Day 3 | nypd (118) | 150 | 25 | 45 | 23/10 | - | tranq | Sg550 | Defense 1 29 80%, Defense 2 20% |  |
| 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 170 | 30 | 114 | 15/6 | frost | cyanide | Cure M 90%, Medicine 1 10% | Medicine 2 80%, Cure M 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 45 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 0 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | B Vest 1 | Defense 1 29 90%, Tool 10% | progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | Ammo 15 | Defense 1 29 90%, Tool 10% |  |
| 0x0216 | Day 3 | hospital (156) | 450 | 33 | 6500 | 80/10 | - | cyanide, acid, tranq | nothing | nothing | scripted HP |
| 0x0016 | Day 3 | hospital (159) | 152 | 30 | 0 | 0/6 | frost | cyanide, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x041A | Day 4 | subway (188) | 500 | 35 | 10000 | 90/13 | - | cyanide, acid, tranq | Ammo 30 90%, Offense 1 10% | Tool | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Range 1 10% | Ammo 30 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Cr Evade 1 10% | Medicine 3 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x041A | Day 4 | subway (188) | 180 | 35 | 0 | 80/19 | - | cyanide, acid, tranq | M79 3 | Cure P | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x001E | Days 4-5 | museum (199) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% | progress branch (V34 = 0); progress branch (V34, V42 = 0); progress branch (V34, V42, V80 = 0); progress branch (V34, V80 = 0) |
| 0x001D | Days 4-5 | museum (210) | 240 | 71 | 2326 | 12/5 | frost | heat, cyanide | Medicine 4 90%, Full Cure 10% | nothing 95%, Defense 1 29 5% |  |
| 0x001F | Days 4-5 | museum (221) | 320 | 50 | 3256 | 32/10 | - | cyanide, acid, tranq | Medicine 4 | Range 1 80%, Bullet Cap 1 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0221 | Days 4-5 | museum (245) | 750 | 100 | 50000 | 60/10 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0421 | Days 4-5 | museum (245) | 900 | 65 | 0 | 60/10 | frost | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| 0x0421 | Days 4-5 | museum (245) | 400 | 75 | 0 | 120/15 | - | heat, cyanide, acid, tranq | Ammo 6 90%, Offense 2 10% | nothing 95%, Defense 2 5% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0223 | Days 4-5 | museum (256) | 2400 | 78 | 34464 | 256/32 | - | cyanide, acid, tranq | M8000 | Tool |  |
| 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing |  |
| 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 50/12 | - | cyanide, acid, tranq | nothing | nothing |  |
| 0x0220 | Days 4-5 | warehouse (269) | 856 | 110 | 2510 | 100/15 | - | cyanide, acid, tranq | At4 | Offense 1 50%, Defense 1 29 50% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x041B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing |  |
| 0x0307 | late addition | sewer (348) | 0 | 6 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0217 | late addition | hospital (380) | 400 | 25 | 6500 | 80/10 | - | cyanide, acid, tranq | G23 | Tool 80%, Super Tool 20% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0218 | Chrysler (EX) | chrysler (291) | 1000 | 60 | 100 | 128/8 | - | heat, cyanide, acid, tranq | Chrysler Key1 | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x000F | Chrysler (EX) | chrysler (295, 434) | 106 | 49 | 4 | 9/3 | - | heat, cyanide, tranq | Ammo 6 90%, Medicine 1 10% | nothing 95%, Revive 5% |  |
| 0x0011 | Chrysler (EX) | chrysler (295) | 98 | 45 | 3 | 8/1 | - | - | Medicine 1 90%, Cure D 10% | Cure D 95%, Medicine 3 5% |  |
| 0x002D | Chrysler (EX) | chrysler (295, 434, 435, 436, 437) | 700 | 100 | 255 | 0/0 | tranq | heat, frost, cyanide, acid | Ammo 30 66%, Revive 34% | nothing 80%, Medicine 4 20% |  |
| 0x021D | Chrysler (EX) | chrysler (383) | 1200 | 72 | 150 | 256/16 | heat | frost, cyanide, acid, tranq | Chrysler Key2 | nothing | progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x021D | Chrysler (EX) | chrysler (383) | 1200 | 72 | 150 | 256/16 | heat | frost, cyanide, acid, tranq | Revive | nothing | progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0422 | Chrysler (EX) | chrysler (390) | 1200 | 88 | 800 | 104/5 | frost | heat, cyanide, acid, tranq | Chrysler Key3 | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0422 | Chrysler (EX) | chrysler (390) | 600 | 88 | 0 | 100/5 | frost | heat, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0422 | Chrysler (EX) | chrysler (390) | 800 | 88 | 0 | 80/4 | frost | heat, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0427 | Chrysler (EX) | chrysler (397) | 1200 | 140 | 2500 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0427 | Chrysler (EX) | chrysler (397) | 1600 | 96 | 0 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 400 | 77 | 64 | 20/5 | frost | cyanide | Cure M 90%, Ammo 15 10% | nothing 95%, Medicine 4 5% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 100 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 0 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x023B | Chrysler (EX) | - (411) | 6400 | 160 | 10000 | 240/39 | - | heat, frost, cyanide, acid, tranq | Chrysler Key6 | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x023B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 148/33 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x043B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 125/23 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x024A | Chrysler (EX) | - (418) | 600 | 112 | 0 | 30/12 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x024A | Chrysler (EX) | - (418) | 1200 | 150 | 128 | 300/37 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x024A | Chrysler (EX) | - (418) | 12000 | 200 | 20000 | 400/58 | - | heat, frost, cyanide, acid, tranq | Chrysler Key7 | nothing | scripted HP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0020 | Chrysler (EX) | - (434, 435) | 375 | 74 | 52 | 15/3 | - | tranq | Ammo 6 90%, Ammo 30 10% | nothing 95%, Medicine 3 5% |  |
| 0x001F | Chrysler (EX) | - (435, 436, 437) | 420 | 85 | 115 | 18/3 | frost, cyanide, acid | heat, tranq | Medicine 2 90%, Medicine 4 10% | nothing 80%, Medicine 4 20% |  |
| 0x0026 | Chrysler (EX) | - (436) | 410 | 92 | 144 | 20/5 | - | cyanide | nothing 80%, Medicine 3 20% | nothing 95%, Medicine 4 5% |  |

## Helpers (not Bestiary entries)

| ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| 0x0100 | Day 1 | sewer (34) | 80 | 6 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | Range 2 90%, Pe 2 10% | Range 1 50%, Pe 1 50% | scripted HP |
| 0x0000 | Day 2 | central_park (75, 80, 82, 419, 420) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| 0x0000 | Day 3 | nypd (123) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| 0x0100 | Day 3 | nypd (123) | 300 | 24 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x0100 | Day 3 | nypd (123) | 200 | 24 | 0 | 0/0 | frost | heat, cyanide, acid, tranq | nothing | nothing |  |
| 0x0100 | Day 3 | nypd (123) | 400 | 24 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing |  |
| 0x0200 | Day 3 | chrysler, hospital (156, 291, 380) | 3392 | 29 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP |
| 0x001A | Days 4-5 | warehouse (263, 265, 333) | 10 | 20 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0125 | Day 6 | liberty (273) | 1600 | 85 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Offense 1 50%, Defense 1 29 50% | scripted HP |
| 0x0125 | Day 6 | liberty (273) | 1750 | 70 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| 0x0125 | Day 6 | liberty (273) | 1900 | 55 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | scripted HP |
| 0x0026 | special scene | - (429) | 1300 | 90 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing |  |
| 0x0226 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0426 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0200 | Chrysler (EX) | chrysler (291) | 200000 | 60 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| 0x0263 | Chrysler (EX) | chrysler (318) | 40000 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0263 | Chrysler (EX) | chrysler (318) | 8800 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0017 | Chrysler (EX) | chrysler (391, 392, 394, 395) | 160 | 16 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0427 | Chrysler (EX) | chrysler (397) | 2800 | 96 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | Chrysler Key4 | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| 0x0231 | Chrysler (EX) | chrysler (404) | 1200 | 104 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| 0x023B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |

## Next

1. Naming pass: tie each stat block to its creature (model / animation bank per actor type, room
   and story context) and merge blocks of the same creature.
2. EX Game: apply the EX scale (story variable V80) to the scaled enemies.
3. Decide the Junk tiers (for example name + HP free; weaknesses; drops and steals).
