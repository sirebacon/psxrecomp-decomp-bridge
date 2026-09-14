# WO-3 (revisited): overlay classifier silently drops function entries — permanent interpreter fallback, recurring, still unfixed upstream

AI/agent-consumption brief, same format as `fmv-dispatch-overhead-ai-brief.md`.
Consolidates the original WO-3 (`field-report-technical.md`), its
first confirmed fix (2026-09-09), and its confirmed *recurrence* months
later (`roomlib-0x80191200-interior.md`) into one document with everything
needed to decide how to fix it upstream.

**Status: previously reported (as "Finding #2" / WO-3) in the original
field report. mstan's team fixed Findings 1, 3, and 4 from that report in
PR #344 — Finding #2 is not in that list and remains unfixed upstream.**
This project has been running a manual, per-address local workaround
(`--force-interior`) ever since, and that workaround has already had to be
extended once when the same bug surfaced at a new address in the same
region months later. That recurrence is itself part of the evidence this
needs a real fix, not another manual patch to the address list.

## Classification

**Recompiler-side, not a game-code issue.** The guest code being
misclassified is entirely ordinary, genuinely-executed PS1 code — the
capture mechanism itself observes it running (`dispatch_entry_pcs`,
`seeds` in the capture JSON all correctly list it). The bug is specifically
in `compile_overlays.py`'s decision about which observed addresses count
as compileable function entries.

## Objective

Stop a captured, genuinely-dispatched-to address inside an overlay from
being silently excluded from that overlay's `function_entry_pcs`, which
leaves it permanently running through the slow instruction-by-instruction
interpreter instead of ever being compiled to native code — with no
automatic recovery and no diagnostic indicating it happened.

## Symptom, first observation (2026-09-09)

RelWithDebInfo build, PE (`Parasite Eve`), in field play:

```
python tools/stall_report.py --port 4370 snap
```

```
interp_share   0.4075
[5] HOTTEST INTERPRETED PCs:
  0x80191B94  insns=383,000,000  ~26,000 insn/entry  [above-floor]
```

`0x80191B94` resolves to `RoomLib_InitD` in the decomp. It sits inside a
captured, otherwise-compiled overlay's address range, but never appears in
that capture's `function_entry_pcs` — so `compile_overlays.py` never
carves it into a compiled shard, and it falls back to the interpreter
*forever*, every single time it's reached, for the life of the process.

