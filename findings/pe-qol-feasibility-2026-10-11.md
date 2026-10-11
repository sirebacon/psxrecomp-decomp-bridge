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
| Skip real-time cutscenes | 🔴 Hard (one experiment) | Scripted events; but the game may have its own debug event skip (see "More ideas") |
| Extra healing / early checkpoints | ✅ Covered differently | God mode, give item; placing new pickups in rooms is 🔴 |
| Fast travel / warp | 🟢 Try it (see "More ideas") | An old debug-warp cheat code suggests room changes are a data write |
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

### Skip real-time cutscenes — 🔴 Hard, with one cheap experiment
In-engine cutscenes are event scripts that move actors, set story flags and load rooms.
Skipping one safely means applying all its effects. A blanket "skip" toggle risks soft-locks.
**Experiment:** an old cheat code (`800A77F0 0004`) turns on what looks like the developers'
own event-skip feature. If the game's own code does the skipping, it presumably applies the
event's effects correctly. Worth testing before writing anything ourselves.

### Early-game safety net — ✅ Covered differently
**God mode**, **Give item** (any healing item) and the **Stats** page already let a struggling
player get past a bottleneck. Placing *new* pickups in rooms is 🔴 (room data and scripts).

### Fast travel / warp — 🟢 Try it
PE already has a New York map for travelling between districts. A "warp to room X" action
looks possible as a plain data write: the old debug-room cheat code writes `0x6048` to
`0x8009D280` (which reads `0x2048` in play), suggesting a "change room" bit plus a room
number. Still to do: confirm it in our build, then build a list of room numbers and safe
entry points (the decomp's room overlays and `Task_BeginSceneTransition` help). Warping
mid-story can break progression, so it belongs in the Debug page. A redesigned map UI is
🔴; the F1 menu is text-only.

---

## More ideas: player complaints and old cheat codes

Two sources: what reviewers and players complain about most (slow movement, the cramped
inventory, hard-to-find items in dark rooms, late-game rooms where *every* visit is a
battle, hard-to-read text, dying after the last boss), and the old **Action Replay**
cheat codes for the US release. Most cheat codes are plain memory writes, which is exactly
what our mods can do, so a code that worked on a real PlayStation is a strong hint for a
mod here. I read each address in a live save to check the values make sense; none of these
has been tried as a mod yet.

| Idea | Verdict | Basis |
|---|---|---|
| Random battles on/off | 🟢 Likely easy | Code `800A781A 8000` sets a flag bit (reads `0x0000` in play) |
| Encounter-rate slider | 🟡 Research | Only on/off is known; a rate needs the encounter-chance variable |
| Event skip | 🟢 Try it | Code `800A77F0 0004` turns on what looks like a built-in debug "event skip"; how it's triggered needs finding out |
| Faster door transitions | 🟡 Try it | Code zeroes `0x800BCFBC..CE`, which hold a dark semi-transparent rectangle (GPU command `0x62090909`): that removes the fade *visual*, maybe not the wait |
| Infinite / refill ammo | 🟢 Easy | Code writes `0x800A1E6E`, the ammo pool our give-item code already uses |
| Outfit picker | 🟢 Easy (cosmetic) | Code writes the costume byte `0x800B0CE2` (reads `0x0A` in play). The "liberated" outfit freezes the game in battle, so it must be blocked or field-only |
| Warp to any room | 🟢 Try it | Debug-room code writes `0x8009D280 = 0x6048` (reads `0x2048` in play), which looks like "change room" + a room number. Data, so no engine change needed; needs a room list |
| Debug room / hidden options | 🟡 Research | Codes reach the developers' debug room and two hidden option chests; what they offer is unknown |
| Hyper Mode | 🔴 Not as a live mod | Code patches an instruction at `0x80073A9C` (a branch, `0x04810005`) in the main program, which can't be patched live in this build (see top) |
| Brighter dark rooms | 🟡 Engine side | A brightness/gamma option in the renderer, not a game change; the F1 graphics page has none yet |
| Highlight interactable spots | 🔴 Hard | Needs the hotspot data per room plus drawing markers in the 3D scene |
| Readable damage numbers / text | 🟡 Research | A fan font hack exists for the disc; the mod system can patch disc data (disc-level patches), so it could be ported. Higher internal resolution is engine work |
| Safety net for the final boss / points of no return | ✅ Engine | Save states (F7, 12 slots) save anywhere |
| Explain the good-luck charms | 🟡 Low value | The game never says what they do; an F1 info row could, once their effect is read from the decomp |
| Clearer evasion feedback | 🔴 Hard | Battle-timing UI; nothing to hook into yet |

**What this changes in the list above:** *Fast travel / warp* moves up from research to "try
it" (the debug warp suggests room changes are data), and *Skip real-time cutscenes* gets a
cheap first experiment: the game's own debug event skip.

Sources: player and reviewer complaints from
[RPGamer review](https://archive.rpgamer.com/games/pe/pe/reviews/perdrev12.html),
[RPGamer staff review](https://archive.rpgamer.com/games/pe/pe/reviews/pestrev5.html),
[RPGFan review](https://www.rpgfan.com/review/parasite-eve-3/),
[Bloody Disgusting retrospective](https://bloody-disgusting.com/news/3257902/ghosts-of-gaming-past-a-review-of-parasite-eve/),
[Cubed3 review](https://www.cubed3.com/games/reviews/playstation/parasite-eve),
[Fanlore](https://fanlore.org/wiki/Parasite_Eve) (font hack); cheat codes from
[Almar's Guides: Parasite Eve Action Replay codes](https://almarsguides.com/retro/walkthroughs/PS1/Games/ParasiteEve/ActionReplay/).

---

## Suggested next steps

1. **Cheat-code toggles first** (cheapest, high demand): random battles on/off, infinite
   ammo, outfit picker. Each is a known address and a data write.
2. **Warp and event skip experiments**: try the debug-room warp's room-change write and the
   debug event skip; if they work, fast travel and cutscene skipping become real options.
3. **Quick turn** and **Dismantle gear**: small, clear, data-only.
4. **FMV skip**: find PE's movie-player variables; the engine work already exists.
5. **Faster text**: check the textbox engine for a speed variable.
6. **Research pass on battle data**: action/ATB costs, arena boundary, damage formula.
   This unlocks the ATB, invisible-walls and DPS items.
7. **Move to a newer engine** when Alex's line is ready. "Call game function" unlocks
   storage-anywhere and makes code-level changes easier.
