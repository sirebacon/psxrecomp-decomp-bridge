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
  **But (verified 2026-10-11):** *new* code we write into memory does run when the game
  reaches it through a function pointer, for example a menu window's callback. See "Can we
  add to the game's own menus?" below.
- **Call a game function directly from the C plugin** (for example "open the storage menu"
  or "warp to a room"). Our engine version has no such call; newer upstream psxrecomp does
  (`psx_mod_call_guest`). *Likely workaround, untested:* injected code running from a game
  callback (above) can itself call any game function with an ordinary MIPS `jal`.

**Possible but not set up / unverified**

- **Build-time code changes:** patch the EXE and regenerate the recompiled C. Permanent (no
  live toggle) and slow to iterate. An earlier attempt "had no effect", but it patched the
  wrong function, so this lever is untested rather than ruled out.
- **Function-entry hooks (verified 2026-10-11, test B):** the engine calls a mod's C code
  when a listed game function starts. The functions are listed in the game config at build
  time; PE lists none in its normal build yet.
- **Patching overlay code:** rooms, battles and menus are code overlays loaded at runtime.
  Changes to *their* code in memory might take effect (they're run from memory, not
  precompiled into the EXE), but that's untested.
- **Drawing over the game:** an early mod drew its own boxes and text into the frame. That
  works for simple 2D shapes; 3D outlines in the world would need the camera maths too.

### Can we add to the game's own menus? Five levers to test

Several items above are 🔴 only because they'd need a new screen or row in the *game's*
menus (a junk shop, DPS on the equip screen, a map). **It's possible: lever 2 was tested
live and works (test A).** The routes, cheapest first:

1. **Change the data the menus are built from. 🟡 likely.** PE's menus are a widget system
   (`MenuWidget_Lifecycle.c`). Each window is built from a *grid descriptor* (position,
   width, visible rows, row limit), and its text comes from the game's string tables. Both
   are data, so a mod can resize windows or change their text. Adding real behaviour needs
   one of the levers below.
2. **Redirect a menu's callback. ✅ verified 2026-10-11 (test A, below).** Every live menu
   window stores its update, draw and item-action routines as *function pointers in RAM*
   (for example `node->update = Menu_StepScrollCursor`). Changing a pointer is a data write.
   Pointing it at *new MIPS code we write into memory* works. The game reaches the pointer
   through the engine's dispatcher, which finds no precompiled function at that address and
   hands it to the engine's interpreter, the same path room and battle overlays use. Our code
   can then jump on to the original routine, or replace it. Patching *existing* code fails
   for a different reason: calls to precompiled functions go straight to the native version
   and never look at RAM. **So mods can add new behaviour to the game's own menus on this
   engine.**
3. **Build-time function hooks. ✅ verified 2026-10-11 (test B, below).** Our engine can call
   a mod's C code at the start of chosen game functions (`mod_function_entry_funcs` in the
   game config, then regenerate and rebuild). The mod sees the CPU registers and memory and
   can change them before the function runs. Hooking `MenuWidget_UpdateAndDraw` runs our C
   every frame a menu is drawn: insert a window, adjust a list, or draw extra text such as
   DPS on the equip screen. It can't skip the original function, and each new hook address
   costs a regenerate and rebuild (about 2 minutes).
