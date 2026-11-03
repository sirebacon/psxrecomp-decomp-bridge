# pe_assets — model / texture research tools (offline)

Research scripts for the player model swap (`findings/pe-model-swap-research-2026-10-19.md`).
They read the disc images and PST save states read-only; outputs (renders, JSON) go next to the
scripts and are git-ignored because they are derived from the game's assets.

Run with `PYTHONPATH=tools` from the bridge root.

| Script | What it does |
|---|---|
| `render_models.py MAP SLOT` | Software-render one room model (frame 0 of its first animation), front / side / back. `NOTEX=1` for shaded geometry. Also the shared decoder: model layout, animation frame decode, skeleton posing, texture relocation (`Render_InitPrimBlock`), TIM upload, PSX texel lookup. |
| `render_saves.py` | For every save state on disk, render every character model of the save's room with the save's own VRAM (room characters' textures are not in the room files). |
| `render_batch.py` | Aya's five outfit bundles (textured from image entries 13-17) and the meshes sharing her 23-part skeleton. |
| `probe_skeletons.py` | Skeleton hierarchy (matrix-command stream) of every room model vs Aya's five bundles. |
| `pst_vram.py` | PST sections (tag 2 RAM, tag 8 VRAM 1024x512x16) and the map a save was made in (`0x8009D280` base-32 token). |
| `anim_bones.py` | Bones / frames per animation row in the player image entries 18-38. |
| `map_images.py` | What each PE image-table entry holds (models, animation rows, TIM rectangles). |

## Recipe packs: building characters from your own disc

Characters from the Parasite Eve disc are never shared as files. A **recipe pack** shares only the
instructions (bridge findings D8 §5), and each player builds it from their own disc:

```
pack.json        {"format": 1, "id": "pe1-cast", "name": "...", "version": "1.0.0", "kind": "recipe"}
LICENSE
characters/<folder>/character.json   {"name": "Daniel", "group": "Cast", "tier": "main"}
characters/<folder>/recipe.json      {"room": 25, "slot": 3, "disc": 1}
```

`room` and `slot` are where the character's model sits on the disc, as `build_skin.py` takes them.

Build it (Python 3.8+ and Pillow):

    python tools/pe_assets/pe_pack_build.py RECIPE.zip --disc1 "Parasite Eve (USA) (Disc 1).cue" --disc2 "... (Disc 2).cue" --out <preferences>/packs

It writes `<id>-<version>.zip`, a normal `assets` pack, into the game's packs folder. The game lists
it under F1 > Collection > Wardrobe > Packs after a restart. Built from your disc: keep it to
yourself and share the recipe. Room animations (`rooms.bin`) come from the discs you give; both
discs cover every room.

`pe_disc.py` reads everything from the disc image alone (ISO 9660, SYSTEM.CNF's executable, its
room and image sector tables, PE.IMG), as the native port does at mount, so `render_models.py`
works without the research RAM snapshot once `use_discs()` is called.
`test_pe_pack_build.py` checks recipes anywhere; set `PE_DISC1` to your disc to also build one.
