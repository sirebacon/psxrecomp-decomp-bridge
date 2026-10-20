import struct, zlib, glob, sys
from pathlib import Path


def sections(path):
    data = Path(path).read_bytes(); h = struct.unpack_from('<9I', data); pos = 36; out = {}
    for _ in range(h[7]):
        tag, flags, size = struct.unpack_from('<IIQ', data, pos); pos += 16
        p = data[pos:pos + size]; pos += size
        if flags & 1: p = zlib.decompress(p[4:])
        out[tag] = p
    return out


def vram_of(path):
    s = sections(path)
    v = s[8]
    if len(v) >= 1024 * 512 * 2: return list(struct.unpack_from('<%dH' % (1024 * 512), v, 0))
    raise ValueError('no vram (tag 8 is %d bytes)' % len(v))


def map_of(ram):
    token = struct.unpack_from('<I', ram, 0x9D280)[0]
    name = ''.join(chr(ram[0x930B4 + ((token >> ((5 - i) * 5 + 2)) & 31)]) for i in range(6)).upper()
    return int(name[2:5]) if name[2:5].isdigit() else None, name


if __name__ == '__main__':
    for p in sorted(glob.glob(r'D:/Recomp Games/**/*.pst', recursive=True)):
        try:
            s = sections(p); print(map_of(s[2]), p.replace('D:/Recomp Games/', ''))
        except Exception as e: print('ERR', p, e)
