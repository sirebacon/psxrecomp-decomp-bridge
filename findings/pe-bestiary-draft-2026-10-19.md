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

## Names

- Names come from the RPGClassics Parasite Eve shrine (enemies and bosses pages), matched by HP, EXP
  and area (`findings/data/pe-bestiary-names-2026-10-19.json`; the shrine facts are in
  `pe-enemy-names-rpgclassics.json`). 128 of 138 stat blocks named: 78 high, 37 medium, 13 low confidence.
- Where the shrine and the game disagree, the game value is kept (the log confirms it): Slime 88 HP
  (shrine 80), Spawn 114 EXP (90), Lizard 896 EXP (986), Mole 462 EXP (457), Scorpion 390 HP (480).
  Tyrannosaur: the script sets 100,000 EXP, which the 16-bit EXP field wraps to 34,464.
- Chrysler Building enemies are written with their EX HP directly and match the shrine EX HP.
- EX Game scale for story enemies: the shrine EX HP of 29 named enemies fits one scale of 1.3969-1.3974 x
  (shared cell N10 = 91546-91582 instead of 65536); off that scale: Frog (sewer), Gold Spider, Mole, Rat, Scorpion, Slime.
- Not extracted (identity or HP set by another actor): Actress, Eve (rehearsal room), Worm x4, Eve (carriage), Ultimate Being (1st, 2nd, 4th), Squirrel (Chrysler).

## Creatures

| Creature | Story (HP / EXP) | Chrysler EX (HP / EXP) |
|---|---|---|
| Rat | 12 / 2, 17 / 2, 14 / 3 | 85 / 2 |
| Parrot | 10 / 1 | 420 / 115 |
| Frog | 34 / 4, 153 / 425 | 460 / 133 |
| Alligator (tail) | 80 / 0 | - |
| Alligator (body) | 120 / 30, 0 / 30 | - |
| Green Snake | 32 / 6 | - |
| Red Snake | 44 / 8 | - |
| Blackbird | 35 / 6 | - |
| Monkey | 57 / 10 | 158 / 9 |
| Plant | 60 / 10 | 280 / 27 |
| Bear | 75 / 12 | 1000 / 894 |
| Yellow Rat | 70 / 26 | - |
| Spider | 78 / 20, 72 / 0 | 205 / 23 |
| Dogman | 98 / 39 | 980 / 920 |
| Giant Dogman | 150 / 45 | - |
| Sheeva (left head) | 300 / 0 | - |
| Sheeva (right head) | 200 / 0 | - |
| Sheeva (center head) | 400 / 0 | - |
| Slime | 88 / 48 | 880 / 855 |
| Fly | 110 / 86 | 240 / 15 |
| Ratman | 120 / 92 | 715 / 364 |
| Spawn | 170 / 114 | 400 / 64 |
| Spawn (offspring) | 45 / 4 | 100 / 8 |
| Giant Slime | 201 / 60 | - |
| Giant Spider (phase 1) | 450 / 6500 | - |
| Hospital map 159 actor | 152 / 0 | - |
| Snake | 99 / 287 | 120 / 5, 780 / 804 |
| Cat | 135 / 361 | 375 / 52 |
| Bat | 112 / 301 | 98 / 3 |
| Alligator | 215 / 522 | - |
| Mole | 161 / 462 | 144 / 7 |
| Centipede (head, phase 1) | 500 / 10000 | - |
| Centipede (middle) | 120 / 0 | - |
| Centipede (tail) | 180 / 0 | - |
| Lizard | 200 / 896 | 315 / 40 |
| Armadillo | 240 / 1202 | 410 / 144 |
| Dinosaur | 280 / 1530 | 106 / 4 |
| Pterodactyl | 320 / 1829, 320 / 3256 | - |
| Scorpion | 430 / 3652, 390 / 2036 | 580 / 160 |
| Armadillo (forced fight) | 240 / 2326 | - |
| Triceratops (phase 1) | 750 / 50000 | - |
| Triceratops (phase 2) | 900 / 0 | - |
| Tyrannosaur | 2400 / 34464 | - |
| Grey Rat | 215 / 135 | - |
| Gold Spider | 242 / 185 | - |
| Crab (claw) | 420 / 0 | - |
| Crab (body) | 856 / 2510 | - |
| Eve (Statue of Liberty) part | 1600 / 0, 1750 / 0, 1900 / 0 | - |
| Giant Spider (phase 2) | 400 / 6500 | - |
| Ultimate Being form | 1300 / 0 | - |
| Ultimate Being (3rd) | 3500 / 0 | - |
| Giant Spider (Chrysler) | - | 1000 / 100 |
| Monster Box | - | 700 / 255 |
| Bird | - | 74 / 2 |
| Eve (Chrysler) | - | 40000 / 0 |
| Eve (Chrysler) part | - | 8800 / 0 |
| Alligator (Chrysler) | - | 1200 / 150 |
| Centipede (Chrysler, head) | - | 1200 / 800 |
| Centipede (Chrysler, middle) | - | 600 / 0 |
| Centipede (Chrysler, tail) | - | 800 / 0 |
| Triceratops (Chrysler, phase 1) | - | 1200 / 2500 |
| Triceratops (Chrysler, phase 2) | - | 1600 / 0 |
| Triceratops (Chrysler, total) | - | 2800 / 0 |
| Cockroach (offspring) | - | 4200 / 10 |
| Cockroach | - | 4200 / 5000 |
| Crab (Chrysler, body) | - | 6400 / 10000 |
| Crab (Chrysler, claw) | - | 1600 / 0 |
| Gold Rat | - | 590 / 327 |
| Giant Rat | - | 790 / 562 |
| Small Bee | - | 600 / 0 |
| Large Bee | - | 1200 / 128 |
| Queen Bee | - | 12000 / 20000 |

