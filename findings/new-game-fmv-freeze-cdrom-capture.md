# New Game FMV freeze — live capture of a CD-ROM Pause/Read race, first reproduction

**Correction added after reading `cdrom.c` directly (same day)**: the
"`int1_pended` frozen at 40" claim below is weaker evidence than originally
stated and should not be read as proof the CD stream stopped delivering
sectors. Reading the actual increment site in `runtime/src/cdrom.c`
(`process_read_stream()`) shows `s_int1_pended` only increments in one
narrow case — a sector delivered *while the guest hasn't yet acked the
previous interrupt*, forcing it to be queued rather than raised immediately.
A perfectly healthy stream where the guest acks every interrupt promptly
could leave this counter completely flat with nothing wrong at all. The
right counter for this question is `cd_dataready_fires` (exposed by the
`fmv_state` debug command, alongside `mdec_decode_count` and
`xa_stream_active`), which was not queried during the live capture. The
command sequence below (Pause/Setmode/Setloc/ReadS from `0x00000F40`) and
the `freeze_check` contradiction (cycle/frame counters advancing normally
while the picture was frozen and audio looped) are still directly-observed
fact and still the strongest lead — only the specific "proof via
`int1_pended`" framing is retracted. Next reproduction should query
`fmv_state` instead of/alongside `cdrom_state`.

Captured 2026-09-13. This bug was first reported very early in this project
("New Game FMV freeze") and could never be reliably reproduced or diagnosed
at the time. It recurred live today, and this time the debug server was
already attached (from unrelated mod-testing work), so it was caught with
real telemetry instead of just a description. Root mechanism not yet fixed
— this document is the capture and the leading hypothesis, not a closed
finding.

## What triggered it (context, not yet confirmed as the actual cause)

Sequence of events immediately before the freeze, for whoever picks this up:
1. Two new mods (`pe.enhancement.increased-storage`, `pe.enhancement.faster-
   movement`) had just been switched from a custom activation-plugin
   implementation to the framework's declarative `[[patch]]` mechanism,
   specifically to fix them not surviving a savestate restore.
2. That fix was verified via the debug server: a `savestate` save to slot 0,
   then an immediate `savestate` load of the same slot, confirming both
   mods' patched instruction words survived the round trip. This
   inadvertently overwrote the user's own save in that slot (a real mistake,
   separate from this finding, and already apologized for).
3. Because their save was gone, the user started a fresh **New Game** —
   a genuine cold boot into the intro FMV, not a savestate resume.
4. The FMV froze on a static frame with the audio looping.

**Not established**: whether the immediately-preceding debug-server
save/load round trip is causally related, or whether this is purely a
cold-boot New Game bug that would have happened regardless (matching the
original report, which was about starting a New Game specifically). Worth
testing a New Game boot with no prior savestate activity in the same
session before concluding either way.

## What the telemetry actually showed

