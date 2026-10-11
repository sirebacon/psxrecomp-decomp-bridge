# Which psxrecomp engine to mod Parasite Eve on: where the repos stand, an RTK-master trial, and what is (and isn't) known about the slowdown

**Date: 2026-10-10. Status: decision made (stay on the current pin), trial measured, root cause of the newer engines' slow
phases NOT proven. Read the "Not established" section before citing any of this.**

## Decision

Keep modding on the current engine: `psxrecomp` `1e041a12` (the long-running local pin plus the autocompile-truncation fix).
It holds about 60 fps once its overlay cache is warm. Do not switch to Alex's v0.4.0 / `stage/pin-i` or to RTK `master`
until there is evidence they match it on this hardware (a 2015 i7-6700HQ laptop).

Everything needed to rebuild this setup is backed up (verified with a fresh clone: identical commit, identical tree, all
submodule pins resolve):

- `sirebacon/psxrecomp`, branch `pe-local-work-old-pin-autocompile-buffer-fix`, tag `pe-pin-2026-10-10` (= `1e041a12`)
- `sirebacon/parasite-eve-recomp`, branch `pe-local-work` (`.gitmodules` points the psxrecomp submodule at the fork above)
- The decomp symbols/seeds were regenerated against `parasite-eve-decomp` `29e130db` and committed (see
  `decomp-restructure-tooling-recheck-2026-10-10.md`).

## Where the repos stand

