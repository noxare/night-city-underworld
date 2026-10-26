import json
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from underworld.mailbox import atomic_json
from underworld.nemesis_mailbox import NemesisMailbox, MAX_REQUEST_BYTES


def hit(event_id="hit-1"):
    return {"event_id": event_id, "session_id": "load-1", "entity_id": "crowd-1",
            "zone": "left_leg", "zone_source": "engine_hit_shapes", "instigator": "V",
            "position": {"x": 0, "y": 0, "z": 0},
            "appearance": {"record": "crowd-record", "template": "npc.ent",
                           "appearance": "face-outfit", "reconstruction_verified": False}}


def envelope(event=None, **changes):
    request = {"schema_version": 1, "slot": "save-1", "timeline": "branch-1",
               "kind": "hit", "event": hit() if event is None else event}
    request.update(changes)
    return request


class NemesisMailboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name) / "ipc"
        self.database = Path(self.tmp.name) / "state" / "nemesis.db"
        self.box = self.open_box()
        self.addCleanup(self.box.close)

    def open_box(self, **changes):
        args = dict(directory=self.directory, database=self.database,
                    slot="save-1", timeline="branch-1", session="load-1")
        args.update(changes)
        return NemesisMailbox(**args)

    def send(self, request):
        atomic_json(self.directory / "nemesis-request.json", request)

    def response(self):
        return json.loads((self.directory / "nemesis-response.json").read_text())

    def count(self):
        return self.box.store.conn.execute("SELECT COUNT(*) FROM nemesis_events").fetchone()[0]

    def test_real_files_restart_replay_and_body_ended(self):
        self.send(envelope())
        self.assertTrue(self.box.poll())
        first = self.response()
        self.assertFalse(self.box.poll())
        restarted = self.open_box()
        try:
            self.assertTrue(restarted.poll())
            replay = self.response()
            self.assertEqual(replay["result"]["person_id"], first["result"]["person_id"])
            self.assertTrue(replay["result"]["duplicate"])
        finally:
            restarted.close()
        event = {"event_id": "gone-1", "session_id": "load-1", "entity_id": "crowd-1",
                 "position": {"x": 8, "y": 2, "z": 0}, "dead": False}
        self.send(envelope(event, kind="body_ended"))
        self.assertTrue(self.box.poll())
        self.assertEqual(self.response()["result"]["mode"], "simulated")
        state = self.box.store.get(first["result"]["person_id"])
        self.assertEqual(state["position"]["x"], 8)
        self.assertEqual(len(state["memories"]), 1)

    def test_response_failure_retries_committed_event_without_double_hit(self):
        self.send(envelope())
        with patch("underworld.nemesis_mailbox.atomic_json", side_effect=PermissionError("busy reader")):
            self.assertFalse(self.box.poll())
        self.assertEqual(self.box.last_error, "response_unavailable")
        self.assertEqual(self.count(), 1)
        self.assertIsNone(self.box.last_payload)
        self.assertTrue(self.box.poll())
        response = self.response()
        self.assertTrue(response["result"]["duplicate"])
        self.assertEqual(len(self.box.store.get(response["result"]["person_id"])["memories"]), 1)

    def test_wrong_save_timeline_session_and_schema_never_mutate(self):
        bad = [envelope(slot="save-2"), envelope(timeline="branch-2"), envelope(schema_version=True),
               envelope({**hit(), "session_id": "old-load"}), envelope(kind="spawn")]
        for request in bad:
            self.send(request)
            self.assertFalse(self.box.poll())
            self.assertEqual(self.box.last_error, "request_rejected")
        self.assertEqual(self.count(), 0)
        self.assertFalse((self.directory / "nemesis-response.json").exists())

    def test_malformed_input_is_bounded_and_valid_next_request_recovers(self):
        path = self.directory / "nemesis-request.json"
        malformed = [b'not json\n', b'\xff\n', b'[]\n', b'{"a":1,"a":2}\n',
                     b'[' * 1100 + b']' * 1100 + b'\n',
                     b' ' * (MAX_REQUEST_BYTES + 1) + b'\n']
        for raw in malformed:
            path.write_bytes(raw)
            self.assertFalse(self.box.poll())
            self.assertFalse(self.box.poll())
        for event in ([], "bad", 42, None):
            self.send(envelope(event=hit()) | {"event": event})
            self.assertFalse(self.box.poll())
        self.send(envelope({**hit(), "zone": []}))
        self.assertFalse(self.box.poll())
        self.assertEqual(self.count(), 0)
        self.send(envelope())
        self.assertTrue(self.box.poll())
        self.assertIsNone(self.box.last_error)

    def test_partial_write_then_completion_and_nonfinite_rejected(self):
        path = self.directory / "nemesis-request.json"
        raw = json.dumps(envelope()).encode()
        path.write_bytes(raw)
        self.assertFalse(self.box.poll())
        self.assertEqual(self.count(), 0)
        path.write_bytes(raw + b'\n')
        self.assertTrue(self.box.poll())
        request = envelope(hit("hit-2"))
        request["event"]["position"]["x"] = float('nan')
        path.write_text(json.dumps(request) + '\n')
        self.assertFalse(self.box.poll())
        self.assertEqual(self.count(), 1)

    def test_context_is_required_and_rejected_before_creating_files(self):
        for changes in ({"slot": "underworld-bridge-demo"}, {"session": None},
                        {"slot": " "}, {"timeline": ""}, {"session": " "}):
            folder = Path(self.tmp.name) / "must-not-exist"
            with self.assertRaises(ValueError):
                self.open_box(directory=folder, **changes)
            self.assertFalse(folder.exists())
        self.assertFalse((self.directory / "nemesis-context.json").exists())

    def test_conflicting_replay_does_not_replace_previous_ack_or_person(self):
        self.send(envelope())
        self.assertTrue(self.box.poll())
        first = self.response()
        self.send(envelope({**hit(), "zone": "right_leg"}))
        self.assertFalse(self.box.poll())
        self.assertEqual(self.response(), first)
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.box.store.get(first["result"]["person_id"])["hits"], {"left_leg": 1})


    def test_transient_database_error_retries_same_request(self):
        self.send(envelope())
        with patch.object(self.box.store, "hit", side_effect=sqlite3.OperationalError("busy")):
            self.assertFalse(self.box.poll())
        self.assertEqual(self.box.last_error, "database_unavailable")
        self.assertEqual(self.count(), 0)
        self.assertTrue(self.box.poll())
        self.assertEqual(self.count(), 1)


    def test_treatment_delivery_requires_load_context_and_replays_after_restart(self):
        self.send(envelope())
        self.assertTrue(self.box.poll())
        person = self.response()["result"]["person_id"]
        treatment = {"event_id": "treat-1", "session_id": "wrong-load", "person_id": person,
                     "zone": "left_leg", "amount": 1}
        self.send(envelope(treatment, kind="treated"))
        self.assertFalse(self.box.poll())
        self.assertEqual(self.box.store.get(person)["hits"]["left_leg"], 1)
        treatment["session_id"] = "load-1"
        self.send(envelope(treatment, kind="treated"))
        self.assertTrue(self.box.poll())
        self.assertEqual(self.response()["result"]["treated"], 1)
        self.assertEqual(self.response()["result"]["remaining"], 0)
        restarted = self.open_box()
        try:
            self.assertTrue(restarted.poll())
            self.assertTrue(self.response()["result"]["duplicate"])
            self.assertEqual(self.response()["result"]["treated"], 1)
        finally:
            restarted.close()
        self.assertEqual(self.count(), 2)
