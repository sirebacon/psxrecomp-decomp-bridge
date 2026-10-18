"""Isolated original Script_SetEntityActionAndWait instruction oracle.

Only the bounded opcode runs. Entity_SetActionMode is replaced by a source-field
hook; no game, animation renderer, audio, device, or scheduler executes.
"""
import struct
from pathlib import Path
from .projectile_geometry import s32

class AnimationWaitOracle:
    start=0x80013300;end=0x800133e8
    def __init__(self,path):
        self.raw=Path(path).read_bytes();self.base=struct.unpack_from('<I',self.raw,24)[0]
    def run(self,*,mode,frames,current=0,previous=0,step=65536,flags=0,node_flags=0):
        actor=0x80100000;node=0x80101000;args=0x80102000;value=args+0x40
        gp=0x80180000;stack=0x801f0000;memory={};r=[0]*32
        def write(a,v,n=4):
            for j in range(n):memory[a+j]=(v>>(8*j))&255
        def read(a,n):return sum(memory.get(a+j,0)<<(8*j) for j in range(n))
        def allowed(a,n):return any(lo<=a and a+n<=hi for lo,hi in
            ((actor,actor+0x280),(node,node+0x2c),(args,args+0x44),(gp,gp+0x600),
             (stack-24,stack),(0x8009d2f0,0x8009d2f4)))
        for a,v,n in [(0x8009d2f0,actor,4),(gp+0x590,node,4),(gp+0x90,0x80000000,4),
            (node+8,node_flags,2),(args,value,4),(value,mode,2),(actor+0xe,mode,1),
            (actor+0xf,frames-1,1),(actor+0x14,current,4),(actor+0x18,previous,4),
            (actor+0x1c,step,4),(actor+0x98,flags,4)]:write(a,v,n)
        r[4]=args;r[28]=gp;r[29]=stack;r[31]=0xdead0000
        pc=self.start;pending=None;hook_pending=False;hook=False;set_calls=0
        for _ in range(300):
            if hook:
                if r[4]!=actor or r[5]!=mode:raise ValueError('unexpected set-mode hook arguments')
                write(actor+0xe,mode,1);write(actor+0xf,frames-1,1)
                write(actor+0x14,0);write(actor+0x18,0)
                write(actor+0x98,read(actor+0x98,4)&~0x200)
                r[2]=0;set_calls+=1;hook=False
            if pc==0xdead0000:return dict(result=r[2],node_flags=read(node+8,2),
                current=read(actor+0x14,4),previous=read(actor+0x18,4),
                flags=read(actor+0x98,4),set_calls=set_calls)
            if not self.start<=pc<self.end:raise ValueError('wait oracle fetch outside routine')
            w=struct.unpack_from('<I',self.raw,pc-self.base+2048)[0]
            op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;sa=w>>6&31;fn=w&63
            imm=((w&65535)^32768)-32768;target=None;next_hook=False
            if op==0:
                if fn==0:r[rd]=(r[rt]<<sa)&0xffffffff
                elif fn==8:target=r[rs]
                elif fn==33:r[rd]=(r[rs]+r[rt])&0xffffffff
                elif fn==35:r[rd]=(r[rs]-r[rt])&0xffffffff
                elif fn==36:r[rd]=r[rs]&r[rt]
                elif fn==43:r[rd]=int(r[rs]<r[rt])
                else:raise ValueError('unsupported wait R instruction')
            elif op==1:
                if rt!=0:raise ValueError('unsupported wait regimm')
                if s32(r[rs])<0:target=pc+4+imm*4
            elif op==2:target=0x80000000|((w&0x3ffffff)<<2)
            elif op==3:
                if 0x80000000|((w&0x3ffffff)<<2)!=0x8001a680:raise ValueError('unapproved wait call')
                r[31]=pc+8;target=pc+8;next_hook=True
            elif op in (4,5):
                if (r[rs]==r[rt])==(op==4):target=pc+4+imm*4
            elif op==9:r[rt]=(r[rs]+imm)&0xffffffff
            elif op==12:r[rt]=r[rs]&(w&65535)
            elif op==13:r[rt]=r[rs]|(w&65535)
            elif op==15:r[rt]=(w&65535)<<16
            elif op in (35,36,37):
                n={35:4,36:1,37:2}[op];a=(r[rs]+imm)&0xffffffff
                if not allowed(a,n):raise ValueError('wait read outside buffers')
                r[rt]=read(a,n)
            elif op in (41,43):
                n=2 if op==41 else 4;a=(r[rs]+imm)&0xffffffff
                if not allowed(a,n):raise ValueError('wait write outside buffers')
                write(a,r[rt],n)
            else:raise ValueError('unsupported wait opcode')
            r[0]=0;next_pc=pending if pending is not None else pc+4
            if pending is not None and hook_pending:hook=True
            pending=target;hook_pending=next_hook;pc=next_pc
        raise ValueError('wait oracle instruction limit')
