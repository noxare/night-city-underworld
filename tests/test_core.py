import tempfile
import unittest
from pathlib import Path
from underworld.core import evaluate
from underworld.store import WorldStore

class SimulationTest(unittest.TestCase):
    def test_event_roundtrip_and_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "world.sqlite3"
            event = {"event_id": "encounter-001", "npc_id": "person-004", "kind": "civilian_helped"}
            db = WorldStore(path)
            self.assertTrue(db.apply("slot-a", event))
            self.assertFalse(db.apply("slot-a", event))
            self.assertEqual(db.reputation("slot-a", "person-004"), 15)
            self.assertTrue(db.apply("slot-b", event))
            db.close()
            db = WorldStore(path)
            self.assertEqual(db.reputation("slot-a", "person-004"), 15)
            self.assertEqual(db.reputation("slot-b", "person-004"), 15)
            db.close()

    def test_harm_and_invalid_event(self):
        event = {"event_id": "hit-001", "npc_id": "person-004", "kind": "civilian_harmed"}
        self.assertEqual(evaluate(event).delta, -20)
        with self.assertRaises(ValueError):
            evaluate({"event_id": "x", "npc_id": "y", "kind": "unknown"})

if __name__ == "__main__":
    unittest.main()
