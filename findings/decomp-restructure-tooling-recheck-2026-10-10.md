# The decomp restructured under us: what changed for the bridge tools, and which old numbers are now historical

**Date: 2026-10-10. Status: re-checked against the pulled tree, no tool code
changes needed. Several earlier numbers describe a source layout that no
longer exists and should be read as historical, not current.**

## What happened

Pulled `khasinski/parasite-eve-decomp` (`8c3ec30f` -> `29e130db`): 3,596
commits, 12,365 files changed. The recent history is dominated by merging
small functions into larger units and renaming them. Regenerated the
recomp's `symbols.toml`, `seeds/ghidra_funcs.txt` and `psx_symbols.h` with
`decomp_bridge.py --no-pull` (1,681 functions, 3,886 seed addresses, 2,586
from the decomp). Those three files are modified but uncommitted in
`parasite-eve-recomp`; nothing was rebuilt, so the overlay code in
`build-release` still reflects the old symbols until the next
autocompile/rebuild.

## The source layout the earlier findings relied on is gone

`src/overlays/` is now 23 directories. Before, it was a directory per room,
each holding a two-line `#include "../room_lib/X.inc"` wrapper or a one-line
macro invocation around one shared implementation. Now:

- `RoomLib_HandlerD*` files: 0 (previously 125 per-room users of the shared
  template).
- `RoomLib_HandlerB` survives only as an `extern` declaration in
  `room_lib.h`; `HandlerD` only in a comment. The implementations live in
  merged units such as `RoomLib_ActorClasses.c`.

## Re-run results

**`classifier_gap_finder.py scan-shared-libs`**: 9 shared templates, 1
matching the `switch` risk pattern (`Memcard_InitVideoBuffers.inc`, 2 users,
in the memcard menu rather than RoomLib). Previously ~18 at-risk templates
and 264 candidate addresses. This is not evidence the game has fewer gaps:
the guest binary did not change, only the decomp's map of it. The scan's
premise ("many per-room files instantiate one shared template") no longer
holds in this tree, so it can no longer enumerate instances.

**`triage.py` over the 501 addresses in `play.ps1`'s `$ForceInterior`**:

| | 2026-09-16 run (211 addrs) | now (501 addrs) |
|---|---|---|
| Resolved to a source file | 3 (1.4%) | 174 (35%) |
| Eligible / ineligible | 0 / 0 | 0 / 0 |
| Unknown | 211 | 501 |

The 501 unknowns: 318 are interior addresses (not a function's own start, so
refused by design), 174 are `semantic_c` but blocked only on a missing
`objdiff.json`, 9 are ambiguous (one symbol, more than one source file; the
check fails closed). The resolution jump is a direct result of the merge:
most functions now map to exactly one plain `.c` file. None of the verdict
reasons involved the `.inc`/macro shared-template resolvers, so those
branches were not exercised on this tree.

**`confidence.py check-address`** spot-checks (`0x8018F300`, `0x8018F308`,
`0x8018F318`, `0x80191068`) behaved as designed on the new tree.

## One thing that reads as better than it is

`0x80191068` and `0x8018F318` now resolve to `RoomLib_ActorClasses.c`,
classified `semantic_c`. That file still contains real inline `asm("")`
barriers, `register ... asm("$N")` pins and GTE references. The decomp's own
`source_quality.py` deliberately does not count empty barriers, register pins
or symbol aliases as assembly ("do not emit instructions"), so `semantic_c`
means "trustworthy by the decomp's convention", not "replaceable by this
toolkit". `generator.py` was not run on these (triage only runs it after a
confidence pass, and nothing passes without `objdiff.json`), but the earlier
conclusion that `confidence.py`/`generator.py` cannot replace the RoomLib
dispatchers rests on pointer parameters and register/GTE use, which this
merge did not remove. Treat that conclusion as unchanged, not re-proven.

## What remains valid / what is now historical

- **Still valid**: the 501-address `--force-interior` list in `play.ps1`.
  Those are guest addresses observed in real captures, independent of how the
  decomp is organised.
- **Historical**: the 264-address `scan-shared-libs` candidate list, the
  "125 files / 1,500 candidates" expansion for `RoomLib_HandlerB`, and any
  function names in older findings (`func_8018F2DC` is now
  `RoomLib_ConfigureHandlerD +0x8`, etc.). The old per-room names can no longer
  be regenerated from source.
- **Open**: building the decomp to produce `objdiff.json` is the only thing
  that can turn the 174 `semantic_c` addresses from "unknown" into a real
  eligible/ineligible verdict. Not attempted: it needs the decomp's full
  toolchain build and nothing in flight depends on it.
