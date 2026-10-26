"""Acceso exclusivo a piloto G3 y fuentes C1; prohibida la cohorte C2."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np
ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT/'experiments/DIN_borde/C2/potencia'
CFG = json.loads((STAGE/'config_v1.json').read_text())
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def clean(v):
    if isinstance(v, dict): return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [clean(x) for x in v]
    if isinstance(v,np.ndarray): return clean(v.tolist())
    if isinstance(v,np.generic): return clean(v.item())
    if isinstance(v,float) and not math.isfinite(v): return str(v)
    return v
def write(path,value):
    with Path(path).open('x') as f:
        f.write(json.dumps(clean(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def frozen(name):
    info=CFG['sources'][name]; p=ROOT/info['path']; data=p.read_bytes()
    if sha(p)!=info['sha256']: raise RuntimeError('Fuente modificada')
    mod=types.ModuleType('c2_power_'+name); mod.__file__=str(p)
    exec(compile(data,str(p),'exec'),mod.__dict__)
    return mod
def code_guard():
    for p in [STAGE/'config_v1.json', *sorted((STAGE/'scripts').glob('*.py'))]:
        original=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
        if p.read_bytes()!=original: raise RuntimeError('Código/config no comprometido: '+str(p))
    if sha(ROOT/CFG['pilot'])!=CFG['pilot_sha256']: raise RuntimeError('Piloto modificado')
def guard(phase='power'):
    allowed={str((ROOT/CFG['pilot']).resolve())} | {str((ROOT/s['path']).resolve()) for s in CFG['sources'].values()}
    prefixes=[str(STAGE.resolve())+'/',str(Path(CFG['power_arrays_dir']).resolve())+'/']
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)): return
        p=str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(x) for x in prefixes): return
        if p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or '/sklearn/datasets/data/' in p or p.endswith(('.npz','.npy','.pt','.pth','.csv')):
            raise PermissionError('C2 potencia: acceso no autorizado '+p)
    sys.addaudithook(audit)
