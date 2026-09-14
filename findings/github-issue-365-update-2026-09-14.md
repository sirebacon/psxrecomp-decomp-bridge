# Draft comment for RetroPortingToolKit/psxrecomp#365

(Copy everything below the line into a comment on the issue.)

---

## Update: corrected root cause, and a fix attempt that doesn't pay off

Since filing this, I dug further and want to correct/refine the technical
explanation, and save whoever picks this up some time on an idea I already
tried.

### Corrected root cause

My original framing was "a MIPS jump-table `switch`'s case targets aren't
recognized as demandable" (a runtime-computed `jr` instead of a static
`jal`). That's not quite it, and it's not even certain the dispatch in
question compiles to an actual jump table at all (small dense switches
often don't). The real, verified cause is narrower and more concrete:

**`FUNCTION_POINTER_TARGET` — the classification that exists specifically
to catch function-pointer/jump-table-style targets — is unreachable dead
code for any capture the tool produces today.** In `compile_overlays.py`,
this classification is only ever assigned via two code paths:

1. `for addr in captured_function_entries: include(addr, 'FUNCTION_POINTER_TARGET')`,
   where `captured_function_entries` comes from `cap.get('function_entry_pcs', [])`.
   Every real capture I checked has `"function_entry_pcs": []` — always
   empty, by design (the classifier derives entries itself later, per your
   own PR #349 review comments on a related report from me).
2. A second path gated by `legacy_seed_mode = bool(legacy_seeds) and not
   cap.get('schema')`. Every real capture has
   `"schema": "psxrecomp overlay capture v2"` set, so `not
   cap.get('schema')` is always `False`. This path never runs either.

Both verified directly against real `overlay_captures.json` data, not
inferred from symptoms. So the addresses in question were never actually
failing a jump-table-specific check — the mechanism meant to classify them
correctly is simply never invoked for any current-format capture.

### A fix I tried, and why I'm not proposing it

The obvious-looking fix is to reuse the existing `dispatch_fragment_demands`
/ "isolated fragment demand retained" recovery that `DISPATCH_ENTRY`
addresses already get, and extend it to also cover addresses that fall
through to `OBSERVED_PC_ONLY`:

```python
elif addr in executed_pcs or addr in legacy_seeds:
    excluded[addr] = 'OBSERVED_PC_ONLY'
    if addr in executed_pcs and addr + 4 <= fragment_hi:      # new
        dispatch_fragment_demands.add(addr)                    # new
```

Tested on a copy of the tool. Offline (`--check` against a static capture
snapshot) it looks great — auto-recovers every previously-stuck address
with no manual `--force-interior` needed, compiles clean.

Live, it's a different story. Recovering every `OBSERVED_PC_ONLY` address
this way means one isolated `gcc`/recompiler invocation per address (by
design — `compile_interior_fragment`'s own docstring: *"one speculative
entry cannot poison trusted roots"*), and the per-candidate overhead ahead
of each of those invocations is real. With ~175 addresses recovered at
once, a live boot got stuck on a single compile pass with zero completions
for 3+ minutes. Capping how many new addresses get recovered per pass (I
used 8) does let it make real progress and eventually converge to a
genuine native steady state — but even then, a clean cold-cache A/B on an
otherwise-identical build showed it takes ~2-3x longer and burns ~2x more
interpreted instructions to converge than simply not attempting the
recovery at all, because the recovery passes don't finish before the
window that actually needed those addresses (an intro FMV, in my case) has
already played out.

So: the diagnosis is solid, but this particular fix shape isn't a win in
practice, at least not without also addressing the per-candidate cost
before it reaches the compiler (or batching multiple addresses per
compile invocation, which conflicts with the isolated-fragment design's
own safety property). Flagging this mainly so it's not the first thing
re-tried.

### Profiled the slowness, and tried batching anyway — your exclusion of orphans from it is correct

The per-candidate cost is a full separate recompiler subprocess spawn
(`psxrecomp-game.exe`, re-parsing the whole `game.toml` from scratch) per
address, not `gcc`. I noticed `compile_batched_fragment_roots` already
exists as a batch-then-bisect-on-failure mechanism, but
`partition_strong_root_demands` explicitly keeps `executed`/orphan-class
addresses out of it (only `static_exact` roots get batched). No comment
explains why, so I tried it anyway on a disposable local copy, purely to
find out empirically.

It's correct to exclude them. Batching multiple orphan addresses into one
recompiler invocation produced real, reproducible
`undefined reference to 'psx_game_text_native_ok'` link failures that do
**not** happen compiling the same addresses one at a time (verified
directly: same address, same capture, completely unmodified
`compile_overlays.py`, singleton `--force-interior` — builds clean).
Compiling multiple genuinely-uncertain interior entries together changes
what code gets reached/linked in ways that don't happen compiling each
alone. So the existing isolation boundary isn't overcautious — it's
guarding against something real, now confirmed rather than just assumed.
Figured this was worth passing along as independent confirmation of a
design choice you already made, in case it's useful.

All of this is from one local checkout/one title (Parasite Eve) — same
caveat as before, I can't independently verify this generalizes the way
your team's PR #349 testing did across titles.

Happy to share the exact patch, capture data, or timing numbers if useful.
