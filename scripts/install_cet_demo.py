"""Install only Underworld-owned Lua files; preserve journals and other mods."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid


def install(game: Path, backup_root: Path, source: Path) -> dict:
    if not (game / 'bin/x64/Cyberpunk2077.exe').is_file():
        raise ValueError('Cyberpunk executable not found')
    cet = game / 'bin/x64/plugins/cyber_engine_tweaks'
    if not cet.is_dir() or not (game / 'bin/x64/version.dll').is_file():
        raise ValueError('Active CET installation not found; no framework files changed')
    files = ('demo.lua', 'init.lua')
    for name in files:
        if not (source / name).is_file():
            raise ValueError('Missing packaged Lua file')
    target = cet / 'mods/night_city_underworld'
    if target.is_symlink():
        raise ValueError('Refusing symlink target')
    backup = backup_root / ('underworld-demo-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
    backup.mkdir(parents=True)
    target.mkdir(parents=True, exist_ok=True)
    receipt = {'version': '0.0.2', 'target': str(target), 'files': []}
    # Complete all backups before touching an installed Lua file.
    for name in files:
        destination = target / name
        existed = destination.exists()
        if existed:
            shutil.copy2(destination, backup / name)
        receipt['files'].append({'name': name, 'existed': existed,
                                 'sha256': hashlib.sha256((source / name).read_bytes()).hexdigest()})
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    changed = []
    try:
        for name in files:
            destination = target / name
            temporary = target / (name + '.underworld-install')
            changed.append(name)
            shutil.copyfile(source / name, temporary)
            temporary.replace(destination)
        for entry in receipt['files']:
            if hashlib.sha256((target / entry['name']).read_bytes()).hexdigest() != entry['sha256']:
                raise OSError('Installed file hash mismatch')
    except Exception:
        for name in changed:
            original = backup / name
            if original.exists():
                shutil.copy2(original, target / name)
            else:
                (target / name).unlink(missing_ok=True)
            (target / (name + '.underworld-install')).unlink(missing_ok=True)
        raise
    receipt['backup'] = str(backup)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', required=True, type=Path)
    parser.add_argument('--backup-root', required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / 'mods/night_city_underworld'
    print(json.dumps(install(args.game, args.backup_root, source), indent=2))
