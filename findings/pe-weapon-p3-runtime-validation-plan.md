# Runtime timing validation: evidence and measurement protocol

Source audit performed by Codex, October 17, 2026. This is not a record of a new live playtest.

## What local source establishes

Paths below are under `D:/Recomp Games/Parasite Eve Project`.

| Evidence | Location | Implication |
|---|---|---|
| Aya's gauge increases by scaledOffense only when the caller enables updates and game flag 0x100 is clear | parasite-eve-decomp/src/main/menu/main_update.c, Menu_MainUpdate, lines 99–109 | Gauge advancement is gated, not an unconditional clock |
| Action execution sets game flag 0x100 | parasite-eve-decomp/src/main/battle/phase.c, line 302 | Firing/action processing can pause the gauge update |
| Action cleanup clears that flag | same file, lines 355–365, and other command-dependent branches | Pause duration is tied to action lifecycle; exact boundaries require measurement |
| Full action completion empties the gauge | parasite-eve-decomp/src/main/battle/turn.c, FinishAction, lines 224–239 | Timing depends on reset as well as refill gates |
| Rate is stat22 × class factor / 10 | parasite-eve-decomp/src/main/battle/enemy_actions.c, lines 281–282 | Source supports the per-update gain, not 94 updates per real second |
| CURRENT equipment switching is allowed at half gauge and costs half a bar | parasite-eve-recomp/src/mods/pe_atb_items.c, opening design comments and default allow table | Switch has a resource/time cost; it is not a free best-of-two weapon choice |
| Battle logger estimates elapsed seconds using frames / 59.9 | parasite-eve-recomp/src/mods/pe_loot_logger.c, pe_secs, line 373; frame increment line 712 | Existing event timestamps are whole-second values and cannot resolve subsecond firing/refill overlap |
| Turn logger fires when a formerly full gauge falls; it does not record every gauge sample or animation boundary | same logger, lines 413–424 | secs/turn is not a direct measurement of fill frequency or firing duration |

**Interpretation:** these source paths support serial-style pause behavior more strongly than
unconditional overlap. They do not prove that the simulator's entire `fill + commit` abstraction
matches every runtime frame. Keep overlap as sensitivity, favor serial as the source-supported
hypothesis, and do not silently rewrite historical baselines.

The simulator's 94-Hz conversion was calibrated from aggregate turns rather than isolated
gauge increments. The logger's 59.9 frame conversion does not prove a 59.9-Hz gauge clock either.
The follow-up experiment compares both conversions on frozen loadouts without declaring either
a newly verified baseline. Firing overhead, reload duration and per-bullet animation are still
assumptions. The simulator also applies bullet damage at turn processing time, so very short
clear times are not precise command-to-last-hit runtime predictions.

## Minimum useful read-only capture

Use an existing debug/read-memory facility when available. No hook or game-code changes were
installed during this audit. Sample each emulated update, avoiding slow host polling that misses
updates. Each row should carry:

```text
capture_id,guest_frame,host_monotonic_ns,game_flags,battle_phase,aya_state_flags,gauge,fill_rate,stat22,action_id,queue_index,loaded_ammo,weapon_id,animation_frame,input_event
```

Correction from live inspection: 0x8009D254 is a **player entity pointer**, not a core pointer.
Read the entity pointer, then read the core pointer at entity+0. Gauge is at
core+0x10; stat22 at +0x22; fill rate at +0x24; state flags at +0x4C; battle phase 0x8009D28C;
game flags 0x8009D1A0. Confirm pointers/ranges using the existing debug facility before reading.
Prefer guest frame deltas over host time if speed limiting, pause or fast-forward is enabled.

Live session established entity 0x800BEF90 → core 0x800B8A20 for the copied Disc 2 Eve setup.
These addresses must be resolved again after loading another state; never assume they are global.
See `live-timing-session/attack-03.json` and `attack-04.json`: these captured canceled turns,
not ammo-consuming attacks. They provide refill observations only and must not calibrate firing.

Capture three or more repeats of each configuration with the same enemy and Aya stats:

1. Isolated idle refill after an action; no Haste, Slow, PE, menu waits or damage interrupts.
2. P90 RoF3 versus RoF10; record reset, first refill increment, last bullet and control return.
3. M10B one versus two Commands, with capacity sufficient to avoid clicks/reloads.
4. A deliberate empty-magazine reload to isolate its duration.
5. A half-bar weapon change in each direction; record gauge debit and new fill rate.

Calculate gauge gain per enabled guest update, enabled updates per second, action reset time,
first post-reset increment, and last-shot/control-return frames separately. A gauge plateau
during flag 0x100 supports paused refill. A net time-per-turn alone does not identify its cause.
Capture actual bonuses, mods, armor, status, build identifier and speed settings with every run.

## Acquisition timing checks

The prior simulation's first M10B observation was Disc2 under its tested policies. That is not
the earliest legal acquisition in the actual game. The policy crafts only in D5/Disc2, Wayne
visits are reconstructed, and the play driver performs a final Wayne maintenance visit. Verify
the first accessible Wayne visit with 300 spendable Junk, actual story eligibility, and whether
the current route can carry the gun and its donors before inferring an early balance need.
No new runtime acquisition timing was measured in this pass.
