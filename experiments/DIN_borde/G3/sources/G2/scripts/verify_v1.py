"""Controles fijados e integridad; no reentrena ni vuelve a medir rho."""
import argparse
import csv
from collections import defaultdict, Counter
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from support_v1 import ROOT, STAGE, RUN, ARRAYS, CFG, sha, clean, write, frozen, guard, code_guard


def reconstruct():
    import torch
    torch.set_num_threads(1); torch.set_num_interop_threads(1)
    core = frozen('core')
    from run_v1 import network
    records = []
    for level in [0, 3, 5]:
        identity = f'S{level:02}_s00_k0_u010'
        d = json.loads((RUN/'states'/(identity+'.json')).read_text())
        for name in ['checkpoint', 'array']:
            assert sha(d[name]['path']) == d[name]['sha256']
        with np.load(ARRAYS/f'data_S{level:02}_s00.npz', allow_pickle=False) as z:
            Z, y, va = [z[key].copy() for key in ['Z', 'y', 'panel_ids']]
        model = network(torch)
        with np.load(d['checkpoint']['path'], allow_pickle=False) as z:
            weights = {key[7:]: torch.tensor(z[key]) for key in z.files if key.startswith('weight_')}
        model.load_state_dict(weights)
        R, U, fp = core.make_geom_state(model, torch.tensor(Z[va]), torch.tensor(y[va]))
        M = core.subset_M(R, U, [0, 1, 2]).numpy()
        with np.load(d['array']['path'], allow_pickle=False) as z:
            expected = z['M'].copy(); f = z['f'].copy()
        rel = float(np.linalg.norm(M-expected)/max(np.linalg.norm(expected), np.finfo(float).tiny))
        records.append(dict(id=identity, relative_M_error=rel, f_identical=bool(np.array_equal(fp.numpy(), f)),
                            pass_test=bool(rel <= 1e-10 and np.array_equal(fp.numpy(), f))))
    result = dict(status='PASS' if all(x['pass_test'] for x in records) else 'FAIL', records=records,
                  retrained=False, rho_recomputed=False)
    write(RUN/'reconstruction.json', result)
    print(json.dumps(clean(result), ensure_ascii=False, indent=2))


def final(errors):
    external = {}
    controls = json.loads((RUN/'controls.json').read_text())
    reconstruction = json.loads((RUN/'reconstruction.json').read_text())
    if controls['status'] != 'PASS' or reconstruction['status'] != 'PASS':
        errors.append('Control obligatorio fallido')
    def register(a):
        p = Path(a['path'])
        if not p.is_relative_to(ARRAYS):
            errors.append('Array fuera de raíz G2: '+str(p)); return
        if a['path'] not in external:
            if sha(p) != a['sha256']:
                errors.append('SHA externo: '+str(p))
            external[a['path']] = a
    datasets = json.loads((RUN/'datasets.json').read_text())
    dataset_f = {}
    for d in datasets:
        register(d['noise']); register(d['array'])
        with np.load(d['array']['path'], allow_pickle=False) as z:
            dataset_f[d['level'], d['split']] = z['Z'][z['panel_ids'], :2]
    planned = {f'S{l:02}_s{s:02}_k{k}_u{u:03}' for l in range(6) for s in range(20) for k in range(5) for u in CFG['updates']}
    observed = set()
    batch_groups, state_counts = defaultdict(set), Counter()
    for path in sorted((RUN/'states').glob('*.json')):
        d = json.loads(path.read_text()); identity = d['id']
        if identity in observed:
            errors.append('Duplicado: '+identity)
        observed.add(identity); state_counts[d['status']] += 1
        if d.get('batch_hash'):
            batch_groups[d['split'], d['initialization'], d['update']].add(d['batch_hash'])
        for key in ['checkpoint', 'array', 'rho_diagnostic']:
            if key in d:
                register(d[key])
        if 'array' in d:
            with np.load(d['array']['path'], allow_pickle=False) as z:
                if not np.array_equal(z['f'], dataset_f[d['level'], d['split']]):
                    errors.append('f no corresponde al panel: '+identity)
        if 'rho_diagnostic' in d:
            r = json.loads(Path(d['rho_diagnostic']['path']).read_text())
            if r['status'] == 'VALID_NUMERICAL_ESTIMATE' and r['implementation_version'] != 'r3':
                errors.append('Versión incorrecta: '+identity)
    if observed != planned:
        errors.append('Universo distinto: faltan'+str(len(planned-observed))+' sobran'+str(len(observed-planned)))
    initial_groups = defaultdict(set)
    trajectory_paths = list((RUN/'trajectories').glob('*.json'))
    for path in trajectory_paths:
        d = json.loads(path.read_text())
        initial_groups[d['split'], d['initialization']].add(d['initial_weights_sha256'])
    if any(len(v) != 1 for v in initial_groups.values()) or len(initial_groups) != 100:
        errors.append('Pesos iniciales no emparejados')
    if any(len(v) != 1 for v in batch_groups.values()) or len(batch_groups) != 700:
        errors.append('Lotes no emparejados')
    if len(trajectory_paths) != 600:
        errors.append('Faltan trayectorias')
    changed = subprocess.check_output(['git', 'diff', '--name-only', CFG['base_main']], cwd=ROOT, text=True).splitlines()
    if any(not p.startswith('experiments/DIN_borde/G2/') for p in changed):
        errors.append('Cambios fuera de G2')
    forbidden_suffixes = {'.npz', '.npy', '.pt', '.pth', '.zip'}
    if any(p.suffix in forbidden_suffixes for p in STAGE.rglob('*') if p.is_file()):
        errors.append('Arrays dentro de Git')
    with (STAGE/'external_manifest.csv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'sha256', 'bytes']); w.writeheader()
        for path in sorted(external):
            w.writerow(external[path])
    result = dict(status='PASS' if not errors else 'FAIL', errors=errors, state_count=len(observed),
             state_statuses=state_counts, trajectory_count=len(trajectory_paths), dataset_panels=len(datasets),
             initial_weights_paired_groups=len(initial_groups), batch_paired_groups=len(batch_groups),
             external_files_verified=len(external), reconstruction=reconstruction,
             source_hashes_unchanged=not any('Fuente' in e for e in errors),
             changed_scope='experiments/DIN_borde/G2/', design_commit='538120b', initial_code_commit='7e6c715',
             no_external_datasets_loaded=True, inferential_nature='EXPLORATORIA')
    write(STAGE/'verification.json', result)
    print(json.dumps(clean(result), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--part', choices=['reconstruct', 'final'], required=True)
    args = parser.parse_args(); code_guard()
    # Sólo documentos/código explícitos del manifest, antes de la guarda de datos.
    errors = []
    for row in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/row['path']) != row['sha256']:
            errors.append('Fuente congelada: '+row['path'])
    guard()
    reconstruct() if args.part == 'reconstruct' else final(errors)


if __name__ == '__main__':
    main()
