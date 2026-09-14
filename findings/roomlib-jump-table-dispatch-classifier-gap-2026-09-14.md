# RoomLib jump-table dispatch: a third, still-open instance of the overlay-classifier gap, systemic across ~125 rooms

**Status: root-caused and locally fixed for two directly-confirmed
instances (21 addresses in the region active during the intro FMV, 182 in
a second, separately-discovered region — both found from real capture
data, not projected, both verified with a real before/after measurement);
the underlying mechanism is shown to be systemic (255 dispatcher files, 64
unique compiled addresses across the game); a computed,
not-yet-individually-verified candidate list is provided for the rest, and
a distinct, non-classifier BIOS-interpretation cost was found and ruled
out along the way (see the second follow-up below). Not yet reported
upstream.**

**Update, same day, later: the root-cause framing below ("MIPS jump-table
`switch` targets not recognized") has been superseded by a more precise,
fully-verified finding, and a real candidate fix now exists and has been
tested to work automatically (no manual address list needed). See "Follow-up
(2026-09-14, continued): corrected root cause and a working automated fix"
near the end of this document before reading the sections below at face
value — they're kept as-written for the historical trail, but the "MIPS
jump-table" explanation specifically should be read as superseded, not
current.**

## Status at a glance — what's actually fixed vs. still open

**None of this has been fixed by mstan's team, and none of it has been
sent to them yet.** Everything below is a local workaround
(`--force-interior` entries in this project's own `play.ps1`) found and
applied in this session. For contrast: mstan's team's actual, already-merged
fix is PR #349 (`fix/observed-overlay-interiors`, see
`roomlib-interior-classification-ai-brief.md`) — that fix is real, working,
and not in question here. Everything in this document is a *different*,
narrower gap their fix doesn't reach, discovered after their fix was
already in place, that they have not seen.

| Item | Status |
|---|---|
| 21 addresses, `0x80191xxx` region (the one active during the intro FMV: `0x80191210`-`0x8019122C`, `0x80191230`, `0x801912A4`-`C8`, `0x80191318`/`8019131C`) | **FIXED.** Live in `build/play.ps1`'s `$ForceInterior` list right now. Verified with a real before/after: the 45M-instruction dirty-RAM spike this document opens with is gone (~450-2200x reduction, reproduced at two timestamps). |
| 182 addresses, separate `0x8018F000` region (`0x8018F77C`-`0x8018F7EC` + `0x8018F95C`-`0x8018FBBC`) | **FIXED.** Also live in `play.ps1`'s `$ForceInterior` list now. Verified *safe* (healthy `autocompile_status`, no compile-storm symptoms) but its real-world performance impact was **not** separately measured — this overlay isn't loaded during the intro sequence the 45M-instruction number came from, so fixing it didn't (and wasn't expected to) move that specific number further. It's a real, directly-confirmed bug (99.5% of that region's executed code was excluded) — just for a different room/scene than the one this document's headline number is about. |
| 640-address candidate list for the other 63 unique dispatcher addresses game-wide (companion file `analysis/roomlib-jump-table-2026-09-14/candidate-addresses.md`) | **NOT FIXED, NOT APPLIED.** This is a computed prediction only (one confirmed instance + a two-point size match, extrapolated). Nothing from this list has been added to `play.ps1`. Do not treat these 63 addresses as fixed — they're "check here first" candidates for whoever plays through those specific rooms/scenes, nothing more yet. |
| The general classifier gap itself | **Root cause corrected (verified); the candidate fix is NOT safe as written — do not apply or propose it as-is.** The original framing on this line ("MIPS jump-table `switch` targets not recognized") is superseded — the actual, fully-verified cause is that `FUNCTION_POINTER_TARGET`, the classification meant to catch exactly this case, is unreachable dead code in the current tool (both its population paths are permanently inactive for real captures; this part is solid). A patch to a **copy** of `compile_overlays.py` (`compile_overlays_patched_test.py`, not the real file) tested clean offline (`built OK: 176, FAILED: 0`) but **failed badly live**: a real boot with the patch active and no `--force-interior` hit 988M+ cumulative interpreted instructions and climbing after 3+ minutes (vs. 45M unfixed, vs. 20K-101K with the existing manual list) — a compile-storm regression, because the patch recovers every `OBSERVED_PC_ONLY` address in every region it ever sees, unscoped. See the correction subsection near the end of this document. The real `compile_overlays.py` is unmodified; the manual `$ForceInterior` list remains the actual deployed fix. |
| The ~20K-100K post-fix residual (`20,304` at T+120s, `101,046` post-skip) | **Not a bug — investigated and ruled out.** Confirmed via `current_func` sampling to be genuine, architecturally-irreducible PS1 BIOS ROM/kernel interpretation during active CD-ROM/MDEC work, not a classifier exclusion. Nothing to fix here; don't spend more time chasing this specific number. |
| Connection to `video-bleed-through-splash.md`'s visual bleed-through glitch | **Still unconfirmed, open question.** Attempted the same repro before and after the fixes above and got a clean result both times — that bug is independently documented as timing/race-sensitive, so this neither confirms nor rules out a relationship. |

