# Why FMV runs at ~50fps instead of 60 — explained

Written for a technical reader (i.e., you two) rather than as a formal
work order — see `fmv-dispatch-overhead-ai-brief.md` for the structured
version with exact addresses and a confidence-graded evidence table.

This investigation surfaced **two separate problems**, not one. Keeping
them clearly apart matters — they're unrelated bugs that happened to turn
up in the same session, not two symptoms of one cause.

## Upstream response (2026-09-12) — read this first

mstan's team reviewed both. Short version: **Problem 1 is partially
addressed, by a different mechanism than we proposed. Problem 2 turned out
not to be a bug at all** — we were comparing two different measurements
and mistaking the expected gap between them for a broken counter. They
also caught two real errors in our own numbers, both corrected below
without qualification. Details are in each problem's own section; see
`docs/internal/WO6_BIOS_INTEGRATION_REVIEW.md` (RetroPortingToolKit/
psxrecomp, PR #348) for their original write-up.

## Problem 1 — cross-region calls pay dispatch overhead they don't need

**Status: partially addressed upstream, by a different fix than proposed.
Tested against this project's actual build (2026-09-12) — it helps: +4%
average fps, roughly half as many sub-60fps dips. See "Upstream response"
below for the numbers.**

The guest code is doing something completely unremarkable — polling for
more stream data in a loop while a video plays. The cost comes entirely
from the fact that this loop's call target crosses from overlay-compiled
code into main-EXE code, and every such crossing currently pays full
dispatch bookkeeping — a call-history ring write, active-call-stack
push/pop, the indirect call itself, a post-dispatch IRQ pump — even though
in this case the call target is a fixed address known at compile time, not
a genuine indirect/computed jump.

**Root cause, precisely:**

- The loop is `RoomLib`-overlay code; its target, `StGetNext`, is main-EXE
  code (statically compiled once, always resident).
- Every `jal` from overlay-compiled code to a target outside that overlay's
  own compiled unit currently routes through the dynamic dispatch/candidate
  lookup path — the same path used for genuine indirect calls where the
  target isn't known until runtime.
- This specific `jal` doesn't need that: the target is a hardcoded
  immediate in the instruction stream, resolvable at compile time. It's
  paying dynamic-dispatch cost for a call that was never actually dynamic.
- ~~Per-call overhead is measurable (~3.2µs...)~~ — **retracted.** Upstream
  correctly pointed out this divided total guest-work time by activation
  count, which folds in whatever real work the callee (`StGetNext`) does,
  not just dispatch bookkeeping. It isn't a clean measurement of dispatch
  cost and shouldn't be cited. We don't have a replacement number — the
  guest-thread saturation itself (96-98% during FMV vs. 43-44% idle) is
  still solid, just not broken down into "this much is dispatch, this much
  is real work."

**Candidate fix (ours)**: recognize direct `jal`/`j` targets resolvable at
compile time (main-EXE functions, other always-resident code) during
overlay compilation and emit a direct native call instead of routing
through runtime dispatch — devirtualizing calls that were never actually
dynamic. See the AI brief for a secondary option (inline caching at the
call site) for calls that must stay dynamic.

**What upstream actually shipped instead**: an O(1) lookup index for
resident dispatch tables, replacing binary search for tables under 2 MiB.
Their own isolated benchmark: ~54-61ns/query (binary search) vs.
~1.2-1.6ns/query (indexed) — a real, measured ~40x speedup for address
*resolution*. But, in their own words: *"this accelerates address
resolution; it does not turn overlay calls into nested C calls or promise
fewer dispatcher activations."* Every dispatch still happens, still pays
the ring-write/stack-push/IRQ-pump cost this problem describes — only the
"which function does this address belong to" lookup step got faster, and
that lookup was never the part of the cost we were pointing at. Their own
validation (Tomba + MMX6, both BIOS variants) explicitly doesn't include a
Parasite Eve FPS result.

**We tested it ourselves against this actual build (2026-09-12).**
Cherry-picked their fix, rebuilt, and ran a same-day, back-to-back A/B
against the unpatched build — same intro FMV, same measurement method,
~4.5 minutes each side:

| | Before | After |
|---|---:|---:|
| Avg fps during FMV | 55.4 | **57.7** |
| % of samples under 58fps | 73% | **37%** |
| % of samples under 55fps | 38% | **13%** |

It genuinely helps — about +4% average fps, and roughly half as many
noticeable dips — even though the raw "how saturated is the guest thread"
and "how many dispatches per second" numbers barely moved between the two
runs. Best guess at why: shaving ~50-60ns off each of 300K+ per-second
address lookups doesn't look like much on its own, but it's apparently
enough to keep the guest thread under its per-frame deadline in some
windows where it was previously landing just over it — fewer overruns,
not less total work. Caveat: one run per side, not a multi-trial average;
treat as a solid single data point pending a repeat.

**Likely affects every psxrecomp title, not just this one.** The cost
comes from the overlay-dispatch architecture itself, not from anything
specific to Parasite Eve's code — `StGetNext` is a PSY-Q SDK function, not
something this game's developers wrote, and any other title built on
psxrecomp that (a) uses overlays for rooms/cutscenes/menus and (b) polls
an SDK stream/audio function in a tight loop during FMV or audio playback
— both very ordinary patterns for late-90s PS1 games — would hit the same
mechanism. **Not tested against another title** — this is a reasoned
inference from where the cost lives (shared architecture, not game logic),
not an empirical confirmation on a second game. Worth checking against
Tomba, Tomba 2, MMX6, GT2, WipeOut 3, or MotK if any of those have a
similarly slow FMV.

**Same category as the RoomLib fix, different mechanism.** Worth being
explicit, since it's easy to conflate: the earlier RoomLib fix was a
*classification* problem — `compile_overlays.py` never promoted a
genuinely-executed address to a compiled function entry, so it fell back
to the interpreter permanently until `--force-interior` fixed it. This is
a *dispatch-cost* problem on code that already classifies and compiles
correctly — `--force-interior` doesn't apply here and would make it worse
(it isolates code into more, not fewer, separately-compiled shards). Both
are recompiler-side; neither implicates the decomp or the original game
code.

## Problem 2 — the `hot_native` diagnostic gives wrong per-function counts

**STATUS: RESOLVED — not a bug.** Upstream confirmed `hot_native` is
working as designed; the discrepancy below was us comparing two different
metrics and mistaking the (expected) gap between them for broken telemetry.

`overlay_loader_take_hot_native` (surfaced via the `PSX_RUNTIME_PERF_DIAG`
log as the `hot_native=ADDR/+COUNT` field) reported one function at
**~270,000-347,000 calls/sec**. Two independent, precisely wall-clock-timed
re-measurements of that exact function using the function-entry/exit
tracer put its rate at **~90-130 calls/sec** — roughly three orders of
magnitude lower. We took this as proof `hot_native` was broken.

It isn't. Upstream's answer: *"the native hot-owner sampler counts owner
activations, including CPS continuation returns. Function-entry tracing
counts invocations."* Those are two different, both-correct things to
count — a single guest call to a function that yields and resumes (a CPS
continuation) can rack up multiple "owner activations" without that being
multiple new invocations. `hot_native` was never wrong; we were comparing
its number to a differently-defined number from a different tool and
calling the gap a bug.

Our hash-bucket-collision theory (a plausible-looking guess: the
misattributed count landed on the entry point of the function whose body
contains the real hot loop) is explicitly refuted, not just unconfirmed:
*"its direct-mapped bucket resets on a collision, so it can undercount but
does not accumulate another owner's calls."* A collision can only make the
count too low, never too high — it can't produce the inflated number we
saw, so it was never a viable explanation to begin with.

Upstream's own assessment, stated plainly in their write-up: *"this WO's
core claim — that `hot_native` is unreliable and gave a wrong answer —
does not hold up... This WO should not be cited as evidence of a
`psxrecomp` diagnostics bug."* The only actual action item is cosmetic:
clarify the telemetry's label and API docs so the next person doesn't make
the same comparison-of-two-different-metrics mistake we did. No counter
algorithm changes, no confirmed corruption.

**Scope beyond this title: superseded — moot.** There's no bug, so there's
nothing to reason about spreading to other titles.

## How we actually found both

Not by reading source and spotting either one — by measuring, and by not
trusting the first measurement.

1. **The premise that started this**: after the earlier RoomLib fix,
   gameplay and menus hit a clean 60fps on this machine. FMV stayed at
   ~50fps. "This laptop just isn't fast enough" doesn't survive that
   comparison — if it were a raw horsepower ceiling, *everything* would be
   uniformly slow, not just video.

2. **Confirmed the guest thread really is the bottleneck, and quantified
   it.** Using the runtime's existing `PSX_RUNTIME_PERF_DIAG` output:
   guest CPU work sits at 96-98% of the frame budget during FMV, versus
   43-44% idle at the title screen.

3. **Asked the obvious next question — which function is eating that
   time — via `hot_native`**, and got the dramatic ~270K-347K/sec answer.
   Wrote that up as the finding (this became Problem 2, later).

4. **Went back to cross-check it independently before treating it as
   settled, and got a very different number.** Armed the function
   entry/exit tracer (`fn_filter`/`fn_entry_dump`) on that exact address and
   watched its call count over a precisely wall-clock-timed window:
   ~86-130/sec, growing linearly, no bursts — versus `hot_native`'s
   ~270K-347K/sec. At the time we treated this gap as proof `hot_native`
   was broken and wrote it up as Problem 2. Upstream's review corrected
   that: the two tools count different things (owner activations including
   CPS continuation returns, vs. plain invocations), so a gap between them
   is expected, not a bug. Both numbers were real; our conclusion about
   what the gap meant was wrong.

5. **Found Problem 1's real answer with a method that doesn't rely on any
   single "hottest function" counter**: armed the entry tracer across the
   whole `0x80000000-0x80200000` range, pulled a raw sample of whatever the
   ring actually recorded, and counted occurrences per address in Python —
   no built-in top-N logic to second-guess. One address dominated at 93.4%
   of a 2000-entry sample, an order of magnitude above the
   originally-blamed function.

6. **Confirmed the mechanism at the instruction level**, not from a
   symbol name: read the raw words at the call site directly
   (`mem_words`) and decoded the MIPS by hand —

   ```
   jal   0x8007C484        ; call
   ...
   beq   $v0,$zero,+5      ; branch on return value
   addiu $s0,$s0,-1        ; decrement counter (delay slot)
   bne   $s0,$zero,-5      ; loop back
   ```

   — an unambiguous drain loop, no interpretation required. `0x8007C484`
   resolves to `StGetNext` in `parasite-eve-decomp`'s `sym.main.txt` — a
   real symbol, not something inferred from behavior. The call site's
   return address (`0x80191BB8`) sits inside the very function whose entry
   point (`0x80191B64`) `hot_native` had reported the huge count for. We
   originally read that as suspicious (a hint of misattribution). With
   Problem 2 resolved as "working as designed," it's not suspicious at all
   — `hot_native` was correctly pointing at the function containing the hot
   loop the whole time; we just misread what its count meant.

## Confidence

High confidence in Problem 1's mechanism and in `StGetNext` as the largest
single identified contributor to it — both confirmed by independent
measurement and by direct disassembly. Lower confidence in how much of the
*average* cost across an entire FMV this one loop explains — its share was
measured at 93% in one busy window and ~1% in one quiet window, and the
quiet-window behavior hasn't been separately characterized. The ~3.2µs/call
figure is retracted (invalid methodology, per upstream). Upstream's shipped
O(1) dispatch-index fix has now been tested against this project's actual
build: a real, positive, but modest effect (+4% average fps, ~half as many
sub-60fps dips) from a single same-day A/B — solid, but not yet confirmed
across repeated runs.

Problem 2 is closed: upstream's review directly refutes both our headline
claim (`hot_native` unreliable) and our hash-collision root-cause guess.
Treat it as resolved, not as an open low-confidence lead. See the AI
brief's evidence table and the "Upstream response" sections for the full
breakdown and exact quotes before citing a number from either problem.
