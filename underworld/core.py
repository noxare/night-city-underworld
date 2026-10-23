"""Minimal deterministic event-to-consequence simulation; no game or OS dependencies."""
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Consequence:
    event_id: str
    kind: str
    npc_id: str
    delta: int
    explanation: str

def evaluate(event: dict[str, Any]) -> Consequence:
    """Convert a validated fictional gameplay event into a reproducible consequence."""
    event_id = event.get("event_id")
    npc_id = event.get("npc_id")
    kind = event.get("kind")
    if not isinstance(event_id, str) or not event_id or len(event_id) > 128:
        raise ValueError("event_id must be a non-empty string up to 128 characters")
    if not isinstance(npc_id, str) or not npc_id or len(npc_id) > 128:
        raise ValueError("npc_id must be a non-empty string up to 128 characters")
    if kind == "civilian_helped":
        return Consequence(event_id, kind, npc_id, 15, "NPC remembers receiving help")
    if kind == "civilian_harmed":
        return Consequence(event_id, kind, npc_id, -20, "NPC remembers being harmed")
    raise ValueError("unsupported event kind")
