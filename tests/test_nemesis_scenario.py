"""File IPC + durable simulation scenario; no REDengine or appearance proof."""
import json
from pathlib import Path
import tempfile
import unittest

from underworld.nemesis_mailbox import NemesisMailbox


class NemesisScenarioTest(unittest.TestCase):
    def test_hit_streamout_background_travel_restart_and_same_person_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / 'people.sqlite3'
            def open_box():
                return NemesisMailbox(root, database, 'campaign', 'timeline', 'load-1')
            def send(box, kind, event):
                request = {'schema_version': 1, 'slot': 'campaign', 'timeline': 'timeline',
                           'kind': kind, 'event': event}
                (root / 'nemesis-request.json').write_text(json.dumps(request) + '\n')
                self.assertTrue(box.poll())
                return json.loads((root / 'nemesis-response.json').read_text())['result']
            event = {'event_id': 'shot-1', 'session_id': 'load-1', 'entity_id': 'original',
                     'zone': 'left_leg', 'zone_source': 'engine_hit_shapes', 'instigator': 'V',
                     'position': {'x': 1, 'y': 2, 'z': 3},
                     'appearance': {'record': 'crowd', 'template': 'person.ent',
                                    'appearance': 'captured-token', 'reconstruction_verified': False}}
            box = open_box()
            try:
                reply = send(box, 'hit', event)
                person = reply['person_id']
                self.assertEqual(reply['plan']['gait'], 'limp')
                # Engine owns this body until an explicit ended-body event.
                with self.assertRaises(ValueError):
                    box.store.advance_to(person, 10, {'x': 20, 'y': 2, 'z': 3})
                send(box, 'body_ended', {'event_id': 'gone-1', 'session_id': 'load-1',
                     'entity_id': 'original', 'position': {'x': 8, 'y': 2, 'z': 3}, 'dead': False})
                box.store.advance_to(person, 10, {'x': 100, 'y': 2, 'z': 3})
                moved = box.store.advance_to(person, 20, {'x': 100, 'y': 2, 'z': 3})
                self.assertAlmostEqual(moved['position']['x'], 22)
            finally:
                box.close()
            box = open_box()
            try:
                state = box.store.get(person)
                self.assertEqual(state['relationship'], 'V_injured_me')
                self.assertEqual(state['appearance'], event['appearance'])
                self.assertEqual(state['memories'][0]['event_id'], 'shot-1')
                self.assertEqual(box.store.advance_to(person, 20, {'x': 100, 'y': 2, 'z': 3}), state)
                duplicate = send(box, 'hit', event)
                self.assertTrue(duplicate['duplicate'])
                self.assertEqual(duplicate['person_id'], person)
                self.assertEqual(box.store.get(person), state)
                # A matching appearance string is deliberately insufficient for respawn.
                with self.assertRaisesRegex(ValueError, 'appearance'):
                    box.store.reserve_spawn(person, {'x': 0, 'y': 2, 'z': 3}, 21,
                        spawn_visible=False, nav_verified=True, budget_available=True)
            finally:
                box.close()
