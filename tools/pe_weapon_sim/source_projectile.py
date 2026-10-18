"""Offline burst-orb decision/physics model; geometry inputs are scenarios.

Source math is integer; random draws reproduce ranges, not the PSX global RNG.
Cosmetic particles/pool exhaustion and process-pass ordering remain unmodeled.
"""
from dataclasses import dataclass
import random
import json
from functools import lru_cache
from pathlib import Path
from .source_battle import signed16

def orb_speed(distance):
    # map156 script root+15704..16064, strict comparisons, L1 distance.
    for threshold,speed in ((3500,250),(3000,200),(2000,150),(1500,120),(1000,100)):
        if distance>threshold:return speed
    return 80

def task_spawns(triples,max_updates=256):
    """Source op0/1/2/4/5, up to stop; does not pretend to drain task pools."""
    pc=0;delay=0;variables=[0]*7;events=[]
    for update in range(1,max_updates+1):
        if delay:
            delay-=1
            if delay:continue
        for _ in range(128):
            if not 0<=pc<len(triples):raise ValueError('task script outside records')
            op,a,b=triples[pc];pc+=1
            if op==0:return events
            if op==1:
                if not 0<=a<7:raise ValueError('invalid task variable')
                variables[a]=b
            elif op==2:events.append(dict(update=update,task=a))
            elif op==4:
                if b==1:raise ValueError('dynamic variable wait unresolved')
                if a<0:raise ValueError('negative delay')
                delay=a;break
            elif op==5:events.append(dict(update=update,held=(a==0)))
            else:raise ValueError('unsupported task opcode')
        else:raise ValueError('task instruction limit')
    raise ValueError('task update limit')

@lru_cache(maxsize=1)
def launch_update():
    path=Path(__file__).resolve().parents[2]/'findings/data/pe-projectile-extract-2026-10-18.json'
    data=json.loads(path.read_text())
    program=next(p for p in data['programs'] if p['map']==156 and p['command']==129)
    spawns=task_spawns(program['triples'])
    launches=[e['update']+1 for e in spawns if e.get('task')==0]
    if len(launches)!=1:raise ValueError('ambiguous orb task launch')
    return launches[0]

@dataclass
class BurstOrb:
    x:int=0
    y:int=-320
    z:int=0
    vx:int=100
    vy:int=24
    vz:int=0
    state:int=0
    timer:int=0
    alive:bool=True
    cooldown:int=1

    def tick(self,rng,*,player_x,player_z=0,player_radius=0,floor_y=0,inside=True):
        """One particle callback and held-effect cooldown update; bool contact."""
        if not self.alive:return False
        if self.cooldown>=2:self.cooldown-=1
        contact=False
        if self.state==0:
            self.timer+=1
            self.x=signed16(self.x+self.vx+rng.randrange(32)-16)
            self.y=signed16(self.y+self.vy+rng.randrange(32)-16)
            self.z=signed16(self.z+self.vz+rng.randrange(32)-16)
            if self.y>=floor_y:self.state=1;self.timer=0
            contact=(self.x-player_x)**2+(self.z-player_z)**2<(150+player_radius)**2
            if not inside:self.state=5;self.timer=0
        elif self.state==1:
            self.timer+=1
            contact=self.timer<9 and (self.x-player_x)**2+(self.z-player_z)**2<(400+player_radius)**2
            if self.timer>=16:self.alive=False
        elif self.state==5:
            self.timer+=1
            if self.timer>=6:self.alive=False
        if contact and self.cooldown==1:
            self.cooldown=25;return True
        return False

class OrbEnemy:
    """Map156 chooser fragment with explicitly assumed outer gates and geometry.

    Close gate <1300 selects slot0; far path forces the verified slot4 path.
    Far-path intermediate chooser branches remain an assumption. No uniform RNG
    choice probabilities are invented. Animations/processes are not emulated.
    """
    def __init__(self,clock,*,distance,rng,height=320,radius=0,launch_update_value=None):
        self.clock=clock;self.distance=distance;self.rng=rng;self.height=height
        self.radius=radius;self.launch_update=launch_update() if launch_update_value is None else launch_update_value;self.phase='charge'
        self.age=0;self.orb=None;self.kind=None;self.impact=None
        self.last_strike_geometric=False;self.actions=0;self.projectiles=0
    def tick(self,*,paused=False):
        poison=self.clock.tick(paused=paused);self.last_strike_geometric=False
        if paused or self.clock.incapacitated:return False,poison
        if self.phase=='charge':
            if self.clock.charge>=9000:
                self.kind='melee' if self.distance<1300 else 'orb'
                self.phase='action';self.age=0;self.actions+=1
                self.orb=None;self.impact=None
            return False,poison
        self.age+=1;strike=False;complete=False
        if self.kind=='melee':
            strike=self.age==35;complete=self.age>=41
        else:
            if self.age==self.launch_update:
                self.orb=BurstOrb(y=-self.height,vx=orb_speed(self.distance));self.projectiles+=1
            if self.orb and self.orb.alive:
                state=self.orb.state
                strike=self.orb.tick(self.rng,player_x=int(self.distance),player_radius=self.radius)
                self.last_strike_geometric=strike
                if state==0 and self.orb.state==1:self.impact=self.age
            # Visual tail is bounded with a scenario max24 updates after impact;
            # exact callback slot traversal, sprite pool and pass order unresolved.
            complete=self.impact is not None and self.age>=max(63,self.impact+25)
            # No airborne timeout is invented; horizon stops the combat if needed.
        if complete:self.clock.charge=0;self.phase='charge'
        return strike,poison



def beam_window(duration,interval,*,spawn_update=47):
    """Uninterrupted beam controller phase ticks; geometric contact assumed.

    Six approach, six expand, duration active, 32 fade callbacks. Held state
    rearm also requires24 updates. These are opportunities, not delivered hits.
    """
    if duration<=0 or interval<=0:raise ValueError('positive beam parameters required')
    first=spawn_update+12
    opportunities=list(range(first,first+duration,max(24,interval)))
    end=spawn_update+12+duration+32-1
    return dict(first_active=first,contact_opportunities=opportunities,callback_end=end,stop_check_update=end+1)