**First and most important finding: this is not a CPU/logic hang.**
`freeze_check` polled twice, 3 seconds apart, showed `psx_cycle_count`
advancing by ~116M cycles (~39M/sec — correct for the PSX's real clock) and
`frame_count` advancing by 205 frames in 3 seconds. Both `gl_present_ring`
and `present_ring` showed continuous, steady ~60 Hz output with the newest
entry only milliseconds old. Windows reported the process as `Responding`.
Every general-purpose signal available said the emulator was healthy and
running in real time — directly contradicting what was on screen (a frozen
frame, confirmed by a screenshot, with looping audio).

**The suspicious signal was in CD-ROM streaming, found via `cdrom_state`
(read the caveat above before trusting the first bullet)**:

- `int1_pended` — **not the general-purpose counter it was first taken for**
  (see the correction at the top of this document) — sat at exactly `40`
  across the same 2-second gap in which `frame_count`/`psx_cycle_count` kept
  advancing normally. Suggestive, not proof, of stalled delivery on its own.
- `ring_dropped` climbed continuously (+301 in 2s, ~150/sec) over the same
  window — data was being discarded at a steady rate while nothing new was
  arriving to replace it. (This counter's exact semantics also weren't
  independently re-verified against its increment site — treat as a lead,
  not confirmed proof, same caveat as above.)
- `pending: {"cmd":"0x09","active":0,"delay":0,"phase":1}` — command `0x09`
  (**Pause**) sitting mid-transition (phase 1) but not marked active — while
  `read_cmd:"0x1B"` (**ReadS**, the streaming-read command FMV playback
  uses) still showed `reading:1`.

**`cdrom_command_history` showed the exact sequence that produced this**,
all issued from the same low-memory function, `0x00000F40` — the same
address `freeze_check`'s `current_func` was pinned at during the freeze:

| seq | cmd | meaning |
|---|---|---|
| 697 | `0x02` Setloc → MSF 23:26:39 | issued while already mid-stream (`reading:1`) |
| 698 | `0x09` **Pause** | marked pending |
| 699 | `0x0E` Setmode | |
| 700 | `0x02` Setloc → MSF 23:26:39 (same target again) | |
| 701 | `0x1B` **ReadS** (streaming restart) | |

After this sequence, `int1_pended` never incremented again. No sector-ready
interrupt ever followed the restart.

## Leading hypothesis, not yet confirmed by reading the emulation source

This looks like a **Pause-landing-during-an-active-streaming-read** race in
the runtime's own CD-ROM emulation (`runtime/src/cdrom.c`), most likely
inside the BIOS's own CD retry/restart logic (the low-memory function at
`0x00000F40` is consistent with a resident kernel CD-driver stub, not game
code). The Pause/Setmode/Setloc/Read-restart pattern reads like a normal
BIOS-level "reseek and resume streaming" sequence — plausibly the same
mechanism used to loop a short attract/idle FMV segment, or to recover from
a transient read hiccup. Whatever `cdrom.c` does in response to a `Pause`
that arrives while `reading` is already `1`, it appears to leave the
emulated controller in a state where the subsequent `Setloc`/`ReadS` restart
never actually completes the handshake needed to raise the next `INT1`.

This is a hypothesis pointed at by directly-observed data (the command
sequence, the frozen `int1_pended`, the address match between the freeze
and the commands), not yet a confirmed root cause — `cdrom.c`'s actual
Pause/Read state-machine handling hasn't been read yet to find the specific
defect.

## Why this one has been so hard to catch before

Everything about this bug's signature explains the original difficulty:
- It is **not** a CPU hang, so nothing that watches for a stuck dispatch
  loop, an exception storm, or an unresponsive process would ever flag it.
- The game's own frame pacing and audio decode continue running completely
  normally, so naive fps/health telemetry looks perfectly fine throughout.
- It is specifically tied to a **cold-boot New Game** streaming-restart
  path, not a savestate resume — most of this project's own testing
  methodology (including this session's) defaults to savestates for speed,
  which would never exercise this exact BIOS retry sequence.
- It requires the debug server already attached with the right commands
  known in advance (`cdrom_state`, `cdrom_command_history`) — without that,
  it presents as nothing more than "the FMV froze," indistinguishable from
  a dozen other possible causes.

## Update, same day, live repro still running: the actual break is MDEC starvation, not `cdrom.c`

The freeze from this capture was **still live** when this was checked, which
made it possible to query the right things this time (`fmv_state`,
`mdec_state`) instead of over-reading `cdrom_state` alone. This changes the
diagnosis significantly from everything above.

**The CD-ROM is completely healthy.** Two `fmv_state` snapshots 3 seconds
apart: `cd_dataready_fires` 242902 -> 243348 (+446) and `cd_irq_delivered`
229784 -> 230231 (+447) — both climbing at a steady, normal rate. `xa_stream_
active` flipped 0 -> 1 between the two snapshots (consistent with the
reported looping audio: the XA stream is restarting rather than progressing).
The `cdrom.c` Pause/Read investigation above, including the already-merged
stale-Pause-`INT2` fix, is very likely **not implicated** — that subsystem is
working correctly throughout the freeze.

**`mdec_decode_count` was frozen solid** at exactly `803` across the same
3-second gap that CD delivery kept advancing in. `mdec_state` confirmed why:
`busy:0`, `input_count:0`, `decode_input_pos == decode_input_end` (both
`18688`), and **`decode_stop_reason: 3` = `MDEC_STOP_CB`** (enum in
`runtime/src/mdec.c`: `NONE=0, INPUT_END=1, CR=2, CB=3, Y0=4, ...`). Reading
the actual decode loop, this value is set here specifically:

```c
if (!decode_rle_block(cbblk, mdec.uv_quant, &pos, end)) {
    mdec.decode_stop_reason = MDEC_STOP_CB; break;
}
```

That is a stop **inside** a macroblock, not the clean top-of-loop
`MDEC_STOP_INPUT_END` a fully-finished chunk would produce. **MDEC was
handed one chunk of compressed video data that cut off partway through a
macroblock's chroma component, correctly stopped (this is not a decoder
bug — it did the right thing given incomplete input), and has not been
given anything more since — even though CD sectors keep arriving normally.**
`dma_out_words` (MDEC's own output counter) was also frozen at the same
value across both `fmv_state` snapshots, confirming no further output has
been produced since.

**Revised leading hypothesis**: the bug is in whatever mechanism is
supposed to feed MDEC's input via DMA as new CD sector data arrives — most
likely in `runtime/src/dma.c`'s MDEC-in channel handling, or in whatever
CD-read-complete callback is responsible for triggering the next MDEC push.
Something in that hand-off stopped after one (apparently truncated) chunk,
even though the CD side of the pipeline it depends on kept working. This has
NOT yet been traced — `dma.c` and the CD-to-MDEC hand-off have not been read
this session.

## What would confirm or fix this, not yet done

0. **Query `fmv_state` (not just `cdrom_state`) on the next reproduction.**
   `cd_dataready_fires` and `mdec_decode_count` are the actual general-purpose
   progress counters for "is a new frame's worth of data really arriving" —
   this is what should have been checked live instead of over-reading
   `int1_pended`. If `cd_dataready_fires`/`mdec_decode_count` are also frozen
   during a future repro, that would be real confirmation the stream stopped;
   if they're still advancing, the freeze is elsewhere entirely (e.g. MDEC
   decode stalling on already-buffered data, or a presentation-side issue
   after all) and the whole CD-ROM hypothesis below would need reconsidering.
