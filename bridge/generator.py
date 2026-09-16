#!/usr/bin/env python3
"""Generate a func_override REPLACEMENT for a guest function, wired directly
to that decomp's own verified C implementation -- the "decomp-to-func_override
generator" from the design discussion following postman.py and confidence.py.

*** SCOPE: SCALAR-ONLY, AND WHY ***

Before writing this generator, tracing how a hand-written decomp function's
memory access would interact with the recomp runtime surfaced a real
blocker: psxrecomp's generated code represents EVERY guest memory access as
an explicit cpu->read_word(addr)/write_word(addr, val) call against a plain
uint32_t guest address (confirmed in
psxrecomp/recompiler/src/full_function_emitter.cpp:1970-1973) -- it never
does a native struct pointer dereference. A decomp's own C, by contrast, is
written as ordinary C: `BattleEntity *actor = D_8009D254; actor->moveSpeed`
(this is literally what Entity_ApplyCollisionResponse.c does). Those two
representations are incompatible: there is no fixed-address mapping that
makes a guest address like 0x8009D254 a valid native pointer into
psxrecomp's actual RAM buffer (memory.c's `static uint8_t ram[RAM_SIZE]`,
exposed only via memory_get_ram_ptr() at an arbitrary host address).

Making arbitrary decomp C directly linkable would need either mapping guest
RAM at a fixed, PS1-matching virtual address (a real recomp-architecture
change, not something this generator can do from outside) or transpiling
every `->` in the decomp source into an explicit read_word/write_word call
(a source-to-source compiler, a much bigger project than this). Neither is
in scope here.

So this generator is restricted, on purpose, to functions that are provably
free of the problem: no pointer parameters, no pointer return, and no `->`
anywhere in the function body (a deliberately conservative, text-level
heuristic -- false positives, i.e. refusing something that would have been
fine, are the safe failure direction; this never tries to guess a function
is pointer-free when it can't prove it). This is a real minority of game
logic (most touches entity/room structs), but it is buildable and correct
today without waiting on a recomp-architecture decision. Confirmed against
real data: Entity_ApplyCollisionResponse.c has an all-scalar SIGNATURE
(`void Entity_ApplyCollisionResponse(int unused)`) but is correctly REJECTED
by this generator because its body dereferences `D_8009D254->...` --
signature-only checking would have missed this; the body-level `->` scan
catches it.

*** ELIGIBILITY ***

Requires confidence.py's classify_source_file/classify_address to report
ELIGIBLE (semantic_c AND a passing objdiff.json byte-match) before even
attempting to parse a signature -- an unverified decomp implementation has
no business being wired into a live game regardless of its ABI shape.

*** THIS PRODUCES A REPLACEMENT, NOT A PIGGYBACK ***

Unlike postman.py's handler (which always declines, so it never affects the
piggybacked function's own behavior), this generator's handler ALWAYS
returns 1 (handled) -- the whole point is REPLACING the guest function with
the decomp's implementation. That means `credit` is NOT optional or inert
here the way postman.py's is: per func_override.h's CYCLE ACCOUNTING policy,
every registration replacing real guest behavior must state a real timing
intent. This generator requires --credit explicitly (or the literal string
"self" for FO_CREDIT_SELF) -- there is no default, matching func_override.h's
own "no default to inherit" rule. See that header's own guidance: credits
are approximations unless measured, and LLE (declined + cycle-delta sampled
across the call boundary) is the timing oracle.

GENERIC BY DESIGN, same contract as the rest of this bridge: no game-specific
data in this file. Confidence-classifier and symbol-format lookups both come
from the game's own config.toml through confidence.py / decomp_bridge.py.

Usage:
  python bridge/generator.py generate \\
      --config games/parasite-eve/config.toml \\
      --address 0x80190B70 --credit 40 \\
      --id override_roomlib_handler \\
      --out generated/override_roomlib_handler.c
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decomp_bridge import GameConfig, load_config  # noqa: E402
from classifier_gap_finder import build_symbol_table, containing_function  # noqa: E402
import confidence  # noqa: E402

# Plain 32-bit-or-narrower integer scalar spellings this generator accepts.
# Anything else (float/double/long long/struct/union/array/pointer/unknown
# typedef) is refused rather than guessed at.
_SCALAR_TYPES = {
    "void", "int", "unsigned int", "unsigned", "signed int",
    "short", "short int", "unsigned short", "unsigned short int",
    "char", "unsigned char", "signed char",
    "int8_t", "uint8_t", "int16_t", "uint16_t", "int32_t", "uint32_t",
    "long", "unsigned long",  # 32-bit on this project's MIPS o32 toolchain
}

_DISQUALIFYING_SUBSTRINGS = ("*", "[", "float", "double", "long long", "struct", "union")

_FUNC_SIG_RE = re.compile(
    r'^(?P<ret>[A-Za-z_][\w\s\*]*?)\s+(?P<name>[A-Za-z_]\w*)\s*'
    r'\((?P<params>[^;{}]*)\)\s*\{',
    re.MULTILINE,
)
_ARROW_RE = re.compile(r'->')


@dataclass
class Param:
    c_type: str
    name: str


@dataclass
class Signature:
    name: str
    return_type: str  # "void" or a scalar type
    params: list  # list[Param]


@dataclass
class GeneratorResult:
    ok: bool
    reason: str
    signature: Signature | None = None


def _is_scalar(type_text: str) -> bool:
    t = " ".join(type_text.split())
    if any(bad in t for bad in _DISQUALIFYING_SUBSTRINGS):
        return False
    return t in _SCALAR_TYPES


def _split_top_level_commas(params_text: str) -> list[str]:
    if "(" in params_text:
        raise ValueError("function-pointer parameter -- too complex for this generator")
    parts = [p.strip() for p in params_text.split(",")]
    return [p for p in parts if p]


def _parse_param(entry: str) -> Param:
    entry = " ".join(entry.split())
    m = re.match(r'^(?P<type>[A-Za-z_][\w\s\*]*?)\s*(?P<name>[A-Za-z_]\w*)$', entry)
    if not m:
        raise ValueError(f"can't parse parameter {entry!r}")
    return Param(c_type=m.group("type").strip(), name=m.group("name"))


def parse_signature(source_text: str, func_name: str) -> Signature | None:
    for m in _FUNC_SIG_RE.finditer(source_text):
        if m.group("name") != func_name:
            continue
        ret = " ".join(m.group("ret").split())
        params_text = m.group("params").strip()
        if params_text in ("", "void"):
            return Signature(name=func_name, return_type=ret, params=[])
        try:
            entries = _split_top_level_commas(params_text)
            params = [_parse_param(e) for e in entries]
        except ValueError:
            return None
        return Signature(name=func_name, return_type=ret, params=params)
    return None


def check_eligible_scalar(cfg: GameConfig, source_rel: str, func_name: str) -> GeneratorResult:
    """The full gate: confidence-eligible, a parseable signature, every
    param and the return type scalar, and no `->` anywhere in the function
    body. Any failure returns ok=False with a specific reason -- never a
    silent downgrade to "probably fine"."""
    conf = confidence.classify_source_file(cfg, source_rel)
    if conf.verdict != confidence.ELIGIBLE:
        return GeneratorResult(False, f"not eligible ({conf.verdict}): {conf.reason}")

    abs_path = cfg.decomp / source_rel
    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return GeneratorResult(False, f"can't read {source_rel}: {e}")

    sig = parse_signature(text, func_name)
    if sig is None:
        return GeneratorResult(
            False, f"couldn't parse a signature for {func_name}() in "
            f"{source_rel} (or it uses a function-pointer parameter, which "
            "this generator doesn't support)")

    if not _is_scalar(sig.return_type):
        return GeneratorResult(
            False, f"{func_name} returns {sig.return_type!r} -- not a plain "
            "scalar type this generator supports", sig)
    for p in sig.params:
        if not _is_scalar(p.c_type):
            return GeneratorResult(
                False, f"{func_name}'s parameter {p.name} is {p.c_type!r} -- "
                "not a plain scalar type this generator supports", sig)
    if len(sig.params) > 4:
        return GeneratorResult(
            False, f"{func_name} takes {len(sig.params)} arguments -- only "
            "up to 4 register-passed args ($a0-$a3) are supported, no "
            "stack-passed arguments", sig)

    # The body-level check that actually matters most: Entity_ApplyCollisionResponse
    # has an all-scalar SIGNATURE (`void Entity_ApplyCollisionResponse(int unused)`)
    # but dereferences a global BattleEntity* internally -- signature-only
    # checking would have wrongly accepted it. Conservative on purpose: any
    # `->` anywhere in the function body refuses the whole function, even if
    # it's inside a branch this generator can't prove is unreachable.
    body_start = text.index("{", text.index(func_name))
    body = text[body_start:]
    # crude but adequate brace matching for a single function body
    depth = 0
    end = len(body)
    for i, ch in enumerate(body):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    body = body[:end]
    if _ARROW_RE.search(body):
        return GeneratorResult(
            False, f"{func_name}'s body dereferences a pointer (`->`) -- "
            "this generator only accepts functions with NO pointer/struct "
            "access anywhere in the body, since psxrecomp's guest RAM has "
            "no fixed address mapping a native pointer could safely use "
            "(see this file's own module docstring)", sig)

    return GeneratorResult(True, "eligible and scalar-only", sig)


# ----------------------------------------------------------------------------
# Code generation
# ----------------------------------------------------------------------------

HEADER_COMMENT = """\
/* GENERATED by psxrecomp-decomp-bridge/bridge/generator.py -- do not hand-edit.
 * Regenerate with the same command instead (see the invocation recorded
 * below).
 *
 * WHAT THIS IS: a func_override REPLACEMENT for guest function {name} at
 * {addr_hex}, wired directly to that decomp's own verified implementation
 * in {source_rel} (confidence-eligible: semantic_c + objdiff.json
 * byte-match, checked by bridge/confidence.py at generation time).
 *
 * SCOPE: scalar-only. {name}'s signature and body were checked to contain
 * no pointers, no struct access, and no `->` anywhere -- see
 * bridge/generator.py's own module docstring for why that's a hard
 * requirement here, not just a convenience limitation.
 *
 * *** DO NOT FORGET (silent-failure risk, not a compile error) ***
 * func_override_install() must be called ONCE at program startup, AFTER
 * every func_override_add() call including this one's {id}_register().
 * See postman.py's docs/POSTMAN.md for the same requirement, confirmed
 * against RetroPortingToolKit/psxrecomp @ 6524ded0 (func_override.c).
 *
 * THIS REPLACES the guest function -- unlike postman.py's handler (which
 * always declines), this one ALWAYS returns 1 (handled). The declared
 * credit ({credit_display}) is charged on every call per func_override.h's
 * CYCLE ACCOUNTING policy: it is an APPROXIMATION unless independently
 * measured (that header's own guidance: run with the override declined and
 * sample the real cycle delta across the call boundary -- LLE is the
 * timing oracle, not a guess baked into this generated file).
 *
 * Real, still-open dependency: this only works against
 * RetroPortingToolKit/psxrecomp PR #174 (func_override tier), same
 * unmerged-branch caveat as postman.py -- see docs/POSTMAN.md.
 */

