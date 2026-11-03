import unittest
from pe_weapon_sim.run_shotgun_review import B,baseline,configuration,scenarios
class ShotgunReviewTests(unittest.TestCase):
 def test_clustered_angles_put_all_three_inside_native_burst_cone(self):
  from pe_weapon_sim.source_battle import burst_contains,signed16
  angles=[-128,0,128]
  for selected in angles:
   self.assertTrue(all(burst_contains(signed16(selected+0x800),target) for target in angles))
 def test_all_records_and_no_installed_rof(self):
  guns=[w for w in B.W.values() if w.kind==2]
  self.assertEqual({w.id for w in guns},set(range(0x68,0x6f)))
  for w in guns:
   cfg=configuration(w,'Disc2','stock')
   self.assertEqual(cfg['power'],w.attack+w.bonus_attack)
   self.assertEqual(cfg['magazine'],w.bullets+w.bonus_bullets)
   self.assertFalse(cfg['eff']['rof_mod'])
   self.assertEqual(cfg['eff']['mode'],'burst')
 def test_magazine_profiles_do_not_sneak_in_historical_investment(self):
  for w in B.W.values():
   if w.kind!=2:continue
   a=configuration(w,'Disc2','attack_only');b=configuration(w,'Disc2','mag2')
   self.assertEqual(a['magazine'],w.bullets+w.bonus_bullets)
   self.assertEqual(b['magazine'],a['magazine']+2)
   self.assertEqual(a['power'],b['power'])
   self.assertEqual(a['range'],b['range'])
 def test_current_grenade_bonuses_in_comparison(self):
  self.assertEqual(configuration(B.W[0x8b],'Disc2','stock')['power'],52+2+18)
  self.assertEqual(baseline()[1][0x85],20)
  self.assertEqual(baseline()[1][0x8a],20)
 def test_chrysler_stress_is_explicit_and_preserves_enemy_stats(self):
  rr=scenarios('EX50')
  self.assertEqual(len(rr),24)
  self.assertEqual(len({(r['foes'][0]['name'],r['ex_hp'],r['ex_defense']) for r in rr}),12)
  self.assertEqual(max(r['ex_defense'] for r in rr),200)
  for r in rr:
   self.assertEqual(r['aya']['level'],50)
   self.assertFalse(r['boss'])
   self.assertEqual(len(r['foes']),1 if r['scenario_kind']=='ex_solo' else 3)
   self.assertTrue(all(f['hp']==r['ex_hp'] and f['defense']==r['ex_defense'] for f in r['foes']))
if __name__=='__main__':unittest.main()
