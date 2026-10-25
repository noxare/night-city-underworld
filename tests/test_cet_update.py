import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.update_cet_framework import update


class CetUpdateTest(unittest.TestCase):
    def test_update_preserves_settings_mod_and_backs_up_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            game = root / 'game'
            (game / 'bin/x64').mkdir(parents=True)
            (game / 'bin/x64/Cyberpunk2077.exe').touch()
            (game / 'bin/x64/version.dll').write_bytes(b'old')
            (game / 'bin/x64/global.ini').write_text('user-setting')
            archive = root / 'cet.zip'
            with zipfile.ZipFile(archive, 'w') as zipped:
                zipped.writestr('bin/x64/version.dll', b'new')
                zipped.writestr('bin/x64/plugins/cyber_engine_tweaks.asi', b'new')
                zipped.writestr('bin/x64/global.ini', 'default')
                zipped.writestr('bin/x64/plugins/cyber_engine_tweaks/mods/existing/init.lua', 'never replace')
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            result = update(game, root / 'backups', archive, digest)
            self.assertEqual((game / 'bin/x64/version.dll').read_bytes(), b'new')
            self.assertEqual((game / 'bin/x64/global.ini').read_text(), 'user-setting')
            self.assertEqual((Path(result['backup']) / 'bin/x64/version.dll').read_bytes(), b'old')
            self.assertFalse((game / 'bin/x64/plugins/cyber_engine_tweaks/mods/existing/init.lua').exists())

    def test_invalid_checksum_changes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'cet.zip'
            archive.write_bytes(b'wrong')
            with self.assertRaises(ValueError):
                update(root / 'game', root / 'backups', archive, 'invalid')
            self.assertFalse((root / 'backups').exists())

    def test_unsafe_archive_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'cet.zip'
            with zipfile.ZipFile(archive, 'w') as zipped:
                zipped.writestr('bin/x64/../../../outside', b'bad')
            with self.assertRaises(ValueError):
                update(root / 'game', root / 'backups', archive, hashlib.sha256(archive.read_bytes()).hexdigest())
            self.assertFalse((root / 'backups').exists())
