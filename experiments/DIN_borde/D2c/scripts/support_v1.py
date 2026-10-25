"""IO, procedencia y guardas; nada de cálculo compartido con el sujeto."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
STAGE = ROOT/'experiments/DIN_borde/D2c'
CONFIG = json.loads((STAGE/'config.json').read_text())
ARRAYS = Path(CONFIG['arrays_dir'])
SOURCES = STAGE/'sources'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def plain(v):
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, np.ndarray):
        return plain(v.tolist())
    if isinstance(v, np.generic):
        return plain(v.item())
    if isinstance(v, float) and not math.isfinite(v):
        return str(v)
    return v


def write(path, data):
    payload = json.dumps(plain(data), indent=2, allow_nan=False, ensure_ascii=False)
    with Path(path).open('x') as file:
        file.write(payload)


def arrays(name, **kwargs):
    p = ARRAYS/(name+'.npz')
    with p.open('xb') as file:
        np.savez_compressed(file, **kwargs)
    return dict(path=str(p), sha256=sha(p), bytes=p.stat().st_size)


def guard():
    allowed = {str((ROOT/p).resolve()) for p in [
        'experiments/DIN_borde/d1/d1_estados.csv', 'experiments/DIN_borde/d6/PROGRESO_d6.csv']}
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p.startswith(str(STAGE)) or p.startswith(str(ARRAYS)) or p in allowed:
            return
        if (p.startswith(str(ROOT/'experiments')) or '/checkpoints/' in p or
                '/baseline/' in p or '/comparators/' in p or '/cuarentena_X/' in p or
                p.endswith(('.pt', '.pth'))):
            raise PermissionError('D2c: lectura fuera del alcance: '+p)
    sys.addaudithook(audit)


def code_guard():
    for p in sorted((STAGE/'scripts').glob('*.py')):
        rel = str(p.relative_to(ROOT))
        committed = subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT)
        if p.read_bytes() != committed:
            raise RuntimeError('Código no comprometido: '+rel)
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', str(STAGE)], check=True,
                   cwd=ROOT, stdout=subprocess.DEVNULL)
    for row in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if '/C1/' in row['path'] or 'BORRADOR_v2' in row['path']:
            p = SOURCES/Path(row['path']).name
        else:
            p = ROOT/row['path']
        if sha(p) != row['sha256']:
            raise RuntimeError('SHA no coincide: '+str(p))


def discovery():
    d1 = list(csv.DictReader((ROOT/'experiments/DIN_borde/d1/d1_estados.csv').open()))
    d6 = list(csv.DictReader((ROOT/'experiments/DIN_borde/d6/PROGRESO_d6.csv').open()))
    late, early, at30 = {}, {}, {}
    duplicates = []
    for rows, update, target in [(d1, 250, late), (d6, 10, early), (d6, 30, at30)]:
        for row in rows:
            if int(row['update']) != update or not 12 <= int(row['split']) <= 167:
                continue
            key = row['trajectory']
            if key in target:
                duplicates.append([update, key])
            target[key] = row
    if duplicates:
        raise RuntimeError('Duplicados: '+repr(duplicates))
    joined, problems = [], []
    for key in sorted(set(late)|set(early)):
        if key not in late or key not in early:
            problems.append(dict(trajectory=key, error='missing_join'))
            continue
        e, l = early[key], late[key]
        try:
            assert int(e['split']) == int(l['split'])
            assert not e['error']
            X = math.log1p(-float(e['p_min_val']))
            L, Y = math.log(float(e['rho_borde'])), math.log(float(l['rho']))
            assert all(math.isfinite(v) for v in [X, L, Y])
        except Exception as ex:
            problems.append(dict(trajectory=key, error=repr(ex)))
            continue
        joined.append(dict(trajectory=key, split=int(e['split']), init=int(e['init']),
                           X=X, L=L, Y=Y, rho_u10=float(e['rho_borde']), rho_u250=float(l['rho']),
                           rho_u30=float(at30[key]['rho_borde']) if key in at30 else None))
    joined.sort(key=lambda r: (r['split'], r['init']))
    sp = np.array([r['split'] for r in joined])
    return dict(sp=sp, X=np.array([r['X'] for r in joined]), L=np.array([r['L'] for r in joined]),
                Y=np.array([r['Y'] for r in joined]), rows=joined, problems=problems,
                source_rows=dict(d1=len(d1), d6=len(d6)))


def input_csv(path, sp, X, L, Y, errors=None, rho_override=None):
    fields = ['trajectory', 'split', 'init', 'X', 'rho_u10', 'rho_u250', 'error']
    counts = {}
    with Path(path).open('x') as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for i, s in enumerate(sp):
            k = counts.get(int(s), 0)
            counts[int(s)] = k+1
            row = dict(trajectory=f'synthetic_s{s}_k{k}', split=int(s), init=k, X=float(X[i]),
                       rho_u10=math.exp(float(L[i])), rho_u250=math.exp(float(Y[i])),
                       error='' if errors is None else errors[i])
            if rho_override is not None and i == 0:
                row['rho_u10'] = rho_override
            writer.writerow(row)
