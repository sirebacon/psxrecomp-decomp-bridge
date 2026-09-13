**Fixed upstream** — `RetroPortingToolKit/psxrecomp` PR #345 ("Flush Windows
PGO profiles through clean runtime exit," merged 2026-09-11) implements
essentially this exact fix: a `_debug_quit()` using the same
`PGO_DEBUG_PORT = 45231` constant, the same broadened `_soft_stop` exception
handling, and the same per-phase `PSX_DEBUG_TOOLS` toggling. The PR doesn't
credit this repo by name, but the match is precise enough (down to the
arbitrary port number) that it isn't independent convergence. Kept below as
the original investigation record.

# PGO training crashes on Windows, and produces empty profiles even when it doesn't

Follow-up to PR #344 ("Fix overlay Clang exports, PGO, and scaffold cache") —
that PR fixed PGO's *compile-time* half (the CMake plumbing was a genuine
no-op before it; now `-DPSX_PGO=generate` produces a real
`-fprofile-instr-generate` build). This is about the *training* half, which
#344 didn't touch: on Windows, `rebuild --force-pgo` doesn't produce a usable
profile-optimized build. Patch: `patches/02-pgo-train-clean-exit.patch`,
against `2113defc` (on top of #344, not before it). Tested end to end.

## Symptom

```
python psxrecomp_cli.py rebuild --config game.toml --project-root . \
    --build-dir build-release --disc "disc/Parasite Eve (USA) (Disc 1).cue" --force-pgo
...
[4/4] Linking CXX executable Parasite_Eve.exe
WARNING: PGO train run 1/2 (60s) — Do not cancel this process.
[WinError 5] Access is denied
```

Reproduced identically on two separate machines/sessions (one via an
automation harness, one by hand in an interactive terminal), so it's not
environment-specific. A full traceback (the framework normally prints only
`str(exc)`, which is why this looked opaque) shows exactly where:

```
File "psxrecomp_cli.py", line 1776, in cmd_rebuild
    run_pgo_train(...)
File "psxrecomp_cli.py", line 1602, in run_pgo_train
    _soft_stop(proc.pid)
File "psxrecomp_cli.py", line 1490, in _soft_stop
    os.kill(pid, 9)
PermissionError: [WinError 5] Access is denied
```

**The trainee launches and trains for the full duration successfully, every
time.** The crash is in the code that stops it afterward, not in starting it.

## Root cause #1 — the crash

```python
def _soft_stop(pid: int, timeout: int = 30) -> None:
    try:
        os.kill(pid, 15)  # SIGTERM
    except ProcessLookupError:
        return
    for _ in range(timeout):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(1)
    try:
        os.kill(pid, 9)
    except ProcessLookupError:
        pass
```

Windows has no real signals — `os.kill(pid, 15)` is already a hard
`TerminateProcess`, not a graceful request. The trainee apparently takes most
or all of the 30-second grace window to actually unwind (SDL/GL teardown), so
the liveness-check loop runs to the end. By the time the fallback
`os.kill(pid, 9)` fires, the process is in its last instant of exiting, and
`OpenProcess` can return `ERROR_ACCESS_DENIED` for that race instead of "not
found." The function only catches `ProcessLookupError`, so this is an
uncaught crash roughly every run.

## Root cause #2 — even a clean run produces an empty profile

Confirmed by manually driving a training run (launch, wait 60s, hard-stop)
outside `psxrecomp_cli.py` entirely: the resulting `.profraw` is **0 bytes**.
LLVM's profiling runtime only flushes counters via an `atexit`-registered
writer. `TerminateProcess` — which is all a "SIGTERM" can be on Windows —
never reaches it. So even fixing root cause #1 (catching the exception)
would just make the crash quieter, not the training useful: you'd still ship
`-DPSX_PGO=use` pointed at zero real profile data.

## Fix

`psxrecomp_cli.py` already has a working clean-exit path that's simply not
being used here: the debug server's `quit` command
(`runtime/src/debug_server.c`, `handle_quit`) does `send_ok(id);
debug_server_shutdown(); exit(0);` — a real libc `exit()`, which the
profiling runtime's `atexit` handler does run.

The debug server is normally compiled out of Release builds
(`PSX_NO_DEBUG_TOOLS`, gated by the `PSX_DEBUG_TOOLS` CMake option). The
patch turns it on **only** for the throwaway instrumented ("generate")
configure — not the final optimized ("use") build, so the shipped/measured
binary is unaffected — then has `run_pgo_train` ask it for a clean quit
instead of hard-killing the trainee, falling back to the old hard-stop if the
debug server isn't reachable (older builds, or if `PSX_DEBUG_TOOLS` ends up
off for some other reason).

One thing this surfaced that's worth calling out explicitly: **CMake cache
entries persist across reconfigures.** Setting `PSX_DEBUG_TOOLS=ON` for the
instrumented configure and just not mentioning it again for the "use"
configure leaves it **on** in the final cache too — I hit this myself,
verified it (`PSX_DEBUG_TOOLS:BOOL=ON` was still set after the "use" build
completed), and the patch explicitly passes `-DPSX_DEBUG_TOOLS=OFF` on both
the "use" configure and the plain non-PGO configure to guard against it.

See `patches/02-pgo-train-clean-exit.patch` for the full diff (one file,
`psxrecomp_cli.py`, +74/-7).

## Verified

Ran the full cycle end to end after the patch, on the same machine that
reproduced the original crash:

| | before | after |
|---|---|---|
| `rebuild --force-pgo` | crashes, `[WinError 5]` | completes, exit 0 |
| `.profraw` (×2, one per train run) | 0 bytes | 6,109,496 bytes each |
| `default.profdata` | never produced | 1,033,888 bytes |
| `CMakeCache.txt` after the run | `PSX_PGO:STRING=generate` (stuck) | `PSX_PGO:STRING=use`, `PSX_DEBUG_TOOLS:BOOL=OFF` |

## Does it actually help?

Yes, in the one scenario I could measure without a controller driving actual
gameplay: boot → intro → settled at the title screen, headless,
`PSX_FPS_TELEMETRY=2`, same tree / same disc / same `-march=native`, only
`PSX_PGO` differing. Two 90-second runs per build, same on-disk save state
(none) each time so both builds hit the identical deterministic scene:

| Build | Run 1 | Run 2 |
|---|---:|---:|
| No PGO | 0.731× | 0.738× |
| PGO-optimized | 0.850× | 0.850× |

Consistent **+16%** relative, both conditions tight within themselves
(<1% run-to-run). That's a much larger and cleaner signal than the other A/B
tests in this project (OpenBIOS vs retail: noise-level; `-march=native`: no
measurable change), so this looks like a genuine win, not variance.

Not measured: interactive gameplay (menus, field movement, battles) — I
can't drive a controller from here, and the 60s training pass only exercised
early-boot content anyway. Whether the improvement holds, grows, or shrinks
once a real playthrough (and a training run that covers more of the game)
is used is still open.

## Offer

Happy to test further on this box (i7-6700HQ, Windows 10) if useful —
including whether the debug-server round trip adds any measurable overhead
to the training runs themselves (it shouldn't; it's one TCP round trip after
the timed portion of the run).
