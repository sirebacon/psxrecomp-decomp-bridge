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

## Follow-up (same day): checked the 21 containing dispatchers directly — found a much bigger structural lever than expected

Acting on Finding 1's own suggestion — if a whole dispatcher function is
confidently verified, `generator.py` could replace it at its own entry
point and sidestep the interior-jump-table problem entirely, without
needing any new interior/case-label machinery — recovered the containing
functions' real *start* addresses (not their interior offsets: `start =
interior_addr - offset`, computed from the same triage data above) and ran
them through the pipeline directly.

**Correction to Finding 1's count**: deduping by start address rather than
by name found **22** distinct dispatchers, not 21 — `RoomLib_FxNotify`
reuses the exact same symbol name at two different addresses
(`0x8018FB78` and `0x8018FB90`), which a name-keyed count silently
collapses into one.

```
python bridge/triage.py run --config games/parasite-eve/config.toml \
    --addresses-file <a file listing the 22 dispatcher start addresses>
```

Result: only **2 of 22** (`RoomLib_Set3Reset_8018F920`,
`func_8018FA84`) resolve to one source file — both `semantic_c`, both
blocked purely on the same missing `objdiff.json`, same as Finding 3. The
other **20 of 22** hit the exact same "ambiguous source file" reason as
Finding 2 — but checking *why*, directly against the real decomp tree,
turned up something more interesting than "more of the same ambiguity":

**All 20 are fully decompiled. Zero are missing.** The ambiguity splits into
two structurally different situations that call for different fixes:

1. **Shared-library dispatchers reused via a thin per-room wrapper.**
   `RoomLib_HandlerD` has **124** per-overlay copies, `RoomLib_HandlerB`
   has **117**, `RoomLib_FxNotify` has **125** (counted directly via
   `rglob`). Spot-checked one: `src/overlays/room_m014/RoomLib_HandlerD.c`
   is **two lines** —
   ```c
   /* MASPSX_FLAGS: --expand-div */
   #include "../room_lib/RoomLib_HandlerD.inc"
   ```
   The real, single, canonical implementation lives in
   `src/overlays/room_lib/RoomLib_HandlerD.inc` (one of ~65 shared
   templates in that directory); every room's own `.c` file is just a
   parameter shim (some rooms additionally `#define` room-specific
   constants before the `#include`, which is why two real copies compared
   directly differ in byte length despite sharing the same underlying
   logic). `resolve_source_file`'s per-address, per-`.c`-file model is
   structurally the wrong level for this pattern: there's one real
   confidence question here (**is `RoomLib_HandlerD.inc` itself
   `semantic_c` and byte-matched?**), not 124 separate ambiguous ones. A
   worthwhile, comparatively cheap extension: teach `confidence.py` to
   recognize a thin `#include ".../room_lib/X.inc"`-only wrapper and
   classify/resolve against the shared template directly — one check
   covering up to 125 real addresses at once, instead of 125 ambiguous
   per-room dead ends.

2. **Genuinely independent per-room implementations that happen to reuse
   the same address.** Checked `func_8018F71C` directly: its 3 per-room
   copies (`room_m075`/`room_m080`/`room_m082`) are real, different,
   fully-written-out C, not a template wrapper (confirmed by reading the
   file — pointer params, array indexing, no shared `#include`). PS1
   overlays reuse the same load address across independent rooms, so this
   is a genuine, structural ambiguity, not an artifact of the resolver
   being lazy: each of these really does need its own separate
   verification, and `confidence.py` correctly can't and shouldn't guess
   which room's copy an address means without also knowing which overlay
   is actually resident.

**A confirmed heuristic gap found while reading `func_8018F71C`, worth
hardening even though it wasn't a live bug here**: its body dereferences
memory via `state[0x33]`, `arg1[1]`, and `*(unsigned short *)(arg2 + 0x64)`
— none of which contain `->`. `generator.py`'s body-level pointer check
(`_ARROW_RE = re.compile(r'->')`) would not have caught this on its own;
this specific function was still correctly rejected because its
*signature* already has pointer parameters (`char *arg1, char *arg2`),
caught by the earlier, separate scalar-type check. But the underlying gap
is real: a function with a purely scalar *signature* that dereferences a
pointer internally via `[]` indexing or an explicit cast instead of `->`
would currently slip past the body check undetected. No such case has
actually been found in real, would-be-accepted data yet — flagged here as
a known limitation to hardening `generator.py`'s body scan before trusting
it against a wider address set, not an active bug.

