"""Estadísticas descriptivas y reglas congeladas; no calcula p-valores."""
import math
import numpy as np
from scipy.stats import rankdata

UPDATES = [5, 10, 20, 30, 50, 150, 250]


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or not np.isfinite(x).all() or not np.isfinite(y).all():
        return None
    a, b = rankdata(x), rankdata(y)
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def center(values, splits):
    out = np.array(values, float).copy()
    for s in np.unique(splits):
        ix = splits == s
        out[ix] -= out[ix].mean()
    return out


def mean_known(values):
    known = [v for v in values if v is not None and math.isfinite(v)]
    return float(np.mean(known)) if known else None


def finite_number(value):
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (ValueError, TypeError):
        return None


def predictive_D(sp, X, L, Y):
    sp, X, L, Y = [np.asarray(v) for v in [sp, X, L, Y]]
    if len(np.unique(sp)) < 5 or L.std() == 0:
        return dict(D=None, beta=None, reason='insufficient_splits_or_constant_L')
    z = (L-L.mean())/L.std()
    B = np.column_stack([center(z**j, sp) for j in [1, 2, 3]])
    C = np.column_stack([B, center(X, sp)])
    y = center(Y, sp)
    if np.linalg.matrix_rank(B) < 3 or np.linalg.matrix_rank(C) < 4:
        return dict(D=None, beta=None, reason='covariates_not_identifiable')
    shuffled = np.random.default_rng(275010).permutation(np.unique(sp))
    assignment = {int(s): i % 5 for i, s in enumerate(shuffled)}
    folds = np.array([assignment[int(s)] for s in sp])
    sb, sf = 0., 0.
    for k in range(5):
        train, test = folds != k, folds == k
        if np.linalg.matrix_rank(C[train]) < 4:
            return dict(D=None, beta=None, reason='training_fold_not_identifiable')
        bb = np.linalg.lstsq(B[train], y[train], rcond=None)[0]
        bc = np.linalg.lstsq(C[train], y[train], rcond=None)[0]
        sb += float(np.sum((y[test]-B[test]@bb)**2))
        sf += float(np.sum((y[test]-C[test]@bc)**2))
    if sb <= np.finfo(float).eps**2*max(1, float(y@y)):
        return dict(D=None, beta=None, reason='zero_base_SSE')
    beta = float(np.linalg.lstsq(C, y, rcond=None)[0][-1])
    return dict(D=1-sf/sb, beta=beta, SSE_base=sb, SSE_full=sf,
                fold_assignment=assignment)


def linear_W(sp, X, L, Y):
    x, l, y = [center(v, sp) for v in [X, L, Y]]
    slope = float(l@y/(l@l)) if l@l else 0.
    e = y-slope*l
    values = []
    for s in np.unique(sp):
        ix = sp == s
        if ix.sum() >= 3:
            values.append(spearman(X[ix], e[ix]))
    return dict(W_adj_legacy=mean_known(values), splits_defined=sum(v is not None for v in values),
                note='Descriptivo; no prueba información condicional adicional')


def event(flags):
    for i in range(len(flags)):
        if all(flags[i:]):
            return dict(index=i, update=UPDATES[i], interval=[0 if i == 0 else UPDATES[i-1], UPDATES[i]],
                        right_censored=False)
    return dict(index=None, update=None, interval=[250, None], right_censored=True)


