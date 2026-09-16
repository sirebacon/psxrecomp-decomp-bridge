#!/usr/bin/env python3
"""Find and name psxrecomp overlay-classifier gaps, using a game's own decomp.

Born out of the Parasite Eve RoomLib jump-table investigation
(psxrecomp-decomp-bridge/findings/roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md
and roomlib-interior-classification-ai-brief.md): compile_overlays.py's
classifier can permanently strand genuinely-executed addresses as
OBSERVED_PC_ONLY (never compiled, forever interpreted) when they're reached
through a mechanism it doesn't currently recognize as a valid function entry
-- a runtime function-pointer callback, in Parasite Eve's case. Finding and
triaging every instance of that by hand, one bare hex address at a time, is
slow and error-prone. This tool automates the two things this project did by
hand across several nights:

  1. `annotate`: take a compile_overlays.py --check transcript (run against
     real overlay_captures.json) and turn its bare OBSERVED_PC_ONLY hex
     addresses into a readable report -- which decomp-known function each
     one actually falls inside, and by how much offset -- plus a ready
     --force-interior argument list a game's own launch script can use.

  2. `scan-pattern`: given a source pattern known to cause this class of gap
     in ONE confirmed instance (e.g. a macro name), search the ENTIRE
     decomp for every other place using the same pattern, and (given the
     confirmed instance's own known-bad interior offsets) compute a
     candidate address list for all of them -- turning "we found one" into
     "here is everywhere this shape of bug can hide", without needing
     anyone to actually play through every one of those areas first.

GENERIC BY DESIGN: this reuses decomp_bridge.py's own GameConfig / symbol-
format loading (the same games/<name>/config.toml every bridge-managed
title already has), so it works for any decomp this bridge already
supports -- not just Parasite Eve -- and inherits new decomp formats
automatically as they're added to decomp_bridge.py's SYMBOL_FORMATS.

Neither subcommand touches the live game or the recompiler tools directly --
both are pure, offline, read-only analysis over files you already have
(a saved --check transcript, and the decomp source tree), so there is
nothing here that can misclassify code as data or apply an unverified fix
by itself. The output is a candidate list for a human to review and verify
against real capture data before trusting it -- see the "Explicit warning"
section of roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md for why
that verification step matters and shouldn't be skipped.

Usage:
  # 1. Save a compile_overlays.py --check transcript against your real
  #    overlay_captures.json (see that tool's own --help), then:
  python classifier_gap_finder.py annotate \\
      --config games/parasite-eve/config.toml \\
      --check-log path/to/saved_check_output.txt

  # 2. Given one CONFIRMED bad dispatcher's own interior offsets (found by
  #    hand once, e.g. via method 1 above plus a live capture), search the
  #    whole decomp for every other function built from the same macro and
  #    compute the same offsets against each:
  python classifier_gap_finder.py scan-pattern \\
      --config games/parasite-eve/config.toml \\
      --pattern "ROOMLIB_STATE_DISPATCH_VARIANT2" \\
      --known-offsets 0x60,0x64,0x68,0x6C,0x70,0x74,0x78,0x7C,0x80,0x84
"""

from __future__ import annotations

import argparse
import bisect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decomp_bridge import GameConfig, load_config, parse_symbol_file  # noqa: E402


# ----------------------------------------------------------------------------
# Symbol table: every known FUNCTION symbol across main EXE + every captured
# overlay this game's config already knows about (same seed_symbol_globs
# decomp_bridge.py itself feeds the recompiler with), sorted by address so we
# can answer "which function contains this address" by nearest-preceding-
# symbol lookup. This is a heuristic, not a guarantee -- a decomp's symbol
# files generally don't carry explicit function sizes, only start addresses,
# so a containing-function answer is "the nearest known function at or before
# this address", which can be wrong for something inside a much later
# function's actual body if a function in between was never named. Good
# enough for turning a bare hex address into readable context for a human to
# verify, not a substitute for actually checking.
# ----------------------------------------------------------------------------

def build_symbol_table(cfg: GameConfig) -> list[tuple[int, str]]:
    entries: dict[int, str] = {}
    for path in cfg.resolve_seed_files():
        for name, addr, is_func in parse_symbol_file(cfg, path):
            if is_func:
                entries[addr] = name
    return sorted(entries.items())


