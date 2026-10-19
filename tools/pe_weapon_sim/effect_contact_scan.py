"""Exploration tool (heuristic, not used by the simulator): does code reachable from a room effect
record set the owner contact bits?

python -m pe_weapon_sim.effect_contact_scan    (prints the Disc2 boss effects)

Validation: all 49 effects the simulator models with source contact (room_modules.actions /
task_actions) are flagged. Reachability follows jal, lui/addiu pointers and pointer tables
whose entries start with a prologue, so unrelated code can be reached (false positives) and
data-flow is not checked; never use a negative result alone to declare an effect harmless.

Contact signature (decomp: room_lib/sound_burst.c, e19.c, timed_spawn.c): test owner flags
& 0x3F000000 (lui 0x3F00), and rewrite them to 0x21/0x19/0x11 << 24 (lui 0x2100 / 0x1900 /
0x1100) and/or set the player's 0x4000 flag (ori 0x4000)."""
import struct, sys
from .room_handlers import room_blob, records, overlay
VRAM = 0x8018EFE8


def u32(b, a): return struct.unpack_from('<I', b, a - VRAM)[0]


def func_words(b, start, limit=3000):
    """Words from start to the next function prologue (addiu sp,sp,-N) after the first jr ra."""
    out = []; seen_ret = False
    for i in range(limit):
        a = start + 4 * i
        if a - VRAM + 4 > len(b): break
        w = u32(b, a)
        if i > 0 and seen_ret and (w >> 16) == 0x27BD and (w & 0x8000):
            break
        out.append((a, w))
        if w == 0x03E00008: seen_ret = True
    return out


def callees(ws):
    for a, w in ws:
        if w >> 26 == 3:
            t = ((w & 0x3FFFFFF) << 2) | 0x80000000
            if 0x8018EFE8 <= t < 0x80200000: yield t
        # function pointers loaded as lui/addiu pairs
    his = {}
    for a, w in ws:
        op = w >> 26; rt = (w >> 16) & 31; rs = (w >> 21) & 31; imm = w & 0xFFFF
        if op == 15: his[rt] = imm << 16
        elif op == 9 and rs in his:
            v = (his[rs] + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF
            if 0x8018EFE8 <= v < 0x80200000: yield v


def scan(map_id, start, depth=5):
    b = room_blob(map_id); seen = set(); hits = {}
    frontier = [start]
    for d in range(depth):
        nxt = []
        for f in frontier:
            if f in seen: continue
            seen.add(f)
            try: ws = func_words(b, f)
            except struct.error: continue
            luis = {w & 0xFFFF for a, w in ws if w >> 26 == 15}
            oris = {w & 0xFFFF for a, w in ws if w >> 26 == 13}
            reg = any(w == ((3 << 26) | (0x800C6C18 >> 2 & 0x3FFFFFF)) for a, w in ws)
            sig = dict(register=reg, test=0x3F00 in luis, rewrite=sorted(x for x in (0x2100, 0x1900, 0x1100) if x in luis), player4000=0x4000 in oris, owner01=0x0100 in luis)
            if sig['test'] or sig['rewrite'] or reg: hits[hex(f)] = sig
            for t in callees(ws):
                try: first = u32(b, t)
                except struct.error: continue
                if (first >> 16) == 0x27BD and first & 0x8000 or any(t == ((w & 0x3FFFFFF) << 2 | 0x80000000) for _, w in ws if w >> 26 == 3):
                    nxt.append(t); continue
                for i in range(64):                     # a data table: follow entries that are functions
                    try: e = u32(b, t + 4 * i)
                    except struct.error: break
                    if 0x8018EFE8 <= e < 0x80200000 and not (e - VRAM) % 4:
                        try: fe = u32(b, e)
                        except struct.error: continue
                        if (fe >> 16) == 0x27BD and fe & 0x8000: nxt.append(e)
        frontier = nxt
    return hits, len(seen)


def starts_for(map_id, record, levels=3):
    """Code addresses reachable from an effect record through data pointers: words pointing into
    the overlay; a word is taken as a function start when it holds a prologue (addiu sp,sp,-N) or
    is directly a record field (callback tables)."""
    b = room_blob(map_id); out = set(); seen = set(); frontier = [(record, 0)]
    while frontier:
        at, lv = frontier.pop()
        if at in seen or lv > levels: continue
        seen.add(at)
        for i in range(32):
            try: w = u32(b, at + 4 * i)
            except struct.error: break
            if not (0x8018EFE8 <= w < 0x80200000) or (w - VRAM) % 4: continue
            try: first = u32(b, w)
            except struct.error: continue
            if (first >> 16) == 0x27BD and first & 0x8000: out.add(w)
            else: frontier.append((w, lv + 1))
    return out


def effect_contact(map_id, command):
    rec = dict(records(map_id))[command]; hits = {}
    for s in starts_for(map_id, rec):
        h, _ = scan(map_id, s); hits.update(h)
    return hits


if __name__ == '__main__':
    for m, cmds in ((269, (137, 138, 139, 77)), (245, (140, 141, 70)), (256, (131, 132, 76)), (428, (152, 153, 75, 78)),
                    (429, (145, 146, 147, 148, 75, 80)), (432, (150, 151, 162, 163, 165)), (156, (0,))):
        rec = dict(records(m))
        for c in cmds:
            if c not in rec: print(m, c, 'no record'); continue
            b = room_blob(m)
            words = [u32(b, rec[c] + 4 * i) for i in range(14)]
            starts = [w for w in words if 0x8018EFE8 <= w < 0x80200000 and (w - VRAM) % 4 == 0]
            allhits = {}; n = 0
            for s in starts:
                h, k = scan(m, s); allhits.update(h); n += k
            print(m, c, 'record', hex(rec[c]), 'fns', n, 'contact sites', allhits)
