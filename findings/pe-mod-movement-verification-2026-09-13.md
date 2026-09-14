# PE mod session, 2026-09-13: inventory floor confirmed, movement speed unresolved, real toolchain bug found

Follow-up to `pe-qol-mod-roadmap.md`'s "Increased Out-of-Combat Run Speed" and
"Increased Storage" items. One shipped clean; the other turned into a much
deeper investigation that ended without a confirmed fix, but did surface a
real, previously-unknown toolchain bug plus a reusable verification method
for future mod work in this game.

## Confirmed working: personal inventory floor

**Root cause of the original "no dice" report**: `g_AyaInventorySlotCount`
(`0x800C0E0C`) is not backed by any static instruction or data byte in the
shipped EXE. It's populated at runtime from a 99-entry per-level progression
table (10 slots at level 1, growing smoothly to 46 by level 99 — captured
live, every entry) whose base address is itself resolved through a
boot-time-computed pointer indirection. Every byte behind that table reads
`0x00` in the static disc image — there is nothing to patch as data, and the
two "personal-inventory instructions" patched earlier in this session had
actually hit the *ceiling clamp* in `Inv_GetAyaSlotLimit`/
`Inv_SetAyaSlotCount` (`0x80052F70`/`0x80052F24`), not the per-level base
value, so they never changed what a level-1 New Game actually starts with.

**Fix, verified working in-game**: rather than reverse-engineer the table
generator, a small vblank-hook plugin
(`src/mods/pe_inventory_floor.c`, package
`pe.enhancement.personal-inventory-floor`) polls the live capacity byte every
frame and raises it to a configurable floor (default 40) whenever the game
has just set it lower — savestate-safe by construction, since a vblank hook
re-runs continuously rather than firing once at boot, and it backs off once
the natural curve exceeds the floor around level 75+. Confirmed showing
`40` in the in-game inventory screen on the user's existing save, no New
Game required.

## Unresolved: out-of-combat run speed

**What's confirmed correct, at every static layer, across three attempts
(5x→8x, then 8x→20x, then a same-day 20x re-verification)**:
- `disc/SLUS_006.62` binary-patched at `0x800185C0` (the `lui $a0` in
  `Entity_ComputeVelocity`, `0x80018598`), each time verified by re-reading
  the file.
- `generated/SLUS_006.62_full_02.c` regenerated and directly grepped —
  `cpu->gpr[4] = 0x0014 << 16;` present, correctly reflecting the disc edit.
- Object file (`SLUS_006.62_full_02.c.obj`) rebuilt after the source, EXE
  rebuilt after the object — full timestamp chain checked, no staleness.
- Live process confirmed running the fresh build (`Get-Process` StartTime
  vs. `Get-Item` LastWriteTime on the exe).

**What was never confirmed**: that any of this changes actual gameplay
speed. Every live-motion capture this session (`FieldActor.motion_z` at
actor `+0x68`/`+0x70`, walked to via `g_PlayerEntity`/`g_CurrentEntity` at
`0x8009D254`/`0x8009D2F0`) returned the *same* frozen value —
`0xFFE98000` (-22.5 in Q16.16) — regardless of which multiplier was
actually compiled in (8x, 20x, or even a diagnostic 1000x swapped in
specifically to make any real effect unmissable), and regardless of a
completely fresh process boot in between. `pos_x`/`pos_z` for that same
actor were observed static across 15+ second windows during which the user
reported actively holding the run key in open space.

That pattern — identical output regardless of a dramatically different
input, across independent process lifetimes — means the test was not
measuring what it was built to measure. It does **not**, on its own, mean
the movement fix doesn't work.

### What was ruled out this session

