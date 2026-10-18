"""Frame-ring timing capture for the isolated Eve session. Never writes guest RAM."""
import argparse
import json
import struct
import time
from .live_probe import call, SESSION


def read(addr,n,port):
    r=call(dict(cmd='read_ram',addr=hex(addr),len=n),port)
    if not r.get('ok'): raise RuntimeError(r)
    return bytes.fromhex(r['hex'])


def main():
    ap=argparse.ArgumentParser(__doc__); ap.add_argument('--port',type=int,default=4374)
    ap.add_argument('--label',required=True); ap.add_argument('--mode',choices=('idle','attack','menu','observe','switch','scan'),default='scan')
    ap.add_argument('--seconds',type=float,default=5); ap.add_argument('--load',type=int,default=-1)
    a=ap.parse_args(); port=a.port
    if a.load>=0:
        call(dict(cmd='savestate',op='load',slot=a.load),port); time.sleep(.3)
        status=call(dict(cmd='savestate_status'),port)
        if not status.get('last_ok') or status.get('pending'): raise RuntimeError(status)
    if a.mode in ('idle','observe','scan') and a.load < 0:
        # Passive measurements must leave the user's controller in control.
        call(dict(cmd='clear_input'),port)
    else:
        call(dict(cmd='set_input',buttons='0xFFFF',lx=128,ly=128),port)
    time.sleep(.1)
    entity=struct.unpack('<I',read(0x8009d254,4,port))[0]
    if not 0x80000000<=entity<0x80200000: raise ValueError('No live player entity')
    core=struct.unpack('<I',read(entity,4,port))[0]
    if not 0x80000000<=core<0x80200000: raise ValueError('No live player core')
    inv=read(0x800c0e20,140,port); slot=inv[0]
    value=struct.unpack_from('<H',inv,40+slot*2)[0]
    if not 256<=value<384: raise ValueError('No equipped record')
    record=0x800c0eac+(value-256)*32
    action=struct.unpack('<I',read(core+104,4,port))[0]
    if a.mode=='scan' and not 0x80000000<=action<0x80200000:
        raise ValueError('No live action record')
    regions=[(0x8009d1a0,128),(0x8009d250,64),(core,128),(0x800c0e20,128) if a.mode in ('menu','observe','switch') else (record,32)]
    if a.mode=='scan': regions[3]=(action,128)
    for i,(addr,n) in enumerate(regions):call(dict(cmd='set_snapshot',slot=i,addr=hex(addr)),port)
    time.sleep(.08)
    start=call(dict(cmd='history'),port)['newest']+1
    events=[]
    if a.mode=='attack':
        for _ in range(11):
            events.append(dict(history=call(dict(cmd='history'),port),input='cross'))
            call(dict(cmd='set_input',buttons='0xBFFF',lx=128,ly=128),port);time.sleep(.06)
            call(dict(cmd='set_input',buttons='0xFFFF',lx=128,ly=128),port);time.sleep(.15)
    elif a.mode=='menu':
        events.append(dict(history=call(dict(cmd='history'),port),input='triangle'))
        call(dict(cmd='press',buttons=61439,frames=6),port)
    elif a.mode=='switch':
        def press(buttons=65535, **axes):
            events.append(dict(history=call(dict(cmd='history'),port),buttons=buttons,axes=axes))
            call(dict(cmd='set_input',buttons=hex(buttons),lx=axes.get('lx',128),ly=axes.get('ly',128)),port)
            time.sleep(.035 if axes else .06)
            # Reset the emulated packet itself, not merely the override flag.
            call(dict(cmd='set_input',buttons='0xFFFF',lx=128,ly=128),port);time.sleep(.4)
        press(61439)
        press(ly=255); press(ly=255)
        press(49151)
        press(ly=255)
        press(49151)
    time.sleep(a.seconds)
    end=call(dict(cmd='history'),port)['newest']
    rows=[]
    for frame in range(start,end+1):
        parts=[]
        for addr,n in regions:
            r=call(dict(cmd='read_frame_ram',frame=frame,addr=hex(addr),len=n),port)
            if not r.get('ok'):raise RuntimeError(r)
            parts.append(bytes.fromhex(r['hex']))
        flags,ctx,b,last=parts
        row=dict(frame=frame,flags=int.from_bytes(flags[:4],'little'),entity=int.from_bytes(ctx[4:8],'little'),
                 phase=int.from_bytes(ctx[60:64],'little'),hp=int.from_bytes(b[12:14],'little'),
                 gauge=int.from_bytes(b[16:18],'little'),stat22=int.from_bytes(b[34:36],'little'),
                 fill_rate=int.from_bytes(b[36:38],'little'),state_flags=int.from_bytes(b[76:80],'little'),
                 action_ptr=int.from_bytes(b[104:108],'little'),extra_hex=last.hex())
        if a.mode=='scan':
            row.update(ammo=int.from_bytes(last[12:16],'little') & 0x3FF,
                       ammo_source='active_action', sampled_action_ptr=action,
                       action_sample_valid=row['action_ptr']==action)
        elif a.mode not in ('menu','observe','switch'):
            row.update(weapon=last[4],ammo=int.from_bytes(last[10:12],'little'),ammo_source='inventory')
        else: row['weapon_slot']=last[0]
        rows.append(row)
    path=SESSION/(a.label+'.json')
    path.write_text(json.dumps(dict(label=a.label,mode=a.mode,entity=hex(entity),core=hex(core),
        record=hex(record),regions=regions,events=events,start=start,end=end,rows=rows),indent=1),encoding='utf-8')
    print(json.dumps(dict(path=str(path),frames=len(rows),first=rows[0],last=rows[-1]),indent=1))
    print(call(dict(cmd='screenshot_file',path=str(SESSION/(a.label+'.png'))),port))


if __name__=='__main__':main()
