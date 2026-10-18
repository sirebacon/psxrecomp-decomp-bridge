import random,unittest
from pe_weapon_sim.effect_cleanup import EffectCleanup
from pe_weapon_sim.beam_delivery import BeamPlayer,BeamOwner,BeamEmitter
from pe_weapon_sim.beam_combat import BeamCombat
from pe_weapon_sim import engine,rules
from pe_weapon_sim.decomp_animation import source_behavior_rules
from pe_weapon_sim.tests.test_source_combat import config,foe,Fixed


def player(**kw):
    return dict(max_hp=500,defense=100,armor_second=10,status_step=60,
        pe_gauge=0,x=1600,z=-6000,critical_resist=100,**kw)

def plans(n=1,duration=60):
    return [dict(owner=str(i),start_update=0,target_x=1000,target_z=-6000,
        duration=duration,interval=duration,scale=65536) for i in range(n)]

class BeamCombatTests(unittest.TestCase):
    def test_result_one_discards_live_visuals_next_script_pass_releases(self):
        c=EffectCleanup(1,2,4)
        for u in range(1,5):self.assertFalse(c.step(u,pool_active_before=99))
        self.assertFalse(c.live);self.assertTrue(c.step(5,pool_active_before=99))
    def test_result_two_waits_for_visuals(self):
        c=EffectCleanup(1,2,4)
        self.assertFalse(c.step(1,result=2,pool_active_before=2))
        self.assertFalse(c.step(2,result=2,pool_active_before=1))
        self.assertFalse(c.step(3,result=2,pool_active_before=0))
        self.assertTrue(c.step(4))
    def test_outside_floor_target_cancels_before_active_phase(self):
        b=BeamCombat([{**plans()[0],'target_z':-2000}],player(),hp=500)
        events=[]
        for _ in range(55):b.begin_update(500,lambda:99);events+=b.update_effects(1,0)
        self.assertEqual([e['event'] for e in events],['beam_cleanup'])
        self.assertEqual(events[0]['effect_update'],55)

    def test_exact_short_and_long_cleanup(self):
        for duration,last in ((60,150),(300,390)):
            e=BeamEmitter(BeamOwner('b'),0,0,duration,duration)
            p=BeamPlayer(500,500)
            for u in range(1,last+1):e.update_effect(p,u,player_x=0,player_z=0,player_radius=23)
            self.assertEqual(e.owner.effect_state,2);self.assertFalse(e.cleanup.live)
            e.update_effect(p,last+1,player_x=0,player_z=0,player_radius=23)
            self.assertEqual((e.held,e.owner.effect_state),(0,4))
    def test_delivery_next_update_and_immediate_timer_tick(self):
        b=BeamCombat(plans(3),player(flags=0x100),hp=500)
        events=[]
        for _ in range(59):
            events+=b.begin_update(500,lambda:99)['events'];b.update_effects(1,0)
        self.assertEqual(events,[])
        events=b.begin_update(500,lambda:99)['events']
        self.assertEqual([e['damage'] for e in events],[74,60,60])
        self.assertEqual(b.player.hp,306);self.assertEqual(b.player.stiffness_timer,8940)
        self.assertEqual(b.player.contact_timer,89)
        b.update_effects(1,0)
        for _ in range(149):b.begin_update(306,lambda:99);b.update_effects(1,0)
        self.assertFalse(b.player.flags&0xc0)
    def test_weapon_radius_changes_strict_contact_boundary(self):
        for kind,expected in ((1,False),(4,True)):
            b=BeamCombat(plans(),{**player(),'x':1630},hp=500)
            contacts=[]
            for _ in range(59):b.begin_update(500,lambda:99);contacts+=b.update_effects(kind,0)
            self.assertEqual(bool(contacts),expected)
    def test_full_engine_opt_in_damage_cleanup_and_ammo(self):
        result=engine.fight(source_behavior_rules(rules.CURRENT),config(rof=1),
            dict(level=20,stat22=79,offense=100),[foe(100000)],Fixed(),random.Random(5),
            time_cap=8,source_options=dict(hp=500,enemy_defaults=dict(charge_step=0),
            linked_beams=plans(3),beam_player=player(flags=0x100),trace=True))
        self.assertEqual(result['beam_damage'],194)
        self.assertEqual(result['_source_state']['hp'],306)
        self.assertEqual(result['beam_cleanups'],3);self.assertEqual(result['ammo_balance'],0)
        events=result['_source_events']
        self.assertEqual([e['update'] for e in events if e['event']=='beam_hit'],[60]*3)
        self.assertEqual([e['effect_update'] for e in events if e['event']=='beam_cleanup'],[151]*3)
        self.assertEqual(result['beam_counter_unresolved'],3)
    def test_menu_pause_freezes_effect_and_status_clocks(self):
        from pe_weapon_sim.source_battle import BattleSession,Gun
        b=BeamCombat(plans(),player(),hp=500)
        def update(session,paused):
            if not paused:
                b.begin_update(b.player.hp,lambda:99);b.update_effects(session.gun.kind,0)
        session=BattleSession({'a':Gun(1,10,10)},{0:0},'a',on_update=update)
        session.advance(59);session.advance(100,paused=True)
        self.assertEqual(b.active_update,59);self.assertEqual(b.player.hp,500)
        session.advance()
        self.assertEqual(b.player.hp,440);self.assertEqual(b.player.stiffness_timer,8940)
        session.advance(100,paused=True)
        self.assertEqual(b.player.stiffness_timer,8940)

    def test_pe_guard_uses_separate_pe_gauge(self):
        b=BeamCombat(plans(),{**player(),'pe_gauge':1},hp=500)
        for _ in range(59):b.begin_update(500,lambda:99);b.update_effects(1,0)
        self.assertEqual(b.begin_update(500,lambda:99)['events'][0]['damage'],30)
    def test_barrier_preserves_hp_and_status(self):
        b=BeamCombat(plans(),player(flags=0x200,max_atk=1000,barrier_energy=100000),hp=500)
        for _ in range(59):b.begin_update(500,lambda:99);b.update_effects(1,0)
        event=b.begin_update(500,lambda:99)['events'][0]
        self.assertTrue(event['barrier']);self.assertEqual(b.player.hp,500)
        self.assertEqual(b.player.barrier_energy,99520);self.assertEqual(b.player.stiffness_timer,8940)

if __name__=='__main__':unittest.main()
