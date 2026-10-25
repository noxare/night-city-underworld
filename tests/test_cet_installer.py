import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.install_cet_demo import install


class CetInstallerTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.game = self.root / 'game'
        (self.game / 'bin/x64/plugins/cyber_engine_tweaks').mkdir(parents=True)
        (self.game / 'bin/x64/Cyberpunk2077.exe').touch()
        (self.game / 'bin/x64/version.dll').touch()
        self.source = self.root / 'source'
        self.source.mkdir()
        for name in ('init.lua', 'demo.lua'):
            (self.source / name).write_text('new-' + name)
        self.target = self.game / 'bin/x64/plugins/cyber_engine_tweaks/mods/night_city_underworld'

    def test_install_preserves_journal_and_backs_up_owned_files(self):
        self.target.mkdir(parents=True)
        (self.target / 'init.lua').write_text('old')
        (self.target / 'demo-events.jsonl').write_text('existing journal')
        result = install(self.game, self.root / 'backups', self.source)
        self.assertEqual((Path(result['backup']) / 'init.lua').read_text(), 'old')
        self.assertEqual((self.target / 'init.lua').read_text(), 'new-init.lua')
        self.assertEqual((self.target / 'demo-events.jsonl').read_text(), 'existing journal')

    def test_missing_cet_does_not_install(self):
        (self.game / 'bin/x64/version.dll').unlink()
        with self.assertRaises(ValueError):
            install(self.game, self.root / 'backups', self.source)
        self.assertFalse(self.target.exists())

    def test_copy_failure_rolls_back_both_files(self):
        self.target.mkdir(parents=True)
        (self.target / 'demo.lua').write_text('old-demo')
        import shutil
        original = shutil.copyfile
        def fail_init(source, target, **kwargs):
            if str(target).endswith('init.lua.underworld-install'):
                raise OSError('simulated disk failure')
            return original(source, target, **kwargs)
        with patch('scripts.install_cet_demo.shutil.copyfile', side_effect=fail_init):
            with self.assertRaises(OSError):
                install(self.game, self.root / 'backups', self.source)
        self.assertEqual((self.target / 'demo.lua').read_text(), 'old-demo')
        self.assertFalse((self.target / 'init.lua').exists())
        self.assertFalse(list(self.target.glob('*.underworld-install')))
