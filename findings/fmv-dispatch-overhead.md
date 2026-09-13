# FMV runs at ~50fps because of dispatch overhead, not MDEC decode cost

**Read follow-up 6 before citing any specific number from this document —
it corrects a wrong per-function figure from the earlier sections below and
grades every remaining claim by confidence. Then read follow-up 7 — it's
mstan's team's upstream review response, which further retracts one of
follow-up 6's own numbers, corrects a disassembly error, and resolves the
WO-7 diagnostic-bug claim as not a bug. Then follow-up 8 — WO-6's actual
fix, tested against this project's real build: it measurably helps
(+4% avg fps during FMV, ~half as many sub-60fps dips).**

Follow-up to `fmv-speed-and-vsync.md`, prompted by a direct challenge to that
file's conclusion: "we're only 10fps away from full speed, and gameplay
hits 60fps on the same machine — this is too specific to be a hardware
wall." That pushback was correct. The earlier conclusion rested on
`interp_share` alone (healthy, ~8.6%), which ruled out the interpreter but
never checked *dispatch* cost — a different thing entirely, and the actual
bottleneck.

## The measurement

Enabled the runtime's built-in per-second diagnostics
(`PSX_RUNTIME_PERF_DIAG=1`, `PSX_RUNTIME_PERF_DIAG_MS=1000` — no rebuild
needed, prints one summary line per second to the log) and compared FMV
playback against the idle title screen:

| | Idle title screen (60fps) | FMV playback (~50fps) |
|---|---:|---:|
| Guest CPU work, ms per second | 431-440 (43-44%) | 960-980 (**96-98%**) |
| Calls/sec to the single hottest dispatched function | ~1,625 | **270,000-347,000** |
| Interpreter fallback | negligible | zero |

The guest thread is essentially saturated during FMV, and almost all of
that is one function being dispatched ~200x more often than at idle.
Confirmed from source (`overlay_loader.c`'s `native_hot_note`) that this
counter fires once per *real dispatch* — the full entry path (native-call
ring write, call-stack push, the function pointer call itself, post-dispatch
IRQ pump) — not a cheap sample. Each of those 300K/sec calls carries that
whole path's overhead, not just the callee's own instructions.

## Finding the exact call site

Used the runtime's function entry/exit tracer (`fn_filter` to arm a tight
address-range filter cheaply, `fn_entry_dump` to read back entries with
`ra`/`a0-a3`/`s0-s3`) targeted at the hot address. Every single entry:

- Same `ra` (return address) every time: `0x80192A44` — one call site.
- `s0` (a loop counter) decrementing by exactly 1 per call, resetting to
  ~0x7D0 (2000) roughly every 2 emulated frames.
- `a2`/pointer-like args advancing by ~256-288 bytes each call — a struct
  array being walked element by element.

Textbook counting loop calling the same subroutine once per iteration. The
call site (`0x80192A44`) sits inside a function named in the decomp as
**`RoomLib_InitFull`** — "fully initialize" a ~2000-entry room-entity pool,
calling a small per-entity constructor (`RoomLib_InitC`, at the hot address
`0x80191B64`) on every slot. Re-armed the same tracer around
`RoomLib_InitFull`'s own address range to find *its* caller and got **zero**
entries there even after clearing the ring — meaning `RoomLib_InitFull`
itself runs as a plain compiled loop with no dispatch overhead of its own;
only its calls *out* to `RoomLib_InitC` cross into the separate compiled
overlay-shard that function lives in, paying dispatch overhead on every one
of those ~2000 iterations.

## Why this is expensive here specifically

`RoomLib_InitC` and `RoomLib_InitFull` are compiled into separate shards —
an ordinary consequence of this build's per-function overlay-shard model,
not a bug introduced by anything patched earlier this project (neither
address is on the existing `--force-interior` list). A cross-shard call
costs real, measured overhead (~3.2 µs, back-calculated from 970ms/sec ÷
300K calls/sec — a believable size for a ring write + stack push + IRQ
pump, not a rounding artifact). On real hardware that same call is a
two-instruction `jal`/`jr`, free by comparison. Calling across that boundary
once is negligible; calling across it **2,000 times in a tight loop, every
couple of frames, for the entire duration of every FMV**, is not — and
that's the entire gap between 50fps and 60fps, measured directly, not
inferred.

## Follow-up: tracing the caller — a correction, and a second hot loop found

Went to find what calls `RoomLib_InitFull` (the name given to the loop
above) using the runtime's function entry/exit tracer (`fn_filter` to arm a
cheap address-range filter, `fn_entry_dump` to read back `func`/`ra`/args).

