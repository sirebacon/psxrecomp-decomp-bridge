import json,struct,unittest
from pathlib import Path
from pe_weapon_sim.projectile_geometry import ContactOwner,drain_action_contacts,point_in_polygon,transform_point
from pe_weapon_sim.extract_projectile_geometry import decode_channels

class GeometryAndBeamTests(unittest.TestCase):
    def test_source_polygon_containment_and_reversed_winding(self):
        polygon=[(-10,-10),(10,-10),(10,10),(-10,10)]
        self.assertTrue(point_in_polygon(0,0,polygon))
        self.assertTrue(point_in_polygon(0,0,list(reversed(polygon))))
        self.assertFalse(point_in_polygon(20<<16,0,polygon))
        with self.assertRaises(ValueError):point_in_polygon(0,0,[])
    def test_source_transform_offset_uses_fixed12_rotation(self):
        identity=[[4096,0,0],[0,4096,0],[0,0,4096]]
        self.assertEqual(transform_point(identity,[735,-1873,-9226],[0,-70,-100]),[735,-1943,-9326])
        self.assertEqual(transform_point(identity,[0,0,0],[0,0,-100]),[0,0,-100])
    def test_transform_rejects_unimplemented_gte_saturation(self):
        with self.assertRaises(ValueError):transform_point([[32767,0,0],[0,4096,0],[0,0,4096]],[0,0,0],[32767,0,0])
    def test_byte_channel_constants_and_rotation_scale(self):
        header=bytes([0,0,2,0])+b'\0'*8
        roots=b''.join(struct.pack('<hh',1,v) for v in (10,-20,30))
        angles=b''.join(bytes([1,v,0,0]) for v in (1,128,255))
        decoded=decode_channels(header+roots+angles,0)
        self.assertEqual(decoded['root_translations'],[[10,-20,30]]*2)
        self.assertEqual(decoded['bone_angles_by_frame'],[[[16,2048,4080]]]*2)
    def test_short_variable_channels_preserve_frames(self):
        header=bytes([2,0,3,0])+b'\0'*8
        channels=[]
        for values in ((1,2,3),(-4,-5,-6),(7,8,9),(0,1024,2048),(0,0,0),(100,200,300)):
            channels.append(struct.pack('<4h',0,*values))
        decoded=decode_channels(header+b''.join(channels),0)
        self.assertEqual(decoded['root_translations'],[[1,-4,7],[2,-5,8],[3,-6,9]])
        self.assertEqual(decoded['bone_angles_by_frame'][2],[[2048,0,300]])
    def test_three_pending_beams_can_drain_in_one_pass(self):
        owners=[ContactOwner(str(i),pending=True) for i in range(3)]
        flags,hits=drain_action_contacts(0x4000,owners,lambda owner,flags:flags|0x800000)
        self.assertEqual(hits,['0','1','2'])
        self.assertFalse(any(o.pending for o in owners));self.assertFalse(flags&0x4000)
        self.assertTrue(flags&0x800000)
    def test_reaction_gate_preserves_owner_pending_but_clears_player_latch(self):
        owner=ContactOwner('beam',pending=True)
        flags,hits=drain_action_contacts(0x800000|0x4000,[owner])
        self.assertEqual(hits,[]);self.assertTrue(owner.pending);self.assertFalse(flags&0x4000)
        flags,hits=drain_action_contacts(0,[owner]);self.assertEqual(hits,[])
        _,hits=drain_action_contacts(0x4000,[owner]);self.assertEqual(hits,['beam'])
    def test_invalid_states_and_dead_owners_do_not_deliver(self):
        owners=[ContactOwner('end',True,4),ContactOwner('dead',True,2,True),ContactOwner('none',True,2,False,False)]
        _,hits=drain_action_contacts(0x4000,owners)
        self.assertEqual(hits,[]);self.assertTrue(all(o.pending for o in owners))
    def test_body_contact_immunity_flag_is_not_action_hit_gate(self):
        owner=ContactOwner('beam',True)
        _,hits=drain_action_contacts(0x1000000|0x4000,[owner]);self.assertEqual(hits,['beam'])
    def test_action_gate_blocks_pass(self):
        for gate in (0x80000,0x100000):
            _,hits=drain_action_contacts(gate|0x4000,[ContactOwner('beam',True)])
            self.assertEqual(hits,[])
    def test_asset_geometry_and_snapshot_crosschecks(self):
        root=Path(__file__).resolve().parents[3]
        data=json.loads((root/'findings/data/pe-projectile-geometry-2026-10-18.json').read_text())
        self.assertEqual([a['frame_count'] for a in data['animations']],[45,36,42,45])
        self.assertTrue(all(a['bone_count']==47 for a in data['animations']))
        self.assertEqual(data['floor_height_setters'][0]['floor_y'],-1873)
        self.assertEqual(len(data['floor_polygons'][0]['vertices_integer']),9)
        self.assertEqual(data['aya_saved_model']['cylinder_radius'],63)
        self.assertEqual(len(data['aya_disc_models']),16)
        for costume in (0,1):
            self.assertEqual([r['cylinder_radius'] for r in data['aya_disc_models'] if r['costume']==costume],[23,35,41,63,37,53,23,27])
        self.assertEqual([o['trigger_cell'] for o in data['linked_beam_owners']],[18,19,20])
