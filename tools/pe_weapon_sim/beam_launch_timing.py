"""Conditional exact timing of an uninterrupted map156 formation launch.

The encounter entry update and actor pose remain explicit inputs. The
room's default helper creation order is proven from bytecode, not enum order.
"""
import json
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from .beam_scheduling import cdiv
from .projectile_geometry import point_in_polygon,s32
from .ratan_oracle import RatanOracle,ratan_source


@lru_cache(maxsize=1)
def atan_table():
    from .extract_enemy_scripts import PROJECT
    return RatanOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup').table


def target_yaw_from_position(position,target):
    x=s32(position[0]-target[0])>>16;z=s32(position[1]-target[1])>>16
    if x==z==0:raise ValueError('coincident turn retains node flag20; full node replay required')
    return (0x1400-ratan_source(z,x,atan_table()))&4095


def turn_step(current,target,step=128):
    if not (0<=current<4096 and 0<=target<4096 and 0<step<=4096):raise ValueError('invalid yaw/step')
    stepped=target
    if current<target:
        delta=target-current
        if delta<2048:
            if step<delta:stepped=current+step
        elif step<delta:
            stepped=current-step
            if stepped<0 and current+4096-target<step:stepped=target
    elif current>target:
        delta=current-target
        if delta<2048:
            if step<delta:stepped=current-step
        elif step<delta:
            stepped=current+step
            if stepped>=4097 and target+4096-current<step:stepped=target
    return stepped&4095


@dataclass
class AnimationClock:
    frames:dict
    step:int=65536
    mode:int=2
    current:int=0
    previous:int=0
    flags:int=0

    def set_mode(self,mode):
        if mode not in self.frames or self.frames[mode]<1:raise ValueError('unknown animation')
        self.mode=mode;self.current=0;self.previous=0;self.flags &= ~0x200

    def advance(self):
        self.previous=self.current;self.flags &= ~8
        if self.flags&0x100:return
        if self.flags&0x200:raise ValueError('stop-frame state requires explicit bounds')
        after=s32(self.current+self.step);last=self.frames[self.mode]-1
        if last<(after>>16):after=((after>>16)%(last+1))<<16;self.flags |= 8
        elif after<0:after=s32(after+((last+1)<<16));self.flags |= 8
        self.current=after


@dataclass
class AnimationWait:
    mode:int
    started:bool=False
    def resume(self,actor):
        if not self.started:
            self.started=True;actor.set_mode(self.mode);actor.flags &= ~0x100;return False
        wrapped=actor.current<actor.previous if actor.step>=0 else actor.previous<actor.current
        return actor.frames[actor.mode]==1 or wrapped


def parent_animation_finish(start,frames,step=65536):
    actor=AnimationClock(frames,step);waits=[AnimationWait(10),AnimationWait(11)];index=0
    for update in range(start,start+10000):
        while waits[index].resume(actor):
            index+=1
            if index==len(waits):return update
        actor.advance()
    raise ValueError('animation wait did not finish')


