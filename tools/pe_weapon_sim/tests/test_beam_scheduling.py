import json,random,unittest
from functools import lru_cache
from pathlib import Path
from pe_weapon_sim.beam_scheduling import retail_sqrt,projected_target,formation_targets,later_target_allowed,BeamOwnerPoll,EffectProcess
from pe_weapon_sim.script_decisions import probe
from pe_weapon_sim.extract_enemy_scripts import PROJECT,BRIDGE,sectors
from pe_weapon_sim.decode_enemy_actions import flow

@lru_cache(maxsize=1)
def source_nodes():
    inv=json.loads((BRIDGE/'findings/data/pe-enemy-scripts-2026-10-18.json').read_text())
    room=next(r for r in inv['rooms'] if r['map']==156 and r['disc']==1)
    with (PROJECT/'parasite-eve-recomp/disc/Parasite Eve (USA) (Disc 1).bin').open('rb') as f:blob=sectors(f,room['lba'],room['sectors'])
    script=next(s for s in room['scripts'] if s['actor_type']==3)
    return script['start'],flow(blob,script['start'],script['end'],inv['handlers'])['nodes']

class BeamSchedulingTests(unittest.TestCase):
    def test_retail_sqrt_positive_boundaries_and_negative_inputs(self):
        from math import isqrt
        rng=random.Random(344)
        for value in (0,1,1000000,1002000,1002001,2147483647,*[rng.randrange(2147483648) for _ in range(1000)]):
            self.assertEqual(retail_sqrt(value),isqrt(value))
        self.assertEqual(retail_sqrt(-1),0);self.assertEqual(retail_sqrt(-2147483648),0)

    def test_mode_entry_overwrites_short_mode(self):
        base,nodes=source_nodes()
        for region in (0,1,2):
            r=probe(nodes,base+5940,base+6024,cells={(1,46):region,(4,27):1},base=base)
            self.assertEqual(r['cells']['4:27'],0 if region==0 else 2)

    def test_projection_matches_actual_script_arithmetic(self):
        base,nodes=source_nodes();rng=random.Random(531)
        for _ in range(100):
            player=[rng.randrange(-5000,5000)*65536+rng.randrange(65536) for _ in range(2)]
            boss=[rng.randrange(-5000,5000)*65536+rng.randrange(65536) for _ in range(2)]
            distance=rng.randrange(200,8000)*65536
            cells={(1,4):boss[0],(1,6):boss[1],(1,41):player[0],(1,43):player[1],(1,7):distance}
            r=probe(nodes,base+6220,base+6588,cells=cells,base=base)
            self.assertEqual(r['status'],'exit')
            self.assertEqual(projected_target(player,boss,distance,200),(r['cells']['1:41'],r['cells']['1:43']))
    def test_second_target_spacing_preserves_zero_z_bug_and_strict_boundary(self):
        base,nodes=source_nodes()
        for dx in (-1001,-1000,0,1000,1001):
            for dz in (0,3000):
                targets=[(0,0),(dx,dz),(2000,0)]
                cells={(4,18):1,(4,21):0,(4,22):0,(4,23):dx,(4,24):dz}
                r=probe(nodes,base+7752,base+8048,cells=cells,base=base)
                self.assertEqual(r['cells'].get('4:19')==1,later_target_allowed(1,targets,[1,0,0]))
    def test_third_target_checks_both_prior_targets_even_if_only_one_active(self):
        base,nodes=source_nodes()
        for triggers in ([1,0,0],[0,1,0],[0,0,0],[1,1,0]):
            for targets in ([(0,0),(5000,0),(5000,0)],[(0,0),(5000,0),(2500,0)]):
                cells={(4,18+i):v for i,v in enumerate(triggers)}
                for i,(x,z) in enumerate(targets):cells[4,21+2*i]=x;cells[4,22+2*i]=z
                r=probe(nodes,base+8964,base+9636,cells=cells,base=base)
                self.assertEqual(r['cells'].get('4:20')==1,later_target_allowed(2,targets,triggers))
    def test_formation_targets_match_decoded_script_for_all_choices(self):
        from pe_weapon_sim.rotation_oracle import RotationOracle
        table=RotationOracle(PROJECT/'parasite-eve-recomp/disc/SLUS_006.62.original-backup').table
        base,nodes=source_nodes()
        for heading in (0,512,1024,2048,3072):
            for mode in (0,2):
                for choice in (0,1,2):
                    boss=(0,-6000*65536);player=(2000*65536,-6000*65536);distance=2000*65536
                    samples=[(player,distance)]*(1 if mode==0 else 3)
                    expected=formation_targets(mode,choice,samples,boss,heading,table)
                    start=10428 if mode==0 else 11260
                    cells={(1,51):choice,(1,9):0}
                    if mode==0:
                        first=probe(nodes,base+9864,base+10384,base=base,distance=distance,position=boss,player=player,limit=100)
                        self.assertEqual(first['status'],'exit')
                        cells.update({tuple(map(int,k.split(':'))):v for k,v in first['cells'].items()})
                    result=probe(nodes,base+start,base+(11032 if mode==0 else 14416),
                        cells=cells,base=base,distance=distance,position=boss,player=player,
                        heading=heading,trig_table=table,limit=300)
                    self.assertEqual(result['status'],'exit')
                    actual=[(result['cells'][f'4:{21+2*i}'],result['cells'][f'4:{22+2*i}']) for i in range(3)]
                    self.assertEqual(actual,expected)

    def test_owner_samples_once_and_releases_after_command_and_held(self):
        cells={18:1,21:100,22:-6000,27:0};p=BeamOwnerPoll(0)
        self.assertEqual(p.poll(cells)['interval'],300)
        cells[21]=999
        self.assertIsNone(p.poll(cells,held=0));self.assertEqual(cells[18],1)
        p.poll(cells,command_complete=True,held=1);self.assertEqual(cells[18],1)
        p.poll(cells,held=0);self.assertEqual(cells[18],0)
    def test_owner_two_explicit_yield_and_short_parameters(self):
        cells={20:1,25:0,26:0,27:1};p=BeamOwnerPoll(2)
        self.assertEqual(p.poll(cells)['duration'],60)
        p.poll(cells,command_complete=True,action_state=2,held=0)
        self.assertEqual(cells[20],1)
        p.poll(cells,action_state=4,held=0);self.assertEqual(cells[20],1)
        p.poll(cells,held=0);self.assertEqual(cells[20],0)
    def test_mark_for_close_still_allows_current_callback(self):
        p=EffectProcess();self.assertTrue(p.begin())
        self.assertTrue(p.actor_gate(action_state=0,held=1,command_value=0,core_flags=0,actor_mode=2))
        self.assertEqual(p.state,4);self.assertFalse(p.begin());self.assertEqual(p.state,5)
        self.assertFalse(p.begin());self.assertEqual(p.state,0)
    def test_actor_gate_is_conditional_and_pause_does_not_mean_pm_stop(self):
        p=EffectProcess()
        self.assertTrue(p.actor_gate(action_state=2,held=1,command_value=0,core_flags=0x180e,actor_mode=0))
        self.assertEqual(p.state,2)
        self.assertFalse(p.actor_gate(action_state=0,held=1,command_value=5,core_flags=0,actor_mode=0))
        self.assertEqual(p.state,2)
    def test_pm_stop_requires_matching_owner_or_force(self):
        p=EffectProcess();self.assertFalse(p.stop(owner_matches=False));self.assertEqual(p.state,2)
        self.assertTrue(p.stop(owner_matches=False,force=True));self.assertEqual(p.state,0)

if __name__=='__main__':unittest.main()
