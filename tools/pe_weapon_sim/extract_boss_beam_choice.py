"""Offline chooser evidence and conditional decision-to-launch fixtures."""
import hashlib,json
from pathlib import Path
from .boss_beam_choice import room_inputs,boss_choice_to_launch,choose_action
from .extract_enemy_scripts import PROJECT,BRIDGE,sectors
from .decode_enemy_actions import flow


def main():
    inputs=room_inputs()
    inv=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    room=next(r for r in inv['rooms'] if r['disc']==1 and r['map']==156)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
    script=next(s for s in room['scripts'] if s['actor_type']==3)
    nodes=flow(blob,script['start'],script['end'],inv['handlers'])['nodes']
    selected=[dict(relative_offset=n['offset']-script['start'],**n) for n in nodes
        if 1876<=n['offset']-script['start']<=1992 or 2080<=n['offset']-script['start']<=2528 or
        3156<=n['offset']-script['start']<=6064 or 16308<=n['offset']-script['start']<=16660]
    opts=dict(start_update=1,boss_position=(0,-1873*65536,-6000*65536),
        player_position=(3000*65536,-1873*65536,-6000*65536),current_yaw=0,
        script_bits=0,committed_action=0,completed_beam=0,initial_charge=8990,charge_step=70,
        ready_latch=0,path_index=1,player_flags=0,triggers=[0,0,0],scale=65536,pm_free_slots=3,
        helpers_ready=True,enemy_core_flags=0,actor_flags=0)
    cases=[]
    for name,changes in [('far_after_charge',{}),('far_aya_locked',dict(player_flags=0x80)),
        ('far_helper_busy',dict(triggers=[1,0,0])),
        ('far_path_movement_boundary',dict(player_position=(2500*65536,-1873*65536,-6000*65536),ready_latch=1)),
        ('far_region2_after_movement',dict(player_position=(2500*65536,-1873*65536,-6000*65536),ready_latch=1,script_bits=4,formation_choice=1)),
        ('middle_roll0',dict(player_position=(1800*65536,-1873*65536,-6000*65536),ready_latch=1,script_bits=4,random_choice=0)),
        ('middle_roll1',dict(player_position=(1800*65536,-1873*65536,-6000*65536),ready_latch=1,script_bits=4,random_choice=1,formation_choice=2))]:
        arguments={**opts,**changes};cases.append(dict(name=name,inputs=arguments,result=boss_choice_to_launch(**arguments)))
    table=[]
    for distance in (1299,1300,1700,1701,2000,2001):
        for choice in (0,1,2):
            table.append(dict(distance=distance,random_input=choice,
                **choose_action(distance=distance*65536,triggers=[0,0,0],player_flags=0,random_choice=choice)))
    source=PROJECT/'parasite-eve-decomp'
    names=['src/main/script/actor_opcodes.c','src/main/script/system_opcodes.c','src/main/script/node_actions.c',
        'src/main/script/node_pool.c','src/main/script/flow_opcodes.c','src/main/battle/context.c',
        'src/main/battle/turn.c','src/main/entity/frame_update.c']
    out=dict(scope='Decoded initialized chooser and one static-world launch join, not full boss AI or balance results',
        rerun_readiness=False,room_sha256=inputs['room_sha256'],script_root=inputs['root'],
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
        selected_nodes=selected,region_polygon=inputs['region_polygon'],path_polygons=inputs['path_polygons'],
        initial_child_scan_offsets=[2080,17792,3388,20816,3252,3156],
        distance_rule='signed32 sum of absolute fixed16 XYZ differences; Manhattan, not Euclidean',
        gates=dict(melee='distance<1300',orb_only='1300<=distance<=1700',
            middle='1700<distance<=2000: explicit rand outcome0 orb;1/2 beams only if triggers all0 and Aya stiffness pair!=2',
            far='distance>2000: beams only if triggers all0 and Aya stiffness pair!=2',
            outer='interrupt/movement/completion/ready-latch gates must admit entry first'),
        stationary_boundary_table=table,cases=cases,
        limits=['initialized chooser resume input, not startup/cutscene timeline','fixed pose and state except source charge/latch',
                'movement boundary reported, not simulated','outer event bits may bypass readiness',
                'choice outcomes explicit, no probability claim','poison/incapacity/dead actors rejected',
                'one volley overlay; do not also count generic attacks for the same boss'])
    target=BRIDGE/'findings/data/pe-boss-beam-choice-2026-10-18.json'
    target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(target)

if __name__=='__main__':main()