def family_summary(name, rows):
    rows = sorted(rows, key=lambda r: (r['split'], r['initialization'], r['update']))
    good = lambda r: r.get('metrics', {}).get('M_valid') is True
    rho_good = lambda r: good(r) and r.get('rho_valid') is True
    visits = []
    for t in UPDATES:
        rr = [r for r in rows if r['update'] == t]
        mg = [r for r in rr if good(r)]
        rg = [r for r in rr if rho_good(r)]
        def med(metric):
            vals = [r['metrics'][metric] for r in mg if r['metrics'].get(metric) is not None]
            return float(np.median(vals)) if vals else None
        visits.append(dict(update=t, planned=100, recorded=len(rr), M_valid=len(mg), rho_valid=len(rg),
                           collapsed=sum(r['metrics']['collapsed'] for r in mg),
                           c_median=med('c'), q_median=med('q'), trace_median=med('trace'),
                           eigen_fraction_median=med('eigmax_fraction'),
                           gamma_minF_median=med('gamma_minF'),
                           diagonal_odds_error_median=med('diagonal_odds_relative_error'),
                           rankF_median=med('rank_F_1e10'),
                           hard_match_fraction=float(np.mean([r['metrics']['hard_match'] for r in mg])) if mg else None,
                           rho_median=float(np.median([r['rho']['rho_borde'] for r in rg])) if rg else None,
                           train_acc_median=float(np.median([r['train']['acc'] for r in mg])) if mg else None,
                           val_acc_median=float(np.median([r['validation']['acc'] for r in mg])) if mg else None))
    coverage = {v['update']: v['M_valid'] >= 90 for v in visits}
    audits = [r for r in rows if r['initialization'] == 0 and r['update'] in [10, 250] and 'audit' in r]
    pass_audits = sum(r.get('audit_pass') is True for r in audits)
    audit_quality = len(audits) >= 36 and pass_audits >= 38
    audit_errors = [finite_number(r.get('audit_relative_error')) for r in audits]
    audit_summary = dict(planned=40, complete=len(audits), pass_count=pass_audits,
                         quality_pass=audit_quality,
                         max_relative_error=max((v for v in audit_errors if v is not None), default=None),
                         failed_ids=[r['id'] for r in rows if r['initialization'] == 0 and r['update'] in [10, 250]
                                     and not r.get('audit_pass')])
    late = [r for r in rows if r['update'] in [150, 250] and good(r)]
    col = [r for r in late if r['metrics']['collapsed']]
    early = [r for r in rows if r['update'] == 5 and good(r)]
    early_col = sum(r['metrics']['collapsed'] for r in early)
    # Límites que conservan los faltantes, sin tratarlos como no colapsados.
    late_lower, late_upper = len(col)/200, (len(col)+200-len(late))/200
    early_upper = (early_col+100-len(early))/100
    H1 = dict(verdict='INDETERMINADO', late_collapsed=len(col), late_valid=len(late),
              late_fraction_lower=late_lower, late_fraction_upper=late_upper,
              early_collapsed=early_col, early_valid=len(early),
              late_q_median=float(np.median([r['metrics']['q'] for r in late])) if late else None)
    if all(coverage[t] for t in [5, 150, 250]):
        if late_lower >= .8 and late_lower-early_upper >= .5:
            H1['verdict'] = 'APARECE'
        elif late_upper <= .2 or H1['late_q_median'] >= .2:
            H1['verdict'] = 'NO_APARECE'
    H2 = dict(verdict='INDETERMINADO', n=len(col), splits=len({r['split'] for r in col}),
              fraction=float(np.mean([r['metrics']['hard_match'] for r in col])) if col else None)
    if all(coverage[t] for t in [150, 250]) and H2['n'] >= 40 and H2['splits'] >= 10:
        if H2['fraction'] >= .9:
            H2['verdict'] = 'APARECE'
        elif H2['fraction'] <= .7:
            H2['verdict'] = 'NO_APARECE'
    rg = [r for r in col if rho_good(r)]
    pooled = spearman([np.log(r['rho']['rho_borde']) for r in rg], [r['metrics']['log1m_star'] for r in rg])
    intra = []
    for s in range(20):
        ss = [r for r in rg if r['split'] == s and r['update'] == 250]
        intra.append(dict(split=s, n=len(ss), value=spearman([np.log(r['rho']['rho_borde']) for r in ss],
                                                            [r['metrics']['log1m_star'] for r in ss])))
    W = mean_known([v['value'] for v in intra])
    H3 = dict(verdict='INDETERMINADO', n=len(rg), splits=len({r['split'] for r in rg}),
              pooled_spearman=pooled, W250=W, W_splits=sum(v['value'] is not None for v in intra),
              rho_fraction=len(rg)/len(col) if col else None, per_split=intra)
    if (all(coverage[t] for t in [150, 250]) and audit_quality and len(rg) >= 40
            and H3['splits'] >= 10 and H3['rho_fraction'] >= .9 and H3['W_splits'] >= 10
            and pooled is not None and W is not None):
        if pooled >= .9 and W >= .5:
            H3['verdict'] = 'APARECE'
        elif pooled <= .5 or W <= 0:
            H3['verdict'] = 'NO_APARECE'
    times = []
    for s in range(20):
        for k in range(5):
            rr = [r for r in rows if r['split'] == s and r['initialization'] == k]
            by_t = {r['update']: r for r in rr}
            if len(by_t) != 7 or not all(good(by_t[t]) for t in UPDATES):
                times.append(dict(split=s, initialization=k, valid=False))
                continue
            tm = event([by_t[t]['train']['acc'] >= .99 for t in UPDATES])
            tc = event([by_t[t]['metrics']['collapsed'] for t in UPDATES])
            dt = tc['index']-tm['index'] if tm['index'] is not None and tc['index'] is not None else None
            times.append(dict(split=s, initialization=k, valid=True, memorization=tm, collapse=tc,
                              index_difference=dt, close=abs(dt) <= 1 if dt is not None else None))
    both = [v for v in times if v.get('index_difference') is not None]
    H4 = dict(verdict='INDETERMINADO', complete_trajectories=sum(v['valid'] for v in times),
              both_events=len(both), splits=len({v['split'] for v in both}),
              close_fraction=float(np.mean([v['close'] for v in both])) if both else None,
              no_memorization=sum(v['valid'] and v['memorization']['right_censored'] for v in times),
              no_collapse=sum(v['valid'] and v['collapse']['right_censored'] for v in times),
              per_trajectory=times)
    if all(coverage.values()) and len(both) >= 40 and H4['splits'] >= 10:
        if H4['close_fraction'] >= .8:
            H4['verdict'] = 'APARECE'
        elif H4['close_fraction'] <= .4:
            H4['verdict'] = 'NO_APARECE'
    pairs = []
    for s in range(20):
        for k in range(5):
            by_t = {r['update']: r for r in rows if r['split'] == s and r['initialization'] == k}
            if 10 in by_t and 250 in by_t and rho_good(by_t[10]) and rho_good(by_t[250]):
                a, b = by_t[10], by_t[250]
                pairs.append(dict(split=s, initialization=k, X=a['metrics']['X'],
                                  L=math.log(a['rho']['rho_borde']), Y=math.log(b['rho']['rho_borde']),
                                  collapsed10=a['metrics']['collapsed']))
    complete_splits = [s for s in range(20) if sum(v['split'] == s for v in pairs) >= 3]
    pairs = [v for v in pairs if v['split'] in complete_splits]
    H5 = dict(verdict='INDETERMINADO', n=len(pairs), splits=len(complete_splits), audit_quality=audit_quality,
              noncollapsed10_fraction=float(np.mean([not v['collapsed10'] for v in pairs])) if pairs else None,
              pairs=pairs)
    if pairs:
        sp, X, L, Y = [np.array([v[key] for v in pairs]) for key in ['split', 'X', 'L', 'Y']]
        pred = predictive_D(sp, X, L, Y)
        halves = [predictive_D(sp[sp % 2 == part], X[sp % 2 == part], L[sp % 2 == part], Y[sp % 2 == part]) for part in [0, 1]]
        H5.update(predictive=pred, halves=halves, **linear_W(sp, X, L, Y))
        if (all(coverage[t] for t in [10, 250]) and audit_quality and len(pairs) >= 90
                and len(complete_splits) >= 18 and H5['noncollapsed10_fraction'] >= .8
                and pred.get('D') is not None and all(h.get('D') is not None for h in halves)):
            if pred['D'] >= .02 and pred['beta'] > 0 and all(h['D'] > 0 for h in halves):
                H5['verdict'] = 'APARECE'
            elif ((pred['D'] <= 0 and all(h['D'] <= 0 for h in halves))
                  or (pred['beta'] <= 0 and all(h['beta'] <= 0 for h in halves))):
                H5['verdict'] = 'NO_APARECE'
    return dict(family=name, recorded=len(rows), planned=700, visits=visits, audit=audit_summary,
                H1=H1, H2=H2, H3=H3, H4=H4, H5=H5)
