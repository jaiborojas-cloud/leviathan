"""Verificación de integridad y contrastes de salidas propias, sin reejecutar redes."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[4]
STAGE = ROOT/'experiments/DIN_borde/D2b'
RUN = STAGE/'results/run_v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    checks = {}
    errors = []
    frozen_commit = '85fffb4'
    manifest = list(csv.DictReader((STAGE/'freeze_manifest.csv').open()))
    for row in manifest:
        tree = frozen_commit if row['tree'] == 'working' else row['tree']
        content = subprocess.check_output(['git', 'show', tree+':'+row['path']], cwd=ROOT)
        if hashlib.sha256(content).hexdigest() != row['sha256']:
            errors.append('Frozen snapshot: '+row['path'])
    checks['frozen_snapshot_entries'] = len(manifest)
    for filename in ['implementation_manifest_v1.csv', 'implementation_manifest_v2.csv', 'postprocess_manifest_v3.csv']:
        for row in csv.DictReader((STAGE/filename).open()):
            if sha(ROOT/row['path']) != row['sha256']:
                errors.append('Código cambiado: '+row['path'])
    env = json.loads((RUN/'environment.json').read_text())
    for item in env['sources'].values():
        if sha(ROOT/item['path']) != item['sha256']:
            errors.append('Fuente cambiada: '+item['path'])
    checks['frozen_scientific_sources'] = 3
    code_commit = env['code_commit']
    for older, newer in [(frozen_commit, '73cb83a'), ('923dbba', code_commit), ('73cb83a', code_commit)]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', older, newer], cwd=ROOT, check=True)
    checks['v2_environment_code_commit'] = code_commit
    checks['version_order'] = 'design85fffb4 -> code73cb83a -> amendment923dbba -> launcher1c7a1bf -> run_v2'
    v1 = json.loads((STAGE/'results/run_v1/INVALID_PROTOCOL_ORDER.json').read_text())
    for item in v1['arrays']:
        if sha(item['path']) != item['sha256']:
            errors.append('Array inválida v1 cambió: '+item['path'])
    checks['invalid_v1_preserved_arrays'] = len(v1['arrays'])
    rows = [json.loads(p.read_text()) for p in sorted(RUN.glob('*.json'))
            if p.name.startswith(('2026', 'wine_'))]
    array_count = 0
    ridge_bounds = []
    universal_bounds = []
    formula_errors = []
    mp.mp.dps = 60
    for r in rows:
        if r['status'] != 'OK':
            errors.append('Red incompleta: '+r['id'])
            continue
        a = r['array']
        if sha(a['path']) != a['sha256']:
            errors.append('Array: '+r['id'])
        with np.load(a['path'], allow_pickle=False) as z:
            p, M, f = z['p'], z['M'], z['f']
            if p.shape != (27, 3) or f.shape != (27, 2) or M.shape != (27, 27):
                errors.append('Forma: '+r['id'])
            if not np.allclose(p.sum(1), 1, rtol=0, atol=1e-12):
                errors.append('Probabilidades: '+r['id'])
            mm = r['metrics']
            py = p[np.arange(27), z['y']]
            D = np.diag(27*(1-py)/py)
            minimum = float(np.linalg.eigvalsh(D-M)[0])
            tol = 1e-7*max(1, np.linalg.norm(D, 2))
            universal_bounds.append(dict(id=r['id'], min_eigen_D_minus_M=minimum,
                                         pass_test=minimum >= -tol))
            if minimum < -tol:
                errors.append('Contracción universal: '+r['id'])
            b = mm['ridge_bound']
            if b:
                tolerance = 1e-7*max(1, np.linalg.norm(M, 2))
                passed = b['lower'] >= -tolerance and b['upper'] >= -tolerance
                ridge_bounds.append(dict(id=r['id'], pass_test=bool(passed), **b))
                if not passed:
                    errors.append('Cota ridge: '+r['id'])
            if 'matched' in r['name'] and 'pert' not in r['name']:
                q = mp.mpf('.85' if '085' in r['name'] else '.7')
                pp = [q, mp.mpf('.6')*(1-q), mp.mpf('.4')*(1-q)]
                C = mp.matrix(2)
                for i in range(2):
                    for j in range(2):
                        C[i, j] = (pp[i] if i == j else 0)-pp[i]*pp[j]
                t = mp.matrix([1-q, -pp[1]])
                lam = mp.eigsy(C)[0][1]
                aa = mp.mpf(str(r['construction']['a']))
                sc = (aa+mp.mpf('2.7'))**2+27
                d = 27*(t.T*(C+mp.mpf('1e-4')*lam*sc/aa**2*mp.eye(2))**-1*t)[0]
                error = abs(float(d)-4)/4
                formula_errors.append(dict(id=r['id'], d_perp_60digits=str(d), relative_error=error))
                if error > 1e-9:
                    errors.append('Fórmula MP: '+r['id'])
        array_count += 1
    stat = json.loads((RUN/'statistic_panels.json').read_text())
    if sha(stat['_array']['path']) != stat['_array']['sha256']:
        errors.append('Array estadística')
    checks['valid_v2_arrays'] = array_count+1
    checks['ridge_bounds_resolved'] = len(ridge_bounds)
    checks['MP_formula_checks'] = len(formula_errors)
    checks['supplemental_contraction_checks'] = len(universal_bounds)
    # La restricción de lectura debe bloquear incluso rutas inexistentes prohibidas.
    sys.path.insert(0, str(STAGE/'scripts'))
    import run_v1
    run_v1.access_guard()
    blocked = []
    for path in ['experiments/T2_A/baseline/DO_NOT_READ',
                 'experiments/T2_A1/predictors_locked.csv',
                 'experiments/T2_A1/quarentena_X/DO_NOT_READ',
                 'docs/archive/import-2026-10-17/extracted/DO_NOT_READ']:
        try:
            open(ROOT/path, 'rb')
        except PermissionError:
            blocked.append(path)
        else:
            errors.append('Guarda no bloqueó: '+path)
    checks['forbidden_access_controls_blocked'] = blocked
    summary = json.loads((RUN/'summary_v3.json').read_text())
    if not all(summary['tests'].values()):
        errors.append('Controles primarios no pasan')
    checks['primary_tests'] = summary['tests']
    files = list(csv.DictReader((STAGE/'manifest.csv').open()))
    for row in files:
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Manifest: '+row['path'])
    checks['manifest_entries'] = len(files)
    modified = subprocess.check_output(['git', 'diff', '--name-only', '85c5f3509401bc7822c9c2349d84a75efa101ccb'], cwd=ROOT, text=True).splitlines()
    if any(not p.startswith('experiments/DIN_borde/D2b/') for p in modified):
        errors.append('Cambios fuera del alcance')
    checks['scope_only_D2b'] = not any(not p.startswith('experiments/DIN_borde/D2b/') for p in modified)
    result = dict(status='PASS' if not errors else 'FAIL', checks=checks, errors=errors,
                  ridge_bounds=ridge_bounds, MP_formula=formula_errors,
                  supplemental_contraction_bounds=universal_bounds,
                  limitation='Auditoría numérica y de integridad; sin intervalos. run_v1 inválida preservada; no diagnostica D6.',
                  script_sha256=sha(Path(__file__)))
    with (STAGE/'verification.json').open('x') as file:
        json.dump(result, file, indent=2, allow_nan=False)
    print(json.dumps(dict(status=result['status'], checks=checks, errors=errors), indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
