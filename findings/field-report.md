# Field report — PE Recompiled from source, on 2015 Windows hardware

**For:** mstan / Alexbeav (psxrecomp + parasite-eve-recomp). Findings 1, 3, 4 are
framework-level; 2 is title-config; 5 is a hardware data point. Findings 1 and 4 were
checked against `mstan/psxrecomp@master` and are **identical there** — the PE recomp pins
`Alexbeav/psxrecomp` (a fork), but these are upstream bugs both lines inherit, so a fix
belongs upstream + merged down.

**Who:** a hobbyist running PE Recompiled locally, built from Alex's repo, with a lot of
AI assistance (in the spirit of the project). Not a demand — just data and a couple of
observations from digging in with `stall_report`.

---

## TL;DR

1. The bundled `cmake-clang-v1` toolchain **cannot compile overlay shards** — hard clang
   error, `ok=0 failed=22`. Any player on that toolchain runs every overlay interpreted,
   forever. *(§ Fact 1)*
2. The scaffold `game.toml` has no `[runtime] overlay_cache` — overlays are never
   captured or compiled until it's added. *(§ Fact 2)*
3. The overlay capture never tags one hot function entry (`RoomLib_InitD`). It then
   interprets forever — ~40% of the frame was that single address. *(§ Fact 3)*
4. `--force-pgo` / the launcher's "Optimize FMV" is inert on this pin — `-DPSX_PGO` is
   an unused CMake variable, the binary is not instrumented. *(§ Fact 4)*
5. With 1–3 fixed, the build tops out at ~0.79× on an i7-6700HQ, held down by a ~22%
   LLE-kernel share. Thread + affinity data included — it's a clean single-core wall.
   *(§ Fact 5)*

---

## Environment

| | |
|---|---|
| `parasite-eve-recomp` | `f0c50693` — "Prepare v0.3.5 three-platform packages" (VERSION 0.3.5) |
| `psxrecomp` submodule | `94ea3b28` — "Exclude private overlay helpers from setup kits" (`pin-20260827-runtime-123-g94ea3b28`) |
| `recomp-ui` | `4eda654` |
| Build | `psxrecomp_cli.py generate` + `cmake --build`, portable `cmake-clang-v1` (clang 22, llvm-mingw) |
| Host | Win10 · i7-6700HQ (2015 mobile, 4C/8T) · GTX 1070 · 48 GB |
| BIOS | retail SCPH-1001 (US), size+CRC verified |
| Disc | USA two-disc set; Disc 1 byte-identical to Redump BIN |
| Instrumentation | `tools/stall_report.py` vs a `RelWithDebInfo` runtime (debug server :4370) |

---

# Facts

## Fact 1 — `cmake-clang-v1` cannot compile overlay shards

With `overlay_cache = true`, autocompile fires. Every shard fails:

```
frag_patched.c:16:6: error: redeclaration of 'overlay_flush_cycles'
                     cannot add 'dllexport' attribute
   16 | void overlay_flush_cycles(void) {
psx_cycles.h:129:6: note: previous declaration is here
  129 | void overlay_flush_cycles(void);
```

```
PSX_SHARD_RESULT ok=0 failed=22 skipped=1
```

Runtime then logs `overlay autocompile has failed 3 consecutive runs (last exit 2)` and
keeps every overlay on the dirty-RAM interpreter.

**Mechanism (verifiable in-tree):** `runtime/include/psx_cycles.h:129`, under
`PSX_OVERLAY_DLL_BUILD`, forward-declares `void overlay_flush_cycles(void);` — *plain*.
`runtime/include/overlay_dispatch_preamble.c.inc:7-16` then **defines** it with
`__declspec(dllexport)`. In a `frag_patched.c` the plain decl (pulled in via
`psx_runtime.h`) precedes the dllexport definition. GCC propagates the export backward and
compiles. clang treats "add dllexport in a redeclaration" as a hard error
(`err_attribute_dll_redeclaration`) — no `-W` downgrade; `-fms-compatibility` breaks
`<vadefs.h>`/`va_list`.

- `autocompile_toolchain_available()` returns true (clang.exe, aliased `gcc`, exists), so
  the runtime believes it can compile.
