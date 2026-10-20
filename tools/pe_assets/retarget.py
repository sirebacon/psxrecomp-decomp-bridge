"""Retarget prototype: play Aya's player animations on another character's skeleton (offline).

Every humanoid shares one body plan (hips -> chest -> arm / head / arm chains, hips -> pelvis -> two
legs) with different chain lengths. Aya's rotations are mapped chain by chain, index for index; a
target segment past the end of Aya's chain keeps the character's own idle angle; the root translation
is scaled by the leg-length ratio. Renders a grid: rows = Aya animation frames, columns = Aya and the
targets, to tools/pe_assets/renders/retarget_*.png (local only).

    PYTHONPATH=tools python tools/pe_assets/retarget.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
from PIL import Image, ImageDraw

AYA_AREA = 12   # jacket + jeans, 29 bones; per-day rows for this skeleton: image entries 31-38
TARGETS = [('Daniel', 25, 3), ('Maeda', 25, 4), ('Baker?', 41, 3), ('Maya', 11, 2)]


def tree(cmds):
    par, st, cur = {}, [], None
    for c in cmds:
        if c == -1: st.append(cur)
        elif c == -2: cur = st.pop()
        else: par[c] = cur; cur = c
    kids = {}
    for k in sorted(par):
        kids.setdefault(par[k], []).append(k)
    return kids


def chains(cmds):
    """{chain name: [part, ...]} for root, chest chains (armA, head, armB) and the two legs."""
    kids = tree(cmds)
    def run(n):
        out = [n]
        while len(kids.get(n, [])) == 1: n = kids[n][0]; out.append(n)
        return out
    root = kids[None][0]
    chest, pelvis = kids[root][0], kids[root][1]
    a, h, b = kids[chest][:3]
    l1, l2 = kids[pelvis][:2]
    return dict(root=[root], chest=[chest], pelvis=[pelvis], armA=run(a), head=run(h), armB=run(b), legA=run(l1), legB=run(l2))


def mapping(src_cmds, dst_cmds):
    s, d = chains(src_cmds), chains(dst_cmds)
    m = {}
    for k, parts in d.items():
        for i, p in enumerate(parts):
            if i < len(s[k]): m[p] = s[k][i]
    return m


def leg_length(md, cmds):
    c = chains(cmds)
    return sum(abs(md['ptab'][p][3]) for p in c['legA']) or 1


def main():
    aya_blob = R.image_blob(AYA_AREA + 8); aya_tex = R.image_blob(AYA_AREA + 3)
    aya = R.model(aya_blob, R.records(aya_blob, 0x0C)[0][0])
    aya_vram = [0] * (1024 * 512); R.upload_tims(aya_tex, aya_vram)
    rows = {s: (aya_blob, o) for o, s, g in R.records(aya_blob, 0x10)}
    day = R.image_blob(31 + 1)          # the 29-bone per-day rows (day 2), rows 4-12
    rows.update({s: (day, o) for o, s, g in R.records(day, 0x10)})
    targets = []
    for name, m, slot in TARGETS:
        blob = R.room_blob(m); vram = R.room_vram(m)
        d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
        for i in range(desc >> 22):
            w = R.word(blob, at + 12 * i + 4)
            if w >> 24 == slot: off, trailing = w & 0xffffff, R.word(blob, at + 12 * i + 8)
        md = R.model(blob, off)
        if (trailing >> 8) & 0xF: R.relocate(md, (trailing >> 6) & 0x3C0, (trailing >> 9) & 0x180, ((trailing >> 18) & 0xFF) + 0x1C0)
        own = sorted([(s, o) for o, s, g in R.records(blob, 0x10) if g == slot])
        idle = R.anim_frame(blob, own[0][1], md['parts'])[1] if own else [[0, 0, 0]] * md['parts']
        targets.append((name, md, vram, mapping(aya['cmds'], md['cmds']), idle, leg_length(md, md['cmds']) / leg_length(aya, aya['cmds'])))
        print(name, 'parts', md['parts'], 'mapped', len(targets[-1][3]), 'leg ratio %.2f' % targets[-1][5])
    R.NOTEX = False
    picks = [(s, f) for s in sorted(rows) for f in (0, None)]
    cell = 180; out = []
    for s, f in picks:
        blob, o = rows[s]; frames = blob[o + 2]
        f = frames // 2 if f is None else f
        if f == 0 and frames <= 1 and s != sorted(rows)[0]: continue
        tr, ang = R.anim_frame_at(blob, o, f)
        row = [R.render(aya, R.pose(aya, tr, ang), aya_vram, 'side', cell)]
        for name, md, vram, mp, idle, ratio in targets:
            tang = [ang[mp[p]] if p in mp and mp[p] < len(ang) else (idle[p] if p < len(idle) else [0, 0, 0]) for p in range(md['parts'])]
            row.append(R.render(md, R.pose(md, [int(tr[0] * ratio), int(tr[1] * ratio), int(tr[2] * ratio)], tang), vram, 'side', cell))
        out.append(('row %d frame %d/%d' % (s, f, frames), row))
    for k in range(0, len(out), 8):
        chunk = out[k:k + 8]
        sheet = Image.new('RGB', (cell * (len(TARGETS) + 1), (cell + 16) * len(chunk)), (10, 10, 12))
        dr = ImageDraw.Draw(sheet)
        for j, (label, imgs) in enumerate(chunk):
            for i, im in enumerate(imgs):
                if im: sheet.paste(im, (cell * i, (cell + 16) * j + 16))
            dr.text((4, (cell + 16) * j + 2), label + '   |   Aya, ' + ', '.join(t[0] for t in TARGETS), fill=(255, 255, 0))
        p = os.path.join(R.OUT, 'retarget_%d.png' % (k // 8)); sheet.save(p); print(p)


if __name__ == '__main__':
    main()
