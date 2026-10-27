"""Auditoría sólo sintética: snapshots por SHA y escrituras exclusivas."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13DR/auditoria'
CFG=json.loads((STAGE/'config.json').read_text())
EXTERNAL=Path(CFG['arrays_dir'])


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    return x


def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(clean(x),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')


def code_guard():
    for p in sorted((STAGE/'scripts').glob('*.py'))+[STAGE/'config.json',STAGE/'DESIGN_FROZEN.md']:
        if subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)!=p.read_bytes():raise RuntimeError('Código no comprometido:'+str(p))
    for r in json.loads((STAGE/'sources/provenance.json').read_text())['sources']:
        if sha(ROOT/r['snapshot_path'])!=r['sha256']:raise RuntimeError('Snapshot modificado')


def guard(extra=None):
    roots=[STAGE.resolve(),EXTERNAL.resolve()]+([Path(extra).resolve()] if extra else [])
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if any(p.is_relative_to(r) for r in roots):return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('Auditoría Q13DR: datos externos prohibidos:'+str(p))
    sys.addaudithook(audit)


def target():
    p=STAGE/'sources/Q13DR/analisis_Q13DR.py'
    spec=importlib.util.spec_from_file_location('q13dr_audited_snapshot',p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def wilson(k,n):
    if n==0:return dict(k=0,n=0,rate=None,lower=None,upper=None)
    z=1.959963984540054;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(k=int(k),n=int(n),rate=p,lower=mid-half,upper=mid+half)
