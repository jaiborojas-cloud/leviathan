"""Estimando C1 intacto y extensión D7 explícita; sólo tablas sintéticas."""
import numpy as np
from support_v1 import CFG


def frame(source, sp, L, Y):
    order = np.random.default_rng(260010).permutation(np.unique(sp))
    assignment = {s: i % 10 for i, s in enumerate(order)}
    fo = np.array([assignment[s] for s in sp])
    z = (L-L.mean())/L.std()
    base = np.column_stack([source.cen(z**j, sp) for j in range(1, 4)])
    return source.cen(Y, sp), base, fo


def conditional(source, sp, X, L, Y, R, B=999):
    yc, base, fo = frame(source, sp, L, Y)
    base = np.column_stack([base, source.cen(R, sp)])
    xc = source.cen(X, sp)
    D = source.D_cv(yc, base, xc, fo)
    beta = np.linalg.lstsq(np.column_stack([base, xc]), yc, rcond=None)[0][-1]
    rng = np.random.default_rng(260001)
    groups = [np.flatnonzero(sp == s) for s in np.unique(sp)]
    null = []
    for _ in range(B):
        xp = X.copy()
        for ids in groups:
            xp[ids] = X[rng.permutation(ids)]
        null.append(source.D_cv(yc, base, source.cen(xp, sp), fo))
    return dict(D=float(D), pendiente_X=float(beta),
                p_exploratorio=float((1+np.sum(np.array(null) >= D-1e-15))/(1+B)),
                D_nulo_q95=float(np.quantile(null, .95)), permutaciones=B)


def independent(sp, X, L, Y, B=999):
    """Reimplementación para control; NO llama ninguna función fuente C1."""
    sp, X, L, Y = map(np.asarray, [sp, X, L, Y])
    groups = [np.flatnonzero(sp == s) for s in np.unique(sp)]
    def centered(v):
        answer = v.astype(float).copy()
        for ix in groups:
            answer[ix] -= np.mean(answer[ix])
        return answer
    z = (L-np.mean(L))/np.std(L)
    design = np.array([centered(z**p) for p in [1, 2, 3]]).T
    outcome = centered(Y)
    order = np.random.default_rng(260010).permutation(np.unique(sp))
    folds = np.array([int(np.flatnonzero(order == s)[0]) % 10 for s in sp])
    def statistic(x):
        augmented = np.column_stack([design, centered(x)])
        losses = []
        for a in [design, augmented]:
            sse = 0.
            for fold in range(10):
                mask = folds == fold
                coef = np.linalg.lstsq(a[~mask], outcome[~mask], rcond=None)[0]
                residual = outcome[mask]-a[mask]@coef
                sse += np.sum(residual**2)
            losses.append(float(sse))
        return 1-losses[1]/losses[0]
    D = statistic(X)
    rng = np.random.default_rng(260001)
    null = []
    for _ in range(B):
        permuted = X.copy()
        for ix in groups:
            permuted[ix] = X[rng.permutation(ix)]
        null.append(statistic(permuted))
    return dict(D=D, p=float((1+np.sum(np.array(null) >= D-1e-15))/(1+B)))
