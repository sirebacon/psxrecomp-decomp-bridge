"""Parasite Eve's assets from the player's own disc image alone (a .cue, or its MODE2/2352 .bin).

The same lookup the native port does when it mounts a disc (parasite-eve-pc
src/main/asset/game_state.c): SYSTEM.CNF names the executable; the executable's data holds the
room sector table (0x80093378, 8 bytes a room: start, then scratch / texture / room sector
counts) and PE.IMG's image sector table (0x800930D8, 81 halfwords); PE.IMG is found through the
ISO 9660 directory. No RAM snapshot and no fixed paths, so a recipe pack can be built on any
machine (pe_pack_build.py).

    disc = Disc('Parasite Eve (USA) (Disc 1).cue')
    blob = disc.room_blob(25)            # as render_models.room_blob(25)
"""
import os, re, struct

RAW = 2352          # MODE2/2352: 24 bytes of header and subheader, then 2048 of data (Form 1)
DATA_AT = 24
ROOMS = 0x80093378
IMAGES = 0x800930D8
ROOM_COUNT = 450    # g_RoomSectorTable entries (SCENE_ROOM_COUNT)


class DiscError(Exception):
    pass


def _bin_of(path):
    """A .cue's single BINARY file, or the path itself for a .bin."""
    if not path.lower().endswith('.cue'):
        return path
    text = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'FILE\s+"([^"]+)"\s+BINARY', text) or re.search(r'FILE\s+(\S+)\s+BINARY', text)
    if not m:
        raise DiscError('%s names no BINARY file' % path)
    if 'MODE2/2352' not in text:
        raise DiscError('%s is not a MODE2/2352 image' % path)
    return os.path.join(os.path.dirname(os.path.abspath(path)), m.group(1))


class Disc:
    def __init__(self, path):
        self.path = _bin_of(path)
        if not os.path.isfile(self.path):
            raise DiscError('no disc image at %s' % self.path)
        self.f = open(self.path, 'rb')
        if os.path.getsize(self.path) % RAW:
            raise DiscError('%s is not a 2352-byte-sector image' % self.path)
        pvd = self.sector(16)
        if pvd[1:6] != b'CD001':
            raise DiscError('%s has no ISO 9660 volume' % self.path)
        self.root = pvd[156:156 + 34]
        boot = self._boot_name()
        exe_lba, exe_size = self.find(boot)
        self.exe = self.read(exe_lba, exe_size)
        if self.exe[:8] != b'PS-X EXE':
            raise DiscError('%s is not a PlayStation executable' % boot)
        img = self.find('PE.IMG')
        if not img:
            raise DiscError('no PE.IMG: not a Parasite Eve disc')
        self.img_lba = img[0]
        base, size = struct.unpack_from('<II', self.exe, 24)
        def data(addr, n):
            at = 0x800 + addr - base
            if addr < base or at + n > len(self.exe) or addr - base + n > size:
                raise DiscError('executable has no table at %08X: not a supported Parasite Eve disc' % addr)
            return self.exe[at:at + n]
        self.rooms = [struct.unpack_from('<II', data(ROOMS, ROOM_COUNT * 8), 8 * i) for i in range(ROOM_COUNT)]
        self.images = list(struct.unpack('<81H', data(IMAGES, 162)))

    # ---- sectors and the file system ----
    def sector(self, lba):
        self.f.seek(lba * RAW)
        raw = self.f.read(RAW)
        if len(raw) != RAW:
            raise DiscError('sector %d is past the end of the image' % lba)
        return raw[DATA_AT:DATA_AT + 2048]

    def sectors(self, lba, count):
        return b''.join(self.sector(lba + i) for i in range(count))

    def read(self, lba, size):
        return self.sectors(lba, (size + 2047) // 2048)[:size]

    def _entries(self, record):
        lba, size = struct.unpack_from('<I', record, 2)[0], struct.unpack_from('<I', record, 10)[0]
        data, at = self.read(lba, size), 0
        while at < len(data):
            n = data[at]
            if n == 0:                                   # records don't cross a sector boundary
                at = (at // 2048 + 1) * 2048
                continue
            rec = data[at:at + n]
            name = rec[33:33 + rec[32]].decode('ascii', 'replace').split(';')[0]
            yield name, rec
            at += n

    def find(self, path):
        """(lba, size) of a file by ISO path ("PE.IMG", "\\SLUS_006.62"), or None."""
        record = self.root
        for part in [p for p in re.split(r'[\\/]', path) if p]:
            for name, rec in self._entries(record):
                if name.upper() == part.split(';')[0].upper():
                    record = rec
                    break
            else:
                return None
        return struct.unpack_from('<I', record, 2)[0], struct.unpack_from('<I', record, 10)[0]

    def _boot_name(self):
        cnf = self.find('SYSTEM.CNF')
        if not cnf:
            raise DiscError('no SYSTEM.CNF: not a PlayStation disc')
        text = self.read(*cnf).decode('ascii', 'replace')
        m = re.search(r'BOOT\s*=\s*cdrom:\\?([^\s;]+)', text, re.I)
        if not m:
            raise DiscError('SYSTEM.CNF names no executable')
        return m.group(1)

    # ---- Parasite Eve's assets, as render_models reads them ----
    def _room(self, m):
        if not 1 <= m <= ROOM_COUNT:
            raise DiscError('no room %d' % m)
        start, packed = self.rooms[m - 1]
        return start, packed & 255, (packed >> 8) & 4095, packed >> 20

    def room_blob(self, m):
        start, scratch, texture, room = self._room(m)
        if not room:
            raise DiscError('room %d is empty' % m)
        return self.sectors(self.img_lba + start + scratch + texture, room)

    def room_texture_blobs(self, m):
        start, scratch, texture, room = self._room(m)
        out = []
        if scratch: out.append(self.sectors(self.img_lba + start, scratch))
        if texture: out.append(self.sectors(self.img_lba + start + scratch, texture))
        return out

    def image_blob(self, idx):
        s0, s1 = self.images[idx], self.images[idx + 1]
        return self.sectors(self.img_lba + s0, s1 - s0)
