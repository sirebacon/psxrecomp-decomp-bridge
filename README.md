# psxrecomp-decomp-bridge

Feeds a C decompilation's function names and boundaries into a
[psxrecomp](https://github.com/mstan/psxrecomp)-based static recompilation,
using the generic contract psxrecomp already defines for every title built
on it (`symbols.toml`, a seed list, `tools/sync_symbols.py`). One config file
per game — no game-specific code in the engine.

Built while getting **Parasite Eve Recompiled** running well on a 2015
laptop; that work is this repo's reference config
(`games/parasite-eve/config.toml`) and turned up four framework-level bugs
along the way, written up in `findings/` for the psxrecomp maintainers.

## Why bridge a decomp into a recomp at all

A static recompiler translates a game's original binary straight off the
disc — it never reads decompiled source. Left alone, that means every
function shows up as `func_80191B94` in generated code, crash dumps, and
debuggers, and the recompiler only knows where code starts because of a
generic address probe.

A decomp, meanwhile, is expensive-to-acquire, hard-won *understanding* —
what a function does, what it's called, where it starts and ends — with no
runtime, no save states, no netplay, none of the infrastructure a recomp
gives you for free. [Matthew Stanley's "Recomp vs. Decomp: The Wrong
Question"](https://1379.tech/recomp-vs-decomp-wrong-question/) makes the
case that the real target is combining both: recomp for the hardened
shared runtime, decomp for the semantic map laid on top of it. This repo is
a small, working instance of that idea — see `docs/` for how far the
bridging can go (naming today; typed data and hook points are documented
extension points, not yet built).

## Quickstart

See `docs/SETUP.md` for the full walkthrough. Short version:

```
python bridge/decomp_bridge.py --config games/parasite-eve/config.toml \
    --decomp /path/to/parasite-eve-decomp --recomp /path/to/parasite-eve-recomp
```

regenerates `symbols.toml`, the recompiler's seed list, and `psx_symbols.h`
in your recomp checkout from the decomp's symbol files. Nothing here is
committed into either upstream repo — those are local, derived build
inputs, regenerated on demand.

## Layout

```
bridge/           decomp_bridge.py — the generic engine, no game-specific code
                  classifier_gap_finder.py — turn a decomp + a compile_overlays.py
                  --check transcript into a named, actionable list of where the
                  overlay classifier is permanently stuck (docs/CLASSIFIER_GAP_FINDER.md)
                  postman.py — generate an on-demand func_override invoker for
                  one guest function, so a candidate address can be called
                  directly instead of needing to reach it through live play
                  (docs/POSTMAN.md — real unmerged-dependency warning inside)
                  confidence.py — decides whether a decomp's C for a given
                  function is trustworthy enough to wire into func_override;
                  the eligibility gate for the not-yet-built generator
                  (docs/ADDING_A_GAME.md, "Adding a confidence classifier")
games/<name>/     one config.toml (+ manual overrides) per game bridged
docs/             ADDING_A_GAME.md, SYMBOL_FORMATS.md, SETUP.md,
                  CLASSIFIER_GAP_FINDER.md, POSTMAN.md
build/            Parasite Eve's own sync/build/play scripts (PE-specific)
patches/          verified + proposed patches against psxrecomp, with license notes
findings/         the perf + framework-bug writeups, four formats for four audiences
```

## Bridging your own game

Not Parasite Eve-specific by design. `docs/ADDING_A_GAME.md` walks through
pointing the engine at a different decomp + psxrecomp-based recomp pair —
normally just a new `games/<name>/config.toml`, no code changes. It also
documents the confidence-classifier extension point reserved for a planned
decomp-to-`func_override` generator (not built yet), so that tool inherits
the same per-game pluggability from day one instead of a later retrofit.

## Findings

Four framework-level bugs found while doing this for Parasite Eve, verified
against `mstan/psxrecomp@master` and `RetroPortingToolKit/psxrecomp@master`
(not just the pinned fork) so they read as upstream issues, not fork drift.
Start at `findings/README.md`.

## License & credits

MIT for what's in this repo (see `LICENSE`). It leans on three upstream
projects with three different licenses — one of them (the decomp) currently
unlicensed, which is why no decomp-derived data is committed here. Full
breakdown in `CREDITS.md` — read it before assuming you can redistribute
something this tool generates.
