"""Read-only developer dashboard for the local Underworld bridge."""
import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import time


def read_json(path):
    try:
        with path.open('rb') as source:
            raw = source.read(16385)
        if len(raw) > 16384: return None
        value = json.loads(raw)
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None


def snapshot(database: Path, directory: Path):
    health = read_json(directory / 'bridge-status.json') or {}
    beat = health.get('heartbeat', 0)
    age = max(0, time.time() - beat) if isinstance(beat, (int, float)) else None
    result = {'app': 'underworld-dashboard', 'version': '0.1.0',
              'bridge': {'online': age is not None and age < 6 and not health.get('stopped'),
                         'age_seconds': round(age, 1) if age is not None else None,
                         'version': health.get('version'), 'pid': health.get('pid')},
              'response': read_json(directory / 'bridge-response.json'),
              'npcs': [], 'events': [], 'database': 'not_found',
              'scope': 'Demo-Daten; echte NPC-Erfassung und Kampagnen-Synchronisierung fehlen noch.'}
    if not database.is_file(): return result
    try:
        with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True, timeout=1)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute('SELECT rowid AS sequence,slot,event_id,npc_id,kind,delta,explanation FROM events ORDER BY rowid DESC LIMIT 100').fetchall()
            result['events'] = [dict(row) for row in rows]
            groups = connection.execute('SELECT slot,npc_id,COUNT(*) AS event_count,SUM(delta) AS total FROM events GROUP BY slot,npc_id ORDER BY slot,npc_id LIMIT 500').fetchall()
            result['npcs'] = [{'slot': row['slot'], 'npc_id': row['npc_id'],
                               'name': 'Mara Quinn (Testkontakt)' if row['npc_id'] == 'mara-quinn-demo' else row['npc_id'],
                               'event_count': row['event_count'], 'reputation': max(-100,min(100,row['total']))}
                              for row in groups]
            result['database'] = 'read_only'
    except sqlite3.Error:
        result['database'] = 'unavailable'
    return result


