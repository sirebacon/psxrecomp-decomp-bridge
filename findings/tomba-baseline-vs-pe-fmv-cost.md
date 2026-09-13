# Tomba's FMV runs clean at baseline — a hypothesis worth revisiting before calling our fix agnostic

Captured 2026-09-13 while setting up a Tomba cross-title checkout to test the
PGO-retrain/LTO changes from `fmv-60fps-alex-briefing.md`. Parking this here
because it surfaced mid-setup, before the actual A/B test was run — a
hypothesis to confirm or kill later, not a finished finding yet.

## What was observed

Fresh `mstan/tombarecomp` checkout, plain baseline build (no PGO, no LTO,
`PSX_DEBUG_TOOLS=OFF` — the tool's own defaults, nothing changed). Two runs,
window-title FPS telemetry (`PSX_FPS_TELEMETRY=1`), polled once per second:

- **Cold run** (first-ever launch, empty overlay cache): steady 59-61fps for
  ~40 seconds, then a real dip — **55 → 46 → 56fps** around the 41-44s mark,
  recovered to 60fps by ~46s.
- **Warm run** (second launch, cache now populated), timed from the moment
  the user pressed Play through to the reported end of whatever played:
  **~119+ seconds at a flawless 59-61fps, no dip anywhere**, including
  through the exact content position where the cold run had stalled.

Cold-dip-that-disappears-on-warm is the same signature as PE's own
overlay-DLL-compile-on-first-use effect — not evidence of a genuine
content-driven cost. On a warm cache, Tomba's own intro sequence (whatever
exactly played in that window — not confirmed frame-by-frame, no debug
tools/screenshot capability on this build) shows **no fps cost at all**,
with zero build-configuration changes applied.

## The hypothesis this raises

Parasite Eve's WO-8 bottleneck (`fmv-frame-stall.md`, `fmv-decompress-stall-
ai-brief.md`) is not a generic FMV/MDEC decode cost. It's a specific,
data-dependent Huffman/RLE decompress function called by the same function
that also calls `RoomLib_InitC` — Parasite Eve's own per-room asset-loading
subsystem. The likely read: PE's engine does real background work (per-room
data decompression) *during* its intro FMV, and that background work is what
the PGO retrain + LTO combination actually helps with — not the video
codec itself, which was never the bottleneck.

Tomba, by contrast, has a structurally simpler room/asset model. If its own
intro sequence doesn't trigger an equivalent background decompression pass,
there's nothing analogous to WO-8 for it to hit — which would explain a
clean 60fps baseline with zero optimization applied.

## Why this matters for the agnostic-fix argument

This directly qualifies the case made in `fmv-pgo-lto-agnostic-case.md`. If
Tomba has no equivalent hot path, then testing our PGO/LTO changes against it
may show **no measurable effect either way** — which would not be evidence
the fix is broken, but it would be evidence that **the fix's benefit is
conditional on a game having PE's specific kind of bottleneck**, not proof of
universal framework-level benefit. That's a materially different claim than
"agnostic," and it's exactly the kind of gap mstan's own evidence bar is
designed to catch. Worth stating plainly to Alex/mstan when we report the
actual Tomba A/B result, whichever way it comes out — a null result here
should be reported as a null result, not buried.

## What would confirm or kill this, not yet done

- **Direct instrometation, not fps-counter inference.** Everything above is
  circumstantial — a cold/warm fps comparison, no frame-level or dispatch-
  level timing. To actually know whether Tomba has an equivalent
  data-dependent decompress hot path, it needs the same treatment WO-8 got:
  `latency_ring` dispatch-duration timing on Tomba's own overlay-resident
  code during its intro sequence, which requires rebuilding with
  `PSX_DEBUG_TOOLS=ON`.
- **Confirm what actually played** during the measured window — no
  screenshot/`present_shot` capability was available on this baseline build,
  so "the FMV" is inferred from the user's report, not confirmed frame-by-
  frame the way PE's investigation always insisted on.
- **Run the actual PGO-retrain + LTO test on this Tomba checkout anyway**,
  even expecting a possible null result — that comparison is still the real
  cross-title evidence mstan's team asked for, and a clean null here is
  useful data, not a wasted test.

## Where things stand

Tomba checkout: `D:\Recomp Games\Tomba Project\tombarecomp`, plain baseline
build in `build-release`, confirmed booting and playable. No PGO/LTO test
run against it yet — this hypothesis surfaced during baseline setup, before
that test started. Picking this back up means: rebuild with debug tools to
check for an equivalent hot path, then run the actual A/B regardless of what
that check finds.
