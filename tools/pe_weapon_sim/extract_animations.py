"""Read animation headers from an existing PST snapshot, without loading the game."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def ram_from_pst(path):
    data = Path(path).read_bytes()
    if len(data) < 36: raise ValueError('truncated PST')
    header = struct.unpack_from('<9I', data)
    if header[0] != 0x50535842 or header[1] not in (3, 4, 5, 6):
        raise ValueError('unsupported PST header')
    pos = 36
    for _ in range(header[7]):
        tag, flags, size = struct.unpack_from('<IIQ', data, pos); pos += 16
        payload = data[pos:pos+size]; pos += size
        if len(payload) != size: raise ValueError('truncated section')
        if tag == 2:
            if flags & ~1: raise ValueError('unknown RAM encoding')
            if flags & 1:
                expected = struct.unpack_from('<I',payload)[0]
                payload = zlib.decompress(payload[4:])
                if len(payload) != expected: raise ValueError('bad decompressed length')
            if len(payload) != 0x200000: raise ValueError('bad RAM size')
            return payload
    raise ValueError('missing RAM section')


def extract(ram):
    def offset(addr, size):
        if not 0x80000000 <= addr <= 0x80200000-size: raise ValueError(hex(addr))
        return addr - 0x80000000
    def u32(addr): return struct.unpack_from('<I',ram,offset(addr,4))[0]
    entity = u32(0x8009D254)
    off = offset(entity,0x1B4)
    model = ram[off+12]
    table = 0x800B0E98 + model * 0xC0
    rows=[]
    for mode in range(48):
        ptr = u32(table+mode*4)
        if not 0x80000000 <= ptr <= 0x801FFFF4:
            rows.append(dict(mode=mode, pointer=hex(ptr), available=False)); continue
        raw=ram[offset(ptr,12):offset(ptr,12)+12]
        rows.append(dict(mode=mode,pointer=hex(ptr),available=True,header_hex=raw.hex(),
            encoding_flags=raw[0],last_bone_index=raw[1],frame_count=raw[2],
            last_frame=raw[2]-1))
    return dict(entity=hex(entity),model_index=model,current_mode=ram[off+14],
        anim_step=struct.unpack_from('<i',ram,off+28)[0],
        entity_flags=hex(u32(entity+0x98)),action_table=hex(table),actions=rows,
        battle_animation_rows=[list(ram[0x106A4+i*5:0x106A4+(i+1)*5]) for i in range(9)])


def disc_bank(ram, disc, index):
    """Scene_LoadEntityTextures case4/6: banks at costume*8 + kind + 0x16."""
    base=struct.unpack_from('<I',ram,0xB0DD8)[0]
    start,end=struct.unpack_from('<HH',ram,0x930D8+index*2)
    with Path(disc).open('rb') as f:
        chunks=[]
        for lba in range(base+start,base+end):
            f.seek(lba*2352); sector=f.read(2352)
            if len(sector)!=2352 or sector[:12]!=b'\x00'+b'\xff'*10+b'\x00':
                raise ValueError('expected raw CD sectors')
            skip=24 if sector[15]==2 else 16
            chunks.append(sector[skip:skip+2048])
    blob=b''.join(chunks)
    directory=struct.unpack_from('<I',blob,4)[0]
    descriptor=struct.unpack_from('<I',blob,directory+16)[0]
    rows=[]
    for i in range(descriptor>>22):
        at=(descriptor&0x3fffff)+12*i
        packed=struct.unpack_from('<I',blob,at+4)[0]
        ptr=packed&0xffffff
        header=blob[ptr:ptr+12]
        if len(header)!=12 or not header[2]: raise ValueError('bad animation header')
        rows.append(dict(mode=packed>>24,frame_count=header[2],last_frame=header[2]-1,
            offset=ptr,header_hex=header.hex()))
    return dict(index=index,sector_start=start,sector_end=end,blob_sha256=hashlib.sha256(blob).hexdigest(),actions=rows)


def main():
    ap=argparse.ArgumentParser(__doc__); ap.add_argument('snapshot'); ap.add_argument('--out',required=True)
    ap.add_argument('--disc')
    a=ap.parse_args(); p=Path(a.snapshot); ram=ram_from_pst(p); result=extract(ram)
    if a.disc:
        result['disc']=str(Path(a.disc).resolve())
        result['weapon_banks']=[dict(costume=costume,kind=kind,**disc_bank(ram,a.disc,costume*8+kind+0x16))
            for costume in range(2) for kind in range(1,9)]
    result.update(snapshot=str(p.resolve()),snapshot_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    Path(a.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=1))


if __name__=='__main__': main()
