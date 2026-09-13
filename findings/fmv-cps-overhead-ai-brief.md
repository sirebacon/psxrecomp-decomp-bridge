# WO-10: does the recompiler itself have a fix for the `0x0010C89C` decompress
stall? A real, source-confirmed mechanism found — but the live A/B test to
size it was unsafe to run to completion, and is reported as inconclusive
rather than oversold

Follow-up to `fmv-decompress-stall-ai-brief.md` (WO-8/WO-9). The user
asked directly: *"based on the document we built is there a solution in
the recompiler to solve this issue?"* This is that investigation's
answer — **partially yes, at the source level; not proven at the
quantitative level, and the reason it isn't proven is itself worth
reporting.**

**Read this whole file before acting on it.** The headline result of the
live experiment below (a large, favorable-looking cycle-count reduction)
is very likely **contaminated by a thermal/ordering confound** and by a
genuine correctness gap in the test method, both disclosed in full — do
not cite the raw percentage from "What we measured" without also citing
"Why we don't trust it" and "The freeze" right below it.

## Short answer

**No — not in the sense of "this function is dispatched wrong" (WO-6's
category) or "this address is misclassified" (the RoomLib fix's
category).** `0x0010C89C` already compiles correctly, classifies
correctly, and dispatches at normal cost. Its cost is real decode work.

**But there is a real, specific, source-confirmed recompiler-level
question worth raising with maintainers**: this function's generated code
pays **2-4 real function calls per basic block** for interrupt-timing and
cycle-accounting bookkeeping — some of them crossing the overlay-DLL
boundary through an indirect callback — and the function has **49 basic
blocks in 864 bytes** (~4.4 real MIPS instructions per block on average).
For a decode loop that runs thousands of iterations per call, that ratio
of bookkeeping-calls-to-real-work is large enough to plausibly matter.
Whether it's a *large* fraction of the measured 20-67ms cost or a small
one, this investigation could not cleanly determine — see below.

## What the source shows, directly (high confidence — this part is solid)

Every CPS-generated basic block in an overlay DLL build
(`PSX_OVERLAY_DLL_BUILD` + `PSX_ENABLE_BLOCK_CYCLES=1`, this project's
standard build) opens with:

```c
block_8010C960:
#ifdef PSX_ENABLE_BLOCK_CYCLES
    if (psx_slice_block(cpu, 0x8010C960u, 2u, 0)) return;
#endif
#ifdef PSX_ENABLE_BLOCK_CYCLES
    psx_icache_fetch(cpu, 0x8010C960u);
#endif
#ifdef PSX_ENABLE_BLOCK_CYCLES
    psx_cyc_step(cpu, 0x2001u);
#endif
    /* ... one real instruction's worth of C, e.g. one shift ... */
```

and every branch, taken or not, closes with:

```c
#ifdef PSX_ENABLE_BLOCK_CYCLES
    psx_cyc_bb_defer_flush();
#endif
    psx_check_interrupts_at(cpu, <target>);
    goto block_<target>;
```

Reading each helper's actual implementation
(`psxrecomp/runtime/include/overlay_dispatch_preamble.c.inc`, the file
`compile_overlays.py` prepends to every overlay DLL):

```c
static OverlayCallbacks g_cbs;
static uint32_t s_pending_cycles;

void overlay_flush_cycles(void) {              /* = psx_cyc_bb_defer_flush() in a DLL build */
    uint32_t cycles = s_pending_cycles;
    s_pending_cycles = 0;
    if (cycles && g_cbs.advance_cycles) g_cbs.advance_cycles(cycles);   /* cross-DLL indirect call */
}
void psx_icache_fetch(CPUState *cpu, uint32_t addr) {
    overlay_flush_cycles();
    if (g_cbs.icache_fetch) g_cbs.icache_fetch(cpu, addr);              /* cross-DLL indirect call */
}
int psx_slice_block(CPUState *cpu, uint32_t block_addr, uint32_t bcyc, int side_effects) {
    overlay_flush_cycles();
    return g_cbs.slice_block ? g_cbs.slice_block(cpu, block_addr, bcyc, side_effects) : 0;  /* cross-DLL indirect call */
}
void psx_check_interrupts_at(CPUState *cpu, uint32_t resume_pc) {
    overlay_flush_cycles();
    if (g_cbs.check_interrupts_at) g_cbs.check_interrupts_at(cpu, resume_pc);  /* cross-DLL indirect call */
    else g_cbs.check_interrupts(cpu);
}
```

