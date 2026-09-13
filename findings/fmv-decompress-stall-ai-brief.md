# WO-8: FMV frame stalls — root-caused to a data-dependent Huffman/RLE
decompress call, proven with a direct iteration-count/duration correlation

Machine-readable companion to `fmv-frame-stall.md` (the full raw
investigation log — CD reads, MDEC, audio, OS scheduling, priority
experiments, all now-ruled-out candidates in chronological order) and
`fmv-frame-stall-plan.md` (the attack plan that drove this). This file is
written for a coding agent or a `psxrecomp`/Parasite-Eve-recomp maintainer
to act on directly. It closes out an investigation that spanned two
sessions and ruled out nine other candidates first — read "Evidence" and
"Tools & methodology" even if you skip everything else, since the *way*
this was found is as reusable as the finding itself.

**Two things are reported here.** The main one (this WO) is a real,
measured, explained performance characteristic — not obviously a bug, see
"Classification." A second, small dev-tooling gap discovered as a
byproduct is filed at the end as **WO-9**: a manually-compiled overlay DLL
is silently rejected by the loader with no visible error unless you know
to ask for it.

---

## Classification

**Not a `psxrecomp` bug and not a hardware ceiling — a real, structural,
data-dependent cost in the game's own asset-decompression path, riding
the recompiler's CPS dispatch mechanism.** The guest code does real work;
it just does *more* real work on some calls than others, because the
compressed data behind a given entity is sometimes larger. This is the
first candidate in this whole investigation (ten checked total) that
turned out to be neither an artifact of measurement nor an
elimination-by-exhaustion "must be hardware" conclusion — it's a positive,
named, disassembled, statistically-confirmed mechanism.

Whether it's *fixable* (worth pre-decompressing or caching this data
outside the hot per-frame path) is a judgment call for maintainers who
know the asset pipeline — see "Candidate fix" for what we'd try, but no
fix is implemented or proposed as definitely correct here.

## Objective

Explain why, even after this project's two previous recompiler-side fixes
(the RoomLib interior-classification fix, and WO-6's dispatch-index
optimization — both already merged/ported, see the companion docs),
Parasite Eve's FMV playback still shows ~8.5% of frames taking >30ms
(worst observed: 134ms), while gameplay on the identical build/machine
shows this at ~12x lower incidence (0.68%, max 44ms) — ruling out a
general hardware/OS explanation and demanding an FMV-specific one.

## Reproduce

1. Build with `-DPSX_DEBUG_TOOLS=ON` and `-march=native` (this project's
   standard perf-investigation config).
2. Boot Parasite Eve (USA) to the rotating boot-intro FMV, `--debug-port
   <N>`.
3. Poll `{"cmd":"latency","count":100}` repeatedly (~2s apart — see
   "Methodology notes" in `fmv-frame-stall.md` re: the 16KB reply-buffer
   cap) and look for `disp_max_us` (added this round — see below) spiking
   into the tens of milliseconds with `disp_addr` reading `0x0010C89C`.
4. Cross-reference against a genuine gameplay location (a debug-server
   `{"cmd":"savestate","op":"load","slot":N}` into any field/room) — the
   same capture shows negligible-rate outliers there, confirming the
   FMV-specificity (full table in `fmv-frame-stall-plan.md`'s "Phase 1
   result").

## Root cause — exact addresses (this build/session; overlay-relative
addresses will differ per build/overlay layout — see "Verify")

**The function**: `0x0010C89C` (guest/KUSEG address `0x8010C89C`). ~200
real MIPS instructions, 864 bytes (`0010B000_7238DF29.ranges`'s own
manifest: `F 8010C89C E037E43D` / `R 8010C89C 360`). Two genuine backward
branches (real loops, not unrolled code) and two real `jr $ra` return
points.

**Disassembly excerpt** (via the runtime's `mem_words` debug command +
a small custom MIPS decoder written for this investigation — see
"Tools & methodology"), showing the loop shape and register roles:

