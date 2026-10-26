import unittest
from dataclasses import replace
from underworld.offscreen import PersistentNPC, simulate_to, leave_view, enter_view


def actor(**changes):
    base = PersistentNPC("survivor-1", "appearance-template-42", (0., 0.),
                         (30., 40.), 2., 0.)
    return replace(base, **changes)


class OffscreenTest(unittest.TestCase):
    def test_speed_and_arrival_and_replay(self):
        result = simulate_to(actor(), 10)
        self.assertAlmostEqual(result.position[0], 12.)
        self.assertAlmostEqual(result.position[1], 16.)
        self.assertEqual(simulate_to(result, 10), result)
        self.assertEqual(simulate_to(result, 50).position, (30., 40.))

    def test_visible_actor_not_moved_and_transition_reconciles_position(self):
        visible = enter_view(actor(), 10)
        self.assertEqual(simulate_to(visible, 300), visible)
        released = leave_view(visible, (12, 16), 300)
        self.assertEqual(simulate_to(released, 305).position, (18., 24.))
        self.assertEqual(released.appearance_id, visible.appearance_id)

    def test_bounded_offscreen_catchup(self):
        far = actor(destination=(100000., 0.))
        after = simulate_to(far, 86400)
        self.assertEqual(after.position, (7200., 0.))
        self.assertEqual(after.last_tick, 86400.)

    def test_invalid_inputs_do_not_mutate(self):
        original = actor()
        for bad in (-1, float('nan'), float('inf'), True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                simulate_to(original, bad)
        for bad in ((float('nan'), 0), (0,), (float('inf'), 0)):
            with self.assertRaises(ValueError):
                leave_view(original, bad, 2)
        with self.assertRaises(ValueError):
            simulate_to(actor(speed_mps=-1), 1)
        with self.assertRaises(ValueError):
            enter_view(actor(), -1)
        self.assertEqual(original.position, (0., 0.))

    def test_coordinates_are_detached_from_mutable_caller_inputs(self):
        position, destination = [0., 0.], [30., 40.]
        npc = actor(position=position, destination=destination)
        position[0] = 999
        destination[1] = 999
        self.assertEqual(npc.position, (0., 0.))
        self.assertEqual(npc.destination, (30., 40.))

    def test_visible_reentry_advances_transition_watermark_without_moving(self):
        visible = enter_view(actor(), 10)
        refreshed = enter_view(visible, 100)
        self.assertEqual(refreshed.position, visible.position)
        self.assertEqual(refreshed.last_tick, 100)
        with self.assertRaises(ValueError):
            leave_view(refreshed, (0., 0.), 20)
        self.assertEqual(enter_view(refreshed, 100), refreshed)

    def test_invalid_records_rejected_at_construction(self):
        for changes in ({'last_tick': -1}, {'visible': 1},
                        {'speed_mps': True}, {'npc_id': ''}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                actor(**changes)

    def test_extreme_numbers_fail_cleanly_without_mutation(self):
        original = actor()
        enormous = 10 ** 1000
        for changes in ({"position": (enormous, 0)}, {"last_tick": enormous},
                        {"speed_mps": enormous}):
            with self.subTest(changes=tuple(changes)), self.assertRaises(ValueError):
                actor(**changes)
        for operation in (lambda: simulate_to(original, enormous),
                          lambda: leave_view(original, (0, 0), enormous)):
            with self.assertRaises(ValueError):
                operation()
        extreme = actor(position=(-1e308, 0), destination=(1e308, 0))
        with self.assertRaisesRegex(ValueError, "movement overflow"):
            simulate_to(extreme, 10)
        self.assertEqual(original.position, (0., 0.))

    def test_large_finite_route_does_not_overflow_intermediate_product(self):
        result = simulate_to(actor(destination=(1e308, 0)), 100)
        self.assertEqual(result.position, (200., 0.))
