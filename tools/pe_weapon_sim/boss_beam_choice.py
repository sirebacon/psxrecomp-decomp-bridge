"""Map156 actor3 chooser gates and one static-world beam decision -> launch join.

Explicit initialized script state is required. This is not a full movement,
reaction, death or repeated-choice interpreter. No balance runner enables it.
"""
import hashlib,json,struct
from functools import lru_cache
from .projectile_geometry import s32,point_in_polygon
from .beam_scheduling import formation_targets,projected_target
from .beam_launch_timing import formation_launch,target_yaw_from_position,turn_step
from .rotation_oracle import RotationOracle
from .source_enemy import EnemyClock


def source_distance(boss,player):
    if len(boss)!=3 or len(player)!=3:raise ValueError('XYZ fixed16 positions required')
    return s32(sum(abs(s32(a-b)) for a,b in zip(boss,player)))


def chooser_gate(*,script_bits,committed_action,completed_beam,ready_latch,path_result,distance):
    """Actor3+3412..4248; returns branch and exact local-state changes."""
    bits=script_bits;completed=completed_beam
    if bits&1:
        bits &= ~1;outcome='wait' if committed_action==1 else 'decide'
    elif bits&64:outcome='wait'
    elif bits&4 and (distance<1200*65536 or path_result==0):outcome='decide'
    elif completed==1:
        completed=0
        outcome='move' if not bits&4 and path_result==1 else 'decide'
    elif ready_latch==0:outcome='wait'
    else:outcome='move' if distance>2000*65536 and not bits&4 and path_result==1 else 'decide'
    return dict(outcome=outcome,script_bits=bits,completed_beam=completed)


def choose_action(*,distance,triggers,player_flags,random_choice=None):
    """Actor3+4752..5592 after turn setup. The interval boundaries are strict."""
    if len(triggers)!=3:raise ValueError('three trigger cells required')
    idle=all(v==0 for v in triggers);locked=(player_flags>>6)&3==2
    if distance<1300*65536:return dict(action='melee',random_consumed=False)
    if distance>2000*65536:return dict(action='beams' if idle and not locked else 'orb',random_consumed=False)
    if distance<=1700*65536:return dict(action='orb',random_consumed=False)
    if random_choice not in (0,1,2):raise ValueError('explicit choice in [0,3) required for 1700<distance<=2000')
    return dict(action='beams' if random_choice!=0 and idle and not locked else 'orb',random_consumed=True)


@lru_cache(maxsize=1)
def room_inputs():
    from .extract_enemy_scripts import PROJECT,BRIDGE,sectors
    inventory=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text(encoding='utf-8'))
    room=next(r for r in inventory['rooms'] if r['disc']==1 and r['map']==156)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:
        blob=sectors(f,room['lba'],room['sectors'])
    if hashlib.sha256(blob).hexdigest()!=room['sha256']:raise ValueError('room hash changed')
    script=next(s for s in room['scripts'] if s['actor_type']==3)
    from .decode_enemy_actions import flow
    nodes=flow(blob,script['start'],script['end'],inventory['handlers'])['nodes']
    region=next(n for n in nodes if n['offset']==script['start']+3316)
    rv=[a['value'] for a in region['args'][:8]]
    region_polygon=[[s32(rv[i])>>16,s32(rv[i+1])>>16] for i in range(0,8,2)]
    path_polygons=[]
    for off in (10244,10276,10308,10340):
        raw=struct.unpack_from('<8i',blob,script['start']+2*off)
        path_polygons.append([[raw[i]>>16,raw[i+1]>>16] for i in range(0,8,2)])
    table=RotationOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup').table
    return dict(region_polygon=region_polygon,path_polygons=path_polygons,table=table,
                room_sha256=room['sha256'],root=script['start'])


def first_choice_update(*,start_update,initial_charge,charge_step,ready_latch,script_bits,
                        committed_action,completed_beam,path_result,distance,max_updates=1000,enemy_flags=0,actor_flags=0):
    """Initialized ordinary main loop: chooser BEFORE late charge-poll child,
    BEFORE Battle_UpdateEnemy. Inputs other than charge/latch/bits stay fixed.
    """
    if start_update<1:raise ValueError('positive start update required')
    if enemy_flags&0x181e or actor_flags&0x1010:raise ValueError('incapacitated/poisoned/dead actor requires full scheduler replay')
    clock=EnemyClock(charge_step,charge=initial_charge,flags=enemy_flags,actor_flags=actor_flags);trace=[];bits=script_bits;completed=completed_beam
    for update in range(start_update,start_update+max_updates):
        gate=chooser_gate(script_bits=bits,committed_action=committed_action,completed_beam=completed,
            ready_latch=ready_latch,path_result=path_result,distance=distance)
        trace.append(dict(update=update,charge=clock.charge,ready_latch=ready_latch,gate=gate['outcome']))
        bits=gate['script_bits'];completed=gate['completed_beam']
        if gate['outcome']!='wait':return dict(update=update,gate=gate,trace=trace)
        # Initial child creation order places the charge poll after the chooser.
        if clock.charge>=9000:ready_latch=1
        clock.tick()
    raise ValueError('no choice reached with fixed supplied state')


