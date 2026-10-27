"""IO exclusivo y acceso limitado del generador de Q13."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT/'experiments/DIN_borde/Q13/cohorte'
CFG = json.loads((STAGE/'config_v1.json').read_text())
EXTERNAL = Path(CFG['arrays_root'])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as file:
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write('\n')


def archive(name, **values):
    path = EXTERNAL/(name+'.npz')
    with path.open('xb') as file:
        np.savez_compressed(file, **values)
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def frozen(name):
    s = CFG['sources'][name]
    p = ROOT/s['path']
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != s['sha256']:
        raise RuntimeError('Fuente modificada: '+name)
    mod = types.ModuleType('q13_frozen_'+name)
    mod.__file__ = str(p)
    exec(compile(data, str(p), 'exec'), mod.__dict__)
    return mod


def code_guard():
    paths = sorted((STAGE/'scripts').glob('*.py'))+[STAGE/'config_v1.json', STAGE/'PROCEDIMIENTO_v1.md']
    for p in paths:
        rel = str(p.relative_to(ROOT))
        if p.read_bytes() != subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT):
            raise RuntimeError('Código sin comprometer: '+rel)
    for s in CFG['sources'].values():
        if sha(ROOT/s['path']) != s['sha256']:
            raise RuntimeError('Fuente no intacta: '+s['path'])
    base = ROOT/'experiments/DIN_borde'
    for line in (base/'Q13/MANIFIESTO_DIN_Q13_v1_CONGELADO.sha256').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        if sha(base/rel) != expected:
            raise RuntimeError('Archivo congelado modificado: '+rel)


def guard():
    allowed = {str((ROOT/CFG['sources'][k]['path']).resolve()) for k in ('core','geometry','rho_v2')}
    roots = [str(STAGE.resolve())+'/', str(EXTERNAL.resolve())+'/']
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(r) for r in roots):
            return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or
            ('/sklearn/datasets/data/' in p and not p.endswith(('.py','.pyc'))) or
            ('/sklearn/datasets/descr/' in p and not p.endswith(('.py','.pyc'))) or
            p.endswith(('.csv','.npz','.npy','.pt','.pth'))):
            raise PermissionError('Q13 cohorte: lectura no autorizada: '+p)
    sys.addaudithook(audit)
