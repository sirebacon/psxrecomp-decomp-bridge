# Groundwork for an in-game mod menu: pad input address (verified) and how different kinds of mods fit

**Date: 2026-10-10. Status: the pad address is verified live. The design sections are a plan, not built.**

## Pad input (verified)

Source in the decomp: `src/main/boot/Boot_InitSystemFlow.c:179` calls
`PadInitDirect(g_AnalogStickState, g_AnalogStickState + 0x22)`, the standard Sony libpad setup with two 34-byte raw
buffers. `g_AnalogStickState = 0x800BE9A0` (`linkers/USA/undefined_syms_manual.txt`, not in `sym.main.txt`).

| Item | Address | Notes |
|---|---|---|
| Port 1 raw buffer | `0x800BE9A0` | byte 0 status (`00` = ok), byte 1 pad id (`41` = digital), bytes 2-3 buttons, bytes 4-7 analog sticks (analog pads only) |
| **Port 1 buttons** | **`0x800BE9A2`** | `u16`, **active-low** (bit clear = pressed) |
| Port 2 raw buffer | `0x800BE9C2` | same layout, +0x22 |

Live check on the running game (debug server `mem_words`): idle first word `0xFFFF4100`; with an injected Start press
(`press buttons=0xFFF7`) it read `0xFFF74100`; after release it returned to `0xFFFF4100`. Start is bit 3 (`0xFFF7`),
confirmed. The other bits are the standard PS1 layout and were not individually tested: 0 Select, 1 L3, 2 R3, 3 Start,
4 Up, 5 Right, 6 Down, 7 Left, 8 L2, 9 R2, 10 L1, 11 R1, 12 Triangle, 13 Circle, 14 Cross, 15 Square.

The game's own processed copy, a block at `0x800A76D8..0x800A76EA` (copied into a battle record by
`Battle_CopyPadStateToRecord`, and passed to `Menu_RunFrameWithArg(D_800A76D8)` in `Entity_FrameUpdate.c`), read zero
at the title screen, so it is only populated in-game. Prefer the raw buffer for a menu hotkey; use the processed block
only if "pressed this frame" versus "held" semantics are needed, after verifying them in play.

## What an in-game toggle menu can and cannot do

Mod mechanisms in the engine (`runtime/include/mod_plugins.h`) and what each can switch live:

- **Declarative `[[patch]]`**: applied from the launcher's mod plan at start. Cannot be toggled live.
- **Per-frame (vblank) plugins** (god mode, the two floors): can be toggled live by a shared flag.
- **Live code patching from a plugin** (`psx_mod_write_code_word`, which routes through the executable-RAM path so a
  restored savestate cannot leave stale compiled code): lets a patch-style mod such as the 20x movement multiplier be
  switched on and off at runtime. The retail `expected` bytes should still be checked before writing.
- **Guest-entry hooks** (`psx_mod_register_function_entry_plugin`): fire when a listed guest function is entered. The
  addresses must be listed in `game.toml` and the game code regenerated.
- **Plugin state**: statically linked plugins can share ordinary C variables; guest memory for anything the game must
  see comes from `psx_mod_alloc_guest_memory`, which keeps it out of the fixed-layout save structures.

Open question: how an in-game change persists across launches. Manifest options are chosen by the launcher, and this
audit did not find a documented way for a plugin to write settings back. Needs checking before promising "remembers my
toggles".

## Three kinds of mod, in increasing difficulty

1. **Value tweaks** (speed, floors, god mode, drop rates): a flag plus a patch or per-frame write. Fit the menu directly.
2. **Data-table changes** (enemy stats, item data): overwrite game tables after they load, or replace data via disc
   asset overlays. The decomp supplies the struct layouts. Watch for fixed array sizes; the inventory array is exactly
   50 entries and sits against the equipment records (see `pe-mod-state-audit-2026-10-10.md`).
3. **Behavior changes such as an enemy randomizer**: hook whichever function chooses or spawns an encounter's enemies
   and substitute the ID from a seeded generator. The hook is the easy half. The hard half is validity: enemy models,
   animations and AI scripts are loaded per area, so swapping in an enemy whose assets are not resident can crash or
   draw garbage. That needs a table of which enemies are interchangeable, stat scaling, and care around bosses and
   story flags. Derive the pick from the seed plus the encounter identity (not a running counter) so a reload gives the
   same result, and mark such options "applies from the next battle" in the menu.

The decomp function that selects battle enemies has not been located yet.
