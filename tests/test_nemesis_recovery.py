"""Explicit durable treatment, without assuming engine HP or visual recovery."""
import unittest
from unittest.mock import patch
from underworld.nemesis import NemesisStore
from tests import test_nemesis_core as fixtures

hit = fixtures.hit


def treatment(person, event="treat-1", zone="left_leg", amount=1):
    return {"event_id": event, "person_id": person, "zone": zone, "amount": amount}


class NemesisRecoveryTest(unittest.TestCase):
    setUp = fixtures.NemesisTest.setUp

    def test_both_legs_to_one_to_healthy_preserves_identity_memory_and_position(self):
        person = self.store.hit(hit())["person_id"]
        self.store.hit(hit("shot-2", zone="left_leg"))
        self.store.hit(hit("shot-3", zone="right_leg"))
        before = self.store.get(person)
        self.assertEqual(before["plan"]["gait"], "both_legs_injured")
        partial = self.store.treat(treatment(person))
        self.assertEqual(partial["remaining"], 1)
        self.assertEqual(partial["plan"]["gait"], "both_legs_injured")
        one_leg = self.store.treat(treatment(person, "treat-2", amount=512))
        self.assertEqual(one_leg["treated"], 1)
        self.assertEqual(one_leg["plan"]["gait"], "limp")
        self.assertEqual(one_leg["plan"]["injured_side"], "Right")
        healthy = self.store.treat(treatment(person, "treat-3", "right_leg"))
        self.assertEqual(healthy["plan"]["gait"], "unclassified")
        self.assertEqual(healthy["plan"]["status"], "requested_not_verified")
        after = self.store.get(person)
        self.assertEqual(after["hits"], {})
        for field in ("person_id", "appearance", "memories", "relationship", "position", "binding", "mode"):
            self.assertEqual(after[field], before[field])
        self.assertEqual(after["intent"], "escape")

    def test_treatment_persists_and_replay_does_not_heal_later_hit(self):
        person = self.store.hit(hit())["person_id"]
        event = treatment(person)
        original = self.store.treat(event)
        self.store.hit(hit("shot-again"))
        other = NemesisStore(self.path, "save-a", "branch-a")
        try:
            self.assertEqual(other.treat(event), {**original, "duplicate": True})
            self.assertEqual(other.get(person)["hits"]["left_leg"], 1)
            with self.assertRaisesRegex(ValueError, "conflicting"):
                other.treat({**event, "amount": 2})
        finally:
            other.close()

    def test_shared_event_namespace_and_save_context_guards(self):
        person = self.store.hit(hit())["person_id"]
        with self.assertRaisesRegex(ValueError, "conflicting"):
            self.store.treat(treatment(person, "shot-1"))
        other = NemesisStore(self.path, "save-b", "branch-a")
        try:
            with self.assertRaisesRegex(ValueError, "unknown"):
                other.treat(treatment(person))
        finally:
            other.close()
        self.assertFalse(self.store.treat(treatment(person))["duplicate"])

    def test_invalid_treatment_is_atomic(self):
        person = self.store.hit(hit())["person_id"]
        before = self.store.get(person)
        for changes in ({"zone": "unknown"}, {"zone": []}, {"zone": "foot"},
                        {"amount": True}, {"amount": 0}, {"amount": -1},
                        {"amount": 513}, {"amount": 1.0}, {"person_id": ""}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.store.treat({**treatment(person), **changes})
        with patch("underworld.nemesis.MAX_EVENTS", 1):
            with self.assertRaisesRegex(ValueError, "budget"):
                self.store.treat(treatment(person))
        self.assertEqual(self.store.get(person), before)
        self.assertFalse(self.store.treat(treatment(person))["duplicate"])

    def test_dead_rejection_and_old_replay_never_resurrects(self):
        person = self.store.hit(hit())["person_id"]
        event = treatment(person)
        self.store.treat(event)
        self.store.mark_dead(person)
        before = self.store.get(person)
        with self.assertRaisesRegex(ValueError, "dead"):
            self.store.treat(treatment(person, "after-death"))
        self.assertTrue(self.store.treat(event)["duplicate"])
        self.assertEqual(self.store.get(person), before)

    def test_pending_spawn_requires_reconciliation_and_offscreen_treatment_changes_speed(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1", {"x": 0, "y": 0, "z": 0},
                                 visible=False, original_gone=True)
        request = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 0,
                                           spawn_visible=False, nav_verified=True, budget_available=True)
        with self.assertRaisesRegex(ValueError, "pending spawn"):
            self.store.treat(treatment(person))
        self.store.spawn_failed(person, request["lease"]["id"], body_absent=True)
        self.store.treat(treatment(person))
        state = self.store.advance(person, 10, {"x": 100, "y": 0, "z": 0})
        self.assertEqual(state["position"]["x"], 35)
        self.assertEqual(state["mode"], "simulated")
