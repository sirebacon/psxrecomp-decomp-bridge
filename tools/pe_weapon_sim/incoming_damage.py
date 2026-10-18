"""Shared Entity_ResolveDropTable HP/barrier branch; status is applied by caller.

Uses an explicit player state. Does not invent reaction animation or item cures.
"""
from .source_enemy import enemy_damage
from .projectile_geometry import s32
from .joint_reconstruction import s16
from .beam_scheduling import cdiv


def resolve_incoming(player,*,owner,power,action_slot,effect_type,effect_chance,roll,reaction=None):
    before=player.hp;barrier=bool(player.flags&0x200)
    damage,critical=enemy_damage(power,player.defense&65535,
        armor_first=player.armor_first,armor_second=player.armor_second,action_slot=action_slot,
        effect_chance=effect_chance,critical_resist=player.critical_resist,roll=roll(),
        player_flags=player.flags,charged_guard=player.atb>0 and not barrier,effect_type=effect_type)
    if critical:player.flags |= 0x8000
    if barrier:
        if damage>0:
            denominator=s16(player.max_hp)
            if denominator==0:raise ValueError('barrier denominator is zero')
            ratio=cdiv(s32(player.max_atk*4),denominator)
            player.barrier_energy=s32(player.barrier_energy-s32(damage*ratio))
    else:
        if damage>0:player.hp=(player.hp-damage)&65535
        if s16(player.hp)!=0:
            player.reaction_requests.append(owner)
            if reaction:reaction(player,owner)
    return dict(owner=owner,power=power,damage=damage,hp_before=before,hp_after=player.hp,
        critical=critical,barrier=barrier)
