"""World direction of each arm / leg segment for Aya vs targets at one frame (retarget debugging)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render_models as R
import retarget as T


def joint_mats(md, tr, ang):
    I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; cur = (I, [0, 0, 0]); st = []; mats = {}
    for c in md['cmds']:
        if c == -1: st.append(cur); continue
        if c == -2: cur = st.pop(); continue
        Rm = R.mm(cur[0], R.rot_yxz(ang[c]) if c < len(ang) else I)
        t = [a + b for a, b in zip(R.mv(cur[0], tr if c == 0 else [0, 0, md['ptab'][c][3]]), cur[1])]
        mats[c] = (Rm, t); cur = (Rm, t)
    return mats


row = int(sys.argv[1]) if len(sys.argv) > 1 else 13
frame = int(sys.argv[2]) if len(sys.argv) > 2 else 0
aya_blob = R.image_blob(T.AYA_AREA + 8); aya = R.model(aya_blob, R.records(aya_blob, 0x0C)[0][0])
rows = {s: (aya_blob, o) for o, s, g in R.records(aya_blob, 0x10)}
day = R.image_blob(32); rows.update({s: (day, o) for o, s, g in R.records(day, 0x10)})
tr, ang = R.anim_frame_at(*rows[row], frame)
models = [('Aya', aya, ang)]
for name, m, slot in T.TARGETS:
    blob = R.room_blob(m)
    d = R.word(blob, 4); desc = R.word(blob, d + 0x0C); at = desc & 0x3fffff
    for i in range(desc >> 22):
        w = R.word(blob, at + 12 * i + 4)
        if w >> 24 == slot: off = w & 0xffffff
    md = R.model(blob, off)
    models.append((name, md, T.retarget_frame(ang, T.mapping(aya['cmds'], md['cmds']), [[0, 0, 0]] * md['parts'], md['parts'])))
for name, md, a in models:
    mats = joint_mats(md, tr, a); c = T.chains(md['cmds'])
    out = []
    for k in ('armA', 'armB'):
        segs = []
        for p in c[k][:5]:
            z = [mats[p][0][i][2] for i in range(3)]   # the bone's local +Z in world
            segs.append('%+.2f,%+.2f,%+.2f' % tuple(z))
        out.append(k + ' ' + ' | '.join(segs))
    print('%-7s' % name, '   '.join(out))
    print('        raw angles armB:', [a[p] for p in c['armB'][:5]])