Manual proof it's fixable at all: `compile_overlays.py --force-interior
0x80191B94` → `interp_share` 40.8% → 4.1%, `dispatch_native` 0.8M → 36.2M.
Real build (RelWithDebInfo → Release), same fix: steady speed 0.72×
(degrading to 0.22× over time) → stable **0.80×**.

## Root cause — where in the code

- `compile_overlays.py`: `classify_overlay_seeds(cap, data, load_addr,
  size, …)` decides which addresses in a capture become entries vs.
  interior fragments vs. plain data.
- `legacy_seeds = _parse_addr_list(cap.get('seeds', []))` reads candidate
  seeds **from the capture itself**, not from the game's own
  `[recompiler] seeds` file (`sync_decomp.py`'s `ghidra_funcs.txt`, in this
  project's case — every decomp-known function address for every overlay).
- The recompiler's *main*-function compile pass is already invoked with
  `--seeds <seeds_path> --ws-config <game.toml>`, i.e. it already has
  access to the full, decomp-derived seed list — but that same list is not
  fed into the **interior classification** step for overlay regions. An
  address can be well-known and decomp-confirmed and still get dropped
  here because the *capture's own* observed seed list (built purely from
  what got dispatched to during that specific run) is incomplete or
  differently-shaped than the full known set.
- Confirmed directly on-disk (see "Recurrence" below): a capture can show
  an address correctly present in `dispatch_entry_pcs` and `seeds`, with
  `function_entry_pcs: []` — the classifier sees it being dispatched to
  and still doesn't promote it.

## Evidence this recurs — it is not a one-off, fixed-forever bug

The original fix (2026-09-09) force-carved 4 addresses in PE's shared
"RoomLib" resident overlay (`0x80191B94`, `0x801927D0`, `0x80192E3C`,
`0x801925D4`), confirmed via a real rebuild: `interp_share` 40.8% → 4.1%.

**Two months of play later, a fifth address in the exact same overlay
region hit the same failure mode independently** — `0x80191200`, found via
an unrelated investigation (comparing an idle-titlescreen window against
an active-video window). Confirmed via the identical mechanism:

```json
{
  "load_addr": "0x8018F000", "size": 20484,
  "dispatch_entry_pcs": ["0x801911F8", "0x80191200", "0x80191320", ...],
  "function_entry_pcs": [],
  "seeds": ["0x801911F8", "0x80191200", "0x80191320", ...]
}
```

`0x80191200` is present in `dispatch_entry_pcs` and `seeds` — the capture
genuinely observed it being dispatched to — and `function_entry_pcs` is
still empty. Textbook repeat of the same bug, same overlay region, new
address, found only because the game happened to exercise a slightly
different code path (the idle/attract-wait loop) than whatever produced
the original capture. **This means the actual population of affected
addresses is a function of exactly what code paths get exercised during
whatever capture happens to run** — there is no reason to believe the
current 5-address force-interior list is complete, only that it's
complete *for the specific play sessions that have been captured so far*.

Confirmed end-to-end after adding the 5th address and doing a real,
from-scratch rebuild (autocompile, real GCC, matching normal play):

| | Active window (before → after) | Idle window (before → after) |
|---|---:|---:|
| `interp_share` | 48.5% → **8.0%** | 93.6% → **7.9%** |
| interpreted instructions (60s sample) | — | 124.6M → **0** |
| `dispatch_interp_fallback` | — | 225,249 → **0** |

The idle window is the more dramatic number: before the fix, the title
screen / attract-wait loop spent **93.6% of its time in the interpreter**
— worse than any active gameplay measured in this project. Per this
project's own testing, this translated to a visible, severe framerate
problem in menus specifically (reported by the user as roughly 12fps)
before the fix, and a stable 60fps after.

## The current "fix" is a manual workaround, not a fix

What's actually deployed (`psxrecomp-decomp-bridge/build/play.ps1`):

```powershell
[string[]]$ForceInterior = @('0x80191B94','0x801927D0','0x80192E3C','0x801925D4','0x80191200'),
```

This is `compile_overlays.py`'s existing `--force-interior` flag, applied
per-address, entirely outside the classifier. It works — every address on
the list gets carved into an isolated "island shard" DLL independent of
the main region — but it requires a human to already know the exact
address, find it via live diagnosis, and add it to a list by hand. It does
nothing for the *next* address this same bug hits in a code path nobody
has exercised yet. The `0x80191200` recurrence is direct proof this
happens: it took roughly two months of otherwise-normal play before that
specific code path got hit and the gap surfaced.

**A related manual-only workaround already tried and explicitly rejected**:
forcing *every* decomp-known overlay address at once (a blunt
"just carve everything" approach) via a patched
`argparse.ArgumentParser(..., fromfile_prefix_chars='@')` and an
`@file` listing 1,131 addresses. Result: a 237-DLL background-compile
storm, ~0.19× — far worse than the bug it was meant to fix. **Brute-forcing
every candidate is not a viable fix**; whatever the real fix is, it needs
to be selective, not exhaustive.

## Candidate fix (not implemented — for the maintainers to evaluate)

After loading a capture in the region-compile path, **union into the
interior-candidate set every address from the game's own
`[recompiler] seeds` list that falls within `[load_addr, load_addr +
size)`** — i.e. bring the same decomp-derived, already-known-complete seed
list that the main-function compile pass already uses into the interior
classification step too, instead of relying solely on whatever a specific
capture happened to observe. Guard: only carve addresses whose bytes are
actually present in *this* captured image (don't force-compile addresses
a particular overlay variant doesn't contain) — this is exactly the guard
that made the blunt "force everything" attempt above fail (no per-capture
presence check) and that a scoped, capture-local version would need to
avoid repeating that failure.

A cheaper, already-half-implemented stopgap exists for a curated address
list specifically (not a substitute for the real fix, just less manual
than hand-editing a `--force-interior` flag list each time): the
`fromfile_prefix_chars='@'` addition to `compile_overlays.py`'s
`ArgumentParser`, so a maintained address list can be passed as `@file`.
Useful for iterating on this bug's own address list; still requires a
human to find each address first.

## Distinguishing test — not every hot interpreted PC is this bug

Worth including explicitly since it cost real investigation time once
already: a second hot address (`0x80193084`, PE's New Game/Continue/
Tutorial menu, 89.9% `interp_share`, 140,846 insn/entry) looked identical
to this bug at first glance but wasn't it — left running with normal
overlay autocompile active for ~90 more seconds, no manual force-interior,
no code change, and the capture matured on its own: `interp_share` dropped
to 0.66% unassisted, and a repeat visit was fast from then on. That's
ordinary "first visit compiles in the background" behavior, not a
permanent classifier miss.

**The test that tells them apart**: revisit the same screen/area a second
time. Stays fast → normal warm-up, not this bug. Warms up slowly *every*
visit → a genuine missing-function-entry case, worth the full
`--force-interior` treatment (or, ideally, the real classifier fix above).

## Scope beyond this title

**Likely affects every psxrecomp-based title, not only Parasite Eve.**
`classify_overlay_seeds` is shared tooling (`compile_overlays.py`), not
game-specific code — any title with overlay-compiled code whose capture
history doesn't happen to include every genuinely-reachable code path will
hit the identical failure mode, silently, for whatever addresses its own
players' sessions haven't captured yet. This project has already observed
it recur once, independently, on a single title over a few months of
normal play — there is no reason to expect other titles are immune, only
that nobody has necessarily gone looking for it via the same
active-vs-idle comparison technique that surfaced the second instance
here. **Not empirically verified against a second title.**

## Verify

1. Reproduce: `{"cmd":"stall_report","secs":60}` (or the `stall_report.py`
   CLI) during both an active-gameplay window and a genuinely idle window
   (confirm idle via `mdec_state`'s `dma_in_words` staying flat across
   several consecutive samples) — compare `interp_share` and `[5] HOTTEST
   INTERPRETED PCs`. Any `[above-floor]`-flagged address with millions of
   instructions and a flat/never-dropping count across repeat visits is a
   candidate.
2. Confirm it's this bug specifically, not warm-up: revisit the same
   screen/area a second time (see "Distinguishing test" above).
3. Confirm the mechanism directly: pull the on-disk `overlay_captures.json`
   for that region — `dispatch_entry_pcs`/`seeds` will include the address,
   `function_entry_pcs` will not.
4. If a fix is prototyped: re-run the same active/idle comparison —
   `interp_share` should drop to the ~8% healthy baseline in both windows,
   with zero interpreted instructions in a confirmed-idle window.

## Risk

Low risk to correctness either way — every interior fragment (forced or
classifier-carved) still passes the same per-function live-byte CRC guard
at dispatch time, so a wrongly-classified address simply won't load
rather than miscompiling. The real risk is scope/performance: carving too
aggressively (as the "force everything" attempt showed) produces a
background-compile storm that's worse than the bug. Any classifier change
needs the same "only carve what's actually present in this capture" guard
that a blunt seed-list union would need to include from the start.

## Upstream response (2026-09-12, `OBSERVED_OVERLAY_INTERIOR_REVIEW.md`, PR #349)

**Confirmed as a real shared-framework bug, independently — without ever
touching Parasite Eve's assets.** mstan's team reproduced the identical
failure class in their own saved Tomba (2 captures) and Mega Man X6 (4
captures) captures, with zero dependency on anything we reported. Direct
quote: *"The failure is reproduced without Parasite Eve assets, and
independently in saved Tomba and Mega Man X6 captures."* This is the
cross-title confirmation this brief's "Scope beyond this title" section
could only argue for by inference — now independently verified.

**Our candidate fix (union the decomp seed list into interior
classification) was explicitly rejected, for a good reason we hadn't
weighed**: *"Known game/decomp seeds are not sufficient authority for
every byte variant at a reused RAM address. Blindly unioning them into
all overlapping captures can nominate data and create excessive
compilation work."* A decomp-known address can correspond to different
actual bytes depending on which overlay variant currently occupies that
RAM location — trusting decomp knowledge over the bytes actually present
risks misclassifying data as code. Fair correction; our proposal didn't
account for this.

**The actual root cause is more precise than our brief's framing**: the
classifier already correctly tags a hostless dispatched-to PC as
`DISPATCH_INTERIOR`. It then requires exact reachability from a
discovered host before emitting it as a *shared alias* — and rejecting a
hostless shared alias is deliberate (treating every such address as a new
walk root risks truncating its real host). **The actual bug**:
`make_interior_fragment_job()` rebuilt its candidate set only from
classifications that survived that shared-alias check — so a rejected but
genuinely-*executed* dispatch entry never reached the isolated-fragment
compiler that already existed and could have handled it. **The fix**:
retain execution evidence independently of the shared-host rejection, so
the two questions ("is this a valid alias of another function" vs.
"should this become its own isolated fragment") stop being coupled. Only
entries also present in actual execution evidence get this recovery — not
every decomp-known or every observed address.

**A correction to our own evidence presentation**: *"Runtime capture JSON
deliberately writes `function_entry_pcs: []`. The offline classifier
derives entries later. That raw empty field alone does not prove that a
PC was dropped."* We read the raw capture's empty field as itself proof
of the bug; it's actually always empty at that stage by design — the
classifier's own later decision is what matters, not the raw capture JSON.

**Validated thoroughly**: a new synthetic test (fails on `master`, passes
on the fix branch, with negative-case coverage for ordinary PCs, static
seeds, missing execution evidence, unaligned addresses, and guard-only
words), a real captured-byte comparison recovering all 4 previously-missed
entries in both Tomba and MMX6 corpora with stable DLL counts on repeat
runs, and 8 live 11,000+-frame headless regression runs (baseline/fix ×
cold/warm × Tomba/MMX6) — zero crashes, zero interpreter aborts.

**Important caveat for testing this against Parasite Eve specifically**:
*"The five reported Parasite Eve addresses and its performance figures are
not independently verified. The owner does not have the underlying
capture bytes, game configuration, or seed file from that run."* They
could not check our specific numbers at all — only the general mechanism,
via their own titles. And their own results already show the runtime
effect isn't uniform across titles: MMX6's warm-run interpreter fallback
at the four recovered PCs dropped to zero, but *"the warm Tomba runs
retain the same interpreter counts at the four Tomba PCs, although
guarded current-byte cache entries now exist"* — compiling an entry
doesn't automatically guarantee every runtime call site starts using the
compiled version. **This means we cannot assume this fix will reproduce
our own local `--force-interior` numbers (93.6%→7.9%) just because it's
merged — that needs the same direct before/after test against our actual
build that WO-6 got, not an assumption from the upstream description.**

Merge status: already on `rtk/master` (merge commit `0baf7bb1`, branch
`fix/observed-overlay-interiors`, tracked as `beads-eio.3.145`). The
review's own scope explicitly excludes a downstream pin-bump
recommendation — pulling it into this project's checkout is on us.

## Tested directly against Parasite Eve (2026-09-12) — confirmed, works standalone

Pulled and tested this the same day, since the review explicitly could
not verify our specific case and its own data showed the fix's runtime
effect isn't uniform across titles.

**Porting it wasn't a clean cherry-pick.** `git cherry-pick 4683e923`
conflicted — this tree has a local patch (`fromfile_prefix_chars='@'`)
touching the same file, and separately lacks a `capture_guard_bytes()`
helper that exists further up `rtk/master`'s own history than what's been
pulled here (this tree only tracks specific cherry-picked fixes, not the
full upstream lineage). Applied the fix's logic by hand instead of fighting
the 3-way merge: the core change (retain execution evidence for a hostless
interior independently of the shared-alias rejection) ported cleanly;
the one missing dependency (`capture_guard_bytes`) was replaced with the
plain region boundary — safe, since the isolated-fragment compiler's own
CRC/audit gate is what actually decides compilability; this only affects
which addresses are considered *candidates* at all.

**Confirmed at the classification level first**, cheaply, without a live
game session — `compile_overlays.py --check --only-region 0x8018F000`
against this project's real accumulated capture data:

```
unhosted_executed_dispatch_fragment_demands: 32
```

Of that 32, three of our five originally reported addresses show up
explicitly recovered:

```
80191B94  excluded: OBSERVED_PC_ONLY; isolated fragment demand retained
80191200  excluded: OBSERVED_PC_ONLY; isolated fragment demand retained
80192E3C  excluded: OBSERVED_PC_ONLY; isolated fragment demand retained
```

(The other two, `0x801927D0` and `0x801925D4`, simply aren't present in
*this* capture at all — expected, given this project's own earlier finding
that the capture store isn't stable session-to-session; not a fix failure,
a capture-coverage gap unrelated to this change.)

**Confirmed live, end-to-end, with the manual workaround fully disabled**
(`-ForceInterior @()` — zero forced addresses, the classifier alone
deciding everything): booted through the intro FMV to the idle title
screen — the exact repro window this bug was originally found in
(previously 93.6% `interp_share`, 124.6M interpreted instructions per 60s).
Sustained multiple consecutive seconds at the idle screen:

```
guest=59.97-60.12 Hz, dirty=0 insn/s, overlay native=+4700-30000 interp=+0
```

Steady 60fps, zero interpreter fallback, entirely without the local
`--force-interior` list. **The upstream fix reproduces (and now supersedes)
this project's own manual workaround.**

**Committed locally** (`a94ab281`, "Port PR #349 (fix/observed-overlay-interiors)
from rtk/master") on top of the WO-6 cherry-pick in this project's
`psxrecomp` checkout, with the porting rationale and test results in the
commit message. `play.ps1`'s `-ForceInterior` default list can likely be
retired now that the real fix is in place — not yet done, since the
manual list is harmless to leave in place as a belt-and-suspenders
fallback and removing it wasn't the point of this test.

**Update, same day, see the follow-up directly below**: retiring this
list turned out to be the wrong call, not just "not yet done" — a
separate, unrelated gap in the same classifier area was found a few hours
later, and the list actually *grew* (by 21 + 182 addresses) rather than
being retired. Read on before assuming this list is safe to remove.

## Follow-up (2026-09-14): a related but distinct gap the PR #349 fix does not cover — MIPS jump-table dispatch

**mstan's team has NOT fixed or seen anything below — read this first so
it's not mistaken for a status update on work they've already done.**

**What mstan's team already fixed (for context, not part of this ask)**:
PR #349, described in full above — the classifier now retains execution
evidence for a "hostless" dispatch target instead of dropping it on a
shared-alias rejection. That fix is real, merged, ported into this
project's checkout, and confirmed working end-to-end (the whole section
above this one). **It is not broken, and this follow-up is not reporting
a regression in it.**

**What's new below, that mstan's team has not seen or fixed**: a
*different*, narrower gap in the same classifier area, which PR #349's
fix does not reach — confirmed by reading `compile_overlays.py` directly
and finding the affected addresses never entered the code path PR #349's
fix operates on in the first place (see "Root cause" below). This is a
follow-up bug report, not a claim that PR #349 needs rework.

**Status of this new finding, locally, tonight — so nothing below gets
mistaken for more than it is:**

- **Fixed and verified, but only as a local workaround, not upstream**:
  two directly-confirmed instances (21 + 182 addresses, both from real
  capture data, not guesses) — live in `build/play.ps1`'s `$ForceInterior`
  list right now, with a measured ~450-2200x reduction in the dirty-RAM
  cost they caused. `compile_overlays.py` itself is unchanged — this is
  the exact same kind of local patch this brief's original bug relied on
  *before* mstan's team's PR #349 fix existed.
- **Not fixed, not applied anywhere, not sent to mstan's team**: a
  further 63 dispatcher addresses game-wide are only a *computed
  prediction* (same macro, inferred offsets) — sitting in a companion
  data file, not in `play.ps1`, not verified live. Don't read "255 files /
  64 unique addresses" below as "64 confirmed bugs" — it's 2 confirmed, 62
  unconfirmed candidates.
- **Investigated and ruled out, not a bug, nothing for mstan's team to
  fix here**: a residual dirty-RAM count that remained after the two
  fixes above turned out to be genuine PS1 BIOS ROM interpretation
  (architecturally unfixable by any classifier change), not a third
  instance of this bug — see below for how that was confirmed.

Retiring the manual `-ForceInterior` list turned out to be premature for a
different reason than "harmless to leave in place." Investigating an
unrelated report (a 45-million-instruction dirty-RAM spike during the
intro FMV, tracked in this project's own
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`, which has the
full trail — this section is the condensed version for this brief's
audience) found 13 new addresses excluded as `OBSERVED_PC_ONLY`, in the
same shared `0x80191xxx` RoomLib region as this brief's original bug.