- `compile_overlays.py --check` passes — it doesn't build a shard that references
  `overlay_flush_cycles`.
- Real MinGW GCC (WinLibs 16.1.0) compiles every shard clean, unchanged inputs.

## Fact 2 — scaffold `game.toml` never enables overlay caching

`probe_disc.py`'s generated `[runtime]` block:

```toml
[runtime]
window_title = "Parasite Eve Recompiled"
memcard_dir  = "saves"
```

No `overlay_cache`. `run_deferred_overlay_init()` (gated on `gc.runtime.overlay_cache` in
`main.cpp`) never runs → no capture store, `overlay_autocapture` never enabled → every
overlay runs interpreted. PE is overlay-dense (menus, rooms, battles, cutscenes).

Adding `overlay_cache = true` (+ `idle_skip = true`) is what turned the pipeline on for us.

## Fact 3 — one overlay function entry is never captured → interprets forever

`stall_report` snap, warm cache, after overlays compiled:

```
interp_share   0.4075
[5] HOTTEST INTERPRETED PCs:
  0x00191B94  insns=383,000,000  ~26,000 insn/entry  [above-floor]
```

`0x80191B94` = `RoomLib_InitD` (khasinski/parasite-eve-decomp), in the resident
room-library overlay — present in essentially all field play and menus. Its overlay DLL
compiled; the capture's `function_entry_pcs` never included this address, so it stayed an
"interior fragment" and dispatched to the interpreter — 383M instructions, ~99% of all
interpreter time.

`compile_overlays.py --force-interior 0x80191B94` (+ 3 other PCs from `stall_report`):

| | before | after |
|---|---:|---:|
| `interp_share` | 40.8% | **4.1%** |
| `dispatch_native` (events) | 0.8M | 36.2M |
| that PC, interpreted insns | 383M | 25M |
| Release speed, menus/field | ~0.72× (dips to 0.22×) | **~0.79×, stable** |

(Forcing *all* 1,131 decomp overlay functions instead was a background-compile storm —
237 half-built DLLs, 0.19× — so that's not the answer; a targeted or seed-informed set
is.)

## Fact 4 — `PSX_PGO` is an unused variable on this pin

Ran the launcher's **Settings → Optimize FMV** (`host_pgo_optimize` →
`psxrecomp_cli.py rebuild --force-pgo`).

- CMake cache after configure: `PSX_PGO:UNINITIALIZED=generate` — passed, never consumed
  by any `option()` / `set(...CACHE)`.
- "Instrumented" build recompiled **4 objects** (`psx_bios_registry.c`, RC icon, link) —
  not the ~5M lines of generated game C.
- `llvm-nm Parasite_Eve.exe` → **zero** `__llvm_profile_*` / `__profc_*` symbols.
- No `PSX_PGO` handling in `runtime/runtime.cmake`, `runtime/CMakeLists.txt`, or the
  recompiler CMake at `94ea3b28`.
- The train step then failed with `[WinError 5] Access is denied` at
  `run_pgo_train`'s `subprocess.Popen([exe, …])` — likely Defender locking the
  just-relinked exe. Moot given the above, but it'd bite a real PGO run too.

## Fact 5 — performance on 2015 hardware

Fully fixed build (overlay_cache + real GCC + `--force-interior` + `idle_skip`), warm
cache, i7-6700HQ:

- **~0.79×** menus/field (≈¾ of an unattended session) · **~0.25×** FMV / heavy scripted
  scenes · **1.00×** at boot.
- `stall_report` composition: ~69% static native · **~22% exception / LLE-kernel** ·
  ~4% interpreter · <1% GPU.

A/B tests:

| change | result |
|---|---|
| OpenBIOS vs retail SCPH-1001 | `exc_share` 20.2% vs 21.8% — no meaningful difference |
| `-march=native -O3` (verified in `build.ninja` FLAGS) | no measurable change |
| CPU affinity — all 8 cores | 0.775× |
| CPU affinity — pinned to 2 cores | 0.77× (no change) |
| CPU affinity — pinned to 1 core | 0.27× (worse — present/audio need a 2nd core) |

