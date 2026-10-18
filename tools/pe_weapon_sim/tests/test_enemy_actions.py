import struct,unittest
from pe_weapon_sim.decode_enemy_actions import flow,timing
from pe_weapon_sim.enemy_catalog import timing_profile

def op(code,*args):return struct.pack('<'+'I'*(2+len(args)),code|(len(args)<<13),0,*args)

class EnemyActionTests(unittest.TestCase):
    def test_known_nonzero_branch_does_not_invent_unreachable_target(self):
        handlers=['Script_JumpIfZero','Entity_MarkCurrentNodeFree','Script_RunEntityCommand']
        blob=op(0,1,12)+op(1)+op(2,0,0)+op(1)
        graph=flow(blob,0,len(blob),handlers)
        self.assertEqual([n['offset'] for n in graph['nodes']],[0,16])
    def test_jump_uses_actor_relative_halfwords(self):
        handlers=['Script_JumpToEntityOffset','Entity_MarkCurrentNodeFree']
        blob=op(0,10)+b'12345678'+op(1)
        graph=flow(blob,0,len(blob),handlers)
        self.assertEqual([n['offset'] for n in graph['nodes']],[0,20])
        self.assertFalse(graph['errors'])
    def test_child_entry_is_reachable_without_fallthrough_after_free(self):
        handlers=['Script_SpawnChildNode','Entity_MarkCurrentNodeFree']
        blob=op(0,10)+op(1)+op(1)
        graph=flow(blob,0,len(blob),handlers)
        self.assertEqual([n['offset'] for n in graph['nodes']],[0,12,20])
    def test_fractional_steps_and_strict_hit_crossing(self):
        t=timing(42,30,131072,98304,20)
        self.assertEqual((t['windup'],t['recovery']),(35,6))
        self.assertEqual(t['hit_exit_update'],14)
        # Direct fixed-point stepping checks the strict whole-frame predicate.
        frame=0;hit=None
        for tick in range(1,21):
            previous=frame;frame+=98304
            if 20<(frame>>16) and 20>=(previous>>16):hit=tick
        self.assertEqual(hit,14)
    def test_wrap_hit_or_nonpositive_steps_are_not_guessed(self):
        with self.assertRaises(ValueError):timing(10,10,65536,0,5)
        with self.assertRaises(ValueError):timing(10,10,65536,65536,9)
        with self.assertRaises(ValueError):timing(10,30,65536,131072,28)
    def test_known_room_timing_and_unknown_identity_fallback(self):
        self.assertEqual(timing_profile(dict(loc='156',name='0x0216'),'fast'),dict(windup=35,recovery=6,reset_on_completion=True))
        self.assertEqual(timing_profile(dict(loc='99999',name='0x0216'),'slow'),{})

    def test_completion_reset_preserves_full_charge_until_action_ends(self):
        from pe_weapon_sim.source_enemy import EnemyClock,ScriptedEnemy
        clock=EnemyClock(90,charge=9000)
        enemy=ScriptedEnemy(clock,windup=2,recovery=2,reset_on_completion=True)
        enemy.tick();self.assertEqual(clock.charge,9000)
        enemy.tick();self.assertEqual(clock.charge,9000)
        self.assertTrue(enemy.tick()[0]);self.assertEqual(clock.charge,9000)
        enemy.tick();enemy.tick()
        self.assertEqual(clock.charge,0);self.assertEqual(enemy.phase,'charge')

    def test_isolated_distance_gate_obeys_strict_threshold(self):
        import json
        from pathlib import Path
        from pe_weapon_sim.script_decisions import probe
        data=json.loads((Path(__file__).resolve().parents[3]/'findings/data/pe-enemy-actions-2026-10-18.json').read_text())
        row=next(r for r in data['scripts'] if r['map']==156 and r['actor_type']==3);base=row['root']
        near=probe(row['nodes'],base+4752,base+4840,base=base,distance=1299*65536)
        far=probe(row['nodes'],base+4752,base+4840,base=base,distance=1300*65536)
        self.assertEqual(near['next_offset'],base+16264)
        self.assertEqual(far['next_offset'],base+4852)
        self.assertEqual(near['status'],'exit')
        unknown=probe(row['nodes'],base+4752,base+4840,base=base)
        self.assertIn('unknown',unknown['status'])
