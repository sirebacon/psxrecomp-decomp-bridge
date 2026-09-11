# Parasite Eve recomp — performance investigation

Working notes, kept as the raw log behind `findings/framework-findings.md` and
`findings/perf-report.html`.

Host: Intel i7-6700HQ (2015, 4C/8T, ~3 GHz sustained) · NVIDIA GL 3.3 · 1× scale
Target: NTSC 59.94 Hz · R3000A 33.8688 MHz · retail SCPH-1001 (US) BIOS

## Short version

PE streams menus / rooms / battles / cutscenes as **code overlays**. psxrecomp only
translates the main EXE ahead of time; overlay code runs static-native,
compiled-on-first-sight-native, or on the **dirty-RAM interpreter**.

The scaffold `game.toml` never set `overlay_cache = true` → 100% of overlay code
interpreted. Enabling it exposed that the bundled clang toolchain can't compile
overlay shards. With real GCC in place, overlays compiled — but one function
(`0x80191B94` = `RoomLib_InitD`) stayed stuck in the interpreter and was ~99% of
the remaining interpreter cost: 383M interpreted instructions.

`compile_overlays.py --force-interior 0x80191B94` (+3 other hot PCs) dropped the
interpreter's wall-clock share from ~41% to ~4%.

## Measured (debug build · stall_report · before → after --force-interior)

| signal | before | after | note |
|---|---:|---:|---|
| `interp_share` (time) | 40.8% | 4.1% | the win |
| `native_share` (time) | 3.1% | 23.0% | overlay code now native |
| `dispatch_native` events | 0.8M | 36.2M | 44× |
| `0x80191B94` interp insns | 383M | 25M | hot loop mostly native |
| Release steady speed | ~0.72× | ~0.80× | + stopped collapsing to 0.22× |
| `exc_share` (time) | 16.5% | 21.8% | now the #1 lever |

Post-fix frame composition (approx, windows overlap): static native 69% ·
native overlay 23% · interpreter 4% · GPU <1% · exception/kernel handling ~22%
(separate overlapping axis).

## Changes on disk (all local, not committed upstream)

- `parasite-eve-recomp/game.toml` `[runtime]`: `overlay_cache = true`, `idle_skip = true`
- `build/play.ps1` — launch wrapper: overlay autocompile via WinLibs GCC,
  `-ForceInterior` hot set, `PSX_FPS_TELEMETRY=2`, `--no-launcher`, `-BuildDir` / `-DebugPort`
- `bridge/decomp_bridge.py` — decomp→recomp bridge: 1,674 symbols + 3,036 seeds (later
  generalized into a config-driven engine — this log predates that refactor)
