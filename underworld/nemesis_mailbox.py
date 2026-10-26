"""Separate real-encounter IPC; never assigns live NPCs to the synthetic demo save."""
import argparse
import json
from pathlib import Path
import time
from .mailbox import atomic_json, lock_worker
from .nemesis import NemesisStore, token


class NemesisMailbox:
    def __init__(self, directory, database, slot, timeline, session=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        if slot == "underworld-bridge-demo":
            raise ValueError("real encounters cannot use the synthetic demo context")
        self.slot, self.timeline = token(slot), token(timeline)
        self.session = token(session) if session is not None else None
        self.store = NemesisStore(database, slot, timeline)
        self.last_payload = None

    def poll(self):
        path = self.directory / "nemesis-request.json"
        try:
            with path.open("rb") as source:
                raw = source.read(16385)
        except FileNotFoundError:
            return False
        if raw == self.last_payload or len(raw) > 16384 or not raw.endswith(b"\n"):
            return False
        request = json.loads(raw)
        if not isinstance(request, dict) or set(request) != {"schema_version", "slot", "timeline", "kind", "event"}:
            raise ValueError("invalid encounter envelope")
        if type(request["schema_version"]) is not int or request["schema_version"] != 1:
            raise ValueError("unsupported encounter protocol")
        if (request["slot"], request["timeline"]) != (self.slot, self.timeline):
            raise ValueError("encounter save context mismatch")
        if self.session is not None and request["event"].get("session_id") != self.session:
            raise ValueError("game-load session mismatch")
        if request["kind"] == "hit":
            result = self.store.hit(request["event"])
        elif request["kind"] == "body_ended":
            result = self.store.end_body(request["event"])
        else:
            raise ValueError("invalid encounter operation")
        atomic_json(self.directory / "nemesis-response.json",
                    {"schema_version": 1, "slot": self.slot, "timeline": self.timeline,
                     "event_id": request["event"]["event_id"], "result": result})
        self.last_payload = raw
        return True

    def close(self):
        self.store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--slot", required=True)
    parser.add_argument("--timeline", required=True)
    parser.add_argument("--session", required=True, help="Explicit game-load nonce, retained across CET reload only")
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    args.database.parent.mkdir(parents=True, exist_ok=True)
    # Separate lock from the old demo worker.
    lock_dir = args.directory / "nemesis-worker"
    lock_dir.mkdir(exist_ok=True)
    with lock_worker(lock_dir):
        box = NemesisMailbox(args.directory, args.database, args.slot, args.timeline, args.session)
        try:
            # Explicit operator-bound context, not a claim of automatic game-save detection.
            atomic_json(args.directory / "nemesis-context.json",
                        {"schema_version": 1, "slot": args.slot, "timeline": args.timeline, "session_id": args.session})
            while True:
                try:
                    box.poll()
                except (OSError, ValueError, TypeError, KeyError) as error:
                    print("Nemesis request rejected:", type(error).__name__, flush=True)
                time.sleep(.1)
        finally:
            box.close()


if __name__ == "__main__":
    main()
