"""Instrumentación propia alrededor de las funciones originales sin cambiarlas."""
import math
import numpy as np
from scipy.spatial import ConvexHull


def complete_faces(f):
    f = np.asarray(f, float)
    centered = f-f.mean(0)
    sv = np.linalg.svd(centered, compute_uv=False)
    if sv[-1] <= 1e-12*sv[0]:
        raise ValueError('f no tiene rango afín2')
    hull = ConvexHull(f)
    tol = 1e-10*max(1, np.max(np.abs(f)))
    faces = set()
    for v in hull.vertices:
        S = tuple(np.flatnonzero(np.max(np.abs(f-f[v]), axis=1) <= tol))
        faces.add(S)
    for eq in hull.equations:
        S = tuple(np.flatnonzero(np.abs(f@eq[:2]+eq[2]) <= tol))
        if not S:
            raise RuntimeError('Cara vacía')
        faces.add(S)
    return sorted(faces)


def chord(M, f):
    faces = complete_faces(f)
    values = []
    for S in faces:
        d = np.full(len(f), -1/len(f))
        d[list(S)] += 1/len(S)
        values.append(float(d@M@d))
    return dict(value=float(np.sqrt(max(0, min(values)))),
                min_squared=float(min(values)), face_count=len(faces),
                largest_face=max(map(len, faces)), faces=[list(S) for S in faces])


def scores(model, X, y, torch):
    with torch.no_grad():
        logits = model(X)
        lse = torch.logsumexp(logits, 1)
        logp = torch.log_softmax(logits, 1)
        wrong = logits.clone()
        wrong[torch.arange(len(y)), y] = -float('inf')
        log1m = torch.logsumexp(wrong, 1)-lse
        logpy = logp[torch.arange(len(y)), y]
        acc = (logits.argmax(1) == y).double().mean()
    return dict(acc=float(acc), loss=float(-logpy.mean()), min_py=float(logpy.exp().min())), {
        'logits': logits.numpy(), 'logpy': logpy.numpy(), 'log1m': log1m.numpy()}


def matrix_metrics(M, f, gram, source_scores, Geometry):
    eigen, vectors = np.linalg.eigh(M)
    tr = float(np.trace(M))
    diag = np.diag(M)
    k = int(np.argmax(diag))
    norm = float(np.linalg.norm(M))
    q = float(np.linalg.norm(M-np.diag(diag))/norm) if norm else float('nan')
    c = float(diag[k]/tr) if tr > 0 else float('nan')
    fe = np.linalg.eigvalsh(gram)
    gamma = 1e-4*max(float(fe[-1]), 1e-14)
    positive = fe > max(float(fe[-1])*1e-10, 1e-300)
    rank = int(positive.sum())
    J = Geometry(M, f).jac(np.zeros((1, 2)))[0]
    h0 = J.T@M@J
    he = np.linalg.eigvalsh(h0)
    logpy, log1m = source_scores['logpy'], source_scores['log1m']
    hard = int(np.argmax(log1m))
    odds = np.exp(log1m-logpy)
    D = np.diag(len(f)*odds)
    dnorm = np.linalg.norm(D)
    faces = chord(M, f)
    symerr = float(np.linalg.norm(M-M.T)/max(norm, np.finfo(float).tiny))
    good = bool(np.isfinite(M).all() and tr > 0 and symerr <= 1e-12
                and eigen[0] >= -1e-8*max(1, eigen[-1])
                and he[-1] > 0 and he[0] > 1e-12*he[-1])
    result = dict(trace=tr, k_star=k, k_hard=hard, py_star=float(np.exp(logpy[k])),
                  log1m_star=float(log1m[k]), X=float(log1m.max()),
                  hard_match=bool(log1m[k] >= log1m.max()-1e-10), c=c, q=q,
                  eigmax_fraction=float(eigen[-1]/tr) if tr > 0 else None,
                  leading_max_coordinate=float(np.max(vectors[:, -1]**2)),
                  leading_k=int(np.argmax(vectors[:, -1]**2)),
                  effective_rank=float(tr*tr/(eigen@eigen)) if tr > 0 else None,
                  minimum_eigenvalue=float(eigen[0]), symmetry_error=symerr,
                  h0_eigenvalues=he.tolist(), gamma=gamma,
                  rank_F_1e10=rank, interpolation_numerically_resolved=(rank == 2*len(f)),
                  gamma_minF=float(gamma/fe[positive][0]) if rank else None,
                  diagonal_odds_relative_error=float(np.linalg.norm(M-D)/dnorm) if dnorm > 0 else None,
                  leverage_star=float(M[k, k]/D[k, k]) if D[k, k] > 0 else None,
                  universal_bound_min_eigenvalue=float(np.linalg.eigvalsh(D-M)[0]),
                  chord=faces, M_valid=good, collapsed=bool(good and c >= .8 and q <= .05))
    return result, eigen, fe


def rho_quality(native, lower):
    if not isinstance(native, dict):
        return False
    try:
        value = float(native['rho_borde'])
        vals = [value, float(native['err_quad']), float(native['dif_dir']), float(native['dif_orden'])]
        return bool(all(math.isfinite(x) for x in vals) and value > 0
                    and abs(vals[1])/value <= 1e-4 and vals[2] <= .01 and vals[3] <= .01
                    and value >= lower*(1-1e-6))
    except (KeyError, TypeError, ValueError):
        return False
