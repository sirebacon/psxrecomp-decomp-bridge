"""Local debug transport for isolated live timing sessions; records every request/response."""
import argparse
import importlib.util
import json
import pathlib
import time

CLIENT = pathlib.Path('D:/Recomp Games/Parasite Eve Project/parasite-eve-recomp/psxrecomp/tools/debug_client.py')
SESSION = pathlib.Path(__file__).resolve().parents[2] / 'findings/live-timing-session'


def call(request, port=4370):
    spec=importlib.util.spec_from_file_location('pe_debug_client',CLIENT)
    client=importlib.util.module_from_spec(spec); spec.loader.exec_module(client)
    with client.connect(port=port,timeout=10) as sock:
        result=client.send_cmd(sock,dict(id=1,**request))
    SESSION.mkdir(exist_ok=True,parents=True)
    with (SESSION/'requests.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(host_ns=time.monotonic_ns(),request=request,response=result))+'\n')
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(__doc__); ap.add_argument('request'); ap.add_argument('--port',type=int,default=4370); a=ap.parse_args()
    print(json.dumps(call(json.loads(a.request),a.port),indent=1))
