import random
import unittest
from pe_weapon_sim import engine,rules
from pe_weapon_sim.decomp_animation import source_combat_rules
from pe_weapon_sim.source_battle import BattleSession,Gun
from pe_weapon_sim.economy import evaluation,surrogate


class Fixed:
    def sample(self,rng): return 10


def foe(hp=1000):
    return dict(hp=hp,level=5,defense=10,boss=False,heat='Average',frost='Average',
                cyanide='Average',acid='Average',tranq='Average')


def config(kind=1,rof=3,mode=None,magazine=10,**eff):
    return dict(kind=kind,power=100,range=1500,magazine=magazine,
                eff=dict(rof=rof,**({'mode':mode} if mode else {}),**eff))


class SourceCombatTests(unittest.TestCase):
    def fight(self,cfg=None,foes=None,**kw):
        return engine.fight(source_combat_rules(rules.CURRENT),cfg or config(),
            dict(level=20,stat22=79,offense=100),foes or [foe()],Fixed(),random.Random(5),**kw)

    def test_hit_damage_occurs_at_event_and_stops_queue_on_kill(self):
        r=self.fight(config(rof=1),[foe(1)],source_options=dict(trace=True))
        hits=[e for e in r['_source_events'] if e['event']=='hit']
        self.assertEqual(r['won'],1);self.assertEqual(r['rounds'],1)
        self.assertAlmostEqual(r['time'],hits[-1]['update']/(59.9/2))
        self.assertEqual(r['damage'],1)

    def test_finite_reserve_and_reloads_in_actual_fight(self):
        r=self.fight(config(magazine=2),[foe(100000)],start_loaded=1,max_turns=1,
            source_options=dict(reserve_ammo={0:2},trace=True))
        self.assertEqual((r['rounds'],r['reloads'],r['loaded_left'],r['reserve_left']),(3,1,0,0))
        self.assertEqual(r['ammo_balance'],0)
        self.assertGreater(r['damage_taken'],0)
        self.assertTrue(any(e['event']=='enemy_hit' for e in r['_source_events']))

    def test_attack_all_reload_resets_counter_and_produces_seven_not_five(self):
        s=BattleSession({'a':Gun(1,5,2)},{0:5},'a',gauge=9000)
        r=s.attack(mode='all',rof=5)
        self.assertEqual(len([e for e in r['events'] if e['event']=='fire']),7)
        self.assertTrue(any(e['event']=='attack_counter_reset' and e['before']==4 and e['after']==5
                            for e in r['events']))
        self.assertEqual((s.gun.loaded,s.reserves[0]),(0,0))
        combat=self.fight(config(rof=5,mode='all',magazine=5),[foe(100000)],start_loaded=2,
            max_turns=1,source_options=dict(reserve_ammo={0:5}))
        self.assertEqual(combat['rounds'],7)
        self.assertEqual(combat['ammo_balance'],0)

    def test_survival_and_horizon_stop_in_flight(self):
        r=self.fight(foes=[foe(100000)],source_options=dict(hp=1,trace=True),enemy_dmg=lambda f:10)
        self.assertEqual(r['won'],0);self.assertEqual(r['damage_taken'],10)
        self.assertEqual(r['rounds'],0)
        r=self.fight(foes=[foe(100000)],time_cap=.1)
        self.assertLessEqual(r['time'],.1);self.assertEqual(r['rounds'],0)

    def test_switch_policy_uses_carried_magazines_and_damage_config(self):
        def choose(state): return 'rifle' if state['turns']==1 else 'primary'
        r=self.fight(config(rof=1),[foe(100000)],max_turns=3,
            source_options=dict(weapons={'rifle':config(4,rof=1)},weapon_policy=choose,
                                reserve_ammo={0:0},trace=True))
        self.assertEqual(r['switches'],2)
        self.assertEqual(r['_source_state']['loaded'],{'primary':8,'rifle':9})
        self.assertEqual(r['ammo_balance'],0)
        self.assertGreater(r['damage'],0)

    def test_modes_and_timed_status_application(self):
        for mode in ('all','random','burst'):
            r=self.fight(config(mode=mode,acid=True),[foe(100000),foe(100000)],max_turns=2,
                source_options=dict(trace=True,enemy_angles={0:0,1:0x100}))
            self.assertGreater(r['rounds'],0);self.assertGreater(r['damage'],0)
            self.assertEqual(r['ammo_balance'],0)

    def test_encounter_suite_and_surrogate_guard(self):
        r=evaluation.benchmark(source_combat_rules(rules.CURRENT),config(mode='all'),
            dict(level=30,stat22=79,offense=100),'Disc2',n=2,suite=('close_normal','endurance'))
        self.assertIn('suite_time',r)
        with self.assertRaises(ValueError):
            surrogate.dps(config(),dict(stat22=79,offense=100),20,rules=source_combat_rules(rules.CURRENT))

    def test_chained_combat_carries_hp_gauge_and_reserves(self):
        first=self.fight(config(rof=1),[foe(1)],source_options=dict(hp=300,reserve_ammo={0:3}))
        state=first['_source_state']
        second=self.fight(config(rof=1),[foe(1)],source_options=dict(hp=300,initial_state=state,trace=True))
        self.assertEqual(second['_source_state']['loaded']['primary'],state['loaded']['primary']-1)
        self.assertEqual(second['_source_state']['reserves'],state['reserves'])
        self.assertLessEqual(second['_source_state']['hp'],state['hp'])
        self.assertEqual(second['ammo_balance'],0)

    def test_switch_does_not_commit_after_horizon(self):
        s=BattleSession({'a':Gun(1,10,3),'b':Gun(4,10,3)},{0:0},'a',gauge=9000,
            should_stop=lambda:s.update>=2)
        s.switch('b',menu_updates=5)
        self.assertEqual(s.equipped,'a')
        self.assertFalse(any(e['event']=='weapon_change' for e in s.events))