**So every block pays, unconditionally**: one `psx_slice_block` call
(itself calling `overlay_flush_cycles`, then an indirect call through
`g_cbs.slice_block`), one `psx_icache_fetch` call (same shape), and
`psx_cyc_step` (this one, `psx_cyc.h`, is a real `static inline` — genuine
local pipeline-interlock bookkeeping, no indirect call, not part of this
concern). **Every branch additionally pays**: `psx_cyc_bb_defer_flush`
(→`overlay_flush_cycles`, possibly another indirect call) and
`psx_check_interrupts_at` (→`overlay_flush_cycles` again, then an
unconditional indirect call to `g_cbs.check_interrupts_at`). None of this
is gated on "does this block actually need an interrupt check" at the
call-site level — every block asks, every time.

**One relevant fact about `psx_slice_block` specifically, found while
reading its real implementation**
(`psxrecomp/runtime/src/dirty_ram_interp.c:2725`,
`psx_slice_block_impl`): its actual time-slicing behavior is **parked,
default off** —

```c
int g_psx_precise_slice = 0;   /* opt-in via PSX_PRECISE_SLICE=1 */
int psx_slice_block_impl(...) {
    if (!g_psx_precise_slice) return 0;   /* <-- this build/session never
                                             goes past this line */
    ...
}
```

So in this project's normal builds (this env var was never set),
`psx_slice_block` is already cheap in what it *does* (one indirect call
that immediately returns 0) — but it's still a real out-of-line
function-pointer call every single block, which is not free even when
the callee is trivial (no inlining across the DLL boundary, a real
call/return, whatever branch-predictor cost an indirect call carries).

## What we tried to measure, and why the result isn't trustworthy as
a clean number

To size this rather than just reason about it, we added a compile-time
toggle to the generated source for `0x0010C89C` only: a set of local
`#define`s that shadow `psx_slice_block`/`psx_icache_fetch`/
`psx_cyc_bb_defer_flush`/`psx_check_interrupts_at` as no-ops, scoped to
just this one function (`#define`d after its CPS entry switch, `#undef`d
right after its closing brace — no other function in the DLL is
affected), combined with the same `__rdtsc()` iteration-counter pattern
from WO-8.

**Phase A** (bookkeeping intact, freshly re-measured this round): 923
clean calls, median **2,141 cycles/iteration**.
**Phase B** (bookkeeping calls neutered, same build otherwise, same FMV
content, launched immediately after): 194 clean calls, median **7,349
cycles/iteration** — i.e. apparently **3.4x worse**, not better.

**Read past the headline number — here's why it's not trustworthy:**

- Directly comparing calls with the *exact same iteration count* (the
  intro FMV is deterministic, so the same call index in both runs decodes
  the same data) shows a split signature: the **first several matched
  pairs show real, substantial improvement** (32-74% *less* time in
  Phase B) — consistent with the hypothesis — but **starting around the
  8th-9th matched call, it flips hard** to Phase B taking 2-4x *longer*
  than Phase A for the same iteration count, and stays that way for the
  rest of the sample.
- This project's own FMV investigation has already established this
  machine (i7-6700HQ, 2015 laptop) as genuinely thermally limited, with
  working frequency counters unavailable to confirm throttling directly
  (`fmv-frame-stall.md`'s "clock/thermal test" section). Phase A and
  Phase B were two back-to-back rebuild+relaunch cycles in the same
  session, with no cooldown between them — **a flip from "clearly better"
  to "clearly worse" partway through a single continuous run is a
  textbook symptom of thermal throttling escalating over the session, not
  a property of the code being measured.**
- We did not have time/a safe way to re-run this with proper thermal
  controls (cooldown periods, alternating order, multiple trials per
  side) before this brief was requested — **so neither the 3.4x-worse
  number nor the early 30-70%-better numbers should be cited as a real
  measurement of this mechanism's cost.** The experiment is inconclusive,
  not negative and not positive.

## The freeze — a real, more important result than the cycle-count number

While Phase B was running live (a second immediate re-launch on the same
neutered build, started to check whether the "worse" result reproduced
immediately or only after more drift), **the game visibly froze at a
specific point during FMV**, observed directly by the user watching the
window. It self-recovered a few seconds later (the log shows guest Hz
dropping into the 50s then climbing back to a clean 60Hz afterward — not
a permanent hang), but a visible multi-second stall is a real, safety-
relevant result on its own, independent of the cycle-count numbers above.

**Why this matters**: `psx_check_interrupts_at` is the mechanism that
lets the game's actual scheduled interrupts (VBLANK, audio DMA,
controller polling) get serviced *during* a long-running native call, not
just after it returns. Fully removing it for the duration of a call that
can run 3,600-14,000+ loop iterations means **nothing this specific
function calls can deliver a timely interrupt while it's running**. That
this produced a visible freeze is direct, positive evidence that these
per-block checks are not simply wasted overhead sitting on top of free
work — **they are actively responsible for keeping this exact hot loop
from stalling far worse than it currently does.** Any real fix attempt
that reduces this bookkeeping's frequency (see "What we'd suggest
maintainers actually try" below) needs to preserve *some* bounded
interrupt-latency guarantee, or it will trade a 20-67ms stall for an
occasional multi-second one — a strictly worse outcome.

