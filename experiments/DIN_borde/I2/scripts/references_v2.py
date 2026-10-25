"""Referencias independientes: cuerdas MP y cuadratura MP de M original."""
import math
import time
from fractions import Fraction
import mpmath as mp
import numpy as np


def exact_triangle(M, f):
    mp.mp.dps = 80
    unique, inverse, counts = np.unique(f, axis=0, return_inverse=True, return_counts=True)
    if len(unique) != 3 or len(set(counts)) != 1:
        raise ValueError('No es triángulo de tres grupos iguales')
    n = len(f)
    mm = mp.matrix([[mp.mpf(float(x)) for x in row] for row in M])
    a0 = mp.matrix([mp.mpf(1)/n]*n)
    vertex, face = [], []
    for j in range(3):
        av = mp.matrix([mp.mpf(int(k == j))/int(counts[j]) for k in inverse])
        af = mp.matrix([mp.mpf(int(k != j))/(n-int(counts[j])) for k in inverse])
        for a, out in [(av, vertex), (af, face)]:
            b = a-a0
            out.append(mp.sqrt(max(mp.mpf(0), (b.T*mm*b)[0])))
    return dict(rho_vert=float(min(vertex)), rho_caras=float(min(face)),
                rho_vert_MP=str(min(vertex)), rho_caras_MP=str(min(face)),
                vertex_chords_MP=[str(v) for v in vertex], face_chords_MP=[str(v) for v in face])


