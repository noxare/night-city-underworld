from contextlib import closing
import json
from pathlib import Path
import tempfile
import time
import unittest
from underworld.dashboard import snapshot, PAGE
from underworld.mailbox import Mailbox, NPC
from underworld.observations import ingest


class DashboardTest(unittest.TestCase):
    def test_session_npc_observation_is_displayed_separately_from_demo_contacts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            value={'schema_version':1,'session_id':'live-session','identity_scope':'session_only',
                'entity_id':'real-engine-handle','observed_hits':3,'collider_tags':['raw-collider'],
                'body_zone':'unknown','animation_control':'unverified','updated_at':123,
                'enabled':True,'target_active':True,'hit_observer_registered':True}
            (root/'npc-probe.json').write_text(json.dumps(value)+'\n')
            self.assertEqual(ingest(root,root/'npc-observations.sqlite3')['status'],'ingested')
            data=snapshot(root/'world.sqlite3',root)
            self.assertEqual(data['npcs'],[])
            self.assertEqual(data['observations']['actors'][0]['observed_hits'],3)
            self.assertEqual(data['observations']['actors'][0]['body_zone'],'unknown')
            self.assertTrue(data['probe']['enabled'])
    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'missing.db'
            data=snapshot(path,Path(folder))
            self.assertEqual(data['database'],'not_found')
            self.assertFalse(path.exists())

    def test_real_journal_reputation_and_heartbeat(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            box=Mailbox(root,root/'world.db')
            try:
                box.store.apply(box.bridge.namespace,{'event_id':'one','npc_id':NPC,'kind':'civilian_helped'})
                (root/'bridge-status.json').write_text(json.dumps({'heartbeat':time.time(),'version':'0.0.2','pid':123}))
                data=snapshot(root/'world.db',root)
                self.assertTrue(data['bridge']['online'])
                self.assertEqual(data['npcs'][0]['reputation'],15)
                self.assertEqual(data['events'][0]['event_id'],'one')
                self.assertEqual(data['database'],'read_only')
                self.assertEqual(box.snapshot()['event_count'],1)
                (root/'bridge-status.json').write_text('{partial')
                self.assertFalse(snapshot(root/'world.db',root)['bridge']['online'])
            finally:box.close()
