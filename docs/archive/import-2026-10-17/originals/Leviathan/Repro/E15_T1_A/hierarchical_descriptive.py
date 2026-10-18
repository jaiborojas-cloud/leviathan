from pathlib import Path
import csv,json
import numpy as np
from scipy.stats import spearmanr
P=Path(__file__).resolve().parent;rows=list(csv.DictReader((P/'linked_geometry.csv').open()));out=[]
for regime in ['true','random']:
 for m in ['C_A','lambda_1pct','lambda_01pct','R_eff','frac50','frac90']:
  for outcome in ['min_abs_det_Dexp_common512','max_Dexp_condition_common512']:
   medians=[]
   for s in range(8):
    rr=[r for r in rows if r['regime']==regime and int(r['split'])==s and r[m] and r.get(outcome)]
    x=[float(r[m]) for r in rr];y=[float(r[outcome]) for r in rr];valid=len(x)>=3 and np.ptp(x)>0 and np.ptp(y)>0
    out.append(dict(regime=regime,metric=m,outcome=outcome,level='within_split',split=s,n=len(x),rho=float(spearmanr(x,y).statistic) if valid else None,note='Descriptive; five inits at most; missing domains retained as missing'))
    if rr:medians.append((float(np.median(x)),float(np.median(y)),len(rr)))
   valid=len(medians)>=3 and np.ptp([v[0] for v in medians])>0 and np.ptp([v[1] for v in medians])>0
   out.append(dict(regime=regime,metric=m,outcome=outcome,level='split_medians',split='all',n=len(medians),rho=float(spearmanr([v[0] for v in medians],[v[1] for v in medians]).statistic) if valid else None,note='Descriptive only; available-state medians. Complete splits='+str(sum(v[2]==5 for v in medians))+'/8; not confirmatory'))
with (P/'hierarchical_correlations.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['regime','metric','outcome','level','split','n','rho','note']);w.writeheader();w.writerows(out)
print('Hierarchical descriptors',len(out))