- **Stale/wrong `[[patch]]` manifests actively fighting the fix**: real bug,
  found and fixed. `pe.enhancement.faster-movement`'s original manifest
  still targeted the pre-fix baseline (`expected` = original 5x bytes,
  `replace` = the old 8x encoding) and was enabled in the user's
  `mods/state.toml`, so it was rewriting the correct EXE-baked value back
  down to 8x in live RAM on every boot. Retired (see the manifest's own
  retirement note) along with the equivalent stale storage-cap manifest.
  Superseded by a fresh `pe.enhancement.faster-movement-live` package using
  the framework's declarative `main_exe` `[[patch]]` mechanism (which calls
  `dirty_ram_mark_executable_range()` via `apply_main_write()` in
  `mod_runtime.cpp` — the correct invalidation path), confirmed live via
  `mem_words` showing `0x3C040014` in RAM after boot. This was a real,
  necessary fix, but did not by itself resolve the "no dice" report.

- **A silently-broken overlay autocompile toolchain**: real bug, found and
  fixed, and the most likely actual explanation for a session's worth of
  confusing results. `PSX_MINGW_BIN` was set (across every relaunch this
  session) to a path that doesn't exist
  (`D:\msys64\mingw64\bin`), which meant every `gcc` invocation this
  session silently resolved to whatever "gcc" is on PATH instead — the
  `cmake-clang-v1` retcomm pack (`C:\Users\...\retcomm\toolchains\
  cmake-clang-v1\latest\bin\gcc.exe`, a clang wrapper), which cannot parse
  `--force-interior` (`clang-22: error: unknown argument:
  '--force-interior'`) and rejects the whole command. Confirmed via
  `autocompile_status`'s `output_tail` showing the actual clang error and
  `degraded:1`. **This means every overlay-driven code path this whole
  session ran through whatever fallback the runtime uses when autocompile
  is failing, not the intended natively-compiled path** — a plausible
  single root cause for erratic-looking behavior well beyond just movement.
  Fixed by launching through `build/play.ps1` directly instead of
  hand-rolling the environment (it does its own correct gcc/python
  discovery); confirmed fixed via `autocompile_status` showing `degraded:0`,
  `fails:0`, and real gcc compiles in `output_tail`.

  A second, compounding bug in the hand-rolled environment: `play.ps1`
  builds `--force-interior` as one repeated flag per address
  (`--force-interior $a --force-interior $b ...`); the manual reconstruction
  used earlier in this session passed one flag followed by five bare
  addresses, which is exactly what clang's "no such file or directory:
  '0x80191B94'" errors were complaining about. Another reason not to
  hand-roll this launch.

- **Stale cached overlay DLL reuse**: checked directly and ruled out. After
  a full cache wipe (`build-release/cache`, 2238 files) and a clean relaunch
  through `play.ps1`, every one of the 291 files that accumulated in the
  cache directory post-wipe has a timestamp at or after the new process's
  start time — none survived from before. Not the explanation.

- **`Entity_ComputeVelocity` being overlay-resident** (the working
  hypothesis for a while, prompted by `play.ps1`'s own header comment that
  "Parasite Eve streams almost everything... as code overlays"): checked
  directly and ruled out. Every currently-compiled overlay fragment leaves a
  `.ranges` manifest (`<base>_<hash>.ranges`, format documented inline:
  `F <addr> <content-hash>` per function entry, `R <addr> <size>` per
  range) naming exactly which addresses it covers. Parsed all 72 `.ranges`
  files present after the clean relaunch — none cover either
  `0x80018598` (the function) or `0x800185C0` (the patched instruction).
  This actually agrees with `pe-qol-mod-roadmap.md`'s original assessment
  ("none of them touch overlay-only content") rather than contradicting it
  — the mid-session overlay-residency theory was a wrong turn, not a
  correction.

### What's still open

By elimination, `Entity_ComputeVelocity` is either running from the
always-resident, statically-compiled main EXE image, or (for the 4 patched
bytes specifically) through the plain single-instruction dirty-RAM
interpreter fallback that doesn't need a promoted overlay compile. Both
paths should, in principle, see the current patched value. That the live
capture never showed *any* variation across three genuinely different
compiled values is the actual unresolved anomaly — and given everything
above checked out, the more likely explanation at this point is
**instrumentation, not the fix**: `g_PlayerEntity`/`0x800BED10` may not
reliably identify the actor actually being driven by player input in this
build, or `FieldActor.motion_x/z` may not hold a value that stays valid
long enough between a ~100-200ms debug-server round-trip to read
meaningfully (i.e. it's a true per-frame instantaneous term consumed and
overwritten within the same tick, not a sampled/latched velocity).

