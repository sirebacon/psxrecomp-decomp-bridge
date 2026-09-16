# `classifier_gap_finder.py`: turning a decomp into a map of where the overlay classifier is stuck

Grew out of the Parasite Eve RoomLib investigation
(`findings/roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md` and
`findings/roomlib-interior-classification-ai-brief.md`): `psxrecomp`'s
overlay classifier can permanently strand genuinely-executed code as
`OBSERVED_PC_ONLY` — never compiled, forever interpreted — when it's reached
through a mechanism the classifier doesn't currently recognize as a valid
function entry (a runtime function-pointer callback, in Parasite Eve's
case). Finding and triaging every instance of that by hand, one bare hex
address at a time across several nights, is slow and error-prone. This tool
automates the two things that manual archaeology actually did.

Lives in `bridge/`, alongside `decomp_bridge.py`, and reuses its `GameConfig`
/ symbol-format loading directly — so it works with any decomp this bridge
already supports (not just Parasite Eve's), and picks up new decomp formats
for free as they're added to `decomp_bridge.py`'s `SYMBOL_FORMATS`.

## The three subcommands

### `annotate` — name the addresses the classifier is stuck on

Takes a saved `compile_overlays.py --check` transcript (run against your
real `overlay_captures.json`) and turns every un-recovered
`OBSERVED_PC_ONLY` bare hex address into: which decomp-known function it
actually falls inside, by what offset, and a ready `--force-interior`
argument list / PowerShell array literal you can paste straight into a
launch script.

```
python bridge/classifier_gap_finder.py annotate \
    --config games/parasite-eve/config.toml \
    --check-log path/to/saved_check_output.txt
```

Validated against this project's own real data: correctly resolved
`0x80190B70` to `RoomLib_HandlerD +0x1C` and `0x80190BAC` to
`RoomLib_Set3Range_80190BAC +0x0` — the same names this project spent real
investigation time recovering by hand.

### `scan-pattern` — find every other place a known-bad pattern hides

Given one already-confirmed bad function's own known-bad interior offsets
(found once, e.g. via `annotate` above plus a live capture), searches the
*entire* decomp for every other function built from the same source pattern
(a macro name, typically) and computes the same offsets against each —
turning "we found one" into "here is a complete list of every place this
exact shape of bug can hide", without needing anyone to actually play
through every one of those areas first.

```
python bridge/classifier_gap_finder.py scan-pattern \
    --config games/parasite-eve/config.toml \
    --pattern "ROOMLIB_STATE_DISPATCH_VARIANT2" \
    --known-offsets 0x60,0x64,0x68,0x6C,0x70,0x74,0x78,0x7C,0x80,0x84
```

Validated against this project's real macro: found the same 64-ish unique
dispatcher addresses this project found by hand with a raw `grep` weeks
ago (the exact count naturally grows as the decomp itself progresses —
re-run any time to pick up newly-decompiled instances for free).

### `scan-shared-libs` — find every AT-RISK pattern automatically, without already knowing one

`scan-pattern` needs you to already know one bad macro's name to start
from. `scan-shared-libs` doesn't: it auto-discovers every shared macro/`.inc`
template reused across many per-room files (the exact shape
`confidence.py`'s func_override eligibility work characterized in detail —
see `findings/func_override-toolkit-pipeline-run-2026-09-16.md`), then
filters to the ones whose own body matches a risk pattern (a `switch`
statement, by default — the confirmed real shape that causes this
project's own RoomLib jump-table classifier gap).

```
python bridge/classifier_gap_finder.py scan-shared-libs \
    --config games/parasite-eve/config.toml
```

**Validated by independently rediscovering the known answer**: run with zero
prior knowledge of which macro was already confirmed bad, this correctly
found `ROOMLIB_STATE_DISPATCH_VARIANT2` (250 per-room users, 66 distinct
names) among its 19 at-risk results — the exact macro
`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md` spent real
investigation nights isolating by hand. Alongside it, it surfaced **18
previously-uncatalogued at-risk templates** (`ROOMLIB_HANDLER_B_ARGS`,
`ROOMLIB_HANDLER_C_ARGS`, `ROOMLIB_HANDLER_D_ARGS`, `ROOMLIB_HANDLER_E_ARGS`,
`ROOMLIB_STATE_DISPATCH`, `ROOMLIB_MSG_DISPATCH`, four `RoomLib_ConfigureHandler*`
`.inc` templates, `RoomLib_AdvanceArcToTarget`/`Y`, `RoomLib_HandlerB`/`C`,
and three more), for **264 distinct candidate addresses** worth checking
against a real `--check` transcript.

Each result comes with a ready `scan-pattern --known-offsets` invocation to
run once a human confirms one instance's actual interior offsets from a
real capture — `scan-shared-libs` finds *what* to investigate, `scan-pattern`
computes candidates once *one* instance is confirmed, matching the same
"prediction, not verification" contract as everything else in this tool.

## What this deliberately does NOT do

All three subcommands are pure, offline, read-only analysis over files you
already have — a saved transcript, and the decomp source tree. None of them
touches a live game, the recompiler, or `compile_overlays.py` itself, and
none applies anything automatically. The output is a **candidate list
for a human to review and verify against real capture data**, not a
verified fix — see the "Explicit warning" section of
`findings/roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md` for why
skipping that verification step (and blanket-applying a large computed list
in one step) caused a real compile-storm regression once already in this
project's own history. Roll out in small batches, checked against real
dirty-RAM behavior after each one — `scan-pattern`'s and `scan-shared-libs`'
own output repeats this warning inline. `scan-shared-libs` additionally
never computes `--force-interior` values directly (unlike `scan-pattern`
with `--known-offsets`) — it has no way to know a jump table's actual
interior offsets without a real capture, so its output is deliberately
just a list of functions worth investigating, not addresses ready to add to
a launch config.

## Known limitations

`annotate`'s "which function contains this address" answer is a
nearest-preceding-symbol heuristic — decomp symbol files generally carry
start addresses, not explicit sizes, so it can misattribute an address to
an earlier function if something in between was never named. Good enough
to turn a bare hex number into useful human context; not a substitute for
checking the actual decompiled source at that offset yourself.

`scan-shared-libs`' address column uses the same flat, global name→address
table `scan-pattern` already relies on — for a name that's genuinely
compiled to a different address per overlay (PS1 overlays can and do vary),
this shows *an* address using that template, from whichever overlay's
symbol file happened to be read last, not necessarily the one for the
specific room you might have in mind. Treat it as "this template is used
somewhere at roughly this address," not a per-room-precise answer.
