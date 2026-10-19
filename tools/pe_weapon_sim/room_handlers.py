"""Room effect handlers: effect id -> program struct -> decompiled functions (offline).

Source: scene/room_load.c installs room directory field 0x04 records: slot 8..84 into
g_PmCmdHandlerTable[slot], 85+ into g_FieldFxTaskPrograms[slot - 85]; u.handler is an
absolute address inside the room overlay. The overlay symbol maps
(configs/USA/overlays/sym.room_m*.txt, splat) name the functions.
"""
import json, re, struct
from functools import lru_cache
from pathlib import Path

from .enemy_reach import room_blob
from .extract_enemy_scripts import PROJECT

CONFIGS = PROJECT / 'parasite-eve-decomp/configs/USA'


def _u32(b, at): return struct.unpack_from('<I', b, at)[0]


@lru_cache(maxsize=None)
def overlay(map_id):
    """(vram base, blob offset of the overlay code, {addr: name}) for a room, or None."""
    files = list((CONFIGS / 'overlays').glob('room_m%03d_*.yaml' % int(map_id)))
    if not files: return None
    text = files[0].read_text()
    vram = int(re.search(r'vram:\s*(0x[0-9A-Fa-f]+)', text).group(1), 16)
    name = re.search(r'basename:\s*(\S+)', text).group(1)
    sym = CONFIGS / 'overlays' / ('sym.%s.txt' % name)
    names = {}
    for path in (sym, CONFIGS / 'sym.main.txt'):
        if path.exists():
            for n, a in re.findall(r'(\w+)\s*=\s*(0x[0-9A-Fa-f]+);', path.read_text()):
                names.setdefault(int(a, 16), n)
    return dict(vram=vram, basename=name, names=names)


def records(map_id):
    """[(command, handler address)] from room directory field 0x04."""
    blob = room_blob(map_id)
    directory = _u32(blob, 4); desc = _u32(blob, directory + 4)
    at = desc & 0x3FFFFF
    return [(blob[at + 12 * i + 7], _u32(blob, at + 12 * i + 8)) for i in range(desc >> 22)]


def handler(map_id, command, words=8):
    """dict(address, symbol, fields=[(value, symbol)]) for an effect command, read from the
    overlay image (room_m*.bin under original/USA/overlays when present)."""
    ov = overlay(map_id)
    rec = dict(records(map_id)).get(command)
    if rec is None: return None
    out = dict(address=rec, symbol=ov['names'].get(rec) if ov else None)
    if ov:
        # The room blob is the overlay image: offset 0 = vram (verified: room 146's command-40
        # struct holds its RoomLib class functions at base 0).
        b = room_blob(map_id); off = rec - ov['vram']
        if 0 <= off <= len(b) - 4 * words:
            out['fields'] = [(v, ov['names'].get(v)) for v in struct.unpack_from('<%dI' % words, b, off)]
    return out
