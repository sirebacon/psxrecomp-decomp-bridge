# Player model swap — research notes, October 19, 2026

Goal (user): let the player swap Aya's model for other characters' models (not Ben, too short),
bought with Junk, available at any time. This note records where the player model comes from and
what a swap needs. **Nothing is built yet.** Probe: scratchpad `probe_models.py` (offline: disc
images plus the PST snapshot for RAM tables; no game connection).

## Where Aya's model comes from

- `Scene_LoadEntityTexture` (decomp `src/main/scene/room_load.c:701`) loads the player bundle for
  `bank = g_SceneAreaType` (`0x800B0CE2`, values 10-14):
  - textures: PE image entry `bank + 3` (entries 13-17, 17 sectors each, 3 TIMs);
  - model + animations: PE image entry `bank + 8` (entries 18-22).
  - Entry sectors: `g_PeImageSectorTable` (`0x800930D8`, u16 per entry, relative to
    `g_DiscLoadState.baseLba`); entry N spans table[N] .. table[N+1].
- From the bundle: `bank_slots[0]` = the model header (bank root record), `bank_rows[0][id]` = the
  animation rows (`room_load.c:785-812`).
- `Scene_InitEntityPlayer` step 39 (`room_load.c:883-908`) puts `bank_slots[0]` on the player
  (`model_state.model_header`), takes animation row 0x15 as the starting action and builds the
  render object (`Render_SetupEntityPrims`).
- On resume, step 32 forces `g_SceneAreaType = 0xE` and restores it from
  `scene_area_type_backup` afterwards (`room_load.c:832-840`).

## Aya's five bundles (identical on both discs)

| Area type | Image entry (model) | Parts | Animation entries | Animation rows | Vertices | Seen in the saves |
|---:|---:|---:|---:|---:|---:|---|
| 10 | 18 | 31 | 15 | 16 | 442 | — |
| 11 | 19 | 23 | 11 | 10 | 468 | early Disc 1 |
| 12 | 20 | 29 | 15 | 16 | 474 | most of the game |
| 13 | 21 | 29 | 15 | 16 | 463 | Disc 2 |
| 14 | 22 | 31 | 15 | 25 | 435 | resume (forced 0xE) |

Model header (`RenderObjectHeader`, `include/pe1/render_object.h:363`): byte 2 part count, byte 3
animation-entry count, +6 vertex count, +8.. packet counts.

**Each bundle carries its own model *and* its own animation set**, so the game already swaps whole
model-plus-animation bundles. Which outfit each area type is (Day 1 dress, main outfit, ...) is
still to be confirmed visually.

## Other characters

- Room files hold every other character's model (room directory `bankRoots` at +0x0C, records slot
  = actor type) with only that room's animations (`bankRows` at +0x10): walk, talk, cutscene moves,
  not Aya's run / aim / battle set.
- Room model shapes (parts, animation entries), most common first: (3, 2) x205 props, (23, 9) x45,
  (25, 7) x42, (23, 11) x37, (27, 11) x34, ... Humanoid characters mostly have **23 parts**; Aya's
  usual bundles have 29-31.

## What a swap needs

1. **Swap between Aya's own outfits (small).** Override the `bank` used by
   `Scene_LoadEntityTexture` (both the texture and the model entry) with a chosen outfit, leaving
   `g_SceneAreaType` itself alone (it also drives disc-swap flags). A costume selector.
2. **Another character as the player (large).** Needs a bundle of that character's mesh plus a full
   player animation set:
   - Aya's animations have per-part tracks for her own skeleton; they only drive a mesh with the
     same part layout. Most characters have 23 parts, like Aya's area-11 bundle, so that bundle's
     animations are the candidate, **if** the part hierarchies match (to check: parent order and
     joint offsets) and if its 10 rows cover everything the player does (the other bundles have 16-25).
   - Character textures come from their rooms' TIMs and must be uploaded where the player's
     textures go (texture page and palette positions).
   - Identifying which room model is which character needs rendering them (an OBJ export).
3. **Store and menu:** Junk purchase at any time, the unlocked set and the chosen model saved with
   the mod's settings (shared with the Bestiary's open storage question).
