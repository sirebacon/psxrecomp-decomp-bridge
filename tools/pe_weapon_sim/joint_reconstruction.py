"""Q12 joint reconstruction, following LIBGTE FGO_02 and Render_TransformVertices."""
from dataclasses import dataclass
from .projectile_geometry import s32

def s16(value):return ((value+32768)&65535)-32768

def rotation_yxz(angles,table):
    def trig(angle):
        angle=s16(angle);s,c=table[abs(angle)&4095]
        return (-s if angle<0 else s),c
    sx,cx=trig(angles[0]);sy,cy=trig(angles[1]);sz,cz=trig(angles[2])
    def mul(a,b):return s32(a*b)>>12
    a=mul(sy,sx);b=mul(cy,sx)
    return [[s16(mul(cy,cz)+mul(a,sz)),s16(-mul(cy,sz)+mul(a,cz)),s16(mul(sy,cx))],
            [s16(mul(sz,cx)),s16(mul(cz,cx)),s16(-sx)],
            [s16(-mul(sy,cz)+mul(b,sz)),s16(mul(sy,sz)+mul(b,cz)),s16(mul(cy,cx))]]

@dataclass
class Matrix:
    rotation:list
    translation:list

def identity(translation=(0,0,0)):
    return Matrix([[4096,0,0],[0,4096,0],[0,0,4096]],list(translation))

def mac_vector(rotation,vector,translation=(0,0,0)):
    values=[]
    for i in range(3):
        acc=(translation[i]<<12)+sum(rotation[i][j]*vector[j] for j in range(3))
        if not -(1<<43)<=acc<(1<<43):raise ValueError('GTE 44-bit overflow not modeled')
        values.append(s32(acc>>12))
    return values

def compose(parent,local_rotation,local_translation):
    columns=[mac_vector(parent.rotation,[local_rotation[i][j] for i in range(3)]) for j in range(3)]
    # RTIR stores IR1..3 into signed16 rotation columns; clamps rather than wraps.
    rotation=[[max(-32768,min(32767,columns[j][i])) for j in range(3)] for i in range(3)]
    return Matrix(rotation,mac_vector(parent.rotation,local_translation,parent.translation))

def reconstruct(model,animation,frame,table,*,world=None,overrides=()):
    if not 0<=frame<animation['frame_count']:raise ValueError('frame outside clip')
    world=world or identity();angles=[list(v) for v in animation['bone_angles_by_frame'][frame]]
    for override in overrides:
        index=override['index'];flags=override['flags']
        if index<=0:continue
        if index>=len(angles):raise ValueError('override bone outside clip')
        for axis in range(3):
            value=override['angles'][axis]
            if flags&(8<<axis):angles[index][axis]=s16(value)
            elif flags&(1<<axis):angles[index][axis]=s16(angles[index][axis]+value)
    stack=[];current=world;output=[]
    for command in model['matrix_commands']:
        if command==-1:stack.append(current);continue
        if command==-2:
            if not stack:raise ValueError('matrix stack underflow')
            current=stack.pop();continue
        if not 0<=command<len(angles):raise ValueError('matrix command outside bones')
        translation=animation['root_translations'][frame] if command==0 else [0,0,model['part_translation_z'][command]]
        current=compose(current,rotation_yxz(angles[command],table),translation)
        output.append(current)
    if stack:raise ValueError('unbalanced matrix stack')
    if len(output)!=model['part_count']:raise ValueError('matrix/model count mismatch')
    return output

def joint_point(matrices,index,offset):
    m=matrices[index]
    return [s16(v) for v in mac_vector(m.rotation,offset,m.translation)]