**Correction to the section above: the caller function is not actually
`RoomLib_InitFull`.** That name came from cross-referencing the observed
return address (`0x80192A44`) against `room_m154.yaml`'s symbol table — a
different overlay than the one already verified to match this session
(`room_m392.yaml`, confirmed because it places `RoomLib_InitC` at exactly
the live-observed address). Checking the address against the *correct*
file instead: `room_m392.yaml`'s own `RoomLib_InitFull` sits at a
completely different address than `0x80192A44`. Tried the next candidate
(`RoomLib_HandlerC`, whose computed address range does contain
`0x80192A44`) and read its actual decomp source — it doesn't call
`RoomLib_InitC` anywhere. So the exact decomp name of the loop's containing
function is **not established** — flagging this rather than let the
earlier name stand uncorrected. Static address-matching against
per-overlay YAML symbol tables is unreliable for this shared, always-
resident code without confirming the specific overlay context matches, and
that confirmation didn't hold up on the second address even though it did
on the first.

**A second, separately-hot loop was found while widening the trace.**
Arming `fn_filter` over the whole shared RoomLib window (`0x8018F000`-
`0x80195000`) and dumping entries turned up another cluster, comparably
frequent to the first, running concurrently:

- `0x80191DC8` (and two related addresses, `0x80191FA4`, `0x80191DFC`),
  called several times per frame from a fixed return address `0x800745C8`,
  with fixed arguments `0x1F8010F4` and `0x1F8010F0`.
- Those two argument values are PS1 hardware addresses — **DICR and DPCR,
  the DMA interrupt/priority control registers.** This is a hardware-status
  poll, almost certainly "wait for a DMA channel to finish" — a legitimate,
  expected pattern for something waiting on MDEC data during video decode.
