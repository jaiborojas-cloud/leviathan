"""Design sensitivity only; no neural states, no observed future outcomes."""
from pathlib import Path
import math,csv,json
import numpy as np
from scipy.stats import binom,betabinom,binomtest,hypergeom
P=Path(__file__).resolve().parent

def save(name,rows):
 with (P/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

def distribution(N,p,icc):
 if icc==0:return binom.pmf(np.arange(N+1),N,p)
 a=p*(1/icc-1);b=(1-p)*(1/icc-1)
 block=betabinom.pmf(np.arange(6),5,a,b);z=np.array([1.])
 for _ in range(N//5):z=np.convolve(z,block)
 return z/z.sum()
rows=[]
for N in [640,800]:
 for p in [.025,.05,.10,.20]:
  for icc in [0,.1,.3]:
   pm=distribution(N,p,icc);cdf=pm.cumsum()
   rows.append(dict(N=N,p=p,within_split_ICC=icc,expected=N*p,sd=float(np.sqrt(np.dot((np.arange(N+1)-N*p)**2,pm))),count_low95=int(np.searchsorted(cdf,.025)),count_high95=int(np.searchsorted(cdf,.975)),prob_at_least10=float(pm[10:].sum()),prob_at_least20=float(pm[20:].sum()),prob_at_least30=float(pm[30:].sum())))
save('event_sensitivity.csv',rows)
rows=[]
for p in [.025,.05,.10,.20]:
 for k in [10,20,30]:
  n=math.ceil(k/p);n80=n;n90=n
  while binom.sf(k-1,n80,p)<.8:n80+=1
  while binom.sf(k-1,n90,p)<.9:n90+=1
  rows.append(dict(p=p,target_events=k,N_for_expectation=n,N_for_80pct_probability_iid=n80,N_for_90pct_probability_iid=n90))
save('sample_size_sensitivity.csv',rows)
rows=[]
for n in [10,20,30,80]:
 for frac in [.1,.3,.5]:
  k=round(n*frac);ci=binomtest(k,n).proportion_ci(method='exact')
  rows.append(dict(n=n,events=k,estimate=k/n,lower95=ci.low,upper95=ci.high,scope='iid Clopper-Pearson illustration, not cluster-adjusted trial CI'))
save('interval_width_examples.csv',rows)
# Exact finite-sample optimistic benchmark: independent tail/outside outcomes,
# known tail size80, no exclusions, no cluster correlation, no full bootstrap gate.
rows=[];N=800;m=80
for p in [.025,.05,.1,.2]:
 for lift in [1,2,3,5]:
  pt=p*lift;po=(N*p-m*pt)/(N-m)
  if not(0<=pt<=1 and 0<=po<=1):continue
  a=np.arange(m+1)[:,None];b=np.arange(N-m+1)[None,:];total=a+b
  mass=binom.pmf(a,m,pt)*binom.pmf(b,N-m,po)
  pv=hypergeom.sf(a-1,N,total,m)
  ok=(total>=30)&(a*N>=3*m*total)&(pv<.025)
  rows.append(dict(p=p,assumed_lift=lift,tail_risk=pt,outside_risk=po,prob_benchmark_pass=float(mass[ok].sum()),not_full_design_power=True))
save('optimistic_power_benchmark.csv',rows)
print('Power/sensitivity tables generated; no new states evaluated.')
