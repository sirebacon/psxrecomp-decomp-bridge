# WO-11: prototyped WO-10's suggested recompiler fix (both variants) — the
codegen mechanism works exactly as designed; the performance win it hoped
for did NOT show up in a properly-controlled measurement

Follow-up to `fmv-cps-overhead-ai-brief.md` (WO-10). User asked to actually
build both suggested strategies behind separate flags and test them. Both
are implemented, in the actual `psxrecomp` recompiler source, gated behind
env vars that default OFF (zero effect on any existing build unless
explicitly opted in). **Read "What the measurement actually showed"
before treating this as a win** — the honest result is more interesting,
and more useful to a maintainer, than a clean success story would be.

## What was built

Two independent, env-gated strategies for skipping the per-block CPS
bookkeeping (`psx_slice_block`/`psx_icache_fetch`/`psx_cyc_bb_defer_flush`+
`psx_check_interrupts_at`) that WO-10 identified as a real, if unquantified,
cost — implemented in `psxrecomp/recompiler/src/code_generator.cpp` +
`include/code_generator.h`, both defaulting OFF so existing builds are
byte-for-byte unaffected until opted in:

- **`PSX_IRQ_BATCH_LOOP=1`**: a block is elidable if it's strictly interior
  to a detected natural loop (`ControlFlowGraph::loops` already exists in
  this recompiler — `(header, back_edge_source)` pairs, found by the
  existing `detect_loops()`), isn't itself a loop header, doesn't call out
  (`jal`/`jalr`), and touches no interrupt-visibility COP0 state (`MTC0`
  Status/Cause, `RFE`). The loop header always keeps the full check, so
  added worst-case interrupt latency is bounded to one loop iteration.
- **`PSX_IRQ_BATCH_CHAIN=1`**: bounded (K=4) straight-line coalescing,
  independent of loop detection — a block only gets elided if it's the
  *private*, unshared successor of a single-successor predecessor (nothing
  else could plausibly need to resume there), capped at 4 consecutive
  blocks so even a long straight run still gets a real checkpoint
  regularly.

Both are implemented as a single `current_block_irq_elidable_` flag,
computed once per block at the top of `translate_basic_block` and
consulted by `emit_interrupt_check`/`emit_interrupt_check_expr` plus the
two inline `psx_slice_block`/`psx_icache_fetch` emission sites — no call
site outside those needed touching.

## A real bug found and fixed while building this (worth knowing about
this recompiler's CFG data for anyone else touching `code_generator.cpp`)

**`BasicBlock::predecessors` is never populated on this generation path.**
Verified empirically: instrumented `compute_loop_interior_elidable` to
dump every block's `predecessors.size()` for a real, live-captured,
multi-loop function (`0x8010C89C`, WO-8's decompress function) to a plain
file (`compile_overlays.py`'s `subprocess.run(..., capture_output=True)`
swallows a successful compile's stdout/stderr silently, so a stderr-based
print never surfaces — write debug output to a file instead if you hit
this) — every single block reported `pred_n=0`, including ones with
multiple real incoming edges. My first implementation walked
`predecessors` backward from each loop's `back_edge_source` to its
`header` to compute the loop body, and with `predecessors` always empty,
that walk terminated immediately, so **the whole loop-batch mechanism was
silently a no-op for its first two build-and-test cycles** — the
generated code was indistinguishable from flags-off, no error, no
warning. Confirmed the env var itself really was reaching the recompiler
correctly first (control test: toggled the existing, already-working
`PSX_CODEGEN_CYCLE_PER_INSN` flag through the identical pipeline and
watched it change the generated code as expected) before concluding the
bug was in the new code, not in env-var plumbing — worth doing that kind
of control check before assuming a new flag itself is broken.

**Fix**: added `compute_predecessors(cfg)`, a small helper that derives a
reverse-edge map from every block's own `successors` list (one pass over
`cfg.blocks`), and used that everywhere the (empty) `.predecessors` field
was previously trusted. After this fix, direct inspection of the
regenerated source confirmed the mechanism works exactly as designed:
interior blocks (e.g. `block_8010C968`) lose all four heavy calls, the
loop header (`block_8010C960`) keeps every one of them unchanged. This
also means **the chain-batch flag's "single predecessor" check was
equally broken until the same fix** — it just happened to matter less
since this specific function's blocks are almost all 2-successor
branches, which the chain criterion excludes anyway (see below).

