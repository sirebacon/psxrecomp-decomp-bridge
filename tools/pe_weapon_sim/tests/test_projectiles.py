import json,random,unittest
from pathlib import Path
from pe_weapon_sim.source_projectile import BurstOrb,OrbEnemy,orb_speed,task_spawns,launch_update
from pe_weapon_sim.source_enemy import EnemyClock

class NoJitter:
    def randrange(self,n):return 16

class ProjectileTests(unittest.TestCase):
    def test_speed_boundaries_are_strict_script_comparisons(self):
        self.assertEqual([orb_speed(d) for d in (1000,1001,1500,1501,2000,2001,3000,3001,3500,3501)],[80,100,100,120,120,150,150,200,200,250])
    def test_asset_task_wait_launches_controller_on_update47(self):
        path=Path(__file__).resolve().parents[3]/'findings/data/pe-projectile-extract-2026-10-18.json'
        x=json.loads(path.read_text());program=next(p for p in x['programs'] if p['map']==156 and p['command']==129)
        self.assertEqual([e for e in task_spawns(program['triples']) if 'task'in e],[dict(update=1,task=1),dict(update=47,task=0)])
        self.assertEqual(launch_update(),48)
    def test_unresolved_task_wait_rejected(self):
        with self.assertRaises(ValueError):task_spawns([(4,0,1),(0,0,0)])
        with self.assertRaises(ValueError):task_spawns([(3,1,2)])
    def test_flight_contact_then_floor_expiry(self):
        orb=BurstOrb(y=-320,vx=100);hits=[];impact=None
        for tick in range(1,40):
            old=orb.state
            if orb.tick(NoJitter(),player_x=1300):hits.append(tick)
            if old==0 and orb.state==1:impact=tick
            if not orb.alive:break
        self.assertEqual((hits,impact,tick),([12],14,30))
    def test_contact_is_xz_only_with_strict_combined_radius(self):
        orb=BurstOrb(y=-10000,vx=0)
        self.assertFalse(orb.tick(NoJitter(),player_x=250,player_radius=100))
        self.assertTrue(orb.tick(NoJitter(),player_x=249,player_radius=100))
    def test_floor_window_stops_at_timer9(self):
        orb=BurstOrb(state=1,timer=7,cooldown=1,x=300)
        self.assertTrue(orb.tick(NoJitter(),player_x=0))
        orb.cooldown=1
        self.assertFalse(orb.tick(NoJitter(),player_x=0))
    def test_contact_rearms_after_24_updates(self):
        orb=BurstOrb(y=-10000,vx=0,vy=0)
        hits=[tick for tick in range(1,27) if orb.tick(NoJitter(),player_x=0)]
        self.assertEqual(hits,[1,25])
    def test_off_polygon_expires_six_updates_later(self):
        orb=BurstOrb(y=-10000,vx=0)
        orb.tick(NoJitter(),player_x=1000,inside=False)
        for _ in range(5):orb.tick(NoJitter(),player_x=1000)
        self.assertTrue(orb.alive)
        orb.tick(NoJitter(),player_x=1000);self.assertFalse(orb.alive)
    def test_chooser_threshold_and_completion_charge_reset(self):
        close=OrbEnemy(EnemyClock(70,charge=9000),distance=1299,rng=NoJitter())
        close.tick();self.assertEqual(close.kind,'melee')
        strikes=[i for i in range(1,42) if close.tick()[0]]
        self.assertEqual(strikes,[35]);self.assertEqual(close.clock.charge,0)
        far=OrbEnemy(EnemyClock(70,charge=9000),distance=1300,rng=NoJitter())
        far.tick();self.assertEqual(far.kind,'orb')
        hits=[i for i in range(1,87) if far.tick()[0]]
        self.assertEqual(hits,[59]);self.assertEqual(far.phase,'charge')
    def test_pauses_freeze_flight(self):
        e=OrbEnemy(EnemyClock(70,charge=9000),distance=1300,rng=NoJitter())
        e.tick();e.tick(paused=True);self.assertEqual(e.age,0)
        self.assertEqual(e.clock.charge,9000)

    def test_full_combat_uses_projectile_backend_and_conserves_ammo(self):
        from pe_weapon_sim import engine,rules
        from pe_weapon_sim.decomp_animation import source_behavior_rules
        class Fixed:
            def sample(self,rng):return 2000
        foe=dict(name='0x0216',loc='156',hp=100000,level=20,defense=33,boss=True,heat='Average',frost='Average',cyanide='Average',acid='Average',tranq='Average')
        cfg=dict(kind=1,power=20,range=5000,magazine=30,eff=dict(rof=1))
        result=engine.fight(source_behavior_rules(rules.CURRENT),cfg,dict(level=20,stat22=79,offense=100),[foe],Fixed(),random.Random(5),time_cap=15,source_options=dict(hp=385,static_enemy_catalog=True,enemy_action_timing='fast',projectile_height=320))
        self.assertEqual(result['projectile_model_matches'],1)
        self.assertGreater(result['projectiles_launched'],0)
        self.assertEqual(result['ammo_balance'],0)

    def test_beam_phase_and_interval_windows_are_opportunities(self):
        from pe_weapon_sim.source_projectile import beam_window
        short=beam_window(60,60)
        self.assertEqual(short,dict(first_active=59,contact_opportunities=[59],callback_end=150,stop_check_update=151))
        self.assertEqual(beam_window(300,300)['contact_opportunities'],[59])
        self.assertEqual(beam_window(300,140)['contact_opportunities'],[59,199,339])
        self.assertEqual(beam_window(300,140)['callback_end'],390)

    def test_close_melee_does_not_perturb_combat_random_stream(self):
        from pe_weapon_sim import engine,rules
        from pe_weapon_sim.decomp_animation import source_behavior_rules
        class Fixed:
            def sample(self,rng):return 1000
        foe=dict(name='0x0216',loc='156',hp=450,level=19,defense=33,boss=True,heat='Average',frost='Average',cyanide='Strong',acid='Strong',tranq='Strong')
        cfg=dict(kind=1,power=100,range=5000,magazine=30,eff=dict(rof=1))
        aya=dict(level=20,stat22=79,offense=100)
        options=dict(hp=385,static_enemy_catalog=True,enemy_action_timing='fast')
        baseline=engine.fight(source_behavior_rules(rules.CURRENT),cfg,aya,[foe],Fixed(),random.Random(5),time_cap=30,source_options=options)
        actual=engine.fight(source_behavior_rules(rules.CURRENT),cfg,aya,[foe],Fixed(),random.Random(5),time_cap=30,source_options=dict(options,projectile_height=320))
        for key in ('time','won','damage_taken','rounds'):self.assertEqual(actual[key],baseline[key])
