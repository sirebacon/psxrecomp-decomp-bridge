"""Original bounded ratan2 oracle; no game execution, calls or writes."""
import struct
from pathlib import Path
from .projectile_geometry import s32
from .beam_scheduling import cdiv

class RatanOracle:
    start=0x80079fb4;end=0x8007a128
    def __init__(self,path):
        self.raw=Path(path).read_bytes();self.base=struct.unpack_from('<I',self.raw,24)[0]
        self.table=struct.unpack_from('<1025h',self.raw,0x8009a6ec-self.base+2048)
    def run(self,y,x):
        r=[0]*32;r[4]=y&0xffffffff;r[5]=x&0xffffffff;r[31]=0xdead0000
        pc=self.start;pending=None;lo=0
        for _ in range(300):
            if pc==0xdead0000:return s32(r[2])
            if not self.start<=pc<self.end:raise ValueError('ratan oracle fetch outside routine')
            w=struct.unpack_from('<I',self.raw,pc-self.base+2048)[0]
            op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;sa=w>>6&31;fn=w&63
            imm=((w&65535)^32768)-32768;target=None
            if op==0:
                if fn==0:r[rd]=(r[rt]<<sa)&0xffffffff
                elif fn==3:r[rd]=(s32(r[rt])>>sa)&0xffffffff
                elif fn==8:target=r[rs]
                elif fn==18:r[rd]=lo
                elif fn==26:lo=cdiv(s32(r[rs]),s32(r[rt]))&0xffffffff
                elif fn==33:r[rd]=(r[rs]+r[rt])&0xffffffff
                elif fn==35:r[rd]=(r[rs]-r[rt])&0xffffffff
                elif fn==36:r[rd]=r[rs]&r[rt]
                elif fn==42:r[rd]=int(s32(r[rs])<s32(r[rt]))
                else:raise ValueError('unsupported ratan instruction')
            elif op==1:
                if rt!=1:raise ValueError('unsupported ratan regimm')
                if s32(r[rs])>=0:target=pc+4+imm*4
            elif op==2:target=0x80000000|((w&0x3ffffff)<<2)
            elif op in (4,5):
                if (r[rs]==r[rt])==(op==4):target=pc+4+imm*4
            elif op==9:r[rt]=(r[rs]+imm)&0xffffffff
            elif op==15:r[rt]=(w&65535)<<16
            elif op==33:
                address=(r[rs]+imm)&0xffffffff
                if not 0x8009a6ec<=address<0x8009a6ec+2050 or address&1:raise ValueError('ratan read outside table')
                r[rt]=self.table[(address-0x8009a6ec)//2]&0xffffffff
            else:raise ValueError('unsupported ratan opcode')
            r[0]=0;next_pc=pending if pending is not None else pc+4;pending=target;pc=next_pc
        raise ValueError('ratan oracle instruction limit')


def ratan_source(y,x,table):
    if not -2147483648<y<2147483648 or not -2147483648<x<2147483648:raise ValueError('unsupported atan overflow')
    negative_x=x<0;negative_y=y<0;x=abs(x);y=abs(y)
    if x==y==0:return 0
    if y<x:
        ratio=cdiv(y,x>>10) if y&0x7fe00000 else cdiv(s32(y<<10),x)
        angle=table[ratio]
    else:
        ratio=cdiv(x,y>>10) if x&0x7fe00000 else cdiv(s32(x<<10),y)
        angle=1024-table[ratio]
    if negative_x:angle=2048-angle
    if negative_y:angle=-angle
    return angle