**Checked whether this was the same bug recurring a third time — it
isn't.** `psxrecomp/tools/compile_overlays.py` already has the PR #349 fix
(confirmed by reading the code directly: `print_seed_audit()` appends
`"; isolated fragment demand retained"` to an `OBSERVED_PC_ONLY` line when
the address is in `unhosted_dispatch = (dispatch_fragment_demands &
executed_pcs) - included_reasons`). The 13 new addresses printed with
**no** such recovery suffix, meaning they were never in
`dispatch_fragment_demands` at all — not that they were in it and the fix
still dropped them.

**Root cause, traced to source**: the addresses are interior case targets
of `ROOMLIB_STATE_DISPATCH_VARIANT2(func_80191244,
RoomLib_ResetAndSignalB_80191984)` (`src/overlays/room_m087/
func_80191244.c`), a macro expanding to `switch (func_800DFB78()) { case
0: ...; case 1: ...; case 2: ...; }` (`room_lib.h`). A dense small-integer
`switch` compiles to a MIPS jump table — each `case` is reached via a
**computed** `jr` (a runtime table read), not a `jal`. `dispatch_
fragment_demands` is apparently populated from statically-discoverable
targets (the kind a disassembly pass can identify directly, like a literal
`jal`); a jump table's destinations come from data read at runtime, which
this classifier's static pass doesn't currently resolve into a demand
record the same way.

