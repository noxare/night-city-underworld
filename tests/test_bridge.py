import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from underworld.bridge import LocalBridge, MAX_MESSAGE_BYTES, serve
from underworld.store import WorldStore


def envelope(slot="save-a", timeline="branch-1", **event_changes):
    event = {"event_id": "help-1", "npc_id": "person-1", "kind": "civilian_helped"}
    event.update(event_changes)
    return {"protocol_version": 1, "slot": slot, "timeline": timeline, "event": event}


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.store = WorldStore(":memory:")
        self.addCleanup(self.store.close)
        self.bridge = LocalBridge(self.store, "save-a", "branch-1")

    def test_roundtrip_retry_and_conflicting_retry(self):
        self.assertEqual(self.bridge.handle(envelope())["reputation"], 15)
        self.assertEqual(self.bridge.handle(envelope())["status"], "duplicate")
        with self.assertRaises(ValueError):
            self.bridge.handle(envelope(kind="civilian_harmed"))
        self.assertEqual(self.bridge.handle(envelope())["reputation"], 15)

    def test_save_and_timeline_isolation(self):
        self.bridge.handle(envelope())
        for slot, timeline in [("save-b", "branch-1"), ("save-a", "branch-2")]:
            request = envelope(slot, timeline)
            with self.assertRaises(ValueError):
                self.bridge.handle(request)
            other = LocalBridge(self.store, slot, timeline)
            self.assertEqual(self.store.reputation(other.namespace, "person-1"), 0)
            self.assertEqual(other.handle(request)["status"], "applied")

    def test_envelope_validation(self):
        invalid = [None, [], {}, {**envelope(), "protocol_version": True},
                   {**envelope(), "protocol_version": 2},
                   {**envelope(), "event": []},
                   {**envelope(), "extra": 1},
                   envelope(kind="unknown"), envelope(npc_id=""),
                   envelope(event_id="x" * 129)]
        for request in invalid:
            with self.subTest(request=request), self.assertRaises(ValueError):
                self.bridge.handle(request)
        self.assertEqual(self.store.reputation(self.bridge.namespace, "person-1"), 0)

    def test_bounded_stream_recovers_after_invalid_messages(self):
        valid = json.dumps(envelope()).encode() + b"\n"
        source = io.BytesIO(b"bad json\n\xff\n" + b"x" * (MAX_MESSAGE_BYTES * 3) + b"\n" + valid + valid)
        output = io.StringIO()
        serve(source, output, self.bridge)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["status"] for r in responses],
                         ["rejected", "rejected", "rejected", "applied", "duplicate"])

    def test_reload_does_not_double_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "world.db"
            for expected in ("applied", "duplicate"):
                store = WorldStore(path)
                try:
                    result = LocalBridge(store, "save-a", "branch-1").handle(envelope())
                    self.assertEqual(result["status"], expected)
                    self.assertEqual(result["reputation"], 15)
                finally:
                    store.close()

    def test_namespace_has_no_delimiter_collisions(self):
        first = LocalBridge(self.store, "a:b", "c")
        second = LocalBridge(self.store, "a", "b:c")
        self.assertNotEqual(first.namespace, second.namespace)

    def test_legacy_database_upgrade_preserves_events(self):
        self.store.conn.execute("PRAGMA user_version=0")
        self.store.apply("legacy-save", envelope()["event"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.db"
            connection = sqlite3.connect(path)
            self.store.conn.backup(connection)
            connection.close()
            migrated = WorldStore(path)
            try:
                self.assertEqual(migrated.reputation("legacy-save", "person-1"), 15)
                self.assertEqual(migrated.conn.execute("PRAGMA user_version").fetchone()[0], 1)
            finally:
                migrated.close()

    def test_future_schema_is_rejected_without_downgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "future.db"
            with sqlite3.connect(path) as connection:
                connection.execute("PRAGMA user_version=99")
            with self.assertRaises(ValueError):
                WorldStore(path)
            with sqlite3.connect(path) as connection:
                self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 99)
