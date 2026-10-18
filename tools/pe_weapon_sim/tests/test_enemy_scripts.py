import struct
import unittest
from pe_weapon_sim.extract_enemy_scripts import instruction,word
from pe_weapon_sim.enemy_catalog import lookup,catalog

class EnemyScriptTests(unittest.TestCase):
    def test_tail_modes_begin_at_sixth_argument(self):
        header=6<<13 | 1<<17
        blob=struct.pack('<8I',header,3,10,11,12,13,14,15)
        ins,end=instruction(blob,0,['setter'])
        self.assertEqual(end,32)
        self.assertEqual([a['mode'] for a in ins['args']],[1,0,0,0,0,3])
    def test_rejects_truncated_and_unknown_records(self):
        with self.assertRaises(ValueError):word(b'123',0)
        with self.assertRaises(ValueError):instruction(struct.pack('<II',7,0),0,['known'])
        with self.assertRaises(ValueError):instruction(struct.pack('<III',(1<<13)|(7<<17),0,9),0,['known'])
    def test_room_identity_uses_rank_and_kind_not_actor_index(self):
        self.assertEqual(lookup(dict(loc='5',name='0x0201'))['charge_step'],60)
        self.assertEqual(lookup(dict(loc='156',name='0x0216'))['charge_step'],70)
        self.assertEqual(lookup(dict(loc='5',name='0x0202')), {})
        self.assertEqual(lookup(dict(loc='99999',name='0x0201')), {})
        self.assertGreater(len(catalog()),20)
