import json,random,unittest
from pathlib import Path
from pe_weapon_sim.beam_launch_timing import AnimationClock,AnimationWait,parent_animation_finish,turn_step,formation_launch,target_yaw_from_position,replay_helper_lifetime
from pe_weapon_sim.pm_pass_oracle import PmPassOracle
from pe_weapon_sim.extract_enemy_scripts import PROJECT,BRIDGE,sectors
from pe_weapon_sim.tests.test_beam_scheduling import source_nodes
from pe_weapon_sim.tests.test_beam_combat import player
from pe_weapon_sim.tests.test_source_combat import config,foe,Fixed
from pe_weapon_sim.script_decisions import probe
from pe_weapon_sim.decode_enemy_actions import flow
from pe_weapon_sim import engine,rules
from pe_weapon_sim.decomp_animation import source_behavior_rules


def launch(**kw):
    values=dict(entry_update=1,targets_fixed=[(1000*65536,-6000*65536)]*3,
        current_yaw=0,target_yaw=0,scale=65536,helpers_idle=True,pm_free_slots=3)
    values.update(kw);return formation_launch(**values)

class BeamLaunchTimingTests(unittest.TestCase):
    def test_target_yaw_matches_original_ratan_routine(self):
        from pe_weapon_sim.ratan_oracle import RatanOracle,ratan_source
        oracle=RatanOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        rng=random.Random(277)
        pairs=[(0,0),(0,100),(100,0),(-100,0),(0,-100)]
        pairs += [(rng.randrange(-10000000,10000000),rng.randrange(-10000000,10000000)) for _ in range(1000)]
        for z,x in pairs:self.assertEqual(ratan_source(z,x,oracle.table),oracle.run(z,x))
        self.assertEqual(target_yaw_from_position((0,0),(0,65536)),2048)
        result=launch(target_yaw=None,boss_position=(0,-6000*65536))
        self.assertEqual(result['target_yaw'],3072)
        self.assertEqual(result['trigger_update'],8)
        with self.assertRaises(ValueError):target_yaw_from_position((0,0),(0,0))

    def test_retail_pm_pass_order_and_freeze(self):
        oracle=PmPassOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        for name,slots in [('primary',list(range(11))),('secondary',list(range(11,22)))]:
            calls=oracle.run(name,0x82)
            self.assertEqual([arg for call,arg in calls if call=='draw'],slots)
            self.assertEqual([arg for call,arg in calls if call=='execute'],slots)
            self.assertEqual(oracle.run(name,2),[])
            calls=oracle.run(name,0x86)
            self.assertFalse(any(call=='execute' for call,arg in calls))
        calls=oracle.run('primary',0x182,[84,85,114,115,130,70,129,0,191,90,100])
        self.assertEqual([arg for call,arg in calls if call=='execute'],[1,2,9,10])
        self.assertFalse(any(call=='execute' for call,arg in oracle.run('secondary',0x182)))
    def test_spawn_insertion_proves_parent_before_reverse_helpers(self):
        inv=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())
        room=next(r for r in inv['rooms'] if r['disc']==1 and r['map']==156)
        with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
        script=next(s for s in room['scripts'] if s['actor_type']==7)
        nodes=flow(blob,script['start'],script['end'],inv['handlers'])['nodes']
        spawns=[]
        for n in nodes:
            if 5052<=n['offset']-script['start']<=5172:
                spawns.append(n['args'][1 if n['handler']=='Script_DispatchScriptCmd' else 0]['value'])
        self.assertEqual(spawns,[4,5,6,3])
        order=[7]
        for actor in spawns:order.insert(1,actor)
        self.assertEqual(order,[7,3,6,5,4])
    def test_polygon_checks_do_not_yield_before_trigger_writes(self):
        base,nodes=source_nodes();geom=json.loads((BRIDGE/'findings/data/pe-projectile-geometry-2026-10-18.json').read_text())
        cells={}
        for i in range(3):cells[4,21+2*i]=1000*65536;cells[4,22+2*i]=-6000*65536
        result=probe(nodes,base+14436,base+15412,base=base,cells=cells,limit=100,
            polygon=geom['floor_polygons'][0]['vertices_integer'])
        self.assertEqual(result['status'],'exit')
        self.assertEqual([result['cells'][f'4:{i}'] for i in (18,19,20)],[1,1,1])
        self.assertEqual(result['cells']['4:21'],1000)
    def test_turn_reaches_target_in_last_call_without_extra_wait(self):
        self.assertEqual(launch(current_yaw=0,target_yaw=512)['trigger_update'],4)
        self.assertEqual(launch(current_yaw=4095,target_yaw=0)['trigger_update'],1)
        self.assertEqual(launch(current_yaw=0,target_yaw=4095)['trigger_update'],1)
        for a,b in [(0,2048),(2048,0),(1200,3100),(3900,100)]:
            value=a;count=0
            while True:
                count+=1;value=turn_step(value,b)
                if value==b:break
                self.assertLess(count,40)
            self.assertEqual(launch(current_yaw=a,target_yaw=b)['turn_calls'],count)
    def test_wait_predicates_match_original_instructions(self):
        from pe_weapon_sim.animation_wait_oracle import AnimationWaitOracle
        oracle=AnimationWaitOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup')
        for frames in (1,42,45):
            for step in (-65536,0,65536):
                for current,previous in ((0,0),(65536,0),(0,65536)):
                    for started in (False,True):
                        actor=AnimationClock({10:frames},step=step,mode=10,current=current,previous=previous,flags=0x100)
                        wait=AnimationWait(10,started=started)
                        expected=wait.resume(actor)
                        actual=oracle.run(mode=10,frames=frames,current=current,previous=previous,
                            step=step,flags=0x100,node_flags=0x20 if started else 0)
                        self.assertEqual(bool(actual['result']),expected)
                        self.assertEqual(actual['current'],actor.current)
                        self.assertEqual(actual['flags'],actor.flags)
                        self.assertEqual(actual['set_calls'],0 if started else 1)

    def test_parent_animation_waits_resume_after_42_and_45_advances(self):
        self.assertEqual(parent_animation_finish(10,{2:48,10:42,11:45}),97)
        actor=AnimationClock({2:48,10:42});wait=AnimationWait(10)
        self.assertFalse(wait.resume(actor))
        for _ in range(41):actor.advance();self.assertFalse(wait.resume(actor))
        actor.advance();self.assertTrue(wait.resume(actor))
    def test_fractional_wrap_discards_remainder_like_source(self):
        actor=AnimationClock({2:3},step=98304,current=2*65536,previous=65536)
        actor.advance();self.assertEqual(actor.current,0)
        self.assertEqual(actor.previous,2*65536)
        self.assertTrue(actor.flags&8)
    def test_animation_pause_does_not_advance_wait(self):
        actor=AnimationClock({2:48,10:42});wait=AnimationWait(10)
        wait.resume(actor);actor.flags |= 0x100
        for _ in range(100):actor.advance();self.assertFalse(wait.resume(actor))
        actor.flags &= ~0x100
        for _ in range(42):actor.advance()
        self.assertTrue(wait.resume(actor))
    def test_source_timeline_uses_helper_scan_order_and_same_tick_pm_start(self):
        result=launch(entry_update=8,current_yaw=0,target_yaw=256)
        self.assertEqual(result['trigger_update'],9)
        self.assertEqual(result['parent_wait_finished'],96)
        self.assertEqual([s['owner'] for s in result['linked_beams']],['helper6','helper5','helper4'])
        self.assertEqual([s['start_update'] for s in result['linked_beams']],[8]*3)
        self.assertEqual(result['events'][0]['earliest_delivery'],68)
    def test_full_combat_uses_generated_launch_times_and_owner_order(self):
        result=launch(entry_update=5)
        fight=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),
            time_cap=14,source_options=dict(hp=500,enemy_defaults=dict(charge_step=0),
            beam_formation=dict(entry_update=5,targets_fixed=[(1000*65536,-6000*65536)]*3,
                current_yaw=0,target_yaw=0,scale=65536,helpers_idle=True,pm_free_slots=3),
            beam_player=player(flags=0x100),trace=True))
        hits=[e for e in fight['_source_events'] if e['event']=='beam_hit']
        self.assertEqual([(e['owner'],e['update'],e['damage']) for e in hits[:3]],
            [('helper6',64,74),('helper5',64,60),('helper4',64,60)])
        cleanup=[e for e in fight['_source_events'] if e['event']=='beam_cleanup']
        self.assertEqual([e['update'] for e in cleanup],[395]*3)
        self.assertEqual(fight['ammo_balance'],0)
        self.assertEqual(fight['_beam_launch_timing']['trigger_update'],5)
    def test_outside_polygon_no_launch_and_no_parent_animation_wait(self):
        result=launch(targets_fixed=[(0,0)]*3)
        self.assertEqual(result['accepted'],[False]*3)
        self.assertEqual(result['linked_beams'],[])
        self.assertEqual(result['parent_wait_finished'],1)
    def test_helper_action_and_effect_lifetimes_replay_to_release(self):
        for slot in (0,1,2):
            events=replay_helper_lifetime(slot)
            self.assertEqual(next(e['update'] for e in events if e['event']=='controller_spawn'),47)
            self.assertEqual(next(e['update'] for e in events if e['event']=='contact'),59)
            self.assertEqual(next(e['update'] for e in events if e['event']=='delivery'),60)
            self.assertEqual(next(e['update'] for e in events if e['event']=='effect_release'),391)
            self.assertEqual(events[-1]['update'],393 if slot==2 else 392)

    def test_navigation_accept_can_cancel_after_integer_target_conversion(self):
        result=launch(targets_fixed=[(262078465,-298188799)]*3)
        self.assertEqual(result['accepted'],[True]*3)
        self.assertTrue(all(not e['beam_floor_valid'] for e in result['events']))
        self.assertTrue(all(e['earliest_contact'] is None for e in result['events']))
        self.assertTrue(all(e['effect_release']==55 for e in result['events']))
        from pe_weapon_sim.beam_combat import BeamCombat
        b=BeamCombat(result['linked_beams'],player(),hp=500)
        events=[]
        for _ in range(55):b.begin_update(500,lambda:99);events+=b.update_effects(1,0)
        self.assertEqual([e['event'] for e in events],['beam_cleanup']*3)

    def test_missing_pm_capacity_is_not_assumed_available(self):
        with self.assertRaises(ValueError):launch(pm_free_slots=2)

    def test_busy_helpers_are_not_assumed_available(self):
        with self.assertRaises(ValueError):launch(helpers_idle=False)

if __name__=='__main__':unittest.main()
