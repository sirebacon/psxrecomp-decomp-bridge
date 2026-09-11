# Setup (Parasite Eve reference config)

1. **Clone the three repos** (this one, the decomp, the recomp):
   ```
   git clone <this repo>            psxrecomp-decomp-bridge
   git clone https://github.com/khasinski/parasite-eve-decomp
   git clone https://github.com/Alexbeav/parasite-eve-recomp
   ```
2. **Get your own legal copies** of the Parasite Eve disc images and a
   retail SCPH-1001 BIOS dump. Not provided here, not linkable here — dump
   your own disc / BIOS chip. `parasite-eve-recomp`'s own README covers
   where these go (`disc/`).
3. **Point the bridge at your checkouts.** Either edit
   `games/parasite-eve/config.toml`'s `[paths] decomp` / `recomp`, or pass
   `--decomp` / `--recomp` on the command line (see below) so you don't have
   to edit the file at all.
4. **(Optional) apply the patches** in `patches/` to your psxrecomp
   checkout — see `patches/README.md` for what each one does and its
   license.
5. **Run the bridge:**
   ```
   python bridge/decomp_bridge.py --config games/parasite-eve/config.toml --no-pull
   ```
   or, from Windows PowerShell, `build\sync.ps1` (pulls the decomp first,
   finds git via GitHub Desktop if there's no standalone git on PATH).
6. **Build.** `build\build_recomp.ps1` runs the sync, then the recompiler
   emitters, C generation, and the runtime build, in order. Needs `cmake`,
   `ninja`, a C/C++ compiler, and `python` on PATH — psxrecomp's own
   `psxrecomp_cli.py ensure-toolchain` can fetch a portable clang+cmake+ninja
   pack if you don't have one, **but see finding #1** — that bundled clang
   cannot compile overlay shards. Use a real GCC (e.g. WinLibs on Windows,
   your distro's `gcc` on Linux) for the overlay autocompile step, or
   overlays silently run in the dirty-RAM interpreter forever.
7. **Play.** `build\play.ps1` wires up the overlay autocompiler and useful
   env vars (see its header for flags). It's Parasite Eve-specific — see
   `docs/ADDING_A_GAME.md` if you're bridging a different title and need
   your own launcher.

## If you're bridging a different game instead

Skip straight to `docs/ADDING_A_GAME.md`. Steps 1–2 are the same shape
(your decomp + your psxrecomp-based recomp + your own legal disc/BIOS), but
everything from step 3 on is your own `games/<name>/config.toml`.
