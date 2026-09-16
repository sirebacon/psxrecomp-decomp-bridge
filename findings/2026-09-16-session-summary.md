# Session summary, 2026-09-16: from "can the func_override toolkit fix dirty RAM" to a real, confirmed bug fix

This ties together a full day's investigation, spread across five separate
findings documents. Read this first for the shape of the day; follow the
links below for the detail behind any one claim.

## The question that started the day

Could the func_override toolkit built earlier this session
(`postman.py`/`confidence.py`/`generator.py`/`triage.py` — invoke, verify,
and replace guest functions with native decomp C) be used to help solve
this project's persistent dirty-RAM/interpreter-performance problem on
low-powered hardware?

**Answer: no, not directly — and the investigation needed to prove that
before it could find what actually does help.**

## Part 1: why func_override can't reach RoomLib's dispatchers

→ `func_override-toolkit-pipeline-run-2026-09-16.md` (+ 4 follow-ups)

Ran the full toolkit against the real, currently-live 211-address
`--force-interior` list. Headline (`0 eligible`) looked like a null result
but wasn't: **91% of the list are interior jump-table offsets inside 22
shared dispatcher functions**, not whole stuck functions — the toolkit was
built for "replace one confidently-verified function," and this project's
actual bottleneck is "a shared dispatcher's internal case-table gets stuck
in the interpreter," a different shape of problem entirely.

Chasing whether the *whole* dispatchers could be replaced instead led to:
- Discovering and resolving two real shared-library code shapes in this
  decomp (a thin `#include "X.inc"` wrapper, and a macro invocation) that
  `confidence.py` now understands — a genuine, reusable improvement.
- Reading `RoomLib_HandlerD.inc` in full and confirming it pins raw MIPS
  registers, uses inline-asm barriers, and drives GTE hardware directly on
  top of heavy pointer arithmetic — not a narrow gap from being
  scalar-only, but structurally incompatible with a register-marshaling
  replacement shim. Every other RoomLib dispatcher checked is built the
  same way.
- **Conclusion, checked and closed**: `confidence.py`/`generator.py` will
  never be able to replace RoomLib's dispatchers. This is real, useful,
  negative information — it stopped further investment in the wrong tool.

## Part 2: the tool that actually helps — found by acting on that conclusion

→ `scan-shared-libs-auto-discovery-2026-09-16.md`

Built `classifier_gap_finder.py scan-shared-libs`: instead of replacing a
dispatcher, find every shared macro/`.inc` template shaped like the
*already known* root cause of this project's RoomLib jump-table classifier
bug (a `switch` statement in shared code → a MIPS jump table → classifier
can't recognize the case targets), with **zero prior knowledge required**.

**Validated by blind rediscovery, not by fitting a known answer**: run
without being told which macro was already confirmed bad, it correctly
surfaced `ROOMLIB_STATE_DISPATCH_VARIANT2` — the exact macro this project
spent real investigation nights isolating by hand weeks ago. Alongside it:
**18 previously-uncatalogued at-risk templates, 264 candidate addresses**
across the whole RoomLib system that had never been looked at before today.

## Part 3: confirming two of those candidates against real gameplay data

→ `roomlib-handlerb-handlerc-confirmed-2026-09-16.md`

Ran `compile_overlays.py --check` against this checkout's own real
`overlay_captures.json` (genuine recent gameplay, not synthetic) and
cross-referenced all 719 real excluded addresses against the 264
candidates. Result: `ROOMLIB_STATE_DISPATCH_VARIANT2` re-confirmed (a
sanity check), plus **two genuinely new classifier gaps** —
`RoomLib_HandlerB` (4 live instances, confirmed offsets) and
`RoomLib_HandlerC` (1 instance) — neither ever on any force-interior list
before this day. Computed the full candidate list for the confirmed one:
125 files, 1,500 candidate addresses, the same scale as the original fix.

## Part 4: live verification — one confirmed fix, one open question

→ `live-verification-attempt-2026-09-16.md`

Added the 22 directly-observed addresses to `build/play.ps1` and tried to
verify the fix live. First discovery: the game's autocompile system was
**degraded** — the exact `autocompile.c` 4096-byte command-buffer overflow
bug this session fixed earlier had recurred, because that fix lived on a
different branch never merged into the plain pin this checkout actually
runs, and the 22 new addresses pushed the command past the buffer again.

**Fixed live, rebuilt, confirmed immediately**: `interp_share` dropped to
3.15%, matching this project's own long-documented healthy baseline
exactly. This is a real, separately-committed fix
(`pe-local-work-old-pin-autocompile-buffer-fix` in the `psxrecomp`
submodule), independent of whether `RoomLib_HandlerB`/`HandlerC` pan out.

The original question — does `RoomLib_HandlerB`/`HandlerC` actually compile
natively during real play — is **still open**, for a mundane reason: ~2
minutes of live capture and synthetic button presses never navigated past
an extended intro sequence to reach a relevant room. Not a negative result,
a navigation limitation. Along the way, a **new, unclaimed hot spot**
(`0x0018F468`, sustained ~256K instructions per dispatch entry) turned up
for free — the same signature every confirmed fix in this project's
history started from, not yet investigated.

## Where things stand

**Confirmed and shipped today:**
- `RoomLib_HandlerB`/`HandlerC` identified as real classifier gaps, added
  to `play.ps1` (marked not-yet-live-verified).
- The `autocompile.c` buffer bug fixed a second time, on the pin that
  actually needed it.
- Two reusable tool improvements: `confidence.py`'s shared-library
  resolution, `classifier_gap_finder.py scan-shared-libs`.

**Still open, in priority order:**
1. Get a human to actually play to a room using `RoomLib_HandlerB`/
   `HandlerC` while `stall_report.py` watches — the only reliable way left
   to close Part 4's open question.
2. Investigate `0x0018F468` — same profile as every previously-confirmed
   fix, currently unclaimed.
3. Propose the `autocompile.c` fix upstream — it has now recurred once
   independently; it will keep recurring on every pin as force-interior
   lists grow.
4. Work through the remaining 17 at-risk templates `scan-shared-libs`
   found but nobody has checked against a real capture yet.
