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
