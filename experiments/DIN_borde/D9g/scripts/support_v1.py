"""IO exclusivo, SHA y guarda de acceso D9g: nunca datos C2/Wine/Iris/T2/C1."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
STAGE=ROOT/'experiments/DIN_borde/D9g'
CFG=json.loads((STAGE/'config.json').read_text())
RUN=STAGE/'results/run_v1'
ARRAYS=Path(CFG['arrays_dir'])
G3=Path(CFG['G3_arrays_dir'])


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def clean(value):
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [clean(v) for v in value]
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,np.generic):return clean(value.item())
    if isinstance(value,float) and not math.isfinite(value):return str(value)
    return value

def write(path,value):
    with Path(path).open('x') as file:
        file.write(json.dumps(clean(value),ensure_ascii=False,indent=2,allow_nan=False))

def csv_write(path,rows,fields=None):
    import csv
    if fields is None:fields=list(dict.fromkeys(key for r in rows for key in r))
    with Path(path).open('x',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
        writer.writerows({k:json.dumps(clean(v),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)

def array(name,**values):
    path=ARRAYS/(name+'.npz')
    with path.open('xb') as file:np.savez_compressed(file,**values)
    return dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size)

def frozen_C1():
    source=CFG['sources']['C1_analysis'];path=ROOT/source['path'];data=path.read_bytes()
    if sha(path)!=source['sha256']:raise RuntimeError('SHA C1')
    module=types.ModuleType('d9g_C1_code_only');module.__file__=str(path)
    exec(compile(data,str(path),'exec'),module.__dict__)
    return module

def code_guard():
    for p in [STAGE/'config.json',STAGE/'DESIGN_FROZEN.md',*sorted((STAGE/'scripts').glob('*.py'))]:
        data=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
        if data!=p.read_bytes():raise RuntimeError('Código/diseño sin commit:'+str(p))
    for name,r in CFG['sources'].items():
        if sha(ROOT/r['path'])!=r['sha256']:raise RuntimeError('Fuente modificada:'+name)

def guard():
    allowed={str((ROOT/r['path']).resolve()) for r in CFG['sources'].values()}
    prefixes=[str(STAGE.resolve())+'/',str(ARRAYS.resolve())+'/',str(G3.resolve())+'/']
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(prefix) for prefix in prefixes):return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or '/sklearn/datasets/data/' in p
            or '/sklearn/datasets/descr/' in p or p.endswith(('.npz','.npy','.pt','.pth','.csv'))):
            raise PermissionError('D9g: dato/código no autorizado:'+p)
    sys.addaudithook(audit)
