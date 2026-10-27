"""Fuentes intactas, IO exclusivo y acceso limitado de calibración M2."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/calibracion'
CFG=json.loads((STAGE/'config_v1.json').read_text())
OUT=STAGE/'results_v1'
EXTERNAL=Path(CFG['arrays_root'])


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')


def archive(name,**values):
    p=EXTERNAL/(name+'.npz')
    with p.open('xb') as f:np.savez_compressed(f,**values)
    return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)


def frozen(name):
    s=CFG['sources'][name];p=ROOT/s['path'];data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=s['sha256']:raise RuntimeError('Fuente modificada:'+name)
    m=types.ModuleType('m2_frozen_'+name);m.__file__=str(p);exec(compile(data,str(p),'exec'),m.__dict__);return m


def code_guard():
    paths=list((STAGE/'scripts').glob('*.py'))+[STAGE/'config_v1.json',STAGE/'PROCEDIMIENTO_v1_CONGELADO.md']
    for p in paths:
        if p.read_bytes()!=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT):raise RuntimeError('Código sin comprometer:'+str(p))
    for s in CFG['sources'].values():
        if sha(ROOT/s['path'])!=s['sha256']:raise RuntimeError('SHA fuente:'+s['path'])
    assert (STAGE/'scripts/recipe_v1.py').read_bytes()==(ROOT/CFG['sources']['recipe']['path']).read_bytes()
    assert (STAGE/'fuentes/support_v1.py').read_bytes()==(ROOT/CFG['sources']['support']['path']).read_bytes()
    versions={k:importlib.metadata.version(k) for k in CFG['versions']}
    if versions!=CFG['versions']:raise RuntimeError('Versiones incorrectas:'+str(versions))
    return versions


def guard():
    allowed={(ROOT/CFG['sources'][k]['path']).resolve() for k in ('core','geometry')}
    roots=[STAGE.resolve(),EXTERNAL.resolve()]
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p in allowed or any(p.is_relative_to(r) for r in roots):return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('M2 calibración: acceso no autorizado:'+str(p))
        parts={x.lower() for x in p.parts}
        if 'datasets' in parts and ('data' in parts or 'descr' in parts) and p.suffix.lower() not in ('.py','.pyc'):
            raise PermissionError('M2: datos externos prohibidos:'+str(p))
    sys.addaudithook(audit)
