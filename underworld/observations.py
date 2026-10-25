"""Bounded, session-scoped NPC evidence; no identity promotion or animation writes."""
from contextlib import closing
import json
import math
from pathlib import Path
import sqlite3
import time

MAX_BYTES = 16384
MAX_ACTORS = 512
REQUIRED = {'schema_version', 'session_id', 'identity_scope', 'observed_hits',
            'collider_tags', 'body_zone', 'animation_control', 'updated_at'}
FLAGS = {'enabled', 'hit_observer_registered', 'player_loaded', 'target_api_available', 'target_active'}
OPTIONAL = FLAGS | {'entity_id', 'last_hit_source', 'last_error'}


def validate(value: object) -> dict:
    if not isinstance(value, dict) or not REQUIRED <= value.keys() or value.keys() - REQUIRED - OPTIONAL:
        raise ValueError('invalid observation fields')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('unsupported observation version')
    if value['identity_scope'] != 'session_only' or value['body_zone'] != 'unknown' or value['animation_control'] != 'unverified':
        raise ValueError('unverified observation cannot assert durable identity or anatomy')
    for key in ('session_id', 'entity_id'):
        item = value.get(key)
        if key == 'entity_id' and item is None:
            continue
        if not isinstance(item, str) or not 1 <= len(item) <= 128 or any(ord(c) < 32 for c in item):
            raise ValueError('invalid observation identity')
    if type(value['observed_hits']) is not int or not 0 <= value['observed_hits'] <= 1000000000:
        raise ValueError('invalid observed hit count')
    tags = value['collider_tags']
    # CET can encode an empty Lua table as {}, but nonempty objects are not arrays.
    if isinstance(tags, dict) and not tags:
        value = {**value, 'collider_tags': []}
        tags = value['collider_tags']
    if not isinstance(tags, list) or len(tags) > 16 or any(not isinstance(tag, str) or len(tag) > 80 for tag in tags):
        raise ValueError('invalid raw collider tags')
    timestamp = value['updated_at']
    if type(timestamp) not in (int, float) or not math.isfinite(timestamp) or not 0 <= timestamp <= 1000000000000:
        raise ValueError('invalid source timestamp')
    for key in FLAGS & value.keys():
        if type(value[key]) is not bool:
            raise ValueError('invalid probe capability flag')
    if 'last_hit_source' in value and (not isinstance(value['last_hit_source'], str) or len(value['last_hit_source']) > 160):
        raise ValueError('invalid hit provenance')
    if 'last_error' in value and (not isinstance(value['last_error'], str) or len(value['last_error']) > 512):
        raise ValueError('invalid probe error')
    return value


def ingest(directory: Path, database: Path) -> dict:
    """Consume a complete probe snapshot; create storage only for a valid target."""
    directory, database = Path(directory), Path(database)
    try:
        with (directory / 'npc-probe.json').open('rb') as source:
            raw = source.read(MAX_BYTES + 1)
    except FileNotFoundError:
        return {'status': 'absent'}
    except OSError:
        return {'status': 'unavailable'}
    if len(raw) > MAX_BYTES:
        return {'status': 'invalid'}
    if not raw.endswith(b'\n'):
        return {'status': 'partial'}
    try:
        value = validate(json.loads(raw))
    except (ValueError, UnicodeError, TypeError, RecursionError):
        return {'status': 'invalid'}
    if not value.get('entity_id'):
        return {'status': 'no_target'}
    evidence = {key: item for key, item in value.items() if key != 'updated_at'}
    canonical = json.dumps(evidence, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    try:
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database, timeout=.2)) as connection:
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, 1):
                return {'status': 'unsupported_schema'}
            with connection:
                connection.execute('''CREATE TABLE IF NOT EXISTS actors (
                    session_id TEXT NOT NULL, entity_id TEXT NOT NULL, evidence TEXT NOT NULL,
                    revision INTEGER NOT NULL, source_updated_at REAL NOT NULL,
                    first_received_at REAL NOT NULL, last_received_at REAL NOT NULL,
                    PRIMARY KEY(session_id,entity_id))''')
                connection.execute('PRAGMA user_version=1')
                connection.execute('BEGIN IMMEDIATE')
                previous = connection.execute('SELECT evidence,revision,source_updated_at FROM actors WHERE session_id=? AND entity_id=?',
                    (value['session_id'], value['entity_id'])).fetchone()
                if previous and value['updated_at'] < previous[2]:
                    return {'status': 'stale', 'revision': previous[1]}
                if previous and canonical == previous[0] and value['updated_at'] == previous[2]:
                    return {'status': 'duplicate', 'revision': previous[1]}
                now = time.time()
                if previous:
                    changed = canonical != previous[0]
                    revision = previous[1] + int(changed)
                    connection.execute('UPDATE actors SET evidence=?,revision=?,source_updated_at=?,last_received_at=? WHERE session_id=? AND entity_id=?',
                        (canonical, revision, value['updated_at'], now, value['session_id'], value['entity_id']))
                    return {'status': 'updated' if changed else 'duplicate', 'revision': revision}
                if connection.execute('SELECT COUNT(*) FROM actors').fetchone()[0] >= MAX_ACTORS:
                    return {'status': 'capacity'}
                connection.execute('INSERT INTO actors VALUES (?,?,?,?,?,?,?)',
                    (value['session_id'],value['entity_id'],canonical,1,value['updated_at'],now,now))
                return {'status': 'ingested', 'revision': 1}
    except (OSError, sqlite3.Error):
        return {'status': 'unavailable'}


def read(database: Path) -> dict:
    """Read evidence without creating or modifying a missing/corrupt database."""
    database = Path(database)
    if not database.is_file():
        return {'actors': [], 'status': 'not_found'}
    try:
        with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True, timeout=.2)) as connection:
            connection.row_factory = sqlite3.Row
            if connection.execute('PRAGMA user_version').fetchone()[0] != 1:
                return {'actors': [], 'status': 'unsupported_schema'}
            rows = connection.execute('SELECT * FROM actors ORDER BY last_received_at DESC,session_id,entity_id LIMIT ?', (MAX_ACTORS,)).fetchall()
            actors = []
            for row in rows:
                evidence = json.loads(row['evidence'])
                evidence.update(revision=row['revision'], source_updated_at=row['source_updated_at'],
                    first_received_at=row['first_received_at'],last_received_at=row['last_received_at'],
                    received_at=row['last_received_at'],updated_at=row['source_updated_at'])
                actors.append(evidence)
            return {'actors': actors, 'status': 'read_only'}
    except (OSError, sqlite3.Error, ValueError, TypeError):
        return {'actors': [], 'status': 'unavailable'}
