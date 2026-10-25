"""Read-only, bounded animation-resource extraction using verified WolvenKit CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

PATTERN = r'(^|[\\/])(hit_reactions|wounded_entry_se)\.behavior$|(^|[\\/])humanoid\.animgraph$'
MAX_BYTES = 128 * 1024 * 1024


def inspect(cli, game, output):
    output.mkdir(parents=True, exist_ok=False)
    candidates=[]
    for root in (game/'archive/pc/content', game/'archive/pc/ep1'):
        if root.is_dir(): candidates.extend(root.glob('*.archive'))
    candidates.sort(key=lambda p: (not any(x in p.name.lower() for x in ('patch','engine','gamedata')),p.name))
    manifest={'pattern':PATTERN,'archives':[],'resources':[],'status':'running'}
    started=time.monotonic()
    def save():
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    save()
    for index,archive in enumerate(candidates[:40]):
        if time.monotonic()-started>480:
            manifest['status']='time_budget';break
        destination=output/('archive-'+str(index))
        destination.mkdir()
        record={'archive':str(archive),'size':archive.stat().st_size,'modified':archive.stat().st_mtime}
        manifest['archives'].append(record)
        with (destination/'unbundle.log').open('wb') as log:
            try:
                result=subprocess.run([str(cli),'unbundle','-p',str(archive),'-o',str(destination),'-gp',str(game),'-r',PATTERN],
                    stdout=log,stderr=subprocess.STDOUT,timeout=90,check=False)
                record['exit_code']=result.returncode
            except subprocess.TimeoutExpired:
                record['timeout']=True;save();continue
        files=[p for p in destination.rglob('*') if p.is_file() and p.suffix in ('.behavior','.animgraph')]
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>MAX_BYTES:
            manifest['status']='size_budget';save();break
        for path in files[:16]:
            if time.monotonic()-started>480:
                manifest['status']='time_budget';save();return manifest
            resource={'path':str(path.relative_to(output)),'archive':str(archive),'size':path.stat().st_size,
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            manifest['resources'].append(resource)
            if path.suffix=='.behavior' and path.stat().st_size<4*1024*1024:
                with path.with_suffix(path.suffix+'.conversion.log').open('wb') as log:
                    try:
                        result=subprocess.run([str(cli),'convert','serialize',str(path)],stdout=log,stderr=subprocess.STDOUT,timeout=45)
                        resource['convert_exit']=result.returncode
                    except subprocess.TimeoutExpired:resource['convert_timeout']=True
                if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>MAX_BYTES:
                    manifest['status']='size_budget';save();return manifest
        save()
    if manifest['status']=='running':
        manifest['status']='complete' if manifest['resources'] else ('command_failed' if any(x.get('exit_code',0)!=0 or x.get('timeout') for x in manifest['archives']) else 'no_matches')
    # Summarize relevant text references without publishing game-resource contents.
    refs=set()
    for path in output.rglob('*.json'):
        if path.name=='manifest.json' or path.stat().st_size>8*1024*1024:continue
        text=path.read_text(encoding='utf-8',errors='replace')
        for value in re.findall(r'[^"\r\n]{0,120}(?:wounded|injured|limp|PainReactionTask|Crippled)[^"\r\n]{0,120}',text,re.I):
            refs.add(value[:240])
            if len(refs)>=80:break
    manifest['reference_candidates']=sorted(refs)[:80]
    save()
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cli',type=Path,required=True);p.add_argument('--game',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    data=inspect(a.cli,a.game,a.output)
    print(json.dumps({'status':data['status'],'archives_checked':len(data['archives']),'resources':data['resources'],
                      'reference_candidates':data.get('reference_candidates',[])},indent=2))
