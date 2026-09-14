# Raw diagnostic captures — New Game FMV freeze, 2026-09-13

Companion to `../../new-game-fmv-freeze-cdrom-capture.md`. This file is the
actual JSON responses behind that write-up, preserved permanently since the
live session could not be saved as a savestate (see the last section).

Boot context: launched via `Parasite_Eve.exe --no-launcher --disc "...Disc
1).cue"`, `PSX_DEBUG_TOOLS=ON`, retail SCPH1001 BIOS. Froze during the intro
FMV after a fresh New Game boot (the user's own save states had just been
lost to an unrelated testing mistake, forcing a New Game start).

## freeze_check, two snapshots 3s apart (early in the investigation)

```json
A: {"current_func":"0x00000F40","in_exception":1,"exception_entries":108320,"exception_reentry_blocks":14091,"i_stat":"0x00000001","dispatch_count":0,"psx_cycle_count":9015348236,"frame_count":16140,"nestgate_rfepend":19654}
B (+3s): {"current_func":"0x00000F40","in_exception":0,"exception_entries":145817,"exception_reentry_blocks":19859,"i_stat":"0x00000001","psx_cycle_count":9131592960,"frame_count":16345,"nestgate_rfepend":19859}
```

`psx_cycle_count` advanced ~116M cycles, `frame_count` advanced 205 frames —
both normal real-time rates. `current_func` pinned at `0x00000F40`
throughout (later disassembled: a generic BIOS kernel exception-vector
trampoline hit on every interrupt, NOT diagnostic on its own — see the
correction in the main write-up).

## freeze_check, rechecked much later (same session, freeze still ongoing)

```json
{"current_func":"0x00000F40","exception_entries":998003,"exception_reentry_blocks":151494,
 "psx_cycle_count":77647225672,"frame_count":137724,"nestgate_rfepend":151494}
```

Same address, same pattern, just far more accumulated — consistent with
continuous interrupt activity over a long real-elapsed freeze duration, not
a new development.

## gl_present_ring / present_ring (steady ~60Hz, right up to "now")

```json
gl_present_ring tail: ids 18732-18751, "cpu" tag, timestamps 328253..328570ms
  (now_ms:328580 — newest entry only 10ms old)
present_ring tail: ids 19155-19174, mode "native43", 320x240, sequential
```

Both confirm the present pipeline itself was running continuously and
normally throughout — this is not a rendering/present-layer freeze.

## cdrom_state, two snapshots 2s apart

```json
A: {"int1_pended":40,"ring_dropped":61003,"read_msf":[23,34,47],
    "last_sector":{"lba":105946,"frame":30084},
    "pending":{"cmd":"0x09","active":0,"phase":1},"read_cmd":"0x1B","reading":1}
B (+2s): {"int1_pended":40,"ring_dropped":61304,"read_msf":[23,27,36],
    "last_sector":{"lba":105410,"frame":30230},"reading":1}
```

`int1_pended` unchanged (later shown to be a narrow counter, NOT proof of a
stalled stream — see correction). `ring_dropped` climbing steadily. Command
history (below) shows what produced this state.

## cdrom_command_history (the actual producing sequence, newest 5 of 702 total)

```json
seq697: cmd=0x02 Setloc [0x23,0x26,0x39] reading=1 read_cmd=0x1B func=0x00000F40
seq698: cmd=0x09 Pause pending_cmd=0x09 pending=1 func=0x00000F40
seq699: cmd=0x0E Setmode [0xE0]
seq700: cmd=0x02 Setloc [0x23,0x26,0x39] (same MSF again)
seq701: cmd=0x1B ReadS reading=1 pending_cmd=0x09 pending=0
```

Full 702-entry response (49KB) was captured but not preserved verbatim
beyond this tail — the tail is what mattered for the write-up. Re-capture
in full on the next reproduction if earlier entries turn out to matter.

## fmv_state, two snapshots 3s apart (the corrected, decisive evidence)