def build_name_table(cfg: GameConfig) -> dict[str, int]:
    """Reverse of build_symbol_table: function name -> address, for
    scan-pattern's filename-to-address resolution."""
    out: dict[str, int] = {}
    for path in cfg.resolve_seed_files():
        for name, addr, is_func in parse_symbol_file(cfg, path):
            if is_func:
                out[name] = addr
    return out


def containing_function(table: list[tuple[int, str]], addr: int) -> tuple[str | None, int | None]:
    addrs = [a for a, _ in table]
    i = bisect.bisect_right(addrs, addr) - 1
    if i < 0:
        return None, None
    faddr, name = table[i]
    return name, addr - faddr


# ----------------------------------------------------------------------------
# annotate: parse a saved compile_overlays.py --check transcript
# ----------------------------------------------------------------------------

# Matches the two real line shapes this project's transcripts have shown all
# along, e.g.:
#   8018F958  DISPATCH_ENTRY
#   8018F77C  excluded: OBSERVED_PC_ONLY; isolated fragment demand retained
#   8018F984  excluded: BRANCH_TARGET_ONLY
_EXCLUDED_RE = re.compile(
    r"^\s*([0-9A-Fa-f]{8})\s+excluded:\s*([A-Z_]+)\s*(.*)$")
_INCLUDED_RE = re.compile(r"^\s*([0-9A-Fa-f]{8})\s+([A-Z_]+)\s*$")


def parse_check_log(path: Path):
    """Yield (addr, reason, retained) for every classified-address line."""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _EXCLUDED_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            reason = m.group(2)
            retained = "retained" in m.group(3)
            yield addr, reason, retained
            continue
        m = _INCLUDED_RE.match(line)
        if m:
            yield int(m.group(1), 16), m.group(2), True


