"""Offline conservative control-flow and action timing extraction.

Edges are possible branches, not probabilities. Opaque handlers are retained without evaluating their effects; animation timing
assumes an uninterrupted, unpaused actor.
"""
import argparse,hashlib,json,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,instruction,sectors

def literal(arg):return arg['value'] if arg['mode']==0 else None

def flow(blob,start,end,handlers):
    todo=[start];nodes={};edges=[];errors=[]
    while todo:
        at=todo.pop()
        if at in nodes:continue
        if not start<=at<end:errors.append(dict(offset=at,error='target outside actor script'));continue
        try:ins,nxt=instruction(blob,at,handlers)
        except ValueError as exc:errors.append(dict(offset=at,error=str(exc)));continue
        if nxt>end:errors.append(dict(offset=at,error='crosses boundary'));continue
        nodes[at]=ins;name=ins['handler'];a=ins['args'];succ=[]
        if name=='Script_JumpToEntityOffset':
            if a and literal(a[0]) is not None:succ=[(start+literal(a[0])*2,'jump')]
        elif name=='Script_JumpIfZero' and len(a)==2:
            test=literal(a[0]);target=literal(a[1])
            if test!=0:succ.append((nxt,'nonzero'))
            if test in (None,0) and target is not None:succ.append((start+target*2,'zero'))
        elif name=='Script_CondBranch' and len(a)==3:
            lhs,rhs,target=map(literal,a)
            if lhs is None or rhs is None or lhs==rhs:succ.append((nxt,'equal'))
            if (lhs is None or rhs is None or lhs!=rhs) and target is not None:succ.append((start+target*2,'not_equal'))
        elif name not in ('Entity_MarkCurrentNodeFree','Entity_MarkCurrentDead'):
            succ=[(nxt,'next')]
        if name in ('Script_SpawnChildNode','Entity_SelectFieldSetter'):
            arg=a[0] if name=='Script_SpawnChildNode' and a else a[1] if len(a)>1 else None
            value=literal(arg) if arg else None
            if value is not None and value<0x80000000:succ.append((start+value*2,'child_or_callback'))
        for dest,kind in succ:
            edges.append(dict(source=at,target=dest,kind=kind));todo.append(dest)
    return dict(nodes=[nodes[k] for k in sorted(nodes)],edges=edges,errors=errors)


def completion_reset(cfg,call_offset):
    """Only prove a zero-charge setter on one straight post-command path."""
    nodes={n['offset']:n for n in cfg['nodes']};edges={}
    for edge in cfg['edges']:
        if edge['kind']!='child_or_callback':edges.setdefault(edge['source'],[]).append(edge['target'])
    at=call_offset;seen=set()
    for _ in range(64):
        targets=edges.get(at,[])
        if len(targets)!=1:return False
        at=targets[0]
        if at in seen or at not in nodes:return False
        seen.add(at);n=nodes[at];a=n['args']
        if n['handler']=='Entity_SetField' and len(a)==2 and literal(a[0])==43:
            return literal(a[1])==0
        if n['handler'] in ('Script_RunEntityCommand','Entity_MarkCurrentNodeFree','Entity_MarkCurrentDead'):return False
    return False


def timing(enter_frames,exit_frames,enter_step,exit_step,hit_frame):
    if min(enter_frames,exit_frames,enter_step,exit_step)<=0:raise ValueError('positive clips and steps required')
    if not 0<=hit_frame<exit_frames-1:raise ValueError('hit must precede wrap; wrap-hit predicate differs')
    # Strict whole-frame crossing: frame > event.frame. Positive fixed16 steps.
    enter=(enter_frames*65536+enter_step-1)//enter_step
    hit=((hit_frame+1)*65536+exit_step-1)//exit_step
    complete=(exit_frames*65536+exit_step-1)//exit_step
    if hit>=complete:raise ValueError('hit crossing overlaps wrap and is not proven')
    return dict(windup=enter+hit,recovery=complete-hit,enter_updates=enter,hit_exit_update=hit,complete_updates=enter+complete)

