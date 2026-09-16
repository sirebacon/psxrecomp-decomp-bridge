# `triage.py`: turn a candidate address list into an eligibility report

Closes the loop between every other tool built this session:
`classifier_gap_finder.py` finds *"here are N addresses the overlay
classifier is stuck on"*; `confidence.py` and `generator.py` each answer one
question about a *single* candidate at a time. `triage.py` runs a whole
list through both and reports which candidates are actually worth spending
more time on — without 640 individual manual checks.

## Usage

```
python bridge/triage.py run \
    --config games/parasite-eve/config.toml \
    --addresses-file saved_annotate_output.txt
```

`--addresses-file` is deliberately permissive: it accepts **any text file
containing `0xXXXXXXXX`-shaped addresses**, so `classifier_gap_finder.py`'s
own saved output works as-is, in any of its formats (the markdown table,
the `--force-interior` argument list, or the PowerShell array literal) —
no reformatting needed. Addresses are extracted by regex, deduplicated, and
sorted; everything else in the file is ignored.

For each address, the report distinguishes two separate questions rather
than collapsing them:

1. **Confidence** (via `confidence.py`) — is there a verified (`semantic_c`
   + byte-matched) decomp implementation at all? `ELIGIBLE` / `INELIGIBLE`
   / `UNKNOWN`, with the specific reason.
2. **Generatable** (via `generator.py`) — checked *only* for confidence-
   eligible addresses — is that implementation also scalar-only (no
   pointers, no struct access), i.e. actually usable by today's generator?

That split matters: confidently verified and immediately generatable are
NOT the same thing. Confirmed against real data —
`Entity_ApplyCollisionResponse` mocked as confidence-eligible still reports
`generatable: no`, with the exact reason (`->` in the body), because being
byte-verified says nothing about whether the implementation touches
pointers. A real candidate can be fully trustworthy and still need manual
work (or the not-yet-built fixed-RAM-mapping path) before it's actually
usable as a native replacement.

## Sample output (real data, fresh Parasite Eve checkout)

```
# Triage: 4 candidate address(es)

0 eligible (0 of those also generator-ready), 1 ineligible, 3 unknown

**1 of the unknowns are semantic_c but blocked only on missing byte-match evidence** -- run `make objdiff-config` (after a build) in the decomp to unlock those.

| Address | Function | +off | Source | Confidence | Generatable |
|---|---|---|---|---|---|
| 0x8001D170 | Entity_ApplyCollisionResponse | 0x0 | src/main/field/Entity_ApplyCollisionResponse.c | unknown | - |
| 0x8007436C | Sys_HleJumpA0 | 0x0 | src/main/sys/Sys_HleJumpA0.c | ineligible | - |
```

Every row uses real addresses and real files from this project's own decomp
— `Entity_ApplyCollisionResponse` (`unknown`, blocked only on missing
`objdiff.json`) and `Sys_HleJumpA0` (`ineligible`, a real BIOS trampoline —
`original_asm`, not `semantic_c`). No `objdiff.json` exists in a fresh
checkout, so `0 eligible` here is the correct, fail-closed answer, not a
bug — the summary line calls out exactly how many results are blocked on
that one missing artifact, so it's obvious what to do next.

## Options

- `--filter {all,eligible,ineligible,unknown,generatable}` — show only
  rows matching that verdict (`generatable` filters to confidence-eligible
  *and* generator-ready rows specifically).
- `--verbose` — print every row's specific reason, plus (for an eligible-
  but-not-generatable row) exactly why the generator refused it.

An address that isn't a function's own start (mid-function offset) or
doesn't resolve to exactly one decomp source file is reported `unknown`
with that specific reason — never silently dropped from the report.

## Generic by design

Same contract as every tool in this bridge: no game-specific data in
`triage.py` itself. It's a pure composition of `classifier_gap_finder.py`'s
symbol table, `confidence.py`'s classification, and `generator.py`'s
scalar-eligibility check — all three already generic, all three driven by
the game's own `config.toml`.
