"""Cierre descriptivo desde los archivos G1; no entrena ni repite rho."""
import csv
import json
from pathlib import Path
import numpy as np
from analysis_v1 import family_summary
from support_v1 import ROOT, STAGE, RUN, ARRAYS, clean, write, sha


def main():
    rows = [json.loads(p.read_text()) for p in sorted((RUN/'states').glob('*.json'))]
    summaries = [family_summary(name, [r for r in rows if r['family'] == name]) for name in ['R27', 'P60', 'W27']]
    write(RUN/'summary.json', dict(exploratory=True, expected_states=2100, recorded_states=len(rows),
                                  families=summaries, p_values_computed=False,
                                  caution='APARECE es un criterio descriptivo congelado, no confirmación ni causalidad.'))
    for family in summaries:
        write(RUN/(family['family']+'_summary.json'), family)
    fields = ['id', 'family', 'split', 'initialization', 'update', 'status', 'M_valid', 'rho_valid',
              'rho', 'chord', 'trace', 'c', 'q', 'k_star_id', 'k_hard_id', 'hard_match', 'py_star',
              'log1m_star', 'X', 'collapsed', 'train_acc', 'train_loss', 'val_acc', 'val_loss',
              'rankF', 'gamma_minF', 'diagonal_odds_error', 'warnings', 'seconds']
    with (RUN/'states.csv').open('x') as file:
        w = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for r in rows:
            m = r.get('metrics', {})
            row = {key: r.get(key, m.get(key)) for key in fields}
            row.update(rho=r.get('rho', {}).get('rho_borde'), chord=m.get('chord', {}).get('value'),
                       train_acc=r.get('train', {}).get('acc'), train_loss=r.get('train', {}).get('loss'),
                       val_acc=r.get('validation', {}).get('acc'), val_loss=r.get('validation', {}).get('loss'),
                       rankF=m.get('rank_F_1e10'), gamma_minF=m.get('gamma_minF'),
                       diagonal_odds_error=m.get('diagonal_odds_relative_error'), warnings=len(r.get('warnings', [])))
            w.writerow(row)
    with (RUN/'by_update.csv').open('x') as file:
        fields = ['family']+list(summaries[0]['visits'][0])
        w = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for fam in summaries:
            for visit in fam['visits']:
                w.writerow(dict(family=fam['family'], **visit))
    with (RUN/'hypotheses.csv').open('x') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['family', 'H1', 'H2', 'H3', 'H4', 'H5', 'late_collapsed', 'H2_match', 'H3_r', 'H3_W',
                    'H4_both', 'H4_close', 'H5_n', 'H5_D', 'H5_beta', 'H5_D_even', 'H5_D_odd', 'H5_W_legacy', 'audits_pass'])
        for f in summaries:
            h5 = f['H5']
            halves = h5.get('halves', [{}, {}])
            w.writerow([f['family'], *[f[h]['verdict'] for h in ['H1', 'H2', 'H3', 'H4', 'H5']],
                        f['H1']['late_collapsed'], f['H2']['fraction'], f['H3']['pooled_spearman'], f['H3']['W250'],
                        f['H4']['both_events'], f['H4']['close_fraction'], h5['n'],
                        h5.get('predictive', {}).get('D'), h5.get('predictive', {}).get('beta'),
                        halves[0].get('D'), halves[1].get('D'), h5.get('W_adj_legacy'), f['audit']['pass_count']])
    with (RUN/'events.csv').open('x') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['family', 'split', 'initialization', 'valid', 'mem_update', 'mem_lower', 'col_update',
                    'col_lower', 'mem_censored', 'col_censored', 'index_difference', 'close'])
        for f in summaries:
            for event in f['H4']['per_trajectory']:
                m, c = event.get('memorization', {}), event.get('collapse', {})
                w.writerow([f['family'], event['split'], event['initialization'], event['valid'],
                            m.get('update'), m.get('interval', [None])[0], c.get('update'), c.get('interval', [None])[0],
                            m.get('right_censored'), c.get('right_censored'), event.get('index_difference'), event.get('close')])
    with (RUN/'audits.csv').open('x') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['id', 'rho_720_400', 'rho_1440_800', 'relative_error', 'pass', 'seconds'])
        for r in rows:
            if r['initialization'] == 0 and r['update'] in [10, 250]:
                w.writerow([r['id'], r.get('rho', {}).get('rho_borde'), r.get('audit', {}).get('rho_borde'),
                            r.get('audit_relative_error'), r.get('audit_pass'), r.get('audit_seconds')])
    with (STAGE/'external_manifest.csv').open('x') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['path', 'sha256', 'bytes'])
        for p in sorted(ARRAYS.glob('*')):
            if p.is_file():
                w.writerow([str(p), sha(p), p.stat().st_size])
    print(json.dumps(clean({f['family']: {h: f[h]['verdict'] for h in ['H1', 'H2', 'H3', 'H4', 'H5']} for f in summaries}), indent=2))


if __name__ == '__main__':
    main()
