"""Potencia C2: piloto G3 exclusivamente; nunca lee una tabla de cohorte C2."""
from concurrent.futures import ProcessPoolExecutor
import csv
import datetime
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
from support_v1 import ROOT, STAGE, CFG, clean, write, sha, frozen, guard, code_guard

OUT = STAGE/'results_v1'
EXTERNAL = Path(CFG['power_arrays_dir'])


def cen(v, sp):
    v = np.asarray(v, float).copy()
    for s in np.unique(sp):
        v[sp == s] -= v[sp == s].mean(axis=0)
    return v


def pinv(B):
    return np.linalg.pinv(B, rcond=np.finfo(float).eps*max(B.shape))


class BatchedC1:
    def __init__(self, sp, X, L, B=1999):
        self.sp = sp
        self.B = B
        z = (L-L.mean())/L.std()
        self.base = np.column_stack([cen(z**k, sp) for k in range(1, 4)])
        rng = np.random.default_rng(260001)
        idx = [np.flatnonzero(sp == s) for s in np.unique(sp)]
        self.candidates = np.empty((len(sp), B+1))
        self.candidates[:, 0] = cen(X, sp)
        for b in range(B):
            xp = X.copy()
            for group in idx:
                xp[group] = X[rng.permutation(group)]
            self.candidates[:, b+1] = cen(xp, sp)
        order = np.random.default_rng(260010).permutation(np.unique(sp))
        assignment = {s: k % 10 for k, s in enumerate(order)}
        self.fold = np.array([assignment[s] for s in sp])
        self.residual_X = self.candidates[:, 0]-self.base@(pinv(self.base)@self.candidates[:, 0])

    def calculate(self, Y0, signal, multipliers):
        """Y=Y0 + beta*signal; comparte ruido entre efectos, C1 idéntico."""
        if Y0.ndim == 1:
            Y0 = Y0[:, None]
        Y0, signal = cen(Y0, self.sp), cen(signal, self.sp)
        q, R = len(multipliers), Y0.shape[1]
        sf = np.zeros((q, self.B+1, R)); sb = np.zeros((q, R))
        rejected = 0
        for k in range(10):
            te, tr = self.fold == k, self.fold != k
            Bt, Be = self.base[tr], self.base[te]
            P = pinv(Bt)
            X = self.candidates
            coeff_x = P@X[tr]
            rx = X[tr]-Bt@coeff_x
            zx = X[te]-Be@coeff_x
            denom = np.sum(rx*rx, axis=0)
            tol = (np.finfo(float).eps*max(Bt.shape))**2*np.maximum(np.sum(X[tr]**2, axis=0), 1e-300)
            degenerate = denom <= tol
            rejected += int(degenerate.sum())
            safe = np.where(degenerate, np.inf, denom)
            e0 = Y0[te]-Be@(P@Y0[tr])
            es = signal[te]-Be@(P@signal[tr])
            t0 = (rx.T@Y0[tr])/safe[:, None]
            ts = (rx.T@signal[tr])/safe
            c0 = zx.T@e0
            cs = zx.T@es
            zz = np.sum(zx*zx, axis=0)
            for a, beta in enumerate(multipliers):
                errors = e0+beta*es[:, None]
                baseline = np.sum(errors**2, axis=0)
                t = t0+beta*ts[:, None]
                cross = c0+beta*cs[:, None]
                sb[a] += baseline
                sf[a] += baseline[None, :]-2*t*cross+t*t*zz[:, None]
        Ds = 1-sf/sb[:, None, :]
        denom = self.residual_X@self.residual_X
        b0 = (self.residual_X@Y0)/denom
        bs = (self.residual_X@signal)/denom
        slopes = np.array([b0+beta*bs for beta in multipliers])
        p = (1+np.sum(Ds[:, 1:, :] >= Ds[:, :1, :]-1e-15, axis=1))/(self.B+1)
        return dict(D=Ds[:, 0, :], p=p, slopes=slopes, all_D=Ds, baseline_SSE=sb,
                    degenerate_fold_candidates=rejected)


