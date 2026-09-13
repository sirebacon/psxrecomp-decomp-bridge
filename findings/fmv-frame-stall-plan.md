# FMV frame-stall investigation — attack plan

Companion to `fmv-frame-stall.md` (the raw investigation log/evidence
trail). This file is the actionable plan: what we're testing, in what
order, and why — kept separate so it doesn't get buried under the log's
growing pile of individual test results.

## Why "hardware" is the explanation of last resort here, not the default

This project has **twice already** had a "this hardware just can't do it"
theory turn out to be wrong, replaced by a specific, findable, fixable
bug in the recompiler:

1. **The RoomLib interior-classification bug** — menus and the title
   screen ran at a fraction of full speed (idle-window `interp_share`
   measured at 93.6% — almost the entire frame running through the
   instruction-by-instruction interpreter instead of compiled native
   code) because the overlay capture's classifier never recognized a
   genuinely-executed address (`0x80191200`) as a function entry. Fixed
   with `--force-interior`. **Menus now sustain a stable 60fps on this
   exact same machine.** See `roomlib-0x80191200-interior.md`.
2. **WO-6, the dispatch-overhead bug** — FMV ran at ~50-55fps average
   because every overlay-to-main-EXE call paid full dynamic-dispatch
   bookkeeping for a target that was actually fixed at compile time. This
   was found only because the user pushed back explicitly on an earlier
   "hardware ceiling" conclusion ("we're only 10fps away from full speed,
   too specific to be a hardware wall"). mstan's team's fix delivered a
   measured, real **+4% average fps** on this exact hardware. See
   `fmv-dispatch-overhead-ai-brief.md`.

Both times, a symptom that looked exactly like "this laptop isn't fast
enough" was a specific, fixable architecture bug. **This slower, older,
thermally-limited machine has been a genuine asset, not a liability** —
it makes costs visible that get lost in the noise on faster hardware,
where nobody would notice a 20ms hitch buried in normal frame-time
variance the way this machine shows a 90ms one. Other psxrecomp
developers reportedly aren't surprised by FMV performance, which is
consistent with this being a real, shared, architectural cost hidden on
their faster machines rather than something specific to this laptop.

**The standard for this investigation**: a hardware/OS-level explanation
is accepted only after direct, positive evidence for it — a clean
sampling profile with nothing to blame, or a same-machine control
comparison that shows the same behavior in a workload we know isn't
FMV-specific. Not by elimination-and-a-shrug once the easy counters run out.

## The key observation currently driving Phase 1

Gameplay and menus, on this exact machine, now sustain a stable 60fps
(per the fixes above). If the machine itself were too slow or too
thermally limited to sustain FMV's workload, the same kind of stalling
should show up under *any* sustained heavy single-core load — not
exclusively during FMV. As far as we know right now, **it only happens
during FMV.** That's the concrete thing Phase 1 tests directly, instead
of assuming it.

## The plan

### Phase 1 — Does the same stall happen during gameplay? (not yet run — do this first)

Every latency-ring measurement so far has only been taken during FMV.
Run the identical capture (per-frame `latency` ring, same duration, same
build) during normal gameplay/field exploration instead.

- **If gameplay comes back clean** (no comparable rate of >30ms frames):
  strong evidence the cause is specific to FMV's code path — MDEC decode
  integration, XA audio interleaving, or something else only exercised
  there — not a blanket hardware/OS ceiling. Redirects the rest of the
  investigation hard toward FMV-specific code.
- **If gameplay stalls at a similar rate**: points toward something more
  general (OS scheduling, background system load) and raises the priority
  of Phase 2's direct profiling.

### Phase 2 — Ground-truth CPU sampling profile during a stall (not yet run)

Every test so far is indirect — counting calls, timing named subsystems,
watching CPU-time-share. None of it can see a plain native loop that
never crosses a dispatch boundary; that's a real blind spot in the
methodology so far, not a hand-wave. Windows ships a command-line CPU
sampling profiler (`wpr.exe` + `tracerpt`) that needs no GUI and can
capture which code address is actually executing during a captured window.

- Start a CPU-sampling ETW trace, play through several FMV stalls, stop,
  extract the profile.
- **If a specific function/loop dominates samples during stall windows
  specifically** (vs. calm windows): a real, named, fixable bug — exactly
  the "hidden by good hardware" scenario this plan exists to catch.
- **If the profile looks normal/varied even during a stall**: strengthens
  the case for something outside the process's own executing code.

### Phase 3 — Cross-title check, if feasible (not yet attempted)

"Other developers aren't surprised" suggests this may be architectural
rather than specific to Parasite Eve's game data. If another
psxrecomp-based title is buildable in this environment (Tomba/MMX6 are
referenced elsewhere in this codebase and in upstream's own validation
matrix), running the same latency-ring capture against its FMV would
directly test that: the same stall signature on completely different game
code would mean a shared runtime issue, not something specific to
Parasite Eve.

### Phase 4 — Hardware/OS as a real hypothesis, only with direct evidence

Only after Phase 1 shows gameplay is clean (isolating this to FMV) *and*
Phase 2's sampling profile shows nothing hot to blame, does a hardware/OS
explanation get taken seriously — and even then, framed as "a direct
sampling profile during captured stalls showed no dominant code path,"
not "we ran out of things to check."

## Status

| Phase | Status |
|---|---|
| 1. Gameplay-vs-FMV latency-ring comparison | **DONE — result below** |
| 2. Root cause found | **DONE — see below; not via ETW, via direct dispatch-level timing** |
| 3. Cross-title check (Tomba/MMX6 if buildable) | Superseded — root cause found, moot for now |
| 4. Hardware/OS with direct evidence | **Ruled out — root cause is a real, findable, data-dependent decode cost** |

## Phase 1 result (2026-09-12) — FMV-specific, not general hardware/OS

Used a debug-server savestate load (`{"cmd":"savestate","op":"load","slot":0}`
— the in-game menu's "slot 1" is 0-indexed in the debug protocol) to drop
directly into a real gameplay location (confirmed via `present_shot`
screenshot: Aya and a companion outside a building, not a menu or FMV),
then ran the identical latency-ring capture used on the boot-intro FMV —
same tooling, same ~106s duration, same machine, same session.

| | Gameplay | FMV (boot intro) |
|---|---:|---:|
| Mean frame time | 16.66ms | 17.99ms |
| p50 | 16.06ms | 16.69ms |
| **Max single-frame stall** | **44.00ms** | **71-134ms** |
| **Frames >30ms** | **0.68%** (41 of 6,017) | **8.53%** (943 of 11,060) |

**A ~12x difference in how often a bad frame happens, and roughly half the
worst-case severity.** If this were a general hardware or OS-scheduling
ceiling, sustained gameplay load should show a comparable rate of stalls —
it doesn't, by a wide margin. This is real evidence the dominant failure
mode is specific to FMV's own code path (most likely MDEC decode
integration or XA audio interleaving — the two systems FMV exercises that
ordinary gameplay doesn't), not a blanket "this machine is too slow/too
hot" explanation.

Gameplay isn't perfectly clean either — one 44ms stall and a handful of
30+ms ones in the sample. That's consistent with the separate, rare
(~0.5%) genuine-OS-descheduling population already found, which wouldn't
be expected to respect an FMV/gameplay boundary. The dominant "CPU-busy-
but-unproductive" majority that makes up ~99% of FMV's stalls is what's
essentially absent here.

**Caveat**: the gameplay sample was largely a standing-still moment (the
savestate's location), not active movement/combat. Real code is still
running (physics, camera, animation, input polling), so the comparison is
valid, but a moving/combat sample would be a stronger control if this
needs to be nailed down further.

**What this changed**: Phase 4 (accepting hardware/OS as the explanation)
got considerably weaker as a hypothesis right after this test — the
FMV-specificity argued for something findable in FMV's own handling. The
natural next step named at the time — MDEC decode and XA audio
integration specifically — turned out to be the wrong guess once actually
measured (see Phase 2 below): both were directly timed and cleared, and
the real cause was a step further down the call chain than either of
those subsystems.

## Phase 2 result (2026-09-12) — root cause found: `0x0010C89C`, a
per-entity Huffman/RLE decompress call in the rotating-intro's own loop

Full evidence trail (caller trace, disassembly, the iteration-count/
duration correlation that proves it rather than infers it, and two build-
pipeline pitfalls worth knowing about if this is picked up again) is in
`fmv-frame-stall.md`'s "Root cause found" section — this is the summary.

Rather than the originally-planned ETW/WPR sampling profile, this used
tooling already in the runtime (the `latency_ring` per-frame instrumentation,
extended to time the native dispatch call itself) plus a temporary
loop-iteration counter added directly to the generated overlay source. That
turned out to be precise enough to settle the question directly:

- **MDEC and XA audio decode, timed directly** (not guessed): max 1.57ms
  and 0.18ms respectively across a full FMV capture — cleared as causes.
  Corrects this doc's earlier guess.
- **The actual native dispatch call to `0x0010C89C`** — a ~200-instruction
  function with a genuine data-dependent loop, disassembled and confirmed
  Huffman/RLE-decode-shaped — occasionally takes 20-67ms per call, and its
  caller is the *same function* that also calls `RoomLib_InitC`
  (`0x80191B64`), tying this investigation, WO-6, and the RoomLib fix
  together into one function in the rotating intro.
- **Direct proof, not inference**: added a real iteration counter inside
  the function's own loop headers. Across 324 real calls, loop iteration
  count correlates with call duration at Pearson r=0.69 / Spearman r=0.73,
  and the two highest-iteration-count calls observed are also the two most
  severe stalls (67ms, 48ms). This is a positive, measured confirmation of
  the "cost is proportional to how much this call has to decompress"
  mechanism — exactly the signature that explains the earlier-documented
  "CPU-busy, fully-scheduled, still 3-4x slower" majority: the thread
  really is busy, doing real (if uneven) work.

**Phase 3 (cross-title check) and Phase 4 (hardware/OS) are moot** — this
is a specific, findable mechanism in this game's own asset-decompression
path riding the recompiler's CPS dispatch, not a general runtime or
hardware limitation. No fix has been attempted yet (this round's goal was
root-causing the *mechanism*, not shipping a change); a plausible future
direction is pre-decompressing/caching this data off the hot thread, but
that's future work, not part of this finding.

## What's already ruled out (context — full detail in `fmv-frame-stall.md`)

Seven candidates already eliminated with direct measurement: dispatch
rate, MDEC decode-cost variance, the present/vsync call itself, CPU
housekeeping before it, disc-image reads, audio/SPU processing, and WO-6's
own dispatch-index change (tested directly against the pre-WO-6 commit,
same stall magnitude). Separately, the stalls split cleanly into two
populations: ~0.5% show genuine OS descheduling (reduced CPU-time
consumption — a real, if rare, scheduling-contention event, and the thing
the priority-boost experiment was detecting), while **99.1%** show the
process consuming its full, normal CPU-time share while still running
3-4x slower — no counted event elevated, nothing measurably different,
just less real work per unit of scheduled time. That 99.1% majority is
what Phases 1-3 are aimed at explaining.
