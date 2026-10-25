"""Reglas congeladas I1–I5; no ejecuta búsquedas ni modifica medidas."""
import csv
import json
from pathlib import Path
import sys
import numpy as np
import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_v1 import ROOT, STAGE, RUN, CFG, clean, write, cases, guard, sha


def finite(x):
    return isinstance(x, (int, float)) and np.isfinite(x)


def main():
    guard()
    cohort = cases()
    tests, rows, comparisons, costs = [], [], [], []
    missing, failed, mp_status = [], [], []
    inputs = {c['id']: c for c in cohort}
    literal = []
    sensitivity = []
    def test(id, kind, observed, reference, tolerance, upper=False, lower=False):
        good = finite(observed) and finite(reference)
        if good:
            delta = observed-reference
            ok = delta <= tolerance if upper else delta >= -tolerance if lower else abs(delta) <= tolerance
        else:
            delta, ok = None, False
        item = dict(id=id, kind=kind, observed=observed, reference=reference,
                    delta=delta, tolerance=tolerance, status='PASS' if ok else 'FAIL')
        tests.append(item)
        return item
    for number, c in enumerate(cohort):
        path = RUN/'states'/f'{number:03d}.json'
        if not path.exists():
            missing.append(c['id']); continue
        d = json.loads(path.read_text())
        if d['id'] != c['id']:
            raise RuntimeError('Orden inputs/resultados')
        r = d['v2']
        if r.get('rho_caras') is None:
            failed.append(dict(id=c['id'], status=r['status']))
            rows.append(dict(id=c['id'], group=c['group'], status=r['status'])); continue
        lam = max(0., float(np.linalg.eigvalsh(c['M'])[-1])); scale = np.sqrt(lam)
        def tol(ref):
            return CFG['reference_atol_scale']*scale+CFG['reference_rtol']*abs(ref)
        test(c['id'], 'rho_caras_le_rho_vert', r['rho_caras'], r['rho_vert'], tol(r['rho_vert']), upper=True)
        v1 = d.get('fresh_v1', c.get('old_v1', {}))
        v1val = v1.get('raw', {}).get('rho_borde')
        row = dict(id=c['id'], group=c['group'], n=len(c['f']), status=r['status'],
                   rho_vert=r['rho_vert'], rho_caras=r['rho_caras'], rho_edge_min=r['rho_edge_min'],
                   winner_kind=r['rho_caras_winner']['kind'],
                   winner_indices=r['rho_caras_winner'].get('face_indices', r['rho_caras_winner'].get('vertex_indices')),
                   direction_rational=r['rho_caras_winner']['direction_rational'],
                   max_face=max(len(f['face_indices']) for f in r['faces']),
                   near_face_count=sum(len(f['near_face_indices']) for f in r['faces']),
                   quad_error=r['rho_caras_winner']['quad_error'],
                   prefix_bound=r['rho_caras_winner']['prefix_bound'], tail_bound=r['rho_caras_winner']['tail_bound'],
                   geometric_vertices=r['geometric_vertices'], evaluations=r['evaluations'],
                   seconds_v2=r['seconds'], v1_rho=v1val, v1_source='fresh_1440_800' if 'fresh_v1' in d else 'archive',
                   seconds_v1=v1.get('seconds'), d_border=c.get('d_border'),
                   contrast_rounding_max=r['contrast_rounding_max'])
        if finite(v1val):
            comparisons.append(dict(id=c['id'], group=c['group'], source=row['v1_source'],
                          v1=v1val, rho_vert=r['rho_vert'], rho_caras=r['rho_caras'],
                          ratio_vert_v1=r['rho_vert']/v1val if v1val > 0 else None,
                          ratio_caras_v1=r['rho_caras']/v1val if v1val > 0 else None))
        if 'fresh_v1' in d and v1['status'] == 'RETURNED':
            costs.append(dict(id=c['id'], group=c['group'], v2_seconds=r['seconds'],
                              v1_seconds=v1['seconds'], ratio=r['seconds']/v1['seconds']))
        if 'reference' in c:
            ref = c['reference']
            if ref['known_exact'] and ref['status'] == 'PASS':
                row['reference_exact'] = ref['exact']
                test(c['id'], 'D2_known_exact', r['rho_caras'], ref['exact'], tol(ref['exact']))
            witness = ref.get('upper_witness', {})
            if witness.get('status') == 'PASS' and finite(ref['upper']):
                test(c['id'], 'D2_known_ray_upper', r['rho_caras'], ref['upper'], tol(ref['upper']), upper=True)
            if c['case']['kind'] == 'coordinate':
                # Fórmula independiente MP80 con TODAS las caras del hull exacto.
                mp.mp.dps = 80
                k = c['case']['k']
                sizes = [len(f['face_indices']) for f in r['faces'] if k in f['face_indices']]
                m = max(sizes) if sizes else 1
                exact = min(mp.mpf(1)/len(c['f']), mp.mpf(1)/m-mp.mpf(1)/len(c['f']))
                row['coordinate_formula_MP'] = str(exact)
                test(c['id'], 'D2_coordinate_MP_formula', r['rho_caras'], float(exact), tol(float(exact)))
            if (c['group'] in ['D2_gaussian', 'D2_interior'] and c['old_Q5'] == 'PASS'
                    and ref['known_exact'] and finite(v1val)):
                ct = CFG['reference_atol_scale']*scale+CFG['compatibility_rtol']*abs(v1val)
                literal.append(dict(id=c['id'], v1=v1val, rho_vert=r['rho_vert'],
                               delta=r['rho_vert']-v1val, tolerance=ct,
                               status='PASS' if abs(r['rho_vert']-v1val) <= ct else 'FAIL'))
        if 'triangle_reference' in d and 'rho_caras' in d['triangle_reference']:
            ref = d['triangle_reference']
            for target in ['rho_vert', 'rho_caras']:
                test(c['id'], 'AG_triangle_'+target, r[target], ref[target], tol(ref[target]))
            test(c['id'], 'AG_d_border_lower', r['rho_caras'], c['d_border'], tol(c['d_border']), lower=True)
            row['reference_exact'] = ref['rho_caras']
            if finite(v1val) and abs(v1val-ref['rho_caras']) <= tol(ref['rho_caras']):
                ct = CFG['reference_atol_scale']*scale+CFG['compatibility_rtol']*abs(v1val)
                literal.append(dict(id=c['id'], v1=v1val, rho_vert=r['rho_vert'],
                               delta=r['rho_vert']-v1val, tolerance=ct,
                               status='PASS' if abs(r['rho_vert']-v1val) <= ct else 'FAIL'))
        if 'witnesses' in c:
            for witness in c['witnesses']:
                ref = witness['upper_estimate']
                test(c['id'], 'G1_axial_'+str(witness['u']), r['rho_caras'], ref, tol(ref), upper=True)
        if 'sensitivity' in d:
            sr = d['sensitivity']
            for key in ['rho_vert', 'rho_caras']:
                item = test(c['id'], 'sensitivity_'+key, sr.get(key), r[key], tol(r[key]))
                sensitivity.append(item)
        if 'MP_reference' in d:
            mr = d['MP_reference']; mp_status.append(dict(id=c['id'], **mr))
            if mr.get('status') == 'MP80_NUMERICAL':
                # Si ganó un límite, la referencia evalúa su normal separada.
                target = r['rho_caras_winner']['length']
                if mr['target'] == 'exact_normal':
                    target = r['rho_caras_winner']['face_component']['length']
                test(c['id'], 'MP_ray_value', target, mr['value'], tol(mr['value'])+mr['clip_effect_bound'])
                test(c['id'], 'MP_order_contrast', mr['difference'], 0., tol(mr['value']))
        rows.append(row)
    control = json.loads((RUN/'controls.json').read_text())
    complete = not missing and not failed
    uncertain_mp = len(mp_status) != 4 or any(m['status'] != 'MP80_NUMERICAL' for m in mp_status)
    failed_tests = [t for t in tests if t['status'] == 'FAIL']
    i2 = 'FAIL' if failed_tests else 'INCONCLUSIVE' if not complete or uncertain_mp else 'PASS'
    i3 = 'FAIL' if any(t['status'] == 'FAIL' for t in literal) else 'PASS' if complete and literal else 'INCONCLUSIVE'
    cost = {}
    if costs:
        cost = dict(count=len(costs), median_v2_seconds=float(np.median([c['v2_seconds'] for c in costs])),
                    p95_v2_seconds=float(np.percentile([c['v2_seconds'] for c in costs], 95)),
                    median_v1_seconds=float(np.median([c['v1_seconds'] for c in costs])),
                    median_ratio=float(np.median([c['ratio'] for c in costs])))
    i4 = 'INCONCLUSIVE' if len(costs) != 102 else 'PASS_DESCRIPTIVE' if (cost['median_v2_seconds'] <= 5
            and cost['p95_v2_seconds'] <= 15 and cost['median_ratio'] <= 5) else 'FAIL_DESCRIPTIVE'
    groups = []
    for group in sorted(set(c['group'] for c in cohort)):
        sub = [r for r in rows if r['group'] == group and finite(r.get('rho_caras'))]
        comp = [c for c in comparisons if c['group'] == group and finite(c['ratio_caras_v1'])]
        groups.append(dict(group=group, states=sum(c['group'] == group for c in cohort), complete=len(sub),
                face_wins=sum(r['winner_kind'] == 'face' for r in sub),
                median_seconds=float(np.median([r['seconds_v2'] for r in sub])) if sub else None,
                median_caras_vert=float(np.median([r['rho_caras']/r['rho_vert'] for r in sub if r['rho_vert'] > 0])),
                median_caras_v1=float(np.median([c['ratio_caras_v1'] for c in comp])) if comp else None))
    summary = dict(verdicts=dict(I1='PASS' if control['status'] == 'PASS' else 'FAIL', I2=i2, I3=i3, I4=i4,
                            I5='PASS_DESCRIPTIVE'), cases=len(cohort), completed=len(rows), missing=missing, failed=failed,
                   test_count=len(tests), failed_tests=failed_tests, MP=mp_status, costs=cost, groups=groups,
                   literal_compatibility=dict(count=len(literal), failed=sum(t['status'] == 'FAIL' for t in literal)),
                   sensitivity_count=len(sensitivity)//2, unknown_references_preserved=True)
    write(RUN/'summary.json', summary)
    write(RUN/'validation.json', dict(tests=tests, literal_compatibility=literal, costs=costs, comparisons=comparisons))
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (RUN/'states.csv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(clean(v)) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    print(json.dumps(clean(summary), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
