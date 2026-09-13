# Pulling mstan's fixes in surfaced a bigger problem: this fork has drifted hard from rtk/master

Written for Alex, as a companion to `fmv-60fps-alex-briefing.md`. This one
isn't a performance finding — it's a practical problem hit today while doing
something that should have been routine (pulling two small upstream fixes
in), and it's going to keep happening on every future upstream fix unless we
decide something about it.

## What we were trying to do

RetroPortingToolKit (mstan's team) merged two fixes relevant to our own
recent investigation: PR #354 (a real CFG-builder bug, independently found by
both sides) and PR #355 (an unrelated offline-build regression fix). Small,
scoped, well-tested changes — 8 files and 4 files respectively. The plan was
to pull just those two into this fork's checkout at
`D:\...\parasite-eve-recomp\psxrecomp` (remotes: `origin` = your
`Alexbeav/psxrecomp`, `rtk` = `RetroPortingToolKit/psxrecomp`).

## What actually happened

A plain `git merge rtk/master` (intending to grab everything currently on
their master, including the two we wanted) produced **over 40 file
conflicts** across systems that have nothing to do with either fix:
`gpu.c`/`gpu_gl_renderer.c`, `dma.c`/`dma_gpu_ll.c` (a `dma_gpu_ll.h`/`.c`
pair that's an add/add conflict — both sides independently created a file
with this name), `display_scanout.h` (same, add/add), `host_keymap.c`,
`frame_pacing.h`, and `psx_lobby_client.c` (a 3,362-line netplay lobby
implementation that appears to be entirely this fork's own, independently-
built feature — nothing upstream is trying to patch a file this large for a
"restore offline builds" fix unless the two sides have built genuinely
different things under the same filename).

Checked how far we've actually diverged:

```
git merge-base HEAD rtk/master
  → 47bda8172e43fdba1879c1a5885904a265c567f6
git log --oneline HEAD...rtk/master | wc -l
  → 350
```

350 commits of *combined* divergence (unique to either side, symmetric
difference — not "we're 350 commits behind," but "there are 350 commits'
worth of history that exists on one side and not the other") since the last
point both trees agree on. That's a lot of independent surface area, and it
matches what the conflict list above looks like: GPU rendering, DMA timing,
netplay/lobby, display scanout, and keymaps have all clearly had real,
substantial work land on one or both sides since the fork point, none of it
coordinated.

## What we did instead

Aborted the broad merge. Cherry-picked the two commits individually with
`-m 1` (mainline-relative diff) instead of merging the whole tree:

- **#355 (netplay auth-header build fix)**: conflicted immediately in
  `runtime/src/main.cpp` and `runtime/src/psx_lobby_client.c` — the exact
  file named above. **Dropped it.** It's patching RTK's stock netplay code;
  this fork's netplay lobby implementation has diverged too far for the fix
  to mean the same thing here, and it isn't something we need for the
  current investigation.
- **#354 (CFG fix)**: mostly clean. Two small conflicts:
  - `docs/internal/FAITHFUL_TIMING_PLAN.md` — a changelog insertion point,
    trivial, kept their entry.
  - `recompiler/src/control_flow.cpp` — one real one. The conflict pulled in
    an `analysis_walk_hi()` helper that turned out, on checking the isolated
    `git diff de8b942f ee1d7254` for that file, to **predate PR #354
    entirely** — it already existed on `rtk/master` before this PR, from
    some earlier commit we never pulled in, and isn't called anywhere on our
    tree's live code path (`find_block_boundaries` here still calls
    `func.end_addr` directly). Dropped that hunk, kept only the actual #354
    diff (the comment update plus the real `rebuild_control_flow_metadata()`
    replacement for the old `detect_loops()`).

Committed as a scoped, documented cherry-pick
(`216ce962` on branch `pe-local-work`, built off your existing `a94ab281`).
Verified: `psxrecomp-game.exe` (the recompiler) builds clean, and
regenerating Parasite Eve's full 4,378-function source against it produces
**byte-identical output** — the fix changes nothing for this title's current
code, so it's now in effect with zero behavioral risk.

## Why this is worth your attention specifically

This is going to happen on **every future upstream fix**, not just this one.
Two outcomes are baked into the current state:

1. **A file this fork has diverged on hard (netplay, GPU renderer, DMA
   timing, display scanout) will keep rejecting upstream fixes to that
   exact area**, even correctness fixes we'd probably want, because the
   surrounding code no longer resembles what the fix was written against.
   We got lucky today — #354 touched files that hadn't drifted. #355 touched
   one that had, and we just... didn't get that fix. If RTK ships a real
   security or correctness fix to netplay next month, we're in the same
   position, except it might not be droppable.
2. **Every cherry-pick from here forward needs the kind of manual diff-
   isolation we did for #354's stray `analysis_walk_hi()` hunk** — checking
   the *actual* upstream diff in isolation (`git diff <parent1> <merge>`)
   rather than trusting what a 3-way merge against our divergent base
   produces, since the merge tool can't tell "this content is new from the
   PR" from "this content is old and just missing on our side." That's slow,
   and it's exactly the kind of manual step that's easy to get wrong under
   time pressure — worth deciding whether it's the right ongoing process
   before it becomes one.

## What we're asking you to decide

1. **Is there an appetite for a periodic reconciliation pass** — even just
   walking the RTK commit log for anything touching files this fork has
   diverged on, and deciding case-by-case whether to port it (like we did
   for #354, and like the earlier RoomLib/WO-6 PR #349 port before it), vs.
   continuing to pull things in only reactively when we happen to need them?
2. **Is the netplay lobby implementation (`psx_lobby_client.c` and
   friends) meant to diverge permanently from RTK's**, or is it something
   that should eventually get upstreamed/reconciled too? If it's meant to
   stay a permanent fork-specific feature, that's fine, but it's worth
   knowing explicitly so future upstream netplay fixes get evaluated as
   "not applicable" quickly instead of re-discovered each time.
3. **Do you want visibility into which specific upstream commits we've
   pulled versus skipped?** Right now that's tracked only in commit messages
   on `pe-local-work` (`a94ab281` for PR #349, `216ce962` for PR #354) — we
   can maintain a running list if that's useful, or point you at `git log`
   directly if you'd rather track it yourself.

None of this blocks anything currently in flight — the CFG fix is in, tested,
and safe. This is purely about the next one being less painful than this one
was.