- WinLibs GCC 16.1.0 → `%LOCALAPPDATA%\Programs\mingw64\` (bundled clang can't build shards:
  hard `cannot add 'dllexport' attribute` error, clang-only)
- Builds: `build-release/` (37.5 MB) · `build-dbg/` (163 MB, RelWithDebInfo, debug server :4370,
  needs `libc++.dll`/`libunwind.dll`/`libwinpthread-1.dll` copied beside it)

## What the decomp actually contributes (asked 2026-09-09)

The recompiler works straight off the disc; it never reads decomp C. The decomp is a
reference layer via the bridge (`bridge/decomp_bridge.py`, `sync_decomp.py` at the time
this was written):
- `symbols.toml` — 1,674 names, **all `emit = false`** → naming only, zero build effect
  (it's why `0x80191B94` reads as `RoomLib_InitD`)
- `seeds/ghidra_funcs.txt` — 1,300 probe baseline **+ 1,736 from decomp** → function-start
  hints the recompiler consumes; additive, helps coverage
- `--force-interior` addrs → the 4 that matter came from `stall_report`, decomp just labeled them

None of the three real problems (overlay_cache off / clang can't build shards / one overlay
function interpreted) are decomp-caused.

## Open — next tests

- ~~Kernel / exception overhead (~22%)~~ — **TESTED 2026-09-09.** OpenBIOS vs retail: no
  difference, exc_share ~20–22% both ways, OpenBIOS marginally slower. Inherent LLE-kernel
  cost, not BIOS-fixable. `kernel_bless clean=205/907` was fine — the "clean=0" note in
  stall_report is a generic canned message. Retail stays the pick (gets kernel-call HLE).
  Only remaining knob: `PSX_EVENT_STEP_*` granularity (trades accuracy — skip for now).
- ~~Per-room overlay tail via full decomp list~~ — **TRIED 2026-09-09.** Patched
  `compile_overlays.py` with `fromfile_prefix_chars='@'` (see `patches/`), forced all
  1,131 decomp overlay funcs via a local `@file` → compile storm, 237 half-built DLLs,
  ~0.19×. Reverted; that `@file` was a throwaway and isn't kept in this repo (see
  `play.ps1 -AllInteriors`, which now refuses to run rather than silently no-op). Right
  approach: grow `-ForceInterior` from per-area `stall_report` hot lists, or a curated
  RoomLib-only subset.
- ~~PGO + `-march=native` rebuild~~ — **DONE 2026-09-10.**
  - `-march=native -O3` applied cleanly (verified in `build.ninja` FLAGS). **No measurable
    change** — menus/field ~0.79× either way. Scalar recomp'd game code + LLE kernel don't
    vectorize. Kept the build (no downside).
  - **PGO not available** in this framework pin. Confirmed twice: (a) our CLI run — "Manually-
    specified variables were not used: PSX_PGO"; (b) user ran the launcher's Settings →
    Optimize FMV — cache shows `PSX_PGO:UNINITIALIZED=generate`, only 4 objects rebuilt,
    `llvm-nm` shows 0 `__llvm_profile_*` symbols, plus `[WinError 5]` in the deferred-rebuild
    helper. Would need patching `psxrecomp/runtime` CMake for `-fprofile-instr-generate/use`.
    Cleaned the stray `PSX_PGO` cache var; `-march=native` retained in build-release.

**All levers on the list are now spent.** Practical result: ~0.79× in menus/field (73% of an
unattended session), ~0.25× in FMV / heavy scenes. Ceiling on this i7-6700HQ is ~0.8×, held
down by the interpreted RoomLib tail + the ~22% LLE kernel. DuckStation for full-speed play;
recomp is the mod-work platform. Remaining chip-away option: grow `-ForceInterior` from
per-area `stall_report` hot lists.

## The bottleneck is one CPU core

Faithful console emulation is a single-thread CPU race. On this box only the i7-6700HQ works:
- 48 GB RAM — working set ~1–2 GB, capacity irrelevant to CPU-bound work
- GTX 1070 — ~99% idle, PS1 graphics are trivial
- 990 PRO NVMe — helps disc read + shard compile, nothing per-frame
- **i7-6700HQ — 100% of the work, ~1 core. The whole constraint.**

The i7-6700HQ's gaming reputation was the discrete GPU. The CPU is a 2015 Skylake 4-core;
Intel mobile single-core barely moved for years after. Geekbench 6 single-core: 6700HQ ~1,200
vs M1 MacBook Air ~2,350 (~2×). Same single-thread work × 2× core speed → the fanless Air
has headroom, this laptop doesn't. Steam Deck / modern phone / any modern desktop CPU closes
the gap. The recompiled game code needs ≈1.3–1.5 GHz-equivalent sustained on a current core
to lock 60; this CPU delivers ~0.8 of that.

### "Task Manager only shows ~17% CPU" — investigated 2026-09-10

Thread enumeration of Parasite_Eve.exe over a 4-min session:
- thread 2952 (emulation): **215 CPU-s of 246 wall-s** (~90% of one core, continuous)
- next threads: 12s / 3s / 2.5s (GL present, audio, misc)
- process total: 233s / 246s = **0.95 cores**

One thread = 92% of all work, compute-bound. Windows migrates it across all 8 cores every
few ms → no single core's graph shows 100%, aggregate looks like ~17–37%. It IS a pegged core.

Affinity A/B (build-release, gameplay):
- all 8 cores: 0.775× · pinned to 2 cores: 0.77× (no change) · pinned to 1 core: 0.27× (worse —
  present/audio threads need a 2nd core to run concurrently)

→ No idle capacity to recruit, no migration cost to remove. Genuine single-core compute wall.

## Not the issue

Not primarily hardware. Hit 1.00× at boot; native frame code runs full speed. The gap
is specific interpreted-code cost: overlays (mostly fixed) + LLE kernel (next).

## Test log

<!-- date · what changed · speed / stall_report result -->
- 2026-09-09 · baseline (overlay_cache off) · ~0.72× → 0.22×, 100% overlays interpreted
- 2026-09-09 · overlay_cache + real GCC · overlays compile, ~0.72× still
- 2026-09-09 · `--force-interior` x4 · interp 41%→4%, Release ~0.80× stable
- 2026-09-09 · OpenBIOS A/B (debug build) · exc_share 20.2% vs retail 21.8%, ~0.62× vs ~0.65× — no win
- 2026-09-09 · force ALL 1,131 overlay interiors · compile storm, 237 DLLs, ~0.19× — reverted to opt-in
- 2026-09-10 · `-march=native -O3` rebuild of build-release · menus/field ~0.79× (unchanged); PGO not implemented in framework
