from pathlib import Path
import json,csv,collections
import numpy as np
from scipy.stats import rankdata
from sklearn.isotonic import IsotonicRegression
P=Path(__file__).resolve().parent;PROTO=json.loads((P/'protocol_T1_B_frozen.json').read_text())
raw=[json.loads(f.read_text()) for f in sorted((P/'states').glob('*/result.json'))];rows=[r for s in raw for r in s['results']];assert len(raw)==80

def write(name,rr):
 fields=list(dict.fromkeys(k for r in rr for k in r))
 with (P/name).open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
def rho(x,y):
 x=np.asarray(x,float);y=np.asarray(y,float);ok=np.isfinite(x)&np.isfinite(y);x=x[ok];y=y[ok]
 return float(np.corrcoef(rankdata(x),rankdata(y))[0,1]) if len(x)>=3 and np.ptp(x)>0 and np.ptp(y)>0 else None
def safequantile(x):
 x=np.array([v for v in x if v is not None and np.isfinite(v)]);return [float(np.quantile(x,.025)),float(np.quantile(x,.975))] if len(x) else [None,None]
def partial(x,y,z):
 rx=rankdata(x);ry=rankdata(y);rz=rankdata(z);D=np.c_[np.ones(len(rz)),rz];a=rx-D@np.linalg.lstsq(D,rx,rcond=None)[0];b=ry-D@np.linalg.lstsq(D,ry,rcond=None)[0];return float(np.corrcoef(a,b)[0,1]) if np.ptp(a)>0 and np.ptp(b)>0 else None
cor=[];stability=[];res=[];area=[];features=[];models=[];positive=[];candidate=[]
for i in range(4):
 for g in ['true','random']:
  allg=[r for r in rows if r['regime']==g and r['radius_index']==i and r['status']=='PASS'];ordered=sorted(allg,key=lambda r:-r['kappa_max'])
  for rank,r in enumerate(ordered,1):
   if r['T1A_classification']=='GEOMETRIC_NONINJECTIVITY':positive.append(dict(state=r['state'],radius_index=i,radius=r['radius'],primary=i==2,kappa_max=r['kappa_max'],minimum_abs_det=r['minimum_abs_det'],rank_within_true=rank,n_true=len(ordered),top10pct=rank<=4,CA=None,angle_max_kappa=r['angle_max_kappa'],r_conj=r['r_conj'],r_over_r_conj=r['radius']/r['r_conj']))
