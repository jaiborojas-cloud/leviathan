"""Frozen prospective analysis. This module does not train or inspect new states.
Input: one eligible trajectory per row, columns split,trajectory,X,Y;
external integrity/eligibility gate must already be checked against protocol.json.
"""
import numpy as np

def tail(x,q=.1):
 x=np.asarray(x,float)
 if len(x)==0 or not np.isfinite(x).all():raise ValueError('Invalid scores')
 cutoff=np.sort(x)[-int(np.ceil(q*len(x)))];return x>=cutoff

def metrics(x,y):
 y=np.asarray(y,int);t=tail(x);p=float(y.mean());precision=float(y[t].mean())
 return dict(N=len(y),events=int(y.sum()),tail_n=int(t.sum()),precision=precision,base=p,delta=precision-p,lift=precision/p if p else None,recall=float(y[t].sum()/y.sum()) if y.sum() else None)

def average_precision(x,y):
 x=np.asarray(x);y=np.asarray(y);tot=y.sum()
 if tot==0:return None
 ans=0.;prev=0
 for threshold in sorted(set(x),reverse=True):
  inc=x>=threshold;tp=y[inc].sum();ans+=(tp-prev)/tot*(tp/inc.sum());prev=tp
 return float(ans)

def evaluate(split,x,y,technical_gate=True,reps=20000,seed=220020):
 split=np.asarray(split);x=np.asarray(x,float);y=np.asarray(y,int)
 if len(split)!=len(x) or len(x)!=len(y) or not np.isin(y,[0,1]).all():raise ValueError('Invalid rows')
 point=metrics(x,y);groups=np.unique(split);positive_groups=len(np.unique(split[y==1]));point['positive_splits']=positive_groups;point['average_precision']=average_precision(x,y)
 if not technical_gate or len(y)<640 or len(groups)<128 or point['events']<30 or positive_groups<10 or point['tail_n']>.15*len(y):
  return dict(decision='INCONCLUSIVE',reason='technical, coverage, events, splits or ties gate',point=point)
 rng=np.random.default_rng(seed);blocks=[np.flatnonzero(split==s) for s in groups];stats=[]
 for _ in range(reps):
  ix=np.concatenate([blocks[i] for i in rng.integers(0,len(blocks),len(blocks))]);m=metrics(x[ix],y[ix]);stats.append([m['precision'],m['base'],m['delta']])
 stats=np.asarray(stats);ci=np.quantile(stats,[.025,.975],axis=0,method='linear')
 loo=[metrics(x[split!=s],y[split!=s])['delta'] for s in groups]
 if not np.isfinite(ci).all() or ci[0,2]==ci[1,2]:return dict(decision='INCONCLUSIVE',reason='nonfinite or degenerate cluster CI',point=point)
 ok=point['lift']>=3 and ci[0,2]>0 and min(loo)>0
 return dict(decision='PASS_PROSPECTIVE_PILOT' if ok else 'FAIL',point=point,CI95_precision=ci[:,0].tolist(),CI95_base=ci[:,1].tolist(),CI95_delta=ci[:,2].tolist(),min_leave_split_out_delta=min(loo),bootstrap_reps=reps,bootstrap_seed=seed)
