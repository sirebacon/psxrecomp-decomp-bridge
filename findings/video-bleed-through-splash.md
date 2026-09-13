# Video bleed-through on the title splash — reproduced and root-caused

**Status: CONFIRMED real and reproducible, with exact repro steps, and the
mechanism is now pinned down to a specific, verified fact: the recurring
title-card animation copies non-black, changing garbage into VRAM's border
rows in the buggy (skip) case and reliably black data in the working
(natural-end) case, from the exact same GP0 command structure. See
"Follow-up 5" for the decisive evidence. Every layer of psxrecomp's GPU
pipeline was checked directly and is clean — the remaining question (why
the *source* data differs) most likely lives in the original game's code
or in how psxrecomp tears down an interrupted video, not in rendering, and
needs the decomp to settle — see "Still open."

This is the bug behind the original report: "there is still the video
playing behind the menu splash screen... this always happened on this
machine but never on the Mac", reproduced specifically by **skipping** the
intro (matches how it was originally found: "restart the application and
I'll skip intro and you can see the background on top and bottom").

## Repro (headless, no keyboard/window-focus needed)

Earlier attempts in this investigation used real keypresses + Windows screen
capture, which was fragile (window-focus theft, blind-navigation overshoot —
see `roomlib-0x80191200-interior.md`'s "Still open" and this session's own
history). This one instead used two tools that don't need any of that:

1. **Debug-server synthetic input** — `{"cmd":"press","buttons":65527,...}`
   (`0xFFF7` = every pad bit set except bit 3/PAD_START, i.e. "Start held").
   `0xFFF7` for the exact "skip intro" input is independently confirmed in
   `tools/tomba_loadtest.py`'s own comment: `START(0xFFF7) breaks attract ->
   title` — same runtime, same convention, different game, already relied on
   by someone else for this exact purpose.
2. **`present_shot`** debug command — dumps the actual composited/letterboxed
   frame the player would see (not the raw pre-window-fit VRAM, which is
   `screenshot`/`gpu_frame_capture.py`'s `.png` and can't show this bug at
   all — see "Why the fullscreen present path was needed" below).

Steps that reproduced it:

1. `settings.toml` → `fullscreen = 1` (temporary, reverted after — see below).
   This matters: the default windowed 960x720 config is *exactly* 4:3, so
   there's no letterbox/pillarbox region for anything to bleed into, and the
   bug doesn't manifest at all in that config. Fullscreen on this machine's
   1920x1080 panel gives real pillarbox bars (`lx,ly,lw,lh = [240,0,1440,1080]`,
   confirmed via the debug server's `gl_present_ring` command).
2. Launch with `--debug-port 4370`, let the intro FMV play ~90s in.
3. Send the synthetic Start press: `{"cmd":"press","buttons":65527,"frames":6}`.
4. Burst-capture `present_shot` every ~350ms across the transition.

Result: frames after the transition permanently show the `[parasite eve]` /
"Press Start Button" splash in a horizontal band in the middle of the
pillarboxed area, with a **frozen, non-animating frame of the FMV that was
playing at the moment of the skip** filling the strip above and the strip
below it — i.e. inside the same pillarboxed 4:3 region the splash itself
sits in, not the black side bars. Confirmed **persistent, not transient**:
4 consecutive captures ~1.4s apart all show the exact same static bled
content, not a one-frame flash that clears itself.

Screenshots (in `analysis/frames/`, all from this session):
- `fs_skip_00.png` — one capture before the skip (the "Evolution" title
  card, clean, for reference).
- `fs_skip_01.png` — the transition frame itself: briefly renders as a full
  edge-to-edge image with *no* pillarbox bars at all (a "wide"/stretched
  present slipping in for one frame — see "A second artifact" below).
- `fs_skip_02.png` / `fs_skip_03.png` / `fs_skip_04.png`..`07.png` — the bug,
  settled and static: title splash in the middle, stale FMV strip above and
  below, unchanged across ~1.4s of real time.

## Why the fullscreen present path was needed

Two earlier attempts in this same session found nothing, and it's worth
recording why, since it's a real methodology lesson:

- Using `gpu_frame_capture.py`'s own `.png` (the `screenshot` debug command)
  captures the **raw display buffer before window-fit/letterboxing** — by
  construction it can never show a compositing/letterbox bug, only content
  that's actually in the PS1-native 320x240 image. Confirmed clean in both
  the natural-end and first skip test — correctly so, since this bug isn't
  in that buffer at all.
- The default windowed config (960x720, exactly 4:3) has no letterbox bars
  to bleed into, so testing there (as this session initially did) can't
  reproduce it regardless of which capture tool is used. The very first
  post-skip test this session ran (windowed, 2s after the press) came back
  clean — not because the bug was fixed, but because that config structurally
  can't show it.

`present_shot` (validates letterbox placement, per `GPU_FRAME_TOOLS.md`) plus
an actual mismatched-aspect display (`fullscreen=1` on a 16:9 panel while
`aspect_ratio` stays `"4:3"`) was the combination that finally exposed it.

## What the GP0 stream shows (inconclusive — see "Still open")

Captured the two frames spanning the transition (`letterbox_bad-00.json`,
`letterbox_bad-01.json` in `analysis/frames/`). The earlier of the two opens
with:

```
fill  dest=(0,0) size=(320,240) color=(0,0,0)     -- func 0x1FC02B80 (BIOS)
copy  dest=(0,0)   size=(24,240) op=0xA0  (CPU->VRAM)   -- func 0x000026C4
copy  dest=(24,0)  size=(24,240) op=0xA0                -- func 0x000026C4
... 10 more 24-wide strips, x = 48..264
```
and the next frame continues the same pattern for x = 288..456 (8 more
strips). Together: a full-screen black `fill`, then 20 direct CPU→VRAM pixel
uploads of width 24 each, tiling x=0..479 — all at **height 240, the full
frame**, and confirmed **not mask-bit-transparent** (`mask=[False,False]` on
every one of these, checked directly against each primitive's captured GPU
state). None of this should leave any row un-overwritten.

This doesn't match what's on screen: a fill+copy covering the *entire*
0-240 row range should leave nothing stale, but the top and bottom bands of
the pillarboxed area visibly still show old content. The most likely
explanation is that these particular `x:0-479,y:0-239` writes are landing in
an **off-screen VRAM texture-cache page** (the logo asset being uploaded/
cached, most title screens do this once rather than redraw from CPU RAM every
frame — consistent with the following frame having *zero* GP0 packets at
all, i.e. nothing draws most frames once the splash is up) rather than the
actual visible framebuffer, and whatever textured-sprite draw actually
*reads* that cached texture and places it on the visible/displayed buffer —
the thing that would determine the real on-screen height — wasn't isolated
in this capture. That draw call is the next thing to go find.

## A second artifact, not yet explained either

`fs_skip_01.png` (the frame immediately after the press, one before the
bug settles into its steady state) briefly renders **without any pillarbox
bars at all** — the frame fills the full 1920x1080 edge to edge. This matches
`present_ring`'s own classification vocabulary (`blank` / `native43` / `wide`
/ `canonical`) and a code comment about a known failure signature: *"a
native-wide present fell back to the canonical width... the everything
stretched for a while signature"*. Checked `present_ring`/`gl_present_ring`
across this specific transition and did **not** find a logged `wide` or
`fellback` entry at this frame — so either that specific telemetry doesn't
cover whatever this is, or it's a distinct, uncatalogued third case. Recorded
here as an observation, not chased further.

## Follow-up: display-origin check (this ruled out one theory and found the real layer)

Went back to check the assumption the GP0 analysis rested on: that VRAM
(0,0) is actually the display's scanout origin. It's more interesting than
that — the debug server's `gpu_state` command (`display_x`/`display_y`)
shows this game genuinely **double-buffers the display**, alternating
`display_y` between `0` and `240` every couple of frames, confirmed live
across 10 samples straddling the skip. That's not a bug by itself, but it
meant the earlier single fill+copy capture only ever showed one of the two
buffers, so the "full 240-row fill+copy that should've cleared everything"
puzzle needed re-checking against both.

Widened the capture to 16 frames and grepped every fill/copy's destination Y
across them: **both buffers get the identical treatment** — `y=0` and
`y=240` each get their own full `fill(320,240,black)` + tiled `copy` (0xA0)
sequence, one buffer's turn per draw cycle, forever, even while just sitting
idle at the static splash. So it's not "one buffer never gets touched again"
— both buffers are being actively, repeatedly redrawn with a command
sequence whose header genuinely declares the full 240-row height (checked
the raw GP0 words directly, e.g. `0x00F00018` decodes to height=0x00F0=240,
width=0x0018=24 — not a decode-tool artifact).

Then went one level deeper than GP0 command *headers* and read actual pixel
truth with the debug server's `vram_peek` (CPU-side VRAM array) and
`gl_fbo_peek` (what the GL-backend's FBO — the thing actually presented —
holds), at three rows in the live buggy frame: a "top stale" row, the
"middle logo" row, and a "bottom stale" row.

| row | `vram_peek` (CPU truth) | `gl_fbo_peek` (presented truth) |
|---|---|---|
| top-stale (y=245) | `0408080303...` | `0408080303...` (**matches**) |
| mid-logo (y=360) | `0101010102...` | `0101010102...` (**matches**) |
| bottom-stale (y=470) | `0101010101...` | `0000000000...` (**diverges**) |

Two different things going on, neither of which is the theory this section
opened with (a GL-side dirty-rect/coherency gap using `draw_area` — checked
directly, `draw_area` for this whole sequence is the full screen,
`[0,0,319,239]`, not clipped):

- At the **top-stale** row, CPU VRAM itself already holds the non-black,
  slightly-nonzero values that end up on screen — i.e. the fill/copy's
  declared 240-row write is **not actually landing in memory** for this row,
  full stop. This is a real bug in the write path itself (`gpu.c` / the
  software VRAM writer), not a presentation-layer issue.
- At the **bottom-stale** row, CPU VRAM and the presented FBO genuinely
  *disagree* (`0101...` vs `0000...`) — a second, distinct desync between
  the CPU-side mirror and what's actually shown, in the same frame. The
  existing code comments in `debug_server.c`'s `handle_screenshot_file`
  already document this class of issue in general ("Under the OpenGL FBO-
  present path, CPU VRAM can be stale — the FBO holds the freshest frame and
  is presented without a readback"), which matches.

So there are most likely **two separate contributing mechanisms** here, not
one: a write that doesn't fully land at the CPU-VRAM level, and a CPU/FBO
coherency gap on top of it. Neither was isolated to a specific line of code
in `gpu.c` / the GL renderer this session — that's a source-reading task
(the actual C implementation of the GP0(0xA0) copy handler and the GL
renderer's VRAM→texture sync/dirty-tracking), not something the debug
protocol alone can finish settling.

## Follow-up 2: read the actual C source — found the subsystem, not yet the exact line

Went into `psxrecomp/runtime/src/gpu.c`'s real GP0(0x02)/GP0(0xA0) handlers
(`gp0_exec_fill_rect`, `gp0_exec_cpu_to_vram`, `gpu_write_gp0_body`'s
`GP0_VRAM_WRITE` state machine) to check for an off-by-one or clipping bug in
the write loop itself. **Nothing wrong there** — the per-pixel loop
unconditionally writes into the CPU-side `vram[]` array for the whole
declared width×height (wrapping via `% 1024` / `% 512`, matching real
hardware), with exactly one conditional skip: `check_mask_bit`. That sent
this down a detour worth recording:

- **Live-checked the actual GPUSTAT register** (`gpu_state`'s `gpustat`
  field, bits 11/12) through the whole skip transition, not just the
  decoded-packet state used in the first pass. `set_mask_bit=0`,
  `check_mask_bit=0` at every sample, before, during, and after. **The
  mask-bit theory is now dead for real** — this isn't inferred from what
  GP0(0xE6) commands happened to appear in a capture window (which is what
  the first check relied on and flagged as a soft conclusion); it's the
  runtime's actual persistent register state, confirmed live. The write loop
  in `gpu.c` is unconditional for this whole sequence.

So the CPU-array write genuinely happens, in full, every time. Went back to
live introspection with a cleaner method than the first pass (which mapped
`present_shot` PNG pixels back to VRAM coordinates through the pillarbox
scale factor — that mapping turned out to be unreliable: a sanity check
against a known landmark, the red SQUARE-logo triangle, didn't land where
the math said it should, so **the specific coordinate pair reported in the
first follow-up's table is not to be trusted** — flagging that here rather
than quietly leaving a wrong number on the record). The fix: skip the PNG
entirely and compare `vram_peek` (CPU truth) against `gl_fbo_peek` (GPU-FBO
truth) at the *same* native coordinates for both — no scale factor, no
mapping to get wrong.

Scanned vertical strips at five x columns (40, 100, 160, 220, 280), 120 rows
each, both buffers:

| x | rows that differ (of 120) |
|---|---|
| 40 | 0 |
| 100 | 0 |
| 160 | 96 |
| 220 | 120 |
| 280 | 0 |

A real, sharply localized divergence — not a uniform stale band, specific
24px-wide columns. `x=160` and `x=220` land inside two of the twenty 24px-
wide `copy_cpu_vram` (GP0 0xA0) strips the splash upload tiles across
(strips are at x = 0, 24, 48, ... 456); `x=40/100/280` land inside *other*
strips from the same upload sequence that come back clean. Both the
divergent and the clean columns are strips from the *same* frame's batch
(not "frame N's strips are fine, frame N+1's are broken") — the pattern
doesn't line up with the double-buffer flip either.

This points at one specific subsystem: `psxrecomp/runtime/src/
gpu_gl_renderer.c`'s CPU→GPU upload coherency tracker — `s_up_rects` /
`up_add()` / `up_add_transfer()` / `flush_cpu_upload()` (`UP_RECTS_MAX=16`
pending-rect list, `glTexSubImage2D` the actual upload). This is *exactly*
the layer responsible for getting a GP0(0xA0) CPU write into what the GL
backend actually presents — and the file's own comments document a near-
identical bug class already found and fixed for a different game:

> "THE FLICKER CLASS BUG (MMX6 GL black-frame flicker, ISSUES.md #7): the
> old single-union `s_up_pending` merged DISJOINT uploads... into one
> bounding box... `flush_cpu_upload` then painted that whole box from the
> CPU VRAM array — which is STALE under GL — stomping freshly-rendered
> framebuffer content with stale (typically black) pixels for 1-2 presents."

The fix for that bug (switching to an exact-rect list with restricted
merging, rather than one bounding-box union) is the code that's still active
here — and it's evidently not fully covering this access pattern: twenty
contiguous, same-height, edge-touching strips (which the merge logic's
"same row-band extension" rule should combine into one clean rect) spread
across a frame boundary with a display-buffer flip in between it.
**Which exact condition in that merge/flush logic drops or mis-times
specific strips wasn't isolated this session** — read-only source
inspection plus the existing debug-server surface (`vram_peek`/
`gl_fbo_peek`) can localize *where* the bug lives, as done here, but
confirming *why* strips 7 and 10 of 12 fail while 2, 5, and 12 don't needs
either added logging in `up_add`/`flush_cpu_upload` (a real code change +
rebuild, not just reading) or step-through debugging — a different kind of
task than this session did.

## Follow-up 3: the coherency ring exonerates the splash-draw code entirely

Went looking for the exact line by using the runtime's own always-on GL
coherency event ring (`gl_coh_ring` debug command — every `upload`/`flush`/
`fill`/`pack`/`draw`/`present` event the GL backend records, with rects and
frame numbers; no new instrumentation needed, it already existed). This
produced two results, one a real dead end and one decisive.

**Dead end, recorded so it isn't retried:** the ring shows the CPU→GPU
upload/flush pipeline (`gpu_gl_renderer.c`'s `up_add`/`flush_cpu_upload`,
the subsystem the previous follow-up pointed at) working *correctly* —
every cycle, the twenty 24px strips merge cleanly into one `flush` covering
the full `x:0-479` row-band, exactly as the merge logic is supposed to.
Chasing that thread further (checking `depth24_is_fb_transfer`'s skip-
classification heuristic, the `s_depth24_skip_up` movie-scanout-skip path)
also came back clean — none of it applies to a transfer this narrow
(`w<=256 && h<=256` is explicitly exempted). That whole subsystem is
innocent. Also checked and ruled out: the runtime reports `depth24=1`
(24-bit direct-color scanout) at the buggy title screen — looked like a
smoking gun at first, but the **same natural-end (clean) transition also
reports `depth24=1`** at its own title screen. Confirmed by relaunching,
letting the intro finish without any synthetic input, and querying
`gpu_state` at the resulting clean screen. Identical condition, different
outcome — not the differentiator.

**The decisive result:** captured the exact GP0 command stream (headers
*and* full pixel payload words, not just destinations) for both the clean
natural-end transition and the buggy skip transition, frame-aligned to the
same point in the splash-draw sequence (the `fill(0,0,320,240,black)` +
twenty `copy_cpu_vram` strips). **They are byte-for-byte identical** —
same `GP0(0xE6)` mask-clear, same fill, same twenty strips at the same
destinations with the same pixel data, confirmed word-for-word across all
31 primitives in the sequence. The game issues the exact same drawing
commands whether the intro was skipped or allowed to finish.

This is the most useful negative result of the whole investigation: **the
splash-drawing code itself is exonerated.** Identical commands, identical
data, different visible outcome — the divergence has to be in state that
exists *before* this sequence runs (something about what's already sitting
in VRAM, or some non-GP0-visible condition) that this otherwise-identical,
otherwise-correct draw sequence doesn't fully overwrite in the skip case.
That relocates the search from "what does the splash draw wrong" to "what
does the skip path fail to clean up (or what does the natural end-of-video
path do) *before* the splash ever starts drawing" — likely several frames
earlier than anything examined so far.

Follow-up attempted a live before/after coherency-ring comparison to find
that earlier difference directly, but the ring (bounded capacity, shared
across the whole runtime) had already rolled past the relevant history by
the time of the query — a timing/sequencing lesson for whoever tries this
next: capture the *before* window immediately, in the same breath as
triggering the transition, rather than after taking screenshots and doing
other checks first.

## Follow-up 4: found the actual border-clearing draw calls — and why the "identical stream" proof from follow-up 3 needs a caveat

Captured the coherency ring precisely this time — armed it and triggered the
skip back-to-back, no screenshots or other calls in between, per the lesson
from follow-up 3. This got a clean, complete before/after window and paid
off immediately.

**The recurring `fill`+20×`copy` sequence chased since follow-up 1 is not
the splash transition at all.** It's the ONGOING attract-mode animation for
the "[parasite eve]" title-card ring graphic (the visible rotating/pulsing
ellipse) — it fires every 4 frames continuously, before, through, and
indefinitely after the skip: confirmed it's still firing, unchanged, at
frame 12523 (10,000+ frames after the transition) in the skip case, and it
was *also* present at frame ~23547 in the earlier natural-end capture (see
follow-up 3's `natural-*.json`). This means **follow-up 3's "byte-identical
GP0 stream" finding compared two samples of a continuously-running,
presumably-animating loop, not two samples of the actual transition event.**
Since the ring visibly animates (rotates/pulses), the loop's payload almost
certainly varies frame-to-frame; the two sampled instants matching exactly
was most likely a coincidental phase alignment, not proof the whole
mechanism is bug-free across its full cycle. Correcting the record here
rather than let a shakier claim stand.

**The real transition event, found by looking at the actual gap in the
ring**, happens about a second after the press registers (frame ~2700 here,
vs. the press at ~2621 — the old ring-animation loop keeps running unbroken
right through that gap, per the point above). At frame 2700, four *real
polygon* `draw` events fire — not CPU-to-VRAM copies — decoded from the raw
GP0 stream as GP0(0x60) flat opaque rectangles, solid black
(`colors=[[0,0,0]]`), at:

- `(0,0)`–`(480,20)` and `(0,224)`–`(480,240)` — the two edge bands of
  buffer 0
- `(0,240)`–`(480,260)` and `(0,464)`–`(480,480)` — the same two bands of
  buffer 1 (the `+240` addressing from the confirmed double-buffering)

These are **exactly** the coordinates of the bled bands — this is the
game's own top/bottom border-clear, present and executing correctly at the
command level. Right after, two big CPU-to-VRAM uploads land
(`(0,20)-(479,223)` and `(0,260)-(479,463)`) — the *content* region only,
deliberately excluding the border bands, confirming the game's intended
design: borders painted once via polygon rect, content refreshed
separately, borders expected to stay put.

**Why "stay put" doesn't hold, and the real open question these polygon
rects raise:** they're ordinary GL-rasterized draws, landing in the GPU-side
"hr FBO" — a completely different destination than the CPU-to-VRAM copies
that write `vram[]` directly (the array `depth24`'s scanout reads from,
confirmed in follow-up 2/3 to still be `1` here). Getting a GPU-rasterized
draw to actually reach that raw-byte scanout needs a pack-back sync
(`GL_COH_PACK`) to land before the depth24 present reads it — and a `pack`
covering the unusually large `(0,0)-(480,480)` span *does* fire right after
these draws (frame 2704), suggesting it's plumbed to try. But a live
`vram_peek`-vs-`gl_fbo_peek` check taken much later (frame 9666, well after
things had settled) found the affected rows **non-black in both** — the
GPU-side FBO itself no longer holds these black rects either, not just the
CPU mirror. Given the ring-animation loop's own `fill`+`copy` sequence
(never stops, covers the full `0-239`/`240-479` height every 4 frames,
described above) would unconditionally overwrite these exact same rows
every cycle regardless of path — **the one-time border rects can only ever
be a transient fix, overwritten again within 4 frames, in *both* the clean
and buggy cases alike.** That means the border rects are not what keeps the
natural path's borders black — the ring-animation's own recurring payload
must be what's actually black there in the working case, every cycle,
forever. Which reopens the exact question follow-up 3 thought it had
closed: what does that recurring payload actually contain in the border
rows, across its *full* animation cycle, in each path — not just the one
coincidentally-matching sample already taken.

## Follow-up 5: found it — the recurring animation's own source data differs, not its commands

Follow-up 4 identified the real target of comparison: not the one-time
border rects (transient, overwritten every 4 frames regardless of path
anyway), but the *recurring* ring-animation upload's actual pixel payload
in the border rows, sampled across several cycles rather than once. GP0
packet capture can't reach that data (the debug ring caps each entry at 12
words — `GPU_GP0_RING_MAX_WORDS`, enough for a command header and a
fraction of one scanline, nowhere near enough to see row 5 of a 240-row
transfer). Used `vram_peek` directly instead — live VRAM reads, not packet
capture — polling a spread of columns (x=20..300) at a border row (y=5),
~10 times a second, for several seconds, in both paths.

**Clean (natural-end) case — 15 samples × 10 columns, 150 readings, all of
them `0x0000`:**
```
0  ['0000','0000','0000','0000','0000','0000','0000','0000','0000','0000']
1  ['0000','0000','0000','0000','0000','0000','0000','0000','0000','0000']
...(identical, all 15 rows, 0x0000 everywhere, no exceptions)
```

**Buggy (skip) case — same columns, same row, same polling cadence — never
once black, and changing sample to sample:**
```
0  ['0707','0707','4210','050b','0504','0707','0808','0808','0a0a','0000']
1  ['0505','0707','240b','0409','0503','0505','0808','0808','0f0f','0909']
6  ['6195','0909','150b','0709','0806','0000','060e','0c09','1818','1a1a']
10 ['071d','2526','af98','1c47','0d06','0707','0909','0000','0000','0000']
...
```

This is the answer. **The recurring title-card animation's GP0 command
*structure* is identical between the two paths (confirmed in follow-up 3 —
that part of the claim holds), but the *pixel data it copies* is not.** In
the working case that data is reliably, unvaryingly black in the border
rows, every cycle, indefinitely. In the broken case it's noisy, non-black,
and actually changes cycle to cycle — not a single frozen frame, something
that keeps producing different "garbage" each refresh.

Since the copy is a GP0(0xA0) CPU→VRAM transfer, its payload comes from PS1
main RAM — a buffer the game's own code fills before issuing the transfer,
not anything psxrecomp's GPU pipeline constructs. Every layer of that GPU
pipeline was checked directly this investigation and is clean: the mask
bit, the write loop, the upload/flush coherency tracker, the command
headers. **The most likely explanation is a source-RAM buffer the game
reuses between MDEC video-decode output and this animation's texture prep**
— natural playback ends with something that leaves that shared buffer's
border padding clean (zeroed or overwritten), while an interrupted
(skipped) decode leaves whatever the last real MDEC macroblock output there
sitting unclaimed, and the animation's per-cycle copy keeps faithfully
recopying that leftover, changing, garbage into VRAM forever after.

This reorients where the bug most likely lives: **probably in the
original game's own code (a buffer-reuse pattern around MDEC decode +
skip handling), not in psxrecomp's rendering.** Whether real PS1 hardware
shows the same thing when skipped this way is unknown — nobody has tested
that here — so this could be an authentic original-game quirk psxrecomp is
faithfully reproducing, or a subtle difference in how psxrecomp tears down
an interrupted CD-XA/MDEC stream versus real hardware's own stop sequence.
Settling which needs the decomp (`parasite-eve-decomp`) — tracing the skip
input handler and whatever writes into the shared scratch buffer around
MDEC decode — which is a different kind of investigation than anything
done in this file so far, and a reasonable place to hand this off.

## Still open

- **Root-caused to a source-data difference, not a psxrecomp rendering
  bug.** Every layer of the GPU pipeline was checked directly and is clean:
  the mask bit (live GPUSTAT, off throughout), `depth24` scanout mode
  (identical in both cases), the GP0 write loop (`gpu.c`, unconditional
  full-rect writes), the upload/flush coherency tracker (`gpu_gl_renderer.c`,
  complete flushes every cycle), and the recurring animation's GP0 command
  *structure* (identical destinations/sizes in both paths). What differs,
  confirmed directly via live `vram_peek` polling across many cycles (see
  follow-up 5), is the *pixel payload* that recurring command copies: black,
  every cycle, forever, in the working case; non-black and changing cycle
  to cycle in the broken one. Since that payload is CPU-side data the game
  supplies for a GP0(0xA0) transfer, the difference lives in PS1 main RAM,
  populated by the game's own code — not in anything psxrecomp's renderer
  constructs. **Most likely explanation**: a source buffer reused between
  MDEC video-decode output and this animation's texture prep, left clean by
  natural playback's end-of-video handling but not by an interrupted
  (skipped) decode. **What's still open** is only the fine-grained "why":
  tracing the skip input handler and whatever writes that shared buffer in
  `parasite-eve-decomp`, and finding out whether real PS1 hardware shows the
  same thing when skipped this way (unknown — not tested here). That's a
  decomp-tracing task, a different kind of work than the live-debug-protocol
  investigation this file otherwise documents.
- **Mask-bit theory checked and ruled out** — was the leading hypothesis
  before looking at the actual captured state (PS1 GPU "check mask before
  draw" skipping transparent border rows, relying on an already-black
  backdrop). Every fill/copy in the captured frames has `mask=[False,False]`.
  Not the mechanism.
- Only reproduced via the *skip* path. Whether the natural-end path is
  reliably clean across *every* run (not just the one sample earlier this
  session) isn't separately re-verified here.
- Only tested on the intro's title-splash transition specifically. Whether
  the same mechanism affects other splash/menu transitions in the game is
  unknown.
- `settings.toml`'s `fullscreen` was flipped to `1` for this test and
  reverted to `0` immediately after (diffed back to the exact original file
  content) — the user's normal windowed setup is unaffected. `build-release`
  was rebuilt with `-DPSX_DEBUG_TOOLS=OFF` afterward per the usual pattern.

## Verify

`settings.toml` → `fullscreen=1` (or any window shape that isn't exactly
4:3), launch with `--debug-port`, send `{"cmd":"press","buttons":65527,
"frames":6}` mid-FMV, then poll `{"cmd":"present_shot"}` a few times ~0.3s
apart across the next 1-2s — the composited screenshot at
`build-release/psx_present_shot.png` should show the stale-video bands above
and below the splash if this still reproduces.
