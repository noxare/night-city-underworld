"""Per-save-slot durable journal with atomic duplicate-event rejection."""
import sqlite3
from pathlib import Path
from .core import evaluate

class WorldStore:
    def __init__(self, file: str | Path):
        self.conn = sqlite3.connect(str(file))
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("CREATE TABLE IF NOT EXISTS events (slot TEXT NOT NULL, event_id TEXT NOT NULL, npc_id TEXT NOT NULL, kind TEXT NOT NULL, delta INTEGER NOT NULL, explanation TEXT NOT NULL, PRIMARY KEY(slot,event_id))")
        self.conn.commit()

    def apply(self, slot: str, event: dict) -> bool:
        if not isinstance(slot, str) or not slot or len(slot) > 128:
            raise ValueError("invalid save slot")
        result = evaluate(event)
        with self.conn:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO events(slot,event_id,npc_id,kind,delta,explanation) VALUES (?,?,?,?,?,?)",
                (slot, result.event_id, result.npc_id, result.kind, result.delta, result.explanation),
            )
        return cursor.rowcount == 1

    def reputation(self, slot: str, npc_id: str) -> int:
        value = self.conn.execute("SELECT COALESCE(SUM(delta),0) FROM events WHERE slot=? AND npc_id=?", (slot,npc_id)).fetchone()[0]
        return max(-100, min(100, value))

    def close(self) -> None:
        self.conn.close()
