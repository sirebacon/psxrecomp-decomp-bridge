# Parasite Eve QoL wishlist: what we can and can't do (2026-10-11)

A remaster-style QoL list for Parasite Eve, checked against what our modding setup
(psxrecomp + the PE decomp + the `PE Enhancements` F1 menu) can actually do today.

**Ratings**

| | Meaning |
|---|---|
| ✅ **Done** | Already in the mod and tested in the game |
| 🟢 **Doable** | Clear approach with tools we have; mostly implementation work |
| 🟡 **Research** | Probably doable, but the game data/code involved isn't mapped yet |
| 🔴 **Hard** | Needs abilities we don't have yet, or far more work than it's worth now |

---

## What our toolkit can and can't do

These limits decide most of the verdicts below.

**Can do (verified in the game)**

- **Read and write any game memory, every frame.** God mode, the stat editor, give item,
  the item editor, run/walk speed and always run all work this way.
- **Add settings to the F1 menu** (`Mods > PE Enhancements`, with sub-pages). The game is
  paused while it's open, it works during FMVs, and its input never reaches the game.
- **Change the game's button mapping table.** This is how Always run works.
- **Use the decomp as a map:** struct layouts, function logic, table addresses, and the
  game's own text (decoded from its glyph codes).

**Can't do (verified)**

- **Patch the main program's code at runtime.** The main EXE is recompiled ahead of time;
  rewriting its instructions in memory doesn't change what runs (tested twice, including
  with the mod API's code-write call). Anything that needs a *code* change in the main EXE
  must either be done by changing the *data* that code reads, or as a build-time change
  (below).
