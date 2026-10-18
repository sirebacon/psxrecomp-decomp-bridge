"""Bounded map-156 beam decisions. No autonomous AI or elapsed animation guesses."""
from dataclasses import dataclass
from .projectile_geometry import s32



def retail_sqrt(value):
    """Lift of Math_IntSqrt at0x8005186c..0x800518a8 (60 bytes).

    Signed compares, shifts30..0 in steps of two. Negative signed input yields0.
    """
    remainder=s32(value);root=0
    for shift in range(30,-1,-2):
        trial=s32(s32((root<<2)+1)<<shift)
        admitted=remainder>=trial
        root=s32(root<<1)
        if admitted:remainder=s32(remainder-trial);root |= 1
    return root


def cdiv(a,b):
    if b==0:raise ValueError('script division by zero')
    return s32((-1 if (a<0)!=(b<0) else 1)*(abs(a)//abs(b)))


def projected_target(player,boss,distance_fixed,offset):
    """Actual per-axis integer divide/multiply sequence, not float normalization."""
    if distance_fixed<offset*65536:return tuple(player)
    denominator=cdiv(distance_fixed,65536)
    return tuple(s32(p+s32(cdiv(s32(cdiv(s32(b-p),65536)*offset),denominator)*65536))
                 for p,b in zip(player,boss))


def later_target_allowed(slot,targets,triggers):
    if slot==1:
        if triggers[0]!=1:return True
        # Retail root+7864 subtracts cell24 from itself. Keep the zero Z term.
        square=s32(s32(targets[1][0]-targets[0][0])**2)
        return retail_sqrt(square)>1000
    if slot==2:
        if not (triggers[0]==1 or triggers[1]==1):return True
        # Both comparisons run even when only one prior owner is triggered.
        for previous in (1,0):
            dx=s32(targets[2][0]-targets[previous][0]);dz=s32(targets[2][1]-targets[previous][1])
            square=s32(s32(dx*dx)+s32(dz*dz))
            if retail_sqrt(square)<=1000:return False
        return True
    raise ValueError('only later slots have spacing predicates')


@dataclass
class BeamOwnerPoll:
    slot:int
    phase:str='idle'

    def __post_init__(self):
        if self.slot not in (0,1,2):raise ValueError('invalid beam owner slot')

    def poll(self,cells,*,command_complete=False,action_state=0,held=0):
        """One externally timed script resume; never assumes actors' update order.

        Trigger remains one until command completion and held-zero. Slot2 also
        waits selected record state0/4 and explicitly yields before its held test.
        """
        trigger=18+self.slot
        if self.phase=='idle':
            if cells.get(trigger,0)!=1:return None
            self.phase='command'
            short=cells[27]==1
            return dict(slot=self.slot,target=(cells[21+2*self.slot],cells[22+2*self.slot]),
                duration=60 if short else 300,interval=60 if short else 300 if self.slot==0 else 140)
        if self.phase=='command':
            if not command_complete:return None
            self.phase='state' if self.slot==2 else 'held'
        if self.phase=='state':
            if action_state not in (0,4):return None
            self.phase='held';return None # explicit one-update yield at root+1432
        if self.phase=='held' and held==0:
            cells[trigger]=0;self.phase='idle'
        return None


@dataclass
class EffectProcess:
    """Pm_Exec state transitions plus FieldFx_UpdateTasks interruption predicates.

    Marking the PM owner for closure does not clear the actor's action record or
    held bits. Explicit Pm_Stop clears the PM slot but has the same distinction.
    """
    state:int=2

    def begin(self):
        if self.state==4:self.state=5;return False
        if self.state==5:self.state=0;return False
        if self.state not in (1,2):return False
        self.state=2;return True

    def actor_gate(self,*,action_state,held,command_value,core_flags,actor_mode):
        if action_state==0:
            if held>0 and command_value<=0 or core_flags&0x180e:self.state=4
            if actor_mode<2:return False
        return True # callback still runs on the update which marks state4

    def stop(self,*,owner_matches,force=False):
        if self.state in (0,6) or not (owner_matches or force):return False
        self.state=0;return True


def lateral_offset(radius,heading,side,table):
    angle=(heading+side*1024)&4095
    a=0x1400-angle
    sine,cosine=table[abs(a)&4095]
    if a<0:sine=-sine
    return (s32((-radius*65536)*(cosine<<4)>>16),
            s32((-radius*65536)*(sine<<4)>>16))


def formation_targets(mode,choice,samples,boss,heading,table):
    """Fixed16 target writes before navigation calls; supplied sample times only.

    mode0 needs one (playerXZ,distance) sample. mode2 requires three, preserving
    the separate player reads. Returned coordinates precede floor/navigation
    validation and division to integer cells at each accepted trigger.
    """
    if mode not in (0,2):raise ValueError('mode1 uses separate sequential path')
    if choice not in (0,1,2):raise ValueError('explicit Script_Random outcome required')
    if len(samples)!=(1 if mode==0 else 3):raise ValueError('wrong target sample count')
    if mode==0:
        center=projected_target(samples[0][0],boss,samples[0][1],1100)
        radius=1200
    else:
        player,distance=samples[0];offset=1100 if choice==0 else 900
        towards=projected_target(player,boss,distance,offset)
        center=tuple(s32(2*p-t) for p,t in zip(player,towards))
        radius=750
    targets=[center]
    for i,side in enumerate((1,-1)):
        origin=center if mode==0 else projected_target(samples[i+1][0],boss,samples[i+1][1],1100)
        delta=lateral_offset(radius,heading,side,table)
        targets.append(tuple(s32(a+b) for a,b in zip(origin,delta)))
    if mode==2 and choice in (1,2):
        delta=lateral_offset(500,heading,1 if choice==1 else -1,table)
        targets[0]=tuple(s32(a+b) for a,b in zip(center,delta))
    return targets
