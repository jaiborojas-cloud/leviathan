"""Integridad y reconstrucción selectiva. No entrena ni repite rho."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from support_v1 import ROOT, STAGE, RUN, ARRAYS, CONFIG, SOURCES, sha, frozen, guard, write
from analysis_v1 import predictive_D, event, spearman
from metrics_v1 import rho_quality


def main():
    errors, checks = [], {}
    files = list(csv.DictReader((STAGE/'manifest.csv').open()))
    for row in files:
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Manifest: '+row['path'])
    checks['manifest_files'] = len(files)
    external = list(csv.DictReader((STAGE/'external_manifest.csv').open()))
    for row in external:
        if sha(row['path']) != row['sha256']:
            errors.append('Externo: '+row['path'])
    checks['external_files'] = len(external)
    for row in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Fuente/contexto: '+row['path'])
    for name in ['implementation_manifest_v1.csv', 'postprocess_manifest_v1.csv']:
        for row in csv.DictReader((STAGE/name).open()):
            if sha(ROOT/row['path']) != row['sha256']:
                errors.append('Código: '+row['path'])
    original_design = subprocess.check_output(['git', 'show', 'bb7fedf:experiments/DIN_borde/G1/DESIGN_FROZEN.md'], cwd=ROOT)
    if original_design != (STAGE/'DESIGN_FROZEN.md').read_bytes():
        errors.append('Diseño alterado')
    env = json.loads((RUN/'environment.json').read_text())
    subprocess.run(['git', 'merge-base', '--is-ancestor', 'bb7fedf', env['code_commit']], cwd=ROOT, check=True)
    if env['code_commit'] != subprocess.check_output(['git', 'rev-parse', '28c6395'], cwd=ROOT, text=True).strip():
        errors.append('Orden de código/ejecución inesperado')
    checks['design_commit'] = 'bb7fedf'
    checks['measurement_code_commit'] = env['code_commit']
    guard()
    with np.load(ARRAYS/'dataset_iris.npz', allow_pickle=False) as z:
        rawX, rawy = z['X'], z['y']
    if rawX.shape != (150, 4) or set(rawy) != {0, 1, 2}:
        errors.append('Dataset Iris inesperado')
    splitdata = {}
    for s in range(20):
        with np.load(ARRAYS/f'split_{s:02}.npz', allow_pickle=False) as z:
            data = {key: z[key].copy() for key in z.files}
        splitdata[s] = data
        tr, va, pp = data['train_ids'], data['pool_ids'], data['panel27_ids']
        if len(tr) != 90 or len(va) != 60 or len(pp) != 27 or len(set(tr)&set(va)):
            errors.append('Partición: '+str(s))
        if not set(pp).issubset(va) or not np.array_equal(np.bincount(rawy[pp]), [9, 9, 9]):
            errors.append('Panel anidado: '+str(s))
        if not np.allclose(data['Z'][tr].mean(0), 0, atol=1e-12):
            errors.append('Scaler mean: '+str(s))
        if not np.allclose(data['Z'][tr].var(0), 1, atol=1e-12):
            errors.append('Scaler variance: '+str(s))
        if not np.allclose(data['Z'], (rawX-data['scaler_mean'])/data['scaler_scale'], atol=1e-12):
            errors.append('Scaler raw: '+str(s))
    checks['splits_checked'] = 20
    rows = [json.loads(p.read_text()) for p in sorted((RUN/'states').glob('*.json'))]
    by = {(r['family'], r['split'], r['initialization'], r['update']): r for r in rows}
    expected = {(f, s, k, t) for f in ['R27', 'P60', 'W27'] for s in range(20) for k in range(5)
                for t in CONFIG['updates']}
    if set(by) != expected or len(rows) != 2100:
        errors.append('No se conserva el universo2100')
    measured = 0
    audited = 0
    for r in rows:
        if r['status'] != 'MEASURED':
            continue
        measured += 1
        with np.load(r['array']['path'], allow_pickle=False) as z:
            M, f, ids = z['M'], z['f'], z['panel_ids']
            intended = splitdata[r['split']]['pool_ids' if r['family'] == 'P60' else 'panel27_ids']
            if not np.array_equal(ids, intended):
                errors.append('IDs: '+r['id'])
            if not np.array_equal(f, splitdata[r['split']]['Z'][ids, :2]):
                errors.append('f: '+r['id'])
            tr = np.trace(M)
            q = np.linalg.norm(M-np.diag(np.diag(M)))/np.linalg.norm(M)
            c = np.diag(M).max()/tr
            m = r['metrics']
            if tr > 0 and (abs(c-m['c']) > 1e-12 or abs(q-m['q']) > 1e-12):
                errors.append('c/q: '+r['id'])
            if r['rho_valid'] != bool(m['M_valid'] and rho_quality(r.get('rho'), m['chord']['value'])):
                errors.append('Calidad rho: '+r['id'])
            if m['collapsed'] != bool(m['M_valid'] and c >= .8 and q <= .05):
                errors.append('Colapso: '+r['id'])
            if 'audit' in r:
                audited += 1
    paired = 0
    batch_matches = 0
    for s in range(20):
        for k in range(5):
            rng = np.random.default_rng(273000+5*s+k)
            h = hashlib.sha256()
            for t in range(1, 251):
                ix = rng.choice(90, size=64, replace=False)
                h.update(np.asarray(ix, np.int64).tobytes())
                if t not in CONFIG['updates']:
                    continue
                r, p, w = [by[(f, s, k, t)] for f in ['R27', 'P60', 'W27']]
                if r['status'] == p['status'] == 'MEASURED':
                    if r['checkpoint'] != p['checkpoint'] or r['train'] != p['train']:
                        errors.append('Pareja R27/P60: '+r['id'])
                    paired += 1
                for obj in [r, p, w]:
                    if obj['status'] == 'MEASURED':
                        if obj['batch_hash'] != h.hexdigest():
                            errors.append('RNG de lotes: '+obj['id'])
                        else:
                            batch_matches += 1
    checks.update(states_preserved=len(rows), states_measured=measured,
                  audits_preserved=audited, paired_snapshots=paired, batch_sequences_checked=batch_matches)
    # Reconstrucción determinista de3 M desde pesos propios, sin entrenar ni rho.
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    core = frozen('core')
    reproductions = []
    for family, widths in [('R27', [64, 32]), ('P60', [64, 32]), ('W27', [128, 64])]:
        r = by[(family, 0, 0, 250)]
        if r['status'] != 'MEASURED':
            reproductions.append(dict(family=family, status='UNAVAILABLE_PRESERVED'))
            continue
        class Net(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.l1 = torch.nn.Linear(4, widths[0])
                self.l2 = torch.nn.Linear(widths[0], widths[1])
                self.l3 = torch.nn.Linear(widths[1], 3)
        model = Net().double()
        with np.load(r['checkpoint']['path'], allow_pickle=False) as z:
            model.load_state_dict({key: torch.tensor(z['weight_'+key]) for key in model.state_dict()})
        with np.load(r['array']['path'], allow_pickle=False) as z:
            original, ids = z['M'], z['panel_ids']
        d = splitdata[0]
        Rb, Ub, f = core.make_geom_state(model, torch.tensor(d['Z'][ids]), torch.tensor(rawy[ids], dtype=torch.long))
        reconstructed = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
        error = float(np.linalg.norm(reconstructed-original)/max(1, np.linalg.norm(original)))
        reproductions.append(dict(family=family, relative_error=error))
        if error > 1e-10:
            errors.append('Reconstrucción M: '+family)
    checks['M_reproductions'] = reproductions
    controls = json.loads((RUN/'controls.json').read_text())
    if not controls['face26']['pass_test']:
        errors.append('Control caras completas')
    rng = np.random.default_rng(275999)
    sp = np.repeat(np.arange(20), 5)
    L, X = rng.normal(size=(2, 100))
    Y = .7*L-.1*L**2+.05*L**3+3*X
    positive = predictive_D(sp, X, L, Y)
    unit = dict(increment_exact=positive['D'] > .999999 and abs(positive['beta']-3) < 1e-10,
                redundant_X=predictive_D(sp, L, L, Y)['D'] is None,
                constant_Y=predictive_D(sp, X, L, np.zeros(100))['D'] is None,
                event_censored=event([False]*7)['right_censored'],
                event_interval=event([False, False, True, True, True, True, True])['interval'] == [10, 20],
                ranks_ties=abs(spearman([1, 1, 2], [2, 2, 3])-1) < 1e-12)
    if not all(unit.values()):
        errors.append('Controles de análisis')
    checks['analysis_unit_controls'] = unit
    denied = []
    for p in [ROOT/'experiments/DIN_borde/C1/c1_cohorte.csv', ROOT/'experiments/DIN_borde/d1/d1_estados.csv',
              ROOT/'experiments/T2_A/baseline/NO_LEER', ROOT/'experiments/T2_A1/predictors_locked.csv']:
        try:
            open(p, 'rb')
        except PermissionError:
            denied.append(str(p.relative_to(ROOT)))
        else:
            errors.append('Guarda: '+str(p))
    import sklearn
    wine = Path(sklearn.__file__).parent/'datasets/data/wine_data.csv'
    try:
        open(wine, 'rb')
    except PermissionError:
        denied.append('sklearn.datasets.data.wine_data.csv')
    else:
        errors.append('Wine no bloqueado')
    checks['forbidden_access_blocked'] = denied
    diff = subprocess.check_output(['git', 'diff', '--name-only', CONFIG['base_main']], cwd=ROOT, text=True).splitlines()
    if any(not p.startswith('experiments/DIN_borde/G1/') for p in diff):
        errors.append('Modificaciones fuera de G1')
    result = dict(status='PASS' if not errors else 'FAIL', errors=errors, checks=checks,
                  scientific_verdicts='Ver summary.json; integridad PASS no implica APARECE.',
                  verifier_sha256=sha(Path(__file__)), p_values_computed=False)
    write(STAGE/'verification.json', result)
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