PAGE = '''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Underworld · Developer Console</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#091017;color:#e4edf1;font:15px system-ui,sans-serif}main{max-width:1250px;margin:auto;padding:36px 24px}header{border-bottom:1px solid #28414e;padding-bottom:24px;display:flex;justify-content:space-between;align-items:center}h1{margin:8px 0;font-size:32px}h2{font-size:19px}.eyebrow{letter-spacing:3px;color:#5ce0ce;font-size:12px}.muted{color:#9bb0bd}section{background:#101e28;border:1px solid #263c49;border-radius:12px;padding:22px;margin-top:20px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.metric{font-size:28px;margin-top:12px}table{width:100%;border-collapse:collapse;text-align:left}td,th{padding:12px 8px;border-bottom:1px solid #263c49;vertical-align:top}th{color:#9bb0bd;font-weight:500}td{overflow-wrap:anywhere}button,input{background:#182d3b;border:1px solid #416071;color:#e4edf1;border-radius:7px;padding:10px}.badge{padding:9px 14px;border-radius:20px;background:#273742}#status[data-online="true"]{color:#5ce0ce;background:#123a36}.scroll{overflow:auto}.note{border-left:3px solid #d7a653;padding:12px 16px;background:#27251c;margin-top:24px}#error{color:#ffab9a}small{font-size:12px}@media(max-width:700px){.cards{grid-template-columns:1fr}main{padding:20px 12px}header{align-items:flex-start;gap:12px}h1{font-size:25px}}
</style><main><header><div><span class="eyebrow">NIGHT CITY : UNDERWORLD</span><h1>Developer Console</h1><div class="muted">Bridge · Kontakte · Ereignisse</div></div><span id="status" class="badge">Verbinde …</span></header>
<div class="note">Nur lesende Ansicht der lokalen Simulation. Angezeigte Kontakte sind bislang Testdaten. Keine echten NPC-Aktionen oder Spielstand-Synchronisierung.</div>
<div class="cards"><section><span class="muted">Python-Bridge</span><div class="metric" id="bridge">—</div><small id="heartbeat" class="muted"></small></section><section><span class="muted">Kontakte / Kontexte</span><div class="metric" id="count">—</div></section><section><span class="muted">Letzte Antwort</span><div class="metric" id="response">—</div><small id="request" class="muted"></small></section></div>
<section><h2>Kontakte im Kern</h2><div class="scroll"><table><thead><tr><th>Kontakt</th><th>Ruf</th><th>Ereignisse</th><th>Kontext</th></tr></thead><tbody id="npcs"></tbody></table></div></section>
<section><h2>Ereignisprotokoll</h2><p class="muted">Letzte 100 gespeicherte Ereignisse. Sequenz ist die Speicherreihenfolge; Zeitstempel werden bisher nicht erfasst.</p><input id="filter" placeholder="NPC, Ereignis oder ID filtern" aria-label="Ereignisse filtern"><div class="scroll"><table><thead><tr><th>#</th><th>Ereignis / ID</th><th>NPC</th><th>Rufänderung</th><th>Folge</th></tr></thead><tbody id="events"></tbody></table></div></section>
<p id="error"></p><p class="muted"><span id="updated">Noch keine Daten</span> · <span id="db"></span> · <button id="refresh">Aktualisieren</button></p></main>
<script>
let current=null;const el=id=>document.getElementById(id);function rows(id,data,columns){const root=el(id);root.replaceChildren();if(!data.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=columns.length;td.textContent='Noch keine gespeicherten Einträge.';tr.append(td);root.append(tr)}for(const item of data){const row=document.createElement('tr');for(const column of columns){const cell=document.createElement('td');cell.textContent=column(item);row.append(cell)}root.append(row)}}
function render(){const d=current;if(!d)return;el('status').textContent=d.bridge.online?'Bridge online':'Bridge offline';el('status').dataset.online=String(d.bridge.online);el('bridge').textContent=d.bridge.version||'Nicht gestartet';el('heartbeat').textContent=d.bridge.online?'Heartbeat vor '+d.bridge.age_seconds+' s':'Kein frischer Heartbeat';el('count').textContent=d.npcs.length;el('response').textContent=d.response?.status||'Noch keine';el('request').textContent=d.response?.request_id||'';el('db').textContent='Datenbank: '+d.database;rows('npcs',d.npcs,[x=>x.name,x=>x.reputation,x=>x.event_count,x=>x.slot]);const query=el('filter').value.toLowerCase();rows('events',d.events.filter(x=>JSON.stringify(x).toLowerCase().includes(query)),[x=>x.sequence,x=>x.kind+' / '+x.event_id,x=>x.npc_id,x=>x.delta>0?'+'+x.delta:x.delta,x=>x.explanation])}
let busy=false;async function update(){if(busy)return;busy=true;try{const r=await fetch('/api/state',{cache:'no-store',signal:AbortSignal.timeout(4000)});if(!r.ok)throw Error('HTTP '+r.status);current=await r.json();render();el('error').textContent='';el('updated').textContent='Aktualisiert '+new Date().toLocaleTimeString('de-DE')}catch(e){el('error').textContent='Dashboard-Verbindung unterbrochen: '+e.message;el('status').textContent='Daten veraltet';el('status').dataset.online='false'}finally{busy=false}}el('refresh').onclick=update;el('filter').oninput=render;update();setInterval(update,2000);
</script></html>'''


def handler(database, directory):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.headers.get('Host') not in ('localhost:8765','127.0.0.1:8765'):
                self.send_error(403); return
            if self.path == '/': content, mime = PAGE.encode(), 'text/html; charset=utf-8'
            elif self.path == '/api/state': content, mime = json.dumps(snapshot(database, directory)).encode(), 'application/json'
            else: self.send_error(404); return
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers(); self.wfile.write(content)
        def log_message(self, *args): pass
    return Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1',8765),handler(args.database,args.directory)).serve_forever()
