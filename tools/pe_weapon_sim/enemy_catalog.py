"""Conservative map + rank/kind joins of static script literals.

This is a scenario built from declarations, not execution of enemy AI. Conflicting
values, indirect operands and absent identity declarations do not produce a match.
Optional `cells` (shared scale cells, e.g. enemy_identity.FIRST_RUN_SHARED_CELLS) add the
scaled-rank identity of the ten scripts using that idiom; omitted, results are unchanged.
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .enemy_identity import cells_key, identity_keys


@lru_cache(maxsize=4)
def catalog(cells=()):
    path=Path(__file__).resolve().parents[2]/'findings/data/pe-enemy-scripts-2026-10-18.json'
    data=json.loads(path.read_text()); candidates=defaultdict(list)
    keys=identity_keys(dict(cells))
    for room in data['rooms']:
        if room['disc']!=1:continue # Both campaign room blobs were verified identical across discs.
        for script in room.get('scripts',[]):
            if script['actor_type']==0:continue
            values=defaultdict(set)
            for fact in script['facts']:
                args=fact['args']
                if fact['handler']=='Entity_SetField' and len(args)==2 and all(a['mode']==0 for a in args):
                    values[args[0]['value']].add(args[1]['value'])
            if not all(len(values[k])==1 for k in (0x29,0x2a,0x3e)):continue
            rank=next(iter(values[0x29]));kind=next(iter(values[0x2a]));step=next(iter(values[0x3e]))
            if not 0<=rank<128 or not 0<=kind<256 or not 0<step<=9000:continue
            p=dict(rank=rank,charge_step=step)
            if len(values[0x45])==1:
                value=next(iter(values[0x45]))&65535
                p['periodic_damage']=value if value<32768 else value-65536
            # Entity_WriteFieldByCmd 0x43 / 0x44: the status strength its hits inflict on Aya
            # (Battle_ApplyEnemyAttack: poison step and period).
            if len(values[0x43])==1 and len(values[0x44])==1:
                p['status_level']=next(iter(values[0x43]))&255
                p['status_period']=next(iter(values[0x44]))&255
            for ident,how in keys.get((room['map'],script['actor_type']),[((kind<<8)|rank,'literal')]):
                q=dict(p,rank=ident&255) if how!='literal' else p
                candidates[(room['map'],ident)].append(q)
    return {key:rows[0] for key,rows in candidates.items() if all(r==rows[0] for r in rows)}

def lookup(foe,cells=None):
    try:key=(int(foe['loc']),int(foe['name'],16))
    except (KeyError,ValueError,TypeError):return {}
    return dict(catalog(cells_key(cells)).get(key,{}))


@lru_cache(maxsize=4)
def action_catalog(cells=()):
    root=Path(__file__).resolve().parents[2]/'findings/data'
    decoded=json.loads((root/'pe-enemy-actions-2026-10-18.json').read_text())
    keys=identity_keys(dict(cells))
    candidates=defaultdict(list)
    for script in decoded['scripts']:
        if not script['actions']:continue
        for ident,_ in keys.get((script['map'],script['actor_type']),[]):
            candidates[(script['map'],ident)].append(sorted([dict(windup=a['windup'],recovery=a['recovery'],slot=a['slot'],reset_on_completion=a['reset_on_completion']) for a in script['actions']],key=lambda a:(a['windup'],a['recovery'],a['slot'])))
    return {key:rows[0] for key,rows in candidates.items() if all(r==rows[0] for r in rows)}

def timing_profile(foe,policy,cells=None):
    if policy not in ('fast','slow'):raise ValueError('timing policy must be fast or slow')
    try:actions=action_catalog(cells_key(cells)).get((int(foe['loc']),int(foe['name'],16)),[])
    except (KeyError,ValueError,TypeError):return {}
    if not actions:return {}
    selected=(min if policy=='fast' else max)(actions,key=lambda a:(a['windup']+a['recovery'],a['windup'],a['slot']))
    return {k:selected[k] for k in ('windup','recovery','reset_on_completion')}
