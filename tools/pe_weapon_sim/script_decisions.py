"""Small offline evaluator for isolated script decision fragments.

Not an AI interpreter: unsupported handlers or unknown inputs stop evaluation.
Explicit position/polar contexts support bounded target fragments. No frame
progression, child concurrency or animation is emulated.
"""
from .beam_scheduling import cdiv,lateral_offset,retail_sqrt

def signed(value):
    value &= 0xffffffff
    return value if value<0x80000000 else value-0x100000000

def probe(nodes,start,end,*,distance=None,fields=None,cells=None,base=0,limit=64,position=None,player=None,heading=None,trig_table=None,polygon=None,player_fields=None,random_values=None,stop_offsets=()):
    by={n['offset']:n for n in nodes};memory=dict(cells or {});fields=dict(fields or {})
    at=start;seen=set();trace=[]
    def read(a):
        if a['mode']==0:return signed(a['value'])
        key=(a['mode'],a['value'])
        if key not in memory:raise ValueError('unknown input '+str(key))
        return memory[key]
    def write(a,value):
        if a['mode']==0:raise ValueError('literal output unsupported')
        memory[(a['mode'],a['value'])]=signed(value)
    player_fields=dict(player_fields or {});random_values=dict(random_values or {})
    status='limit'
    for _ in range(limit):
        if at in stop_offsets:status='boundary';break
        if not start<=at<end:status='exit';break
        if at in seen:status='backedge';break
        if at not in by:status='missing instruction';break
        seen.add(at);trace.append(at);n=by[at];a=n['args'];name=n['handler'];nxt=at+8+4*len(a)
        try:
            if name=='Script_AssignValue':write(a[0],read(a[1]))
            elif name=='Entity_GetPositionByType':
                if read(a[0])!=0 or read(a[1])!=0 or player is None:raise ValueError('unknown position selector')
                write(a[3],player[0]);write(a[4],0);write(a[5],player[1]);write(a[6],1)
            elif name=='Script_GetEntityVec3':
                selector=read(a[0])
                if selector==0 and position is not None:
                    for dest,value in zip(a[1:],(position[0],0,position[1])):write(dest,value)
                elif selector==5 and heading is not None:
                    # Unused literal-zero output operands are intentionally discarded.
                    if a[2]['mode']==0:raise ValueError('heading destination must be writable')
                    write(a[2],heading)
                else:raise ValueError('unknown vector selector')
            elif name=='Entity_PolarToPosition':
                if position is None or trig_table is None:raise ValueError('missing polar context')
                radius=read(a[0])
                if radius%65536:raise ValueError('fractional polar radius unsupported')
                delta=lateral_offset(radius//65536,read(a[1]),0,trig_table)
                write(a[2],position[0]+delta[0]);write(a[3],position[1]+delta[1])
            elif name=='Entity_GetDistanceComponents':
                if read(a[0])!=0 or read(a[1])!=0 or distance is None:raise ValueError('unknown target/distance')
                write(a[2],distance)
            elif name=='Entity_GetField':
                key=read(a[0])
                if key not in fields:raise ValueError('unknown core field '+str(key))
                write(a[1],fields[key])
            elif name=='Script_EvalExpr':
                op=read(a[0]);lhs=read(a[2]);rhs=read(a[3])
                operations={0:lambda:lhs+rhs,1:lambda:lhs-rhs,2:lambda:lhs|rhs,3:lambda:lhs&rhs,4:lambda:lhs^rhs,5:lambda:int(bool(lhs or rhs)),6:lambda:int(bool(lhs and rhs)),7:lambda:int(not lhs),9:lambda:int(lhs>rhs),10:lambda:int(lhs<rhs),11:lambda:int(lhs==rhs),12:lambda:int(lhs>=rhs),13:lambda:int(lhs<=rhs),14:lambda:int(lhs!=rhs),15:lambda:lhs*rhs,16:lambda:cdiv(lhs,rhs),18:lambda:lhs>>rhs,19:lambda:lhs,23:lambda:-lhs}
                if op not in operations:raise ValueError('unsupported expression')
                write(a[1],operations[op]())
            elif name=='Script_TestBit':write(a[2],read(a[0])&(1<<read(a[1])))
            elif name=='Script_SetBit':write(a[0],read(a[0])|(1<<read(a[1])))
            elif name=='Script_ClearBit':write(a[0],read(a[0])&~(1<<read(a[1])))
            elif name=='Entity_FindByTypeId':
                if read(a[0])!=0 or read(a[2]) not in player_fields:raise ValueError('unknown cross-actor field')
                write(a[3],player_fields[read(a[2])])
            elif name=='Script_Random':
                if at not in random_values:raise ValueError('explicit random result required')
                value=random_values[at]
                if not read(a[1])<=value<read(a[2]):raise ValueError('random result outside source range')
                write(a[0],value)
            elif name=='Entity_CallAction':
                from .projectile_geometry import point_in_polygon
                if polygon is None or read(a[2])!=len(polygon):raise ValueError('unknown polygon context')
                write(a[4],int(point_in_polygon(read(a[0]),read(a[1]),polygon)))
            elif name=='Script_GetSqrt':
                value=read(a[0])
                write(a[1],retail_sqrt(value))
            elif name=='Script_JumpIfZero':
                if read(a[0])==0:nxt=read(a[1])*2+base
            elif name=='Script_CondBranch':
                if read(a[0])!=read(a[1]):nxt=read(a[2])*2+base
            elif name=='Script_JumpToEntityOffset':nxt=read(a[0])*2+base
            else:raise ValueError('unsupported handler '+name)
        except (ValueError,KeyError) as exc:status=str(exc);break
        at=nxt
    return dict(status=status,next_offset=at,trace=trace,cells={f'{mode}:{index}':value for (mode,index),value in sorted(memory.items())})
