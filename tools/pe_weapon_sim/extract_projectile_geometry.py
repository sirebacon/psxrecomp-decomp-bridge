"""Extract model geometry and launch animation channels offline; no rerun."""
import argparse,hashlib,json,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,word,sectors
from .extract_animations import ram_from_pst
from .decode_enemy_actions import flow

def model_geometry(blob,offset):
    if offset<0 or offset+28>len(blob):raise ValueError('model header outside asset')
    parts=blob[offset+2];vertices=struct.unpack_from('<H',blob,offset+6)[0]
    packets=struct.unpack_from('<4H',blob,offset+8)
    section=offset+28+parts*12+vertices*12+sum(packets)*12
    commands=section+16+parts*16+8
    count=struct.unpack_from('<H',blob,offset+24)[0]
    if commands+count>len(blob):raise ValueError('model body outside asset')
    return dict(offset=offset,part_count=parts,vertex_count=vertices,packet_counts=packets,
        cylinder_section_offset=section,cylinder_section=struct.unpack_from('<4h',blob,section),
        cylinder_radius=struct.unpack_from('<h',blob,section+6)[0],
        matrix_commands=list(struct.unpack_from('<'+str(count)+'b',blob,commands)),
        part_translation_z=[struct.unpack_from('<i',blob,offset+28+i*12+8)[0] for i in range(parts)],
        bounds=[struct.unpack_from('<8h',blob,section+16+i*16) for i in range(parts)])

def decode_channels(blob,offset):
    flags,last,frames=struct.unpack_from('<BBB',blob,offset)
    if frames==0:raise ValueError('empty animation')
    cursor=offset+12;channels=[]
    def channel(short,translation=False):
        nonlocal cursor
        marker=struct.unpack_from('<h',blob,cursor)[0] if short else blob[cursor]
        sample_at=cursor+(2 if short else 1)
        fmt='h' if translation else 'H' if short else 'B'
        values=[struct.unpack_from('<'+fmt,blob,sample_at+i*(2 if short else 1))[0] for i in range(1 if marker else frames)]
        if marker:values*=frames
        cursor+=4 if marker else ((frames>>1)+1)*4 if short else ((frames>>2)+1)*4
        return values
    translations=[channel(True,True) for _ in range(3)]
    short=(flags&3)==2
    for bone in range(last+1):
        angles=[channel(short) for _ in range(3)]
        if not short:angles=[[value*16 for value in row] for row in angles]
        channels.append(angles)
    return dict(offset=offset,encoding_flags=flags,frame_count=frames,bone_count=last+1,end_offset=cursor,
        root_translations=[list(v) for v in zip(*translations)],
        bone_angles_by_frame=[[[channels[b][axis][f] for axis in range(3)] for b in range(last+1)] for f in range(frames)])

