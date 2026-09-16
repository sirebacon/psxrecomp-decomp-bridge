# `postman.py`: invoke a guest function on demand, without reaching it through live play

## The problem

Verifying a candidate address that [`classifier_gap_finder.py`](CLASSIFIER_GAP_FINDER.md)
finds normally means reaching that exact game state through live play, to
observe the real function actually execute. This project hit a hard limit on
that during its own RoomLib investigation: synthetic input could not reliably
drive field movement to reach several candidate states, and the project's
own 640-address candidate list was never fully verified against live capture
data for exactly that reason (see `findings/roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md`'s
"Explicit warning" section).

A **postman** sidesteps needing to organically reach a call site at all: it
generates a native override, piggybacked on any address the game *already*
dispatches constantly (a per-frame tick, a main-loop function — anything with
enough capture data to know it fires reliably), that polls a small
scratch-RAM protocol and, on request, calls the real target function on
demand with chosen argument values.

## What `postman.py` actually does

`python bridge/postman.py generate ...` writes ONE `.c` file implementing:

- a poll handler, hung off `--trigger-hook` (an existing, frequently-dispatched
  guest **code** address) via psxrecomp's `func_override` tier
- a tiny request/response protocol over three scratch guest **data**
  addresses you choose (`--trigger-addr` the request/ready flag,
  `--args-addr` the argument words, `--result-addr` the return value)
- the actual call, via `func_override_guest_call`, to `--target` — the
  function you actually want to invoke

```
python bridge/postman.py generate \
    --target 0x80190B70 --arg-types u32,u32,ptr,u32 \
    --trigger-hook 0x80046264 \
    --trigger-addr 0x800A1000 --args-addr 0x800A1004 --result-addr 0x800A1014 \
    --id postman_roomlib_test \
    --out generated/postman_roomlib_test.c
```

To invoke afterward: write the argument words to `--args-addr`, then write
`1` to `--trigger-addr`; poll that same address for `2` (result ready); read
the return value from `--result-addr`. The handler always returns 0
(declines), so the piggybacked hook's own original behavior is completely
unaffected — this only observes and injects, it never blocks or replaces
whatever normally runs at `--trigger-hook`.

This only **writes a `.c` file**. It never touches a live game, a
recompiler, or your build — wiring the generated file in and calling its
`<id>_register()` from your game's own override/mod init is a manual,
separate step, the same way `classifier_gap_finder.py`'s output is a
candidate list for a human to review, not something applied automatically.

## *** Real, unmerged dependency — read this before using the generated code ***

This is only usable against [RetroPortingToolKit/psxrecomp PR #174](https://github.com/RetroPortingToolKit/psxrecomp/pull/174)
("func_override tier"), branch `feat/func-override-tier` @ `6524ded0` as of
2026-09-16 — **an open, unmerged, experimental branch**, present in neither
this bridge's old known-good psxrecomp pin nor its current c4/wave5 pin.
Using the generated code means pulling that branch (or whatever it becomes
once reviewed/merged) into a psxrecomp checkout your game can actually build
against — a real, currently-external dependency, not something already
available in a stock checkout.

### What's actually been verified (2026-09-16, against 6524ded0)

Earlier drafts of this tool guessed at several details from the PR's own
prose description. Those guesses have since been checked against the real
source — `func_override.h`/`.c`, `cpu_state.h`, `memory.c` — by cloning that
exact commit into a scratch checkout and reading it directly, and the
generated `.c` file was test-compiled (`-c -Wall -Wextra -Wpedantic` against
that checkout's real `runtime/include`, not linked into a full game) with
zero warnings. Confirmed:

- `func_override_guest_call(cpu, target, site_ra)`: arguments go in
  `cpu->gpr[4..7]` before the call, result comes back in `cpu->gpr[2]` —
  exactly the o32 convention this tool assumed. `site_ra` turned out to be a
  **stop-PC sentinel** for an internal dispatch loop (`psx_dispatch_call`
  runs the target "to completion, `pc == site_ra`"), not a value that needs
  to already exist as a real call site — so passing the piggyback hook's own
  address works mechanically. The one real edge case: if that address ever
  appears as an internal branch target *inside* the target function's own
  body, the dispatch loop could stop early. Vanishingly unlikely for two
  unrelated functions, but worth knowing if target and trigger-hook end up
  close together in the same code region.
- Guest memory access inside an override goes through **`cpu->read_word`/
  `cpu->write_word`** — function-pointer members already on `CPUState`
  itself ("wired at init to psx_read/psx_write" per `cpu_state.h`), not a
  free function you declare yourself. The generated code now uses these
  directly instead of the earlier invented `psx_read_u32`/`psx_write_u32`
  placeholders.
- `CPUState.gpr[32]`'s layout was independently confirmed twice — once from
  `psxrecomp/recompiler/include/code_generator.h` (the recompiler's own
  copy) and again from this PR branch's own `runtime/include/cpu_state.h`.

### Two non-obvious requirements this verification surfaced

Both are called out again, loudly, in the generated file's own header
comment — they're easy to miss because neither one is a compile error:

1. **`func_override_install()` must be called once at startup, AFTER every
   `func_override_add()`** (including this generator's own
   `<id>_register()`). Skip it and the dispatcher hook stays `NULL` forever
   — every registered override, this one included, silently never fires.
   No error, no log. `postman.py`'s output can't call this for you since
   it's a once-per-program step, not once-per-override.
2. **The override hook only consults on a genuine CALL** (`jal`/`jalr`) to
   `--trigger-hook` — a tail transfer (`j`/`jr`) into that address does not
   consult it at all (`func_override.h`'s own "SCOPE" section). Pick a
   trigger-hook address that's actually *called* somewhere, or the poll
   handler never runs.

This is still a live, unmerged branch that can change — re-confirm against
whatever commit you actually build against, don't assume 6524ded0's
behavior is permanent.

## Known limitations

- **Up to 4 register-passed arguments only** (`$a0`-`$a3`). Stack-passed
  arguments (a 5th+) are not implemented — `postman.py` refuses to generate
  a call needing more than 4, rather than silently emitting something wrong.
- **No struct-by-value or floating-point arguments.** Every arg type is a
  raw 32-bit word (`u32`/`s32`/`ptr` all share the same underlying
  representation) — this is a scalar-ABI tool, not a general C calling
  convention bridge.
- **You choose the trigger-hook and scratch addresses yourself.** `postman.py`
  has no way to know which addresses are actually safe/unused in a given
  game's RAM map — picking a bad one (code the game itself uses, or an
  infrequently-dispatched hook that never gives you a chance to poll) is on
  you, the same way `classifier_gap_finder.py`'s candidate lists require
  independent verification before trusting them.

## Generic by design

Same contract as `decomp_bridge.py` and `classifier_gap_finder.py`: every
game-specific value (target address, trigger hook, scratch RAM layout) is a
CLI argument. `postman.py` itself contains no game-specific data and works
for any psxrecomp-based title, once that title's own checkout has the
`func_override` branch available — not just Parasite Eve's.
