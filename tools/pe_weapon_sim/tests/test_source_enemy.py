import random
import unittest
from pe_weapon_sim.source_enemy import EnemyClock,ScriptedEnemy,counter_probability,enemy_damage
from pe_weapon_sim.source_battle import BattleSession,Gun,build_queue
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim import engine,rules


class SourceEnemyTests(unittest.TestCase):
    def test_counter_integer_rolls_and_rank_branches(self):
        self.assertEqual([counter_probability(210,d) for d in (1,0,-1,-2)], [.21,.13,.07,.05])
        self.assertEqual(counter_probability(0,0),0)
        self.assertEqual(counter_probability(10000,-1),1)

    def test_charge_overshoot_and_actor_hold_reset(self):
        c=EnemyClock(79,charge=8990)
        c.tick();self.assertEqual(c.charge,9069)
        c.tick();self.assertEqual(c.charge,9000)
        c.actor_flags=0x1000;c.tick();self.assertEqual(c.charge,0)
        c=EnemyClock(79,flags=1);c.tick();self.assertEqual(c.charge,48)

    def test_status_cycles_and_poison_use_update_clock(self):
        c=EnemyClock(9000,flags=0x1800|0x10,actor_flags=0x1000,periodic_damage=7)
        c.tick();self.assertEqual(c.flags&0x1800,0x1000)
        c.tick();self.assertEqual(c.charge,0)
        c.tick();self.assertEqual(c.flags&0x1800,0x800)
        c.tick();c.tick();self.assertFalse(c.incapacitated)
        c=EnemyClock(0,flags=0x10,periodic_damage=7)
        self.assertEqual(sum(c.tick() for _ in range(30)),0)
        self.assertEqual(c.tick(),7)
        before=(c.charge,c.flags);c.tick(paused=True);self.assertEqual((c.charge,c.flags),before)

    def test_explicit_script_policy_is_not_instant_full_charge_damage(self):
        e=ScriptedEnemy(EnemyClock(3000),windup=2,recovery=1)
        self.assertEqual([e.tick()[0] for _ in range(5)],[False,False,False,False,True])

    def test_enemy_damage_integer_pipeline(self):
        damage,crit=enemy_damage(100,50,armor_first=20,effect_chance=20,roll=0,effect_type=10)
        self.assertEqual((damage,crit),(52,True)) # (100-10-20)*3/2 /2
        self.assertEqual(enemy_damage(10,100)[0],0)
        self.assertEqual(enemy_damage(101,charged_guard=True)[0],50)
        self.assertEqual(enemy_damage(100,50,armor_first=20,armor_second=40,action_slot=3)[0],50)

    def test_counter_keeps_bar_and_one_command(self):
        for mode,shots in ((None,3),('random',1),('all',3)):
            s=BattleSession({'a':Gun(1,30,30)},{0:0},'a',gauge=1000)
            r=s.attack(counter=True,rof=3,commands=3,mode=mode)
            self.assertEqual(len([e for e in r['events'] if e['event']=='fire']),shots)
            self.assertGreater(s.gauge,1000)
            self.assertEqual(r['events'][0]['event'],'counter_start')

    def test_counter_queue_uses_attacker_without_random_draws(self):
        r=random.Random(4);before=r.getstate()
        q=build_queue('random',5,3,[1,2],2,r,counter=True)
        self.assertEqual(q,[dict(target=2,command=0)])
        self.assertEqual(r.getstate(),before)

    def test_counter_schedules_during_refill_and_conserves_ammo(self):
        class Fixed:
            def sample(self,rng):return 10
        foe=dict(hp=100000,level=5,defense=10,boss=False,heat='Average',frost='Average',
            cyanide='Average',acid='Average',tranq='Average')
        c=dict(kind=1,power=100,range=1500,magazine=30,eff=dict(rof=1,counter=True))
        r=engine.fight(source_behavior_rules(rules.CURRENT),c,
            dict(level=20,stat22=79,offense=100,hp_level=10000),[foe],Fixed(),random.Random(5),
            max_turns=1,source_options=dict(trace=True,enemy_defaults=dict(charge_step=120,
                windup=1,recovery=1,hit_probability=1)))
        self.assertGreater(r.get('counters',0),0)
        self.assertGreater(r['rounds'],1)
        self.assertEqual(r['ammo_balance'],0)
        self.assertTrue(any(e['event']=='counter_start' for e in r['_source_events']))

    def test_current_poison_modifier_is_applied_once_to_tick_damage(self):
        class Fixed:
            def sample(self,rng):return 10
        foe=dict(hp=100000,level=16,defense=10,boss=False,heat='Average',frost='Average',
            cyanide='Average',acid='Weak',tranq='Average')
        cfg=dict(kind=1,power=100,range=1500,magazine=30,eff=dict(rof=1,acid=True))
        r=engine.fight(source_behavior_rules(rules.CURRENT),cfg,
            dict(level=20,stat22=79,offense=100),[foe],Fixed(),random.Random(5),time_cap=6,
            source_options=dict(enemy_defaults=dict(charge_step=0)))
        self.assertEqual(r['poison'],5) # base4, CURRENT125%, one31-update tick