- **Call a game function from a mod** (for example "open the storage menu" or "warp to a
  room"). Our engine version has no such call; newer upstream psxrecomp does
  (`psx_mod_call_guest`), so this becomes possible if we move to a newer engine.

**Possible but not set up / unverified**

- **Build-time code changes:** patch the EXE and regenerate the recompiled C. Permanent (no
  live toggle) and slow to iterate. An earlier attempt "had no effect", but it patched the
  wrong function, so this lever is untested rather than ruled out.
- **Function-entry hooks:** the engine can call a mod when a game function starts, but only
  for functions listed in the game config at build time; PE lists none yet.
- **Patching overlay code:** rooms, battles and menus are code overlays loaded at runtime.
  Changes to *their* code in memory might take effect (they're run from memory, not
  precompiled into the EXE), but that's untested.
- **Drawing over the game:** an early mod drew its own boxes and text into the frame. That
  works for simple 2D shapes; 3D outlines in the world would need the camera maths too.

---

## Summary

| Wish | Verdict | Short reason |
|---|---|---|
| Visible invisible walls (battle) | 🔴 Hard | Need the arena boundary data *and* 3D drawing in the world |
| Items on one ATB segment | 🟡 Research | Depends on whether action costs are data or main-EXE code |
| Modern controls: analog | ✅ Already in the game | The field code already supports free analog movement |
| Modern controls: always run | ✅ Done | Always run toggle + hold-to-walk |
| Modern controls: quick turn | 🟢 Doable | Write the facing angle on a button press |
| Expanded inventory | ✅ Done | Inventory-floor mod raises bag size; editor bag mods |
| Storage from anywhere | 🔴 Hard (🟢 on a newer engine) | Needs "call game function"; give item covers most needs meanwhile |
| Easier mods / permits | ✅ Done | Item editor sets mods directly; give item gives Tool Kits / Mod Permit |
| Dismantle unwanted gear | 🟢 Doable | Remove the item in the editor and grant its mods/bonuses elsewhere |
| Stat / DPS transparency | 🟡 Research | F1 can show read-only numbers; the damage formula needs mapping |
| Skip FMVs | 🟡 Research | Engine has FMV skip; PE needs its skip configuration found |
| Faster or skippable dialogue | 🟡 Research | Text speed is probably a variable; skipping scripted scenes is hard |
| Skip real-time cutscenes | 🔴 Hard | Scripted events; skipping safely means understanding each script |
| Extra healing / early checkpoints | ✅ Covered differently | God mode, give item; placing new pickups in rooms is 🔴 |
| Fast travel / warp | 🟡 Research (🟢 on a newer engine) | Room-transition data needs mapping; a game-function call makes it easy |
| Clearer map | 🔴 Hard | New map UI; the F1 menu is text-only |

---

## Combat & controls

### Visible invisible walls — 🔴 Hard
Two problems. We'd need to find where a battle's movement boundary is stored (battle
code in the decomp; not mapped yet), and then draw an outline *in 3D* over the
pre-rendered background, which means reading the game's camera matrix and projecting
points ourselves. 2D overlay drawing works, but 3D lines in the world are a project of
their own.
**Cheaper alternative (🟡):** if the boundary is data, *enlarging* it might be possible
without drawing anything. Needs the battle-area research first.

### Streamlined ATB items — 🟡 Research
If the "needs a full gauge" rule is a constant in main-EXE code, we can't change it live
(it could be a build-time change). If it's a per-command cost in a table, it's a data write
and becomes 🟢.
**Already possible:** faster ATB overall, via the **Active time** stat in the Stats page
(the level drives the gauge's fill rate).

### Modern controls
- **Analog movement — ✅ in the game already.** The field movement code reads the analog
  stick and moves Aya at any angle (`Scene_PlayerMovement.c`). Battle movement wasn't
  checked.
- **Always run — ✅ Done.** `Always run` toggle (hold the run button to walk), plus
  `Run speed` and `Walk speed`. D-pad only; analog full tilt already runs.
- **Quick turn — 🟢 Doable.** Aya's facing angle is a known field (`actor+0x3A`). A mod can
  flip it 180° on a button combo while she's standing. Needs a free button and a check that
  the game doesn't overwrite it the same frame.

## Inventory & gear

### Expanded inventory — ✅ Done
The **inventory-floor** mod raises Aya's bag size. The Item Editor can also put bag +1/+2/+4
mods on armor, and refuses changes that would strand items.

### Storage box from anywhere — 🔴 Hard now, 🟢 on a newer engine
Opening Wayne's storage means running the game's storage-menu code. Our engine can't call
game functions; newer upstream psxrecomp can (`psx_mod_call_guest`), which would make this
an F1 action. **Meanwhile:** `Debug > Give item` gets you any item without a trip to storage.

### Easier mods / permits — ✅ Done
The **Item Editor** sets any mod on the equipped gun or armor directly (game names, one per
kind, bag-safety guard). **Give item** hands out Tool Kits, Super Tool Kits and the Mod
Permit.

### Dismantle gear — 🟢 Doable
The game already has the logic to move bonuses/mods between items and delete the donor
(`Inv_TransferItemBetweenLists`). A mod can do the same with data writes: remove an item
from the bag and add its +N bonuses or mods to the equipped gear. Main care point: freeing
the equipment record correctly and never removing the equipped item.

### Stat / DPS transparency — 🟡 Research
**Display is easy:** F1 can show read-only rows such as "Shots per turn", "Damage per shot"
or "Est. damage per turn" for the equipped gun. **The work** is mapping the damage formula
from the battle code (`Battle_ApplyDamage` and friends) so the numbers are right. Showing it
in the game's own equip screen (instead of F1) would be 🔴.

## Pacing

### Skip FMVs — 🟡 Research
The engine has an FMV auto-skip switch (`psx_mod_set_auto_skip_fmv`), which ends movies
through the game's own end-of-movie path once a game supplies a few addresses in
`game.toml` (`[video] fmv_skip_*`). PE has none configured yet; without them the engine
falls back to injecting START. Finding PE's movie-player variables in the decomp is the
task.

### Faster / skippable dialogue — 🟡 Research
Text printing speed is likely a variable in the textbox engine (`Menu_TextboxDraw.c`); if
so, faster text is a data write. "Skip this dialogue" is much harder: textboxes are driven
by event scripts, and skipping must still run each script's side effects.

### Skip real-time cutscenes — 🔴 Hard
In-engine cutscenes are event scripts that move actors, set story flags and load rooms.
Skipping one safely means applying all its effects. A blanket "skip" toggle risks soft-locks.

### Early-game safety net — ✅ Covered differently
**God mode**, **Give item** (any healing item) and the **Stats** page already let a struggling
player get past a bottleneck. Placing *new* pickups in rooms is 🔴 (room data and scripts).

### Fast travel / warp — 🟡 Research, 🟢 on a newer engine
PE already has a New York map for travelling between districts. A "warp to room X" debug
action needs either the room-transition variables (the decomp has
`Task_BeginSceneTransition`; the data it sets isn't mapped yet) or a game-function call
(newer engine). A redesigned map UI is 🔴; the F1 menu is text-only.

---

## Suggested next steps

1. **Quick turn** and **Dismantle gear**: small, clear, data-only.
2. **FMV skip**: find PE's movie-player variables; the engine work already exists.
3. **Faster text**: check the textbox engine for a speed variable.
4. **Research pass on battle data**: action/ATB costs, arena boundary, damage formula.
   This unlocks the ATB, invisible-walls and DPS items.
5. **Move to a newer engine** when Alex's line is ready. "Call game function" unlocks
   storage-anywhere and warp, and may make code-level changes easier.