## Verified correct via direct source inspection

```c
/* PSX_IRQ_BATCH_LOOP=1, block_8010C968 — a genuine loop-interior block */
block_8010C968:
#ifndef PSX_NO_DEBUG_TOOLS
    debug_server_cyc_observe(0x8010C968u);
#endif
#ifdef PSX_ENABLE_BLOCK_CYCLES
    psx_cyc_step(cpu, 0x102u);          /* kept: cheap, local, no cross-DLL call */
#endif
    cpu->gpr[1] = cpu->gpr[8] ^ 0x03FF;  /* the actual instruction */
    ...
    if (_bc_8010C96C) {
        goto block_8010CB84;             /* no psx_cyc_bb_defer_flush/check_interrupts_at */
    } else {
        goto block_8010C974;
    }

/* the loop header itself, unchanged */
block_8010C960:
#ifdef PSX_ENABLE_BLOCK_CYCLES
    if (psx_slice_block(cpu, 0x8010C960u, 2u, 0)) return;
#endif
#ifdef PSX_ENABLE_BLOCK_CYCLES
    psx_icache_fetch(cpu, 0x8010C960u);
#endif
    ...
```

Confirmed with both flags off that the generated source for this same
function is unchanged in structure from before this work (every block
still carries its full bookkeeping) — a real, direct diff check, not an
assumption.

**Chain-batch (`PSX_IRQ_BATCH_CHAIN=1`) shows minimal effect on this
particular function** — a quick check of two candidate single-successor
blocks (`0x8010C928`, `0x8010C92C`) found them still carrying full
bookkeeping. This function's own structure is the likely reason, not a
remaining bug: 49 blocks in 864 bytes with the overwhelming majority
showing 2 successors (a real conditional branch) per the earlier
diagnostic dump — this is about as branchy as PS1 code gets, so there are
few genuinely single-predecessor/single-successor "private" chains for
this criterion to find. Not deeply re-verified beyond this spot check;
flagged as a real limitation rather than confirmed root-caused.

## The build ran and played correctly

Launched the actual game with each flag independently, through the full
FMV sequence, on the live debug-server-connected build: no crash, no
visible corruption, FPS in the normal 40-57Hz range for this section
across every configuration tested. Not a substitute for real correctness
validation (see "What this doesn't prove" below), but a meaningful first
signal that the change doesn't break anything obviously.

## What the measurement actually showed — read this before citing a number

