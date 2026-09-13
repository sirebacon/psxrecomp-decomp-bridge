# FMV performance: where our fix and mstan's independent review actually land

Written for Alex. Purpose: put our measured FMV performance fix and
RetroPortingToolKit's (mstan's team) independent review of the same
investigation side by side, honestly, including the one gap neither side has
closed — and ask you to weigh in on it, since any real fix here changes the
build for every title on `psxrecomp`, not just Parasite Eve.

Companion document: `fork-divergence-merge-strategy.md` — a separate,
practical problem hit today while pulling mstan's fixes into this fork, worth
reading alongside this one since it affects how anything below actually gets
adopted.

## TL;DR

- We found a real, reproducible FMV performance win: **retraining PGO with an
  FMV-inclusive window, plus project-wide LTO, took the boot-intro FMV from
  ~52-54fps to ~58-61fps** on this machine.
- mstan's team reviewed the same investigation thread independently. They
  merged the one clear correctness bug we'd also found ourselves (a CFG
  builder defect), and left the performance-adjacent work as **drafts,
  explicitly stating the PE gain "has not been independently reproduced."**
- Digging into *why* it hasn't been reproduced turned up something more
  interesting than a disagreement: **the actual FMV decode hot path lives in
  a dynamically-compiled overlay DLL that neither our LTO/PGO setup nor
  mstan's scoped IPO option ever touches.** Both optimization paths bypass
  `compile_overlays.py`'s separate `gcc -shared -O2` build entirely. So our
  measured win is real, but **we cannot currently explain what it's actually
  optimizing** — which is exactly the kind of gap that should be closed
  before anyone recommends this as a default.
- The ask: read the "the load-bearing gap" section below and tell us what you
  think is worth trying — extending compile_overlays.py's build to carry
  profile/IPO flags, something else on the runtime side, or a different
  attribution experiment to run before touching that path at all.

## 1. Where this started

Investigation thread: `fmv-frame-stall-plan.md` → `fmv-frame-stall.md` (WO-8,
the root cause) → `fmv-decompress-stall-ai-brief.md` (WO-8/WO-9 writeup) →
`fmv-cps-overhead-ai-brief.md` (WO-10) → `fmv-irq-batch-prototype-ai-brief.md`
(WO-11 and everything after it, including the win below).

**Root cause (WO-8, proven not guessed)**: `0x0010C89C`, a ~200-instruction,
data-dependent Huffman/RLE-shaped decompress function, occasionally costs
20-67ms per call during FMV. A temporary iteration counter added to the
function's own generated source showed iteration count correlates with call
duration at Pearson r=0.69 / Spearman r=0.73 across 324 real calls — direct
evidence, not inference. Its caller is the same function that also calls
`RoomLib_InitC`, tying this to the earlier RoomLib/WO-6 dispatch-overhead work.

**Structurally important**: this address does **not** exist in the
statically-compiled main-EXE C shards (`generated/SLUS_006.62_full_53.c`/
`_54.c` show it as `/* nop */` at generation time) despite living in main-EXE
address range (`0x0010xxxx`). It's dynamically captured and compiled through
the ordinary overlay pipeline — actual source lives at
`build-release/cache/SLUS-00662/gcc/win-x64/cg10_022d09e7_gcc15c8ed0_f0/
7238DF29_patched.c`, compiled to `0010B000_7238DF29.dll`. This detail turns
out to matter a lot — see section 4.

## 2. What we shipped locally and measured

Two independent changes, tested separately and together:

