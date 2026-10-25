"""Postproceso reproducible; sólo lee resultados propios, no repite geometría."""
import csv
import json
from pathlib import Path
import numpy as np

STAGE = Path(__file__).resolve().parents[1]
RUN = STAGE/'results/run_v2'


def main():
    rows = [json.loads(p.read_text()) for p in sorted(RUN.glob('*.json'))
            if p.name.startswith(('2026', 'wine_'))]
    by_id = {r['id']: r for r in rows}
    ok = [r for r in rows if r['status'] == 'OK']
    tests = {}
    tests['complete_86'] = len(ok) == len(rows) == 86
    tests['all_algebra'] = bool(ok) and all(r['metrics']['algebra_pass'] for r in ok)
    tests['grouped_nondiagonal'] = sum(r['name'] == 'grouped3' for r in ok) == 3 and all(
        r['metrics']['offdiag_fraction'] > .5 for r in ok if r['name'] == 'grouped3')
    tests['dominance_counterexample'] = sum(r['name'] == 'lopsided' for r in ok) == 3 and all(
        not r['metrics']['dominance_agrees'] for r in ok if r['name'] == 'lopsided')
    matched, sameX, embeds, sensitivities, post, slopes = [], [], [], [], [], []
    for seed in [2026102700, 2026102701, 2026102702]:
        def get(name):
            return by_id.get(f'{seed}_{name}')
        required = ['matched_q070', 'matched_q085', 'uniform_a1', 'uniform_a005']
        if any(not get(name) or get(name)['status'] != 'OK' for name in required):
            continue
        a, b = get('matched_q070'), get('matched_q085')
        G1, G2 = np.array(a['G_grid']), np.array(b['G_grid'])
        rel = float(np.linalg.norm(G1-G2)/np.linalg.norm(G1))
        item = dict(seed=seed, relative_G=rel, delta_X=abs(a['metrics']['X']-b['metrics']['X']),
                    rho_ratio=b['native']['rho_borde']/a['native']['rho_borde'],
                    max_eig_fraction=max(a['metrics']['maxeig_fraction'], b['metrics']['maxeig_fraction']),
                    min_effective_rank=min(a['metrics']['effective_rank'], b['metrics']['effective_rank']))
        item['pass'] = (rel <= 1e-5 and item['delta_X'] >= .5 and item['max_eig_fraction'] < .14
                        and item['min_effective_rank'] > 10)
        matched.append(item)
        c, d = get('uniform_a1'), get('uniform_a005')
        ratio = d['native']['rho_borde']/c['native']['rho_borde']
        Gc, Gd = np.array(c['G_grid']), np.array(d['G_grid'])
        scale = float(np.sum(Gc*Gd)/np.sum(Gc*Gc))
        ratio_error = abs(ratio/np.sqrt(scale)-1)
        sameX.append(dict(seed=seed, delta_X=abs(c['metrics']['X']-d['metrics']['X']),
                          rho_ratio=ratio, field_scale=scale, rho_scaling_error=float(ratio_error),
                          pass_test=abs(c['metrics']['X']-d['metrics']['X']) < 1e-10
                          and abs(ratio-1) > .05 and ratio_error < 1e-4))
        for q in ['070', '085']:
            base, pert = get('matched_q'+q), get('matched_pert_q'+q)
            if pert and pert['status'] == 'OK':
                sensitivities.append(dict(seed=seed, q=q,
                                          relative_rho=pert['native']['rho_borde']/base['native']['rho_borde'],
                                          X=pert['metrics']['X']))
            emb = by_id.get('wine_matched_q'+q)
            if seed == 2026102700 and emb and emb['status'] == 'OK':
                gerr = float(np.linalg.norm(np.array(emb['G_grid'])-np.array(base['G_grid']))/np.linalg.norm(base['G_grid']))
                embeds.append(dict(q=q, relative_G=gerr, pass_test=gerr <= 1e-5))
        rr = [get(f'uniform_eps_{e}') for e in [4, 6, 8]]
        if all(r and r['status'] == 'OK' for r in rr):
            x = np.log([1e-4, 1e-6, 1e-8])
            slopes.append(dict(seed=seed,
                               trace_slope=float(np.polyfit(x, np.log([r['metrics']['trace'] for r in rr]), 1)[0]),
                               rho_slope=float(np.polyfit(x, np.log([r['native']['rho_borde'] for r in rr]), 1)[0])))
    for r in ok:
        if r['name'].startswith('post_') and r['construction']['epsilon'] == 1e-8:
            lo, hi = r['coordinate_lower_ratio'], r['coordinate_upper_ratio']
            post.append(dict(id=r['id'], lower=lo, upper=hi, pass_test=lo >= .95 and hi <= 1.05))
    tests['same_G_different_X'] = len(matched) == 3 and all(i['pass'] for i in matched)
    tests['same_X_different_G'] = len(sameX) == 3 and all(i['pass_test'] for i in sameX)
    tests['wine_embedding'] = len(embeds) == 2 and all(i['pass_test'] for i in embeds)
    tests['post_coordinate'] = len(post) == 9 and all(i['pass_test'] for i in post)
    stats = json.loads((RUN/'statistic_panels.json').read_text())
    exact = stats['exact_affine']
    tests['W_counterexample'] = (abs(exact['W_C1']-.7) <= 1e-12 and
                                abs(exact['Pearson_X_e']) < 1e-10 and
                                exact['undefined_both_linear'] == 64)
    summary = dict(total=len(rows), OK=len(ok), errors=[r['id'] for r in rows if r['status'] != 'OK'],
                   tests=tests, matched=matched, sameX=sameX, wine_embeddings=embeds,
                   sensitivities=sensitivities, post_coordinate=post, scaling_slopes=slopes,
                   native_fidelity={v: sum(r.get('native_fidelity') == v for r in ok)
                                    for v in ['PASS', 'FAIL', 'ZERO_GEOMETRY_FLOATING_UNRESOLVED']},
                   interpolation_resolved=sum(r['metrics']['interpolation_resolved'] for r in ok),
                   max_M_error=max((r['metrics']['M_error'] for r in ok), default=None),
                   max_R_error=max((r['metrics']['R_error'] for r in ok), default=None),
                   max_U_error=max((r['metrics']['U_error'] for r in ok), default=None),
                   Q6='PASS' if tests['complete_86'] and tests['all_algebra'] and tests['grouped_nondiagonal'] and tests['dominance_counterexample'] else 'INCONCLUSIVE',
                   Q7='PASS' if tests['post_coordinate'] else 'INCONCLUSIVE',
                   Q8='PASS' if tests['same_G_different_X'] and tests['same_X_different_G'] and tests['W_counterexample'] else 'INCONCLUSIVE',
                   Q9='PASS' if all(tests.values()) else 'INCONCLUSIVE', Q10='PASS_DESCRIPTIVE',
                   D6_cause='INCONCLUSIVE')
    with (RUN/'summary.json').open('x') as f:
        json.dump(summary, f, indent=2, allow_nan=False)
    fields = ['id', 'status', 'X', 'min_py', 'trace', 'maxdiag_fraction', 'maxeig_fraction',
              'effective_rank', 'offdiag_fraction', 'rank_A', 'gamma', 'algebra_pass',
              'M_error', 'rho', 'native_fidelity', 'seconds', 'warnings']
    with (RUN/'networks.csv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            m = r.get('metrics', {})
            row = {k: m.get(k) for k in fields}
            row.update(id=r['id'], status=r['status'], rho=r.get('native', {}).get('rho_borde'),
                       native_fidelity=r.get('native_fidelity'), seconds=r['seconds'], warnings=len(r['warnings']))
            w.writerow(row)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