Ran 4 short (~22s), **alternating** trials (baseline, loop-batch,
baseline, loop-batch — not one long back-to-back block, specifically to
avoid the exact thermal-drift confound that corrupted WO-10's earlier A/B)
against the real intro FMV, using the runtime's existing `latency` debug
command (`{"cmd":"latency","raw":1,"count":70}`) to record, per frame, the
single worst native-dispatch call's address and duration
(`disp_addr`/`disp_max_us` — already-existing instrumentation from WO-8,
no new runtime changes needed). Filtered each trial's frames to ones
where `disp_addr == 0x0010C89C` (our target function was the single worst
dispatch that frame):

| | Baseline (trials 1+3) | Loop-batch (trials 2+4) |
|---|---:|---:|
| Frames captured | 2,238 | 2,457 |
| Frames where this function was the worst dispatch | 307 | 603 |
| Mean duration on those frames | 7.89ms | 8.06ms |
| Worst single duration observed | 15.36ms | 16.41ms |

**No measurable improvement — if anything, marginally worse, well within
noise.** This is the honest, load-bearing result of this round, not a
footnote. Two candidate explanations, both plausible, neither confirmed:

1. **Most of the removed calls may already have been nearly free in this
   exact build.** `psx_slice_block`'s real "precise slicing" behavior is
   parked/disabled by default (`g_psx_precise_slice = 0`, opt-in via
   `PSX_PRECISE_SLICE=1`, never set anywhere in this project) — so in
   production its call body is one indirect call that immediately returns
   0. If `psx_check_interrupts_at`'s and `psx_icache_fetch`'s callback
   implementations have similarly cheap fast paths when nothing is
   actually due, removing them saves the *call* overhead (a real, if
   possibly small, cost) but not any meaningful *work* — which would mean
   the dominant cost really is the decode arithmetic itself, reinforcing
   WO-8's original finding rather than revealing a second, separate,
   comparably-sized win sitting on top of it. Not verified directly this
   round — would need micro-timing the callback bodies specifically, the
   same way WO-10's (abandoned, unsafe) neutering experiment tried to do
   at the macro level.
2. **Content-alignment drift between differently-performing builds,
   captured at a fixed wall-clock offset.** Each trial starts polling 35
   real seconds after launch, not at a fixed point in the FMV's own
   content — if the two builds' overall speed differs even slightly, 35
   real seconds of one build corresponds to a *different* point in the
   video/audio timeline than 35 real seconds of the other, so the two
   sides may simply not be comparing the same underlying work. This
   trial design cannot rule that out, and it's a real limitation of doing
   this by wall-clock timing rather than by loading an identical savestate
   positioned right before the segment of interest for every trial.

**One number that IS worth noting, cautiously**: this function was the
single-worst dispatch on roughly twice as many frames under loop-batch
(603 vs 307, over comparable total frame counts). That's consistent with
this function's *typical* (non-worst-case) calls getting cheaper — enough
to surface as "worst dispatch" in frames it previously wasn't — while its
own worst-case tail didn't visibly shrink. Interesting, but not something
this dataset can confirm confidently on its own; flagged as a lead, not a
finding.

## What this doesn't prove (be precise about this with anyone reading it)

- **No correctness validation beyond "it ran and looked fine."** This
  codebase has a `PSX_COSIM` co-simulation mode specifically for
  confirming a codegen change produces bit-identical CPU/RAM state against
  the interpreter — not run here. Skipping fewer interrupt-timing
  checkpoints changes *when* a masked-but-pending interrupt can become
  deliverable; for this specific function (no COP0 writes, no device
  touches, confirmed via `block_side_effect_free`) that risk is low by
  construction, but "low by construction" is not the same as "verified."
- **Only one function was ever exercised.** Both flags are global (every
  function in every build gets the same treatment once enabled) but only
  `0x0010C89C`'s behavior under them was actually inspected or measured.
  A function with COP0 traffic, device touches, or calls inside what looks
  like a tight loop would be excluded by the existing guards — but that
  exclusion logic itself has not been tested against such a function.
- **Four short trials is a demonstration, not a benchmark.** A real
  verdict needs many more trials, ideally anchored to an identical
  savestate/content position rather than a fixed wall-clock offset, and
  ideally on hardware without this machine's documented thermal ceiling.

## Follow-up (2026-09-13) — where overall FMV performance actually stands
with every fix applied, and ruling out one specific regression theory

After this round, the user asked directly: *"I feel like we are not
utilizing all of the fixes we have done to make it max fps... the
baseline is slower now than it was before. Why would that be the case if
we use all fixes. Maybe the debug software is slowing it down?"* — a fair
question given how many rebuilds this whole arc (WO-8 through WO-11) went
through. Checked rather than assumed:

**Both real, confirmed fixes are still in the tree at HEAD** — verified
directly with `git log`, not from memory: `a94ab281` (the RoomLib
interior-classification port, PR #349) and `bda01335` (WO-6's dispatch
index) are both present and ancestors of the current checkout. Nothing
was lost or reverted by any of this session's recompiler-prototyping
work.

**The debug-tools theory was tested directly, not just discussed — and it
does not hold up.** `build-release`'s `CMakeCache.txt` confirmed
`PSX_DEBUG_TOOLS:BOOL=ON`, and that flag is not free: `debug_server_cyc_observe()`
genuinely runs at every basic block of the statically-compiled main-EXE/BIOS
code when it's on (real comparisons, a cached `getenv`, an address check —
not a no-op; it only compiles out under `PSX_NO_DEBUG_TOOLS`, which overlay
DLLs always use regardless of this flag). Rebuilt with `-DPSX_DEBUG_TOOLS=OFF`
and ran a same-session, back-to-back comparison against a fresh
`PSX_DEBUG_TOOLS=ON` rebuild, aligned by **frame count** (not wall clock,
so a genuine speed difference between the two builds couldn't hide inside
a fixed time window):