- The caller, `0x800745C8`, has **no symbol anywhere in the decomp** — it
  falls outside every address range `parasite-eve-decomp` covers, which
  points at precompiled Sony SDK library code linked into the game (not
  the developers' own source), rather than anything traceable further in
  this repo.

Same underlying shape as the first loop either way: a near-free hardware
operation on real silicon, routed through this recomp's full dispatch path
on every poll, in a loop that runs many times per frame for the whole video.

## Follow-up 2: ground-truth disassembly settles the loop, opens a bigger lead

Static per-overlay symbol matching kept giving wrong or unconfirmable
answers (see the correction above), so switched to the one method that
can't be wrong: reading the actual live instruction bytes. The debug
server's `mem_words` command (`{"cmd":"mem_words","addr":"0x...","count":N}`)
returns raw 32-bit words at any address — decoded them by hand (MIPS opcode
field, `jal`/`j`/branch target math) rather than trusting any symbol table.

**The loop, confirmed byte-for-byte:**

```
0x80192a30  241007D0        li    $s0, 0x7D0        ; 2000 — the loop count
0x80192a34  3C04801D        lui   $a0, 0x801d
0x80192a38  24841464        addiu $a0, $a0, 0x1464   ; $a0 = 0x801D1464
0x80192a3c  0C0646D9        jal   0x80191B64         ; call RoomLib_InitC
0x80192a40  00000000        nop                       ; delay slot
0x80192a44  ...                                       ; return address — matches every live-traced `ra` exactly
...
0x80192a58  1440FFF6        bne   $v0, $zero, 0x80192a38   ; loop-closing branch, confirmed
```

That `bne` at `0x80192a58` branches back to `0x80192a38` — genuinely closing
a repeat loop, not a one-shot call. This is no longer inferred from
call-count patterns; it's read directly out of the live process's memory.

**The function's real start, also confirmed by reading backwards**: at
`0x8019292C` there's a `jr ra` (return) immediately followed by a `nop`,
and the very next instruction at `0x80192934` begins a fresh prologue
(`addiu $sp, $sp, -0x30`, register saves) — an unambiguous function
boundary. **The function containing this loop starts at `0x80192934`.**

**This function does not appear anywhere in `parasite-eve-decomp`** — not
by address in any overlay's symbol table, not as a named C function calling
`RoomLib_InitC` by name (searched the whole source tree for both). Either
it belongs to an overlay variant the decomp project hasn't named yet, or
it's still in an un-decompiled state. This is a genuine documented gap,
not a dead end from this investigation's methodology — the byte-level
facts above are solid regardless of what the function is eventually named.

**A second, unexpected lead**: continuing to read forward past the loop,
at `0x80192aa4` there's another call — `jal 0x8010C89C`. That address is
not new to this project: it's the exact PC flagged in
`roomlib-0x80191200-interior.md`'s "Still open" section, back near the very
start of this whole investigation arc — a hot interpreted PC that showed up
once and then "did not reproduce in three subsequent fresh sessions."
Finding it called directly from inside this same FMV-triggered routine is
a plausible explanation for that old non-reproduction: it may simply need
FMV playback specifically to be reached, which none of the earlier retry
sessions were testing for. Worth revisiting that old thread with this in
hand, rather than treating it as closed.

## Follow-up 3: chased `0x0010C89C` — real, but a dead end for the perf story

Went back to check whether the `0x0010C89C` connection found in follow-up 2
actually explains the old "still open" mystery from
`roomlib-0x80191200-interior.md` (245,694 instructions on one interpreted
entry, partial native/interp split, never reproduced since). Short answer:
**confirmed it's real and reachable from here, but it does not reproduce
the old symptom — this is a different, much cheaper thing wearing the same
address.**

- `stall_report`'s `phase_hot` breakdown during FMV shows `0x0010C89C`
  consistently in the **native** set alongside `RoomLib_InitC` and the
  loop-container function — confirming this address genuinely does get hit
  from FMV code, not a coincidence.
- Traced its actual callers with `fn_filter`/`fn_entry_dump`: every single
  call returns to `0x80192AAC` — which matches the `jal 0x8010C89C` found by
  direct disassembly in follow-up 2 (at `0x80192aa4`, return = `+8`)
  exactly. One call site, confirmed twice over (live trace + static
  disassembly agree).
- But the actual call *pattern* is small and steady, not explosive: called
  about **once every 4 frames**, cycling through **15 distinct object
  pointers** spaced exactly `0x7E0` (2016) bytes apart — a small, fixed-size
  struct array, not the 2000-entry pool `RoomLib_InitC` walks. Two
  secondary arguments alternate between exactly two fixed values across
  calls. This reads as a modest, ordinary per-tick maintenance routine —
  roughly 15 calls/sec, three-to-four orders of magnitude below
  `RoomLib_InitC`'s 300K/sec. Confirmed always native and interpreter-free
  (`dispatch_interp_fallback` stayed at 0 in a focused check, and only rose
  to a tiny 244/45s in a longer general run, fully attributable to expected
  always-interpreted kernel-window code per `stall_report`'s own note, not
  to this address specifically).

**Conclusion: retracting the implied connection from follow-up 2.** Finding
the same address reachable from FMV code was a real, useful thing to check,
but what's actually happening here is unrelated in scale and character to
the old "245,694 insn/entry, partial interp fallback" incident. That old
mystery is **still open, still unexplained, and still not reproduced** —
this wasn't it. If it resurfaces again, it's most likely a *different*
calling context (a different overlay reaching this same address while
uncaptured) than the one exercised by this FMV path.

## Follow-up 4: one more caller level found by disassembly; the level above hit real tool limits

Went to trace who calls the loop-container function (`0x80192934`), per
its live-observed `ra=0x80192E44`. Direct disassembly (same `mem_words`
method as follow-up 2) found the actual call cleanly:

```
0x80192e34  jal 0x8003EB04     ; a conditional call (gated by a branch above it)
0x80192e3c  jal 0x80192934     ; the loop — called UNCONDITIONALLY, no gate
0x80192e44  ...                 ; return point, matches every live-traced `ra`
```

So the loop runs every single time *this* containing function runs — no
internal condition skips it. Reading backwards from there found a clean
`jr ra`+`nop` boundary at `0x80192CE0`/`E4`, with a real prologue
(`addiu $sp,$sp,-0x30`, five register saves) starting right after at
**`0x80192CE8`**. This is a bigger function: several calls out to
low-address (`0x8006xxxx`/`0x8007xxxx`) system/library routines before
reaching the loop — consistent with "entering a scene/room" setup work,
of which the entity-pool reset is one part.

**Tracing *this* function's own caller hit a real methodology wall.**
`fn_filter`/`fn_entry_dump` (the tool that worked for every previous level)
came back empty again — this call, like the `0x80192934` one before it,
isn't a genuine overlay-dispatch event, so the entry/exit tracer can't see
it. Tried two more specialized tools that looked purpose-built for exactly
this: `callret_watch` (arm a `[lo,hi)` window, record calls whose *target*
lands in it) came back with zero entries despite arming correctly —
reading its source, it's wired specifically into the interpreter's own
call-tracking (`dirty_ram_interp.c`), and this code path runs fully
native, so it's simply blind here. `ra_load_watch` needs a *known* target
value to watch for, which defeats the purpose of using it to *discover* an
unknown caller. Going one more level would need either a much wider blind
disassembly scan (impractical without knowing where to start looking) or a
new capability this session's tools don't provide.

**A real, useful finding came out of chasing the burst question instead.**
Checked whether the "bursts vs calm stretches" pattern (established in
follow-up 3) lines up with new overlay loads — it doesn't:
`overlay_loader_status`'s `loads` counter sat flat at 15 across a 20-second
window (frames 9687-10861) with no new loads at all, ruling out "a fresh
overlay/room load triggers this" as the mechanism. Separately, checked the
InitC call rate *right now* against the live FPS counter during a
confirmed-slow stretch (47.9-49.3fps): the call rate was only ~78/sec —
nowhere near the 300K/sec burst level, yet the game was still measurably
below 60fps. **This means there are two separate, stacked costs**: a
modest baseline slowdown present even *without* the InitC burst (matching
the original `fmv-speed-and-vsync.md` MDEC/structural-cost finding, plus
the smaller dispatch costs found since — the DMA-poll loop, `0x0010C89C`'s
own 15/sec), and the much larger, intermittent InitC burst layered on top
of it at specific moments. Both are real; they're not the same thing.

## Follow-up 5: correcting follow-up 4's "calm baseline" claim — it was a measurement artifact

Went to characterize the "modest baseline" cost follow-up 4 described (the
~78/sec InitC reading during a confirmed-slow, apparently non-burst
stretch). Direct measurement shows that reading was wrong, and says why.

Polled the debug server's raw, global `dispatch_native` counter
(`overlay_loader_status`, a plain cumulative count — no hashing, no
capacity limit, unlike the function-entry tracer used for the "78/sec"
reading) once a second for 20 seconds:

```
frame 5869..6892 (20s): dispatch_native running at 220,000-320,000 calls/sec,
continuously, no drop to anything near 78/sec at any point sampled.
```

**Correction: there is no separate "calm baseline" distinct from the
burst.** The overlay-dispatch rate stays in the 220K-320K/sec range
throughout — the `78/sec` figure in follow-up 4 was almost certainly the
function-entry tracer (`fn_filter`/`fn_entry_dump`) losing entries under
this exact load, not a real quiet period: that tool's own stats showed
`stack_overflows` and `tail_calls` climbing throughout every session it was
used this investigation, direct evidence it drops/miscounts events at high
volume. The plain global counter has no such limit and is the one to
trust here.

**This also lets the whole cost be quantified cleanly.** Cross-checking
against the runtime's own per-second diagnostic in the same window:
`dispatch_native` ≈ 270,000/sec average, `work guest` ≈ 974-980 ms of
guest-thread time per second (97-98% saturated). At the ~3.2µs/call
dispatch overhead figure established in the original write-up
(back-calculated independently from a different session's numbers),
270,000 × 3.2µs ≈ **864ms of the ~975ms of guest-thread time per second is
dispatch bookkeeping, not the game's own logic** — two independent
estimates landing within about 10% of each other. That's about as
complete an answer as this investigation is going to get without reading
the recompiler's own source: **during FMV, this game issues on the order
of a quarter-million overlay-dispatch calls every second, essentially
continuously, and the fixed per-call overhead of dispatching each one — not
any single loop, not MDEC decode, not one bad function — is nearly the
whole cost.**

## Follow-up 6: major correction — `RoomLib_InitC`'s own dispatch rate was wrong; found the real dominant contributor, with a name

Went back in to build enough evidence to actually hand this to mstan/Alex,
and cross-validating the headline number surfaced a real error in this
investigation that needs correcting before anyone else reads it.

**The error**: everything above about `RoomLib_InitC` being dispatched
270,000-347,000 times a second came from the runtime's `hot_native`
diagnostic field (`overlay_loader_take_hot_native`, surfaced in the
`PSX_RUNTIME_PERF_DIAG` log lines). Cross-checked it two ways this
session:

1. Armed `fn_filter` on exactly `RoomLib_InitC`'s address range and polled
   `fn_stats.entry_total` against a precisely-timed 10-second window (Python
   wall clock, not assumed) → **86 calls/sec**, not 300,000.
2. Polled the same narrow filter every 0.5s for 24 seconds and watched the
   counter directly → **steady, unbroken growth of ~90-130 per second**, no
   jumps, no bursts. This rules out "the average hides an occasional huge
   spike" — there wasn't one in this window, and the growth curve is flat.

Both independent methods agree with each other and disagree with
`hot_native`'s "252,511/sec" reading by roughly three orders of magnitude.
**The `hot_native` field cannot be trusted for per-function attribution** —
whatever the actual bug in it is (a hash-bucket artifact is one plausible
guess, but not confirmed), it should not be relied on again in this
investigation, and the specific rate figures in follow-ups 1-5 attributed
to `RoomLib_InitC` specifically are retracted. The loop itself is still
100% real (confirmed by direct disassembly, unaffected by this) — it's
just called far less often than previously reported.

**What actually accounts for the volume**: pulled a genuine, non-sampled
census instead of trusting any single hot-function counter — armed
`fn_filter` across the whole main+overlay address space
(`0x80000000`-`0x80200000`) and read back a raw 2000-entry slice of
whatever the ring actually recorded, then counted it in Python (no
built-in top-N logic to trust or distrust):

```
0x8007C484   1867 of 2000 (93.4%)
0x80084FE4     31
0x80084FC4     13
0x80000E10      8
...
0x80191B64      2   (RoomLib_InitC itself — barely present)
```

**`0x8007C484` is `StGetNext`** — a real, named function in
`parasite-eve-decomp`'s main-EXE symbol table (`sym.main.txt:1424`), not a
guess. Traced its live call site (`fn_entry_dump` on that address) and it
returns to a single, constant `ra=0x80191BB8` — right next door to
`RoomLib_InitC`. Disassembled that call site directly and it's the exact
same shape as the original loop, just calling a different, real, named
function:

```
0x80191bb0  jal 0x8007C484        ; call StGetNext
0x80191bb4  addiu $a1,$sp,0x14    ; (delay slot / arg setup)
0x80191bb8  beq $v0,$zero,+5      ; branch on StGetNext's return value
0x80191bbc  addiu $s0,$s0,-1      ; decrement loop counter (delay slot)
0x80191bc0  bne  $s0,$zero,-5     ; loop back to 0x80191bb4 if not done
```

— and reading a little further back, this whole loop lives *inside*
`RoomLib_InitC`'s own function body (which starts with the standard
prologue at `0x80191B64`, the same address `hot_native` had misattributed
the huge count to — plausibly *how* the misattribution happened, since the
real hot loop and the mislabeled one share an entry point). `StGetNext`
is a PSY-Q SDK stream/queue function; a tight loop draining it this
aggressively reads as an audio- or CD-stream buffer being serviced, which
fits "only happens during FMV" far better than a room-entity reset would.

**The overall picture, evidence-graded:**

| Claim | Confidence | Evidence |
|---|---|---|
| Overlay-dispatch rate during FMV is usually 200K-320K/sec | High | Confirmed across many independent, precisely-timed polls of the raw global counter, across multiple sessions |
| It can also drop much lower at specific moments (one window measured ~4,400/sec) | Medium | Seen once, in an otherwise-consistent series of high readings — a real dip, but not yet characterized (what moment, how often) |
| `StGetNext`, called from inside `RoomLib_InitC`, is the largest single identified contributor | High | Named decomp symbol + disassembly-confirmed loop + a live census showing it as 93% of one sampled window |
| `StGetNext` accounts for ~93% of the total *on average*, not just in that one sample | Low | Not established — its share may vary the same way the total rate does; only measured directly in one busy window and one quiet window (1% share in the quiet one) |
| `RoomLib_InitC`'s own dispatch (not the loop inside it) is ~90-130/sec | High | Two independent precisely-timed measurements agree |
| Per-call dispatch overhead (~3.2µs) roughly explains the guest-thread saturation seen during busy windows | Medium | Consistent across two different sessions' worth of numbers, but the constant itself was back-calculated, not measured directly |

**Recommendation before this goes to mstan/Alex**: lead with the High-
confidence rows — the dispatch mechanism's per-call cost, applied at
hundreds of thousands of calls per second, is real and measured multiple
independent ways; `StGetNext` inside `RoomLib_InitC` is a concrete, named,
disassembly-confirmed example. Don't lead with a single "X% of frame time"
number or claim `StGetNext` explains *all* of it — those are the Low/Medium
rows, and presenting them with the same confidence as the rest would be a
mistake a maintainer reading the disassembly could catch.

## What's still open

- **The loop itself is now fully confirmed at the byte level** (see
  follow-up 2) — real 2000-count loop, real `jal`/`bne` pair, real function
  boundary at `0x80192934`. What's still missing is only its *decomp name*
  — it isn't findable anywhere in `parasite-eve-decomp`'s source, which
  looks like a genuine gap in that project's coverage rather than something
  wrong with this investigation.
- **Why this function runs when it does** is still open, one level further
  in than before: the immediate caller's real entry (`0x80192CE8`) is now
  confirmed by disassembly, but *its* caller hit a genuine tool wall this
  session — `fn_entry_dump`, `callret_watch`, and `ra_load_watch` all
  couldn't reach it (see follow-up 4 for why each one didn't work). Closing
  this needs either a wider blind disassembly search or a capability this
  session's tools don't have.