write('positive_cases.csv',positive)
draws=np.random.default_rng(151510).integers(0,8,size=(5000,8))
for g in ['true','random']:
 states=sorted({r['state'] for r in rows if r['regime']==g and r['C_A']is not None and r['status']=='PASS'})
 by={r['state']:{i:next(z for z in rows if z['state']==r['state'] and z['radius_index']==i) for i in range(4)} for r in rows if r['state']in states}
 states=[s for s in states if all(by[s][i]['status']=='PASS' for i in range(4))];rr=[by[s][2] for s in states]
 X=np.array([[r['C_A'],r['kappa_nominal_disk'],r['kappa_nominal_endpoint']]+[by[r['state']][i]['kappa_max'] for i in range(4)]+[by[r['state']][i]['kappa_prefix_max'] for i in range(4)] for r in rr]);splits=np.array([r['split'] for r in rr]);n=len(rr)
 boot=[]
 for draw in draws:
  ix=np.concatenate([np.flatnonzero(splits==s) for s in draw]);z=rankdata(X[ix],axis=0);c=np.corrcoef(z,rowvar=False)[0,1:];boot.append(c)
 boot=np.array(boot);nomdisk=rho(X[:,0],X[:,1]);nomend=rho(X[:,0],X[:,2])
 for i in range(4):
  y=X[:,3+i];yp=X[:,7+i];observed=rho(X[:,0],y);obs_prefix=rho(X[:,0],yp);ci=safequantile(boot[:,2+i]);delta=boot[:,2+i]-boot[:,0];delta_end=boot[:,2+i]-boot[:,1]
  cor.append(dict(regime=g,radius_index=i,radius=PROTO['radii'][i],primary=i==2,n=n,rho_nominal_disk=nomdisk,rho_nominal_endpoint=nomend,rho_common_endpoint=observed,rho_common_prefix=obs_prefix,delta_vs_nominal_disk=observed-nomdisk,delta_vs_nominal_endpoint=observed-nomend,rho_boot_low=ci[0],rho_boot_high=ci[1],delta_vs_disk_boot_low=safequantile(delta)[0],delta_vs_disk_boot_high=safequantile(delta)[1],delta_vs_endpoint_boot_low=safequantile(delta_end)[0],delta_vs_endpoint_boot_high=safequantile(delta_end)[1],bootstrap_reps=5000,bootstrap_seed=151510,interval_type='descriptive cluster resampling sensitivity; overlapping splits, not confirmatory'))
  for s in range(8):
   sel=splits==s;other=~sel
   stability.append(dict(regime=g,radius_index=i,type='within_split',excluded_or_split=str(s),n=int(sel.sum()),rho=rho(X[sel,0],y[sel])))
   stability.append(dict(regime=g,radius_index=i,type='leave_one_split_out',excluded_or_split=str(s),n=int(other.sum()),rho=rho(X[other,0],y[other])))
  for j,state in enumerate(states):
   keep=np.arange(n)!=j;stability.append(dict(regime=g,radius_index=i,type='leave_one_state_out',excluded_or_split=state,n=n-1,rho=rho(X[keep,0],y[keep]),is_max_CA=j==int(np.argmax(X[:,0])),is_max_kappa=j==int(np.argmax(y))))
  xx=np.log10(X[:,0]);yy=np.log10(np.maximum(y-1,1e-12));pred=np.full(n,np.nan);ext=np.zeros(n,bool)
  for s in range(8):
   tr=splits!=s;te=~tr;model=IsotonicRegression(increasing=True,out_of_bounds='clip').fit(xx[tr],yy[tr]);pred[te]=model.predict(xx[te]);ext[te]=(xx[te]<xx[tr].min())|(xx[te]>xx[tr].max())
  residual=yy-pred;med=float(np.median(residual));mad=float(np.median(abs(residual-med)));z=(residual-med)/max(1.4826*mad,1e-12)
  full=IsotonicRegression(increasing=True,out_of_bounds='clip').fit(xx,yy);models.append(dict(regime=g,radius_index=i,x_definition='log10(C_A)',y_definition='log10(max(kappa-1,1e-12))',x_thresholds=full.X_thresholds_.tolist(),y_thresholds=full.y_thresholds_.tolist(),fit_scope='T1B exploratory calibration, not external validation'))
  for j,r in enumerate(rr):
   obs=by[r['state']][i];out={k:obs[k] for k in ['state','split','init','regime','radius_index','radius','C_A','kappa_max','lambda_1pct','lambda_01pct','R_eff','frac50','frac90','nominal_radius','angular_K_abs_cv','angular_K_peak_to_rms','angular_K_top10_energy','K_rms','r_conj','r_inj_upper','A_embed','A_embed_censored']};out.update(log_deformation=float(yy[j]),crossfit_prediction=float(pred[j]),residual_log10=float(residual[j]),deformation_observed_over_predicted=float(10**residual[j]),large_residual=bool(abs(residual[j])>np.log10(2)),robust_z=float(z[j]),extrapolation_clipped=bool(ext[j]));res.append(out)
  for feat in ['lambda_1pct','lambda_01pct','R_eff','frac50','frac90','nominal_radius','angular_K_abs_cv','angular_K_peak_to_rms','angular_K_top10_energy','K_rms']:
   ff=np.array([by[s][i][feat] for s in states],float);features.append(dict(regime=g,radius_index=i,feature=feat,n=n,rho_signed_residual=rho(ff,residual),rho_abs_residual=rho(ff,abs(residual)),note='Exploratory; feature screening in discovery panel, not confirmation'))
   for s in range(8):
    keep=splits!=s;stability.append(dict(regime=g,radius_index=i,type='residual_feature_leave_split_out',excluded_or_split=str(s),feature=feat,n=int(keep.sum()),rho=rho(ff[keep],residual[keep])))
  R=np.array([r['nominal_radius'] for r in rr]);yratio=np.log10(np.maximum(X[:,2]-1,1e-12))-yy
  area.append(dict(regime=g,radius_index=i,n=n,rho_CA_Rnom=rho(X[:,0],R),rho_Rnom_kappa_nominal=rho(R,X[:,2]),rho_Rnom_kappa_common=rho(R,y),rho_Rnom_log_deformation_gain=rho(R,yratio),median_nominal_to_common_deformation_ratio=float(np.median(10**yratio)),partial_rank_CA_nominal_given_Rnom=partial(X[:,0],X[:,2],R),partial_rank_CA_common_given_Rnom=partial(X[:,0],y,R),large_drop_abs_delta_gt_01=abs(observed-nomdisk)>.1,note='No causal mediation identification; CA remains on its own fixed-area nominal domain'))
  for name,xxalt in [('CA',X[:,0]),('CA_A_over_4pi',X[:,0]*.02/(4*np.pi)),('CA_Rnom_squared',X[:,0]*R*R),('CA_rcommon_squared',X[:,0]*PROTO['radii'][i]**2)]:
   lx=np.log10(xxalt);predalt=np.full(n,np.nan)
   for s in range(8):
    tr=splits!=s;te=~tr;m=IsotonicRegression(increasing=True,out_of_bounds='clip').fit(lx[tr],yy[tr]);predalt[te]=m.predict(lx[te])
   candidate.append(dict(regime=g,radius_index=i,observable=name,rho=rho(xxalt,y),crossfit_MAE_log10=float(np.mean(abs(yy-predalt))),crossfit_median_abs_error=float(np.median(abs(yy-predalt))),note='Descriptive candidate only; fixed common scale multiples preserve Spearman ranks'))