| Frame ~2470–2520 into the same FMV | FPS |
|---|---:|
| `PSX_DEBUG_TOOLS=OFF` | 50.0–51.4 |
| `PSX_DEBUG_TOOLS=ON` (fresh rebuild, same session, immediately after) | 52.7–54.1 |

**No improvement from disabling debug tools — if anything, marginally
lower.** This directly rules out "the debug server is the reason it feels
slower" as the explanation, rather than leaving it as an untested guess.

**What this same comparison incidentally proved, which matters more**:
two back-to-back launches of the *identical* build (`PSX_DEBUG_TOOLS=ON`,
run once during the loop-batch trials earlier in this doc, run again here)
showed FMV FPS at the same frame-count position varying by roughly 5-8%
run to run, with zero code difference between them. That's a real,
directly measured amount of ordinary session-to-session noise on this
specific machine — this project has documented its thermal ceiling
before (`fmv-frame-stall.md`'s clock/thermal section; frequency counters
don't work on this hardware to confirm throttling directly, but the
mechanism is well established as a live suspect throughout this whole
project) — plus normal background system load and FMV content-position
drift between separately-timed launches. A "feels slower than before"
impression of this size, with no saved prior build to diff against, is
fully explainable by this noise band alone; it does not require a real
regression to have happened.

