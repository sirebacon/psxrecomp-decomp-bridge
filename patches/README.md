# Patches against psxrecomp

These are diffs against `Alexbeav/psxrecomp` / `mstan/psxrecomp`, licensed
**PolyForm Noncommercial 1.0.0** upstream — which explicitly permits
modification and redistribution for noncommercial purposes, so publishing
diffs here (for a noncommercial hobby/preservation project) is exactly the
use that license anticipates. Applying one of these to your own checkout
puts you under the same terms as the code you're patching.

Apply with `git apply patches/<file>.patch` from your psxrecomp checkout
root, or `patch -p1 < patches/<file>.patch`.

## `01-compile-overlays-fromfile-prefix.patch`

**Verified working** — this is the actual `git diff` from a checkout that's
been running with it for weeks. Adds `fromfile_prefix_chars='@'` to
`compile_overlays.py`'s argument parser so a curated `--force-interior`
address list can be passed as `@somefile.args` instead of repeating
`--force-interior 0x...` hundreds of times on one command line. Pure
ergonomics — doesn't change what gets compiled.

## `02-pgo-train-clean-exit.patch` — fixed upstream, not by us

**Landed in `RetroPortingToolKit/psxrecomp` PR #345** (2026-09-11), same day
as this patch. No patch needed here for it anymore; kept for the record.

**Verified working** — see `findings/pgo-train-fix.md` for the full writeup.
Fixes PGO *training* on Windows: `rebuild --force-pgo` crashed with
`[WinError 5] Access is denied` in the process-stop code (not the launch),
and even a run that didn't crash produced a 0-byte `.profraw`, because a hard
`TerminateProcess` (all a "SIGTERM" can be on Windows) never reaches LLVM's
`atexit`-registered profile writer. Fix asks the runtime's debug server for a
clean `exit(0)` instead. Tested end to end: real 6.1MB `.profraw` files, a
1MB merged `default.profdata`, full instrument→train→optimize cycle
completing.

This one is against `2113defc` — i.e. **on top of** PR #344 ("Fix overlay
Clang exports, PGO, and scaffold cache"), which fixed PGO's compile-time
plumbing but didn't touch training.

## Finding #1 (clang `dllexport`) — fixed upstream, not by us

The `PSX_OVERLAY_EXPORT` macro fix for finding #1 in
`findings/framework-findings.md` landed in mainline via PR #344, and per its
description was tested there — we never patched or verified it ourselves
(we'd worked around it with real GCC instead). No patch needed here for it
anymore.
