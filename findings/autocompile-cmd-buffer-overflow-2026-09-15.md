# `autocompile.c`'s fixed 4096-byte command buffer silently truncates long overlay-autocompile commands, causing total autocompile failure

**Date found: 2026-09-15. Status: root-caused, fix in progress (see the update
at the bottom once applied and verified).**

## Symptom

After tonight's `psxrecomp`/`recomp-ui` framework upgrade (see
`PE-windows-framework-upgrade-report-2026-09-15.md`), launching Parasite Eve
through the real launcher (`build/play.ps1`, with its full 208-address
`$ForceInterior` default — the accumulated, verified fix from
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`) produced
catastrophically slow gameplay: **8-9 fps (0.14x real-time)**, both in menus
and during the intro FMV.

## Root cause

`psxrecomp/runtime/src/autocompile.c`:

```c
static char s_cmd[4096];   /* large: the runtime-constructed bundled tcc cmd has
                            * many absolute paths (python+script+recompiler+tcc+...) */
...
void autocompile_configure(const char *cmd, const char *cwd) {
    snprintf(s_cmd, sizeof(s_cmd), "%s", cmd ? cmd : "");
    ...
}
```

`play.ps1` constructs `PSX_OVERLAY_AUTOCOMPILE_CMD` (later read via
`std::getenv` into a `std::string` in `main.cpp` — no truncation risk there)
and passes it to `autocompile_configure()`. With the full 208-address
`--force-interior` list, this command is **6,392 characters** long. `snprintf`
safely, silently truncates anything past `sizeof(s_cmd) - 1` = 4095 bytes —
cutting the command off mid-argument, partway through the `--force-interior`
flag list.

The truncated command then fails at the very first argparse step:

```
usage: compile_overlays.py [-h] [--captures CAPTURES] --game-toml GAME_TOML ...
compile_overlays.py: error: argument --force-interior: expected one argument
```

Confirmed directly via `autocompile_status`'s `degraded_reason`:

```
overlay autocompile failed 3 consecutive runs (last exit 2); nothing is being
compiled to native code, so overlay execution stays in the interpreter.
```

**Effect: every single overlay autocompile invocation fails identically, on
every retry, for the life of the process.** Nothing ever gets compiled to
native code — the entire game runs through the pure interpreter, which is
exactly the 8fps/0.14x observed. Three consecutive failures also latch the
autocompile system into a permanent `degraded` state for that process
lifetime (`state: idle`, no further retries at all) — a fresh relaunch is
needed to clear it, the failure doesn't self-heal.

**A second, smaller instance of the same bug exists nearby**, in the Windows
`cmd.exe`-wrapping code a few hundred lines later:

```c
char full[4200];
snprintf(full, sizeof(full), "cmd.exe /C \"%s\"", s_cmd);
```

Even if `s_cmd` itself were made large enough, `full` (which wraps `s_cmd`
plus `cmd.exe /C ""` overhead) would need to grow correspondingly, or it
becomes the new truncation point instead.

## Why this was never caught before tonight

This project's `$ForceInterior` list grew incrementally over several nights
(5 → 26 → 208 addresses, each addition verified separately via the offline
`compile_overlays.py --check` tool, which does **not** go through
`autocompile_configure()`/`s_cmd` at all — it's a completely separate,
direct-invocation code path). The live, in-game `PSX_OVERLAY_AUTOCOMPILE_CMD`
env-var path through this exact buffer was last exercised with the *smaller*
address lists from earlier sessions (well under 4096 chars); tonight is the
first time the full 208-address list was actually exercised live, through a
freshly-rebuilt exe, on the new framework. So this is a real, previously
latent bug that any prior smaller `$ForceInterior` list was too short to
trigger — not a regression introduced by tonight's framework upgrade itself.

## Scaling ceiling worth knowing about before just enlarging the buffer

Windows' own `cmd.exe` has a practical command-line length limit of roughly
8,191 characters (a `cmd.exe` constraint, not one this project's code
imposes) — the `cmd.exe /C "..."` wrapping in the second bug above means the
*effective* usable length for `s_cmd` is bounded by that ceiling regardless
of how large the buffers are made, not by `CreateProcess`'s own much larger
32,767-character limit. 208 addresses (6,392 chars) fits comfortably under
8,191; a substantially longer future force-interior list (e.g. the
640-address computed candidate list from
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`, explicitly
**not** recommended for blanket application anyway) would not, and would
need a fundamentally different invocation mechanism (e.g. an `@file`-style
argument file — this project already has a retired local patch,
`fromfile_prefix_chars='@'`, that did exactly this for `compile_overlays.py`,
though it isn't in the current checkout) rather than a bigger fixed buffer.

## Immediate workaround applied (while the real fix was pending)

Temporarily trimmed `build/play.ps1`'s default `$ForceInterior` list from
208 down to the first 26 addresses (the original 5 WO-3 addresses + the
21-address RoomLib cluster) — the subset already verified to fix the
specific, most user-visible FMV/menu slowdown. The remaining 182 addresses
(a separate, non-FMV-visible region, per
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`'s own findings)
were dropped for this workaround only. This produces a ~1,300-character
command, safely under the buffer limit, and restored gameplay from 8fps to
roughly 38-42fps while overlay compilation warms up. `play.ps1.bak` holds
the untouched, full-208-address original for restoration once the real fix
lands.

## Recommended real fix

1. Enlarge `s_cmd` (and the `full` wrapper buffer alongside it) to
   comfortably hold the full 208-address command with headroom — e.g.
   8192/8320 bytes, chosen to sit just under `cmd.exe`'s own ~8191-character
   ceiling rather than an arbitrary round number.
2. Longer term, consider whether `autocompile_configure()` should reject an
   over-length command with a clear, loud error at configure time instead of
   silently truncating via `snprintf` — a truncated argument list currently
   fails with a generic argparse error that gives no hint the real cause is
   a buffer limit, costing real debugging time (as it did here).

---

## Update: fix applied and verified

**Status: fixed, rebuilt, and confirmed working end to end.**

### The fix

`psxrecomp/runtime/src/autocompile.c`, two buffers enlarged together:

```c
// before
static char s_cmd[4096];
...
char full[4200];
snprintf(full, sizeof(full), "cmd.exe /C \"%s\"", s_cmd);

// after
static char s_cmd[8192];
...
char full[sizeof(s_cmd) + 32];
snprintf(full, sizeof(full), "cmd.exe /C \"%s\"", s_cmd);
```

8192 was chosen deliberately, not as a round-number bump: it sits just under
`cmd.exe`'s own practical ~8,191-character command-line ceiling, which is
the real limiting factor here (see "Scaling ceiling" above) — the `full`
buffer that actually gets executed can't usefully exceed that regardless of
how large `s_cmd` itself is made. `full` now grows in lockstep with `s_cmd`
(`sizeof(s_cmd) + 32`, the fixed `cmd.exe /C ""` wrapper overhead) instead
of being a second, independently-sized constant that could silently become
the new truncation point.

The other two `s_cmd` usages (`autocompile_report_interpreter`'s bounded
token copy into a separate `MAX_PATH` buffer, and a plain `strstr` search)
were checked and don't assume any particular size — no other changes
needed.

### Verification

Rebuilt `psx-runtime` clean (`cmake --build build-release --target
psx-runtime` — 4 files recompiled, 0 errors). Relaunched through the real
`build/play.ps1` with its full, untouched 208-address `$ForceInterior`
default (6,392-character command, the exact one that used to fail):

| | Before the fix | After the fix |
|---|---|---|
| `autocompile_status.compile.last_exit` | `2` (argparse failure) | `0` (success) |
| `autocompile_status.compile.degraded` | `1`, permanently latched | `0`, never triggers |
| Gameplay speed | 8-9 fps (0.14x) | 35-45 fps (0.6-0.75x), climbing as the overlay cache warms up |

No crash, no argparse error, no degraded-state latch across multiple
consecutive autocompile runs (`runs` climbing normally, `last_exit: 0`
throughout). The residual gap to a full 60fps looks like ordinary
cold-cache warm-up on a freshly rebuilt executable — consistent with this
project's own long-documented "first visit compiles in the background,
full warm-up needs a playthrough" behavior — not a new problem introduced
by this fix.

The temporary workaround (trimming `play.ps1`'s default `$ForceInterior`
list to 26 addresses) has been reverted; the file is back to its original,
full 208-address default, now working correctly end to end.

### For Alex

This is a real, previously-latent bug in the shared framework
(`psxrecomp/runtime/src/autocompile.c`), not Parasite-Eve-specific — any
title whose `PSX_OVERLAY_AUTOCOMPILE_CMD` (or configured
`overlay_autocompile_cmd`) exceeds 4,096 characters would hit the identical
silent-truncation failure. Worth upstreaming as its own small, self-contained
fix (two buffer-size changes, no behavioral change otherwise) independent of
anything else in tonight's framework-upgrade report.

---

## Follow-up (same night): fixing the buffer wasn't the whole story — a second, still-open regression in the c4/wave5 pin itself

After the buffer fix above, gameplay speed recovered from 8fps to the
30-45fps range — real progress, but never the expected ~60fps, even after
letting the overlay cache fully warm (confirmed idle, 364 real DLLs built,
nothing left queued). `dirty_ram_insns` kept climbing into the billions
without ever settling, well past the point (by guest frame count) where
every prior test this project has run settles cleanly.

### Controlled A/B: isolated to the framework pin itself, not our own fixes

Built and ran the exact same launch (`build/play.ps1`, same disc/BIOS,
`-VsyncOff`, same debug port) three ways, back to back:

| Configuration | Result |
|---|---|
| **Old pin** (`psxrecomp` `67a31460`, `recomp-ui` `4eda654` — pre-upgrade) | Clean: `dirty_ram_insns` flat at the harmless 257 baseline through frame 9,535, settles to **20,304** by frame 10,748 (t+140s) — exactly matching every prior measurement this project has ever taken |
| **New pin** (`psxrecomp` c4/wave5 + buffer fix), full 208-address force-interior list | `dirty_ram_insns` still climbing at 1.3B+ past frame 35,000 (many minutes), never settles |
| **New pin, zero force-interior addresses** (ruling out our own fix as the cause) | Still climbing (1.34B by frame 12,672) well past the frame count where the old pin cleanly settled — growth rate decelerating but not plateauing |

**This rules out our own `--force-interior` list as the cause.** The
original hypothesis — that the new jump-table classifier (`fe2c0046b`)
handling some of our forced addresses differently than the old classifier
might create a real correctness conflict — is refuted by the third row:
the stuck/non-settling behavior happens on the new pin even with *zero*
forced addresses. Something else in the `psxrecomp`/`recomp-ui` c4/wave5
upgrade itself causes markedly heavier interpreter usage during the
intro/FMV window, independent of anything this project has added locally.

### Status: unresolved, not yet root-caused

This is now a confirmed, real regression isolated to the framework pin
itself (clean A/B, three configurations, same test harness) — but *why*
is still open. Candidates not yet checked: something in the new BIOS HLE
plan (`bios_hle_plan.c` appeared as a changed/new file in the c4 build
output during compilation), a change in idle-skip or frame-pacing
behavior, or something else entirely in the ~50 commits between the old
pin and c4/wave5. Given the old pin is fully clean and working, and
chasing this further live risked more inconclusive back-and-forth, the
practical decision for tonight was to revert to the old, known-good pin
for actual play and treat this as its own follow-up investigation with
dedicated time later — not something to report to Alex as fixed, only as
found and precisely isolated.
