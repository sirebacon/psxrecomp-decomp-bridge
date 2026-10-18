import unittest
from pe_weapon_sim.source_timing import gauge_gain, refill_updates, step_gauge, switch_to_attack
from pe_weapon_sim import engine


class SourceTimingTests(unittest.TestCase):
    def test_retail_integer_order_and_status_precedence(self):
        self.assertEqual(gauge_gain(79, 2), 63)
        self.assertEqual(gauge_gain(79, 2, slow=True), 38)
        self.assertEqual(gauge_gain(79, 2, haste=True), 94)
        self.assertEqual(gauge_gain(79, 2, slow=True, haste=True), 38)

    def test_update_gates_and_ready_cap(self):
        self.assertEqual(step_gauge(8990, 79), 9000)
        self.assertEqual(step_gauge(100, 79, menu_mode=0), 100)
        self.assertEqual(step_gauge(100, 79, game_flags=0x100), 100)
        self.assertEqual(step_gauge(100, 79, menu_mode=2), 179)

    def test_borrowed_switch_keeps_overshoot_and_uses_destination_rate(self):
        r = switch_to_attack(0, 79, 63)
        self.assertEqual((r.entry_updates, r.entry_gauge, r.after_gauge), (57, 4503, 3))
        self.assertEqual(r.attack_updates, 143)
        self.assertEqual(r.total_updates, 200)

    def test_full_bar_switch_and_return_cost(self):
        current = switch_to_attack(9000, 79, 63)
        retail = switch_to_attack(9000, 79, 63, half_bar=False)
        self.assertEqual(current.after_gauge, 4500)
        self.assertEqual(current.total_updates, 72)
        self.assertEqual(retail.total_updates, 143)
        back = switch_to_attack(current.after_gauge, 63, 79)
        self.assertEqual(back.after_gauge, 0)
        self.assertEqual(back.attack_updates, 114)

    def test_borrowed_cancel_refund(self):
        r = switch_to_attack(7800, 79, 63, completed=False)
        self.assertEqual(r.after_gauge, 7800)
        self.assertEqual(r.attack_updates, 16)

    def test_source_engine_opt_in_and_stalled_rate(self):
        self.assertAlmostEqual(engine.fill_seconds(79, 2, source_steps=True), 143 / engine.TICK_HZ)
        self.assertEqual(refill_updates(9000, 0), 0)
        with self.assertRaises(ValueError):
            refill_updates(0, 0)
