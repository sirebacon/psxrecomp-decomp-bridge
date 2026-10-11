# Parasite Eve mod state audit: what actually runs in the game, and why "Increased Storage" cannot work as built

**Date: 2026-10-10. Status: verified against the running game (live RAM reads over the debug server) and the decomp's own
struct definitions. Corrects an earlier statement in the same session that "all six mods are off by default".**

## What the six packages really do

| Package | Default | Mechanism | Effect in the running game |
|---|---|---|---|
| `pe.enhancement.faster-movement-live` | **ON** | Live declarative `[[patch]]`, `main_exe` `0x800185C0`, `expected 05 00 04 3C` -> `14 00 04 3C` | **Active.** Live RAM at `0x800185C0` reads `3C040014` (20x; retail is 5x). |
| `pe.enhancement.bonus-points-floor` | **ON** (999) | Per-frame C plugin, holds `g_AyaBonusPoints` (`0x800C0E10`) at the floor | Not re-verified this session; earlier confirmed. |
| `pe.enhancement.personal-inventory-floor` | **ON** (40) | Per-frame C plugin raising the carried-slot count | Not re-verified this session. |
| `pe.enhancement.god-mode` | off | Per-frame C plugin topping up live battle HP | Not re-verified this session. |
| `pe.enhancement.faster-movement` | n/a (retired) | Empty package (historical record) | None. |
| `pe.enhancement.increased-storage` | n/a (retired) | Empty package; description claims the 80-slot clamps are "baked into the shipped executable" | **None. See below.** |

## The "baked into the executable" changes do nothing at runtime

The project's `disc/SLUS_006.62` (the boot EXE the static game code is generated from) is not retail:

- `0x800185C0` = `3C040014` (20x movement; retail `3C040005`)
- `0x80052F28` = `slti ..,0x51` and `0x80052F94` = `slti ..,0x51` (81), `0x80052F34` / `0x80052FB4` = `addiu ..,0x50` (80) —
  the inventory clamps raised from retail 51/50 to 81/80.

But the game loads its code from the real disc image at runtime, so live RAM holds the retail bytes. Reading the running
game:

- `0x80052F24..`: `28820033`, `24040032` (51 / 50) and `0x80052F90..`: `28630033` (51) — **retail clamps, unchanged.**

So the 80-slot change exists only in the file the game code is generated from, never in what executes. It also makes the
static translation disagree with live bytes on those pages, which the runtime reports as diverged text pages
(`text_diverged_pages` was 1-2 in every stall report) and which forces the affected entries through the dirty-RAM
interpreter. That is a small cost on top of no benefit.

## Why raising the clamp can never work

`include/pe1/aya.h` in the decomp: `AyaSaveState` has `s16 inventory_items[50]` at offset `0x48`, i.e.
`0x800C0E48..0x800C0EAB`, and the struct "ends at 0xAC, where equipment records begin"
(`sizeof(AyaSaveState) == 0xAC`, asserted). The struct prefix is also part of the memory-card save layout. Raising the
clamp to 80 would write 30 extra item IDs (60 bytes) over the equipment records, and a save written that way would not
fit the card format. The only reason this never corrupted anything is that the change never reached the running game.

A real storage increase needs a different design (a relocated or separate inventory, with every access and the save
format accounted for, or a new storage chest in a separate system), not a clamp edit.

## Decision (2026-10-10): Increased Storage is parked

The user chose not to pursue extra storage for now. If it is revisited, the viable shape is a plugin-held side store
outside the save structures (not a raised clamp), with a separate persistence story, and a rule for what happens to its
items when the mod is disabled (hide rather than delete, and warn). The game's separate NYPD/warehouse storage system
has not been inspected and might offer headroom without a side store. The retired `pe.enhancement.increased-storage`
package stays an empty placeholder; nothing about storage should be re-enabled until that design exists.

## Cleanup done (2026-10-10, same day)

Extracted `SLUS_006.62` straight from the disc image (read-only ISO9660 walk of the Disc 1 BIN) and compared it with the
four copies in `disc/`:

- `SLUS_006.62.original-backup` is byte-identical to the disc's file (sha256 `5d94938e...351b`). That is also exactly
  the `executable_sha256` pinned in `project-manifest.toml`, so the patched file had been violating the project's own pin.
- The working `SLUS_006.62` (and `.patched`) differed in **7 words**, not the 5 first suspected:
  `0x800185C0` (movement 20x), `0x800523B8` and `0x800523C0` (the personal-inventory capacity lookup replaced by a
  hard-coded 40), and the four clamps `0x80052F28`, `0x80052F34`, `0x80052F94`, `0x80052FB4`.

Restored the retail bytes (the modified file is kept as `disc/SLUS_006.62.baked-7-words-2026-10-10`), regenerated the
game C and rebuilt (`build_recomp.ps1 -SkipSync`). Only three generated shards changed (`full_02`, `full_22`,
`full_23`); the generated code at `0x800185C0` is now the retail `3C040005`. Verified in the running game:

- live `0x800185C0` = `3C040014`: 20x still active, now only through the live patch
- live capacity words and clamp words are retail
- `text_diverged_pages` 1 (was 2; the one left is the page the live movement patch deliberately changes)
- zero interpreted instructions, steady 60 fps, autocompile idle (the overlay cache survived)

The two retired packages' descriptions, which still claimed the values were "baked into the executable", were rewritten
in the Parasite Eve repo. Rule going forward: never edit `disc/SLUS_006.62`; every mod is a live `[[patch]]` or a
plugin, checked against the retail bytes.

## What this means for the work

1. Do not ship or re-enable an Increased Storage mod based on the clamp values. Redefine the goal first.
2. The 20x movement mod is the one confirmed-working change. Whether 20x feels right (the manifest warns of a
   sliding/skating look) is a playtest for the user.
3. Cleanup worth doing, none of it done yet: restore `disc/SLUS_006.62` to the retail bytes so static code matches live
   RAM, remove the stale 80-slot claim from the retired package, then rebuild. The overlay shard cache is keyed by overlay
   content and engine codegen hash, so regenerating the main EXE code should not invalidate it. Any future change should be
   a live `[[patch]]` with retail `expected` bytes (the mechanism that works), never a disc-file edit.
4. The three default-ON mods mean a fresh install starts with 20x speed, 999 bonus points and a 40-slot personal floor
   without opting in. Decide whether that is intended.