Spun out of `pe-mod-movement-verification-2026-09-13.md`'s dirty-RAM
follow-up, which found the immediate instance during an intro-FMV
investigation. This document is the full, standalone technical trail from
the user asking "have you figured out the dirty ram problem" through to
the systemic scope — kept separate because it outgrew being a subsection
of a mod-verification document and is a real, actionable recompiler
finding in its own right, in the same family as
`roomlib-interior-classification-ai-brief.md` and
`roomlib-0x80191200-interior.md`.

## The symptom that started this

Live-monitoring `freeze_check`/`overlay_loader_status` through a full
intro-FMV boot (fresh launch, `fullscreen=1` per
`video-bleed-through-splash.md`'s repro method, synthetic Start-press skip
via the debug server — no keyboard needed):

- Flat at the usual idle baseline (203 blocks / 257 instructions,
  identified separately as harmless BIOS interrupt-vector interpretation)
  for the first ~90 seconds.
- Then **exploded to 17 million, then 45+ million interpreted
  instructions**, still climbing at roughly 2M/sec, through the skip
  transition and settling menu.
- **Went completely flat again the instant the menu screen stabilized**
  (unchanged across 4+ seconds once settled) — so this is tied to
  something active specifically during FMV/video-decode playback, not a
  permanent leak.

## Root cause

`autocompile_status`'s `output_tail` during the spike showed the
classifier explicitly excluding a run of addresses as
`"excluded: OBSERVED_PC_ONLY"`:

```
80191230, 801912A4, 801912A8, 801912AC, 801912B0, 801912B4, 801912B8,
801912BC, 801912C0, 801912C4, 801912C8, 80191318, 8019131C
```

Traced these to actual source via `room_m087.yaml`'s function-offset table
and `sym.room_m087.txt`:

- `0x801912A4`-`0x801912C8` sit inside `func_80191244`, a 136-byte
  function whose entire decompiled body
  (`src/overlays/room_m087/func_80191244.c`) is one macro invocation:
  `ROOMLIB_STATE_DISPATCH_VARIANT2(func_80191244,
  RoomLib_ResetAndSignalB_80191984)`.
- `0x80191318`/`0x8019131C` sit inside the next function,
  `RoomLib_Notify2ArmB_801912CC` (168 bytes).

`room_lib.h`'s macro definition:

```c
#define ROOMLIB_STATE_DISPATCH_VARIANT2(name, tickFn) \
    int name(RoomEnt *o) { \
        switch (func_800DFB78()) { \
        case 0: \
            if (o->link->variant < 2) { \
                return 0; \
        ...
```

A `switch` over dense small-integer cases compiles to a MIPS jump table:
the CPU reaches each `case` body via a **computed** `jr` (jump register,
loaded from a table read at runtime), not a `jal` call. That's exactly the
shape that produces a cluster of addresses individually "observed
executing" but never seen as a called function entry — which is precisely
what `OBSERVED_PC_ONLY` means.

## Why this isn't just the already-fixed bug recurring

