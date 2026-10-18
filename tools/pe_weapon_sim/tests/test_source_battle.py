import random
import unittest
from pe_weapon_sim.source_battle import Gun,BattleSession,build_queue,burst_contains,ammo_pool
from pe_weapon_sim.decomp_animation import queued_shot_timeline
from pe_weapon_sim.engine import source_sequence


class SourceBattleTests(unittest.TestCase):
    def session(self,kind=1,capacity=30,loaded=30,reserve=0,**kw):
        return BattleSession({'a':Gun(kind,capacity,loaded)},{ammo_pool(kind):reserve},'a',gauge=9000,**kw)

    def test_ordinary_schedule_agrees_with_prior_derivation(self):
        for kind in range(1,9):
            s=self.session(kind);r=s.attack(rof=3)
            expected=queued_shot_timeline(kind,3)
            self.assertEqual([e['update'] for e in r['events'] if e['event']=='fire'],expected['fire_updates'])
            self.assertEqual(r['updates'],expected['update_calls'])

    def test_dispatch_refills_empty_without_midqueue_clip(self):
        s=self.session(capacity=3,loaded=0,reserve=2);r=s.attack()
        self.assertEqual(s.gun.loaded,1);self.assertEqual(s.reserves[0],0)
        self.assertEqual(r['updates'],25)
        self.assertEqual([e['update'] for e in r['events'] if e['event']=='ammo_transfer'],[0])

    def test_midqueue_reload_uses_clip_and_conserves_ammo(self):
        s=self.session(capacity=2,loaded=1,reserve=2);r=s.attack(rof=3)
        fires=[e['update'] for e in r['events'] if e['event']=='fire']
        self.assertEqual(len(fires),3);self.assertEqual(s.gun.loaded,0);self.assertEqual(s.reserves[0],0)
        self.assertGreater(fires[1]-fires[0],35)
        self.assertEqual(sum(e.get('amount',0) for e in r['events'] if e['event']=='ammo_transfer'),2)
        # Ending empty doesn't cause the former automatic end-of-turn refill.
        self.assertEqual(len([e for e in r['events'] if e['event']=='ammo_transfer']),1)
        begin=next(e['update'] for e in r['events'] if e['event']=='reload_start')
        end=next(e['update'] for e in r['events'] if e['event']=='reload_ready')
        self.assertEqual(end-begin,35)

    def test_no_reserve_does_not_manufacture_shots(self):
        s=self.session(capacity=2,loaded=1,reserve=0);r=s.attack(rof=5)
        self.assertEqual(len([e for e in r['events'] if e['event']=='fire']),1)
        self.assertEqual(s.gun.loaded,0)

    def test_random_queue_is_sampled_before_execution(self):
        q=build_queue('random',5,2,[1,2,3],1,random.Random(2))
        self.assertEqual(len(q),14);self.assertEqual([x['command'] for x in q],[0]*7+[1]*7)
        self.assertTrue(all(x['target'] in (1,2,3) for x in q))
        with self.assertRaises(ValueError):
            build_queue('random',15,3,[1,2,3],1,random.Random(2))

    def test_all_repeats_in_same_target_slot(self):
        s=self.session();r=s.attack(rof=3,mode='all',targets=(1,2),selected=1)
        fires=[e for e in r['events'] if e['event']=='fire']
        self.assertEqual([e['target'] for e in fires],[1,1,1,2,2,2])
        self.assertEqual(fires[1]['update']-fires[0]['update'],10)
        self.assertEqual(s.gun.loaded,24)

    def test_burst_uses_angles_and_single_round_for_multiple_targets(self):
        s=self.session();r=s.attack(mode='burst',targets=(0,1,2),selected=0,
            target_angles={0:0,1:0x400,2:0x800})
        hits=[e for e in r['events'] if e['event']=='hit']
        self.assertEqual(len(hits),1);self.assertEqual(s.gun.loaded,29)
        self.assertEqual(hits[0]['targets'],[t for t,a in {0:0,1:0x400,2:0x800}.items() if burst_contains(0,a)])
        self.assertEqual(hits[0]['update'],15) # fire14 + hitTrigger2 -1
        # The retail predicate's facing convention admits the opposite vector.
        self.assertTrue(burst_contains(0,0x800))
        self.assertTrue(burst_contains(0,0x600))
        self.assertFalse(burst_contains(0,0))

    def test_dead_target_callback_skips_queued_slot(self):
        live={0:True,1:True}
        s=self.session()
        r=s.attack(mode='all',rof=3,targets=(0,1),selected=0,
            target_alive=lambda t:live[t],on_hit=lambda e:live.update({t:False for t in e['targets']}))
        self.assertEqual([e['target'] for e in r['events'] if e['event']=='fire'],[0,1])

    def test_switch_carries_magazines_pool_and_refills_with_new_rate(self):
        guns={'a':Gun(1,10,3),'b':Gun(4,10,7)}
        s=BattleSession(guns,{0:20},'a',gauge=9000)
        s.switch('b',menu_updates=10)
        self.assertEqual(s.gauge,4500+17*63)
        self.assertEqual(s.update,27)
        self.assertEqual([g.loaded for g in s.guns.values()],[3,7])
        self.assertEqual(s.reserves[0],20)
        s.switch('a',stream_updates=5)
        self.assertEqual(s.guns['b'].loaded,7)
        self.assertEqual(s.equipped,'a')

    def test_cancel_refunds_borrow_and_does_not_switch(self):
        s=BattleSession({'a':Gun(1,10,3),'b':Gun(2,10,7)},{0:0},'a',gauge=7800)
        s.switch('b',menu_updates=5,cancel=True)
        self.assertEqual((s.gauge,s.equipped),(7800,'a'))

    def test_sequence_api_and_input_not_mutated(self):
        guns={'a':Gun(1,3,0),'b':Gun(2,4,1)}
        r=source_sequence(guns,{0:5},'a',[dict(op='attack',rof=2),dict(op='switch',destination='b')])
        self.assertEqual(guns['a'].loaded,0)
        self.assertEqual(r['loaded'],{'a':1,'b':1})
        self.assertEqual(r['reserves'][0],2)

    def test_ammo_pool_mapping_and_capacity_cap(self):
        self.assertEqual([ammo_pool(k) for k in range(1,9)],[0,0,0,0,0,1,2,'club'])
        self.assertEqual(Gun(1,1200,0).capacity,999)

    def test_shared_reserve_is_used_by_each_gun_without_free_refill(self):
        s=BattleSession({'a':Gun(1,3,0),'b':Gun(4,4,0)},{0:5},'a',gauge=9000)
        s.attack(rof=2);s.switch('b');s.attack()
        self.assertEqual((s.guns['a'].loaded,s.guns['b'].loaded,s.reserves[0]),(1,1,0))

    def test_dead_initial_target_and_club_ammo(self):
        s=self.session();r=s.attack(rof=3,target_alive=lambda _:False)
        self.assertFalse(any(e['event']=='fire' for e in r['events']))
        s=self.session(kind=8,loaded=0,reserve=0);r=s.attack(rof=3)
        self.assertEqual(len([e for e in r['events'] if e['event']=='fire']),3)
        self.assertEqual(s.gun.loaded,0)