def cmd_annotate(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    table = build_symbol_table(cfg)
    if not table:
        print("warning: no function symbols loaded from this game's "
              "seed_symbol_globs -- check games/<name>/config.toml "
              "[decomp] settings", file=sys.stderr)

    stuck: list[tuple[int, str | None, int | None]] = []
    seen: set[int] = set()
    for addr, reason, retained in parse_check_log(Path(args.check_log)):
        if reason != "OBSERVED_PC_ONLY" or retained or addr in seen:
            continue
        seen.add(addr)
        name, offset = containing_function(table, addr)
        stuck.append((addr, name, offset))
    stuck.sort()

    if not stuck:
        print("No un-recovered OBSERVED_PC_ONLY addresses found in this "
              "transcript -- either the classifier caught everything, or "
              "check-log doesn't have the shape this tool expects "
              "(see the module docstring for the exact line formats matched).")
        return 0

    print(f"# {len(stuck)} un-recovered OBSERVED_PC_ONLY address(es)\n")
    print("Each of these was genuinely observed executing but never "
          "promoted to a compiled function -- permanently interpreted, "
          "every time it's reached, until worked around.\n")
    print("| Address | Nearest known function | +offset |")
    print("|---|---|---|")
    for addr, name, offset in stuck:
        name_s = name or "(no symbol found at or before this address)"
        offset_s = f"0x{offset:X}" if offset is not None else "?"
        print(f"| 0x{addr:08X} | {name_s} | {offset_s} |")

    print(f"\n# Ready-to-paste --force-interior list ({len(stuck)} addresses)\n")
    print(" ".join(f"--force-interior 0x{addr:08X}" for addr, _, _ in stuck))
    print(f"\n# Or as a PowerShell array literal for a launch script default:\n")
    print("@(" + ",".join(f"'0x{addr:08X}'" for addr, _, _ in stuck) + ")")
    print(
        "\n**Verify before trusting**: this list is exactly what your "
        "capture happened to observe -- not a completeness guarantee for "
        "every code path in the game. Re-run a longer/different session "
        "and re-annotate to catch anything this one missed, and confirm "
        "each address actually compiles clean (`--check`) before adding it "
        "to a real launch config.")
    return 0


# ----------------------------------------------------------------------------
# scan-pattern: find every other place a known-bad pattern is used
# ----------------------------------------------------------------------------

def cmd_scan_pattern(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    name_table = build_name_table(cfg)
    pattern = re.compile(args.pattern)
    # Two real decomp filename conventions cover an address-bearing file:
    # the plain auto-generated `func_XXXXXXXX.c`, and a later, more
    # descriptive rename that still keeps the address as a trailing suffix
    # (`RoomLib_StateDispatchVariant2_XXXXXXXX.c`). Match either by looking
    # for 8 trailing hex digits, not just the bare `func_` prefix.
    addr_suffix_re = re.compile(r"_([0-9A-Fa-f]{8})$")

    matches: list[tuple[int, Path]] = []
    unresolved: list[Path] = []
    for c_file in sorted(cfg.decomp.rglob(args.file_glob)):
        try:
            text = c_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not pattern.search(text):
            continue
        m = addr_suffix_re.search(c_file.stem)
        if m:
            addr = int(m.group(1), 16)
        else:
            addr = name_table.get(c_file.stem)
        if addr is None:
            unresolved.append(c_file)
            continue
        matches.append((addr, c_file))
    matches.sort()

    print(f"# Pattern {args.pattern!r} found in {len(matches) + len(unresolved)} "
          f"file(s), address-resolved for {len(matches)}\n")
    if unresolved:
        print(f"**{len(unresolved)} match(es) could not be address-resolved** "
              "(filename isn't `func_XXXXXXXX` and doesn't match any known "
              "function symbol name) -- listed below for manual lookup, not "
              "included in the candidate list:")
        for f in unresolved:
            print(f"  - {f.relative_to(cfg.decomp)}")
        print()

    print("| Address | Source file |")
    print("|---|---|")
    for addr, f in matches:
        print(f"| 0x{addr:08X} | {f.relative_to(cfg.decomp)} |")

    if args.known_offsets:
        offsets = [int(x, 0) for x in args.known_offsets.split(",")]
        print(f"\n# Computed candidates: {len(matches)} base address(es) x "
              f"{len(offsets)} known offset(s) = {len(matches) * len(offsets)} "
              "candidate address(es)\n")
        print(
            "**This is a prediction, not a verification.** It assumes every "
            "matched function shares the exact same internal layout as the "
            "one instance the offsets were confirmed against -- true only if "
            "the compiler generated byte-identical structure at each site "
            "(check a couple by comparing actual function sizes/offsets in "
            "your decomp's own config data before trusting the rest, the "
            "way this project cross-checked room_m087 against scene_e27 "
            "before trusting its own 64-address list). Do not apply this "
            "list to a live launch config in one blanket step -- see "
            "roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md's "
            "'Explicit warning' section for why a large force-interior list "
            "added all at once can cause a compile-storm regression that's "
            "worse than the bug it's meant to fix. Roll out in small "
            "batches, verifying dirty-RAM behavior after each one.")
        candidates = sorted(
            base + off for base, _ in matches for off in offsets)
        print("\n" + " ".join(f"--force-interior 0x{a:08X}" for a in candidates))
    else:
        print(
            "\n(Pass --known-offsets 0x60,0x64,... -- the offsets confirmed "
            "bad at one already-verified instance -- to compute predicted "
            "interior addresses for every match above.)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser(
        "annotate",
        help="Turn a compile_overlays.py --check transcript's bare "
             "OBSERVED_PC_ONLY addresses into a named, actionable report.")
    p1.add_argument("--config", required=True,
                     help="games/<name>/config.toml for this title")
    p1.add_argument("--check-log", required=True,
                     help="Saved stdout from `compile_overlays.py --check ...`")
    p1.set_defaults(func=cmd_annotate)

    p2 = sub.add_parser(
        "scan-pattern",
        help="Find every decomp function using a known-bad source pattern, "
             "and (given known offsets from one confirmed instance) compute "
             "a candidate interior-address list for all of them.")
    p2.add_argument("--config", required=True,
                     help="games/<name>/config.toml for this title")
    p2.add_argument("--pattern", required=True,
                     help="Regex searched against each .c file's full text "
                          "(e.g. a macro name known to cause this class of "
                          "classifier gap)")
    p2.add_argument("--file-glob", default="**/*.c",
                     help="Glob (relative to [paths].decomp) restricting "
                          "which files are searched (default: **/*.c)")
    p2.add_argument("--known-offsets", default=None,
                     help="Comma-separated hex/decimal offsets from one "
                          "already-confirmed instance's own function start "
                          "(e.g. 0x60,0x64,0x68). Omit to just list matches "
                          "without computing candidates.")
    p2.set_defaults(func=cmd_scan_pattern)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