def advance_turn(update,current,target,step):
    for calls in range(1,4098):
        current=turn_step(current,target,step)
        if current==target:return update,current,calls
        update+=1
    raise ValueError('turn did not converge')


def boss_choice_to_launch(*,start_update,boss_position,player_position,current_yaw,
                          script_bits,committed_action,completed_beam,initial_charge,
                          charge_step,ready_latch,path_index,player_flags,triggers,enemy_core_flags,actor_flags,
                          scale,pm_free_slots,helpers_ready,random_choice=None,formation_choice=None):
    """One decoded choice under fixed world/state, through normal formation launch.

    start_update is the main node's first chooser resume, NOT room/battle startup.
    Movement/reaction/death/PM interruptions are boundaries, not invented delays.
    """
    if path_index not in (1,2,3,4):raise ValueError('explicit local32 path index required')
    inputs=room_inputs();bx,bz=boss_position[0],boss_position[2];px,pz=player_position[0],player_position[2]
    distance=source_distance(boss_position,player_position)
    path_result=int(point_in_polygon(px,pz,inputs['path_polygons'][path_index-1]))
    polling=first_choice_update(start_update=start_update,initial_charge=initial_charge,charge_step=charge_step,
        ready_latch=ready_latch,script_bits=script_bits,committed_action=committed_action,
        completed_beam=completed_beam,path_result=path_result,distance=distance,
        enemy_flags=enemy_core_flags,actor_flags=actor_flags)
    base=dict(scope='One initialized static-world chooser -> formation path; no outer movement/reaction replay',
        ready_for_balance=False,room_sha256=inputs['room_sha256'],distance=distance,path_result=path_result,
        chooser_update=polling['update'],charge_trace=polling['trace'],linked_beams=[])
    if polling['gate']['outcome']=='move':return dict(base,action='move',reason='source movement setup boundary')
    # Main preparation clears bit7, then turns toward Aya at local10=128.
    yaw=target_yaw_from_position((bx,bz),(px,pz))
    decision_update,yaw,pre_turn_calls=advance_turn(polling['update'],current_yaw,yaw,128)
    action=choose_action(distance=distance,triggers=triggers,player_flags=player_flags,random_choice=random_choice)
    base.update(action=action['action'],decision_update=decision_update,pre_turn_calls=pre_turn_calls,
                action_random_consumed=action['random_consumed'])
    if action['action']!='beams':return base
    if helpers_ready is not True:raise ValueError('free trigger cells do not prove initialized helpers')
    # +5592 explicitly yields one update. +5648 faces Aya at speed128; with fixed
    # world inputs the preceding turn has already aligned it, so no extra yield.
    mode=2 if point_in_polygon(px,pz,inputs['region_polygon']) else 0
    update=decision_update+1;sample=((px,pz),distance);extra_turn_calls=0
    if mode==0:
        center=projected_target((px,pz),(bx,bz),distance,1100)
        target=target_yaw_from_position((bx,bz),center)
        update,yaw,extra_turn_calls=advance_turn(update,yaw,target,128)
        choice=0;samples=[sample]
    else:
        if formation_choice not in (0,1,2):raise ValueError('explicit formation layout choice in [0,3) required')
        choice=formation_choice;samples=[sample]*3
    targets=formation_targets(mode,choice,samples,(bx,bz),yaw,inputs['table'])
    timing=formation_launch(entry_update=update,targets_fixed=targets,current_yaw=yaw,boss_position=(bx,bz),
        scale=scale,helpers_idle=True,pm_free_slots=pm_free_slots)
    base.update(mode=mode,formation_random_consumed=mode==2,formation_choice=choice if mode==2 else None,
        targets_fixed=targets,center_turn_calls=extra_turn_calls,formation_entry_update=update,
        linked_beams=timing['linked_beams'],launch_timing=timing)
    return base
