"""DIN-C2: generación y publicación exclusivamente, sin análisis estadístico."""
import argparse
import concurrent.futures as cf
import datetime
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
from support_v1 import ROOT, STAGE, CFG, RUN, ARRAYS, clean, write, array, diagnostic, frozen, guard, code_guard

INSTRUMENTS = None


def network(torch):
    class Network(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = torch.nn.Linear(13, 64)
            self.l2 = torch.nn.Linear(64, 32)
            self.l3 = torch.nn.Linear(32, 3)
        def forward(self, x):
            return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
    return Network().double()


def scores(model, X, y, torch):
    with torch.no_grad():
        logits = model(X)
        logp = torch.log_softmax(logits, 1)
        wrong = logits.clone()
        wrong[torch.arange(len(y)), y] = -torch.inf
        log1m = torch.logsumexp(wrong, 1)-torch.logsumexp(logits, 1)
        logpy = logp[torch.arange(len(y)), y]
        pred = logits.argmax(1)
    return dict(acc=float((pred == y).double().mean()), loss=float(-logpy.mean())), dict(
        logits=logits.numpy(), logpy=logpy.numpy(), log1m=log1m.numpy(), pred=pred.numpy())


def checkpoint(name, model, optimizer, rng, update, torch):
    values = dict(update=np.array(update), rng_state_utf8=np.frombuffer(json.dumps(rng.bit_generator.state).encode(), dtype=np.uint8))
    for key, value in model.state_dict().items():
        values['weight_'+key] = value.detach().numpy()
    for i, (_, parameter) in enumerate(model.named_parameters()):
        for key, value in optimizer.state[parameter].items():
            values[f'optimizer_{i}_{key}'] = value.detach().numpy() if torch.is_tensor(value) else np.array(value)
    return array(name+'_checkpoint', **values)


def prepare():
    from sklearn.preprocessing import StandardScaler
    means = np.zeros((3, 13))
    means[:, :2] = [[2., 0.], [-1., math.sqrt(3)], [-1., -math.sqrt(3)]]
    y = np.repeat(np.arange(3), 39)
    tr = np.array([39*c+i for c in range(3) for i in range(30)], dtype=np.int64)
    va = np.array([39*c+i for c in range(3) for i in range(30, 39)], dtype=np.int64)
    metadata = []
    for split in CFG['splits']:
        epsilon = np.random.default_rng(611000+split).normal(size=(117, 13))
        base = array(f'noise_s{split:02}', epsilon=epsilon, means=means, y=y, train_ids=tr, panel_ids=va)
        for level, s in enumerate(CFG['levels']):
            raw = means[y]+s*epsilon
            scaler = StandardScaler().fit(raw[tr])
            Z = scaler.transform(raw)
            info = array(f'data_S{level:02}_s{split:02}', Z=Z, y=y, train_ids=tr, panel_ids=va,
                         scaler_mean=scaler.mean_, scaler_scale=scaler.scale_)
            metadata.append(dict(level=level, s=s, split=split, noise=base, array=info,
                 controls=dict(train_balance=np.bincount(y[tr], minlength=3).tolist(),
                   panel_balance=np.bincount(y[va], minlength=3).tolist(), disjoint=not bool(set(tr)&set(va)),
                   standardized_mean_error=float(np.max(np.abs(Z[tr].mean(0)))),
                   standardized_std_error=float(np.max(np.abs(Z[tr].std(0)-1))))))
    write(RUN/'datasets.json', metadata)
    return metadata


def controls(metadata):
    checks = dict(datasets=all(d['controls']['disjoint'] and d['controls']['train_balance'] == [30]*3
        and d['controls']['panel_balance'] == [9]*3 and d['controls']['standardized_mean_error'] < 1e-12
        and d['controls']['standardized_std_error'] < 1e-12 for d in metadata),
        reproduction_gate=json.loads((STAGE/'cohorte/compuerta_v1/reconstruction.json').read_text())['status']=='PASS')
    result = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks)
    write(RUN/'controls.json', result)
    if not all(checks.values()):
        raise RuntimeError('Control fallido; no entrenar')
    return checks


