"""Start only the Underworld localhost dashboard and verify its identity."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.error import URLError


def check():
    try:
        with urlopen('http://127.0.0.1:8765/api/state',timeout=2) as response:
            data=json.load(response)
        if data.get('app') != 'underworld-dashboard': raise RuntimeError('Port 8765 belongs to another application')
        return data
    except (URLError,TimeoutError): return None


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--database',type=Path,required=True)
    p.add_argument('--directory',type=Path,required=True)
    a=p.parse_args()
    data=check()
    if data is None:
        environment=os.environ.copy();environment.pop('RUNNER_TRACKING_ID',None)
        flags=subprocess.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0
        with (a.runtime/'dashboard.log').open('ab') as log:
            process=subprocess.Popen([sys.executable,'-m','underworld.dashboard','--database',str(a.database),'--directory',str(a.directory)],cwd=a.runtime,env=environment,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=flags,start_new_session=os.name!='nt')
        for _ in range(50):
            data=check()
            if data is not None: break
            if process.poll() is not None: raise RuntimeError('Dashboard exited; inspect dashboard.log')
            time.sleep(.1)
        if data is None: raise RuntimeError('Dashboard did not respond')
    print(json.dumps({'url':'http://127.0.0.1:8765','verified':True,'bridge':data['bridge'],'npcs':len(data['npcs']),'events':len(data['events'])}))