```json
A: {"mdec_decode_count":803,"xa_stream_active":0,
    "cd_dataready_fires":242902,"cd_irq_delivered":229784}
B (+3s): {"mdec_decode_count":803,"xa_stream_active":1,
    "cd_dataready_fires":243348,"cd_irq_delivered":230231}
```

`cd_dataready_fires`/`cd_irq_delivered` climbing normally (+446/+447 in 3s)
— CD-ROM delivery confirmed healthy. `mdec_decode_count` frozen solid.
`xa_stream_active` toggled 0->1 (consistent with looping audio).

## mdec_state (queried once the CD-ROM was ruled out)

```json
{"command":"0x32002480","expected_halfwords":0,"input_count":0,"busy":0,
 "input_full":0,"decode_macroblocks":275,"decode_blocks":1651,
 "decode_stop_reason":3,"decode_input_pos":18688,"decode_input_end":18688,
 "dma_in_words":1256960,"dma_out_words":52800}
```

`decode_stop_reason:3` = `MDEC_STOP_CB` (enum in `runtime/src/mdec.c`).
`decode_input_pos == decode_input_end` — MDEC correctly finished decoding
everything it was given (mid-macroblock, at the Cb/chroma component) and
has received nothing since.

## cdrom_sector_history (most recent entry, confirms video sectors ARE arriving)

```json
seq328839 lba=105994 frame=134263 xa_file=1 xa_channel=1 xa_submode=0x48
  xa_coding=0x00 data_delivered=1 xa_audio_delivered=0 skip_reason=0
```

`xa_submode:0x48` has the Video bit (0x40) set, not Audio (0x20) —
confirms this is a video-tagged sector, and `data_delivered:1` shows it WAS
delivered to the CPU via the normal path. Rules out a CD-XA filter mismatch
(`filter_file:0`/`filter_channel:0` vs. this sector's `xa_file:1`/
`xa_channel:1`) as the cause — filtering only gates the hardware
auto-XA-audio fast path, not regular data/video sector delivery.

## mem_words at 0x00000F00-0x00000F5C (the "stuck" address, disassembled)

```json
{"addr":"0x00000F00","words":["0xAC43FFFC","0x08001A9C","0x00000000","0x3C1A0000",
 "0x275A0C80","0x03400008","0x00000000","0x00000000","0x3C010000","0x03E00008",
 "0xAC2475D0","0x3C020000","0x24426CF4","0x3C010000","0x03E00008","0xAC2275D0",
 "0x241A0100","0x8F5A0008","0x00000000","0x8F5A0000","0x00000000","0x23440008",
 "0x8C820088","0x00000000"]}
```

The word at `0x00000F40` (`0x241A0100`) decodes to `li $k0, 0x0100` — the
start of a generic BIOS kernel-vector trampoline (tag a call, jump to a
shared dispatcher), consistent with being hit on any interrupt system-wide.
Not specific to CD/video handling — this is why `current_func` sitting here
is not itself diagnostic (see correction in the main write-up).

## hle_dump (checked twice, unchanged both times)

```json
{"backend":"HLE (LLE fallback)","boot_skip":1,"boot_turbo_active":0,"total":13768}
```

Identical both times, hours apart — not a mid-session change.

## Savestate capture attempted, refused

```json
{"cmd":"savestate","op":"save","slot":90}
-> {"ok":false,"error":"savestate request refused (LLE run cannot load
    states; check slot / configuration / netplay host)"}
```

Could not snapshot this exact frozen session for later reload. The refusal
itself is informative: it means the guest is currently executing genuinely
low-level-emulated BIOS code (not the HLE fast path) at the moment of the
freeze — worth remembering as a property of the bug, not just an
inconvenience. A savestate taken *earlier* in the same session (slot 0,
during unrelated mod-verification testing, before the New Game boot) DID
succeed — so the refusal is tied to the current guest execution state, not
a blanket property of this build/BIOS configuration.
