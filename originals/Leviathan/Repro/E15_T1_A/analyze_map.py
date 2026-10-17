from pathlib import Path
import csv,json,collections,hashlib
import numpy as np
from scipy.stats import spearmanr,pearsonr
P=Path(__file__).resolve().parent
rows=[json.loads(p.read_text()) for p in sorted((P/'states').glob('*/result.json'))]
old=list(csv.DictReader((P/'inherited_results_states.csv').open()));lookup={(int(r['split']),int(r['init']),r['regime']):r for r in old}
metrics=['C_A','lambda_1pct','lambda_01pct','R_eff','frac50','frac90']
joined=[]
for r in rows:
 x=r.copy();orig=lookup[r['split'],r['init'],r['regime']]
 for m in metrics:
  val=orig.get(m+'_median');x[m]=float(val) if val and val.lower()!='nan' else None
 common=[]
 for ph in [0,1]:
  f=P/'states'/r['state']/'jacobi'/f'n512_phase{ph}.npz'
  if f.exists():
   with np.load(f) as z:common.append(z['determinant'])
 x['min_abs_det_Dexp_common512']=min(float(abs(a).min()) for a in common) if len(common)==2 else None
 x['max_Dexp_condition_common512']=max(float((np.maximum(1,abs(a))/np.minimum(1,abs(a))).max()) for a in common) if len(common)==2 else None
 joined.append(x)
