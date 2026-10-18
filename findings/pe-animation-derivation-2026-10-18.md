# Animation extraction and timing derivation — 2026-10-18

## Extraction

All work was offline. No game input, save loading or new live capture was used.
`extract_animations.py` parses the existing isolated slot9 PST using the runtime's
BootStateHeader/section format, decompressing only its RAM section. RAM provides the
PE.IMG baseLBA1013, sector boundary table at0x800930D8 and loaded action table at0x800B0E98.
The PST SHA256 is recorded in `data/pe-animation-extract-2026-10-18.json`.

From the Disc2 raw BIN, the extractor reads the 2048-byte payload of each CD sector.
Scene_LoadEntityTextures case4 selects bank index = variant*8 + actionKind +0x16.
Its case6 resolves the directory at blob+u32(blob+4), then bankRowEntries at directory+0x10.
Each12-byte row has offset in low24 bits of word+4 and action mode in its high byte.
The animation header's byte2 is frame_count. Bank payload hashes, sector ranges, offsets,
raw12-byte headers, modes and frame counts are retained. No copyrighted animation payload
was copied into the simulator, only header metadata. Both extracted variants are termed
costume0/1 in the new API; the exact story/outfit selection still follows the loader.

Extracted16 banks (8 classes x2 variants), with142 animation-header entries total:
each firearm bank has modes4..12; club banks have modes4..11. All3 target angles have
matching aim lengths within a bank and matching follow-through lengths. Variant1 grenade
and club aiming clips are30frames instead of15; other timing lengths agree between variants.

The loaded snapshot's modes4..12 match variant0 handgun headers. The global five-byte
weapon timing rows also match the simulator's original ANIM data exactly.

## Source derivation

Source paths are under Parasite Eve Project/parasite-eve-decomp/src/main:

- `field/actor_collision.c:31`: Entity_AdvanceAnim copies current to previous, then adds
  signed16.16 animStep unless held by entity flag0x100; wraps at frame_count. SetActionMode
  resets both frame values and reads lastFrame=header.frame_count-1.
- `entity/frame_update.c:198`: Battle_Update runs before Entity_AdvanceAnim in each normal
  entity update. Thus current-frame and previous-frame boundary checks differ by an update.
- `boot/frame_loop.c:114` and `draw/frame.c:29`: one entity update per normal main-loop
  iteration; Draw_RenderFrame normally uses VSync(2). `psyq/libetc/vsync.c:12` explains the
  two-VBlank target. Normal nominal NTSC rate is59.9/2=29.95 updates/s. This is a no-stall
  conversion, not a guarantee under slow rendering/loading/paused or special display paths.
- `battle/attack.c:94`: Battle_StepCharacterAction waits for the aim's last current frame,
  drains timing counters0 then1 while holding that pose, then switches to follow-through,
  resets hit timer and calls Battle_FinalizeAttackResult. The five-byte weapon row values
  are hold-update counters and a hit trigger, NOT counts of full animation loops.
- The following shot completes when previousFrame equals its last sample. With another
  ordinary queued shot and ammo available, the next aiming pose starts at its last sample
  and is held; counter1 gains counter2. Once the hold drains, another update releases/fires.
- `battle/player_turn.c:63`: changing target adds counter3 to counter1. That value is not
  mandatory post-turn recovery. The former model added it to every turn incorrectly.

`decomp_animation.queued_shot_timeline` expresses that uninterrupted ordinary queue path.
Update0 is the initial battle call; fire events and queue completion are zero-based.
Commit duration counts all calls through completion, so completion24 means25 update calls.
For handgun: first fire at14, next at30, next at46; three-shot queue finishes56, taking57
calls (~1.903s). The model reports queue-finish time, not final damage resolution: timed hits
are delayed from fire by hitTrigger and asynchronous effect behavior remains separate.

## Simulation integration and validation

`decomp_animation.source_rules(CURRENT or VANILLA)` creates a distinctly named experimental
profile. Engine commitment uses extracted lengths/holds; gauge refill uses exact integer
updates and the same29.95Hz normal-loop assumption. Economy surrogate uses the same fill
and commitment functions and preserves the parent damage rules. Historical defaults remain
unchanged for reproducing saved reports. The profile explicitly rejects Burst, Random and
AttackAll rather than silently applying ordinary-queue timing to their alternate paths.

Added6 tests for extracted bank metadata, frame-boundary order, same-target/retarget holds,
rifle holds, variant differences, source-profile integration and malformed snapshots.
Full suite:76 passing. Generated64 duration cases and14 benchmark groups (7 firearm classes
x2 timing profiles, each8 matched seeds per encounter). See `pe-animation-durations-2026-10-18.md`
and `data/pe-animation-validation-2026-10-18.json`. Benchmark equipment is synthetic/frozen;
the profile changes both clock and animation timing, and suite scores penalize losses.

Reproduce from bridge root with PYTHONPATH=tools and bundled Python:

    python -m pe_weapon_sim.extract_animations findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst --disc "D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 2).bin" --out findings/data/pe-animation-extract-2026-10-18.json
    python -m pe_weapon_sim.run_animation_validation
    python -m unittest discover -s tools/pe_weapon_sim/tests -q

## Corrections and remaining scope

Earlier source audit favored serial timing from the action pause flag. The traced ordinary
shot dispatch does not set0x100; FinishAction sets it for certain non-shot commands, and
phase.c handles PE/special actions. Ordinary queued shooting supports overlap, subject to
other pauses. Do not generalize PE's blocking behavior to every gun attack. Existing live
captures without pause flag are compatible with this, even though their firing was unverified.

This is a source-derived ordinary-queue timing model, not full instruction-level battle
emulation. The fight engine still aggregates damage at turn time, chooses targets through
its older policy and retains assumed reload scheduling/RELOAD_S0.8. Burst-mode repeated-hit
branches, interruptions, target deaths, asynchronous effects and reload paths need their own
state-machine integration. In particular, source can reload between queued attacks and use
mode12; end-of-turn-only refill is not established. Extracted mode12 lengths are35/40/45
frames by class, but adding those unconditionally would be wrong. Weapon switch mode13
is a base actor animation (16frames in this snapshot); asset streaming/wait flags must be
handled before treating that clip length alone as complete switching cost. These boundaries
are explicit so the new results are not mistaken for completed dynamic portfolio validation.
