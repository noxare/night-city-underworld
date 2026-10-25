"""Start the persistent local Underworld worker without depending on a CI checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def health(directory: Path):
    try:
        value = json.loads((directory / 'bridge-status.json').read_text())
        if value.get('version') == '0.0.2' and not value.get('stopped') and abs(time.time() - value['heartbeat']) < 5:
            return value
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def stop(directory: Path):
    current = health(directory)
    if not current:
        return {'stopped': True, 'message': 'No healthy Underworld worker'}
    request = directory / 'bridge-control.json'
    temporary = request.with_suffix('.tmp')
    temporary.write_text(json.dumps({'stop_instance': current['instance']}) + '\n')
    temporary.replace(request)
    for _ in range(70):
        if not health(directory):
            return {'stopped': True, 'instance': current['instance']}
        time.sleep(0.1)
    raise RuntimeError('Underworld worker did not acknowledge stop')


def start(directory: Path, database: Path, runtime: Path):
    current = health(directory)
    if current:
        return {'reused': True, **current}
    directory.mkdir(parents=True, exist_ok=True)
    database.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    # This user-owned worker intentionally outlives the CI step that installs it.
    environment.pop('RUNNER_TRACKING_ID', None)
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    with (runtime / 'bridge-worker.log').open('ab') as log:
        process = subprocess.Popen([sys.executable, '-m', 'underworld.mailbox',
            '--directory', str(directory), '--database', str(database)],
            cwd=runtime, env=environment, stdin=subprocess.DEVNULL,
            stdout=log, stderr=log, creationflags=flags, start_new_session=os.name != 'nt')
    for _ in range(100):
        current = health(directory)
        if current and current.get('pid') == process.pid:
            return {'reused': False, **current}
        if process.poll() is not None:
            raise RuntimeError('Worker exited; inspect bridge-worker.log')
        time.sleep(0.1)
    raise RuntimeError('Worker heartbeat missing; inspect bridge-worker.log')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    print(json.dumps(stop(args.directory) if args.stop else start(args.directory, args.database, args.runtime), indent=2))
