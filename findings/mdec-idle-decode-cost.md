# Title-screen idle wait-loop runs slower than active video decode — `idle_skip` doesn't cover it

**Correction notice:** an earlier version of this doc claimed MDEC video
decode "never idles" at Parasite Eve's title screen and that continuous
decode was the performance cost. A longer follow-up test disproved that
claim outright — the decode stream idles correctly. The real mechanism is
below, verified with three separate live-counter tests.

## What we saw

In menus, frame rate visibly drops. Specifically: the title-screen's
looping intro/attract video runs at a *higher* real-time speed than the
screen sits at while idling between plays — backwards from what "video
decode costs CPU" would predict, since idling should be the cheap state.

## Test 1 — does the video stream actually idle? (13 minutes, `mdec_state` every 10s)

Queried the runtime's own `mdec_state` debug-server command every 10 seconds
for 13 minutes from a fresh boot (no input, no skip). `dma_in_words` (CD →
MDEC transfer count):

```
t=10 ...climbing...
t=200: 20,882,016
t=210: 20,899,552   <- decode winds down
t=210..300 (90s): 20,899,552, 20,899,552, ... (bit-identical, 9 samples in a row)  <- FULLY IDLE
t=310: 116,736      <- new cycle begins
t=310..500: ...climbing again...
t=510..610 (100s): 20,899,552 flat again          <- FULLY IDLE, second time
t=620: new cycle begins, still running at test end
```

Two full ~190-second active-decode cycles, each followed by a ~90-100
second stretch of **completely flat** counters. **The stream correctly
idles between attract-mode plays.** This directly disproves the original
version of this finding.

## Test 2 — is idle actually slower? (same 13-minute run, FPS telemetry)

`PSX_FPS_TELEMETRY=2` running the whole time, averaged `speed=` per phase
(matched to the mdec_state windows above):

| Phase | State | Avg `speed=` |
|---|---|---:|
| Active decode, window 1 | busy | 0.704× |
| **Idle, window 1** | confirmed flat | **0.309×** |
| Active decode, window 2 | busy | 0.700× |
| **Idle, window 2** | confirmed flat | **0.290×** |
| Active decode, window 3 | busy | 0.705× |

Three independent active windows land at ~0.70×; two independent idle
windows land at ~0.30×, in one continuous run. Not noise — idling is
measurably ~2.3× slower than actively decoding video.

## Test 3 — is `idle_skip` covering the wait loop? (separate 315s run, sampled every 15s)

`game.toml` sets `idle_skip = true` specifically to fast-forward guest idle
spin-loops instead of executing every iteration. The runtime exposes its own
counters via `{"cmd":"idle_skip"}`. Sampled every 15 seconds across a run
that spans one active-decode window and the following idle window:

```
t=0:   {"enabled":1,"skips":90,"cycles_skipped":1822332,"last_pc":"0x8008518C","last_quantum":11}
t=15:  {"enabled":1,"skips":90,"cycles_skipped":1822332,"last_pc":"0x8008518C","last_quantum":11}
...
t=300: {"enabled":1,"skips":90,"cycles_skipped":1822332,"last_pc":"0x8008518C","last_quantum":11}
t=315: {"enabled":1,"skips":90,"cycles_skipped":1822332,"last_pc":"0x8008518C","last_quantum":11}
```

**Identical for the entire 315-second run.** `idle_skip` fired 90 times once
— almost certainly during BIOS boot / early init, before this sampling
window even started — and never again, including throughout the entire
confirmed-idle stretch at the title screen (cross-checked against the
`mdec_dma_in` column sampled in the same run: flat from t≈210 onward, same
as test 1). `last_pc=0x8008518C` sits inside `Spu_ReadWithPrepare`
(khasinski/parasite-eve-decomp, `configs/USA/sym.main.txt`) — an SPU
transfer-wait routine. So the one loop `idle_skip` ever matched here is
audio DMA setup during boot, nothing to do with the title screen at all.

## Conclusion (superseded — see `roomlib-0x80191200-interior.md`)

The paragraph that stood here originally treated `idle_skip` never firing as
the root cause. Following up with a direct `stall_report` comparison of the
same active vs. idle windows found the actual mechanism: during idle,
`interp_share` is 93.6% (vs 48.5% active), and one address —
`0x80191200`, in the same shared "RoomLib" resident overlay as finding #2's
original hot addresses — accounts for ~87% of all interpreted instructions
in that window, at 201,213 instructions per call. It's a captured-but-never-
classified function entry, the exact finding #2 pattern, just a previously
unidentified address. `idle_skip` never firing is a real, correctly-observed
symptom (an interpreted loop isn't something its detector was ever going to
catch), not the cause itself. Full writeup, capture data, and the confirmed
fix: `roomlib-0x80191200-interior.md`.

## Verify

`{"cmd":"idle_skip"}` and `{"cmd":"mdec_state"}` over the debug-server
protocol (`--debug-port`), sampled a few times a minute apart while sitting
at the title screen with no input. `idle_skip`'s `skips`/`cycles_skipped`
should climb during a genuinely-idle stretch (`mdec_state`'s `dma_in_words`
flat); if it doesn't, that's this bug.

## Offer

Happy to help identify why this specific wait loop doesn't get picked up by
`idle_skip`'s detector — we have the decomp's symbol names but not a
call-graph tool to trace which function `0x8008518C` (the *last* PC
`idle_skip` matched, at boot) corresponds to, or what the title-screen loop
actually looks like.
