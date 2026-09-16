# Prototyping a fix for `0x0010C89C`: the caching hypothesis is confirmed real, the naive implementation is unsafe

**Date: 2026-09-16. Status: real positive finding (inputs genuinely repeat,
caching is viable) plus a real negative finding (the specific "skip the
whole function" implementation breaks execution) — not a working fix yet,
and the live build was left exactly as it started.**

## Why this was attempted

`fmv-frame-stall.md`'s 2026-09-16 follow-up re-confirmed `0x0010C89C` (a
per-entity Huffman/RLE decompress call in the rotating intro) is still a
real, live cost in the actual `build-release` a player runs — 6.5-27ms per
call, every ~4th frame, unaddressed by the PGO+LTO fix already shipped.
That doc's own "not yet done" list named two possible fixes: pre-decompress
off the hot thread, or cache decoded output across the intro's repeat
cycles if the same entities recur. This is an attempt at the second,
cheaper option.

## Step 1: confirm the repeat hypothesis before writing any fix code

Added temporary, self-contained instrumentation directly to the function's
generated overlay source (same `fprintf`/`stderr` pattern as this
function's own prior `PE_PROBE` instrumentation from the original
2026-09-12 investigation) at `block_8010C89C:`, logging `$a0`-`$a3`
(`cpu->gpr[4..7]`) on every call. Compiled manually with
`compile_overlays.py`'s exact `_compile_dll_direct()` flags and the
matching `overlay_pair_id()` export (same documented workaround the
original investigation used to avoid the loader's publish-atomicity
rejection), swapped into the live cache slot
(`build-release\cache\SLUS-00662\gcc\win-x64\cg10_5d7c70a8_gcc15c8ed0_f0\
0010B000_7238DF29.dll`), launched with `-NoAutocompile` so the pipeline
couldn't regenerate over the edit mid-test.

**One real gotcha caught immediately**: `_compile_dll_direct()`
unconditionally passes `-DPSX_NO_DEBUG_TOOLS` for every overlay build,
regardless of the runtime EXE's own debug-tools setting ("the shipped/
native runtime is built without debug tools, so define it here too or the
overlay emits calls to symbols the runtime doesn't have" — `compile_
overlays.py:4161-4165`). The first instrumentation draft was wrapped in
`#ifndef PSX_NO_DEBUG_TOOLS` and would have silently never executed in a
compiled overlay. Moved it outside that guard before testing.

**Result — the repeat pattern is real and exactly matches the
double-buffer theory already on record**: `$a1` (output cursor) strictly
alternates between two fixed addresses (`0x80132700`/`0x80122D00`) every
single call, and `$a0` (input pointer) cycles through a set of ~7 distinct
values with a period of 7 calls — meaning the exact `(a0, a1)` pair only
repeats every 14 calls (`lcm(7,2)`), not every 7. Confirmed directly:
`a0=0x80142900` recurred at calls 1, 8, and 15, but only calls 1 and 15
share the same `a1` too (call 8 has the opposite buffer phase). `$a2`
(the shared Huffman/lookup table base) stayed constant at `0x80162100`
across every single call, exactly as previously characterized.

## Step 2: the fix — cache-and-skip on an exact `(a0, a1)` repeat

Since nothing else writes to this function's own double-buffer between
calls, a repeat of the exact same `(a0, a1)` pair means the destination
buffer still holds the correct decompressed bytes from the prior call —
in principle, the whole ~200-instruction decode loop can be skipped and
the function can return immediately, with no data to copy at all (the
buffer already has the right content sitting in it from last time).

Implementation: a small fixed-size (16-entry) ring-buffer cache of
`(a0, a1)` pairs, checked at function entry (`block_8010C89C:`); on a hit,
`return;` immediately; on a miss, record the pair and fall through to the
existing (unmodified, guaranteed-correct) decompression logic. No changes
to the decompression algorithm itself — only a bypass around it.

## Result: the cache mechanism itself works correctly, but "return" isn't safe here

Both test launches deterministically reproduced calls 1-15 in the *exact*
same order and register values every time (this section of the intro is
fully deterministic), producing exactly one clean cache hit at call 15
(`a0=0x80142900, a1=0x80132700`, matching call 1) — proof the caching
logic itself is correct and finds the repeat exactly where the probe data
said it would.

**But immediately after that hit, both runs hit `psxrecomp runtime:
execution completed, PC=0x00000000`** — the whole process cleanly exited,
every single time, right after the skipped call. A control test with the
byte-identical *original*, unpatched DLL under the exact same
`-NoAutocompile` launch conditions ran past 1900+ frames with no exit —
ruling out `-NoAutocompile` or anything else as the cause. **The early
`return;` on a cache hit is what breaks it.**

**Most likely mechanism (not yet confirmed by reading generated code
further)**: `return;` at `block_8010C89C:` skips whatever cycle-accounting
and/or dispatch-continuation bookkeeping the real decompression loop's own
blocks perform before reaching one of the function's two real `jr $ra`
exit points (`0x8010CBC0`/`0x8010CBF4`, per the original 2026-09-12
disassembly). This project's own `PSX_ENABLE_BLOCK_CYCLES` cycle-model-
unification requirement (`compile_overlays.py:4166-4173`) exists
specifically because native and interpreted code paths must charge
*identical* cycles for the same guest code — skipping a whole function's
worth of per-block cycle charging is exactly the kind of thing that model
depends on, and the caller (`0x80192934`) or something reading `cpu->pc`/
`cpu->gpr[31]` shortly after is the likely victim.

## What this means

**The underlying idea is sound and validated with real data** — the same
entities genuinely recur, caching genuinely applies, and a cache lookup
adds negligible cost of its own. **The specific implementation attempted
(bare early return) is not safe** and would need either: replaying the
correct cycle-accounting for a "virtual" run of the skipped work (defeating
much of the point), or actually copying the cached output bytes into the
destination buffer via a fixed-size `memcpy` (avoiding early-return
entirely, so all of the function's own exit-path bookkeeping still runs
normally) once the exact output byte count per call is known — which
requires instrumenting the function's *exit* points, not just its entry,
to measure `$a1`'s final position. Not attempted this round.

## Cleanup — verified, not just asserted

The live cache DLL was restored from a byte-for-byte backup and confirmed
identical via SHA-256 hash before and after
(`05E662A86CCDAB155640F7486D663024A69850E5D31D1DFA7CA600E690F49BBD`) — not
just "should be fine." All temporary artifacts (`_patched.c`, the two test
DLLs, the backup) were deleted afterward, leaving only the original
`.dll`/`.ranges`/`.pair-lock` triad untouched. A final normal launch
(no `-NoAutocompile`) ran cleanly past 1900 frames at a healthy ~60fps
with zero errors, confirming the project is back to exactly its
pre-experiment working state.

## Suggested next step

Instrument the function's two real exit points
(`0x8010CBC0`/`0x8010CBF4`) to capture `$a1`'s value at return (giving the
exact byte count written per call), then re-attempt the fix as a
`memcpy`-based cache that always lets the function run its normal control
flow to completion — populating the cache on a miss, and on a hit,
replacing only the decompression loop's *body* (not the whole function)
with a copy from the cache, so every block's cycle-accounting and exit
path still executes exactly as it does today.
