# Parasite Eve Recompiled — Windows psxrecomp/recomp-ui Framework Upgrade Report

**Date:** 2026-09-15
**Scope:** upgrading an existing Windows dev checkout from the old
`release/wave2-v0.3.0-source` framework lineage to the `codex/wave5-c4-20260915`
pin (the same commits `v0.4.0` ships) — not a fresh clean-install test.
**Test machine:** Windows 10 Home, Ninja + Clang toolchain (`cmake-clang-v1`),
mingw64 gcc for the overlay-DLL side pipeline.
**Source:** `Alexbeav/parasite-eve-recomp` + `Alexbeav/psxrecomp` (submodule)

**Verdict: one real, worth-fixing framework issue — an undocumented hard
version dependency between `psxrecomp` and `recomp-ui` that fails with
misleading errors when they drift out of sync.** Everything else about the
upgrade (the new `PRELOADED_MODS_DIR` mod-loading mechanism, the actual game
build) worked as documented once that was resolved. This is a narrower,
single-issue report, not a full clean-install pass like the macOS one —
different scope, different audience (a developer doing a from-source
framework bump, not an end user running a release zip).

---

## Finding: `psxrecomp` and `recomp-ui` have an undocumented hard version dependency; updating one without the other fails with misleading, unrelated-looking errors

**Severity: Medium-High** (safe once you know about it — reversible, no data
risk — but the failure mode actively points you at the wrong cause).

### What happened

Bumping only the `psxrecomp` submodule pin (old: `67a31460`, based on the
`release/wave2-v0.3.0-source` lineage → new: `0e962bf6`, the `c4`/`wave5`
pin) without also updating the sibling `recomp-ui` submodule produced a
clean CMake configure, then ~20 C++ compile errors in `main.cpp`:

```
error: unknown type name 'RecompLauncherCNetplayChatMessage'
error: no member named 'host_country' in 'RecompLauncherCNetplayLobby'
error: no member named 'allow_spectators' in 'RecompLauncherCNetplayLobby'
error: no member named 'max_spectators' in 'RecompLauncherCNetplayLobby'
error: no member named 'spectator_count' in 'RecompLauncherCNetplayLobby'
error: unknown type name 'RecompLauncherCNetplayOnlinePlayer';
       did you mean 'RecompLauncherCNetplayMember'?
error: no member named 'country' in 'RecompLauncherCNetplayMember'
error: no member named 'lobby_name' in 'RecompLauncherCNetplayMember'
error: no member named 'in_lobby' in 'RecompLauncherCNetplayMember'
error: no member named 'hosting' in 'RecompLauncherCNetplayMember'
error: no member named 'is_spectator' in 'RecompLauncherCNetplayMember'
error: no member named 'memcard_offer_valid' in 'RecompLauncherCNetplayMember'
...
fatal error: too many errors emitted, stopping now [-ferror-limit=]
```

### Root cause

None of these errors are actually about netplay chat/spectator features —
they're a symptom, not the disease. `psxrecomp/runtime/src/main.cpp` at the
new pin calls into a newer netplay lobby API surface
(`RecompLauncherCNetplayChatMessage`, expanded `RecompLauncherCNetplayLobby`/
`RecompLauncherCNetplayMember` struct fields) that only exists in a matching
newer `recomp-ui/src/recomp_launcher.h`. The old `recomp-ui` pin (`4eda654`)
predates that API entirely, so the compiler sees `main.cpp` reference types
and fields that genuinely don't exist yet in the checked-out header — hence
real, correct compile errors, just about the wrong root cause.

Nothing in `.gitmodules`, the build output, or a configure-time check states
that `psxrecomp` and `recomp-ui` must move together. The only way to
discover the correct pairing was cross-referencing `framework_pins.txt` from
the published `v0.4.0` tag, which happens to bump both
(`psxrecomp=667900c`→`0e962bf6`, `recomp-ui=4eda654`→`ff92028`) in the same
commit — the pairing is implicit in "what shipped together," not stated
anywhere explicitly.

### Fix applied and verified

Updated `recomp-ui` to `ff92028ec86e30503694c70c532b93b8198663aa` (the exact
commit `v0.4.0`'s own `framework_pins.txt` pairs with the new `psxrecomp`
pin). Reconfigured and rebuilt from scratch:

```
cmake -S . -B build-release
cmake --build build-release --target psx-runtime
```

Result: clean build, 0 errors, 159/159 build steps completed, linked
`Parasite_Eve.exe` successfully.

### Recommendation

A cheap, high-value fix: have `psxrecomp`'s build assert a minimum
`recomp-ui` API/commit compatibility at configure time — even a simple
version-number check in `recomp_launcher.h` that `runtime.cmake` reads and
compares — so a mismatched pair fails with *"recomp-ui is too old for this
psxrecomp; update it to at least X"* instead of ~20 misleading struct-field
errors in unrelated netplay code. This would have saved real debugging time
here and will do the same for the next person (or the next game's
integrator) who updates one submodule without realizing the other needs to
move too.

---

## What held up

- The new `PRELOADED_MODS_DIR` mod-loading mechanism (added in this same
  framework pin) worked exactly as documented once `CMakeLists.txt` was
  updated to declare it. Build log confirmed: *"staged mod catalog OK: 10
  package(s) = 6 game-owned + 4 framework-owned, all under mods/bundled, no
  mods/packages."*
- This project's own custom mod plugins (`src/mods/*.c`, compiled via
  `target_sources()` — a separate mechanism from `PRELOADED_MODS_DIR`,
  which only covers package-manifest staging, not plugin source
  compilation) built and linked cleanly against the new framework with no
  changes needed to the plugin code itself.
- Live-verified after the full upgrade: booted the rebuilt `Parasite_Eve.exe`
  and read guest RAM directly via the debug server — a mod-controlled value
  (`g_AyaBonusPoints` floor) read back identically (`999`, matching its
  configured default) before and after the framework bump, confirming the
  mod system carries its actual runtime behavior through the upgrade
  correctly, not just "it compiles."
- `PSX_MAX_PLAYERS=2` appearing in the configure log despite this game
  requesting `MAX_PLAYERS 1` looked like a discrepancy at first glance but
  isn't one — checked `runtime.cmake` directly: it's documented, intentional
  behavior (compiled controller capacity always includes both physical PS1
  controller ports; a game's own logical player count is a separate,
  correctly-respected setting). Noting this only so it doesn't get
  re-investigated as a false lead by someone else.

---

## Handoff

Reproducible with just the two commit hashes above — no special setup
needed beyond a normal from-source build. The submodule-pairing issue is
independent of anything OS-specific; it would reproduce identically on
macOS/Linux since it's a pure C++ header/struct mismatch, not a
platform-conditional code path.

If reporting alongside the macOS clean-install report: this is a distinct,
non-overlapping finding — that report's seven findings are all about the
packaged-release end-user setup flow (missing bundled dylibs, dead dialogs,
slow uncached builds, file-naming confusion, Gatekeeper, manual toolchain
installs, vsync discoverability). This one is specific to developers/game
integrators building from source and touching the framework's own git
submodules directly.