**This is offered as a follow-up bug report for the same PR #349 area,
not a claim that PR #349 itself is broken.** The fixed mechanism correctly
recovers unhosted-but-statically-demandable addresses; MIPS jump-table
case targets from a runtime-computed `switch` appear to fall outside what
currently counts as "demandable." Not yet turned into a standalone
synthetic test the way the original bug's fix was validated (8 live
11,000+-frame regression runs, Tomba/MMX6 corpora, etc.) — this is a
single-title, single-instance finding so far, offered at the same
confidence level as this brief's own original 2026-09-09 report before
independent verification, not at the level of the validated fix above.

**Code changed** (not just documentation): added the 13 addresses to
`build/play.ps1`'s `$ForceInterior` default list, alongside the five
already there from this brief's original bug — same workaround mechanism,
applied because the classifier (even fixed) doesn't yet catch this shape
of code automatically. Verified with a real before/after, same method as
this brief's own Table above:

| | `dirty_ram_insns`, ~2 min into the intro FMV / post-skip |
|---|---|
| Before | 45,338,450 (still climbing) |
| After | 20,304 → 101,046 (settled, not climbing) |

**Two more directly-confirmed instances found the same night, chasing that
remaining `20,304`/`101,046` residual** — both found by running
`compile_overlays.py --check` offline against this session's real
`overlay_captures.json` (this brief's own verification method from the
section above), not by guessing:

- **8 more addresses in the same `0x80191xxx` region**,
  `0x80191210`-`0x8019122C`, missed the first time only because the
  runtime's `autocompile_status` output is capped and had literally cut
  the printed list off mid-word right before them.
- **A separately-discovered, much larger gap in a different overlay**,
  `load=0x8018F000`: of 183 observed-executed addresses in that entire
  region, only 1 (the dispatch entry itself) was classified — **182 of 183
  excluded**, the most severe instance of this bug class found in this
  project so far.

Both added to `play.ps1` and verified safe (no compile-storm symptoms).
**Neither changed the `20,304`/`101,046` residual at all** — reproduced
to the exact integer across three separate launches (no fix / +8
addresses / +182 addresses). That turned out to be the correct, useful
result: sampling `current_func` at that residual showed it's genuine PS1
BIOS ROM/kernel interpretation (`0x1FC01ACC`, `0x00000F40`, `0x00001794`),
not a classifier gap at all — there's no overlay compiler for BIOS ROM, so
this is an architecturally-irreducible cost of active CD-ROM/MDEC work
during FMV playback, not a fourth instance of this bug. Full trail in
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`.

**Scope check, not yet acted on**: grepping the decomp for this macro
(`ROOMLIB_STATE_DISPATCH_VARIANT2`) finds **250 files**, deduplicating to
**64 unique compiled addresses** across the game (many rooms share an
identical overlay layout). A byte-identical function-size cross-check at a
second, independently-addressed instance (`room_m087`'s 136/168-byte pair
vs. `scene_e27`'s identically-sized pair) suggests the internal jump-table
layout — and therefore the case-target offsets — is likely the same
everywhere this macro appears, giving a computed (not live-verified)
candidate list for the other 63 addresses in
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`'s companion
data file. **Explicitly not blanket-applied** — this brief's own "force
everything" experiment (1,131 addresses, 237-DLL compile storm, ~0.19x)
is exactly the failure mode a 640-address version of the same idea risks
repeating; the companion document recommends incremental rollout with
real before/after checks instead, and that has not been done yet.