**PGO retrain, FMV-inclusive window.** `psxrecomp_cli.py pgo-train` defaults
to `train_secs=60, train_runs=2` from a cold, deterministic, no-input boot —
this window likely never reaches sustained FMV content, so the profile never
saw `0x0010C89C`'s own hot loop. Retrained with `train_secs=100,
train_runs=1`. Measured twice independently at matched frame-count positions
against the established baseline: **~58-60fps vs. ~52-54fps at the same
content position** — reproduced across two separate cold-boot launches.

**Project-wide LTO** (`-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`, zero
`CMakeLists.txt` changes needed — modern CMake applies it as a global target
default), stacked on top of the retrained profile. Two runs: 59.1-60.9fps and
58.7-61.4fps, with a sustained band of 58.5-61.4fps for the entire remainder
of the FMV once warmed up. **Not isolated from the PGO retrain** — this is
"PGO-retrain + LTO together," not a clean measurement of LTO's own
contribution. Don't cite an "LTO added exactly N fps" number from this.

**A false alarm, corrected.** An earlier round (`fmv-irq-batch-prototype-ai-
brief.md` Follow-up 4) concluded LTO caused a severe performance collapse
plus visual corruption when playing past FMV into a New Game. A matched
retest (same savestates, same transition, both configs timed back-to-back —
Follow-up 5) found **no LTO-specific performance effect at all** (+15 vs. +7
overlay revalidation attempts, both a clean 60fps). The original claim was
confounded by comparing sessions with different amounts of accumulated
overlay state, not a real LTO effect. The visual corruption is real, but has
its own, LTO-independent root cause — see `savestate-restore-lazy-
revalidation-race.md`. We corrected this across every document that had
cited it as soon as the retest disproved it.

**Current standing local config**: PGO=use (FMV-inclusive profile), LTO on,
debug tools off. This is a build-configuration change only — no recompiler
codegen changes are involved in this specific win (the WO-10/WO-11
IRQ-batching codegen prototype, tested separately, showed a null result — see
section 3).

## 3. What mstan's team found, independently

Full source: `fmv-followups-pr-handoff.md` (their handoff to us) plus direct
inspection of `RetroPortingToolKit/psxrecomp@master` after the fact — they
kept working after writing that handoff, and two more things landed than the
handoff describes. Baseline reviewed: `3a275d49397b`. Current master as of
this writing: `0690e5c1` (via the `rtk` remote).

**Merged, and directly relevant to our own investigation — PR #354.** We
independently found and worked around the same bug: the CFG builder
populated `BasicBlock::successors` but never populated `predecessors`, and
classified any backward-address edge as a loop even on an acyclic graph. We
worked around it locally with a hand-rolled `compute_predecessors()` (derive
predecessors from every block's successors) to get our own IRQ-batching
prototype's block classification working at all. mstan's team found the same
underlying defect and fixed it properly — `rebuild_control_flow_metadata()`:
unique reverse edges, declared-entry reachability, and dominance-proven
natural back edges via an iterative DFS + reverse-postorder immediate-
dominator fixed point. Validated against 1,000 randomized CFGs checked
against an *independent* dominance oracle (not another copy of the same
algorithm), a 12,000-block chain test, and 67 CTests total. We cherry-picked
this into our fork today (see the companion document) — it builds clean and
regenerates every one of PE's 4,378 functions byte-identical, so it's now in
effect locally with zero behavioral risk.

**Merged, but inert by design — PR #356 (IPO/LTO).** `PSX_RUNTIME_IPO`
defaults OFF, and even ON it only opts in specific runtime-target
configurations (Release/RelWithDebInfo/MinSizeRel) — not third-party
libraries, not Debug, and **not independently-compiled overlay DLLs**. This
is explicitly narrower than our project-wide
`CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`. Their own review ran 11,000+ frames
each on Tomba/MMX6/Ape Escape with IPO on and confirmed nothing broke — no
FMV-specific measurement, no Parasite Eve. Direct quote from their merged
doc: *"This establishes a reasonable correctness baseline for merging the
experimental option while it remains OFF by default. It does not establish a
performance win... The PE gain has not been independently reproduced."*

**Merged, but zero code — PR #357 (IRQ-batching RFC).** Direct quote:
*"Status: design review only. No IRQ batching implementation or runtime flag
is added."* This is the same territory as our own WO-10/WO-11 investigation
(section-by-section below), formalized as an accepted design document, not a
shippable change.

**Their disposition of each of our specific findings:**

| Finding | Our framing | Their disposition |
|---|---|---|
| WO-8 (decompress cost) | Root-caused via dispatch-duration timing, r=0.69-0.73 | Retained as a lead, but a fair critique: our timing "cannot distinguish guest decode from callback overhead" — we measured the whole call, not the two components separately |
| WO-9 (pair-id rejection) | Framed as a dev-tooling gap worth improving | Confirmed correct behavior, not a bug. Diagnostic history is optional, not a correctness fix |
| WO-10 (callback overhead) | Plausible, explicitly unquantified in our own writeup | Same: "plausible cost, unquantified here" |
| WO-11 (CFG bug found while prototyping) | Worked around locally | Confirmed and fixed properly upstream — PR #354, above |
| WO-11 (IRQ-batching prototype itself) | Implemented, honestly reported as a null result | Independently reinforced: their PR #357 built a real-cache counterexample proving the underlying elision pattern **changes guest-visible state** (14 vs. 7 cycles, load give-back 0 vs. 99, a valid vs. invalid cache tag) when a cold interior-block fetch check is skipped. **Our own prototype's `emit_pre_icache` skip is exactly this pattern** — still gated behind `PSX_IRQ_BATCH_LOOP`/`_CHAIN` env vars, default off, but this is now a confirmed risk if ever enabled, not a hypothetical one. |
| PGO "pipeline stops at generate phase" | Reported as a reproduced pipeline quirk | Disputed pending a concrete failing command/revision/exit-code record from us — we have this evidence from our own testing and haven't sent it over yet |

## 4. The load-bearing gap neither side has closed

This is the part worth your attention most.

mstan's own merged IPO documentation contains this warning, written before
either of us connected it to WO-8 specifically:

> `compile_overlays.py` launches a separate `-shared -O2` compiler command
> with neither profile flags nor IPO. They do not directly profile/optimize
> PE's dynamic decoder DLL. Gains may come from linked code or callbacks,
> which must be measured.

We checked. It's exactly true, and exactly describes our own measured win.
`_compile_dll_direct()` in `tools/compile_overlays.py` invokes:

```
gcc -shared -O2 -DPSX_OVERLAY_DLL_BUILD -DPSX_NO_DEBUG_TOOLS
    -DPSX_ENABLE_BLOCK_CYCLES=1 -DPSX_OVERLAY_FLAVOR=0 ...
