# Parasite Eve disc layout: what disc 1 and disc 2 share (verified against the user's dumps)

**Date: 2026-10-10. Status: verified by reading both ISO9660 volumes directly. The starting claim came from the decomp
developer via the user: the discs are the same except for the FMVs, and the game checks three files.**

## What the decomp says

`OpenPeImage()` (`src/main/render/Render_InitDisplayLists.c`) calls `DsSearchFile` for three paths whose strings sit at
`0x80011330`, `0x80011348` and `0x80011354`. `include/pe1/pe_image.h` (written from those data bytes) names them:

| Path | Role |
|---|---|
| `\FMV1\PEDISC01.IDF;1` | disc 1 marker (sets `g_PeImageMountFlags` bit 0) |
| `\PE.IMG;1` | the main asset archive, about 206 MB; its start sector is stored in `g_PeImageBaseLba` and every read is relative to it |
| `\FMV2\PEDISC02.IDF;1` | disc 2 marker (bit 1) |

Two details in the relayed description differ from the decomp header and from the discs: the archive is **`PE.IMG`**
(not `PE1.IMG`), and the disc 2 marker is in **`FMV2`** (not `FMV1`).

## What the two discs contain

| | Disc 1 | Disc 2 |
|---|---|---|
| Root | `FMV1/`, `PE.IMG`, `SLUS_006.62`, `SYSTEM.CNF` | `FMV2/`, `PE.IMG`, `SLUS_006.68`, `SYSTEM.CNF`, `XASTREAM/` |
| Marker | `FMV1/PEDISC01.IDF` (40 B) | `FMV2/PEDISC02.IDF` (40 B) |
| `PE.IMG` | sector 1013, 206,213,120 B, sha256 `c3709b2d...` | **identical** (same sector, size and hash) |
| Boot EXE | `SLUS_006.62`, sha256 `5d94938e...` | `SLUS_006.68`: **byte-identical** to the disc 1 file (0 differing words of 506,368; same header) |
| `SYSTEM.CNF` | differs (it names the boot file) | differs |
| Other | 22 disc 1 FMV `.STR` files | 28 disc 2 FMV `.STR` files and an `XASTREAM/` audio folder |

So the game's code and its data archive are the same on both discs. Only the FMV streams, the extra XA audio on disc 2,
the two marker files, the boot file's name and `SYSTEM.CNF` differ.

## What follows for the mod project

- One generated game, one overlay shard cache and one set of mods serve both discs. Every mod patch site checked
  (`0x800185C0`, the four inventory clamps, the two capacity words) holds the same retail bytes on disc 2, so `expected`
  checks pass on either disc.
- Overlay code is loaded out of `PE.IMG` (sector offsets relative to the base LBA), so shards compiled while playing disc 1
  also apply on disc 2, and an ahead-of-time overlay extractor only has to read `PE.IMG` once.
- Anything that rebuilds or overlays disc content must keep the marker files for the disc being played; the game decides
  which disc it has from those, not from the executable.
- `PE.IMG` holds room geometry, entity models and textures, string tables and scene data, so data-level mods (and the
  decomp's tier-1 sector tables, e.g. the entity-texture ranges `D_800930D8`/`D_800930DA`) are the place to look when working
  out which enemies' assets are available in which areas for a randomizer.
