"""Acceso, SHA e IO exclusivos de G1. Ningún cargador de Wine/T2/C1."""
import csv
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
STAGE = ROOT/'experiments/DIN_borde/G1'
CONFIG = json.loads((STAGE/'config.json').read_text())
ARRAYS = Path(CONFIG['arrays_dir'])
RUN = STAGE/'results/run_v1'
SOURCES = {
    'core': ('docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/core.py',
             'b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd'),
    'geometry': ('docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/geometry.py',
                 'b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3'),
    'rho': ('experiments/T2_A1/fase0prima/rho_borde.py',
            'd8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b')}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


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


def write(p, v):
    data = json.dumps(clean(v), ensure_ascii=False, indent=2, allow_nan=False)
    with Path(p).open('x') as file:
        file.write(data)


def array(name, **values):
    p = ARRAYS/(name+'.npz')
    with p.open('xb') as file:
        np.savez_compressed(file, **values)
    return dict(path=str(p), sha256=sha(p), bytes=p.stat().st_size)


def frozen(name):
    path, expected = SOURCES[name]
    content = (ROOT/path).read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise RuntimeError('Fuente modificada: '+path)
    m = types.ModuleType('g1_frozen_'+name)
    m.__file__ = str(ROOT/path)
    exec(compile(content, str(ROOT/path), 'exec'), m.__dict__)
    return m


def guard():
    allowed = {str((ROOT/p).resolve()) for p, _ in SOURCES.values()}
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or p.startswith(str(STAGE)+'/') or p.startswith(str(ARRAYS)+'/'):
            return
        if '/sklearn/datasets/data/' in p and not p.endswith(('iris.csv', '.py', '.pyc')):
            raise PermissionError('G1: dataset no autorizado: '+p)
        if '/sklearn/datasets/descr/' in p and not p.endswith(('iris.rst', '.py', '.pyc')):
            raise PermissionError('G1: descripción no autorizada: '+p)
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or
                p.endswith(('.npz', '.pt', '.pth'))):
            raise PermissionError('G1: datos ajenos/prohibidos: '+p)
    sys.addaudithook(audit)


def code_guard():
    for p in sorted((STAGE/'scripts').glob('*.py')):
        rel = str(p.relative_to(ROOT))
        committed = subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT)
        if committed != p.read_bytes():
            raise RuntimeError('Código no comprometido: '+rel)
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', str(STAGE)], check=True,
                   cwd=ROOT, stdout=subprocess.DEVNULL)
    for name, (p, expected) in SOURCES.items():
        if sha(ROOT/p) != expected:
            raise RuntimeError('SHA '+name)
