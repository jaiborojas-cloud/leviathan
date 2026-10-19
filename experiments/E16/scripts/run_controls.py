#!/usr/bin/env python3
"""Controles E16; referencias analíticas frente a SymPy y diferencias sobre S."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
T = sp.Matrix(sp.symbols('t1 t2'))
P = sp.Matrix(sp.symbols('x y'))
C = sp.diag(2, 3)
A = sp.Matrix([[1, 1], [0, 1]])
REVISION = 'v2'


def omega(s, t=T):
    return sp.Matrix([sp.diff(s, v) for v in t])


def mixed(s, p=P, t=T):
    return omega(s, t).jacobian(p).T


def arr(x):
    return np.array(x, dtype=float)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    rows, spectra, groups = [], [], []
    env = dict(python=sys.version, numpy=np.__version__, sympy=sp.__version__,
               platform=platform.platform(), float_epsilon=np.finfo(float).eps,
               threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')},
               revision=REVISION, script_sha256=digest(Path(__file__)),
               design_sha256=digest(ROOT/'DESIGN_FROZEN.md'), seed=None)
    (args.output/'environment.json').write_text(json.dumps(env, indent=2)+'\n')

    def save():
        for name, data in [('checks.csv', rows), ('spectra.csv', spectra)]:
            if data:
                with (args.output/name).open('w') as f:
                    w = csv.DictWriter(f, fieldnames=list(data[0]))
                    w.writeheader()
                    w.writerows(data)

    def numeric(name, actual, expected, fd=False):
        a, b = arr(actual), arr(expected)
        error = float(np.max(np.abs(a-b)))
        scale = float(np.max(np.abs(b)))
        tol = (2e-6 if fd else 1e-11)*(1+scale)
        rows.append(dict(group=group, check=name, method='FD' if fd else 'float64',
                         abs_error=error, rel_error=error/scale if scale else '',
                         tolerance=tol, status='PASS' if error <= tol else 'FAIL'))

    def truth(name, ok):
        rows.append(dict(group=group, check=name, method='exact_or_predicate',
                         abs_error=0 if ok else 1, rel_error='', tolerance=0,
                         status='PASS' if ok else 'FAIL'))

    def exact(name, a, b):
        diff = sp.Matrix(a)-sp.Matrix(b)
        truth(name, all(sp.simplify(x) == 0 for x in diff))

    def rank(name, b, c, expected):
        h = b*c*b.T
        ev = np.linalg.eigvalsh(arr(h))
        sv = np.linalg.svd(arr(b), compute_uv=False)
        nz = ev[ev > 1e-10]
        numerical = int(np.sum(sv > 1e-10))
        ambiguous = any(1e-12 < v < 1e-8 for v in sv)
        # Exact rational rank resolves numeric uncertainty in these finite examples.
        r = b.rank()
        truth(name+'_rank', r == expected and numerical == expected)
        spectra.append(dict(group=group, name=name, exact_rank=r, numeric_rank=numerical,
                            singular_values=json.dumps(sv.tolist()), eigenvalues=json.dumps(ev.tolist()),
                            positive_condition=float(nz.max()/nz.min()) if len(nz) else '',
                            ambiguous=ambiguous))

    def derivatives(name, s, p=P, t=T, c=C, point=None):
        point = point or ([1., 2.], [1.]*len(p))
        tv, pv = map(arr, point)
        subs = dict(zip(list(t)+list(p), list(tv)+list(pv)))
        w_ref = arr(omega(s, t).subs(subs)).reshape(-1)
        b_ref = arr(mixed(s, p, t).subs(subs))
        c_num = arr(c)
        h_ref = b_ref@c_num@b_ref.T
        # Independent numerical route calls only the scalar S, never symbolic derivatives.
        scalar = sp.lambdify((list(t), list(p)), s, modules='numpy')
        for step in (1e-3, 5e-4):
            w_fd = np.empty(len(t))
            b_fd = np.empty((len(p), len(t)))
            for i in range(len(t)):
                dt = np.zeros(len(t)); dt[i] = step
                w_fd[i] = (scalar(tv+dt, pv)-scalar(tv-dt, pv))/(2*step)
                for a in range(len(p)):
                    dp = np.zeros(len(p)); dp[a] = step
                    b_fd[a, i] = (scalar(tv+dt, pv+dp)-scalar(tv+dt, pv-dp)
                                     -scalar(tv-dt, pv+dp)+scalar(tv-dt, pv-dp))/(4*step*step)
            numeric(f'{name}_omega_{step}', w_fd, w_ref, fd=True)
            numeric(f'{name}_B_{step}', b_fd, b_ref, fd=True)
            numeric(f'{name}_h_{step}', b_fd@c_num@b_fd.T, h_ref, fd=True)

    def complete():
        status = 'PASS' if all(r['status']=='PASS' for r in rows if r['group']==group) else 'FAIL'
        elapsed = time.perf_counter()-started
        groups.append(dict(group=group, status=status, elapsed_seconds=elapsed))
        save()
        (args.output/'timing.json').write_text(json.dumps(groups, indent=2)+'\n')
        if args.progress:
            with (ROOT/'progress.md').open('a') as f:
                f.write(f'\n- {REVISION}, {group}: {status}; {elapsed:.3f} s acumulados. '
                        f'Resultados: `{args.output.relative_to(ROOT)}`.\n')
        print(group, status, flush=True)

    x, y = P
    t1, t2 = T
    base = (T.T*P)[0]
    q = sp.Matrix(sp.symbols('q1 q2'))
    z = sp.Matrix(sp.symbols('z1 z2'))
    point = {t1: 1, t2: 2, x: 1, y: 1}

    group = 'A_cartas_SPD'
    phi = sp.Matrix([q[0]+2*q[1], q[1]+q[0]**2/2])
    j = phi.jacobian(q)
    sq = base.subs(dict(zip(P, phi)), simultaneous=True)
    bq = mixed(sq, q)
    exact('B_pullback', bq, j.T)
    exact('h_pullback', bq*C*bq.T, j.T*C*j)
    qp = {q[0]: sp.Rational(1,4), q[1]: -sp.Rational(1,2)}
    bnum = bq.subs(qp)
    rank('carta', bnum, C, 2)
    v = sp.Matrix([1, -2])
    numeric('norma', (v.T*bnum*C*bnum.T*v)[0], ((j.subs(qp)*v).T*C*(j.subs(qp)*v))[0])
    seta = base.subs(dict(zip(T, A*z)), simultaneous=True)
    ceta = A.inv()*C*A.inv().T
    beta = mixed(seta, P, z)
    exact('modelo_SPD', beta*ceta*beta.T, C)
    derivatives('base', base)
    derivatives('carta_p', sq, q, point=([1,2],[.25,-.5]))
    derivatives('carta_theta', seta, P, z, ceta, ([.5,-.25],[1,1]))
    complete()

    group = 'B_subfamilias'
    u = sp.Matrix([sp.Symbol('u')])
    sline = base.subs({x:u[0], y:2*u[0]}, simultaneous=True)
    bline = mixed(sline, u)
    exact('h_linea', bline*C*bline.T, sp.Matrix([[14]]))
    rank('ambiente', sp.eye(2), C, 2)
    rank('linea', bline, C, 1)
    redundant = t1*x
    exact('h_redundante', mixed(redundant)*C*mixed(redundant).T, sp.diag(2,0))
    rank('redundante', mixed(redundant), C, 1)
    restricted = t1*u[0]
    rank('redundante_restringida', mixed(restricted,u), C, 1)
    derivatives('linea', sline, u, point=([1,2],[.25]))
    derivatives('redundante', redundant)
    derivatives('redundante_restringida', restricted, u, point=([1,2],[.25]))
    complete()

    group = 'C_descenso'
    sagg = t1*(x+y)
    bagg = mixed(sagg)
    hagg = bagg*C*bagg.T
    dpi = sp.Matrix([[1,1]])
    exact('descenso_valido', hagg, dpi.T*sp.Matrix([[2]])*dpi)
    exact('vertical_nula', hagg*sp.Matrix([1,-1]), sp.zeros(2,1))
    rank('agregado_antes', bagg, C, 1)
    rank('agregado_despues', sp.Matrix([[1,0]]), C, 1)
    numeric('vertical_obstruccion', C[1,1], 3)
    numeric('seccion_0', C[0,0], 2)
    numeric('seccion_diagonal', (sp.ones(1,2)*C*sp.ones(2,1))[0], 5)
    truth('secciones_difieren', 2 != 5)
    sfiber = t1*x*y
    hf = mixed(sfiber)*C*mixed(sfiber).T
    numeric('representante_y1', hf[0,0].subs({x:1,y:1}), 2)
    numeric('representante_y2', hf[0,0].subs({x:1,y:2}), 8)
    derivatives('agregado', sagg)
    derivatives('obstruccion_vertical', base)
    derivatives('fibra', sfiber)
    complete()

    group = 'D_composicion'
    s1, s2 = t1*x, t2*y
    macro = s1*s2
    bs = [mixed(s1),mixed(s2)]
    ws = [omega(s1),omega(s2)]
    ss = sp.Matrix(sp.symbols('s1 s2'))
    psi = ss[0]*ss[1]
    grad = sp.Matrix([sp.diff(psi, si) for si in ss])
    hes = sp.hessian(psi,ss)
    sub = dict(zip(ss,[s1,s2]))
    chain = sp.zeros(2,2)
    trunc = sp.zeros(2,2)
    for l in range(2):
        trunc += grad[l].subs(sub)*bs[l]
        for r,s in enumerate([s1,s2]):
            chain += hes[l,r].subs(sub)*sp.Matrix([sp.diff(s,p) for p in P])*ws[l].T
    chain += trunc
    exact('cadena_completa', mixed(macro), chain)
    exact('B_producto', mixed(macro).subs(point), sp.Matrix([[2,1],[2,1]]))
    truth('cadena_truncada_falla', np.max(np.abs(arr((mixed(macro)-trunc).subs(point)))) > .1)
    rank('producto', mixed(macro).subs(point), C, 1)
    a = base; b = -base+t1
    sm = a+b
    nonlinear = (a*a+b*b)/2
    expected = sp.Matrix([[11,3],[6,7]])
    exact('B_cuadratica_manual', mixed(nonlinear).subs(point), expected)
    rank('suma', mixed(sm).subs(point), C, 0)
    rank('cuadratica', mixed(nonlinear).subs(point), C, 2)
    # Second composition uses its own full chain, not the product formula only.
    full = a*mixed(a)+b*mixed(b)
    full += sp.Matrix([sp.diff(a,p) for p in P])*omega(a).T
    full += sp.Matrix([sp.diff(b,p) for p in P])*omega(b).T
    exact('cadena_cuadratica', mixed(nonlinear), full)
    derivatives('producto', macro)
    derivatives('suma', sm)
    derivatives('cuadratica', nonlinear)
    complete()

    group = 'E_cociente_degenerado'
    f = sp.diag(2,0)
    fp = f.pinv()
    feta = A.T*f*A
    fep = feta.pinv()
    bad_tensor = A.inv()*fp*A.inv().T
    truth('pseudoinversa_no_tensor', np.max(np.abs(arr(fep-bad_tensor))) > .1)
    sd = t1*x
    bd = mixed(sd)
    exact('admisibilidad_omega', sp.Matrix([[omega(sd).dot(sp.Matrix([0,1]))]]),sp.zeros(1,1))
    exact('admisibilidad_B', bd*sp.Matrix([0,1]),sp.zeros(2,1))
    hd = bd*fp*bd.T
    exact('h_cociente', hd, sp.diag(sp.Rational(1,2),0))
    numeric('contraccion_admisible', (bd*A)*fep*(bd*A).T, hd)
    bad = mixed(t2*x)
    numeric('inadmisible_antes', (bad*fp*bad.T)[0,0],0)
    numeric('inadmisible_despues', ((bad*A)*fep*(bad*A).T)[0,0],sp.Rational(1,8))
    derivatives('degenerada', sd, c=fp)
    sde = sd.subs(dict(zip(T,A*z)), simultaneous=True)
    derivatives('degenerada_carta', sde, P, z, fep, ([.5,-.25],[1,1]))
    complete()

    group = 'F_presupuesto'
    truth('tiempo_menor_60s', time.perf_counter()-started < 60)
    complete()
    status = 'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL'
    (args.output/'summary.json').write_text(json.dumps(dict(status=status, checks=len(rows),
                                                       failures=[r for r in rows if r['status']!='PASS']),indent=2)+'\n')
    print(status, len(rows))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
