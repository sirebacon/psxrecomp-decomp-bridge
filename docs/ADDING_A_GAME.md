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

## Adding a confidence classifier (contract for the planned func_override generator)

**Not built yet** — this section documents the extension point up front so
the tool inherits genericity from day one instead of needing a retrofit,
the same way `SYMBOL_FORMATS` did for `decomp_bridge.py` itself.

The planned decomp-to-`func_override` generator (see
`findings/c4-wave5-fps-regression-2026-09-15.md` and the design discussion
that followed it) needs to know, per candidate function, whether a decomp's
own C implementation is trustworthy enough to wire into a live game as a
native replacement. That answer is decomp-specific: Parasite Eve's decomp
tracks it via `tools/scripts/source_quality.py`'s `classify()` (per-file
`semantic_c` / `asm_constrained` / `text_data` / `original_asm`) plus
separate SHA-1/`make check` byte-verification — but a different decomp
bridged in later may use a different convention, or none at all. The
generator must never assume PE's semantics apply to a decomp that hasn't
declared them.

Same pattern as symbol formats: a registry the generator consults, keyed by
a new optional `[decomp] confidence_classifier` config value, e.g.

```toml
[decomp]
format = "splat"
confidence_classifier = "source_quality"   # this decomp's own convention
```

```python
def _classify_via_source_quality(cfg: GameConfig, func_addr: int) -> Confidence:
    ...  # PE-specific adapter: locate the function's source file via the
         # existing symbol table, shell out to or import that decomp's own
         # source_quality.py, require semantic_c AND a passing byte-match
         # check before returning "eligible"

CONFIDENCE_CLASSIFIERS = {
    "source_quality": _classify_via_source_quality,
}
```

A decomp whose config doesn't set `confidence_classifier` must make the
generator **refuse to run for that game**, with a clear message, rather than
silently falling back to some generic heuristic — a tool that writes native
code into a running game should fail closed on missing eligibility
information, not guess. `_classify_via_source_quality` (or any other
adapter) is the only place PE-specific (or any other decomp-specific)
confidence semantics may live; `bridge/*.py`'s shared code stays as
format-agnostic about confidence as it already is about symbol formats.