## Coverage

| | Regular | Bosses / forced | Helpers (0 EXP, 0 BP) |
|---|---:|---:|---:|
| first seen Day 1 | 5 | 4 | 0 |
| first seen Day 2 | 7 | 0 | 1 |
| first seen Day 3 | 12 | 12 | 2 |
| first seen Day 4 | 6 | 4 | 0 |
| first seen Days 4-5 | 8 | 11 | 1 |
| first seen Day 6 | 0 | 3 | 0 |
| first seen late addition | 0 | 2 | 0 |
| first seen special scene | 0 | 3 | 0 |
| first seen Chrysler (EX) | 23 | 31 | 3 |
| **total distinct stat blocks** | **61** | **70** | **7** |

Bosses / forced = the can't-escape flag with a reward. Helpers are boss parts, props and scripted
actors with no EXP or BP; they would not get Bestiary entries.

A creature can have several stat blocks (tougher copies later, forced fights, Chrysler).

## Regular enemies

| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| Rat | 0x0002 | Day 1 | sewer, theater (12, 14, 27, 28) | 12 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| Rat (medium) | 0x0002 | Day 1 | theater (13) | 17 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% | tougher rat in map 13 |
| Parrot | 0x0002 | Day 1 | theater (14) | 10 | 4 | 1 | 2/1 | frost, cyanide, acid | heat, tranq | Medicine 1 90%, nothing 10% | Ammo 6 80%, nothing 20% |  |
| Frog | 0x0004 | Day 1 | sewer (28, 32) | 34 | 6 | 4 | 8/3 | frost | heat, acid, tranq | Ammo 6 90%, Medicine 1 10% | Ammo 6 80%, nothing 20% |  |
| Rat (sewer variant) (low) | 0x0002 | Day 1 | sewer (30) | 14 | 4 | 3 | 5/2 | heat, cyanide | frost | Revive 90%, Medicine 1 10% | Medicine 2 80%, nothing 20% | map 30, drops Revive 90%; not in the shrine list |
| Green Snake | 0x0007 | Day 2 | central_park (59, 62, 78) | 32 | 18 | 6 | 5/3 | - | heat | Medicine 1 90%, nothing 10% | Cure P 80%, Medicine 1 20% |  |
| Red Snake | 0x0008 | Day 2 | central_park (59, 66, 67, 78, 82) | 44 | 18 | 8 | 7/3 | - | heat, cyanide, acid | Ammo 6 90%, Cure P 10% | Cure P 80%, Medicine 2 20% |  |
| Blackbird | 0x0008 | Day 2 | central_park, nypd (61, 67, 80, 81, 87, 100 +2) | 35 | 18 | 6 | 6/3 | cyanide | - | Junk 90%, Medicine 1 10% | Junk 90%, Medicine 2 10% | progress branch (V74 = 0); progress branch (V74, V80 = 0) |
| Blackbird | 0x000C | Day 2 | central_park, nypd (61, 67, 80, 81, 87, 100 +5) | 35 | 22 | 6 | 6/3 | cyanide | - | Junk 90%, Medicine 1 10% | Junk 90%, Medicine 2 10% | progress-scaled copy (defense 22) |
| Monkey | 0x000A | Day 2 | central_park (63, 83, 358) | 57 | 18 | 10 | 9/3 | - | tranq | Ammo 6 99%, Offense 1 1% | Medicine 1 99%, Offense 2 1% |  |
| Plant | 0x000B | Day 2 | central_park (65, 85, 87) | 60 | 18 | 10 | 9/4 | heat | cyanide, acid, tranq | Ammo 6 90%, Cure P 10% | Ammo 6 80%, Cure P 20% |  |
| Bear | 0x000C | Day 2 | central_park (75, 80, 82) | 75 | 18 | 12 | 16/5 | heat | tranq | Ammo 15 90%, Medicine 1 10% | Ammo 6 50%, Ammo 15 50% |  |
| Yellow Rat | 0x0010 | Day 3 | nypd (100, 110, 113, 121) | 70 | 15 | 26 | 11/5 | heat, cyanide, tranq | frost | Medicine 1 90%, nothing 10% | Ammo 6 |  |
| Spider | 0x000F | Day 3 | nypd (104, 113, 115, 116, 122) | 78 | 18 | 20 | 13/6 | frost | cyanide, tranq | Ammo 15 90%, Cure M 10% | Ammo 6 50%, Ammo 15 50% |  |
| Spider (no reward) (low) | 0x000F | Day 3 | nypd (104, 113, 115, 116, 120, 122) | 72 | 20 | 0 | 0/6 | frost | cyanide, tranq | nothing | nothing | NYPD; script spawn without EXP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Blackbird | 0x000C | Day 3 | nypd (107) | 35 | 22 | 6 | 6/3 | cyanide | - | Offense 1 | Junk 90%, Medicine 2 10% | progress-scaled copy (defense 22); progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| Dogman | 0x0011 | Day 3 | nypd (107, 111, 122) | 98 | 20 | 39 | 15/10 | - | tranq | Medicine 2 90%, Junk 10% | Medicine 1 90%, Medicine 3 10% |  |
| Blackbird | 0x0008 | Day 3 | nypd (120) | 35 | 18 | 6 | 6/3 | cyanide | - | Full Cure | Junk 90%, Medicine 2 10% | progress branch (V74 = 0); progress branch (V74, V80 = 0) |
| Blackbird | 0x000C | Day 3 | nypd (120) | 35 | 22 | 6 | 6/3 | cyanide | - | Full Cure | Junk 90%, Medicine 2 10% | progress-scaled copy (defense 22) |
| Spider | 0x000F | Day 3 | nypd (120) | 78 | 18 | 20 | 13/6 | frost | cyanide, tranq | Medicine 3 | Ammo 6 50%, Ammo 15 50% |  |
| Blackbird | 0x000C | Day 3 | nypd (121) | 35 | 22 | 6 | 6/3 | cyanide | - | Tool | Junk 90%, Medicine 2 10% | progress-scaled copy (defense 22); progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| Slime (medium) | 0x0012 | Day 3 | hospital (126, 129, 137, 139, 140, 141 +6) | 88 | 30 | 48 | 6/3 | heat, acid, tranq | frost | Ammo 6 90%, Cure P 10% | Ammo 6 50%, Medicine 1 50% | shrine lists 80 HP; game and log say 88 |
| Fly | 0x0013 | Day 3 | hospital (137, 140, 146, 147, 324, 327) | 110 | 30 | 86 | 9/5 | frost | heat, cyanide, acid | Medicine 2 90%, Cure M 10% | Ammo 6 50%, Cure M 50% |  |
| Ratman | 0x0014 | Day 3 | hospital (141, 146, 153, 154, 328) | 120 | 30 | 92 | 11/6 | heat, cyanide | frost, tranq | Medicine 2 66%, nothing 34% | Ammo 6 50%, Medicine 2 50% |  |
| Snake | 0x0016 | Day 4 | chinatown, sewer2 (162, 163, 167) | 99 | 34 | 287 | 8/6 | frost | heat, cyanide, acid, tranq | Ammo 6 90%, nothing 10% | Cure P |  |
| Cat | 0x0017 | Day 4 | chinatown (162, 163) | 135 | 34 | 361 | 21/8 | frost | heat, tranq | Ammo 6 90%, Ammo 15 10% | Ammo 15 90%, Medicine 2 10% |  |
| Bat | 0x0017 | Day 4 | sewer2, subway (167, 168, 169, 173, 178, 186) | 112 | 36 | 301 | 10/4 | heat | - | Cure D 90%, Ammo 6 10% | Medicine 2 80%, Cure D 20% |  |
| Frog (sewer) | 0x0018 | Day 4 | sewer2 (168, 169) | 153 | 36 | 425 | 12/8 | heat | cyanide, acid, tranq | Medicine 2 80%, Junk 20% | Junk |  |
| Alligator | 0x0019 | Day 4 | sewer2 (174) | 215 | 50 | 522 | 26/8 | heat | cyanide, tranq | Range 1 50%, Cr Evade 1 50% | Junk 80%, Tool 20% |  |
| Mole (medium) | 0x0019 | Day 4 | subway (186, 187) | 161 | 40 | 462 | 15/8 | heat, frost | cyanide, acid, tranq | Cure P 90%, Ammo 6 10% | nothing 99%, Offense 1 1% | shrine lists 457 EXP |
| Lizard (medium) | 0x001D | Days 4-5 | museum (197, 198, 199, 201, 206, 207 +8) | 200 | 40 | 896 | 16/4 | cyanide | heat, tranq | Junk 66%, Medicine 2 34% | nothing 90%, Ammo 30 10% | shrine lists 986 EXP |
| Armadillo | 0x001D | Days 4-5 | museum (197, 198, 199, 203, 206, 207 +10) | 240 | 71 | 1202 | 12/5 | frost | heat | Ammo 15 90%, Medicine 3 10% | nothing 80%, Ammo 15 20% |  |
| Dinosaur | 0x001E | Days 4-5 | museum (197, 198, 199, 203, 206, 207 +11) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% |  |
| Pterodactyl (medium) | 0x001F | Days 4-5 | museum (203, 223, 224, 229, 231, 233 +3) | 320 | 50 | 1829 | 32/10 | - | cyanide, acid, tranq | Medicine 3 90%, Ammo 30 10% | Cure D 50%, Ammo 15 50% | lower-EXP copy |
| Scorpion (tougher) (low) | 0x0020 | Days 4-5 | museum (205) | 430 | 78 | 3652 | 24/9 | - | cyanide, tranq | Medicine 3 90%, Range 2 10% | nothing 80%, Range 2 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Scorpion (medium) | 0x0020 | Days 4-5 | museum (231, 234, 243) | 390 | 78 | 2036 | 24/9 | - | cyanide, tranq | Cure P 90%, Ammo 30 10% | Cure P 90%, Medicine 4 10% | shrine lists 480 HP |
| Grey Rat | 0x001A | Days 4-5 | warehouse (263, 265, 333) | 215 | 40 | 135 | 40/5 | - | tranq | Ammo 30 | Ammo 30 |  |
| Gold Spider | 0x001A | Days 4-5 | warehouse (263, 265, 333) | 242 | 40 | 185 | 32/9 | heat | cyanide, acid, tranq | Ammo 30 | Cure M |  |
| Bird (medium) | 0x000A | Chrysler (EX) | chrysler (298, 308, 311) | 74 | 40 | 2 | 6/1 | cyanide | - | Junk 90%, Medicine 2 10% | Junk 80%, Medicine 3 20% | Chrysler; shrine 76 HP |
| Rat | 0x000B | Chrysler (EX) | chrysler (298, 308, 311) | 85 | 42 | 2 | 8/2 | heat, cyanide, tranq | frost, acid | nothing 90%, Cure M 10% | nothing 80%, Medicine 2 20% | Chrysler |
| Dinosaur (medium) | 0x000F | Chrysler (EX) | chrysler (299, 309, 310) | 106 | 49 | 4 | 9/3 | - | heat, cyanide, tranq | Ammo 6 90%, Medicine 1 10% | nothing 95%, Revive 5% | Chrysler; shrine 6 EXP |
| Bat | 0x0011 | Chrysler (EX) | chrysler (299, 309, 310, 385, 388, 389) | 98 | 45 | 3 | 8/1 | - | - | Medicine 1 90%, Cure D 10% | Cure D 95%, Medicine 3 5% | Chrysler |
| Snake | 0x0014 | Chrysler (EX) | chrysler (384, 386, 387, 391, 392, 393 +3) | 120 | 48 | 5 | 8/2 | - | heat, cyanide, acid, tranq | Ammo 6 90%, Medicine 1 10% | nothing 50%, Cure P 50% | Chrysler |
| Monkey | 0x0015 | Chrysler (EX) | chrysler (384, 387) | 158 | 62 | 9 | 10/2 | - | tranq | nothing 99%, Revive 1% | nothing 80%, Medicine 2 20% | Chrysler |
| Mole | 0x0013 | Chrysler (EX) | chrysler (385, 388, 389) | 144 | 52 | 7 | 12/4 | heat, frost | cyanide, acid, tranq | Medicine 2 90%, Ammo 15 10% | Medicine 2 95%, Revive 5% | Chrysler |
| Plant | 0x0015 | Chrysler (EX) | chrysler (391, 393, 394, 395, 396, 399 +2) | 280 | 65 | 27 | 15/5 | heat | cyanide, acid, tranq | Medicine 2 90%, Cure P 10% | nothing 80%, Medicine 3 20% | Chrysler |
| Spider | 0x0017 | Chrysler (EX) | chrysler (391, 392, 394, 395) | 205 | 68 | 23 | 15/3 | frost | cyanide, acid, tranq | nothing 80%, Ammo 30 20% | Cure M 95%, Revive 5% | Chrysler |
| Fly | 0x0016 | Chrysler (EX) | chrysler (392, 393, 396, 401) | 240 | 60 | 15 | 12/4 | frost | heat, cyanide, acid | Cure M 90%, Medicine 3 10% | nothing 95%, Medicine 3 5% | Chrysler |
| Lizard | 0x001A | Chrysler (EX) | chrysler (398, 400, 403) | 315 | 70 | 40 | 15/3 | - | heat, tranq | Medicine 3 90%, Cure M 10% | Ammo 15 50%, Ammo 30 50% | Chrysler |
| Cat | 0x0020 | Chrysler (EX) | chrysler (398, 400, 403) | 375 | 74 | 52 | 15/3 | - | tranq | Ammo 6 90%, Ammo 30 10% | nothing 95%, Medicine 3 5% | Chrysler |
| Frog | 0x001E | Chrysler (EX) | chrysler (405, 407, 408, 409, 410) | 460 | 88 | 133 | 20/4 | frost | heat, acid, tranq | nothing 80%, Ammo 15 20% | Medicine 3 95%, Revive 5% | Chrysler |
| Parrot | 0x001F | Chrysler (EX) | chrysler (405, 406, 407, 408, 409) | 420 | 85 | 115 | 18/3 | frost, cyanide, acid | heat, tranq | Medicine 2 90%, Medicine 4 10% | nothing 80%, Medicine 4 20% | Chrysler |
| Armadillo | 0x0026 | Chrysler (EX) | chrysler (405, 408, 409, 413, 416, 417) | 410 | 92 | 144 | 20/5 | - | cyanide | nothing 80%, Medicine 3 20% | nothing 95%, Medicine 4 5% | Chrysler |
| Scorpion | 0x0023 | Chrysler (EX) | chrysler (406, 410) | 580 | 98 | 160 | 24/4 | frost | heat, cyanide, tranq | Ammo 6 90%, Ammo 30 10% | Medicine 4 80%, Revive 20% | Chrysler |
| Gold Rat | 0x0028 | Chrysler (EX) | - (412, 414, 415, 421, 422, 423 +1) | 590 | 95 | 327 | 25/5 | heat, cyanide, tranq | frost | nothing 90%, Revive 10% | Medicine 4 80%, Ammo 30 20% | Chrysler |
| Ratman | 0x002D | Chrysler (EX) | - (412, 414, 415) | 715 | 104 | 364 | 28/7 | cyanide | frost, tranq | Ammo 15 90%, Ammo 30 10% | nothing 95%, Revive 5% | Chrysler |
| Giant Rat | 0x0030 | Chrysler (EX) | - (412) | 790 | 150 | 562 | 32/8 | heat, cyanide, tranq | frost | Medicine 3 90%, Medicine 4 10% | nothing 80%, Rocket 20% | Chrysler |
| Snake (upper floors) (medium) | 0x002E | Chrysler (EX) | - (419, 420) | 780 | 98 | 804 | 28/6 | - | heat, cyanide, acid | nothing 66%, Medicine 4 34% | nothing 80%, Medicine 4 20% | Chrysler; shrine 800 HP |
| Slime | 0x0031 | Chrysler (EX) | - (419, 420, 421, 422, 423) | 880 | 112 | 855 | 35/7 | acid, tranq | frost | Junk 90%, Medicine 4 10% | Ammo 30 80%, Medicine 4 20% | Chrysler |
| Bear | 0x0035 | Chrysler (EX) | - (419, 420) | 1000 | 128 | 894 | 35/7 | heat | tranq | nothing 80%, Medicine 4 20% | nothing 95%, Revive 5% | Chrysler |
| Dogman | 0x0034 | Chrysler (EX) | - (421, 422, 423, 424) | 980 | 120 | 920 | 44/11 | - | - | Ammo 30 90%, Revive 10% | nothing 80%, Medicine 4 20% | Chrysler |

