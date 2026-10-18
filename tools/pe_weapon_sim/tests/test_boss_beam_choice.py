import json,random,unittest
from pe_weapon_sim.boss_beam_choice import chooser_gate,choose_action,source_distance,first_choice_update,boss_choice_to_launch,room_inputs
from pe_weapon_sim.tests.test_beam_scheduling import source_nodes
from pe_weapon_sim.script_decisions import probe
from pe_weapon_sim.extract_enemy_scripts import PROJECT,BRIDGE,sectors
from pe_weapon_sim.decode_enemy_actions import flow


def options(**kw):
    result=dict(start_update=1,boss_position=(0,-1873*65536,-6000*65536),
        player_position=(3000*65536,-1873*65536,-6000*65536),current_yaw=0,
        script_bits=0,committed_action=0,completed_beam=0,initial_charge=8990,
        charge_step=70,ready_latch=0,path_index=1,player_flags=0,triggers=[0,0,0],
        scale=65536,pm_free_slots=3,helpers_ready=True,enemy_core_flags=0,actor_flags=0)
    result.update(kw);return result

class BossBeamChoiceTests(unittest.TestCase):
    def test_distance_is_three_axis_manhattan(self):
        self.assertEqual(source_distance((0,0,0),(1000*65536,700*65536,1000*65536)),2700*65536)
    def test_action_choices_match_fresh_bytecode_at_boundaries(self):
        base,nodes=source_nodes()
        mapping={16264:'melee',15476:'orb',5592:'beams'}
        for distance in (1299,1300,1700,1701,2000,2001):
            for triggers in ([0,0,0],[1,0,0],[0,1,0],[0,0,1]):
                for flags in (0,0x40,0x80,0xc0,0x100):
                    for choice in (0,1,2):
                        cells={(4,18+i):v for i,v in enumerate(triggers)}
                        got=probe(nodes,base+4752,base+5592,base=base,cells=cells,distance=distance*65536,
                            player_fields={21:(flags>>6)&3},random_values={base+5224:choice},limit=100)
                        self.assertEqual(got['status'],'exit')
                        expected=choose_action(distance=distance*65536,triggers=triggers,player_flags=flags,random_choice=choice)
                        self.assertEqual(mapping[got['next_offset']-base],expected['action'])
                        self.assertEqual(base+5224 in got['trace'],expected['random_consumed'])
    def test_outer_gate_priority_matches_raw_bit_tests_and_branches(self):
        base,nodes=source_nodes();rng=random.Random(777)
        mapping={3388:'wait',4248:'move',4472:'decide'}
        for _ in range(500):
            bits=rng.randrange(128);committed=rng.randrange(2);completed=rng.randrange(2)
            ready=rng.randrange(2);path=rng.randrange(2);distance=rng.choice([1199,1200,1701,2000,2001])*65536
            cells={(1,22):bits,(1,3):committed,(1,44):completed,(1,35):ready,(1,1):path}
            got=probe(nodes,base+3412,base+4248,base=base,cells=cells,distance=distance,
                stop_offsets=[base+3388,base+4248,base+4472],limit=100)
            self.assertEqual(got['status'],'boundary')
            expected=chooser_gate(script_bits=bits,committed_action=committed,completed_beam=completed,
                ready_latch=ready,path_result=path,distance=distance)
            self.assertEqual(mapping[got['next_offset']-base],expected['outcome'])
            self.assertEqual(got['cells']['1:22'],expected['script_bits'])
            self.assertEqual(got['cells']['1:44'],expected['completed_beam'])
    def test_charge_poll_runs_after_chooser_in_reverse_child_order(self):
        inv=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())
        room=next(r for r in inv['rooms'] if r['disc']==1 and r['map']==156)
        with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
        script=next(s for s in room['scripts'] if s['actor_type']==3)
        spawned=[n['args'][0]['value']*2 for n in flow(blob,script['start'],script['end'],inv['handlers'])['nodes']
            if n['handler']=='Script_SpawnChildNode' and 1888<=n['offset']-script['start']<=1980]
        self.assertEqual(list(reversed(spawned)),[2080,17792,3388,20816,3252,3156])
        result=first_choice_update(start_update=1,initial_charge=8990,charge_step=70,ready_latch=0,
            script_bits=0,committed_action=0,completed_beam=0,path_result=0,distance=3000*65536)
        self.assertEqual(result['update'],3)
        self.assertEqual([r['ready_latch'] for r in result['trace']],[0,0,1])
    def test_source_slow_changes_ready_time_and_incapacity_is_rejected(self):
        common=dict(start_update=1,initial_charge=0,charge_step=70,ready_latch=0,script_bits=0,
            committed_action=0,completed_beam=0,path_result=0,distance=3000*65536)
        self.assertEqual(first_choice_update(**common)['update'],131)
        self.assertEqual(first_choice_update(**common,enemy_flags=1)['update'],217)
        with self.assertRaises(ValueError):first_choice_update(**common,actor_flags=0x1000)
        with self.assertRaises(ValueError):first_choice_update(**common,enemy_flags=0x1800)

    def test_sticky_ready_latch_and_event_gate_can_bypass_current_charge(self):
        common=dict(start_update=7,initial_charge=0,charge_step=70,script_bits=0,committed_action=0,
            completed_beam=0,path_result=0,distance=3000*65536)
        self.assertEqual(first_choice_update(ready_latch=1,**common)['update'],7)
        common['script_bits']=1
        self.assertEqual(first_choice_update(ready_latch=0,**common)['update'],7)
    def test_static_world_choice_produces_mode0_launch_without_entry_timestamp(self):
        result=boss_choice_to_launch(**options())
        self.assertEqual((result['action'],result['mode']),('beams',0))
        self.assertEqual(result['chooser_update'],3)
        self.assertEqual(result['decision_update'],10)
        self.assertEqual(result['formation_entry_update'],11)
        self.assertEqual(result['launch_timing']['trigger_update'],11)
        self.assertEqual([p['owner'] for p in result['linked_beams']],['helper6','helper5','helper4'])
    def test_movement_gate_is_reported_without_inventing_travel_delay(self):
        result=boss_choice_to_launch(**options(player_position=(2500*65536,-1873*65536,-6000*65536),ready_latch=1))
        self.assertEqual(result['action'],'move');self.assertEqual(result['linked_beams'],[])
    def test_region_selects_mode2_and_requires_separate_layout_random(self):
        args=options(player_position=(2500*65536,-1873*65536,-6000*65536),ready_latch=1,script_bits=4)
        with self.assertRaises(ValueError):boss_choice_to_launch(**args)
        result=boss_choice_to_launch(**args,formation_choice=2)
        self.assertEqual(result['mode'],2);self.assertTrue(result['formation_random_consumed'])
        self.assertFalse(result['action_random_consumed'])
    def test_full_engine_joins_decision_to_consistent_static_launch(self):
        from pe_weapon_sim import engine,rules
        from pe_weapon_sim.decomp_animation import source_behavior_rules
        from pe_weapon_sim.tests.test_source_combat import config,foe,Fixed
        from pe_weapon_sim.tests.test_beam_combat import player
        decision=boss_choice_to_launch(**options())
        result=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),
            time_cap=15,source_options=dict(hp=500,enemy_defaults=dict(charge_step=0),
            boss_beam_choice=options(),beam_player={**player(),'x':3000,'z':-6000},trace=True))
        self.assertEqual(result['_boss_beam_choice']['chooser_update'],3)
        self.assertEqual(result['_beam_launch_timing']['trigger_update'],11)
        hits=[e for e in result['_source_events'] if e['event']=='beam_hit']
        self.assertEqual(hits,[]) # Source targets do not blanket-hit a stationary Aya.
        self.assertEqual(result['_beam_launch_timing']['events'][0]['earliest_delivery'],70)
        self.assertEqual(result['beam_cleanups'],3)
        self.assertEqual(result['ammo_balance'],0)

    def test_integration_rejects_conflicting_player_position(self):
        from pe_weapon_sim import engine,rules
        from pe_weapon_sim.decomp_animation import source_behavior_rules
        from pe_weapon_sim.tests.test_source_combat import config,foe,Fixed
        from pe_weapon_sim.tests.test_beam_combat import player
        with self.assertRaisesRegex(ValueError,'positions must match'):
            engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
                dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),
                time_cap=1,source_options=dict(hp=500,enemy_defaults=dict(charge_step=0),
                boss_beam_choice=options(),beam_player=player()))

    def test_stiffness_and_busy_helpers_prevent_beam_selection(self):
        for kw in (dict(player_flags=0x80),dict(triggers=[1,0,0])):
            result=boss_choice_to_launch(**options(ready_latch=1,**kw))
            self.assertEqual(result['action'],'orb');self.assertEqual(result['linked_beams'],[])

if __name__=='__main__':unittest.main()
