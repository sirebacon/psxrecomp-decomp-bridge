# Enemy model catalog — October 19, 2026

The 3D model behind every Bestiary creature, with where to find it on disc. Stats, drops and the stat
blocks' own locations are in `findings/pe-bestiary-draft-2026-10-19.md`; human characters in
`findings/pe-model-catalog-2026-10-19.md`. Built by `tools/pe_assets/catalog_enemies.py`; every
appearance is in `findings/data/pe-enemy-model-catalog-2026-10-19.json`.

**How to find a model:** read the room's sectors from its LBA on "Parasite Eve (USA) (Disc N).bin"
(2048 user-data bytes each); the model header sits at the offset, i.e. at disc sector:byte. A
creature's model is the room model in the bank slot numbered like its script actor.

**Renders** (local only, git-ignored): `tools/pe_assets/renders/enemies/` — one shaded render per mesh,
plus `_tex` when a save state in one of its rooms had the textures loaded; contact sheets
`tools/pe_assets/renders/enemies_sheet_*.png`. Enemy rooms carry no textures of their own.

58 distinct meshes for 380 creature appearances.

| Mesh | Creature(s) | Parts | Verts | Maps | First copy: map / slot, room LBA, offset, sector:byte | Textured render |
|---|---|---:|---:|---|---|---|
| mesh000 | Actress | 28 | 447 | 5 | 5 / 2, 11049, 37044, 11067:180 | - |
| mesh001 | Giant Rat, Gold Rat, Grey Rat, Rat, Rat (sewer variant), Yellow Rat | 26 | 269 | 12, 13, 14, 16, 27, 28, 30, 100, 110, 113 +14 | 12 / 5, 12007, 21032, 12017:552 | - |
| mesh002 | Parrot | 20 | 179 | 14, 22, 405, 406, 407, 408, 409, 435, 436, 437 | 14 / 7, 12381, 29328, 12395:656 | - |
| mesh003 | Eve (carriage), Eve (rehearsal room) | 49 | 904 | 23, 89 | 23 / 2, 13904, 35156, 13921:340 | - |
| mesh004 | Frog, Frog (sewer) | 17 | 359 | 28, 32, 168, 169, 405, 407, 408, 409, 410 | 28 / 8, 15016, 29328, 15030:656 | - |
| mesh005 | Alligator, Alligator (Chrysler), Alligator (body) | 52 | 554 | 34, 174, 348, 383 | 34 / 3, 16597, 33384, 16613:616 | - |
| mesh006 | Green Snake, Red Snake, Snake, Snake (upper floors) | 13 | 130 | 59, 62, 66, 67, 78, 82, 162, 163, 167, 384 +10 | 59 / 5, 24373, 14364, 24380:28 | - |
| mesh007 | Bird, Blackbird | 23 | 218 | 61, 67, 80, 81, 87, 100, 107, 110, 116, 120 +5 | 61 / 5, 24699, 14992, 24706:656 | yes |
| mesh008 | Monkey | 23 | 343 | 63, 83, 358, 384, 387 | 63 / 3, 25172, 3600, 25173:1552 | - |
| mesh009 | Plant | 28 | 562 | 65, 85, 87, 391, 393, 394, 395, 396, 399, 401 +1 | 65 / 3, 25672, 18660, 25681:228 | yes |
| mesh010 | Bear | 23 | 714 | 75, 80, 82, 419, 420 | 75 / 5, 27630, 37324, 27648:460 | - |
| mesh011 | Worm | 11 | 263 | 86 | 86 / 3, 30202, 37116, 30220:252 | - |
| mesh012 | Gold Spider, Hospital map 159 actor, Spider, Spider (no reward) | 24 | 178 | 104, 113, 115, 116, 120, 122, 159, 263, 265, 333 +4 | 104 / 4, 34667, 18888, 34676:456 | - |
| mesh013 | Dogman, Giant Dogman | 32 | 385 | 107, 111, 114, 118, 122, 421, 422, 423, 424 | 107 / 5, 35066, 33032, 35082:264 | - |
| mesh014 | Sheeva (body) | 56 | 1020 | 123 | 123 / 1, 38622, 54696, 38648:1448 | - |
| mesh015 | Giant Slime, Slime | 23 | 147 | 126, 129, 137, 139, 140, 141, 147, 149, 152, 324 +8 | 126 / 7, 39315, 19048, 39324:616 | - |
| mesh016 | Fly | 28 | 422 | 137, 140, 146, 147, 324, 327, 392, 393, 396, 401 | 137 / 5, 41106, 45232, 41128:176 | - |
| mesh017 | Ratman | 27 | 433 | 141, 146, 153, 154, 328, 412, 414, 415 | 141 / 6, 42154, 59856, 42183:464 | - |
| mesh018 | Spawn | 38 | 504 | 145, 152, 153, 154, 332, 399, 401, 402 | 145 / 6, 42972, 17796, 42980:1412 | - |
| mesh019 | Spawn (offspring) | 2 | 21 | 145, 152, 153, 154, 332, 399, 401, 402 | 145 / 7, 42972, 43112, 42993:104 | - |
| mesh020 | Giant Spider (Chrysler), Giant Spider (phase 1), Giant Spider (phase 2) | 47 | 1064 | 156, 291, 380 | 156 / 3, 45891, 44636, 45912:1628 | - |
| mesh021 | Cat | 43 | 456 | 162, 163, 398, 400, 403, 434, 435 | 162 / 5, 47149, 32704, 47164:1984 | - |
| mesh022 | Bat | 22 | 197 | 167, 168, 169, 173, 178, 186, 295, 299, 309, 310 +3 | 167 / 7, 48209, 32772, 48225:4 | - |
| mesh023 | Mole | 32 | 314 | 186, 187, 385, 388, 389 | 186 / 4, 51257, 50824, 51281:1672 | - |
| mesh024 | Centipede (Chrysler, head), Centipede (head, phase 1) | 30 | 318 | 188, 390 | 188 / 5, 51727, 58028, 51755:684 | - |
| mesh025 | Centipede (Chrysler, middle), Centipede (middle) | 16 | 193 | 188, 390 | 188 / 6, 51727, 71976, 51762:296 | - |
| mesh026 | Centipede (Chrysler, middle), Centipede (middle) | 16 | 193 | 188, 390 | 188 / 7, 51727, 79692, 51765:1868 | - |
| mesh027 | Centipede (Chrysler, tail), Centipede (tail) | 28 | 257 | 188, 390 | 188 / 8, 51727, 87408, 51769:1392 | - |
| mesh030 | Dinosaur | 33 | 321 | 197, 198, 199, 203, 206, 207, 214, 217, 218, 219 +14 | 197 / 5, 53843, 14364, 53850:28 | yes |
| mesh028 | Lizard | 21 | 214 | 197, 198, 199, 201, 206, 207, 217, 218, 220, 223 +7 | 197 / 6, 53843, 29416, 53857:744 | - |
| mesh029 | Armadillo, Armadillo (forced fight) | 31 | 231 | 197, 198, 199, 203, 206, 207, 210, 214, 217, 219 +14 | 197 / 7, 53843, 40088, 53862:1176 | yes |
| mesh031 | Pterodactyl | 34 | 387 | 203, 221, 223, 224, 229, 231, 233, 234, 242, 246 | 203 / 6, 55320, 62020, 55350:580 | yes |
| mesh032 | Scorpion, Scorpion (tougher) | 39 | 545 | 205, 231, 234, 243, 406, 410 | 205 / 4, 55688, 15712, 55695:1376 | - |
| mesh033 | Triceratops (Chrysler, phase 1), Triceratops (phase 1) | 8 | 199 | 245, 397 | 245 / 6, 64914, 93284, 64959:1124 | - |
| mesh034 | Triceratops (Chrysler, phase 2), Triceratops (phase 2) | 6 | 72 | 245, 397 | 245 / 7, 64914, 103752, 64964:1352 | - |
| mesh035 | Triceratops (Chrysler, total), Triceratops part | 29 | 797 | 245, 397 | 245 / 8, 64914, 56248, 64941:952 | - |
| mesh036 | Tyrannosaur | 39 | 929 | 256 | 256 / 2, 67633, 59196, 67661:1852 | - |
| mesh039 | Crab (Chrysler, body), Crab (body) | 26 | 318 | 269, 411 | 269 / 3, 69927, 40836, 69946:1924 | - |
| mesh037 | Crab (Chrysler, claw), Crab (claw) | 7 | 78 | 269, 411 | 269 / 4, 69927, 56624, 69954:1328 | - |
| mesh040 | Crab (Chrysler, claw), Crab (claw) | 5 | 37 | 269, 411 | 269 / 6, 69927, 65104, 69958:1616 | - |
| mesh038 | Crab (Chrysler, claw), Crab (claw) | 5 | 42 | 269, 411 | 269 / 8, 69927, 68408, 69960:824 | - |
| mesh041 | Eve (Statue of Liberty, reward holder) | 45 | 1008 | 273 | 273 / 2, 71025, 78668, 71063:844 | yes |
| mesh049 | Monster Box | 42 | 195 | 295, 434, 435, 436, 437 | 295 / 3, 75097, 32144, 75112:1424 | - |
| mesh050 | Eve (Chrysler) | 31 | 435 | 318 | 318 / 3, 78191, 72676, 78226:996 | - |
| mesh051 | Eve (Chrysler) part | 23 | 476 | 318 | 318 / 4, 78191, 96540, 78238:284 | - |
| mesh042 | Ultimate Being (1st) | 38 | 653 | 350 | 350 / 2, 84552, 76472, 84589:696 | - |
| mesh043 | Ultimate Being form | 19 | 343 | 350 | 350 / 3, 84552, 111228, 84606:636 | - |
| mesh052 | Cockroach, Cockroach (offspring) | 54 | 596 | 404 | 404 / 3, 94063, 50772, 94087:1620 | - |
| mesh053 | Cockroach larva | 5 | 30 | 404 | 404 / 4, 94063, 79068, 94101:1244 | - |
| mesh054 | Squirrel | 24 | 223 | 413, 416, 417, 437 | 413 / 3, 95875, 31288, 95890:568 | - |
| mesh055 | Small Bee | 38 | 252 | 418 | 418 / 3, 96754, 72252, 96789:572 | - |
| mesh056 | Large Bee | 47 | 391 | 418 | 418 / 4, 96754, 83956, 96794:2036 | - |
| mesh057 | Queen Bee | 47 | 560 | 418 | 418 / 5, 96754, 102472, 96804:72 | - |
| mesh044 | Ultimate Being (1st) | 41 | 726 | 428 | 428 / 2, 99302, 51400, 99327:200 | - |
| mesh046 | Ultimate Being (3rd) | 44 | 921 | 429 | 429 / 2, 99602, 82400, 99642:480 | - |
| mesh045 | Ultimate Being form | 2 | 5 | 429 | 429 / 3, 99602, 131972, 99666:900 | - |
| mesh047 | Ultimate Being (4th) | 47 | 484 | 430 | 430 / 2, 99900, 35208, 99917:392 | yes |
| mesh048 | Eve (final form) | 54 | 1049 | 432 | 432 / 2, 100283, 73876, 100319:148 | - |

Stat blocks with no model in their actor's slot (set up by another actor): Alligator (tail) 0x0100 (map 34 actor 4), Sheeva (left head) 0x0100 (map 123 actor 2), Sheeva (right head) 0x0100 (map 123 actor 3), Sheeva (center head) 0x0100 (map 123 actor 4), Eve (Statue of Liberty) part 0x0125 (map 273 actor 5), Eve (Statue of Liberty) part 0x0125 (map 273 actor 6), Eve (Statue of Liberty) part 0x0125 (map 273 actor 7)
