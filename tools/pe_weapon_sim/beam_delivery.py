"""Linked-beam HP/barrier/stiffness delivery on the actor-ordered contact drain.

The full combat adapter and component callers supply the
shared scale, Aya stats, geometry contacts, pass timing and reaction handler.
"""
from dataclasses import dataclass,field
from .projectile_geometry import ContactOwner,drain_action_contacts,s32
from .joint_reconstruction import s16
from .incoming_damage import resolve_incoming
from .effect_cleanup import EffectCleanup

@dataclass
class BeamOwner(ContactOwner):
    scale:int=65536
    effect_chance:int=50
    action_slot:int=3
    def power(self):return (s32(self.scale*90)>>16)&65535

@dataclass
class BeamPlayer:
    hp:int
    max_hp:int
    defense:int=0
    armor_first:int=0
    armor_second:int=0
    critical_resist:int=0
    effect_flags:int=0
    flags:int=0
    atb:int=0
    max_atk:int=0
    barrier_energy:int=0
    stiffness_timer:int=0
    status_step:int=0
    motion:list=field(default_factory=lambda:[0,0,0])
    mode:int=0
    base_mode:int=0
    reaction_requests:list=field(default_factory=list)
    contact_timer:int=0

def stiffness_lock(player,roll):
    """Enemy effect5 ordering, including resist roll before one-time immunity."""
    if player.flags&0xc0==0x80:return 'already_locked'
    if player.effect_flags&8 and roll()<50:return 'resisted'
    if player.flags&0xc0==0xc0:
        player.flags &= ~0xc0
        return 'immunity_consumed'
    player.flags=(player.flags&~(0xc0|0x100))|0x80
    player.stiffness_timer=9000
    return 'locked'

def tick_stiffness(player,*,paused=False):
    if paused or player.flags&0xc0 not in (0x40,0x80):return False
    player.stiffness_timer=(player.stiffness_timer-player.status_step)&65535
    if s16(player.stiffness_timer)<=0:
        if player.flags&0xc0==0x80 and player.mode==17:player.mode=player.base_mode
        player.flags &= ~0xc0
        return True
    if player.flags&0xc0==0x80:player.motion[:]=[0,0,0]
    return False

def deliver_beams(player,owners,roll,*,reaction=None):
    """One admitted source action-hit scan. roll() returns rand()%100 outcomes.

    This preserves sequential changes: the first lock removes Haste before the
    next owner's defense is calculated. Reaction requests are surfaced rather
    than inventing relative hit angle, animation state or Counter priority.
    """
    events=[]
    def apply(owner,flags):
        player.flags=flags|0x10000000
        result=resolve_incoming(player,owner=owner.name,power=owner.power(),
            action_slot=owner.action_slot,effect_type=5,effect_chance=owner.effect_chance,
            roll=roll,reaction=(lambda p,name:reaction(p,owner)) if reaction else None)
        player.motion[:]=[0,0,0]
        status=stiffness_lock(player,roll)
        # Menu scan clears transient critical bit after this owner's HP display.
        player.flags &= ~0x8000
        events.append(dict(result,status=status))
        player.contact_timer=90
        return player.flags|0x10000000|0x1000000
    player.flags,delivered=drain_action_contacts(player.flags,owners,apply)
    return dict(delivered=delivered,events=events)


@dataclass
class BeamEmitter:
    owner:BeamOwner
    target_x:int
    target_z:int
    duration:int
    interval:int
    spawn_update:int=47
    target_valid:bool=True
    held:int=1
    countdown:int=0
    last_update:int=0
    cleanup:object=field(default=None,init=False,repr=False)

    def __post_init__(self):
        if self.duration<=0 or self.interval<=0 or self.spawn_update<1:raise ValueError('invalid beam timing')
        # Uninterrupted controller: 6 approach +6 expand +duration +32 fade.
        end=self.spawn_update+12+self.duration+32-1 if self.target_valid else self.spawn_update+5
        self.cleanup=EffectCleanup(self.spawn_update,self.spawn_update+8,end)

    def update_effect(self,player,update,*,player_x,player_z,player_radius):
        """One consecutive effect update, using the caller's world target.

        Geometry contact schedules pending delivery; it does not deduct HP.
        Caller orders this pass against the battle drain. Controller return1 kills
        the slot even with live visuals; opcode0 releases the owner next update.
        """
        if self.duration<=0 or self.interval<=0:raise ValueError('positive beam timing required')
        if update!=self.last_update+1:raise ValueError('effect updates must be consecutive')
        if player_radius<0:raise ValueError('negative player cylinder radius')
        self.last_update=update
        if self.cleanup.step(update):
            self.finish_tasks();return False
        if self.held>=2:self.held-=1
        if update==self.spawn_update and self.owner.effect_state==1:self.owner.effect_state=2
        if not self.target_valid:return False
        first=self.spawn_update+12
        if not first<=update<first+self.duration:return False
        if self.countdown:self.countdown-=1
        within=(player_x-self.target_x)**2+(player_z-self.target_z)**2<(600+player_radius)**2
        if not within or self.countdown:return False
        contact=False
        if self.held==1:
            player.flags |= 0x4000
            self.owner.pending=True;self.held=25;contact=True
        self.countdown=self.interval
        return contact

    def finish_tasks(self):
        """Release the owner when opcode0 sees no live controller slots."""
        self.held=0;self.owner.effect_state=4


def tick_beam_player(player,*,paused=False):
    if paused:return
    tick_stiffness(player)
    if player.flags&0x200 and player.barrier_energy<=65536:player.flags &= ~0x200
    if player.flags&0x1000000:
        player.contact_timer=(player.contact_timer-1)&255
        if ((player.contact_timer+128)&255)-128<=0:player.flags &= ~0x1000000