def wilson(success, n):
    z = CFG['power_Wilson_z']; phat = success/n
    center = (phat+z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/(1+z*z/n)
    return dict(success=int(success), n=n, rate=phat, lower=center-half, upper=center+half)


def controls():
    source = frozen('C1_analysis')
    records = []
    for j in range(4):
        rng = np.random.default_rng(414000+j)
        sp = np.repeat(np.arange(20), 5)
        L = rng.normal(size=100)+np.repeat(rng.normal(size=20), 5)
        X = rng.normal(size=100)+(.2+.2*j)*L
        Y = .4*L-.1*L*L+.1*j*X+rng.normal(size=100)
        original = source.primaria(sp, X, L, Y, 3, 260001, 1999)
        engine = BatchedC1(sp, X, L)
        batch = engine.calculate(Y, np.zeros(100), [0.])
        gotD, gotp = float(batch['D'][0, 0]), float(batch['p'][0, 0])
        records.append(dict(original=original, batched_D=gotD, batched_p=gotp,
                absolute_D_error=abs(gotD-original['D']),
                pass_test=abs(gotD-original['D']) <= 1e-10 and gotp == original['p']))
    result = dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL', records=records)
    write(OUT/'controls.json', result)
    if result['status'] != 'PASS':
        raise RuntimeError('FWL no coincide con C1; no planificar')


def pilots():
    path = ROOT/CFG['pilot']
    if sha(path) != CFG['pilot_sha256']:
        raise RuntimeError('SHA piloto G3')
    rows = list(csv.DictReader(path.open()))
    answer = []
    for level in [2]:
        sub = sorted([r for r in rows if int(r['level']) == level], key=lambda r: (int(r['split']), int(r['k'])))
        if len(sub) != 500 or any(r['pair_valid'] != 'True' for r in sub):
            raise RuntimeError('Piloto no completo')
        if {(int(r['split']), int(r['k'])) for r in sub} != {(s, k) for s in range(100) for k in range(5)}:
            raise RuntimeError('Universo piloto distinto')
        sp = np.array([int(r['split']) for r in sub])
        X = np.array([float(r['X10']) for r in sub])
        L = np.log([float(r['rho_caras_10']) for r in sub])
        Y = np.log([float(r['rho_caras_250']) for r in sub])
        z = (L-L.mean())/L.std()
        B = np.column_stack([cen(z**k, sp) for k in range(1, 4)])
        yc = cen(Y, sp)
        alpha = np.linalg.lstsq(B, yc, rcond=None)[0]
        residual = yc-B@alpha
        rank = int(np.linalg.matrix_rank(B)); df = 500-100-rank
        answer.append(dict(level=level, s=.8, X=X, L=L, Y=Y,
                 alpha=alpha, sigma2=float(residual@residual/df), df=df, rank=rank,
                 SSE=float(residual@residual), pilot_source_sha256=sha(path)))
    return answer


def frame_task(task):
    N, pilot, frame = task
    level = pilot['level']; start = time.perf_counter()
    rng = np.random.default_rng(np.random.SeedSequence([412000, level, N, frame]))
    draw = rng.choice(100, N, replace=True)
    ids = (draw[:, None]*5+np.arange(5)).ravel()
    X, L = pilot['X'][ids], pilot['L'][ids]
    sp = np.repeat(np.arange(N), 5)
    engine = BatchedC1(sp, X, L)
    signal = engine.residual_X
    variance = float(np.mean(signal**2))
    if variance <= 0:
        raise RuntimeError('X sin residuo; no identificable')
    beta = [math.sqrt(d/(1-d)*.8*pilot['sigma2']/variance) for d in CFG['power_targets']]
    rng = np.random.default_rng(np.random.SeedSequence([413000, level, N, frame]))
    noise = rng.normal(size=(5*N, 100))
    Y0 = (engine.base@pilot['alpha'])[:, None]+math.sqrt(pilot['sigma2'])*cen(noise, sp)
    result = engine.calculate(Y0, signal, beta)
    success = (result['D'] > 0)&(result['p'] < .05)&(result['slopes'] > 0)
    name = f'N{N}_L{level}_frame{frame}'
    path = EXTERNAL/(name+'.npz')
    with path.open('xb') as f:
        np.savez_compressed(f, D=result['D'], p=result['p'], slopes=result['slopes'], all_D=result['all_D'],
               baseline_SSE=result['baseline_SSE'], success=success, bootstrap_splits=draw, noise=noise,
               effect=np.array(CFG['power_targets']), beta=np.array(beta))
    record = dict(N=N, level=level, frame=frame, success=success.sum(axis=1).tolist(), replicates=100,
         beta=beta, D_cv_mean=result['D'].mean(axis=1).tolist(), variance_residual_X=variance, sigma2=pilot['sigma2'],
         degenerate_fold_candidates=result['degenerate_fold_candidates'], seconds=time.perf_counter()-start,
         array=dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size))
    write(OUT/(name+'.json'), record)
    return record


def main():
    code_guard(); guard('power')
    OUT.mkdir(parents=True, exist_ok=False); EXTERNAL.mkdir(parents=True, exist_ok=False)
    write(OUT/'environment.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        python=sys.version, numpy=np.__version__, platform=platform.platform(), workers=2, BLAS=1,
        code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))
    controls()
    pilot = pilots()
    write(OUT/'pilot.json', pilot)
    start = time.perf_counter(); candidates = []; chosen = None
    for N in CFG['power_candidates']:
        with ProcessPoolExecutor(max_workers=2) as pool:
            records = list(pool.map(frame_task, [(N, p, f) for p in pilot for f in range(4)]))
        levels = []
        for level in [2]:
            rows = [r for r in records if r['level'] == level]
            total = np.sum([r['success'] for r in rows], axis=0)
            stats = [dict(D_target=d, **wilson(int(k), 400)) for d, k in zip(CFG['power_targets'], total)]
            passed = next(x for x in stats if x['D_target'] == .012)['lower'] >= .8 and stats[0]['upper'] <= .10
            levels.append(dict(level=level, s=.8, estimates=stats, pass_size=passed))
        result = dict(N=N, levels=levels, frames=records, selected=all(l['pass_size'] for l in levels))
        write(OUT/f'candidate_{N}.json', result); candidates.append(result)
        print(json.dumps(clean(dict(N=N, levels=levels, selected=result['selected']))), flush=True)
        if result['selected']:
            chosen = N
            break
    summary = dict(status='PASS_PLANNING' if chosen else 'INCONCLUSIVE_PLANNING', selected_splits=chosen,
                   candidates=candidates, seconds=time.perf_counter()-start, training_started=False,
                   conditional_model='Ruido Gaussiano, soporte de covariables piloto; no potencia universal.')
    write(OUT/'summary.json', summary)
    print(json.dumps(dict(status=summary['status'], selected_splits=chosen, seconds=summary['seconds'])), flush=True)


if __name__ == '__main__':
    main()
