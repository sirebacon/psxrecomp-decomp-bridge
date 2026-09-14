# Draft follow-up comment for RetroPortingToolKit/psxrecomp#365

(Copy everything below the line into a new comment on the issue — this is
a follow-up to the `FUNCTION_POINTER_TARGET` dead-code update.)

---

## Follow-up: profiled the recovery slowness, tried batching, and it confirms your existing design boundary is correct

After posting the `FUNCTION_POINTER_TARGET` diagnosis above, I dug into
*why* a naive fix (recovering these addresses via the existing
`OBSERVED_PC_ONLY` fragment-demand path) isn't practical, since "it
converges but too slowly" wasn't a satisfying enough answer on its own.

### What's actually slow

Every singleton orphan recovery (`compile_interior_fragment` →
`compile_fragment_batch`) spawns a **full separate `psxrecomp-game.exe`
recompiler subprocess** — not `gcc` — which re-parses the entire
`game.toml` config from scratch for a single-address `dispatch_root` seed.
That per-candidate subprocess spawn, repeated once per address, is the
dominant cost. With ~175 addresses needing recovery in one region, that's
~175 separate recompiler-process launches done sequentially.

### The natural fix already exists in the tool — but it's walled off from this exact case

`compile_batched_fragment_roots` already implements a batch-then-bisect
mechanism: compile multiple addresses in **one** recompiler invocation,
and only if the whole batch fails, recursively split it in half to
isolate the bad root. That would eliminate almost all the subprocess-spawn
overhead if it applied here.

Tracing where it's actually wired up: `partition_strong_root_demands`
explicitly puts `executed` addresses (the exact `OBSERVED_PC_ONLY`/orphan
class this issue is about) into an `isolated` set that never reaches that
batching path — only statically-verified `static_exact` roots get
batched. There's no comment explaining why, so rather than assume it was
just overcautious, I tested it.

### Tried it anyway, on a disposable local copy — and the exclusion is correct

Rerouted orphan recovery through the existing `compile_batched_fragment_roots`
mechanism instead of the singleton wrapper, grouping up to 16 addresses
per recompiler invocation. Result: real, reproducible
`undefined reference to 'psx_game_text_native_ok'` link failures across
most of the batch.

Confirmed this is specifically caused by batching, not anything else about
the capture or environment: ran the *exact same address*, completely
**unmodified** `compile_overlays.py`, singleton `--force-interior` (no
batching at all) — builds clean, no such error. Same address, same
capture, same game state; the only variable was whether it was compiled
alone or grouped with other orphan entries.

### Conclusion

Compiling multiple genuinely-uncertain interior entries together changes
what code gets reached/linked in ways that don't happen compiling each
one alone. Your existing exclusion of `executed`/orphan addresses from the
batching path isn't overcautious — it's guarding against something real,
now empirically confirmed rather than just inferred from the code
structure. That closes off batching as a way to fix the per-candidate
slowness without deeper changes to how the recompiler handles
reachability/linkage for grouped uncertain roots — which is a much bigger
piece of work than a `compile_overlays.py`-only patch, and squarely in
the territory of whoever owns that codegen path.

Passing this along mainly as independent confirmation of a design decision
you already made, and so nobody re-discovers the same link failure by
trying the "just batch them" idea themselves.

Same caveat as always: one local checkout, one title (Parasite Eve) — not
independently verified against your own test corpus.
