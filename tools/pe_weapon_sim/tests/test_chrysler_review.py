import unittest
from collections import Counter
from pe_weapon_sim.run_chrysler_review import B,baseline,chrysler_ids,configuration
class ChryslerReviewTests(unittest.TestCase):
 def test_complete_remaining_roster_and_alias(self):
  ids=chrysler_ids()
  self.assertEqual(len(ids),31)
  self.assertEqual(Counter(B.W[i].kind for i in ids),{1:15,3:3,4:5,5:5,6:1,8:2})
  self.assertIn(0x60,ids) # AM444 in the location table is AM44 in native records.
  self.assertFalse(any(B.W[i].kind==2 for i in ids))
 def test_latest_native_buffs_are_the_baseline(self):
  bonuses=baseline()[1]
  self.assertEqual({i:bonuses[i] for i in (0x5f,0x69,0x85,0x8a,0x8b)}, {0x5f:5,0x69:10,0x85:20,0x8a:20,0x8b:18})
 def test_builtins_and_no_magazine_investment(self):
  for i in chrysler_ids():
   w=B.W[i];a=configuration(w,'EX50','stock');b=configuration(w,'EX50','attack_only')
   self.assertFalse(a['eff']['rof_mod']);self.assertFalse(b['eff']['rof_mod'])
   self.assertEqual(a['magazine'],max(1,w.bullets+w.bonus_bullets))
   self.assertEqual(a['magazine'],b['magazine'])
   self.assertEqual(b['power']-a['power'],50)
 def test_commands_and_cyanide_are_preserved(self):
  self.assertEqual(configuration(B.W[0x4a],'EX50','stock')['eff']['commands'],3)
  self.assertTrue(configuration(B.W[0x88],'EX50','stock')['eff']['cyanide'])
if __name__=='__main__':unittest.main()
