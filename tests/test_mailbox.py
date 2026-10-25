import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from underworld.mailbox import Mailbox, SLOT, TIMELINE, NPC, atomic_json


def request(number='1', kind=None):
    return {'protocol_version': 1, 'request_id': 'request-' + number,
            'slot': SLOT, 'timeline': TIMELINE,
            'event': False if kind is None else {'event_id': 'event-' + number, 'npc_id': NPC, 'kind': kind}}


class MailboxTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.box = Mailbox(self.root / 'ipc', self.root / 'world.db')
        self.addCleanup(self.box.close)

    def test_real_file_roundtrip_and_retry_after_process_restart(self):
        value = request(kind='civilian_helped')
        atomic_json(self.box.directory / 'bridge-request.json', value)
        self.assertTrue(self.box.poll())
        response = json.loads((self.box.directory / 'bridge-response.json').read_text())
        self.assertEqual(response['state']['reputation'], 15)
        self.assertEqual(response['status'], 'applied')
        another = Mailbox(self.box.directory, self.root / 'world.db')
        try:
            self.assertTrue(another.poll())
            response = json.loads((self.box.directory / 'bridge-response.json').read_text())
            self.assertEqual(response['status'], 'duplicate')
            self.assertEqual(response['state']['reputation'], 15)
        finally:
            another.close()

    def test_preconditions_conflicts_and_context(self):
        self.assertEqual(self.box.handle(request(kind='clinic_discovered'))['status'], 'rejected')
        self.assertEqual(self.box.handle(request(kind='civilian_helped'))['status'], 'applied')
        self.assertEqual(self.box.handle(request(kind='civilian_harmed'))['status'], 'rejected')
        self.assertEqual(self.box.handle(request('2', 'shipment_investigated'))['status'], 'applied')
        result = self.box.handle(request('3', 'clinic_discovered'))
        self.assertTrue(result['state']['discovered'])
        bad = request('4', 'civilian_helped'); bad['slot'] = 'campaign'
        self.assertEqual(self.box.handle(bad)['status'], 'rejected')
        self.assertEqual(self.box.snapshot()['event_count'], 3)

    def test_partial_message_and_stale_ack_are_not_processed(self):
        path = self.box.directory / 'bridge-request.json'
        path.write_text(json.dumps(request(kind='civilian_helped')))
        self.assertFalse(self.box.poll())
        self.assertFalse((self.box.directory / 'bridge-response.json').exists())
        atomic_json(path, request(kind='civilian_helped'))
        self.assertTrue(self.box.poll())
        self.assertFalse(self.box.poll())

    def test_subprocess_restart_snapshot_and_single_worker_lock(self):
        # Exercise the actual separately running worker, not only handle().
        ipc = self.root / 'process-ipc'
        database = self.root / 'process.db'
        command = [sys.executable, '-m', 'underworld.mailbox', '--directory', str(ipc), '--database', str(database)]
        process = None
        def wait_response(request_id):
            for _ in range(100):
                try:
                    reply = json.loads((ipc / 'bridge-response.json').read_text())
                    if reply.get('request_id') == request_id: return reply
                except (OSError, ValueError): pass
                time.sleep(0.05)
            self.fail('No response from separate Python worker')
        try:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ipc.mkdir(exist_ok=True)
            atomic_json(ipc / 'bridge-request.json', request(kind='civilian_helped'))
            self.assertEqual(wait_response('request-1')['state']['reputation'], 15)
            duplicate_worker = subprocess.run(command, capture_output=True, timeout=5)
            self.assertNotEqual(duplicate_worker.returncode, 0)
            process.terminate(); process.wait(timeout=5)
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            atomic_json(ipc / 'bridge-request.json', request('snapshot'))
            reply = wait_response('request-snapshot')
            self.assertEqual(reply['state']['reputation'], 15)
            self.assertEqual(reply['state']['event_count'], 1)
        finally:
            if process is not None and process.poll() is None:
                process.terminate(); process.wait(timeout=5)
