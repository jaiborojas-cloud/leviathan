"""DIN-G1: nuevos entrenamientos Iris; instrumentos intactos; sin Wine/T2/C1."""
import concurrent.futures as cf
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
from support_v1 import ROOT, STAGE, CONFIG, RUN, ARRAYS, SOURCES, clean, write, array, frozen, guard, code_guard
from metrics_v1 import scores, matrix_metrics, chord, rho_quality

_DATA = None
_INSTRUMENTS = None


def prepare():
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    dataset = load_iris()
    X, y = np.array(dataset.data, dtype=np.float64), np.array(dataset.target, dtype=np.int64)
    if X.shape != (150, 4) or set(y) != {0, 1, 2}:
        raise RuntimeError('Iris inesperado; no se sustituye dataset')
    meta = array('dataset_iris', X=X, y=y)
    splits = []
    for s in CONFIG['splits']:
        tr, va = train_test_split(np.arange(150), train_size=90, test_size=60,
                                  stratify=y, random_state=271000+s)
        scaler = StandardScaler().fit(X[tr])
        Z = scaler.transform(X)
        rng = np.random.default_rng(274000+s)
        panel = np.sort(np.concatenate([rng.choice(va[y[va] == c], 9, replace=False) for c in range(3)]))
        metadata = array(f'split_{s:02}', Z=Z, y=y, train_ids=tr, pool_ids=np.sort(va),
                         panel27_ids=panel, scaler_mean=scaler.mean_, scaler_scale=scaler.scale_)
        splits.append(dict(split=s, **metadata))
    write(RUN/'dataset.json', dict(dataset='sklearn.load_iris', shape=list(X.shape),
                                  classes=dataset.target_names.tolist(), array=meta, splits=splits,
                                  forbidden_datasets_loaded=False))


def checkpoint(name, model, optimizer, rng, step, torch):
    values = {'update': np.array(step),
              'rng_state_utf8': np.frombuffer(json.dumps(rng.bit_generator.state).encode(), dtype=np.uint8)}
    for key, value in model.state_dict().items():
        values['weight_'+key] = value.detach().numpy()
    for i, (_, parameter) in enumerate(model.named_parameters()):
        for key, value in optimizer.state[parameter].items():
            values[f'optimizer_{i}_{key}'] = value.detach().numpy() if torch.is_tensor(value) else np.array(value)
    return array(name, **values)


def measure(family, s, k, step, model, train_stats, Z, y, ids, ckpt, batches, core, geom, rho, torch):
    identity = f'{family}_s{s:02}_k{k}_u{step:03}'
    path = RUN/'states'/(identity+'.json')
    start = time.perf_counter()
    result = dict(id=identity, family=family, split=s, initialization=k, update=step,
                  checkpoint=ckpt, batch_hash=batches, train=train_stats, status='ERROR_MATRIX')
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            Xp, yp = torch.tensor(Z[ids]), torch.tensor(y[ids], dtype=torch.long)
            val, sc = scores(model, Xp, yp, torch)
            result['validation'] = val
            Rb, Ub, fp = core.make_geom_state(model, Xp, yp)
            M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
            U = torch.cat(Ub, 0)
            gram = (U.T@U).numpy()
            f = fp.numpy()
            met, eig, fe = matrix_metrics(M, f, gram, sc, geom.Geometry)
            met.update(k_star_id=int(ids[met['k_star']]), k_hard_id=int(ids[met['k_hard']]))
            result['metrics'] = met
            t0 = time.perf_counter()
            try:
                native = rho.rho_borde(geom.Geometry(M, f), ndir=720, orden=400)
                result['rho'] = native
                result['rho_valid'] = bool(met['M_valid'] and rho_quality(native, met['chord']['value']))
            except Exception:
                result['rho_exception'] = traceback.format_exc()
                result['rho_valid'] = False
            result['rho_seconds'] = time.perf_counter()-t0
            if k == 0 and step in [10, 250]:
                t1 = time.perf_counter()
                try:
                    high = rho.rho_borde(geom.Geometry(M, f), ndir=1440, orden=800)
                    result['audit'] = high
                    error = abs(result['rho']['rho_borde']-high['rho_borde'])/high['rho_borde']
                    result['audit_relative_error'] = error
                    result['audit_pass'] = bool(result['rho_valid'] and rho_quality(high, met['chord']['value']) and error <= .01)
                except Exception:
                    result['audit_exception'] = traceback.format_exc()
                    result['audit_pass'] = False
                result['audit_seconds'] = time.perf_counter()-t1
            result['array'] = array(identity, M=M, f=f, panel_ids=ids, logits=sc['logits'],
                                     logpy=sc['logpy'], log1m=sc['log1m'], eigenvalues=eig,
                                     fisher_eigenvalues=fe)
            result['status'] = 'MEASURED'
        except Exception:
            result['exception'] = traceback.format_exc()
        result['warnings'] = [dict(category=w.category.__name__, message=str(w.message)) for w in captured]
    result['seconds'] = time.perf_counter()-start
    write(path, result)
    return result['status']


