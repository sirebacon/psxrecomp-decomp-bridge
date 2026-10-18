"""Bounded original PM pass oracle. Only two small retail runner functions execute.

Calls are intercepted; no game functions, emulator, saves or device IO execute.
"""
import struct
from pathlib import Path
from .projectile_geometry import s32

class PmPassOracle:
    windows={'primary':(0x80069594,0x80069660),'secondary':(0x80069660,0x800696f0)}
    def __init__(self,path):
        self.raw=Path(path).read_bytes()
        if self.raw[:8]!=b'PS-X EXE':raise ValueError('not PS-X executable')
        self.base=struct.unpack_from('<I',self.raw,24)[0]
    def run(self,pass_name,flags,commands=None):
        start,end=self.windows[pass_name];r=[0]*32;pc=start;pending=None;hook=None
        sentinel=0xdead0000;stack=0x801f0000;bank=0x80100000;memory={};calls=[]
        r[29]=stack;r[31]=sentinel
        def store(a,v,n=4):
            for j in range(n):memory[a+j]=(v>>(8*j))&255
        store(0x8009d1a0,flags);store(0x800942e4,bank)
        for i,v in enumerate(commands or [130]*11):store(bank+2572*i+1,v,1)
        def read(a,n):
            if not (stack-32<=a and a+n<=stack or a in (0x8009d1a0,0x800942e4) or bank<=a<bank+11*2572):
                raise ValueError('out-of-window PM oracle read')
            return sum(memory.get(a+j,0)<<(8*j) for j in range(n))
        hooks={0x800661a4:'screen_setup',0x800661cc:'screen_reset',0x8006f8ec:'draw',0x8006f9f0:'execute'}
        for _ in range(3000):
            if hook:
                calls.append((hooks[hook],r[4]));r[2]=0;hook=None
            if pc==sentinel:return calls
            if not start<=pc<end:raise ValueError('out-of-window PM oracle fetch')
            w=struct.unpack_from('<I',self.raw,pc-self.base+2048)[0]
            op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;sa=w>>6&31;fn=w&63
            imm=(w&65535)^32768;imm-=32768;target=None;next_hook=None
            if op==0:
                if fn==0:r[rd]=(r[rt]<<sa)&0xffffffff
                elif fn==33:r[rd]=(r[rs]+r[rt])&0xffffffff
                elif fn==8:target=r[rs]
                else:raise ValueError('unsupported PM oracle R function')
            elif op==3:
                destination=0x80000000|((w&0x3ffffff)<<2)
                if destination not in hooks:raise ValueError('unapproved PM oracle call')
                r[31]=pc+8;target=pc+8;next_hook=destination
            elif op in (4,5):
                if (r[rs]==r[rt])==(op==4):target=pc+4+imm*4
            elif op==9:r[rt]=(r[rs]+imm)&0xffffffff
            elif op==10:r[rt]=int(s32(r[rs])<imm)
            elif op==11:r[rt]=int(r[rs]<(imm&0xffffffff))
            elif op==12:r[rt]=r[rs]&(w&65535)
            elif op==15:r[rt]=(w&65535)<<16
            elif op in (35,36):r[rt]=read((r[rs]+imm)&0xffffffff,4 if op==35 else 1)
            elif op==43:
                address=(r[rs]+imm)&0xffffffff
                if not stack-32<=address<=stack-4:raise ValueError('out-of-window PM oracle write')
                store(address,r[rt])
            else:raise ValueError('unsupported PM oracle opcode')
            r[0]=0;next_pc=pending if pending is not None else pc+4
            # Call arguments can be assigned in the delay slot.
            if pending is not None and hook_pending is not None:hook=hook_pending
            pending=target;hook_pending=next_hook;pc=next_pc
        raise ValueError('PM oracle instruction limit')
