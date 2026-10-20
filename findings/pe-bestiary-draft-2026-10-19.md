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

- 145 logged (room, enemy) pairs; 144 found in the extraction, 140 with matching HP, defense and EXP.
- Drops, steals and BP matched on every found pair; resistances match every log row that recorded them
  (the first 42 enemy rows predate resistance logging and read as average).
- Not found (1): m188 0x021A. Mostly bosses whose identity is set by another actor or computed.
- Scripts the evaluator could not finish: 2.

## Names

- Names come from the RPGClassics Parasite Eve shrine (enemies and bosses pages), matched by HP, EXP
  and area (`findings/data/pe-bestiary-names-2026-10-19.json`; the shrine facts are in
  `pe-enemy-names-rpgclassics.json`). 144 of 151 stat blocks named: 84 high, 41 medium, 19 low confidence.
- Where the shrine and the game disagree, the game value is kept (the log confirms it): Slime 88 HP
  (shrine 80), Spawn 114 EXP (90), Lizard 896 EXP (986), Mole 462 EXP (457), Scorpion 390 HP (480).
  Tyrannosaur: the script sets 100,000 EXP, which the 16-bit EXP field wraps to 34,464.
- Chrysler Building enemies are written with their EX HP directly and match the shrine EX HP.
- EX Game scale for story enemies: the shrine EX HP of 29 named enemies fits one scale of 1.3969-1.3974 x
  (shared cell N10 = 91546-91582 instead of 65536); off that scale: Frog (sewer), Gold Spider, Mole, Rat, Scorpion, Slime.
- Not extracted (identity or HP set by another actor): Worm growth sizes (150 / 175 / 200, set by the fight script), Ultimate Being (2nd form body 1600 / wings 1200).

## Creatures

| Creature | Story (HP / EXP) | Chrysler EX (HP / EXP) |
|---|---|---|
| Actress | 40 / 0 | - |
| Rat | 12 / 2, 17 / 2, 14 / 3 | 85 / 2 |
| Parrot | 10 / 1 | 420 / 115 |
| Eve (rehearsal room) | 92 / 0 | - |
| Frog | 34 / 4, 153 / 425 | 460 / 133 |
| Alligator (tail) | 80 / 0 | - |
| Alligator (body) | 120 / 30, 0 / 30 | - |
| Green Snake | 32 / 6 | - |
| Red Snake | 44 / 8 | - |
| Blackbird | 35 / 6 | - |
| Monkey | 57 / 10 | 158 / 9 |
| Plant | 60 / 10 | 280 / 27 |
| Bear | 75 / 12 | 1000 / 894 |
| Worm | 120 / 80 | - |
| Eve (carriage) | 330 / 0 | - |
| Yellow Rat | 70 / 26 | - |
| Spider | 78 / 20, 72 / 0 | 205 / 23 |
| Dogman | 98 / 39 | 980 / 920 |
| Giant Dogman | 150 / 45 | - |
| Sheeva (left head) | 300 / 0 | - |
| Sheeva (right head) | 200 / 0 | - |
| Sheeva (center head) | 400 / 0 | - |
| Sheeva (body) | 10 / 1000 | - |
| Slime | 88 / 48 | 880 / 855 |
| Fly | 110 / 86 | 240 / 15 |
| Ratman | 120 / 92 | 715 / 364 |
| Spawn | 170 / 114 | 400 / 64 |
| Spawn (offspring) | 0 / 4, 45 / 4 | 0 / 8, 100 / 8 |
| Giant Slime | 201 / 60 | - |
| Giant Spider (phase 1) | 450 / 6500 | - |
| Hospital map 159 actor | 152 / 20 | - |
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
| Triceratops part | 400 / 0 | - |
| Tyrannosaur | 2400 / 34464 | - |
| Grey Rat | 215 / 135 | - |
| Gold Spider | 242 / 185 | - |
| Crab (claw) | 420 / 0 | - |
| Crab (body) | 856 / 2510 | - |
| Eve (Statue of Liberty) part | 1600 / 0, 1750 / 0, 1900 / 0 | - |
| Eve (Statue of Liberty, reward holder) | 10 / 0 | - |
| Ultimate Being (1st) | 1500 / 0 | - |
| Ultimate Being form | 950 / 0, 1300 / 0 | - |
| Giant Spider (phase 2) | 400 / 6500 | - |
| Ultimate Being (3rd) | 3500 / 0 | - |
| Ultimate Being (4th) | 7992 / 0 | - |
| Eve (final form) | 2200 / 10000 | - |
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
| Cockroach larva | - | 1200 / 0 |
| Crab (Chrysler, body) | - | 6400 / 10000 |
| Crab (Chrysler, claw) | - | 1600 / 0 |
| Gold Rat | - | 590 / 327 |
| Giant Rat | - | 790 / 562 |
| Squirrel | - | 670 / 2 |
| Small Bee | - | 600 / 0 |
| Large Bee | - | 1200 / 128 |
| Queen Bee | - | 12000 / 20000 |

## Coverage

| | Regular | Bosses / forced | Helpers (0 EXP, 0 BP) |
|---|---:|---:|---:|
| first seen Day 1 | 5 | 6 | 0 |
| first seen Day 2 | 7 | 2 | 1 |
| first seen Day 3 | 12 | 14 | 2 |
| first seen Day 4 | 6 | 4 | 0 |
| first seen Days 4-5 | 8 | 11 | 1 |
| first seen Day 6 | 0 | 4 | 0 |
| first seen late addition | 0 | 4 | 0 |
| first seen special scene | 0 | 6 | 0 |
| first seen Chrysler (EX) | 24 | 32 | 2 |
| **total distinct stat blocks** | **62** | **83** | **6** |

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
| Dinosaur | 0x001E | Days 4-5 | museum (197, 198, 199, 203, 206, 207 +13) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% |  |
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
| Squirrel | 0x0035 | Chrysler (EX) | - (413, 416, 417) | 670 | 200 | 2 | 250/30 | - | heat, frost, cyanide, acid, tranq | Medicine 4 90%, Revive 10% | Cure C 80%, Revive 20% | Chrysler 51-60; also a forced copy in map 437; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Snake (upper floors) (medium) | 0x002E | Chrysler (EX) | - (419, 420) | 780 | 98 | 804 | 28/6 | - | heat, cyanide, acid | nothing 66%, Medicine 4 34% | nothing 80%, Medicine 4 20% | Chrysler; shrine 800 HP |
| Slime | 0x0031 | Chrysler (EX) | - (419, 420, 421, 422, 423) | 880 | 112 | 855 | 35/7 | acid, tranq | frost | Junk 90%, Medicine 4 10% | Ammo 30 80%, Medicine 4 20% | Chrysler |
| Bear | 0x0035 | Chrysler (EX) | - (419, 420) | 1000 | 128 | 894 | 35/7 | heat | tranq | nothing 80%, Medicine 4 20% | nothing 95%, Revive 5% | Chrysler |
| Dogman | 0x0034 | Chrysler (EX) | - (421, 422, 423, 424) | 980 | 120 | 920 | 44/11 | - | - | Ammo 30 90%, Revive 10% | nothing 80%, Medicine 4 20% | Chrysler |

## Bosses and forced fights

| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| Actress | 0x0201 | Day 1 | theater (5) | 40 | 9 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP; first battle (map 5); scripted HP |
| Rat | 0x0002 | Day 1 | theater (16) | 12 | 4 | 2 | 5/2 | heat, cyanide, tranq | frost | Ammo 6 80%, nothing 20% | Ammo 6 80%, nothing 20% |  |
| Parrot | 0x0002 | Day 1 | theater (22) | 10 | 4 | 1 | 2/1 | frost, cyanide, acid | heat, tranq | Medicine 1 90%, nothing 10% | Ammo 6 80%, nothing 20% |  |
| Eve (rehearsal room) (medium) | 0x0204 | Day 1 | theater (23) | 92 | 5 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | Pe 1 80%, Pe 3 20% | scripted HP; map 23; shrine 100 |
| Alligator (tail) | 0x0100 | Day 1 | sewer (34) | 80 | 6 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | Range 2 90%, Pe 2 10% | Range 1 50%, Pe 1 50% | scripted HP; sewer boss part; reward on the body |
| Alligator (body) | 0x0307 | Day 1 | sewer (34) | 120 | 200 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | scripted HP; first boss, sewer; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Worm (medium) | 0x020D | Day 2 | central_park (86) | 120 | 13 | 80 | 80/4 | - | frost, cyanide, acid, tranq | Defense 1 29 66%, Ammo 15 34% | Ammo 15 80%, Tool 20% | map 86; shrine sizes 125 / 150 / 175 / 200 (the script grows the survivors); progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Eve (carriage) (medium) | 0x020E | Day 2 | central_park (89) | 330 | 13 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Pe 3 80%, Defense 3 20% | scripted HP; map 89; shrine 320; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dogman | 0x0011 | Day 3 | nypd (114) | 98 | 20 | 39 | 15/10 | - | tranq | Medicine 2 90%, Junk 10% | Medicine 1 90%, Medicine 3 10% |  |
| Giant Dogman | 0x0012 | Day 3 | nypd (118) | 150 | 25 | 45 | 23/10 | - | tranq | Sg550 | Defense 1 29 80%, Defense 2 20% |  |
| Sheeva (left head) | 0x0100 | Day 3 | nypd (123) | 300 | 24 | 0 | 0/0 | heat | frost, cyanide, acid, tranq | nothing | nothing | NYPD map 123; reward set elsewhere |
| Sheeva (right head) | 0x0100 | Day 3 | nypd (123) | 200 | 24 | 0 | 0/0 | frost | heat, cyanide, acid, tranq | nothing | nothing |  |
| Sheeva (center head) | 0x0100 | Day 3 | nypd (123) | 400 | 24 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing |  |
| Sheeva (body) (medium) | 0x0312 | Day 3 | nypd (123) | 10 | 24 | 1000 | 110/8 | - | cyanide, acid, tranq | M9 2 | Super Tool | scripted HP; map 123; holds the 1000 EXP and BP for the three heads; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (medium) | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 170 | 30 | 114 | 15/6 | frost | cyanide | Cure M 90%, Medicine 1 10% | Medicine 2 80%, Cure M 20% | shrine lists 90 EXP; game says 114; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 0 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | HP written after spawn; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x0015 | Day 3 | hospital (145, 152, 153, 154, 332) | 45 | 30 | 4 | 3/1 | cyanide | acid, tranq | nothing | nothing | spawned by Spawn; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Slime | 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | B Vest 1 | Defense 1 29 90%, Tool 10% | progress branch (V80, V97 = 0); progress branch (V97 = 0) |
| Giant Slime | 0x0014 | Day 3 | hospital (149) | 201 | 30 | 60 | 21/11 | heat, acid | frost, cyanide, tranq | Ammo 15 | Defense 1 29 90%, Tool 10% |  |
| Giant Spider (phase 1) | 0x0216 | Day 3 | hospital (156) | 450 | 33 | 6500 | 80/10 | - | cyanide, acid, tranq | nothing | nothing | scripted HP; shrine total 860 = 450 + phase 2 |
| Hospital map 159 actor (low) | 0x0016 | Day 3 | hospital (159) | 152 | 30 | 20 | 24/6 | frost | cyanide, tranq | Cure M 80%, Ammo 15 20% | Offense 1 80%, Offense 2 20% | unnamed; not in the shrine lists; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x0016 | Day 3 | hospital (159) | 152 | 30 | 0 | 0/6 | frost | cyanide, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (head, phase 1) (medium) | 0x041A | Day 4 | subway (188) | 500 | 35 | 10000 | 90/13 | - | cyanide, acid, tranq | Ammo 30 90%, Offense 1 10% | Tool | scripted HP; shrine head 810; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (middle) | 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Range 1 10% | Ammo 30 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (middle) | 0x041A | Day 4 | subway (188) | 120 | 32 | 0 | 65/19 | - | cyanide, acid, tranq | Medicine 3 90%, Cr Evade 1 10% | Medicine 3 | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (tail) | 0x041A | Day 4 | subway (188) | 180 | 35 | 0 | 80/19 | - | cyanide, acid, tranq | M79 3 | Cure P | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dinosaur | 0x001E | Days 4-5 | museum (199) | 280 | 47 | 1530 | 32/10 | frost | heat, cyanide, tranq | Ammo 15 90%, Medicine 3 10% | Medicine 1 80%, Medicine 2 20% | progress branch (V34 = 0); progress branch (V34, V42 = 0); progress branch (V34, V42, V80 = 0); progress branch (V34, V80 = 0) |
| Armadillo (forced fight) (medium) | 0x001D | Days 4-5 | museum (210) | 240 | 71 | 2326 | 12/5 | frost | heat, cyanide | Medicine 4 90%, Full Cure 10% | nothing 95%, Defense 1 29 5% |  |
| Pterodactyl | 0x001F | Days 4-5 | museum (221) | 320 | 50 | 3256 | 32/10 | - | cyanide, acid, tranq | Medicine 4 | Range 1 80%, Bullet Cap 1 20% | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (phase 1) (medium) | 0x0221 | Days 4-5 | museum (245) | 750 | 100 | 50000 | 60/10 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | shrine total 1600; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (phase 2) (medium) | 0x0421 | Days 4-5 | museum (245) | 900 | 65 | 0 | 60/10 | frost | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| Triceratops part (low) | 0x0421 | Days 4-5 | museum (245) | 400 | 75 | 0 | 120/15 | - | heat, cyanide, acid, tranq | Ammo 6 90%, Offense 2 10% | nothing 95%, Defense 2 5% | map 245; second actor of the fight; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Tyrannosaur | 0x0223 | Days 4-5 | museum (256) | 2400 | 78 | 34464 | 256/32 | - | cyanide, acid, tranq | M8000 | Tool | script EXP 100000 wraps to 34464 (u16); shrine says 30000 |
| Crab (claw) (medium) | 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing | shrine lists 410 |
| Crab (claw) (medium) | 0x021B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 50/12 | - | cyanide, acid, tranq | nothing | nothing | shrine lists 410 |
| Crab (body) | 0x0220 | Days 4-5 | warehouse (269) | 856 | 110 | 2510 | 100/15 | - | cyanide, acid, tranq | At4 | Offense 1 50%, Defense 1 29 50% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Crab (claw) (medium) | 0x041B | Days 4-5 | warehouse (269) | 420 | 65 | 0 | 80/12 | - | cyanide, acid, tranq | nothing | nothing |  |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1600 | 85 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Offense 1 50%, Defense 1 29 50% | scripted HP; map 273; shrine forms 1850 / 800 / 2550 / 2200 |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1750 | 70 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Range 1 50%, Pe 1 50% | scripted HP |
| Eve (Statue of Liberty) part (low) | 0x0125 | Day 6 | liberty (273) | 1900 | 55 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Bullet Cap 1 50%, Cr Evade 1 50% | scripted HP |
| Eve (Statue of Liberty, reward holder) (low) | 0x0325 | Day 6 | liberty (273) | 10 | 100 | 0 | 1000/20 | - | cyanide, acid, tranq | nothing | Tool 80%, Trading Card 20% | map 273; BP 1000/20; progress branch (V0 = 0) / unresolved branch; progress branch (V0, V74 = 0) / unresolved branch; progress branch (V0, V74, V80 = 0) / unresolved branch; progress branch (V0, V80 = 0) / unresolved branch; progress branch (V74 = 0) / unresolved branch; progress branch (V74, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Alligator (body) (low) | 0x0307 | late addition | sewer (348) | 0 | 6 | 30 | 31/3 | heat, tranq | frost, cyanide, acid | Kv Vest 1 | Offense 1 50%, Cr Evade 1 50% | late-addition copy, HP set elsewhere; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being (1st) | 0x0225 | late addition | cruiser (350) | 1500 | 60 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP; maps 350 / 428; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being form (low) | 0x0225 | late addition | cruiser (350) | 950 | 80 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Junk | scripted HP; map 350; shrine 2nd form is 1600 body + 1200 wings; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Spider (phase 2) (medium) | 0x0217 | late addition | hospital (380) | 400 | 25 | 6500 | 80/10 | - | cyanide, acid, tranq | G23 | Tool 80%, Super Tool 20% | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being (1st) | 0x0225 | special scene | - (428) | 1500 | 50 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Ammo 30 80%, Full Recover 20% | scripted HP; maps 350 / 428; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being form (low) | 0x0026 | special scene | - (429) | 1300 | 90 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | cruiser special scene 429; shrine 1500 / 1600+1200 / 3500 / 8000 |
| Ultimate Being (3rd) (medium) | 0x0226 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | 3500 matches the shrine; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being (3rd) (medium) | 0x0426 | special scene | - (429) | 3500 | 42 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | Super Tool | scripted HP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Ultimate Being (4th) (medium) | 0x0226 | special scene | - (430) | 7992 | 1200 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | Junk | scripted HP; map 430; shrine 8000; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Eve (final form) | 0x0223 | special scene | - (432) | 2200 | 50 | 10000 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP; map 432 (statue special scene); progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Giant Spider (Chrysler) | 0x0218 | Chrysler (EX) | chrysler (291) | 1000 | 60 | 100 | 128/8 | - | heat, cyanide, acid, tranq | Chrysler Key1 | nothing | scripted HP; floor 10; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Dinosaur (medium) | 0x000F | Chrysler (EX) | chrysler (295, 434) | 106 | 49 | 4 | 9/3 | - | heat, cyanide, tranq | Ammo 6 90%, Medicine 1 10% | nothing 95%, Revive 5% | Chrysler; shrine 6 EXP |
| Bat | 0x0011 | Chrysler (EX) | chrysler (295) | 98 | 45 | 3 | 8/1 | - | - | Medicine 1 90%, Cure D 10% | Cure D 95%, Medicine 3 5% | Chrysler |
| Monster Box | 0x002D | Chrysler (EX) | chrysler (295, 434, 435, 436, 437) | 700 | 100 | 255 | 0/0 | tranq | heat, frost, cyanide, acid | Ammo 30 66%, Revive 34% | nothing 80%, Medicine 4 20% | Chrysler |
| Eve (Chrysler) | 0x0263 | Chrysler (EX) | chrysler (318) | 40000 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | floor 77 (map 318); progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Eve (Chrysler) part (low) | 0x0263 | Chrysler (EX) | chrysler (318) | 8800 | 130 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | same room; role unknown; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Alligator (Chrysler) (medium) | 0x021D | Chrysler (EX) | chrysler (383) | 1200 | 72 | 150 | 256/16 | heat | frost, cyanide, acid, tranq | Chrysler Key2 50%, Revive 50% | nothing | floor 20, a pair; shrine 1100; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, head) (medium) | 0x0422 | Chrysler (EX) | chrysler (390) | 1200 | 88 | 800 | 104/5 | frost | heat, cyanide, acid, tranq | Chrysler Key3 | nothing | scripted HP; floor 30; shrine head 1600 total; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, middle) (medium) | 0x0422 | Chrysler (EX) | chrysler (390) | 600 | 88 | 0 | 100/5 | frost | heat, cyanide, acid, tranq | nothing | nothing | shrine 500; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Centipede (Chrysler, tail) | 0x0422 | Chrysler (EX) | chrysler (390) | 800 | 88 | 0 | 80/4 | frost | heat, cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (Chrysler, phase 1) (medium) | 0x0427 | Chrysler (EX) | chrysler (397) | 1200 | 140 | 2500 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; floor 40; shrine total 2900; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Triceratops (Chrysler, phase 2) (medium) | 0x0427 | Chrysler (EX) | chrysler (397) | 1600 | 96 | 0 | 200/21 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| Triceratops (Chrysler, total) (low) | 0x0427 | Chrysler (EX) | chrysler (397) | 2800 | 96 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | Chrysler Key4 | nothing | shrine total 2900; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (medium) | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 400 | 77 | 64 | 20/5 | frost | cyanide | Cure M 90%, Ammo 15 10% | nothing 95%, Medicine 4 5% | Chrysler; shrine 78 EXP; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 0 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | Chrysler; HP written after spawn; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Spawn (offspring) (low) | 0x001F | Chrysler (EX) | chrysler (399, 401, 402) | 100 | 50 | 8 | 3/1 | cyanide | acid, tranq | nothing | nothing | Chrysler; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach (offspring) (medium) | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP; same HP, 10 EXP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | scripted HP; floor 50; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach (offspring) (medium) | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 10 | 10/18 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | same HP, 10 EXP; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach | 0x0231 | Chrysler (EX) | chrysler (404) | 4200 | 104 | 5000 | 321/18 | - | heat, frost, cyanide, acid, tranq | Chrysler Key5 | nothing | floor 50; progress branch (V11 = 0) / unresolved branch; progress branch (V11, V80 = 0) / unresolved branch; progress branch (V80 = 0) / unresolved branch; unresolved branch |
| Cockroach larva (low) | 0x0231 | Chrysler (EX) | chrysler (404) | 1200 | 104 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | map 404; grows into a second Cockroach |
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
| Squirrel | 0x0035 | Chrysler (EX) | - (437) | 670 | 200 | 2 | 250/30 | - | heat, frost, cyanide, acid, tranq | Medicine 4 90%, Revive 10% | Cure C 80%, Revive 20% | Chrysler 51-60; also a forced copy in map 437; progress branch (V80 = 0) / unresolved branch; unresolved branch |

## Helpers (not Bestiary entries)

| Name | ID | First seen | Where (maps) | HP | Def | EXP | BP | Weak | Strong | Drop | Steal | Notes |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| ? | 0x0000 | Day 2 | central_park (75, 80, 82, 419, 420) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| ? | 0x0000 | Day 3 | nypd (123) | 10 | 0 | 0 | 0/0 | - | - | nothing | nothing |  |
| ? | 0x0200 | Day 3 | chrysler, hospital (156, 291, 380) | 3392 | 29 | 0 | 0/0 | - | cyanide, acid, tranq | nothing | nothing | scripted HP |
| ? | 0x001A | Days 4-5 | warehouse (263, 265, 333) | 10 | 20 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |
| ? | 0x0200 | Chrysler (EX) | chrysler (291) | 200000 | 60 | 0 | 0/0 | - | heat, frost, cyanide, acid, tranq | nothing | nothing | scripted HP |
| ? | 0x0017 | Chrysler (EX) | chrysler (391, 392, 394, 395) | 160 | 16 | 0 | 0/0 | frost | cyanide, acid, tranq | nothing | nothing | progress branch (V80 = 0) / unresolved branch; unresolved branch |

