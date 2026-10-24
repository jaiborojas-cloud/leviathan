#!/usr/bin/env python3
"""Desenlaces AF, exclusivamente después del commit de predictores."""
from outcome_numerics_v1 import *
import argparse,resource,platform,importlib.util
from scipy.integrate import solve_ivp
from scipy.stats import kendalltau
from concurrent.futures import ProcessPoolExecutor

def load_e16(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def controls(gm,audit):
 result=[]
 def check(name,ok,error=0.,details=''):result.append({'control':name,'status':'PASS' if ok else 'FAIL','error':float(error),'details':details})
 for name,K,L in [('sphere',1.,1.5*np.pi),('hyperbolic',-1.,4.),('plane',0.,1.)]:
  def event(t,z):return z[0]
  sol=solve_ivp(lambda t,z:[z[1],-K*z[0]],(0,L),[0.,1.],events=event,dense_output=True,method='DOP853',rtol=1e-12,atol=1e-14,max_step=.05);roots=[v for v in sol.t_events[0] if v>1e-9];expected=np.sin(L) if K==1 else (np.sinh(L) if K==-1 else L);err=abs(sol.y[0,-1]-expected)/max(1,abs(expected));check(name+'/Jacobi',err<1e-8 and len(roots)==(1 if K==1 else 0) and (K!=1 or abs(roots[0]-np.pi)<1e-8),err)
 delta=.001;f=np.array([[delta,delta],[delta,-delta],[-delta,delta],[-delta,-delta]]);M=np.eye(4);g=audit.AuditedGeometry(M,f);tr=integrate(g,np.array([0.]),CFG['R_max']);known=1/(1+np.exp(-.3))-.5;err=abs(tr.last-known);check('synthetic4/known_escape',tr.status=='ESCAPE' and err<1e-7,err,f'expected={known};norm=linf;face=+P1')
 if tr.sol is not None:
  good,details=mp_check(g,[('known_escape',tr.at(tr.last)[:2,0])]);check('synthetic4/escape_MP',good,max(q['K_error'] for q in details))
 else:check('synthetic4/escape_MP',False,1.)
 class Constant:
  M=np.eye(2)
  def jac(self,p):return np.tile(np.eye(2),(len(p),1,1))
 for n in CFG['rays']:
  ts=np.arange(n)*2*np.pi/n;r=np.linspace(0,.1,33);rings=r[:,None,None]*np.column_stack([np.cos(ts),np.sin(ts)])[None,:,:];value=gm.area7(Constant(),gm.triangles(rings));err=abs(value-np.pi*.1**2)/(np.pi*.1**2);check(f'area7/flat/n{n}',err<1e-4,err)
 # Control real AD (sólo fuentes sintéticas E16).
 d=load_e16('af_d_control',ROOT.parent/'D/scripts/run.py');ac=load_e16('af_ac_control',ROOT.parent/'AC/scripts/run_v2.py');data=json.loads((ROOT.parent/'H/data.json').read_text())
 with mp.workdps(80):
  th=[mp.mpf(str(x)) for x in data['states']['h00']];inp=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels']['P0']];cv,jc,_,ch=d.analytic_mp(th,inp);ux=d.analytic_B(cv,jc,[1,0],'quadratic')[0]*ch;uy=d.analytic_B(cv,jc,[0,1],'quadratic')[0]*ch
 flat=ac.Metric('quadratic',np.array(ux.tolist(),float),np.array(uy.tolist(),float));A=np.array(data['perspectives'][0],float);sh=next(q for q in rows(ROOT.parent/'AC/results/run_v2/shooting.csv') if q['path']=='Q0/reference/132' and float(q['rtol'])==1e-12);unit=np.array([np.cos(float(sh['angle'])),np.sin(float(sh['angle']))]);v=float(sh['L'])*unit/np.sqrt(unit@flat.geometry(A)[0]@unit);flat_sol,_=ac.integrate(flat,A,v,1e-12);err=max(abs(float(flat.geometry(flat_sol.sol(t)[:2])[2])) for t in np.linspace(0,1,9));check('AD_flat/K',err<1e-7,err)
 for m in CFG['index_meshes']:
  for kind,L,expected in [('sphere',.75*np.pi,0),('sphere',1.5*np.pi,1),('hyperbolic',1.,0),('AD_flat',float(sh['L']),0)]:
   if kind=='sphere':p=np.column_stack([np.zeros(m+1),np.linspace(0,L,m+1)]);N=np.column_stack([np.ones(m+1),np.zeros(m+1)]);coeff=None
   elif kind=='hyperbolic':p=np.column_stack([np.linspace(0,L,m+1),np.zeros(m+1)]);N=np.column_stack([np.zeros(m+1),np.exp(-p[:,0])]);coeff=None
   else:
    z=flat_sol.sol(np.linspace(0,1,m+1));p=z[:2].T;hs=np.array([flat.geometry(x)[0] for x in p]);hv=np.einsum('bij,bj->bi',hs,z[2:4].T);N=np.column_stack([-hv[:,1],hv[:,0]]);N/=np.sqrt(np.einsum('bi,bij,bj->b',N,hs,N))[:,None];coeff=(flat.A,flat.B,flat.C)
   H,grad0=normal_block(p,N,None,None,8,kind,coeff);H2,_=normal_block(p,N,None,None,16,kind,coeff);ev=np.linalg.eigvalsh(H);tau=max(CFG['index_abs_tol'],CFG['index_rel_tol']*max(abs(ev)));count=int(sum(ev< -tau));err=np.max(abs(H-H2))/max(1,np.max(abs(H2)));check(f'{kind}/{L}/normal/{m}',count==expected and err<1e-5,err,f'negative={count},expected={expected}')
 return result

TABLE_NAMES=['outcomes','ray_events','boundary','profiles','mp_events','arrays','morse','normal_bands','normal_spectra','normal_vectors','normal_nodes','selected_ray']

def analyse_state(task):
 st,array_root,deadline=task;gm,audit=imports();M=np.array(st['M']);f=np.array(st['f']);start=time.monotonic();tables={k:[] for k in TABLE_NAMES};sid=st['id'];logical=sid.replace('/','_');g=audit.AuditedGeometry(M,f)
 def budget():
  if time.monotonic()>deadline or time.monotonic()-start>CFG['per_state_seconds']:raise TimeoutError('FIXED_BUDGET')
 def archive(trace,label):
  if trace.sol is None:return
  grid=np.linspace(0,trace.last,CFG['radial_scan']);values=trace.at(grid);dest=Path(array_root)/(logical+'_'+label+'.npy')
  if dest.exists():raise FileExistsError(dest)
  np.save(dest,values,allow_pickle=False);tables['arrays'].append({'state':sid,'label':label,'logical_file':dest.name,'shape':str(values.shape),'sha256':sha(dest),'r_start':0.,'r_end':trace.last})
  roots=first_roots(trace);selected={0,trace.n//4,trace.n//2,3*trace.n//4}
  if np.isfinite(roots).any():selected.add(int(np.nanargmin(roots)))
  end=trace.at(trace.last);esc=np.where(np.max(abs(end[:2]),axis=0)>=CFG['escape_threshold']-1e-5)[0] if trace.status=='ESCAPE' else []
  selected.update(int(i) for i in esc)
  for i in sorted(selected):
   for j,r in enumerate(grid):z=values[:,i,j];tables['profiles'].append({'state':sid,'label':label,'ray':i,'r':float(r),'p1':float(z[0]),'p2':float(z[1]),'v1':float(z[2]),'v2':float(z[3]),'j':float(z[4]),'jprime':float(z[5])})
  for i,z in enumerate(end.T):tables['boundary'].append({'state':sid,'label':label,'ray':i,'r':trace.last,'p1':float(z[0]),'p2':float(z[1]),'v1':float(z[2]),'v2':float(z[3]),'j':float(z[4])})
 for n in CFG['rays']:
  row={'state':sid,'seed':st['seed'],'target':st['target'],'scale':st['scale'],'n':n,'status':'INCONCLUSIVE_NUMERICAL','r_conj':None,'r_col_lower':None,'r_col':None,'r_esc':None,'r_deg':None,'type':'UNKNOWN','censored':False,'coverage':0.,'A_emb':None,'A_at_limit':None,'A32':None,'A64':None,'area_error':None,'MP_status':'UNKNOWN','escape_face':'','escape_p1':None,'escape_p2':None,'escape_euclidean_norm':None,'escape_a_min':None,'escape_a_max':None,'escape_Neff':None,'outward':None,'boundary_trend':'UNKNOWN','min_metric_eigenvalue':None,'max_metric_condition':None,'reason':''}
  try:
   budget();trace=integrate(g,np.arange(n)*2*np.pi/n,CFG['R_max'],budget);row['coverage']=trace.last;row['status']=trace.status;row['reason']=trace.reason;archive(trace,'n'+str(n));roots=first_roots(trace)
   for i,c in enumerate(roots):tables['ray_events'].append({'state':sid,'n':n,'ray':i,'angle':2*np.pi*i/n,'first_conjugate':float(c) if np.isfinite(c) else None,'root_censor_at':trace.last,'root_status':'OBSERVED' if np.isfinite(c) else 'CENSORED_AT_STOP','stop':trace.status})
   if trace.status=='INCONCLUSIVE_NUMERICAL' or trace.sol is None:raise FloatingPointError(trace.reason or 'NO_ACCEPTED_STEP')
   points=[('origin',np.zeros(2))];conj=float(np.nanmin(roots)) if np.isfinite(roots).any() else None;row['r_conj']=conj
   if conj is not None:i=int(np.nanargmin(roots));points.append(('first_conjugate',trace.at(conj)[:2,i]))
   col=first_collision(trace)
   if col:
    row.update(r_col_lower=col[0],r_col=col[1]);top=audit.topology(trace.at(col[1])[:2].T,0)
    for q in top['intersections']:points.append(('first_collision',np.array(q['point'],float)))
   if trace.status=='ESCAPE':
    row['r_esc']=trace.last;end=trace.at(trace.last);i=int(np.argmax(np.max(abs(end[:2]),axis=0)));p=end[:2,i];v=end[2:4,i];axis=int(np.argmax(abs(p)));row.update(escape_face=('+' if p[axis]>0 else '-')+'P'+str(axis+1),escape_p1=float(p[0]),escape_p2=float(p[1]),escape_euclidean_norm=float(np.linalg.norm(p)),outward=bool(p@v>0));points.append(('first_escape',p));z=f@p;weights=np.exp(z-max(z));weights/=sum(weights);sample_p=trace.at(np.linspace(.9*trace.last,trace.last,8))[:2,i,:].T;mins=[]
    for q in sample_p:z=f@q;aa=np.exp(z-max(z));aa/=sum(aa);mins.append(min(aa))
    row.update(escape_a_min=float(min(weights)),escape_a_max=float(max(weights)),escape_Neff=float(1/sum(weights*weights)),boundary_trend='DECREASING_MIN_WEIGHT_OBSERVED' if np.all(np.diff(mins)<=1e-12) and p@v>0 else 'UNKNOWN')
   candidates=[(row[key],label) for key,label in [('r_conj','CONJUGATE'),('r_col','COLLISION'),('r_esc','ESCAPE')] if row[key] is not None];event=min([v for v,label in candidates],default=None);row['censored']=event is None;row['r_deg']=event;row['type']='CENSORED_RMAX' if event is None else '+'.join(sorted(label for r,label in candidates if abs(r-event)<=CFG['radius_agreement']*max(event,1e-12)))
   limit=CFG['R_max'] if event is None else event*(1-1e-6)
   if not candidates:points.append(('censored_limit',trace.at(trace.last)[:2,0]))
   good,details=mp_check(g,points)
   for q in details:tables['mp_events'].append({'state':sid,'n':n,**q})
   row['MP_status']='PASS' if good else 'INCONCLUSIVE'
   try:
    areas=[]
    for nr in CFG['area_rings']:
     budget();rings=trace.at(np.linspace(0,limit,nr+1))[:2].transpose(2,1,0);area=float(gm.area7(g,gm.triangles(rings)))
     if not np.isfinite(area) or area<=0:raise ValueError('NONFINITE_AREA')
     areas.append(area)
    row.update(A32=areas[0],A64=areas[1],A_at_limit=areas[-1],A_emb=None if row['censored'] else areas[-1],area_error=abs(areas[1]-areas[0])/max(abs(areas[1]),1e-30))
   except Exception as e:row['reason']+=';AREA:'+str(e)
  except Exception as e:row['reason']+=';'+type(e).__name__+':'+str(e)
  row['min_metric_eigenvalue']=float(g.audit['min_eigenvalue']) if np.isfinite(g.audit['min_eigenvalue']) else None;row['max_metric_condition']=float(g.audit['max_condition']);tables['outcomes'].append(row)
 # Ángulo0 fijado: extensión individual, no elegir el rayo del mínimo observado.
 try:
  budget();selected=integrate(g,np.array([CFG['index_angle']]),CFG['R_max'],budget);archive(selected,'selected_angle0');rr=first_roots(selected);conj=float(rr[0]) if len(rr) and np.isfinite(rr[0]) else None;tables['selected_ray'].append({'state':sid,'angle':0.,'conjugate':conj,'coverage':selected.last,'status':selected.status,'reason':selected.reason})
  if conj is None or selected.status=='INCONCLUSIVE_NUMERICAL':raise ValueError('NO_VALID_CONJUGATE_ON_FIXED_RAY')
  # Contraste de radio propio con jacsolve archivado, sin eventos, sólo si segmento cabe.
  if conj*1.25>selected.last:raise ValueError('POSTCONJUGATE_TARGET_CENSORED')
  reference=audit.jacsolve(g,np.array([0.]),conj*1.25);xx=np.linspace(0,conj*1.25,513);jj=reference.sol(xx).reshape(6,1,-1)[4,0];ids=np.where((jj[1:-1]>0)&(jj[2:]<=0))[0];rc=brentq(lambda r:reference.sol(r).reshape(6,1)[4,0],xx[ids[0]+1],xx[ids[0]+2]) if len(ids) else None;radius_ok=rc is not None and abs(rc-conj)/conj<.02
  for factor in CFG['index_factors']:
   length=conj*factor
   for m in CFG['index_meshes']:
    case=f'{sid}/{factor}/{m}';row={'state':sid,'factor':factor,'mesh':m,'L':length,'selected_conjugate':conj,'index':None,'minimum':None,'threshold':None,'gradient':None,'quadrature_error':None,'MP_minimum':None,'MP_error':None,'radius_contrast':radius_ok,'status':'INCONCLUSIVE','reason':''}
    try:
     budget();z=selected.at(np.linspace(0,length,m+1))[:,0,:];points=z[:2].T;N=normal_frame(g,points,z[2:4].T);H,gg=normal_block(points,N,M,f,8,budget=budget);H2,_=normal_block(points,N,M,f,16,budget=budget);ev,vec=eigh(H);tau=max(CFG['index_abs_tol'],CFG['index_rel_tol']*max(abs(ev)));count=int(sum(ev< -tau));gradient=float(max(abs(gg)))/max(1,length);qe=float(np.max(abs(H-H2))/max(1,np.max(abs(H2))));ok=gradient<=CFG['index_gradient_tol'] and qe<=1e-5 and radius_ok;mpvalue=None;error=None
     if m==max(CFG['index_meshes']):
      cur1=mp_rayleigh(M,f,points,N,vec[:,0],16,budget);cur2=mp_rayleigh(M,f,points,N,vec[:,0],32,budget)
      with mp.workdps(80):error=float(max(abs(cur1-cur2),abs(cur2-mp.mpf(float(ev[0]))))/max(1,abs(cur2)));mpvalue=mp.nstr(cur2,70)
      ok=ok and error<=1e-4
     row.update(index=count,minimum=float(ev[0]),threshold=tau,gradient=gradient,quadrature_error=qe,MP_minimum=mpvalue,MP_error=error,status='PASS_NUMERICAL' if ok else 'INCONCLUSIVE',reason='' if ok else 'GRADIENT_QUADRATURE_RADIUS_OR_MP')
     for i in range(m-1):
      for j in range(max(0,i-1),min(m-1,i+2)):tables['normal_bands'].append({'case':case,'row':i,'column':j,'dimension':m-1,'value':float(H[i,j])})
     for i,value in enumerate(ev):tables['normal_spectra'].append({'case':case,'mode':i,'eigenvalue':float(value),'threshold':tau,'negative':bool(value< -tau)})
     for i in np.flatnonzero(ev< -tau):
      for j in range(m-1):tables['normal_vectors'].append({'case':case,'mode':int(i),'node':j+1,'coefficient':float(vec[j,i]),'eigenvalue':float(ev[i])})
     for j,p in enumerate(points):tables['normal_nodes'].append({'case':case,'node':j,'p1':float(p[0]),'p2':float(p[1]),'normal1':float(N[j,0]),'normal2':float(N[j,1])})
    except Exception as e:row['reason']=type(e).__name__+':'+str(e)
    tables['morse'].append(row)
 except Exception as e:
  for factor in CFG['index_factors']:
   for m in CFG['index_meshes']:tables['morse'].append({'state':sid,'factor':factor,'mesh':m,'L':None,'selected_conjugate':None,'index':None,'minimum':None,'threshold':None,'gradient':None,'quadrature_error':None,'MP_minimum':None,'MP_error':None,'radius_contrast':False,'status':'INCONCLUSIVE','reason':type(e).__name__+':'+str(e)})
 return tables,{'state':sid,'seconds':time.monotonic()-start,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'blocked_prohibited_reads':ACCESS['blocked']}

def assessments(predictions,tables):
 perstate=[]
 for pred in predictions:
  sid=pred['state'];rs=[r for r in tables['outcomes'] if r['state']==sid];valid=len(rs)==2 and all(r['status']!='INCONCLUSIVE_NUMERICAL' and r['MP_status']=='PASS' for r in rs);radius_error=None;area_error=None;q1='INCONCLUSIVE'
  if valid:
   match=rs[0]['censored']==rs[1]['censored'];r0=CFG['R_max'] if rs[0]['censored'] else rs[0]['r_deg'];r1=CFG['R_max'] if rs[1]['censored'] else rs[1]['r_deg'];radius_error=abs(r0-r1)/max(abs(r1),1e-30);aa=[r[key] for r in rs for key in ['A32','A64']];hasarea=all(v is not None for v in aa)
   if hasarea:area_error=(max(aa)-min(aa))/max(abs(max(aa)),1e-30)
   if match and radius_error<=CFG['radius_agreement'] and hasarea and area_error<=CFG['area_agreement'] and (rs[0]['censored'] or set(rs[0]['type'].split('+'))&set(rs[1]['type'].split('+'))):q1='PASS'
   elif radius_error>.1 or hasarea and area_error>.1:q1='FAIL'
  mr=[r for r in tables['morse'] if r['state']==sid];q2='INCONCLUSIVE'
  if len(mr)==6 and all(r['status']=='PASS_NUMERICAL' for r in mr):
   expected=all(r['index']==(0 if r['factor']<1 else 1) for r in mr);stable=all(len({r['index'] for r in mr if r['factor']==factor})==1 for factor in CFG['index_factors']);q2='PASS' if expected else ('FAIL' if stable else 'INCONCLUSIVE')
  aa=[r[key] for r in rs for key in ['A32','A64'] if r[key] is not None];area_answer='?';lo=hi=None
  if len(aa)==4:
   delta=max(aa)-min(aa);lo=max(0,min(aa)-delta);hi=max(aa)+delta
   if lo>CFG['area_target']:area_answer='CONSTRUCTIBLE_TO_OBSERVED_RADIUS'
   elif hi<CFG['area_target'] and all(not r['censored'] and r['r_deg'] is not None for r in rs):area_answer='NOT_CONSTRUCTIBLE_BEFORE_EVENT'
  radius_answer='OBSERVED_OR_RMAX_CENSORED' if valid else '?';perstate.append({'state':sid,'seed':int(pred['seed']),'target':float(pred['target']),'Q1':q1,'radius_error':radius_error,'area_error':area_error,'Q2':q2,'Q2_eligible':bool(len(mr)==6 and all(r['selected_conjugate'] is not None for r in mr)),'area_answer':area_answer,'area_lower':lo,'area_upper':hi,'radius_answer':radius_answer})
 correlations=[]
 for n in CFG['rays']:
  rr=[r for r in tables['outcomes'] if r['n']==n];ranks=[];missing=False
  for pred in predictions:
   r=next((x for x in rr if x['state']==pred['state']),None)
   if r is None or r['status']=='INCONCLUSIVE_NUMERICAL' or r['MP_status']!='PASS':missing=True;ranks.append(None)
   else:ranks.append(CFG['R_max']+1 if r['censored'] else r['r_deg'])
  for field in ['abs_K0','max_abs_K_small','X_max']:
   xs=[float(p[field]) if p[field] not in [None,''] else None for p in predictions];tau=None
   if not missing and all(v is not None for v in xs):value=kendalltau(xs,ranks).statistic;tau=float(value) if np.isfinite(value) else None
   correlations.append({'n':n,'predictor':field,'tau_b':tau,'states':40,'unknown':sum(v is None for v in ranks),'censor_policy':'greater_than_Rmax; censored ties; no independent-state p-value'})
 q3='INCONCLUSIVE'
 if all(r['tau_b'] is not None for r in correlations):
  stable=all(abs(next(r['tau_b'] for r in correlations if r['n']==512 and r['predictor']==p)-next(r['tau_b'] for r in correlations if r['n']==1024 and r['predictor']==p))<=CFG['kendall_resolution_tol'] for p in ['abs_K0','max_abs_K_small','X_max']);q3='PASS' if stable and all(r['tau_b']<=-CFG['kendall_threshold'] for r in correlations) else ('FAIL' if stable and all(r['tau_b']>=CFG['kendall_threshold'] for r in correlations) else 'INCONCLUSIVE')
 unknown_area=sum(r['area_answer']=='?' for r in perstate);unknown_radius=sum(r['radius_answer']=='?' for r in perstate);q4='PASS' if unknown_radius<unknown_area else 'FAIL';return perstate,correlations,q3,q4

def main(out,arrays,workers):
 if out.exists() or arrays.exists():raise FileExistsError('preservar versiones; no sobrescribir')
 stage1=ROOT/'results/stage1_v1';frozen=json.loads((stage1/'predictors_sha256.json').read_text())
 for p,h in frozen.items():assert sha(stage1/p)==h,p
 out.mkdir(parents=True);arrays.mkdir(parents=True);started=time.monotonic();gm,audit=imports();ctrl=controls(gm,audit);table(out/'controls.csv',ctrl);states=json.loads((stage1/'synthetic_states.json').read_text())['states'];preds=rows(stage1/'predictors.csv');alltables={n:[] for n in TABLE_NAMES};timings=[]
 def save():
  for name,rs in alltables.items():table(out/(name+'.csv'),rs)
  write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_parent_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'workers':workers,'worker_resources':timings,'arrays_root':str(arrays)})
 tasks=[(st,str(arrays),started+CFG['budget_seconds']) for st in states]
 with ProcessPoolExecutor(max_workers=workers) as pool:
  for st,(tables,timing) in zip(states,pool.map(analyse_state,tasks,chunksize=1)):
   for name,rr in tables.items():alltables[name].extend(rr)
   timings.append(timing);save();print('STATE',st['id'],[(r['n'],r['type'],r['status']) for r in tables['outcomes']],flush=True)
 perstate,corr,q3,q4=assessments(preds,alltables);valid=all(c['status']=='PASS' for c in ctrl);q1='PASS' if all(q['Q1']=='PASS' for q in perstate) else ('FAIL' if any(q['Q1']=='FAIL' for q in perstate) else 'INCONCLUSIVE');q2='PASS' if all(q['Q2']=='PASS' and q['Q2_eligible'] for q in perstate) else ('FAIL' if any(q['Q2']=='FAIL' for q in perstate) else 'INCONCLUSIVE')
 if not valid:q1=q2=q3=q4='INCONCLUSIVE'
 table(out/'state_assessments.csv',perstate);table(out/'correlations.csv',corr);groups=[]
 for T in CFG['curvature_targets']:
  rr=[r for r in perstate if r['target']==T];oo=[r for r in alltables['outcomes'] if r['target']==T and r['n']==1024];ev=[r for r in oo if r['r_deg'] is not None];areas=[r['A_emb'] for r in ev if r['A_emb'] is not None];types={label:sum(label==r['type'] for r in oo) for label in {r['type'] for r in oo}};dominant=max(sorted(types),key=types.get);groups.append({'target':T,'states':len(rr),'censored_1024':sum(r['censored'] for r in oo),'unknown_1024':sum(r['status']=='INCONCLUSIVE_NUMERICAL' for r in oo),'dominant_type':dominant,'median_observed_rdeg':float(np.median([r['r_deg'] for r in ev])) if ev else None,'observed_events':len(ev),'median_event_A_emb':float(np.median(areas)) if areas else None,'areas_observed':len(areas),'fraction_not_constructible':sum(r['area_answer']=='NOT_CONSTRUCTIBLE_BEFORE_EVENT' for r in rr)/len(rr),'fraction_area_unknown':sum(r['area_answer']=='?' for r in rr)/len(rr),'fraction_radius_unknown':sum(r['radius_answer']=='?' for r in rr)/len(rr)})
 table(out/'by_scale.csv',groups);write(out/'summary.json',{'status':'VALID_EXPLORATORY' if valid else 'INVALID','Q1':q1,'Q2':q2,'Q3':q3,'Q4':q4,'states':len(perstate),'controls':len(ctrl),'controls_pass':sum(c['status']=='PASS' for c in ctrl),'Q1_counts':{s:sum(r['Q1']==s for r in perstate) for s in ['PASS','FAIL','INCONCLUSIVE']},'Q2_conditional_eligible':sum(r['Q2_eligible'] for r in perstate),'Q2_conditional_pass':sum(r['Q2']=='PASS' for r in perstate),'area_unknown':sum(r['area_answer']=='?' for r in perstate),'radius_unknown':sum(r['radius_answer']=='?' for r in perstate),'predictors_sha256':frozen['predictors.csv'],'states_sha256':frozen['synthetic_states.json'],'blocked_prohibited_reads_parent':ACCESS['blocked'],'blocked_prohibited_reads_workers':sum(r['blocked_prohibited_reads'] for r in timings),'transfer_to_T2':'NONE; synthetic paired calibration only'})
 write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'mpmath':mp.__version__,'geometry_sha256':CFG['geometry_sha256'],'audit_sha256':CFG['audit_sha256'],'code_sha256':sha(Path(__file__)),'numerics_sha256':sha(ROOT/'scripts/outcome_numerics_v1.py'),'workers':workers,'predictor_commit':'e798206'});save();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/stage2_v1');p.add_argument('--arrays',type=Path,default=Path('/workspace/work/e16-af-v1-arrays'));p.add_argument('--workers',type=int,default=2);a=p.parse_args();main(a.out,a.arrays,a.workers)