write('correlations.csv',cor);write('stability.csv',stability);write('residuals.csv',res);write('residual_feature_correlations.csv',features);write('area_effect.csv',area);write('dimensionless_candidates.csv',candidate);(P/'isotonic_models.json').write_text(json.dumps(models,indent=2))
primary=[r for r in res if r['radius_index']==2];write('large_residuals.csv',[r for r in primary if r['large_residual']])
summary=dict(states=80,state_radius_rows=len(rows),numerical_PASS=sum(r['status']=='PASS' for r in rows),numerical_INCONCLUSIVE=sum(r['status']!='PASS' for r in rows),primary_radius=PROTO['primary_radius'],correlations=cor,positive_cases=positive,primary_large_residual_counts={g:sum(r['large_residual'] for r in primary if r['regime']==g) for g in ['true','random']},primary_residual_features=[r for r in features if r['radius_index']==2],area_effect=[r for r in area if r['radius_index']==2],dimensionless_primary=[r for r in candidate if r['radius_index']==2],cpu_seconds=sum(s['cpu_seconds'] for s in raw),sum_state_wall_seconds=sum(s['wall_seconds'] for s in raw),limitations=['No causal inference or within-panel confirmation','Bootstrap intervals descriptive only: overlapping splits','Common outcome radius does not make the CA measurement domain common','Missing CA for positives: tail ranks defined, CA residuals undefined','Angular K features measured on boundary in launch-angle measure, not spatial-area concentration'])
(P/'analysis_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'primary':[r for r in cor if r['primary']],'positive_primary':[r for r in positive if r['primary']],'large_residuals':summary['primary_large_residual_counts']},indent=2))