If sharing this brief's update with mstan's team: the honest framing is
"a related, narrower gap in the same classifier area your PR #349 fix
already improved, found in one more instance, with one confirmed fix and
an unverified projection for ~63 more" — not "PR #349 has a bug." Their
own review process for the original report could not independently verify
this project's PE-specific numbers, only the general mechanism via their
own titles' captures; expect the same distinction to apply here.

**Update, same day, later — the "MIPS jump-table" framing throughout the
section above is superseded.** Keep it for the historical trail (it's what
was believed at the time and it's not unreasonable on its face), but do
not forward it to mstan's team as the root cause — see the follow-up
immediately below for the corrected, fully-verified explanation and a
tested fix.

## Follow-up (2026-09-14, continued): corrected root cause — `FUNCTION_POINTER_TARGET` is dead code — plus a tested fix

Challenged to justify the "MIPS jump-table" claim directly rather than
re-assert it, which led to actually reading `room_lib.h`'s full macro
definition and `compile_overlays.py`'s classifier logic end-to-end, rather
than inferring either from behavior. Two findings, the second superseding
the first:

**1. The dispatch mechanism may not be a jump table at all.**
`ROOMLIB_STATE_DISPATCH_VARIANT2`'s `case 0` calls through `o->sub.cb`, a
struct field assigned at runtime by a separate macro
(`ROOMLIB_ARM_IF_WINDOW_VIA`, `o->sub.cb = handler;`) — a genuine runtime
function-pointer callback, not a compile-time table. A 3-case `switch`
is also smaller than what compilers typically turn into an actual jump
table. This doesn't change the bottom line (still unclassified, still
fixable the same way) but it means "MIPS jump-table" was probably the
wrong mechanism name.

