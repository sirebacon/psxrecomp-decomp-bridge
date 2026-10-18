"""Bind the hospital burst-orb task program directly from raw room assets."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,word,sectors
from .source_projectile import task_spawns,orb_speed,BurstOrb,beam_window
import random

def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--out',required=True);cli=ap.parse_args()
    inventory_path=BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json'
    inventory=json.loads(inventory_path.read_text());rows=[]
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as disc:
        for room in inventory['rooms']:
            if room['disc']!=1 or room['map'] not in (156,291,380):continue
            blob=sectors(disc,room['lba'],room['sectors']);base=0x8018efe8
            directory=word(blob,4);desc=word(blob,directory+4)
            for i in range(desc>>22):
                at=(desc&0x3fffff)+i*12;slot=word(blob,at+4)>>24;ptr=word(blob,at+8)
                if slot not in (129,130):continue
                offset=ptr-base
                callbacks=[word(blob,offset+4*j) for j in range(8)]
                script=word(blob,offset+52);pc=script-base;triples=[]
                for _ in range(128):
                    triple=struct.unpack_from('<hhh',blob,pc);triples.append(triple);pc+=6
                    if triple[0]==0:break
                else:raise ValueError('unterminated task script')
                if callbacks[0] not in (0x80190230,0x80190f94):raise ValueError('unexpected overlay callback binding')
                rows.append(dict(map=room['map'],command=slot,program_address=hex(ptr),program_offset=offset,
                    callback_addresses=[hex(v) for v in callbacks],initializer=hex(word(blob,offset+48)),
                    script_address=hex(script),triples=triples,task_events=task_spawns(triples),room_sha256=room['sha256']))
    samples=[]
    for height in (320,640):
        for distance in (1000,1300,1500,2000,3000,3500,4000):
            for seed in range(8):
                orb=BurstOrb(y=-height,vx=orb_speed(distance));rng=random.Random(seed);hits=[];impact=None
                for update in range(1,257):
                    previous=orb.state
                    if orb.tick(rng,player_x=distance):hits.append(update)
                    if previous==0 and orb.state==1:impact=update
                    if not orb.alive:break
                samples.append(dict(height=height,distance=distance,seed=seed,speed=orb_speed(distance),
                    hits=hits,impact=impact,particle_end=update,launch_update=48,scope='aligned stationary point player, flat floor, always inside polygon; jitter range only'))
    source=PROJECT/'parasite-eve-decomp'
    names=('src/overlays/room_lib/spark_attacks.c','src/main/fieldfx/geometry.c','src/main/fieldfx/task_list.c','src/main/fieldfx/collision.c','src/main/script/actor_opcodes.c','src/main/script/system_opcodes.c','src/main/battle/context.c','configs/USA/overlays/room_m156_hospital.yaml','configs/USA/overlays/sym.room_m156_hospital.txt')
    actions=json.loads((BRIDGE/'findings/data/pe-enemy-actions-2026-10-18.json').read_text())
    gates=[];random_ranges=[];state_branches=[];beam_parameters=[]
    for row in actions['scripts']:
        nodes=row['nodes']
        for i,node in enumerate(nodes):
            args=node['args'];name=node['handler']
            origin=dict(map=row['map'],actor_type=row['actor_type'],offset=node['offset'])
            if row['map']==156 and row['actor_type'] in (4,5,6) and name=='Pm_ScriptSendCommand0' and len(args)==5 and all(v['mode']==0 for v in args[1:]) and args[1]['value']==1:
                duration=args[3]['value'];interval=args[4]['value']
                beam_parameters.append(dict(origin,slot_index=args[2]['value'],duration=duration,interval=interval,**beam_window(duration,interval)))
            if name=='Script_Random':random_ranges.append(dict(origin,args=args))
            if name=='Script_CondBranch':state_branches.append(dict(origin,args=args))
            if name=='Entity_GetDistanceComponents' and len(args)==3 and i+1<len(nodes):
                nxt=nodes[i+1];a=nxt['args']
                if nxt['handler']=='Script_EvalExpr' and len(a)==4 and a[0]['mode']==0 and a[0]['value'] in (9,10) and a[2]==args[2] and a[3]['mode']==0:
                    gates.append(dict(origin,target=args[:2],operator='>' if a[0]['value']==9 else '<',threshold_fixed=a[3]['value'],threshold_units=a[3]['value']/65536))
    result=dict(beam_parameters=beam_parameters,choice_inventory=dict(distance_gates=gates,random_ranges=random_ranges,state_branches=state_branches,scope='local syntactic comparisons; not probabilities or full reachability proof'),scope='Static bindings and conditional effect ticks; not complete projectile geometry or full AI',
        inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in names},programs=rows,samples=samples)
    Path(cli.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'Bound {len(rows)} task programs and ran {len(samples)} conditional flight samples.')
if __name__=='__main__':main()
