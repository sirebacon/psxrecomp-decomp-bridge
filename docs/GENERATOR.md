# `generator.py`: wire a decomp's own verified C directly into a live game

## What this is, and how it fits with postman.py and confidence.py

The last piece of the func_override design discussion: given a candidate
guest function, generate a `func_override` **replacement** wired directly to
that decomp's own already-verified C implementation — bypassing the overlay
classifier's `OBSERVED_PC_ONLY` interpreter fallback entirely, instead of
working around it. `postman.py` invokes a function on demand for
verification; `confidence.py` decides whether a given implementation is
trustworthy enough to use; `generator.py` is the tool that actually produces
the replacement, and only for candidates `confidence.py` calls eligible.

## *** Real blocker found before writing any of this — read this first ***

Before generating anything, I traced how a hand-written decomp function's
memory access would actually interact with the recomp runtime, because the
original plan ("call the decomp function directly, marshal register
arguments in and out") looked simple. It isn't, for most real game code.

Confirmed directly from source
(`psxrecomp/recompiler/src/full_function_emitter.cpp:1970-1973`): every
guest memory access in psxrecomp's *generated* code is an explicit
`cpu->read_word(addr)` / `write_word(addr, val)` call against a plain
`uint32_t` guest address — never a native struct pointer dereference. A
decomp's own C, by contrast, is written as ordinary C:

```c
BattleEntity *actor = D_8009D254;
int radius = actor->renderObject.table_value70;
```

(this is literally `Entity_ApplyCollisionResponse.c`, read directly from the
real decomp). Those two representations are incompatible. psxrecomp's actual
guest RAM is a `static uint8_t ram[RAM_SIZE]` in `memory.c`, exposed only
through `memory_get_ram_ptr()` at whatever arbitrary address the host
allocator gives it — there is no fixed mapping that makes a guest address
like `0x8009D254` a valid native pointer into that buffer. Calling a decomp
function whose body dereferences a struct pointer, without such a mapping,
reads garbage host memory.

Making arbitrary decomp C directly linkable would need either mapping guest
RAM at a fixed, PS1-matching virtual address (a real recomp-architecture
change, out of scope for a bridge tool) or transpiling every `->` in decomp
source into an explicit `read_word`/`write_word` call (a source-to-source
compiler, a much bigger project). Neither is attempted here.

**So `generator.py` is scoped, on purpose, to functions provably free of the
problem**: no pointer parameters, no pointer return, and no `->` anywhere in
the function body. This was a deliberate choice, presented to and confirmed
by the project owner, over two costlier alternatives (writing up the finding
as a recomp-architecture question instead of building anything, or
prototyping the fixed-RAM-mapping approach). It's a real minority of game
logic — most touches entity/room structs — but it's buildable and correct
today.

## What `generator.py` actually does

```
python bridge/generator.py generate \
    --config games/parasite-eve/config.toml \
    --address 0x80190B70 --credit 40 \
    --id override_roomlib_handler \
    --out generated/override_roomlib_handler.c
```

1. Resolves the address to its containing decomp function and source file
   (reusing `classifier_gap_finder.py`'s symbol table and
   `confidence.py`'s `resolve_source_file`).
2. Requires `confidence.classify_source_file` to report `ELIGIBLE` —
   `semantic_c` **and** a passing `objdiff.json` byte-match. An unverified
   implementation never reaches the signature check at all.
3. Parses the function's real C signature out of its own source file, and
   refuses (with a specific reason) anything that isn't provably scalar-only:
   a pointer or array parameter/return, `float`/`double`/`long long`,
   more than 4 arguments (no stack-passed args), an unparseable signature
   (e.g. a function-pointer parameter), or **any `->` anywhere in the
   function body** — checked even when the signature itself is all-scalar,
   because that's exactly what `Entity_ApplyCollisionResponse` looks like:
   `void Entity_ApplyCollisionResponse(int unused)` is a fully scalar
   signature, but the body dereferences a global `BattleEntity*`
   immediately. Signature-only checking would have wrongly accepted it;
   this generator correctly refuses it in practice, not just in theory.
4. If accepted, writes one `.c` file: an `extern` declaration of the real
   decomp function, a `func_override` handler that reads `cpu->gpr[4..N]`
   into the declared parameter types, calls the real implementation, and
   writes a non-void return into `cpu->gpr[2]` — then a `_register()`
   function.

## This produces a REPLACEMENT, not a piggyback

Unlike `postman.py`'s handler (which always declines, so it never changes
the piggybacked function's own behavior), this generator's handler **always
returns 1** — the whole point is replacing the guest function. That makes
`--credit` a real, required decision, not a formality: `func_override.h`'s
CYCLE ACCOUNTING policy has no default to inherit, and a replacement that
charges the wrong cycle count shifts IRQ phase for the rest of the session.
`--credit` takes a nonnegative integer or the literal string `self` (for
`FO_CREDIT_SELF`, only correct if you separately make the implementation
call `psx_advance_cycles()` itself — this generator's shim does not do that
for you). A negative value other than `self` is rejected outright: only
`FO_CREDIT_SELF` (-1) is a valid negative credit per `func_override.h`;
anything else fails at registration (`FO_ERR_ARGS`), silently, since this
tier prints nothing — better to catch it before generating the file than to
let it fail invisibly at runtime. Per `func_override.h`'s own guidance, a
credit is an approximation unless independently measured (LLE: run with the
override declined, sample the real cycle delta across the call boundary).

## Verified by actually running the generated code, not just compiling it

Beyond a `-Wpedantic` compile against the real PR #174 headers (same rigor
as `postman.py`), the accept path was verified by actually **executing**
the generated handler: a synthetic pure-scalar test function
(`TestScalarAdd(int a, unsigned int b)`, clamped at 100) was compiled
together with its generated override shim and a small test harness that
constructs a `CPUState`, sets `gpr[4]`/`gpr[5]`, calls the generated handler,
and checks `gpr[2]` against the real function's own return value — for both
the normal-add case and the clamp branch. Both matched exactly. Real
candidates weren't used for this because every one already read in this
project (`Entity_ApplyCollisionResponse` included) touches pointer/struct
data internally, which is exactly what the generator is supposed to reject
— so the accept path needed a synthetic fixture to exercise at all, and the
reject path was verified against that same real, pointer-heavy function.

## Real, unmerged dependency

Same as `postman.py` — see `docs/POSTMAN.md`. This only works against
[RetroPortingToolKit/psxrecomp PR #174](https://github.com/RetroPortingToolKit/psxrecomp/pull/174),
branch `feat/func-override-tier` @ `6524ded0` as of 2026-09-16, open and
unmerged. `func_override_install()` must still be called once after every
registration, and the target address must be reached via a genuine call
(`jal`/`jalr`), not a tail transfer — both called out again in the generated
file's own header comment.

## Known limitations

- **Scalar-only, no exceptions** — see "Real blocker found" above. This is
  the load-bearing limitation, not a convenience one.
- **Up to 4 register-passed arguments**, matching `postman.py`'s own scope.
- **The body-level `->` check is a text heuristic**, not a full static
  analysis — deliberately conservative (refuses when unsure) rather than
  permissive, but it can't prove a function is *definitely* pointer-free in
  every exotic case (e.g. pointer arithmetic spelled without `->`, though
  none of the real project code encountered so far does this).
- **You choose `--credit` yourself** — `generator.py` has no way to measure
  the original function's real timing; it only refuses formats it can prove
  are wrong (non-integer, invalid negative).

## Generic by design

Same contract as every other tool in this bridge: no game-specific data in
`generator.py` itself. The confidence classifier, symbol table, and source
resolution all come from the game's own `config.toml` through
`confidence.py` and `decomp_bridge.py`.
