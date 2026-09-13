# Making the case: are the PGO/LTO config changes actually framework-agnostic?

Written for Alex and mstan, directly answering the question behind mstan's
stated rule: *"If the fixes are agnostic, we just need to test it against a
handful of potentially impacted games, and if they are ok, I'm ok to merge.
But if it's game specific, it should live in the game repo."*

Companion to `fmv-60fps-alex-briefing.md` (the original findings) and
`fork-divergence-merge-strategy.md`. This document does one narrower thing:
walk through exactly what the two build-configuration changes behind our
FMV win actually are, make the case for why they're structurally agnostic
rather than Parasite-Eve-specific, and — just as important — lay out
mstan's own stated concerns plainly rather than talk around them, since
several of them are fair and still open.

## What the two changes actually are

Of the four things that got Parasite Eve's FMV to a steady ~58-61fps, only
two are ours and not already in mstan's tree (see `fmv-60fps-alex-briefing.md`
section 2-3 for the other two, WO-6 and RoomLib, both already his). The two
in question:

**PGO training window**: `psxrecomp_cli.py pgo-train --train-secs 100
--train-runs 1` instead of the tool's own default (`train_secs=60,
train_runs=2`). One command-line parameter to an existing, already-shipped
tool. No source file changed.

**Project-wide LTO**: `-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON` passed to the
existing `cmake -S . -B build-release` configure step. One flag. No
`CMakeLists.txt` edit — modern CMake applies it as a global target default
with zero code changes.

That's the entire diff. Neither one touches `psxrecomp`'s recompiler,
runtime source, or code generator. Neither one is a patch, a new flag added
to the codebase, or a new function — they're both invocations of
infrastructure mstan's team already built and ships (the PGO pipeline
predates this investigation; the CMake IPO property is a standard CMake
feature, not something either of us added).

## Why that makes them structurally agnostic

Three separate reasons, stacked:

1. **Neither setting can see Parasite Eve at all.** `-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`
   is a link-time instruction to the compiler toolchain: "cross-translation-unit
   inline and optimize the object files you're given." It has no concept of
   which game those object files came from. The PGO training window is
   almost the same story — it's a duration and iteration count fed to a boot
   loop; it doesn't know or care what game.toml points at.
2. **The mechanism they exploit is generic, not PE-specific.** PGO helps any
   title whose default training window doesn't happen to reach its own
   heaviest, longest-running content before the profile is captured — that's
   a property of *how the tool is invoked*, not of Parasite Eve's assets.
   LTO's cross-translation-unit inlining and dead-code elimination benefits
   scale with how large and cross-referential the linked unit is (the "whole
   runtime and `recomp-ui`" scope mstan's own IPO doc already names as
   exactly the shape of codebase LTO helps most) — again a property of the
   framework's build shape, not this game's code.
3. **We already have a natural comparison inside the same review thread.**
   Mstan's own PR #356 is the scoped, opt-in version of the same LTO idea
   (`PSX_RUNTIME_IPO`), built and merged as framework infrastructure with no
   game-specific carve-out. If the underlying mechanism were somehow PE-only,
   that framing wouldn't make sense as something his own team chose to build
   as a general option in the first place.

None of this proves the *result* generalizes — only that the *mechanism*
does. That distinction is the entire point of mstan's rule, and it's why the
next section matters more than this one.

## Mstan's concerns, stated plainly (not glossed over)

These are real, and some of them aren't fully answered yet. In his own
team's words, from the IPO experiment doc merged alongside PR #356:

> "This establishes a reasonable correctness baseline for merging the
> experimental option while it remains OFF by default. It does not
> establish a performance win... The PE gain has not been independently
> reproduced."

Breaking down what's actually being asked for, from that same document's
own "evidence needed" list — and being honest about which of these we have
and which we don't:

| What mstan's team says is needed | Do we have it? |
|---|---|
| Repeated, content-aligned LTO off/on trials with the *same* PGO profile, compiler, debug flags, assets, input and cache state | **Partially.** We have repeated matched trials for LTO-on (twice) but never isolated LTO's own contribution from the PGO retrain's — every LTO measurement we have is "PGO-retrain + LTO together." |
| Per-frame tails/maxima and audio underruns, not just periodic average fps | **No.** All our numbers are fps-counter readings at matched content positions, not full per-frame distributions. A real regression in the tail (occasional stutter) could hide inside an average that still looks good. |
| Regenerated title regression across multiple titles (their standard: Tomba, MMX6, Ape Escape — LLE boot, FMV, menus, gameplay) | **No — this is the actual ask.** We only have Parasite Eve. We don't have the other titles' assets or a local checkout set up to test them. |
| Shipping-compiler/platform coverage, binary size, build/link time, peak memory | **No.** We measured fps only; never checked what LTO costs in build time, link time, or binary size, which their own doc explicitly flags as a real cost worth recording. |
| Exact profile/capture identities and raw measurements, not summarized claims | **Partially.** We have the raw fps numbers and can supply the exact commands/config, but haven't packaged profile-identity metadata (codegen hash, `.gcda` identity) the way their own validation report does. |

Separately, and specifically about the PGO-training-window claim: their team
disputes our earlier "the pipeline silently stops at the generate phase"
framing, pending a concrete failing command, revision, and exit-code record
— and they're right to hold that line rather than accept a described-but-
unreproduced pipeline bug. That dispute is orthogonal to the `train_secs`
finding itself (which is just "the default window is short," not "the tool
is broken"), but it's worth keeping the two claims clearly separated so one
doesn't cast doubt on the other by association.

**The honest summary of where this leaves us**: the *mechanism* case for
agnosticism is solid. The *evidence* case — the actual cross-title numbers
mstan's rule requires before merging anything — isn't done. We're bringing
a plausible, twice-measured, single-title result; his bar is explicitly a
multi-title one, and that bar is the right one given what a wrong default
would cost every other game on the framework.

## What would actually close the gap

A concrete proposal, scoped to what's realistically testable from each side:

**From us**: package the exact reproduction recipe — precise commands,
matched savestate/content positions, the codegen-hash/profile identity of
the build we measured — so anyone can rerun it without guessing at what we
did. This is the thing we can do without needing assets we don't have.

**From mstan's team, if there's appetite**: run the same recipe against
Tomba/MMX6/Ape Escape using the harness that already exists for #354's
validation — cold + warm frame counts, screenshot inspection, and ideally
the per-frame tail/audio data their own doc calls for, not just an average.
Two configurations worth testing side by side rather than assuming ours is
the right shape: our blanket `CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON` versus
their already-merged, narrower `PSX_RUNTIME_IPO=ON` — if the *scoped* flag
gets the same win, that's the safer default to standardize on, since it
deliberately excludes third-party/vendored code and Debug builds that a
blanket setting does not.

**Also worth doing regardless of the above**: isolate LTO's own contribution
from the PGO retrain's, since right now "PGO-retrain + LTO together" is the
only number we have and it likely overstates what LTO alone is worth.

None of this is a demand — it's an attempt to hand mstan's team something
that's already halfway to meeting their own stated bar, rather than asking
them to take a single-title result on faith.
