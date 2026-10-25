"""Postproceso desde retornos preservados; no repite el análisis del sujeto."""
import csv
import json
from pathlib import Path
import numpy as np
from independent_v1 import wilson
from support_v1 import STAGE, ROOT, ARRAYS, sha, write

RUN = STAGE/'results/run_v1'


def main():
    comparisons = [json.loads(p.read_text()) for p in sorted((RUN/'comparisons').glob('*.json'))]
    cli = [json.loads(p.read_text()) for p in sorted((RUN/'cli').glob('*.json'))]
    mc = [json.loads(line) for line in (RUN/'monte_carlo.jsonl').read_text().splitlines()]
    rates = []
    for scenario in ['N0', 'N1', 'N2', 'P010', 'P015']:
        rr = [r for r in mc if r['scenario'] == scenario]
        good = [r for r in rr if r['status'] == 'OK']
        k = sum(r['verdict'] == 'PASS' for r in good)
        bounds = wilson(k, len(good))
        sensitivity = [dict(replicate=r['replicate'], B199=r['verdict'], B5000=r['sensitivity']['verdict'],
                            p199=r['result']['p'], p5000=r['sensitivity']['p'])
                       for r in good if r['sensitivity']]
        author_interval = wilson(4, 96) if scenario == 'N0' else (
            wilson(22, 32) if scenario == 'P010' else (wilson(32, 32) if scenario == 'P015' else None))
        overlap = bool(bounds[0] <= author_interval[1] and author_interval[0] <= bounds[1]) if author_interval else None
        interpretation = 'DESCRIPTIVE_CONDITIONAL_NULL' if scenario == 'N1' else (
            'NO_INFLATION_AT_MEASURED_SCOPE' if scenario.startswith('N') and bounds[1] <= .075 else
            ('INFLATION' if scenario.startswith('N') and bounds[0] > .05 else
             ('COMPATIBLE_WITH_SECTION6' if overlap else 'INCONCLUSIVE')))
        rates.append(dict(scenario=scenario, completed=len(good), requested=400, PASS=k,
                          fraction=k/len(good), Wilson95=bounds, B=199,
                          author_Wilson95=author_interval, author_interval_overlap=overlap,
                          interpretation=interpretation, sensitivity=sensitivity,
                          realised_r_mean=float(np.mean([r['realised_r'] for r in good])) if scenario.startswith('P') else None))
    tests = dict(all32_comparisons=len(comparisons) == 32 and all(r['status'] == 'PASS' for r in comparisons),
                 monte_carlo_complete=len(mc) == 2000 and all(r['status'] == 'OK' for r in mc),
                 all17_CLI_recorded=len(cli) == 17 and all(r['status'] == 'RECORDED' for r in cli),
                 no_inflation_valid_nulls=all(r['Wilson95'][1] <= .075 for r in rates if r['scenario'] in ['N0', 'N2']),
                 compatible_power=all(r['author_interval_overlap'] for r in rates if r['scenario'].startswith('P')))
    summary = dict(A1='FAIL', A2='PASS' if tests['all32_comparisons'] else 'FAIL',
                   A3='FAIL', A4='PASS' if all(tests.values()) else 'INCONCLUSIVE', A5='PASS_DESCRIPTIVE',
                   checks=tests, rates=rates,
                   max_D_error=max(r.get('D_error', 0) for r in comparisons),
                   max_D_fast_error=max(r.get('D_fast_error', 0) for r in comparisons),
                   max_explicit_fast_null_error=max(r['independent'].get('max_fast_explicit_null_error', 0) for r in comparisons),
                   all_operational_p_identical=all(r.get('p_identical', True) for r in comparisons),
                   literal_p_discrepancies=[r['case'] for r in comparisons if r.get('literal_p_differs')],
                   subject_errors=[r['case'] for r in cli if r.get('returncode') != 0],
                   violated_CLI_contracts=[r['case'] for r in cli if not r.get('contract_pass')],
                   audit_execution_errors=[r['case'] for r in cli+comparisons if r['status'] == 'AUDIT_ERROR'],
                   snapshots='6b17d25216381238f5a0f38f8eb9e7eb87f0a4da',
                   limitations=['B199 en Monte Carlo; no tamaño exacto B5000',
                                'potencia retrospectiva, no garantía de cohorte nueva',
                                'X=h(L) puede mejorar base cúbica sin información condicional',
                                'datos de descubrimiento gastados; no confirmación'])
    write(RUN/'summary.json', summary)
    with (RUN/'A2_comparisons.csv').open('x') as f:
        fields = ['case', 'status', 'B', 'D_subject', 'D_reference', 'D_error', 'p_subject',
                  'p_reference', 'beta_subject', 'verdict_reference', 'seconds']
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for r in comparisons:
            s = r['subject'].get('primary', {})
            q = r.get('independent', {})
            w.writerow(dict(case=r['case'], status=r['status'], B=r.get('B'), D_subject=s.get('D'),
                            D_reference=q.get('D'), D_error=r.get('D_error'), p_subject=s.get('p'),
                            p_reference=q.get('p'), beta_subject=s.get('pendiente_X'),
                            verdict_reference=r.get('reference_verdict'), seconds=r['seconds']))
    with (RUN/'A3_CLI.csv').open('x') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['case', 'expected', 'returncode', 'actual_verdict', 'n_table', 'contract_pass', 'seconds'])
        for r in cli:
            o = r.get('output') or {}
            w.writerow([r['case'], r.get('expected'), r.get('returncode'), o.get('veredicto'),
                        o.get('n_tabla'), r.get('contract_pass'), r['seconds']])
    with (RUN/'A4_rates.csv').open('x') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['scenario', 'PASS', 'n', 'fraction', 'Wilson95_low', 'Wilson95_high', 'B', 'interpretation'])
        for r in rates:
            w.writerow([r['scenario'], r['PASS'], r['completed'], r['fraction'], *r['Wilson95'], r['B'], r['interpretation']])
    with (STAGE/'external_manifest.csv').open('x') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['path', 'sha256', 'bytes'])
        for p in sorted(ARRAYS.iterdir()):
            if p.is_file():
                w.writerow([str(p), sha(p), p.stat().st_size])
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