## Bosses and forced fights

| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| Rat | 0x0002 | Day 1 | theater (16) | 12 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| Parrot | 0x0002 | Day 1 | theater (22) | 10 | 4 | 1 | 2/1 | frost, cyanide, acid | heat, tranq | Medicine 1 90%, nothing 10% | Ammo 6 80%, nothing 20% |  |
| Alligator (tail) | 0x0100 | Day 1 | sewer (34) | 80 | 6 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | Range 2 90%, Pe 2 10% | Range 1 50%, Pe 1 50% | scripted HP; sewer boss part; reward on the body |
| Alligator (body) | 0x0307 | Day 1 | sewer (34) | 120 | 200 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | scripted HP; first boss, sewer; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dogman | 0x0011 | Day 3 | nypd (114) | 98 | 20 | 39 | 15/10 | - | tranq | Medicine 2 90%, Junk 10% | Medicine 1 90%, Medicine 3 10% |  |
| Giant Dogman | 0x0012 | Day 3 | nypd (118) | 150 | 25 | 45 | 23/10 | - | tranq | Sg550 | Defense 1 29 80%, Defense 2 20% |  |
| Sheeva (left head) | 0x0100 | Day 3 | nypd (123) | 300 | 24 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | nothing | nothing | NYPD map 123; reward set elsewhere |
| Sheeva (right head) | 0x0100 | Day 3 | nypd (123) | 200 | 24 | 0 | 0/0 | frost | heat, cyanide, acid, tranq | nothing | nothing |  |
| Sheeva (center head) | 0x0100 | Day 3 | nypd (123) | 400 | 24 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing |  |
| Spawn (medium) | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 170 | 30 | 114 | 15/6 | frost | cyanide | Cure M 90%, Medicine 1 10% | Medicine 2 80%, Cure M 20% | shrine lists 90 EXP; game says 114; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 45 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | spawned by Spawn; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 0 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Slime | 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | B Vest 1 | Defense 1 29 90%, Tool 10% | progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| Giant Slime | 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | Ammo 15 | Defense 1 29 90%, Tool 10% |  |
| Giant Spider (phase 1) | 0x0216 | Day 3 | hospital (156) | 450 | 33 | 6500 | 80/10 | - | cyanide, acid, tranq | nothing | nothing | scripted HP; shrine total 860 = 450 + phase 2 |
| Hospital map 159 actor (low) | 0x0016 | Day 3 | hospital (159) | 152 | 30 | 0 | 0/6 | frost | cyanide, tranq | nothing | nothing | unnamed; no reward; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (head, phase 1) (medium) | 0x041A | Day 4 | subway (188) | 500 | 35 | 10000 | 90/13 | - | cyanide, acid, tranq | Ammo 30 90%, Offense 1 10% | Tool | scripted HP; shrine head 810; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (middle) | 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Range 1 10% | Ammo 30 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (middle) | 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Cr Evade 1 10% | Medicine 3 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (tail) | 0x041A | Day 4 | subway (188) | 180 | 35 | 0 | 80/19 | - | cyanide, acid, tranq | M79 3 | Cure P | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dinosaur | 0x001E | Days 4-5 | museum (199) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% | progress branch (V34 = 0); progress branch (V34, V42 = 0); progress branch (V34, V42, V80 = 0); progress branch (V34, V80 = 0) |
| Armadillo (forced fight) (medium) | 0x001D | Days 4-5 | museum (210) | 240 | 71 | 2326 | 12/5 | frost | heat, cyanide | Medicine 4 90%, Full Cure 10% | nothing 95%, Defense 1 29 5% |  |
| Pterodactyl | 0x001F | Days 4-5 | museum (221) | 320 | 50 | 3256 | 32/10 | - | cyanide, acid, tranq | Medicine 4 | Range 1 80%, Bullet Cap 1 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (phase 1) (medium) | 0x0221 | Days 4-5 | museum (245) | 750 | 100 | 50000 | 60/10 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | shrine total 1600; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (phase 2) (medium) | 0x0421 | Days 4-5 | museum (245) | 900 | 65 | 0 | 60/10 | frost | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| ? | 0x0421 | Days 4-5 | museum (245) | 400 | 75 | 0 | 120/15 | - | heat, cyanide, acid, tranq | Ammo 6 90%, Offense 2 10% | nothing 95%, Defense 2 5% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Tyrannosaur | 0x0223 | Days 4-5 | museum (256) | 2400 | 78 | 34464 | 256/32 | - | cyanide, acid, tranq | M8000 | Tool | script EXP 100000 wraps to 34464 (u16); shrine says 30000 |
| Crab (claw) (medium) | 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing | shrine lists 410 |
| Crab (claw) (medium) | 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 50/12 | - | cyanide, acid, tranq | nothing | nothing | shrine lists 410 |
| Crab (body) | 0x0220 | Days 4-5 | warehouse (269) | 856 | 110 | 2510 | 100/15 | - | cyanide, acid, tranq | At4 | Offense 1 50%, Defense 1 29 50% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Crab (claw) (medium) | 0x041B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing |  |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1600 | 85 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Offense 1 50%, Defense 1 29 50% | scripted HP; map 273; shrine forms 1850 / 800 / 2550 / 2200 |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1750 | 70 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1900 | 55 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | scripted HP |
| Alligator (body) (low) | 0x0307 | late addition | sewer (348) | 0 | 6 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | late-addition copy, HP set elsewhere; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Spider (phase 2) (medium) | 0x0217 | late addition | hospital (380) | 400 | 25 | 6500 | 80/10 | - | cyanide, acid, tranq | G23 | Tool 80%, Super Tool 20% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being form (low) | 0x0026 | special scene | - (429) | 1300 | 90 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | cruiser special scene 429; shrine 1500 / 1600+1200 / 3500 / 8000 |
| Ultimate Being (3rd) (medium) | 0x0226 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | 3500 matches the shrine; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being (3rd) (medium) | 0x0426 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Spider (Chrysler) | 0x0218 | Chrysler (EX) | chrysler (291) | 1000 | 60 | 100 | 128/8 | - | heat, cyanide, acid, tranq | Chrysler Key1 | nothing | scripted HP; floor 10; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dinosaur (medium) | 0x000F | Chrysler (EX) | chrysler (295, 434) | 106 | 49 | 4 | 9/3 | - | heat, cyanide, tranq | Ammo 6 90%, Medicine 1 10% | nothing 95%, Revive 5% | Chrysler; shrine 6 EXP |
| Bat | 0x0011 | Chrysler (EX) | chrysler (295) | 98 | 45 | 3 | 8/1 | - | - | Medicine 1 90%, Cure D 10% | Cure D 95%, Medicine 3 5% | Chrysler |
| Monster Box | 0x002D | Chrysler (EX) | chrysler (295, 434, 435, 436, 437) | 700 | 100 | 255 | 0/0 | tranq | heat, frost, cyanide, acid | Ammo 30 66%, Revive 34% | nothing 80%, Medicine 4 20% | Chrysler |
| Eve (Chrysler) | 0x0263 | Chrysler (EX) | chrysler (318) | 40000 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | floor 77 (map 318); progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Eve (Chrysler) part (low) | 0x0263 | Chrysler (EX) | chrysler (318) | 8800 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | same room; role unknown; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Alligator (Chrysler) (medium) | 0x021D | Chrysler (EX) | chrysler (383) | 1200 | 72 | 150 | 256/16 | heat | frost, cyanide, acid, tranq | Chrysler Key2 | nothing | floor 20, a pair; shrine 1100; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Alligator (Chrysler) (medium) | 0x021D | Chrysler (EX) | chrysler (383) | 1200 | 72 | 150 | 256/16 | heat | frost, cyanide, acid, tranq | Revive | nothing | floor 20, a pair; shrine 1100; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, head) (medium) | 0x0422 | Chrysler (EX) | chrysler (390) | 1200 | 88 | 800 | 104/5 | frost | heat, cyanide, acid, tranq | Chrysler Key3 | nothing | scripted HP; floor 30; shrine head 1600 total; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, middle) (medium) | 0x0422 | Chrysler (EX) | chrysler (390) | 600 | 88 | 0 | 100/5 | frost | heat, cyanide, acid, tranq | nothing | nothing | shrine 500; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, tail) | 0x0422 | Chrysler (EX) | chrysler (390) | 800 | 88 | 0 | 80/4 | frost | heat, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (Chrysler, phase 1) (medium) | 0x0427 | Chrysler (EX) | chrysler (397) | 1200 | 140 | 2500 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; floor 40; shrine total 2900; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (Chrysler, phase 2) (medium) | 0x0427 | Chrysler (EX) | chrysler (397) | 1600 | 96 | 0 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| Triceratops (Chrysler, total) (low) | 0x0427 | Chrysler (EX) | chrysler (397) | 2800 | 96 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | Chrysler Key4 | nothing | shrine total 2900; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (medium) | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 400 | 77 | 64 | 20/5 | frost | cyanide | Cure M 90%, Ammo 15 10% | nothing 95%, Medicine 4 5% | Chrysler; shrine 78 EXP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 100 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | Chrysler; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 0 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach (offspring) (medium) | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; same HP, 10 EXP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach (offspring) (medium) | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | same HP, 10 EXP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | scripted HP; floor 50; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | floor 50; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Crab (Chrysler, body) (medium) | 0x023B | Chrysler (EX) | - (411) | 6400 | 160 | 10000 | 240/39 | - | heat, frost, cyanide, acid, tranq | Chrysler Key6 | nothing | scripted HP; floor 60; shrine 6500; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Crab (Chrysler, claw) (medium) | 0x023B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 148/33 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | shrine 1500 |
| Crab (Chrysler, claw) (medium) | 0x023B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | shrine 1500 |
| Crab (Chrysler, claw) (medium) | 0x043B | Chrysler (EX) | - (411) | 1600 | 112 | 0 | 125/23 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |
| Small Bee (medium) | 0x024A | Chrysler (EX) | - (418) | 600 | 112 | 0 | 30/12 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | shrine 500 |
| Large Bee (medium) | 0x024A | Chrysler (EX) | - (418) | 1200 | 150 | 128 | 300/37 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | shrine 1400 |
| Queen Bee (medium) | 0x024A | Chrysler (EX) | - (418) | 12000 | 200 | 20000 | 400/58 | - | heat, frost, cyanide, acid, tranq | Chrysler Key7 | nothing | scripted HP; floor 70; shrine 11300; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cat | 0x0020 | Chrysler (EX) | - (434, 435) | 375 | 74 | 52 | 15/3 | - | tranq | Ammo 6 90%, Ammo 30 10% | nothing 95%, Medicine 3 5% | Chrysler |
| Parrot | 0x001F | Chrysler (EX) | - (435, 436, 437) | 420 | 85 | 115 | 18/3 | frost, cyanide, acid | heat, tranq | Medicine 2 90%, Medicine 4 10% | nothing 80%, Medicine 4 20% | Chrysler |
| Armadillo | 0x0026 | Chrysler (EX) | - (436) | 410 | 92 | 144 | 20/5 | - | cyanide | nothing 80%, Medicine 3 20% | nothing 95%, Medicine 4 5% | Chrysler |

## Helpers (not Bestiary entries)

| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| ? | 0x0000 | Day 2 | central_park (75, 80, 82, 419, 420) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| ? | 0x0000 | Day 3 | nypd (123) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| ? | 0x0200 | Day 3 | chrysler, hospital (156, 291, 380) | 3392 | 29 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP |
| ? | 0x001A | Days 4-5 | warehouse (263, 265, 333) | 10 | 20 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x0200 | Chrysler (EX) | chrysler (291) | 200000 | 60 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| ? | 0x0017 | Chrysler (EX) | chrysler (391, 392, 394, 395) | 160 | 16 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x0231 | Chrysler (EX) | chrysler (404) | 1200 | 104 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing |  |

## Next

1. Extract the missing bosses (Eve fights, Worms, Sheeva, Ultimate Being) from the actors that set them up.
2. Read the EX scale from an EX-game save (story variable V80) to confirm the derived range.
3. Decide the Junk tiers (for example name + HP free; weaknesses; drops and steals).
