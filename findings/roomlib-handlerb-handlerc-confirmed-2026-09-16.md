# `RoomLib_HandlerB` and `RoomLib_HandlerC`: two brand-new classifier gaps, confirmed against a real `--check` transcript

**Date: 2026-09-16. Status: confirmed with real, live capture data — not a
prediction. Candidate list computed, not yet applied to a live launch
config.**

## What was done

Ran `compile_overlays.py --check` for real, against this checkout's actual
`build-release/overlay_captures.json` (a genuine capture from recent
gameplay, last written 2026-09-15 23:41 — not synthetic, not a saved
sample):

```
python psxrecomp/tools/compile_overlays.py \
    --captures build-release/overlay_captures.json \
    --game-toml build-release/game.toml \
    --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe \
    --runtime-include psxrecomp/runtime/include \
    --check
```

This produced a real, 896-line transcript covering 4 captured overlay
regions, with **719 unique un-recovered `OBSERVED_PC_ONLY` addresses**
across the whole capture. Cross-referenced every one of those against the
264 candidate addresses `scan-shared-libs-auto-discovery-2026-09-16.md`
found (using `classifier_gap_finder.py`'s own `containing_function`
resolution, not a hand check) — the exact "confirm before trusting" step
that document's own warning called for.

## Result: two confirmed hits, one already-known sanity check

**42 real, un-recovered addresses landed inside one of the 19 at-risk
templates.** They split three ways:

1. **`func_80191C78` (18 addresses)** — an instance of
   `ROOMLIB_STATE_DISPATCH_VARIANT2`, the macro already confirmed bad in
   `roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`. Expected,
   and a useful sanity check that this cross-reference method actually
   works: it correctly re-found a known-true positive.

2. **`RoomLib_HandlerB` — a genuinely NEW confirmed instance, never on any
   force-interior list before today.** Four separate address instances
   showed real excluded addresses in this one capture alone:
   `0x80191D70`, `0x80191E0C`, `0x80191ED8`, `0x801929BC` — each with
   several of its own interior offsets excluded (e.g. `0x80191ED8`'s
   instance alone showed offsets `+0x4` through `+0x2C` all excluded). The
   **union of every confirmed offset across all four instances** is a
   clean, evenly-spaced set: `0x0, 0x4, 0x8, 0xC, 0x10, 0x14, 0x18, 0x1C,
   0x20, 0x24, 0x28, 0x2C` — the same "consecutive 4-byte jump-table case"
   shape as the already-known `ROOMLIB_STATE_DISPATCH_VARIANT2` bug,
   independently confirmed on a different macro.

3. **`RoomLib_HandlerC` — also genuinely new.** One instance
   (`0x801929EC`) showed three consecutive interior offsets excluded
   (`+0x0`, `+0x4`, `+0x8`).

## Computed the full candidate list for the confirmed one

With real offsets in hand for `RoomLib_HandlerB`, ran the natural next step
— `scan-pattern` against every real user of that exact template (anchored
to the literal `.inc` include, not a bare name match, which over-matched
482 unrelated files including `RoomLib_HandlerBArgs` and cross-references
before the pattern was tightened):

```
python bridge/classifier_gap_finder.py scan-pattern \
    --config games/parasite-eve/config.toml \
    --pattern "RoomLib_HandlerB\.inc" \
    --known-offsets 0x0,0x4,0x8,0xC,0x10,0x14,0x18,0x1C,0x20,0x24,0x28,0x2C
```

**125 files found, all 125 address-resolved, 1,500 candidate addresses
computed** (125 base addresses × 12 confirmed offsets). This is the exact
scale of the original `ROOMLIB_STATE_DISPATCH_VARIANT2` fix, on a second,
independently-discovered macro.

## What this does NOT mean yet

