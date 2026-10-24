"""Optimización acotada, validación de testigos y estadísticas AH."""
from ah_common import *
from scipy.optimize import minimize
from scipy.stats import spearmanr

class EvaluationBudget(Exception):pass

def search(family,base_theta,base_support,budget,sinks=None):
 F=family;seeds=[np.zeros(2)]+[radius*np.array([np.cos(a),np.sin(a)]) for radius in CFG['q_radii'] for a in np.arange(8)*2*np.pi/8];u_grid=list(np.arange(8)*2*np.pi/8);branches=[]
 for i,(angle,support) in enumerate(F.edges):branches.append({'name':f'edge{i}','kind':'edge','angle':angle,'support':support,'lo':angle,'hi':angle})
 for i,(lo,_) in enumerate(F.edges):
  hi=F.edges[(i+1)%len(F.edges)][0]+(2*np.pi if i==len(F.edges)-1 else 0);branches.append({'name':f'sector{i}','kind':'sector','angle':(lo+hi)/2,'support':None,'lo':lo+1e-4,'hi':hi-1e-4})
 evaluations,candidates,optimizers=sinks if sinks is not None else ([],[],[]);candidates.append({'branch':'baseline','kind':'baseline','q':[0.,0.],'theta':base_theta,'support':base_support.tolist(),'origin':'baseline'})
 def value(q,theta,support,idx):
  budget()
  if len(evaluations)>=CFG['global_evaluations']:raise EvaluationBudget('GLOBAL_EVALUATIONS')
  try:L=F.fast(q,theta,support)
  except Exception as e:
   evaluations.append([idx,float(q[0]),float(q[1]),float(theta),np.nan]);raise
  evaluations.append([idx,float(q[0]),float(q[1]),float(theta),float(L)]);return L/F.rho0
 for idx,branch in enumerate(branches):
  if len(evaluations)>=CFG['global_evaluations']:optimizers.append({'branch':branch['name'],'success':False,'message':'GLOBAL_EVALUATIONS','nfev':0});continue
  try:
   angles=[branch['angle']]
   if branch['kind']=='sector':
    for a in u_grid+[base_theta]:
     while a<branch['lo']:a+=2*np.pi
     if branch['lo']<=a<=branch['hi'] and all(abs(a-x)>1e-10 for x in angles):angles.append(a)
   grid=[]
   for q in seeds:
    for theta in angles:grid.append((value(q,theta,branch['support'],idx),q,theta))
   best=min(grid,key=lambda x:x[0]);q=best[1];theta=best[2];candidates.append({'branch':branch['name'],'kind':branch['kind'],'q':q.tolist(),'theta':theta,'support':None if branch['support'] is None else branch['support'].tolist(),'origin':'grid'})
   if branch['kind']=='edge':
    objective=lambda x:value(x,branch['angle'],branch['support'],idx);x0=q;bounds=[(-12,12)]*2
   else:
    objective=lambda x:value(x[:2],x[2],None,idx);x0=np.r_[q,theta];bounds=[(-12,12)]*2+[(branch['lo'],branch['hi'])]
   opt=minimize(objective,x0,method='L-BFGS-B',bounds=bounds,options={'maxfun':120,'maxiter':40,'ftol':1e-10,'gtol':1e-6});qq=opt.x[:2];tt=branch['angle'] if branch['kind']=='edge' else float(opt.x[2]);candidates.append({'branch':branch['name'],'kind':branch['kind'],'q':qq.tolist(),'theta':tt,'support':None if branch['support'] is None else branch['support'].tolist(),'origin':'optimizer'});optimizers.append({'branch':branch['name'],'success':bool(opt.success),'message':str(opt.message),'nfev':int(opt.nfev),'nit':int(opt.nit),'normalized_fun':float(opt.fun)})
  except EvaluationBudget as e:optimizers.append({'branch':branch['name'],'success':False,'message':str(e),'nfev':0})
 return candidates,optimizers,np.asarray(evaluations)

