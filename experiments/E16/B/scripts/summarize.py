#!/usr/bin/env python3
"""Síntesis descriptiva de las tablas; no modifica outcomes ni criterios."""
import argparse
import csv
import json
from pathlib import Path
import statistics


def summarize(source):
    source=Path(source)
    checks=list(csv.DictReader((source/'checks.csv').open()))
    ranks=list(csv.DictReader((source/'spectra.csv').open()))
    kernels=list(csv.DictReader((source/'kernel.csv').open()))
    by_key={(r['config'],r['check']):r for r in checks}
    ratios=[]
    for r in checks:
        if r['check']=='B_FD_0.002':
            smaller=by_key[r['config'],'B_FD_0.001']
            ratios.append(float(r['abs_error'])/float(smaller['abs_error']))
    data={'identities':sum(r['method']=='autodiff_identity' for r in checks),
          'FD_checks':sum(r['method']=='FD' for r in checks),
          'max_condition_g':max(float(r['condition_g']) for r in kernels),
          'B_FD_error_ratio_delta_to_half':{'min':min(ratios),'median':statistics.median(ratios),'max':max(ratios)},
          'by_composition':{}}
    for kind in ['sum','product','quadratic']:
        selected=[r for r in ranks if r['composition']==kind]
        data['by_composition'][kind]={'count':len(selected),
            'ranks_autodiff':sorted(set(int(r['rank_autodiff']) for r in selected)),
            'independently_validated_ranks':sum(r['rank_status']=='PASS' for r in selected),
            'mixed_term_norm_min':min(float(r['norm_B_mixed']) for r in selected),
            'mixed_term_norm_max':max(float(r['norm_B_mixed']) for r in selected),
            'max_B_FD_error':max(float(r['max_B_FD_error']) for r in selected)}
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=json.dumps(summarize(a.source),indent=2)+'\n'
    if a.output:a.output.write_text(result)
    else:print(result,end='')