def measure(level, split, k, step, model, optimizer, rng, batches, Z, y, tr, va, core, rho, torch):
    identity = f'c2_s{split:04d}_k{k}_u{step:03}'
    start = time.perf_counter()
    result = dict(id=identity, level=level, s=CFG['levels'][level], split=split, initialization=k,
                  update=step, batch_hash=batches.hexdigest(), status='FAILED', rho_valid=False)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            result['checkpoint'] = checkpoint(identity, model, optimizer, rng, step, torch)
            result['train'], _ = scores(model, torch.tensor(Z[tr]), torch.tensor(y[tr]), torch)
            result['validation'], sc = scores(model, torch.tensor(Z[va]), torch.tensor(y[va]), torch)
            Rb, Ub, fp = core.make_geom_state(model, torch.tensor(Z[va]), torch.tensor(y[va]))
            M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
            f = fp.numpy()
            eig = np.linalg.eigvalsh(M); trace = float(np.trace(M))
            diag = np.diag(M); star = int(np.argmax(diag)); hard = int(np.argmin(sc['logpy']))
            norm = float(np.linalg.norm(M))
            good = bool(np.isfinite(M).all() and trace > 0)
            result['metrics'] = dict(trace=trace, c=float(diag[star]/trace) if trace > 0 else None,
                 q=float(np.linalg.norm(M-np.diag(diag))/norm) if norm > 0 else None,
                 k_star=star, k_hard=hard, k_star_id=int(va[star]), k_hard_id=int(va[hard]),
                 py_star=float(np.exp(sc['logpy'][star])), logpy_star=float(sc['logpy'][star]),
                 log1m_star=float(sc['log1m'][star]), X=float(sc['log1m'].max()),
                 mal=bool(sc['pred'][star] != y[va[star]]) if good else None,
                 hard_match=bool(sc['logpy'][star] <= sc['logpy'][hard]+1e-10),
                 minimum_eigenvalue=float(eig[0]), maximum_eigenvalue=float(eig[-1]), M_finite_positive_trace=good)
            result['array'] = array(identity+'_state', M=M, f=f, logits=sc['logits'], logpy=sc['logpy'],
                    log1m=sc['log1m'], pred=sc['pred'], labels=y[va], panel_ids=va, eigenvalues=eig)
            clock = time.perf_counter()
            try:
                full = rho.rho_borde_v2(M, f)
            except Exception as e:
                full = dict(status='FAILED', exception=repr(e), traceback=traceback.format_exc())
            result['rho_seconds'] = time.perf_counter()-clock
            result['rho_diagnostic'] = diagnostic(identity+'_rho', full)
            small_keys = ['status', 'rho_caras', 'rho_vert', 'rho_edge_min', 'rho_caras_winner', 'rho_vert_winner',
                          'contrast_rounding_max', 'min_input_eigenvalue', 'implementation_version', 'seconds', 'reason']
            result['rho'] = {key: full[key] for key in small_keys if key in full}
            values = [full.get('rho_caras'), full.get('rho_vert')]
            valid = good and full['status'] == 'VALID_NUMERICAL_ESTIMATE' and all(
                    isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in values)
            if valid:
                valid = values[0] <= values[1]
                for key in ['rho_caras_winner', 'rho_vert_winner']:
                    w = full[key]
                    valid = valid and w['quad_error'] <= 1e-6*w['length'] and w['prefix_bound']+w['tail_bound'] <= 1e-6*w['length']
            result['rho_valid'] = bool(valid)
            result['status'] = 'MEASURED' if valid else 'INVALID_RHO'
        except Exception as e:
            result['exception'] = repr(e)
            result['traceback'] = traceback.format_exc()
        result['warnings'] = [dict(category=w.category.__name__, message=str(w.message)) for w in captured]
    result['seconds'] = time.perf_counter()-start
    write(RUN/'states'/(identity+'.json'), result)
    return result['status']