**Where FMV performance stood at this point** (RoomLib interior-classification
fix, WO-6's dispatch index, `-march=native`, PGO — all present in
`build-release` as configured): roughly **50–57 FPS during the boot-intro
FMV** (guest Hz, i.e. ~0.83-0.95x of the PS1's native 59.94Hz), consistent
across every measurement in the whole WO-8/WO-9/WO-10/WO-11 arc regardless
of which experimental flag was active, with the ~5-8% run-to-run band
above layered on top of that range. **This number is now superseded —
see the next section, found within the hour of writing the paragraph
above.**

## Follow-up 2 (same day) — retraining PGO to actually cover the FMV
segment is a real, confirmed, substantial win — found by directly asking
"is there a pre-process that could help?"

The user asked a plain question after the above was written: *"is there
anyway we can do a pre-process to make the FPS better?"* Three real
options exist (pre-warming the overlay cache before the player's first
session; pre-decompressing the FMV's own asset data, which would need
reverse-engineering `0x0010C89C`'s bitstream format first and wasn't
attempted; and retraining PGO). The third was cheap, already-proven
infrastructure in this project, and testable immediately — so it was
tested rather than just proposed.

**Why the existing PGO profile was suspect**: this project's PGO
training defaults to `train_secs=60, train_runs=2` from a cold,
deterministic boot with no controller input (no `[pgo]` override in
`game.toml`). Given established boot timing throughout this whole
project (title screen and the rotating intro typically don't get reached
until 20-40+ real seconds in), a 60-second training window quite
plausibly barely touched the FMV's own hot loops — including
`0x0010C89C` itself — meaning the compiler's profile-guided branch
layout/inlining decisions were optimized for boot/menu code, not for the
exact content this whole investigation has been about.

**Retrained with `train_secs=100, train_runs=1`** via
`psxrecomp_cli.py pgo-train` — long enough to carry well past FMV start.
Hit two real process snags worth recording: (1) the pipeline's instrumented
("generate") phase completed and produced a fresh `default.profdata`, but
stopped there instead of automatically continuing to the "use" rebuild —
had to finish that step manually (`cmake -S . -B build-release
-DPSX_PGO=use` + rebuild); (2) that same reconfigure carried
`PSX_DEBUG_TOOLS=ON` forward from the training pipeline's own instrumented
build (this project's own `pgo-train-fix` finding from early on
already documented this exact gotcha — cache variables persist across
reconfigures unless explicitly overridden) — fixed with an explicit
`-DPSX_DEBUG_TOOLS=OFF` reconfigure before the final measurement.

**Result — measured twice, independently, both launches from cold boot,
compared at identical frame-count positions against this document's own
just-established ~50-54fps baseline** (same content position, ~frame
2400-2520 into the boot FMV):

| | Before (existing PGO profile, boot-only coverage) | After (retrained, FMV-inclusive) |
|---|---:|---:|
| FPS at frame ~2400-2520, run 1 | 52.7-54.1 | 58.3-59.9 |
| FPS at frame ~2400-2520, run 2 (repeat) | — | 57.5-59.6 |

**A real, reproducible, substantial improvement — roughly +6 to +8 FPS
(+12-15% relative) at the same content position, confirmed across two
independent cold-boot launches**, not a single noisy sample. This is
well outside the ~5-8% run-to-run noise band this same document
characterized just before this follow-up — that band tops out around
2-3fps at these frame counts, not 6-8. Several stretches of the FMV in
both retrained runs now sit at or above 59fps, i.e. essentially full
native speed, where the pre-retrain baseline never exceeded ~55.

**This directly changes this document's own "very unlikely to be pushed
further by anything recompiler-side" claim above — that conclusion was
correct about codegen-level changes (WO-10/WO-11's bookkeeping-batching
idea) but wrong to imply nothing build-side was left on the table.**
Retraining PGO isn't a recompiler code change at all — it's a build-time
pre-process, exactly what the user asked about — and it moved the needle
by an order of magnitude more than anything measured elsewhere in this
whole arc. **This is now the standing recommendation for anyone asking
"how do we get more FMV FPS" from this project's findings**: retrain PGO
with training coverage that actually reaches the content you care about,
before reaching for a recompiler-level change.

**Not yet done**: a rigorous multi-trial statistical treatment of this
specific result (this doc has been careful elsewhere about single-sample
claims) — two independent full-launch confirmations at a consistent
frame-count position is stronger evidence than anything else in this
document's tables, but not the same as N≥8 trials with variance reported.
Also not yet done: retraining with `train_runs=2` (the framework default)
or a longer duration to see if coverage further into the game (past FMV,
into actual gameplay) helps or hurts other content's performance — this
result is specifically about the boot-intro FMV segment.

## Follow-up 5 (same day) — Follow-up 4's "LTO causes a performance
collapse" claim does NOT hold up under a matched, controlled retest.
Read this before treating Follow-up 4 as settled.

Follow-up 4 (below) concluded LTO caused a severe performance collapse
(guest Hz into the 20s-30s, 11,179 revalidation attempts) at the
gameplay→menu savestate transition, based on comparing two sessions that
were **not actually matched** — different accumulated overlay/game state
between the LTO-on run (reached via extended live play) and the LTO-off
run (a single clean savestate load). That gap wasn't caught at the time.

**Redid it properly**: same two savestate files, same fresh-boot
starting point, same exact `load slot0 → load slot1` sequence, timed
`overlay_loader_status` samples over a 4+ second window immediately
after, for both LTO-off and LTO-on back to back in the same investigation
pass.

| | reval_attempts delta | Resolved by | Performance |
|---|---:|---:|---:|
| LTO-off | +15 | first ~0.2s sample | steady 60fps throughout |
| LTO-on | +7 | first ~0.2s sample | steady 60fps throughout |

**No storm, no collapse, on either build, for this controlled
transition.** LTO-on's count is even slightly *smaller* than LTO-off's.
The visual corruption (see `savestate-menu-vram-glitch.md`) reproduced
identically on both — confirming again that it's independent of LTO —
but the severe performance regression from Follow-up 4 did **not**
reproduce under matched conditions on either side.

**Corrected conclusion**: Follow-up 4's performance-collapse finding is
not confirmed and should not be cited as an established LTO bug. The
most likely explanation for what was originally observed is that the
LTO-on session at the time had accumulated a much larger amount of
resident overlay content (from extended live play — FMV, gameplay,
multiple room transitions) than the matched retest's minimal
fresh-boot-plus-two-loads scenario, and that *volume* of resident
candidates — not LTO specifically — determines how large the mandatory
post-restore catch-up cost is. This was not confirmed either (no
LTO-off run with an equally large resident-overlay set was tested), so
it remains a hypothesis, not a finding — but the specific claim "LTO
causes this" is retracted for lack of reproducing under a fair
comparison. `savestate-restore-lazy-revalidation-race.md` (written
between Follow-up 4 and this correction) already correctly hedged this
as "not yet confirmed" rather than settled; this follow-up formalizes
that the matched test then run did not support it.

**Practical upshot**: there is currently no confirmed reason to keep LTO
disabled. The FMV-only win from Follow-up 3 stands; the visual glitch is
a separate, LTO-independent issue tracked in
`savestate-menu-vram-glitch.md`/`savestate-restore-lazy-revalidation-race.md`.
Whether to re-enable LTO now that its specific performance objection
didn't hold up is a call for whoever owns this build going forward — not
re-decided unilaterally here since the user had asked to hold off on it
this session for reasons beyond just this one performance claim.

## Follow-up 4 (same day) — RETRACTED (see Follow-up 5 above): the claim
that LTO causes a severe performance stall once you actually play past
FMV did not reproduce under a matched retest. Kept below for the
record — do not cite its performance conclusion.

Follow-up 3 recommended `-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON` based on
FMV-only measurements. The user then actually played on that build and
hit a real, reproducible bug the FMV-only testing never could have
caught: navigating New Game → through the FMV → into gameplay → back to
the title/New-Game-select menu produced **severe on-screen static/noise
corruption across the entire background** (the New Game/Continue/Tutorial
text box itself rendered fine — it's a separate draw layer — but
everything behind it was corrupted), alongside a real performance
collapse (guest Hz falling into the 25-37 range, `dirty_ram` interpreter
throughput spiking to 1.2-1.7M insn/s, and `overlay_loader_status`
showing `reval_attempts` in the thousands — 11,179 in one capture — with
`reval_crc_miss: 0` every time, meaning something was repeatedly
triggering full code-revalidation checks on the RoomLib overlay region
via writes to co-located data (`last_write_pc=0x8007BFF0` →
`0x0018F958`) without the underlying code ever actually changing).

**Isolated directly, not guessed**: used the exact savestate the user had
already made at this precise screen to jump back to it instantly (no FMV
replay needed) and rebuilt with `-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF`
(PGO kept). Same savestate, same screen: **clean, correct rendering,
100% RT, 60fps, `dirty_ram` interp throughput back to 0, zero
revalidation storm.** LTO on vs. off, identical everything else, is the
only variable that changed between the corrupted and clean result.

**Root cause not identified** — only isolated to LTO as the trigger for
the *performance* half of what was observed. The leading hypothesis, not
yet confirmed: LTO's more aggressive cross-translation-unit
inlining/reordering exposed a pre-existing correctness bug (undefined
behavior, a strict-aliasing violation, or an ordering assumption between
the dirty-RAM write tracker and whatever writes `0x0018F958`) that a
normal per-TU build's weaker optimization never triggered. **This is why
Follow-up 3's FMV-only measurement missed it entirely**: FMV never
exercises this code path, so a change that's completely safe for FMV can
still be actively unsafe once you go past it into actual gameplay — a
real, concrete lesson about the limits of testing one content segment and
generalizing "safe" to the whole game.

**Correction, found within the same live session — this is actually TWO
separate bugs, not one.** Further testing (switching between two
user-made savestates, one mid-gameplay and one at the menu) reproduced
the *visual* corruption again on the LTO-OFF build, with **no
performance impact at all** (steady 60fps, `dirty_ram` interp at 0,
`revalidations` at 0 the whole time) — direct proof the background-static
glitch is NOT caused by LTO. A follow-up screenshot taken moments later,
once the game had advanced past that static menu into real FMV content,
showed clean, correct rendering again — the corruption is a **single
static frame's stale background, not a persistent state**, and it clears
itself the moment new content actually renders. So:

- **The LTO-specific bug** (real, cleanly isolated above): a severe
  performance collapse — the revalidation storm, guest Hz into the
  20s-30s — present only with LTO on. Fixed by keeping LTO off.
- **A separate, pre-existing, cosmetic bug** (not caused by LTO, not
  investigated further this round): a stale/wrong background image
  appears at this specific menu after a savestate-driven scene
  transition, self-clearing once the game advances to new content. Likely
  the same general class of bug as this project's older, still-unresolved
  `video-bleed-through-splash.md` finding (stale VRAM/frame content
  surviving an abnormal transition) — worth revisiting that finding's
  methodology (`vram_peek`/`gl_fbo_peek` comparison around the transition)
  if this cosmetic issue is ever prioritized, but out of scope for
  tonight's LTO investigation.

**Corrected standing recommendation: PGO (FMV-inclusive retrain from
Follow-up 2) alone, LTO OFF.** `build-release` has been rebuilt with LTO
disabled and confirmed clean at the exact screen that broke. Do not
re-enable `CMAKE_INTERPROCEDURAL_OPTIMIZATION` without first bisecting
which specific translation unit(s)/functions LTO is mis-optimizing and
understanding why — Follow-up 3's own text below is left in place
for the record (what was tried, what looked good in FMV-only testing)
but its recommendation is superseded by this correction.

## Follow-up 3 (same day, SUPERSEDED — see Follow-up 4 above before
acting on anything in this section) — user asked "any other
pre-processing to help FMV?"; enabling LTO on top of the retrained PGO
profile looked like it finished the job — FMV now runs at essentially
full native speed throughout

