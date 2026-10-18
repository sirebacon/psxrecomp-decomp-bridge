import json,random,unittest
from pathlib import Path
from pe_weapon_sim.rotation_oracle import RotationOracle
from pe_weapon_sim.joint_reconstruction import rotation_yxz,identity,compose,reconstruct,joint_point
from pe_weapon_sim.beam_delivery import BeamOwner,BeamPlayer,deliver_beams,stiffness_lock,tick_stiffness

class JointAndBeamIntegrationTests(unittest.TestCase):
    def test_source_rotation_matches_original_instructions(self):
        oracle=RotationOracle('D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        rng=random.Random(91)
        for angles in ([0,0,0],[1024,0,0],[0,-1024,0],[0,0,2048],*[[rng.randrange(-32768,32768) for _ in range(3)] for _ in range(64)]):
            self.assertEqual(rotation_yxz(angles,oracle.table),oracle.run(angles))
    def test_hierarchy_stack_and_part_z_translation(self):
        oracle=RotationOracle('D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        model=dict(matrix_commands=[0,-1,1,-2,2],part_count=3,part_translation_z=[0,10,20])
        animation=dict(frame_count=1,root_translations=[[1,2,3]],bone_angles_by_frame=[[[0,0,0]]*3])
        pose=reconstruct(model,animation,0,oracle.table,world=identity([100,200,300]))
        self.assertEqual([m.translation for m in pose],[[101,202,303],[101,202,313],[101,202,323]])
        self.assertEqual(joint_point(pose,1,[0,-70,-100]),[101,132,213])
    def test_unbalanced_stack_is_not_silently_accepted(self):
        oracle=RotationOracle('D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        with self.assertRaises(ValueError):reconstruct(dict(matrix_commands=[-2],part_count=0),dict(frame_count=1,root_translations=[[0,0,0]],bone_angles_by_frame=[[]]),0,oracle.table)
    def test_simultaneous_beams_remove_haste_before_later_damage(self):
        player=BeamPlayer(500,500,defense=100,armor_second=10,flags=0x4000|0x100)
        owners=[BeamOwner(str(i),pending=True) for i in range(3)]
        result=deliver_beams(player,owners,lambda:99)
        self.assertEqual([e['damage'] for e in result['events']],[74,60,60])
        self.assertEqual(player.hp,306);self.assertEqual(player.stiffness_timer,9000)
        self.assertEqual([e['status'] for e in result['events']],['locked','already_locked','already_locked'])
        self.assertFalse(player.flags&0x100);self.assertFalse(player.flags&0x4000)
    def test_reaction_change_does_not_regate_same_pass(self):
        player=BeamPlayer(500,500,flags=0x4000)
        owners=[BeamOwner(str(i),True) for i in range(3)]
        def reaction(p,o):p.flags |= 0x800000
        result=deliver_beams(player,owners,lambda:99,reaction=reaction)
        self.assertEqual(result['delivered'],['0','1','2']);self.assertEqual(player.hp,230)
    def test_barrier_uses_energy_and_still_allows_stiffness(self):
        p=BeamPlayer(500,500,defense=100,armor_second=10,flags=0x4000|0x200,atb=9000,max_atk=1000,barrier_energy=10000)
        e=deliver_beams(p,[BeamOwner('beam',True)],lambda:99)['events'][0]
        self.assertEqual((p.hp,p.barrier_energy,e['damage']),(500,9520,60))
        self.assertEqual(e['status'],'locked');self.assertEqual(p.reaction_requests,[])
    def test_guard_and_armor_second_parameter(self):
        p=BeamPlayer(500,500,armor_first=99,armor_second=10,atb=1,flags=0x4000)
        e=deliver_beams(p,[BeamOwner('beam',True)],lambda:99)['events'][0]
        self.assertEqual(e['damage'],40);self.assertEqual(p.hp,460)
    def test_resist_roll_precedes_consumption_of_one_time_immunity(self):
        p=BeamPlayer(500,500,flags=0xc0|0x100,effect_flags=8)
        self.assertEqual(stiffness_lock(p,lambda:49),'resisted');self.assertEqual(p.flags,0x1c0)
        self.assertEqual(stiffness_lock(p,lambda:50),'immunity_consumed');self.assertEqual(p.flags,0x100)
        self.assertEqual(stiffness_lock(p,lambda:50),'locked');self.assertEqual(p.flags&0x1c0,0x80)
    def test_status_does_not_refresh_and_expires_in_status_units(self):
        p=BeamPlayer(500,500,flags=0x80,stiffness_timer=100,status_step=60,motion=[1,2,3],mode=17,base_mode=4)
        self.assertEqual(stiffness_lock(p,lambda:0),'already_locked');self.assertEqual(p.stiffness_timer,100)
        self.assertFalse(tick_stiffness(p,paused=True));self.assertEqual(p.stiffness_timer,100)
        self.assertFalse(tick_stiffness(p));self.assertEqual(p.stiffness_timer,40);self.assertEqual(p.motion,[0,0,0])
        self.assertTrue(tick_stiffness(p));self.assertEqual(p.mode,4);self.assertFalse(p.flags&0xc0)
    def test_zero_damage_can_still_lock_and_request_reaction(self):
        p=BeamPlayer(500,500,armor_second=1000,flags=0x4000)
        e=deliver_beams(p,[BeamOwner('beam',True)],lambda:99)['events'][0]
        self.assertEqual(p.hp,500);self.assertEqual(e['status'],'locked');self.assertEqual(p.reaction_requests,['beam'])
    def test_owner_power_uses_signed_wrap_then_u16_storage(self):
        self.assertEqual(BeamOwner('beam',scale=32768).power(),45)
        self.assertEqual(BeamOwner('beam',scale=65536).power(),90)
    def test_saved_joint_validation_artifact(self):
        path=Path(__file__).resolve().parents[3]/'findings/data/pe-joint-reconstruction-validation-2026-10-18.json'
        data=json.loads(path.read_text())
        self.assertEqual(data['retail_rotation_checks'],1000)
        self.assertEqual(data['saved_pose']['joint_count'],29);self.assertEqual(data['saved_pose']['mismatches'],[])
        self.assertEqual(len(data['boss_local_pose_samples']),168)
        self.assertFalse(data['readiness']['balance_rerun'])

    def test_world_target_contact_then_batched_damage_status(self):
        from pe_weapon_sim.beam_delivery import BeamEmitter
        p=BeamPlayer(500,500,flags=0x100,defense=100,armor_second=10)
        emitters=[BeamEmitter(BeamOwner(str(i),effect_state=1),1000,-2000,60,60) for i in range(3)]
        for tick in range(1,59):
            for emitter in emitters:self.assertFalse(emitter.update_effect(p,tick,player_x=1600,player_z=-2000,player_radius=23))
        self.assertEqual([e.owner.effect_state for e in emitters],[2,2,2])
        for emitter in emitters:self.assertTrue(emitter.update_effect(p,59,player_x=1600,player_z=-2000,player_radius=23))
        self.assertEqual(p.hp,500) # Contacts have not yet been delivered.
        result=deliver_beams(p,[e.owner for e in emitters],lambda:99)
        self.assertEqual(result['delivered'],['0','1','2']);self.assertEqual(p.hp,306)
    def test_player_weapon_radius_affects_strict_beam_contact(self):
        from pe_weapon_sim.beam_delivery import BeamEmitter
        p=BeamPlayer(500,500)
        handgun=BeamEmitter(BeamOwner('handgun'),0,0,60,60)
        rifle=BeamEmitter(BeamOwner('rifle'),0,0,60,60)
        for tick in range(1,60):
            h=handgun.update_effect(p,tick,player_x=640,player_z=0,player_radius=23)
            r=rifle.update_effect(p,tick,player_x=640,player_z=0,player_radius=63)
        self.assertFalse(h);self.assertTrue(r)
    def test_emitter_leaves_pending_until_external_delivery_and_finish(self):
        from pe_weapon_sim.beam_delivery import BeamEmitter
        p=BeamPlayer(500,500);e=BeamEmitter(BeamOwner('beam'),0,0,300,140)
        contacts=[]
        for tick in range(1,391):
            if e.update_effect(p,tick,player_x=0,player_z=0,player_radius=23):contacts.append(tick)
        self.assertEqual(contacts,[59,199,339]);self.assertTrue(e.owner.pending)
        self.assertEqual(e.owner.effect_state,2)
        e.finish_tasks();self.assertEqual(e.owner.effect_state,4);self.assertEqual(e.held,0)
