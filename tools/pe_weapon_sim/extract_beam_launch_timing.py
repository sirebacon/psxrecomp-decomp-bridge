"""Extract phase/timing proof and focused fixtures. Never runs balance suites."""
import hashlib,json,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,sectors,word
from .decode_enemy_actions import flow
from .beam_launch_timing import formation_launch,replay_helper_lifetime


def main():
    inv=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())
    room=next(r for r in inv['rooms'] if r['map']==156 and r['disc']==1)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
    if hashlib.sha256(blob).hexdigest()!=room['sha256']:raise ValueError('room hash changed')
    creator=next(s for s in room['scripts'] if s['actor_type']==7)
    creates=[dict(relative_offset=n['offset']-creator['start'],**n) for n in flow(blob,creator['start'],creator['end'],inv['handlers'])['nodes']
        if 5052<=n['offset']-creator['start']<=5172]
    if [n['args'][1 if n['handler']=='Script_DispatchScriptCmd' else 0]['value'] for n in creates]!=[4,5,6,3]:raise ValueError('unexpected owner creation sequence')
    raw=(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup').read_bytes();base=word(raw,24)
    regions={'frame_update':(0x80035558,0x80035c84),'primary_pm':(0x80069594,0x80069660),
        'secondary_pm':(0x80069660,0x800696f0),'animation_wait':(0x80013300,0x800133e8),
        'ratan2':(0x80079fb4,0x8007a128),'atan_table':(0x8009a6ec,0x8009a6ec+2050)}
    code={name:dict(start=hex(start),end=hex(end),sha256=hashlib.sha256(raw[start-base+2048:end-base+2048]).hexdigest()) for name,(start,end) in regions.items()}
    calls=[]
    for a in range(*regions['frame_update'],4):
        w=word(raw,a-base+2048)
        if w>>26==3:calls.append(dict(address=hex(a),target=hex(0x80000000|((w&0x3ffffff)<<2))))
    parent=next(s for s in room['scripts'] if s['actor_type']==3)
    polygon=parent['start']+2*10372
    vertices=struct.unpack_from('<18i',blob,polygon)
    pairs=[list(vertices[i:i+2]) for i in range(0,18,2)]
    geom=json.loads((BRIDGE/'findings/data/pe-projectile-geometry-2026-10-18.json').read_text())
    if pairs!=geom['floor_polygons'][0]['vertices_fixed']:raise ValueError('navigation polygon differs from beam floor')
    common=dict(entry_update=1,targets_fixed=[(1000*65536,-6000*65536)]*3,
        current_yaw=0,boss_position=(0,-6000*65536),scale=65536,helpers_idle=True,pm_free_slots=3)
    fixture=formation_launch(**common)
    source=PROJECT/'parasite-eve-decomp'
    files=['src/main/entity/frame_update.c','src/main/script/flow_opcodes.c','src/main/script/node_actions.c',
        'src/main/script/system_opcodes.c','src/main/battle/context.c','src/main/field/actor_collision.c',
        'src/main/pm/process.c','src/main/psyq/libgte/ratan.c']
    report=dict(scope='Offline conditional formation launch timing; no gameplay, balance sweep or complete boss AI',
        rerun_readiness=False,room_sha256=room['sha256'],original_regions=code,frame_direct_calls=calls,
        creation_commands=creates,creation_order=[4,5,6,3],actor_scan_order=[3,6,5,4],
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in files},
        navigation=dict(returns_immediately=True,polygon_offset=polygon,vertices_fixed=pairs),
        normal_phase_order=['actor_scripts','battle_delivery','secondary_PM','movement','render_joints','primary_PM_draw_then_execute','animation_advance'],
        fixture_inputs=common,fixture=fixture,helper_replays={str(slot):replay_helper_lifetime(slot) for slot in (0,1,2)},
        limits=['entry/chooser/earned stats and actor state supplied','uninterrupted normal flag path',
                'no moving target tracking','busy helpers/PM exhaustion rejected','coincident turn flag20 edge rejected',
                'world pose at render must still be supplied for launch-joint trajectories'])
    target=BRIDGE/'findings/data/pe-beam-launch-timing-2026-10-18.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(target)

if __name__=='__main__':main()
