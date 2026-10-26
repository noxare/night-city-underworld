import json
from pathlib import Path
import tempfile
import unittest
from underworld.nemesis import NemesisStore, reaction
from underworld.nemesis_mailbox import NemesisMailbox
from underworld.mailbox import atomic_json


def hit(event="shot-1", session="game-session", entity="crowd-1", zone="left_leg", verified=False):
    return {"event_id": event, "session_id": session, "entity_id": entity, "zone": zone,
            "zone_source": "unknown" if zone == "unknown" else "engine_hit_shapes",
            "instigator": "V", "position": {"x": 0, "y": 0, "z": 0},
            "appearance": {"record": "crowd-record", "template": "person.ent",
                           "appearance": "specific-face-outfit", "reconstruction_verified": verified}}


class NemesisTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "nemesis.db"
        self.store = NemesisStore(self.path, "save-a", "branch-a")
        self.addCleanup(self.store.close)

    def test_promotion_is_durable_idempotent_and_records_V_memory(self):
        event = hit()
        result = self.store.hit(event)
        other = NemesisStore(self.path, "save-a", "branch-a")
        try:
            again = other.hit(event)
            self.assertEqual(again["person_id"], result["person_id"])
            self.assertTrue(again["duplicate"])
            state = other.get(result["person_id"])
            self.assertEqual(state["relationship"], "V_injured_me")
            self.assertEqual(len(state["memories"]), 1)
            self.assertEqual(state["plan"]["gait"], "limp")
            self.assertEqual(state["appearance"]["appearance"], "specific-face-outfit")
        finally:
            other.close()
        with self.assertRaises(ValueError):
            self.store.hit(hit(zone="right_leg"))

    def test_shared_record_never_merges_two_people_and_context_isolated(self):
        first = self.store.hit(hit())
        second = self.store.hit(hit("shot-2", entity="crowd-2"))
        self.assertNotEqual(first["person_id"], second["person_id"])
        other = NemesisStore(self.path, "save-b", "branch-a")
        try:
            with self.assertRaises(ValueError):
                other.get(first["person_id"])
        finally:
            other.close()

    def test_unknown_zone_does_not_invent_limb_and_two_legs_do_not_run(self):
        self.assertEqual(reaction({"unknown": 3})["gait"], "unclassified")
        self.assertIsNone(reaction({"left_leg": 1, "right_leg": 1})["movement"])
        bad = hit()
        bad["zone_source"] = "unknown"
        with self.assertRaises(ValueError):
            self.store.hit(bad)
        self.store.hit(hit())
        response = self.store.hit(hit("shot-2", zone="right_leg"))
        self.assertEqual(response["plan"]["intent"], "seek_help")

    def test_offscreen_simulation_and_materialization_preserve_person_and_look(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        for visible, gone in [(True, True), (False, False), (None, True)]:
            with self.assertRaises(ValueError):
                self.store.dematerialize(person, "game-session", "crowd-1",
                                         {"x": 1, "y": 0, "z": 0}, visible=visible, original_gone=gone)
        with self.assertRaises(ValueError):
            self.store.advance(person, 1, {"x": 20, "y": 0, "z": 0})
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 1, "y": 0, "z": 0}, visible=False, original_gone=True)
        state = self.store.advance(person, 5, {"x": 20, "y": 0, "z": 0})
        self.assertAlmostEqual(state["position"]["x"], 8)
        request = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 10,
                                          spawn_visible=False, nav_verified=True, budget_available=True)
        self.assertEqual(request["appearance"]["appearance"], "specific-face-outfit")
        with self.assertRaises(ValueError):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 11,
                                     spawn_visible=False, nav_verified=True, budget_available=True)
        self.store.confirm_spawn(person, request["lease"]["id"], "game-session", "owned-1", 11)
        result = self.store.hit(hit("shot-again", entity="owned-1", verified=True))
        self.assertEqual(result["person_id"], person)
        self.assertEqual(len(self.store.get(person)["memories"]), 2)

    def test_unverified_appearance_and_dead_people_are_never_respawned(self):
        person = self.store.hit(hit())["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 0, "y": 0, "z": 0}, visible=False, original_gone=True)
        with self.assertRaisesRegex(ValueError, "appearance"):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 1,
                                     spawn_visible=False, nav_verified=True, budget_available=True)
        self.store.mark_dead(person)
        with self.assertRaises(ValueError):
            self.store.hit(hit("later"))
        with self.assertRaises(ValueError):
            self.store.advance(person, 1, {"x": 20, "y": 0, "z": 0})

    def test_expired_spawn_needs_reconciliation_and_late_ack_rejected(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 0, "y": 0, "z": 0}, visible=False, original_gone=True)
        r = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 0,
                                    spawn_visible=False, nav_verified=True, budget_available=True)
        with self.assertRaises(ValueError):
            self.store.confirm_spawn(person, r["lease"]["id"], "s", "new", 11)
        with self.assertRaises(ValueError):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 11,
                                     spawn_visible=False, nav_verified=True, budget_available=True)

    def test_body_unload_transfers_position_and_duplicate_lifecycle_is_safe(self):
        person = self.store.hit(hit())["person_id"]
        event = {"event_id": "unload-1", "session_id": "game-session", "entity_id": "crowd-1",
                 "position": {"z": 0, "x": 7, "y": 2}, "dead": False}
        self.store.end_body(event)
        self.assertTrue(self.store.end_body(event)["duplicate"])
        self.assertEqual(self.store.get(person)["mode"], "simulated")
        self.assertEqual(self.store.get(person)["position"], {"x": 7, "y": 2, "z": 0})
        event["dead"] = True
        with self.assertRaises(ValueError):
            self.store.end_body(event)

    def test_recycled_entity_id_cannot_impersonate_retired_person(self):
        person = self.store.hit(hit())["person_id"]
        self.store.end_body({"event_id": "gone", "session_id": "game-session",
                             "entity_id": "crowd-1", "position": {"x": 0, "y": 0, "z": 0}, "dead": False})
        with self.assertRaisesRegex(ValueError, "retired"):
            self.store.hit(hit("new-stranger"))
        self.assertEqual(len(self.store.get(person)["memories"]), 1)

    def test_worker_rejects_wrong_game_load_session(self):
        folder = Path(self.tmp.name) / "session-ipc"
        box = NemesisMailbox(folder, self.path, "save-a", "branch-a", session="correct-load")
        try:
            atomic_json(folder / "nemesis-request.json",
                        {"schema_version": 1, "slot": "save-a", "timeline": "branch-a",
                         "kind": "hit", "event": hit(session="wrong-load")})
            with self.assertRaisesRegex(ValueError, "session mismatch"):
                box.poll()
            self.assertFalse((folder / "nemesis-response.json").exists())
        finally:
            box.close()

    def test_actual_files_replay_ack_and_reject_demo_context(self):
        folder = Path(self.tmp.name) / "ipc"
        box = NemesisMailbox(folder, self.path, "save-a", "branch-a")
        try:
            request = {"schema_version": 1, "slot": "save-a", "timeline": "branch-a", "kind": "hit", "event": hit()}
            atomic_json(folder / "nemesis-request.json", request)
            self.assertTrue(box.poll())
            original = json.loads((folder / "nemesis-response.json").read_text())
            self.assertFalse(box.poll())
            restarted = NemesisMailbox(folder, self.path, "save-a", "branch-a")
            try:
                self.assertTrue(restarted.poll())
            finally:
                restarted.close()
            replay = json.loads((folder / "nemesis-response.json").read_text())
            self.assertEqual(replay["result"]["person_id"], original["result"]["person_id"])
            self.assertTrue(replay["result"]["duplicate"])
            request["slot"] = "wrong-save"
            atomic_json(folder / "nemesis-request.json", request)
            with self.assertRaises(ValueError):
                box.poll()
        finally:
            box.close()
        with self.assertRaises(ValueError):
            NemesisMailbox(folder, self.path, "underworld-bridge-demo", "v1")
