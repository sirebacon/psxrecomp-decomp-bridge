"""Common retail enemy timers and counter-roll arithmetic, without room-script AI."""
from dataclasses import dataclass


def counter_probability(hp_level,rank_difference):
    """Count the actual successful rand()%100 outcomes in Battle_RollEnemySpawn."""
    diff=((rank_difference+128)&255)-128
    threshold=hp_level if diff>0 or diff<-1 else 3*hp_level
    scale=10 if diff>0 else 50 if diff==0 or diff<-1 else 100
    return sum(roll*scale<threshold for roll in range(100))/100


def enemy_damage(power,stat20=0,*,armor_first=0,armor_second=0,action_slot=0,
                 effect_chance=0,critical_resist=0,roll=99,player_flags=0,
                 charged_guard=False,effect_type=0):
    """Entity_ResolveDropTable: damage component, excluding PE-barrier/status paths."""
    scale=stat20//5
    if player_flags&0x1000: scale=scale*3//10
    if player_flags&0x100: scale=scale*3//10
    damage=power-scale-(armor_first if action_slot<3 else armor_second)
    critical=roll<effect_chance*(100-critical_resist)//100
    if critical: damage=int(damage*3/2)
    if charged_guard: damage=int(damage/2)
    if effect_type==10: damage=int(damage/2)
    return max(0,damage),critical


@dataclass
class EnemyClock:
    charge_step: int
    charge: int=0
    flags: int=0
    actor_flags: int=0
    periodic_damage: int=0

    def __post_init__(self):
        if not 0<=self.charge<=65535 or not 0<=self.charge_step<=65535:
            raise ValueError('u16 charge/step required')

    @property
    def incapacitated(self): return bool(self.flags&0x180E)

    def tick(self,*,paused=False):
        """Battle_UpdateEnemy ordering; returns poison damage, not an AI attack."""
        if paused: return 0
        if self.charge==0:
            changed=bool(self.flags&0x180E)
            if self.flags&0xE:
                self.flags=(self.flags&~0xE)|(((((self.flags>>1)&7)-1)&7)*2)
            if self.flags&0x1800:
                self.flags=(self.flags&~0x1800)|((((((self.flags>>11)&3)-1)&3)<<11))
            if changed and not self.incapacitated: self.actor_flags&=~0x1000
        if self.charge<9000:
            next_charge=(self.charge+self.charge_step)&65535
            self.charge=(next_charge-(self.charge_step*2//5 if self.flags&1 else 0))&65535
        else:
            self.charge=0 if self.actor_flags&0x1000 else 9000
        damage=0
        if self.flags&0x10:
            ticks=(self.flags>>5)&31
            if ticks>=30: damage=self.periodic_damage;self.flags&=~0x3E0
            else: self.flags=(self.flags&~0x3E0)|((ticks+1)<<5)
        return damage


class ScriptedEnemy:
    """Explicit scenario policy atop the shared timers, not a decoded room script.

    Plays supplied windup/strike/recovery update counts. Charge resets at start
    by default, or at completion when a decoded post-command setter proves it. Missing durations/steps must be labeled as assumptions.
    """
    def __init__(self,clock,*,windup=10,recovery=10,reset_on_completion=False):
        if min(windup,recovery)<0: raise ValueError('negative action duration')
        self.clock=clock;self.windup=windup;self.recovery=recovery
        self.phase='charge';self.remaining=0;self.reset_on_completion=reset_on_completion

    def tick(self,*,paused=False):
        poison=self.clock.tick(paused=paused)
        if paused or self.clock.incapacitated: return False,poison
        strike=False
        if self.phase=='charge' and self.clock.charge>=9000:
            if not self.reset_on_completion:self.clock.charge=0
            self.phase='windup';self.remaining=self.windup
        elif self.phase=='windup':
            self.remaining-=1
            if self.remaining<=0:
                strike=True;self.phase='recover';self.remaining=self.recovery
        elif self.phase=='recover':
            self.remaining-=1
            if self.remaining<=0:
                if self.reset_on_completion:self.clock.charge=0
                self.phase='charge'
        return strike,poison
