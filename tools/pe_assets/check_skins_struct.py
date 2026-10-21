"""Structural check of every installed skin: Aya layout (>= 29 parts), matrix commands reach every part once,
and every animation (bundle rows, day1-8, rooms.bin) has one channel set per part; meta.bin gun part."""
import os, sys, struct
sys.path.insert(0, r"D:\Recomp Games\psxrecomp-decomp-bridge\tools")
sys.path.insert(0, r"D:\Recomp Games\psxrecomp-decomp-bridge\tools\pe_assets")
import render_models as R
from gen_collection_data import SKINS

ROOT = r"D:\Recomp Games\Parasite Eve Project\parasite-eve-recomp\build-release\pe_skins"
bad_total = 0
for n, p, k, a, folder, src in SKINS:
    if k != 1 or folder == 'eve': continue
    d = os.path.join(ROOT, folder); probs = []
    try:
        b = open(os.path.join(d, 'model.bin'), 'rb').read()
        md = R.model(b, R.records(b, 0x0C)[0][0]); np_ = md['parts']
        if np_ < 29: probs.append('only %d parts (not Aya layout)' % np_)
        seen = [c for c in md['cmds'] if c >= 0]
        if sorted(seen) != list(range(np_)): probs.append('commands reach %d of %d parts' % (len(set(seen)), np_))
        rows = 0
        for o, s, g in R.records(b, 0x10):
            rows += 1
            if b[o + 1] + 1 != np_: probs.append('bundle row %d has %d parts' % (s, b[o + 1] + 1))
        for day in range(1, 9):
            db = open(os.path.join(d, 'day%d.bin' % day), 'rb').read()
            for o, s, g in R.records(db, 0x10):
                rows += 1
                if db[o + 1] + 1 != np_: probs.append('day%d row %d has %d parts' % (day, s, db[o + 1] + 1))
        rb = open(os.path.join(d, 'rooms.bin'), 'rb').read()
        cnt = struct.unpack_from('<I', rb, 4)[0]
        for i in range(cnt):
            fp, off, size = struct.unpack_from('<III', rb, 8 + 12 * i)
            rows += 1
            if rb[off + 1] + 1 != np_: probs.append('room row %08X has %d parts' % (fp, rb[off + 1] + 1))
        mb = open(os.path.join(d, 'meta.bin'), 'rb').read()
        gun = struct.unpack_from('<I', mb, 4)[0]
        if gun != 0x12: probs.append('gun part %d (expected 18)' % gun)
    except Exception as e:
        probs.append('ERROR %s' % e)
    bad_total += bool(probs)
    print('%-16s %s' % (folder, 'OK  parts %d, %d animations checked' % (np_, rows) if not probs else '; '.join(probs[:4])))
print('skins with problems:', bad_total)
