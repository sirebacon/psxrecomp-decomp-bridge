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
model-plus-animation bundles. Rendered (textured from entries 13-17):

| Area type | Outfit |
|---:|---|
| 10 | black evening dress (Day 1 play) |
| 11 | long dress, 23 parts, a reduced animation set (Day 1 scenes) |
| 12 | black jacket and jeans (main outfit) |
| 13 | white T-shirt and jeans (Disc 2) |
| 14 | Aya's transformed (green) final-battle form |

### Player animations

- Outfit bundles 10 / 12 / 13 / 14 hold rows 0-3, 13-23 and 28 for their own skeleton (31 / 29 / 29 / 31 bones).
- More player rows (4-12) load per area and day: `Scene_LoadEntityTextures` (`room_load.c:964`, step 4)
  reads image entry `(requested_entity_bank - 10) / 2 * 8 + day + 0x16`: entries 23-30 are for the
  31-bone skeleton, 31-38 for the 29-bone one. Per-day textures: entry `day + 0x26` (39-44).
- Area 11 (23 parts) has only rows 21-23 and 28-34, so it is **not** a full moveset.

### Animation and skeleton format (decomp)

- Skeleton = the model's matrix-command bytes (`Render_*` in `render/object.c:72-118`): -1 push,
  -2 pop, otherwise a part index; each part's matrix = parent x its animated rotation, translated by
  the animation's root translation (part 0) or by `(0, 0, parts[i].translation_z)` (bone length).
- Animation row = `RenderAnimationDataHeader` (`render_object.h:476`): 3 root-translation channels,
  then 3 angle channels (YXZ, `RotMatrixYXZ`) per bone up to `last_bone_index`; channels are constant
  (marker != 0) or per-frame byte (x16) / halfword samples (`anim/bone_rotations.c`).
- Animations carry rotations only; bone lengths come from the model. A mesh with the same hierarchy
  plays another skeleton's rotations directly.

## Other characters

- Room files hold every other character's model (room directory `bankRoots` at +0x0C, records slot
  = actor type) with only that room's animations (`bankRows` at +0x10): walk, talk, cutscene moves,
  not Aya's run / aim / battle set.
- Room model shapes (parts, animation entries), most common first: (3, 2) x205 props, (23, 9) x45,
  (25, 7) x42, (23, 11) x37, (27, 11) x34, ... Humanoid characters mostly have **23 parts**; Aya's
  usual bundles have 29-31.

## Who is who (rendered, `tools/pe_assets`)

**Catalog of every model with its disc location:** `findings/pe-model-catalog-2026-10-19.md`
(data: `findings/data/pe-model-catalog-2026-10-19.json`; renders local in `tools/pe_assets/renders/`).

**Texture source (found):** `Scene_LoadRoom` (`room_load.c:420-489`) reads each room as three runs
of sectors: a *scratch* blob (`packed & 255` sectors from the room start) and a *texture* blob
(`(packed >> 8) & 4095` sectors) whose TIM records it uploads to VRAM, then the room data
(`packed >> 20`). The character and enemy textures are in those first two blobs, so everything renders
textured straight from the disc (`render_models.room_vram`). Earlier extractions read only the third run.

| Character | Skeleton | Where |
|---|---|---|
| Daniel (also a gun-drawn variant) | 25 parts | NYPD, theater, finale (maps 25, 94, 275, ...) |
| Maeda (also with a backpack) | 27 parts | cruiser, finale (maps 25, 90, 276, ...) |
| Eve | 49 parts (Day 1), 47, 45 (Statue) | maps 23, 69, 88, 273 |
| Melissa (opera singer) | 28 parts | theater (map 4) |
| Ben | 23 parts, **Aya's** | theater, NYPD (maps 6, 25, 43-58, 115, 121, 373) |
| Maya (hospital gown) | 23, Aya's | theater, Central Park, Chrysler (11, 31, 68-79, 127, 318) |
| Aya's date (Carnegie Hall) | 23, Aya's | maps 2-10 |
| Chief Baker? (heavy-set, dark suit; also with a gun) | 23, Aya's | NYPD (41, 44, 47) |
| Policewoman (brown hair, vest) | 23, Aya's | maps 48, 52, 276 |
| Police officer (moustache) | 23, Aya's | maps 52, 108 |
| Dr. Klamp? (bearded, long coat) | 23, Aya's | museum (196, 199, 239, 344, 367) |
| Sailors / crew | 23 (Aya's or the second 23-part layout) | carrier, cruiser (271, 275, 276, 426) |
| Ushers, capped police, opera cast, NYPD staff, police dog | various | see the catalog |

### One body plan

Every humanoid is hips -> chest (arm chain, head chain, arm chain) + hips -> pelvis (two 4-part
legs). Only the chain lengths differ (extra segments are hands / fingers / hair at chain ends):

| Skeleton | Arm / head / arm | Legs |
|---|---|---|
| Aya dress (area 11), 94 room models | 5 / 2 / 5 | 4 / 4 |
| Daniel | 5 / 2 / 7 | 4 / 4 |
| Maeda | 6 / 4 / 6 | 4 / 4 |
| Aya main (areas 12, 13) | 8 / 2 / 8 | 4 / 4 |
| Second 23-part layout | 4 / 2 / 6 | 4 / 4 |

## What a swap needs

1. **Swap between Aya's own outfits (small).** Override the `bank` used by
   `Scene_LoadEntityTexture` (both the texture and the model entry) with a chosen outfit, leaving
   `g_SceneAreaType` itself alone (it also drives disc-swap flags). A costume selector.
2. **Another character as the player (large, but workable).** A bundle of the character's mesh plus
   Aya's full moveset **retargeted** to its skeleton:
   - No compatible character can use Aya's animations as they are: the only skeleton that 94 room
     models share is the dress's, whose set is incomplete.
   - Retarget offline, chain by chain, from the 29-bone set (bundle 12 + entries 31-38): map each
     chain's leading segments, hold extra segments at rest, and scale the root height by the leg-length
     ratio so feet stay on the ground. Bone lengths come from the character's own model.
   - Textures: repack the character's texture into the player's slot (one 4-bit page at x=960,
     y=256; palettes rows 448-449) and rewrite the faces' page / palette. The source texture is in
     the character's room scratch / texture blobs (found).
   - Runtime: in `Scene_LoadEntityTexture` step 6 and `Scene_LoadEntityTextures` step 6, swap in the
     custom bundle / rows instead of the disc's.
   - Check in game: hit boxes and the anchor (`anchor_y`, `anchor_matrix_index`), the gun / hand
     attachment parts, and battle animations that may assume Aya's proportions.
3. **Store and menu:** Junk purchase at any time, the unlocked set and the chosen model saved with
   the mod's settings (shared with the Bestiary's open storage question).
