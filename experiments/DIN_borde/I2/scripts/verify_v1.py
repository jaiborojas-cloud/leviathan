"""Integridad, soportes completos y trazabilidad; no vuelve a medir longitudes."""
import csv
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
from common_v1 import ROOT, STAGE, GEOM, V1, CFG, sha, write


def main():
    errors, counts = [], {}
    for row in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Fuente congelada: '+row['path'])
    # El archivo público tiene versiones sucesivas; los originales se conservan.
    for manifest, replacements in [('implementation_manifest_v1.csv', {'rho_borde_v2.py':'versions/r1/rho_borde_v2.py'}),
           ('implementation_manifest_v2.csv', {}),
           ('implementation_manifest_r2.csv', {'rho_borde_v2.py':'versions/r2/rho_borde_v2.py'}),
           ('implementation_manifest_r3.csv', {}), ('analysis_manifest_v1.csv', {})]:
        for row in csv.DictReader((STAGE/manifest).open()):
            p = ROOT/row['path']
            if p.name in replacements and p.parent == STAGE:
                p = STAGE/replacements[p.name]
            if sha(p) != row['sha256']:
                errors.append('Versión: '+str(p))
    total_faces, brackets, warnings = 0, 0, 0
    for version in ['run_v1', 'run_r2', 'run_r3']:
        run = STAGE/'results'/version
        files = sorted((run/'states').glob('*.json'))
        counts[version] = len(files)
        if len(files) != 302:
            errors.append(version+' no tiene302 salidas')
        for path in files:
            d = json.loads(path.read_text())
            a = d['arrays']; ap = Path(a['path'])
            if sha(ap) != a['sha256']:
                errors.append('Array: '+str(ap))
            if version != 'run_r3':
                continue
            r = d['v2']
            if r.get('rho_caras') is None:
                errors.append('No completado r3: '+d['id']); continue
            if r['global_optimum_certified'] or r['geometry_sha256'] != CFG['geometry_sha']:
                errors.append('Metadatos: '+d['id'])
            if r['rho_caras'] > r['rho_vert']:
                errors.append('Orden: '+d['id'])
            import numpy as np
            with np.load(ap, allow_pickle=False) as z:
                f = z['f'].copy()
            for face in r['faces']:
                u = [Q(x) for x in face['direction_rational']]
                projections = [sum(Q(float(row[k]))*u[k] for k in range(2)) for row in f]
                top = max(projections)
                expected = [i for i, v in enumerate(projections) if v == top]
                if expected != face['face_indices']:
                    errors.append('Cara incompleta: '+d['id'])
                total_faces += 1
            if len(r['cones']) != r['geometric_vertices']:
                errors.append('Conos incompletos: '+d['id'])
            for cone in r['cones']:
                if len(cone['optimizer_attempts']) != 3 or len(cone['grid']) != 9:
                    errors.append('Multinicio: '+d['id'])
            gc = r['geometry_check']
            if gc['absolute_error'] > 1e-8*max(1, gc['jac0_speed_original'], gc['speed_contrast']):
                errors.append('Jac original: '+d['id'])
            rays = r['faces']+[x for c in r['cones'] for x in c['candidates']]
            brackets += sum(len(x.get('rejected_roundoff_brackets', [])) for x in rays)
            warnings += sum(len(x.get('warnings', [])) for x in rays)
    changed = subprocess.check_output(['git', 'diff', '--name-only', CFG['base_main']], cwd=ROOT, text=True).splitlines()
    if any(not p.startswith('experiments/DIN_borde/I2/') for p in changed):
        errors.append('Fuera de alcance')
    if sha(GEOM) != CFG['geometry_sha'] or sha(V1) != CFG['v1_sha']:
        errors.append('Instrumentos protegidos')
    result = dict(status='PASS' if not errors else 'FAIL', errors=errors, counts=counts,
                  exact_complete_faces_verified=total_faces, retained_roundoff_brackets=brackets,
                  retained_quad_warnings=warnings, original_sources_unchanged=True if not errors else None,
                  arrays_outside_git=True, numerical_global_certificate=False,
                  design_commit='0927faa', initial_code_commit='a105dbe',
                  amendments=['3f993fa', '33a9b43', 'f7996f8'],
                  instrument_r2_commit='35aebfd', instrument_r3_commit='76ecd66')
    write(STAGE/'verification.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
