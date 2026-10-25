"""Integridad de auditoría; PASS aquí no equivale a aprobar el script C1."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from support_v1 import ROOT, STAGE, ARRAYS, SOURCES, sha, write, guard

RUN = STAGE/'results/run_v1'


def main():
    errors = []
    manifest = list(csv.DictReader((STAGE/'manifest.csv').open()))
    for row in manifest:
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Manifest: '+row['path'])
    for row in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        data = subprocess.check_output(['git', 'show', row['tree']+':'+row['path']], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            errors.append('Fuente congelada: '+row['path'])
        p = SOURCES/Path(row['path']).name if '/C1/' in row['path'] or 'BORRADOR_v2' in row['path'] else ROOT/row['path']
        if sha(p) != row['sha256']:
            errors.append('Fuente actual: '+str(p))
    frozen_design = subprocess.check_output(['git', 'show', 'a6ad5d0:experiments/DIN_borde/D2c/DESIGN_FROZEN.md'], cwd=ROOT)
    if frozen_design != (STAGE/'DESIGN_FROZEN.md').read_bytes():
        errors.append('Diseño alterado')
    for row in csv.DictReader((STAGE/'implementation_manifest_v1.csv').open()):
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Código alterado: '+row['path'])
    env = json.loads((RUN/'environment.json').read_text())
    subprocess.run(['git', 'merge-base', '--is-ancestor', 'a6ad5d0', env['code_commit']], cwd=ROOT, check=True)
    if env['code_commit'] != subprocess.check_output(['git', 'rev-parse', '0f22130'], cwd=ROOT, text=True).strip():
        errors.append('Commit de medición inesperado')
    external = list(csv.DictReader((STAGE/'external_manifest.csv').open()))
    for row in external:
        if sha(row['path']) != row['sha256']:
            errors.append('Array/tabla externa: '+row['path'])
    summary = json.loads((RUN/'summary.json').read_text())
    if not all(summary['checks'].values()) or summary['audit_execution_errors']:
        errors.append('Comprobaciones de auditoría no completas')
    mc = [json.loads(line) for line in (RUN/'monte_carlo.jsonl').read_text().splitlines()]
    p_errors = 0
    sensitivity = 0
    for r in mc:
        with np.load(r['array']['path'], allow_pickle=False) as z:
            if z['X'].shape != (780,) or z['sp'].shape != (780,):
                errors.append('Forma MC: '+str(r['replicate']))
            p = (1+np.count_nonzero(z['null'] >= r['result']['D']-1e-15))/200
            if p != r['result']['p']:
                p_errors += 1
            if r['sensitivity']:
                pp = (1+np.count_nonzero(z['null5000'] >= r['sensitivity']['D']-1e-15))/5001
                if pp != r['sensitivity']['p']:
                    p_errors += 1
                sensitivity += 1
    if p_errors:
        errors.append('Conteos p MC: '+str(p_errors))
    # La referencia sólo importa NumPy; no comparte funciones del sujeto.
    reference_tree = ast.parse((STAGE/'scripts/independent_v1.py').read_text())
    imports = []
    for node in ast.walk(reference_tree):
        if isinstance(node, ast.Import):
            imports += [n.name for n in node.names]
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    if imports != ['numpy']:
        errors.append('Referencia no independiente: '+str(imports))
    chord_ast = ast.parse((SOURCES/'c1_cohorte.py').read_text())
    fun = next(n for n in chord_ast.body if isinstance(n, ast.FunctionDef) and n.name == 'cuerda')
    if [fun.lineno, fun.end_lineno] != [50, 55] or not (STAGE/'ERRATAS_METADATA.md').exists():
        errors.append('Metadatos cuerda no aclarados')
    chord = json.loads((RUN/'chord_face26.json').read_text())
    if not chord['exceeds_concrete_ray'] or not 25.99 < chord['ratio'] < 26.01:
        errors.append('Contraejemplo de cuerda no conservado')
    observed_cli = {p.stem: json.loads(p.read_text()) for p in (RUN/'cli').glob('*.json')}
    for name in ['missing47_omitted', 'splits40_omitted', 'duplicates']:
        r = observed_cli[name]
        if r['output']['veredicto'] != 'PASS' or r['contract_pass']:
            errors.append('Defecto reproducible no conservado: '+name)
    for name in ['rho_zero', 'rho_negative', 'L_constant', 'Y_constant']:
        if observed_cli[name]['returncode'] == 0:
            errors.append('Fallo esperado del sujeto no conservado: '+name)
    guard()
    blocked = []
    for p in ['experiments/T2_A/baseline/NO_LEER', 'experiments/T2_A1/predictors_locked.csv',
              'experiments/DIN_borde/d3/NO_LEER', 'experiments/T2_A1/checkpoints/NO_LEER.pt']:
        try:
            open(ROOT/p, 'rb')
        except PermissionError:
            blocked.append(p)
        else:
            errors.append('Guarda: '+p)
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'de1cb4edcae812b7e3f7ff53d65ae5bb994ac9c4'], cwd=ROOT, text=True).splitlines()
    if any(not p.startswith('experiments/DIN_borde/D2c/') for p in changed):
        errors.append('Cambios fuera de D2c')
    result = dict(status='PASS' if not errors else 'FAIL', errors=errors,
                  meaning='Integridad y reproducibilidad de la auditoría; C1 tiene defectos demostrados.',
                  checks=dict(manifest_files=len(manifest), external_files=len(external),
                              comparisons=32, Monte_Carlo=len(mc), null_replicates=1200, power_replicates=800,
                              sensitivity_B5000=sensitivity, p_recounts_errors=p_errors,
                              original_CLI_cases=len(observed_cli), reference_imports=imports,
                              metadata_cuerda_actual_lines=[fun.lineno, fun.end_lineno],
                              forbidden_reads_blocked=blocked, scope_only_D2c=True,
                              design_commit='a6ad5d0', measurement_code_commit=env['code_commit']),
                  question_verdicts={key: summary[key] for key in ['A1', 'A2', 'A3', 'A4', 'A5']},
                  verifier_sha256=sha(Path(__file__)))
    write(STAGE/'verification.json', result)
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
