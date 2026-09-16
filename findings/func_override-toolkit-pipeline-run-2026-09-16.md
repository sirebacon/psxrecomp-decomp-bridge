# Running the full func_override toolkit against real production data: a structural mismatch, not a dead end

**Date: 2026-09-16. Status: a real pipeline run against real data, surfacing a
genuine gap between what the toolkit (`confidence.py`/`generator.py`) was
built to solve and what this project's actual `--force-interior` list is
made of.**

## What was run

`bridge/triage.py` against `build/play.ps1`'s own `$ForceInterior` default —
the real, currently-live, 211-address list this project depends on for
acceptable FMV/gameplay speed (not a synthetic or historical sample; this is
today's production configuration). No filtering, no cherry-picking: every
address in that array, run through `confidence.py` and (where eligible)
`generator.py`'s scalar-only check.

```
python bridge/triage.py run --config games/parasite-eve/config.toml \
    --addresses-file build/play.ps1
```

## Headline result, and why it's more interesting than it looks

```
0 eligible (0 of those also generator-ready), 0 ineligible, 211 unknown
```

Read alone, that looks like a null result. It isn't — the *reasons* behind
those 211 `unknown`s split into three sharply different buckets, and the
biggest one is a real, previously-implicit architectural finding:

| Count | % | Reason |
|---|---|---|
| 192 | 91.0% | **Interior jump-table offset — not a function's own start at all** |
| 16 | 7.6% | Resolves to a real function start, but the address maps to **more than one** decomp source file |
| 3 | 1.4% | Resolves cleanly, classified `semantic_c` — blocked only on missing `objdiff.json` byte-match evidence |

## Finding 1: the toolkit, as built, structurally can't reach 91% of this list

`confidence.py` and `generator.py` were designed around "one candidate
address = one whole decomp function" — resolve an address to its containing
function, classify that function's own source file, generate a replacement
for that function. That model is correct for a genuinely stuck whole
function (an `OBSERVED_PC_ONLY` address that IS a function's real entry
point, just never recognized as one).

It is the wrong model for the majority of what's actually in this project's
own `--force-interior` list. 192 of 211 real addresses are **interior
offsets inside a larger dispatcher function** — exactly the RoomLib
jump-table dispatch problem this whole investigation started from
(`roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`). These aren't
un-decompiled functions waiting for a name; they're `case` labels inside one
big `switch`-shaped dispatcher, which the overlay classifier needs to treat
as separate compilable units but which the decomp correctly does NOT (and
should NOT) list as 192 separate C functions — there's no meaningful
"implementation of 0x8018FA88" apart from the dispatcher it lives inside.

The 192 interior addresses cluster into only **21 distinct containing
functions** — meaning the real shape of this problem is "20-40 stuck
interior offsets per dispatcher," not "192 independent stuck functions":

| Interior addresses | Containing function |
|---|---|
| 40 | `RoomLib_Set3Reset_8018F920` |
| 23 | `RoomLib_Set3Reset_8018FAE4` |
| 21 | `func_8018FA2C` |
| 20 | `func_8018F79C` |
| 17 | `func_8018FA84` |
| 12 | `RoomLib_FxNotify` |
| 10 | `RoomLib_NotifyArmB_801911D8` |
| 10 | `RoomLib_HandlerD` |
| 8 | `func_8018F71C` |
| 7 | `RoomLib_FxShimmer_8018FB58` |
| (11 more, smaller) | |

Six of the top ten containing functions already have real, decomp-assigned
names (`RoomLib_*`) — this isn't a "the decomp hasn't caught up yet"
situation, it's a genuine, permanent shape mismatch between "one classifier
gap = one candidate function" (what `confidence.py`/`generator.py` assume)
and "one classifier gap = one case label inside a shared dispatcher" (what
this project's actual hot spots are). **Extending the toolkit to usefully
cover most of this project's own motivating problem would mean teaching it
about interior/case-label granularity, not just whole-function granularity
— a real scoping gap in `generator.py` as it stands, not a bug.**

## Finding 2: address-only source resolution is ambiguous for overlay code, confirmed concretely

The 16 "resolves to a function start but not one source file" addresses
aren't a resolver bug — spot-checked directly: `func_8018F79C` (offset 0,
one of the interior-cluster dispatchers above) exists as **three separate,
independent files** in the real decomp tree:

```
src/overlays/room_m075/func_8018F79C.c
src/overlays/room_m080/func_8018F79C.c
src/overlays/room_m082/func_8018F79C.c
```

Same guest address, three different rooms, three genuinely different
implementations — PS1 overlays reload code at the same fixed addresses
per-overlay, so an address alone never uniquely identifies a source file for
overlay-region code; you also need to know which overlay is resident.
`confidence.py`'s `resolve_source_file` correctly refuses to guess here
(`len(exact) > 1: return None`, reported `unknown` rather than silently
picking one) — this is fail-closed behavior working as designed, not a
defect, but it's a real, confirmed limit worth documenting precisely rather
than leaving as an abstract "ambiguous" code comment: **any future caller
needs the active overlay/room context, not just the address, to resolve
overlay-region source files reliably.**

## Finding 3: even in the best case, only 3 of 211 real addresses would ever qualify today

`func_8018FA84`, `RoomLib_Set3Range_8018FBBC`, and `func_80192E3C` are the
*only* addresses in this entire real, production-critical list that cleanly
resolve to one function start, one source file, and classify `semantic_c`.
All three report `unknown`, not `eligible`, purely because no `objdiff.json`
exists in this checkout (confirmed: `make objdiff-config` needs
`build/USA/main.map`, which needs a prior full decomp build — not attempted
here, a real, separate, heavier step). Once that byte-match evidence exists,
these three become the toolkit's actual, current reach against this
project's own hot-path list: **3 out of 211, ~1.4%.**

## What this means, honestly

This isn't a failure of `confidence.py`/`generator.py`/`triage.py` — every
one of them did exactly what it was built and tested to do, and did it
correctly against real data (fail-closed on ambiguity, correct
semantic_c/interior-offset classification, accurate aggregation). What it
reveals is that **the toolkit's scope (whole confidently-verified scalar
functions) and this project's own actual bottleneck (interior jump-table
offsets inside shared dispatchers) are two different shapes of problem**,
and closing that gap — if it's worth closing — means teaching the pipeline
about case-label/interior granularity and overlay-aware source resolution,
not iterating on what's already built. Worth deciding deliberately before
investing further, the same way the scalar-only scoping decision for
`generator.py` was made deliberately rather than discovered by surprise
later.

## Reproducing this

```
python bridge/triage.py run --config games/parasite-eve/config.toml \
    --addresses-file build/play.ps1 --verbose
```

`--verbose` prints the specific reason for every one of the 211 rows. Re-run
any time `build/play.ps1`'s `$ForceInterior` list grows (it has grown twice
already, per its own inline history) to get a fresh breakdown for free.