## Mid-fight values

Stat writes after the setup (`phases` in the extract): growth, phase changes and the real HP of
scripted bosses. Each write's run of arithmetic is evaluated at the first-playthrough scale; *unknown*
means the value is built from something the fight tracks (damage carried over, current HP). Death
handling (HP set to 0) is left out. Window = room offsets of the evaluated instructions.

- Scripted bosses: setup stores HP + 1,000,000; the next block writes the fighting HP (Actress 40,
  Eve carriage 330, Giant Spider 450, Centipede 500, Crab 856, Eve final form 2200, ...).
- Worms: max HP 120 at the start, then 150, 180 and 210 as each one dies (defense 13); the damage
  already taken carries into the new maximum.
- Centipede: the head's 500 is followed by a 300 HP phase that also switches the kind byte to 2, which
  is why the log recorded it as 0x021A. Chrysler Centipede: 1200 then 300.
- Ultimate Being: no separate 2nd-form block; the script tracks HP as a percentage of max and, below 60%,
  clamps it to 60% (+ the scripted offset) to trigger the change. 4th form: 7992, then 999,999 and
  499,999 in the special-bullet phase.

| Name | ID | Map / actor | Window (room offsets) | HP write sector:byte | Writes |
|---|---|---|---|---|---|
| Actress | 0x0201 | 5 / 2 | 139488-140256 | 11117:320 | hp 40, hp_cap 40, defense 9, exp 0, rank 1, kind 2 |
| Rat | 0x0002 | 13 / 2 | 32576-33428 | 12161:1988 | hp 13, hp_cap 13, defense 4, exp 2, rank 2, kind 0 |
| Eve (rehearsal room) | 0x0204 | 23 / 2 | 301956-302808 | 14051:1720 | hp scripted 92, hp_cap 1000092, defense 5, exp 0, rank 4, kind 2 |
| Alligator (tail) | 0x0100 | 34 / 4 | 171344-172056 | 16680:1992 | hp scripted 80, hp_cap 1000080, defense 6, kind 1 |
| Alligator (body) | 0x0307 | 34 / 3 | 157100-157936 | 16673:1584 | hp 120, hp_cap 120, defense 200, exp 30, rank 7, kind 3 |
| Worm | 0x020D | 86 / 3 | 99548-100364 | 30250:1988 | hp unknown, hp_cap 210, defense 13 |
| Worm | 0x020D | 86 / 3 | 101036-101852 | 30251:1428 | hp unknown, hp_cap 180, defense 13 |
| Worm | 0x020D | 86 / 3 | 102756-103572 | 30252:1100 | hp unknown, hp_cap 150, defense 13 |
| Eve (carriage) | 0x020E | 89 / 1 | 328240-329028 | 31118:692 | hp 330, hp_cap 330, defense 13, exp 0, rank 14, kind 2 |
| Sheeva (body) | 0x0312 | 123 / 1 | 229032-229884 | 38733:1836 | hp 10, hp_cap 10, defense 24, exp 1000, rank 18, kind 3 |
| ? | 0x0200 | 156 / 4 | 230332-231020 | 46003:1524 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| ? | 0x0200 | 156 / 5 | 231756-232444 | 46004:900 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| ? | 0x0200 | 156 / 6 | 233180-233868 | 46005:276 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| ? | 0x0200 | 291 / 5 | 215296-215984 | 74591:824 | hp unknown, hp_cap unknown, defense unknown, kind 2 |
| ? | 0x0200 | 291 / 6 | 216720-217408 | 74592:200 | hp unknown, hp_cap unknown, defense unknown, kind 2 |
| ? | 0x0200 | 380 / 4 | 230772-231460 | 89181:1964 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| ? | 0x0200 | 380 / 5 | 232196-232884 | 89182:1340 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| ? | 0x0200 | 380 / 6 | 233620-234308 | 89183:716 | hp scripted 3392, hp_cap 1003392, defense 29, kind 2 |
| Giant Spider (phase 1) | 0x0216 | 156 / 3 | 208444-209248 | 45992:1728 | hp 450, hp_cap 450, defense 33, exp 6500, rank 22, kind 2 |
| Centipede (head, phase 1) | 0x041A | 188 / 5 | 247604-248440 | 51847:1976 | hp 500, hp_cap 500, defense 35, exp 10000, rank 26, kind 2 |
| Centipede (head, phase 1) | 0x041A | 188 / 5 | 263256-263384 | 51855:1176 | hp 300, hp_cap 300, kind 2 |
| Triceratops (phase 2) | 0x0421 | 245 / 7 | 208692-209392 | 65015:1976 | hp 900, hp_cap 900, defense 65, exp 0, rank 33, kind 2 |
| Crab (body) | 0x0220 | 269 / 3 | 176208-177044 | 70013:212 | hp 856, hp_cap 856, defense 110, exp 2510, rank 32, kind 2 |
| Eve (Statue of Liberty) part | 0x0125 | 273 / 5 | 299596-300244 | 71171:1156 | hp scripted 1600, hp_cap 1001600, defense 85, rank 37, kind 1 |
| Eve (Statue of Liberty) part | 0x0125 | 273 / 6 | 300656-301304 | 71172:168 | hp scripted 1750, hp_cap 1001750, defense 70, rank 37, kind 1 |
| Eve (Statue of Liberty) part | 0x0125 | 273 / 7 | 301716-302364 | 71172:1228 | hp scripted 1900, hp_cap 1001900, defense 55, rank 37, kind 1 |
| Alligator (body) | 0x0307 | 348 / 2 | 168572-169408 | 84184:768 | hp 120, hp_cap 120, defense 200, exp 30, rank 7, kind 3 |
| Alligator (body) | 0x0307 | 348 / 2 | 169836-170020 | 84184:1956 | hp unknown, hp_cap unknown |
| Ultimate Being (1st) | 0x0225 | 350 / 2 | 230756-231656 | 84664:1512 | hp 1500, hp_cap 1500, defense 60, exp 0, rank 37, kind 2 |
| Ultimate Being (1st) | 0x0225 | 350 / 2 | 232572-232876 | 84665:1380 | hp unknown |
| Ultimate Being (1st) | 0x0225 | 350 / 2 | 246016-246216 | - | defense 98 |
| Ultimate Being (1st) | 0x0225 | 350 / 2 | 246016-246216 | 84672:456 | hp scripted 1, defense 98 |
| Ultimate Being form | 0x0225 | 350 / 3 | 247488-248388 | 84672:1860 | hp 950, hp_cap 950, defense 80, exp 0, rank 37, kind 2 |
| Ultimate Being form | 0x0225 | 350 / 3 | 254168-254320 | - | defense 50 |
| Ultimate Being form | 0x0225 | 350 / 3 | 254168-254320 | 84676:368 | hp scripted 1, defense 50 |
| Giant Spider (phase 2) | 0x0217 | 380 / 3 | 208220-209056 | 89170:1504 | hp 400, hp_cap 400, defense 25, exp 6500, rank 23, kind 2 |
| Ultimate Being (1st) | 0x0225 | 428 / 2 | 163524-164392 | 99381:1864 | hp 1500, hp_cap 1500, defense 50, exp 0, rank 37, kind 2 |
| Ultimate Being (4th) | 0x0226 | 430 / 2 | 232076-232816 | 100013:784 | hp 7992, hp_cap 7992, defense 1200, exp 0, rank 38, kind 2 |
| Ultimate Being (4th) | 0x0226 | 430 / 2 | 247016-247200 | 100020:1424 | hp 999999 |
| Ultimate Being (4th) | 0x0226 | 430 / 2 | 247256-247272 | 100020:1512 | hp 499999 |
| Eve (final form) | 0x0223 | 432 / 2 | 299440-300244 | 100429:564 | hp 2200, hp_cap 2200, defense 50, exp 10000, rank 35, kind 2 |
| ? | 0x0200 | 291 / 4 | 214048-214560 | 74590:1448 | hp scripted 200000, hp_cap 1200000, defense 60, kind 2 |
| Giant Spider (Chrysler) | 0x0218 | 291 / 3 | 195136-195780 | 74581:660 | hp 1000, hp_cap 1000, defense 60, exp 100, rank 24, kind 2 |
| Centipede (Chrysler, head) | 0x0422 | 390 / 3 | 245992-246636 | 91097:316 | hp 1200, hp_cap 1200, defense 88, exp 800, rank 34, kind 2 |
| Centipede (Chrysler, head) | 0x0422 | 390 / 3 | 261452-261564 | 91104:1420 | hp 300, hp_cap 300, kind 2 |
| Triceratops (Chrysler, phase 1) | 0x0427 | 397 / 3 | 183536-184040 | 92620:1312 | hp 1200, hp_cap 1200, defense 140, exp 2500, rank 39, kind 2 |
| Triceratops (Chrysler, phase 2) | 0x0427 | 397 / 4 | 197172-197644 | 92627:612 | hp 1600, hp_cap 1600, defense 96, exp 0, rank 39, kind 2 |
| Crab (Chrysler, body) | 0x023B | 411 / 3 | 165732-166376 | 95534:1976 | hp 6400, hp_cap 6400, defense 160, exp 10000, rank 59, kind 2 |
| Queen Bee | 0x024A | 418 / 5 | 268380-269024 | 96885:176 | hp 12000, hp_cap 12000, defense 200, exp 20000, rank 74, kind 2 |
| Queen Bee | 0x024A | 418 / 5 | 281432-281472 | 96891:896 | hp unknown |

## Where in the data

How to go back to any stat block. Rooms are read from "Parasite Eve (USA) (Disc N).bin" ("both" =
byte-identical on the two discs) starting at the room LBA, 2048 user-data bytes per sector. Offsets
are into that room blob; the HP sector / byte is where the HP-setting `Entity_SetField` instruction
sits. *entry* is where evaluation started: the script start, or the stat block a boss script jumps
to. Full detail (rank, kind, EXP, defense, drop and steal writes) is in
`findings/data/pe-bestiary-draft-2026-10-19.json` (`sources`) and the raw
`pe-bestiary-extract-2026-10-19.json`. Re-run: `python -m pe_weapon_sim.extract_bestiary --out
findings/data/pe-bestiary-extract-2026-10-19.json` then `python -m pe_weapon_sim.report_bestiary`.

