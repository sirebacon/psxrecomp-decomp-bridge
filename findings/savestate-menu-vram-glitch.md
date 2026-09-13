# Savestate-load VRAM/background corruption at the New-Game/title menu —
real, precisely reproducible, self-clearing, root cause narrowed but not
yet pinned down

**Root cause narrowed considerably since this was written** — see
`savestate-restore-lazy-revalidation-race.md` for the source-level
mechanism (a real, by-design gap in the overlay loader's post-restore
revalidation being lazy rather than eager, quoted directly from the
runtime's own code and comments). Keep reading below for the original
live discovery and repro; the "leading hypothesis" section further down
is superseded by that follow-up document.

Found live, 2026-09-13, while the user was actually playing (not a
targeted investigation that went looking for this) — reported as "screen
frozen, music still playing" after New Game → FMV → gameplay → back to
the main menu, then reproduced deliberately via manual savestate
switching. Separate from and unrelated to the same night's PGO/LTO/FMV
work (`fmv-irq-batch-prototype-ai-brief.md`) except that chasing it is
what led to discovering LTO's own separate bug — see that document for
the LTO story; this one is the cosmetic/VRAM issue that LTO turned out
*not* to be responsible for.

## Symptom

At the title screen's New Game/Continue/Tutorial menu, the menu box
itself renders correctly (readable, correctly composited — it's drawn on
a separate layer), but the background behind it shows severe TV-static/
noise-style corruption: fine per-pixel color-fringed grain replacing what
should be the game's background artwork, plus a strip of corrupted
blocky texture data in the frame's right margin. Confirmed via
`present_shot` screenshots (not the user's description alone).

## Precise, deterministic repro (isolated via debug-server savestate
control, not guessed)

1. Load a savestate captured **during real gameplay** (VRAM holds an
   actual rendered scene — confirmed via `present_shot`: a real outdoor
   gameplay scene, 100% RT, clean).
2. Immediately load a **different** savestate that resumes at the New
   Game/Continue/Tutorial menu.
3. **Result: corrupted, every single time.** Reproduced 2/2 attempts
   this session, both after fresh process launches and mid-session.
4. **Load that exact same menu savestate a second time, immediately
   after step 3, with no other action in between: clean, correct
   rendering, every time.** Also reproduced 2/2.
5. Loading the menu savestate **without** first loading a gameplay
   savestate (e.g., straight from a fresh boot) never showed the bug in
   any of this session's tests.

So the trigger is specifically: *first* time this menu's rendering code
runs after VRAM held a **different, real** scene's content — not the
menu savestate itself, not corruption of the save file (fresh re-saves
under a clean build reproduced it identically), and not something that
needs replaying the whole game to hit (savestate-switchable in seconds).

## What's already ruled out, directly

- **Not caused by LTO.** Reproduced identically on a build with
  `CMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF` (the same build LTO's own
  performance bug was cleanly ruled correct on) — see
  `fmv-irq-batch-prototype-ai-brief.md` Follow-up 4's correction. LTO was
  the first suspect (it was the most recent change), but this reproduces
  with or without it.
- **Not a save-corruption or persistent-state issue.** The exact same
  savestate file that shows the bug on its first load renders perfectly
  on a second, immediate, identical load — the save itself is fine, and
  no user-visible game state (position, inventory, progress) was ever
  observed to be wrong.
- **Not a GPU-upload/coherency mismatch** — the specific mechanism behind
  this project's older, still-open `video-bleed-through-splash.md`
  finding. Checked directly this time (that finding's own methodology):
  `vram_peek` (raw CPU-side VRAM bytes) and `gl_fbo_peek` (what the GPU
  actually presents) were read at multiple coordinates inside the
  corrupted region during an active repro and came back **byte-for-byte
  identical** (`hex` fields matched exactly at every sampled coordinate).
  Whatever's wrong, both sides agree on it — the noise is genuinely
  *in* VRAM at the moment of the bad load, not a stale-texture/upload-
  timing disagreement between CPU and GPU views of otherwise-correct
  data. This is a materially different mechanism from the older bug
  despite the superficial similarity (both are "wrong background behind
  a title-ish screen after an unusual transition").

## Leading hypothesis (narrowed, not confirmed)

A live capture of `overlay_loader_status` during one corrupted instance
showed `reval_attempts: 11179` with `reval_crc_miss: 0` **every one of
those 11,179 times** — a massive burst of code-revalidation checks on
the RoomLib overlay region (`checked: ['0x0018E000']`), all false
positives (the code never actually needed reloading), correlated with
`hot_native_owner` sitting on a low BIOS/kernel address
(`0x00000E10`) and `dirty_ram` interpreter throughput spiking to
1.2-1.7M instructions/sec — i.e. a real, measured burst of unusual
overlay-loader activity landing at exactly this transition, not merely
correlated in time by coincidence.

This is consistent with: the menu's background-drawing routine lives in
an overlay region that isn't resident while gameplay's own overlays are
loaded. The *first* time execution reaches it after returning from a
gameplay context, the loader has to (re)discover/(re)validate/load that
region from scratch — and something about doing that exactly at a
savestate-load boundary (mid-transition, before the loader's caches are
in their normal steady state) causes either a genuinely wrong native
compile to run once, or a fallback to the interpreter that doesn't
faithfully reproduce whatever pixel-writing sequence the background draw
needs. By the second load, that region is already resident/validated
from the first attempt, so it runs the normal (correct) path.
**Not verified directly** — would need the same live tooling used in the
WO-8/WO-9 investigations (`overlay_cps_probe` armed on the specific PC
that draws this background, `phase_hot`, or a targeted `fn_filter` trace
across exactly this transition) to catch which address is responsible
and whether it's really running interpreted/differently on the first
pass. Flagged as the concrete next step, not attempted this session —
this finding was reached live, mid-playtest, and stopped at "precisely
characterized and safely reproducible" rather than pushing on to full
root cause, since it's cosmetic and non-blocking (see below).

## Severity and impact

**Cosmetic and self-clearing, not blocking.** No crash, no corrupted
save, no lost progress. The corrupted frame(s) resolve on their own once
the game advances past that static screen into any new content (a
`present_shot` taken moments after the user proceeded past the menu
showed a completely clean, correctly-rendered FMV scene — the earlier
menu corruption was gone). The "screen frozen, music still playing"
original report is most likely this same static corrupted frame simply
sitting on screen for a few seconds (a real single bad frame, not an
animating one, so it *looks* frozen) while the user is still deciding
what to click — not a genuine hang. Worth fixing for polish, not urgent
for playability.

## Reproduce it yourself

1. Build with `-DPSX_DEBUG_TOOLS=ON`, launch with `--debug-port <N>`.
2. Get one savestate mid-gameplay and one at the New Game/Continue/
   Tutorial menu (either via the in-game hotkey or
   `{"cmd":"savestate","op":"save","slot":N}`).
3. `{"cmd":"savestate","op":"load","slot":<gameplay>}` then immediately
   `{"cmd":"savestate","op":"load","slot":<menu>}` — take a
   `{"cmd":"present_shot"}` and read the resulting PNG.
4. Repeat the menu-slot load alone (no gameplay-slot load first) —
   compare.

## State left after this session

Diagnosis only — no code changed, nothing needs reverting. The build
currently running has `PSX_DEBUG_TOOLS=ON` (needed to capture the
evidence above); switch back to the `-DPSX_DEBUG_TOOLS=OFF` production
config (per `fmv-irq-batch-prototype-ai-brief.md`'s standing
recommendation: PGO on, LTO off, debug tools off) for normal play — the
bug is cosmetic enough that leaving debug tools on isn't required to
keep playing around it, but it also isn't needed for the bug to happen
(it reproduces the same either way).
