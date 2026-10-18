"""Extract beam scheduling/target bytecode and PM bindings without running game."""
import hashlib,json,re,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,sectors
from .extract_animations import ram_from_pst
from .decode_enemy_actions import flow


def main():
    inventory_path=BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json'
    inv=json.loads(inventory_path.read_text())
    room=next(r for r in inv['rooms'] if r['disc']==1 and r['map']==156)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as disc:
        blob=sectors(disc,room['lba'],room['sectors'])
    assert hashlib.sha256(blob).hexdigest()==room['sha256']
    scripts=[]
    for script in room['scripts']:
        if script['actor_type'] not in (3,4,5,6):continue
        decoded=flow(blob,script['start'],script['end'],inv['handlers'])
        scripts.append(dict(actor_type=script['actor_type'],root=script['start'],errors=decoded['errors'],
            nodes=[dict(relative_offset=n['offset']-script['start'],**n) for n in decoded['nodes']]))
    source=PROJECT/'parasite-eve-decomp'
    symbol_path=source/'configs/USA/sym.main.txt'
    symbols={int(a,16):n for n,a in re.findall(r'(\w+)\s*=\s*(0x[0-9A-Fa-f]+);',symbol_path.read_text())}
    snapshot=BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst'
    ram=ram_from_pst(snapshot)
    def word(a):return struct.unpack_from('<I',ram,a-0x80000000)[0]
    table=word(0x800942e0);record=word(table+85*4)
    callbacks={name:dict(address=hex(word(record+4*i)),symbol=symbols.get(word(record+4*i)))
        for i,name in enumerate(('init','initialize','send','start','execute','stop','unload'))}
    assert callbacks['execute']['symbol']=='FieldFx_UpdateTasks'
    assert callbacks['stop']['symbol']=='FieldFx_CloseTaskOwner'
    names=['src/main/fieldfx/geometry.c','src/main/pm/process.c','src/main/battle/context.c',
           'src/main/script/system_opcodes.c','src/main/script/value_ops.c','src/main/script/node_actions.c',
           'src/main/script/actor_opcodes.c','src/main/script/flow_opcodes.c']
    exe=(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup').read_bytes()
    exe_base=struct.unpack_from('<I',exe,24)[0]
    sqrt_code=exe[0x8005186c-exe_base+2048:0x800518a8-exe_base+2048]
    out=dict(retail_sqrt=dict(address='0x8005186c',length=len(sqrt_code),sha256=hashlib.sha256(sqrt_code).hexdigest()),scope='Offline static extraction; actor concurrency and absolute launch updates are not simulated',
        rerun_readiness=False,room_sha256=hashlib.sha256(blob).hexdigest(),
        inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
        snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
        pm_handler85=dict(table=hex(table),record=hex(record),callbacks=callbacks),scripts=scripts,
        findings=dict(mode_entry=dict(offset=5940,region_zero=0,region_nonzero=2,short_mode1='not produced by this entry'),
            sequential_projection_offsets=[6220,7088,8300],formation_modes=[0,2],
            mode0=dict(central_toward_player_to_boss=1100,lateral=1200,heading='after turn at10384'),
            mode2=dict(choice_range=[0,3],first_away=[1100,900,900],first_lateral=[0,500,-500],
                       later_toward=1100,later_lateral=[750,-750],player_samples=3),
            spacing_second=dict(offset=7752,strict_threshold=1000,z_term='cell24-cell24'),
            spacing_third=dict(offset=8964,strict_threshold=1000,compares_both_prior=True),
            trigger_writes=[6884,8032,8096,9532,9596,14700,14980,15260],
            actor_field48='selected action-record state',actor_field82='held counter (coreFlags >>24)&63',
            stop='PM slot close does not directly clear actor held bits or action record'))
    target=BRIDGE/'findings/data/pe-beam-scheduling-extract-2026-10-18.json'
    target.write_text(json.dumps(out,indent=2)+'\n');print(target)

if __name__=='__main__':main()