```
0x8010C89C  lui   $t0,0x8012        ; table/state base setup (once)
0x8010C8A0  addiu $t0,$t0,-5236
0x8010C8A4  addi  $a2,$a2,2048      ; $a2 = Huffman/lookup table base
0x8010C8A8  lui   $at,0x0001
0x8010C8AC  add   $a3,$a2,$at       ; $a3 = second table region ($a2+0x10000)
...
0x8010C908  lw    $t1,0($a0)        ; block_8010C960 (LOOP HEADER 1)
0x8010C90C  lhu   $t4,4($a0)        ; $a0 = input cursor, advances 2-12B/iter
...
0x8010CA7C  srl   $t0,$zero,$v0     ; block_8010CA7C (LOOP HEADER 2)
0x8010CA84  add   $t0,$t0,$a2       ; table lookup via $a2
0x8010CA88  lw    $t1,0($t0)
...                                  ; shift/mask "bit-refill" + 2 table
                                     ; lookups per pass — textbook bitstream
                                     ; (Huffman/RLE) decode shape
0x8010CBC0  jr    $ra               ; return point 1
0x8010CBF4  jr    $ra               ; return point 2
```

Register roles, confirmed by watching several live calls (not guessed):
- `$a2`/`$a3` — a shared table base, **constant `0x80162100` across every
  call observed** (a single, static Huffman/lookup table, not per-call
  data).
- `$a0` — an input-buffer cursor, advances 2-12 bytes per loop iteration.
- `$a1` — the output cursor, advances 2 bytes per iteration, and
  **alternates between exactly 2 base values across different calls** — a
  double-buffered output target.

**Caller**: `ra=0x80192AAC` (a `jal 0x8010C89C` at `0x80192aa4`), inside
the function starting at `0x80192934`. **This is the exact same function
that also calls `RoomLib_InitC` (`0x80191B64`)** — the address this
project's earlier RoomLib interior-classification fix and WO-6's
dispatch-overhead investigation were both centered on. Confirmed via a
temporary printf probe reading `cpu->gpr[31]` (return address) at the
`c->fn(cpu)` dispatch call site in `overlay_loader.c`, since reverted.

**A structural note for the recompiler team**: this address does **not**
exist in the statically-compiled main-EXE C shards
(`generated/SLUS_006.62_full_53.c`/`_54.c` both show it as `/* nop */`,
all-zero, at generation time) despite being in main-EXE address range
(`0x0010xxxx`/`0x8010xxxx`). It's dynamically captured/compiled through
the same overlay pipeline as a true overlay, just happening to live in
main-EXE address space — the actual generated source for this build lives
at `build-release/cache/SLUS-00662/gcc/win-x64/cg10_022d09e7_gcc15c8ed0_f0/
7238DF29_patched.c`, compiled to `0010B000_7238DF29.dll`. Worth knowing if
this is ever grepped for in the wrong generated-source set.

## Mechanism

The function's own loop-iteration count varies per call — presumably
proportional to how much compressed data a given entity/frame's payload
actually contains — and each iteration costs a roughly-fixed amount of
work (bit-refill + two table lookups + branch). More iterations, more
wall-clock time, with no external event (no I/O wait, no lock, no OS
preemption) involved at all: it's a plain, correctly-executing, CPU-bound
loop that simply has to do more passes on some calls than others. That's
also exactly why nothing else in this investigation ever found a cause:
dispatch rate, MDEC decode, XA audio, disc I/O, the present/vsync call,
and general audio/SPU processing were all checked and cleared (see
`fmv-frame-stall.md`), and a direct CPU-time cross-reference showed
99.1% of the worst frames consumed *normal, full* CPU-time despite
running 3-4x slower — the thread genuinely was busy the whole time, just
not on anything any of those earlier checks were looking at.

## Evidence (confidence-graded — cite accordingly)