**2. The real, fully-verified explanation: `FUNCTION_POINTER_TARGET` —
the classification that exists specifically for function-pointer/jump
targets like this — can never fire against any capture the current tool
produces.** Read every place `compile_overlays.py` assigns this
classification:

- Path A: `for addr in captured_function_entries: include(addr,
  'FUNCTION_POINTER_TARGET')`, where `captured_function_entries` comes
  from `cap.get('function_entry_pcs', [])`. Checked the real
  `overlay_captures.json` directly: **every capture has
  `"function_entry_pcs": []`** — always empty by design, per this same
  brief's own upstream-response section above ("Runtime capture JSON
  deliberately writes `function_entry_pcs: []`. The offline classifier
  derives entries later."). Path A can never run.
- Path B is gated by `legacy_seed_mode = bool(legacy_seeds) and not
  cap.get('schema')`. Every real capture has `"schema": "psxrecomp
  overlay capture v2"` set, so `not cap.get('schema')` is always `False`.
  Path B can never run either.
- **Both of `FUNCTION_POINTER_TARGET`'s population paths are permanently
  inactive for any current-format capture.** This is verified against
  real data (the actual `overlay_captures.json` this project has been
  using all along), not inferred from symptoms — and it explains why
  *neither* a jump-table case target nor a runtime-callback target would
  ever be classified correctly, without needing to settle which of the
  two this specific macro actually compiles to.

**A fix, written and tested against real capture data (not yet upstream,
not yet touching the real `compile_overlays.py`):** reuse this brief's own
PR #349 recovery mechanism (`dispatch_fragment_demands` /
"isolated fragment demand retained") for addresses that fall through to
`OBSERVED_PC_ONLY`, not only `DISPATCH_ENTRY`. Patch (on a copy,
`compile_overlays_patched_test.py`), in the final classification pass:

