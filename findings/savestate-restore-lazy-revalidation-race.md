# Root-cause narrowing for the savestate/menu VRAM glitch and LTO's
performance collapse: both trace to the same deliberate-but-incomplete
design — lazy, per-candidate overlay revalidation after a savestate
restore

Follow-up to `savestate-menu-vram-glitch.md` (the live discovery and
precise repro) and `fmv-irq-batch-prototype-ai-brief.md` (where LTO's
separate performance bug was found and isolated). This document is a
source-level analysis done *without* touching the running build — the
user asked to hold off on re-enabling LTO for live testing, so this
pushes the investigation as far as static reading of the actual
mechanism allows, and it turns out that's fairly far.

**Bottom line up front**: the "revalidation storm" caught live earlier is
not a bug — it's fully intentional, deliberately-designed behavior with
its own explanatory comment already in the source. What's actually wrong
(the visual corruption) is a real, narrow gap in that same design: it's
*lazy* (revalidate-on-next-touch) rather than *eager* (revalidate-
everything-before-the-next-frame), which leaves a real window where the
first frame after a savestate restore can draw using stale, not-yet-
rechecked native code. LTO's performance bug is very likely the same
mechanism, just with the *unavoidable* one-time catch-up cost itself
taking far longer under LTO for reasons not yet identified.

## The mechanism, as written by whoever built it (not inferred — quoted)

`psxrecomp/runtime/src/memory.c:807-824`:

```c
/* Savestate restores RAM via memcpy and never hits the store chokepoint that
 * bumps overlay_page_gen. Without this, ENTRY_VALID overlays keep the gen-gated
 * fast path and run native code against restored bytes they were not validated
 * for — hang / freeze after the restored frame presents. */
void dirty_ram_text_guard_resync_after_restore(void) {
    ...
}
```

That comment names the exact failure class this session hit — "hang /
freeze after the restored frame presents" — as an already-known risk the
code is guarding against. The actual guard, `memory.c:826-835`:

```c
void overlay_watch_invalidate_after_ram_restore(void) {
    for (uint32_t pg = 0; pg < DIRTY_RAM_PAGE_COUNT; pg++)
        overlay_page_gen[pg]++;                       /* every page, unconditionally */
    extern void overlay_loader_note_code_write(void);
    extern void overlay_loader_resync_validation_after_restore(void);
    overlay_loader_note_code_write();
    dirty_ram_text_guard_resync_after_restore();
    psx_kernel_bless_resync_after_restore();
    overlay_loader_resync_validation_after_restore();
}
```

and `overlay_loader.c:2849-2862`:

```c
void overlay_loader_resync_validation_after_restore(void)
{
    /* Host-only validation memos. Page gens were already bumped by
     * overlay_watch_invalidate_after_ram_restore; force every candidate off
     * the gen fast-path (including ENTRY_INVALID + gen==val_gen skips, and
     * nranges==0 bodies whose gensum never moves). Static-match cache is the
     * same class for AOT game/BIOS overlays. */
    for (int i = 0; i < s_cand_n; i++)
        s_cand[i].val_gen ^= 0x80000000u;
#ifdef PSX_HAS_OVERLAY_DISPATCH
    memset(s_static_match_cache, 0, sizeof(s_static_match_cache));
#endif
}
```

So on every savestate load, **every** overlay page's generation counter
is bumped and **every** cached-valid candidate is deliberately kicked off
its fast path. This is by design — the whole point is to prevent exactly
the "stale native code running against newly-restored bytes" class of
bug the first comment describes.

## Why the "storm" isn't the bug

