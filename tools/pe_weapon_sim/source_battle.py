"""Offline, update-stepped player action simulation derived from retail C.

Models finite pooled ammo, queued/repeated fire, timed hit callbacks, and carried
weapon/gauge state. Caller supplies target eligibility/angles and damage callback.
No enemy AI, asset I/O latency prediction or controller automation.
"""
from dataclasses import dataclass
import random
from .decomp_animation import assets
from .source_timing import FULL, HALF, gauge_gain, refill_updates, step_gauge


def ammo_pool(kind):
    if kind not in range(1,9): raise ValueError('unknown weapon kind')
    return 0 if kind <= 5 else kind-5 if kind <= 7 else 'club'


def signed16(n):
    return ((n+32768)&65535)-32768


def burst_contains(player_angle, target_angle):
    """Literal Battle_ResolveHitOnTimer 0x80 angular predicate (PSX angle units)."""
    centered=signed16(player_angle-0x800)
    if centered < -0x600: lower,upper=player_angle-0x600,player_angle+0x600
    elif centered < 0x600: lower,upper=player_angle-0xA00,player_angle-0x600
    else: lower,upper=player_angle-0x1600,player_angle-0xA00
    lower,upper,angle=map(signed16,(lower,upper,target_angle))
    if -0x600 <= centered < 0x600: return lower <= angle <= upper
    return not (angle < upper and lower < angle)


def action_frames(kind, costume=0):
    bank=next(b for b in assets()['weapon_banks'] if b['kind']==kind and b['costume']==costume)
    return {a['mode']:a['frame_count'] for a in bank['actions']}


