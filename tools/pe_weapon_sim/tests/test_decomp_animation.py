import tempfile
from pathlib import Path
import unittest
from pe_weapon_sim.decomp_animation import assets, queued_shot_timeline, source_rules
from pe_weapon_sim.extract_animations import ram_from_pst
from pe_weapon_sim import engine, rules


class DecompAnimationTests(unittest.TestCase):
    def test_all_banks_and_delay_bytes(self):
        d=assets()
        self.assertEqual(len(d['weapon_banks']),16)
        self.assertEqual(d['battle_animation_rows'][4],[10,7,0,10,4])
        from pe_weapon_sim.data import ANIM
        self.assertTrue(all(tuple(d['battle_animation_rows'][k])==v for k,v in ANIM.items()))
        loaded={a['mode']:a['header_hex'] for a in d['actions'] if a['available']}
        bank=next(b for b in d['weapon_banks'] if b['costume']==0 and b['kind']==1)
        self.assertTrue(all(loaded[a['mode']]==a['header_hex'] for a in bank['actions']))
        self.assertEqual(queued_shot_timeline(3,1)['follow_frames'],3)
        self.assertEqual(queued_shot_timeline(2,1)['follow_frames'],30)

    def test_single_handgun_boundary_order(self):
        # 14 advances reach aim frame14, fire on call14; previous frame9
        # is visible to battle logic on call24 after follow-through wraps.
        t=queued_shot_timeline(1,1)
        self.assertEqual(t['fire_updates'],[14])
        self.assertEqual(t['queue_finish_update'],24)
        self.assertEqual(t['update_calls'],25)

    def test_queued_handgun_and_retarget_hold(self):
        self.assertEqual(queued_shot_timeline(1,3)['fire_updates'],[14,30,46])
        self.assertEqual(queued_shot_timeline(1,3,target_changes=(1,))['fire_updates'],[14,40,56])
        self.assertEqual(queued_shot_timeline(1,3)['update_calls'],57)

    def test_rifle_holds_and_costume_difference(self):
        self.assertEqual(queued_shot_timeline(4,1)['fire_updates'],[31])
        self.assertEqual(queued_shot_timeline(5,1,costume=1)['fire_updates'][0] -
                         queued_shot_timeline(5,1,costume=0)['fire_updates'][0],15)

    def test_explicit_engine_profile(self):
        r=source_rules(rules.CURRENT)
        self.assertNotEqual(r['name'],rules.CURRENT['name'])
        self.assertAlmostEqual(engine.commit_seconds(1,3,r),57/(59.9/2))
        self.assertAlmostEqual(engine.rule_fill_seconds(79,2,False,r),143/(59.9/2))

    def test_bad_pst_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.pst';p.write_bytes(b'bad')
            with self.assertRaises(ValueError): ram_from_pst(p)
