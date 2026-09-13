# Parasite Eve QoL/mod roadmap: what's doable now vs. later

For the user's own PE mod project (not an upstream/Alex-facing document like
the others in this folder). Sorts a wishlist of QoL ideas — plus the two
content-mod goals (Armor mods, Weapon mods) — into what the current decomp
and recomp state actually supports today versus what needs more work first,
grounded in what's actually decompiled right now, not guesses.

## How "doable now" was actually checked

Two real constraints from this project's own findings, not assumptions:

1. **The decomp project only targets `assets/USA/main.exe`** (`decomp.yaml`
   has exactly one target, no overlay/room binaries). Anything living in
   per-room overlay content — the way WO-8's FMV decompress function does —
   is out of this decomp project's reach entirely, regardless of how much
   time passes. Anything living in `main.exe` is fair game.
2. **The recomp side already ships a real mod-loader** (`.psxmod` packages,
   `mods/preloaded/` + `mods/builtin/`) — proven working on Tomba
   (`tomba.enhancement.widescreen`, `.skip-fmv`, `.hybrid-controller`, etc.,
   each a real C plugin + manifest). PE's own `psxrecomp` checkout already
   ships several **framework-level** builtin mods
   (`psx.enhancement.cd-speed`, `psx.enhancement.fast-loading`,
   `psx.enhancement.pgxp`, `psx.presentation.bezel`) but PE's own
   `mods/preloaded/packages/` is empty — no PE-specific mod has been built
   yet.

Every item below was checked against the actual decomp symbol table
(`configs/USA/sym.main.txt`) rather than assumed.

## Doable now (main.exe is decomp'd here, or the framework already has it)

### Increased storage / inventory limits
**Strong candidate — the exact control points are already named.**
`Inv_GetAyaSlotLimit` and `Inv_SetAyaSlotCount` (plus `Inv_GetBonusSlotCount`,
`Inv_GetPackedListCount`) are already decompiled. A slot-limit increase is
about as close to "change one constant/return value" as a PS1 game mod gets.
A single centralized storage box would need more — understanding how the
active/bonus list selection (`Inv_SelectActiveList`, `Inv_ResetActiveList`,
`Inv_IsActiveListOverrideSelected`) ties to save-slot-specific data — but the
building blocks are already named and readable.

### Streamlined inventory/equip menus
**Doable, moderate effort.** The whole menu flow is extensively decompiled:
`Menu_CreateEquipScreen`, `Menu_EquipGridHandler`, `Menu_EquipSelectInput`,
`Menu_InventoryNavigate`, `Menu_DrawItemSlot`, `Menu_CreateItemActionSubmenu`,
`Menu_HandleItemInput`, and more. Redesigning the flow (fewer button presses,
clearer stat comparisons) means understanding and patching real, already-
named UI state machines, not reverse-engineering from scratch.

