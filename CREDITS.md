# Credits & upstream licenses

This repo is a bridge between two independent projects, plus the perf work
that came out of running the combination on modest hardware. It ships no
code from either upstream project — see below for exactly what that means
per project.

## khasinski/parasite-eve-decomp

The reference reimplementation this bridge reads symbol names and function
addresses from. **No license currently selected** — its `LICENSE.md` states
project-authored source stays under the authors' default copyright until one
is chosen. Because of that, **this repo does not commit any output derived
from it** (no `symbols.toml`, no seed list) — `bridge/decomp_bridge.py`
generates those locally from your own clone, and they stay untracked
(`games/*/config.toml` and `games/*/symbols.manual.toml` are ours; the
generated files land in *your* recomp checkout, never here).

If you maintain this decomp: an explicit permissive license on the symbol
files specifically (even if the reimplemented C stays unlicensed for the
obvious IP reasons) would let tools like this one ship a working example
end to end. Happy to talk through it.

## Alexbeav/psxrecomp (fork) and mstan/psxrecomp (upstream)

The static recompiler + runtime. **PolyForm Noncommercial 1.0.0** —
permits modification and redistribution for noncommercial purposes, which
covers everything in `patches/`. Those patches are diffs against this
codebase and inherit its terms; see `patches/README.md`.

`findings/` quotes short (a few lines) excerpts of this codebase's source
and build errors for the purpose of describing and reproducing the bugs
being reported — commentary, not a redistribution of the work itself.

## Alexbeav/parasite-eve-recomp

The Parasite Eve-specific game repo (build scripts, `game.toml`, the
`.psxmod`/plugin scaffold) that pulls in psxrecomp + recomp-ui as
dependencies. **GPL-3.0-only** for its own scripts/config; dependencies keep
their own licenses. This repo doesn't copy its source — `games/parasite-eve/`
only holds *our own* config values (paths, address ranges, symbol-file
locations) that happen to describe how to work with it.

## Parasite Eve

Trademarks, characters, and all game data belong to Square Enix. No disc
image, BIOS dump, or extracted asset is distributed here or ever should be.

## Matthew Stanley (mstan) — ["Recomp vs. Decomp: The Wrong
Question"](https://1379.tech/recomp-vs-decomp-wrong-question/)

The "decomp-annotated-recomp" framing this bridge follows: recomp for
shared, hardened infrastructure; decomp for the semantic understanding
(names, structure) that infrastructure alone can't provide. Worth reading
before extending this tool.

## RetroPortingToolKit/psxrecomp

The active development tree for psxrecomp (R.A.I.D. org). `findings/`
verifies the reported bugs against this tree, not just the pinned fork, to
establish they're upstream issues rather than fork drift.

## This repo

Built with heavy AI assistance (Claude), in the spirit of the wider
recomp/decomp modding scene. Please sanity-check the mechanisms described in
`findings/` against the actual tree before acting on them — they're offered
as leads, not verified patches (except where `patches/README.md` says
otherwise).