| Claim | Confidence | Method |
|---|---|---|
| MDEC decode duration (max 1.57ms) and XA audio decode duration (max 0.18ms) are both far too small to explain 20-134ms stalls | High | Direct per-call timing via new `latency_ring` extensions (`latency_ring_mdec_begin/end`, `latency_ring_xa_begin/end`), wrapping the actual `execute_decode()`/`maybe_deliver_xa_audio()` calls, sampled across a full FMV capture window |
| `0x0010C89C`'s single-call dispatch duration reaches 20-67ms | High | Direct per-call timing via a new `latency_ring_dispatch_begin/end` extension wrapping `overlay_loader.c`'s actual native dispatch call (`c->fn(cpu)`), at both call sites, across two independent capture rounds (first round: 34-42ms; second, larger round: up to 67.2ms) |
| `0x0010C89C`'s caller is the same function that also calls `RoomLib_InitC` | High | Temporary printf probe on `cpu->gpr[31]` at the exact dispatch call site, live, during FMV — a direct read of the register, not inference |
| The function is a genuine Huffman/RLE-shaped bitstream decoder, not unrolled/dead code | High | Full instruction-by-instruction disassembly (`mem_words` + custom decoder script) confirming real backward branches and live register-value tracking across multiple calls (constant table base, alternating output buffer) |
| Call duration correlates with loop iteration count | **High — directly measured, not inferred** | A real iteration counter added to the function's own generated source (details below), correlated against `__rdtsc()`-measured call duration across 324 real calls: **Pearson r=0.69, Spearman r=0.73** (rank correlation, more robust to noise). One clear TSC-migration artifact (`iters=12305, tsc=24`) identified and excluded by an unambiguous sanity filter (`tsc > 50×iters`), not by hand-picking a nicer result. |
| The two highest-iteration calls in the sample are also the two most severe stalls | High | Same dataset: 14,050 iterations → 67.2ms; 14,090 iterations → 47.8ms; both stand out clearly from the rest of the (324-row) distribution |
| Gameplay shows this class of stall at ~12x lower incidence than FMV on the same build/machine | High | Identical `latency_ring` capture methodology run at a real gameplay savestate location vs. the boot FMV — full table in `fmv-frame-stall-plan.md`'s Phase 1 result |
| The specific semantic type of data being decompressed (animation? per-frame entity table? script bytecode?) | **Not established** | Structurally characterized only (per-entity, shared static Huffman-shaped table, double-buffered output) — not pursued further since it wasn't needed to explain the mechanism; would need decomp-side tracing of what populates the `$a0`-addressed buffer, upstream of this call |

## Tools & methodology — how this was actually found

This section is deliberately detailed. Everything here is either an
existing `psxrecomp` runtime debug-server command (two of which we had
not seen documented or used anywhere else in this project's own notes)
or a small, self-contained, fully-reverted temporary instrumentation
pattern that should be easy to reuse on a different title or a different
stall.

### 1. Extend the existing per-frame `latency_ring`, don't build something new

`psxrecomp/runtime/src/latency_ring.c`/`.h` already had an always-on
per-frame timestamp ring (used throughout this whole multi-session
investigation, originally built for a completely different `"latency"`
debug command). Rather than writing new tooling, we kept extending this
one struct/API pattern every time a new candidate needed timing:

```c
/* latency_ring.h */
uint64_t latency_ring_dispatch_begin(void);
void     latency_ring_dispatch_end(uint64_t start, uint32_t addr);
```

`latency_ring_dispatch_begin()` returns a `QueryPerformanceCounter`
timestamp; `_end()` computes the delta and updates the **current frame
slot's** max-so-far fields (`dispatch_max_us`, `dispatch_max_addr`,
`dispatch_count`) — cheap (one QPC read in, one QPC read + a couple of
comparisons out, no allocation, no locking), and it composes: MDEC, XA
audio, and dispatch timing all sit side-by-side in the same per-frame
struct without interfering with each other. Wired into exactly the call
sites that mattered: `mdec.c`'s `execute_decode()`, `cdrom.c`'s
`maybe_deliver_xa_audio()`, and **both** of `overlay_loader.c`'s
`c->fn(cpu)` native-dispatch call sites.

**Practical limit worth knowing**: the debug server's raw-dump reply
buffer is a fixed `rawbuf[16384]` (`debug_server.c`'s `handle_latency`).
Every field you add to the per-frame JSON shrinks how many frames fit in
one poll before it silently truncates (not an error — you just get fewer
frames back, or in the worst case a malformed/truncated JSON parse
failure on the client). We had to drop `count` from 150→70 once when
adding fields; budget for this before adding a fifth or sixth field to
the same struct.

### 2. `overlay_cps_probe` — an existing debug command, undocumented outside
this brief, essential for diagnosing "why does this address never go
native"

```json
{"cmd":"overlay_cps_probe","addr":"0x8010C89C"}   // arm
{"cmd":"overlay_cps_probe"}                        // dump last decision
```

Returns `outcome` (`0`=no candidate found at all, `1`=CRC mismatch→
interpreter, `2`=ran native, `3`=device-touch→interpreter, `4`=blocked)
plus the internal candidate-index state (`ci`, `chosen_nranges`,
`cands_in_range`, `crc_matched`). This is a live tap into
`overlay_loader.c`'s own dispatch-resolution decision for one address —
we used it twice: once to confirm the real game genuinely calls this
address at a plausible rate (it does — ~15-30/sec during FMV), and once,
much more usefully, to diagnose why a *manually-compiled* replacement DLL
for this address was resolving to `outcome:0` (interpreter fallback)
despite its `.ranges` manifest being present and correctly indexed — see
WO-9 below. If you're ever debugging "this address should be native but
isn't," arm this before adding print statements anywhere else.

### 3. `overlay_loader_status` — the loader's last rejection reason, stored
but not logged anywhere by default

`overlay_loader.c`'s internal `loader_log()` helper (used for every
`LoadLibrary`/ABI/manifest-mismatch rejection reason in the loader) only
writes to a static buffer (`s_last_msg`) — it does **not** write to
stderr, so none of those rejection reasons show up in a normal play
session's log no matter how verbose. The only way to see the most recent
one is:

```json
{"cmd":"overlay_loader_status"}
```

which returns (among other counters) `"last_msg"`. This is how we found
the exact rejection reason in WO-9 below — worth knowing this exists
before assuming a load failure is unexplainable from outside.

### 4. `mem_words` + a small custom MIPS decoder for ground-truth disassembly

`{"cmd":"mem_words","addr":"0x8010C89C","count":150}` returns raw 32-bit
words at a live address — no rebuild, no symbol table needed. We wrote a
small (~90 line) standalone Python MIPS decoder against this (opcode
field extraction, sign-extension, branch-target arithmetic, tagging
backward branches and `jal`/`jr` specifically) rather than trusting any
static/symbolic tool, since this address doesn't even exist in the
statically generated shards (see "Root cause" above) — there was nothing
for a symbolic disassembler to show. This is the same technique used
earlier in this project's WO-6 investigation and is worth keeping around
as a standing utility rather than rewriting each time; happy to hand over
the script.

### 5. A self-contained iteration counter added directly to the generated
overlay source — the key technique for turning "looks correlated" into a
measured number

To get the iteration-count/duration correlation in "Evidence" above, we
edited the **generated** `_patched.c` for this function directly (not the
recompiler itself — a one-off, temporary, hand-patch of one function's
output for measurement purposes only):

```c
/* near the top of the file */
unsigned long long g_probe_c89c_iters = 0;
static unsigned long long g_c89c_entry_tsc = 0;
static unsigned long long g_c89c_call_no = 0;

/* at the true start of a fresh top-level call — see pitfall #2 below for
 * exactly where that is in CPS-generated code */
g_c89c_entry_tsc = __rdtsc();
g_c89c_call_no++;
g_probe_c89c_iters = 0;

/* inside each of the function's two loop-header blocks */
g_probe_c89c_iters++;

/* immediately before each of the function's two real `return;` statements */
if (g_c89c_call_no <= 800) {
    fprintf(stderr, "PE_ITERS_SELF: call=%llu iters=%llu tsc=%llu\n",
            g_c89c_call_no, g_probe_c89c_iters, __rdtsc() - g_c89c_entry_tsc);
}
```

**Why `__rdtsc()` and not a cross-DLL extern/callback**: overlay DLLs are
`LoadLibrary`'d dynamically at runtime, not statically linked against the
runtime EXE — the EXE is built and linked before any overlay DLL exists.
A plain `extern` declaration in `overlay_loader.c` referencing a global
defined inside the overlay DLL fails at **link time**
(`undefined symbol`), and there's no import-library relationship to fix
that. `__rdtsc()` (via `<x86intrin.h>`) needs no external symbol at
all — it's a CPU instruction, fully self-contained inside the one
generated file being measured. `fprintf(stderr, ...)` likewise needs
nothing external (stdio is a process-wide CRT resource any DLL can use).
This pattern generalizes to instrumenting *any* single generated overlay
function without touching the runtime EXE at all.

**Two pitfalls hit and worked around, both worth knowing before repeating
this**:

1. **`compile_overlays.py`'s autocompile regenerates `_patched.c` from
   scratch** whenever it decides a DLL needs rebuilding — it does not
   preserve hand edits to previously-generated source. If you rename/
   delete a DLL to force a rebuild while iterating on a hand-patched
   source file, the next autocompile pass silently wipes your edits
   before compiling. Worked around by extracting the exact `gcc`
   invocation `compile_overlays.py`'s own `_compile_dll_direct()` uses
   and calling it manually, then launching with `-NoAutocompile` so the
   pipeline never touches the region again during the measurement
   session.
