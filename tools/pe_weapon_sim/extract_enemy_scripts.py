"""Offline room/script inventory. Static records are not an executed AI trace."""
import argparse, hashlib, json, re, struct
from pathlib import Path
from .extract_animations import ram_from_pst

PROJECT=Path('D:/Recomp Games/Parasite Eve Project')
BRIDGE=Path(__file__).resolve().parents[2]

def word(blob,at):
    if at<0 or at+4>len(blob): raise ValueError('word outside asset')
    return struct.unpack_from('<I',blob,at)[0]

def instruction(blob,at,handlers):
    header=word(blob,at); tail=word(blob,at+4)
    opcode=header&8191; count=(header>>13)&15
    if opcode>=len(handlers) or not handlers[opcode]: raise ValueError('unknown opcode')
    modes=header>>17; args=[]
    for i in range(count):
        mode=modes&7
        if mode>4: raise ValueError('unsupported argument mode')
        args.append(dict(mode=mode,value=word(blob,at+8+4*i)))
        modes >>=3
        if i==4:modes=tail
    return dict(offset=at,opcode=opcode,handler=handlers[opcode],args=args),at+8+4*count

def sectors(f,start,count):
    out=[]
    for lba in range(start,start+count):
        f.seek(lba*2352);s=f.read(2352)
        if len(s)!=2352 or s[:12]!=b'\0'+b'\xff'*10+b'\0':raise ValueError('invalid raw sector')
        if s[15] not in (1,2):raise ValueError('unsupported sector mode')
        skip=24 if s[15]==2 else 16
        out.append(s[skip:skip+2048])
    return b''.join(out)

def room(blob,handlers):
    directory=word(blob,4)
    def records(field):
        desc=word(blob,directory+field);at=desc&0x3fffff;count=desc>>22
        if at+count*12>len(blob):raise ValueError('record table outside room')
        return [(word(blob,at+12*i+4)&0xffffff,word(blob,at+12*i+4)>>24,blob[at+12*i+11]) for i in range(count)]
    banks=[]
    for ptr,mode,group in records(16):
        if ptr+12>len(blob):raise ValueError('animation outside room')
        banks.append(dict(actor_type=group,mode=mode,offset=ptr,frame_count=blob[ptr+2],header_hex=blob[ptr:ptr+12].hex()))
    blocks=records(20)
    if not blocks:return dict(animations=banks,scripts=[])
    base=blocks[0][0];count=word(blob,base+4)
    if count>256:raise ValueError('implausible relocation count')
    roots=[base+word(blob,base+8+4*i) for i in range(count)]
    boundaries=sorted(set(roots+[p for field in (24,28,32,36,40,44,48) for p,_,_ in records(field)]+[len(blob)]))
    scripts=[]
    wanted={'Entity_SetField','Entity_SetFieldByTypeId','Script_SetEntityAnim12Args','Script_SetEntityAnim5Args','Script_SetBattleEntryCoords','Entity_SelectFieldSetter'}
    for actor,start in enumerate(roots):
        end=next((v for v in boundaries if v>start),len(blob));at=start;facts=[];decoded=0;error=None
        try:
            while at<end:
                ins,nxt=instruction(blob,at,handlers)
                if nxt>end:raise ValueError('instruction crosses script boundary')
                if ins['handler'] in wanted:facts.append(ins)
                decoded+=1;at=nxt
        except ValueError as exc:error=str(exc)
        scripts.append(dict(actor_type=actor,start=start,end=end,decoded_instructions=decoded,stop_offset=at,stop_reason=error,facts=facts))
    return dict(animations=banks,scripts=scripts)

def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--out',required=True);a=ap.parse_args()
    snapshot=BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst'
    ram=ram_from_pst(snapshot)
    symbols=(PROJECT/'parasite-eve-decomp/configs/USA/sym.main.txt').read_text()
    names={int(addr,16):name for name,addr in re.findall(r'(\w+)\s*=\s*(0x[0-9A-Fa-f]+);',symbols)}
    handlers=[names.get(word(ram,0x910a0+i*4)) for i in range((0x91464-0x910a0)//4)]
    campaign=json.loads((BRIDGE/'findings/data/pe-campaign-2026-10-17.json').read_text())
    maps=sorted({int(e['map']) for e in campaign['events'] if e['type']=='battle'})
    results=[]
    for disc in (1,2):
        path=PROJECT/f'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc {disc}).bin'
        with path.open('rb') as f:
            for map_id in maps:
                try:
                    start=word(ram,0x93378+(map_id-1)*8);packed=word(ram,0x9337c+(map_id-1)*8)
                    lba=word(ram,0xb0dd8)+start+(packed&255)+((packed>>8)&4095);count=packed>>20
                    blob=sectors(f,lba,count)
                    results.append(dict(disc=disc,map=map_id,lba=lba,sectors=count,sha256=hashlib.sha256(blob).hexdigest(),**room(blob,handlers)))
                except (ValueError,IndexError,struct.error) as exc:results.append(dict(disc=disc,map=map_id,error=str(exc)))
    out=dict(scope='Linear static inventory, not control-flow reachability or runtime action selection. IDs in campaign log are core rank/kind, not actor type.',snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),handlers=handlers,rooms=results)
    source=PROJECT/'parasite-eve-decomp'
    source_files=('src/main/scene/room_load.c','src/main/script/flow_opcodes.c','src/main/script/system_opcodes.c','src/main/script/node_pool.c','src/main/battle/context.c','configs/USA/sym.main.txt')
    out['source_sha256']={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in source_files}
    half=len(results)//2
    out['disc_room_equality']=all(a.get('sha256') is not None and a.get('sha256')==b.get('sha256') for a,b in zip(results[:half],results[half:]))
    Path(a.out).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(dict(rooms=len(results),errors=sum('error'in r for r in results),facts=sum(len(s['facts']) for r in results for s in r.get('scripts',[])),animations=sum(len(r.get('animations',[])) for r in results))))
if __name__=='__main__':main()
