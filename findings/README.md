# Findings

Perf + framework-bug investigation from running Parasite Eve Recompiled from
source on a 2015 laptop (i7-6700HQ). Same five findings, four formats for
four different uses:

| File | Audience / use |
|---|---|
| **`framework-findings.md`** | Start here. The most rigorously fact-checked version — a "not fork drift" verification table (checked against `mstan/psxrecomp` and `RetroPortingToolKit/psxrecomp`), then the five findings with repro/root-cause/candidate-fix/verify/risk for each. Written for the framework maintainers. |
| `field-report.md` | Shorter, narrative version — TL;DR first, facts, then suggestions. Easier first read if `framework-findings.md` is more detail than you need. |
| `field-report-technical.md` | Same five findings as AI work orders (WO-1..5) — objective/reproduce/root-cause/candidate-fix/verify/risk per item, meant to be handed to a coding agent with the psxrecomp repo checked out. |
| `perf-report.html` | Visual version — charts, timeline. Open it directly in a browser. |
| `perf-investigation-log.md` | The raw working log behind all of the above — dated test entries, dead ends included (e.g. the ~0.19× compile-storm experiment). Primary source if you want to see the actual sequence of tests rather than the write-up. |

## The five findings, briefly

1. The bundled `cmake-clang-v1` toolchain can't compile a single overlay
   shard (`dllexport` redeclaration clang treats as a hard error) — every
   player on it runs 100% interpreted overlays, permanently, across every
   psxrecomp title.
2. A captured overlay can silently lose a function entry the capture doesn't
   classify as a boundary, and the auto-compile path has no fallback for it
   — one such entry cost ~40% of the frame here.
3. `PSX_PGO` is passed to CMake but consumed by nothing — `rebuild
   --force-pgo` / the launcher's "Optimize FMV" is a silent no-op.
4. The from-source project scaffold (`probe_disc.py`) never sets
   `overlay_cache = true` — a from-source build interprets 100% of overlays
   until that's added by hand.
5. Not a bug: a clean single-core compute wall on 2015-era CPUs, with one
   accuracy-neutral mitigation suggested (sim-protecting frame skip).

Findings 1, 3, and 4 are verified identical in `mstan/psxrecomp@master` and
`RetroPortingToolKit/psxrecomp@master` — upstream bugs, not fork drift from
the `Alexbeav/psxrecomp` pin this project actually builds against.
