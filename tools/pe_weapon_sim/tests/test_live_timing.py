import unittest
from pe_weapon_sim.analyze_live_timing import analyze


class TestLiveTimingAnalysis(unittest.TestCase):
    def row(self, frame, gauge, **extra):
        return dict(frame=frame,gauge=gauge,fill_rate=79,entity=0x800BEF90,
                    hp=343,flags=2,**extra)

    def test_gauge_step_and_weapon_debit(self):
        rows=[self.row(0,9000,weapon_slot=18),self.row(1,4500,weapon_slot=19),
              self.row(2,4500,weapon_slot=19),self.row(3,4579,weapon_slot=19),
              self.row(4,4579,weapon_slot=19),self.row(5,4658,weapon_slot=19)]
        result=analyze(dict(label='synthetic',rows=rows))
        self.assertEqual(result['gain_counts'],{'(79, 79)':2})
        self.assertEqual(result['gain_gap_vblanks'],{'2':1})
        self.assertEqual(result['weapon_changes'][0]['gauge_after'],4500)
        self.assertFalse(result['ammo_changes'])

    def test_capture_gap_rejected(self):
        with self.assertRaises(ValueError):
            analyze(dict(label='gap',rows=[self.row(0,0),self.row(2,79)]))


if __name__=='__main__':unittest.main()