def validate_candidates(F,candidates,budget,validated=None):
 if validated is None:validated=[]
 for i,candidate in enumerate(candidates):
  row={'candidate':i,**candidate,'quad_status':'UNKNOWN','MP_status':'NOT_SELECTED'}
  try:
   budget();qr=F.validate(candidate['q'],candidate['theta'],candidate['support']);row.update(qr);row['quad_status']='PASS' if qr['quad_error']/qr['length']<=1e-7 else 'INCONCLUSIVE'
  except TimeoutError:raise
  except Exception as e:row['reason']=type(e).__name__+':'+str(e)
  validated.append(row)
 good=[v for v in validated if v['quad_status']=='PASS'];ordered=sorted(good,key=lambda v:v['length']);selected=ordered[:3]
 base=next(v for v in validated if v['branch']=='baseline')
 if base['quad_status']=='PASS' and base not in selected:selected.append(base)
 hp=MPFamily(F)
 for row in selected:
  try:
   budget();row.update(hp.validate(row['q'],row['theta'],row['support'],row,budget))
  except TimeoutError:raise
  except Exception as e:row.update(MP_status='INCONCLUSIVE',reason=type(e).__name__+':'+str(e))
 pool=[v for v in selected if v['MP_status']=='PASS'];winner=min(pool,key=lambda v:v['length']) if pool else None
 return winner,base,validated

def summarize(result):
 valid=[r for r in result if r['status']=='PASS'];groups=[]
 for name in ['triangle','AF']:
  allrows=[r for r in result if r['group']==name];rr=[r for r in valid if r['group']==name];rat=[r['rho1_over_true'] if name=='triangle' else r['rho1_over_rho0'] for r in rr];corr=float(spearmanr([r['rho1'] for r in rr],[r['d_border'] if name=='triangle' else r['rho0'] for r in rr]).statistic) if len(rr)>2 else None;times=[r['time_total']/r['time_rho0'] for r in rr]
  groups.append({'group':name,'states':len(allrows),'valid':len(rr),'unknown':len(allrows)-len(rr),'median_ratio':float(np.median(rat)) if rat else None,'max_ratio':max(rat) if rat else None,'spearman':corr if corr is None or np.isfinite(corr) else None,'median_rho0_seconds':float(np.median([r['time_rho0'] for r in rr])) if rr else None,'median_total_seconds':float(np.median([r['time_total'] for r in rr])) if rr else None,'median_cost_ratio':float(np.median(times)) if rr else None})
 tri=[r for r in valid if r['group']=='triangle'];qq1='FAIL' if any(r['rho1']<r['d_border']*(1-1e-7) for r in tri) else ('PASS' if len(tri)==40 else 'INCONCLUSIVE');g=groups[0]
 q2='FAIL' if g['max_ratio'] is not None and g['max_ratio']>1.5+1e-7 else ('PASS' if len(tri)==40 and g['median_ratio']<=1.2-1e-7 else ('FAIL' if len(tri)==40 and g['median_ratio']>1.2+1e-7 else 'INCONCLUSIVE'))
 q3='PASS' if len(tri)==40 and g['spearman']>=.95 else ('FAIL' if len(tri)==40 else 'INCONCLUSIVE')
 q4='FAIL_DESCRIPTIVE' if any(g['median_cost_ratio'] is not None and g['median_cost_ratio']>10 for g in groups) else ('PASS_DESCRIPTIVE' if len(valid)==80 else 'INCONCLUSIVE')
 afr=[r for r in valid if r['group']=='AF'];q5='FAIL_DESCRIPTIVE' if any(r['rho1_over_rho0']>1+1e-7 for r in afr) else ('PASS_DESCRIPTIVE' if len(afr)==40 else 'INCONCLUSIVE')
 inversions=0
 for i,a in enumerate(afr):
  for b in afr[i+1:]:inversions+=int((a['rho0']-b['rho0'])*(a['rho1']-b['rho1'])<0)
 return groups,{'status':'VALID_EXPLORATORY','states':80,'valid':len(valid),'Q1':qq1,'Q2':q2,'Q3':q3,'Q4':q4,'Q5':q5,'AF_inversions':inversions,'AF_pairs':len(afr)*(len(afr)-1)//2,'AF_true_distance':'UNKNOWN'}