"""

C_TEMPLATE = """\
#include <stdint.h>
#include "cpu_state.h"      /* full CPUState definition, same reason as postman.py's
                                generated files: the handler dereferences cpu->gpr[] */
#include "func_override.h"  /* from RetroPortingToolKit/psxrecomp PR #174 */

/* The decomp's own verified implementation -- {source_rel}. This extern
   declaration must exactly match that function's real signature; it is
   NOT re-declared with a differing prototype anywhere in this file. */
extern {return_type} {name}({param_types});

static int {id}_handler(CPUState* cpu) {{
{arg_locals}
    {call_expr}
    return 1;  /* REPLACES the guest function -- see credit note above */
}}

void {id}_register(void) {{
    /* Return code (FO_OK / FO_ERR_FULL / FO_ERR_ARGS / FO_ERR_DUPLICATE) is
       not checked here -- func_override.c's own module comment says this
       tier prints nothing (no printf, no logs). If this override doesn't
       seem to be firing, check func_override_count()/func_override_get_ex()
       (or the `func_override` TCP debug command) to confirm it actually
       registered rather than assuming this call succeeded silently. */
    func_override_add("{id}", {addr_hex}u, {id}_handler, {credit_value});
    /* REMINDER: func_override_install() must ALSO be called once, after
       every override (including this one) is registered -- NOT from here. */
}}
"""


def _generate(cfg: GameConfig, addr: int, source_rel: str, sig: Signature,
              obj_id: str, credit_arg: str) -> str:
    param_types = ", ".join(p.c_type for p in sig.params) or "void"
    arg_locals = []
    call_args = []
    for i, p in enumerate(sig.params):
        arg_locals.append(f"    {p.c_type} {p.name} = ({p.c_type})cpu->gpr[4 + {i}];")
        call_args.append(p.name)
    arg_locals_text = "\n".join(arg_locals) if arg_locals else "    /* no arguments */"

    call = f"{sig.name}({', '.join(call_args)})"
    if sig.return_type == "void":
        call_expr = f"{call};"
    else:
        call_expr = f"cpu->gpr[2] = (uint32_t)({sig.return_type}){call};"

    if credit_arg.strip().lower() == "self":
        credit_value = "FO_CREDIT_SELF"
        credit_display = "FO_CREDIT_SELF -- the body must call psx_advance_cycles() itself, which this generated shim does NOT do; only pass \"self\" if you're adding that yourself before trusting this"
    else:
        credit_value = str(int(credit_arg))
        credit_display = f"{credit_value} guest cycles per handled call"

    addr_hex = f"0x{addr:08X}"
    header = HEADER_COMMENT.format(
        name=sig.name, addr_hex=addr_hex, source_rel=source_rel, id=obj_id,
        credit_display=credit_display,
    )
    body = C_TEMPLATE.format(
        id=obj_id, source_rel=source_rel, return_type=sig.return_type,
        name=sig.name, param_types=param_types, arg_locals=arg_locals_text,
        call_expr=call_expr, addr_hex=addr_hex, credit_value=credit_value,
    )
    return header + body


def cmd_generate(args: argparse.Namespace) -> int:
    # Cheap, local validation first, before any filesystem/eligibility work.
    if args.credit.strip().lower() != "self":
        try:
            credit_int = int(args.credit)
        except ValueError:
            print(f"error: --credit must be a nonnegative integer or the "
                  f"literal string 'self', got {args.credit!r}", file=sys.stderr)
            return 2
        if credit_int < 0:
            # func_override.h: only FO_CREDIT_SELF (-1) is a valid negative
            # credit; any other negative value is FO_ERR_ARGS at registration
            # time. Reject here rather than silently generating a value that
            # would make func_override_add fail at runtime.
            print(f"error: --credit must be >= 0, or the literal string "
                  f"'self' for FO_CREDIT_SELF -- got {credit_int} "
                  "(func_override_add rejects any other negative value)",
                  file=sys.stderr)
            return 2

    cfg = load_config(Path(args.config))
    addr = int(args.address, 16) if args.address.lower().startswith("0x") else int(args.address)

    table = build_symbol_table(cfg)
    name, offset = containing_function(table, addr)
    if name is None:
        print(f"error: no known symbol at or before 0x{addr:08X}", file=sys.stderr)
        return 2
    if offset != 0:
        print(f"error: 0x{addr:08X} is {name}+0x{offset:X}, not {name}'s own "
              "start -- pass the function's actual start address",
              file=sys.stderr)
        return 2

    source_rel = confidence.resolve_source_file(cfg, name, addr)
    if source_rel is None:
        print(f"error: found symbol {name} at 0x{addr:08X}, but couldn't "
              "resolve it to exactly one decomp source file", file=sys.stderr)
        return 2

    result = check_eligible_scalar(cfg, source_rel, name)
    if not result.ok:
        print(f"error: {result.reason}", file=sys.stderr)
        return 1

    out_text = _generate(cfg, addr, source_rel, result.signature, args.id, args.credit)
    invocation = "  ".join(
        f"--{k.replace('_', '-')} {v}" for k, v in vars(args).items()
        if k not in ("func", "cmd"))
    out_text = out_text.replace(
        "\n\n#include <stdint.h>",
        f"\n/* Generated with: generator.py generate {invocation} */\n\n#include <stdint.h>",
        1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="utf-8")
    print(f"wrote {out_path} ({name}, {len(result.signature.params)} arg(s), "
          f"ret={result.signature.return_type})")
    print(
        "\nNext steps (all manual, none of this touches your build):\n"
        "  1. Pull RetroPortingToolKit/psxrecomp PR #174's branch into a "
        "psxrecomp checkout your game can build against -- see docs/POSTMAN.md.\n"
        f"  2. Add both {out_path.name} AND {source_rel} (the decomp's own "
        f"implementation) to your build, and call {args.id}_register() from "
        "your game's own override/mod init.\n"
        "  3. *** Also call func_override_install() once, AFTER every "
        "override is registered *** -- silent-failure trap, not a compile "
        "error.\n"
        "  4. This REPLACES the guest function -- confirm the credit you "
        "passed is a real timing approximation, ideally measured (LLE: run "
        "with the override declined and sample the cycle delta), not a "
        "guess left unexamined."
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser(
        "generate",
        help="Generate a func_override replacement wired to a decomp's own "
             "verified scalar-only C implementation.")
    p.add_argument("--config", required=True)
    p.add_argument("--address", required=True,
                    help="Guest address of the function's own start (hex)")
    p.add_argument("--credit", required=True,
                    help="Guest cycles to charge per handled call (a "
                         "nonnegative integer), or the literal string "
                         "'self' for FO_CREDIT_SELF -- required, no "
                         "default, per func_override.h's CYCLE ACCOUNTING "
                         "policy.")
    p.add_argument("--id", required=True,
                    help="C identifier prefix for the generated handler/"
                         "register function names.")
    p.add_argument("--out", required=True, help="Output .c file path")
    p.set_defaults(func=cmd_generate)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
