"""Isolated original RotMatrixYXZ instruction oracle; never runs the game.

Executes only the bounded 656-byte math routine, with angle/output buffers and
retail sine data. Unsupported instructions or out-of-window fetches fail closed.
"""
import struct
from pathlib import Path
from .projectile_geometry import s32

class RotationOracle:
    start=0x80079754
    end=0x800799e4
    def __init__(self,path):
        raw=Path(path).read_bytes()
        if raw[:8]!=b'PS-X EXE':raise ValueError('not a PS-X executable')
        self.base=struct.unpack_from('<I',raw,24)[0];self.raw=raw
        self.code=raw[self.start-self.base+2048:self.end-self.base+2048]
        self.table=[struct.unpack_from('<hh',raw,0x800966ec-self.base+2048+4*i) for i in range(4096)]
    def run(self,angles):
        memory={};r=[0]*32;lo=0;pc=self.start;pending=None
        source=0x801f0000;output=source+0x100;sentinel=0xdead0000
        for i,value in enumerate(angles):
            v=value&65535;memory[source+2*i]=v&255;memory[source+2*i+1]=v>>8
        def read(addr,n):
            if source<=addr and addr+n<=source+6 or output<=addr and addr+n<=output+18:
                return sum(memory.get(addr+i,0)<<(8*i) for i in range(n))
            if 0x800966ec<=addr and addr+n<=0x8009a6ec:
                return int.from_bytes(self.raw[addr-self.base+2048:addr-self.base+2048+n],'little')
            raise ValueError('oracle read outside buffers/table '+hex(addr))
        r[4]=source;r[5]=output;r[31]=sentinel
        for steps in range(2048):
            if pc==sentinel:
                return [[s32(read(output+2*(3*i+j),2)<<16)>>16 for j in range(3)] for i in range(3)]
            if not self.start<=pc<self.end:raise ValueError('oracle fetch outside rotation routine')
            w=struct.unpack_from('<I',self.code,pc-self.start)[0];op=w>>26
            rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sa=(w>>6)&31;fn=w&63
            imm=w&65535;simm=(imm^32768)-32768;target=None
            if op==0:
                if fn==0:r[rd]=(r[rt]<<sa)&0xffffffff
                elif fn==3:r[rd]=(s32(r[rt])>>sa)&0xffffffff
                elif fn==18:r[rd]=lo
                elif fn==25:lo=(r[rs]*r[rt])&0xffffffff
                elif fn==33:r[rd]=(r[rs]+r[rt])&0xffffffff
                elif fn==35:r[rd]=(r[rs]-r[rt])&0xffffffff
                elif fn==8:target=r[rs]
                else:raise ValueError('unsupported R function '+str(fn))
            elif op==1:
                if rt not in (0,1):raise ValueError('unsupported REGIMM')
                if (s32(r[rs])<0 if rt==0 else s32(r[rs])>=0):target=(pc+4+simm*4)&0xffffffff
            elif op==2:target=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
            elif op==12:r[rt]=r[rs]&imm
            elif op==15:r[rt]=imm<<16
            elif op in (33,35):
                addr=(r[rs]+simm)&0xffffffff;value=read(addr,2 if op==33 else 4)
                r[rt]=((value^32768)-32768)&0xffffffff if op==33 else value
            elif op==41:
                addr=(r[rs]+simm)&0xffffffff
                if not output<=addr<=output+16:raise ValueError('oracle write outside output')
                memory[addr]=r[rt]&255;memory[addr+1]=(r[rt]>>8)&255
            else:raise ValueError('unsupported opcode '+str(op))
            r[0]=0;next_pc=pending if pending is not None else pc+4
            pending=target;pc=next_pc
        raise ValueError('oracle instruction limit')
