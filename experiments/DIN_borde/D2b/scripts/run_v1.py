"""DIN-D2b v1: sólo redes y controles sintéticos; fuentes externas intactas."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import types
import warnings

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
STAGE = ROOT / 'experiments/DIN_borde/D2b'
CONFIG = json.loads((STAGE / 'config.json').read_text())
SOURCES = {
    'core': ('docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/core.py',
             'b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd'),
    'geometry': ('docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/geometry.py',
                 'b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3'),
    'rho': ('experiments/T2_A1/fase0prima/rho_borde.py',
            'd8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b')}


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(path, obj):
    def finite(v):
        if isinstance(v, dict):
            return {k: finite(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [finite(x) for x in v]
        if isinstance(v, float) and not math.isfinite(v):
            return str(v)
        return v
    with Path(path).open('x') as f:
        json.dump(finite(obj), f, indent=2, allow_nan=False)


def access_guard():
    allowed = {str((ROOT / p).resolve()) for p, _ in SOURCES.values()}

    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        sensitive = ('/experiments/T2' in p or '/docs/archive/' in p or
                     any(s in p for s in ['/baseline/', '/comparators/', '/cuarentena_X/']) or
                     p.endswith('predictors_locked.csv') or
                     ('/sklearn/datasets/data/' in p))
        if sensitive and p not in allowed:
            raise PermissionError('DIN-D2b: acceso prohibido: ' + p)
    sys.addaudithook(audit)


def frozen(name):
    path, expected = SOURCES[name]
    p = ROOT / path
    b = p.read_bytes()
    if hashlib.sha256(b).hexdigest() != expected:
        raise RuntimeError('SHA fuente: ' + path)
    m = types.ModuleType('din_d2b_frozen_' + name)
    m.__file__ = str(p)
    exec(compile(b, str(p), 'exec'), m.__dict__)
    return m


def descriptors():
    out = []
    names = ['uniform_a1', 'uniform_a005', 'matched_q070', 'matched_q085',
             'matched_pert_q070', 'matched_pert_q085', 'grouped3', 'aligned',
             'lopsided', 'near_duplicate', 'random_tiny', 'pre_mixed']
    names += ['uniform_eps_' + str(e) for e in range(2, 9, 2)]
    names += [f'post_q{q}_eps_{e}' for q in [30, 60, 90] for e in range(2, 9, 2)]
    assert len(names) == 28
    for seed in CONFIG['seeds']:
        out.extend(dict(seed=seed, name=name, id=f'{seed}_{name}') for name in names)
    out.extend(dict(seed=CONFIG['seeds'][0], name=f'wine_matched_q{q}',
                    id=f'wine_matched_q{q}') for q in ['070', '085'])
    assert len(out) == 86
    return out


def matched_formula(a, q):
    import numpy as np
    p = np.array([q, .6*(1-q), .4*(1-q)])
    C = np.diag(p[:2]) - np.outer(p[:2], p[:2])
    t = np.array([1-q, -p[1]])
    sc = (a + 2.7)**2 + 27
    lam = np.linalg.eigvalsh(C)[-1]
    dp = 27*t @ np.linalg.solve(C + 1e-4*lam*sc/a**2*np.eye(2), t)
    dc = 27*t @ np.linalg.solve(C + 1e-4*lam*np.eye(2), t)
    return float(dp), float(dc)


def model_case(desc, core):
    import numpy as np
    import torch
    from scipy.optimize import brentq

    class Tiny(torch.nn.Module):
        def __init__(self, din=2, w1=27, w2=27):
            super().__init__()
            self.l1 = torch.nn.Linear(din, w1)
            self.l2 = torch.nn.Linear(w1, w2)
            self.l3 = torch.nn.Linear(w2, 3)

        def forward(self, X):
            return self.l3(torch.relu(self.l2(torch.relu(self.l1(X)))))

    name, seed = desc['name'], desc['seed']
    local_seed = seed + int(hashlib.sha256(name.encode()).hexdigest()[:7], 16)
    torch.manual_seed(local_seed)
    rng = np.random.default_rng(local_seed)
    panel_rng = np.random.default_rng(seed)
    x = np.linspace(-1, 1, 27)
    yy = panel_rng.normal(size=27)
    f = np.column_stack([x, (yy-yy.mean())/yy.std()])
    y = np.zeros(27, dtype=np.int64)
    meta = {}
    q = .7
    target = None
    grouped = name in ['grouped3', 'lopsided', 'near_duplicate']
    if name == 'near_duplicate':
        centers = np.array([[-1., 0.], [0., 1.], [1., 0.]])
        f = np.repeat(centers, 9, axis=0) + rng.normal(scale=1e-3, size=(27, 2))
        f = f[np.argsort(f[:, 0])]
    X = torch.tensor(f)
    if name == 'random_tiny':
        model = Tiny(w1=8, w2=8)
        return model, X, torch.arange(27) % 3, meta
    if name == 'aligned':
        model = Tiny(w1=1, w2=1)
        with torch.no_grad():
            for par in model.parameters():
                par.zero_()
            model.l1.bias.fill_(1)
            model.l2.bias.fill_(1)
    elif grouped:
        sizes = [25, 1, 1] if name == 'lopsided' else [9, 9, 9]
        cuts = np.cumsum(sizes)[:-1]
        lo = f[cuts-1, 0] + (f[cuts, 0]-f[cuts-1, 0])/3
        hi = f[cuts-1, 0] + 2*(f[cuts, 0]-f[cuts-1, 0])/3
        model = Tiny(w1=4, w2=3)
        w = np.zeros((3, 4))
        v1 = np.array([1, -1, 0, 0])/(hi[0]-lo[0])
        v2 = np.array([0, 0, 1, -1])/(hi[1]-lo[1])
        w[0], w[1], w[2] = -v1, v1-v2, v2
        with torch.no_grad():
            model.l1.weight.zero_()
            model.l1.weight[:, 0] = 1
            model.l1.bias.copy_(torch.tensor(-np.array([lo[0], hi[0], lo[1], hi[1]])))
            model.l2.weight.copy_(torch.tensor(w))
            model.l2.bias.copy_(torch.tensor([1.1, .1, .1]))
        meta['group_sizes'] = sizes
        if name == 'lopsided':
            q = .6
            y[:25] = 1
    else:
        model = Tiny()
        a = .05 if name == 'uniform_a005' else 1.
        if 'matched' in name:
            q = .85 if '085' in name else .7
            a = brentq(lambda z: matched_formula(z, q)[0]-4, 1e-4, 1, xtol=1e-14)
            dp, dc = matched_formula(a, q)
            meta.update(a=a, d_perp=dp, d_const=dc)
        elif name == 'pre_mixed':
            a = 20
            target = np.linspace(.45, .8, 27)
        elif name.startswith('uniform_eps_'):
            q = 1 - 10.**(-int(name.rsplit('_', 1)[1]))
        elif name.startswith('post_'):
            a = 20
            hard = int(name.split('_')[1][1:])/100
            eps = 10.**(-int(name.rsplit('_', 1)[1]))
            target = np.full(27, 1-eps)
            target[0] = hard
            meta.update(hard=hard, epsilon=eps)
        thresholds = np.r_[f[0, 0]-(f[1, 0]-f[0, 0])/2,
                            (f[:-1, 0]+f[1:, 0])/2]
        H1 = np.maximum(f[:, :1]-thresholds[None, :], 0)
        H2 = a*np.eye(27) + .1*np.ones((27, 27))
        with torch.no_grad():
            model.l1.weight.zero_()
            model.l1.weight[:, 0] = 1
            model.l1.bias.copy_(torch.tensor(-thresholds))
            model.l2.weight.copy_(torch.tensor(np.linalg.solve(H1, H2).T))
            model.l2.bias.zero_()
        meta['a'] = a
    with torch.no_grad():
        model.l3.weight.zero_()
        p = np.array([q, .6*(1-q), .4*(1-q)])
        if name == 'lopsided':
            p = np.array([.6, .3, .1])
        model.l3.bias.copy_(torch.tensor(np.r_[np.log(p[:2]/p[2]), 0]))
        if target is not None:
            pp = np.column_stack([target, .6*(1-target), .4*(1-target)])
            Z = np.log(pp[:, :2]/pp[:, 2:])
            actual_H = torch.relu(model.l2(torch.relu(model.l1(X)))).numpy()
            bb = Z.mean(0)
            model.l3.weight[:2].copy_(torch.tensor(np.linalg.solve(actual_H, Z-bb).T))
            model.l3.bias[:2].copy_(torch.tensor(bb))
            model.l3.bias[2] = 0
        if 'pert_' in name or name == 'near_duplicate':
            # Sensibilidad fijada: sin optimizar ni recalibrar después del ruido.
            scale = 1e-3 if name == 'near_duplicate' else 1e-4
            model.l3.weight.add_(torch.tensor(rng.normal(scale=scale, size=tuple(model.l3.weight.shape))))
    if name.startswith('wine_'):
        source_model = model
        model = core.WineMLP()
        with torch.no_grad():
            for par in model.parameters():
                par.zero_()
            model.l1.bias.fill_(-1)
            model.l2.bias.fill_(-1)
            model.l1.weight[:27, :2].copy_(source_model.l1.weight)
            model.l1.bias[:27].copy_(source_model.l1.bias)
            model.l2.weight[:27, :27].copy_(source_model.l2.weight)
            model.l2.bias[:27].copy_(source_model.l2.bias)
            model.l3.bias.copy_(source_model.l3.bias)
        X = torch.column_stack([X, torch.zeros((27, 11))])
    return model, X, torch.tensor(y, dtype=torch.long), meta


def independent_jac(model, X):
    import numpy as np
    import torch
    pars = [model.l1.weight, model.l1.bias, model.l2.weight, model.l2.bias,
            model.l3.weight[:2]-model.l3.weight[2:3], model.l3.bias[:2]-model.l3.bias[2]]
    pars = [p.detach().clone().requires_grad_(True) for p in pars]
    W1, b1, W2, b2, W3, b3 = pars
    zz = torch.relu(torch.relu(X@W1.T+b1)@W2.T+b2)@W3.T+b3
    rows = []
    for n in range(len(X)):
        for c in range(2):
            gs = torch.autograd.grad(zz[n, c], pars, retain_graph=True)
            rows.append(torch.cat([v.ravel() for v in gs]).detach().numpy())
    p = torch.softmax(torch.column_stack([zz.detach(), torch.zeros(len(X))]), 1).numpy()
    return np.stack(rows), p


def norm_error(a, b):
    import numpy as np
    return float(np.linalg.norm(a-b)/max(1., np.linalg.norm(b)))


def algebra(model, X, y, core):
    import numpy as np
    import torch
    Rb, Ub, fp = core.make_geom_state(model, X, y)
    M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
    R = torch.cat(Rb, 1).numpy()
    U = torch.cat(Ub, 0).numpy()
    A, p = independent_jac(model, X)
    N = len(p)
    t = np.tile(np.eye(3)[:, :2][None, :, :], (N, 1, 1)) - p[:, None, :2]
    AA = A.reshape(N, 2, -1)
    Rc = np.einsum('ni,nid->nd', t[np.arange(N), y.numpy()], AA)
    Uc = (np.einsum('nci,nid->dnc', t, AA)*np.sqrt(p/N)[None, :, :]).reshape(U.shape)
    _, sv, vt = np.linalg.svd(A, full_matrices=False)
    rank = int(np.sum(sv > 1e-12*sv[0]))
    Q = vt[:rank].T
    Rq, Uq = R@Q, Q.T@U
    Fq = Uq@Uq.T
    fe, fv = np.linalg.eigh(Fq)
    lm = float(np.linalg.eigvalsh(U.T@U)[-1])
    gamma = 1e-4*max(lm, 1e-14)
    factor = (Rq@fv)/np.sqrt(np.maximum(fe, 0)+gamma)
    Mref = factor@factor.T
    eig = np.linalg.eigvalsh(M)
    py = p[np.arange(N), y.numpy()]
    Xpredictor = float(np.log1p(-py.min()))
    D0 = np.diag(N*(1-py)/py)
    resolved = rank == 2*N and fe[0]/fe[-1] > 1e-10
    reference0 = None
    ridge_bound = None
    if resolved:
        M0 = (Rq@fv/fe)@(Rq@fv).T
        reference0 = norm_error(M0, D0)
        eta = gamma/(fe[0]+gamma)
        E = D0-Mref
        ridge_bound = dict(eta=float(eta),
                          lower=float(np.linalg.eigvalsh(E)[0]),
                          upper=float(np.linalg.eigvalsh(eta*D0-E)[0]))
    diag = np.diag(M)
    tr = float(np.trace(M))
    metrics = dict(R_error=norm_error(R, Rc), U_error=norm_error(U, Uc),
                   M_error=norm_error(M, Mref), rank_A=rank,
                   F_min=float(fe[0]), F_max=float(fe[-1]), gamma=gamma,
                   floor_active=lm < 1e-14, M_min=float(eig[0]), M_max=float(eig[-1]),
                   trace=tr, maxdiag_fraction=float(diag.max()/tr),
                   maxeig_fraction=float(eig[-1]/tr),
                   effective_rank=float(tr**2/(eig@eig)),
                   offdiag_fraction=float(np.linalg.norm(M-np.diag(diag))/np.linalg.norm(M)),
                   X=Xpredictor, min_py=float(py.min()), max_py=float(py.max()),
                   argmax_diag=int(np.argmax(diag)), argmin_py=int(np.argmin(py)),
                   dominance_agrees=bool(py[np.argmax(diag)] <= py.min()+1e-10),
                   interpolation_resolved=bool(resolved), M0_error=reference0,
                   ridge_bound=ridge_bound)
    metrics['algebra_pass'] = bool(metrics['R_error'] <= 1e-10 and metrics['U_error'] <= 1e-10
                                  and metrics['M_error'] <= 1e-7
                                  and eig[0] >= -1e-8*max(1, eig[-1])
                                  and (not resolved or reference0 <= 1e-7))
    arrays = dict(M=M, M_reference=Mref, factor=factor, R=R, U=U, A=A,
                  p=p, y=y.numpy(), f=fp.numpy(), eigenvalues=eig,
                  fisher_eigenvalues=fe, inputs=X.numpy())
    for key, v in model.state_dict().items():
        arrays['weight_'+key] = v.numpy()
    return metrics, arrays


def split_ray(f, factor, theta):
    """Longitud del rayo COMPLETO con cortes según brechas; no optimiza ángulo."""
    import numpy as np
    from scipy.integrate import quad
    u = np.array([math.cos(theta), math.sin(theta)])
    r = f@u
    r -= r.max()
    gaps = -r[r < -1e-13]
    if not len(gaps):
        return dict(value=0., error=0., tail=0., cutoff=0.)
    breaks = np.unique(np.r_[0., 1/gaps, 8/gaps, 32/gaps])
    def integrand(s):
        a = np.exp(s*r)
        a /= a.sum()
        v = a*(r-a@r)
        return float(np.linalg.norm(v@factor))
    vals = [quad(integrand, a, b, epsrel=1e-10, epsabs=1e-11, limit=150)
            for a, b in zip(breaks[:-1], breaks[1:])]
    lam = np.linalg.norm(factor, 2)**2
    tail = 2*np.sqrt(lam)*np.exp(-gaps*breaks[-1]).sum()/np.sum(r >= -1e-13)
    return dict(value=float(sum(v for v, _ in vals)), error=float(sum(e for _, e in vals)),
                tail=float(tail), cutoff=float(breaks[-1]))


def chord_lower(M, f):
    import numpy as np
    from scipy.spatial import ConvexHull
    hull = ConvexHull(f)
    sets = [[int(i)] for i in hull.vertices]
    sets += [list(map(int, edge)) for edge in hull.simplices]
    values = []
    for S in sets:
        delta = np.full(len(f), -1/len(f))
        delta[S] += 1/len(S)
        values.append(np.sqrt(max(0., delta@M@delta)))
    return float(min(values))


def one_case(desc, result_dir):
    import numpy as np
    import torch
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    access_guard()
    start = time.perf_counter()
    result = dict(**desc, status='ERROR')
    warning_list = []
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            core, geom, rho = frozen('core'), frozen('geometry'), frozen('rho')
            model, X, y, meta = model_case(desc, core)
            met, arrays = algebra(model, X, y, core)
            result.update(metrics=met, construction=meta)
            f, M, T = arrays['f'], arrays['M'], arrays['factor']
            t0 = time.perf_counter()
            native = rho.rho_borde(geom.Geometry(M, f))
            result['native_seconds'] = time.perf_counter()-t0
            result['native'] = native
            result['reference_at_native_theta'] = split_ray(f, T, native['theta'])
            ref = result['reference_at_native_theta']
            if desc['name'] == 'aligned':
                result['native_fidelity'] = 'ZERO_GEOMETRY_FLOATING_UNRESOLVED'
                result['log_rho'] = None
            else:
                rel = abs(native['rho_borde']-ref['value'])/max(ref['value'], 1e-12)
                result['native_relative_error'] = float(rel)
                result['native_fidelity'] = 'PASS' if rel <= 1e-4 else 'FAIL'
                result['log_rho'] = float(np.log(native['rho_borde'])) if native['rho_borde'] > 0 else None
            result['chord_lower'] = chord_lower(arrays['M_reference'], f)
            if desc['name'].startswith('post_'):
                u = f.mean(0)-f[0]
                th = math.atan2(u[1], u[0])
                result['extinction_upper'] = split_ray(f, T, th)
                coordinate = math.sqrt(max(M[0, 0], 0))/27
                result['coordinate_prediction'] = coordinate
                result['coordinate_lower_ratio'] = result['chord_lower']/coordinate
                result['coordinate_upper_ratio'] = result['extinction_upper']['value']/coordinate
            grid = np.array([(x, y) for x in [-1., 0., 1.] for y in [-1., 0., 1.]])
            J = geom.Geometry(M, f).jac(grid)
            arrays['G_grid'] = np.einsum('bni,nm,bmj->bij', J, M, J)
            result['G_grid'] = arrays['G_grid'].tolist()
            if 'matched' in desc['name'] and 'pert' not in desc['name']:
                H = np.eye(27)-np.ones((27, 27))/27
                predicted_M = meta['d_perp']*H + meta['d_const']*np.ones((27, 27))/27
                result['matched_M_error'] = norm_error(M, predicted_M)
            array_path = Path(CONFIG['arrays_dir']) / (desc['id']+'.npz')
            with array_path.open('xb') as file:
                np.savez_compressed(file, **arrays)
            result['array'] = dict(path=str(array_path), sha256=digest(array_path),
                                   bytes=array_path.stat().st_size)
            result['status'] = 'OK'
            warning_list = [dict(category=w.category.__name__, message=str(w.message)) for w in caught]
    except Exception:
        result['exception'] = traceback.format_exc()
        if 'caught' in locals():
            warning_list = [dict(category=w.category.__name__, message=str(w.message)) for w in caught]
    result['warnings'] = warning_list
    result['seconds'] = time.perf_counter()-start
    dump(Path(result_dir)/(desc['id']+'.json'), result)
    return dict(id=desc['id'], status=result['status'], seconds=result['seconds'])


def statistic_panel(L, X, Y):
    import numpy as np
    from scipy.stats import rankdata
    def corr(x, y):
        if np.linalg.norm(x-x.mean()) < 1e-10 or np.linalg.norm(y-y.mean()) < 1e-10:
            return None
        return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])
    lc, yc, xc = (a-a.mean(1, keepdims=True) for a in [L, Y, X])
    beta = float(np.sum(lc*yc)/np.sum(lc*lc))
    e = yc-beta*lc
    bx = np.sum(lc*xc)/np.sum(lc*lc)
    ex = xc-bx*lc
    LL = np.stack([lc, L**2-(L**2).mean(1, keepdims=True)], 2).reshape(-1, 2)
    bq = np.linalg.lstsq(LL, yc.ravel(), rcond=None)[0]
    eq = (yc.ravel()-LL@bq).reshape(L.shape)
    bxq = np.linalg.lstsq(LL, xc.ravel(), rcond=None)[0]
    exq = (xc.ravel()-LL@bxq).reshape(L.shape)
    ws = [corr(x, ee) for x, ee in zip(X, e)]
    wq = [corr(x, ee) for x, ee in zip(X, eq)]
    partial = [corr(x, ee) for x, ee in zip(ex, e)]
    partialq = [corr(x, ee) for x, ee in zip(exq, eq)]
    def mean(v):
        known = [x for x in v if x is not None]
        return float(np.mean(known)) if known else None
    return dict(beta=beta, W_C1=mean(ws), W_quadratic_Y=mean(wq),
                W_both_linear=mean(partial), W_both_quadratic=mean(partialq),
                undefined_both_linear=partial.count(None),
                undefined_both_quadratic=partialq.count(None),
                residual_X_linear_norm=float(np.linalg.norm(ex)),
                residual_X_quadratic_norm=float(np.linalg.norm(exq)),
                residual_Y_quadratic_norm=float(np.linalg.norm(eq)),
                Pearson_X_e=float(np.corrcoef(xc.ravel(), e.ravel())[0, 1]),
                per_split_W=ws)


def statistics(result_dir):
    import numpy as np
    rng = np.random.default_rng(CONFIG['statistics_seed'])
    out, arrays = {}, {}
    L = np.tile([0., .01, .02, .03, 1.], (64, 1))
    panels = {'exact_affine': (L, L-2, -L**2)}
    panels['noisy_affine'] = (L, L-2, -L**2+rng.normal(scale=.001, size=L.shape))
    L2 = np.tile(np.linspace(-1, 1, 5), (64, 1))
    X2 = -2+.25*L2**2
    panels['nonlinear_redundant'] = (L2, X2, X2+rng.normal(scale=.001, size=L.shape))
    Z, T = rng.normal(size=(2, 64, 5))
    panels['measurement_error'] = (Z+.7*T, -2+.2*Z, .5*Z+rng.normal(scale=.05, size=L.shape))
    L3, T = rng.normal(size=(2, 64, 5))
    panels['positive_increment'] = (L3, -2+.2*T, .5*L3+.4*T+rng.normal(scale=.1, size=L.shape))
    for key, (l, x, y) in panels.items():
        out[key] = statistic_panel(l, x, y)
        arrays.update({key+'_L': l, key+'_X': x, key+'_Y': y})
    array_path = Path(CONFIG['arrays_dir'])/'statistic_panels.npz'
    with array_path.open('xb') as file:
        np.savez_compressed(file, **arrays)
    out['_array'] = dict(path=str(array_path), sha256=digest(array_path))
    dump(Path(result_dir)/'statistic_panels.json', out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='run_v1')
    a = ap.parse_args()
    result = STAGE/'results'/a.run_id
    result.mkdir(parents=True, exist_ok=False)
    Path(CONFIG['arrays_dir']).mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    import numpy as np
    import scipy
    import torch
    import sklearn
    env = dict(python=sys.version, platform=platform.platform(), numpy=np.__version__,
               scipy=scipy.__version__, torch=torch.__version__, sklearn=sklearn.__version__,
               code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               config=CONFIG, sources={k: dict(path=p, sha256=digest(ROOT/p)) for k, (p, _) in SOURCES.items()})
    dump(result/'environment.json', env)
    stats = statistics(result)
    print('Controles estadísticos:', json.dumps({k: v.get('W_C1') for k, v in stats.items() if not k.startswith('_')}), flush=True)
    completed = []
    with cf.ProcessPoolExecutor(max_workers=CONFIG['workers']) as pool:
        futures = [pool.submit(one_case, d, str(result)) for d in descriptors()]
        for fut in cf.as_completed(futures, timeout=CONFIG['total_budget_s']):
            item = fut.result()
            completed.append(item)
            print(f"{len(completed)}/86 {item['id']}: {item['status']} {item['seconds']:.2f}s", flush=True)
    dump(result/'resources.json', dict(seconds=time.perf_counter()-start, workers=CONFIG['workers'],
                                       completed=completed))


if __name__ == '__main__':
    main()