1. **Read `runtime/src/cdrom.c`'s Pause-command handling in more depth than
   this pass covered.** What's confirmed so far: `exec_command()` already has
   a deliberate, documented fix (lines ~2059-2078) that cancels a Pause's
   pending completion the instant ANY new command arrives — including
   `ReadS` — specifically to prevent a stale Pause-complete `INT2` from
   firing mid-read (a real bug that hit other titles, per the comment's own
   MOHU/GT1 references). That fix looks like it should apply cleanly to this
   capture's sequence, which means the actual defect (if `fmv_state`
   confirms the stream really did stop) is likely NOT the stale-Pause-INT2
   case already handled, but something else — possibly in
   `read_continues_current_stream()`'s same-LBA-continuation check, or in
   `process_read_stream()`'s `warm_route_consumer_blocked()`/
   `accelerated_consumer_blocked()` gates (both checked by inspection this
   pass and not obviously implicated for PE's FMV mode bits, but not
   exercised against a real repro either). Trace whether `Setloc`/`ReadS`
   correctly re-arms `s_cd_timing_next_due` and whether `process_read_stream`
   actually gets called with nonzero `cycles` afterward.
2. **Reproduce deliberately**, isolated from today's savestate testing —
   several clean New Game boots, ideally with `cdrom_command_history`
   cleared and re-armed each time, to establish a real reproduction rate
   rather than relying on one accidental catch.
3. **Check whether `Setloc`/`ReadS` reuse the exact same MSF** (`23:26:39`
   in this capture) is significant — a Setloc back to the *current* read
   position (rather than a genuinely new target) might be the specific
   trigger, distinct from a normal seek-elsewhere-and-resume.
4. Confirm whether this is a `psxrecomp` framework bug (affecting any title
   that does this same BIOS-level Pause/restart pattern) or something
   specific to how Parasite Eve's FMV player uses the CD-ROM API — worth
   checking against another title (Tomba is already set up in this
   project) if a reliable repro is found.

## Raw data

Every JSON response behind this write-up (both rounds of diagnosis) is
preserved in `analysis/new-game-fmv-freeze-2026-09-13/raw-captures.md`,
including the full disassembly at the "stuck" address and the exact
`fmv_state`/`mdec_state`/`cdrom_sector_history` snapshots that produced the
corrected conclusion below. That file also documents that a savestate of
this exact session could not be taken (`"LLE run cannot load states"`) --
the game could not be preserved for reload, only these captures could.
