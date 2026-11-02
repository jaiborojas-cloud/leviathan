"""Recuperación documental con respuestas inmutables; no ejecuta experimentos DIN."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import argparse
import json


def recuperar(job, out):
    ident = job['id']
    meta_path = out / (ident + '.json')
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    now = datetime.now(ZoneInfo('UTC'))
    result = dict(job, fecha_utc=now.isoformat(),
                  fecha_mexico=now.astimezone(ZoneInfo('America/Mexico_City')).isoformat(),
                  commit_protocolo='a9b85e64dc9d32bd99a593765a40b74019e7ab7d',
                  total_declarado=None, n_recuperados=None)
    data = b''
    try:
        req = Request(job['url'], headers={'User-Agent': 'Q15-literature-review/1.0 (research metadata retrieval)'})
        with urlopen(req, timeout=25) as r:
            result.update(http_status=r.status, url_final=r.url, content_type=r.headers.get('Content-Type'))
            data = r.read(32 * 1024 * 1024 + 1)
            if len(data) > 32 * 1024 * 1024:
                result.update(estado='TRUNCADA_ACCESO', error='respuesta supera 32 MiB de transporte; no es truncamiento científico')
            else:
                result['estado'] = 'RECUPERADA_PENDIENTE_PARSEAR'
    except HTTPError as e:
        data = e.read(65536)
        result.update(http_status=e.code, estado='BLOQUEADA' if e.code in (401,403,429) else 'ERROR_HTTP',error=str(e))
    except (URLError, TimeoutError, OSError) as e:
        result.update(http_status=None,estado='ERROR_ACCESO',error=str(e))
    raw_path=out/(ident+'.raw')
    with raw_path.open('xb') as f:
        f.write(data)
    result.update(bytes=len(data),artefacto=raw_path.name,sha256_artefacto=sha256(data).hexdigest())
    with meta_path.open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--jobs',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    jobs=json.loads(args.jobs.read_text())
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(lambda j:recuperar(j,args.out),jobs):
            print(json.dumps({k:result.get(k) for k in ['id','http_status','estado','bytes','error']},ensure_ascii=False),flush=True)