**Concrete next step for whoever picks this up**: before trusting any
further live-motion capture, find and verify a different signal that is
known to correlate with player input in real time — e.g. cross-check
`Camera_EntityTracking.c`'s follow-target pointer against
`g_PlayerEntity`, or capture `pos_x`/`pos_z` deltas over a much longer,
unambiguous displacement (walk between two fixed, distant landmarks and
diff position before/after) rather than trying to sample instantaneous
per-frame motion through a network round-trip. Once a reliable live signal
exists, the speed verification itself should be quick — everything upstream
of it (the compiled value, the RAM patch, the toolchain) already checks out
clean as of this session.

## Follow-up (same night, autonomous — no user input): found the actual instrumentation bug

Continued investigating without live user testing, per the user's request.
Two real findings, one still open.

### `g_CurrentEntity` is not a stable "the player" reference — this is the bug

Every earlier live-motion capture this session read `g_CurrentEntity`
(`0x8009D2F0`) under the assumption that it reliably identified Aya. It
doesn't. `Entity_UpdateList.c` (now read in full) shows `g_CurrentEntity` is
just the loop variable of the per-frame actor-update walk — it takes on
*every* actor's address in turn, once per frame, as the list is iterated:

```c
node = g_FieldActorListHead;
while (node != 0) {
    if ((node->flags & 0x80) == 0) Entity_UpdateAndRender(node);
    node = node->next;
}
```

`g_PlayerEntity` (`0x8009D254`) is the actual stable pointer to Aya's node —
confirmed distinct from `g_CurrentEntity` on live capture after loading
save slot 0 this session (`0x800BEF90` vs. `0x800BED10`, different
addresses). Every one of tonight's earlier "frozen, input-independent
motion" captures was almost certainly reading `g_CurrentEntity` at whatever
arbitrary actor it happened to be visiting at the moment the debug-server
round-trip landed — not Aya specifically, and not necessarily the same
actor twice. That fully explains the identical, input-independent readings
across every earlier attempt: they were coincidence, not signal. This is
the real resolution to "how do we know the tests are accurate" — they
weren't, and now there's a concrete reason why, not just a suspicion.

