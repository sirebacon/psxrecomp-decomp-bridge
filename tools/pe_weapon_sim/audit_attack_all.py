"""Check retail US instruction signatures for Attack All's reload-counter path.

Read-only binary audit, not execution/emulation. Exact addresses are for SLUS00662.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def audit(path):
    data=Path(path).read_bytes()
    if data[:8]!=b'PS-X EXE': raise ValueError('PS-X EXE required')
    base=struct.unpack_from('<I',data,24)[0]
    def word(address): return struct.unpack_from('<I',data,0x800+address-base)[0]
    expected={
        0x80023288:0x8C820068, # lw v0,Combatant.action(a0)
        0x80023290:0x8C420010, # lw v0,BattleAction.turnWord(v0)
        0x80023294:0x08008D6A, # j 0x800235A8, shared counter-write/fire tail
        0x80023298:0x3042000F, # delay slot: andi v0,v0,15
        0x800235A8:0xA382046C, # sb v0,g_BattleRemainingActions(gp)
        0x800235AC:0x0C008C02, # jal Battle_FinalizeAttackResult
        0x800235BC:0x0C01462A, # alternate branch: jal CommitAmmoAndUpdate
        0x800235C4:0x10400010, # zero transfer -> idle branch
        0x800235D4:0x0C0069A0, # nonzero -> Entity_SetActionMode
        0x800235D8:0x2405000C, # delay slot: a1 = 12 (reload pose)
        0x80022184:0x94A2001A, # caller reload branch reads animPrev.integer
        0x8002218C:0x1462001A, # waits until lastFrame==animPrev.integer
        0x800221EC:0x90450014, # target-angle aim mode selected from core
        0x800221F0:0x0C0069A0, # then Entity_SetActionMode, reentering aim
    }
    checks=[dict(address=hex(a),expected=hex(v),actual=hex(word(a)),match=word(a)==v)
            for a,v in expected.items()]
    if not all(c['match'] for c in checks): raise ValueError('retail instruction signature mismatch')
    return dict(executable=str(Path(path).resolve()),sha256=hashlib.sha256(data).hexdigest(),
        text_base=hex(base),checks=checks,
        conclusion='Retail ready path writes turnWord & 15 into remaining-actions before firing; '
            'successful alternate reload enters mode12. Decomp caller waits for mode12 end, '
            'restarts aim and re-enters this ready path. This supports reset semantics, '
            'without claiming a live execution trace or full battle parity.')


def main():
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('exe');ap.add_argument('--out',required=True)
    a=ap.parse_args();result=audit(a.exe)
    Path(a.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f"Verified {len(result['checks'])} retail instruction signatures.")


if __name__=='__main__': main()
