import json,random,unittest
from collections import defaultdict
from pe_weapon_sim.enemy_power import power_expression,evaluate_power,power_profile,records,ROOT
from pe_weapon_sim.script_decisions import probe
from pe_weapon_sim.beam_delivery import BeamPlayer
from pe_weapon_sim.incoming_damage import resolve_incoming
from pe_weapon_sim.tests.test_source_combat import config,foe,Fixed
from pe_weapon_sim.tests.test_beam_combat import player,plans
from pe_weapon_sim import engine,rules
from pe_weapon_sim.decomp_animation import source_behavior_rules

class SharedCombatTests(unittest.TestCase):
    def test_scaled_powers_match_raw_arithmetic_slices(self):
        data=json.loads((ROOT/'pe-enemy-actions-2026-10-18.json').read_text())
        checked=0
        for row in data['scripts']:
            for node in row['nodes']:
                if node['handler'] not in ('Script_SetEntityAnim12Args','Script_SetEntityAnim5Args'):continue
                expr=power_expression(row,node)
                if not expr or expr['kind']!='scaled':continue
                for scale in (32768,65536,98304,2147483647):
                    result=probe(row['nodes'],expr['proof_offsets'][0],node['offset'],base=row['root'],
                        cells={(4,expr['shared_cell']):scale})
                    self.assertEqual(result['status'],'exit')
                    operand=node['args'][4];value=result['cells'][f"{operand['mode']}:{operand['value']}"]&65535
                    self.assertEqual(evaluate_power(expr,{expr['shared_cell']:scale}),value)
                checked+=1
        self.assertEqual(checked,365)
    def test_known_regular_enemy_and_scale_requirement(self):
        profile=power_profile(dict(loc='5',name='0x0201'),0,{10:65536})
        self.assertEqual(profile,dict(power=15,action_slot=0,effect_type=0,critical_chance=10))
        self.assertEqual(power_profile(dict(loc='5',name='0x0201'),0,{10:32768})['power'],7)
        with self.assertRaises(ValueError):power_profile(dict(loc='5',name='0x0201'),0,{})
        self.assertEqual(power_profile(dict(loc='99999',name='0x0201'),0,{10:65536}),{})
    def test_cfg_merge_rejects_ambiguous_operand_producer(self):
        data=json.loads((ROOT/'pe-enemy-actions-2026-10-18.json').read_text())
        row=next(r for r in data['scripts'] if r['map']==156 and r['actor_type']==3)
        node=next(n for n in row['nodes'] if n['handler']=='Script_SetEntityAnim12Args')
        self.assertIsNotNone(power_expression(row,node))
        modified={**row,'edges':row['edges']+[dict(source=-1,target=node['offset'],kind='child_or_callback')]}
        self.assertIsNone(power_expression(modified,node))
    def test_all_declaration_coverage_is_explicit(self):
        rows,catalog=records()
        self.assertEqual((len(rows),sum(bool(r['expression']) for r in rows)),(393,381))
        self.assertEqual(len(catalog),284)
    def test_shared_hp_branch_and_pe_gauge_guard(self):
        p=BeamPlayer(500,500,defense=100,armor_first=10,atb=1,critical_resist=100)
        e=resolve_incoming(p,owner='normal',power=100,action_slot=0,effect_type=0,effect_chance=50,roll=lambda:99)
        self.assertEqual((e['damage'],p.hp),(35,465));self.assertEqual(p.reaction_requests,['normal'])
    def test_shared_barrier_bypasses_pe_guard_and_has_no_reaction(self):
        p=BeamPlayer(500,500,defense=100,armor_second=10,atb=9000,flags=0x200,max_atk=1000,barrier_energy=100000)
        e=resolve_incoming(p,owner='normal',power=100,action_slot=3,effect_type=0,effect_chance=0,roll=lambda:99)
        self.assertEqual((e['damage'],p.hp,p.barrier_energy),(70,500,99440))
        self.assertEqual(p.reaction_requests,[])
    def test_zero_damage_still_requests_reaction_and_consumes_roll(self):
        rolls=[];p=BeamPlayer(500,500,armor_first=1000)
        e=resolve_incoming(p,owner='normal',power=100,action_slot=0,effect_type=0,effect_chance=0,roll=lambda:rolls.append(1) or 99)
        self.assertEqual(e['damage'],0);self.assertEqual(rolls,[1]);self.assertEqual(p.reaction_requests,['normal'])
    def test_type10_half_damage_keeps_integer_order(self):
        p=BeamPlayer(500,500,atb=1)
        e=resolve_incoming(p,owner='steal',power=103,action_slot=0,effect_type=10,effect_chance=0,roll=lambda:99)
        self.assertEqual((e['damage'],p.hp),(25,475))
    def test_full_engine_barrier_beam_hit_does_not_enter_generic_hit_branch(self):
        r=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),time_cap=2.1,
            source_options=dict(hp=500,enemy_defaults=dict(charge_step=0),linked_beams=plans(),
                beam_player=player(flags=0x200,max_atk=1000,barrier_energy=100000),trace=True))
        self.assertEqual(r['beam_hits'],1);self.assertEqual(r['beam_damage'],0)
        self.assertEqual(r['_source_state']['hp'],500)
        self.assertEqual(r['_source_state']['beam_player']['barrier_energy'],99520)
        self.assertFalse(any(e['event']=='enemy_barrier_hit' for e in r['_source_events']))
    def test_mixed_normal_attack_uses_shared_barrier_reducer(self):
        r=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),time_cap=.1,
            source_options=dict(hp=500,enemy_defaults=dict(charge_step=9000,initial_charge=9000,windup=1,recovery=1,power=100,hit_probability=1),
                linked_beams=plans(),beam_player=player(flags=0x200,max_atk=1000,barrier_energy=100000),trace=True))
        self.assertEqual(r['_source_state']['hp'],500)
        self.assertEqual(r['_source_state']['beam_player']['barrier_energy'],99360)
        self.assertTrue(any(e['event']=='enemy_barrier_hit' for e in r['_source_events']))
    def test_regular_enemy_power_profile_is_used_in_full_combat(self):
        enemy={**foe(100000),'loc':'5','name':'0x0201'}
        r=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100,defense=0),[enemy],Fixed(),random.Random(5),time_cap=.1,
            source_options=dict(trace=True,enemy_defaults=dict(charge_step=9000,initial_charge=9000,windup=1,recovery=1,
                hit_probability=1,source_action_slot=0,source_shared_cells={10:65536},critical_resist=100)))
        self.assertEqual(r['power_catalog_matches'],1)
        self.assertEqual(r['explicit_power_hits'],1)
        self.assertEqual(r.get('legacy_damage_hits',0),0)
        hits=[e['damage'] for e in r['_source_events'] if e['event']=='enemy_hit']
        self.assertEqual(hits,[15]) # The previous level-based fallback would have used8.

if __name__=='__main__':unittest.main()
