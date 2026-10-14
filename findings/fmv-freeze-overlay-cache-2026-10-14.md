# FMV freeze: movie player left uncompiled after a game.toml change (2026-10-14)

## Symptom

Story movies (Day 1 theater and others) froze on their first frame, every time, with or
without save states. The game kept running at ~60 fps; the scene never advanced. The
New Game opening movie still played.

## What the game was doing (live, debug port 4370)

- Hottest interpreted PC `0x801212A0` (~45% of time, ~6,000 instructions per pass): inside
  `MenuCardFirst_UpdateVideoFrame` (`0x80121270`, decomp
  `src/overlays/menu_memcard/video_frame.inc`), the movie player's per-frame update in the
  `menu_memcard` overlay (which also holds the game's video player and its `\FMV000.STR`
  table). It spins on `while (StGetNext(...) != 0) if (--retries == 0) return 0;`: no movie
  frame ever arrives in the stream ring.
- The drive was fine: `cdrom_timing` showed every data sector delivered on schedule, none
  late or lost. Data-ready interrupts were raised and acknowledged, but the stream handler
  never requested the sector (`request` stayed `0x00`), so the runtime overwrote them
  (`ring_dropped` climbing). The game then paused and restarted the stream from the same
  spot about every 6 seconds: the endless "freeze".
- In the working opening movie, `request` was `0x80` and the disc position advanced.

## Cause

The overlay compile cache is keyed by the game config:
`build-release/cache/SLUS-00662/gcc/win-x64/cg10_<...>_gc<game.toml hash>_f0/`. Adding
hooks to `game.toml` `mod_function_entry_funcs` (2026-10-13 afternoon: the spell hook
`0x80024250`, the analog pad hook `0x8003EB04`) switched the runtime to a fresh, empty cache
folder. In the old folder (`gc2c727bcc`) the movie player overlay region `0x00121000` had
been compiled (5 DLLs, one per player variant). In the new one (`gc0408ccb0`) about 3,000
other pieces compiled but the movie player never did (a leftover
`0012912A_fragment_patched.c` with no DLL suggests a failed attempt). Interpreted, the
player is too slow for the stream library, which drops the movie.

Not a decomp problem, and not the decomp syncs: an A/B build with the seeds from before
both syncs froze the same way.

## Fix (workaround)

Copied `00121000_*` (dll, ranges, pair-lock) from the old cache folder into the current
one. The movie then played through. Overlay DLLs don't depend on the main-EXE hook list.

## Open

- Why the runtime's autocompile doesn't produce the `0x00121000` DLL in the new cache
  (`stall_report` showed `autocompile state=running, result_seen=0`). Check the compile log
  for that region / the fragment file.
- Until fixed: after any `game.toml` change, carry `00121000_*` into the new cache folder
  (or re-test a story movie). Report upstream (psxrecomp runtime / overlay autocompile),
  with this file, if it reproduces from a clean cache.