The actual re-check happens lazily, one candidate at a time, inside the
normal dispatch path (`overlay_loader.c` — the same
`cand_gensum()`/`val_gen` compare used everywhere else in the loader,
covered in this project's earlier WO-8/WO-9/WO-10 work):

```c
uint32_t gen = cand_gensum(c);
if (c->state == ENTRY_VALID && gen == c->val_gen) {
    s_gen_fastpath++;
    return 1;                      /* fast path: nothing changed */
}
...
uint32_t live = cand_crc(c);        /* the "expensive" path */
s_rehashes++;                       /* <- this is what showed up as "reval_attempts: 11179" */
...
```

Since the restore-time resync guarantees `gen != c->val_gen` for
*every* candidate, the **first** dispatch to each one after a restore is
guaranteed to take the `cand_crc()` path once. `reval_attempts: 11179`
with `reval_crc_miss: 0` is exactly what "every resident candidate pays
one legitimate, successful recheck" looks like — not a runaway loop, not
an infinite retry, just the real one-time cost of however many overlay
candidates happen to be resident scaled across however many actually get
touched again. This also matches every *other* savestate-triggered stall
observed this session (both saves and loads, with and without LTO) —
they're all this same, intended, unavoidable catch-up cost, just usually
brief enough to be a non-issue.

## Why the visual corruption still happens

The design guarantees *correctness eventually* (nothing stays wrong
forever — that's what "hang/freeze" the comment is preventing), but it
does **not** guarantee the *very first frame* drawn after the restore is
correct. Revalidation is triggered per-candidate, on that candidate's own
next dispatch — there's no synchronous "block until everything relevant
to the next frame is revalidated" step before the restored state is
allowed to render. If the specific candidate responsible for drawing the
New Game/Continue/Tutorial menu's background hasn't been dispatched yet
by the time that first post-restore frame is composited, whatever was
last resident at that dispatch slot (potentially: nothing meaningful, or
a partially-applied intermediate state) draws instead — one bad frame,
self-correcting from the very next touch onward. This lines up exactly
with what was observed live:

- Corrupted on the first load after a different scene's VRAM content,
  clean on an immediate second load of the exact same savestate (the
  second load's candidates are almost certainly already revalidated from
  the first load's own dispatches, so there's no gap left to fall into).
- CPU VRAM and the presented framebuffer agreeing byte-for-byte on the
  wrong data (`savestate-menu-vram-glitch.md`) — consistent with "the
  actual pixel data written was wrong," which a stale-or-not-yet-
  recompiled dispatch producing incorrect output would directly cause,
  rather than a GPU-side upload/coherency disagreement (which was
  directly ruled out).
- Reproducing identically with LTO on or off — this mechanism has
  nothing to do with LTO; it's a property of the lazy-revalidation
  design itself, present in the source regardless of optimization level.

## Update: the LTO-performance link did NOT hold up under a matched
retest — see `fmv-irq-batch-prototype-ai-brief.md` Follow-up 5

After this document was written, a matched, controlled retest (same
savestates, same fresh-boot starting point, same exact transition, timed
`overlay_loader_status` sampling) was run for both LTO-off and LTO-on
back to back. Result: **+15 revalidations (LTO-off) vs. +7 (LTO-on)**,
both resolved within ~0.2s, both fully clean 60fps throughout — no storm,
no collapse, on *either* build. The original "LTO causes a severe
performance collapse" claim (Follow-up 4 in the FMV brief) did not
reproduce and has been retracted there. The section immediately below
(kept for the record, since the reasoning was sound given what was known
at the time) should be read with that correction in mind: **the
performance side of this investigation is currently unconfirmed as an
LTO-specific issue.** The visual corruption itself, and everything above
this note explaining its mechanism, stands unaffected by this
correction — only the LTO-performance link is in question now.

## Why LTO makes the performance side worse (SUPERSEDED — see the
correction immediately above; kept for the record, not confirmed)

The catch-up cost itself (running `cand_crc()`'s CRC32 loop once per
resident candidate) is unavoidable and by design. LTO's isolated
performance bug (found and cleanly A/B'd in
`fmv-irq-batch-prototype-ai-brief.md`'s Follow-up 4) most plausibly means
LTO is making *that specific, already-necessary catch-up work* slower —
not causing extra or incorrect work. Candidate mechanisms, none verified
yet:

- LTO's cross-TU inlining/reordering pessimizing the hot loop in
  `cand_crc()` (`memory.c`'s `crc32_update`, or whatever backs it) or
  `cand_gensum()`'s per-page summation, e.g. by changing register
  allocation or defeating an auto-vectorization the per-TU build got for
  free.
- LTO changing how many candidates end up needing the expensive path
  simultaneously by altering unrelated inlining decisions elsewhere in
  the loader (a scope/breadth change rather than a per-call speed
  change) — this would show up as a *larger* `reval_attempts` count
  under LTO for the identical transition, which was not checked directly
  (no side-by-side attempt count was captured with matched conditions).
- Something specific to how LTO handles the `extern`-declared functions
  crossing the `memory.c`/`overlay_loader.c` boundary in this exact
  resync path — plausible given LTO's entire value proposition is
  optimizing across exactly those boundaries, and this path is one of
  the more unusual/rarely-exercised ones in the codebase (savestate
  restore is not a hot, frequently-tested code path the way normal
  dispatch is).

## Candidate fix directions (not implemented, not validated — for
whoever picks this up)

**For the visual corruption specifically** (independent of LTO): make the
post-restore resync *eager* for whatever the very next frame actually
needs, rather than purely lazy. Two shapes this could take, in order of
invasiveness:
1. Cheapest: force a synchronous full revalidation pass over all
   currently-`ENTRY_VALID` candidates immediately in
   `overlay_watch_invalidate_after_ram_restore()`, before returning
   control to the frame loop — trades a guaranteed-longer pause at
   restore time (which already happens anyway, just currently spread
   across the first several dispatches instead of paid up front) for
   eliminating the "wrong first frame" window entirely.
2. More surgical: specifically eager-revalidate only candidates in the
   region(s) covering the current display-list/rendering call chain
   before presenting the first restored frame, deferring everything else
   to the existing lazy path — same correctness guarantee for what's
   about to be drawn, without paying the full catch-up cost up front.

**For LTO's performance regression**: needs the live A/B this document
couldn't do (holding off per the user's request) — specifically, compare
`reval_attempts` count *and* wall-clock time for the identical
gameplay→menu transition under LTO-on vs LTO-off, to distinguish "same
attempt count, slower per-attempt" from "more attempts happening" as the
mechanism. Only after that split is known does it make sense to guess at
which specific function/boundary LTO is mishandling.

## What this document does and doesn't establish

**Established from source, high confidence**: the exact mechanism by
which a lazy, per-candidate revalidation design can produce a
first-frame-wrong/self-correcting-after visual glitch following any
savestate restore, and that this mechanism is completely independent of
LTO. This is a real, load-bearing explanation, not speculation — every
piece of it is quoted directly from the runtime's own source and its own
comments, and every prediction it makes (corrupted-once, clean-twice;
CPU/GPU agreement on the wrong data; LTO-independence) matches what was
directly observed live in `savestate-menu-vram-glitch.md`.

**Not established — genuinely unknown until a live LTO comparison is
run**: which specific function or boundary LTO mishandles to turn an
ordinarily-brief catch-up cost into a multi-second collapse. The three
candidate mechanisms above are reasoned guesses, not findings.

## Scope and relationship to other findings

- Distinct from `video-bleed-through-splash.md` (the older bug): that one
  was a genuine CPU/GPU coherency disagreement (checked directly there,
  and re-checked here — different mechanism). This one is a single
  subsystem (`overlay_loader`'s candidate-validity cache) not being fully
  reconciled before the first frame renders.
- Explains, retroactively, several other savestate-triggered stalls
  observed earlier the same session (brief FPS drops after both `save`
  and `load` operations, self-recovering) — those are almost certainly
  the same intended catch-up cost, just short enough on those particular
  saves/regions not to be visually alarming.
- Cosmetic in impact (per `savestate-menu-vram-glitch.md`): no crash, no
  save corruption, self-clears. This document upgrades the *confidence*
  and *precision* of that finding's root cause without changing its
  assessed severity.

## Next steps if this is picked up again

1. Confirm the "first dispatch after restore is unvalidated" theory
   directly: arm `overlay_cps_probe` on the specific PC responsible for
   the menu's background draw (not yet identified — would need the same
   `fn_filter`/disassembly tracing method as WO-8/WO-9) and watch its
   `outcome` transition across a restore. Expect: `outcome` reflecting a
   stale/fast-path hit on the very first post-restore call, then a normal
   revalidate-and-match on the next.
2. Once LTO is back in scope: capture `reval_attempts` deltas for the
   identical transition under both configs to settle "slower per-attempt"
   vs. "more attempts" before guessing further at LTO's specific fault.
3. If a fix is attempted, validate it against the precise repro in
   `savestate-menu-vram-glitch.md` (load gameplay save → load menu save →
   `present_shot` → compare) rather than general play-testing, since the
   bug is single-frame and easy to miss without a screenshot taken at the
   exact right moment.