```python
elif addr in executed_pcs or addr in legacy_seeds:
    excluded[addr] = 'OBSERVED_PC_ONLY'
    if addr in executed_pcs and addr + 4 <= fragment_hi:      # new
        dispatch_fragment_demands.add(addr)                    # new
```

Ran offline via `--check` against this project's real
`build-release/overlay_captures.json`, **with no `--force-interior` flags
at all** (the manual list played no role):

```
=== SHARD BUILD SUMMARY ===
  built OK : 176
  skipped  : 1
  FAILED   : 0
```

All 175 previously-`OBSERVED_PC_ONLY`-stuck addresses across both of this
project's captured overlay regions (154 in the `0x8018F000` region, 21 in
the `0x80191xxx` region — a superset of this brief's own originally
reported addresses and the newer jump-table-region ones) were picked up
automatically as "isolated fragment demand retained" and compiled without
error. This supersedes the manually-maintained `$ForceInterior` address
list for these regions — the classifier now finds and recovers them
itself.

**Scope of what this test actually proves, stated plainly:**
- Proves: the classification logic can be fixed cheaply, reusing
  already-shipped, already-runtime-validated recovery machinery (the same
  isolated-fragment/CRC-guard path PR #349's own fix uses) rather than
  inventing something new.
- Does not prove: in-game runtime behavior beyond a clean offline
  `--check` compile (no live soak test of this specific patch yet).
  Generalization beyond the 2 overlay regions this project has ever
  captured. Whether this exact patch shape (routing through
  `OBSERVED_PC_ONLY`) is what mstan's team would want, versus properly
  reviving `FUNCTION_POINTER_TARGET`'s own two population paths instead.

**If sharing this with mstan's team, the accurate framing is:** "the
follow-up gap reported above isn't a jump-table-specific miss — it's that
`FUNCTION_POINTER_TARGET` itself is unreachable dead code in the shipped
tool, verified against real capture data" — that part is solid and worth
reporting. **Do not forward the patch itself as a fix** — see the
correction immediately below, found minutes after the section above was
written: it fails live.

## Correction (2026-09-14, same day, minutes later): the patch above is not safe — do not use or forward it as written

Tested the patch live (not just the offline `--check` above) in a fresh
`build-dbg` boot with the classifier patch active and zero
`--force-interior` addresses. Watched `dirty_ram_insns` through the intro
FMV:

| Elapsed since boot | `dirty_ram_insns` | compile state |
|---|---:|---|
| ~15s | 2.4M | running |
| 90s | 535M | running |
| 195s | **988M**, still climbing | still "running", `shard_ok: 0` |

The *original unfixed* bug this brief documents topped out at
`383,000,000` insns at one hot PC in the field report that opened this
brief — comparable order of magnitude to what this patch produces, i.e.
**no better than having no fix at all**, and far worse than this brief's
own already-working PR #349 port (93.6%→7.9% `interp_share`) or the
jump-table follow-up's manual list (settles at 20K-101K). Killed the
process after 3+ minutes with zero shards reported complete.

**Why the offline test looked clean but live failed**: the offline
`--check` only replayed the 2 overlay regions already sitting in
`overlay_captures.json`. Live, the game visits many more regions during
real play, and the compile log was caught mid-run building a fragment for
`load=0x00052000` — a region never present in the offline capture at all.
The patch recovers *every* `OBSERVED_PC_ONLY` address in *every* region,
unconditionally, each as its own separately-compiled DLL. Live, each newly
visited area queues another batch of one-DLL-per-address compiles that
never catches up — the same compile-storm shape as this brief's own
rejected 1,131-address/237-DLL experiment, just triggered through the
classifier instead of a manual list.

**Bottom line for anything shared with mstan's team**: the
`FUNCTION_POINTER_TARGET`-is-dead-code diagnosis is verified and worth
reporting on its own. The specific patch that routes recovered addresses
through `OBSERVED_PC_ONLY`'s existing fragment-demand path is **not**
verified safe and should not be presented as a candidate fix without
first adding real scoping (e.g. only recovering addresses hot across
repeated visits rather than on first sight, a concurrency cap on isolated
fragment compiles, or per-region opt-in) — none of which exists yet.
