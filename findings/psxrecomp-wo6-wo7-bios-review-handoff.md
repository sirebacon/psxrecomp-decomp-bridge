# psxrecomp review handoff: WO-6, WO-7 and BIOS PRs #343 / #346

## Outcome

The combined work is merged into `RetroPortingToolKit/psxrecomp` master through
[PR #348](https://github.com/RetroPortingToolKit/psxrecomp/pull/348), at commit
[`89db8168`](https://github.com/RetroPortingToolKit/psxrecomp/commit/89db8168dbb1da035aacd1d9631d5a3bb9469c1a).
[PR #343](https://github.com/RetroPortingToolKit/psxrecomp/pull/343) and
[PR #346](https://github.com/RetroPortingToolKit/psxrecomp/pull/346) are also marked
merged. Their original commits and authorship were preserved in the integration
history. The landed source tree matches the tested branch.

The review resulted in an unconditional resident-dispatch lookup optimization,
a clarification of the WO-7 counters, BIOS setup followups, and fixes to the
BIOS patch-range execution guards. No regressions were observed in the tested
Tomba and Mega Man X6 paths. This is not a claim that Parasite Eve's reported
FMV slowdown has been fully resolved.

## WO-6: what changed, and what the measurements establish

Resident game dispatch now uses an immutable physical-word lookup index for
eligible tables spanning less than 2 MiB. Wider or ambiguous tables retain the
previous binary search. The optimization is enabled without a feature flag.

The important execution contracts are unchanged:

- Live instruction bytes are still validated before native execution. A cached
  address lookup does not cache permission to execute stale code.
- KUSEG, KSEG0 and KSEG1 addresses resolve through the same physical address.
- Flat CPS dispatch, continuation returns, interrupt checks and mod hooks remain
  in place. Overlay-to-resident calls were not converted into nested C calls.

Tomba's index contains 18,130 dispatch entries and occupies 265,706 bytes.
MMX6's contains 18,858 entries and occupies 255,918 bytes.

An isolated benchmark using the actual emitted lookup, simplified table records
and 4,096 repeated mixed-hit queries measured approximately **54-61 ns/query for
binary search versus 1.2-1.6 ns/query for the index**. This establishes that the
lookup itself is substantially cheaper in that benchmark. It does not measure
the entire dispatcher, prove fewer dispatch activations, or establish an
end-to-end FPS improvement.

Two corrections to the supplied analysis matter when interpreting the result:

- Dividing total guest-work time by dispatch count does not isolate dispatch
  bookkeeping. The reported approximately 3.2 microseconds includes guest work
  and cannot be treated as a directly measured fixed dispatch cost.
- The branch at `0x80191BC0`, with immediate `FFFB`, targets `0x80191BB0`, not
  `0x80191BB4`.

The proposed nested/direct-call transformation was not landed; the shipped
change targets address-resolution cost while retaining the existing execution
boundaries.

## WO-7: counter semantics, not confirmed count corruption

The hot-native-owner sampler counts **owner activations**, including CPS
continuation/resume entries. Function-entry tracing counts **function
invocations**. A function invoked around 100 times can therefore accumulate
many more owner activations while repeatedly calling and resuming.

The sampler uses direct-mapped buckets. A collision replaces the recorded owner
and resets its count; it does not accumulate another owner's calls. Collisions
can cause undercounting, not the alleged inflation mechanism.

The runtime label now explicitly reports `hot_native_owner` and an activation
lower bound, and the API documentation explains the distinction. The counting
algorithm was not changed. This investigation did not confirm counter corruption.

## BIOS #343: followups included

The original setup-host work was integrated with these followups:

- BIOS setup detection must find a **configured** backend, not just any
  dispatch/full filename pair in the directory.
- Both generated files and the matching backend descriptor must exist; a stale
  pre-descriptor pair or unrelated game output cannot complete BIOS setup.
- Detection uses the configured framework location, including relocated
  framework checkouts.
- Expected-retail discovery is preserved for `OpenBIOS;SCPH1001` and alternate
  retail stems.
- The CLI regression test registered but missing from the PR was supplied.

The compiled host probe passed seven positive/negative cases using real
recomp-ui headers and a native compiler, including alternate stems, relocated
paths, missing files, stale descriptors and unrequested backends. The CLI tests
also cover profile forwarding, UTF-8 subprocess output and failure propagation.

## BIOS #346: execution-safety fixes included

Declared kernel patch ranges allow the unchanged surrounding BIOS body to run
natively while the guest's actual patched instructions execute on the
interpreter. The integration adds safeguards to that mechanism:

- Run patch guards before cycle charging and before terminators, including a
  jump/return at the beginning of a patched range.
- Guard entry through interior labels so an internal branch cannot bypass a
  start-only check.
- Compare the complete declared range and hand off at the requested RAM PC,
  rather than restarting at the range's beginning.
- Fail closed to interpretation if a range begins across an unsafe branch or
  load-delay boundary.
- Do not hand back from the interpreter with a pending load.
- Clear the range metadata during memory reset.

No patch ranges were widened, and no guest patch effects were replaced with
host-side approximations. Focused emitter tests cover the terminator/interior
entry cases and unsafe delay boundaries; runtime tests cover acceptance inside
declared ranges and rejection of changes outside them.

## Validation performed

Both baseline and integration used freshly generated game/BIOS code and
isolated builds, overlay caches and memory cards. The final baseline was master
`b4ea4c37`; the integration was refreshed and rebuilt against it before the
final matrix. Original game checkouts and saves were not modified.

Environment: Windows, native Clang 22, Release recompiler and RelWithDebInfo
runtimes; LLE BIOS boot/calls, native overlay compilation, debug diagnostics and
headless framebuffer readback. Title-owned mod sources were built/staged. UI,
Vulkan, netplay, rewind and PGXP were disabled in this test configuration.

### Automated checks

- 65 enabled recompiler tests passed.
- 78 executed runtime tests passed: **143 executed CTest tests total**.
- CTest retains three disabled recompiler tests, two disabled runtime tests and
  one explicitly skipped runtime test. These were not counted as executed
  passes.
- The disabled overlay-pair executable test was additionally run directly and
  passed all five scenarios.
- The BIOS host probe passed its seven cases with the required headers/compiler
  present, rather than taking its missing-dependency skip path.
- The newly inherited relocation/AOT tooling checks passed 4 + 24 tests.

Some pre-existing test-harness problems were repaired to make these gates
usable: Windows text/byte fixtures, a stale assertion demanding unsafe
continuation-range clipping, duplicated cache-tag formatting, and the Windows
mod-runtime test's insufficient default stack for its real 1 MiB hashing buffer.
These harness repairs do not change production guest behavior.

### Final live regression matrix

All eight runs below completed with clean exits, native execution and 32
completed 128-byte memory-card read transactions per run.

| Game | BIOS | Baseline frames | Integration frames | Kernel-body mismatches: baseline -> integration |
| --- | --- | ---: | ---: | ---: |
| Tomba | OpenBIOS | 11,005 | 11,015 | 22 -> 0 |
| Tomba | SCPH-1001 | 11,009 | 11,008 | 11 -> 0 |
| Mega Man X6 | OpenBIOS | 11,002 | 11,013 | 7 -> 0 |
| Mega Man X6 | SCPH-1001 | 11,014 | 11,015 | 11 -> 0 |

Screenshots show real FMV playback and MMX6's gameplay demo. The integration
runs retain both native overlay and native kernel execution, with zero remaining
kernel-body mismatches in the final samples. Card-read coverage is not a
save/write/load round-trip test.

An extra OpenBIOS/MMX6 run on each side checked the demo fade-out through more
than 11,150 frames. The baseline and integration screenshots at frame 11,019
matched byte-for-byte, as did the subsequent Capcom screen. The initially darker
integration screenshot was a later sample of the normal fade, not missing
background rendering.

The earlier exploratory runs included two failed attempts: a baseline Tomba
screenshot exceeded a five-second TCP deadline, and an integration MMX6 cold
run spent most of its budget in host startup and reached only 1,414 frames.
Their retries passed; the baseline also exhibited slow startup. Neither failed
attempt is counted as a pass. All eight final refreshed runs passed.

Both BIOS images were regenerated. OpenBIOS emitted 651 functions, with zero
tagged interpreter fallbacks and four existing unsupported-instruction skips.
Retail emitted 1,309, with its one existing load-delay fallback and one existing
unsupported-instruction skip. The retail BIOS SHA-256 used was
`71af94d1e47a68c11e8fdb9f8368040601514a42a5a399cda48c7d3bff1e99d3`.

## Confidence limits and suggested downstream check

The evidence supports merging for the tested boot, FMV and attract/demo paths,
generated dispatch contracts, BIOS patch boundaries and card reads. It does not
establish full-game correctness, hardware differential equivalence, audible
audio quality, UI behavior, save/load round trips or cross-platform coverage.
Tomba 2, alternate retail BIOS images and a new Parasite Eve FPS run were not
part of this matrix.

For the Parasite Eve followup, update to the merged framework, rebuild the
recompiler, regenerate resident game and BIOS code, and use matching regenerated
overlay caches. Compare the same FMV segment with warmed caches. Measure lookup
or dispatcher time directly if attributing overhead, and keep function-entry
counts separate from owner activation counts. The remaining question is how
much the merged changes improve that game's actual frame pacing, not whether
the isolated lookup benchmark represents total guest-work cost.

The committed review and detailed scope are available in
[WO6_BIOS_INTEGRATION_REVIEW.md](https://github.com/RetroPortingToolKit/psxrecomp/blob/89db8168dbb1da035aacd1d9631d5a3bb9469c1a/docs/internal/WO6_BIOS_INTEGRATION_REVIEW.md).
