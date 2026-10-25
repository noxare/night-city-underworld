"""Bounded JSON-lines proof for a future local game adapter; no engine hooks."""
import argparse
import json
import sys
from .store import WorldStore

PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 16384


class LocalBridge:
    """A process is bound to one explicit save timeline, never a global default."""

    def __init__(self, store: WorldStore, slot: str, timeline: str):
        for value in (slot, timeline):
            if not isinstance(value, str) or not value or len(value) > 128:
                raise ValueError("slot and timeline must be nonempty identifiers up to 128 characters")
        self.store = store
        self.slot = slot
        self.timeline = timeline
        # JSON tuple encoding avoids delimiter collisions and legacy slot overlap.
        self.namespace = json.dumps([slot, timeline], separators=(",", ":"), ensure_ascii=True)

    def handle(self, request: object) -> dict:
        if not isinstance(request, dict):
            raise ValueError("request must be an object")
        if set(request) != {"protocol_version", "slot", "timeline", "event"}:
            raise ValueError("unexpected or missing envelope fields")
        if type(request["protocol_version"]) is not int or request["protocol_version"] != PROTOCOL_VERSION:
            raise ValueError("unsupported protocol version")
        if request["slot"] != self.slot or request["timeline"] != self.timeline:
            raise ValueError("save context mismatch")
        event = request["event"]
        if not isinstance(event, dict) or set(event) != {"event_id", "npc_id", "kind"}:
            raise ValueError("invalid event fields")
        applied = self.store.apply(self.namespace, event)
        return {"protocol_version": PROTOCOL_VERSION, "slot": self.slot,
                "timeline": self.timeline, "event_id": event["event_id"],
                "status": "applied" if applied else "duplicate",
                "reputation": self.store.reputation(self.namespace, event["npc_id"])}


def serve(source, target, bridge: LocalBridge) -> None:
    """Binary input and text output; malformed input never terminates the stream."""
    while True:
        raw = source.readline(MAX_MESSAGE_BYTES + 1)
        if not raw:
            return
        try:
            if len(raw) > MAX_MESSAGE_BYTES:
                while raw and not raw.endswith(b"\n"):
                    raw = source.readline(MAX_MESSAGE_BYTES + 1)
                raise ValueError("message too large")
            request = json.loads(raw.decode("utf-8"))
            response = bridge.handle(request)
        except (ValueError, UnicodeError, RecursionError):
            response = {"protocol_version": PROTOCOL_VERSION, "status": "rejected",
                        "error": "invalid_request"}
        target.write(json.dumps(response, separators=(",", ":")) + "\n")
        target.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--slot", required=True)
    parser.add_argument("--timeline", required=True)
    args = parser.parse_args()
    store = WorldStore(args.database)
    try:
        serve(sys.stdin.buffer, sys.stdout, LocalBridge(store, args.slot, args.timeline))
    finally:
        store.close()


if __name__ == "__main__":
    main()
