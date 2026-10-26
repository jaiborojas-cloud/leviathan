"""Análisis exploratorio fijado; fuente C1 sin cambios y D7 explícito."""
import csv
from collections import Counter
import json
import math
import time
import traceback
import numpy as np
from scipy.stats import spearmanr
from support_v1 import CFG, RUN, clean, write, frozen, guard, code_guard
from statistics_v1 import conditional


def finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def csv_write(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('x') as file:
        w = csv.DictWriter(file, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({key: json.dumps(clean(v), ensure_ascii=False) if isinstance(v, (list, dict)) else v for key, v in row.items()})


def estimate(source, pairs, target):
    valid = []
    for row in pairs:
        if row['pair_valid'] and finite(row.get('rho_'+target+'_10')) and row['rho_'+target+'_10'] > 0 and finite(row.get('rho_'+target+'_250')) and row['rho_'+target+'_250'] > 0:
            valid.append(row)
    counts = Counter(row['split'] for row in valid)
    eligible = [s for s in CFG['splits'] if counts[s] >= 3]
    selected = [row for row in valid if row['split'] in eligible]
    reasons = []
    if len(valid) < 95:
        reasons.append('Más de5 faltantes de100')
    if len(eligible) < 16:
        reasons.append('Menos de16 splits con≥3')
    if len(selected) < 95:
        reasons.append('Conjunto final inferior a95/100')
    result = dict(target=target, planned=100, valid_pairs=len(valid), adjusted_pairs=len(selected),
                    eligible_splits=len(eligible), reasons=reasons, gate='INDETERMINADO')
    if not selected:
        return result
    sp = np.array([r['split'] for r in selected])
    X = np.array([r['X10'] for r in selected])
    L = np.log([r['rho_'+target+'_10'] for r in selected])
    Y = np.log([r['rho_'+target+'_250'] for r in selected])
    R = np.array([r['R250'] for r in selected])
    if np.allclose(source.cen(X, sp), 0, atol=1e-8):
        reasons.append('X sin variación intra-split: NO_IDENTIFICABLE')
    if np.ptp(L) == 0:
        reasons.append('L sin variación')
    try:
        primary = source.primaria(sp, X, L, Y, 3, 260001, 999)
        primary['p_exploratorio'] = primary.pop('p')
        result['C1_exact'] = primary
        result['D7_conditional_R'] = conditional(source, sp, X, L, Y, R, 999)
        D = primary['D']; Dc = result['D7_conditional_R']['D']
        result['fraction_removed_descriptive'] = 1-Dc/D if D > .01 else None
        result['level_signal'] = ('INCREMENTO_DESCRIPTIVO' if D >= .02 and primary['pendiente_X'] > 0 else
                    'SIN_INCREMENTO_FUERA_MUESTRA' if D <= 0 else 'INCREMENTO_PEQUENO_O_SIGNO_INVERSO')
    except Exception as e:
        reasons.append('Estimando indefinido: '+repr(e))
        result['traceback'] = traceback.format_exc()
    result['gate'] = 'VALIDA' if not reasons else 'INDETERMINADO'
    return result


def decide(levels):
    if any(l['primary']['gate'] != 'VALIDA' or l['V'] is None for l in levels):
        return dict(verdict='INDETERMINADO', reason='Faltan compuertas o variancias completas')
    V = np.array([l['V'] for l in levels])
    D = np.array([l['primary']['C1_exact']['D'] for l in levels])
    beta = np.array([l['primary']['C1_exact']['pendiente_X'] for l in levels])
    numerators = np.array([l['V_numerator_over_500'] for l in levels])
    high, low = np.flatnonzero(numerators >= 40), np.flatnonzero(numerators <= 20)
    manipulation = len(high) > 0 and len(low) > 0 and numerators.max()-numerators.min() >= 20
    correlation = float(spearmanr(D, V).statistic) if np.ptp(D) and np.ptp(V) else None
    result = dict(V=V.tolist(), D=D.tolist(), high_levels=high.tolist(), low_levels=low.tolist(),
                  spearman_D_V=correlation, manipulation=bool(manipulation))
    if not manipulation:
        return dict(result, verdict='INDETERMINADO', reason='No se produjeron niveles de variación alta y baja con rango≥.04')
    peak = np.flatnonzero(D >= D.max()-1e-10)
    qualifies = [int(k) for k in peak if k in [1, 2, 3, 4] and numerators[k] >= numerators.max()-10 and D[k] >= .02 and beta[k] > 0]
    gap = float(D[high].mean()-D[low].mean())
    support = finite(correlation) and correlation >= .6 and bool(qualifies) and gap >= .02
    best_low = int(low[np.argmax(D[low])])
    contradiction = (finite(correlation) and correlation <= -.3 and D[best_low] >= D[high].max()+.02
                       and D[best_low] >= .02 and beta[best_low] > 0)
    verdict = ('APOYO_DESCRIPTIVO' if support else 'CONTRADICE_DESCRIPTIVAMENTE' if contradiction else 'NO_APOYO_DESCRIPTIVO')
    return dict(result, verdict=verdict, peak_levels=peak.tolist(), qualifying_peak_levels=qualifies,
                mean_D_high_minus_low=gap, contradiction=bool(contradiction))


def main():
    code_guard(); guard()
    if json.loads((RUN/'controls.json').read_text())['status'] != 'PASS' or json.loads((RUN/'reconstruction.json').read_text())['status'] != 'PASS':
        raise RuntimeError('Controles obligatorios no aprobados; corrida inválida')
    start = time.perf_counter()
    source = frozen('C1_analysis')
    states, failures, pairs, split_rows, levels = [], [], [], [], []
    lookup = {}
    for level in range(6):
        for split in CFG['splits']:
            for k in CFG['initializations']:
                for update in CFG['updates']:
                    identity = f'S{level:02}_s{split:02}_k{k}_u{update:03}'
                    path = RUN/'states'/(identity+'.json')
                    d = json.loads(path.read_text()) if path.exists() else dict(id=identity, level=level,
                        s=CFG['levels'][level], split=split, initialization=k, update=update, status='MISSING', rho_valid=False)
                    lookup[level, split, k, update] = d
                    m, rho = d.get('metrics', {}), d.get('rho', {})
                    row = dict(id=identity, level=level, s=CFG['levels'][level], split=split, k=k,
                        update=update, status=d['status'], rho_valid=d['rho_valid'], rho_caras=rho.get('rho_caras'),
                        rho_vert=rho.get('rho_vert'), rho_seconds=d.get('rho_seconds'), **m,
                        train_acc=d.get('train', {}).get('acc'), train_loss=d.get('train', {}).get('loss'),
                        val_acc=d.get('validation', {}).get('acc'), val_loss=d.get('validation', {}).get('loss'))
                    states.append(row)
                    if not d['rho_valid']:
                        failures.append(d)
                a, b = lookup[level, split, k, 10], lookup[level, split, k, 250]
                ma, mb = a.get('metrics', {}), b.get('metrics', {})
                ra, rb = a.get('rho', {}), b.get('rho', {})
                pair = dict(level=level, s=CFG['levels'][level], split=split, k=k,
                        X10=ma.get('X'), R250=mb.get('log1m_star'), mal250=mb.get('mal'),
                        k_star250=mb.get('k_star'), k_hard10=ma.get('k_hard'), c250=mb.get('c'), q250=mb.get('q'),
                        rho_caras_10=ra.get('rho_caras'), rho_caras_250=rb.get('rho_caras'),
                        rho_vert_10=ra.get('rho_vert'), rho_vert_250=rb.get('rho_vert'),
                        pair_valid=bool(a['rho_valid'] and b['rho_valid'] and finite(ma.get('X')) and finite(mb.get('log1m_star'))))
                pairs.append(pair)
    for level, s in enumerate(CFG['levels']):
        ps = [r for r in pairs if r['level'] == level]
        variances, variance_numerators, modes = [], [], []
        for split in CFG['splits']:
            rows = [r for r in ps if r['split'] == split]
            measured = [r for r in rows if isinstance(r['mal250'], bool)]
            p = float(np.mean([r['mal250'] for r in measured])) if measured else None
            wrong_count = sum(r['mal250'] for r in measured)
            v = wrong_count*(5-wrong_count)/25 if len(measured) == 5 else None
            counts = Counter(r['k_star250'] for r in measured)
            modal = max(counts.values())/5 if len(measured) == 5 else None
            split_rows.append(dict(level=level, s=s, split=split, measured=len(measured), mal_fraction=p,
                                  variance=v, modal_dominant_fraction=modal))
            if v is not None:
                variances.append(v); variance_numerators.append(wrong_count*(5-wrong_count)); modes.append(modal)
        final = [r for r in states if r['level'] == level and r['update'] == 250]
        measured = [r for r in ps if isinstance(r['mal250'], bool)]
        V = sum(variance_numerators)/500 if len(variances) == 20 else None
        summary = dict(level=level, s=s, V=V, V_numerator_over_500=sum(variance_numerators) if V is not None else None,
              V_complete_splits=float(np.mean(variances)) if variances else None,
              splits_with_variance=len(variances), measured_mal=len(measured),
              mal_fraction=float(np.mean([r['mal250'] for r in measured])) if measured else None,
              modal_dominant_fraction=float(np.mean(modes)) if modes else None,
              variance_regime='ALTA' if V is not None and V >= .08 else 'BAJA' if V is not None and V <= .04 else 'INTERMEDIA' if V is not None else 'DESCONOCIDA',
              primary=estimate(source, ps, 'caras'), secondary=estimate(source, ps, 'vert'),
              k_hard10_matches_final=float(np.mean([r['k_hard10'] == r['k_star250'] for r in ps if r['pair_valid']])) if any(r['pair_valid'] for r in ps) else None,
              median_c250=float(np.median([r['c'] for r in final if finite(r.get('c'))])),
              median_q250=float(np.median([r['q'] for r in final if finite(r.get('q'))])),
              train_acc250=float(np.median([r['train_acc'] for r in final if finite(r['train_acc'])])),
              val_acc250=float(np.median([r['val_acc'] for r in final if finite(r['val_acc'])])))
        levels.append(summary)
        print(json.dumps(clean(dict(level=level, s=s, V=V, primary=summary['primary']))), flush=True)
    rule = decide(levels)
    result = dict(nature='EXPLORATORIO', planned_trajectories=600, planned_states=4200,
                  state_count=len(states), invalid_states=len(failures), levels=levels, H_var=rule,
                  permutations=999, p_confirmatorio=False, primary='rho_caras', secondary='rho_vert',
                  seconds=time.perf_counter()-start)
    write(RUN/'analysis.json', result)
    write(RUN/'failures.json', failures)
    csv_write(RUN/'states.csv', states)
    csv_write(RUN/'trajectories.csv', pairs)
    csv_write(RUN/'split_variance.csv', split_rows)
    flat = []
    for l in levels:
        a, b = l['primary'], l['secondary']
        flat.append(dict(level=l['level'], s=l['s'], mal_fraction=l['mal_fraction'], V=l['V'], variance_regime=l['variance_regime'],
             valid=a['valid_pairs'], gate=a['gate'], D_X=a.get('C1_exact', {}).get('D'),
             beta_X=a.get('C1_exact', {}).get('pendiente_X'), p_exploratorio=a.get('C1_exact', {}).get('p_exploratorio'),
             D_X_cond_R=a.get('D7_conditional_R', {}).get('D'), fraction_removed=a.get('fraction_removed_descriptive'),
             D_X_secondary=b.get('C1_exact', {}).get('D'), median_c250=l['median_c250'], median_q250=l['median_q250'],
             train_acc250=l['train_acc250'], val_acc250=l['val_acc250']))
    csv_write(RUN/'levels.csv', flat)
    print(json.dumps(clean(rule), ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