The test build (with the neutering macros, the iteration counter, and the
manual `overlay_pair_id()` export needed to load a hand-compiled DLL —
see WO-9) was stopped and fully deleted immediately after the freeze was
observed. A follow-up clean relaunch (normal autocompile, no
instrumentation) was run and confirmed healthy (normal ~52-55fps FMV
numbers, no freeze, no leaked debug output) before this document was
written.

## What we'd suggest maintainers actually try (not implemented, not
validated — starting points only)

Given the freeze result, **removing these calls is not a safe direction**
on its own. Two directions that might reduce cost *without* losing
interrupt timeliness, for whoever owns codegen:

1. **Batch the check, don't remove it.** Rather than calling
   `psx_check_interrupts_at`/`psx_icache_fetch`/`psx_slice_block` at
   *every* block boundary inside a loop the recompiler can already see is
   a tight backward-branching cycle (this function's own loop headers are
   statically identifiable at compile time — the recompiler generates the
   `goto`s), emit the checks once every *K* iterations instead of every
   block, with `K` chosen conservatively enough to bound worst-case
   interrupt latency to something still acceptable (e.g. sub-frame). This
   keeps the correctness property (bounded latency) while cutting the
   call count by roughly a factor of `K` for exactly this shape of
   function — dense intra-loop branching with no side effects visible
   outside the loop.
2. **Devirtualize `g_cbs.*` where possible.** These are function pointers
   crossing a DLL boundary specifically because overlay DLLs are
   `LoadLibrary`'d dynamically (the same structural reason WO-8's
   iteration counter had to use `__rdtsc()` instead of a shared extern).
   If there's a build mode where overlay DLLs could be statically linked
   or LTO'd against the runtime (trading the current hot-swap/dynamic-
   capture workflow for something more rigid), the indirect-call cost
   specifically (as opposed to the "some check happens every block" cost)
   would go away. This is a much bigger architectural question than
   anything else in this project's findings and may not be worth it for
   the size of the win — flagged as an idea, not a recommendation.

**Not suggested**: applying `-O3`/PGO to just this DLL, or hand-unrolling
the loop — neither addresses the per-block indirect-call structure, which
is what the source reading points at as the actual mechanism.

## Honest bottom line for the maintainers

- **Confirmed by direct source reading (trust this)**: the function pays
  real, non-trivial per-block bookkeeping, including several indirect
  calls across the overlay-DLL boundary, on a 49-block, densely-branching
  function — structurally the kind of code where this cost ratio is
  worst-case, not average-case.
- **Not confirmed by measurement (do not trust the specific numbers)**:
  how much of the 20-67ms per-call cost this bookkeeping actually
  accounts for. The one live attempt to measure it was confounded
  (likely thermal drift across a two-phase back-to-back session) and,
  more importantly, revealed that a naive test of the hypothesis breaks
  a real correctness property (interrupt timeliness) badly enough to
  visibly freeze the game.
- **If this is worth pursuing further**: it needs a properly controlled
  experiment (alternating A/B order across several trials, cooldown
  between runs, ideally on non-thermally-limited hardware) AND a fix
  design that explicitly preserves bounded interrupt latency rather than
  removing the checks outright. Neither was in scope to do safely in this
  session.

## Risk

None to the current build — all test-only changes were reverted and the
production build was reconfirmed healthy. The risk described above
(interrupt starvation / visible freeze) applies only to the deleted test
build and to any future attempt to reduce this bookkeeping without
preserving a latency bound — flagged explicitly so nobody re-attempts the
"just remove the calls" version of this experiment without the same
warning.
