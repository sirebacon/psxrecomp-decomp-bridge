"""Source geometry primitives and action-contact drain; not combat integration."""
from dataclasses import dataclass

def s32(value):
    value &= 0xffffffff
    return value if value<0x80000000 else value-0x100000000

def point_in_polygon(x_fixed,z_fixed,vertices):
    if len(vertices)<3:raise ValueError('polygon needs at least three vertices')
    x=x_fixed>>16;z=z_fixed>>16;inside=False
    current_x,current_z=vertices[-1]
    for next_x,next_z in vertices:
        previous_x,previous_z=current_x,current_z
        current_x,current_z=next_x,next_z
        if ((z>=current_z and z<previous_z) or (z<current_z and z>=previous_z)):
            if x<current_x and x<previous_x:inside=not inside
            elif x<current_x or x<previous_x:
                cross=s32((previous_x-current_x)*(z-current_z))
                dz=previous_z-current_z
                product=s32(dz*(x-current_x))
                if (cross<product if dz<0 else product<cross):inside=not inside
    return inside

def transform_point(rotation,translation,point):
    """Unsaturated sf12 matrix-vector subset, with explicit safe-range check.

    GTE saturation/overflow flags are not emulated; rejecting avoids silently
    claiming exactness outside this subset. Rotation entries are signed16.
    """
    values=[sum(rotation[i][j]*point[j] for j in range(3))>>12 for i in range(3)]
    if any(not -32768<=v<=32767 for v in values):raise ValueError('GTE saturation requires emulation')
    return [((s32(v+translation[i])+32768)&65535)-32768 for i,v in enumerate(values)]

@dataclass
class ContactOwner:
    name:str
    pending:bool=False
    effect_state:int=2
    dead:bool=False
    has_effect:bool=True

def drain_action_contacts(player_flags,owners,apply=None):
    """Menu_MainUpdate action-hit scan only; separate body-contact path omitted.

    Outer reaction gate is evaluated once. Owner pending is consumed only on
    eligible delivery. Global player hit latch is cleared even on gated passes.
    Caller supplies hit effects/damage; this function does not invent beam power.
    """
    delivered=[]
    gated=bool(player_flags&0x980000) # reaction timer 0x800000 or action gates0x180000
    if not gated:
        for owner in owners:
            if owner.dead or not owner.has_effect:continue
            if player_flags&0x4000 and owner.pending and owner.effect_state in (1,2):
                delivered.append(owner.name);owner.pending=False
                if apply is not None:player_flags=apply(owner,player_flags)
    return player_flags&~0x4000,delivered
