# psxrecomp — five findings from a from-source build, verified in mainline

**Context:** a hobbyist ran **Parasite Eve Recompiled** from source on a 2015 Windows
laptop (i7‑6700HQ). It was slow; I went digging with `tools/stall_report.py`. The five
items below are all framework-level. Done with heavy AI assistance — please sanity‑check
each mechanism against the tree before acting.

**Not fork drift.** The PE title pins `Alexbeav/psxrecomp` (a fork), but I checked the
relevant files in **`RetroPortingToolKit/psxrecomp@master`** (the active tree, 1.9k
commits) and **`mstan/psxrecomp@master`** — the bugs are present, identical, in all three.

| Finding | RetroPortingToolKit @ master | mstan @ master | how checked |
|---|---|---|---|
| 1 · clang can't compile overlay shards | present | present | fetched `runtime/include/psx_cycles.h` from both — plain `overlay_flush_cycles` decl under `PSX_OVERLAY_DLL_BUILD` |
| 2 · captured overlay can silently lose a function entry | present (logic unchanged) | not checked directly | RTK `classify_overlay_seeds` fetched; the auto path takes entries from the capture + `[[overlays]]` in game.toml, not from `[recompiler] seeds` |
| 3 · `PSX_PGO` is an unused CMake variable | present | present | fetched `runtime/runtime.cmake` from both (no `PSX_PGO`/`-fprofile-*`); both `psxrecomp_cli.py` pass `-DPSX_PGO` |
| 4 · `probe_disc.py` scaffolds `game.toml` without `overlay_cache` | present | present | fetched `tools/new_project_layout/probe_disc.py` from both — `[runtime]` = `window_title` + `memcard_dir` only |
| 5 · single-core ceiling on older CPUs | n/a (data point) | n/a | thread + `stall_report` measurements below |

I fetched the four files above from `RetroPortingToolKit/psxrecomp@master` directly (and
three of them from `mstan/psxrecomp@master`); everything else is from the pinned
`Alexbeav/psxrecomp @ 94ea3b28` checkout. Line numbers are from that checkout and may have
drifted — each item has a `grep` anchor.

---

## 1. clang cannot compile overlay shards — `dllexport` redeclaration

**Impact:** the portable `cmake-clang-v1` toolchain (what `ensure-toolchain` downloads;
also, per `docs/COMPILING_OVERLAYS.md`, what the setup wizard / RetComM pull) **cannot
build a single overlay shard**. `autocompile_toolchain_available()` checks the compiler
binary is present and openable, not that a shard actually compiles — so the runtime
believes it can compile; it can't. Any player on that toolchain runs every overlay on the
dirty-RAM interpreter, permanently — across every psxrecomp title, not just PE. (Real
GNU MinGW GCC compiles every shard fine; the failure is clang-specific.)

**Repro** (clang toolchain on PATH, a game with `overlay_cache=true`, ≥1 captured overlay):

```
python tools/compile_overlays.py --captures <exe>/overlay_captures.json --game-toml game.toml \
  --recompiler recompiler/build/psxrecomp-game.exe --runtime-include runtime/include --cps \
  --compiler gcc --gcc <cmake-clang-v1>/bin/gcc.exe --out-dir <exe>/cache
```

```
frag_patched.c:16:6: error: redeclaration of 'overlay_flush_cycles' cannot add 'dllexport' attribute
psx_cycles.h:129:6: note: previous declaration is here
...
PSX_SHARD_RESULT ok=0 failed=22 skipped=1
```

Runtime then logs `overlay autocompile has failed 3 consecutive runs` and interprets
everything.

**Root cause** (verifiable in-tree):

- `grep -n overlay_flush_cycles runtime/include/psx_cycles.h` — under
  `#if defined(PSX_OVERLAY_DLL_BUILD)`: a **plain** `void overlay_flush_cycles(void);`.
- `grep -n overlay_flush_cycles runtime/include/overlay_dispatch_preamble.c.inc` — a
  `__declspec(dllexport)` **definition** (`#ifdef _WIN32 … #else __attribute__((visibility("default"))) … #endif`).
