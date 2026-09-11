# psxrecomp field report — technical companion (AI work orders)

Companion to `psxrecomp-field-report.md`. This version is written to be handed to a coding
AI that has the **`psxrecomp` framework repo checked out** (and ideally a
`parasite-eve-recomp` game repo beside it with a legal disc, for the overlay repros).

Line numbers are from `Alexbeav/psxrecomp @ 94ea3b28` (branch
`release/wave2-v0.3.0-source`, what `parasite-eve-recomp` pins) and may have drifted —
every item gives a `grep` anchor. Do **not** invent behavior: verify each claim against
the tree before changing anything.

**Fork context:** `Alexbeav/psxrecomp` is a fork of `mstan/psxrecomp`. WO-1 and WO-4 were
checked against `mstan/psxrecomp@master` and are **identical there** — these are upstream
bugs, not fork drift. WO-3 / WO-5 are core code the fork doesn't modify, so almost
certainly the same. A fix belongs upstream, then merged down + a submodule pin bump.

---

## Codebase orientation (for the AI)

- **Three execution tiers** (`docs/EXECUTION_MODEL.md`): (1) static AOT C from the disc
  EXE + BIOS, linked into the runtime; (2) native overlays — captured at runtime, compiled
  to per-region DLLs by `tools/compile_overlays.py`; (3) the dirty-RAM interpreter
  (`runtime/src/dirty_ram_interp.c`) — the fallback for anything not yet native.
- **Overlay pipeline:** runtime capture (`runtime/src/overlay_capture.c`) writes
  `overlay_captures.json`; autocompile (`runtime/src/autocompile.c`) spawns the command in
  `[runtime] overlay_autocompile_cmd` (or an env override); `tools/compile_overlays.py`
  turns captured bytes back through `psxrecomp-game` and links a DLL; the loader
  (`runtime/src/overlay_loader.c`) dispatches into it.
- **The overlay link contract** is `runtime/include/overlay_dispatch_preamble.c.inc`. It
  and `overlay_api.h` + `psx_cycles.h` are listed in
  `runtime/codegen_hash_sources.cmake` — editing any of them changes the codegen hash and
  auto-invalidates the overlay cache (`cg<N>_<hash>` path segment). This is correct and
  expected; you do not need to bump anything by hand.
- **`stall_report.py`** needs a `PSX_DEBUG_TOOLS=ON` build (RelWithDebInfo or Debug) — a
  Release runtime ships no TCP server.

---

## WO-1 — clang cannot compile overlay shards (`dllexport` redeclaration)

**Objective:** make `tools/compile_overlays.py` succeed with an llvm-mingw clang toolchain
(the `cmake-clang-v1` pack), not only with GNU GCC.

**Reproduce**

```
# with cmake-clang-v1 on PATH, a game repo with overlay_cache=true, and one captured overlay:
python psxrecomp/tools/compile_overlays.py \
  --captures <exe-dir>/overlay_captures.json --game-toml game.toml \
  --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe \
  --runtime-include psxrecomp/runtime/include --cps \
  --compiler gcc --gcc <cmake-clang-v1>/bin/gcc.exe --out-dir <exe-dir>/cache
```

Every shard fails:

```
frag_patched.c:16:6: error: redeclaration of 'overlay_flush_cycles' cannot add 'dllexport' attribute
psx_cycles.h:129:6: note: previous declaration is here
...
PSX_SHARD_RESULT ok=0 failed=22 skipped=1
```

**Root cause**

- `grep -n 'overlay_flush_cycles' runtime/include/psx_cycles.h` → under
  `#if defined(PSX_OVERLAY_DLL_BUILD)` (≈ line 128), a **plain** forward declaration:
  `void overlay_flush_cycles(void);` (≈ line 129).
- `grep -n 'overlay_flush_cycles' runtime/include/overlay_dispatch_preamble.c.inc` → a
  **`__declspec(dllexport)`** *definition* (lines ≈ 7–16), same `#ifdef _WIN32 … #else
  __attribute__((visibility("default"))) … #endif` idiom.
- In a `frag_patched.c` the plain decl (via `psx_runtime.h` → `psx_cycles.h`) precedes the
  dllexport definition (from the prepended preamble). GCC back-propagates the export and
  compiles. clang emits `err_attribute_dll_redeclaration` — a hard error, **not**
  suppressible with any `-W…`. `-fms-compatibility` "fixes" it but then breaks
  `<vadefs.h>` / `va_list`.
