#!/usr/bin/env python3
"""AE prospectivo: disco, índice normal y búsqueda de ramas con censura explícita."""
from numerics_v1 import *
from scipy.optimize import least_squares
import argparse,time,resource,platform,scipy

def main(out):
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);started=time.monotonic();metric,prep=prepare();center=np.array(MAIN['center'],float);chol=np.linalg.cholesky(metric.geometry(center)[0]);records=[];profiles=[];resolutions=[];events=[];mp_audits=[];indices=[];bands=[];spectra=[];modes=[];index_nodes=[];search=[];controls=[];errors=[];tables={'rays':records,'profiles':profiles,'resolutions':resolutions,'events':events,'mp_audits':mp_audits,'indices':indices,'normal_bands':bands,'normal_spectra':spectra,'normal_modes':modes,'index_nodes':index_nodes,'shooting':search,'controls':controls,'failures':errors}
 for p,h in MAIN.get('main_sources',{}).items():assert sha(E16/p)==h
 def save():
  for n,rr in tables.items():table(out/(n+'.csv'),rr)
  write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})
 def budget():
  if time.monotonic()-started>MAIN['budget_seconds']:save();raise TimeoutError('BUDGET; restantes UNKNOWN')
 def control(name,good,error=0.,reason=''):controls.append({'control':name,'status':'PASS' if good else 'FAIL','error':float(error),'reason':reason})
 # Controles de Jacobi y área, con signo de K independiente de softmax.
 for name,K,L in [('sphere',1.,1.5*np.pi),('hyperbolic',-1.,4.),('flat',0.,1.)]:
  def rhs(s,z):return [z[1],-K*z[0],z[0]]
  def event(s,z):return z[0]
  sol=solve_ivp(rhs,(0,L),[0.,1.,0.],method='DOP853',rtol=1e-12,atol=1e-14,max_step=.05,dense_output=True,events=event);zs=[r for r in sol.t_events[0] if r>1e-7];expected=(np.sin(L),1-np.cos(L)) if K==1 else ((np.sinh(L),np.cosh(L)-1) if K==-1 else (L,L*L/2));err=max(abs(sol.y[0,-1]-expected[0]),abs(sol.y[2,-1]-expected[1]))/max(1,abs(expected[0]),abs(expected[1]));ok=len(zs)==(1 if K==1 else 0) and err<1e-7 and (K!=1 or abs(zs[0]-np.pi)<1e-8);control(name+'/Jacobi',ok,err)
  if K==1:control('sphere/area_at_pi',abs(2*np.pi*sol.sol(np.pi)[2]-4*np.pi)<1e-7,abs(2*np.pi*sol.sol(np.pi)[2]-4*np.pi))
 circle=np.column_stack([np.cos(np.linspace(0,2*np.pi,64,endpoint=False)),np.sin(np.linspace(0,2*np.pi,64,endpoint=False))]);control('collision/crossed',intersections(np.array([[-1.,-1.],[1.,1.],[-1.,1.],[1.,-1.]])) is not None);control('collision/circle',intersections(circle) is None);sph=np.array([[np.sin(np.pi),0,np.cos(np.pi)],[-np.sin(np.pi),0,np.cos(np.pi)]]);control('sphere/opposite_rays_pi',np.linalg.norm(sph[0]-sph[1])<1e-8,np.linalg.norm(sph[0]-sph[1]))
 # Control plano real de AD, usando IVP fijado por AC, no reabriendo su shooting.
 ac=load('ac_control_ae',E16/'AC/scripts/run_v2.py');d=load('d_control_ae',E16/'D/scripts/run.py');data=json.loads((E16/'H/data.json').read_text())
 with mp.workdps(80):
  th=[mp.mpf(str(x)) for x in data['states']['h00']];inp=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels']['P0']];cv,jc,_,ch=d.analytic_mp(th,inp);ux=d.analytic_B(cv,jc,[1,0],'quadratic')[0]*ch;uy=d.analytic_B(cv,jc,[0,1],'quadratic')[0]*ch
 flat=ac.Metric('quadratic',np.array(ux.tolist(),float),np.array(uy.tolist(),float));A=np.array(data['perspectives'][0],float);shoot=next(q for q in rows(E16/'AC/results/run_v2/shooting.csv') if q['path']=='Q0/reference/132' and float(q['rtol'])==1e-12);angle=float(shoot['angle']);unit=np.array([np.cos(angle),np.sin(angle)]);v=unit/np.sqrt(unit@flat.geometry(A)[0]@unit);flat_sol,_,_=trace(flat,A,v,float(shoot['L']));err=max(abs(float(flat.geometry(flat_sol.sol(s)[:2])[2])) for s in np.linspace(0,float(shoot['L']),9));jerr=abs(flat_sol.y[4,-1]-float(shoot['L']));control('AD_flat/K_Jacobi',err<1e-7 and jerr<1e-7,max(err,jerr))
 def unit_normals(points,velocities,m):
  ns=[]
  for p,v in zip(points,velocities):h=m.geometry(p)[0];hv=h@v;n=np.array([-hv[1],hv[0]]);n/=np.sqrt(n@h@n);ns.append(n)
  return np.array(ns)
 for m in MAIN['index_meshes']:
  for kind,factor in [('sphere',.75),('sphere',1.25),('hyperbolic',1.),('flat_ad',1.)]:
   L=factor*np.pi if kind=='sphere' else (1. if kind=='hyperbolic' else float(shoot['L']));ss=np.linspace(0,L,m+1)
   if kind=='sphere':points=np.column_stack([np.zeros(m+1),ss]);ns=np.column_stack([np.ones(m+1),np.zeros(m+1)]);expected=0 if factor<1 else 1
   elif kind=='hyperbolic':points=np.column_stack([ss,np.zeros(m+1)]);ns=np.column_stack([np.zeros(m+1),np.exp(-ss)]);expected=0
   else:zz=flat_sol.sol(ss);points=zz[:2].T;ns=unit_normals(points,zz[2:4].T,flat);expected=0
   H,g=normal_block(points,ns,flat,8,kind,budget);H2,_=normal_block(points,ns,flat,16,kind,budget);ev=np.linalg.eigvalsh(H);tau=max(1e-8,1e-7*max(abs(ev)));count=int(sum(ev< -tau));err=np.max(abs(H-H2))/max(1,np.max(abs(H2)));control(f'{kind}/{factor}/normal/{m}',count==expected and err<1e-5,err,f'negative={count},expected={expected}')
 save();bundles={}
 for nrays in MAIN['ray_counts']:
  sols=[];local=[]
  for i in range(nrays):
   theta=2*np.pi*i/nrays;v=np.linalg.solve(chol.T,[np.cos(theta),np.sin(theta)]);row={'n':nrays,'ray':i,'angle':theta,'status':'UNKNOWN','coverage':0.,'conjugate':None,'domain_censor':None,'reason':''}
   try:
    budget();sol,zs,censor=trace(metric,center,v,MAIN['r_max']);coverage=float(sol.t[-1]);status='RIGHT_CENSORED_DOMAIN' if censor else ('COMPLETE' if sol.success else 'INCONCLUSIVE_NUMERICAL');row.update(status=status,coverage=coverage,conjugate=zs[0] if zs else None,domain_censor=coverage if censor else None,reason='' if sol.success else sol.message);sols.append(sol)
    samples=np.r_[np.linspace(0,MAIN['r_max'],MAIN['radial_levels'])[np.linspace(0,MAIN['r_max'],MAIN['radial_levels'])<coverage],coverage]
    for s,z in zip(samples,sol.sol(samples).T):profiles.append({'n':nrays,'ray':i,'r':float(s),'p0':float(z[0]),'p1':float(z[1]),'j':float(z[4]),'jprime':float(z[5]),'I':float(z[6])})
    for event_type,value in [('conjugate',row['conjugate']),('domain_censor',row['domain_censor'])]:
     if value is not None:events.append({'n':nrays,'ray':i,'event':event_type,'r_lower':value,'r_upper':value,'partner':''})
   except Exception as e:row.update(status='INCONCLUSIVE_NUMERICAL',reason=type(e).__name__+':'+str(e));sols.append(None);errors.append({'stage':'ray','case':f'{nrays}/{i}','reason':row['reason']})
   local.append(row);records.append(row)
   if i%32==0:save();print('RAYS',nrays,i,row['status'],flush=True)
  coverage=min(q['coverage'] for q in local);first_conj=min([q['conjugate'] for q in local if q['conjugate'] is not None],default=None);collision=None;previous=0.
  if all(s is not None for s in sols):
   for r in np.linspace(0,MAIN['r_max'],MAIN['radial_levels']):
    if r>coverage:break
    if r<MAIN['collision_radius_min']:previous=float(r);continue
    crossing=intersections(np.array([s.sol(r)[:2] for s in sols]))
    if crossing is not None:collision=(previous,float(r),crossing);events.append({'n':nrays,'ray':crossing[0],'event':'front_collision_bracket','r_lower':previous,'r_upper':float(r),'partner':crossing[1]});break
    previous=float(r)
  candidate=min([q for q in [first_conj,collision[1] if collision else None] if q is not None],default=None);event_observed=candidate is not None and candidate<=coverage
  safe_count=sum(q['coverage']>=MAIN['r_fixed'] and (q['conjugate'] is None or q['conjugate']>MAIN['r_fixed']) and q['status']!='INCONCLUSIVE_NUMERICAL' for q in local);fraction=safe_count/nrays
  resolutions.append({'n':nrays,'first_conjugate':first_conj,'first_collision_lower':collision[0] if collision else None,'first_collision_upper':collision[1] if collision else None,'coverage_all':coverage,'r_deg':candidate if event_observed else None,'A_deg':float(2*np.pi/nrays*sum(s.sol(candidate)[6] for s in sols)) if event_observed else None,'degeneration_status':'OBSERVED_SAMPLED_EVENT' if event_observed else 'RIGHT_CENSORED','safe_count_at_fixed':safe_count,'fraction_at_fixed':fraction,'censored_before_fixed':sum(q['coverage']<MAIN['r_fixed'] for q in local),'failed':sum(q['status']=='INCONCLUSIVE_NUMERICAL' for q in local),'r_safe_common':None,'A_safe_common':None});bundles[nrays]=(sols,local);save()
 # Comparación de áreas en radio común anterior a censura/evento.
 mincov=min(q['coverage_all'] for q in resolutions);degs=[q['r_deg'] for q in resolutions if q['r_deg'] is not None];rsafe=.95*min([mincov]+degs)
 for rr in resolutions:
  sols,_=bundles[rr['n']];rr['r_safe_common']=rsafe;rr['A_safe_common']=float(2*np.pi/rr['n']*sum(s.sol(rsafe)[6] for s in sols)) if rsafe>0 and all(s is not None for s in sols) else None
 # Contraste MP de geodésica/Jacobi completo, no sólo K sobre trayectoria float.
 mp_good=True
 for coarse_idx in MAIN['mp_rays']:
  sols,local=bundles[1024];idx=2*coarse_idx;sol=sols[idx];q=local[idx]
  if sol is None or q['coverage']<=0:mp_good=False;continue
  length=.95*q['coverage'];theta=q['angle'];v=np.linalg.solve(chol.T,[np.cos(theta),np.sin(theta)]);values=[]
  try:
   for digits,steps in zip(MAIN['mp_digits'],MAIN['mp_steps']):values.append(mp_trace(prep[digits],center,v,length,digits,steps,budget))
   f=sol.sol(length);scale=np.maximum(1,abs(f));err=float(np.max(abs(values[1][0]-f)/scale));convergence=float(np.max(abs(values[0][0]-values[1][0])/scale));good=err<=MAIN['mp_agreement'] and convergence<=MAIN['mp_agreement'] and len(values[0][1])==len(values[1][1]);mp_good=mp_good and good;mp_audits.append({'ray':idx,'length':length,'error_float_MP':err,'error_MP_steps':convergence,'MP50_conjugates':len(values[0][1]),'MP80_conjugates':len(values[1][1]),'status':'PASS' if good else 'INCONCLUSIVE','reason':''})
  except Exception as e:mp_good=False;mp_audits.append({'ray':idx,'length':length,'error_float_MP':'','error_MP_steps':'','MP50_conjugates':'UNKNOWN','MP80_conjugates':'UNKNOWN','status':'INCONCLUSIVE','reason':str(e)})
  save();print('MP',idx,mp_audits[-1]['status'],flush=True)
 # Q2 medición de Hessiana de longitud por segmentos en carta normal.
 q2_observations=[]
 for nrays in MAIN['ray_counts']:
  sols,local=bundles[nrays]
  for ray_angle in MAIN['index_ray_angles']:
   idx=int(round(ray_angle/(2*np.pi)*nrays))%nrays;q=local[idx];sol=sols[idx];conj=q['conjugate'];targets=[factor*conj for factor in MAIN['index_factors_with_conjugate']] if conj else MAIN['index_radii_without_conjugate']
   for target_id,length in enumerate(targets):
    for m in MAIN['index_meshes']:
     name=f'{nrays}/{idx}/{target_id}/{m}';row={'case':name,'n':nrays,'ray':idx,'target':target_id,'L':length,'mesh':m,'source_conjugate':conj,'index':None,'gradient':None,'minimum':None,'threshold':None,'MP_Rayleigh':None,'quadrature_error':None,'status':'INCONCLUSIVE','reason':''}
     try:
      budget()
      if sol is None or length>q['coverage']:raise ValueError('RIGHT_CENSORED_TARGET')
      zz=sol.sol(np.linspace(0,length,m+1));points=zz[:2].T;ns=unit_normals(points,zz[2:4].T,metric);H,g=normal_block(points,ns,metric,8,'soft',budget);H2,_=normal_block(points,ns,metric,16,'soft',budget);ev,vec=eigh(H);tau=max(MAIN['index_absolute_tol'],MAIN['index_relative_tol']*max(abs(ev)));count=int(sum(ev< -tau));quaderr=float(np.max(abs(H-H2))/max(1,float(np.max(abs(H2)))));gradient=float(max(abs(g)))/max(1,length);w=vec[:,0];mpcur=[]
      with mp.workdps(80):
       zero=[mp.mpf(0)]*(m-1);base=mp_length(prep[80],points,ns,zero)
       for step in MAIN['mp_direction_steps']:
        h=mp.mpf(step);lp=mp_length(prep[80],points,ns,[h*mp.mpf(float(x)) for x in w]);lm=mp_length(prep[80],points,ns,[-h*mp.mpf(float(x)) for x in w]);mpcur.append((lp+lm-2*base)/h**2)
       mperror=float(abs(mpcur[-1]-mp.mpf(float(ev[0])))/max(1,abs(mpcur[-1])));mpstep=float(abs(mpcur[0]-mpcur[1])/max(1,abs(mpcur[-1])))
      good=quaderr<=1e-5 and gradient<=MAIN['gradient_tol'] and mperror<=MAIN['mp_Rayleigh_tol'] and mpstep<=MAIN['mp_Rayleigh_tol'];row.update(index=count,gradient=gradient,minimum=float(ev[0]),threshold=tau,MP_Rayleigh=mp.nstr(mpcur[-1],60),quadrature_error=quaderr,status='PASS_NUMERICAL' if good else 'INCONCLUSIVE',reason='' if good else 'gradient_or_quadrature_or_MP')
      for j,p in enumerate(points):index_nodes.append({'case':name,'node':j,'p0':p[0],'p1':p[1],'normal0':ns[j,0],'normal1':ns[j,1]})
      for i in range(m-1):
       for j in range(max(0,i-1),min(m-1,i+2)):bands.append({'case':name,'row':i,'column':j,'value':float(H[i,j]),'dimension':m-1})
      for i,value in enumerate(ev):spectra.append({'case':name,'mode':i,'eigenvalue':float(value),'threshold':tau,'negative':bool(value< -tau)})
      for i in np.flatnonzero(ev< -tau):
       for j in range(m-1):modes.append({'case':name,'mode':int(i),'node':j+1,'normal_coefficient':float(vec[j,i]),'eigenvalue':float(ev[i])})
     except Exception as e:row['reason']=type(e).__name__+':'+str(e)
     indices.append(row);save();print('INDEX',name,row['status'],row['index'],flush=True)
   q2_observations.append((nrays,idx,conj))
 # Q3 sólo para objetivos posteriores a conjugados observados.
 for nrays in MAIN['ray_counts']:
  sols,local=bundles[nrays]
  for ray_angle in MAIN['index_ray_angles']:
   idx=int(round(ray_angle/(2*np.pi)*nrays))%nrays;q=local[idx];sol=sols[idx];conj=q['conjugate']
   if conj is None:search.append({'n':nrays,'ray':idx,'factor':'','start':'','status':'INCONCLUSIVE','L':None,'base_L':None,'endpoint_error':None,'shorter':False,'reason':'NO_OBSERVED_CONJUGATE','MP_endpoint_error':None});continue
   for factor in [1.05,1.25]:
    baseL=conj*factor
    if sol is None or baseL>q['coverage']:search.append({'n':nrays,'ray':idx,'factor':factor,'start':'','status':'INCONCLUSIVE','L':None,'base_L':baseL,'endpoint_error':None,'shorter':False,'reason':'RIGHT_CENSORED_TARGET','MP_endpoint_error':None});continue
    target=sol.sol(baseL)[:2]
    for start_id in range(MAIN['shoot_angles']):
     a0=2*np.pi*start_id/MAIN['shoot_angles'];rec={'n':nrays,'ray':idx,'factor':factor,'start':start_id,'status':'INCONCLUSIVE','L':None,'base_L':baseL,'endpoint_error':None,'shorter':False,'reason':'','MP_endpoint_error':None}
     try:
      budget()
      def residual(x):
       length=np.exp(x[1]);v=np.linalg.solve(chol.T,[np.cos(x[0]),np.sin(x[0])]);s,_,censor=trace(metric,center,v,length)
       if censor or not s.success:raise ValueError('SHOOTING_CENSORED_OR_FAILED')
       return (s.y[:2,-1]-target)/max(1,np.linalg.norm(target-center))
      opt=least_squares(residual,[a0,np.log(baseL)],bounds=([a0-np.pi/8,np.log(.1*baseL)],[a0+np.pi/8,np.log(1.5*MAIN['r_max'])]),xtol=1e-12,gtol=1e-12,ftol=1e-12,max_nfev=MAIN['shoot_nfev']);err=float(np.linalg.norm(residual(opt.x)));length=float(np.exp(opt.x[1]));rec.update(L=length,endpoint_error=err)
      if not opt.success or err>MAIN['endpoint_tol']:raise ValueError('SHOOTING_NONCONVERGENCE:'+str(opt.message))
      shorter=length<baseL-MAIN['shorter_tol']*max(1,baseL);vv=np.linalg.solve(chol.T,[np.cos(opt.x[0]),np.sin(opt.x[0])]);hp,_=mp_trace(prep[80],center,vv,length,80,1024,budget);mperr=float(np.linalg.norm(hp[:2]-target))/max(1,np.linalg.norm(target-center));rec.update(status='PASS_NUMERICAL' if mperr<=1e-5 else 'INCONCLUSIVE',shorter=shorter,MP_endpoint_error=mperr,reason='' if mperr<=1e-5 else 'MP_ENDPOINT')
     except Exception as e:rec['reason']=str(e)
     search.append(rec);save()
 valid=all(q['status']=='PASS' for q in controls);areas=[q['A_safe_common'] for q in resolutions];areastable=all(q is not None for q in areas) and abs(areas[0]-areas[1])/max(1,abs(areas[1]))<=MAIN['convergence_area'];q1='INCONCLUSIVE' # K0 negativo: predicción positiva no aplicable en el centro fijado.
 applicable=all(q[2] is not None for q in q2_observations);q2='INCONCLUSIVE'
 if applicable and all(q['status']=='PASS_NUMERICAL' for q in indices) and mp_good:
  matches=all(q['index']==(0 if q['target']==0 else 1) for q in indices);q2='PASS' if matches else ('FAIL' if all(len({q['index'] for q in indices if q['target']==target})==1 for target in range(3)) else 'INCONCLUSIVE')
 q3='INCONCLUSIVE';eligible=[q for q in search if q['start']!='']
 if eligible and all(q['status']=='PASS_NUMERICAL' for q in eligible) and all(q[2] is not None for q in q2_observations):
  groups={(q['n'],q['ray'],q['factor']) for q in eligible};found=[any(q['shorter'] for q in eligible if (q['n'],q['ray'],q['factor'])==group) for group in groups];q3='PASS' if all(found) else ('FAIL' if not any(found) else 'INCONCLUSIVE')
 if not valid:q1=q2=q3='INCONCLUSIVE'
 write(out/'summary.json',{'run_status':'VALID_EXPLORATORY' if valid else 'INVALID','Q1':q1,'Q2':q2,'Q3':q3,'Q1_reason':'K(center)<0: positive-local-curvature prediction not applicable; domain/radius censoring retained','controls':len(controls),'controls_pass':sum(q['status']=='PASS' for q in controls),'mp_ray_contrast':'PASS' if mp_good else 'INCONCLUSIVE','area_consistency':'PASS' if areastable else 'INCONCLUSIVE','r_safe_common':rsafe,'cut_locus':'UNKNOWN; finite shooting only; no claim of global minimum','K_range_phase0':json.loads((ROOT/'results/phase0_v1/summary.json').read_text())['K_min']});write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__,'config_sha256':sha(ROOT/'config.json'),'code_sha256':sha(Path(__file__)),'metric_sha256':sha(ROOT/'scripts/metric_v1.py')});save();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/main_v1');main(p.parse_args().out)
