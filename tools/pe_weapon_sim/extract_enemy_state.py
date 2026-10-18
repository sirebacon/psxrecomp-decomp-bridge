"""Read enemy timer/action metadata from a saved PST; never starts the game."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from .extract_animations import ram_from_pst


def extract(path):
    ram=ram_from_pst(path)
    def off(addr,n=4):
        if not 0x80000000<=addr<=0x80200000-n: raise ValueError('invalid RAM pointer')
        return addr-0x80000000
    def u32(addr): return struct.unpack_from('<I',ram,off(addr))[0]
    def u16(addr): return struct.unpack_from('<H',ram,off(addr,2))[0]
    player=u32(0x8009D254);core=u32(player)
    result=dict(snapshot=str(Path(path).resolve()),sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        aya_hp_level=u16(0x800C0E28),aya_rank=struct.unpack_from('<b',ram,off(core+4,1))[0],enemies=[])
    entity=u32(0x8009D20C);seen=set()
    while entity and entity not in seen:
        seen.add(entity)
        if len(seen)>100: raise ValueError('actor list exceeds sane bound')
        core=u32(entity)
        if core and entity!=player:
            pos=off(core,0xD0)
            enemy=dict(entity=hex(entity),core=hex(core),model_index=ram[off(entity+12,1)],
                rank=struct.unpack_from('<b',ram,pos+4)[0],kind=ram[pos+5],
                charge=u16(core+12),charge_step=u16(core+142),hp=u32(core+16),
                defense=u16(core+140),periodic_damage=struct.unpack_from('<h',ram,pos+150)[0],
                flags=hex(u32(core)),action_slot=(u32(core)>>21)&7,
                effect_chance=ram[pos+144],effect_pointer=hex(u32(core+24)))
            ptr=u32(core+24)
            if ptr:
                p=off(ptr,16)
                enemy['effect']=dict(state=ram[p],effect_type=ram[p+1],enter_mode=ram[p+2],
                    exit_mode=ram[p+3],enter_step=struct.unpack_from('<i',ram,p+4)[0],
                    exit_step=struct.unpack_from('<i',ram,p+8)[0],power=u16(ptr+12),
                    category=ram[p+14],hit_frame=ram[p+15])
            result['enemies'].append(enemy)
        entity=u32(entity+4)
    return result


def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('snapshot');ap.add_argument('--out',required=True)
    a=ap.parse_args();r=extract(a.snapshot)
    Path(a.out).write_text(json.dumps(r,indent=2),encoding='utf-8')
    print(f"Extracted {len(r['enemies'])} enemy cores offline.")


if __name__=='__main__':main()
