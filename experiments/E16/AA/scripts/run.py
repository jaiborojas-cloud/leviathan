#!/usr/bin/env python3
"""E16-AA: continuación prospectiva a KKT físico 1e-7."""
import argparse,csv,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
import mpmath as mp
from autograd import grad,hessian
from scipy.optimize import minimize
from scipy.linalg import eigh,eigvalsh
ROOT=Path(__file__).resolve().parents[1];CFG=json.loads((ROOT/'config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rows(p):return list(csv.DictReader(p.open()))
def fmt(x):return mp.nstr(x,40)
def rel(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rs):
 if rs:
  with p.open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def point_hash(z):return hashlib.sha256(json.dumps(np.asarray(z,float).tolist(),separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dot(a,b):return mp.fsum(x*y for x,y in zip(a,b))

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('k_z',ROOT.parent/'P/scripts/kernel.py');d=load('d_z',ROOT.parent/'D/scripts/run.py');g=load('g_z',ROOT.parent/'G/scripts/run.py');xmod=load('x_z',ROOT.parent/'X/scripts/run.py');y=load('y_z',ROOT.parent/'Y/scripts/run.py');stopping=load('stop_z',ROOT.parent/'S/scripts/stopping.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text());sources=rows(ROOT.parent/'S/results/run_v1/paths.csv');oldv=rows(ROOT.parent/'S/results/run_v1/vertices.csv');zp=rows(ROOT.parent/'Z/results/run_v1/paths.csv');zv=rows(ROOT.parent/'Z/results/run_v1/vertices.csv')
 checks=[];paths=[];vertices=[];gradients=[];monitor=[];spectra=[];audits=[];comparisons=[];costs=[];timings=[];tables={'checks':checks,'paths':paths,'vertices':vertices,'gradients':gradients,'monitor':monitor,'spectra':spectra,'audits':audits,'comparisons':comparisons,'costs':costs}
 def check(name,e,tol):
  ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(str(tol)));checks.append({'name':name,'error':fmt(e),'tolerance':str(tol),'status':'PASS' if ok else 'INCONCLUSIVE'});return ok
 def checkpoint():
  for name,rs in tables.items():table(out/(name+'.csv'),rs)
  elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;within=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib'];dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':within,'timings':timings})
  if not within:
   dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'resource_budget','completed_paths':len(paths),'remaining_paths':12-len(paths)});raise TimeoutError('budget; partial preserved, remaining UNKNOWN')
 dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'INCOMPLETE'})
 check('control/stopping',0 if stopping.controls() else 1,0)
 ctrl={'calls':0,'point':None};ww=np.array([1.,2.,4.,8.,16.])
 def callback_control(xx):
  ctrl['calls']+=1;ctrl['point']=np.asarray(xx).copy()
  if ctrl['calls']==2:raise StopIteration
 control=minimize(lambda xx:.5*float(np.sum(ww*xx*xx)),np.array([.8,-.7,.6,-.5,.4]),jac=lambda xx:ww*xx,bounds=[(-1.,1.)]*5,method='L-BFGS-B',callback=callback_control,options={'maxiter':10,'ftol':0.,'gtol':1e-14})
 check('control/native_callback',0 if ctrl['calls']==2 and control.status==99 and not control.success and np.array_equal(control.x,ctrl['point']) else 1,0)
 prepared={}
 for digits in CFG['precision']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(a)) for a in data['states']['h00']];zz=[[mp.mpf(str(a)) for a in data['inputs'][j]] for j in data['panels']['P0']];cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]={}
   for kind in ['sum','quadratic']:
    a=mp.matrix([mp.mpf(str(a)) for a in data['perspectives'][0]]);b=mp.matrix([mp.mpf(str(a)) for a in data['perspectives'][1]]);ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l;prepared[digits][kind]=(a,b,ux,uy)
 for source in sources:
  begin=time.monotonic();name=source['path'];m0=int(source['segments']);m=2*m0;n=m-1;cs=len(checks);ms=len(monitor);kind='sum' if source['lineage']=='C0' else 'quadratic';rr=sorted([r for r in oldv if r['path']==name],key=lambda r:int(r['index']));z0=np.array([[float(r['t']),float(r['s'])] for r in rr]);zr=sorted([r for r in zv if r['path']==name],key=lambda r:int(r['index']));initial=np.array([[float(r['t']),float(r['s'])] for r in zr]);zrow=next(r for r in zp if r['path']==name);weights=np.linalg.norm(np.diff(z0,axis=0),axis=1);weights=np.repeat(weights/np.sum(weights)/2,2);M=y.mass(weights);box=np.array([[0.,1.],[-.25,.25]]*n);xx0=k.pack(initial,'free');a,b,ux,uy=prepared[80][kind];obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',initial[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float));physical_grad=grad(obj.value);meter={'mp_local':0,'mp_global':0,'AD_extra':0,'SPD_edges':0};nit=0;unverified=0;rule=stopping.SustainedRule(CFG['monitor_interval'],CFG['required_streak'],CFG['KKT_tolerance']);stop_hash=''
  def coords(xx):return np.asarray(k.coords(np.asarray(xx,float),'free',initial[:,0]),float)
  def adgrad(xx):meter['AD_extra']+=1;return np.asarray(physical_grad(xx),float)
  def kkt(xx,gg,value):return float(np.max(abs(xx-np.clip(xx-gg,box[:,0],box[:,1]))))/max(1,abs(float(value)))
  def full_gradient(xx,prefix,save=False,gad=None):
   zz=coords(xx);gad=adgrad(xx) if gad is None else gad;fd0=[];gm=[]
   with mp.workdps(80):
    a,b,ux,uy=prepared[80][kind];pts=k.mp_points(a,b,zz);vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);meter['mp_global']+=1;value=k.reference(pts,kind,ux,uy);scale=max(1,abs(value))
    for j in range(1,m):
     for axis,direction in enumerate([vv,nn]):
      fd=[]
      for step in CFG['gradient_steps']:
       h=mp.mpf(step);lp=k.reference([pts[j-1],pts[j]+h*direction,pts[j+1]],kind,ux,uy);lm=k.reference([pts[j-1],pts[j]-h*direction,pts[j+1]],kind,ux,uy);meter['mp_local']+=2;fd.append((lp-lm)/(2*h))
      i=2*(j-1)+axis;fd0.append(fd[0]);gm.append(fd[-1])
      if save:gradients.append({'path':name,'node':j,'coordinate':'t' if axis==0 else 's','AD':repr(float(gad[i])),'MP_fd_1':fmt(fd[0]),'MP_fd_2':fmt(fd[1])})
    ge=max(abs(mp.mpf(float(a))-b) for a,b in zip(gad,gm))/scale;fe=max(abs(a-b) for a,b in zip(fd0,gm))/scale;ok=check(prefix+'/gradient_AD',ge,CFG['gradient_tolerance']) and check(prefix+'/gradient_steps',fe,CFG['gradient_steps_tolerance']);res=kkt(xx,np.array([float(q) for q in gm]),value)
   return value,gm,res,ok,ge,fe
  def audit(xx,iteration,force=False):
   nonlocal unverified,stop_hash
   beforeL=meter['mp_local'];beforeG=meter['mp_global'];gad=adgrad(xx);advalue=float(obj.value(xx));adk=kkt(xx,gad,advalue);reason='';value=None;res=None;verified=False
   if not force and np.isfinite(adk) and adk>CFG['AD_screen']:state='SCREENED_NONSTATIONARY'
   else:
    try:
     value,gg,res,verified,ge,fe=full_gradient(xx,name+'/monitor/'+str(iteration),gad=gad);state='STATIONARY' if verified and res<=CFG['KKT_tolerance'] else ('NONSTATIONARY' if verified else 'UNVERIFIED')
    except (ValueError,ZeroDivisionError) as e:state='UNVERIFIED';reason=type(e).__name__+':'+str(e)
    if state=='UNVERIFIED':unverified+=1
   requested=rule.observe(iteration,verified,res if res is not None else float('inf'));digest=point_hash(coords(xx))
   if requested:stop_hash=digest
   monitor.append({'path':name,'iteration':iteration,'state':state,'AD_kkt':repr(adk),'MP_kkt':repr(res) if res is not None else '', 'MP_verified':verified,'streak':rule.streak,'stop_requested':requested,'point_sha256':digest,'MP_local_calls':meter['mp_local']-beforeL,'MP_global_calls':meter['mp_global']-beforeG,'reason':reason});checkpoint();return requested,value
  check(name+'/initial_hash',0 if point_hash(initial)==zrow['final_point_sha256'] else 1,0)
  _,initial_length=audit(xx0,0,True)
  if initial_length is not None:
   with mp.workdps(120):check(name+'/initial_length',rel(initial_length,mp.mpf(zrow['final_length'])),CFG['embedding_tolerance'])
  def callback(xx):
   nonlocal nit
   nit+=1
   if nit%CFG['monitor_interval']==0 and audit(xx,nit)[0]:raise StopIteration
  opt=minimize(obj.fun,xx0,jac=lambda xx:np.asarray(physical_grad(xx),float),bounds=[tuple(q) for q in box],method=CFG['optimizer']['method'],options={kk:vv for kk,vv in CFG['optimizer'].items() if kk!='method'},callback=callback);xx=np.asarray(opt.x,float);zz=coords(xx);digest=point_hash(zz);check(name+'/callback_count',abs(nit-int(opt.nit)),0)
  if rule.requested:
   route='PHYSICAL_SUSTAINED';accepted=True;check(name+'/native_stop',0 if opt.status==99 and not opt.success else 1,0);check(name+'/stop_hash',0 if digest==stop_hash else 1,0);check(name+'/stop_iteration',abs(nit-rule.stop_iteration),0)
  elif opt.success:route='NATIVE_CONTROL' if kind=='sum' else 'NATIVE_VERIFIED';accepted=True
  else:route='UNVERIFIED_TERMINATION';accepted=False
  value,gm,res,gradient_ok,ge,fe=full_gradient(xx,name+'/final',True);check(name+'/final_KKT',res,CFG['KKT_tolerance']);spectral_reason='';margin=float(np.min(np.minimum(xx-box[:,0],box[:,1]-xx)));interior=margin>CFG['boundary_margin']
  with mp.workdps(120):
   a,b,ux,uy=prepared[120][kind];pts=k.mp_points(a,b,zz);meter['mp_global']+=1;val120=k.reference(pts,kind,ux,uy);check(name+'/final_precision',rel(value,val120),CFG['precision_tolerance']);check(name+'/nonworse',max(0,val120-initial_length)/max(1,abs(initial_length)) if initial_length is not None else 1,CFG['nonworse_tolerance']);check(name+'/boxes',max(0,float(np.max(box[:,0]-xx)),float(np.max(xx-box[:,1]))),0);check(name+'/endpoints',float(np.max(abs(zz[[0,-1]]-np.array([[0,0],[1,0]])))),0);spd=True
   for u0,du,uu,dd in k.mp_edges(pts,kind,ux,uy):pa,pd=g.positive([u0*u0.T,du*u0.T+u0*du.T,du*du.T]);spd=spd and bool(pa and pd);meter['SPD_edges']+=1
   check(name+'/final_SPD',0 if spd else 1,0)
   if kind=='sum':straight=mp.sqrt(((b-a).T*(ux*ux.T)*(b-a))[0]);check(name+'/control_length',rel(val120,straight),1e-8);check(name+'/control_normal',float(np.max(abs(zz[:,1]))),1e-6)
  physical_good=accepted and unverified==0 and all(r['status']=='PASS' for r in checks[cs:]);ss=len(checks);mu=None;tau=None;mass_witness=False;spectral_good=False;route_basis='UNKNOWN';bilateral=False
  try:
   raw=np.asarray(hessian(obj.value)(xx),float);H=(raw+raw.T)/2;gf=np.array([float(q) for q in gm]);small=np.linalg.norm(gf)<=float(CFG['gradient_floor']);B=xmod.basis(gf,small);Hr=B.T@H@B;Mr=B.T@M@B;Hr=(Hr+Hr.T)/2;Mr=(Mr+Mr.T)/2;np.linalg.cholesky(M);full=eigvalsh(H,M);ev,evec=eigh(Hr,Mr);mu=float(ev[0]);tau=CFG['spectral_relative_floor']*max(1,float(np.max(abs(ev))));v=xmod.canonical(B@evec[:,0]);scale=max(1,float(np.linalg.norm(H,ord=np.inf)),abs(mu)*float(np.linalg.norm(M,ord=np.inf)));route_basis='SMALL_GRADIENT' if small else 'GRADIENT_RESTRICTED'
   check(name+'/spectral_symmetry',float(np.max(abs(raw-raw.T)))/scale,CFG['eigen_tolerance']);check(name+'/spectral_basis',float(np.max(abs(B.T@B-np.eye(B.shape[1])))),CFG['basis_tolerance'])
   if not small:check(name+'/basis_gradient',float(np.max(abs((gf/np.linalg.norm(gf))@B))),CFG['basis_tolerance'])
   interlace=float(np.max(abs(ev-full))) if small else max(0,float(np.max(full[:-1]-ev)),float(np.max(ev-full[1:])));check(name+'/interlacing',interlace/max(1,float(np.max(abs(full)))),CFG['eigen_tolerance']);rvec=H@v-mu*(M@v);rvec=rvec if small else rvec-gf*float(gf@rvec)/float(gf@gf);check(name+'/eigen_residual',float(np.max(abs(rvec)))/scale,CFG['eigen_tolerance'])
   for j,evj in enumerate(ev):spectra.append({'path':name,'index':j,'eigenvalue':repr(float(evj)),'threshold':repr(tau),'mode_class':'NEGATIVE' if evj< -tau else ('NEAR_ZERO' if abs(evj)<=tau else 'POSITIVE')})
   qs={};measured={}
   for digits in CFG['precision']:
    with mp.workdps(digits):
     q=[mp.mpf(float(a)) for a in v];gg=[mp.mpf(a) for a in gm]
     if not small:coefficient=dot(gg,q)/dot(gg,gg);q=[a-coefficient*b for a,b in zip(q,gg)]
     maxnode=max(mp.sqrt(q[2*j]**2+q[2*j+1]**2) for j in range(n));q=[a/maxnode for a in q];jmax=max(range(len(q)),key=lambda j:abs(q[j]))
     if q[jmax]<0:q=[-a for a in q]
     qs[digits]=q;massnorm=y.mass_quad(q,weights);check(name+'/'+str(digits)+'/spectral_constraint',abs(dot(gg,q))/max(1,mp.sqrt(dot(gg,gg))),CFG['MP_constraint_tolerance']);a,b,ux,uy=prepared[digits][kind];pts=k.mp_points(a,b,zz);vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);dp=[q[2*j]*vv+q[2*j+1]*nn for j in range(n)];baseL=value if digits==80 else val120;der=[];cur=[]
     for step in CFG['audit_steps']:
      h=mp.mpf(step);plus=[pts[0]]+[p+h*dq for p,dq in zip(pts[1:-1],dp)]+[pts[-1]];minus=[pts[0]]+[p-h*dq for p,dq in zip(pts[1:-1],dp)]+[pts[-1]];meter['mp_global']+=2;lp=k.reference(plus,kind,ux,uy);lm=k.reference(minus,kind,ux,uy);der.append((lp-lm)/(2*h));cur.append((lp+lm-2*baseL)/(h*h*massnorm))
     check(name+'/'+str(digits)+'/spectral_slope',abs(der[-1])/max(1,abs(baseL)),CFG['slope_tolerance']);check(name+'/'+str(digits)+'/spectral_slope_steps',rel(*der),CFG['slope_steps_tolerance']);check(name+'/'+str(digits)+'/mass_rayleigh',rel(mp.mpf(mu),cur[-1]),CFG['rayleigh_tolerance']);check(name+'/'+str(digits)+'/mass_rayleigh_steps',rel(*cur),CFG['rayleigh_steps_tolerance']);measured[digits]=(der[-1],cur[-1]);audits.append({'path':name,'precision':digits,'vector_sha256':hashlib.sha256(json.dumps([fmt(a) for a in q],separators=(',',':')).encode()).hexdigest(),'mass_norm_squared':fmt(massnorm),'derivative_1':fmt(der[0]),'derivative_2':fmt(der[1]),'mass_rayleigh_1':fmt(cur[0]),'mass_rayleigh_2':fmt(cur[1])})
     if digits==120:
      basecoords=[(mp.mpf(float(t)),mp.mpf(repr(float(s)))) for t,s in zz];h=mp.mpf('1e-10');bilateral=all(mp.mpf(str(box[i,0]))<=basecoords[j+1][axis]+sg*h*q[i]<=mp.mpf(str(box[i,1])) for j in range(n) for axis in [0,1] for i in [2*j+axis] for sg in [-1,1])
   with mp.workdps(120):
    check(name+'/spectral_direction_precision',max(abs(a-b) for a,b in zip(qs[80],qs[120])),CFG['precision_tolerance']);check(name+'/spectral_slope_precision',rel(measured[80][0],measured[120][0]),CFG['precision_tolerance']);check(name+'/spectral_rayleigh_precision',rel(measured[80][1],measured[120][1]),CFG['precision_tolerance']);mass_witness=measured[120][1]< -mp.mpf(CFG['witness_tolerance'])*max(1,abs(mp.mpf(mu)))
   spectral_good=all(r['status']=='PASS' for r in checks[ss:]);mass_witness=bool(mass_witness and spectral_good)
  except (ValueError,ZeroDivisionError,np.linalg.LinAlgError) as e:spectral_reason=type(e).__name__+':'+str(e)
  eligible=bool(physical_good and spectral_good and interior)
  paths.append({'path':name,'lineage':source['lineage'],'provenance_arm':source['arm'],'segments':m,'first_order_status':'PASS' if physical_good else 'INCONCLUSIVE','termination_route':route,'native_success':bool(opt.success),'native_status':int(opt.status),'native_message':str(opt.message),'iterations':int(opt.nit),'nfev':int(opt.nfev),'njev':int(opt.njev),'initial_length':fmt(initial_length) if initial_length is not None else '', 'final_length':fmt(val120),'final_KKT':repr(res),'gradient_AD_error':fmt(ge),'gradient_step_error':fmt(fe),'unverified_monitors':unverified,'final_streak':rule.streak,'final_point_sha256':digest,'SPD':spd,'box_margin':repr(margin),'interior':interior,'spectral_status':'PASS' if spectral_good else 'INCONCLUSIVE','spectral_reason':spectral_reason,'basis_route':route_basis,'minimum_mass':repr(mu) if mu is not None else '', 'spectral_threshold':repr(tau) if tau is not None else '', 'negative_MP_witness':mass_witness,'bilateral_probe_feasible':bilateral,'stationary_comparison_eligible':eligible,'minimum_status':'UNKNOWN','rejected_zero_edges':obj.rejections['zero_edge'],'rejected_invalid_primitive':obj.rejections['invalid_primitive']})
  for j,p in enumerate(zz):vertices.append({'path':name,'index':j,'t':repr(float(p[0])),'s':repr(float(p[1]))})
  comparisons.append({'path':name,'Z_initial_minimum_mass':zrow['minimum_mass'],'Z_initial_KKT':zrow['final_KKT'],'AA_final_minimum_mass':repr(mu) if mu is not None else '', 'AA_final_gradient_norm':repr(float(np.linalg.norm([float(q) for q in gm]))),'AA_final_KKT':repr(res),'Z_initial_length':zrow['final_length'],'AA_final_length':fmt(val120),'difference':repr(mu-float(zrow['minimum_mass'])) if mu is not None else '', 'stationary_comparison_eligible':eligible,'first_order_status':paths[-1]['first_order_status'],'minimum_status':'UNKNOWN'})
  costs.append({'path':name,'solver_function_calls':int(opt.nfev),'solver_gradient_calls':int(opt.njev),'additional_AD_gradient_calls':meter['AD_extra'],'MP_local_calls':meter['mp_local'],'MP_global_calls':meter['mp_global'],'MP120_SPD_edges':meter['SPD_edges'],'AD_hessian_calls':1,'screened_monitors':sum(r['state']=='SCREENED_NONSTATIONARY' for r in monitor[ms:]),'full_MP_monitors':sum(r['MP_global_calls']>0 for r in monitor[ms:]),'dense_arrays_archived':0});timings.append({'path':name,'seconds':time.monotonic()-begin});checkpoint();print(paths[-1],flush=True)
 dump(out/'provenance.json',{'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__});dump(out/'summary.json',{'status':'PASS_PROTOCOL' if len(paths)==12 and all(r['first_order_status']=='PASS' and r['spectral_status']=='PASS' for r in paths) and all(r['status']=='PASS' for r in checks) else 'INCONCLUSIVE','paths':len(paths),'first_order_pass':sum(r['first_order_status']=='PASS' for r in paths),'spectral_pass':sum(r['spectral_status']=='PASS' for r in paths),'stationary_comparison_eligible':sum(r['stationary_comparison_eligible'] for r in paths),'negative_MP_witnesses':sum(r['negative_MP_witness'] for r in paths),'monitors':len(monitor),'screened_monitors':sum(r['state']=='SCREENED_NONSTATIONARY' for r in monitor),'full_MP_monitors':sum(r['MP_global_calls']>0 for r in monitor),'checks':len(checks),'passed_checks':sum(r['status']=='PASS' for r in checks),'minimum_certificates':0});checkpoint();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(p.parse_args().out)