`0x800BEF90` (this session's actual `g_PlayerEntity`) has every hallmark of
being correct: `flags` has no skip bits set, `pos_x`/`pos_z` are
plausible-scale world coordinates (unlike `0x800BED10`'s suspiciously small
0-15-range values from earlier), and `move_factor`/`move_speed` read sane
baseline values.

### A working autonomous input-injection method now exists

The debug server supports fully scripted controller input with no user
involvement: `set_input` (`{"cmd":"set_input","buttons":"<hex>"}`, holds
indefinitely until `clear_input`) and `press` (auto-releases after N
frames). **The button word is the raw PS1 SIO word: active-low (0=pressed,
1=released), bit layout SELECT,L3,R3,START,UP,RIGHT,DOWN,LEFT,L2,R2,L1,R1,
TRIANGLE,CIRCLE,CROSS,SQUARE from bit 15 down to bit 0** (confirmed
empirically via `pad_status`, which echoes the raw word back — sending
`"0204"` first, expecting it to mean "Down+Circle pressed," actually means
the opposite under this convention and was caught immediately by checking
`pad_status` rather than assumed). The corrected encoding for
Down+Circle is `0xFDFB`; Down alone is `0xFDFF`. `keybinds.ini` confirms
this game's `S` key is bound to Circle (`circle = S`), the run modifier
referenced throughout this session.

**Caution learned live**: injecting Circle (the run-key binding) while also
testing near a save's spawn point can trigger the field "interact/confirm"
action instead of running, if there's anything interactable nearby —
observed directly as `g_GameStateFlags` (`0x8009D1A0`) flipping
`0x0 → 0x1` immediately after a Circle injection and *staying* there even
after `clear_input`, confirming a real state change (a dialog/menu), not
input echo. Reloading the same savestate reverted it to `0x0`, isolating
the cause cleanly. For future autonomous tests: **inject a pure direction
first and confirm motion before ever adding the run button**, to avoid
this confound.

### Still unresolved: no motion at all on save slot 0, even for plain Down

With the correct actor identified (`0x800BEF90`), a completely fresh
savestate reload (ruling out the interact-menu confound above), and a clean
`Down`-only injection (`0xFDFF`) held for 4+ real seconds — confirmed still
being read as held via `pad_status`, confirmed the game loop itself
advancing normally via `freeze_check` (not paused) — `pos_x`/`pos_z`/
`motion_x`/`motion_z` never left their resting values. Also tried Down on
both the digital pad and the analog-stick axis (`ly:255`) simultaneously,
in case the game's movement path only reads the stick; no change.

This is a clean negative result, not a re-run of the earlier
instrumentation bug — the actor, the input encoding, and the game's running
state were all independently confirmed correct this time. Two honest
explanations remain open: (a) save slot 0's specific stored position is
somewhere movement is legitimately locked (indoors at a fixed spot,
mid-scripted-sequence despite `g_GameStateFlags` reading 0, a load zone,
etc.) — very possible for whatever save happened to be in slot 0 — or
(b) there's a real gap in the synthetic-input path for field movement
specifically (as opposed to menu navigation, which the fold-to-stick
comment in `main.cpp` suggests was the originally-intended use case for
digital-injection-into-analog-paths). Not yet distinguished.

**Resolved, same night**: tried a second, genuinely different save
(slot 2 — confirmed by converting its `.thumb` file, a raw
`PSTH`-magic 128x96 RGBA dump, to a viewable PNG first: slot 0 is an
outdoor gated entrance, explaining the earlier interact-menu confound;
slot 1 is just the title screen; slot 2 is Aya alone in an indoor room,
open floor, nothing obviously interactable nearby). Same clean method —
fresh load, confirm `g_PlayerEntity` (a different address here,
`0x800BED10` for this save, confirming the address is per-session and
must always be re-dereferenced rather than assumed), `Down`-only,
10+ samples over 4 real seconds. **Zero motion again**, identical to slot
0. Also re-ran with the digital pad AND the analog stick axis (`ly:255`)
set simultaneously, and separately relaunched the whole game with
`PSX_DEV_INPUT=1` set (the environment variable gating
`dev_any_input_enabled()` in `main.cpp`, which the "fold D-pad onto stick"
comment implies matters for injected-input paths) — same null result under
every combination.

**Conclusion**: this isn't a bad-save-slot artifact. Three independent,
clean reproductions (two different saves/actors, digital pad, analog
stick, with and without `PSX_DEV_INPUT`) all agree: **the debug server's
`set_input`/`press` injection does not drive field-exploration movement in
this build**, even though it correctly updates the readable pad state
(`pad_status` reflects it accurately). The likely explanation, not yet
confirmed by reading further source: the "fold injected D-pad onto stick"
mechanism referenced in `main.cpp` was built and tested for *menu*
navigation, and field movement's actual input read may go through a
separate path this injection doesn't reach. This caps how far the
autonomous-testing approach can go tonight — **verifying the run-speed fix
still needs a real human at the keyboard**, but everything upstream of
that (which actor to watch, how to read its state cleanly, how to avoid
the interact-menu confound) is now solid and reusable for whenever that
test happens.

## Follow-up: a real dirty-RAM baseline, not just theory

The user's last question ("did you start running tests on that?") was fair
— everything above about dirty RAM was mechanism explanation and
inference, not a controlled measurement. Ran one.

**Method**: `freeze_check`'s `dirty_ram_blocks`/`dirty_ram_insns` are
process-lifetime counters — confirmed they do **not** reset on a
savestate reload (identical values before and after reloading slot 2
mid-session), so a clean A/B needs a full process restart between
conditions, not just a save reload. Controlled test: same save (slot 2),
same fresh-boot-to-measurement window (savestate load, then a fixed 3s
wait), toggling `mods/state.toml`'s `enabled` flags for both
`pe.enhancement.faster-movement-live` and
`pe.enhancement.personal-inventory-floor` between runs, confirming via
`mem_words` at `0x800185C0` that the mod state actually took effect each
time (`0x3C040005` original / `0x3C040014` patched).

**Result**:

| Config | frame_count at measurement | `dirty_ram_blocks` | `dirty_ram_insns` | `dispatch_interp_fallback` | `invalidations` |
|---|---|---|---|---|---|
| Mods disabled | 2547 | 203 | 257 | 203 | 0 |
| Mods enabled (matched) | 2612 | 203 | 257 | 203 | 0 |

Identical, down to the exact integer, across two independent fresh boots.
**Both of this project's mods contribute zero measurable dirty RAM.** The
203 blocks / 257 instructions are entirely baseline engine behavior (BIOS
kernel routines, the shared RoomLib overlay's own load/init sequence,
etc.) — present whether or not any mod is active. This directly answers
the "does it dirty from the very beginning" question from earlier tonight:
yes, some interpreter fallback is present from boot, but it is small
(low hundreds of instructions, not a meaningful fraction of a
33M-cycle/frame budget), constant, and **entirely attributable to the
engine itself, not to any mod work done this session.**

`dispatch_interp_fallback` matching `dirty_ram_blocks` exactly in both
runs (203 = 203) suggests these two counters are tracking the same
underlying event through two different reporting paths, not independent
measurements — worth keeping in mind if a future investigation treats them
as corroborating rather than duplicate evidence.

This also incidentally re-confirms the mod-enablement mechanism itself
works exactly as designed: RAM at `0x800185C0` correctly flipped between
the original `0x3C040005` and the patched `0x3C040014` in lockstep with
`state.toml`'s `enabled` flag across both restarts, with no leakage either
direction.

**For future mod work**: this same before/after-toggle method (full
restart, not just a savestate reload, matched frame-count window) is the
right way to check whether any new patch adds dirty-RAM overhead — cheap,
decisive, and fully autonomous.

## Follow-up (2026-09-14): a real, separate dirty-RAM bug found and fixed — during the intro FMV, not idle gameplay

The user pushed back, correctly, on treating the idle-gameplay dirty-RAM
baseline above as the whole story — they specifically suspected dirty RAM
in the already-known, still-unresolved intro-skip video-bleed-through bug
(`video-bleed-through-splash.md`). That bug was root-caused to a
stale-pixel-data mechanism, not a CPU-code interpreter issue, and its own
"Still open" section never checked whether the MDEC/CD-XA teardown code
was itself running interpreted — a real, legitimate gap. Went and checked
it directly rather than reasserting the idle-gameplay conclusion.

**Found a second, much larger dirty-RAM source, specific to the intro FMV**:
launched fresh (`fullscreen=1` per that doc's own repro method, reverted
after), and watched `freeze_check` continuously through ~90-120s of intro
playback. Flat at the usual 203 blocks/257 instructions for the first
~90s, then **exploded to 17 million, then 45 million+ interpreted
instructions**, still climbing at ~2M/sec, by the time of the skip and
settling at the post-skip menu — then **went completely flat again the
instant the menu stabilized** (unchanged across 4+ seconds once settled).
So this cost is real, large, and specifically tied to something active
during FMV/video-decode playback (most likely CD-ROM/MDEC-related BIOS
polling, given part of it traced to BIOS ROM addresses like `0x1FC0C114`)
— not a permanent leak, and not the same mechanism as the tiny idle-gameplay
baseline documented above.

**Root cause, and it's the known bug class**: `autocompile_status`'s
`output_tail` during this window showed the classifier explicitly
excluding a cluster of addresses — `0x80191230, 0x801912A4-C8,
0x80191318, 0x8019131C` — as `"excluded: OBSERVED_PC_ONLY"`: genuinely
executed, but refused promotion to native compilation, forcing permanent
interpretation for the rest of that run. This is the **exact same failure
mode**, in the **exact same `0x80191xxx` shared RoomLib region**, as the
two bugs this project already found and fixed
(`roomlib-interior-classification-ai-brief.md`,
`roomlib-0x80191200-interior.md`) — just a different, not-yet-covered set
of addresses in the same neighborhood, only reached via the intro/menu
path rather than normal gameplay (which is why the idle-gameplay baseline
test above never saw it).

**Fix applied and verified with a real before/after**: added the 13 newly
found addresses to `build/play.ps1`'s default `$ForceInterior` list,
alongside the five already there. Relaunched fresh, replayed the identical
~90-120s intro window:

| | dirty_ram_insns at ~T+120s / post-skip |
|---|---|
| Before fix | 45,338,450 (still climbing) |
| After fix | 20,304 → 101,046 (settled, not climbing) |

**Roughly a 450-2200x reduction**, confirmed via two independent
timestamps. This is a real, decisive, already-merged-into-the-launch-script
fix, not a hypothesis.

**What this does NOT establish**: a confirmed link to the actual visual
bleed-through bug. Tried to reproduce the visual glitch both before and
after the fix (same synthetic-Start-press method as
`video-bleed-through-splash.md`) and got a clean menu both times — the
original doc already documents this bug as timing/race-sensitive (not
reliably reproduced on every attempt), so two clean results don't rule
out a connection, they just don't confirm one either. What's true
independent of that open question: this was a real, previously-uncataloged
interpreter-classification bug, in the same family as two already-fixed
ones, now fixed with a measured, order-of-magnitude improvement during the
game's intro sequence specifically. Worth re-attempting the visual repro
several more times now that this is fixed, to see if the bleed-through
rate changes — not done here due to its inherent non-determinism needing
many trials to say anything statistically meaningful.

### The actual root cause, traced all the way down

The user pushed further: finding 13 addresses and force-including them is
a patch, not an explanation. Traced it properly.

**What code this is**: `sym.room_m087.txt` + `room_m087.yaml` pin the
excluded addresses to `func_80191244`, a 136-byte function. Its decomp
source (`src/overlays/room_m087/func_80191244.c`) is one line:
`ROOMLIB_STATE_DISPATCH_VARIANT2(func_80191244,
RoomLib_ResetAndSignalB_80191984)` — a macro (`room_lib.h`) that expands to
`switch (func_800DFB78()) { case 0: ...; case 1: tickFn(o); case 2: return
0; }`. A dense small-integer `switch` compiles to a MIPS jump table, so
each `case` body is a separate address the CPU reaches via a *computed*
`jr`, not a `jal` call — exactly the shape that produces multiple
"observed executing, never called" addresses packed a few bytes apart,
matching the pattern found (`0x801912A4..C8` in 4-byte steps, plus
`0x80191318`/`0x8019131C` in the neighboring
`RoomLib_Notify2ArmB_801912CC`).

**Scope**: `grep -r ROOMLIB_STATE_DISPATCH src/overlays` matches **250
files** — this macro (both variants) is used in roughly two dispatchers per
room across nearly the entire game. Tonight's 13 addresses are just the
ones this specific intro/title sequence happened to exercise; the same
classifier gap almost certainly exists, unnoticed, in most of the other
~125 rooms' own copies of the identical pattern, waiting to be found the
same way the original bug's 5th address was found two months after the
first four (see `roomlib-interior-classification-ai-brief.md`'s own
"recurrence" section).

**Why the already-fixed classifier still misses this**: checked
`psxrecomp/tools/compile_overlays.py` directly — mstan's team's upstream
fix (PR #349, ported into this checkout as commit `a94ab281`, documented
in `roomlib-interior-classification-ai-brief.md`) **is already present**.
`print_seed_audit()` (line ~1884) appends `"; isolated fragment demand
retained"` to an `OBSERVED_PC_ONLY` exclusion when the address is in
`unhosted_dispatch = (dispatch_fragment_demands & executed_pcs) -
included_reasons`. Tonight's captured output showed the 13 addresses as
plain `"excluded: OBSERVED_PC_ONLY"` with **no** recovery suffix — meaning
they were never in `dispatch_fragment_demands` at all. That set is built
from *statically discoverable* jump targets (the kind a disassembly pass
can see directly, like a `jal` or a literal branch); a `switch`'s jump
table is populated from a data table read at runtime (`lw` from a table
address, then `jr`), which this classifier's static pass evidently doesn't
resolve into a demand record the same way. **This is a real, narrower,
still-open gap, distinct from (though closely related to) the bug PR #349
already fixed** — the fixed mechanism recovers unhosted-but-demandable
addresses; jump-table case targets from a runtime-computed `switch` appear
to fall outside what counts as "demandable" for it. Not reported upstream
yet — would need the same kind of synthetic before/after test the
original brief used, on a MIPS jump-table case specifically, to make an
actionable report.

**Practical takeaway**: the `--force-interior` fix applied tonight is the
correct, necessary treatment for this specific gap (not a workaround
standing in for a fix that already exists) — the improved classifier
genuinely does not catch this shape of code. Given the 250-file scope, a
worthwhile follow-up (not done tonight) would be to grep every room's
compiled address for its own `ROOMLIB_STATE_DISPATCH`/`_VARIANT2`
instances and their neighboring interior addresses, and force-include the
whole set proactively, rather than continuing to discover them one
intro-sequence or one boss-room at a time.

### The residual 203/257 identified: BIOS ROM, not a bug, nothing to fix

Sampled `current_func` repeatedly during the baseline window to see what
was actually behind the count. Two addresses only:

- `0x00000F40` — already identified earlier this same session as a generic
  BIOS kernel interrupt-vector trampoline, hit on every hardware interrupt.
  Confirmed harmless by direct disassembly at the time.
- `0x1FC01ACC` — decisive: `0x1FC00000` is the real, hardware-defined base
  address of the PlayStation BIOS ROM itself (the KSEG1 uncached mirror).
  This address is *inside the BIOS ROM*, not game or overlay code.

This matches the boot log's own `bios_backend=HLE (LLE fallback)` line:
most BIOS calls get a fast native (HLE) replacement, and whatever isn't
covered genuinely interprets the real BIOS ROM (LLE) — there is no overlay
compiler for BIOS ROM the way there is for game code, so this is
architecture working as intended, not a classification miss. This is
categorically different from the two real, fixed overlay-classification
bugs this project has found before (`roomlib-interior-classification-ai-brief.md`,
`roomlib-0x80191200-interior.md`), which were about *game* code wrongly
stuck in the interpreter. **Conclusion: no fix needed or possible here** —
257 instructions of BIOS interrupt handling spread across thousands of
frames is immeasurably small against a ~33M-cycle/frame budget, the same
class of non-issue as this project's own prior "clean compute wall, not a
bug" finding. The concrete, reusable win from this line of investigation
is the verification method above, not a code change.

## Reusable verification method for future PE mod work

1. **Always launch via `build/play.ps1`**, never a hand-rolled environment.
   Two real, non-obvious bugs this session (wrong `PSX_MINGW_BIN`,
   malformed `--force-interior`) both came from reimplementing its logic
   instead of calling it.
2. **Check `autocompile_status` immediately after every launch**, before
   trusting any subsequent test. `degraded` must be `0`, `fails` must be
   `0`; if not, `output_tail` has the real compiler error. Debugging
   gameplay behavior on top of a broken autocompiler wastes hours on
   phantom bugs, as this session's log demonstrates.
3. **To check whether a specific address is overlay-resident**: after a
   clean launch, grep `build-release/cache/**/*.ranges` for `F <addr>` /
   `R <addr> <size>` entries bracketing the target. This is a direct,
   file-backed answer, not an inference from filenames or coarse
   dispatch-native/interp-fallback counters.
4. **To check whether a `[[patch]]` write actually reached RAM**: query
   `mem_words` at the target address after boot. To check it isn't being
   fought by a stale manifest elsewhere, check both the source
   (`mods/preloaded/packages/`) and staged
   (`build-release/mods/packages/`) copies plus `mods/state.toml`'s
   `enabled` flags — this session had two real instances of a stale staged
   copy silently overriding a corrected source copy.
