# Live verification attempt for `RoomLib_HandlerB`/`HandlerC`: one real, immediate fix found and applied; the original question still open

**Date: 2026-09-16. Status: mixed. A real, confirmed bug found and fixed
live on the currently-checked-out pin (not the same instance as the
earlier, separately-committed fix on a different branch). The
`RoomLib_HandlerB`/`HandlerC` live confirmation itself remains open — the
session ran out of a reliable way to navigate to the specific room state
without visual feedback, not because anything failed.**

## What was attempted

Launched the game for real (`build/play.ps1 -BuildDir build-dbg -DebugPort
4370`, the debug-server-enabled build) with the updated 230-address
`$ForceInterior` default (208 existing + 22 new `RoomLib_HandlerB`/
`RoomLib_HandlerC` addresses from `roomlib-handlerb-handlerc-confirmed-
2026-09-16.md`), intending to use `psxrecomp/tools/stall_report.py` to
directly observe whether those addresses compile natively during real
play, closing the gap the earlier offline `--check` re-verification left
open.

## Found and fixed a real, immediate blocker first

The very first snapshot showed:

```
>> DEGRADED: overlay autocompile failed 3 consecutive runs (last exit 2);
   nothing is being compiled to native code, so overlay execution stays
   in the interpreter.
```

This is the exact `autocompile.c` 4096-byte command-buffer overflow this
project diagnosed and fixed earlier — but that fix lives on a separate
branch (`pe-local-work-c4-autocompile-buffer-fix`, based on the c4/wave5
pin) that was never merged back into the plain old pin this checkout
currently runs. Adding 22 more addresses to an already-long
`--force-interior` list pushed the constructed command further past the
unpatched 4096-byte buffer, re-triggering the identical failure mode on a
different pin.

**Fixed directly on the currently-checked-out pin**: `s_cmd[4096]` →
`s_cmd[8192]`, `full[4200]` → `full[sizeof(s_cmd) + 32]` — the same change
already validated once this session, applied again here since this pin
never had it. Rebuilt `psx-runtime` for `build-dbg` and relaunched.

**Confirmed fixed immediately**, first snapshot after relaunch:

```
autocompile end snapshot: configured=1 state=idle consecutive_fails=0 last_exit=-1
dispatch_native   117,916
dispatch_interp_fallback   203
interp_share   0.0315
```

`interpreted instructions: 257` matches this project's own long-documented
"harmless BIOS baseline" number exactly. This is a real, immediate,
directly-observed fix — not a repeat of the earlier one, a second instance
of the identical bug on a pin that never received it.

## The original question: still open, for a mundane reason

A 75-second windowed capture, then several synthetic `Start`/`Confirm`
button presses over roughly two more minutes (`psxrecomp/tools/raw_tcp.py`
`press buttons=... frames=...`, the same synthetic-input mechanism used
elsewhere in this project's history), never reached a point where
`RoomLib_HandlerB`/`RoomLib_HandlerC`'s specific addresses
(`0x80191D70`-`0x801929F4`) showed up as hot or dispatched at all. The
capture stayed inside an extended intro/logo sequence the whole time —
`0x0010C89C` (the already-documented, architecturally-unavoidable
MDEC/FMV decode cost) and a second, sustained hot address (see below)
dominated throughout, with `interp_share` climbing to 95%+ purely from that
content, unrelated to the addresses being tested.

This is a **methodology limitation, not a negative result**: without
visual feedback or specific knowledge of which menu inputs reach a
`RoomLib_HandlerB`/`HandlerC`-using room, blind synthetic-input navigation
isn't a reliable way to get there in a bounded amount of time. The
addresses remain exactly where the previous document left them: real,
directly observed in an actual gameplay capture, not yet independently
re-confirmed live.

## A genuinely new side-finding, not yet investigated

`0x0018F468` showed sustained, heavy interpreter load throughout the
button-press attempts — 100M+ instructions, ~256K instructions per dispatch
entry, the same order of magnitude as the known FMV decode cost, and
climbing the entire time it was observed. This address sits in the
`0x8018Fxxx` region (the same broad area as several already-fixed
force-interior entries) but is **below** every address already in
`play.ps1`'s list (`0x8018F77C` is the earliest existing entry) — meaning
this is very likely a **previously-uncharacterized hot spot**, not a
recurrence of anything already fixed. Not investigated further this
session — flagged here so it isn't lost, since it showed the same
signature (sustained near-100%-of-window interpreter load) that every
confirmed classifier-gap fix in this project's history started from.

## What this changes

The `RoomLib_HandlerB`/`HandlerC` addresses in `play.ps1` remain correctly
marked not-yet-live-verified — nothing in this session moved that forward
either way. What this session did establish, concretely: the exact same
autocompile buffer bug can recur on a DIFFERENT pin than the one it was
originally fixed on whenever a force-interior list grows past ~4096
characters, which is worth fixing on every pin this project maintains
rather than treating as a one-time fix, and is a strong argument for
proposing the upstream fix now rather than continuing to patch pins one at
a time as they hit the same ceiling.

## Suggested next steps

1. **Upstream the `autocompile.c` buffer fix** (flagged as worth doing
   independently since it was first found) — it will keep recurring on
   every pin as force-interior lists grow, exactly as it just did here.
2. **For `RoomLib_HandlerB`/`HandlerC`**: either have a human actually play
   to a relevant room while `stall_report.py run --secs N` watches (the
   reliable way every prior fix in this project was actually confirmed),
   or invest in learning the specific input sequence to reach one first.
3. **`0x0018F468`**: worth a dedicated look with the same methodology this
   project's own `roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`
   and `fmv-frame-stall.md` used — a real, unclaimed hot spot showed up
   for free while testing something else.
