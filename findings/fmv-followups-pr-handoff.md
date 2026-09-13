# FMV follow-ups: merged fixes and draft experiments

Completed 2026-09-12, America/Los_Angeles (merge timestamps are 2026-09-13 UTC).
Repository: `RetroPortingToolKit/psxrecomp`.
Reviewed baseline: `3a275d49397ba2e2f4cc4399d76ffd47465e8d44`.
Resulting upstream master: `ee1d72543c219139d17c85470ec6c0526d554593`.

## Outcome

Two objectively supported fixes are merged. Two experimental/design follow-ups
remain draft PRs, with no auto-merge. No IRQ/slice/I-cache check suppression or
IPO default change was merged. No performance improvement is claimed.

| PR | Disposition | Contents | Commit |
| --- | --- | --- | --- |
| [#355](https://github.com/RetroPortingToolKit/psxrecomp/pull/355) | Merged | Restore offline builds by guarding optional netplay authentication/chat dependencies | Merge `de8b942fb4f1d62087ce212c94cf1625a2805395` |
| [#354](https://github.com/RetroPortingToolKit/psxrecomp/pull/354) | Merged | Repair live CFG reverse edges, reachability and natural-loop metadata; correct final fallthrough guards | Merge `ee1d72543c219139d17c85470ec6c0526d554593` |
| [#356](https://github.com/RetroPortingToolKit/psxrecomp/pull/356) | Draft; do not merge yet | Opt-in runtime IPO/LTO experiment, support checks and PGO orchestration tests | Head `20ec948ab1143677f90947644591c5d5f033a034` |
| [#357](https://github.com/RetroPortingToolKit/psxrecomp/pull/357) | Draft; do not merge yet | IRQ-batching RFC, correctness invariants and real-cache counterexample; **not a batching implementation** | Head `847c2baf379bdbd5353a6d941643284e5a4b6dd9` |

Both drafts are rebased onto the resulting master. Their remaining work is
explicitly deferred for evidence/review, not silently approved for later merging.

## What was confirmed and fixed

### CFG metadata — #354

The live `ControlFlowAnalyzer` populated successors but omitted predecessors.
It also classified a backward-address edge as a loop even when the graph was
acyclic. A real MIPS fixture reproduces both errors:

`80010000 -> 80010020 -> 80010010 -> return`

The fix builds unique reverse edges, declared-entry reachability and
dominance-proven natural back edges, including independent alias entries.
It preserves successor ordering, block ownership and instruction ranges.
Existing final fallthrough guards now use reachability instead of treating any
incoming edge as proof of reachability.

Crucially, this remains an incomplete static graph for runtime CPS/indirect
entries. Its metadata does **not** authorize removing IRQ, cache or device work.
No retail-game failure was demonstrated to originate from these metadata defects.

### Offline runtime build regression — #355

Fresh master builds with netplay disabled failed on unconditional recomp-net
headers; launcher-enabled offline source also retained account-client references.
The fix puts authentication and chat-report dependencies behind their existing
feature guards. Enabled account paths are retained; no guest timing code changes.

This prerequisite was applied equally to baseline and fixed title builds, so
the CFG A/B comparison did not compare different offline-build workarounds.

## Validation performed

All six fresh native builds passed: baseline/fixed for Tomba, MMX6 and Ape Escape.
Game and SCPH-1001 BIOS code was regenerated. Dispatch tables, declarations and
guest code-range manifests are byte-identical across CFG variants for each title.
Generated final tails change as expected; the codegen/cache identity changes
from `30317be3` to `4fe894d2`.

All **67 enabled recompiler CTests passed**, including:

- Real MIPS/alias/duplicate/external-edge fixtures and generated fallthrough tests.
- Nested/multiple-latch, irreducible and unreachable-loop cases; a 12,000-block chain.
- 1000 deterministic random CFGs checked against an independent vertex-removal
  dominance oracle, not another copy of the production algorithm.
- Offline auth preprocessing against real source guards and compilation of the
  real disabled-lobby C translation unit without recomp-net dependencies.

Three pre-existing disabled tests were not counted as passes:
`interpreter_perf_guards`, `runtime_perf_diag_guards`, `overlay_pair_dedup_runtime`.
The enabled suite was rerun after the CFG rebase. Subsequent changes were docs only;
the landed source tree matches the tested production source.

### Live title matrix

Windows x64 / Clang 22.1.8 / RelWithDebInfo / OpenGL headless / debug tools ON /
netplay and launcher UI OFF. Retail SCPH-1001 LLE boot; existing deterministic
HLE thread scheduler unchanged. Separate saves and overlay caches per variant.
No game mods or timing-check suppression. Warm runs reuse the same variant's
cold-run cache. Input runs use that existing cache with bounded button injection.

| Title | Baseline cold / warm frames | Fixed cold / warm frames | Additional input run: baseline / fixed |
| --- | --- | --- | --- |
| Tomba! USA, SCUS-94236 | 11003 / 11003 | 11000 / 11004 | 14004 / 14011 |
| Mega Man X6 USA v1.1, SLUS-01395 | 11015 / 11000 | 11026 / 11016 | 14005 / 14020 |
| Ape Escape USA, SCUS-94423 | 11005 / 11005 | 11004 / 11011 | Not run |

All **16 runs** reached their frame threshold and exited 0, with native overlay
dispatch, nonzero guest SPU output and zero BIOS kernel-verification mismatches.
Screenshots were inspected: Tomba FMV/title, MMX6/Ape gameplay attract demos,
Tomba's initial scene/dialogue and pause response, and MMX6's new-game story.

These are bounded regression smokes, **not full playthroughs**. Input delivery
was wall-clock polled, not lockstep; injection frames and dialogue boundaries
differed, so this is not a deterministic guest-state equivalence result.
Headless host audio output was inactive: SPU counters do not establish audible
host-output quality. Online sign-in, other platforms, unvisited levels and
IPO-enabled title behavior were not validated. No GitHub checks were reported;
the test evidence is local, not a claimed green CI run.

The checks support the two scoped merges; they cannot establish zero regression
risk everywhere. Tomba2 was deliberately untouched. No game repository pins or
user game configurations were updated.

Portable details are committed in
[CFG_METADATA_VALIDATION.md](https://github.com/RetroPortingToolKit/psxrecomp/blob/ee1d72543c219139d17c85470ec6c0526d554593/docs/internal/CFG_METADATA_VALIDATION.md).

## Why the remainder stays draft

### #356 — IPO/LTO and PGO validation

`PSX_RUNTIME_IPO` defaults OFF. ON explicitly checks C/C++ support and opts only
optimized runtime target configurations into IPO, not third-party targets,
Debug builds or independently compiled overlay DLLs. This is narrower than the
contributor's project-wide IPO setting.

Actual Clang two-file C/C++ IPO compile/link/execution passed, along with default,
parent-policy, unsupported-toolchain, unrelated-target and Debug-OFF checks.
Mocked PGO success/failure tests also passed. These were repeated after rebase.

No real IPO-enabled game run or end-to-end PGO training was performed for this
draft. The title matrix above used IPO OFF and is not evidence for turning it ON.
Needed before promotion: shipping compiler/platform and launcher coverage,
IPO-enabled title regression, representative PGO coverage, content-aligned repeated
trials with matching profiles, frame-time tails/audio evidence, and measured
build/link/size costs. The PE gain has not been independently reproduced.

### #357 — IRQ batching remains a design question

The real-cache test proves that keeping a loop-header fetch while omitting a
cold body fetch changes guest state: **14 vs 7 cycles**, load give-back **0 vs 99**,
and a valid vs invalid body cache tag. It was rebuilt and passed after rebase.
This tests the described elision operation, not the unavailable prototype patch.

The RFC requires preservation of cycles, cache state, event deadlines and every
CPS/alias/indirect entry, plus safe cache identity for behavior-changing flags.
A loop iteration or fixed block count is not a guest event-deadline proof.
Static predecessor count is not proof that a block is private to runtime dispatch.

Needed next: the actual prototype and diagnostic patches/base revision, explicit
invariants, synthetic deadline/cache/alias/nested-loop tests, and first-divergence
game/oracle regression. It must also demonstrate a repeatable benefit before being
presented as a performance fix. Nothing in #357 enables batching.

## Disposition of the other brief claims

- **WO-8 decoder/decompression stalls:** retained as a profiling lead in #357.
  Inclusive native-dispatch time cannot distinguish guest decode from callback
  overhead. No verified shared-framework fix or speculative predecode cache was added.
- **WO-9 loader diagnostics:** mismatched DLL/manifest pair rejection is correct.
  A longer diagnostic history is optional, not a correctness fix. #357 proposes
  bounded TCP/ring observability if desired, without weakening pair validation.
- **WO-10 callback overhead:** plausible cost, unquantified here. No no-op callback
  or check-removal experiment was merged.
- **WO-11 graph issue:** corrected and merged in #354; timing optimization stays #357.
- **Reported PGO early stop:** successful current orchestration already performs
  generate/debug-ON -> train -> use/debug-OFF. Injected training failure reports
  failure rather than success. A failing command/revision/exit record is needed
  before calling this a current CLI bug. Standard overlay DLL compilation is a
  separate `-shared -O2` path without PGO/IPO flags; do not claim the decoder DLL
  was trained by the runtime PGO pipeline. Regression tests are in draft #356.

For PE-specific conclusions, the contributor would need to supply matching
capture bytes/configuration/seeds, DLL/manifest/profile identities, instrumentation
and bounded raw measurements. Their absence did not block the confirmed fixes.

## Local handoff and tracking

- Validation evidence: `F:\Projects\psxrecomp\_validation-fmv-prs`.
  Per-title `results/retail-cold`, `retail-warm` and `retail-input` contain JSON
  reports/screenshots. Fresh generated sources, builds and isolated configs remain
  available. No copyrighted assets, captures, profiles or saves were committed.
- Draft worktrees: `_wt-runtime-ipo` on `experiment/runtime-ipo-validation` and
  `_wt-irq-batching-rfc` on `rfc/fmv-irq-batching-invariants`; both clean and pushed.
- The user's dirty main checkout and existing game work were preserved. Upstream
  merges do not imply the dirty local checkout was reset or game pins advanced.
- Central Beads: `beads-eio.3.148` and `.151` closed with validated merge commits;
  `.149` and `.150` open for deferred draft follow-up. Updates are saved locally.
  Dolt remote push failed because the configured remote data ref is missing;
  remote issue synchronization is not claimed and was not repaired in this task.

Requested integration/draft preparation is complete. Remaining experimental
promotion work is deferred pending the evidence above, not running in the background.
