#!/usr/bin/env python3
"""Batch-triage a candidate address list through confidence.py and
generator.py's eligibility checks -- closes the loop between the pieces
built this session: classifier_gap_finder.py produces "here are N addresses
the overlay classifier is stuck on"; this tool turns that into "here's which
of those have a decomp implementation trustworthy enough to use
(confidence.py) and which of THOSE are actually generatable right now
(generator.py's scalar-only scope), so nothing further needs 640 individual
manual checks.

INPUT: any text file containing 0xXXXXXXXX-shaped addresses -- deliberately
permissive so you can feed this classifier_gap_finder.py's OWN saved output
verbatim, in any of its formats (the markdown table, the --force-interior
argument list, or the PowerShell array literal), without reformatting
anything. Addresses are extracted by regex, deduplicated, and sorted; text
around them is ignored.

For each address:
  1. Resolve to its containing decomp function and source file (reusing
     classifier_gap_finder.py's symbol table and confidence.py's
     resolve_source_file) -- an address that isn't a function's own start,
     or doesn't resolve to exactly one source file, is reported UNKNOWN
     with the specific reason, never silently skipped.
  2. Classify via confidence.py: ELIGIBLE / INELIGIBLE / UNKNOWN.
  3. Only for ELIGIBLE results, additionally check generator.py's
     scalar-only eligibility -- an address can be a verified, trustworthy
     decomp implementation (confidence-eligible) and still not be
     generatable today (pointer/struct access in the body), and the report
     says which is which rather than collapsing the two questions.

GENERIC BY DESIGN, same contract as the rest of this bridge: no game-specific
data here, everything comes from the game's own config.toml through
confidence.py / decomp_bridge.py / generator.py.

Usage:
  python bridge/triage.py run \\
      --config games/parasite-eve/config.toml \\
      --addresses-file saved_annotate_output.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decomp_bridge import GameConfig, load_config  # noqa: E402
from classifier_gap_finder import build_symbol_table, containing_function  # noqa: E402
import confidence  # noqa: E402
import generator  # noqa: E402

_ADDR_RE = re.compile(r'0x([0-9A-Fa-f]{8})')


def extract_addresses(text: str) -> list[int]:
    seen: set[int] = set()
    out: list[int] = []
    for m in _ADDR_RE.finditer(text):
        addr = int(m.group(1), 16)
        if addr not in seen:
            seen.add(addr)
            out.append(addr)
    return sorted(out)


def triage_one(cfg: GameConfig, table, addr: int) -> dict:
    name, offset = containing_function(table, addr)
    if name is None:
        return {
            "addr": addr, "name": None, "offset": None, "source": None,
            "verdict": confidence.UNKNOWN,
            "reason": "no known symbol at or before this address",
            "generatable": False, "gen_reason": None,
        }
    if offset != 0:
        return {
            "addr": addr, "name": name, "offset": offset, "source": None,
            "verdict": confidence.UNKNOWN,
            "reason": f"{name}+0x{offset:X}, not the function's own start "
                      "-- classify the real start address instead",
            "generatable": False, "gen_reason": None,
        }

    source_rel = confidence.resolve_source_file(cfg, name, addr)
    if source_rel is None:
        return {
            "addr": addr, "name": name, "offset": 0, "source": None,
            "verdict": confidence.UNKNOWN,
            "reason": "couldn't resolve to exactly one decomp source file",
            "generatable": False, "gen_reason": None,
        }

    conf = confidence.classify_source_file(cfg, source_rel)
    row = {
        "addr": addr, "name": name, "offset": 0, "source": source_rel,
        "verdict": conf.verdict, "reason": conf.reason,
        "generatable": False, "gen_reason": None,
    }
    if conf.verdict == confidence.ELIGIBLE:
        gen = generator.check_eligible_scalar(cfg, source_rel, name)
        row["generatable"] = gen.ok
        row["gen_reason"] = gen.reason
    return row


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    try:
        text = Path(args.addresses_file).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"error: can't read {args.addresses_file}: {e}", file=sys.stderr)
        return 2

    addrs = extract_addresses(text)
    if not addrs:
        print(f"no 0xXXXXXXXX-shaped addresses found in {args.addresses_file}",
              file=sys.stderr)
        return 1

    table = build_symbol_table(cfg)
    rows = [triage_one(cfg, table, a) for a in addrs]

    n_eligible = sum(1 for r in rows if r["verdict"] == confidence.ELIGIBLE)
    n_ineligible = sum(1 for r in rows if r["verdict"] == confidence.INELIGIBLE)
    n_unknown = sum(1 for r in rows if r["verdict"] == confidence.UNKNOWN)
    n_generatable = sum(1 for r in rows if r["generatable"])
    n_blocked_on_objdiff = sum(
        1 for r in rows
        if r["verdict"] == confidence.UNKNOWN
        and r.get("reason") and "objdiff.json wasn't found" in r["reason"]
    )

    if args.filter != "all":
        wanted = {
            "eligible": confidence.ELIGIBLE,
            "ineligible": confidence.INELIGIBLE,
            "unknown": confidence.UNKNOWN,
        }
        if args.filter == "generatable":
            rows = [r for r in rows if r["generatable"]]
        else:
            rows = [r for r in rows if r["verdict"] == wanted[args.filter]]

    print(f"# Triage: {len(addrs)} candidate address(es)\n")
    print(f"{n_eligible} eligible ({n_generatable} of those also "
          f"generator-ready), {n_ineligible} ineligible, {n_unknown} unknown\n")
    if n_blocked_on_objdiff:
        print(f"**{n_blocked_on_objdiff} of the unknowns are semantic_c but "
              "blocked only on missing byte-match evidence** -- run "
              "`make objdiff-config` (after a build) in the decomp to "
              "unlock those.\n")

    if not rows:
        print(f"(no rows match --filter {args.filter})")
        return 0

    print("| Address | Function | +off | Source | Confidence | Generatable |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        addr_s = f"0x{r['addr']:08X}"
        name_s = r["name"] or "?"
        off_s = "-" if r["name"] is None else f"0x{r['offset']:X}"
        src_s = r["source"] or "-"
        if r["verdict"] != confidence.ELIGIBLE:
            gen_s = "-"
        else:
            gen_s = "yes" if r["generatable"] else "no"
        print(f"| {addr_s} | {name_s} | {off_s} | {src_s} | {r['verdict']} | {gen_s} |")

    if args.verbose:
        print("\n## Details\n")
        for r in rows:
            print(f"- 0x{r['addr']:08X} ({r['name'] or '?'}): {r['reason']}")
            if r["verdict"] == confidence.ELIGIBLE and not r["generatable"]:
                print(f"  - not generator-ready: {r['gen_reason']}")

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser(
        "run",
        help="Triage every address found in a text file through "
             "confidence.py and generator.py's eligibility checks.")
    p.add_argument("--config", required=True)
    p.add_argument("--addresses-file", required=True,
                    help="Any text file containing 0xXXXXXXXX-shaped "
                         "addresses -- classifier_gap_finder.py's saved "
                         "output works as-is, in any of its formats.")
    p.add_argument("--filter", choices=["all", "eligible", "ineligible",
                                          "unknown", "generatable"],
                    default="all", help="Only show rows matching this "
                         "verdict (default: all)")
    p.add_argument("--verbose", action="store_true",
                    help="Also print the specific reason for every row, "
                         "and why an eligible row isn't generator-ready "
                         "when it isn't.")
    p.set_defaults(func=cmd_run)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
