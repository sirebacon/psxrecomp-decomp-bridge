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

## The two subcommands

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

## What this deliberately does NOT do

Both subcommands are pure, offline, read-only analysis over files you
already have — a saved transcript, and the decomp source tree. Neither
touches a live game, the recompiler, or `compile_overlays.py` itself, and
neither applies anything automatically. The output is a **candidate list
for a human to review and verify against real capture data**, not a
verified fix — see the "Explicit warning" section of
`findings/roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md` for why
skipping that verification step (and blanket-applying a large computed list
in one step) caused a real compile-storm regression once already in this
project's own history. Roll out in small batches, checked against real
dirty-RAM behavior after each one — the tool's own `scan-pattern` output
repeats this warning inline.

## Known limitation

`annotate`'s "which function contains this address" answer is a
nearest-preceding-symbol heuristic — decomp symbol files generally carry
start addresses, not explicit sizes, so it can misattribute an address to
an earlier function if something in between was never named. Good enough
to turn a bare hex number into useful human context; not a substitute for
checking the actual decompiled source at that offset yourself.