2. **A CPS-generated function's "fresh call" path is not the switch case
   you'd expect.** Every CPS-generated function begins with something
   like:
   ```c
   if (cpu->pc != 0u) {
       switch (_cont) {
           case 0x80100004u: goto block_80100004;   /* a continuation */
           ...
           case 0x8010C89Cu: break;                  /* "own entry" case */
           default: ...
       }
   }
   /* <-- the ACTUAL fresh-call landing point for the common case */
   debug_server_log_call_entry(0x8010C89Cu);
   block_8010C89C:
       ...
   ```
   A genuine fresh top-level call (the overwhelmingly common case — a
   `jal` from elsewhere dispatching in) leaves `cpu->pc == 0` on entry,
   which skips the **entire** `if (cpu->pc != 0u) {...}` block — the
   `case <own-entry-addr>: break;` arm is only reached by an explicit
   resume-at-own-start, not the normal call path. We first placed the
   counter-reset code inside that case and got obviously-wrong data
   (`call_no` stuck at 0, `iters` climbing monotonically forever across
   dozens of prints) — caught before it was trusted, by the data itself
   being an impossible shape, not by re-reading the codegen a second
   time first. Fixed by moving the reset to the unconditional line right
   after the `if` block, which both the "own entry" case's `break` and
   the `cpu->pc==0` skip converge on.

All of the above — the source edits, the manual DLL, its `.ranges` file —
were fully reverted after measurement; nothing from this section is
present in the current tree.

## Candidate fix (not implemented, for whoever owns this asset path)

**We don't have enough visibility into the asset pipeline to say this
confidently, so treat these as starting points, not a prescription:**

- If the same entity's compressed data is decoded repeatedly across the
  rotating intro's cycle (rather than once per unique entity), caching
  the decoded output the first time and reusing it on subsequent passes
  would eliminate the repeat cost entirely. Not yet checked whether this
  is the case — `$a0`'s advancing input-buffer-per-call pattern is
  consistent with either "one entity per call, many unique entities per
  frame" or "the same entities revisited every intro cycle"; the
  double-buffered `$a1` output target is consistent with re-decode into
  alternating buffers rather than a persistent decoded cache, which
  argues weakly for "yes, it re-decodes every time," but this wasn't
  confirmed.
- If the data genuinely differs every call (no redundant work to cache),
  the only lever left is spreading the cost — decoding off the hot
  render/dispatch thread ahead of when it's needed, if the engine's
  structure allows a frame or two of lookahead during FMV specifically.
- **Not a fix**: nothing about this is `--force-interior`/dispatch-index/
  RoomLib-classification territory — this function already runs fully
  native, with correct classification, at normal dispatch cost. The cost
  is intrinsic to the decode work itself, not a `psxrecomp` overhead on
  top of it.

## Scope beyond this title

**Unknown, not characterized.** Unlike WO-6 (SDK-level `StGetNext`,
almost certainly present in any PS1-era title using overlays) or the
RoomLib classification bug (a recompiler-classifier defect, title-
agnostic by construction), this specific function and its data format are
almost certainly Parasite Eve-specific asset-decompression code, not
shared SDK/engine code — nothing here suggests this reproduces on Tomba,
MMX6, or any other psxrecomp title. Worth checking only if another title
shows an FMV-specific (not general) frame-stall pattern with a similar
"CPU-busy, normal dispatch rate, no elevated exception/interp share"
signature — the *methodology* (time the dispatch call by duration, not
subsystem or rate) generalizes even though this specific address won't.

## Verify (for whoever picks this up)

1. Re-resolve the address before reusing anything above — it's specific
   to this session's overlay layout. Arm `overlay_cps_probe` on the
   caller function (`0x80192934`, itself reached from `RoomLib_InitC`'s
   sibling call site) to confirm the same caller relationship still
   holds, then use `mem_words` to re-disassemble and confirm the same
   loop shape.
2. Re-run the `latency_ring_dispatch_*` capture (already in the tree,
   `TEMPORARY (2026-09-12 FMV-dip investigation)`-tagged, cheap to leave
   permanently) during FMV and confirm `disp_addr`/`disp_max_us` still
   points at the same address with comparable magnitudes.
