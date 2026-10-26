"""IO exclusivo, fuentes intactas y guarda de datos de DIN-G3."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
STAGE = ROOT/'experiments/DIN_borde/C2'
CFG = json.loads((STAGE/'cohorte/config_v1.json').read_text())
RUN = STAGE/'cohorte/run_v1'
ARRAYS = Path(CFG['arrays_dir'])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(v):
    if isinstance(v, dict):
        return {str(k): clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, np.ndarray):
        return clean(v.tolist())
    if isinstance(v, np.generic):
        return clean(v.item())
    if isinstance(v, float) and not math.isfinite(v):
        return str(v)
    return v


def write(path, value):
    encoded = json.dumps(clean(value), ensure_ascii=False, indent=2, allow_nan=False)
    with Path(path).open('x') as file:
        file.write(encoded)


def array(name, **values):
    path = ARRAYS/(name+'.npz')
    with path.open('xb') as file:
        np.savez_compressed(file, **values)
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def diagnostic(name, value):
    path = ARRAYS/(name+'.json')
    write(path, value)
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def frozen(name):
    source = CFG['sources'][name]
    path = ROOT/source['path']
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != source['sha256']:
        raise RuntimeError('Fuente modificada: '+name)
    module = types.ModuleType('c2_frozen_'+name)
    module.__file__ = str(path)
    exec(compile(content, str(path), 'exec'), module.__dict__)
    return module


def guard(phase="cohort"):
    # No código estadístico ni datos piloto están permitidos durante la cohorte.
    allowed = {str((ROOT/s['path']).resolve()) for s in CFG['sources'].values()}
    roots = [str((STAGE/'cohorte').resolve())+'/', str((STAGE/'cohorte_scripts').resolve())+'/',
             str(ARRAYS.resolve())+'/', str(Path(CFG['gate_arrays_dir']).resolve())+'/']
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(r) for r in roots):
            return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p
              or ('/sklearn/datasets/data/' in p and not p.endswith(('.py', '.pyc')))
              or ('/sklearn/datasets/descr/' in p and not p.endswith(('.py', '.pyc')))
              or p.endswith(('.npz', '.npy', '.pt', '.pth', '.csv'))):
            raise PermissionError('DIN-C2 cohorte: acceso no autorizado: '+p)
    sys.addaudithook(audit)


def code_guard():
    paths = sorted((STAGE/'cohorte_scripts').glob('*.py')) + [STAGE/'cohorte/config_v1.json', STAGE/'cohorte/c2_plan.json']
    for path in paths:
        rel = str(path.relative_to(ROOT))
        committed = subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT)
        if path.read_bytes() != committed:
            raise RuntimeError('Código/config no comprometido: '+rel)
    if sha(STAGE/'cohorte/c2_plan.json') != CFG['plan_sha256']:
        raise RuntimeError('Plan modificado')
    for name, source in CFG['sources'].items():
        if sha(ROOT/source['path']) != source['sha256']:
            raise RuntimeError('SHA fuente: '+name)
    frozen_manifest = STAGE/'MANIFIESTO_DIN_C2_v1_CONGELADO.sha256'
    for line in frozen_manifest.read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        if sha(ROOT/rel) != expected:
            raise RuntimeError('Archivo congelado modificado: '+rel)
