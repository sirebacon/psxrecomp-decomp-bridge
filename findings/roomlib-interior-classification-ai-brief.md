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
