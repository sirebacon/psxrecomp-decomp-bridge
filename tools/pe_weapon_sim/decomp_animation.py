"""Uninterrupted ordinary queued-shot timing from extracted assets and retail C.

Update zero begins immediately before Battle_UpdatePlayerTurn. Its battle logic
runs before Entity_AdvanceAnim. Does not model burst-mode repeated hits, reload,
dead targets, interruptions, menu input or asynchronous effect readiness.
"""
import functools
import json
from pathlib import Path


@functools.lru_cache(maxsize=1)
def assets():
    return json.loads((Path(__file__).resolve().parents[2] / 'findings/data/pe-animation-extract-2026-10-18.json').read_text())


def queued_shot_timeline(kind, shots, *, costume=0, target_changes=()):
    if kind not in range(1,9) or shots < 1 or costume not in (0,1):
        raise ValueError('known kind/costume and positive shot count required')
    changes=set(target_changes)
    if any(i < 1 or i >= shots for i in changes): raise ValueError('invalid target change index')
    bank=next(b for b in assets()['weapon_banks'] if b['kind']==kind and b['costume']==costume)
    frames={a['mode']:a['frame_count'] for a in bank['actions']}
    if len({frames[m] for m in (6,8,10)})!=1 or len({frames[m] for m in (7,9,11)})!=1:
        raise ValueError('angle-specific durations require explicit angle')
    w0,w1,per,retarget,_=assets()['battle_animation_rows'][kind]
    # First aim reaches last sample after frame_count-1 animator calls.
    fire=frames[6]-1+w0+w1
    fires=[fire]
    for i in range(1,shots):
        # Follow-through completes when animPrev == last frame. The next aim
        # is placed on its last frame and held; per-shot count is drained,
        # then an additional battle update releases the pose and fires.
        fire += frames[7] + w1 + per + 1 + (retarget if i in changes else 0)
        fires.append(fire)
    finish=fires[-1]+frames[7]
    return dict(kind=kind,costume=costume,shots=shots,fire_updates=fires,
        queue_finish_update=finish,update_calls=finish+1,
        aim_frames=frames[6],follow_frames=frames[7],target_changes=sorted(changes))


def commit_seconds(kind, shots, rules):
    hz=rules.get('battle_update_hz',59.9/2)
    if hz<=0: raise ValueError('positive battle update frequency required')
    if shots==0: return 0.0
    return queued_shot_timeline(kind,shots,costume=rules.get('animation_costume',0))['update_calls']/hz


def source_rules(rules, *, costume=0, update_hz=59.9/2):
    """Explicit experimental profile; stable name separates historical caches."""
    return dict(rules,name=rules['name']+f'-asset-queue-c{costume}-{update_hz:g}',
        damage_rules_name=rules.get('damage_rules_name',rules['name']),
        animation_model='asset_queue',animation_costume=costume,
        battle_update_hz=update_hz,source_gauge=True)


def source_combat_rules(rules, *, costume=0, update_hz=59.9/2):
    result=source_rules(rules,costume=costume,update_hz=update_hz)
    result.update(name=result['name']+'-combat',combat_backend='source')
    return result


def source_behavior_rules(rules, **kw):
    result=source_combat_rules(rules,**kw)
    result.update(name=result['name']+'-charge-v1',enemy_model='charge')
    return result
