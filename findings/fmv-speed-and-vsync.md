# FMV speed: no hidden interpreter bug found, and vsync-off doesn't help on Windows

Follow-up prompted by a real observation: "gameplay and in-game menus seem
good now, but FMVs are still very slow" — a sharp inference, since if this
were a pure hardware ceiling, everything would be uniformly slow, not just
video. Two things were checked; both came back negative for a *new* fixable
bug, which is itself useful to have on record.

## Check 1 — does FMV have its own missed-function-entry bug like RoomLib?

Profiled the intro FMV directly (plays automatically on every boot — no
input needed, a good repeatable test case) with `stall_report`, on the
current build with the `0x80191200` / `roomlib-*` fixes already applied:

```
interp_share   0.0859
static_share   0.6475
native_share   0.2175
gpu_share      0.0099
exc_share      0.2165
[5] HOTTEST INTERPRETED PCs (delta): (empty)
```

**No elevated interp_share, no hot interpreted PC.** This is the same
healthy composition as gameplay and menus post-fix, not the 48-94%
interp_share RoomLib showed before it was fixed. Likely explanation: RoomLib
is shared code used across most scenes, not just menus, so fixing it there
already helped FMV too, without FMV needing its own separate fix.

Caveat: this was one 60-second window early in one intro playthrough, not
an exhaustive sweep of every FMV in the game. Absence of a hot PC here isn't
proof no FMV anywhere has this problem — just that the intro FMV, sampled
this way, doesn't.

## Check 2 — does vsync-off help, the way it did on the reporter's Mac?

Early in this project (before any of the fixes above), `PSX_VSYNC=0` was
tried because the same reporter's Mac had FMV running at ~80% speed until
that variable was set, which fixed it there. It did not fix Windows then.
Worth re-testing now that the RoomLib interpreter noise (a much bigger
effect) is gone — a real alternative explanation deserves a real test, not
just standing on an old negative result.

Two 70-second runs of the same intro FMV, `PSX_FPS_TELEMETRY=2`, otherwise
identical (real window, real vsync path this time — headless/dummy video
doesn't exercise present-cadence code the same way):

| | Vsync ON (default) | Vsync OFF (`PSX_VSYNC=0`) |
|---|---:|---:|
| Runtime's own present-cadence log line | `driver vsync (60.0 Hz panel)` | `wall-clock pacer` |
| Speed, first ~10 samples | settles at ~1.00x | settles at ~1.00x |
| Speed, last 30 samples (tail of window) | 0.835x | **0.785x** |
| Overall average | — | 0.920x |

**Vsync-off does not help — if anything it's slightly worse** (within
plausible run-to-run noise, one run per condition, but clearly not the
clear win it was on Mac). Confirms the original finding from early in this
project rather than overturning it.

## Conclusion

Both machines show the same *symptom* (FMV below full speed) but very
likely different *causes*. Whatever the Mac's vsync/compositor interaction
was, this Windows box doesn't have that specific problem. The remaining
Windows FMV cost — speed settling around 0.78-0.84x rather than 1.0x once
warmed up, healthy interp_share the whole time — lines up with genuine MDEC
software-decode cost (see `mdec-idle-decode-cost.md`: real hardware did
this on dedicated silicon for free; this runtime does it on the same single
CPU thread as everything else) plus the ~22% structural LLE-kernel share,
not a hidden bug this toolkit can find or a pacing artifact `PSX_VSYNC` can
fix.

## Verify

`stall_report run --secs N` during FMV playback → `interp_share` should be
low (~8-10%) and the hottest-PC list empty if this still holds. For vsync:
compare `PSX_FPS_TELEMETRY=2` speed averages with and without `PSX_VSYNC=0`
over a matched window of the same FMV — look for the runtime's own
"present cadence" log line to confirm which path was actually active.

## Still open

- Only the intro FMV was checked. Other FMVs (mid-game cutscenes) haven't
  been profiled — if one of them behaves differently (elevated interp_share,
  a hot PC), that would be a new, separate finding, not covered by this one.
- The video-bleed-through-splash-screen transition bug is a related but
  distinct issue (compositing/VRAM clearing, not decode speed) — not
  resolved by anything here.
