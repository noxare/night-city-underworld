"""Pinned official CET update; preserve settings, user mods and rollback on error."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
from datetime import datetime, timezone
import uuid
import zipfile


def update(game: Path, backup_root: Path, archive: Path, digest: str) -> dict:
    payload = archive.read_bytes()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError('CET archive checksum mismatch')
    selected = {}
    with zipfile.ZipFile(io.BytesIO(payload)) as zipped:
        if sum(item.file_size for item in zipped.infolist()) > 200 * 1024 * 1024:
            raise ValueError('CET package too large')
        for item in zipped.infolist():
            if item.is_dir():
                continue
            path = PurePosixPath(item.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in item.filename or ':' in item.filename:
                raise ValueError('Unsafe CET archive path')
            if path.parts[:2] != ('bin', 'x64'):
                raise ValueError('Unexpected CET package layout')
            relative = str(path)
            if '/mods/' in relative:
                continue
            destination = game.joinpath(*path.parts)
            # Settings/logs/databases are never replaced by a framework update.
            if destination.exists() and destination.suffix.lower() in ('.json', '.ini', '.log', '.db', '.sqlite3'):
                continue
            selected[relative] = zipped.read(item)
    for required in ('bin/x64/version.dll', 'bin/x64/plugins/cyber_engine_tweaks.asi'):
        if required not in selected:
            raise ValueError('Required CET binary missing')
    if not (game / 'bin/x64/Cyberpunk2077.exe').is_file():
        raise ValueError('Game executable missing')
    backup = backup_root / ('cet-1.38.0-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
    backup.mkdir(parents=True)
    existed = {}
    for relative in selected:
        destination = game / relative
        existed[relative] = destination.exists()
        if destination.exists():
            old = backup / relative
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, old)
    manifest = {'version': '1.38.0', 'archive_sha256': digest, 'backup': str(backup), 'files': existed}
    (backup / 'receipt.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    changed = []
    try:
        for relative, data in selected.items():
            destination = game / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            changed.append(relative)
            destination.write_bytes(data)
            if hashlib.sha256(destination.read_bytes()).digest() != hashlib.sha256(data).digest():
                raise OSError('CET installed file hash mismatch')
    except Exception:
        for relative in changed:
            if existed[relative]:
                shutil.copy2(backup / relative, game / relative)
            else:
                (game / relative).unlink(missing_ok=True)
        raise
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', required=True, type=Path)
    parser.add_argument('--backup-root', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(update(args.game, args.backup_root, args.archive, args.sha256), indent=2))
