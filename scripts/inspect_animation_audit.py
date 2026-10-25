"""Summarize local game-resource audit metadata; never uploads full resources."""
import json
from pathlib import Path
import re
import sys

root=Path(sys.argv[1])
folders=sorted((p for p in root.iterdir() if (p/'manifest.json').is_file()),key=lambda p:p.stat().st_mtime,reverse=True)
if not folders: raise SystemExit('No audit manifest found')
folder=folders[0]
manifest=json.loads((folder/'manifest.json').read_text())
print(json.dumps({'status':manifest['status'],'archives':manifest['archives'],'resources':manifest['resources']},indent=2))
for log in list(folder.glob('archive-*/unbundle.log'))[:3]:
    raw=log.read_text(encoding='utf-8',errors='replace')
    print('UNBUNDLE_LOG',str(log.relative_to(folder)),raw[-1800:])
for path in list(folder.rglob('*.json')):
    if path.name=='manifest.json' or path.stat().st_size>16*1024*1024:continue
    try:data=json.loads(path.read_text(encoding='utf-8'))
    except (ValueError,OSError):continue
    nodes=[('',data)];matches=[];types=set();steps=0
    while nodes and steps<100000:
        pointer,value=nodes.pop();steps+=1
        if isinstance(value,dict):
            for key in ('$type','Type','type'):
                if isinstance(value.get(key),str):types.add(value[key][:100])
            nodes.extend((pointer+'/'+str(k),v) for k,v in value.items())
        elif isinstance(value,list):
            nodes.extend((pointer+'/'+str(i),v) for i,v in enumerate(value))
        elif isinstance(value,str) and re.search('wound|pain|limp|crippl|flee|fear|crowd|civilian|combat',value,re.I):
            if len(matches)<50:matches.append({'pointer':pointer[-200:],'value':value[:160]})
    print(json.dumps({'json':str(path.relative_to(folder)),'root_keys':list(data)[:12] if isinstance(data,dict) else [],'types':sorted(types)[:50],'matches':matches},indent=2))