- `overlay_abi` / `overlay_init` in the preamble use the same idiom but are (as of this
  pin) not forward-declared plain anywhere, so only `overlay_flush_cycles` currently
  collides. Grep to confirm before assuming.

**Candidate fix (minimal, low-risk)**

Introduce one export macro and use it on **both** sites. Suggested location:
`runtime/include/overlay_api.h` (already in the codegen-hash source list, already pulled
by both the preamble and `psx_cycles.h`'s consumers):

```c
#if defined(PSX_OVERLAY_DLL_BUILD)
#  if defined(_WIN32)
#    define PSX_OVERLAY_EXPORT __declspec(dllexport)
#  else
#    define PSX_OVERLAY_EXPORT __attribute__((visibility("default")))
#  endif
#else
#  define PSX_OVERLAY_EXPORT
#endif
```

Then:

- `psx_cycles.h` ≈ line 129: `PSX_OVERLAY_EXPORT void overlay_flush_cycles(void);`
- `overlay_dispatch_preamble.c.inc`: replace each `#ifdef _WIN32 … #endif` export block
  with `PSX_OVERLAY_EXPORT` on the definition line (`overlay_flush_cycles`, `overlay_abi`,
  `overlay_init`, and the `overlay_pair_id` in `compile_overlays.py`'s
  `add_overlay_pair_export` — keep that string in sync).

A declaration and definition that agree on the attribute compile clean on both clang and
GCC.

**Alternative (even smaller):** wrap the `psx_cycles.h:129` declaration in the identical
`#ifdef _WIN32 __declspec(dllexport) #else … #endif` block the preamble uses. Uglier
(duplicated idiom) but a one-file change.

**Verify**

- Re-run the repro with the clang toolchain → `PSX_SHARD_RESULT ok=N failed=0`.
- Re-run with GNU GCC → still `failed=0` (no regression).
- `nm`/`llvm-nm` a produced `.dll` → `overlay_flush_cycles`, `overlay_abi`, `overlay_init`
  all exported.
- `docs/COMPILING_OVERLAYS.md` "Is the cache actually being USED?" flow: `stall_report`
  shows `dispatch_native > 0` after a warm run.

**Also worth doing:** extend `compile_overlays.py --check` to build one *synthetic* shard
that `#include`s `psx_runtime.h` + the preamble and references `overlay_flush_cycles`, so
a toolchain that can't build shards fails the preflight with `PSX_SHARD_RESULT` instead of
only at runtime. Anchor: `grep -n "def .*check\|--check\|shardcheck" tools/compile_overlays.py`.

**Risks:** none functional — it's an attribute-consistency fix. The codegen hash changes
(psx_cycles.h / overlay_api.h are hash sources), so existing overlay caches rebuild once.
That's the intended behavior of the hash mechanism, not a regression.

**Upstream:** `mstan/psxrecomp/master/runtime/include/psx_cycles.h` has the identical plain
`void overlay_flush_cycles(void);` under `PSX_OVERLAY_DLL_BUILD`. Same bug in both lines.

---

## WO-2 — overlay caching is off in the scaffolded `game.toml`

**Objective:** ensure a from-source or first-run build actually captures + compiles
overlays instead of interpreting all of them.

**Where**

- `grep -n 'overlay_cache\|\[runtime\]' tools/new_project_layout/probe_disc.py` — the
  `game.toml` `[runtime]` block emitter. As generated it contains only `window_title` and
  `memcard_dir`.
- `grep -n 'runtime.overlay_cache\|overlay_cache' runtime/src/main.cpp` — the whole
  `run_deferred_overlay_init()` path is gated on `gc.runtime.overlay_cache`.
- Check the release path: `grep -rn 'overlay_cache' packaging/ docs/ci/` and whether
  `scripts/package_setup_release.sh` or the first-run Generate wizard injects it.

**Decision needed (not for the AI to make alone):** is `overlay_cache` intentionally off
for the setup-host shape and turned on only after first-run Generate & rebuild? If so this
is just a from-source scaffold gap. If the shipped `game.toml` also lacks it, every player
interprets all overlays.

**Candidate fix:** have `probe_disc.py` emit `overlay_cache = true` in `[runtime]` (with a
short comment), and/or set it in the Generate-flow config write. Keep `idle_skip` as a
separate opt-in.

**Verify:** fresh scaffold + generate + run → boot log shows
`overlay autocompile enabled` and `additive overlay capture store = …`.

---

## WO-3 — captured overlays miss interior function entries → permanent interpreter

**Objective:** stop hot in-overlay functions that the capture classifier doesn't tag as
entries from dispatching to the interpreter forever.

**Reproduce (PE, `RoomLib_InitD`)**

```
# RelWithDebInfo build, overlays warm, in field play:
python tools/stall_report.py --port 4370 snap
```

```
interp_share   0.4075
[5] HOTTEST INTERPRETED PCs:
  0x00191B94  insns=383,000,000  ~26,000 insn/entry  [above-floor]
```

`0x80191B94` is inside a captured, compiled overlay's range, but never appears in that
capture's `function_entry_pcs`, so `compile_overlays.py` doesn't carve it and it stays an
"orphan interior" → interpreter.

Manual proof it's fixable:
`compile_overlays.py --force-interior 0x80191B94` → `interp_share` 40.8% → 4.1%,
`dispatch_native` 0.8M → 36.2M.

**Where in `compile_overlays.py`**

- `grep -n 'def classify_overlay_seeds\|function_entry_pcs\|legacy_seeds\|forced_interiors' tools/compile_overlays.py`
  - `classify_overlay_seeds(cap, data, load_addr, size, …)` — decides entries/interiors.
  - `legacy_seeds = _parse_addr_list(cap.get('seeds', []))` — reads seeds **from the
    capture**, not from the game's `[recompiler] seeds` file.
  - `forced_interiors = { (int(v,0) & 0x1FFFFFFF) | 0x80000000 for v in args.force_interior }`
- The recompiler is already invoked with `--seeds <seeds_path> --ws-config <game.toml>`
  (`grep -n "'--seeds'" tools/compile_overlays.py`) — trace where `seeds_path` comes from;
  it may already be the game's file for the *main*-function pass but not fed into interior
  classification.

**Candidate approach**

After loading a capture in the region-compile path, union into the interior-candidate set
every address from the game's `[recompiler] seeds` list that falls within
`[load_addr, load_addr + size)`. Only carve the ones whose bytes are actually present in
the captured image (don't force-compile addresses the overlay variant doesn't contain —
forcing *all* 1,131 decomp overlay addresses at once produced a 237-DLL background-compile
storm and 0.19× on our box; scoping to "present in this capture" avoids that).

Simpler stopgap already landed locally: `argparse.ArgumentParser(…,
fromfile_prefix_chars='@')` (one line at `grep -n 'ArgumentParser(' tools/compile_overlays.py`)
so a curated `--force-interior` list can be passed as `@file`. Useful but manual.

**Verify:** `stall_report` `interp_share` drops and `[5] HOTTEST INTERPRETED PCs` no
longer shows overlay-region (`[above-floor]`) addresses with millions of insns;
`dispatch_native / dispatch_interp_fallback` ratio rises.

**Risks:** over-carving inflates shard count and compile time; the "present in this
capture" guard is the safety. Interior fragments must still pass the per-function live-byte
CRC guard at dispatch, so a wrongly-forced address just won't load — it won't miscompile.

---

## WO-4 — `PSX_PGO` is an unused CMake variable; `--force-pgo` is a silent no-op

**Objective:** either restore PGO, or make `rebuild --force-pgo` fail loudly instead of
running a pointless instrument→train→use cycle.

**Reproduce**

```
python psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . \
  --build-dir build-release --target psx-runtime --exe-basename <Name> --force-pgo \
  --disc <cue> --train-secs 60 --train-runs 1
```

- `build-release/CMakeCache.txt` → `PSX_PGO:UNINITIALIZED=generate` (passed, never
  consumed).
- The "instrumented" build recompiles ~4 objects, not the generated game C.
- `llvm-nm build-release/<Name>.exe | grep -i 'llvm_profile\|profc'` → nothing.
- `run_pgo_train` then dies with `[WinError 5] Access is denied` at its
  `subprocess.Popen` (line ≈ 1587) — the freshly-relinked exe is momentarily locked
  (Defender / SmartScreen).

**Where**

- `grep -n 'PSX_PGO\|fprofile\|profile-instr\|profile-generate' -r runtime/ recompiler/`
  → **no hits in any CMake file.** The CLI (`grep -n 'PSX_PGO' psxrecomp_cli.py`, line
  ≈ 1370: `f"-DPSX_PGO={pgo}"`) is ahead of the framework.
- **Upstream:** identical in `mstan/psxrecomp@master` — `psxrecomp_cli.py` passes
  `-DPSX_PGO`, `runtime/runtime.cmake` has no `PSX_PGO` / `-fprofile-*`. Same in both.

**Candidate fixes (pick one, or both)**

1. **Restore the plumbing.** Add to the runtime target's CMake:
   ```cmake
   if(PSX_PGO STREQUAL "generate")
     target_compile_options(psx-runtime PRIVATE -fprofile-instr-generate)
     target_link_options(psx-runtime PRIVATE -fprofile-instr-generate)
   elseif(PSX_PGO STREQUAL "use")
     target_compile_options(psx-runtime PRIVATE
       -fprofile-instr-use=${CMAKE_BINARY_DIR}/pgo/default.profdata
       -Wno-profile-instr-out-of-date -Wno-profile-instr-unprofiled)
     target_link_options(psx-runtime PRIVATE
       -fprofile-instr-use=${CMAKE_BINARY_DIR}/pgo/default.profdata)
   endif()
   ```
   (`run_pgo_train` already sets `LLVM_PROFILE_FILE` and merges with `llvm-profdata` — see
   `grep -n 'LLVM_PROFILE_FILE\|llvm-profdata\|default.profdata' psxrecomp_cli.py`.)
2. **Fail fast.** In `cmd_rebuild`, after the `pgo="generate"` configure, read
   `build_dir/CMakeCache.txt`; if it contains `PSX_PGO:UNINITIALIZED` (or a
   `Manually-specified variables were not used` line in the configure output), raise
   `RuntimeError("this framework build has no PGO support (PSX_PGO ignored); rebuilding "
   "without it")` and fall through to the plain build.

Also wrap the `run_pgo_train` `Popen` in a short retry-with-backoff (3× / 2s) for the
`[WinError 5]`.

**Verify:** with fix (1), `llvm-nm` shows `__llvm_profile_*` after `pgo=generate`;
`stall_report` / frame-time improves after `pgo=use`. With fix (2), `--force-pgo` on a
no-PGO framework prints the message and produces a normal build.

---

## WO-5 — single-core wall on older CPUs; one accuracy-neutral mitigation

**Not a bug.** Data point + one idea. psxrecomp is built around a hardware-accurate LLE
runtime and a deterministic scheduler (for netplay rollback) — accuracy and determinism
read as load-bearing design goals, not accidents. So a "fast/low-accuracy tier" is the
wrong suggestion. The accuracy-neutral one:

**Sim-protecting frame skip.** Decouple "advance the guest one video frame" from "present
to the host." When the wall-clock pacer detects the frame ran over budget, execute the
next guest frame but skip the host present (`SwapWindow` / renderer present), keeping the
audio callback fed and input polled at the normal cadence. The *simulation* stays
bit-exact; only display smoothness degrades. Cap consecutive skips (e.g. 2–3) so a
sustained slowdown still shows *something*.

**Where to look:** `grep -n 'present_vsync_owns_cadence\|s_frame_pacer\|g_present_slow_count\|FramePacer' runtime/src/main.cpp`
— the pacing/present loop already tracks slow presents (`g_present_slow_count`, the
`SDL_RenderSetVSync(…, 0)` self-heal). The existing `PSX_SMOOTH_60FPS` / frame-
interpolation code is *present-side* and about upsampling a slower guest to a 60 Hz panel;
this is the inverse — a budget-overrun policy on the guest-advance side. They can coexist.

**Data backing the need** (i7-6700HQ, 2015 mobile, fully-fixed build):

- ~0.79× menus/field, ~0.25× FMV, 1.00× at boot.
- `stall_report` composition: ~69% static native, ~22% exception/LLE-kernel, ~4% interp.
- OpenBIOS vs retail: `exc_share` 20.2% vs 21.8% — the kernel cost is structural.
- `-march=native -O3`: no measurable change (scalar workload).
- Thread-level, 4 min: emulation thread 215 s / 246 s wall; whole process 0.95 cores; one
  thread = 92% of work. Affinity: 8-core 0.775×, 2-core 0.77×, 1-core 0.27×.
- Geekbench 6 single-core: 6700HQ ≈ 1,200, M1 MacBook Air ≈ 2,350 (same build locks 60 on
  the M1).

---

## Notes for whoever runs these

- WO-1 is the highest-value and lowest-risk. It's a correctness fix for the shipped
  toolchain path, testable in isolation.
- WO-1, WO-3, WO-4 are framework (`psxrecomp`). WO-2 spans `probe_disc.py` (framework
  tool) and the title config. WO-5 is a runtime feature.
- Every "fix" here is a *candidate*. Confirm the mechanism against the current tree first;
  the maintainers know intent that a checked-out repo doesn't show.
