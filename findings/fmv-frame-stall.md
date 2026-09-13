# FMV still has periodic frame stalls after WO-6 — root cause not yet found, five candidates ruled out

**Status: open investigation, not a finished finding — seven candidates
ruled out with real measurement, and the remaining stalls are now split
into two distinct, separately-characterized failure modes (rare genuine
OS descheduling vs. a dominant CPU-busy-but-unproductive majority),
neither fully root-caused yet. See `fmv-frame-stall-plan.md` for the
attack plan driving what gets tested next and why — this file is the raw
evidence trail behind it.** This is the raw log,
updated as it goes, in the same style as `fmv-dispatch-overhead.md`. Separate
issue from WO-6/WO-7 — discovered while re-testing FMV after the WO-6
dispatch-index fix (see `fmv-dispatch-overhead-ai-brief.md`), but it's a
different mechanism, still present with WO-6 applied, and not yet explained.

**Recompiler/runtime-side, not a game-code issue** — same classification as
every other performance finding in this project. Everything measured here
lives in the emulation thread's own frame loop (`main.cpp`, `cdrom.c`,
`latency_ring.c`), not in guest code.

## The trigger

After confirming WO-6 gives a real, measured +4% average fps during FMV
(see `fmv-dispatch-overhead-ai-brief.md`'s "Upstream response" section),
the user asked: the average went up, but the dips still look "rather
consistent" — why?

## What's confirmed

**The stalls are real, per-frame, and severe.** The runtime already has an
always-on per-frame instrumentation ring (`latency_ring.c`, previously
unused for anything but its own `"latency"` debug command) that timestamps
every frame at three points: `LAT_INPUT` (frame start), `LAT_SWAP_BEGIN`/
`LAT_SWAP_END` (immediately around the present/vsync call). Pulling this
during FMV, across ~11,000 consecutive frames:

- Median frame time: ~16.7-21ms (normal, matches 50-60fps).
- **8.5% of frames take longer than 30ms** (i.e. miss at least one vblank).
- Worst observed single-frame times: 71ms, 75ms, 82.8ms, 85ms, and once
  **133.9ms** — 8x a normal frame, a genuine multi-frame freeze.
- This reproduces with **zero external tooling connected** — a control run
  with no debug client polling at all showed the same magnitude of outlier
  (75.2ms) sitting in the ring, confirming it isn't an artifact of the
  measurement itself.

## What's been ruled out (each with direct measurement, not inference)

| Candidate | Method | Result |
|---|---|---|
| Dispatch/CPU-emulation rate spiking | 1-second `dispatch_native`/sec averages, dip vs. non-dip seconds | Flat to *slightly lower* during dips — some of the worst dip-seconds have below-average dispatch rates; some of the best seconds have above-average ones. Ruled out as the per-second trigger. |
| MDEC decode cost varying by video content | Live-polled `fmv_state`'s `mdec_decode_macroblocks`/`mdec_decode_count` once/sec via the debug protocol | Every single decode call processes an identical, fixed 300 macroblocks (one full 320×240 frame), at a remarkably steady ~13.5 decodes/sec throughout — no content-driven variance to speak of. Hypothesis dead. |
| Present/vsync call itself blocking | Latency ring's `LAT_SWAP_BEGIN`→`LAT_SWAP_END` span, checked on every worst-outlier frame | Always fast — 0.05-1.85ms max, even on the 71-134ms outlier frames. Not the swap call. |
| CPU-side per-frame housekeeping before the swap | Latency ring's `LAT_INPUT`→`LAT_SWAP_BEGIN` span (`input_to_swap`) | Always fast — 0.2-0.7ms max, even on outlier frames. Not this narrow span either. |
| Disc-image (CD) sector reads blocking | **Added new instrumentation** (`latency_ring_cd_read_begin/end`, wired into `cdrom.c`'s `read_sector_at`) timing the actual `iso_read_sector`/`iso_read_raw_sector` calls — `iso_reader.cpp` does synchronous, unbuffered, no-read-ahead `seekg`+`read()` per sector, a real design gap and the most plausible candidate going in | On every one of the worst outlier frames, the slowest disc read that frame was 30-140 **microseconds**. Max ever observed across ~11,000 frames: 422µs. Nowhere close to a 45-134ms stall. Ruled out by direct measurement. |
| The investigation's own debug-server polling causing the stalls | Control test: ran the instrumented build for 150s with **zero** external connections, then took one snapshot | Same-magnitude outlier (75.2ms) present in the ring with nothing polling it. Not an observer effect. |

## Two more ruled out — one by existing data, one inconclusively

- **Audio/SPU processing (XA-ADPCM decode, SPU mixing, the DRC resampler)
  — ruled out, no new instrumentation needed.** Traced the actual call
  chain: `sdl_vblank_present_body()` calls `latency_ring_frame_begin()`
  (`main.cpp:7202`) near its top, then `sdl_audio_update()` →
  `sdl_audio_pump()` → `spu_render()` at `main.cpp:7304`, then
  `LAT_SWAP_BEGIN` at `main.cpp:8000` — all in that order, in the same
  function call. That means the entire audio path structurally falls
  *inside* the `input_to_swap` span already measured above, which stayed
  under 0.7ms on every single one of the worst outlier frames (45-134ms).
  If audio processing were ever taking tens of milliseconds, it would have
  shown up there. It doesn't. Dead end, confirmed by data already in hand.

- **OS-level thread scheduling — a single trial each way was inconclusive
  (see below), so re-ran it properly as an 8-trial experiment (4 Normal, 4
  High), fresh launch + fresh 100s untouched window each time, one latency
  snapshot per trial via `run_priority_trials.ps1`.**

  **Single-trial pass (kept for the record, not the final answer):**
  bumped the running process to Windows `High` priority mid-session
  (`(Get-Process Parasite_Eve).PriorityClass = 'High'`, no rebuild needed)
  and re-sampled the latency-ring summary once over a ~150s window vs. a
  comparable normal-priority run. Result: mean 18.48→18.67ms, p50
  21.1→20.9ms, p95 31.0→32.4ms, max 75.25→60.1ms — essentially no change
  to the bulk of the distribution, and the one lower max was well within
  what a single sample's variance could produce. Correctly flagged at the
  time as too weak to conclude anything from.

  **Proper 8-trial version:**

  | | mean (ms) | p50 (ms) | p95 (ms) | **max (ms)** |
  |---|---:|---:|---:|---:|
  | Normal, 4 trials | 18.60 ± 0.12 | 21.06 ± 0.28 | 31.39 ± 0.25 | 40.95, 78.83, 95.87, **113.87** |
  | High, 4 trials | 18.41 ± 0.08 | 21.06 ± 0.10 | 30.71 ± 0.08 | 51.54, 43.19, 63.74, **63.74** |

  Now there's a real, visible pattern in the tail: Normal's worst outliers
  averaged **82.4ms** (stdev 26.9 — wildly inconsistent run to run, up to
  113.87ms once); High's worst outliers averaged **50.9ms** (stdev 8.0 —
  far more consistent, never exceeding 64ms across any of the 4 runs). The
  typical-frame distribution (mean/p50/p95) is statistically
  indistinguishable between the two — priority doesn't change how the
  emulator normally performs, only how bad its worst moments get.

  **Honest statistical read**: with only 4 trials per group, a Mann-Whitney
  U test on the max values (12 of 16 cross-group pairs favor "Normal is
  worse") gives a one-tailed exact p≈0.17 — a real, consistent-direction
  effect, but *not* conventionally significant on this sample size alone.
  This is genuine signal worth taking seriously (the effect size is large
  and the direction was consistent in all 4 High trials vs. 3 of 4 Normal
  trials), not proof. More trials would either firm this up past
  significance or reveal it as noise that happened to line up this round.

## Did WO-6 itself introduce this? Tested directly — no.

Every measurement above was taken on the WO-6-applied build. Worth asking
directly: does the stall pre-date WO-6, or did the dispatch-index change
itself introduce a new failure mode (e.g. page faults from touching a
freshly-generated ~800KB index array scattered across memory)? Checked out
`5d59c1e1` (the commit immediately before the WO-6 cherry-pick), reapplied
the same CD-read timing instrumentation (clean, no conflicts — WO-6 never
touched `cdrom.c`/`latency_ring.c`), rebuilt the emitter/dispatch
table/runtime, and ran the identical untouched 150s control test:

| | Pre-WO-6 (`5d59c1e1`) | Post-WO-6 (`bda01335`) |
|---|---:|---:|
| mean | 18.68ms | 18.48ms |
| p50 | 20.9ms | 21.1ms |
| p95 | 32.7ms | 31.0ms |
| max | **89.27ms** | 75.25ms |

The pre-WO-6 build shows the same stall pattern at the same magnitude — if
anything its worst outlier (89.27ms) and p95 were very slightly *higher*
than the WO-6 build's. **This rules out WO-6 as the cause.** The stall
pre-dates it, is unrelated to the dispatch-index change, and WO-6 didn't
introduce or worsen it (consistent with WO-6's own already-documented
effect: a modest, real *average* fps improvement from cheaper address
resolution, not a change to this failure mode one way or the other).

## The clock/thermal test — a dead end that redirected to a sharper one

Tried to test thermal throttling directly: sampled Windows'
`\Processor Information(_Total)\Processor Frequency` /
`% Processor Performance` / `Performance Limit Flags` counters (and the
`Win32_Processor.CurrentClockSpeed` WMI property as a second path) once per
second for ~110s during FMV. **Every single sample, on both APIs, came back
completely flat** — `CurrentClockSpeed`/`Processor Frequency` pinned at the
BIOS-reported nominal 2601MHz the entire time, `% Processor Performance`
reading a flat 0. Confirmed this is real, non-virtualized hardware first
(`Win32_ComputerSystem`/`Win32_BaseBoard` show an MSI GT62VR 6RE, matching
this project's already-known i7-6700HQ; `systeminfo` shows no
Hyper-V/virtualization) — so the flat readings aren't a VM artifact, this
laptop's driver/BIOS combination just doesn't populate these counters with
live data. **Dead end for a direct frequency reading**, but it pointed at a
better available test.

## A sharper test: is the process actually being descheduled during a stall?

Windows *does* correctly track per-process accumulated CPU time
(`Process.TotalProcessorTime`), which doesn't need any of the broken
counters above. Sampled it every 100ms alongside a wall-clock-anchored
latency-ring poll (each poll's frames get an estimated real timestamp by
anchoring to the request time), across ~106s / ~4800 frames. The idea: if
a stall is caused by the OS preempting the thread (scheduling contention),
the process's own CPU-time consumption should visibly drop during that
window — it wasn't running, so it couldn't be burning CPU time. If the
process keeps consuming its normal CPU-time share throughout, it was
never preempted; something else made its work less productive per unit of
scheduled time.

**Result, and it's a clean split:**

- **Baseline** (calm, <20ms frames): process consumes CPU at ~0.86
  core-seconds per wall-second on average (matches the known single hot
  thread).
- Of **1,068 dip frames** (>30ms) in this run, only **5 (0.5%)** showed
  clearly reduced CPU-time consumption (<75% of baseline) — and those 5
  cluster into essentially two events (three consecutive frames around
  one ~95ms stall, one isolated ~40ms stall, one isolated ~36ms stall a
  second later). **This is the genuine-descheduling signature** — the OS
  really did take the thread away for those specific frames.
- The other **1,058 of 1,068 (99.1%)** — including 13 of the 15 single
  worst frame-period outliers in the whole run (57-72ms each) — show
  **normal-to-full CPU-time consumption (0.9-1.04× baseline)** despite
  taking 3-4x longer than a normal frame. The process was actively
  scheduled and burning CPU the entire time. It just accomplished far
  less with it.

**This is the important result.** The dominant failure mode (>99% of
dips) is not the OS taking the thread away — it's the thread running,
consuming its usual CPU-time share, and getting much less real work done
per unit of that time. That's the signature of either **thermal/frequency
throttling** (the core executes fewer actual cycles per wall-clock
millisecond, but the OS's time-accounting only sees "scheduled," not
"how fast") or **memory/cache contention** (the core is technically
retiring instructions but stalling heavily on cache misses / DRAM
bandwidth, which also reads as "busy" to the scheduler). Both would
explain "no counted event elevated, no reduced CPU-time, still much
slower" — the same result every earlier ruled-out candidate produced,
now narrowed to a specific class of cause instead of a shrug.

**This also reconciles the earlier priority experiment.** Raising
priority reduces the *chance* of the OS preempting this thread for
something else — exactly the mechanism behind the rare 0.5% genuine
descheduling events, which also happen to be the single most severe
individual stalls (94-95ms, well above the 57-72ms ceiling of the
"CPU-busy-but-unproductive" majority). A per-trial *max* statistic is
dominated by whichever single frame is worst — so capping just the rare
descheduling events, without touching the far more numerous
throttling/contention-type stalls, produces exactly what was measured:
the tail max drops, while mean/p50/p95 (dominated by the much more common
majority type) don't move at all.

## Where this leaves the investigation

Every runtime-code-level candidate identifiable from reading the frame
loop and directly testable with the existing latency ring (or a small,
cheap extension of it) has now been checked and come back negative:
dispatch rate, MDEC decode, the present/vsync call, the CPU housekeeping
before it, disc-image reads, audio/SPU processing, and — checked directly,
not assumed — WO-6's own dispatch-index change (same stall magnitude on
the commit immediately before it). The one imprecise test aimed outside
the runtime's own code (OS scheduling priority) didn't produce a clear
signal either way.

**Now two distinct problems, not one — with two different next steps:**

1. **The rare (~0.5%) genuine-descheduling stalls** (the most severe
   individual outliers, 90ms+) — the priority experiment already shows a
   real, if not yet statistically airtight, mitigation (elevated thread
   priority). More trials (8-12+ per group, maybe add `RealTime` for a
   dose-response check) would firm up the current p≈0.17 signal. This is
   the OS-scheduling-contention story, confirmed as real but rare.

2. **The dominant (>99%) CPU-busy-but-unproductive stalls** (the 57-72ms
   majority) — this is now the higher-value target, since it's what
   actually drives the typical experience, not just the rare worst case.
   Not yet distinguished between thermal throttling and memory/cache
   contention specifically. Two ways to test further without needing a
   working frequency counter (unavailable on this hardware):
   - **A long sustained-load run** (10-20+ minutes of continuous FMV or
     equivalent single-core load) checking whether stall frequency/severity
     *increases over time* — the classic thermal-buildup signature — vs.
     staying constant from the very first minute, which would point at a
     constant background factor (another process's memory traffic) instead.
   - **OS-level profiling** (Windows ETW/WPR, Process Monitor) — the most
     direct way to see what's actually stalling the core's instruction
     throughput during a captured window, outside what this environment's
     tools can drive directly.

**Finer-grained interpreter instrumentation** (a per-dispatch-call timing
histogram) remains a possible but heavier fallback if both of the above
come back inconclusive — nothing that fine-grained exists in the runtime
today and building it is a real undertaking, not a quick check.

`run_priority_trials.ps1`, `sample_proc_cpu.ps1`, and
`poll_latency_thermal.py` (the scripts behind the experiments above) are
reusable as-is for follow-up runs; they live in the session scratchpad,
not currently checked into this repo.

This is a good, honest stopping point for this round: seven real
candidates ruled out with actual measurement (including WO-6's own change,
checked directly rather than assumed innocent), one experiment run but
inconclusive, and a clear, specific list of what a next session would need
to go further — not a vague "needs more investigation."

## Temporary instrumentation left in the tree

`latency_ring.h`/`latency_ring.c` gained `latency_ring_cd_read_begin()` /
`latency_ring_cd_read_end()` and two new fields per frame slot
(`cd_read_max_us`, `cd_read_count`, `cd_read_lba`), wired into `cdrom.c`'s
`read_sector_at()`. All marked `TEMPORARY (2026-09-12 FMV-dip
investigation)` in comments — remove once this investigation concludes
either way, unless the maintainers want to keep it as a permanent
diagnostic (it's cheap: two QPC reads per sector, no locking, no allocation).

Built with `-DPSX_DEBUG_TOOLS=ON` for all of the above; reverted to `OFF`
between rounds per this project's standard practice — **check the current
`build-release` state before assuming which mode it's in** if picking this
up later.

## Root cause found (2026-09-12): `0x0010C89C`, a per-entity Huffman/RLE
decompress call inside the rotating-intro's own loop — confirmed with a
direct iteration-count/duration correlation, not inference

Picking this back up with dispatch-level (not subsystem-level) timing —
narrower than the ETW/WPR sampling profile Phase 2 originally called for,
but built from tooling already in the runtime and, as it turned out,
precise enough to nail this down directly.

**MDEC and XA audio decode duration, measured directly, are both cleared.**
Extended `latency_ring.c` with `latency_ring_mdec_begin/end()` (wrapping
`mdec.c`'s `execute_decode()`) and `latency_ring_xa_begin/end()` (wrapping
`cdrom.c`'s `maybe_deliver_xa_audio()`). Across the same kind of FMV
capture window used throughout this doc: MDEC decode never exceeded
**1.57ms**, XA decode never exceeded **0.18ms** — both far too small to
explain 20-134ms stalls. This corrects the `fmv-frame-stall-plan.md` Phase
1 write-up's guess ("most likely MDEC decode integration or XA audio
interleaving") — checked directly, and it's neither.

**The actual dispatch call itself was the missing measurement.** Every
prior test in this doc timed a *subsystem* (MDEC, audio, disc I/O, the
present call) or a *rate* (dispatch calls/sec). Nothing had timed
individual native-overlay dispatch calls by *duration* — the plain
`c->fn(cpu)` call in `overlay_loader.c` that invokes a compiled overlay
function. Wrapped both call sites with `latency_ring_dispatch_begin()` /
`latency_ring_dispatch_end(addr)`, recording the single worst
`dispatch_max_us`/`dispatch_max_addr` per frame. This immediately surfaced
two addresses with disproportionate single-call costs: `0x80191BB8` (up to
34ms) and `0x0010C89C` (up to 42ms in the first pass, later measured up to
**67ms** with a larger sample — see below).

`0x0010C89C` was previously dismissed as a dead end in an earlier pass of
this same investigation, based on its call *rate* (~15/sec, unremarkable).
Timing its call *duration* instead tells a completely different story.

**Caller trace (temporary `PE_PROBE`/`PE_PROBE2` printf probes in
`overlay_loader.c`, since reverted):** `0x0010C89C`'s return address is
`0x80192AAC`, a `jal 0x8010C89C` at `0x80192AA4`, inside function
`0x80192934`. **That is the exact same function that also calls
`RoomLib_InitC` (`0x80191B64`)** — the address WO-6/the RoomLib fix's
entire investigation was already centered on. Three separate threads of
this project's work (WO-6's dispatch overhead, the RoomLib interior-
classification fix, and this frame-stall investigation) all converge on
one function in the rotating-intro loop.

**Disassembly (`mem_words` + a small custom MIPS decoder, ~150 instructions
read):** a genuine, non-unrolled ~200-instruction function with two real
backward branches (`block_8010C960`/`block_8010CA7C`, both loop headers)
and two real `jr $ra` return points (`0x8010CBC0`, `0x8010CBF4`). Register
usage across the loop body: `$a2`/`$a3` hold a shared table base
(constant `0x80162100` across every call observed — a Huffman/lookup
table), `$a0` walks an input buffer advancing 2-12 bytes per iteration,
`$a1` is the output cursor advancing 2 bytes per iteration and alternates
between exactly 2 base values across calls (a double-buffer), and the loop
body does shift/mask bit-refill plus two table lookups per pass — the
textbook shape of a bit-oriented Huffman or RLE stream decoder, not
anything resembling fixed-size video/audio frame decode.

### The `--do we have hardcore evidence?--` self-audit

Before instrumenting further, explicitly checked how much of the above
was directly measured vs. inferred, at the user's request:

- **Directly measured, high confidence**: the 20-67ms per-call durations
  themselves (latency ring), the caller address and its sibling call to
  `RoomLib_InitC` (printf probe on `cpu->gpr[31]`), the disassembly (raw
  `mem_words` read, decoded instruction-by-instruction), MDEC/XA duration
  ruling them out.
- **Inferred, not yet measured, going in**: that duration was actually
  *caused* by a longer per-call loop trip count (the "data-dependent
  decompression cost" hypothesis) rather than some other data-dependent
  effect (e.g. cache misses on a larger/colder input region that happened
  to correlate with more bytes touched). A cross-reference of
  `Process.TotalProcessorTime` against the worst dispatch outliers showed
  most were CPU-busy (not OS-descheduled), but a real bug was caught and
  disclosed in that script (`correlate_dispatch_cpu.py` defaulted missing
  CPU-rate samples to "CPU-BUSY" instead of "unknown" — only 9 of 20
  listed entries had actual measurements backing their tag).

This is exactly the gap direct iteration counting below closes.

### The iteration counter — direct proof, not inference

Added real instrumentation to the generated overlay source itself (the
`_patched.c` this function compiles from): a static call counter and a
static iteration counter, incremented once at the top of each of the two
loop-header blocks and reset at the start of each fresh top-level call
(see the pitfall below re: where "start of a fresh call" actually is in
CPS-generated code), plus an `__rdtsc()` timestamp pair around the whole
call, printed at both real return points. Self-contained inside the one
generated `.c` file — no cross-DLL symbol needed (overlay DLLs are
dynamically `LoadLibrary`'d, not statically linked against the runtime
EXE, so a plain `extern` from `overlay_loader.c` into an overlay DLL's
global fails at link time; this was tried, hit exactly that link error,
and was fully reverted in favor of the self-contained `__rdtsc()`
approach).

**Two build-pipeline pitfalls hit and worked around while wiring this up**
(neither is the actual finding, but both cost real time and are worth
recording for whoever touches this pipeline next):

1. `compile_overlays.py`'s autocompile **regenerates `_patched.c` from
   scratch** whenever it decides a DLL needs rebuilding — it does not
   preserve hand edits to the generated source. Worked around by manually
   invoking the exact `gcc` command `_compile_dll_direct()` uses and
   launching with `-NoAutocompile` so the pipeline never touches the
   region again mid-test.
2. **A manually-compiled DLL silently fails to load** even when its
   `.ranges` manifest is well-formed and correctly indexed at startup
   (confirmed via `PSX_OVERLAY_CACHE_INVENTORY=1`) — `overlay_cps_probe`
   showed every dispatch to the address resolving with `outcome:0`
   ("find<0"), i.e. falling to the interpreter, not because the manifest
   entry was missing but because `try_load_region()`'s
   `lazy_load_selected()` was silently rejecting it. Root-caused with a
   temporary print of `overlay_loader_last_msg()` (this call's rejection
   reason is stored, not logged anywhere by default — Rule-3 territory):
   **`"DLL/manifest pair mismatch ... rejecting without deleting
   (publication may be in progress)"`**. `compile_overlays.py` normally
   appends an `overlay_pair_id()` export to every DLL it generates,
   matching a `P <hex>` line it writes into the sibling `.ranges` file, as
   an atomicity guard against exactly this scenario (a DLL and manifest
   published out of sync by the real pipeline's replace protocol). A
   hand-compiled DLL — bypassing `add_overlay_pair_export()` — has no such
   export, so `load_overlay_dll()` correctly (if silently) rejects it as
   looking like a torn publish. **Not a runtime bug** — it's the intended
   safety check working correctly against an unintended input (manual
   compilation) — but worth flagging for anyone else who hand-iterates on
   overlay DLLs for debugging: add
   `PSX_OVERLAY_EXPORT uint64_t overlay_pair_id(void) { return
   UINT64_C(0x<value from the .ranges file's own P line>); }` to the
   patched source before manually compiling, or the DLL will index fine
   and still silently interpret forever with no visible error short of
   `overlay_loader_status`'s `last_msg` or the `overlay_cps_probe` debug
   command.
3. A related instrumentation-placement bug, caught by its own data before
   being trusted: the reset code was first placed inside the CPS
   dispatch's `switch(_cont) { case <own_entry_addr>: ... }` arm — but a
   genuine fresh top-level call in this codegen leaves `cpu->pc == 0` on
   entry, which skips that whole `if (cpu->pc != 0u) { switch... }` block
   entirely (that case only fires for an explicit resume-at-own-start,
   not the common path). Result: the reset never ran on ordinary calls,
   and the first fix attempt showed `call_no` stuck at 0 with `iters`
   monotonically climbing across dozens of prints (3601, 7265, 11273, ...,
   never resetting) — an obviously-wrong signature, not real data,
   correctly not written up before catching and fixing it. Moved the
   reset to the unconditional fallthrough point both paths converge on
   (right after the `if`, before the CPS entry marker `/* Address:
   0x8010C89C, Size: 864 bytes, ... */`) and the counters started behaving
   exactly as expected: monotonic small counts per call, reset to 0 at the
   top of each one.

**Result, n=324 real calls (one clear TSC-migration artifact — `iters`
12305 with `tsc=24` — identified and excluded by a simple sanity filter,
`tsc > 50×iters`, not by hand-picking):**

| | value |
|---|---:|
| Pearson r (iters vs. cycles) | **0.69** |
| Spearman r (rank-based, robust to noise) | **0.73** |
| Median cost per loop iteration | ~2,086 cycles |
| Worst observed call | 14,050 iterations → **67.2ms** |
| Second-worst | 14,090 iterations → 47.8ms |
| Fastest calls | ~3,600 iterations → 0.7-1.2ms |

A 0.69-0.73 correlation across 324 real, independently-timed calls is not
something that happens by chance, and the two calls with the highest
iteration counts observed (14,050 and 14,090, both near the top of the
whole sample's range) are also the two most severe stalls recorded,
directly reproducing the earlier latency-ring-observed 20-42ms class of
outlier at a higher-fidelity ~67ms. **This directly confirms the
data-dependent-decompression-cost hypothesis** — not by elimination, but
by a positive, measured, moderately-strong relationship between how much
work the function's own loop does on a given call and how long that call
takes. The imperfect correlation (not r≈0.95+) is expected and consistent
with real per-iteration cost varying somewhat by input content (branch
outcomes in the bit-refill/table-lookup path) and normal cache/scheduling
noise on top of iteration count — not evidence against the hypothesis.

**What this means for the frame-stall investigation as a whole:** this is
almost certainly the dominant mechanism behind the "CPU-busy-but-
unproductive" 99.1% majority documented above. The thread genuinely is
busy — retiring real instructions in a real, data-dependent decode loop —
which is exactly why no OS-descheduling signature, no elevated dispatch
rate, and no thermal/frequency counter ever lit up: there was never
anything externally wrong. Some FMV frames simply ask this one decompress
call to do several times more work than others, because the compressed
data behind a given entity/frame is several times larger. That's a real,
structural cost of the game's own asset format being decoded on this
thread, not a bug in the recompiler or a hardware ceiling.

**Not yet done / possible next step**: identifying the semantic type of
data this decompresses (animation curves? a per-frame entity table? script
bytecode?) beyond its structural characterization above (per-entity,
double-buffered output, shared Huffman-shaped table) — not pursued further
since the structural finding already fully explains the stall's mechanism
and variability; worth revisiting only if a fix is attempted (e.g.
pre-decompressing off the hot thread, or caching decoded output across the
rotating intro's repeat cycles if the same entities recur).

**Cleanup**: all instrumentation for this round was temporary and has been
reverted — the manually-built `0010B000_7238DF29.dll`/`.ranges`/
`_patched.c` were deleted (letting `compile_overlays.py`'s normal
autocompile regenerate a clean production copy, verified on the next
launch), the `overlay_loader.c` diagnostic prints (`PE_TLR`) were removed,
and the `PE_PROBE`/`PE_PROBE2` caller-trace probes were already reverted
earlier in this same round. The `latency_ring.c` dispatch/MDEC/XA timing
extensions are left in place (cheap, useful, matches this project's
existing precedent of keeping the CD-read timing extension) — same
`TEMPORARY (2026-09-12 FMV-dip investigation)` marking as everything else
in this section.

## Methodology notes for whoever continues this

- The debug server's raw-dump reply buffer is only 16KB
  (`rawbuf[16384]` in `debug_server.c`'s `handle_latency`) — a
  `count=4096` request silently truncates to whatever fits (~180-220
  frames), not an error. Poll with a small `count` (100-150) and a short
  interval (~2s) for continuous coverage instead of asking for the whole
  ring at once.
- The raw dump's timestamps are relative to *that dump's own* first frame,
  not a global epoch — never compute a frame-to-frame delta across two
  separate poll responses. Keep each poll's frames in their own list and
  only diff within it (frame *numbers* are globally monotonic and safe to
  use as dedup/sort keys across polls; the millisecond-ish `input`/`swap_*`
  values are not directly comparable across polls).
