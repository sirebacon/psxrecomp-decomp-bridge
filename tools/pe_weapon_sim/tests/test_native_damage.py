import unittest
from pe_weapon_sim.native_damage import hit_damage
from pe_weapon_sim import rules
class NativeDamageTests(unittest.TestCase):
    def test_status_gate_uses_pre_quality_damage_not_minimum_floor(self):
        self.assertEqual(hit_damage(100,1,1000,1,'crit',100,rules.CURRENT,False,with_positive=True),(2,False))
        self.assertEqual(hit_damage(0,1,0,1,'graze',100,rules.CURRENT,False,with_positive=True),(1,True))
    def test_integer_quality_and_defense(self):
        # (100/5+100)*100/100 - 11 = 109; graze floors to 32.
        self.assertEqual(hit_damage(100,100,11,1,'graze',100,rules.CURRENT,False),32)
    def test_installed_rof7_does_not_round_to_29_percent(self):
        r=dict(rules.CURRENT,rof_mod_hit_pct={7:29})
        # atk_pm=200000//126=1587; attack=190*18//100=34, defense 1.
        self.assertEqual(hit_damage(100,100,10,7,'hit',100,r,True),33)
        self.assertEqual(hit_damage(100,100,10,7,'hit',100,r,False),22)
    def test_element_scales_attack_and_defense_before_quality(self):
        self.assertEqual(hit_damage(100,100,11,1,'crit',80,rules.CURRENT,False),132)
    def test_floor(self):
        self.assertEqual(hit_damage(100,1,1000,1,'crit',100,rules.CURRENT,False),2)
        self.assertEqual(hit_damage(100,1,1000,1,'hit',100,rules.CURRENT,False),1)
if __name__=='__main__':unittest.main()
