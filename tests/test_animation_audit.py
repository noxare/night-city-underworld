import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from scripts.audit_animation_resources import inspect, PATTERN


class AnimationAuditTest(unittest.TestCase):
    def test_filtered_extraction_manifest_preserves_archive_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);game=root/'game';archives=game/'archive/pc/content'
            archives.mkdir(parents=True);(archives/'basegame_engine.archive').write_bytes(b'fixture')
            def execute(command,**kwargs):
                if command[1]=='unbundle':
                    self.assertIn('-r',command);self.assertEqual(command[-1],PATTERN)
                    output=Path(command[command.index('-o')+1]);(output/'wounded_entry_se.behavior').write_bytes(b'test')
                return SimpleNamespace(returncode=0)
            with patch('scripts.audit_animation_resources.subprocess.run',side_effect=execute):
                result=inspect(root/'console.exe',game,root/'audit')
            self.assertEqual(result['status'],'complete')
            self.assertEqual(len(result['resources']),1)
            self.assertIn('basegame_engine.archive',result['resources'][0]['archive'])
            self.assertEqual(len(result['resources'][0]['sha256']),64)
            self.assertEqual((archives/'basegame_engine.archive').read_bytes(),b'fixture')

    def test_missing_archives_are_reported_without_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            result=inspect(root/'console.exe',root/'game',root/'audit')
            self.assertEqual(result['status'],'no_matches')
