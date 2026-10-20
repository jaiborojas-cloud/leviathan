#!/usr/bin/env python3
"""Descriptivos deterministas a partir de las tablas, sin cambiar decisiones."""
import argparse
import csv
from decimal import Decimal, localcontext
import json
from pathlib import Path


def summarize(folder):
    folder=Path(folder)
    ranks=list(csv.DictReader((folder/'ranks.csv').open()))
    negatives=list(csv.DictReader((folder/'negative_controls.csv').open()))
    with localcontext() as ctx:
        ctx.prec=60
        d=Decimal
        main=[r for r in ranks if r['point']!='control']
        ratios=[d(r['FD4_error_0.002'])/d(r['FD4_error_0.001']) for r in main]
        out={'main_min_sigma_min':str(min(d(r['sigma_min']) for r in main)),
             'main_min_sigma_to_tau':str(min(d(r['sigma_min'])/d(r['tau']) for r in main)),
             'max_FD4_to_allowed_error':str(max(d(r['FD4_error_0.002'])/(d(r['tau'])/10) for r in ranks)),
             'FD4_error_ratio_delta_to_half':{'min':str(min(ratios)),'max':str(max(ratios))},
             'min_negative_error_to_tau':str(min(d(r['transported_error'])/d(r['threshold']) for r in negatives)),
             'controls_rank_counts':{str(i):sum(r['point']=='control' and int(r['rank_reference'])==i for r in ranks) for i in [0,1]},
             'by_composition':{kind:{'count':sum(r['composition']==kind for r in main),
                                   'ranks':sorted(set(int(r['rank_reference']) for r in main if r['composition']==kind))}
                               for kind in ['sum','product','quadratic']}}
        return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--output',type=Path)
    args=p.parse_args();text=json.dumps(summarize(args.folder),indent=2)+'\n'
    if args.output:args.output.write_text(text)
    else:print(text,end='')
