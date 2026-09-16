# Parasite Eve on the `psxrecomp` c4/wave5 pin: a real, isolated, still-unresolved FPS regression

**Date: 2026-09-15. Status: isolated via a clean controlled A/B, not yet
root-caused. This is a handoff for further investigation, not a fix.**

## TL;DR

Upgrading this checkout's `psxrecomp`/`recomp-ui` pins to match the public
`v0.4.0` release (`codex/wave5-c4-20260915`, same commits Alex's own
integration testing used) causes gameplay to never reach full speed during
the intro FMV — it settles around 30-45fps instead of 60fps, and the
`dirty_ram_insns` interpreter counter climbs into the billions without ever
flattening, well past the point where every single measurement this project
has ever taken (going back weeks) settles cleanly. A controlled 3-way A/B
proves this is a real regression in the framework pin itself, **not** caused
by anything this project added locally (its own `--force-interior` list, its
own mods, or the `autocompile.c` buffer-overflow fix found and fixed
earlier the same night — see
`autocompile-cmd-buffer-overflow-2026-09-15.md`, which this document
follows on from).

## The controlled A/B

Same launch every time: `build/play.ps1`, same disc/BIOS, `-VsyncOff`, same
debug port, same machine, back to back.

| Configuration | `psxrecomp` pin | `recomp-ui` pin | Result |
|---|---|---|---|
| **Old (pre-upgrade)** | `67a31460` | `4eda654` | Clean: `dirty_ram_insns` flat at the harmless 257 baseline through frame 9,535, settles to **20,304** by frame 10,748 (t+140s) — matches every prior measurement this project has ever recorded |
| **New (c4/wave5)**, full 208-address force-interior list | `pe-local-work-c4-autocompile-buffer-fix`* | `ff92028` | Still climbing at 1.3B+ past frame 35,000 (many real-time minutes), never settles |
| **New (c4/wave5)**, zero force-interior addresses | same | `ff92028` | Still climbing (1.34B by frame 12,672) well past the frame count where the old pin cleanly settles; growth rate decelerating but not plateauing |

\* `pe-local-work-c4-autocompile-buffer-fix` = `psxrecomp` at
`0e962bf6` (the exact commit `v0.4.0`'s own `framework_pins.txt` uses) plus
one small local fix (a 4096-byte fixed buffer in `autocompile.c` that
silently truncated long autocompile commands — orthogonal to this
regression, already fixed and documented separately).

**The third row rules out this project's own `--force-interior` list as the
cause.** The original hypothesis going into this A/B — that the new
jump-table classifier enhancement (`fe2c0046b`, "Recognize bounded MIPS
switches with scheduled table constants") might classify some of our forced
addresses differently and create a real correctness conflict when we force
them anyway — is refuted by the zero-force-interior row: the non-settling
behavior happens on the new pin regardless of whether any addresses are
forced at all.

## What this means

Something in the ~50+ commits between the old pin and `c4/wave5` causes
markedly heavier interpreter usage during the intro-FMV window specifically,
independent of anything Parasite-Eve-specific. Given the old pin settles
perfectly and the new pin doesn't, under otherwise identical conditions,
this looks like a real regression in the shared framework, not a
Parasite-Eve-specific issue — though it has only been reproduced on this one
title so far.

## A `git bisect` was attempted and hit a real methodological snag — worth knowing before re-attempting

Started a standard `git bisect` between the two pins to find the exact
commit. Git needed the merge-base tested first (the two branches don't have
simple linear ancestry — `pe-local-work` diverged from a much older point in
`origin/main`'s history than `c4/wave5` did). Built and tested that
merge-base commit (`47bda817`, "runtime: fix savestates at dirty
boundaries") using the same 208-address force-interior list — and it showed
`dirty_ram_insns` climbing to 108M+ by frame 2,164, dramatically faster than
even the confirmed-good old-pin baseline (which stays flat at 257 until
frame 9,535).

**This isn't necessarily evidence that the merge-base itself is "bad" in the
same way as the c4/wave5 tip.** It's more likely a sign that this project's
208 hardcoded addresses — tuned against the RoomLib function layout as it
existed in one specific historical build — don't line up with the same
functions anymore at a sufficiently distant point in `psxrecomp`'s history
(intervening compiler/codegen changes can shift where overlay functions
land). That makes the "does `dirty_ram_insns` settle" signal, using this
project's own address list, **unreliable as a bisect oracle across a wide
historical range** — a real methodological trap, not a dead end, but
something whoever picks this up should design around rather than repeat.

**Recommended approach for whoever continues this**: bisect using either
(a) zero force-interior consistently at every step, comparing raw
growth-rate/settle-time against the *old pin's own* zero-force-interior
baseline (not yet measured — this project only ever tested zero-force-interior
on the new pin, never the old one, so that specific baseline still needs
establishing) rather than the with-fix baseline, or (b) a synthetic
reproduction that doesn't depend on Parasite-Eve-specific addresses at all
(e.g., whatever headless/scripted repro this project's own team already
uses for cross-title validation, mentioned in earlier upstream review
threads).

## Where things were left

Reverted this checkout back to the old, known-good pin (`psxrecomp` `67a31460`,
`recomp-ui` `4eda654`) so Parasite Eve is playable at full speed tonight. The
`autocompile.c` buffer-overflow fix (a real, separate, already-verified bug)
still needs porting forward whenever the new pin is adopted — it's
independent of this regression and doesn't require it to be resolved first.

## Suggested next steps for Alex / whoever owns this

1. Try to reproduce on a title that doesn't depend on Parasite-Eve-specific
   `--force-interior` addresses at all (a stock title with no local
   overlay-classifier workarounds), to get a clean pass/fail signal free of
   the address-drift confound found here.
2. If reproducible cross-title, a real `git bisect` using that clean signal
   should isolate the exact commit efficiently (the search space is roughly
   50 commits, i.e. ~6 bisect steps).
3. Candidates worth a first look, purely from skimming commit messages in
   the range (not vetted — see caveat below):
   - `69d783f5` "tools: O(1) overlay dispatch instead of a sparse switch" —
     touched, read its full commit message, and it looks *unlikely*: it's
     extensively self-validated (hash-collision-tested against all 524,288
     word-aligned addresses in the 2MB RAM window, and the author's own
     measurement showed a **6.3% throughput improvement**, not a
     regression). Mentioned here mainly to save someone else from
     re-checking it first.
   - `f07f8019` "runtime: validate stale-static ranges in full — drop the
     exec_pc clip" and `4d9060a5` "codegen: stale-static guard on
     inter-piece host transfers" — not yet examined in detail, but the
     "stale-static" framing sounds directly relevant to whether compiled
     overlay code gets correctly recognized as still valid vs. incorrectly
     treated as stale (which would force it back to the interpreter) —
     worth checking first.
   - `aa6fa2c9` "runtime: arm the page watch for static overlay code
     ranges" — also unexamined, also plausibly relevant to overlay
     residency/invalidation behavior.

All of the above is speculation from commit *messages* only — none of these
three have actually been checked out and tested individually. That's the
natural next step if someone wants to pick this up without redoing the full
bisect from scratch.