def trajectory(task):
    import torch
    torch.set_num_threads(1)
    global INSTRUMENTS
    if INSTRUMENTS is None:
        torch.set_num_interop_threads(1)
        guard()
        INSTRUMENTS = frozen('core'), frozen('rho_v2')
    core, rho = INSTRUMENTS
    level, split, k, deadline = task
    beginning = time.perf_counter()
    completed, error = [], None
    initial_hash = None
    try:
        with np.load(ARRAYS/f'data_S{level:02}_s{split:02}.npz', allow_pickle=False) as z:
            Z, y, tr, va = [z[key].copy() for key in ['Z', 'y', 'train_ids', 'panel_ids']]
        torch.manual_seed(621000+5*split+k)
        model = network(torch)
        initial_hash = hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()
        optimizer = torch.optim.Adam(model.parameters(), lr=.006)
        rng = np.random.default_rng(631000+5*split+k)
        xt, yt = torch.tensor(Z[tr]), torch.tensor(y[tr], dtype=torch.long)
        batches = hashlib.sha256()
        for step in range(1, 251):
            if time.perf_counter() > deadline:
                raise TimeoutError('Presupuesto43200s agotado; sin sustitución')
            ids = rng.choice(len(tr), size=64, replace=False)
            batches.update(np.asarray(ids, dtype=np.int64).tobytes())
            optimizer.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(xt[ids]), yt[ids])
            if not torch.isfinite(loss):
                raise RuntimeError('Pérdida no finita')
            loss.backward(); optimizer.step()
            if step in CFG['updates']:
                status = measure(level, split, k, step, model, optimizer, rng, batches,
                                 Z, y, tr, va, core, rho, torch)
                completed.append(dict(update=step, status=status))
    except Exception:
        error = traceback.format_exc()
    done = {x['update'] for x in completed}
    for step in CFG['updates']:
        if step not in done:
            identity = f'c2_s{split:04d}_k{k}_u{step:03}'
            write(RUN/'states'/(identity+'.json'), dict(id=identity, level=level, s=CFG['levels'][level],
                split=split, initialization=k, update=step, status='UNMEASURED', rho_valid=False, exception=error))
    record = dict(level=level, s=CFG['levels'][level], split=split, initialization=k, completed=completed,
                   error=error, initial_weights_sha256=initial_hash, seconds=time.perf_counter()-beginning)
    write(RUN/'trajectories'/f'c2_s{split:04d}_k{k}.json', record)
    return dict(level=level, split=split, k=k, error=error, states=len(completed),
                invalid=sum(x['status'] != 'MEASURED' for x in completed), seconds=record['seconds'])


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--part', choices=['prepare', 'cohort'], required=True)
    args = parser.parse_args()
    code_guard(); guard()
    if args.part == 'prepare':
        if json.loads((STAGE/'cohorte/compuerta_v1/reconstruction.json').read_text())['status'] != 'PASS':
            raise RuntimeError('Compuerta previa requerida')
        import torch, scipy, sklearn
        RUN.mkdir(parents=True, exist_ok=False); ARRAYS.mkdir(parents=True, exist_ok=False)
        (RUN/'states').mkdir(); (RUN/'trajectories').mkdir()
        write(RUN/'environment.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             python=sys.version, platform=platform.platform(), torch=torch.__version__, numpy=np.__version__,
             scipy=scipy.__version__, sklearn=sklearn.__version__, workers=2, threads=1,
             commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             sources=CFG['sources']))
        metadata = prepare()
        checks = controls(metadata)
        print(json.dumps(clean(dict(status='PASS', checks=checks))), flush=True)
    else:
        gate_path = 'experiments/DIN_borde/C2/cohorte/compuerta_v1/reconstruction.json'
        committed_gate = subprocess.check_output(['git', 'show', 'HEAD:'+gate_path], cwd=ROOT)
        if committed_gate != (ROOT/gate_path).read_bytes():
            raise RuntimeError('Compuerta no comprometida')
        if json.loads((RUN/'controls.json').read_text())['status'] != 'PASS':
            raise RuntimeError('Controles primero')
        begin = time.perf_counter(); deadline = begin+CFG['budget_seconds']
        tasks = [(level, split, k, deadline) for split in CFG['splits'] for k in CFG['initializations'] for level in range(len(CFG['levels']))]
        records = []
        with cf.ProcessPoolExecutor(max_workers=2) as pool:
            jobs = {pool.submit(trajectory, t): t[:3] for t in tasks}
            for job in cf.as_completed(jobs):
                try:
                    record = job.result()
                except Exception:
                    record = dict(task=jobs[job], error=traceback.format_exc(), status='WORKER_FAILED')
                records.append(record)
                print(json.dumps(clean(dict(done=len(records), total=len(tasks), **record))), flush=True)
        write(RUN/'execution.json', dict(records=records, seconds=time.perf_counter()-begin,
                code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))


if __name__ == '__main__':
    main()
