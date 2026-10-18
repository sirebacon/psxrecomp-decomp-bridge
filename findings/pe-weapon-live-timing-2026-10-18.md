# Live timing validation — 2026-10-18

Status: partial validation; firing duration and completed weapon-switch cost remain open.

Correction from subsequent source audit: the inventory ammo field is synchronized separately
from active BattleAction ammo. Statements below calling these canceled/nonexecuted samples
are provisional labels, not established action outcomes. No inventory decrease does not
exclude firing. See `pe-source-audit-2026-10-18.md`; active-action snapshots are required.

## Reproducible setup

Used an isolated copy in `findings/live-timing-session`, including executable, assets,
settings, cache and saves. Original save files were not edited. Disc 2 slot 1 is outside
the Eve fight: move forward, then skip the event. Isolated slot 9 preserves combat start.
Current normal frontend uses debug port 4378; earlier headless runs used other ports.
The user activated native god mode in the current session; HP subsequently read 385/385.
God-mode samples are for timing, not survival or damage-balance conclusions.

## Evidence and exclusions

- `attack03` and `attack04` each contain an observed zero-to-full gauge refill of 230
  guest VBlanks at fill_rate 79, gauge cap 9000. This is about 3.840 seconds at nominal
  59.9 VBlanks/second. Positive increments were 79, mostly separated by two VBlanks,
  occasionally three. This is one setup, not a universal clock calibration.
- Those captures did not consume ammunition or show action pause flag 0x100. Treat
  them as nonexecuted/canceled-turn refill samples, not successful attacks.
- `switch01` through `switch04` never changed equipped slot. Exclude them from switch
  cost estimation. Menu navigation sometimes entered weapon-effect details.
- `windowed-attack01` also did not consume ammunition. Switching from headless to a
  normal frontend and loading the complete gcc cache did not resolve that observation.
- `god-passive-attack01` records 873 consecutive guest VBlanks with controller override
  released. HP stayed 385, gauge stayed 9000, and ammo changed only from 10 to 48 at frame
  20194. No ammo decrease or pause flag appeared. This is an ammo replenishment observation,
  not a verified firing sample or timed reload: initiation was not identified.
- Current inventory has USP-TU, M8000, Club3 and Maeda's Gun. A USP/M8000 switch alone
  would not validate the previously modeled secondary-class niches.

## Instrumentation and next steps

`live_probe.py` records debug requests in `requests.jsonl`. `live_timing_capture.py`
captures four RAM regions at consecutive guest VBlanks; `analyze_live_timing.py`
checks continuity and reports gauge steps, pause flags, ammo and equipped-slot changes.
Resolve player core through entity pointer at 0x8009D254, then entity+0; the global is
not itself a core pointer. Passive idle/observe captures now release input overrides
when keeping the current state, allowing the user's controller to supply the action.

Next require an actual ammo decrease for firing validation, and an equipped-slot
change for switching validation. Measure gauge debit, refill and action boundaries
from those verified events before replacing simulation assumptions. Preserve the
existing optimistic portfolio results as bounds. Do not relabel them as measured costs.

Two new analyzer tests brought the full simulation test suite to 64 passing tests.
Raw JSON and screenshots remain in the isolated session directory.