This project already found and fixed this general failure class twice
(`roomlib-interior-classification-ai-brief.md`): mstan's team's upstream
fix (PR #349, `fix/observed-overlay-interiors`) teaches the classifier to
retain execution evidence for a "hostless" dispatch target instead of
dropping it when a shared-alias check rejects it. That fix **is already
present** in this project's `psxrecomp` checkout (ported as commit
`a94ab281`) — confirmed directly by reading
`psxrecomp/tools/compile_overlays.py`: `print_seed_audit()` appends
`"; isolated fragment demand retained"` to an `OBSERVED_PC_ONLY` line when
the address is in
`unhosted_dispatch = (dispatch_fragment_demands & executed_pcs) -
included_reasons`.

Tonight's 13 addresses printed with **no** such recovery suffix — meaning
they were never in `dispatch_fragment_demands` at all, not that they were
in it and still got dropped. That set is built from statically
discoverable jump targets (the kind a disassembly pass can identify
directly, e.g. a literal `jal`). A `switch`'s jump-table targets come from
a runtime data-table read (`lw` from a table address computed from the
switch value, then `jr`) — this classifier's static pass evidently doesn't
resolve that into a demand record the same way it does a direct call.

**Conclusion: this is a real, narrower, still-open gap, related to but
distinct from the bug PR #349 fixed.** The fixed mechanism recovers
unhosted-but-statically-demandable addresses; MIPS jump-table case targets
from a runtime-computed `switch` fall outside what currently counts as
"demandable." Worth reporting upstream as a follow-up to PR #349, but not
done here — would need the same kind of synthetic before/after test the
original brief used, built around a jump-table case specifically.

## Fix applied and verified

Added the 13 addresses to `build/play.ps1`'s default `$ForceInterior`
list (alongside the five already there from the earlier bug). Relaunched
fresh, replayed the identical ~90-120s intro window:

| | dirty_ram_insns at ~T+120s / post-skip |
|---|---|
| Before fix | 45,338,450 (still climbing) |
| After fix | 20,304 → 101,046 (settled, not climbing) |

A ~450-2200x reduction, confirmed at two independent timestamps. Real,
measured, already in the launch script — not a hypothesis.

**Not established**: a confirmed link to the still-open
`video-bleed-through-splash.md` visual bug. Attempted the same synthetic
skip both before and after this fix and got a clean menu both times — that
bug is independently documented as timing/race-sensitive (not reliably
reproduced every attempt), so two clean results neither confirm nor rule
out a connection. What's true independent of that open question: this is
a real, previously-uncataloged interpreter-classification bug, now fixed
with a measured order-of-magnitude improvement specific to the game's
intro sequence.

## Scope: this is systemic, not a one-off

Grepped the whole decomp for the macro:

```
grep -r ROOMLIB_STATE_DISPATCH src/overlays   # 255 files
```

- **250 files** use `ROOMLIB_STATE_DISPATCH_VARIANT2` (the variant
  confirmed buggy above).
- **5 files** use the plain `ROOMLIB_STATE_DISPATCH` (a related but
  smaller macro — not confirmed either way tonight, listed for
  completeness: `room_m063`, `room_m083` at `0x8018F250`, plus
  `room_m358`/`room_m384`/`room_m387` at `0x80192744`).
- Every dispatcher function's file name encodes its own compiled VRAM
  address (`func_XXXXXXXX.c` or the more descriptively renamed
  `RoomLib_StateDispatchVariant2_XXXXXXXX.c`) — extracted all 250
  addresses programmatically, no misses.
- **Deduplicated to 64 unique addresses.** Many rooms share an identical
  overlay code layout (same "room template," different room-specific data
  elsewhere), so the same dispatcher lands at the same address across
  dozens of rooms — e.g. `0x8018F500`/`0x80190240` alone covers ~29 rooms
  (`m022, m032, m059, m061, m062, m066, m067, m078, m081, m197, m198, m199,
  m201, m206, m207, m210, m214, m217, m218, m219, m220, m226, m227, m232,
  m386, m405, m407, m408, m409, scene_e18, scene_e26`).

**Cross-check that the internal jump-table structure is identical, not
just superficially similar sizes**: compared `func_80191244` (room_m087,
136 bytes, our confirmed live capture) against `func_80190258`
(`scene_e27`, a different unique address) via `scene_e27.yaml`'s own
function-offset table — **also exactly 136 bytes**
(`0x12F8 - 0x1270 = 0x88`). Same for the following
`RoomLib_Notify2ArmB`-equivalent function in both rooms: **168 bytes each**
(`room_m087`: `0x238C-0x22E4`; `scene_e27`: `0x13A0-0x12F8`). Byte-identical
sizes at two independently-checked, differently-addressed instances is
strong (not certain) evidence the compiled jump-table layout — and
therefore the relative offsets of the excluded case-target addresses — is
identical everywhere this exact macro invocation appears.

