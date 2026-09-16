# `scan-shared-libs`: auto-discovering RoomLib jump-table classifier-gap candidates, validated by rediscovering the known answer

**Date: 2026-09-16. Status: built, validated, real output produced against
this project's own decomp. A candidate list for further investigation, not
a verified fix — see the standard warning at the end of this document
before acting on anything in it.**

## The problem this solves

`classifier_gap_finder.py`'s existing `scan-pattern` command needs a human
to already know one bad macro's name before it can search for more
instances of the same bug. That's exactly backwards from what's actually
needed: the original RoomLib jump-table investigation
(`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`) spent real
nights manually isolating `ROOMLIB_STATE_DISPATCH_VARIANT2` as the first
confirmed instance of this bug class before `scan-pattern` could even be
pointed at it.

`scan-shared-libs` removes that requirement. Using the exact shared-library
detection logic `confidence.py`'s func_override eligibility work built and
validated earlier today (`func_override-toolkit-pipeline-run-2026-09-16.md`)
— recognizing a per-room `.c` file as either a thin `#include "X.inc"`
wrapper or a macro invocation around one real, shared implementation — it
auto-discovers **every** such shared template in the decomp, then filters
to the ones whose own body matches a risk pattern (a `switch` statement by
default, the confirmed real shape behind the RoomLib jump-table bug: a
`switch` compiles to a MIPS jump table, and jump-table case targets are
reached via a computed `jr`, which the overlay classifier doesn't recognize
as a valid function entry).

## The validation that actually matters: it rediscovered the known answer

Run with **zero prior knowledge** of which macro was already confirmed bad:

```
python bridge/classifier_gap_finder.py scan-shared-libs \
    --config games/parasite-eve/config.toml
```

```
# Shared-library scan: 135 shared template(s) found (>= 2 per-room user(s)
each across **/*.c), 19 match risk pattern '\bswitch\s*\('
```

Among those 19 results: **`ROOMLIB_STATE_DISPATCH_VARIANT2`, 250 per-room
users, 66 distinct names** — the exact macro `roomlib-jump-table-dispatch-
classifier-gap-2026-09-14.md` spent real investigation nights isolating by
hand. This isn't a coincidence the tool was tuned to produce; it's a
genuine, blind rediscovery using nothing but structural detection (thin
wrapper/macro shape + a `switch` statement in the body) — real evidence the
detection method generalizes, not just fits one known case after the fact.

## The actual new result: 18 previously-uncatalogued at-risk templates

Alongside the already-known macro, the same run surfaced candidates nobody
had investigated before:

| Template | Kind | Per-room users | Distinct names |
|---|---|---|---|
| `ROOMLIB_STATE_DISPATCH_VARIANT2` | macro | 250 | 66 |
| `ROOMLIB_HANDLER_B_ARGS` | macro | 113 | 28 |
| `ROOMLIB_HANDLER_C_ARGS` | macro | 115 | 28 |
| `ROOMLIB_HANDLER_D_ARGS` | macro | 114 | 27 |
| `ROOMLIB_HANDLER_E_ARGS` | macro | 115 | 28 |
| `ROOMLIB_MSG_DISPATCH` | macro | 13 | 4 |
| `ROOMLIB_STATE_DISPATCH` | macro | 5 | 2 |
| `RoomLib_ConfigureHandlerB.inc` | inc | 12 | 3 |
| `RoomLib_ConfigureHandlerC.inc` | inc | 10 | 1 |
| `RoomLib_ConfigureHandlerD.inc` | inc | 10 | 1 |
| `RoomLib_ConfigureHandlerE.inc` | inc | 10 | 1 |
| `RoomLib_ConfigureWindowHandler.inc` | inc | 5 | 2 |
| `RoomLib_AdvanceArcToTarget.inc` | inc | 125 | 34 |
| `RoomLib_AdvanceArcToTargetY.inc` | inc | 125 | 34 |
| `RoomLib_HandlerB.inc` | inc | 125 | 8 |
| `RoomLib_HandlerC.inc` | inc | 125 | 3 |
| `RoomLib_UpdateTimedRender.inc` | inc | 8 | 5 |
| `RoomLib_UpdateDampedParticle.inc` | inc | 10 | 2 |
| `RoomLib_PollAndResetActor.inc` | inc | 2 | 2 |

**264 distinct candidate addresses total** across these 19 templates —
confirmed by spot-checking one entry directly:
`ROOMLIB_HANDLER_B_ARGS(name, armHandler, phaseHandler)` really is a
function (`int name(RoomEnt *o, int query, unsigned int op, int arg0, int
arg1, int arg2) { ... }`, read directly in `room_lib.h:506`), not a data
structure the naming might suggest — the risk-pattern match is against real
executable code, not a false positive from matching struct field names.

## What this does NOT claim

Matching `--risk-pattern` means the shared template's C body *contains* a
`switch` statement — meaning the compiler *can* produce a jump table there,
not that it definitely did at every site, or that the classifier definitely
mishandles it the way it mishandled `ROOMLIB_STATE_DISPATCH_VARIANT2`. This
tool has no way to know a jump table's actual interior offsets without a
real capture — unlike `scan-pattern --known-offsets`, it deliberately never
emits a `--force-interior` list. Each result comes with the exact
`scan-pattern` invocation to run once a human confirms one instance's real
interior offsets from a live capture or a saved `--check` transcript
(`classifier_gap_finder.py annotate`).

The reported "Address" for a name is resolved through the same flat,
global name→address table `scan-pattern` already uses — for a name that
genuinely compiles to a different address per overlay, this shows *an*
address using that template, from whichever overlay's symbol file was read
last, not necessarily a specific room's exact address. One concrete
instance of this already surfaced: `RoomLib_HandlerBArgs` (no address
suffix) resolved to `(unresolved)` rather than guessing, since no symbol in
the flat table matches that exact bare name — correct, fail-closed
behavior, not a bug.

**Do not blanket-apply any of these 264 addresses to a live launch
config.** See `roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`'s
"Explicit warning" section for why a large, unverified `--force-interior`
list caused a real compile-storm regression once already in this project's
own history. Roll out in small batches, verified against real dirty-RAM
behavior after each one — exactly the discipline that document already
established, now with 18 more templates worth applying it to.

## Reproducing this

```
python bridge/classifier_gap_finder.py scan-shared-libs \
    --config games/parasite-eve/config.toml
```

Options: `--risk-pattern` (default a `switch` statement — widen or narrow
as needed), `--min-users` (default 2 — raise to focus on the
most-duplicated, highest-blast-radius templates first), `--file-glob`
(default `**/*.c`, matching `scan-pattern`'s own default).