fields=sorted(set(k for r in joined for k in r))
with (P/'linked_geometry.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(joined)
def dist(a):
 a=[x for x in a if x is not None and np.isfinite(x)]
 return dict(n=len(a),min=min(a),q25=float(np.quantile(a,.25)),median=float(np.median(a)),q75=float(np.quantile(a,.75)),max=max(a)) if a else dict(n=0)
summary={'n':len(rows),'counts':{},'by_split':{},'by_init':{},'distributions':{},'correlations':[],'limitations':['No confirmatory inference; no causal interpretation','Conjugate and A_embed event distributions conditional on detected events. Censored values are not maxima.','No certified lower bounds r_inj; upper bounds numerical only','C_A and concentration missing in invalid C1 domains; no imputation or repaired domain estimands','Splits share Wine samples and are not independent datasets']}
for regime in ['true','random']:
 rr=[r for r in rows if r['regime']==regime];summary['counts'][regime]=dict(collections.Counter(r['classification'] for r in rr));summary['by_split'][regime]={str(s):dict(collections.Counter(r['classification'] for r in rr if r['split']==s)) for s in range(8)};summary['by_init'][regime]={str(j):dict(collections.Counter(r['classification'] for r in rr if r['init']==j)) for j in range(5)}
 summary['distributions'][regime]={'r_conj_detected':dist([r.get('r_conj') for r in rr]),'r_inj_numerical_upper':dist([r.get('r_inj_upper') for r in rr]),'A_embed_event_estimates':dist([r.get('A_embed') for r in rr if not r['A_embed_censored']]),'A_embed_ratio_event_estimates':dist([r.get('A_embed_ratio') for r in rr if not r['A_embed_censored']]),'area_right_censored_count':sum(r['A_embed_censored'] and r.get('A_embed')is not None for r in rr),'unknown_area_count':sum(r.get('A_embed')is None for r in rr),'censoring_note':'Observed to nominal A=0.02; no mathematical certificate or maximum beyond nominal.'}
 for m in metrics:
  for outcome in ['min_abs_det_Dexp_common512','max_Dexp_condition_common512','r_conj','A_embed']:
   eligible=[r for r in joined if r['regime']==regime and r.get(m)is not None and r.get(outcome)is not None and (outcome!='A_embed' or not r['A_embed_censored'])]
   x=[r[m] for r in eligible];y=[r[outcome] for r in eligible];ok=len(x)>=3 and np.ptp(x)>0 and np.ptp(y)>0
   summary['correlations'].append(dict(regime=regime,metric=m,outcome=outcome,n=len(x),spearman=float(spearmanr(x,y).statistic) if ok else None,pearson=float(pearsonr(x,y).statistic) if ok else None,note='Descriptive pooled states, hierarchical dependence; no p values' if ok else 'Not estimable: unavailable pairs, censoring or insufficient variation'))
summary['positive_states']=[r['state'] for r in rows if r['classification']=='GEOMETRIC_NONINJECTIVITY'];summary['cut_locus_probable']=[r['state'] for r in rows if r.get('cut_locus_probable')]
summary['new_cpu_seconds']=sum(r.get('new_cpu_seconds',0) for r in rows);summary['new_state_wall_seconds_sum']=sum(r.get('new_wall_seconds',0) for r in rows);summary['gate']='COMPLETE' if len(rows)==80 else 'INCOMPLETE';summary['T1_B']='OPEN_POPULATION_DESIGN' if len(summary['positive_states'])>2 else 'SPECIFIC_CASE_SERIES_ONLY' if set(summary['positive_states'])=={'split0_j1_true','split0_j3_true'} else 'UNDETERMINED'
(P/'descriptive_summary.json').write_text(json.dumps(summary,indent=2))
with (P/'correlations.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['regime','metric','outcome','n','spearman','pearson','note']);w.writeheader();w.writerows(summary['correlations'])
# Hierarchical descriptive rows and contrast availability, no survivor inference.
with (P/'split_summary.csv').open('w') as f:
 fields=['split','regime','n','injective','noninjective','inconclusive','numerical_failure','median_min_abs_det','median_max_condition'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for s in range(8):
  for g in ['true','random']:
   rr=[r for r in rows if r['split']==s and r['regime']==g];co=collections.Counter(r['classification'] for r in rr);w.writerow(dict(split=s,regime=g,n=len(rr),injective=co['INJECTIVE_AT_NOMINAL_RADIUS'],noninjective=co['GEOMETRIC_NONINJECTIVITY'],inconclusive=co['INCONCLUSIVE'],numerical_failure=co['NUMERICAL_FAILURE'],median_min_abs_det=np.median([r['min_abs_det_Dexp'] for r in rr if 'min_abs_det_Dexp'in r]) if rr else None,median_max_condition=np.median([r['max_Dexp_condition'] for r in rr if 'max_Dexp_condition'in r]) if rr else None))
contrasts=[]
for g in ['true','random']:
 for m in metrics:
  for c in ['INJECTIVE_AT_NOMINAL_RADIUS','GEOMETRIC_NONINJECTIVITY']:
   rr=[r for r in joined if r['regime']==g and r['classification']==c];contrasts.append(dict(regime=g,metric=m,classification=c,n_states=len(rr),available=dist([r[m] for r in rr]),note='Missing C1 domains not imputed'))
(P/'group_contrasts.json').write_text(json.dumps(contrasts,indent=2))
try:
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained');colors={'true':'#146b8c','random':'#db8835'}
 for g in ['true','random']:
  rr=[r for r in rows if r['regime']==g];x=np.arange(8)+(0.15 if g=='random' else -.15);h=[sum(r['split']==s and r['classification']=='GEOMETRIC_NONINJECTIVITY' for r in rr) for s in range(8)];axs[0,0].bar(x,h,.3,label=g,color=colors[g]);
  for r in rr:
   if r.get('A_embed')is not None:axs[0,1].scatter(r['split']+(r['init']-2)*.04+(.14 if g=='random' else -.14),r['A_embed'],marker='^' if r['A_embed_censored'] else 'o',color=colors[g],alpha=.65,s=26)
  valid=[r for r in joined if r['regime']==g and r['C_A']is not None and r.get('min_abs_det_Dexp_common512')is not None];axs[1,0].scatter([r['C_A'] for r in valid],[r['min_abs_det_Dexp_common512'] for r in valid],c=colors[g],label=g,alpha=.75)
  vals=[r['A_embed'] for r in rr if not r['A_embed_censored'] and r.get('A_embed')is not None];axs[1,1].scatter(np.arange(len(vals)),vals,c=colors[g],label=g)
 axs[0,0].set(title='No inyectividad por split (5 estados por régimen)',xlabel='Split',ylabel='Estados positivos');axs[0,0].set_xticks(range(8));axs[0,0].set_ylim(0,5);axs[0,0].legend()
 axs[0,1].axhline(.02,color='gray',ls='--');axs[0,1].set(title='Área: círculo=evento; triángulo=censura nominal',xlabel='Split (desplazamiento por init)',ylabel='A_embed estimada / nivel de censura')
 axs[1,0].set_xscale('log');axs[1,0].set_yscale('log');axs[1,0].set(title='Asociación descriptiva donde C_A está disponible',xlabel='C_A',ylabel='Mínimo |det Dexp| (512, ambas fases)');axs[1,0].legend()
 axs[1,1].axhline(.02,color='gray',ls='--');axs[1,1].set(title='Sólo áreas con evento detectado',xlabel='Índice del evento dentro del régimen',ylabel='A_embed estimada')
 fig.suptitle('Leviathan / E15-T1-A — diagnósticos descriptivos; sin inferencia causal');fig.savefig(P/'population_diagnostics.png',dpi=170);plt.close(fig)
except ImportError as e:print('Plot dependency unavailable',e)
print(json.dumps({k:summary[k] for k in ['n','counts','positive_states','cut_locus_probable','gate','T1_B']},indent=2))
