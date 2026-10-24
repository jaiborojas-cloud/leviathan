#!/usr/bin/env python3
"""Deriva/valida tablas descriptivas desde CSV, sin ejecutar geometría."""
from ag_common_v1 import *
from scipy.stats import spearmanr
import argparse

def derive():
 r=ROOT/'results/run_v1';a=rows(r/'states.csv');tri=a[:40];grids=rows(r/'rho_resolutions.csv')
 truth={'group':'triangle','states':40,'rho_over_true_median':float(np.median([float(x['ratio_true']) for x in tri])),'rho_over_true_max':max(float(x['ratio_true']) for x in tri),'rho_vs_true_spearman':float(spearmanr([float(x['rho']) for x in tri],[float(x['d_border_exact']) for x in tri]).statistic),'escape_over_true_min':min(float(x['escape_to_true']) for x in tri),'escape_over_true_max':max(float(x['escape_to_true']) for x in tri),'rho_exact_error_max':max(float(x['rho_exact_error']) for x in tri),'rho_resolution_error_max_all':max(float(x['rho_resolution_error']) for x in a),'MP_directional_speed_error_max_all':max(float(x['MP_speed_error']) for x in a),'max_steps_AF':max(int(x['steps']) for x in a[40:]),'max_steps_triangle':max(int(x['steps']) for x in tri),'distance_true_AF':'UNKNOWN','interpretation':'Comparación con respuesta analítica sólo en triangle; descriptiva, sin nueva regla confirmatoria.'}
 checks=[]
 for group in ['triangle','AF','ALL']:
  rr=[x for x in a if group=='ALL' or x['group']==group]
  for n in [720,1440]:
   for order in [400,800]:
    rh=[float(next(g['augmented_min'] for g in grids if g['state']==s['state'] and int(g['n'])==n and int(g['order'])==order)) for s in rr]
    for method in ['coarse_escape','d_escape']:
     dd=[float(s[method]) for s in rr];rat=np.array(rh)/dd;checks.append({'group':group,'n':n,'order':order,'escape_variant':method,'min_ratio':float(min(rat)),'median_ratio':float(np.median(rat)),'max_ratio':float(max(rat)),'spearman':float(spearmanr(rh,dd).statistic)})
 assert min(x['min_ratio'] for x in checks)>1
 assert all(x['max_ratio']>2 for x in checks)
 assert all(x['spearman']<.9 for x in checks if x['group'] in ['AF','ALL'])
 assert all(x['spearman']>.9 for x in checks if x['group']=='triangle')
 return truth,checks

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args();truth,checks=derive()
 if args.out:
  if args.out.exists():raise FileExistsError(args.out)
  args.out.mkdir(parents=True);write(args.out/'known_truth_summary.json',truth);table(args.out/'stability_from_archives.csv',checks)
 else:
  r=ROOT/'results/run_v1';assert truth==json.loads((r/'known_truth_summary.json').read_text());saved=rows(r/'stability_from_archives.csv');assert len(saved)==len(checks)
  for expected,actual in zip(checks,saved):assert all(str(v)==actual[k] for k,v in expected.items())
  print('PASS_DERIVED: verdad conocida y24 contrastes desde archivos, sin geometría')
