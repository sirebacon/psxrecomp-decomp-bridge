# FMV freeze: story movies stop getting frames partway (2026-10-14)

Status: **root cause open; worked around** by the mod's movie watchdog (PE `02e97a2`,
F1 > PE Enhancements > `Unstick movies`, on by default).

## Symptom

Story movies froze, every time, with or without save states. The game kept running at
~60 fps; the picture stopped and the scene never moved on. The New Game opening movie
played.

## What the game is doing (live, debug port 4370)

- The movie player is `MenuCardFirst_UpdateVideoFrame` (`0x80121270`, `menu_memcard`
  overlay, decomp `src/overlays/menu_memcard/video_frame.inc`). It spins on
  `while (StGetNext(...) != 0) if (--retries == 0) return 0;`: no new frame ever arrives.
- `\FMV004.STR` (VideoEntry `end` = 561) stops at **frame 439 every time**
  (`g_MenuCardVideoLastTime` `0x801227E8` = `0x1B7`; MDEC input stops at the same word
  count, 2,956,288, run after run). Deterministic, not a race.
- The drive is fine: `cdrom_timing` shows every data sector delivered on schedule, none
  late or lost; the sectors are valid video sectors (`0x0160`/`0x8001` headers) with
  `data_delivered = 1`. Data-ready interrupts are raised and acknowledged, but the stream
  handler never requests the sector (`request` stays `0x00`), so the runtime overwrites
  them (`ring_dropped` climbing). The game re-seeks and re-reads the same stretch (around
  28:23–29:02, header frame numbers ~511) about every 6 s, forever.

## What it is not (A/B tested)

- **Save states**: freezes from a New Game with no state loaded.
- **The decomp syncs**: a build with the seeds from before both syncs froze the same way.
- **The two hooks added 2026-10-13** (`0x80024250`, `0x8003EB04`): a build with the old
  `game.toml`, using the old overlay cache folder, froze the same way.
- **The interpreted movie player**: first suspected (in the new cache folder,
  `gc0408ccb0`, the player overlay `0x00121000` had never been compiled, so it ran
  interpreted and stalled at the very first frame). Copying the compiled `00121000_*`
  files from the old folder (`gc2c727bcc`) made it compiled; the movie then got further
  (to frame 439) and stalled there instead. One run after the copy played through, which
  was luck or a different movie.

## Workaround

`Unstick movies`: while that player is loaded (first two instructions `27BDFFD0 AFB10024`)
and a movie is running (`g_MenuCardVideoFinished` `0x801223F5` = 0, `g_MenuCardVideoEntry`
`0x801227E4` set), a last frame that hasn't moved for 5 s sets `Finished`, the game's own
end of movie. The rest of that movie is lost; the story carries on. Play log row
`fmv_watchdog` names the movie and frame.

## Next steps for the real cause

- Why the stream library stops accepting sectors at a fixed frame: read libpress's
  `StCdInterrupt` / ring state at the stall (ring full of an incomplete frame? a frame
  larger than its slot? end-frame from `StSetStream`?), and compare a sector-by-sector
  trace of the same stretch in a working emulator (DuckStation) against ours.
- Keep `00121000_*` compiled after `game.toml` changes (the interpreted player stalls
  even earlier).
- Report upstream (psxrecomp CD/stream emulation) once the mechanism is known.