## Computed candidate list (not individually verified except room_m087)

Using the confirmed offsets from the one live-captured instance
(`function_start + {0x60, 0x64, 0x68, 0x6C, 0x70, 0x74, 0x78, 0x7C, 0x80,
0x84}`), computed candidate interior addresses for all 64 unique dispatcher
addresses — 640 addresses total. Full list saved for reference (not
inlined at full length here to keep this document readable); the 64 base
addresses this was computed from:

```
8018F500 8018F508 8018F50C 8018F510 8018F514 8018F518 8018F51C 8018F520
8018F524 8018F534 8018F54C 8018F554 8018F558 8018F560 8018F578 8018F594
8018F5A4 8019019C 80190240 80190248 8019024C 80190250 80190254 80190258
8019025C 80190260 80190264 80190274 8019028C 80190294 80190298 801902A0
801902B8 801902D4 801902E4 80190504 8019050C 80190518 801905A0 80190668
80190A1C 80190A24 80190EDC 80190F38 80190F7C 80191150 80191244 8019124C
80191258 801912E0 801913A8 80191658 80191660 8019175C 80191764 80191C78
80191CBC 80191E90 80192398 801923A0 80193C94 801949D4 8019568C 801963CC
```

(`0x80191244` in this list is the one already directly confirmed via live
capture; its own 10 candidate addresses match the originally-found
`0x801912A4`-`0x801912C8` exactly, which is the self-consistency check
that this offset-projection method is being applied correctly.)

**This is a prediction, not a verification.** It rests on: (a) one
confirmed live instance, (b) a two-point size match across differently-
addressed instances as evidence of identical internal structure, and
(c) the assumption that the neighboring `RoomLib_Notify2ArmB`-style
function's own two interior addresses (found at `+0x4C`/`+0x50` from *its*
start in room_m087) also generalize — not independently re-checked at a
second site the way the dispatcher function's own offsets were. Treat this
list as "check here first" triage, not a ready-to-ship patch.

## Explicit warning: do not blanket-apply this list without testing