- ~~Confirmed there are two separate, stacked slowdowns...~~ — **partly
  corrected in follow-up 5, then refined again in follow-up 6**: the
  dispatch rate is usually 200K-320K/sec, but follow-up 6 caught one
  genuine drop to ~4,400/sec in an otherwise-consistent series of high
  readings — so "always continuous, never varies" (follow-up 5's claim)
  overstated it too. What triggers that occasional drop is unknown.
- ~~`RoomLib_InitC`'s own 2000-iteration loop is not the majority of the
  cost...~~ — **superseded by follow-up 6**: `RoomLib_InitC`'s own entry
  dispatch is confirmed ~90-130/sec (not the 270K-347K/sec originally
  reported — that figure came from an unreliable diagnostic field and is
  retracted). The real dominant contributor, found via a proper census
  rather than a single hot-function counter, is `StGetNext` — a named,
  disassembly-confirmed PSY-Q SDK stream function called in a tight loop
  from inside `RoomLib_InitC`'s own body. See follow-up 6 for the full
  evidence grading before citing any of this externally.
- ~~New, concrete lead: this function also calls `0x8010C89C`...~~ —
  **checked in follow-up 3 and it's a dead end.** Same address, genuinely
  reachable from here, but a small ~15-calls/sec maintenance routine, not
  the old expensive symptom. `0x0010C89C`'s original "still open" mystery
  (245,694 insn/entry, partial interp) remains unresolved and unreproduced.
- **The `RoomLib_InitC` call rate is not uniform across the whole FMV.** A
  45-second `stall_report` window later in the same video showed it called
  only ~18/sec on average — nowhere near the 270K-347K/sec measured in the
  original per-second diagnostic. The massive rate is real (confirmed twice
  now) but appears to happen in **bursts tied to specific moments** in the
  video (likely scene-internal transitions), not continuously throughout.
  This doesn't change the core finding — those bursts are real and
  measured — but it means the "~50fps average" is likely an average across
  bad bursts and calmer stretches, not uniformly bad the whole time. Worth
  knowing before trying to characterize "how much of the video is affected."
- **The DMA-poll loop's caller (`0x800745C8`) is outside decomp coverage
  entirely** — it's very likely precompiled SDK library code, not something
  `parasite-eve-decomp` can name further. If confirmed, that half of the
  cost may not be addressable by decomp-side changes at all, only by a
  psxrecomp-side change to how such tiny, hot cross-region calls dispatch.
- **Whether this specific caller/callee pair could be co-compiled** to
  avoid the cross-shard call (a `compile_overlays.py`-side question — could
  a hot caller/callee pair detected this way be fused into one compiled
  unit) wasn't explored; that's upstream-psxrecomp territory, not something
  fixed locally here.
- Only the intro FMV was profiled. Not verified whether other FMVs in the
  game hit the same `RoomLib_InitFull` pattern, though given it's shared
  "RoomLib" code (not FMV-specific code), it plausibly would.
- A real bug was hit and set aside, not fixed: the debug server's
  `dispatch_tail` command returns a truncated/malformed JSON reply for any
  non-trivial `count` (reproduced at both `count=80` and `count=5`) —
  worth a real bug report upstream, but `fn_filter`/`fn_entry_dump` gave
  everything needed here instead.

## Verify

`PSX_RUNTIME_PERF_DIAG=1` (optionally `PSX_RUNTIME_PERF_DIAG_MS=1000`),
compare the `overlay native=+N hot_native=0xADDR/+M` and `work guest=X ms/s`
fields in the logged `runtime cadence` lines between an idle window and an
FMV window — `hot_native` should again point at `0x80191B64` with a call
count two orders of magnitude above idle if this still reproduces. To
confirm the call site: `{"cmd":"fn_filter","lo":"0x80191B60","hi":"0x80191B70"}`
then `{"cmd":"fn_entry_dump","count":"30"}` — every entry's `ra` should read
`0x80192A44`.

## Follow-up 7: mstan's team reviewed this — pulled latest `psxrecomp`, read their response

Per mstan: "pull latest code and read [the] wo6-wo7-bios review handoff."
Fetched `rtk` (`RetroPortingToolKit/psxrecomp`) and read
`docs/internal/WO6_BIOS_INTEGRATION_REVIEW.md` off `rtk/master`
(tip `89db8168`, merging PR #348 — integration branch
`integrate/wo6-bios343-346`, tracked as `beads-eio.3.140`). This is their
official response to the WO-6 and WO-7 work orders from this file's
evidence table. Full quoted text is in `fmv-dispatch-overhead-ai-brief.md`'s
"Upstream response" subsections; summary here.

**Two corrections to our own numbers, both accepted without qualification:**

1. **The ~3.2µs/call figure (Medium-confidence row in follow-up 6's table)
   is invalid.** Upstream: *"the supplied brief's 3.2 microseconds divides
   total guest work by activations and therefore does not isolate dispatch
   cost."* Correct — it folds in `StGetNext`'s own real work, not just
   dispatch bookkeeping. Retracted, no replacement number.
2. **A MIPS branch-target miscalculation**: the `bne` at `0x80191BC0` with
   immediate `FFFB` targets `0x80191BB0` (the `jal` itself), not `0x80191BB4`
   (the delay slot) as follow-up 6's disassembly block stated. Independently
   re-derived and confirmed — the error was using the delay slot's address
   as the PC-relative base instead of the branch instruction's own address.
   `0x80191BB0` also makes more sense as a loop-back target than
   `0x80191BB4` would have.

**WO-6 (the dispatch-overhead fix) — partially addressed, by a different
mechanism than we proposed, not tested against Parasite Eve by either
side.** Upstream shipped an unconditional O(1) physical-word index for
resident dispatch tables under 2 MiB (wide/ambiguous tables keep binary
search; CPS returns, live-code validation, interrupt checks, and mod hooks
all preserved). Their isolated benchmark: ~54-61ns/query (binary search)
vs. ~1.2-1.6ns/query (indexed) — a real, measured speedup for the address
*resolution* step specifically. Their own caveat, verbatim: *"this
accelerates address resolution; it does not turn overlay calls into nested
C calls or promise fewer dispatcher activations."* In other words: this is
not the devirtualization we proposed (skip dispatch entirely for
statically-known targets) — every dispatch still happens, still pays the
ring-write/stack-push/IRQ-pump cost this file's evidence table describes.
Only the lookup-which-function-owns-this-address step got faster, and that
step was never what we measured as the cost. Their validation matrix
(Tomba + MMX6, OpenBIOS + SCPH-1001, 11,000+ frames each, zero kernel
mismatches after the fix) is real regression evidence but explicitly not a
Parasite Eve FPS result — quote: *"not... a full playthrough... or Parasite
Eve FPS result."* Whether this change measurably helps Parasite Eve's FMV
framerate is genuinely unknown and untested by either side. **Concrete next
step, approved by the user**: pull the fix into the actual Parasite Eve
`psxrecomp` checkout and measure.

**WO-7 (the `hot_native` diagnostic "bug") — resolved as not a bug.**
Upstream: *"the native hot-owner sampler counts owner activations,
including CPS continuation returns. Function-entry tracing counts
invocations."* These are two different, both-legitimate metrics — a single
guest call that yields/resumes via a CPS continuation can register multiple
owner activations without being multiple new invocations, which explains
the ~90-130/sec (entry tracer) vs. ~270K-347K/sec (`hot_native`) gap
without either number being wrong. Our hash-bucket-collision theory is
explicitly refuted, not merely unconfirmed: *"its direct-mapped bucket
resets on a collision, so it can undercount but does not accumulate another
owner's calls"* — a collision can only lower the count, never inflate it,
so it could never have produced what we saw. Their stated fix is cosmetic
only: *"clarify the telemetry label and API docs; no counter algorithm
change or confirmed counter corruption."* Their closing assessment, quoted
in full because it's the correct verdict on our own work: *"this WO's core
claim — that `hot_native` is unreliable and gave a wrong answer — does not
hold up... This WO should not be cited as evidence of a `psxrecomp`
diagnostics bug."* Follow-up 6's framing of this as an open, unfixed
tooling bug is superseded — it's closed, and it was never a bug.

**Net effect on this file's evidence table (follow-up 6)**: the ~3.2µs row
is now retracted rather than Medium-confidence; every other row stands. The
WO-6/WO-7 status lines throughout earlier follow-ups that describe either
as "unfixed"/"open" are superseded by this follow-up — see
`fmv-dispatch-overhead-explained.md` and `fmv-dispatch-overhead-ai-brief.md`
for the corrected versions meant for external reading.

## Follow-up 8: tested WO-6's actual fix against this project's real build — it helps

Upstream's own validation explicitly excluded a Parasite Eve FPS result
(their matrix was Tomba + MMX6 only). Pulled their fix and tested it here,
since that was the one concrete open question left after follow-up 7.

**Method**: `git fetch` both `psxrecomp` remotes (`origin`=Alexbeav,
`rtk`=RetroPortingToolKit). `rtk/master` tip `89db8168` merges PR #348; the
specific commit implementing WO-6/WO-7 (isolated from the two unrelated
BIOS PRs #343/#346 also bundled into that integration branch) is
`63b205df` ("Index immutable resident dispatch keys and clarify owner
telemetry") — a small, self-contained diff (5 files, +125/-16). Committed
the one outstanding uncommitted local change (the PGO clean-exit fix, see
`pgo-train-fix.md`) first to get a clean tree, then `git cherry-pick
63b205df` onto the local `94ea3b28`-based checkout — applied clean, zero
conflicts.

**A real gotcha hit along the way, worth recording**: the first rebuild
attempt silently used a STALE emitter binary. `psxrecomp_cli.py generate`
searches several candidate build directories for `psxrecomp-game.exe` and
picks the first that exists (`psxrecomp/recompiler/build` before the
project-root `build-recompiler` this repo's own `build_recomp.ps1` script
builds into) — since an old pre-cherry-pick exe already existed at
`psxrecomp/recompiler/build/psxrecomp-game.exe` from months of earlier
sessions, `generate` happily ran it and reported "Dispatch table unchanged"
even though the source had genuinely changed. Confirmed by direct
inspection of the emitted `k_psx_game_dispatch_index` array (absent) and
by comparing file mtimes on the two candidate emitter binaries. Fix: build
the emitters into `psxrecomp/recompiler/build` specifically (the directory
the CLI actually checks first), not just `build-recompiler`. After that,
`generate` reported "Dispatch table written" and the new
`k_psx_game_dispatch_index[]` array (a `uint16_t[]`, since this table's
29,827 entries fit under 65,535) was present in the generated
`SLUS_006.62_dispatch.c`. Worth a real bug report upstream separately —
`build_recomp.ps1`'s own build step and the CLI's own search-order
disagree on which directory is canonical, silently.

**Test procedure**: same-day, same-machine, back-to-back A/B. Both builds:
`PSX_RUNTIME_PERF_DIAG=1`/`_MS=1000`, `PSX_FPS_TELEMETRY=2`, autocompile
on (warm overlay cache from many prior sessions), no controller input
(deterministic boot → intro FMV). Ran each build continuously through the
same intro-FMV content for ~4.5 minutes (270-283 one-second perf-diag
samples with `dispatch_native > 50,000/sec`, i.e. excluding idle/loading
gaps), then parsed every `runtime cadence` line for `guest=X Hz` (≈fps),
`work guest=X ms/s`, and `overlay native=+N`.

**Results**:

| Metric | Before (`5d59c1e1`, no WO-6) | After (`bda01335`, WO-6 cherry-picked) |
|---|---:|---:|
| Avg guest Hz during FMV | 55.43 | **57.74** |
| Min/max guest Hz | 41.79 / 63.87 | 45.89 / 61.98 |
| Avg `work guest` ms/s | 955.9 | 962.7 |
| Avg `dispatch_native`/s | 322,465 | 337,939 |
| % samples <58Hz | 73.1% (196/268) | **36.7%** (104/283) |
| % samples <55Hz | 37.7% (101/268) | **13.1%** (37/283) |

A real, positive effect: +2.3fps average (+4.2% relative), and roughly
half as many low-fps samples by either threshold — even though `work
guest` ms/s and `dispatch_native`/s, the two coarse aggregate counters,
are statistically indistinguishable between the runs (both landed in the
same ~955-963ms/s / ~320-340K/s bands). This matches upstream's own
framing: the fix doesn't reduce dispatch/activation *count*, so it
shouldn't move those two counters — but shaving ~50-60ns off each of
300K+/sec address lookups (O(log 29,827) binary search → O(1) array read)
is apparently enough, in some windows, to keep the guest thread's per-frame
work under the real-time budget rather than just over it. Fewer overruns,
not less total work — a plausible mechanism, not confirmed at the
instruction level.

**Caveats, stated plainly**: this is one continuous run per side, not a
repeated-trial average. Both runs share the same real-time-dependent
factors (background system load on this specific laptop, any minor
real-time branching in the guest code) that could shift a single run's
numbers independent of the code change. The direction (WO-6 helps) and
rough size (~4% avg fps, ~half the dip rate) are a solid single data
point, consistent with the mechanism upstream described in their own
write-up — but this is not a statistically-controlled multi-trial
benchmark, and a maintainer wanting tighter numbers should repeat it a
few times.

**State left in this checkout**: WO-6 (`bda01335`) is cherry-picked and
built as the current state of the local `psxrecomp` checkout — emitters
rebuilt into `psxrecomp/recompiler/build`, `generated/SLUS_006.62_dispatch.c`
regenerated with the index present, `build-release/Parasite_Eve.exe`
relinked against it. `PSX_DEBUG_TOOLS` was never touched this round (no
debug-server commands were needed — `PSX_RUNTIME_PERF_DIAG` is a plain
env-var diagnostic, not gated behind that flag), so no revert needed there.
Both FMV documents (`fmv-dispatch-overhead-explained.md`,
`fmv-dispatch-overhead-ai-brief.md`) and `findings/README.md` updated with
this result.