```

No `-flto`, no `-fprofile-use`/`-fprofile-generate`, nothing PGO- or
IPO-related at all, regardless of what the main runtime build is configured
with. And `0x0010C89C` — the actual WO-8 decode hot path we root-caused —
**lives in an overlay DLL compiled through exactly this path**, not in the
statically-linked main-EXE/runtime that our `CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`
and mstan's `PSX_RUNTIME_IPO` both apply to.

So: our measured 52-54fps → 58-61fps win is real and reproduced twice. But
**the specific function we spent the most effort root-causing cannot have
been what LTO improved**, because LTO's project-wide setting, as configured,
literally never touches the compiler invocation that builds it. The PGO
retrain is a separate question — PGO instruments/profiles the statically-
linked runtime and main-EXE code, and it's plausible the win there comes from
better-optimized callback/dispatch code *around* the overlay call (register
allocation at the ABI boundary, branch prediction in the calling convention
glue, etc.) rather than the decode loop itself — but we have not measured
that distinction, only asserted it's plausible, exactly the same standard
mstan's team held our WO-8 claim to.

**This means the actual mechanism behind our win is currently unexplained.**
That's not a reason to distrust the measurement — it was taken carefully,
twice, at matched frame positions — but it is a real gap before recommending
this configuration as a new baseline for every title on the framework, and it
points at a possible next step nobody has proposed yet: **extending
`compile_overlays.py`'s DLL build to carry profile-guided and/or
whole-program optimization flags**, which neither our project-wide setting
nor mstan's scoped `PSX_RUNTIME_IPO` currently does for any title.

## 5. What we're asking you to think about

1. **Is extending `compile_overlays.py`'s overlay-DLL compile path with its
   own PGO/LTO worth prototyping?** This is new surface area neither review
   has touched — it would need its own correctness validation (overlay DLLs
   are loaded/unloaded dynamically per-title-run; LTO-optimized code
   generated across a DLL boundary has different constraints than the
   statically-linked runtime mstan validated).
2. **If not that, what attribution experiment would convince you the current
   win is real and not measurement noise?** We can run whatever matched A/B
   you'd want — isolate PGO from LTO, or instrument the overlay ABI boundary
   directly.
3. **Do you want the PGO-early-stop dispute chased down first?** We have the
   concrete failing command/revision/exit-code evidence mstan's team asked
   for; we just haven't packaged it yet. Say the word and we will.
4. **Scope reminder, already raised once**: whatever gets decided here
   applies to every title built on this framework, not just Parasite Eve.
   Same standard mstan's team already applied to PR #356/#357 — we'd rather
   over-validate before proposing anything as a default than repeat the
   Follow-up 4 mistake (a real, if smaller-scale, false alarm from this same
   investigation).
