# `bridge/save_survey.py`: batch classifier-gap survey across memory-card saves

Automates the manual pipeline used throughout the 2026-09-16 session
(swap `card1.mcd`, launch, capture a window with `stall_report.py`, run
`compile_overlays.py --check`, annotate with `classifier_gap_finder.py`)
across every save file in a folder, instead of doing it by hand once per
save. Built after that session found a real result (the GiantWorms boss
fight) from exactly one manually-tested save out of 26 downloaded ones —
see `findings/roomlib-giantworms-boundary-extension-and-inventory-gap-2026-09-16.md`.

## Usage

```
python bridge/save_survey.py --config games/parasite-eve/config.toml \
    --saves-dir "D:\Recomp Games\Parasite Eve Project\pe saves" \
    --out-dir findings/save-survey-2026-09-16 \
    --build-dir build-dbg --debug-port 4370 --secs 60
```

Useful flags: `--only <substring>` to filter to matching save filenames,
`--limit N` to cap how many saves run, `--boot-timeout` if a heavier
`-ForceInterior` list needs longer than 120s to autocompile before the
debug port comes up.

## What it needs

- A `build-dbg`-style build with `PSX_DEBUG_TOOLS=ON` (the debug server
  `stall_report.py` connects to doesn't exist in a release build).
- `--saves-dir` full of `*.zip` files, each containing one `*.mcr`/`*.mcd`
  (a plain 128KB raw PS1 memory-card image — ePSXe's `.mcr` extension and
  this project's `.mcd` are the same format).
- `build/play.ps1` (this repo's existing generic launcher, resolved
  relative to this script's own location) and the target's own
  `settings.toml` for the configured `card1` path.

## What it does per save

1. Unzip, copy the `.mcr` over the build's `card1.mcd`.
2. Launch `play.ps1` with the debug port enabled, wait for it to come up.
3. Capture a fixed window with `stall_report.py run --secs N`.
4. Run `compile_overlays.py --check` against that build dir's
   `overlay_captures.json`, then `classifier_gap_finder.py annotate`.
5. Kill the game, store everything under `--out-dir/<save-name>/`.

The original `card1.mcd`/`card2.mcd` are backed up once at the very start
of the whole run (not per-save) and restored at the end.

## The one non-obvious pitfall this tool works around

`overlay_captures.json` is **not** a per-run snapshot. The runtime's own
`overlay_capture.c` keeps an immutable, additive vault
(`overlay_captures.json.d/<content-hash>.json`) that `compile_overlays.py
--check` unions in full every time, by design — "different byte variants
at the same load address ... survive future captures, rebuilds, and
regenerations," per that file's own comment. Naively reading the
"excluded addresses" count out of one save's `--check` run actually
reports a number cumulative across **every** capture this build directory
has ever seen, not something specific to that save — confirmed directly
during this tool's own validation (a Zoo-save test reported the exact
same 271-address count as a completely unrelated GiantWorms capture from
earlier the same day, because the vault simply hadn't been touched by the
Zoo run at all).

The fix: the script snapshots the vault's file set before launching each
save and diffs it after that save's capture window closes. `SUMMARY.md`
ranks saves by `new_variants_this_save` (genuinely per-save) and
`interp_share` (genuinely windowed, from `stall_report.py`'s own
before/after delta), and reports the cumulative excluded-address count
separately, clearly labeled as cumulative rather than per-save.

## What it does NOT do

No synthetic input is sent. This project's own debug-server input
injection is confirmed to only reach menu navigation, not field movement
(`findings/pe-mod-movement-verification-2026-09-13.md`) — not a reliable
way to script "walk to X" regardless of how it's driven. Whatever a save
boots into, or is left sitting at, is exactly what gets captured. A save
that lands mid-battle or mid-cutscene will show activity for free (as
GiantWorms did); a save that lands in a quiet field state may show
nothing until a human actually plays it.

## Reading the output

`SUMMARY.md` at the top of `--out-dir` ranks every save. Per-save folders
each have `play.log` (the raw launch log), `stall_report.txt`/`.json`,
`check.txt` (the raw `--check` transcript), `annotate.md` (resolved
addresses + function names), and `new_vault_variants.txt` when that save
added anything new to the vault. Treat a high `new_variants_this_save` or
elevated `interp_share` as a lead worth a closer manual look (the way
GiantWorms was), not a finished finding — everything downstream of this
tool (writing up a `findings/*.md`, deciding whether to add addresses to
`play.ps1`) is still a human-in-the-loop step, per this project's own
"not yet live-verified until confirmed" discipline.
