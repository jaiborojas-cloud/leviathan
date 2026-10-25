"""Sólo referencias sintéticas propias; IO y acceso explícitos de I2."""
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
STAGE = ROOT/'experiments/DIN_borde/I2'
CFG = json.loads((STAGE/'config.json').read_text())
ARRAYS = Path(CFG['arrays_root'])
RUN = STAGE/'results/run_v1'
GEOM = ROOT/'docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/geometry.py'
V1 = ROOT/'experiments/T2_A1/fase0prima/rho_borde.py'


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


def write(p, value):
    data = json.dumps(clean(value), ensure_ascii=False, indent=2, allow_nan=False)
    with Path(p).open('x') as f:
        f.write(data)


def array(name, **data):
    p = ARRAYS/(name+'.npz')
    with p.open('xb') as f:
        np.savez_compressed(f, **data)
    return dict(path=str(p), sha256=sha(p), bytes=p.stat().st_size)


def guard():
    allowed = {str(GEOM.resolve()), str(V1.resolve())}
    roots = [str(p.resolve())+'/' for p in [STAGE, ARRAYS, Path('/workspace/work/din-d2-v1-arrays'),
                Path('/workspace/work/din-d2b-v2-arrays'), Path('/workspace/work/din-g1-v1-arrays')]]
    permitted_stages = [str(ROOT/p)+'/' for p in ['experiments/DIN_borde/D2',
                         'experiments/DIN_borde/D2b', 'experiments/DIN_borde/G1',
                         'experiments/E16/AG', 'experiments/E16/AH']]
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(r) for r in roots+permitted_stages):
            return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p
                or '/sklearn/datasets/data/' in p or p.endswith(('.pt', '.pth', '.npz', '.npy'))):
            raise PermissionError('DIN-I2 prohíbe ese dato: '+p)
    sys.addaudithook(audit)


def code_guard():
    files = list((STAGE/'scripts').glob('*.py'))+[STAGE/'rho_borde_v2.py']
    for p in files:
        rel = str(p.relative_to(ROOT))
        if p.read_bytes() != subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT):
            raise RuntimeError('Código no comprometido: '+rel)
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', str(STAGE)], cwd=ROOT, check=True)
    for p, digest in [(GEOM, CFG['geometry_sha']), (V1, CFG['v1_sha'])]:
        if sha(p) != digest:
            raise RuntimeError('Fuente congelada cambió: '+str(p))


def v1_module():
    if sha(V1) != CFG['v1_sha']:
        raise RuntimeError('V1_SHA')
    m = types.ModuleType('i2_v1_intacto')
    m.__file__ = str(V1)
    exec(compile(V1.read_bytes(), str(V1), 'exec'), m.__dict__)
    return m


