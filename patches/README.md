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

## What's *not* here: the clang `dllexport` fix

`findings/framework-findings.md` finding #1 proposes a `PSX_OVERLAY_EXPORT`
macro to fix the bundled clang toolchain's hard "cannot add 'dllexport'
attribute" error on every overlay shard. That fix is **not included as a
patch** — we worked around it by using real GCC instead of patching
psxrecomp directly, so the macro fix has only been reasoned through, never
compiled and verified against clang. Treat the candidate fix in the finding
as a starting point for whoever picks it up, not a tested patch.