The 1,500 computed candidates are **still a prediction, not a
verification** — this capture only directly observed 4 of `RoomLib_HandlerB`'s
125 real instances actually executing, and only some of their offsets. The
same caveat `roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`
already established applies here: confirm a couple of the other 121
instances share the exact same internal layout (e.g. compare function
sizes) before trusting the full list, and **do not blanket-apply 1,500
addresses to a live launch config in one step** — this project has already
hit a real compile-storm regression doing exactly that once with a much
smaller list. `RoomLib_HandlerC` has even less direct evidence (3 offsets
from one instance) and needs the same treatment before its own full
candidate list is computed.

## Why this matters

This is the first real, end-to-end validation of the whole
`scan-shared-libs` → `scan-pattern` pipeline built earlier today, using
data neither tool had ever seen: it took a genuinely blind structural
prediction (19 at-risk templates, 264 addresses, "might have this bug")
and, cross-referenced against real gameplay capture data, turned two of
them into confirmed, real classifier gaps with a computed 1,500-address
candidate list ready for the same careful, incremental rollout that fixed
`ROOMLIB_STATE_DISPATCH_VARIANT2` and `0x80191200` before it.

## Suggested next step

Pick a small handful of `RoomLib_HandlerB`'s 1,500 computed addresses
(start with the 4 directly-observed instances' own confirmed offsets, not
the full predicted list), add them to `build/play.ps1`'s `$ForceInterior`
default the same incremental way the last two fixes were applied, and
verify a real dirty-RAM before/after — the established, working pattern for
every confirmed fix in this project so far.

## Follow-up (same day): added the 22 directly-observed addresses to `play.ps1`; mechanical re-verification was inconclusive, not negative

Added all 22 directly-observed addresses (19 `RoomLib_HandlerB` + 3
`RoomLib_HandlerC`) to `build/play.ps1`'s `$ForceInterior` default.
Attempted to mechanically confirm the fix works the same way
`roomlib-0x80191200-interior.md` did — re-running `compile_overlays.py
--check` with `--force-interior` set for these addresses and looking for
the `"; isolated fragment demand retained"` success marker
`classifier_gap_finder.py`'s own `parse_check_log` already knows to look
for.

**Result: inconclusive, not negative.** None of the 22 new addresses showed
the `retained` marker on a second `--check` pass against this same
capture — but neither did 23 of the 24 already-proven-working addresses
already in `play.ps1` (only `0x80191B94` showed `retained`; the rest were
completely absent from the transcript, not even listed as excluded). Ruled
out two mundane explanations directly rather than assuming: not a
PowerShell cross-process argument-passing bug (retried with proper
`@()`-array splatting instead of a `cmd /c` string, same result), and not
an interaction with `--only-region` (retried against the full unrestricted
capture, same result).

Since the SAME capture can't even re-confirm most of its own already-shipped
fixes on a second pass, this points at the capture itself being too narrow
for this kind of re-verification (`Captures: 4 overlay(s) to process` at
the top of every run from this file — a short session, not a full
playthrough) rather than anything specific to `RoomLib_HandlerB`/`HandlerC`.
**The 22 addresses are still real** — they're the exact addresses this
document's own cross-reference against the FIRST, unforced `--check` run
found as genuinely excluded `OBSERVED_PC_ONLY` hits from actual gameplay.
What's unconfirmed is specifically whether `--force-interior` successfully
carves them into compiled fragments, which this particular capture can't
settle either way.

`play.ps1` keeps the 22 addresses, with a comment stating plainly that
they're not yet live-verified — matching how this file has handled a
"found but not yet confirmed" entry before (its 2026-09-13 FMV additions
carried the same kind of caveat until a real play session confirmed them).
**The reliable next step is what confirmed every entry already in this
list**: an actual live launch, play through content that exercises
`RoomLib_HandlerB`/`RoomLib_HandlerC`, and a real dirty-RAM before/after —
not a second offline `--check` pass against a capture too narrow to
re-prove its own already-shipped fixes.