This project already tried, and explicitly rejected, a much larger
version of exactly this idea for the *original* RoomLib bug: forcing every
decomp-known overlay address at once (1,131 addresses via a patched
`fromfile_prefix_chars='@'` argument) produced a 237-DLL background-compile
storm and tanked speed to ~0.19x — far worse than the bug it was meant to
fix (documented in `roomlib-interior-classification-ai-brief.md` and the
raw `perf-investigation-log.md`). At 640 addresses this candidate list is
roughly half that scale and far more precisely targeted (all confirmed
instances of one specific, already-proven-buggy macro pattern, not "every
address the decomp happens to know about") — but the prior failure mode is
real and worth respecting. **Recommended approach**: add candidates
incrementally, in small batches (e.g. one unique dispatcher address's 10
candidates at a time), with a real before/after `dirty_ram_blocks`/compile-
storm check after each batch — the same matched-restart method documented
in the parent mod-verification doc — rather than adding all 64×10 at once
on the strength of a two-point size match alone.

## Follow-up: the post-fix residual (20,304 / 101,046) is not this bug — it's genuine BIOS cost

The user asked to keep targeting the specific post-fix numbers
(`20,304` at ~T+120s, `101,046` post-skip) — still ~80-400x the fully-idle
baseline of 257. Investigated properly rather than assuming it was more of
the same bug.

**Found and fixed two more real, directly-confirmed classifier gaps along
the way** (not projections — both found via `compile_overlays.py --check`
run offline against this session's real `overlay_captures.json`, same
method as `roomlib-interior-classification-ai-brief.md`'s own verification
section):

1. **8 addresses missed the first time**, `0x80191210`-`0x8019122C`,
   immediately before the already-fixed `0x80191230` — missed because the
   runtime's `autocompile_status` `output_tail` is capped and had
   literally cut the printed list off mid-word right before these entries.
2. **A separate, much larger gap in a different overlay**, `load=0x8018F000`:
   `executed_pcs: 183`, `function_entry_pcs: 1` — only the dispatch entry
   itself (`0x8018F958`) is classified; **182 of 183 observed addresses in
   the entire region are excluded** (two contiguous clusters,
   `0x8018F77C`-`0x8018F7EC` and `0x8018F95C`-`0x8018FBBC`). This is a real,
   severe instance of the same bug family — 99.5% of a region's executed
   code stuck in the interpreter — just not the one active during this
   specific intro-boot sequence (this overlay likely belongs to whatever
   room got visited during this session's later, unrelated menu/save
   testing, not the intro/title path). Added to `play.ps1` alongside the
   others.

**Both fixes verified safe** (healthy `autocompile_status`, no compile-storm
symptoms) but **neither changed the target residual at all** — `20,304`
and `101,046` reproduced exactly, to the integer, across three separate
launches (no fix, +8 addresses, +182 addresses). That's not a failed fix,
it's the actual answer: **this residual isn't caused by any classifier
exclusion**.

**Confirmed by sampling `current_func` repeatedly at the settled
post-skip state**: every sample was `0x00000F40`, `0x1FC01ACC`, or
`0x00001794` — never a game-overlay address. `0x1FC00000` is the real
hardware base address of the PS1 BIOS ROM; `0x00000F40`/`0x00001794` sit
in low kernel RAM. There is no overlay compiler for BIOS ROM — LLE
fallback for whatever BIOS calls aren't HLE-covered is always interpreted,
by architecture, not by a fixable classifier decision. Given this scales
with *active* CD-ROM/MDEC work (idle baseline 257 vs. this ~20K-100K
during actual video streaming) and goes fully flat the instant the video
stops, this is the legitimate cost of real BIOS-level CD/MDEC interrupt
handling during FMV — not a bug, and not something `--force-interior` (or
any overlay-classifier fix) can touch.

**Net result of this whole thread**: the original 45-million-instruction
classifier bug is fixed (now two confirmed fixes: 21 addresses in the
active region, 182 in a separately-discovered one). What's left after that
fix is a small, legitimate, architecturally-irreducible BIOS-interpretation
floor that scales with real CD/MDEC activity — a different kind of thing
entirely, not a further instance of the same bug to keep chasing.

## Recommended next steps

1. **Report upstream as a PR #349 follow-up**: the classifier's
   `dispatch_fragment_demands` set doesn't currently recognize MIPS
   jump-table case targets (from a runtime-computed `switch`) as
   demandable the way it does static `jal` targets. Needs the same kind of
   synthetic test the original brief used, built around a jump-table case
   specifically, to make an actionable report mstan's team can verify
   independently (their own review process for the original bug explicitly
   could not verify PE-specific numbers, only the general mechanism via
   their own titles — expect the same here).
2. ~~Verify a second instance live~~ **Done, though not the way originally
   planned**: rather than deliberately reaching `scene_e27`, running
   `compile_overlays.py --check` against this session's accumulated real
   capture data turned up a second, independently-discovered, directly-confirmed
   gap (the 182-address `0x8018F000` region) — a stronger form of
   verification than the planned live visit, since it's real capture data
   rather than one more live sample. The 640-address *projected* list for
   the other 63 dispatcher addresses is still unverified, though — that
   part of this recommendation still stands.
3. **Incrementally roll out the computed candidate list** per the warning
   above, batch by batch, watching for compile-storm symptoms
   (`autocompile_status.state` stuck non-idle, `shard_fail` climbing, or
   FPS dropping) after each addition — not a single blanket patch.
4. Re-attempt the `video-bleed-through-splash.md` visual repro several
   more times now that the intro-specific instance is fixed, to gather
   enough trials to say anything statistically meaningful about whether
   the bleed-through rate changed — a single clean/dirty result either way
   isn't enough given that bug's documented non-determinism.

## Follow-up (2026-09-14, continued): corrected root cause and a working automated fix

Re-examined the "MIPS jump-table `switch`" root-cause claim above after a
direct challenge to justify it, by reading `room_lib.h`'s actual macro
definition in full (not just the `switch` skeleton excerpted earlier) and
by reading `compile_overlays.py`'s classifier logic directly rather than
inferring it from behavior.

**Two corrections, in order of how the investigation actually went:**

1. **The dispatcher isn't necessarily a compile-time jump table at all.**
   `ROOMLIB_STATE_DISPATCH_VARIANT2`'s `case 0` calls through
   `o->sub.cb`, a struct field. Grepping `room_lib.h` further found a
   *different* macro, `ROOMLIB_ARM_IF_WINDOW_VIA` (~line 2272-2284),
   assigning `o->sub.cb = handler;` at runtime. So at least `case 0`'s
   dispatch is a genuine runtime function-pointer callback — undiscoverable
   by any static disassembly pass, not just this one. A 3-case `switch`
   (`case 0/1/2`) is also below the size where compilers typically bother
   building an actual jump table anyway. This cast real doubt on the
   original framing but didn't yet explain *why* the classifier misses it.

2. **The actual, fully-verified explanation: `FUNCTION_POINTER_TARGET` — the
   classification that exists specifically to catch function-pointer/jump
   targets like this — is dead code in the current tool.** Read
   `compile_overlays.py` end to end for every place this classification is
   assigned:
   - `for addr in captured_function_entries: include(addr,
     'FUNCTION_POINTER_TARGET')` — but `captured_function_entries` comes
     from `cap.get('function_entry_pcs', [])`, and checking the real
     `overlay_captures.json` directly: **every single capture has
     `"function_entry_pcs": []`** — always empty, by design (the classifier
     derives these itself elsewhere; this field was never meant to be the
     source, per mstan's team's own prior note referenced in
     `roomlib-interior-classification-ai-brief.md`).
   - The second path is gated by `legacy_seed_mode = bool(legacy_seeds) and
     not cap.get('schema')` — every real capture has
     `"schema": "psxrecomp overlay capture v2"` set, so `not
     cap.get('schema')` is always `False`. This path never runs either.
   - **Net result, verified against real data, not inferred**: no capture
     produced by the current tool can ever populate `FUNCTION_POINTER_TARGET`.
     It's unreachable. This is *why* neither a jump-table case target nor a
     runtime callback target ever gets classified as one — the mechanism
     meant to catch both is switched off by construction, not failing to
     recognize a specific instruction pattern.

   This finding doesn't depend on resolving whether the dispatch mechanism
   is a jump table or a callback — it explains why *neither* would ever
   have been caught.

### A working fix, written and tested (not yet upstream)

Rather than reviving `FUNCTION_POINTER_TARGET`'s dead paths, the simpler
fix reuses machinery that's already known-safe: PR #349's own
`dispatch_fragment_demands` / "isolated fragment demand retained" recovery,
today only fed by `DISPATCH_ENTRY`/`STATIC_DISPATCH_ENTRY` reasons. The
patch adds the same treatment for addresses that fall through to
`OBSERVED_PC_ONLY` in the final classification pass (`compile_overlays.py`
~line 1783-1789):

```python
for addr in sorted(candidates - set(included)):
    if addr in all_branch_targets or addr in jump_table_targets:
        excluded[addr] = 'BRANCH_TARGET_ONLY'
    elif addr in executed_pcs or addr in legacy_seeds:
        excluded[addr] = 'OBSERVED_PC_ONLY'
        if addr in executed_pcs and addr + 4 <= fragment_hi:      # <- new
            dispatch_fragment_demands.add(addr)                    # <- new
    else:
        excluded[addr] = 'UNKNOWN'
```

Applied to a **copy** of the tool
(`psxrecomp/tools/compile_overlays_patched_test.py` — the real
`compile_overlays.py` was not touched) and run offline via `--check`
against this session's real `build-release/overlay_captures.json`, with
**no `--force-interior` flags at all**:

```
Overlay 8018F000_150BCC29: executed_pcs 183, unhosted_executed_dispatch_fragment_demands 154
  → all 154 previously-OBSERVED_PC_ONLY addresses now show
    "excluded: OBSERVED_PC_ONLY; isolated fragment demand retained"
  interior fragments @0x0018F000: 154/154 exact-demand orphan interior(s) -> isolated island shards

Overlay 80191000_91CA50B4: unhosted_executed_dispatch_fragment_demands 21
  interior fragments @0x00191000: 21/21 exact-demand orphan interior(s) -> isolated island shards

=== SHARD BUILD SUMMARY ===
  built OK : 176
  skipped  : 1  (cached / data-only / safe coverage loss)
  FAILED   : 0
```

Every previously-stuck address across both captured overlay regions (175
total: 154 + 21) was picked up automatically and compiled without error —
**with the manual `$ForceInterior` list in `play.ps1` playing no role in
this test run at all.** This is a stronger result than the 208-address
manual list built up earlier tonight: it makes that manual list
unnecessary going forward, for these regions and (by the same mechanism)
any other region with the same shape of gap, without needing to
individually discover and hand-add each address.

**What this test does and doesn't establish:**
- **Does establish**: the classifier logic itself can be fixed, cheaply,
  in a way that reuses an already-shipped, already-safe recovery path —
  not a new, unproven mechanism. Proven via real capture data, not
  projection.
- **Does not establish**: in-game runtime correctness beyond a clean
  `--check` compile (no soak test done against this specific patch yet,
  though the underlying fragment-recovery mechanism itself is the same one
  PR #349 already validated at runtime). Generalization to overlay regions
  never captured this session (the real game has far more than these 2).
  Whether mstan's team would accept this exact patch shape or prefer a
  different one (e.g. reviving `FUNCTION_POINTER_TARGET` properly instead
  of routing through `OBSERVED_PC_ONLY`).

**Recommended next step**: propose this as a candidate fix on issue #365
(or a new PR) — framed explicitly as "here's a fix that tests clean
against real capture data" rather than "this is merged/validated," since
mstan's team's own process for the original PR #349 fix involved broader
synthetic tests and multi-title validation this local test doesn't
replicate.

### Correction, same day, a few minutes later — the patch is NOT safe live as written

The offline `--check` result above is real but was misleading about
real-world safety, and it's important this isn't taken further than it
should be. Ran the actual patched classifier **live**, in a real game
process (`build-dbg`, fresh boot, zero `--force-interior`), and watched
`dirty_ram_insns` through the intro FMV:

| Elapsed since boot | `dirty_ram_insns` | `autocompile_status.compile.state` |
|---|---:|---|
| ~15s | 2.4M | running |
| ~53s | 85M | running |
| 90s | 535M | running |
| 195s (3.25 min) | **988M**, still climbing | still "running", `shard_ok: 0` |

For contrast: the *original unfixed* bug topped out at 45M by this point;
the *already-deployed* manual `$ForceInterior` list settles at
20,304-101,046. This patched run blew past **988 million** and was still
climbing with zero shards reported complete after over 3 minutes. Killed
the process rather than let it run further.

**Root cause of the discrepancy**: the offline `--check` only replayed the
2 overlay regions already sitting in `overlay_captures.json`. Live, the
game visits many more overlay regions during actual play — the compile
log was caught mid-run building a fragment for `load=0x00052000`, a
region never present in the offline capture file at all. The patch as
written recovers *every* `OBSERVED_PC_ONLY` address in *every* region,
unconditionally, each as its own separately-compiled DLL ("isolated
island shard"). Live, each newly-visited area adds another batch of
one-DLL-per-address compiles to an already-overloaded background queue
that never catches up — this is the same compile-storm failure mode as
the previously-rejected 1,131-address/237-DLL experiment
(`roomlib-interior-classification-ai-brief.md`), just reached through the
classifier fix instead of a manual address list.

**What this does and does not change**:
- Does not change: the `FUNCTION_POINTER_TARGET`-is-dead-code diagnosis.
  That's verified against real data independent of whether this specific
  patch is safe to ship.
- Does change: **do not propose this patch upstream, or apply it locally,
  as written.** It is not a ready fix — it needs real scoping before it's
  anywhere close to safe: e.g. only recovering addresses observed hot
  across repeated visits (not on first sight), a cap on concurrent
  isolated-fragment compiles, per-region opt-in rather than global, or
  batching multiple addresses into fewer DLLs instead of one-per-address.
  None of that is implemented yet.
- The currently-deployed fix for dirty RAM remains the manual 208-address
  `$ForceInterior` list in `play.ps1` — untouched by this test, still the
  actual working mitigation right now.
