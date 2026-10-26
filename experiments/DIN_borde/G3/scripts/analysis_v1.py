"""G3: C1 intacto, V continua y secundarios; sin datos piloto en el análisis."""
import csv
from collections import Counter
import json
import math
import time
import traceback
import numpy as np
from scipy.stats import spearmanr
from support_v1 import CFG, RUN, STAGE, clean, write, frozen, guard, code_guard
from statistics_v1 import conditional


def finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def csv_write(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('x') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(clean(v), ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def estimate(source, pairs, target):
    planned = 5*len(CFG['splits'])
    valid = [r for r in pairs if r['pair_valid'] and finite(r.get('rho_'+target+'_10'))
             and r['rho_'+target+'_10'] > 0 and finite(r.get('rho_'+target+'_250')) and r['rho_'+target+'_250'] > 0]
    counts = Counter(r['split'] for r in valid)
    eligible = [s for s in CFG['splits'] if counts[s] >= 3]
    selected = [r for r in valid if r['split'] in eligible]
    reasons = []
    if len(valid) < .95*planned:
        reasons.append('Faltantes>5%')
    if len(eligible) < math.ceil(.8*len(CFG['splits'])):
        reasons.append('Splits con≥3<80%')
    if len(selected) < .95*planned:
        reasons.append('Conjunto ajustado<95%')
    result = dict(target=target, planned=planned, valid_pairs=len(valid), adjusted_pairs=len(selected),
                  eligible_splits=len(eligible), reasons=reasons, verdict='INCONCLUSIVE', gate='INCONCLUSIVE')
    if not selected:
        return result
    sp = np.array([r['split'] for r in selected])
    X = np.array([r['X10'] for r in selected])
    L = np.log([r['rho_'+target+'_10'] for r in selected])
    Y = np.log([r['rho_'+target+'_250'] for r in selected])
    R = np.array([r['R250'] for r in selected])
    if np.allclose(source.cen(X, sp), 0, atol=1e-8):
        reasons.append('X sin variación intra-split')
    if np.ptp(L) == 0:
        reasons.append('L sin variación')
    try:
        primary = source.primaria(sp, X, L, Y, 3, 260001, 1999)
        primary['p_exploratorio'] = primary.pop('p')
        result['C1_exact'] = primary
        if not reasons:
            result['gate'] = 'VALIDA'
            result['verdict'] = ('PASS_DESCRIPTIVO' if primary['p_exploratorio'] < .05 and primary['D'] > 0
                                 and primary['pendiente_X'] > 0 else 'NOT_MET')
    except Exception as e:
        reasons.append('Primaria indefinida: '+repr(e)); result['primary_traceback'] = traceback.format_exc()
    try:
        result['D7_conditional_R'] = conditional(source, sp, X, L, Y, R, 1999)
        D = result.get('C1_exact', {}).get('D')
        result['fraction_removed_descriptive'] = 1-result['D7_conditional_R']['D']/D if finite(D) and D > .01 else None
    except Exception as e:
        result['D7_conditional_R'] = dict(status='INCONCLUSIVE_SECONDARY', exception=repr(e), traceback=traceback.format_exc())
    try:
        legacy = source.W_perm(sp, X, source.resid(Y, [L], sp), 260002, 1999)
        if 'p' in legacy:
            legacy['p_exploratorio'] = legacy.pop('p')
        result['W_adj_legacy'] = dict(legacy, nature='LEGADO; no prueba información condicional nueva')
    except Exception as e:
        result['W_adj_legacy'] = dict(status='INCONCLUSIVE_SECONDARY', exception=repr(e), traceback=traceback.format_exc())
    return result


def load_records():
    states, pairs, failures = [], [], []
    lookup = {}
    for level, s in enumerate(CFG['levels']):
        for split in CFG['splits']:
            for k in CFG['initializations']:
                for update in CFG['updates']:
                    identity = f'S{level:02}_s{split:02}_k{k}_u{update:03}'
                    path = RUN/'states'/(identity+'.json')
                    d = json.loads(path.read_text()) if path.exists() else dict(id=identity, level=level,
                         s=s, split=split, initialization=k, update=update, status='MISSING', rho_valid=False)
                    lookup[level, split, k, update] = d
                    m, rho = d.get('metrics', {}), d.get('rho', {})
                    states.append(dict(id=identity, level=level, s=s, split=split, k=k, update=update,
                      status=d['status'], rho_valid=d['rho_valid'], rho_caras=rho.get('rho_caras'), rho_vert=rho.get('rho_vert'),
                      rho_seconds=d.get('rho_seconds'), **m, train_acc=d.get('train', {}).get('acc'),
                      train_loss=d.get('train', {}).get('loss'), val_acc=d.get('validation', {}).get('acc'),
                      val_loss=d.get('validation', {}).get('loss')))
                    if not d['rho_valid']:
                        failures.append(d)
                a, b = lookup[level, split, k, 10], lookup[level, split, k, 250]
                ma, mb = a.get('metrics', {}), b.get('metrics', {})
                ra, rb = a.get('rho', {}), b.get('rho', {})
                pairs.append(dict(level=level, s=s, split=split, k=k, X10=ma.get('X'), R250=mb.get('log1m_star'),
                    mal250=mb.get('mal'), k_star250=mb.get('k_star'), k_hard10=ma.get('k_hard'),
                    c250=mb.get('c'), q250=mb.get('q'),
                    rho_caras_10=ra.get('rho_caras'), rho_caras_250=rb.get('rho_caras'),
                    rho_vert_10=ra.get('rho_vert'), rho_vert_250=rb.get('rho_vert'),
                    pair_valid=bool(a['rho_valid'] and b['rho_valid'] and finite(ma.get('X')) and finite(mb.get('log1m_star')))))
    return states, pairs, failures


def describe(level, pairs, states, source):
    ps = [p for p in pairs if p['level'] == level]
    final = [s for s in states if s['level'] == level and s['update'] == 250]
    split_rows, continuous, binary, modes = [], [], [], []
    binary_numerators = []
    for split in CFG['splits']:
        rows = [r for r in ps if r['split'] == split]
        rc = [r['R250'] for r in rows if finite(r['R250'])]
        mal = [r['mal250'] for r in rows if isinstance(r['mal250'], bool)]
        vc = float(np.var(rc, ddof=0)) if len(rc) == 5 else None
        m = sum(mal)
        vb = m*(5-m)/25 if len(mal) == 5 else None
        stars = [r['k_star250'] for r in rows if r['k_star250'] is not None]
        modal = max(Counter(stars).values())/5 if len(stars) == 5 else None
        split_rows.append(dict(level=level, s=CFG['levels'][level], split=split, n_R=len(rc),
                n_mal=len(mal), V_cont=vc, V_bin=vb, mal_fraction=m/len(mal) if mal else None,
                modal_dominant_fraction=modal))
        if vc is not None:
            continuous.append(vc)
        if vb is not None:
            binary.append(vb); binary_numerators.append(m*(5-m))
        if modal is not None:
            modes.append(modal)
    N = len(CFG['splits']); planned = 5*N
    cs = [r['c'] for r in final if finite(r.get('c'))]
    qs = [r['q'] for r in final if finite(r.get('q'))]
    medc = float(np.median(cs)) if cs else None
    medq = float(np.median(qs)) if qs else None
    regime = ('COLAPSO_OPERACIONAL' if len(cs) == planned and len(qs) == planned and medc >= .8 and medq <= .05 else
              'NO_CUMPLE_COLAPSO' if len(cs) == planned and len(qs) == planned else 'REGIMEN_INCONCLUSIVE')
    individual = [r for r in final if finite(r.get('c')) and finite(r.get('q'))]
    mal = [r['mal250'] for r in ps if isinstance(r['mal250'], bool)]
    summary = dict(level=level, s=CFG['levels'][level], regime=regime,
        median_c250=medc, median_q250=medq,
        collapsed_fraction=float(np.mean([r['c'] >= .8 and r['q'] <= .05 for r in individual])) if individual else None,
        collapsed_fraction_n=len(individual), mal_fraction=float(np.mean(mal)) if mal else None,
        V_cont=float(np.mean(continuous)) if len(continuous) == N else None,
        V_cont_complete_splits=float(np.mean(continuous)) if continuous else None, V_cont_splits=len(continuous),
        V_bin=sum(binary_numerators)/(25*N) if len(binary) == N else None,
        V_bin_splits=len(binary), modal_dominant_fraction=float(np.mean(modes)) if modes else None,
        k_hard10_matches_final=float(np.mean([r['k_hard10'] == r['k_star250'] for r in ps if r['pair_valid']])) if any(r['pair_valid'] for r in ps) else None,
        train_acc250=float(np.median([r['train_acc'] for r in final if finite(r['train_acc'])])),
        val_acc250=float(np.median([r['val_acc'] for r in final if finite(r['val_acc'])])),
        primary=estimate(source, ps, 'caras'), secondary=estimate(source, ps, 'vert'))
    return summary, split_rows


def global_reading(levels, power):
    eligible = [l['level'] for l in levels if l['regime'] == 'COLAPSO_OPERACIONAL']
    detected = [l['level'] for l in levels if l['primary']['verdict'] == 'PASS_DESCRIPTIVO']
    present = sorted(set(eligible)&set(detected))
    estimates = power['candidates'][-1]['levels']
    sufficient = all(l['estimates'][-1]['lower'] >= .8 for l in estimates)
    complete = all(l['primary']['valid_pairs'] == l['primary']['planned'] for l in levels)
    if present:
        verdict = 'SENAL_PRESENTE_FUERA_DE_WINE_DESCRIPTIVA'
    elif all(l['primary']['verdict'] == 'NOT_MET' for l in levels) and sufficient and complete and eligible:
        verdict = 'AUSENTE_CON_POTENCIA_SIMULADA_DESCRIPTIVA'
    else:
        verdict = 'INDETERMINADO_PARA_COLAPSO'
    V = [l['V_cont'] for l in levels]
    D = [l['primary'].get('C1_exact', {}).get('D') for l in levels]
    correlation = float(spearmanr(V, D).statistic) if all(finite(x) for x in V+D) and np.ptp(V) and np.ptp(D) else None
    return dict(verdict=verdict, eligible_collapse_levels=eligible, detected_levels=detected,
        detected_in_collapse=present, sufficient_simulated_power=sufficient, complete_pairs=complete,
        spearman_D_Vcont=correlation, D=D, V_cont=V, trend_inferential=False,
        absence_scope='Sólo niveles elegibles y tamaño .026 bajo modelo de potencia; no prueba del nulo.')


def main():
    code_guard(); guard()
    for name in ['controls.json', 'reconstruction.json']:
        if json.loads((RUN/name).read_text())['status'] != 'PASS':
            raise RuntimeError('Control obligatorio fallido; no interpretar cohorte')
    power = json.loads((STAGE/'results/power_v1/summary.json').read_text())
    if power['status'] != 'PASS_PLANNING' or power['selected_splits'] != len(CFG['splits']):
        raise RuntimeError('Tamaño no coincide con planificación')
    source = frozen('C1_analysis'); start = time.perf_counter()
    states, pairs, failures = load_records()
    levels, split_rows = [], []
    for level in range(len(CFG['levels'])):
        summary, splits = describe(level, pairs, states, source)
        pe = power['candidates'][-1]['levels'][level]['estimates'][-1]
        summary['power_D026'] = pe
        levels.append(summary); split_rows.extend(splits)
        print(json.dumps(clean(summary), ensure_ascii=False), flush=True)
    reading = global_reading(levels, power)
    result = dict(nature='EXPLORATORIO', planned_trajectories=CFG['planned_trajectories'],
       planned_states=CFG['planned_states'], state_count=len(states), invalid_states=len(failures),
       splits_per_level=len(CFG['splits']), levels=levels, reading=reading, permutations=1999,
       p_confirmatorio=False, primary='rho_caras', secondary='rho_vert', seconds=time.perf_counter()-start)
    write(RUN/'analysis.json', result); write(RUN/'failures.json', failures)
    csv_write(RUN/'states.csv', states); csv_write(RUN/'trajectories.csv', pairs)
    csv_write(RUN/'split_variance.csv', split_rows)
    flat = []
    for l in levels:
        a, b = l['primary'], l['secondary']; c = a.get('C1_exact', {}); r = a.get('D7_conditional_R', {})
        flat.append(dict(level=l['level'], s=l['s'], n=a['valid_pairs'], verdict=a['verdict'], regime=l['regime'],
          D=c.get('D'), p_exploratorio=c.get('p_exploratorio'), beta_X=c.get('pendiente_X'),
          V_cont=l['V_cont'], V_bin=l['V_bin'], mal_fraction=l['mal_fraction'],
          median_c250=l['median_c250'], median_q250=l['median_q250'], collapsed_fraction=l['collapsed_fraction'],
          train_acc250=l['train_acc250'], val_acc250=l['val_acc250'], power_D026=l['power_D026']['rate'],
          power_D026_lower95=l['power_D026']['lower'], D_X_cond_R=r.get('D'),
          fraction_removed=a.get('fraction_removed_descriptive'),
          D_secondary=b.get('C1_exact', {}).get('D'), p_secondary=b.get('C1_exact', {}).get('p_exploratorio'),
          verdict_secondary=b['verdict'], W_adj_legacy=a.get('W_adj_legacy', {}).get('W'),
          p_W_legacy=a.get('W_adj_legacy', {}).get('p_exploratorio')))
    csv_write(RUN/'levels.csv', flat)
    print(json.dumps(clean(reading), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