4. **A mod-drawn screen in the game's style. 🟢 proven.** An early version of our menu drew
   its own boxes and text into the frame and read the pad. A shop or map screen can be built
   this way, looking like the game but entirely run by the mod. Pausing the game underneath
   it still needs working out (for example by opening the game's own menu first).
5. **Newer engine: call game functions (`psx_mod_call_guest`). 🟢 later.** Lets a mod open the
   storage menu or run any game routine directly.

**Test A — passed (2026-10-11, live, slot 2 save, game's Triangle menu open).**

- The menu's current window (`0x800A2370`, the left icon column) had
  `update = 0x80063E0C` (`Menu_StepScrollCursor`) at node `+0x2C`, as the decomp says
  (active-window list head `0x8009D154`, current window `0x8009D15C`).
- I wrote 7 MIPS instructions into unused RAM at `0x801E8000` (a 45 KB block that stayed
  zero across three RAM dumps): add 1 to a counter at `0x801E8100`, then `j 0x80063E0C`.
  Then I set the window's `update` to `0x801E8000`.
- **Pressing DOWN twice took the counter 0 → 1 → 2, and the cursor still moved** (Use
  Item → Change Weapon). The engine's interpreter stats list our addresses as executed.
- **Replacing the behaviour works too.** A routine that just returns "handled"
  (`li v0,1; jr ra`) made DOWN do nothing. Restoring the original pointer brought the menu
  back to normal.

What this means: the game's menus can run mod-written code, both *added to* and *instead of*
the game's own. This doesn't need a rebuild or a newer engine. Practical notes for building
on it:
- Mod code should live in memory the engine gives the mod (`psx_mod_alloc_guest_memory`),
  not in "free-looking" RAM like the test used.
- Pointers must be re-applied whenever the game rebuilds a window (each menu open), so a
  per-frame plugin watches the window list.
- Our routines are interpreted, so they're slower than native, but fine for menu logic.
- The routines are written as MIPS machine code, so we'd want a small assembler step in
  the mod build (or keep them tiny and let the C plugin do the heavy lifting through
  shared memory).

**Test B — passed (2026-10-11, live, slot 2 save, game's Triangle menu open).**

- I added `mod_function_entry_funcs = ["0x80062FEC", "0x80063E0C"]` to `game.toml`
  `[recompiler]` (`MenuWidget_UpdateAndDraw` and `Menu_StepScrollCursor`; the first
  address comes from the seed list between `MenuWidget_InitPool` and
  `MenuWidget_OffsetPosition`). Then I ran `build-recompiler\psxrecomp-game.exe --config
  game.toml` (7 s) and rebuilt (about 2 min).
- Regenerating changed exactly two lines in one shard (`SLUS_006.62_full_28.c`): a
  `psx_mod_function_entry(cpu, addr)` call at the top of each function, before the body
  reads any register.
- A probe plugin (`psx_mod_register_function_entry_plugin`, no manifest or activation
  needed) logged:
  - `MenuWidget_UpdateAndDraw` about once per frame while the menu was open (120 calls in
    a few seconds);
  - `Menu_StepScrollCursor` once per input, with the game's real arguments: window
    `0x800A2370`, flags `0x10` when the menu opened and `0x4000` for each DOWN.
- The menu behaved normally. Afterwards I removed the config line and probe, restored the
  shard and rebuilt; `generated/` matches the pre-test backup byte for byte.

### Which lever for what

| | Redirect a pointer (A) | Build-time hook (B) |
|---|---|---|
| Language | MIPS machine code | C, in the mod plugin |
| Rebuild needed | No, works live | Yes, per new hook address (~2 min) |
| Where it works | Anywhere the game calls through a pointer (menu windows, many callbacks) | Start of any precompiled game function |
| Replace the game's code | Yes | No: runs first, then the original always runs (it can change the arguments) |
| Speed | Interpreted | Native |
| Best for | Swapping a window's behaviour, adding new handlers | Running C at a known moment: per-frame menu work, reading or tweaking arguments |

They combine well: a hook (B) on a menu-building function can set a window's pointer (A)
at exactly the right moment, and the MIPS part can stay a few instructions that call back
into the game.

Now that A works, the 🔴 "needs a new game screen" items drop to 🟡: a shop for junk, DPS
in the equip screen, storage from anywhere. Next step: build one small real feature on it,
for example an extra row in an existing game menu.

---

## Summary

| Wish | Verdict | Short reason |
|---|---|---|
| Visible invisible walls (battle) | 🔴 Hard | Need the arena boundary data *and* 3D drawing in the world |
| Items on one ATB segment | ✅ Done (PE `c3feba9`, `d5980d7`) | `Half-bar ATB` submenu: Items (default), PE, Change weapon/armor and Escape can each be allowed from a half bar at half cost; the others' tabs are removed on a half bar; the bar turns gold. Verified in a battle |
| Modern controls: analog | ✅ Already in the game | The field code already supports free analog movement |
| Modern controls: always run | ✅ Done | Always run toggle + hold-to-walk |
| Modern controls: quick turn | 🟢 Doable | Write the facing angle on a button press |
| Combat pacing with faster Aya | 🟡 Research | Speed mods should be field-only (check why combat feels faster); an enemy-speed slider needs battle data |
| Expanded inventory | ✅ Done | Inventory-floor mod raises bag size; editor bag mods |
| Storage from anywhere | 🔴 Hard (🟢 on a newer engine) | Needs "call game function"; give item covers most needs meanwhile |
| Easier mods / permits | ✅ Done | Item editor sets mods directly; give item gives Tool Kits / Mod Permit |
| Dismantle unwanted gear | 🟢 Doable | Remove the item in the editor and grant its mods/bonuses elsewhere |
| Improved enemy drops | 🟢 bonus drops / 🟡 real drop rates | Our own "bonus item after a win" is easy; changing the game's own item gains needs the battle data mapped |
| Stat / DPS transparency | ✅ First version done (PE `7c9a068`) | Highlighting a gun in the game's own menu shows "PWR n" (power per turn, from the decomp's damage formula) in the title bar, through a build-time hook on `Draw_PrintRawText` |
| Skip FMVs | 🟡 Research | Engine has FMV skip; PE needs its skip configuration found |
| Faster or skippable dialogue | 🟡 Research | Text speed is probably a variable; skipping scripted scenes is hard |
| Skip real-time cutscenes | 🔴 Hard (one experiment) | Scripted events; but the game may have its own debug event skip (see "More ideas") |
| Extra healing / early checkpoints | ✅ Covered differently | God mode, give item; placing new pickups in rooms is 🔴 |
| Fast travel / warp | 🟢 Try it (see "More ideas") | An old debug-warp cheat code suggests room changes are a data write; phone-to-phone warp for visited places |
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

### Streamlined ATB items — ✅ Done: "half bar for items" (PE `c3feba9`, verified in battle 2026-10-11)

**Built and tested** with a build-time hook on `Battle_Update` (0x800299CC), in a save state
taken mid-fight. Toggle: `PE Enhancements > Half-bar items` (default off).

- Triangle at a half-full gauge opened the item list.
- Medicine used from a gauge of about 7650 left **3150** (= − 4500; vanilla leaves 0), and
  HP went 41 → 45.
- Backing out with Circle put the gauge back (about 7600). The item stayed in the bag and no
  attack was possible.
- **Indicator:** the ATB bar turns **gold** between half and full (its four vertex colours,
  `0x800B00E8 + slot×0x24`, offsets +4/+0xC/+0x14/+0x1C), is normal blue below half, and
  shows the game's own full-bar colours at full.
- In the battle menus, Circle is cancel and Square is not.

**Per-action version (PE `d5980d7`, verified in battle 2026-10-11).**
`PE Enhancements > Half-bar ATB ›` submenu:

| Row | Default |
|---|---|
| Enabled | off |
| Items | on |
| Parasite Energy | off |
| Change weapon | off |
| Change armor | off |
| Escape | off |

- **Tabs:** the battle menu's tabs come from `g_MenuItemContextFlag` (`0x8009CEF0`), bits
  0–4 = Use Item / PE / Change Weapon / Change Armor / Escape. Bit order was confirmed by
  allowing PE: the tab reappeared. On a half-bar borrow the mod clears the bits of actions
  that aren't allowed, so those tabs aren't in the menu at all, and puts the flag back when
  the turn ends.
- **What the turn did** is read from the battle queue (`Battle_StepScriptEntry`: 1–2
  shots, 3–0x182 item, 0x183–0x196 PE, 0x197–0x198 equipment, 0x199+ escape), plus
  equipment-slot and item-count changes. Move doesn't count.
- **Cost:**

  | Turn | Gauge after |
  |---|---|
  | Borrowed, allowed action | saved − 4500 |
  | Borrowed, nothing done | saved |
  | Borrowed, anything else | 0 (no free actions) |
  | Full bar, allowed action | 4500 (half cost) |
  | Full bar, attack | 0, as vanilla |

- **Checked live:**
  - half-bar menu with only Use Item (flags `0x7F` → `0x61`);
  - Use Item + PE once PE is allowed (`0x63`);
  - backing out restores tabs and gauge;
  - the full-bar menu keeps all five tabs;
  - Medicine from about 7100 left 2600;
  - Heal (PE) from a full bar left 4500.
- **Not yet checked:** weapon/armor change and escape on a half bar (same code path,
  classified by queue command or slot change).

Original research and design below.
**Idea:** let Aya use an item once her turn gauge is **half** full, and have an item cost
**half** a bar instead of a whole turn. Attacks and Parasite Energy still need a full bar.

**How the game's turn works (decomp, read 2026-10-11; nothing tested in battle yet):**
- **The turn gauge** is the field the decomp calls `hpAlive` in Aya's battle record
  (`Combatant +0x10`, u16, **0..9000**). The HUD draws the ATB bar from it
  (`Battle_ActiveAndEnemyStatusFlow.c`: width = gauge × 56 / 9000). It fills each frame by
  `scaledOffense` (`+0x24`, from the Active Time stat); slow costs 2/5 of that and haste adds
  half (`Menu_MainUpdate.c`).
  **Naming trap:** the fields called `exp_or_acc` / `maxAtk` (`+0x08` / `+0x28`, 16.16) are
  **Parasite Energy**, the PE bar, not the turn gauge.
- **The only gate is one check in main-EXE code.** `Battle_Update.c` (phase `D_8009D28C`
  == 0) does `if (gauge >= 9000)`. Then a press of the attack button (pressed bits
  `D_8009D1F4 & 0x200`) starts targeting, and a press of the item button (`& 0x80`) opens
  Aya's item list (`Inventory_OpenAyaItemList`; item-menu state `0x8009D1F0` = 1). Either way
  the battle moves to phase 1, handled by `Battle_HandleItemMenu`
  (`Battle_TargetAndEnemyTurnFlow.c`).
- **A finished action empties the gauge.** `FinishAction()` sets it to 0. That happens when
  the item is used (menu state −1), and also when the player backs out of the turn.
- **Items are queued battle commands** (queue `0x800BE830`; a command value of 3..0x182 means
  "item value − 3"). Unexecuted item commands go back to the bag (`Battle_FlushScriptSounds`).
  So a mod can see from data whether the turn used an item.
- The item rows are only dimmed while another action is queued or the battle is ending
  (`Pad_IsMenuConfirmAvailable`). The gauge isn't re-checked inside the menu.

**Why it's doable without patching code ("borrow and refund"):** the gate reads a data
field, so a mod can make the check pass, then fix the gauge afterwards.

1. **Borrow (start of the item turn).** In battle phase 0, if Aya's gauge is between 4500 and
   9000 and the item button is pressed this frame (and attack isn't), the mod saves the
   gauge, a copy of Aya's bag, and then sets the gauge to 9000. The game's own check then
   opens the item list exactly as it would on a full bar.
   - **Best timing:** a build-time hook (lever B) on `Battle_Update` runs our C code right
     before the check, in the same frame as the press. Only the item button is pressed, so
     the borrowed full bar can't be spent on an attack.
   - **Without a hook:** do it from the per-frame plugin. That leaves a one-frame window
     where the attack button would also work, plus the "gauge full" chime and flash. Fine for
     a prototype.
2. **Refund (end of the turn).** When the battle returns to phase 0, the mod compares Aya's bag
   with the saved copy:
   - an item was used → gauge = saved − 4500;
   - nothing changed (backed out) → gauge = saved.
3. **Same rule from a full bar (optional):** an item turn started at 9000 leaves 4500, so
   "items cost half a bar" holds everywhere.

**Half-bar indicator (optional):** the bar's colours are plain HUD data (`D_800B00EC..`,
rewritten by the game every frame). A mod or hook could tint the bar once it passes half, as
the game does for a full bar. Not needed for the mechanic.

**Open questions for the first battle test:**
- which pad buttons bits `0x80` / `0x200` are (Triangle / Cross expected);
- whether the full-bar chime or flash appears when borrowing without the hook;
- what backing out of the item menu does in vanilla (it may already cost the turn);
- that enemies' timing isn't affected.

Testing needs a save state just before a fight.

**Already possible:** a faster turn gauge overall, via the **Active time** stat on the Stats
page.

### Modern controls
- **Analog movement — ✅ in the game already.** The field movement code reads the analog
  stick and moves Aya at any angle (`Scene_PlayerMovement.c`). Battle movement wasn't
  checked.
- **Always run — ✅ Done.** `Always run` toggle (hold the run button to walk), plus
  `Run speed` and `Walk speed`. D-pad only; analog full tilt already runs.
- **Quick turn — 🟢 Doable.** Aya's facing angle is a known field (`actor+0x3A`). A mod can
  flip it 180° on a button combo while she's standing. Needs a free button and a check that
  the game doesn't overwrite it the same frame.

### Combat pacing with faster Aya — 🟡 Research
Playtest note: with the speed mods on, Aya feels faster in combat as well as outside it.
That makes battles easier, but also much more fun and active. Two ways to balance it:

1. **Keep battles at stock speed.** Our `Run speed` / `Walk speed` / `Always run` code is
   meant to be field-only: it switches off while the battle flag (`0x8009D1A0 & 2`) is set,
   and battle movement uses its own constants. So the first step is to check *what* is fast
   in combat: our mod (a bug in the battle gate), or the engine's turbo key (Tab speeds up
   *everything*, enemies included). If it's ours, fixing the gate restores stock battles. 🟢
2. **Speed enemies up to match.** Keeps the more active feel without making fights easier.
   Needs the enemy movement and ATB speed in the battle data mapped (`Battle_StepEnemyMovement`,
   enemy `Combatant` fields). If they're per-enemy values in memory, an "Enemy speed" slider
   is a data write. 🟡 It could also come with an "Aya battle speed" slider, if the battle
   movement constants turn out to be data too.

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
Permit.(maybe in game buy mods based off the number of junk given in. new ingame menu might be required to create a shop)

### Dismantle gear — 🟢 Doable
The game already has the logic to move bonuses/mods between items and delete the donor
(`Inv_TransferItemBetweenLists`). A mod can do the same with data writes: remove an item
from the bag and add its +N bonuses or mods to the equipped gear. Main care point: freeing
the equipment record correctly and never removing the equipped item.
- **already dismantled items should be re-acquired somehow** either by buying it via junk or random drop chance from enemy if the item was already destroyed.

### Improved enemy drops — 🟢 bonus drops, 🟡 the game's own drops

> **Superseded by the loot-overhaul design:**
> [pe-loot-overhaul-design-2026-10-11.md](pe-loot-overhaul-design-2026-10-11.md). The real
> drop is each enemy's `rewardSlotId` (+0x9E), handed out through a 10-slot reward list. The
> "reward queue" below is actually the battle command queue.
What the decomp shows about items changing hands in battle (from reading the code; nothing
tested live yet):

- **Taking items from enemies.** Each enemy has a takeable item, `stealItemId`
  (`EnemyCombatant+0x9F`), and a chance mode in bits 12–13 of `statusFlags2` (`+0xCC`):
  mode 0 is a coin flip, mode 2 always succeeds (`Battle_ResolveHitOnTimer.c`). Both live in
  the enemy's battle record in RAM, so a mod could raise the chance or swap in a better
  item when a battle starts. That's a data write. 🟡 What still needs confirming in the game:
  which of Aya's actions triggers it, and where the enemy records sit in memory.
- **Battle reward queue.** At the end of a battle the game adds every queued entry with a
  value of 3–0x182 to the inventory as an item (`Battle_FlushScriptSounds.c`,
  `Battle_PhaseAndEnemyEffectFlow.c`; queue at `0x800BE830`). That looks like the game's own
  drop delivery. Finding what fills the queue, and from which per-enemy data, is the research
  that would let us raise real drop rates or improve the item pool. 🟡
- **Not drops:** `Entity_HitAndDropTable.c` is misnamed. It computes enemy attack damage.
  The "loot" fields (`lootItemId` `+0xA0`) are enemies *stealing* Aya's items or ammo, which
  she gets back when the thief dies.

**Doable now (🟢): our own bonus drops.** The mod can spot a won battle (the battle flag
clears without a game over) and give a random item through the same path `Debug > Give item`
uses. Settings would be a chance per win and an item pool (healing only, ammo, or anything).
It doesn't need the game's drop logic at all. The one thing to handle is a full bag: skip the
drop, or show a footer note.

### Stat / DPS transparency — ✅ first version done (PE `7c9a068`, verified live)
Highlight a gun in the game's own menu (for example Change Weapon) and the title bar reads
"Handgun  PWR 20". The number is **power per turn before enemy defense**, from the decomp's
damage code (`Battle_StepEnemyMovement.c`, despite the name):

- per shot = (Aya attack ÷ 5 + gun attack) × shot% ÷ 100, where shot% depends on shots per
  turn: 1 → 100, 2 → 60, 3 → 41, 5 → 25, 7 → 18, 10 → 13;
- per turn = shots × per shot. In battle each shot then loses enemy defense ÷ shots and is
  scaled by weaknesses or resistances;
- Aya attack = her `stat1E` (player → core + 0x1E); gun attack = base + bonus (max 999),
  halved by mod effect 16; shots = 1, or 2/3/5/7/10 for the group-1 mods (table at
  `0x800923D0`).

How it's shown: a build-time hook on `Draw_PrintRawText` swaps the text pointer for a copy
with " PWR n" appended. It does this only when the call comes from the title-bar function
`Menu_DrawContextHelpText` and the text is a gun's (table C). Toggle: `Weapon power`.
Checked by hand on two weapons: M84F 20, Club 16.

**PWR is per turn, not per second.** Aya's turn gauge fills at a rate set only by her
Active Time stat and haste/slow (`Menu_MainUpdate.c`, start of the battle update), never by
the gun. So a
per-second figure is PWR × the same factor for every gun, and the ranking doesn't change.
PWR leaves out enemy defense, weaknesses and range (all per enemy), and also magazine size
and reloading. That last one *can* change the ranking: a big-burst gun with a small
magazine reloads more often.

**To do later (true DPS, two steps):**
1. **Turns per minute from the ATB code.** Compute Aya's time between turns from her stats.
   *Corrected 2026-10-11:* the turn gauge is the Combatant field the decomp calls
   `hpAlive` (+0x10, 0..9000; the HUD draws the ATB bar from it). It fills each frame by
   `scaledOffense` (+0x24, derived from the Active Time stat). Slow costs 2/5 of that and
   haste adds half (`Menu_MainUpdate.c`, start of the battle update). So a turn takes about
   `9000 / scaledOffense` frames. The `exp_or_acc` / `atbStep` math nearby is **Parasite
   Energy** regeneration, not the turn gauge (see "Streamlined ATB items").

   This shows how much Active Time matters, but doesn't change how guns rank.
2. **Sustained power with magazine size and reloads.** This is the part that changes the
   ranking. First confirm in the decomp how battle reloading works and what it costs (time
   or a turn; see `Inv_DrawSlotItemIcon` / `BattleCmd_CommitAmmoAndUpdate`). Also check
   whether a burst larger than the loaded rounds fires fewer shots. Then show it next to
   PWR, for example "Handgun  PWR 20 (18)".

**Next improvements:**
- with two copies of the same gun, show the highlighted copy (it currently uses the
  equipped one or the first match);
- show per-shot damage against the current enemy during battle;
- add the same text in other screens.

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

**Player-friendly version: warp between save phones.** Instead of any room, offer only the
save phones, and only ones in places Aya has already visited. Phones are safe entry points
(the game already expects you to arrive and leave there), and the list is short, so it fits
an F1 choice row. Extra research: a "visited" check, either a story/room-visited flag in the
save data or our own record of rooms Aya has entered (the mod can log the current room
every frame). That version can sit on the main page rather than in Debug.

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
| Random battles on/off | ✅ Done (PE `556805b`) | `No random battles` row: a live view of the game's own switch, bit `0x8000` at `0x800A781A` (`g_BattleSkip`). It's in the script-variable area the game **saves**, so a save made with it on keeps battles off until the row is turned off. Bit set/clear verified live; stopping encounters still needs a playtest |
| Encounter-rate slider | 🟡 Research | Only on/off is known; a rate needs the encounter-chance variable |
| Event skip | 🟢 Works (first test 2026-10-14, PE `a0cb1ac`) | Code `800A77F0 0004` (`g_EventSkip`, bit 0x4 of script variable 0) is the game's own debug event skip. With it on, a cutscene went straight into gameplay, no button needed. F1 > Debug > `Event skip (test)`. Still to check: story flags/items after skipped scenes, and a hold-X-to-skip trigger built on it |
| Faster door transitions | 🟡 Try it | Code zeroes `0x800BCFBC..CE`, which hold a dark semi-transparent rectangle (GPU command `0x62090909`): that removes the fade *visual*, maybe not the wait |
| Infinite / refill ammo | ✅ Done (PE `556805b`) | `Infinite ammo` row: Refill spares (the gun's pool, capacity 999) or Never reload (also keeps the loaded rounds full, in battle via Aya's action `attackWord`). Verified in the field (3 → 6 loaded, pool 6 → 999); battle side still needs a playtest |
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

## Ideas from the Parasite Eve 2 HD Remaster

What the PE2 native port has that PE1 lacks *and that we could do as a mod*. Engine and
HD-art items (resolution, PGXP, 60 fps, widescreen, single-disc play, HD assets, texture
packs, languages) belong to mstan/Alex or an art project; see
[pe1-vs-pe2-native-features-2026-10-11.md](pe1-vs-pe2-native-features-2026-10-11.md).

| Idea | Verdict | How |
|---|---|---|
| Faster loading (doors, "Now Loading") | 🟢 Doable | The engine already gives mods `psx_mod_set_load_acceleration` (faster wall-clock loads, same game timing) and `psx_mod_set_disc_speed` (faster emulated CD). A `Faster loading` row turns them on; test music/FMV sync |
| Infinite Parasite Energy | 🟢 Doable | Same pattern as God mode: keep Aya's battle PE value full each frame. The PE field needs finding in the battle data first |
| Booster hotkeys | 🟢 Doable | Toggle God mode / infinite PE / run speed with button combos instead of opening F1 (we already read the pad). On-screen status icons would need drawing into the frame: 🟡 |
Single-disc play (no disc swap) is left out on purpose: swapping or merging discs is engine
and launcher work, not a mod.

Already matched in PE1: hold-Tab turbo (PE2's Speed x4), God mode (infinite HP), max bonus
points, max EXP (Stats > Level), save states, and modern analog controls.

---

## Suggested next steps

1. **Cheat-code toggles first** (cheapest, high demand): random battles on/off and infinite
   ammo are ✅ done; the outfit picker is left.
2. **Faster loading** toggle: the engine switches exist; mostly testing.
3. **Warp and event skip experiments**: try the debug-room warp's room-change write and the
   debug event skip; if they work, fast travel and cutscene skipping become real options.
4. **Infinite Parasite Energy**, **booster hotkeys**, **quick turn**, **dismantle gear**,
   **bonus drops after a win**: small, data-only.
5. **Check why combat feels faster with the speed mods** (our battle gate or the turbo key).
6. **FMV skip**: find PE's movie-player variables; the engine work already exists.
7. **Faster text**: check the textbox engine for a speed variable.
8. **Research pass on battle data**: action/ATB costs, arena boundary, damage formula, the PE
   field, enemy speed, and the reward queue. This unlocks the ATB, invisible-walls, DPS,
   infinite-PE, enemy-speed and real drop-rate items.
9. **Move to a newer engine** when Alex's line is ready. "Call game function" unlocks
   storage-anywhere and makes code-level changes easier.