- In a `frag_patched.c` the plain decl (via `psx_runtime.h` → `psx_cycles.h`) precedes the
  dllexport definition (prepended preamble). GCC back‑propagates the export and compiles.
  clang rejects it as a hard error ("cannot add 'dllexport' attribute") — not downgradable
  with any tested `-W…` flag; `-fms-compatibility` gets past it but then breaks
  `<vadefs.h>` / `va_list` (at least with this toolchain's bundled headers).
- `overlay_abi` / `overlay_init` use the same preamble idiom; as of this pin they're not
  forward‑declared plain elsewhere, so only `overlay_flush_cycles` currently collides —
  grep to confirm in mainline.

**Candidate fix** — one export macro, used on both the declaration and the definition:

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

Put it somewhere `psx_cycles.h` is guaranteed to see (it currently has no include of its
own — `overlay_api.h` pulls *it*, not the reverse — so either add the macro to a header
`psx_cycles.h` includes, or define it inline in the same `#if defined(PSX_OVERLAY_DLL_BUILD)`
block right above the declaration). Then use `PSX_OVERLAY_EXPORT` on the `psx_cycles.h`
declaration **and** on the matching definitions in `overlay_dispatch_preamble.c.inc`
(`overlay_flush_cycles`, `overlay_abi`, `overlay_init`) and on `overlay_pair_id` in
`compile_overlays.py`'s `add_overlay_pair_export`. Declaration and definition then agree
on the attribute — clean on clang and GCC.

*Smaller alternative:* wrap only the `psx_cycles.h` decl in the identical
`#ifdef _WIN32 __declspec(dllexport) …` block the preamble already uses.

**Verify:** re-run the repro on clang → `ok=N failed=0`; re-run on GNU GCC → still
`failed=0`; `stall_report` shows `dispatch_native > 0` after a warm run.

**Risk:** none functional. `psx_cycles.h` and `overlay_api.h` are both listed in
`runtime/codegen_hash_sources.cmake` (verified), so the codegen hash changes and existing
overlay caches rebuild once — intended behavior of the hash mechanism, not a regression.

**Preflight gap:** nothing tests the toolchain against a real shard compile up front.
`autocompile_toolchain_available()` only checks the compiler binary. `compile_overlays.py
--check` does build shards, but it needs a captures file (`PSX_OVERLAY_CAPTURES` or
`--captures`), so it can't be run cold. A `--check` mode that builds one self-contained
shard (preamble + `psx_runtime.h` + a reference to `overlay_flush_cycles`, no capture
needed) would catch a broken toolchain before a player ever hits it.

---

## 2. A captured overlay can silently lose a function entry — and the auto path has no fallback

On PE, one such entry cost ~40% of the frame. The mechanism is generic; PE is the
demonstration.

**Evidence** (`stall_report` snap, warm cache, RelWithDebInfo build):

```
interp_share   0.4075
[5] HOTTEST INTERPRETED PCs:
  0x00191B94  insns=383,000,000  ~26,000 insn/entry  [above-floor]
```

`0x80191B94` (= `RoomLib_InitD` per khasinski/parasite-eve-decomp) is inside a captured,
compiled overlay's range but is never in that capture's `function_entry_pcs` — the runtime
reaches it by a path (computed jump / jump table / fall-through) that the capture's
PC-classification doesn't tag as a function entry. So `compile_overlays.py` doesn't carve
it, and it dispatches to the interpreter forever.

`compile_overlays.py --force-interior 0x80191B94` (+ 3 other PCs from `stall_report`):
`interp_share` **40.8% → 4.1%**, `dispatch_native` **0.8M → 36.2M**. Release menus/field
speed went from ~0.72× (dipping to 0.22×) to a stable ~0.79× after this plus a warm cache.

**Where** (`grep -n 'def classify_overlay_seeds\|def _collect_toml_overlay_entries\|forced_interiors\|fromfile_prefix_chars' tools/compile_overlays.py`):

- `classify_overlay_seeds()` builds the entry set from the capture
  (`function_entry_pcs` / `executed_pcs` / `dispatch_entry_pcs`) **plus**
  `_collect_toml_overlay_entries()` — which reads `[[overlays]]` blocks in `game.toml`
  (per-`load_addr` `entry` / `entries` / `function_entry_pcs` lists, optionally CRC-guarded).
- It does **not** read the game's `[recompiler] seeds` file. PE ships no `[[overlays]]`
  block, so nothing supplies the missed entry, and the only fixes are the manual
  `[[overlays]]` list or `--force-interior` — both per-address / per-load-address by hand.

**Candidate:** when a captured overlay is compiled, also treat every address from the
game's `[recompiler] seeds` file that (a) lands in `[load_addr, load_addr+size)` and
(b) has bytes present in *this* captured image as an entry candidate. A title with a
decent seed file (PE's is ~3,000 addrs, ~1,130 in the overlay range) then gets coverage
without hand-maintaining `[[overlays]]`. Guard (b) matters — forcing *all* ~1,130 at once
was a 237-DLL background-compile storm and 0.19× here.

*(I added `fromfile_prefix_chars='@'` to the ArgumentParser locally so a curated
`--force-interior` list can be passed as `@file` — a stopgap, not in mainline.)*

**Verify:** `stall_report [5]` no longer lists overlay-region (`[above-floor]`) PCs with
millions of insns; `dispatch_native / dispatch_interp_fallback` rises.

**Risk:** over-carving inflates shard count/time — guard (b) is the safety. A wrongly-forced
address should just fail the per-function live-byte CRC guard at dispatch rather than
miscompile.

---

## 3. `PSX_PGO` is an unused CMake variable — `rebuild --force-pgo` is a silent no-op

The launcher's **Settings → Optimize FMV** and `psxrecomp_cli.py rebuild --force-pgo`
both do nothing useful.

**Evidence:**

- `psxrecomp_cli.py` `_cmake_configure` passes `-DPSX_PGO={pgo}`, and `docs/` describes
  PGO as a real feature (`[pgo] enabled = true` in game.toml; "Do not set `PSX_PGO` in CI"
  in `GAME_PROJECT_SETUP.md`; also in `LOCAL_CODEGEN_SDK.md` / `FAITHFUL_TIMING_PLAN.md`).
- **But no build file consumes it.** Across the whole tree: `PSX_PGO` appears only in
  `psxrecomp_cli.py` and four docs (`GAME_PROJECT_SETUP.md`, `LOCAL_CODEGEN_SDK.md`,
  `FAITHFUL_TIMING_PLAN.md`, and a comment in `docs/ci/templates/setup-release.yml`);
  no `.cmake` / `CMakeLists.txt` references it, and `fprofile` / `profile-instr` /
  `profile-generate` appear **nowhere**. CMakeCache ends up with
  `PSX_PGO:UNINITIALIZED=generate`.
- The "instrumented" build recompiles ~4 objects (`psx_bios_registry.c`, RC icon, link) —
  not the generated game C.
- `llvm-nm <exe> | grep -i 'llvm_profile\|profc'` → nothing. Not instrumented.
- `run_pgo_train` then dies at its `subprocess.Popen` with `[WinError 5] Access is denied`
  (via the launcher's Windows deferred-rebuild `.bat`). Cause not confirmed — most likely
  the freshly-relinked exe briefly AV-locked, or an exec context issue in the `.bat`. Moot
  given the above, but it'd bite a real PGO run too.

**Candidate fixes (either or both):**

1. Restore the plumbing on the runtime target:
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
   (`run_pgo_train` already sets `LLVM_PROFILE_FILE` and merges with `llvm-profdata`.)
2. In `cmd_rebuild`, after the `generate` configure, read `CMakeCache.txt`; if it has
   `PSX_PGO:UNINITIALIZED`, log "this build has no PGO support; rebuilding without it" and
   fall through to a plain build instead of a pointless train pass.

Plus a short retry/backoff around the `run_pgo_train` `Popen` for the `[WinError 5]`.

---

## 4. `probe_disc.py` scaffolds `game.toml` without `overlay_cache`

`grep -n 'overlay_cache\|\[runtime\]' tools/new_project_layout/probe_disc.py` — the
emitted `[runtime]` block is `window_title` + `memcard_dir` only. Without
`overlay_cache = true`, `run_deferred_overlay_init()` (gated on it in `main.cpp`) never
runs — no capture, no autocompile, every overlay interpreted.

A from-source build therefore interprets 100% of overlays until it's added by hand. If the
release path (first-run Generate, or `packaging/`) injects it, this is only a from-source
gap; if not, shipped titles are affected too — I couldn't confirm which.

**Candidate:** emit `overlay_cache = true` (with a comment) from `probe_disc.py`, and/or
set it in the Generate-flow config write. Keep `idle_skip` separate/opt-in.

---

## 5. Single-core ceiling on older CPUs + one accuracy-neutral mitigation

**Not a bug.** A data point. psxrecomp is built around a hardware-accurate LLE runtime
and a deterministic scheduler (for netplay rollback) — accuracy and determinism are
clearly load-bearing design goals here, not accidents. A "fast/low-accuracy tier" would
cut against that; this suggestion doesn't:

**Sim-protecting frame skip.** Decouple "advance the guest one video frame" from "present
to the host." On a wall-clock budget overrun, run the next guest frame but skip the host
present, keeping the audio callback fed and pads polled at the normal cadence. The
*simulation* stays bit-exact — only display smoothness degrades. Cap consecutive skips
(2–3) so a sustained slowdown still shows something.

**Where:** `grep -n 'present_vsync_owns_cadence\|s_frame_pacer\|g_present_slow_count\|FramePacer' runtime/src/main.cpp`
— the pacing loop already tracks slow presents (`g_present_slow_count`, and a
`SDL_RenderSetVSync(sdl_renderer, 0)` self-heal after 3 presents >250 ms). This would be a
budget-overrun policy on the *guest-advance* side; the existing `PSX_SMOOTH_60FPS` /
interpolation work is present-side and can coexist.

### Appendix — measurements (i7‑6700HQ, 2015 mobile 4C/8T · GTX 1070 idle · retail SCPH‑1001)

Fully-fixed build (overlay_cache + real GCC + targeted `--force-interior` + `idle_skip`),
warm cache:

- **~0.79×** menus/field (≈¾ of an unattended session) · **~0.25×** FMV / heavy scripted
  scenes · **1.00×** at boot.
- `stall_report` time shares (from one snap; the tool notes its rolling windows overlap
  and boundary seconds bleed, so these are approximate and don't sum cleanly):
  static native ~69% · native overlay ~23% · interpreter ~4% · GPU <1% · and
  exception / LLE-kernel ~22% on a partially-overlapping counter.

| A/B | result |
|---|---|
| OpenBIOS vs retail SCPH‑1001 | `exc_share` 20.2% vs 21.8% — no meaningful difference (kernel cost is structural, not a config error) |
| `-march=native` added to the `-O3` build (verified in `build.ninja` FLAGS) | no measurable change (scalar recompiled + kernel workload doesn't vectorize) |
| CPU affinity: all 8 cores / 2‑core pin / 1‑core pin | 0.775× / 0.77× / 0.27× |

Thread-level, ~4‑min session: the emulation thread used **215 CPU‑s of 246 wall‑s**
(~90% of one core, continuous); the whole process totalled **0.95 cores**; that one thread
was ~92% of all the process's CPU. The scheduler migrates it across all 8 logical cores,
so aggregate Task Manager reads ~17–37% and no single core's graph shows 100% — but the
critical path is a saturated core.

Geekbench 6 single‑core (published figures): i7‑6700HQ ≈ 1,200 · Apple M1 ≈ 2,350 — ~2×.
The same build runs playably on an M1 MacBook Air (the user's other machine). Clean
single‑core compute wall on this box: no idle capacity to recruit, no migration cost to
remove.

---

## Offer

Full `stall_report` snap/run dumps and generate + build logs are on hand, and I can
regenerate the failing `frag_patched.c` on request. Glad to test a patch for #1 or #2 on
this exact i7‑6700HQ.