def physical_trajectory(task):
    import torch
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    global _INSTRUMENTS
    if _INSTRUMENTS is None:
        guard()
        _INSTRUMENTS = (frozen('core'), frozen('geometry'), frozen('rho'))
    core, geom, rho = _INSTRUMENTS
    arch, s, k, deadline = task
    families = ['R27', 'P60'] if arch == 'reference' else ['W27']
    beginning = time.perf_counter()
    completed = []
    failed = None
    try:
        with np.load(ARRAYS/f'split_{s:02}.npz', allow_pickle=False) as z:
            Z, y, tr, pool, p27 = [z[key].copy() for key in ['Z', 'y', 'train_ids', 'pool_ids', 'panel27_ids']]
        widths = [64, 32] if arch == 'reference' else [128, 64]
        class Network(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.l1 = torch.nn.Linear(4, widths[0])
                self.l2 = torch.nn.Linear(widths[0], widths[1])
                self.l3 = torch.nn.Linear(widths[1], 3)

            def forward(self, x):
                return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
        torch.manual_seed(272000+5*s+k)
        model = Network().double()
        optimizer = torch.optim.Adam(model.parameters(), lr=.006)
        rng = np.random.default_rng(273000+5*s+k)
        xt, yt = torch.tensor(Z[tr]), torch.tensor(y[tr], dtype=torch.long)
        batch_hash = hashlib.sha256()
        for step in range(1, 251):
            if time.perf_counter() > deadline:
                raise TimeoutError('Presupuesto global7200s agotado; no sustitución')
            ids = rng.choice(len(tr), size=64, replace=False)
            batch_hash.update(np.asarray(ids, dtype=np.int64).tobytes())
            optimizer.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(xt[ids]), yt[ids])
            if not torch.isfinite(loss):
                raise RuntimeError('Pérdida no finita')
            loss.backward()
            optimizer.step()
            if step in CONFIG['updates']:
                train_stats, _ = scores(model, xt, yt, torch)
                snap = checkpoint(f'{arch}_s{s:02}_k{k}_u{step:03}', model, optimizer, rng, step, torch)
                for family in families:
                    pp = pool if family == 'P60' else p27
                    state = measure(family, s, k, step, model, train_stats, Z, y, pp,
                                    snap, batch_hash.hexdigest(), core, geom, rho, torch)
                    completed.append((family, step, state))
    except Exception:
        failed = traceback.format_exc()
    done = {(family, step) for family, step, _ in completed}
    for family in families:
        for step in CONFIG['updates']:
            if (family, step) not in done:
                identity = f'{family}_s{s:02}_k{k}_u{step:03}'
                write(RUN/'states'/(identity+'.json'), dict(id=identity, family=family, split=s,
                      initialization=k, update=step, status='UNMEASURED', exception=failed,
                      warnings=[], rho_valid=False))
    record = dict(architecture=arch, split=s, initialization=k, completed=completed,
                  error=failed, seconds=time.perf_counter()-beginning)
    write(RUN/'trajectories'/f'{arch}_s{s:02}_k{k}.json', record)
    return dict(architecture=arch, split=s, initialization=k, error=failed,
                states=len(completed), seconds=record['seconds'])


def controls():
    f = np.column_stack([np.r_[np.linspace(-1, 1, 26), 0.], np.r_[np.zeros(26), 1.]])
    M = np.eye(27)*1e-12
    M[0, 0] += 1
    ch = chord(M, f)
    d = np.full(27, -1/27)
    d[:26] += 1/26
    known = math.sqrt(float(d@M@d))
    passed = ch['largest_face'] == 26 and abs(ch['value']/known-1) < 1e-10
    write(RUN/'controls.json', dict(face26=dict(pass_test=passed, computed=ch, reference=known)))
    if not passed:
        raise RuntimeError('Control de cara completa falló; corrida inválida')


def main():
    code_guard()
    guard()
    RUN.mkdir(parents=True, exist_ok=False)
    ARRAYS.mkdir(parents=True, exist_ok=False)
    (RUN/'states').mkdir()
    (RUN/'trajectories').mkdir()
    begin = time.perf_counter()
    import torch
    import scipy
    import sklearn
    write(RUN/'environment.json', dict(python=sys.version, platform=platform.platform(),
              numpy=np.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__, torch=torch.__version__,
              code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              config=CONFIG, sources={name: dict(path=p, sha256=d) for name, (p, d) in SOURCES.items()}))
    controls()
    prepare()
    tasks = [(arch, s, k, begin+7200) for s in CONFIG['splits'] for k in CONFIG['initializations']
             for arch in ['reference', 'wide']]
    results = []
    with (RUN/'progress.jsonl').open('x') as log:
        with cf.ProcessPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(physical_trajectory, task) for task in tasks]
            for future in cf.as_completed(futures):
                r = future.result()
                results.append(r)
                log.write(json.dumps(clean(r), allow_nan=False)+'\n')
                log.flush()
                print(f"{len(results)}/200 {r['architecture']} s{r['split']:02} k{r['initialization']}: "
                      f"{r['states']} estados, {r['seconds']:.1f}s, error={bool(r['error'])}", flush=True)
    write(RUN/'resources.json', dict(seconds=time.perf_counter()-begin, physical_networks=len(results),
                                    planned_family_trajectories=300, planned_states=2100, workers=2,
                                    task_errors=[r for r in results if r['error']]))


if __name__ == '__main__':
    main()