def cases():
    data = json.loads((ROOT/'experiments/DIN_borde/D2/results/run_v1/inputs.json').read_text())
    panels = {p['id']: p for p in data['panels']}
    archive = {r['state']: r for r in json.loads((ROOT/'experiments/DIN_borde/D2/results/run_v1/raw_and_references.json').read_text())}
    arrs = {r['state']: r for r in csv.DictReader((ROOT/'experiments/DIN_borde/D2/results/run_v1/arrays.csv').open()) if r['label'] == 'M'}
    q5 = {r['state']: r for r in csv.DictReader((ROOT/'experiments/DIN_borde/D2/results/run_v1/states.csv').open())}
    answer, fresh_d2 = [], set()
    for form in ['gaussian', 'interior', 'near_collinear', 'mass_face']:
        subset = [c for c in data['cases'] if c['form'] == form and c['seed'] == 2026102600]
        for kind in ['coordinate', 'constant', 'isotropic', 'random_rank1']:
            fresh_d2.add(next(c['id'] for c in subset if c['kind'] == kind))
    for c in data['cases']:
        a = arrs[c['id']]
        path = Path('/workspace/work/din-d2-v1-arrays')/a['file']
        if sha(path) != a['sha256']:
            raise RuntimeError('D2 input SHA '+c['id'])
        M = np.load(path, allow_pickle=False)
        old = archive[c['id']]
        answer.append(dict(id='D2/'+c['id'], group='D2_'+c['form'], M=M,
                           f=np.array(panels[c['panel']]['f']), case=c,
                           old_v1=old['native'], reference=old['reference']['global'],
                           old_Q5=q5[c['id']]['Q5'], fresh_v1=c['id'] in fresh_d2,
                           sensitivity=c['id'] in fresh_d2, MP_ray=c['id'] in [
                             'near_collinear/2026102600/random_rank1', 'mass_face/2026102600/random_rank1'],
                           source=dict(path=str(path), sha256=a['sha256'])))
    ag = json.loads((ROOT/'experiments/E16/AG/results/run_v1/inputs.json').read_text())
    tab = {r['state']: r for r in csv.DictReader((ROOT/'experiments/E16/AG/results/run_v1/states.csv').open())}
    first = {group: next(c['id'] for c in ag if c['group'] == group) for group in ['triangle', 'AF']}
    for c in ag:
        row = tab[c['id']]
        answer.append(dict(id='AG/'+c['id'], group='AG_'+c['group'], M=np.array(c['M']), f=np.array(c['f']),
                           old_AG_rho=float(row['rho']), d_border=float(row['d_border_exact']) if row['d_border_exact'] else None,
                           fresh_v1=True, sensitivity=c['id'] == first[c['group']],
                           MP_ray=c['id'] == first['AF'],
                           source=dict(path='experiments/E16/AG/results/run_v1/inputs.json',
                                       sha256=sha(ROOT/'experiments/E16/AG/results/run_v1/inputs.json'))))
    names = ['uniform_a1', 'uniform_a005', 'matched_q070', 'matched_q085', 'matched_pert_q070',
             'matched_pert_q085', 'grouped3', 'aligned']
    for name in names:
        p = ROOT/f'experiments/DIN_borde/D2b/results/run_v2/2026102700_{name}.json'
        old = json.loads(p.read_text())
        a = old['array']
        if sha(a['path']) != a['sha256']:
            raise RuntimeError('D2b SHA')
        with np.load(a['path'], allow_pickle=False) as z:
            M, f = z['M'].copy(), z['f'].copy()
        answer.append(dict(id='D2b/'+name, group='D2b', M=M, f=f, old_v1=dict(raw=old['native']),
                           fresh_v1=name in ['uniform_a1', 'aligned'], sensitivity=name in ['uniform_a1', 'aligned'],
                           MP_ray=False, source=a))
    for name in ['R27_s00_k0_u010', 'P60_s00_k0_u010', 'W27_s00_k0_u010', 'P60_s02_k0_u010']:
        p = ROOT/f'experiments/DIN_borde/G1/results/run_v1/states/{name}.json'
        old = json.loads(p.read_text())
        a = old['array']
        if sha(a['path']) != a['sha256']:
            raise RuntimeError('G1 SHA')
        with np.load(a['path'], allow_pickle=False) as z:
            M, f = z['M'].copy(), z['f'].copy()
        witnesses = json.loads((ROOT/f'experiments/DIN_borde/G1/results/run_v1/angular_diagnostic/{name}.json').read_text())
        answer.append(dict(id='G1/'+name, group='G1_Iris', M=M, f=f, old_G1_rho=old['rho']['rho_borde'],
                           witnesses=witnesses['rays'], fresh_v1=True, sensitivity=True,
                           MP_ray=name == 'P60_s02_k0_u010', source=a))
    if len(answer) != 302 or sum(c['fresh_v1'] for c in answer) != 102 or sum(c['sensitivity'] for c in answer) != 24:
        raise RuntimeError('Conteo fijado de inputs')
    return answer
