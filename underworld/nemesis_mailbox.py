"""Opt-in encounter IPC. Importing this module never starts or installs a worker.

The caller must provide a verified save/timeline and a nonce for the current game
load. This developer entrypoint does not discover saves or authorize actor changes.
"""
import argparse
import json
from pathlib import Path
import sqlite3
import time

from .mailbox import atomic_json, lock_worker
from .nemesis import NemesisStore, token

MAX_REQUEST_BYTES = 16384
POLL_SECONDS = 0.1


def _identifier(value):
    token(value)
    if not value.strip():
        raise ValueError("empty encounter context")
    return value


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("nonfinite JSON number")


class NemesisMailbox:
    def __init__(self, directory, database, slot, timeline, session):
        self.slot, self.timeline = _identifier(slot), _identifier(timeline)
        self.session = _identifier(session)
        if slot == "underworld-bridge-demo":
            raise ValueError("real encounters cannot use the synthetic demo context")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        database = Path(database)
        database.parent.mkdir(parents=True, exist_ok=True)
        self.store = NemesisStore(database, slot, timeline)
        self.last_payload = None
        self.last_rejected = None
        self.last_error = None

    def _handle(self, request):
        required = {"schema_version", "slot", "timeline", "kind", "event"}
        if not isinstance(request, dict) or set(request) != required:
            raise ValueError("invalid encounter envelope")
        if type(request["schema_version"]) is not int or request["schema_version"] != 1:
            raise ValueError("unsupported encounter protocol")
        if (request["slot"], request["timeline"]) != (self.slot, self.timeline):
            raise ValueError("encounter save context mismatch")
        event = request["event"]
        if not isinstance(event, dict):
            raise ValueError("invalid encounter event")
        if event.get("session_id") != self.session:
            raise ValueError("game-load session mismatch")
        if request["kind"] == "hit":
            result = self.store.hit(event)
        elif request["kind"] == "body_ended":
            result = self.store.end_body(event)
        elif request["kind"] == "treated":
            # Session authorizes this delivery, not the durable treatment ID.
            # The store validates its own exact event schema after this gate.
            result = self.store.treat({key: value for key, value in event.items() if key != "session_id"})
        else:
            raise ValueError("invalid encounter operation")
        return {"schema_version": 1, "slot": self.slot, "timeline": self.timeline,
                "event_id": event["event_id"], "result": result}

    def poll(self):
        """Read at most one bounded request; retry committed results after IO failure.

        Invalid input is remembered only in a single bounded in-memory slot. No
        success acknowledgement is published for it. SQLite's event ledger owns
        restart/retry deduplication, including commit-before-response failures.
        """
        try:
            with (self.directory / "nemesis-request.json").open("rb") as source:
                raw = source.read(MAX_REQUEST_BYTES + 1)
        except OSError:
            self.last_error = "request_unavailable"
            return False
        if raw == self.last_payload or raw == self.last_rejected:
            return False
        if len(raw) > MAX_REQUEST_BYTES or not raw.endswith(b"\n"):
            self.last_error = "request_incomplete_or_oversized"
            return False
        try:
            request = json.loads(raw.decode("utf-8"), object_pairs_hook=_object, parse_constant=_nonfinite)
            response = self._handle(request)
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
            self.last_rejected = raw
            self.last_error = "request_rejected"
            return False
        except sqlite3.Error:
            self.last_error = "database_unavailable"
            return False
        try:
            atomic_json(self.directory / "nemesis-response.json", response)
        except OSError:
            self.last_error = "response_unavailable"
            return False
        self.last_payload = raw
        self.last_rejected = None
        self.last_error = None
        return True

    def close(self):
        self.store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--slot", required=True)
    parser.add_argument("--timeline", required=True)
    parser.add_argument("--session", required=True, help="Verified current game-load nonce; never reuse after loading a save")
    args = parser.parse_args()
    # Validate before creating files; the context is always explicit operator input.
    for value in (args.slot, args.timeline, args.session):
        _identifier(value)
    if args.slot == "underworld-bridge-demo":
        parser.error("real encounters cannot use the synthetic demo context")
    args.directory.mkdir(parents=True, exist_ok=True)
    lock_dir = args.directory / "nemesis-worker"
    lock_dir.mkdir(exist_ok=True)
    with lock_worker(lock_dir):
        box = NemesisMailbox(args.directory, args.database, args.slot, args.timeline, args.session)
        try:
            atomic_json(args.directory / "nemesis-context.json",
                        {"schema_version": 1, "slot": box.slot, "timeline": box.timeline, "session_id": box.session})
            while True:
                box.poll()
                time.sleep(POLL_SECONDS)
        finally:
            box.close()


if __name__ == "__main__":
    main()
