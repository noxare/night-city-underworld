"""Local bounded file IPC for CET. Python/SQLite own all demo consequences."""
import argparse
import json
import os
from pathlib import Path
import time
import uuid
from .bridge import LocalBridge, MAX_MESSAGE_BYTES
from .store import WorldStore

VERSION = '0.0.2'
SLOT = 'underworld-bridge-demo'
TIMELINE = 'v1'
NPC = 'mara-quinn-demo'


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    data = json.dumps(value, separators=(',', ':')).encode() + b'\n'
    if len(data) > MAX_MESSAGE_BYTES:
        raise ValueError('response too large')
    with temporary.open('wb') as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


class Mailbox:
    def __init__(self, directory: Path, database: Path):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        database.parent.mkdir(parents=True, exist_ok=True)
        self.store = WorldStore(database)
        self.bridge = LocalBridge(self.store, SLOT, TIMELINE)
        self.last_payload = None

    def snapshot(self) -> dict:
        kinds = [row[0] for row in self.store.conn.execute(
            'SELECT kind FROM events WHERE slot=? AND npc_id=? ORDER BY rowid',
            (self.bridge.namespace, NPC))]
        return {'reputation': self.store.reputation(self.bridge.namespace, NPC),
                'event_count': len(kinds), 'shipment': 'civilian_helped' in kinds,
                'clinic': 'shipment_investigated' in kinds,
                'discovered': 'clinic_discovered' in kinds}

    def handle(self, request: object) -> dict:
        request_id = request.get('request_id') if isinstance(request, dict) else None
        response = {'protocol_version': 1, 'request_id': request_id, 'slot': SLOT,
                    'timeline': TIMELINE, 'server_version': VERSION}
        try:
            if not isinstance(request, dict) or set(request) != {'protocol_version', 'request_id', 'slot', 'timeline', 'event'}:
                raise ValueError('invalid_envelope')
            if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
                raise ValueError('invalid_request_id')
            if type(request['protocol_version']) is not int or request['protocol_version'] != 1:
                raise ValueError('unsupported_protocol')
            if request['slot'] != SLOT or request['timeline'] != TIMELINE:
                raise ValueError('context_mismatch')
            event = request['event']
            before = self.snapshot()
            if event is None or event is False:
                response['status'] = 'snapshot'
            else:
                if not isinstance(event, dict) or event.get('npc_id') != NPC:
                    raise ValueError('invalid_demo_actor')
                # Existing IDs must pass the core's duplicate/conflict check first.
                existing = self.store.conn.execute('SELECT 1 FROM events WHERE slot=? AND event_id=?',
                    (self.bridge.namespace, event.get('event_id') if isinstance(event.get('event_id'), str) else '')).fetchone()
                if not existing:
                    if before['event_count'] >= 100:
                        raise ValueError('demo_limit_reached')
                    if event.get('kind') == 'shipment_investigated' and (not before['shipment'] or before['clinic']):
                        raise ValueError('shipment_not_available')
                    if event.get('kind') == 'clinic_discovered' and (not before['clinic'] or before['discovered']):
                        raise ValueError('clinic_not_available')
                envelope = {key: value for key, value in request.items() if key != 'request_id'}
                response.update(self.bridge.handle(envelope))
            response['state'] = self.snapshot()
        except (ValueError, TypeError):
            response['status'] = 'rejected'
            response['error'] = 'invalid_request_or_action'
            response['state'] = self.snapshot()
        return response

    def poll(self) -> bool:
        try:
            with (self.directory / 'bridge-request.json').open('rb') as source:
                payload = source.read(MAX_MESSAGE_BYTES + 1)
        except (FileNotFoundError, PermissionError):
            return False
        if payload == self.last_payload or not payload.endswith(b'\n'):
            return False
        try:
            if len(payload) > MAX_MESSAGE_BYTES:
                return False
            request = json.loads(payload.decode('utf-8'))
        except (ValueError, UnicodeError, RecursionError):
            return False
        response = self.handle(request)
        try:
            atomic_json(self.directory / 'bridge-response.json', response)
        except PermissionError:
            # A CET reader can briefly hold the file on Windows; replay is safe.
            return False
        self.last_payload = payload
        return True

    def close(self):
        self.store.close()


def lock_worker(directory: Path):
    handle = (directory / 'bridge-worker.lock').open('a+b')
    try:
        if os.name == 'nt':
            import msvcrt
            if handle.seek(0, 2) == 0:
                handle.write(b'0'); handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise RuntimeError('An Underworld worker already owns this mailbox')
    return handle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    with lock_worker(args.directory):
        mailbox = Mailbox(args.directory, args.database)
        instance = uuid.uuid4().hex
        last_heartbeat = 0
        try:
            while True:
                mailbox.poll()
                now = time.time()
                if now - last_heartbeat >= 1:
                    try:
                        atomic_json(args.directory / 'bridge-status.json', {
                            'protocol_version': 1, 'version': VERSION, 'instance': instance,
                            'pid': os.getpid(), 'heartbeat': now, 'slot': SLOT, 'timeline': TIMELINE})
                        last_heartbeat = now
                    except PermissionError:
                        pass
                    try:
                        control = json.loads((args.directory / 'bridge-control.json').read_text())
                        if control.get('stop_instance') == instance:
                            break
                    except (OSError, ValueError):
                        pass
                time.sleep(0.1)
        finally:
            mailbox.close()
            try:
                atomic_json(args.directory / 'bridge-status.json', {
                    'version': VERSION, 'instance': instance, 'pid': os.getpid(),
                    'heartbeat': 0, 'stopped': True, 'slot': SLOT, 'timeline': TIMELINE})
            except OSError:
                pass


if __name__ == '__main__':
    main()