3. If pursuing a fix, re-add the iteration counter (pattern above) as the
   ground-truth check that any caching/prefetch change actually reduces
   iteration count or call frequency for the affected calls, not just
   that frame time improved (which could be confounded by anything else
   changing at the same time).

## Risk

None to game correctness from this investigation itself (pure
measurement, no functional code changed, all instrumentation reverted
and verified clean — a follow-up launch with normal autocompile enabled
regenerated a fresh production DLL with no instrumentation, ran without
error). Risk applies only to whatever fix is eventually attempted, which
this brief does not propose with enough confidence to assess on its own.

---

# WO-9: a manually-compiled overlay DLL is silently rejected — no visible
error unless you know to ask `overlay_loader_status`/`overlay_cps_probe`

**STATUS: not a bug — the loader is working as designed.** Filed as a
dev-tooling/dev-experience gap, found as a byproduct of WO-8's
instrumentation work, not a game-performance issue.

## Classification

Not a bug in `psxrecomp`'s production path — this only affects a
developer hand-compiling a replacement overlay DLL outside the normal
`compile_overlays.py` pipeline (exactly what WO-8's iteration-counter
instrumentation required). The loader's rejection is the *correct*
behavior for an out-of-band publish; the gap is purely one of
discoverability.

## Symptom, exactly as observed

A hand-compiled DLL (correct exports, correct manifest-matching function
set, `.ranges` sidecar present and — confirmed via
`PSX_OVERLAY_CACHE_INVENTORY=1` at startup — correctly scanned and
indexed with the right function count) still resolves every dispatch to
its address as `outcome:0` ("no candidate found") via `overlay_cps_probe`
— i.e. falls to the interpreter forever, with **no error printed
anywhere** in the normal play-session log, `stdout`, or `stderr`.

## Root cause

`overlay_loader.c`'s `loader_log()` helper — called from every rejection
branch inside `load_overlay_dll()` (ABI mismatch, missing export, and the
one that applies here) — only writes into a static buffer
(`s_last_msg`), never to `stderr`/`stdout`/any log file. The actual
rejection reason, retrieved via `{"cmd":"overlay_loader_status"}`'s
`last_msg` field immediately after triggering the load:

```
DLL/manifest pair mismatch in <path> -- rejecting without deleting
(publication may be in progress)
```

`compile_overlays.py`'s normal pipeline (`add_overlay_pair_export()`)
stamps every DLL it produces with an `overlay_pair_id()` export whose
return value matches a `P <hex>` line it writes into the sibling
`.ranges` manifest — a real, sensible atomicity guard against a DLL and
its manifest being read mid-publish (a torn write from the pipeline's own
replace protocol). A hand-compiled DLL that skips
`add_overlay_pair_export()` has no such export (`dll_has_pair_id=0`),
while the pre-existing `.ranges` file already has a pair ID
(`manifest_has_pair_id=1`) — `load_overlay_dll()` correctly treats this
mismatch as indistinguishable from a torn publish and rejects the whole
DLL, **silently** as far as any log a developer would normally look at.

## Workaround (not a maintainer-facing fix — for anyone else hand-
compiling an overlay DLL for debugging)

Add the matching export by hand before compiling, using the exact value
from the DLL's own sibling `.ranges` file's `P` line:

```c
PSX_OVERLAY_EXPORT uint64_t overlay_pair_id(void) {
    return UINT64_C(0x<value from the .ranges file's P line>);
}
```

## Candidate fix (for maintainers, optional — quality-of-life only)

Route `loader_log()`'s rejection messages to `stderr` (or a dedicated,
opt-in verbose flag, mirroring the existing `PSX_OVERLAY_CACHE_INVENTORY`
pattern for the startup scan) rather than only a query-on-demand buffer.
Zero risk to production behavior (log-only change); would have saved
real debugging time here, and would help anyone else who hand-iterates
on overlay DLLs for a similar investigation. Not urgent — both
`overlay_loader_status` and `overlay_cps_probe` already exist and solve
this once you know to reach for them; this is a "would have been nice to
discover sooner" note, not a functional gap.

## Scope beyond this title

Title-agnostic (shared `overlay_loader.c` code, not Parasite-Eve-specific
in any way) — but also low-impact, since it only affects manual/
out-of-band DLL compilation during debugging, not the normal
`compile_overlays.py` pipeline any real playthrough uses.

## Risk

None. Read-only/logging-only concern.
