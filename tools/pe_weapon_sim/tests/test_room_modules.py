"""Room-module effects (room_modules.py): FieldFx object engine + falling sprite burst port.

Regression tests of the port's behaviour; the script words, handler tables and module kind are
read from the original room data (independent of the port)."""
import random, unittest

from pe_weapon_sim.room_handlers import handler, records
from pe_weapon_sim.room_modules import (ModuleObject, catalog, joint_track, module_spec, slot_record,
                                        timeline)
from pe_weapon_sim.enemy_identity import FIRST_RUN_SHARED_CELLS as C, cells_key

VARS = {0: 3, 1: 10, 2: 180, 3: 180}           # 146 actor 6 Pm_ScriptSendCommand0 before slot 3


class DataTests(unittest.TestCase):
    def test_room_146_handler_records(self):
        self.assertEqual(dict(records(146)), {40: 0x80192564, 166: 0x8019260C, 37: 0x801924AC})
        names = [n for _, n in handler(146, 40)['fields'][:7]]
        self.assertEqual(names[0], 'RoomLib_ClassNop0')
        self.assertTrue(names[1].startswith('RoomLib_PlantScript'))
        self.assertTrue(names[4].startswith('RoomLib_RegisterPairedTables'))

    def test_module_script_from_room_data(self):
        spec = module_spec(146, 40)
        self.assertEqual(spec['kind'], 'RoomEffect_FallingBurstInit')
        self.assertEqual(spec['script'][0], 0x10000)                  # start slot 0 (the burst clock)
        self.assertEqual(spec['script'][-1], 0xFFFFFFFF)

    def test_catalog_identities(self):
        cat = sorted(catalog(cells_key(C)))
        for k in [(65, 11, 3), (146, 19, 3), (147, 19, 3), (324, 19, 3), (327, 19, 3), (111, 17, 3), (167, 23, 3)]:
            self.assertIn(k, cat)
        self.assertEqual(slot_record(146, 6, 3), (6, 7, 65536, 65536))


class EngineTests(unittest.TestCase):
    def test_script_ops(self):
        h = {0: lambda o, s, d: None}
        o = ModuleObject([0x100005, 0x200003, 0x300001, 0x500002, 0x20002, 0xFFFFFFFF], h, h, random.Random(0))
        o.run_script()
        self.assertEqual((o.regs[0], o.vars[2], o.wait), (7, 7, 2))
        for _ in range(3): o.run_script()
        self.assertEqual(o.halted, 1)

    def test_close_needs_halt_and_no_slots(self):
        done = {}
        def init(o, s, d): pass
        def upd(o, s, d):
            if o.last_slot_halted(): s['flag'] = 2
        o = ModuleObject([0x10000, 0xFFFFFFFF], {0: init}, {0: upd}, random.Random(0))
        ticks = 0
        while not o.tick(): ticks += 1
        self.assertEqual(o.closed, 2)                                     # halt on pass 1, controller frees on pass 2


class FallingBurstTests(unittest.TestCase):
    def setUp(self):
        r = slot_record(146, 6, 3)
        self.joint = joint_track(146, 6, r[0], r[1], r[2], r[3], 4096)

    def test_release_is_deterministic(self):
        rel = {timeline(146, 40, VARS, self.joint, d, 100, random.Random(k))['release'] for d in (100, 400, 900) for k in range(3)}
        self.assertEqual(rel, {284})                                      # vs the 20-update placeholder

    def test_reload_spaces_contacts(self):
        for k in range(6):
            c = timeline(146, 40, VARS, self.joint, 100, 100, random.Random(k))['contacts']
            self.assertTrue(all(b - a >= 180 for a, b in zip(c, c[1:])))

    def test_far_aya_is_not_hit(self):
        self.assertEqual(timeline(146, 40, VARS, self.joint, 2000, 100, random.Random(1))['contacts'], [])


class TaskRunnerTests(unittest.TestCase):
    def test_timed_spawn_scene_flash(self):
        from pe_weapon_sim.room_modules import task_spec, task_timeline
        self.assertEqual(task_spec(154, 187)['script'][:4], [(5, 0, 0), (1, 6, 102), (4, 48, 0), (2, 0, 0)])
        r = task_timeline(154, 187, 5000, 100)                        # no distance test: unavoidable
        self.assertEqual(r, dict(contacts=[55], release=104))

    def test_burst_orb_contact_depends_on_speed(self):
        from pe_weapon_sim.room_modules import task_timeline
        near, far = task_timeline(156, 129, 800, 100, random.Random(1)), task_timeline(156, 129, 2500, 100, random.Random(1))
        self.assertEqual(len(near['contacts']), 1); self.assertLess(near['contacts'][0], far['contacts'][0])

    def test_sound_burst_steps_from_script_and_range(self):
        from pe_weapon_sim.room_modules import task_plan
        tp = task_plan(dict(loc='205', name='0x0020'), 3, C)
        self.assertEqual(tp['scene']['steps'], (38, 15, 192))
        self.assertEqual(len(tp['run'](900, 100, random.Random(1))['contacts']), 1)
        self.assertEqual(tp['run'](3500, 100, random.Random(1))['contacts'], [])   # hand ~442 + 38 x 64 + 200

    def test_spark_ring_and_burst_sparks(self):
        from pe_weapon_sim.room_modules import task_plan
        ring = task_plan(dict(loc='242', name='0x001F'), 3, C)
        self.assertEqual(ring['run'](1000, 100, random.Random(1))['contacts'], [36])   # captured position: stationary Aya is hit
        sparks = task_plan(dict(loc='242', name='0x001F'), 4, C)
        self.assertEqual(sparks['scene']['slot_value'], 64)
        self.assertEqual(sparks['run'](300, 100, random.Random(1))['contacts'], [])     # lands beyond her
        self.assertEqual(len(sparks['run'](600, 100, random.Random(1))['contacts']), 1)


class HomingFlashTests(unittest.TestCase):
    def test_three_phases_one_hit_and_range(self):
        from pe_weapon_sim.room_modules import task_plan, task_spec
        self.assertEqual([t for t in task_spec(163, 123)['script'] if t[0] == 2], [(2, 0, 0)] * 3)   # three controllers
        tp = task_plan(dict(loc='163', name='0x0017'), 3, C)
        self.assertEqual(tp['scene']['steps'], (80, 400, 150))
        near = tp['run'](800, 100, random.Random(1))
        self.assertEqual(len(near['contacts']), 1)                    # shared owner bits: one hit
        self.assertEqual(tp['run'](3500, 100, random.Random(1))['contacts'], [])   # 300 + 36 x 80 + 150


if __name__ == '__main__':
    unittest.main()