| Line | State on 2026-10-10 |
|---|---|
| Our pin (`1e041a12`) | Base `47bda817` (2026-08-29) plus about 90 commits beyond it (91 not in `rtk/master`; PR #349/#354 ports, PGO clean-exit fix, `fromfile_prefix_chars` patch, autocompile fix). Only exists on the user's fork. |
| `Alexbeav/psxrecomp` `main` | Stale (last commit 2026-08-31). Real work is on branches. |
| `Alexbeav/psxrecomp` `stage/pin-i` | Active (commits dated today, many `PS1B-nnn` issue branches). 1,294 commits ahead of our pin. Contains the `wave5-c4` commits. |
| `RetroPortingToolKit/psxrecomp` `master` (mstan) | Active (today). 1,293 commits ahead of our pin. Does NOT contain the `wave5-c4` tag. |
| Alex vs mstan | Diverged at `193a60b8` (2026-09-14, the commit issue #380 was filed against); each has about 1,000 commits the other lacks. |
| `Alexbeav/parasite-eve-recomp` `main` = `v0.4.0` | Pins psxrecomp `0e962bf6` (the c4 candidate). Alex said on 2026-10-10: "working down the last few issues", a bit over 200 from 250 that morning. |

Alex's published Parasite Eve state, which matters for any "his version is faster" comparison:

- v0.4.0 `game.toml` does not set `overlay_cache` or `idle_skip`. His own commit `b40243e` (2026-10-01, on the
  `normalize/release-standard-20260930` branch) says: "Without the key the runtime never starts the overlay loader." That
  branch turns it on and also boots through the real BIOS (`bios_hle = false`).
- His releases are "owned-input setup packages": no prebuilt playable title, no shipped overlay cache. Every user generates
  and compiles locally.
- The engine has an ahead-of-time static overlay path (`compile_overlays.py --static` -> `generated/overlays_static.c`,
  linked into the exe, no warm-up), but it is opt-in per title through an `aot/overlays.json` profile. No branch of his
  Parasite Eve repo has one.
- Nothing published explains a faster menu in his build.

The issue #380 gap (`function_entry_pcs` hardcoded empty in `overlay_capture.c`) is present, unfixed, in all three engine
lines (ours, `pin-i`, `rtk/master`).

## The RTK-master trial

Built side by side so the working setup was never touched: a git worktree
`parasite-eve-recomp-rtk` (branch `rtk-trial`), disc/BIOS linked rather than copied, its own copy of the saves, its own
build dir `build-rtk`, psxrecomp on `rtk/master` `26b3878e`, plain Release with debug tools on, no PGO or LTO. Launched
through `play.ps1` with a scratch config so overlay autocompile was wired identically.

Three changes were needed to get it to configure and build:

1. `CMakeLists.txt`: the newer engine hard-errors unless mods are wired through `PRELOADED_MODS_DIR` (and the hand-written
   staging block removed). Restored from the earlier commit `bcc9043`.
2. `recomp-ui` has to move with the engine (the older pin lacks launcher struct fields the new `main.cpp` expects); used its
   current `master`.
3. RTK's `compile_overlays.py` has no `fromfile_prefix_chars='@'`, so `play.ps1`'s `@file` force-interior list needs a
   one-line patch (committed on the trial's psxrecomp branch `pe-on-rtk-master`). RTK `master` independently contains the
   same autocompile buffer fix we made (8192 bytes, and it now fails loudly), and its message recommends an `@file`.

Results:

- **Cold cache is severe.** First launch: about 34 fps (0.57x) at the intro, then 3.5-6 fps while shards compiled. Over about
  25 minutes the trial compiled 601 shards (your warm build has 454, so the newer engine makes about 40% more) and
  oscillated between about 35 fps (`interp_share` 0.37) and about 6 fps (0.93) as new areas were visited.
- **Warm cache is healthy.** With 600+ shards: `interp_share` about 0.06, zero interpreted instructions, zero interpreter
  fallbacks, menu/start screen at 60 fps. The intro FMV ran about 47-52 fps against about 60 on the current engine; that gap
  is the same size as what PGO+LTO gave on the old engine (about 52-54 -> 58-61) and the trial had neither, but that
  attribution was not tested.
- An earlier statement in this session that the trial "never settles" was wrong and has been retracted: those slumps were
  shards still compiling.
- Old savestates do not load on the newer engine (`savestate_status` `last_ok: 0`, screen stayed on the title), so gameplay
  could not be measured without the user playing in the trial window.

## The New Game / Continue / Tutorial menu

Measured live on the trial while the user reported under 30 fps:

- Hot interpreted PC `0x801930D8` (menu overlay code): 14.8M instructions in the 20s window, 55,160 instructions per entry,
  `interp_share` 0.72. Minutes later, with nothing changed by hand, `interp_share` was 0.066 then 0.044. The overlay
  compiled and the menu recovered. This project recorded the same warm-up behavior for this menu on the old engine
  (`0x80193084`, resolved in about 90s on revisit).
- During the slow phase `text_native_blocked` reached about 44.2 million and `text_exact_mismatches` matched it almost
  exactly (44,180,867): the last failing range was `0x001909B4`, 6,552 bytes, live bytes differing from the reference.
  After recovery the counter nearly stopped growing (44.18M -> 44.20M). At the title screen it was a few thousand per 20s.
- The guard that does this exact-range validation is what commits `f07f8019` ("validate stale-static ranges in full, drop the
  exec_pc clip") and `4d9060a5` ("stale-static guard on inter-piece host transfers") changed (2026-08-30). The third
  suspect, `aa6fa2c9` (page watch for static overlay ranges), only affects games on the AOT-static overlay path, so it is
  unlikely to matter for Parasite Eve. All three are in both `stage/pin-i` and `rtk/master`, and none are in our pin.
- Alex's `f2dc2039` / RTK's `67e9b4cf` ("keep interpreting through game text that dispatch refuses", 2026-09-30) is the
  closest fix on record, but it targets a retail-BIOS-intro loop on a PAL title, and RTK `master` (the trial) already
  contains it while the 44M-mismatch loop still happened. It is not the fix for this menu.

## Overlay shard cache facts

- Per machine, per install: compiled from the overlay bytes on the player's own disc, so it cannot be shared or shipped
  with a repo.
- Keyed by overlay content, compiler flavor and the engine's codegen hash. An engine update that changes the codegen hash
  invalidates the whole cache; this is what made the menu slow again on 2026-09-13.
- The decompile does not remove the need for it: the decomp supplies names, addresses and boundaries, not the machine code
  the recompiler translates. Forcing every known overlay function at once caused a compile storm (about 0.19x) on the old
  engine.
- The real fix for old hardware is a pre-baked cache built at setup (the engine's AOT static mode is the existing
  mechanism, but needs a per-title profile). Not built.

## Not established

- Whether the stale-static guards actually cause the newer engines' worse cold phases, or only correlate with them. No
  revert-and-compare was run (reverting `4d9060a5` changes codegen and would invalidate the cache; `f07f8019` is
  runtime-only and would not).
- Whether the old engine shows the same mismatch counts at this menu when cold. Its cache is warm, so it was not measured.
- The original c4 regression report: 30-45 fps in gameplay with `dirty_ram_insns` in the billions. Everything measured here
  is title, intro and menu. The savestate incompatibility blocked gameplay measurement.
- What Alex's "fixed" build is. It is not in any published branch, release, or config.
- Whether PGO+LTO closes the roughly 50 vs 60 fps gap on the trial. Not built.

## Corrections made along the way

- Free disk space on D: was reported as 3.5 GB; it is 3.5 TB (unit misread). It was never a constraint.
- The "trial never settles" claim above, retracted.
- An early check of the PE repo's `psxrecomp` remote used the wrong remote and returned nothing; redone against the right one.

## Suggested next steps

1. Ask Alex which build and config his fast menu runs, whether PE has an AOT overlay profile locally, and whether releases
   ship a prebuilt cache. Include: the `text_exact_mismatches` figure and range above, the c4 gameplay regression with its
   three unbisected suspects, and issue #380.
2. If wanted, run the runtime-only experiment: revert `f07f8019` in the trial, relink (cache survives), and compare a cold
   visit of this menu.
3. Have the user play to a gameplay spot in the trial and press F7, to finally measure the gameplay case.
4. Meanwhile, mod on the current engine: playtest the storage mod past slot 50 and the run-speed mod, then FMV skip.
