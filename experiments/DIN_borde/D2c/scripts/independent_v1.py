"""Referencia propia. NO importa ni ejecuta fuentes del sujeto auditado."""
import numpy as np


def centered(v, labels):
    v = np.asarray(v, dtype=float)
    _, ix, count = np.unique(labels, return_inverse=True, return_counts=True)
    return v - (np.bincount(ix, weights=v)/count)[ix]


def covariates(L, labels, degree=3):
    L = np.asarray(L, float)
    z = (L-np.mean(L))/np.sqrt(np.mean((L-np.mean(L))**2))
    return np.stack([centered(np.power(z, k), labels) for k in range(1, degree+1)], axis=1)


def pinverse(M):
    u, s, vt = np.linalg.svd(M, full_matrices=False)
    if not len(s):
        return np.zeros((M.shape[1], M.shape[0]))
    use = s > np.finfo(float).eps*max(M.shape)*s[0]
    return (vt[use].T/s[use])@u[:, use].T


def folds(labels):
    ordered = np.unique(labels)
    shuffle = np.random.default_rng(260010).permutation(ordered)
    assigned = {int(s): j % 10 for j, s in enumerate(shuffle)}
    return np.array([assigned[int(s)] for s in labels])


def d_explicit(labels, X, L, Y, degree=3):
    B = covariates(L, labels, degree)
    x, y = centered(X, labels), centered(Y, labels)
    if np.linalg.norm(x) < 1e-12:
        return dict(D=None, beta=None)
    C = np.column_stack((B, x))
    ff = folds(labels)
    errors_base, errors_full = [], []
    for k in range(10):
        train, test = ff != k, ff == k
        a = pinverse(B[train])@y[train]
        b = pinverse(C[train])@y[train]
        errors_base.extend((y[test]-B[test]@a).tolist())
        errors_full.extend((y[test]-C[test]@b).tolist())
    sb = np.dot(errors_base, errors_base)
    sf = np.dot(errors_full, errors_full)
    beta = (pinverse(C)@y)[-1]
    return dict(D=float(1-sf/sb), beta=float(beta), SSE_base=float(sb), SSE_full=float(sf))


_PERM = {}


def permutations(labels, B, seed=260001):
    labels = np.asarray(labels)
    _, inv = np.unique(labels, return_inverse=True)
    key = (tuple(inv), B, seed)
    if key not in _PERM:
        rows = [np.flatnonzero(labels == s) for s in np.unique(labels)]
        rng = np.random.default_rng(seed)
        out = np.tile(np.arange(len(labels)), (B, 1))
        for b in range(B):
            for row in rows:
                out[b, row] = rng.permutation(row)
        _PERM[key] = out
    return _PERM[key]


class FixedBase:
    """FWL por lotes; misma OLS y mismos folds, sin ajustar polinomios al resultado."""
    def __init__(self, labels, L, Y, degree=3):
        self.labels = np.asarray(labels)
        self.B = covariates(L, labels, degree)
        self.y = centered(Y, labels)
        ff = folds(labels)
        self.parts, self.sb = [], 0.
        for k in range(10):
            tr, te = ff != k, ff == k
            bt, be = self.B[tr], self.B[te]
            pp = pinverse(bt)
            a = pp@self.y[tr]
            e = self.y[te]-be@a
            yr = self.y[tr]-bt@a
            self.sb += e@e
            self.parts.append((tr, te, bt, be, pp, e, yr))

    def evaluate(self, candidates):
        # candidates: filas=observaciones, columnas=permutaciones.
        out = np.zeros(candidates.shape[1])
        for tr, te, bt, be, pp, eb, yr in self.parts:
            xx = candidates[tr]
            q = pp@xx
            residual = xx-bt@q
            den = np.sum(residual**2, axis=0)
            scale = np.maximum(np.sum(xx**2, axis=0), 1.)
            beta = np.divide(yr@residual, den, out=np.zeros_like(den), where=den > 1e-24*scale)
            ee = eb[:, None]-(candidates[te]-be@q)*beta
            out += np.sum(ee**2, axis=0)
        return 1-out/self.sb


def primary(labels, X, L, Y, B=199, seed=260001, degree=3, explicit_null=False):
    observed = d_explicit(labels, X, L, Y, degree)
    if observed['D'] is None:
        return dict(**observed, p=None, p_literal=None, p_fast=None, null=None)
    design = FixedBase(labels, L, Y, degree)
    idx = permutations(labels, B, seed)
    xc = centered(X, labels)
    null = np.concatenate([design.evaluate(xc[idx[start:start+128]].T) for start in range(0, B, 128)])
    observed['D_fast'] = float(design.evaluate(xc[:, None])[0])
    reference_null = None
    if explicit_null:
        reference_null = np.array([d_explicit(labels, X[ii], L, Y, degree)['D'] for ii in idx])
        observed['max_fast_explicit_null_error'] = float(np.max(np.abs(reference_null-null)))
    chosen = reference_null if reference_null is not None else null
    D = observed['D']
    return dict(**observed, p=float((1+np.count_nonzero(chosen >= D-1e-15))/(B+1)),
                p_literal=float((1+np.count_nonzero(chosen >= D))/(B+1)),
                p_fast=float((1+np.count_nonzero(null >= D-1e-15))/(B+1)), null=null)


def verdict(result):
    if result.get('D') is None or result.get('p') is None:
        return 'INCONCLUSIVE'
    return 'PASS' if result['p'] < .05 and result['beta'] > 0 else 'NOT_MET'


def author_control(name, labels, X, L, Y, seed=1, r=.3):
    rng = np.random.default_rng(seed)
    zL = (L-L.mean())/L.std()
    bb = covariates(L, labels)
    yc = centered(Y, labels)
    e = yc-bb@pinverse(bb)@yc
    if name == 'X_igual_L':
        return L.copy(), L, Y
    if name == 'X_cubica_L':
        return zL**3-2*zL, L, Y
    if name == 'Y_g_L':
        return L-2, L, -zL**2+.05*rng.standard_normal(len(L))
    if name == 'X_constante':
        return np.zeros(len(L)), L, Y
    if name == 'L_con_error':
        zl = centered((L-L.mean())/L.std(), labels)
        y2 = Y+3*zl*centered(Y, labels).std()
        return L.copy(), L+.5*L.std()*rng.standard_normal(len(L)), y2
    if name == 'incremento_real':
        return r*e/e.std()+np.sqrt(1-r*r)*rng.standard_normal(len(L)), L, Y
    if name == 'nulo_ruido':
        return rng.standard_normal(len(L)), L, Y
    raise ValueError(name)


def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    c = (p+z*z/(2*n))/(1+z*z/n)
    h = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0., c-h), min(1., c+h)]
