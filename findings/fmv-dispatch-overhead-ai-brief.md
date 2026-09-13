# WO-6 & WO-7: two separate problems found in the same investigation

Machine-readable companion to `fmv-dispatch-overhead.md` (full investigation
log) and `fmv-dispatch-overhead-explained.md` (technical narrative version).
This file is written for a coding agent with the `psxrecomp` repo checked
out to act on. It supersedes every specific rate number in
`fmv-dispatch-overhead.md`'s follow-ups 1-5 — those are retracted; only the
numbers here and in that document's "Follow-up 6" table are current.

**Two unrelated problems surfaced in this investigation. Keep them
separate — WO-6 is a real game-performance issue with a proposed fix;
WO-7 is a bug in `psxrecomp`'s own diagnostic tooling, found as a
byproduct of investigating WO-6, with no fix proposed (root cause not
diagnosed). Neither is fixed as of this writing.**

## UPSTREAM RESPONSE (2026-09-12) — read this before anything below

mstan's team reviewed both and responded via
`docs/internal/WO6_BIOS_INTEGRATION_REVIEW.md` on `RetroPortingToolKit/
psxrecomp` (merged as PR #348, integration branch `integrate/
wo6-bios343-346`, tracked as `beads-eio.3.140`). Summary, details in each
WO's own "Upstream response" section below:

- **WO-6: partially addressed, by a different mechanism than proposed.**
  They shipped an O(1) index for resident dispatch-table lookups (measured
  ~54-61ns/query binary search → ~1.2-1.6ns/query indexed — a real,
  isolated benchmark of the lookup itself). They are explicit this "does
  not turn overlay calls into nested C calls or promise fewer dispatcher
  activations" — i.e., it is not the devirtualization fix we proposed, and
  does not remove the per-call ring/stack/IRQ bookkeeping. Whether it moves
  the needle on Parasite Eve's actual FMV framerate is untested by either
  side as of this writing.
- **WO-7: not a bug.** `hot_native` and the function-entry tracer count two
  different things (owner activations including CPS continuation returns,
  vs. plain invocations) — the "1000x discrepancy" we reported was us
  comparing two different metrics, not a broken counter. Their fix is a
  telemetry-label/API-doc clarification, not a code change.
- **They also corrected two errors in our own material**, both accepted
  here without qualification: our back-calculated "~3.2µs/call" dispatch
  overhead figure is invalid (it divides total guest-work time by
  activation count, which folds in real callee computation, not just
  dispatch cost — retracted, see WO-6 below) and our disassembly's branch
  target was off by one instruction (`0x80191BC0`'s `bne ...,FFFB` targets
  `0x80191BB0`, not `0x80191BB4` as originally written — corrected in WO-6
  below with the arithmetic shown).

---

# WO-6: cross-region dispatch overhead (FMV runs ~50fps instead of 60)

## Classification

**Recompiler-side issue, not a game-code issue.** The guest instruction
stream is correct, ordinary PS1-era code (a stream-drain loop, unremarkable
on real hardware). The cost is entirely a property of how `psxrecomp`
compiles/dispatches a direct call whose target crosses from
overlay-compiled code into main-EXE-compiled code. No decomp or game-logic
change is implicated by this finding. Contrast with the earlier, separate
`roomlib-0x80191200-interior.md` finding (also recompiler-side, different
mechanism: a missed function-entry classification causing full
interpreter fallback, fixed via `--force-interior`) — that fix does not
apply here; this is a dispatch-cost issue on code that already classifies
and compiles correctly, not a classification/coverage gap.

## Objective

Reduce per-call dispatch overhead for direct calls from overlay-compiled
code to statically-resolvable targets (main-EXE functions, or other
always-resident code), specifically to recover guest CPU time during FMV
playback, currently measured at ~87-98% saturated with dispatch bookkeeping
during high-load windows.

## Reproduce

1. Build with `-DPSX_DEBUG_TOOLS=ON`.
2. Launch Parasite Eve (USA) to the intro FMV (`--debug-port <N>`).
3. Poll `{"cmd":"overlay_loader_status"}`'s `dispatch_native` field twice,
   1 second apart, during FMV playback. Expect 200,000-320,000/sec in most
   windows (see "Evidence" for the one observed exception).
4. For idle-baseline contrast: same poll at the idle title screen (no FMV)
   returns ~1,600-4,500/sec — confirms this is FMV-specific, not a general
   runtime cost.

## Root cause — exact addresses (this build/session; overlay-relative
addresses will differ per build/overlay layout, re-resolve via the method
in "Verify")

- Hot call site: `0x80191bb0` — `jal 0x8007C484`.
- `0x8007C484` = `StGetNext`, confirmed via `parasite-eve-decomp`'s
  `configs/USA/sym.main.txt:1424` (`StGetNext = 0x8007C484; // type:func`)
  — a main-EXE, PSY-Q-SDK-shaped stream/queue function.
- The call lives inside a loop, disassembled directly via the runtime's
  `mem_words` debug command (raw memory read, not decompiled/symbolic):

  ```
  0x80191bb0  0C01F121  jal   0x8007C484      ; call StGetNext
  0x80191bb4  27A50014  addiu $a1,$sp,0x14    ; delay slot / arg setup
  0x80191bb8  10400005  beq   $v0,$zero,+5    ; branch on return value
  0x80191bbc  2610FFFF  addiu $s0,$s0,-1      ; loop counter decrement (delay slot)
  0x80191bc0  1600FFFB  bne   $s0,$zero,-5    ; branch back to 0x80191bb0 (see correction below)
  ```

  **Correction (flagged by upstream review, verified independently):**
  the branch target was originally miscalculated as `0x80191BB4`. Correct
  MIPS branch-target arithmetic: `target = addr_of_branch + 4 +
  (sign_extend(offset) << 2)` — for this instruction,
  `0x80191bc0 + 4 + (-5 << 2) = 0x80191bc4 - 0x14 = 0x80191BB0`. The
  original write-up used the delay slot's own address as the base instead
  of the branch instruction's address, an off-by-one-instruction error.
  `0x80191BB0` is the `jal` itself — the loop re-executing the call
  instruction each iteration, which is the only sensible target for a
  "call this repeatedly" loop (branching into the delay slot at
  `0x80191BB4` instead would not have made sense). This does not change
  the finding that the loop exists and calls `StGetNext` repeatedly; it
  corrects exactly where the back-branch lands.

- This loop is the body of the function whose entry point is `0x80191B64`
  (standard prologue confirmed at that address: `27BDFFD0` =
  `addiu $sp,$sp,-0x30`). That entry point is itself dispatched at
  **~90-130 calls/sec** (confirmed twice independently — see "Evidence")
  from a separate, outer 2000-iteration loop at `ra=0x80192A44`
  (`jal 0x80191B64` at `0x80192a3c`, inside a function starting at
  `0x80192CE8`).
- Both the outer function (`0x80192CE8`) and its own caller are reached via
  plain intra-region `jal`, not overlay dispatch — the entry/exit tracer
  (`fn_filter`/`fn_entry_dump`) cannot see calls at that level; only
  disassembly reached them.

## Mechanism

`StGetNext` (main EXE, statically compiled once) is called via a fixed,
compile-time-constant `jal` from code compiled as part of a separate
overlay shard. Per `psxrecomp/runtime/src/overlay_loader.c`
(~line 3611-3654, the branch containing `native_hot_note`/`s_disp_native++`
/`c->fn(cpu)`), every such dispatch pays: a native-call ring write
(`s_nring[slot]=...`), an active-call-stack push/pop
(`s_active_stack[s_active_depth++]`), the indirect function-pointer call
itself, and `overlay_post_dispatch_irq_pump(cpu)` after return. None of
this is needed for a `jal` whose target is a fixed, known address — real
hardware executes it as a 2-instruction call with no such bookkeeping.

## Evidence (confidence-graded — cite accordingly)

| Claim | Confidence | Method |
|---|---|---|
| Overlay-dispatch rate during FMV is usually 200K-320K/sec | High | Raw global counter (`overlay_loader_status.dispatch_native`), polled with host-clock-timed deltas, repeated across multiple independent sessions |
| Rate can drop sharply at specific moments (one window: ~4,400/sec) | Medium | Observed once; trigger/frequency of the drop not characterized |
| `StGetNext`, called from inside the function at `0x80191B64`, is the largest identified single contributor | High | Named decomp symbol (`sym.main.txt:1424`) + direct disassembly of the loop + a census (`fn_filter` armed on `0x80000000-0x80200000`, raw 2000-entry sample, counted with no top-N logic) showing it at 93.4% (1867/2000) of one busy-window sample |
| `StGetNext` accounts for ~93% of dispatch volume *on average*, not just in the one sampled window | Low | Only measured directly in one busy window (93%) and one quiet window (~1%); likely varies with the same thing that causes the rate itself to vary |
| The function at `0x80191B64`'s own dispatch rate is ~90-130/sec | High | Two independent methods agree: (a) `fn_filter` armed on its exact range + `fn_stats.entry_total` over a host-clock-timed 10s window; (b) the same filter polled every 0.5s for 24s showing steady, unbroken linear growth (no bursts) |
| ~~~3.2µs of fixed overhead per dispatch call~~ | **Retracted** | Upstream review correctly identified the methodology flaw: this divided total guest-work time by activation count, which folds in whatever real computation the callee (`StGetNext`) does, not just dispatch bookkeeping. It does not isolate dispatch cost and should not be cited. No replacement figure is available — isolating the bookkeeping cost specifically would need direct instrumentation of the dispatch path itself, not back-calculation from aggregate counters. |

The retracted 270K-347K/sec figure for the function at `0x80191B64` is not
repeated here — see **WO-7** below, which *is* that finding.

## Candidate fix (for `psxrecomp` maintainers — not implemented here)

**Primary**: in the overlay compiler (`compile_overlays.py` / the
recompiler's codegen), detect direct `jal`/`j` targets whose destination is
statically resolvable at compile time (main-EXE functions, or other
code known to be always resident) and emit a direct native call instead of
routing through the runtime dispatch/candidate-lookup path. This is
"devirtualizing" calls that are not actually dynamic. Would apply broadly,
not just to this call site.

**Secondary / complementary**: for calls that must remain dynamic (true
indirect/computed jumps), an inline cache at the call site (cache the last
resolved candidate + a cheap validity guard, skip full lookup on a hit)
would reduce — not eliminate — the same class of cost.

**Not a fix**: `--force-interior` does not help here and would make things
worse if misapplied — it isolates code into *more* separately-compiled
shards, increasing cross-boundary call count rather than reducing it. No
local config/mod-level lever was found that changes cross-region call
codegen; this requires a `psxrecomp` source change.

## Scope beyond this title

**Likely affects every psxrecomp-based title, not only Parasite Eve.** The
cost is a property of the overlay-dispatch architecture, not of anything
specific to this game's code — `StGetNext` is a PSY-Q SDK function, not
game-specific logic, and any title that (a) uses overlays for
rooms/cutscenes/menus and (b) polls an SDK stream/audio function in a
tight loop during FMV or audio playback (an ordinary pattern for PS1-era
games) would hit the same mechanism regardless of which specific SDK
function is involved. **Not empirically verified against a second title**
— this is inferred from the cost living in shared architecture rather than
game logic, not confirmed by reproducing it elsewhere. Worth checking
against other psxrecomp titles with FMV-heavy scenes (Tomba, Tomba 2,
MMX6, GT2, WipeOut 3, MotK are all referenced elsewhere in this codebase's
own comments) if any show a similar FMV-specific slowdown.

## Upstream response (2026-09-12, `WO6_BIOS_INTEGRATION_REVIEW.md`, PR #348)

Shipped: an unconditional immutable physical-word index for resident
dispatch tables spanning less than 2 MiB (wide/ambiguous tables keep the
original binary search). Measured via an isolated benchmark of the emitted
lookup (simplified table records, 4,096 repeated mixed-hit queries):
**~54-61ns/query for binary search vs. ~1.2-1.6ns/query for the index** —
a real ~40x speedup for address *resolution* specifically. Their own
caveat, quoted directly: **"This accelerates address resolution; it does
not turn overlay calls into nested C calls or promise fewer dispatcher
activations."** — i.e., every dispatch still happens, still pays the
ring-write/stack-push/IRQ-pump cost this WO describes; only the "which
compiled function does this address belong to" lookup step got faster.

**What this means for this WO's objective**: the lookup they sped up was
never identified here as the dominant cost (this WO's "Mechanism" section
points at the per-dispatch bookkeeping, not the candidate-resolution
search), so a ~50-60ns/query improvement is likely a small fraction of
whatever the true per-call overhead is — which is now unknown in absolute
terms since the ~3.2µs figure above is retracted. Their validation matrix
(Tomba + MMX6, both BIOS variants) explicitly excludes a Parasite Eve FPS
result — see their doc's own "Scope of confidence" section.

**Now tested against Parasite Eve (2026-09-12, this session).** Cherry-picked
their commit (`63b205df`, "Index immutable resident dispatch keys and
clarify owner telemetry") onto this project's checkout (clean cherry-pick,
no conflicts), rebuilt the emitter + regenerated + rebuilt the runtime,
and ran a same-day, same-machine, back-to-back A/B against the unpatched
build — same intro-FMV content, same `PSX_RUNTIME_PERF_DIAG` methodology,
one continuous run each side (~270-280 FMV-window samples, i.e. ~4.5
minutes each):

| Metric | Before (unpatched) | After (WO-6 index) |
|---|---:|---:|
| Avg guest Hz (≈fps) during FMV | 55.43 | **57.74** |
| Min/max guest Hz | 41.79 / 63.87 | 45.89 / 61.98 |
| Avg `work guest` ms/s (saturation) | 955.9 | 962.7 |
| Avg `dispatch_native`/s | 322,465 | 337,939 |
| Samples below 58Hz | 73.1% (196/268) | **36.7%** (104/283) |
| Samples below 55Hz | 37.7% (101/268) | **13.1%** (37/283) |

**Real, measurable improvement**: +2.3fps average (+4.2% relative), and
roughly half as many sub-60fps dips, despite `work guest` ms/s and
`dispatch_native`/s being statistically indistinguishable between the two
runs (both ~955-963ms/s saturation, both ~320-340K dispatches/sec) — i.e.
this doesn't show up as "less total dispatch work" in the coarse
per-second counters, consistent with upstream's own caveat that the fix
doesn't reduce dispatch/activation count. The likely mechanism: shaving
~50-60ns off *every one* of ~300K+ per-second address lookups (O(log
29,827) binary-search comparisons down to one O(1) array read) is a small
fraction of the 1-second budget on its own, but it's apparently often
enough to keep the guest thread's per-frame work *under* the real-time
deadline in windows where it was previously landing just *over* it —
fewer overruns, not less total work.

**Caveats on this result**: single run per side, not a multi-trial average
— background system load and minor real-time-dependent branching could
shift both runs slightly. The direction and rough magnitude (a few percent
average fps, meaningfully fewer bad dips) are consistent with the
mechanism upstream described, but this should be treated as a solid single
data point, not a fully statistically-controlled benchmark. Worth a repeat
run or two before quoting the exact percentages externally with high
confidence.

## Verify (for whoever picks this up)

1. Confirm current build's exact addresses before reusing any address
   above — they are specific to this session's overlay layout and will
   shift with different overlay load order/build. Re-resolve via: arm
   `fn_filter` on `lo=0x80000000,hi=0x80200000`, `fn_clear`, wait briefly,
   `fn_entry_dump`, count occurrences per `func` in the returned sample —
   the dominant address should again resolve to a real `sym.main.txt`
   symbol via direct lookup.
2. Confirm the loop shape by disassembly (`mem_words`) at the resolved
   call site before trusting any live trace's `ra`/counts (see WO-7 — a
   live diagnostic field was flatly wrong this session, so treat
   single-source live-trace numbers as unconfirmed until cross-checked).
3. If a fix is prototyped, re-run the idle-vs-FMV `dispatch_native`
   comparison (see "Reproduce") before/after — the idle baseline
   (~1,600-4,500/sec) should be unaffected; the FMV rate should drop
   substantially if the fix targets a meaningful fraction of the ~200K-320K/sec
   volume.

## Risk

Low risk to game correctness if the candidate fix is implemented as a
pure codegen optimization (same semantics, fewer bookkeeping side effects
per call) — but the removed bookkeeping (native-call ring, active-call
stack, post-dispatch IRQ pump) may be relied on elsewhere for debugging or
correctness invariants (e.g., the native-call ring is described elsewhere
in `psxrecomp` as attributing "a wrong-variant native run on a production
binary" — Tomba 2 splash reload loop). Any implementation should confirm
those diagnostic/correctness paths still function for calls that keep
going through full dispatch, and should not silently disable them for
*all* calls, only ones proven statically resolvable.

---

# WO-7: `hot_native` diagnostic reports wrong per-function call counts

**STATUS: RESOLVED — not a bug.** See "Upstream response" below. Kept in
full as the original report, since the reasoning and the correction are
both instructive, but do not cite the "wrong counter" framing further —
it's settled.

## Classification

**Bug in `psxrecomp`'s own runtime diagnostics, not a game-performance
issue and not related to WO-6's fix.** Found as a byproduct of
investigating WO-6, when a number this field reported turned out to be
unreproducible by two other, independent measurement methods. This is a
report that the tool itself is wrong, separate from anything about
Parasite Eve.

## Objective

Diagnose and fix the misattribution in `overlay_loader_take_hot_native` /
`native_hot_note` (`psxrecomp/runtime/src/overlay_loader.c`) so the
`hot_native=ADDR/+COUNT` field in `PSX_RUNTIME_PERF_DIAG` output can be
trusted for per-function attribution again.

## Symptom, exactly as observed

During one session's FMV playback, `PSX_RUNTIME_PERF_DIAG`'s per-second log
line reported `hot_native=0x00191B64/+252511` (i.e., the function at guest
address `0x80191B64` dispatched 252,511 times in that one second). Two
independent re-measurements of that *exact* address's real dispatch rate,
taken in later sessions:

1. `fn_filter` armed on `lo=0x80191B60,hi=0x80191B70`, `fn_stats.entry_total`
   read against a Python-timed 10-second window → **86 calls/sec.**
2. The same filter polled every 0.5s for 24 seconds, watching the counter
   directly → **steady linear growth of ~90-130/sec, no jumps.**

Both agree with each other (~90-130/sec) and disagree with `hot_native`'s
252,511/sec by roughly three orders of magnitude. This is not "the rate
varies a lot" (WO-6's dispatch-volume variability is a separate, confirmed,
much smaller-magnitude phenomenon) — it's the same address, compared
against itself, disagreeing by ~1000-2500x.

## Root cause

**Not diagnosed.** Not fixed, not attempted — flagging for whoever owns
`overlay_loader.c`. One concrete lead: `native_hot_note`
(`psxrecomp/runtime/src/overlay_loader.c`, ~line 488-494) hashes the
dispatched address into one of `NATIVE_HOT_CAP` (256) buckets via
`slot = ((pc >> 2) * 2654435761u) & (NATIVE_HOT_CAP - 1u)`, and resets a
bucket's count to 0 whenever a *different* address lands in the same slot
(`if (h->pc != pc) { h->pc = pc; h->calls = 0; }`). The misattributed count
in the observed case landed on `0x80191B64` — the entry point of the exact
function whose *body* (not entry point) contains the real hot loop found
in WO-6 (the `StGetNext` drain loop at `0x80191bb0`, ~90 bytes past the
entry). This proximity is suggestive of a bucketing-by-containing-function
artifact rather than a genuine hash collision between unrelated addresses,
but this was not traced further — treat as a hypothesis, not a finding.

## Candidate fix

**Superseded** — see "Upstream response" below. No code fix needed;
upstream is handling this as a documentation/label clarification.

## Scope beyond this title

**Superseded — moot.** This section originally argued that since
`hot_native` is shared runtime code, a bug in it would affect every
psxrecomp title's performance diagnostics, making this higher priority
than WO-6. Per the upstream response above, there is no bug, so there is
no cross-title impact to reason about. Left here only so the reasoning
trail isn't silently deleted — do not cite the "affects every title"
claim for WO-7.

## Verify

Reproduce the discrepancy first, since this may be data/timing-dependent:
during FMV playback, compare a `PSX_RUNTIME_PERF_DIAG` log line's
`hot_native=ADDR/+COUNT` against the same `ADDR`'s rate measured via
`fn_filter`+`fn_stats.entry_total` (or `fn_filter` polled repeatedly) over
a precisely host-clock-timed window covering the same real time. Large
disagreement (order-of-magnitude or more) reproduces this bug; rough
agreement means it may be state- or timing-dependent and needs a wider
sweep to characterize.

## Risk

None to game correctness — this is a read-only diagnostic. Risk is entirely
to anyone else's *investigation* if they trust `hot_native` for
per-function attribution without cross-checking it, as this investigation
initially did.

## Upstream response (2026-09-12, `WO6_BIOS_INTEGRATION_REVIEW.md`, PR #348)

**Verdict: no counter algorithm change, no confirmed counter corruption.**
Quoted directly: *"the native hot-owner sampler counts owner activations,
including CPS continuation returns. Function-entry tracing counts
invocations."* — `hot_native` and `fn_filter`/`fn_entry_dump` were never
measuring the same thing. The "three orders of magnitude" gap reported
above is the expected size of that difference for this call site, not
evidence of a broken counter.

This also directly refutes the "Root cause" hypothesis above: *"Its
direct-mapped bucket resets on a collision, so it can undercount but does
not accumulate another owner's calls."* — a collision cannot inflate a
count by absorbing hits from a different address; it can only zero the
bucket out. The hash-collision theory in this WO's "Root cause" section is
wrong and should not be repeated.

Their fix: *"Clarify the telemetry label and API docs"* — a documentation
change, not a code change, since there was no bug to fix.

**What we got wrong, stated plainly**: this WO's core claim — that
`hot_native` is unreliable and gave a wrong answer — does not hold up.
The two independent re-measurements that seemed to contradict it (~90-130
calls/sec via the entry tracer) were correctly measuring invocations; they
were never in a position to reproduce or contradict a counter that measures
a different, broader quantity (owner activations including CPS
continuation returns). Filed here as a full correction, not a footnote —
this WO should not be cited as evidence of a `psxrecomp` diagnostics bug.
