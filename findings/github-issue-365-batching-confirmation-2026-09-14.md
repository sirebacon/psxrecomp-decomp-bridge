# Draft follow-up comment for RetroPortingToolKit/psxrecomp#365

(Copy everything below the line into a new comment on the issue — this is
a follow-up to the `FUNCTION_POINTER_TARGET` dead-code update.)

---

## Follow-up: profiled the recovery slowness, and found a minimal, reproducible batching bug — not just a design boundary

After posting the `FUNCTION_POINTER_TARGET` diagnosis above, I dug into
*why* a naive fix (recovering these addresses via the existing
`OBSERVED_PC_ONLY` fragment-demand path) isn't practical, since "it
converges but too slowly" wasn't a satisfying enough answer on its own.
What I found is smaller and more concrete than I expected — a minimal
2-address reproduction, not just a scale problem.

### What's actually slow

Every singleton orphan recovery (`compile_interior_fragment` →
`compile_fragment_batch`) spawns a **full separate `psxrecomp-game.exe`
recompiler subprocess** — not `gcc` — which re-parses the entire
`game.toml` config from scratch for a single-address `dispatch_root` seed.
That per-candidate subprocess spawn, repeated once per address, is the
dominant cost. With ~175 addresses needing recovery in one region, that's
~175 separate recompiler-process launches done sequentially.

### The natural fix exists in the tool — but it's walled off from this exact case, for what turns out to be a good reason

`compile_batched_fragment_roots` already implements a batch-then-bisect
mechanism: compile multiple addresses in **one** recompiler invocation,
and only if the whole batch fails, recursively split it in half to
isolate the bad root. That would eliminate almost all the subprocess-spawn
overhead if it applied here.

Tracing where it's wired up: `partition_strong_root_demands` explicitly
puts `executed` addresses (the exact `OBSERVED_PC_ONLY`/orphan class this
issue is about) into an `isolated` set that never reaches that batching
path — only statically-verified `static_exact` roots get batched. No
comment explains why, so rather than assume it was overcautious, I tested
it.

### Minimal reproduction

Patch (on top of an **otherwise-completely-stock** `compile_overlays.py`
— no classifier changes at all, so this is independent of the
`FUNCTION_POINTER_TARGET` finding above), in `_do_frags`'s orphan-fragment
loop:

```python
# before: one compile_interior_fragment(a, ...) call per address, in a
# `for a in orphans:` loop.

# after: route the same orphan addresses through the tool's own existing
# batch-then-bisect mechanism instead.
def _orphan_compile_one(roots):
    return compile_fragment_batch(
        set(roots), data, load_addr, size, phys_addr, cache_dir,
        args, frag_env, toml, job['producer_ranges'],
        job['cross_call_allow'], manifest_provenance=ORPHAN_MANIFEST_PROVENANCE)

def _orphan_on_success(roots, frag_ids, status):
    record_fragment_success(frag_ids, status, ORPHAN_MANIFEST_PROVENANCE)

def _orphan_on_singleton_failure(a, status):
    record_fragment_failure(a, status)

for offset in range(0, len(memo_filtered), BATCH_SIZE):
    chunk = memo_filtered[offset:offset + BATCH_SIZE]
    compile_batched_fragment_roots(
        chunk, _orphan_compile_one, _orphan_on_success,
        _orphan_on_singleton_failure,
        should_bisect=fragment_batch_failure_is_partitionable)
```

Repro command (real addresses/capture from my checkout — obviously your
own capture data will have different addresses, but the shape should
carry over):

```
python compile_overlays_batching_only_test.py \
  --game-toml game.toml --recompiler psxrecomp-game.exe \
  --runtime-include runtime/include --cps --compiler gcc --gcc gcc.exe \
  --check --captures overlay_captures.json \
  --force-interior 0x80190B70 --force-interior 0x80190B74
```

**Result with `BATCH_SIZE=2`, forcing just these two addresses together**:

```
undefined reference to `psx_game_text_native_ok'
SHARD FAIL [fragment] interior 0x80190B70 @region 0x00190000: compile-error
SHARD FAIL [fragment] interior 0x80190B74 @region 0x00190000: compile-error
```

**Same two addresses, same capture, completely unmodified
`compile_overlays.py`, each forced individually (no batching at all)**:
both build clean, no such error.

This isn't a large-batch/scale problem — it reproduces with the smallest
possible batch, just two addresses compiled together in one recompiler
invocation instead of two separate invocations. I also confirmed it at
`BATCH_SIZE=16` (a bigger batch spanning more of the region) before
narrowing it down to this 2-address minimal case.

### Conclusion, and a guess at the mechanism (unverified)

Compiling two genuinely-uncertain interior entries together in one
recompiler invocation changes what code gets reached/linked, in a way
that produces an unresolved symbol neither address's own code needs when
compiled alone. Your existing exclusion of `executed`/orphan addresses
from the batching path isn't overcautious — it's guarding against
something real and easy to hit, now confirmed with a 2-address repro
rather than just inferred from the code structure.

Pure speculation on the actual cause, since I don't know the recompiler's
codegen internals well enough to say for sure: `psx_game_text_native_ok`
sounds like a text-rendering-related native/HLE helper. My guess is the
recompiler's reachable-code discovery, when given multiple `dispatch_root`
seeds in one job, ends up including a code path (reachable from one root
but not the other) that calls this helper, without whatever normally
guarantees that helper's declaration/import gets emitted for a
single-root job. That's a guess, not something I traced into
`code_generator.cpp` myself.

### What I did *not* check

Whether this is specific to these two addresses/this region, or general
to any two orphan addresses batched together. Only tested one pair from
one region in one title's capture.

Passing this along mainly as independent, now-minimally-reproduced
confirmation of a design decision you already made, and so nobody
re-discovers the same link failure by trying the "just batch them" idea
themselves.

Same caveat as always: one local checkout, one title (Parasite Eve) — not
independently verified against your own test corpus.
