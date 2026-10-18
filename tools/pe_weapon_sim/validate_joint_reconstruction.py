"""Offline joint reconstruction audit and isolated retail math checks. No fights."""
import hashlib,json,random,struct
from pathlib import Path
from .extract_enemy_scripts import PROJECT,BRIDGE,word
from .extract_animations import ram_from_pst
from .extract_projectile_geometry import model_geometry,decode_channels
from .joint_reconstruction import Matrix,reconstruct,joint_point,rotation_yxz,identity
from .rotation_oracle import RotationOracle
from .beam_delivery import BeamOwner,BeamPlayer,BeamEmitter,deliver_beams,tick_stiffness

def validate(output):
    exe=PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup';oracle=RotationOracle(exe)
    rng=random.Random(52)
    for _ in range(1000):
        angles=[rng.randrange(-32768,32768) for _ in range(3)]
        if rotation_yxz(angles,oracle.table)!=oracle.run(angles):raise AssertionError('retail rotation mismatch')
    snapshot=BRIDGE/'findings/live-timing-session/saves/scph1001/state_80072534_disc2_slot09.pst'
    ram=ram_from_pst(snapshot);p=word(ram,0x9d254)-0x80000000;o=p+0x1b4
    model=model_geometry(ram,word(ram,o)-0x80000000)
    clip=decode_channels(ram,word(ram,p+0x1b0)-0x80000000)
    def matrix(at):
        return Matrix([list(struct.unpack_from('<3h',ram,at+i*6)) for i in range(3)],list(struct.unpack_from('<3i',ram,at+20)))
    world=matrix(o+0x34);ptr=word(ram,o+0x84)-0x80000000
    saved=[matrix(ptr+i*32) for i in range(model['part_count'])];overrides=[]
    for i in range(2):
        at=o+0xa0+i*8
        overrides.append(dict(index=ram[at+6],flags=ram[at+7],angles=list(struct.unpack_from('<3h',ram,at))))
    previous=word(ram,p+0x18)>>16
    actual=reconstruct(model,clip,previous,oracle.table,world=world,overrides=overrides)
    mismatches=[i for i,(a,b) in enumerate(zip(actual,saved)) if a!=b]
    if mismatches:raise AssertionError('saved-pose joint mismatch '+str(mismatches))
    geometry_path=BRIDGE/'findings/data/pe-projectile-geometry-2026-10-18.json';geometry=json.loads(geometry_path.read_text())
    boss_model=geometry['models'][0];samples=[]
    for animation in geometry['animations']:
        for frame in range(animation['frame_count']):
            matrices=reconstruct(boss_model,animation,frame,oracle.table)
            samples.append(dict(mode=animation['mode'],frame=frame,
                orb_local_actor_point=joint_point(matrices,7,geometry['orb_joint_offset']),
                beam_local_actor_point=joint_point(matrices,31,geometry['beam_joint_offset'])))
    sources=('src/main/psyq/libgte/fgo_02.c','src/main/anim/bone_rotations.c','src/main/render/object.c','src/main/entity/frame_update.c')
    fixture_player=BeamPlayer(500,500,defense=100,armor_second=10,flags=0x100,status_step=60)
    fixture_emitters=[BeamEmitter(BeamOwner(str(i),effect_state=1),1000,-2000,60,60) for i in range(3)]
    for update in range(1,60):
        for emitter in fixture_emitters:emitter.update_effect(fixture_player,update,player_x=1600,player_z=-2000,player_radius=23)
    fixture_result=deliver_beams(fixture_player,[e.owner for e in fixture_emitters],lambda:99)
    if [e['damage'] for e in fixture_result['events']]!=[74,60,60] or fixture_player.hp!=306:raise AssertionError('beam sequence fixture failed')
    for _ in range(150):expired=tick_stiffness(fixture_player)
    if not expired or fixture_player.flags&0xc0:raise AssertionError('status fixture did not expire')
    core=word(ram,p)-0x80000000
    result=dict(beam_component_fixture=dict(scope='controlled geometry/status checks, not encounter simulation',player_hp_after=fixture_player.hp,damage_events=fixture_result['events'],status_step_input=60,status_ticks_until_clear=150),saved_aya_status_step3c=struct.unpack_from('<H',ram,core+0x3c)[0],model_sha256={name:hashlib.sha256((BRIDGE/'tools/pe_weapon_sim'/name).read_bytes()).hexdigest() for name in ('joint_reconstruction.py','rotation_oracle.py','beam_delivery.py','projectile_geometry.py')},scope='Rotation oracle and source-pose checks only; no balance rerun or actual launch-frame scheduling',
        retail_rotation_checks=1000,retail_function_range=[hex(oracle.start),hex(oracle.end)],
        retail_function_sha256=hashlib.sha256(oracle.code).hexdigest(),exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
        source_sha256={n:hashlib.sha256((PROJECT/'parasite-eve-decomp'/n).read_bytes()).hexdigest() for n in sources},
        snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),geometry_sha256=hashlib.sha256(geometry_path.read_bytes()).hexdigest(),
        saved_pose=dict(actor=hex(p+0x80000000),rendered_frame=previous,next_animation_frame=word(ram,p+20)>>16,
            joint_count=len(actual),mismatches=mismatches,world_matrix=dict(rotation=world.rotation,translation=world.translation),overrides=overrides),
        boss_local_pose_samples=samples,
        readiness=dict(balance_rerun=False,remaining=['actual actor pose/heading and cached render-frame mapping at effect launch','beam target strategies and actor/process phase coupling','cosmetic pool completion','full combat reaction/cure integration and incoming-status hook ordering']))
    Path(output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'Validated 1000 original rotation cases, {len(actual)} saved joint matrices, {len(samples)} boss pose samples. No balance runs.')
    return result
if __name__=='__main__':
    validate(BRIDGE/'findings/data/pe-joint-reconstruction-validation-2026-10-18.json')