Checked for one more concrete, checkable build-time lever before
proposing anything speculative: **Link-Time Optimization was not enabled
anywhere in this project** — no `CMAKE_INTERPROCEDURAL_OPTIMIZATION`, no
`-flto`, in either the top-level `CMakeLists.txt` or
`psxrecomp/runtime/CMakeLists.txt`, confirmed by grep and by its total
absence from `CMakeCache.txt` before this change. Notable given the sheer
number of separately-compiled translation units this project links into
one binary (60+ generated `SLUS_006.62_full_*.c` shards alone, plus the
whole runtime and `recomp-ui`) — exactly the shape of codebase LTO
benefits most, since without it none of those units' functions can be
inlined into each other or have dead code eliminated across the boundary.

**Enabled it** (`cmake -S . -B build-release
-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`, no CMakeLists.txt changes
needed — modern CMake applies this as a global default across all
targets), on top of the just-retrained, FMV-inclusive PGO profile from
Follow-up 2 above. Full rebuild (235 steps instead of 212 — LTO adds
its own optimization/codegen objects — plus a slower link step), no
errors.

**Result — measured twice, independently, same frame-count methodology as
every other trial in this document:**

| | Frame ~2400-2500 FPS |
|---|---:|
| PGO retrained only (Follow-up 2) | 57.5-59.9 |
| PGO retrained + LTO, run 1 | 59.1-60.9 |
| PGO retrained + LTO, run 2 | 58.7-61.4 |

