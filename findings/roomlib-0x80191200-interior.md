# A second hot RoomLib address stuck in the interpreter — `0x80191200`

Supersedes the "idle_skip doesn't cover it" framing at the end of
`mdec-idle-decode-cost.md` — that data point (idle_skip's counters frozen
through the idle stretch) is real, but it's a symptom, not the root cause.
This is the root cause, and it's the same bug class as finding #2, same
resident overlay, a different address.

**Status: CONFIRMED end-to-end.** Fix applied to `build/play.ps1` and
re-verified against the real `build-release/cache` (not just the isolated
test directory) — see **Confirmed result** below for the before/after.

## The comparison that found it

`stall_report.py run --secs 60`, once during the title screen's active-video
window and once during a confirmed-idle window (idle = `mdec_state`'s
`dma_in_words` flat across 9 consecutive 10s samples — see
`mdec-idle-decode-cost.md`):

| | Active-decode window | Idle window |
|---|---:|---:|
| `interp_share` | 48.5% | **93.6%** |
| `static_share` | 50.6% | 6.2% |
| Hottest interpreted PC | `0x80191B94`, 27,379 insn/entry | **`0x80191200`, 201,213 insn/entry** |
| That PC's share of all interpreted instructions | — | **108M / 124.6M ≈ 87%** |

`0x80191200` sits inside the same shared "RoomLib" resident-overlay region
as the original 4 `--force-interior` addresses from the earlier field
report (`0x80191B94`, `0x801927D0`, `0x80192E3C`, `0x801925D4`) —
`RoomLib_HandlerD` (decomp) is at `0x80191280`, 128 bytes away. Same region,
same failure mode, an address nobody had found yet because it's specifically
hot in the idle/attract-wait path, not the field/battle paths the original
four were found from.

## Confirming it's finding #2's mechanism, not something new