def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--out',required=True);a=ap.parse_args()
    source=BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json';inventory=json.loads(source.read_text())
    exe=PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup';raw=exe.read_bytes()
    if raw[:8]!=b'PS-X EXE':raise ValueError('expected PS-X executable')
    load=struct.unpack_from('<I',raw,0x18)[0];initial=0x800109b0-load+0x800
    defaults=[]
    for slot in range(6):
        at=initial+0x1c+slot*16
        defaults.append(dict(enter_step=struct.unpack_from('<i',raw,at+4)[0],exit_step=struct.unpack_from('<i',raw,at+8)[0],category=raw[at+14],hit_frame=raw[at+15]))
    rows=[]
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as disc:
        for room in inventory['rooms']:
            if room['disc']!=1:continue
            blob=sectors(disc,room['lba'],room['sectors'])
            for script in room.get('scripts',[]):
                if script['actor_type']==0:continue
                cfg=flow(blob,script['start'],script['end'],inventory['handlers'])
                nodes=cfg['nodes'];records={};steps={};calls=[]
                for ins in nodes:
                    name=ins['handler'];args=ins['args'];v=[literal(x) for x in args]
                    if name in ('Script_SetEntityAnim12Args','Script_SetEntityAnim5Args') and len(v) in (5,11) and v[0] is not None and 0<=v[0]<6:
                        slot=v[0];rec=dict(defaults[slot],slot=slot,effect_type=v[1],enter_mode=v[2],exit_mode=v[3],power=v[4],power_operand=args[4],declaration_offset=ins['offset'])
                        if len(v)==11:rec.update(category=v[9],hit_frame=v[10])
                        records.setdefault(slot,[]).append(rec)
                    if name=='Script_SetBattleEntryCoords' and len(v)==3 and None not in v:steps.setdefault(v[0],set()).add(tuple(v[1:]))
                    if name=='Script_RunEntityCommand' and v:calls.append(dict(offset=ins['offset'],slot=v[0],operand=args[0]))
                actions=[];banks={b['mode']:b['frame_count'] for b in room['animations'] if b['actor_type']==script['actor_type']}
                for slot,recs in records.items():
                    if slot>=3 or len(recs)!=1 or not any(c['slot']==slot for c in calls):continue
                    rec=recs[0]
                    if slot in steps:
                        if len(steps[slot])!=1:continue
                        rec['enter_step'],rec['exit_step']=next(iter(steps[slot]))
                    if rec['category'] not in (1,3) or rec['hit_frame'] is None:continue
                    if rec['enter_mode'] not in (6,8,10,12,14) or rec['exit_mode'] not in (7,9,11,13,15):continue
                    try:t=timing(banks[rec['enter_mode']],banks[rec['exit_mode']],rec['enter_step'],rec['exit_step'],rec['hit_frame'])
                    except (KeyError,ValueError):continue
                    rec['reset_on_completion']=all(completion_reset(cfg,c['offset']) for c in calls if c['slot']==slot)
                    actions.append(dict(rec,**t,enter_frames=banks[rec['enter_mode']],exit_frames=banks[rec['exit_mode']]))
                if calls or actions:
                    rows.append(dict(map=room['map'],actor_type=script['actor_type'],root=script['start'],actions=actions,calls=calls,**cfg))
    from .script_decisions import probe
    example=next(r for r in rows if r['map']==156 and r['actor_type']==3)
    root=example['root']
    decision_probes=[dict(map=156,actor_type=3,distance=value,precondition='entered close-action gate at root+4752; outer state/position/charge gates are not evaluated',**probe(example['nodes'],root+4752,root+4840,base=root,distance=value*65536)) for value in (1299,1300)]
    out=dict(selection_probes=decision_probes,source_sha256={name:hashlib.sha256((PROJECT/'parasite-eve-decomp'/name).read_bytes()).hexdigest() for name in ('src/main/battle/context.c','src/main/field/actor_collision.c','src/main/battle/enemy_slots.c','src/main/script/system_opcodes.c','src/main/script/flow_opcodes.c','src/main/script/node_actions.c')},scope='Possible control flow including conditional child/callback edges; not executable AI or action probabilities. Timing conditional on no interruption, no animation holds, and own actor bank.',inventory_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),exe_sha256=hashlib.sha256(raw).hexdigest(),initial_records=defaults,scripts=rows)
    Path(a.out).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(dict(scripts=len(rows),timed_actions=sum(len(r['actions']) for r in rows),calls=sum(len(r['calls']) for r in rows),default_steps=defaults)))
if __name__=='__main__':main()