Thread-level, 4-min session:

| | CPU time |
|---|---:|
| emulation thread (2952) | **215 s of 246 s wall** (~90% of one core, continuous) |
| next 3 threads (GL present / audio / misc) | 12 s · 3 s · 2.5 s |
| whole process | 0.95 cores |

One thread = 92% of the work, compute-bound, migrated across all 8 cores by the scheduler
(so no single core's Task Manager graph reads 100% — aggregate looks like ~17–37%).

Single-core Geekbench 6: i7-6700HQ ≈ 1,200 · Apple M1 (MacBook Air) ≈ 2,350. The same
build locks 60 on the M1. This is a clean single-core compute wall — no idle capacity to
recruit, no migration cost to remove.

---

# Our issues, and what could help

### 1. Bundled toolchain can't build overlays

*Impact:* on this pin, any player whose overlay backend resolves to `cmake-clang-v1` gets
zero native overlays, permanently — and the setup wizard advertises overlay compilation.

*Could help:*
- Give the `psx_cycles.h:129` declaration (and any other shim symbol forward-declared
  plain under `PSX_OVERLAY_DLL_BUILD`) the *same* export attribute the preamble uses.
  That removes the plain→dllexport mismatch; clang then accepts it.
- Have `compile_overlays.py --check` build one synthetic shard that pulls in
  `psx_runtime.h` + the preamble, so a toolchain that can't build shards fails the
  preflight loudly instead of at runtime.

### 2. Overlay caching off by default in the scaffold config

*Impact:* built-from-source (and possibly shipped, if the release `game.toml` doesn't set
it) runs 100% interpreted overlays.

*Could help:* `probe_disc.py` emitting `overlay_cache = true`, or the first-run Generate
flow setting it. If it's already on in the release path, this is just a scaffold gap.

### 3. Missed interior function entries

*Impact:* a hot resident-overlay function silently interprets forever; costs ~40% of the
frame here until hand-forced.

*Could help:* `compile_overlays.py` treating the game's own `[recompiler] seeds` list (or
an explicit seed file) as candidate interior boundaries *within a captured overlay's
range*. The game repo already ships `ghidra_funcs.txt`; the decomp names ~1,150 overlay
functions. (We locally patched `fromfile_prefix_chars='@'` to pass a big
`--force-interior` list — happy to share.)

### 4. `PSX_PGO` inert

*Could help:* wire the `-fprofile-instr-generate/-use` flags back in behind `PSX_PGO`,
**or** have `cmd_rebuild` read `PSX_PGO` back from `CMakeCache.txt` after configure and
fail fast with a clear message instead of running a pointless train pass. Plus a short
retry/backoff around the `run_pgo_train` `Popen` for the `[WinError 5]`.

### 5. Older hardware is a hard single-core wall — one idea that's accuracy-neutral

The ~22% LLE-kernel cost and the single-thread ceiling aren't things a 2015 CPU gets
under. psxrecomp is built around a hardware-accurate LLE runtime and a deterministic
scheduler (for netplay rollback) — accuracy and determinism are clearly load-bearing
goals here. So the useful thing isn't a speed-hack tier (that cuts against the grain);
it's:

**Sim-protecting frame skip.** When a frame overruns budget, skip *rendering* the next
one and keep *simulating* at real-time. The simulation stays bit-exact — audio stays
pitch-correct, input stays responsive — you get visual stutter instead of uniform
slow-motion. Perceptually that turns a rough 0.8× into something close to playable, and
it's the one perf lever that doesn't compromise accuracy. A project targeting frame-
perfect accuracy across a hardware range arguably needs it, or accuracy becomes
"unplayable on anything old."

---

## Offer

Full `stall_report` snap/run dumps, generate + build logs, the failing `frag_patched.c`,
and the `fromfile` patch are on hand. Glad to test a patch for #1 or #3 on this exact
i7-6700HQ.

There's a companion doc, **`psxrecomp-field-report-technical.md`**, written to hand to a
coding AI with the repo checked out — per-issue repro, grep anchors, candidate patches
(including a `PSX_OVERLAY_EXPORT` macro for #1 and CMake for #4), and verification steps.