### Quick-swap hotkey loadouts
**Doable, moderate effort.** Needs the same `Inv_*`/`Menu_ItemUseAction`
equip-application code (named) plus a runtime hotkey binding — the mod
framework already supports custom input handling (see Tomba's
`hybrid-controller` mod as a working precedent for binding new actions to
pad input outside the game's own menu flow).

### Save-anywhere / flexible saves
**Two real paths, both available today, for different reasons:**
- **Fastest path**: the runtime already has a generic savestate mechanism
  (used throughout this project's own testing this session — arbitrary
  save/load slots via the debug server, independent of PE's own memory-card
  system). Exposing that as a player-facing quicksave/quickload hotkey is a
  framework feature, not a decomp dependency. **Caveat, and an important
  one**: this is the exact mechanism behind the savestate/menu VRAM
  corruption bug this project is still mid-investigation on
  (`savestate-restore-lazy-revalidation-race.md`) — that should get fixed
  first, or a save-anywhere feature built on it will inherit the bug.
- **Deeper path**: PE's own save system is extensively decompiled —
  `Save_InitSystem`, `Save_BuildCardFile`, `Save_StartWriteSlot`,
  `Save_LoadCardFileIntoRuntime`, `Save_BuildHeader`/`RestoreHeader`, and
  more — enough to plausibly add a "save anywhere" that writes a real
  memory-card-format save rather than a runtime snapshot, if that's
  preferred over the snapshot approach.

### Fast-forward / speed boost
**Already exists at the framework level.** The runtime's own source
(`main.cpp`) already references an existing hold-to-turbo hotkey — a
"fast-forward bind" is already wired up as a runtime feature, independent of
PE's own code. If it isn't already reachable/visible to a player today, this
is a near-zero-effort surfacing task (expose/rebind), not new engineering.

### Reduced load times
**Already built, just needs enabling.** `psx.enhancement.cd-speed` and
`psx.enhancement.fast-loading` are already present as builtin mods in PE's
own `psxrecomp` checkout. Nobody's turned them on for PE yet.

### Scene/FMV skip
**Framework capability confirmed working on another title, not yet wired
for PE.** Tomba's `game.toml` shows the exact shape this needs:
`fmv_skip_total_table`, `fmv_skip_movie_id`, `fmv_skip_end_total`, plus a
real `tomba.enhancement.skip-fmv` mod built against it. PE's `game.toml` has
none of this configured yet. This needs finding PE's own equivalent
movie-ID table and frame-total variable — genuine reverse-engineering work,
similar in *kind* to the WO-8 investigation (live instrumentation, not
static decomp reading), but narrower in scope than a full decompile.

## Needs targeted investigation first (plausible, not yet confirmed)

### Visible combat boundaries
**Likely feasible, not yet pinned down.** Battle code is extensively
decompiled — `Battle_SetEntryCoords`, `Battle_GetContextField`/
`SetContextField`, `Battle_UpdateEntityFacing`, and dozens more — so the
system governing movement bounds during active-time battles is almost
certainly in scope. The *specific* function that clamps/rejects
out-of-bounds movement hasn't been identified by name yet — worth a targeted
search/trace rather than assumed blocked.

### Dialogue/message fast-forward beyond generic turbo
The existing turbo/fast-forward hotkey already speeds up dialogue scenes
along with everything else. A dedicated "skip to next unread line" feature
would need the specific text-advance function, which didn't turn up in a
symbol search (no `Msg_`/`Dialog_`-prefixed functions found) — either it's
named differently, or it's an area the decomp hasn't reached in depth yet.
Worth a direct check before assuming either way.

## Needs real reverse-engineering work (not blocked by decomp completeness, just not started)

### Modern control scheme (replacing tank controls)
**The harder one.** Low-level pad handling is decompiled (`Pad_StopHandler`,
`Pad_DequeueHandler`, `PAD_init2`), but the actual movement/turn-processing
logic that would need reinterpreting for a relative/modern control scheme
hasn't turned up under an obvious name yet. This is also not purely a
decomp-coverage problem — converting tank controls to modern relative
movement changes game feel in ways that need real design iteration, not
just a code patch. Tomba's `hybrid-controller` mod is a useful existing
precedent for how the framework supports this kind of input remapping, but
PE's specific movement code needs its own investigation first.

## Blocked or much further out

### Anything that turns out to live in overlay-resident, per-room code
The one hard boundary in this whole list: **the decomp project cannot reach
overlay content at all**, by design (`decomp.yaml` targets `main.exe` only).
If any QoL idea above turns out to depend on code that's dynamically loaded
per-room rather than statically resident in `main.exe` — the same category
WO-8's decompress function fell into — decomp progress will never get us
there. That would need the same live-instrumentation approach used for WO-8
(dispatch timing, disassembly, register tracing), not a decomp lookup.
Nothing on this list is *known* to fall into that category yet, but it's
worth checking before committing real effort to any single item.

## Armor mods / weapon mods (new content, not pure QoL)

Different category from everything above — these add new items rather than
change existing behavior, which is a harder bar. **A real foothold exists**:
`Inv_LookupItemData`/`Inv_LookupData` are already decompiled, meaning the
item-data lookup path is understood well enough to be a real starting point.
What's not yet confirmed is whether the *full* item-data table schema
(stats, damage formulas, equip-slot rules, icon/name references) is mapped
in enough depth to safely add new entries rather than only read/tweak
existing ones. Treat this as a mid-term goal: plausible given current
decomp coverage of the lookup path, but needs a dedicated schema-mapping
pass before attempting new item creation — closer in spirit to the
FMV-skip item above (needs targeted work) than to the inventory-limit item
(already has its exact control point named).

### Increased out-of-combat run speed
**Doable, one caveat worth verifying first.** `Task_SetEntityMoveSpeed`
(`0x80018F74`) plus `Entity_ComputeVelocity`/`Entity_ComputeVelocityToTarget`
are already decompiled — a direct, named control point for how fast an
entity moves, which is exactly what this needs. The one thing not yet
confirmed: whether field-exploration movement and battle movement share
this same call path with different arguments, or go through genuinely
separate code (the `Battle_*` module is large and separate, which suggests
they might). That matters because the ask is specifically *out-of-combat*
only — worth a quick trace to confirm the speed change can be scoped to
field movement without touching battle movement, before assuming it's a
trivial constant edit.

## Chosen priorities (per user, 2026-09-13)

Five targets picked from the list above: **Increased Storage, Streamlined
Menus, Quick-Swap Loadouts, FMV Skip, and Increased Out-of-Combat Run
Speed.** All five check out as either already-doable or bounded, targeted
effort — none of them touch overlay-only content, and none need new decomp
progress this project doesn't already have. Suggested order:

1. **Increased storage/inventory limits** — smallest, most-already-named
   surface area on this whole list (`Inv_GetAyaSlotLimit`/`SetAyaSlotCount`).
2. **Increased out-of-combat run speed** — similarly small once the
   field-vs-battle call-path question above is confirmed
   (`Task_SetEntityMoveSpeed`).
3. **Streamlined menus** — larger surface area (multiple `Menu_*`
   functions) but no unknowns, just more code to work through.
4. **Quick-swap loadouts** — builds on the same `Inv_*`/menu code as #3,
   plus a new hotkey binding (real precedent exists: Tomba's
   `hybrid-controller` mod).
5. **FMV skip** — the only one needing genuine reverse-engineering
   (finding PE's own movie-ID table/frame-total variables), but with a
   working reference implementation (Tomba's `skip-fmv` mod) to build from
   rather than starting blind.