| Name | ID | HP | Disc | Map | Room LBA | Actor | Script start | Entry | HP write (room offset) | HP sector:byte |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| Actress | 0x0201 | 40 | both | 5 | 11049 | 2 | 137428 | 139232 | 140464 | 11117:1200 |
| Rat | 0x0002 | 12 | both | 12 | 12007 | 5 | 87556 | 87556 | 88088 | 12050:24 |
| Rat | 0x0002 | 12 | both | 14 | 12381 | 6 | 76428 | 76428 | 76960 | 12418:1184 |
| Rat | 0x0002 | 12 | both | 27 | 14756 | 3 | 35032 | 35032 | 35564 | 14773:748 |
| Rat | 0x0002 | 12 | both | 28 | 15016 | 7 | 96344 | 96344 | 96876 | 15063:620 |
| Rat | 0x0002 | 17 | both | 13 | 12146 | 2 | 32176 | 32176 | 33596 | 12162:828 |
| Parrot | 0x0002 | 10 | both | 14 | 12381 | 7 | 84064 | 84064 | 84624 | 12422:656 |
| Rat | 0x0002 | 12 | both | 16 | 12657 | 6 | 94508 | 94508 | 95112 | 12703:904 |
| Parrot | 0x0002 | 10 | both | 22 | 13656 | 4 | 69284 | 69284 | 69872 | 13690:240 |
| Eve (rehearsal room) | 0x0204 | 92 | both | 23 | 13904 | 2 | 299736 | 301772 | 302776 | 14051:1720 |
| Frog | 0x0004 | 34 | both | 28 | 15016 | 8 | 103980 | 103980 | 104540 | 15067:92 |
| Frog | 0x0004 | 34 | both | 32 | 15937 | 6 | 56388 | 56388 | 56948 | 15964:1652 |
| Rat (sewer variant) | 0x0002 | 14 | both | 30 | 15416 | 5 | 39708 | 39708 | 40296 | 15435:1384 |
| Alligator (tail) | 0x0100 | 80 | both | 34 | 16597 | 4 | 170980 | 170980 | 171976 | 16680:1992 |
| Alligator (body) | 0x0307 | 120 | both | 34 | 16597 | 3 | 156740 | 156740 | 158496 | 16674:800 |
| Green Snake | 0x0007 | 32 | both | 59 | 24373 | 5 | 73932 | 73932 | 74492 | 24409:764 |
| Green Snake | 0x0007 | 32 | both | 62 | 24966 | 6 | 66812 | 66812 | 67372 | 24998:1836 |
| Green Snake | 0x0007 | 32 | both | 78 | 28502 | 5 | 71596 | 71596 | 72072 | 28537:392 |
| Red Snake | 0x0008 | 44 | both | 59 | 24373 | 6 | 84740 | 84740 | 85300 | 24414:1332 |
| Red Snake | 0x0008 | 44 | both | 66 | 25849 | 5 | 61120 | 61120 | 61680 | 25879:240 |
| Red Snake | 0x0008 | 44 | both | 67 | 26119 | 4 | 98196 | 98196 | 98756 | 26167:452 |
| Red Snake | 0x0008 | 44 | both | 78 | 28502 | 4 | 59224 | 59224 | 59784 | 28531:392 |
| Red Snake | 0x0008 | 44 | both | 82 | 29291 | 3 | 156508 | 156508 | 157068 | 29367:1420 |
| Blackbird | 0x0008 | 35 | both | 61 | 24699 | 5 | 62360 | 62360 | 62976 | 24729:1536 |
| Blackbird | 0x0008 | 35 | both | 67 | 26119 | 3 | 80016 | 80016 | 80632 | 26158:760 |
| Blackbird | 0x0008 | 35 | both | 80 | 28938 | 6 | 170500 | 170500 | 171116 | 29021:1132 |
| Blackbird | 0x0008 | 35 | both | 81 | 29123 | 3 | 55440 | 55440 | 56056 | 29150:760 |
| Blackbird | 0x0008 | 35 | both | 87 | 30394 | 4 | 133988 | 133988 | 134604 | 30459:1484 |
| Blackbird | 0x0008 | 35 | both | 100 | 33998 | 5 | 181288 | 181288 | 181820 | 34086:1596 |
| Blackbird | 0x0008 | 35 | both | 110 | 35723 | 6 | 80828 | 80828 | 81444 | 35762:1572 |
| Blackbird | 0x0008 | 35 | both | 358 | 85783 | 6 | 121896 | 121896 | 122512 | 85842:1680 |
| Blackbird | 0x000C | 35 | both | 61 | 24699 | 5 | 62360 | 62360 | 62976 | 24729:1536 |
| Blackbird | 0x000C | 35 | both | 67 | 26119 | 3 | 80016 | 80016 | 80632 | 26158:760 |
| Blackbird | 0x000C | 35 | both | 80 | 28938 | 6 | 170500 | 170500 | 171116 | 29021:1132 |
| Blackbird | 0x000C | 35 | both | 81 | 29123 | 3 | 55440 | 55440 | 56056 | 29150:760 |
| Blackbird | 0x000C | 35 | both | 87 | 30394 | 4 | 133988 | 133988 | 134604 | 30459:1484 |
| Blackbird | 0x000C | 35 | both | 100 | 33998 | 5 | 181288 | 181288 | 181820 | 34086:1596 |
| Blackbird | 0x000C | 35 | both | 107 | 35066 | 6 | 138344 | 138344 | 138960 | 35133:1744 |
| Blackbird | 0x000C | 35 | both | 110 | 35723 | 6 | 80828 | 80828 | 81444 | 35762:1572 |
| Blackbird | 0x000C | 35 | both | 116 | 36934 | 8 | 207464 | 207464 | 208080 | 37035:1232 |
| Blackbird | 0x000C | 35 | both | 121 | 38061 | 8 | 196996 | 196996 | 197612 | 38157:1004 |
| Blackbird | 0x000C | 35 | both | 358 | 85783 | 6 | 121896 | 121896 | 122512 | 85842:1680 |
| Monkey | 0x000A | 57 | both | 63 | 25172 | 3 | 75984 | 75984 | 76488 | 25209:712 |
| Monkey | 0x000A | 57 | both | 83 | 29586 | 3 | 78708 | 78708 | 79212 | 29624:1388 |
| Monkey | 0x000A | 57 | both | 358 | 85783 | 4 | 111784 | 111784 | 112288 | 85837:1696 |
| Plant | 0x000B | 60 | both | 65 | 25672 | 3 | 73636 | 73636 | 74196 | 25708:468 |
| Plant | 0x000B | 60 | both | 85 | 29946 | 3 | 73876 | 73876 | 74436 | 29982:708 |
| Plant | 0x000B | 60 | both | 87 | 30394 | 3 | 123136 | 123136 | 123696 | 30454:816 |
| ? | 0x0000 | 10 | both | 75 | 27630 | 4 | 154396 | 154396 | 154540 | 27705:940 |
| ? | 0x0000 | 10 | both | 80 | 28938 | 4 | 159096 | 159096 | 159240 | 29015:1544 |
| ? | 0x0000 | 10 | both | 82 | 29291 | 4 | 166884 | 166884 | 167028 | 29372:1140 |
| ? | 0x0000 | 10 | both | 419 | 97046 | 4 | 200056 | 200056 | 200184 | 97143:1528 |
| ? | 0x0000 | 10 | both | 420 | 97283 | 4 | 200048 | 200048 | 200176 | 97380:1520 |
| Bear | 0x000C | 75 | both | 75 | 27630 | 5 | 155436 | 155436 | 155996 | 27706:348 |
| Bear | 0x000C | 75 | both | 80 | 28938 | 5 | 160136 | 160136 | 160696 | 29016:952 |
| Bear | 0x000C | 75 | both | 82 | 29291 | 5 | 167924 | 167924 | 168484 | 29373:548 |
| Worm | 0x020D | 120 | both | 86 | 30202 | 3 | 95976 | 95976 | 96536 | 30249:280 |
| Eve (carriage) | 0x020E | 330 | both | 89 | 30958 | 1 | 327340 | 327976 | 329320 | 31118:1640 |
| Yellow Rat | 0x0010 | 70 | both | 100 | 33998 | 6 | 197972 | 197972 | 198360 | 34094:1752 |
| Yellow Rat | 0x0010 | 70 | both | 110 | 35723 | 5 | 72272 | 72272 | 72744 | 35758:1064 |
| Yellow Rat | 0x0010 | 70 | both | 113 | 36213 | 6 | 106496 | 106496 | 106968 | 36265:472 |
| Yellow Rat | 0x0010 | 70 | both | 121 | 38061 | 9 | 213764 | 213764 | 214236 | 38165:1244 |
| Spider | 0x000F | 78 | both | 104 | 34667 | 4 | 46864 | 46864 | 47424 | 34690:320 |
| Spider | 0x000F | 78 | both | 113 | 36213 | 7 | 115052 | 115052 | 115612 | 36269:924 |
| Spider | 0x000F | 78 | both | 115 | 36684 | 5 | 155392 | 155392 | 155952 | 36760:304 |
| Spider | 0x000F | 78 | both | 116 | 36934 | 7 | 196452 | 196452 | 197012 | 37030:404 |
| Spider | 0x000F | 78 | both | 122 | 38296 | 3 | 111136 | 111136 | 111696 | 38350:1104 |
| Spider (no reward) | 0x000F | 72 | both | 104 | 34667 | 5 | 57876 | 57876 | 58072 | 34695:728 |
| Spider (no reward) | 0x000F | 72 | both | 113 | 36213 | 8 | 126064 | 126064 | 126260 | 36274:1332 |
| Spider (no reward) | 0x000F | 72 | both | 115 | 36684 | 6 | 166404 | 166404 | 166600 | 36765:712 |
| Spider (no reward) | 0x000F | 72 | both | 116 | 36934 | 9 | 224232 | 224232 | 224428 | 37043:1196 |
| Spider (no reward) | 0x000F | 72 | both | 120 | 37743 | 5 | 92772 | 92772 | 92968 | 37788:808 |
| Spider (no reward) | 0x000F | 72 | both | 122 | 38296 | 4 | 122148 | 122148 | 122344 | 38355:1512 |
| Blackbird | 0x000C | 35 | both | 107 | 35066 | 6 | 138344 | 138344 | 138960 | 35133:1744 |
| Dogman | 0x0011 | 98 | both | 107 | 35066 | 5 | 129076 | 129076 | 129700 | 35129:676 |
| Dogman | 0x0011 | 98 | both | 111 | 35887 | 6 | 147456 | 147456 | 148080 | 35959:624 |
| Dogman | 0x0011 | 98 | both | 122 | 38296 | 5 | 125736 | 125736 | 126360 | 38357:1432 |
| Dogman | 0x0011 | 98 | both | 114 | 36443 | 6 | 94544 | 94544 | 95212 | 36489:1004 |
| Giant Dogman | 0x0012 | 150 | both | 118 | 37541 | 6 | 126780 | 126780 | 127204 | 37603:228 |
| Blackbird | 0x0008 | 35 | both | 120 | 37743 | 6 | 96360 | 96360 | 96976 | 37790:720 |
| Blackbird | 0x000C | 35 | both | 120 | 37743 | 6 | 96360 | 96360 | 96976 | 37790:720 |
| Spider | 0x000F | 78 | both | 120 | 37743 | 4 | 81760 | 81760 | 82320 | 37783:400 |
| Blackbird | 0x000C | 35 | both | 121 | 38061 | 8 | 196996 | 196996 | 197612 | 38157:1004 |
| ? | 0x0000 | 10 | both | 123 | 38622 | 5 | 249816 | 249816 | 249912 | 38744:56 |
| Sheeva (left head) | 0x0100 | 300 | both | 123 | 38622 | 2 | 247812 | 247812 | 247988 | 38743:180 |
| Sheeva (right head) | 0x0100 | 200 | both | 123 | 38622 | 3 | 248480 | 248480 | 248656 | 38743:848 |
| Sheeva (center head) | 0x0100 | 400 | both | 123 | 38622 | 4 | 249148 | 249148 | 249324 | 38743:1516 |
| Sheeva (body) | 0x0312 | 10 | both | 123 | 38622 | 1 | 228736 | 228868 | 230444 | 38734:1068 |
| Slime | 0x0012 | 88 | both | 126 | 39315 | 7 | 92480 | 92480 | 93040 | 39360:880 |
| Slime | 0x0012 | 88 | both | 129 | 39879 | 3 | 85396 | 85396 | 85956 | 39920:1988 |
| Slime | 0x0012 | 88 | both | 137 | 41106 | 4 | 146352 | 146352 | 146912 | 41177:1504 |
| Slime | 0x0012 | 88 | both | 139 | 41562 | 6 | 91476 | 91476 | 92036 | 41606:1924 |
| Slime | 0x0012 | 88 | both | 140 | 41840 | 5 | 149684 | 149684 | 150244 | 41913:740 |
| Slime | 0x0012 | 88 | both | 141 | 42154 | 7 | 206380 | 206380 | 206940 | 42255:92 |
| Slime | 0x0012 | 88 | both | 147 | 43692 | 6 | 223980 | 223980 | 224540 | 43801:1308 |
| Slime | 0x0012 | 88 | both | 152 | 44690 | 6 | 209556 | 209556 | 210116 | 44792:1220 |
| Slime | 0x0012 | 88 | both | 324 | 79523 | 4 | 144636 | 144636 | 145196 | 79593:1836 |
| Slime | 0x0012 | 88 | both | 326 | 79962 | 6 | 91212 | 91212 | 91772 | 80006:1660 |
| Slime | 0x0012 | 88 | both | 327 | 80239 | 5 | 149624 | 149624 | 150184 | 80312:680 |
| Slime | 0x0012 | 88 | both | 328 | 80552 | 7 | 206856 | 206856 | 207416 | 80653:568 |
| Fly | 0x0013 | 110 | both | 137 | 41106 | 5 | 154080 | 154080 | 154640 | 41181:1040 |
| Fly | 0x0013 | 110 | both | 140 | 41840 | 6 | 157412 | 157412 | 157972 | 41917:276 |
| Fly | 0x0013 | 110 | both | 146 | 43321 | 6 | 256908 | 256908 | 257468 | 43446:1468 |
| Fly | 0x0013 | 110 | both | 147 | 43692 | 5 | 213904 | 213904 | 214464 | 43796:1472 |
| Fly | 0x0013 | 110 | both | 324 | 79523 | 5 | 152364 | 152364 | 152924 | 79597:1372 |
| Fly | 0x0013 | 110 | both | 327 | 80239 | 6 | 157352 | 157352 | 157912 | 80316:216 |
| Ratman | 0x0014 | 120 | both | 141 | 42154 | 6 | 196332 | 196332 | 196892 | 42250:284 |
| Ratman | 0x0014 | 120 | both | 146 | 43321 | 7 | 266984 | 266984 | 267544 | 43451:1304 |
| Ratman | 0x0014 | 120 | both | 153 | 45045 | 6 | 225764 | 225764 | 226324 | 45155:1044 |
| Ratman | 0x0014 | 120 | both | 154 | 45393 | 9 | 268180 | 268180 | 268740 | 45524:452 |
| Ratman | 0x0014 | 120 | both | 328 | 80552 | 6 | 196808 | 196808 | 197368 | 80648:760 |
| Spawn | 0x0015 | 170 | both | 145 | 42972 | 6 | 142920 | 142920 | 143480 | 43042:120 |
| Spawn | 0x0015 | 170 | both | 152 | 44690 | 4 | 197416 | 197416 | 197976 | 44786:1368 |
| Spawn | 0x0015 | 170 | both | 153 | 45045 | 4 | 213624 | 213624 | 214184 | 45149:1192 |
| Spawn | 0x0015 | 170 | both | 154 | 45393 | 7 | 256040 | 256040 | 256600 | 45518:600 |
| Spawn | 0x0015 | 170 | both | 332 | 81336 | 6 | 142256 | 142256 | 142732 | 81405:1420 |
| Spawn (offspring) | 0x0015 | 0 | both | 145 | 42972 | 7 | 152736 | 152736 | 154392 | 43047:792 |
| Spawn (offspring) | 0x0015 | 0 | both | 152 | 44690 | 5 | 207232 | 207232 | 208888 | 44791:2040 |
| Spawn (offspring) | 0x0015 | 0 | both | 153 | 45045 | 5 | 223440 | 223440 | 225096 | 45154:1864 |
| Spawn (offspring) | 0x0015 | 0 | both | 154 | 45393 | 8 | 265856 | 265856 | 267512 | 45523:1272 |
| Spawn (offspring) | 0x0015 | 0 | both | 332 | 81336 | 7 | 151988 | 151988 | 153644 | 81411:44 |
| Spawn (offspring) | 0x0015 | 45 | both | 145 | 42972 | 7 | 152736 | 152736 | 152996 | 43046:1444 |
| Spawn (offspring) | 0x0015 | 45 | both | 152 | 44690 | 5 | 207232 | 207232 | 207492 | 44791:644 |
| Spawn (offspring) | 0x0015 | 45 | both | 153 | 45045 | 5 | 223440 | 223440 | 223700 | 45154:468 |
| Spawn (offspring) | 0x0015 | 45 | both | 154 | 45393 | 8 | 265856 | 265856 | 266116 | 45522:1924 |
| Spawn (offspring) | 0x0015 | 45 | both | 332 | 81336 | 7 | 151988 | 151988 | 152248 | 81410:696 |
| Giant Slime | 0x0014 | 201 | both | 149 | 44119 | 4 | 87788 | 87788 | 88368 | 44162:304 |
| Giant Slime | 0x0014 | 201 | both | 149 | 44119 | 4 | 87788 | 87788 | 88368 | 44162:304 |
| ? | 0x0200 | 3392 | both | 156 | 45891 | 4 | 230240 | 230240 | 230900 | 46003:1524 |
| ? | 0x0200 | 3392 | both | 156 | 45891 | 5 | 231664 | 231664 | 232324 | 46004:900 |
| ? | 0x0200 | 3392 | both | 156 | 45891 | 6 | 233088 | 233088 | 233748 | 46005:276 |
| ? | 0x0200 | 3392 | both | 291 | 74486 | 5 | 215204 | 215204 | 215864 | 74591:824 |
| ? | 0x0200 | 3392 | both | 291 | 74486 | 6 | 216628 | 216628 | 217288 | 74592:200 |
| ? | 0x0200 | 3392 | both | 380 | 89069 | 4 | 230680 | 230680 | 231340 | 89181:1964 |
| ? | 0x0200 | 3392 | both | 380 | 89069 | 5 | 232104 | 232104 | 232764 | 89182:1340 |
| ? | 0x0200 | 3392 | both | 380 | 89069 | 6 | 233528 | 233528 | 234188 | 89183:716 |
| Giant Spider (phase 1) | 0x0216 | 450 | both | 156 | 45891 | 3 | 208280 | 208280 | 209656 | 45993:760 |
| Hospital map 159 actor | 0x0016 | 152 | both | 159 | 46542 | 1 | 80204 | 80336 | 80864 | 46581:992 |
| ? | 0x0016 | 152 | both | 159 | 46542 | 2 | 91176 | 91176 | 91460 | 46586:1348 |
| Snake | 0x0016 | 99 | both | 162 | 47149 | 6 | 175024 | 175024 | 175724 | 47234:1644 |
| Snake | 0x0016 | 99 | both | 163 | 47419 | 8 | 174276 | 174276 | 174976 | 47504:896 |
| Snake | 0x0016 | 99 | both | 167 | 48209 | 8 | 106488 | 106488 | 107188 | 48261:692 |
| Cat | 0x0017 | 135 | both | 162 | 47149 | 5 | 161520 | 161520 | 162364 | 47228:572 |
| Cat | 0x0017 | 135 | both | 163 | 47419 | 7 | 160596 | 160596 | 161440 | 47497:1696 |
| Bat | 0x0017 | 112 | both | 167 | 48209 | 7 | 92904 | 92904 | 93692 | 48254:1532 |
| Bat | 0x0017 | 112 | both | 168 | 48483 | 8 | 111216 | 111216 | 112004 | 48537:1412 |
| Bat | 0x0017 | 112 | both | 169 | 48794 | 8 | 120864 | 120864 | 121652 | 48853:820 |
| Bat | 0x0017 | 112 | both | 173 | 49458 | 7 | 95020 | 95020 | 95808 | 49504:1600 |
| Bat | 0x0017 | 112 | both | 178 | 50183 | 3 | 66056 | 66056 | 66844 | 50215:1308 |
| Bat | 0x0017 | 112 | both | 186 | 51257 | 5 | 126816 | 126816 | 127604 | 51319:628 |
| Frog (sewer) | 0x0018 | 153 | both | 168 | 48483 | 9 | 124784 | 124784 | 125428 | 48544:500 |
| Frog (sewer) | 0x0018 | 153 | both | 169 | 48794 | 7 | 107744 | 107744 | 108388 | 48846:1892 |
| Alligator | 0x0019 | 215 | both | 174 | 49723 | 6 | 202936 | 202936 | 203668 | 49822:916 |
| Mole | 0x0019 | 161 | both | 186 | 51257 | 4 | 114724 | 114724 | 115512 | 51313:824 |
| Mole | 0x0019 | 161 | both | 187 | 51462 | 4 | 56828 | 56828 | 57616 | 51490:272 |
| Centipede (head, phase 1) | 0x041A | 500 | both | 188 | 51727 | 5 | 246896 | 246896 | 248948 | 51848:1140 |
| Centipede (middle) | 0x041A | 120 | both | 188 | 51727 | 6 | 276072 | 276072 | 276772 | 51862:292 |
| Centipede (middle) | 0x041A | 120 | both | 188 | 51727 | 7 | 294216 | 294216 | 294916 | 51871:4 |
| Centipede (tail) | 0x041A | 180 | both | 188 | 51727 | 8 | 312492 | 312492 | 313048 | 51879:1752 |
| Lizard | 0x001D | 200 | both | 197 | 53843 | 6 | 146160 | 146160 | 147004 | 53914:1596 |
| Lizard | 0x001D | 200 | both | 198 | 54157 | 5 | 143456 | 143456 | 144300 | 54227:940 |
| Lizard | 0x001D | 200 | both | 199 | 54486 | 7 | 181132 | 181132 | 181976 | 54574:1752 |
| Lizard | 0x001D | 200 | both | 201 | 54878 | 3 | 54200 | 54200 | 55044 | 54904:1796 |
| Lizard | 0x001D | 200 | both | 206 | 55956 | 4 | 141208 | 141208 | 142052 | 56025:740 |
| Lizard | 0x001D | 200 | both | 207 | 56237 | 5 | 138908 | 138908 | 139752 | 56305:488 |
| Lizard | 0x001D | 200 | both | 217 | 57888 | 5 | 144836 | 144836 | 145680 | 57959:272 |
| Lizard | 0x001D | 200 | both | 218 | 58158 | 4 | 119564 | 119564 | 120408 | 58216:1624 |
| Lizard | 0x001D | 200 | both | 220 | 58712 | 3 | 126972 | 126972 | 127816 | 58774:840 |
| Lizard | 0x001D | 200 | both | 223 | 59433 | 4 | 204676 | 204676 | 205520 | 59533:720 |
| Lizard | 0x001D | 200 | both | 226 | 60266 | 4 | 144720 | 144720 | 145564 | 60337:156 |
| Lizard | 0x001D | 200 | both | 227 | 60530 | 5 | 88884 | 88884 | 89728 | 60573:1664 |
| Lizard | 0x001D | 200 | both | 229 | 60927 | 5 | 231292 | 231292 | 232136 | 61040:712 |
| Lizard | 0x001D | 200 | both | 232 | 61816 | 5 | 53632 | 53632 | 54476 | 61842:1228 |
| Armadillo | 0x001D | 240 | both | 197 | 53843 | 7 | 158780 | 158780 | 159568 | 53920:1872 |
| Armadillo | 0x001D | 240 | both | 198 | 54157 | 6 | 156124 | 156124 | 156912 | 54233:1264 |
| Armadillo | 0x001D | 240 | both | 199 | 54486 | 8 | 193752 | 193752 | 194540 | 54580:2028 |
| Armadillo | 0x001D | 240 | both | 203 | 55320 | 5 | 210140 | 210140 | 210928 | 55422:2032 |
| Armadillo | 0x001D | 240 | both | 206 | 55956 | 5 | 153844 | 153844 | 154632 | 56031:1032 |
| Armadillo | 0x001D | 240 | both | 207 | 56237 | 6 | 151496 | 151496 | 152284 | 56311:732 |
| Armadillo | 0x001D | 240 | both | 214 | 57328 | 6 | 121348 | 121348 | 122136 | 57387:1304 |
| Armadillo | 0x001D | 240 | both | 217 | 57888 | 6 | 157488 | 157488 | 158276 | 57965:580 |
| Armadillo | 0x001D | 240 | both | 219 | 58392 | 4 | 111644 | 111644 | 112432 | 58446:1840 |
| Armadillo | 0x001D | 240 | both | 220 | 58712 | 4 | 139672 | 139672 | 140460 | 58780:1196 |
| Armadillo | 0x001D | 240 | both | 224 | 59764 | 5 | 216956 | 216956 | 217744 | 59870:656 |
| Armadillo | 0x001D | 240 | both | 226 | 60266 | 5 | 157340 | 157340 | 158128 | 60343:432 |
| Armadillo | 0x001D | 240 | both | 227 | 60530 | 6 | 101520 | 101520 | 102308 | 60579:1956 |
| Armadillo | 0x001D | 240 | both | 233 | 61956 | 3 | 140800 | 140800 | 141588 | 62025:276 |
| Armadillo | 0x001D | 240 | both | 242 | 64204 | 6 | 233244 | 233244 | 234032 | 64318:560 |
| Armadillo | 0x001D | 240 | both | 246 | 65261 | 6 | 211500 | 211500 | 212288 | 65364:1344 |
| Dinosaur | 0x001E | 280 | both | 197 | 53843 | 5 | 131952 | 131952 | 132740 | 53907:1668 |
| Dinosaur | 0x001E | 280 | both | 198 | 54157 | 4 | 129200 | 129200 | 129988 | 54220:964 |
| Dinosaur | 0x001E | 280 | both | 199 | 54486 | 6 | 166924 | 166924 | 167712 | 54567:1824 |
| Dinosaur | 0x001E | 280 | both | 203 | 55320 | 4 | 195820 | 195820 | 196608 | 55416:0 |
| Dinosaur | 0x001E | 280 | both | 206 | 55956 | 3 | 126984 | 126984 | 127772 | 56018:796 |
| Dinosaur | 0x001E | 280 | both | 207 | 56237 | 4 | 124732 | 124732 | 125520 | 56298:592 |
| Dinosaur | 0x001E | 280 | both | 214 | 57328 | 5 | 107140 | 107140 | 107928 | 57380:1432 |
| Dinosaur | 0x001E | 280 | both | 217 | 57888 | 4 | 130596 | 130596 | 131384 | 57952:312 |
| Dinosaur | 0x001E | 280 | both | 218 | 58158 | 3 | 105372 | 105372 | 106160 | 58209:1712 |
| Dinosaur | 0x001E | 280 | both | 219 | 58392 | 3 | 97436 | 97436 | 98224 | 58439:1968 |
| Dinosaur | 0x001E | 280 | both | 220 | 58712 | 5 | 154712 | 154712 | 155500 | 58787:1900 |
| Dinosaur | 0x001E | 280 | both | 223 | 59433 | 3 | 190468 | 190468 | 191256 | 59526:792 |
| Dinosaur | 0x001E | 280 | both | 224 | 59764 | 3 | 187492 | 187492 | 188280 | 59855:1912 |
| Dinosaur | 0x001E | 280 | both | 226 | 60266 | 3 | 130512 | 130512 | 131300 | 60330:228 |
| Dinosaur | 0x001E | 280 | both | 229 | 60927 | 3 | 201732 | 201732 | 202520 | 61025:1816 |
| Dinosaur | 0x001E | 280 | both | 231 | 61482 | 3 | 255152 | 255152 | 255940 | 61606:1988 |
| Dinosaur | 0x001E | 280 | both | 234 | 62253 | 4 | 257912 | 257912 | 258700 | 62379:652 |
| Dinosaur | 0x001E | 280 | both | 242 | 64204 | 4 | 203748 | 203748 | 204536 | 64303:1784 |
| Dinosaur | 0x001E | 280 | both | 246 | 65261 | 5 | 197356 | 197356 | 198144 | 65357:1536 |
| Dinosaur | 0x001E | 280 | both | 199 | 54486 | 6 | 166924 | 166924 | 167712 | 54567:1824 |
| Pterodactyl | 0x001F | 320 | both | 203 | 55320 | 6 | 225212 | 225212 | 226000 | 55430:720 |
| Pterodactyl | 0x001F | 320 | both | 223 | 59433 | 5 | 217296 | 217296 | 218084 | 59539:996 |
| Pterodactyl | 0x001F | 320 | both | 224 | 59764 | 4 | 201716 | 201716 | 202504 | 59862:1800 |
| Pterodactyl | 0x001F | 320 | both | 229 | 60927 | 4 | 216004 | 216004 | 216792 | 61032:1752 |
| Pterodactyl | 0x001F | 320 | both | 231 | 61482 | 5 | 284496 | 284496 | 285284 | 61621:612 |
| Pterodactyl | 0x001F | 320 | both | 233 | 61956 | 4 | 155728 | 155728 | 156516 | 62032:868 |
| Pterodactyl | 0x001F | 320 | both | 234 | 62253 | 6 | 287224 | 287224 | 288012 | 62393:1292 |
| Pterodactyl | 0x001F | 320 | both | 242 | 64204 | 5 | 217988 | 217988 | 218776 | 64310:1688 |
| Pterodactyl | 0x001F | 320 | both | 246 | 65261 | 7 | 226396 | 226396 | 227184 | 65371:1904 |
| Scorpion (tougher) | 0x0020 | 430 | both | 205 | 55688 | 4 | 111820 | 111820 | 112884 | 55743:244 |
| Armadillo (forced fight) | 0x001D | 240 | both | 210 | 56759 | 5 | 62184 | 62184 | 62972 | 56789:1532 |
| Pterodactyl | 0x001F | 320 | both | 221 | 59008 | 5 | 117836 | 117836 | 118760 | 59065:2024 |
| Scorpion | 0x0020 | 390 | both | 231 | 61482 | 4 | 269424 | 269424 | 270304 | 61613:2016 |
| Scorpion | 0x0020 | 390 | both | 234 | 62253 | 5 | 272168 | 272168 | 273048 | 62386:664 |
| Scorpion | 0x0020 | 390 | both | 243 | 64528 | 3 | 113408 | 113408 | 114288 | 64583:1648 |
| Triceratops (phase 1) | 0x0221 | 750 | both | 245 | 64914 | 6 | 193100 | 193100 | 194036 | 65008:1524 |
| Triceratops (phase 2) | 0x0421 | 900 | both | 245 | 64914 | 7 | 208144 | 208144 | 209724 | 65016:828 |
| Triceratops part | 0x0421 | 400 | both | 245 | 64914 | 8 | 220748 | 220748 | 221708 | 65022:524 |
| Tyrannosaur | 0x0223 | 2400 | both | 256 | 67633 | 2 | 268416 | 268416 | 268972 | 67764:684 |
| Grey Rat | 0x001A | 215 | both | 263 | 68850 | 7 | 175616 | 175616 | 176172 | 68936:44 |
| Grey Rat | 0x001A | 215 | both | 265 | 69112 | 4 | 107684 | 107684 | 108240 | 69164:1744 |
| Grey Rat | 0x001A | 215 | both | 333 | 81615 | 5 | 110120 | 110120 | 110676 | 81669:84 |
| Gold Spider | 0x001A | 242 | both | 263 | 68850 | 8 | 190860 | 190860 | 191416 | 68943:952 |
| Gold Spider | 0x001A | 242 | both | 265 | 69112 | 3 | 92944 | 92944 | 93500 | 69157:1340 |
| Gold Spider | 0x001A | 242 | both | 333 | 81615 | 4 | 95396 | 95396 | 95952 | 81661:1744 |
| ? | 0x001A | 10 | both | 263 | 68850 | 9 | 205680 | 205680 | 206104 | 68950:1304 |
| ? | 0x001A | 10 | both | 265 | 69112 | 5 | 122848 | 122848 | 123272 | 69172:392 |
| ? | 0x001A | 10 | both | 333 | 81615 | 6 | 125268 | 125268 | 125692 | 81676:764 |
| Crab (claw) | 0x021B | 420 | both | 269 | 69927 | 4 | 192268 | 192268 | 192896 | 70021:384 |
| Crab (claw) | 0x021B | 420 | both | 269 | 69927 | 5 | 199228 | 199228 | 199856 | 70024:1200 |
| Crab (claw) | 0x021B | 420 | both | 269 | 69927 | 8 | 217372 | 217372 | 217984 | 70033:896 |
| Crab (claw) | 0x021B | 420 | both | 269 | 69927 | 9 | 221056 | 221056 | 221668 | 70035:484 |
| Crab (body) | 0x0220 | 856 | both | 269 | 69927 | 3 | 175696 | 175696 | 177564 | 70013:1436 |
| Crab (claw) | 0x041B | 420 | both | 269 | 69927 | 6 | 206188 | 206188 | 206712 | 70027:1912 |
| Crab (claw) | 0x041B | 420 | both | 269 | 69927 | 7 | 211780 | 211780 | 212304 | 70030:1360 |
| Eve (Statue of Liberty) part | 0x0125 | 1600 | both | 273 | 71025 | 5 | 299380 | 299380 | 300164 | 71171:1156 |
| Eve (Statue of Liberty) part | 0x0125 | 1750 | both | 273 | 71025 | 6 | 300440 | 300440 | 301224 | 71172:168 |
| Eve (Statue of Liberty) part | 0x0125 | 1900 | both | 273 | 71025 | 7 | 301500 | 301500 | 302284 | 71172:1228 |
| Eve (Statue of Liberty, reward holder) | 0x0325 | 10 | both | 273 | 71025 | 2 | 279068 | 282120 | 283120 | 71163:496 |
| Alligator (body) | 0x0307 | 0 | both | 348 | 84102 | 2 | 168220 | 168220 | 170144 | 84185:160 |
| Ultimate Being (1st) | 0x0225 | 1500 | both | 350 | 84552 | 2 | 230116 | 230480 | 232052 | 84665:628 |
| Ultimate Being form | 0x0225 | 950 | both | 350 | 84552 | 3 | 246960 | 247352 | 248588 | 84673:780 |
| Giant Spider (phase 2) | 0x0217 | 400 | both | 380 | 89069 | 3 | 207912 | 207912 | 209480 | 89171:584 |
| Ultimate Being (1st) | 0x0225 | 1500 | both | 428 | 99302 | 2 | 162704 | 163300 | 164592 | 99382:752 |
| Ultimate Being form | 0x0026 | 1300 | both | 429 | 99602 | 3 | 314136 | 314136 | 314524 | 99755:1180 |
| Ultimate Being (3rd) | 0x0226 | 3500 | both | 429 | 99602 | 2 | 289068 | 289068 | 289608 | 99743:840 |
| Ultimate Being (3rd) | 0x0426 | 3500 | both | 429 | 99602 | 2 | 289068 | 289068 | 291364 | 99744:548 |
| Ultimate Being (4th) | 0x0226 | 7992 | both | 430 | 99900 | 2 | 231088 | 231940 | 233028 | 100013:1604 |
| Eve (final form) | 0x0223 | 2200 | both | 432 | 100283 | 2 | 298096 | 299320 | 301080 | 100430:24 |
| ? | 0x0200 | 200000 | both | 291 | 74486 | 4 | 213924 | 213924 | 214440 | 74590:1448 |
| Giant Spider (Chrysler) | 0x0218 | 1000 | both | 291 | 74486 | 3 | 194868 | 194868 | 196188 | 74581:1628 |
| Dinosaur | 0x000F | 106 | both | 295 | 75097 | 5 | 298716 | 298716 | 299456 | 75243:448 |
| Dinosaur | 0x000F | 106 | both | 434 | 100743 | 5 | 344184 | 344184 | 344924 | 100911:860 |
| Bat | 0x0011 | 98 | both | 295 | 75097 | 4 | 285212 | 285212 | 285952 | 75236:1280 |
| Monster Box | 0x002D | 700 | both | 295 | 75097 | 3 | 274036 | 274036 | 275032 | 75231:600 |
| Monster Box | 0x002D | 700 | both | 434 | 100743 | 3 | 319640 | 319640 | 320636 | 100899:1148 |
| Monster Box | 0x002D | 700 | both | 435 | 101021 | 3 | 293384 | 293384 | 294380 | 101164:1516 |
| Monster Box | 0x002D | 700 | both | 436 | 101277 | 3 | 229728 | 229728 | 230724 | 101389:1348 |
| Monster Box | 0x002D | 700 | both | 437 | 101502 | 3 | 255108 | 255108 | 256104 | 101627:104 |
| Bird | 0x000A | 74 | both | 298 | 75599 | 3 | 69256 | 69256 | 69768 | 75633:136 |
| Bird | 0x000A | 74 | both | 308 | 76573 | 3 | 70984 | 70984 | 71496 | 76607:1864 |
| Bird | 0x000A | 74 | both | 311 | 77034 | 3 | 70824 | 70824 | 71336 | 77068:1704 |
| Rat | 0x000B | 85 | both | 298 | 75599 | 4 | 85208 | 85208 | 85720 | 75640:1752 |
| Rat | 0x000B | 85 | both | 308 | 76573 | 4 | 86936 | 86936 | 87448 | 76615:1432 |
| Rat | 0x000B | 85 | both | 311 | 77034 | 4 | 86776 | 86776 | 87288 | 77076:1272 |
| Dinosaur | 0x000F | 106 | both | 299 | 75757 | 3 | 110896 | 110896 | 111636 | 75811:1044 |
| Dinosaur | 0x000F | 106 | both | 309 | 76714 | 3 | 110904 | 110904 | 111644 | 76768:1052 |
| Dinosaur | 0x000F | 106 | both | 310 | 76878 | 4 | 124312 | 124312 | 125052 | 76939:124 |
| Bat | 0x0011 | 98 | both | 299 | 75757 | 4 | 124672 | 124672 | 125412 | 75818:484 |
| Bat | 0x0011 | 98 | both | 309 | 76714 | 4 | 124696 | 124696 | 125436 | 76775:508 |
| Bat | 0x0011 | 98 | both | 310 | 76878 | 3 | 110904 | 110904 | 111644 | 76932:1052 |
| Bat | 0x0011 | 98 | both | 385 | 90149 | 4 | 123804 | 123804 | 124544 | 90209:1664 |
| Bat | 0x0011 | 98 | both | 388 | 90576 | 3 | 111912 | 111912 | 112652 | 90631:12 |
| Bat | 0x0011 | 98 | both | 389 | 90740 | 3 | 111752 | 111752 | 112492 | 90794:1900 |
| Eve (Chrysler) | 0x0263 | 40000 | both | 318 | 78191 | 3 | 299744 | 299744 | 300424 | 78337:1416 |
| Eve (Chrysler) part | 0x0263 | 8800 | both | 318 | 78191 | 4 | 326848 | 326848 | 327648 | 78350:2016 |
| Alligator (Chrysler) | 0x021D | 1200 | both | 383 | 89750 | 3 | 159748 | 159748 | 160256 | 89828:512 |
| Snake | 0x0014 | 120 | both | 384 | 89981 | 3 | 92104 | 92104 | 92616 | 90026:456 |
| Snake | 0x0014 | 120 | both | 386 | 90298 | 3 | 40728 | 40728 | 41240 | 90318:280 |
| Snake | 0x0014 | 120 | both | 387 | 90426 | 3 | 93832 | 93832 | 94344 | 90472:136 |
| Snake | 0x0014 | 120 | both | 391 | 91282 | 3 | 129776 | 129776 | 130288 | 91345:1264 |
| Snake | 0x0014 | 120 | both | 392 | 91485 | 3 | 145020 | 145020 | 145532 | 91556:124 |
| Snake | 0x0014 | 120 | both | 393 | 91686 | 3 | 159208 | 159208 | 159720 | 91763:2024 |
| Snake | 0x0014 | 120 | both | 394 | 91883 | 3 | 131504 | 131504 | 132016 | 91947:944 |
| Snake | 0x0014 | 120 | both | 395 | 92069 | 3 | 131504 | 131504 | 132016 | 92133:944 |
| Snake | 0x0014 | 120 | both | 396 | 92263 | 3 | 159048 | 159048 | 159560 | 92340:1864 |
| Monkey | 0x0015 | 158 | both | 384 | 89981 | 4 | 102720 | 102720 | 103176 | 90031:776 |
| Monkey | 0x0015 | 158 | both | 387 | 90426 | 4 | 104448 | 104448 | 104904 | 90477:456 |
| Mole | 0x0013 | 144 | both | 385 | 90149 | 3 | 111904 | 111904 | 112644 | 90204:4 |
| Mole | 0x0013 | 144 | both | 388 | 90576 | 4 | 125320 | 125320 | 126060 | 90637:1132 |
| Mole | 0x0013 | 144 | both | 389 | 90740 | 4 | 125224 | 125224 | 125964 | 90801:1036 |
| Centipede (Chrysler, head) | 0x0422 | 1200 | both | 390 | 90977 | 3 | 245356 | 245356 | 247144 | 91097:1384 |
| Centipede (Chrysler, middle) | 0x0422 | 600 | both | 390 | 90977 | 4 | 274172 | 274172 | 274644 | 91111:212 |
| Centipede (Chrysler, middle) | 0x0422 | 600 | both | 390 | 90977 | 5 | 291848 | 291848 | 292320 | 91119:1504 |
| Centipede (Chrysler, tail) | 0x0422 | 800 | both | 390 | 90977 | 6 | 309656 | 309656 | 310128 | 91128:880 |
| Plant | 0x0015 | 280 | both | 391 | 91282 | 6 | 154776 | 154776 | 155288 | 91357:1688 |
| Plant | 0x0015 | 280 | both | 393 | 91686 | 4 | 169824 | 169824 | 170336 | 91769:352 |
| Plant | 0x0015 | 280 | both | 394 | 91883 | 6 | 156504 | 156504 | 157016 | 91959:1368 |
| Plant | 0x0015 | 280 | both | 395 | 92069 | 6 | 156504 | 156504 | 157016 | 92145:1368 |
| Plant | 0x0015 | 280 | both | 396 | 92263 | 4 | 169664 | 169664 | 170176 | 92346:192 |
| Plant | 0x0015 | 280 | both | 399 | 92984 | 3 | 160872 | 160872 | 161384 | 93062:1640 |
| Plant | 0x0015 | 280 | both | 401 | 93380 | 3 | 229476 | 229476 | 229988 | 93492:612 |
| Plant | 0x0015 | 280 | both | 402 | 93620 | 3 | 162608 | 162608 | 163120 | 93699:1328 |
| Spider | 0x0017 | 205 | both | 391 | 91282 | 4 | 140392 | 140392 | 140848 | 91350:1584 |
| Spider | 0x0017 | 205 | both | 392 | 91485 | 4 | 155636 | 155636 | 156092 | 91561:444 |
| Spider | 0x0017 | 205 | both | 394 | 91883 | 4 | 142120 | 142120 | 142576 | 91952:1264 |
| Spider | 0x0017 | 205 | both | 395 | 92069 | 4 | 142120 | 142120 | 142576 | 92138:1264 |
| ? | 0x0017 | 160 | both | 391 | 91282 | 5 | 151364 | 151364 | 151512 | 91355:2008 |
| ? | 0x0017 | 160 | both | 392 | 91485 | 5 | 166608 | 166608 | 166756 | 91566:868 |
| ? | 0x0017 | 160 | both | 394 | 91883 | 5 | 153092 | 153092 | 153240 | 91957:1688 |
| ? | 0x0017 | 160 | both | 395 | 92069 | 5 | 153092 | 153092 | 153240 | 92143:1688 |
| Fly | 0x0016 | 240 | both | 392 | 91485 | 6 | 170020 | 170020 | 170532 | 91568:548 |
| Fly | 0x0016 | 240 | both | 393 | 91686 | 5 | 180484 | 180484 | 180996 | 91774:772 |
| Fly | 0x0016 | 240 | both | 396 | 92263 | 5 | 180324 | 180324 | 180836 | 92351:612 |
| Fly | 0x0016 | 240 | both | 401 | 93380 | 6 | 251908 | 251908 | 252420 | 93503:516 |
| Triceratops (Chrysler, phase 1) | 0x0427 | 1200 | both | 397 | 92531 | 3 | 182988 | 182988 | 184472 | 92621:152 |
| Triceratops (Chrysler, phase 2) | 0x0427 | 1600 | both | 397 | 92531 | 4 | 196696 | 196696 | 197976 | 92627:1368 |
| Triceratops (Chrysler, total) | 0x0427 | 2800 | both | 397 | 92531 | 5 | 208920 | 208920 | 209500 | 92633:604 |
| Lizard | 0x001A | 315 | both | 398 | 92772 | 3 | 138556 | 138556 | 139260 | 92839:2044 |
| Lizard | 0x001A | 315 | both | 400 | 93169 | 4 | 151828 | 151828 | 152532 | 93243:980 |
| Lizard | 0x001A | 315 | both | 403 | 93805 | 3 | 138396 | 138396 | 139100 | 93872:1884 |
| Cat | 0x0020 | 375 | both | 398 | 92772 | 4 | 150780 | 150780 | 151520 | 92845:2016 |
| Cat | 0x0020 | 375 | both | 400 | 93169 | 3 | 138556 | 138556 | 139296 | 93237:32 |
| Cat | 0x0020 | 375 | both | 403 | 93805 | 4 | 150716 | 150716 | 151456 | 93878:1952 |
| Spawn | 0x001F | 400 | both | 399 | 92984 | 4 | 171532 | 171532 | 172044 | 93068:12 |
| Spawn | 0x001F | 400 | both | 401 | 93380 | 4 | 240136 | 240136 | 240648 | 93497:1032 |
| Spawn | 0x001F | 400 | both | 402 | 93620 | 4 | 173268 | 173268 | 173780 | 93704:1748 |
| Spawn (offspring) | 0x001F | 0 | both | 399 | 92984 | 5 | 181156 | 181156 | 182636 | 93073:364 |
| Spawn (offspring) | 0x001F | 0 | both | 401 | 93380 | 5 | 249760 | 249760 | 251240 | 93502:1384 |
| Spawn (offspring) | 0x001F | 0 | both | 402 | 93620 | 5 | 182892 | 182892 | 184372 | 93710:52 |
| Spawn (offspring) | 0x001F | 100 | both | 399 | 92984 | 5 | 181156 | 181156 | 181368 | 93072:1144 |
| Spawn (offspring) | 0x001F | 100 | both | 401 | 93380 | 5 | 249760 | 249760 | 249972 | 93502:116 |
| Spawn (offspring) | 0x001F | 100 | both | 402 | 93620 | 5 | 182892 | 182892 | 183104 | 93709:832 |
| Cockroach (offspring) | 0x0231 | 4200 | both | 404 | 94063 | 3 | 198952 | 198952 | 201232 | 94161:528 |
| Cockroach | 0x0231 | 4200 | both | 404 | 94063 | 3 | 198952 | 198952 | 201232 | 94161:528 |
| Cockroach (offspring) | 0x0231 | 4200 | both | 404 | 94063 | 3 | 198952 | 198952 | 199532 | 94160:876 |
| Cockroach | 0x0231 | 4200 | both | 404 | 94063 | 3 | 198952 | 198952 | 199532 | 94160:876 |
| Cockroach larva | 0x0231 | 1200 | both | 404 | 94063 | 4 | 218664 | 218664 | 219156 | 94170:20 |
| Frog | 0x001E | 460 | both | 405 | 94317 | 5 | 127220 | 127220 | 127904 | 94379:928 |
| Frog | 0x001E | 460 | both | 407 | 94683 | 4 | 86604 | 86604 | 87288 | 94725:1272 |
| Frog | 0x001E | 460 | both | 408 | 94838 | 5 | 127252 | 127252 | 127936 | 94900:960 |
| Frog | 0x001E | 460 | both | 409 | 95013 | 4 | 112640 | 112640 | 113324 | 95068:684 |
| Frog | 0x001E | 460 | both | 410 | 95196 | 3 | 136264 | 136264 | 136948 | 95262:1780 |
| Parrot | 0x001F | 420 | both | 405 | 94317 | 4 | 113344 | 113344 | 114084 | 94372:1444 |
| Parrot | 0x001F | 420 | both | 406 | 94510 | 4 | 139436 | 139436 | 140176 | 94578:912 |
| Parrot | 0x001F | 420 | both | 407 | 94683 | 3 | 72696 | 72696 | 73436 | 94718:1756 |
| Parrot | 0x001F | 420 | both | 408 | 94838 | 3 | 98732 | 98732 | 99472 | 94886:1168 |
| Parrot | 0x001F | 420 | both | 409 | 95013 | 3 | 98732 | 98732 | 99472 | 95061:1168 |
| Armadillo | 0x0026 | 410 | both | 405 | 94317 | 3 | 98732 | 98732 | 99380 | 94365:1076 |
| Armadillo | 0x0026 | 410 | both | 408 | 94838 | 4 | 112624 | 112624 | 113272 | 94893:632 |
| Armadillo | 0x0026 | 410 | both | 409 | 95013 | 5 | 125688 | 125688 | 126336 | 95074:1408 |
| Armadillo | 0x0026 | 410 | both | 413 | 95875 | 4 | 110052 | 110052 | 110700 | 95929:108 |
| Armadillo | 0x0026 | 410 | both | 416 | 96347 | 4 | 110092 | 110092 | 110740 | 96401:148 |
| Armadillo | 0x0026 | 410 | both | 417 | 96498 | 4 | 109996 | 109996 | 110644 | 96552:52 |
| Scorpion | 0x0023 | 580 | both | 406 | 94510 | 3 | 124776 | 124776 | 125516 | 94571:588 |
| Scorpion | 0x0023 | 580 | both | 410 | 95196 | 4 | 149376 | 149376 | 150116 | 95269:612 |
| Crab (Chrysler, body) | 0x023B | 6400 | both | 411 | 95454 | 3 | 165236 | 165236 | 166896 | 95535:1008 |
| Crab (Chrysler, claw) | 0x023B | 1600 | both | 411 | 95454 | 4 | 181472 | 181472 | 181928 | 95542:1704 |
| Crab (Chrysler, claw) | 0x023B | 1600 | both | 411 | 95454 | 5 | 188132 | 188132 | 188588 | 95546:172 |
| Crab (Chrysler, claw) | 0x023B | 1600 | both | 411 | 95454 | 8 | 205584 | 205584 | 206040 | 95554:1240 |
| Crab (Chrysler, claw) | 0x023B | 1600 | both | 411 | 95454 | 9 | 208984 | 208984 | 209440 | 95556:544 |
| Crab (Chrysler, claw) | 0x043B | 1600 | both | 411 | 95454 | 6 | 194792 | 194792 | 195248 | 95549:688 |
| Crab (Chrysler, claw) | 0x043B | 1600 | both | 411 | 95454 | 7 | 200188 | 200188 | 200644 | 95551:1988 |
| Gold Rat | 0x0028 | 590 | both | 412 | 95694 | 3 | 124504 | 124504 | 125016 | 95755:88 |
| Gold Rat | 0x0028 | 590 | both | 414 | 96035 | 3 | 112508 | 112508 | 113020 | 96090:380 |
| Gold Rat | 0x0028 | 590 | both | 415 | 96195 | 3 | 112508 | 112508 | 113020 | 96250:380 |
| Gold Rat | 0x0028 | 590 | both | 421 | 97495 | 3 | 150556 | 150556 | 151068 | 97568:1564 |
| Gold Rat | 0x0028 | 590 | both | 422 | 97685 | 3 | 150556 | 150556 | 151068 | 97758:1564 |
| Gold Rat | 0x0028 | 590 | both | 423 | 97875 | 3 | 150556 | 150556 | 151068 | 97948:1564 |
| Gold Rat | 0x0028 | 590 | both | 424 | 98056 | 3 | 100432 | 100432 | 100944 | 98105:592 |
| Ratman | 0x002D | 715 | both | 412 | 95694 | 4 | 132780 | 132780 | 133292 | 95759:172 |
| Ratman | 0x002D | 715 | both | 414 | 96035 | 4 | 120784 | 120784 | 121296 | 96094:464 |
| Ratman | 0x002D | 715 | both | 415 | 96195 | 4 | 120784 | 120784 | 121296 | 96254:464 |
| Giant Rat | 0x0030 | 790 | both | 412 | 95694 | 5 | 142636 | 142636 | 143148 | 95763:1836 |
| Squirrel | 0x0035 | 670 | both | 413 | 95875 | 3 | 97540 | 97540 | 98280 | 95922:2024 |
| Squirrel | 0x0035 | 670 | both | 416 | 96347 | 3 | 97548 | 97548 | 98288 | 96394:2032 |
| Squirrel | 0x0035 | 670 | both | 417 | 96498 | 3 | 97388 | 97388 | 98128 | 96545:1872 |
| Small Bee | 0x024A | 600 | both | 418 | 96754 | 3 | 245928 | 245928 | 246400 | 96874:640 |
| Large Bee | 0x024A | 1200 | both | 418 | 96754 | 4 | 258144 | 258144 | 258632 | 96880:584 |
| Queen Bee | 0x024A | 12000 | both | 418 | 96754 | 5 | 267904 | 267904 | 269432 | 96885:1144 |
| Snake (upper floors) | 0x002E | 780 | both | 419 | 97046 | 3 | 189872 | 189872 | 190384 | 97138:1968 |
| Snake (upper floors) | 0x002E | 780 | both | 420 | 97283 | 3 | 189864 | 189864 | 190376 | 97375:1960 |
| Slime | 0x0031 | 880 | both | 419 | 97046 | 6 | 211076 | 211076 | 211588 | 97149:644 |
| Slime | 0x0031 | 880 | both | 420 | 97283 | 6 | 211068 | 211068 | 211580 | 97386:636 |
| Slime | 0x0031 | 880 | both | 421 | 97495 | 5 | 167852 | 167852 | 168364 | 97577:428 |
| Slime | 0x0031 | 880 | both | 422 | 97685 | 5 | 167852 | 167852 | 168364 | 97767:428 |
| Slime | 0x0031 | 880 | both | 423 | 97875 | 5 | 167852 | 167852 | 168364 | 97957:428 |
| Bear | 0x0035 | 1000 | both | 419 | 97046 | 5 | 200960 | 200960 | 201416 | 97144:712 |
| Bear | 0x0035 | 1000 | both | 420 | 97283 | 5 | 200952 | 200952 | 201408 | 97381:704 |
| Dogman | 0x0034 | 980 | both | 421 | 97495 | 4 | 158832 | 158832 | 159352 | 97572:1656 |
| Dogman | 0x0034 | 980 | both | 422 | 97685 | 4 | 158832 | 158832 | 159352 | 97762:1656 |
| Dogman | 0x0034 | 980 | both | 423 | 97875 | 4 | 158832 | 158832 | 159352 | 97952:1656 |
| Dogman | 0x0034 | 980 | both | 424 | 98056 | 4 | 108708 | 108708 | 109228 | 98109:684 |
| Cat | 0x0020 | 375 | both | 434 | 100743 | 4 | 330816 | 330816 | 331556 | 100904:1828 |
| Cat | 0x0020 | 375 | both | 435 | 101021 | 4 | 304560 | 304560 | 305300 | 101170:148 |
| Parrot | 0x001F | 420 | both | 435 | 101021 | 5 | 317928 | 317928 | 318668 | 101176:1228 |
| Parrot | 0x001F | 420 | both | 436 | 101277 | 5 | 255644 | 255644 | 256384 | 101402:384 |
| Parrot | 0x001F | 420 | both | 437 | 101502 | 5 | 278924 | 278924 | 279664 | 101638:1136 |
| Armadillo | 0x0026 | 410 | both | 436 | 101277 | 4 | 240904 | 240904 | 241552 | 101394:1936 |
| Squirrel | 0x0035 | 670 | both | 437 | 101502 | 4 | 266284 | 266284 | 267024 | 101632:784 |

## Next

1. Extract the missing bosses (Eve fights, Worms, Sheeva, Ultimate Being) from the actors that set them up.
2. Read the EX scale from an EX-game save (story variable V80) to confirm the derived range.
3. Decide the Junk tiers (for example name + HP free; weaknesses; drops and steals).