Inspected the on-disk capture after a session with overlay autocompile
active (real GCC, matching `play.ps1`'s normal setup) for 6 minutes:

```json
{
  "load_addr": "0x8018F000", "size": 20484,
  "dispatch_entry_pcs": ["0x801911F8", "0x80191200", "0x80191320", ...],
  "function_entry_pcs": [],
  "seeds": ["0x801911F8", "0x80191200", "0x80191320", ...]
}
```

`0x80191200` is genuinely observed and recorded (`dispatch_entry_pcs`,
`seeds`) — the capture sees it being dispatched to. `function_entry_pcs` is
empty — `compile_overlays.py`'s classifier never promotes it to an actual
carveable function boundary. Textbook finding #2.

Autocompile's own tally for this region after 6 minutes, running with only
the *original* 4 force-interior addresses (not yet including this one):
`shard_ok=0, shard_fail=0, shard_skipped=5` — nothing built for this region
at all, and `0x80191200` and `0x80191B94` were still massively hot in the
interpreter at the end (199M and 57M instructions respectively) despite
`0x80191B94` supposedly already being on the force-interior list. Worth
being clear about: I don't have a confirmed explanation for why the
already-known address regressed here too in this particular session (same
mechanism, a stale/incompatible cache from an earlier capture generation is
the most likely explanation, not a new bug) — the fix step below (a clean
recompile) resolves both regardless.

## Confirming the fix mechanism still works

Ran `compile_overlays.py` directly against the on-disk capture, adding
`0x80191200` to the existing four:

```
python tools/compile_overlays.py --captures overlay_captures.json --game-toml game.toml \
    --recompiler recompiler/build/psxrecomp-game.exe --runtime-include runtime/include --cps \
    --compiler gcc --gcc <mingw>/gcc.exe \
    --force-interior 0x80191B94 --force-interior 0x801927D0 --force-interior 0x80192E3C \
    --force-interior 0x801925D4 --force-interior 0x80191200
```

```
interior fragments @0x0018F000: 5/5 exact-demand orphan interior(s) -> isolated island shards
=== SHARD BUILD SUMMARY ===
  built OK : 5
  skipped  : 1  (cached / data-only / safe coverage loss)
  FAILED   : 0
```

All 5 forced addresses compile into isolated "island shard" DLLs
independent of the main region (which still correctly skips as data-only on
its own — it has no root seeds besides the forced ones). The mechanism
works exactly as designed; `0x80191200` just hadn't been found and added
yet.

## Fix applied

`psxrecomp-decomp-bridge/build/play.ps1`'s default `-ForceInterior` list:

```powershell
# before
[string[]]$ForceInterior = @('0x80191B94','0x801927D0','0x80192E3C','0x801925D4'),
# after
[string[]]$ForceInterior = @('0x80191B94','0x801927D0','0x80192E3C','0x801925D4','0x80191200'),
```

Anyone building/playing via that script now gets this address carved
automatically.

## Confirmed result

Rebuilt the real `build-release/cache` with the corrected 5-address
`--force-interior` list (autocompile, real GCC, same setup `play.ps1` uses),
let it warm up 60s, then re-ran the identical active/idle `stall_report`
comparison:

| | Active window (before → after) | Idle window (before → after) |
|---|---:|---:|
| `interp_share` | 48.5% → **8.0%** | 93.6% → **7.9%** |
| interpreted instructions (60s) | — | 124.6M → **0** |
| `dispatch_interp_fallback` | — | 225,249 → **0** |
| `static_share` / `native_share` | 50.6% / 0% → 65.6% / 21.8% | 6.2% / 0% → 65.9% / 21.5% |

Both phases now land at essentially the same ~8% interp_share, matching the
healthy composition from the original 2026-09-09 fix
(~69% static · ~23% native overlay · ~4% interp · ~22% exception) — this
confirms the fix, doesn't just theoretically explain it. The idle window's
interpreted-instruction count is exactly zero in this sample.

## A second hot address that did NOT need this fix — `0x80193084`

Worth recording since it looks identical at first glance but has a
different resolution. User reported the New Game/Continue/Tutorial menu
(reached from the title) as very slow. Live `stall_report` there:
`interp_share 89.9%`, `0x80193084` alone responsible for 55.3M of ~55.36M
interpreted instructions (140,846 insn/entry) — same shared RoomLib region,
same shape of symptom as `0x80191200`.

Difference: with overlay autocompile active and left running at that screen
for ~90 more seconds (no manual force-interior, no code change), the
capture matured on its own and the runtime correctly classified and
compiled it — `interp_share` dropped to **0.66%** unassisted. A repeat visit
to the same menu was fast from then on.

**This is the normal "first visit to an area compiles it in the background,
native from then on" behavior the project already documents** (see
`build/play.ps1`'s own header comment) — not a permanent finding-#2-class
bug. The distinguishing test, now established: **does a repeat visit to the
same screen stay fast, or does it warm up slowly every time?** Stays fast →
normal warm-up, no fix needed. Warms up again every time → likely a
permanent missing-function-entry bug like `0x80191200`, worth the full
force-interior treatment.

Practical implication: **not every hot interpreted PC found this way needs
a code fix.** Confirm with a repeat-visit check before spending time on
`--force-interior` testing.

## Still open

- **`0x0010C89C`** also showed up hot in the pre-fix run — 245,694 insn/entry,
  and appearing in *both* the interpreted-hot list and the native
  `phase_hot` set (partially compiled / partially falling back). Followed
  up: it did not reproduce in three subsequent fresh sessions (active +
  idle snapshots all came back with `interp_share` at the healthy ~8%
  baseline and an empty hottest-PC list). Likely dependent on the exact
  sequence of overlay loads in that one session rather than a stable,
  always-reproducible bug — see the capture-store observation below.
  Not resolved, just not currently reproducing; revisit if it turns up
  again.
- **The overlay capture store doesn't appear to be stable across sessions.**
  Across three separate runs today, the RoomLib region's captured extent
  changed shape each time: 20,484 bytes → 4,100 bytes → a differently
  positioned 12,292-byte region. `0x8010C89C`'s containing region likewise
  came and went between runs. This means two otherwise-identical sessions
  can end up with different captured/compiled coverage, which is itself a
  source of run-to-run performance variance independent of any one missing
  function entry. Not confirmed as a bug — just an observation worth
  someone with the capture-store source in front of them checking.
- Whether `0x80191200` specifically is why Mac performs differently is
  unconfirmed — no Mac-side data, just the Windows-side mechanism and fix.

## Verify

`stall_report.py run --secs 60` during a confirmed-idle window (cross-check
against `mdec_state`'s `dma_in_words` being flat) — `interp_share` should
drop well below 93.6%, and `0x80191200` should no longer top the hottest
interpreted PC list once the corrected force-interior list has fed a fresh
`build-release/cache`.
