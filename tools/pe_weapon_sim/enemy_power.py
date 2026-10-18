"""Conservative common action-power extraction. No action selection is invented.

Only literals or an adjacent unique-CFG-predecessor multiply/shift pair are
accepted. External shared scales are required, never replaced with 1.0 silently.
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from .projectile_geometry import s32

ROOT=Path(__file__).resolve().parents[2]/'findings/data'
DECLARATIONS={'Script_SetEntityAnim12Args','Script_SetEntityAnim5Args'}


def power_expression(row,node):
    a=node['args'];power=a[4]
    if power['mode']==0:return dict(kind='literal',value=power['value']&65535,proof_offsets=[node['offset']])
    by={n['offset']:n for n in row['nodes']};pred=defaultdict(set)
    for edge in row['edges']:
        # A node which is also a child/callback entry is not proved straight-line.
        pred[edge['target']].add(edge['source'])
    at=node['offset'];chain=[]
    for _ in range(2):
        if len(pred[at])!=1:return None
        prev=by.get(next(iter(pred[at])))
        if not prev or prev['handler']!='Script_EvalExpr':return None
        if prev['offset']+8+4*len(prev['args'])!=at:return None
        chain.append(prev);at=prev['offset']
    shift,multiply=chain;sa=shift['args'];ma=multiply['args']
    lit=lambda value:dict(mode=0,value=value)
    if not (sa[0]==lit(18) and sa[1]==power and sa[2]==ma[1] and sa[3]==lit(16)
            and ma[0]==lit(15) and ma[2]['mode']==4 and ma[3]['mode']==0):return None
    return dict(kind='scaled',shared_cell=ma[2]['value'],multiplier=ma[3]['value'],
        proof_offsets=[multiply['offset'],shift['offset'],node['offset']])


def evaluate_power(expression,shared_cells):
    if expression['kind']=='literal':return expression['value']
    cells={int(k):v for k,v in shared_cells.items()};cell=expression['shared_cell']
    if cell not in cells:raise ValueError('explicit shared scale cell '+str(cell)+' required')
    if not isinstance(cells[cell],int):raise ValueError('source scale must be integer')
    return (s32(cells[cell]*expression['multiplier'])>>16)&65535


@lru_cache(maxsize=4)
def records(cells=()):
    """cells: optional shared cells adding the scaled-rank identities (enemy_identity)."""
    decoded=json.loads((ROOT/'pe-enemy-actions-2026-10-18.json').read_text(encoding='utf-8'))
    from .enemy_identity import identity_keys
    keys=identity_keys(dict(cells))
    identities={k:v[0][0] for k,v in keys.items()}
    extracted=[];candidates=defaultdict(list)
    for row in decoded['scripts']:
        chance=[n['args'][1]['value'] for n in row['nodes'] if n['handler']=='Entity_SetField'
            and n['args'][0]==dict(mode=0,value=63) and n['args'][1]['mode']==0]
        all_chance=[n for n in row['nodes'] if n['handler']=='Entity_SetField' and n['args'][0]==dict(mode=0,value=63)]
        critical=chance[0]&255 if chance and len(chance)==len(all_chance) and len(set(chance))==1 else None
        declarations=defaultdict(list)
        for node in row['nodes']:
            if node['handler'] in DECLARATIONS and node['args'][0]['mode']==0:
                declarations[node['args'][0]['value']].append(node)
        for slot,nodes in declarations.items():
            for node in nodes:
                expression=power_expression(row,node);a=node['args']
                entry=dict(map=row['map'],actor_type=row['actor_type'],slot=slot,
                    declaration_offset=node['offset'],expression=expression,critical_chance=critical,
                    effect_type=a[1]['value'] if a[1]['mode']==0 else None,
                    identity=identities.get((row['map'],row['actor_type'])))
                extracted.append(entry)
                # Reject alternate declarations rather than choosing one.
                if len(nodes)==1 and expression and critical is not None and entry['identity'] is not None and entry['effect_type'] is not None:
                    for ident,_ in keys.get((row['map'],row['actor_type']),[]):
                        candidates[row['map'],ident,slot].append(entry)
    catalog={}
    def signature(e):
        x={k:v for k,v in e['expression'].items() if k!='proof_offsets'}
        return (json.dumps(x,sort_keys=True),e['critical_chance'],e['effect_type'])
    for key,entries in candidates.items():
        if all(signature(e)==signature(entries[0]) for e in entries):catalog[key]=entries[0]
    return extracted,catalog


def power_profile(foe,slot,shared_cells,scaled_identities=False):
    try:key=(int(foe['loc']),int(foe['name'],16),slot)
    except (KeyError,ValueError,TypeError):return {}
    from .enemy_identity import cells_key
    entry=records(cells_key(shared_cells) if scaled_identities else ())[1].get(key)
    if entry is None and scaled_identities:
        # Power held in a local on an identity-keyed path (local_power), evaluated at these cells.
        from .local_power import catalog as local_catalog
        local=local_catalog(cells_key(shared_cells)).get(key)
        if local:
            return dict(power=local['power'],action_slot=slot,effect_type=local['effect_type'],
                critical_chance=local['critical_chance'],power_source='local path '+local['path'])
    if entry is None:return {}
    return dict(power=evaluate_power(entry['expression'],shared_cells),action_slot=slot,
        effect_type=entry['effect_type'],critical_chance=entry['critical_chance'])