def formation_launch(*,entry_update,targets_fixed,current_yaw,scale,helpers_idle,pm_free_slots,target_yaw=None,boss_position=None,step=128,animation_step=65536):
    """Formation tail+14416 onward, normal flags and enough PM slots.

    entry_update is an eligible actor update, starting at1. Caller must establish
    formation target generation/entry and yaw, idle helpers and available slots.
    Output linked_beams is accepted directly by the full combat source backend.
    """
    if entry_update<1 or not isinstance(entry_update,int):raise ValueError('invalid entry update')
    if helpers_idle is not True:raise ValueError('busy/unknown helpers require full node replay')
    if len(targets_fixed)!=3 or any(len(p)!=2 for p in targets_fixed):raise ValueError('three fixed16 target pairs required')
    root=Path(__file__).resolve().parents[2]
    geom=json.loads((root/'findings/data/pe-projectile-geometry-2026-10-18.json').read_text())
    polygon=geom['floor_polygons'][0]['vertices_integer']
    accepted=[bool(point_in_polygon(x,z,polygon)) for x,z in targets_fixed]
    if target_yaw is None:
        if boss_position is None:raise ValueError('boss_position or explicit retail target_yaw required')
        target_yaw=target_yaw_from_position(boss_position,targets_fixed[0])
    elif boss_position is not None:raise ValueError('supply position or yaw, not both')
    update=entry_update;calls=0;yaw=current_yaw
    while True:
        calls+=1;yaw=turn_step(yaw,target_yaw,step)
        if yaw==target_yaw:break
        update+=1
        if calls>4096:raise ValueError('turn did not converge')
    if not isinstance(pm_free_slots,int) or pm_free_slots<sum(accepted):raise ValueError('insufficient verified free primary PM slots')
    # Same-tick polygon calls/assignments do not yield; boss precedes all helpers.
    plans=[];events=[]
    for slot in (2,1,0):
        if not accepted[slot]:continue
        owner='helper'+str(slot+4)
        x,z=targets_fixed[slot]
        integer_x,integer_z=cdiv(x,65536),cdiv(z,65536)
        floor_valid=bool(point_in_polygon(integer_x<<16,integer_z<<16,polygon))
        release=update+(390 if floor_valid else 54)
        plans.append(dict(owner=owner,start_update=update-1,target_x=integer_x,target_z=integer_z,
            duration=300,interval=300 if slot==0 else 140,scale=scale))
        events.append(dict(owner=owner,trigger_update=update,helper_resume_update=update,
            first_effect_update=update,controller_spawn=update+46,beam_floor_valid=floor_valid,
            earliest_contact=update+58 if floor_valid else None,
            earliest_delivery=update+59 if floor_valid else None,effect_release=release,
            trigger_clear=release+2 if slot==2 else release+1))
    frames={a['mode']:a['frame_count'] for r in json.loads((root/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())['rooms']
            if r['disc']==1 and r['map']==156 for a in r['animations'] if a['actor_type']==3}
    return dict(scope='Conditional uninterrupted formation tail; entry/pose/targets/idle helpers/PM capacity supplied',
        ready_for_balance=False,turn_calls=calls,trigger_update=update,accepted=accepted,
        actor_order=[3,6,5,4],target_yaw=target_yaw,linked_beams=plans,events=events,
        parent_wait_finished=parent_animation_finish(update,frames,animation_step) if plans else update)


@dataclass
class HelperActionClock:
    """Entity_TriggerAnimEvent slot3, independent owner with no parent/interrupt.

    The record's completion is governed by effect opcode0, not the end of clip11.
    """
    actor:AnimationClock
    state:int=0
    selected:bool=False

    def request(self):
        a=self.actor
        previous=a.previous;current=a.current
        next_frame=(current>>16)+a.frames[a.mode] if previous>current else current>>16
        crossed=a.frames[a.mode]-1>=previous>>16 and a.frames[a.mode]-1<next_frame
        if a.mode==10 and crossed:
            a.set_mode(11);self.state=1
        elif a.mode==11 and crossed:
            a.set_mode(2);a.step=65536
        elif a.mode not in (0,1,6,7,8,9,10,11,12,13,14,15) and self.state==0:
            self.selected=True;a.set_mode(10);a.step=65536
        if self.state==4:
            a.set_mode(2);a.step=65536;self.state=0;self.selected=False;return True
        return False


def replay_helper_lifetime(slot,*,duration=300,interval=None,target_valid=True):
    """Focused actor -> battle -> render -> primary-FX -> animation pass replay."""
    from .beam_delivery import BeamEmitter,BeamOwner,BeamPlayer,deliver_beams
    from .beam_scheduling import BeamOwnerPoll
    if interval is None:interval=300 if slot==0 else 140
    owner=BeamOwner('helper'+str(slot+4),effect_state=0)
    emitter=BeamEmitter(owner,1000,-6000,duration,interval,target_valid=target_valid)
    player=BeamPlayer(10000,10000,critical_resist=100)
    actor=AnimationClock({2:48,10:42,11:45});command=HelperActionClock(actor)
    cells={18+slot:1,21+2*slot:1000,22+2*slot:-6000,27:0}
    polling=BeamOwnerPoll(slot);events=[]
    for update in range(1,500):
        if update==1:polling.poll(cells)
        finished=command.request() if polling.phase=='command' else False
        polling.poll(cells,command_complete=finished,action_state=command.state,held=emitter.held)
        if cells[18+slot]==0:
            events.append(dict(event='trigger_clear',update=update));return events
        for hit in deliver_beams(player,[owner],lambda:99)['events']:
            events.append(dict(event='delivery',update=update))
        # Owner action state is a pointer observed and written by the FX program.
        if not emitter.cleanup.finished:
            owner.effect_state=command.state
            contact=emitter.update_effect(player,update,player_x=1000,player_z=-6000,player_radius=23)
            command.state=owner.effect_state
            if contact:events.append(dict(event='contact',update=update))
            if update==emitter.spawn_update:events.append(dict(event='controller_spawn',update=update))
            if emitter.cleanup.finished:events.append(dict(event='effect_release',update=update))
        actor.advance()
    raise ValueError('helper trigger did not clear')
