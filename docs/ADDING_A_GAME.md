# Pointing the bridge at a different game

`bridge/decomp_bridge.py` has no Parasite Eve-specific logic in it. Everything
that differs between titles lives in one `games/<name>/config.toml`. To bridge
a different decomp + psxrecomp-based recomp pair:

1. Copy `games/parasite-eve/` to `games/<your-game>/` (config + a fresh,
   empty `symbols.manual.toml`).
2. Set `[paths] decomp` / `recomp` to the two checkouts (relative to the
   config file, or absolute) -- or leave them and pass `--decomp` /
   `--recomp` on the command line instead.
3. Point `[decomp] main_symbol_files` / `seed_symbol_globs` at your decomp's
   function symbol file(s). If your decomp uses the same
   `NAME = 0xADDR; // type:func` convention khasinski's PE decomp does
   (shared with the wider splat-family of decomp tooling), `format = "splat"`
   just works. If it doesn't, see **Adding a symbol format** below.
4. Set `[addresses] ram_lo` / `ram_hi` to the valid code window for that
   game's main RAM (check its `game.toml` `load_address` / `text_size`, or
   the recompiler's own seed-validation error if you get the window wrong).
5. Leave `[names]` alone unless the decomp names something that collides
   with `bridge/decomp_bridge.py`'s `DEFAULT_RESERVED` set or the game's own
   runtime symbols -- then add it to `reserved_extra`.
6. Run it:
   ```
   python bridge/decomp_bridge.py --config games/<your-game>/config.toml --no-pull
   ```

You do **not** need to touch `symbols.toml`'s schema, the seeds file format,
or `tools/sync_symbols.py` -- those are psxrecomp's own contract and are
identical for every title built on it (verified against
`psxrecomp/tools/new_project_layout/sync_symbols.py`).

## Where the seeds file goes

The engine reads the target's own `game.toml` `[recompiler].seeds` value and
writes there. If that game.toml doesn't declare one yet, it falls back to
`[paths] seeds_fallback` in your config. You shouldn't normally need to set
`seeds_fallback` to anything other than the default.

## Manual overrides

`games/<name>/symbols.manual.toml` (path set by `[paths] manual_toml`) always
wins over a decomp-derived entry at the same address or name. Same schema
regardless of game -- see `games/parasite-eve/symbols.manual.toml` for the
format.

## Adding a symbol format

If your decomp's symbol file isn't the `splat`-style
`NAME = 0xADDR; // type:func` convention, add a parser function with the
signature

```python
def _parse_my_format(path: Path) -> list[tuple[str, int, bool]]:
    ...  # (name, addr, is_func) per entry
```

and register it in `SYMBOL_FORMATS` in `bridge/decomp_bridge.py`. Everything
else in the engine (address filtering, manual-override merge, name-collision
handling, output rendering) is format-agnostic and needs no changes.

## Adding a confidence classifier

Built in `bridge/confidence.py` (see `docs/POSTMAN.md`'s neighbor doc — this
is the eligibility gate the planned decomp-to-`func_override` generator will
consult; the generator itself isn't built yet, but the registry it depends
on is real and tested, the same way `SYMBOL_FORMATS` predates every game
that now uses it).

The generator needs to know, per candidate function, whether a decomp's own
C implementation is trustworthy enough to wire into a live game as a native
replacement. That answer is decomp-specific: Parasite Eve's decomp tracks it
via `tools/scripts/source_quality.py`'s `classify()` (per-file `semantic_c`
/ `asm_constrained` / `text_data` / `original_asm`) plus that decomp's own
`objdiff.json` byte-match evidence (`make objdiff-config`) — but a different
decomp bridged in later may use a different convention, or none at all.
`bridge/confidence.py` never assumes PE's semantics apply to a decomp that
hasn't declared them.

Same pattern as symbol formats: a registry keyed by `[decomp]
confidence_classifier` in that game's config.toml, e.g.

```toml
[decomp]
format = "splat"
confidence_classifier = "source_quality"   # this decomp's own convention
```

```python
def _classify_via_source_quality(cfg: GameConfig, source_rel: str) -> ConfidenceResult:
    ...  # PE-specific adapter: import that decomp's own source_quality.py,
         # require classify() == "semantic_c" AND a passing objdiff.json
         # byte-match before returning ELIGIBLE

CONFIDENCE_CLASSIFIERS = {
    "source_quality": _classify_via_source_quality,
}
```

A decomp whose config doesn't set `confidence_classifier` gets `UNKNOWN`
back, not a guess — confirmed by `bridge/confidence.py`'s own test run (see
below), not just asserted here. `_classify_via_source_quality` (or any
other adapter) is the only place decomp-specific confidence semantics may
live; the rest of `bridge/confidence.py` stays as format-agnostic about
confidence as `decomp_bridge.py` already is about symbol formats.

One deliberate, documented divergence from Parasite Eve's own
progress-reporting policy: that project's `audit_report.py` credits both
`semantic_c` and `original_asm` as "done" for byte-match reporting (an
`original_asm` BIOS trampoline is as complete as it'll ever get). This
module's eligibility bar is narrower on purpose — `original_asm` means
"this is raw assembly, not C," so there's no typed C for a `func_override`
adapter to call no matter how well-verified the assembly is. Confirmed
against real files in this project's own decomp: `Entity_ApplyCollisionResponse.c`
and five other pin/barrier-bearing-but-ASM-free files all classify
`semantic_c`; `Sys_HleJumpA0.c` and `psyq/libc/strcmp.c` (real BIOS
trampolines) both classify `original_asm` — the two really are
distinguishable in this decomp, not a hypothetical distinction.

Try it:

```
python bridge/confidence.py check-file --config games/parasite-eve/config.toml \
    --source src/main/field/Entity_ApplyCollisionResponse.c
python bridge/confidence.py check-address --config games/parasite-eve/config.toml \
    --address 0x8001D170
```

Both currently report `unknown` against a fresh Parasite Eve checkout with
no `objdiff.json` generated yet — that's the fail-closed behavior working as
designed, not a bug: run `make objdiff-config` (after a build) in the decomp
to generate the byte-match evidence this module requires before it will
ever report `eligible`.