### What this changes

The original recommendation ("check whether whole dispatchers are
eligible") was worth doing, but the real payoff isn't "2 more addresses
unlocked" — it's discovering that most of this specific class of stuck
dispatcher is a **shared-library reuse problem**, not 100+ independent
verification problems. Extending `confidence.py` to resolve through
`room_lib/*.inc` wrappers is a comparatively small, high-leverage change
that would collapse the biggest remaining ambiguity bucket; it's a
different and cheaper piece of work than either the interior-jump-table
extension from Finding 1 or an overlay-aware resolver for the genuinely
independent per-room case above.

## Follow-up 2 (same day): built and verified the `room_lib/*.inc` resolver

`resolve_source_file` now detects the exact shape confirmed above — every
candidate `.c` file for a name is a thin wrapper (no function body of its
own, exactly one `#include "*.inc"`) pointing at the identical target — and
resolves to that shared `.inc` directly instead of giving up. Verified
against the two real cases this session found:

- `RoomLib_HandlerD` and `RoomLib_HandlerB` both now resolve cleanly to
  `src/overlays/room_lib/RoomLib_HandlerD.inc` / `RoomLib_HandlerB.inc`,
  both classify `semantic_c`, both correctly still report `unknown` (not
  `eligible`) since `objdiff.json` doesn't exist yet — exercised the
  `eligible` and `ineligible` branches too via a mocked `objdiff.json`, both
  correct.
- `func_8018F71C` (the confirmed genuinely-independent per-room case) is
  still correctly left ambiguous — the detector requires every candidate to
  be a provable pure wrapper, and these have real, different bodies.

**A real surprise while counting usage**: a precise full-decomp-tree scan
(does this `.c` file's own `#include` target equal the exact `.inc` in
question, regardless of filename) found **125 real per-room users for
*both* `RoomLib_HandlerD` and `RoomLib_HandlerB`** — not the 124 and 117
this document counted earlier by filename. That's not a bug: filename-based
counting misses instances where the same shared dispatcher is wrapped under
a not-yet-renamed `func_XXXXXXXX` placeholder in a specific room (confirmed
directly — e.g. `scene_e22/func_8018F690.c` wraps `RoomLib_HandlerD.inc`
under a name that doesn't mention HandlerD at all). The two totals landing
on the same number (125) is coincidence, not a shared miscount — verified
independently for each template.

**Found and scoped, not fixed, along the way**: this shared-library pattern
has (at least) two real variants in this decomp, only one of which the new
resolver covers. `RoomLib_HandlerD.c`/`RoomLib_HandlerB.c` are literal
`#include "X.inc"` wrappers (covered). `RoomLib_FxNotify.c` and
`RoomLib_Set3Reset_8018FAE4.c` — checked directly — instead do
`#include "../room_lib/room_lib.h"` followed by a **macro invocation**
(`ROOMLIB_FX_NOTIFY(RoomLib_FxNotify)`, `ROOMLIB_SET3_RESET(name, 0x100, 0x1)`)
that expands to the real body from a definition in a header, not a file
include. This is almost certainly the *more* common convention in this
codebase (most of the remaining 18 unresolved dispatchers use it) and would
need a different detector — finding and expanding the macro definition
itself, and confirming its literal per-call arguments don't change the
*shape* of the generated code (some do carry real per-instance constants,
e.g. `0x100, 0x1` above) — genuinely more involved than the `.inc`-wrapper
case, and deliberately not attempted in this pass. `resolve_source_file`
correctly leaves these as ambiguous (`None`) rather than guessing.

**Also hardened during this pass, not found broken but worth noting**: the
wrapper-vs-target path comparison now explicitly `.resolve()`s both sides
before comparing, rather than relying on `cfg.decomp`'s own path already
being in resolved form — no observed failure on this filesystem, but cheap
insurance against a subtly different failure on another one.