def mp_ray(M, f, winner, seconds=300):
    """No usa el factor double del instrumento. Racionaliza f/u y agrupa.

    eigsy MP del contraste original; conserva TODOS sus modos positivos.
    Negativos de redondeo se registran con cota de efecto sobre longitud.
    """
    start = time.perf_counter()
    mp.mp.dps = 80
    deadline = start+seconds
    def budget():
        if time.perf_counter() > deadline:
            raise TimeoutError('MP_REFERENCE_BUDGET')
    def rational(s):
        q = Fraction(s)
        return mp.mpf(q.numerator)/q.denominator
    u = [rational(v) for v in winner['direction_rational']]
    unique, inverse, counts = np.unique(f, axis=0, return_inverse=True, return_counts=True)
    g = len(unique)
    ff = [[mp.mpf(float(x)) for x in row] for row in unique]
    projections = [sum(row[k]*u[k] for k in range(2)) for row in ff]
    top = max(projections)
    delta = [top-p for p in projections]
    # Construir gaps con Fraction ANTES de MP elimina falsos empates MP80.
    uq = [Fraction(s) for s in winner['direction_rational']]
    pq = [sum(Fraction(float(row[k]))*uq[k] for k in range(2)) for row in unique]
    mx = max(pq)
    dq = [mx-p for p in pq]
    maximum = max(dq)
    delta = [rational(str(d/maximum)) for d in dq]
    support = [k for k, d in enumerate(delta) if d == 0]
    if len(support) == g:
        return dict(status='CONSTANT', value=0., seconds=time.perf_counter()-start)
    counts = list(map(int, counts))
    # Agrupación exacta de los floats de M, sin eigendecomposición double.
    mm = mp.matrix(g)
    ids = [np.flatnonzero(inverse == k).tolist() for k in range(g)]
    for i in range(g):
        for j in range(g):
            mm[i, j] = mp.fsum(mp.mpf(float(M[a, b])) for a in ids[i] for b in ids[j])/(counts[i]*counts[j])
    C = mp.matrix(g-1)
    for i in range(g-1):
        for j in range(g-1):
            C[i, j] = mm[i, j]-mm[i, g-1]-mm[g-1, j]+mm[g-1, g-1]
    budget()
    ev, V = mp.eigsy(C)
    budget()
    pos = [i for i in range(g-1) if ev[i] > 0]
    factors = [[V[j, k]*mp.sqrt(ev[k]) for j in range(g-1)] for k in pos]
    clip = max(mp.mpf(0), -min(ev))
    scale = mp.sqrt(max(mp.mpf(0), max(ev)))
    # ||beta||2 <= ||beta||1 y TV total <=2g: cota conservadora de clipping.
    clip_effect = 2*g*mp.sqrt(clip)
    lo = mp.mpf(-32)
    hi = mp.log(48/min(d for d in delta if d > 0))
    parts = int(mp.ceil((hi-lo)/2))
    cuts = [lo+(hi-lo)*i/parts for i in range(parts+1)]
    roots = []
    if ev[g-2] > 0 and ev[g-2] >= (1-mp.mpf('1e-10'))*mp.fsum(max(mp.mpf(0), v) for v in ev):
        mode = factors[-1]
        def derivative(x):
            z = [mp.exp(x)*d for d in delta]
            aa = [mp.mpf(c)*mp.exp(-zz) if zz < 1000 else mp.mpf(0) for c, zz in zip(counts, z)]
            total = mp.fsum(aa); aa = [a/total for a in aa]
            mean = mp.fsum(a*zz for a, zz in zip(aa, z))
            return mp.fdot([aa[k]*(mean-z[k]) for k in range(g-1)], mode)
        nr = int(mp.ceil((hi-lo)/mp.mpf('.125')))
        scan = [lo+(hi-lo)*i/nr for i in range(nr+1)]
        vals = [derivative(x) for x in scan]
        for i in range(nr):
            if vals[i]*vals[i+1] < 0:
                a, b, ya = scan[i], scan[i+1], vals[i]
                for _ in range(150):
                    mid = (a+b)/2; ym = derivative(mid)
                    if ym*ya > 0:
                        a, ya = mid, ym
                    else:
                        b = mid
                    if b-a < mp.mpf('1e-35'):
                        break
                roots.append((a+b)/2)
        cuts = sorted(set(cuts+roots))
    def integrand(x):
        z = [mp.exp(x)*d for d in delta]
        aa = [mp.mpf(c)*mp.exp(-zz) if zz < 1000 else mp.mpf(0) for c, zz in zip(counts, z)]
        total = mp.fsum(aa)
        aa = [a/total for a in aa]
        mean = mp.fsum(a*zz for a, zz in zip(aa, z))
        beta = [aa[k]*(mean-z[k]) for k in range(g-1)]
        return mp.sqrt(mp.fsum(mp.fdot(beta, fac)**2 for fac in factors))
    values = []
    # GL nodos generados independientemente en MP, no leggauss double.
    for order in [32, 64]:
        nodes, weights = mp.gauss_quadrature(order, 'legendre')
        value = mp.mpf(0)
        for a, b in zip(cuts[:-1], cuts[1:]):
            budget()
            mid, half = (a+b)/2, (b-a)/2
            value += half*mp.fsum(weights[i]*integrand(mid+half*nodes[i]) for i in range(order))
        values.append(value)
    prefix = 2*scale*mp.exp(lo)
    ms = sum(counts[i] for i in support)
    tail = 2*scale*mp.fsum(counts[i]*mp.exp(-delta[i]*mp.exp(hi)) for i in range(g) if delta[i] > 0)/ms
    # Para ganador límite se contrasta aquí SU normal, no el valor del límite.
    return dict(status='MP80_NUMERICAL', value=float(values[-1]+prefix+tail),
                value_MP=str(values[-1]+prefix+tail), GL32_MP=str(values[0]), GL64_MP=str(values[1]),
                difference=float(abs(values[1]-values[0])), prefix_bound=str(prefix), tail_bound=str(tail),
                min_contrast_eigenvalue=str(min(ev)), clip_effect_bound=float(clip_effect),
                positive_modes=len(pos), parts=parts, seconds=time.perf_counter()-start,
                dominant_roots_MP=[str(r) for r in roots], implementation_version='r2',
                target='exact_normal' if winner['kind'] == 'vertex_limit' else winner['kind'])
