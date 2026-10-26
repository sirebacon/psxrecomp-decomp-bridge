"""Room-animation packs for Aya's own outfits (offline, from the user's own disc).

Rooms install player animations for one of three Aya skeletons (build_skin.alt_sources): 29 parts
(jacket, T-shirt), 31 (evening dress), 23 (Day 1 long dress) -- the outfit the story puts Aya in
there. Worn elsewhere through the Wardrobe, an outfit gets room animations (door opening, room
events) made for another skeleton: the native animation sweep shows the evening dress fits only 63
of the 250 room animations, the jacket and T-shirt 178.

Each pack holds the room animations of the OTHER skeletons, retargeted to the outfit's own, in the
skins' rooms.bin format ('PERR', fingerprint table of Aya's originals; build_skin.write_room_rows),
so the game's skin loader swaps them in the same way. Output (git-ignored, game-derived):
tools/pe_assets/skins/outfit_<name>/rooms.bin; copy the folder to pe_skins/ beside the game's
preferences.

    PYTHONPATH=tools python tools/pe_assets/build_outfit_rooms.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
import retarget as T
import build_skin as B

# Wearable outfits: image entry bank + 8 (Scene_LoadEntityTexture). 11 and 14 have no full moveset.
OUTFITS = {10: 'outfit_evening', 12: 'outfit_jacket', 13: 'outfit_tshirt'}


def build(bank):
    aya_blob = R.image_blob(B.AYA_AREA + 8)
    aya = R.model(aya_blob, R.records(aya_blob, 0x0C)[0][0])
    aya_rows = {s: o for o, s, g in R.records(aya_blob, 0x10)}
    aya_idle = R.anim_frame_at(aya_blob, aya_rows[0x15], 0)[1]

    blob = R.image_blob(bank + 8)
    md = R.model(blob, R.records(blob, 0x0C)[0][0])
    rows = {s: o for o, s, g in R.records(blob, 0x10)}
    idle = R.anim_frame_at(blob, rows[0x15], 0)[1] if 0x15 in rows else [[0, 0, 0]] * md['parts']
    mp = T.semantic_mapping(aya, md)
    corr = T.shoulder_deltas(aya, md, mp, aya_idle, idle)
    B.alt_sources(md, idle)                 # sources for 31- and 23-part rows, onto this outfit
    ratio = T.leg_length(md, md['cmds']) / T.leg_length(aya, aya['cmds'])

    foreign = {fp: d for fp, d in B.room_player_rows().items() if d[1] + 1 != md['parts']}
    out_dir = os.path.join(B.HERE, 'skins', OUTFITS[bank])
    os.makedirs(out_dir, exist_ok=True)
    n, size = B.write_room_rows(os.path.join(out_dir, 'rooms.bin'), foreign, aya, md, mp, idle, corr, ratio, None)
    print(OUTFITS[bank], 'parts', md['parts'], ':', n, 'room animations of other skeletons,', size, 'bytes')


if __name__ == '__main__':
    for bank in OUTFITS:
        build(bank)
