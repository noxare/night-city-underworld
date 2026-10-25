import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from underworld.observations import ingest, read


def observation(**changes):
    value = dict(schema_version=1, session_id='session-a', identity_scope='session_only',
        entity_id='123ULL', observed_hits=2, collider_tags=['raw-leg-collider'],
        body_zone='unknown', animation_control='unverified', updated_at=100,
        enabled=True, hit_observer_registered=True)
    value.update(changes)
    return value


class ObservationTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.db = self.root / 'npc-observations.sqlite3'

    def write(self, value):
        (self.root / 'npc-probe.json').write_text(json.dumps(value) + '\n')

    def test_persistence_dedup_and_raw_provenance(self):
        self.write(observation())
        self.assertEqual(ingest(self.root,self.db), {'status':'ingested','revision':1})
        self.assertEqual(ingest(self.root,self.db), {'status':'duplicate','revision':1})
        result = read(self.db)
        self.assertEqual(result['status'],'read_only')
        self.assertEqual(len(result['actors']),1)
        actor = result['actors'][0]
        self.assertEqual(actor['body_zone'],'unknown')
        self.assertEqual(actor['source_updated_at'],100)
        self.assertGreater(actor['first_received_at'],100)
        self.write(observation(updated_at=101))
        self.assertEqual(ingest(self.root,self.db), {'status':'duplicate','revision':1})
        self.write(observation(observed_hits=3,updated_at=102))
        self.assertEqual(ingest(self.root,self.db), {'status':'updated','revision':2})

    def test_cross_session_identity_and_stale_snapshot(self):
        self.write(observation())
        ingest(self.root,self.db)
        self.write(observation(session_id='session-b'))
        ingest(self.root,self.db)
        self.assertEqual(len(read(self.db)['actors']),2)
        self.write(observation(updated_at=99,observed_hits=90))
        self.assertEqual(ingest(self.root,self.db)['status'],'stale')
        self.assertEqual(read(self.db)['actors'][1]['observed_hits'],2)

    def test_invalid_or_no_target_creates_no_database(self):
        for changes in ({'schema_version':True},{'collider_tags':['x']*17},
                        {'collider_tags':{'unexpected':'tag'}},{'observed_hits':-1},{'body_zone':'left_leg'},
                        {'updated_at':float('nan')},{'extra':'unexpected'}):
            self.write(observation(**changes))
            self.assertEqual(ingest(self.root,self.db)['status'],'invalid')
            self.assertFalse(self.db.exists())
        value=observation();value.pop('entity_id')
        self.write(value)
        self.assertEqual(ingest(self.root,self.db)['status'],'no_target')
        self.assertFalse(self.db.exists())
        self.assertEqual(read(self.db),{'actors':[],'status':'not_found'})
        self.assertFalse(self.db.exists())

    def test_partial_and_oversize_snapshots_do_not_overwrite_evidence(self):
        self.write(observation());ingest(self.root,self.db)
        path=self.root/'npc-probe.json'
        path.write_text('{partial')
        self.assertEqual(ingest(self.root,self.db)['status'],'partial')
        path.write_bytes(b'x'*16385+b'\n')
        self.assertEqual(ingest(self.root,self.db)['status'],'invalid')
        self.assertEqual(read(self.db)['actors'][0]['revision'],1)

    def test_future_schema_is_preserved(self):
        self.write(observation())
        with sqlite3.connect(self.db) as connection:
            connection.execute('PRAGMA user_version=99')
        # Explicit close matters for Windows temporary-directory cleanup.
        connection.close()
        self.assertEqual(ingest(self.root,self.db)['status'],'unsupported_schema')
        self.assertEqual(read(self.db)['status'],'unsupported_schema')

    def test_cet_empty_table_compatibility_and_probe_flags(self):
        self.write(observation(collider_tags={},target_active=True,player_loaded=True,
            target_api_available=True,last_error='sample probe warning'))
        self.assertEqual(ingest(self.root,self.db)['status'],'ingested')
        actor=read(self.db)['actors'][0]
        self.assertEqual(actor['collider_tags'],[])
        self.assertTrue(actor['target_active'])
        self.assertEqual(actor['last_error'],'sample probe warning')
