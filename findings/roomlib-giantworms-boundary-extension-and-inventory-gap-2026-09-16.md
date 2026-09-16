# GiantWorms save unlocks two new classifier-gap discoveries: a bigger RoomLib boundary, and the first non-RoomLib gap

**Date: 2026-09-16. Status: confirmed against real capture data, not yet
live-verified. 271 addresses, none overlapping anything already in
`build/play.ps1`.**

## How this was found

The user downloaded the full PS1 save collection from
[fantasyanime.com's Parasite Eve saves page](https://fantasyanime.com/squaresoft/parasiteeve/pe_saves.htm)
and asked whether it could help testing. It did, immediately: PS1 memory
cards are a plain 128KB raw image, and the downloaded ePSXe-format
`epsxe000.mcr` files are byte-for-byte compatible with this project's
`saves/card1.mcd`. Copying in the "GiantWorms" save (backing up the
existing card first) boots the game directly into the Giant Worms boss
fight — a room this project could never reach before except by blind,
unguided synthetic button presses through an extended intro sequence.

With the game sitting in a real, sustained boss-fight state, a fresh
`compile_overlays.py --check` was run against this exact session's own
`build-dbg/overlay_captures.json` (confirmed updated at 12:21:49 PM,
i.e. capturing this save's actual gameplay, not stale data):

```
python psxrecomp/tools/compile_overlays.py --captures build-dbg/overlay_captures.json --game-toml build-dbg/game.toml --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe --runtime-include psxrecomp/runtime/include --check
```

Then `classifier_gap_finder.py annotate` was run against the transcript to
resolve every excluded address to its containing function:

```
python bridge/classifier_gap_finder.py annotate --config games/parasite-eve/config.toml --check-log giantworms_check.txt
```

Result: **271 addresses, real observed executions, marked
`excluded: OBSERVED_PC_ONLY`** (with some `BRANCH_TARGET_ONLY` interspersed)
— permanently interpreted every time they're reached, exactly the "stuck
in the interpreter" signature behind every dirty-RAM fix this project has
made. Checking each address against `build/play.ps1`'s existing
`$ForceInterior` list found **zero overlap** — every one of these 271 is
newly discovered.

## Discovery 1: the 2026-09-14 "182 addresses" gap was itself incomplete

`play.ps1` already carries a 182-address RoomLib force-interior block found
2026-09-14, in two clusters: `0x8018F77C`-`0x8018F7EC` (29 addrs) and
`0x8018F95C`-`0x8018FBBC` (153 addrs). That capture's own writeup was
explicit that this was "directly observed," not a completeness guarantee.

This new, richer capture (a real boss fight, not a short idle/menu window)
shows the *same* contiguous RoomLib dispatch region extending on **both
sides** of that already-known block:

- **Before it**: `0x8018F2F4`-`0x8018F370` (31 addresses) — a standalone
  `func_8018F2DC`, then a run of small handlers (`RoomLib_Spawn6`,
  `RoomLib_CloseTarget` x5, `RoomLib_WindowHandler`,
  `RoomLib_RegisterTable3`, `func_8018F358`).
- **Immediately after the first known cluster ends** (`0x8018F7EC`): new
  addresses resume at `0x8018F7F4` — exactly `func_8018F79C+0x58`. This is
  the same `func_8018F79C` hot spot chased earlier this session via
  `stall_report.py` during live play (interpreted-instruction count
  climbing 36.6M → 70M → 140M) — now confirmed by the offline `--check`
  transcript to be a real classifier gap, not just a hot PC.
- **Immediately after the second known cluster ends** (`0x8018FBBC`): new
  addresses resume at `0x8018FBC0` and run continuously through
  `0x8018FD00` — `RoomLib_Set3Range`, `RoomLib_Set3Size`, `func_8018FBE8`,
  `RoomLib_FxNotify`, `func_8018FC2C`, two `RoomLib_SetArgs3` templates,
  `RoomLib_SetPair`, `RoomLib_FxShimmer`.
- **A further run from `0x80191008` through `0x801911FC`**, stopping
  exactly where the already-known `0x80191200` entry begins — including a
  brand-new named dispatcher, **`RoomLib_HandlerE`** (`0x8019100C`-
  `0x80191024`), never identified in this project before, and interior
  offsets of **`RoomLib_HandlerD`** (`0x80191068`, `0x8019106C`,
  `0x801910F0`-`0x801910FC`).

Every new address here fits *exactly* into the gaps immediately adjacent to
clusters already known to be real: nothing overlaps, and every boundary
lines up with where the older, shorter captures simply ran out of runtime
to observe further. This isn't a new bug — it's the true extent of a bug
this project already knew about, previously undersized because no capture
had run long enough inside this specific code path until now.

**Note on `RoomLib_HandlerD`**: this dispatcher was confirmed earlier this
session (reading `RoomLib_HandlerD.inc` in full) to be structurally
impossible to replace via the `func_override` toolkit — it pins raw MIPS
registers, uses inline-asm barriers, and drives GTE hardware directly.
That finding is about *replacing* the function with native decomp C.
Force-interior is a completely different, already-proven mechanism (making
the classifier recognize these addresses as legitimate interior jump
targets rather than orphaned code) and is not blocked by that finding.

## Discovery 2: the first classifier gap ever found outside RoomLib

Nine addresses resolve to `Inv_RecalcSlotStats` (4 addresses,
`0x800521B4`-`0x800523F4`) and `Inv_GetAyaSlotLimit` (5 addresses,
`0x80052F7C`-`0x80052FC8`) — the **inventory subsystem**, structurally
unrelated to RoomLib's shared dispatch templates. Every classifier gap
this project has found before today, across the entire investigation
history, has been in the RoomLib region (`0x8018Fxxx`-`0x80193xxx`). This
is the first evidence the same underlying problem (a `switch`-driven
jump table the classifier can't statically resolve) exists elsewhere in
the codebase too.

This is a small cluster (9 addresses vs. 253 for the RoomLib boundary
extension), but it's a meaningful scope finding: it suggests running
`classifier_gap_finder.py scan-shared-libs` with a wider `--file-glob`
against non-RoomLib source (inventory, combat, or other systems with
their own dispatch-style code) could surface more gaps of the same shape
that nobody has looked for yet, since every prior scan in this project
was scoped to RoomLib specifically.

## What was done

Added all 271 addresses to `build/play.ps1`'s `$ForceInterior` default,
grouped and commented by cluster, immediately following the
`RoomLib_HandlerB`/`HandlerC` block from earlier today — **marked
NOT YET LIVE-VERIFIED**, the same discipline used for every entry added
this session: real, directly-observed addresses from a genuine gameplay
capture, but no independent live before/after dirty-RAM confirmation yet.

## Suggested next steps

1. **Live-verify this block** the same way every earlier-confirmed entry
   in `play.ps1` was verified: launch with the updated list, load the
   GiantWorms save (now that save-loading is a proven methodology), and
   watch `stall_report.py` for `interp_share`/dispatch-native counts
   before and after.
2. **Extend `scan-shared-libs` beyond RoomLib** — the inventory-subsystem
   discovery suggests the same switch-in-shared-code pattern may exist in
   other game systems nobody has scanned yet.
3. **Explore the remaining 24 save files** — this session used 2 of 26
   downloaded saves and found a major result from the second one. The
   other areas (Central Park, Alligator, Chinatown, Sewers, Museum, T-Rex,
   Hospital, Sperm Bank, Warehouse, Centipede, Helicopter, etc.) are
   untested and each is a plausible source of more real, direct capture
   data the same way this one was.
4. **`0x0018F468`** (flagged in `live-verification-attempt-2026-09-16.md`,
   still unclaimed) — worth checking against this same GiantWorms capture
   now that a full transcript exists.
