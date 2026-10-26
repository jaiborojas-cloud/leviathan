"""Tablas inmutables por SHA; bloqueo de fuentes y cohortes externas."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
STAGE=ROOT/'experiments/DIN_borde/D9g_c'
CFG=json.loads((STAGE/'config.json').read_text())
RUN=STAGE/'results/run_v1'
ARRAYS=Path(CFG['arrays_dir'])


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    return x

def write(p,x):
    with Path(p).open('x') as f:f.write(json.dumps(clean(x),indent=2,ensure_ascii=False,allow_nan=False))

def csv_write(p,rows,fields=None):
    if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
    with Path(p).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:json.dumps(clean(v),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)

def array(name,**values):
    p=ARRAYS/(name+'.npz')
    with p.open('xb') as f:np.savez_compressed(f,**values)
    return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)

def code_guard():
    for p in [STAGE/'config.json',STAGE/'DESIGN_FROZEN.md',*sorted((STAGE/'scripts').glob('*.py'))]:
        data=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
        if data!=p.read_bytes():raise RuntimeError('Sin commit:'+str(p))
    for name,r in CFG['sources'].items():
        if sha(ROOT/r['path'])!=r['sha256']:raise RuntimeError('SHA fuente:'+name)

def guard():
    roots=[str(STAGE.resolve())+'/',str(ARRAYS.resolve())+'/']
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=str(Path(os.fsdecode(args[0])).resolve())
        if any(p.startswith(r) for r in roots):return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/workspace/work/din-' in p or '/docs/archive/' in p
            or '/sklearn/datasets/data/' in p or '/sklearn/datasets/descr/' in p or p.endswith(('.csv','.npz','.npy','.pt','.pth'))):
            raise PermissionError('D9g-c: acceso prohibido:'+p)
    sys.addaudithook(audit)