**This isn't a narrow improvement at one content position — it's the
whole picture.** Sampling *every* `[FPS]` line across both full runs,
from frame ~550 (right after the FMV's own cold-capture settles) through
frame ~3100, shows a sustained band of **58.5-61.4fps for the entire
sequence**, both runs, no exceptions — i.e. **essentially full native
59.94Hz throughout the boot-intro FMV**, where the pre-Follow-up-2
baseline sagged into the low 50s and the very first measurements in this
whole investigation arc (months of work, `fmv-frame-stall.md` onward) saw
lows in the 40s and stall spikes to 134ms.

**Caveat on attribution**: this test adds LTO *on top of* the already-
retrained PGO profile — it was not tested against the old (boot-only)
PGO profile, nor with LTO alone and PGO off, so this result is properly
read as "PGO-retrain + LTO together" rather than isolating how much of
the jump from Follow-up 2's ~58fps to this ~60fps is LTO's own
contribution versus a second-order interaction with the same profile.
For the practical recommendation this distinction doesn't matter — ship
both together — but don't cite an "LTO added exactly N fps" number from
this document, since that specific isolation was never run.

**Standing recommendation updated again**: `-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`
alongside an FMV-inclusive PGO retrain (Follow-up 2) is now the combined
answer to "how do we get more FMV FPS" — found entirely through build
configuration, zero source changes, in direct response to the user asking
whether any pre-process could help. `build-release` is left in this
state (PGO=use with the FMV-inclusive profile, LTO on, debug tools off)
as the new working baseline.

**Not yet done**: checking whether LTO measurably affects build time
enough to matter for iteration speed (this rebuild was noticeably slower
than a non-LTO one, unmeasured precisely); confirming LTO doesn't
regress non-FMV content (menus/gameplay were already fast and headroom-
free per earlier findings, so a regression there seems unlikely but
wasn't checked); and the still-outstanding item from Follow-up 2
(isolating LTO's own contribution, and whether `train_runs=2` or a
longer/broader training window helps further on top of this).

## Recommendation

**Don't ship this as a performance fix based on what's measured here** —
the mechanism is real, correctly implemented, and low-risk by
construction for this address, but it did not demonstrate the win WO-10
hypothesized. Worth two follow-ups if this is picked up again, in order
of cost: (1) a cheap first check — directly time the actual callback
bodies (`icache_fetch`, `check_interrupts_at`'s real implementations) in
isolation to see whether they have a fast path this whole approach is
correctly bypassing nothing expensive from, which would explain the null
result outright; (2) if those turn out non-trivial, redo the A/B with a
savestate-anchored trial design and enough repetitions to trust the
numbers, on hardware without a thermal ceiling if available.

## State left in the tree

`code_generator.h`/`.cpp`'s changes are real, working, and left in place
(both flags default OFF — zero effect on existing builds). All temporary
debug instrumentation added while diagnosing the predecessors bug (the
file-based `PE_LOOPS`/`PE_TBB_HIT` dumps) has been removed. The
`0010B000_7238DF29` region's cache entry (DLL/ranges/generated source) was
deleted after testing so a normal autocompile-enabled launch regenerates
a clean production copy — verified: relaunched with autocompile on, both
flags unset, confirmed normal ~52-55fps FMV numbers and no leftover
artifacts before writing this up.
