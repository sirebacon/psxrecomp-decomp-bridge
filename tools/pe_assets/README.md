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