def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--out',required=True);cli=ap.parse_args()
    inventory=BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json';x=json.loads(inventory.read_text())
    room=next(r for r in x['rooms'] if r['disc']==1 and r['map']==156)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
    directory=word(blob,4);desc=word(blob,directory+12);models=[]
    for i in range(desc>>22):
        packed=word(blob,(desc&0x3fffff)+i*12+4)
        models.append(dict(actor_type=packed>>24,**model_geometry(blob,packed&0xffffff)))
    polygons=[];floor_writes=[];spawns=[]
    for script in room['scripts']:
        for node in flow(blob,script['start'],script['end'],x['handlers'])['nodes']:
            args=node['args'];values=[a['value'] if a['mode']==0 else None for a in args]
            if node['handler']=='Script_SetInventorySlotPointer' and len(values)==2 and None not in values:
                offset=script['start']+2*values[0];count=values[1]
                if not 3<=count<=1024 or offset+count*8>len(blob):raise ValueError('invalid floor polygon')
                raw=[struct.unpack_from('<ii',blob,offset+8*i) for i in range(count)]
                polygons.append(dict(actor_type=script['actor_type'],setter_offset=node['offset'],offset=offset,vertices_fixed=raw,vertices_integer=[[p[0]>>16,p[1]>>16] for p in raw]))
            if node['handler']=='Entity_SetFieldByTypeId' and len(values)==4 and values[0]==0 and values[2]==255 and values[3] is not None:
                floor_writes.append(dict(actor_type=script['actor_type'],offset=node['offset'],floor_y=((values[3]+32768)&65535)-32768))
            if node['handler']=='Script_SpawnEntityAt':spawns.append(dict(actor_type=script['actor_type'],**node))
    animations=[]
    for row in room['animations']:
        if row['actor_type']==3 and row['mode'] in (8,9,10,11):animations.append(dict(mode=row['mode'],**decode_channels(blob,row['offset'])))
    snapshot=BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst'
    ram=ram_from_pst(snapshot);player=word(ram,0x9d254)-0x80000000
    model=word(ram,player+0x1b4)-0x80000000
    aya=model_geometry(ram,model)
    radius=struct.unpack_from('<h',ram,player+0x224)[0]
    aya_banks=[]
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as disc:
        base_lba=word(ram,0xb0dd8)
        for costume in (0,1):
            for kind in range(1,9):
                index=costume*8+kind+0x16
                first,last=struct.unpack_from('<HH',ram,0x930d8+index*2)
                bank=sectors(disc,base_lba+first,last-first)
                bank_directory=word(bank,4);descriptor=word(bank,bank_directory+12)
                for i in range(descriptor>>22):
                    packed=word(bank,(descriptor&0x3fffff)+i*12+4)
                    if packed>>24==0:
                        geom=model_geometry(bank,packed&0xffffff)
                        aya_banks.append(dict(costume=costume,kind=kind,index=index,cylinder_radius=geom['cylinder_radius'],bank_sha256=hashlib.sha256(bank).hexdigest()))
    if radius!=aya['cylinder_radius']:raise ValueError('Aya model/runtime radius mismatch')
    # Source bindings of the three beam owners, with raw command provenance.
    actions=json.loads((BRIDGE/'findings/data/pe-enemy-actions-2026-10-18.json').read_text());beams=[]
    for row in actions['scripts']:
        if row['map']!=156 or row['actor_type'] not in (4,5,6):continue
        selected=[n for n in row['nodes'] if n['handler'] in ('Pm_ScriptSendCommand0','Script_RunEntityCommand','Entity_GetField')]
        actor_type=row['actor_type'];slot=actor_type-4
        beams.append(dict(actor_type=actor_type,root=row['root'],trigger_cell=18+slot,target_cells=[21+2*slot,22+2*slot],parameter_slot=slot,position_source=dict(type_id=3,sub_id=31),action_slot=3,effect_type=5,power_expression='u16((shared_cell10 * 90) >> 16)',armor_parameter='second (selected record slot3)',status_effect='stiffness lock; source effect type5',commands=selected,scope='independent owner copies type3/sub31 position when triggered; no actual parent attachment required by this path'))
    source=PROJECT/'parasite-eve-decomp';names=('src/main/anim/bone_rotations.c','src/main/render/object.c','src/main/entity/combat.c','src/main/menu/main_update.c','src/main/field/actor_collision.c','src/main/fieldfx/geometry.c','src/main/script/actor_opcodes.c','src/main/script/system_opcodes.c','src/main/battle/enemy_actions.c','include/pe1/battle_ailment.h','src/overlays/room_lib/spark_attacks.c')
    out=dict(rerun_readiness=dict(ready=False,user_instruction='Hold balance reruns until geometry and linked-beam delivery are coherent.',remaining=['fixed-point skeletal/world pose reconstruction','actual actor orientation and target-cell strategies','effect pool drain / process ordering','incoming stiffness and delivered damage integration']),scope='Decoded raw channels/model geometry; world pose reconstruction and battle reruns deferred',
        inventory_sha256=hashlib.sha256(inventory.read_bytes()).hexdigest(),snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),room_sha256=room['sha256'],
        source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in names},models=models,animations=animations,
        aya_disc_models=aya_banks,aya_saved_model=dict(cylinder_radius=radius,model_address=hex(model+0x80000000),cylinder_section=aya['cylinder_section'],scope='existing Disc2 snapshot model, not universal costume proof'),
        floor_polygons=polygons,floor_height_setters=floor_writes,spawn_commands=spawns,orb_joint_index=7,orb_joint_offset=[0,-70,-100],beam_joint_index=31,beam_joint_offset=[0,0,-100],linked_beam_owners=beams)
    Path(cli.out).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('Decoded',len(models),'model records and',sum(a['frame_count'] for a in animations),'animation frames. Saved Aya radius:',radius)
if __name__=='__main__':main()