def build_queue(mode, rof, commands, targets, selected, rng,*,counter=False):
    """Battle_FillActionQueue: ordinary/burst slots, random slots, all-target batches."""
    if mode not in (None,'burst','random','all') or not 1<=rof<=15 or not 1<=commands<=3:
        raise ValueError('invalid mode/RoF/commands')
    if not targets or selected not in targets: raise ValueError('eligible selected target required')
    if counter:
        return [dict(target=selected,command=0) for _ in range(1 if mode in ('random','all') else rof)]
    queue=[]
    for command in range(commands):
        chosen=(list(targets) if mode=='all' else
                [rng.choice(targets) for _ in range(rof*3//2)] if mode=='random' else
                [selected]*rof)
        queue.extend(dict(target=t,command=command) for t in chosen)
    if len(queue)>45: raise ValueError('queue exceeds retail 45-entry storage')
    return queue


@dataclass
class Gun:
    kind: int
    capacity: int
    loaded: int

    def __post_init__(self):
        if self.kind not in range(1,9) or self.capacity<1: raise ValueError('invalid gun')
        self.capacity=min(999,self.capacity)
        if not 0<=self.loaded<=self.capacity: raise ValueError('invalid loaded ammo')


class BattleSession:
    def __init__(self,guns,reserves,equipped,*,stat22=79,gauge=0,costume=0,seed=7,
                 on_update=None,should_stop=None):
        if equipped not in guns or not 0<=gauge<=FULL or costume not in (0,1):
            raise ValueError('invalid initial state')
        if any(v<0 for v in reserves.values()): raise ValueError('negative reserve')
        self.guns={k:Gun(v.kind,v.capacity,v.loaded) for k,v in guns.items()}
        self.reserves=dict(reserves);self.equipped=equipped;self.stat22=stat22
        self.gauge=gauge;self.costume=costume;self.update=0;self.events=[]
        self.rng=random.Random(seed)
        self.on_update=on_update;self.should_stop=should_stop or (lambda:False)
        self.slow=False;self.haste=False;self.serial=False
        self.on_idle=None;self.action_busy=False

    @property
    def gain(self): return gauge_gain(self.stat22,self.gun.kind,slow=self.slow,haste=self.haste)

    @property
    def stopped(self): return self.should_stop()

    @property
    def gun(self): return self.guns[self.equipped]

    def event(self,kind,**fields):
        event=dict(update=self.update,event=kind,weapon=self.equipped,**fields)
        self.events.append(event);return event

    def advance(self,count=1,*,paused=False):
        if not isinstance(count,int) or count<0: raise ValueError('nonnegative integer update count required')
        for _ in range(count):
            if self.stopped: break
            self.gauge=step_gauge(self.gauge,self.gain,menu_mode=0 if paused else 1,
                game_flags=0x100 if self.serial and self.action_busy else 0)   # flag 0x100 during actions
            self.update+=1
            if self.on_update: self.on_update(self,paused)
            if self.on_idle and not paused and not self.action_busy and not self.stopped:
                self.on_idle()

    def wait_gauge(self,target=FULL):
        while self.gauge<target and not self.stopped:
            if self.gain<=0: raise ValueError('zero fill rate cannot reach the target')
            self.advance()

    def reload(self):
        if self.gun.kind==8: return 0
        pool=ammo_pool(self.gun.kind)
        amount=min(self.gun.capacity-self.gun.loaded,self.reserves.get(pool,0))
        self.reserves[pool]=self.reserves.get(pool,0)-amount
        self.gun.loaded+=amount
        if amount: self.event('ammo_transfer',amount=amount,pool=pool,loaded=self.gun.loaded)
        return amount

    def switch(self,destination,*,half_bar=True,menu_updates=0,stream_updates=0,cancel=False,free=False):
        """One equip turn. Explicit stream wait holds mode13, while gauge can refill.

        No predicted disk latency. Menu is paused. No queue can fire in this turn.
        No-stall mode13 completion uses the snapshot's base actor clip.
        """
        if destination not in self.guns or destination==self.equipped: raise ValueError('different owned gun required')
        if min(menu_updates,stream_updates)<0: raise ValueError('negative delay')
        # free (candidate rule, not retail): no gauge wait and no gauge cost; the equip clip still plays.
        if not free: self.wait_gauge(HALF if half_bar else FULL)
        saved=self.gauge
        if self.stopped: return
        if cancel and (not half_bar or saved>=FULL): raise ValueError('only borrowed cancellation modeled')
        self.action_busy=True
        self.advance(menu_updates,paused=True)
        if self.stopped: self.action_busy=False;return
        if cancel:
            self.event('switch_cancel',gauge=self.gauge);self.action_busy=False;return
        old=self.equipped;self.equipped=destination
        self.gauge=saved if free else (saved-HALF if half_bar else 0)
        self.event('weapon_change',old=old,gauge=self.gauge,loaded=self.gun.loaded)
        # encounter.c releases the mode13 hold after bank streaming is ready;
        # completion checks animPrev, hence frame_count+1 battle calls.
        clip=next(a['frame_count'] for a in assets()['actions'] if a['mode']==13 and a['available'])
        self.advance(stream_updates+clip+1)
        if not self.stopped:
            self.event('switch_ready',gauge=self.gauge,stream_updates=stream_updates,clip_calls=clip+1)
        self.action_busy=False

    def attack(self,*,rof=1,commands=1,mode=None,targets=(0,),selected=0,
               target_alive=None,target_angles=None,player_angle=0,on_hit=None,max_updates=100000,counter=False,fire_speed=1.0,fire_cadence=None,no_hold=False):
        """Retail's player queue for supplied stable target geometry.

        target_alive(id) and on_hit(event) can update enemy health between hits.
        Defaults are living targets and no damage. Return absolute event times.
        """
        queue=build_queue(mode,rof,commands,list(targets),selected,self.rng,counter=counter)
        alive=target_alive or (lambda _:True)
        angles=target_angles or {}
        if mode=='burst' and set(targets)-set(angles): raise ValueError('burst needs every target angle')
        if not counter: self.wait_gauge()
        start=self.update;event_start=len(self.events)
        if self.stopped:
            return dict(start=start,end=start,updates=0,events=[],loaded=self.gun.loaded,reserves=dict(self.reserves))
        if not counter: self.gauge=0
        self.action_busy=True
        self.event('counter_start' if counter else 'attack_start',mode=mode,queue=[dict(q) for q in queue])
        if self.gun.loaded==0: self.reload() # Battle_DispatchEntityEffect
        frames=action_frames(self.gun.kind,self.costume)
        if fire_speed>1:
            # Experiment (R-E): Aya's animation step scaled during the volley -> aim / follow loops k x shorter.
            frames=dict(frames);frames[6]=max(1,round(frames[6]/fire_speed));frames[7]=max(1,round(frames[7]/fire_speed))
        trig=assets()['battle_animation_rows'][self.gun.kind][4]
        if fire_cadence:
            # Experiment (R-E): the follow loop of an installed RoF 5+ volley plays in at most fire_cadence frames.
            frames=dict(frames);frames[7]=min(frames[7],fire_cadence)
        if fire_speed>1 or fire_cadence:
            frames[7]=max(frames[7],trig)      # never shorter than the hit frame (else the next shot drops the pending hit)
        w0,w1,per,retarget,trigger=assets()['battle_animation_rows'][self.gun.kind]
        frame=previous=0;pose='aim';hold=False;index=0;remaining=rof
        committed=True;pending=None

        def fire(target):
            nonlocal pending
            if self.gun.kind!=8:
                if not self.gun.loaded:
                    self.event('empty_click',target=target);return
                self.gun.loaded-=1
            self.event('fire',target=target,loaded=self.gun.loaded)
            pending=(self.update+trigger-1,target,index)

        def advance_slot():
            nonlocal index,w1
            old=queue[index]['target'];index+=1
            if index<len(queue) and queue[index]['target']!=old:
                w1=(w1+retarget)&255

        while index<len(queue) and not self.stopped:
            if self.update-start>=max_updates: raise RuntimeError('player queue did not terminate')
            target=queue[index]['target']
            if committed:
                if not alive(target):
                    self.event('skip_dead_target',target=target);advance_slot();self.advance();continue
                pose='aim';frame=previous=0;hold=False;committed=False
            if pose=='reload':
                if previous==frames[12]-1:
                    self.event('reload_ready',target=target)
                    pose='aim';frame=previous=0;hold=False
            elif pose=='aim' and frame==frames[6]-1:
                if w0: w0-=1;hold=True
                elif w1: w1-=1;hold=True
                else:
                    if mode=='all': self.event('attack_counter_reset',before=remaining,after=rof)
                    pose='follow';frame=previous=0;hold=False;remaining=rof
                    w1=assets()['battle_animation_rows'][self.gun.kind][1];fire(target)
            elif pose=='follow' and previous==frames[7]-1:
                repeated=mode=='all' and remaining!=1
                if repeated:
                    if self.gun.loaded or self.gun.kind==8:
                        if alive(target): remaining-=1;fire(target)
                        else: committed=True;advance_slot()
                    elif self.reload():
                        self.event('reload_start',target=target,clip_frames=frames[12])
                        pose='reload';frame=previous=0;hold=False
                    else:
                        committed=True;advance_slot()
                elif index+1==len(queue):
                    advance_slot()
                elif not alive(queue[index+1]['target']):
                    # attack.c advances once internally, then player_turn.c once.
                    self.event('skip_dead_target',target=queue[index+1]['target'])
                    index+=1;committed=True;advance_slot()
                elif self.gun.loaded or self.gun.kind==8:
                    pose='aim';frame=frames[6]-1;previous=0;hold=True
                    w1=(w1+(0 if no_hold else per))&255;advance_slot()   # no_hold: experiment R-E (per-shot hold removed)
                elif self.reload():
                    self.event('reload_start',target=target,clip_frames=frames[12])
                    pose='reload';frame=previous=0;hold=False;advance_slot()
                else:
                    # No transfer: retail advances the queue, retaining follow pose.
                    advance_slot()
            if pending and pending[0]==self.update:
                _,hit_target,slot=pending;pending=None
                facing=player_angle(hit_target) if callable(player_angle) else player_angle
                hit_targets=([t for t in targets if alive(t) and burst_contains(facing,angles[t])]
                    if mode=='burst' else [hit_target] if alive(hit_target) else [])
                event=self.event('hit',targets=hit_targets,queue_slot=slot)
                if on_hit: on_hit(event)
            previous=frame
            if not hold:
                frame=(frame+1)%frames[6 if pose=='aim' else 7 if pose=='follow' else 12]
            self.advance()
        self.event('attack_done',gauge=self.gauge,loaded=self.gun.loaded)
        self.action_busy=False
        return dict(start=start,end=self.update,updates=self.update-start,
                    events=self.events[event_start:],loaded=self.gun.loaded,reserves=dict(self.reserves))
