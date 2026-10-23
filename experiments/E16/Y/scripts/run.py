#!/usr/bin/env python3
"""E16-Y: masa consistente y mínimo restringido bajo subdivisión."""
import argparse,csv,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
import mpmath as mp
from autograd import grad,hessian
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
def dot(a,b):return mp.fsum(x*y for x,y in zip(a,b))
def refine(coords):return [q for a,b in zip(coords[:-1],coords[1:]) for q in [a,tuple((x+y)/2 for x,y in zip(a,b))]]+[coords[-1]]
def mass(weights):
 m=len(weights);out=np.zeros((2*(m-1),2*(m-1)))
 for edge,w in enumerate(weights):
  for a in [edge,edge+1]:
   for b in [edge,edge+1]:
    if 0<a<m and 0<b<m:
     for axis in [0,1]:out[2*(a-1)+axis,2*(b-1)+axis]+=w*(2 if a==b else 1)/6
 return out
def mass_quad(v,weights):
 q=[(mp.mpf(0),mp.mpf(0))]+list(zip(v[::2],v[1::2]))+[(mp.mpf(0),mp.mpf(0))]
 return mp.fsum(mp.mpf(float(w))/3*(dot(a,a)+dot(a,b)+dot(b,b)) for w,a,b in zip(weights,q[:-1],q[1:]))
def transfer(m):
 out=np.zeros((2*(2*m-1),2*(m-1)))
 for j in range(1,2*m):
  for axis in [0,1]:
   if j%2==0:out[2*(j-1)+axis,2*(j//2-1)+axis]=1
   else:
    for node in [(j-1)//2,(j+1)//2]:
     if 0<node<m:out[2*(j-1)+axis,2*(node-1)+axis]=.5
 return out

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('k_y',ROOT.parent/'P/scripts/kernel.py');d=load('d_y',ROOT.parent/'D/scripts/run.py');xmod=load('x_y',ROOT.parent/'X/scripts/run.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text());sources=rows(ROOT.parent/'S/results/run_v1/paths.csv');vertices=rows(ROOT.parent/'S/results/run_v1/vertices.csv');oldgrad=rows(ROOT.parent/'S/results/run_v1/gradients.csv');xp=rows(ROOT.parent/'X/results/run_v1/paths.csv')
 checks=[];gradients=[];spectra=[];paths=[];comparisons=[];audits=[];costs=[];timings=[];tables={'checks':checks,'gradients':gradients,'spectra':spectra,'paths':paths,'comparisons':comparisons,'audits':audits,'costs':costs}
 def check(name,e,tol):
  ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(str(tol)));checks.append({'name':name,'error':fmt(e),'tolerance':str(tol),'status':'PASS' if ok else 'INCONCLUSIVE'});return ok
 def checkpoint():
  for n,rs in tables.items():table(out/(n+'.csv'),rs)
  elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;within=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib'];dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':within,'timings':timings})
  if not within:
   dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE','reason':'budget','completed_meshes':len(paths)});raise TimeoutError('budget; partial results retained')
 dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'INCOMPLETE'})
 controlM=mass(np.array([.5,.5]));check('control/mass',float(np.max(abs(controlM-np.eye(2)/3))),CFG['basis_tolerance']);controlH=np.diag([-2.,3.]);bb=xmod.basis(np.array([1.,0.]));check('control/restricted',abs(float(eigvalsh(bb.T@controlH@bb,bb.T@controlM@bb)[0])-9),CFG['basis_tolerance']);check('control/full',abs(float(eigvalsh(controlH,controlM)[0])+6),CFG['basis_tolerance'])
 prepared={}
 for digits in CFG['precision']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(a)) for a in data['states']['h00']];zz=[[mp.mpf(str(a)) for a in data['inputs'][j]] for j in data['panels']['P0']];cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]={}
   for kind in ['sum','quadratic']:
    a=mp.matrix([mp.mpf(str(a)) for a in data['perspectives'][0]]);b=mp.matrix([mp.mpf(str(a)) for a in data['perspectives'][1]]);ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l;prepared[digits][kind]=(a,b,ux,uy)
 for source in sources:
  name=source['path'];m0=int(source['segments']);kind='sum' if source['lineage']=='C0' else 'quadratic';rr=sorted([r for r in vertices if r['path']==name],key=lambda r:int(r['index']));z0=np.array([[float(r['t']),float(r['s'])] for r in rr]);weights0=np.linalg.norm(np.diff(z0,axis=0),axis=1);weights0/=np.sum(weights0);S=transfer(m0);saved={}
  for level in ['coarse','fine']:
   begin=time.monotonic();cs=len(checks);label=name+'/'+level;weights=weights0 if level=='coarse' else np.repeat(weights0/2,2);m=len(weights);coords={};pts={};baseL={};calls=0;gradientcalls=0
   for digits in CFG['precision']:
    with mp.workdps(digits):
     base=[(mp.mpf(float(t)),mp.mpf(repr(float(s)))) for t,s in z0];coords[digits]=base if level=='coarse' else refine(base);a,b,ux,uy=prepared[digits][kind];vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);pts[digits]=[a+q[0]*vv+q[1]*nn for q in coords[digits]];baseL[digits]=k.reference(pts[digits],kind,ux,uy);calls+=1;check(label+'/'+str(digits)+'/length',rel(baseL[digits],mp.mpf(source['length'])),CFG['subdivision_tolerance'])
   z=np.array([[float(a),float(b)] for a,b in coords[80]]);a,b,ux,uy=prepared[80][kind];obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float));x=k.pack(z,'free');gad=np.asarray(grad(obj.value)(x),float)
   if level=='coarse':
    with mp.workdps(80):gm=[mp.mpf(r['mp_fd_2']) for r in oldgrad if r['path']==name+'/final']
    check(label+'/archive_gradient_AD',float(np.max(abs(gad-np.array([float(a) for a in gm]))))/max(1,abs(float(baseL[80]))),CFG['gradient_agreement_tolerance']);gradienterr=0.;steperr=0.
   else:
    gm=[];errors=[];step_errors=[]
    with mp.workdps(80):
     a,b,ux,uy=prepared[80][kind];vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);scale=max(1,abs(baseL[80]))
     for j in range(1,m):
      for axis,direction in enumerate([vv,nn]):
       fd=[]
       for step in CFG['gradient_steps']:
        h=mp.mpf(step);p=pts[80][j];plus=p+h*direction;minus=p-h*direction;lp=k.reference([pts[80][j-1],plus,pts[80][j+1]],kind,ux,uy);lm=k.reference([pts[80][j-1],minus,pts[80][j+1]],kind,ux,uy);gradientcalls+=2;fd.append((lp-lm)/(2*h))
       i=2*(j-1)+axis;gm.append(fd[-1]);errors.append(abs(mp.mpf(float(gad[i]))-fd[-1])/scale);step_errors.append(abs(fd[0]-fd[1])/scale);gradients.append({'path':name,'level':level,'node':j,'coordinate':'t' if axis==0 else 's','AD':repr(float(gad[i])),'MP_fd_1':fmt(fd[0]),'MP_fd_2':fmt(fd[1])})
     gradienterr=max(errors);steperr=max(step_errors);check(label+'/new_gradient_AD',gradienterr,CFG['gradient_agreement_tolerance']);check(label+'/new_gradient_steps',steperr,CFG['gradient_steps_tolerance'])
   gf=np.array([float(a) for a in gm]);raw=np.asarray(hessian(obj.value)(x),float);H=(raw+raw.T)/2;M=mass(weights);np.linalg.cholesky(M);small=np.linalg.norm(gf)<=float(CFG['gradient_floor']);B=xmod.basis(gf,small);Hr=B.T@H@B;Mr=B.T@M@B;Hr=(Hr+Hr.T)/2;Mr=(Mr+Mr.T)/2;full=eigvalsh(H,M);ev,evec=eigh(Hr,Mr);mu=float(ev[0]);scale=max(1,float(np.linalg.norm(H,ord=np.inf)),abs(mu)*float(np.linalg.norm(M,ord=np.inf)));v=xmod.canonical(B@evec[:,0]);v/=np.sqrt(float(v@M@v));tau=CFG['spectral_relative_floor']*max(1,float(np.max(abs(ev))))
   check(label+'/symmetry',float(np.max(abs(raw-raw.T)))/scale,CFG['eigen_tolerance']);check(label+'/basis',float(np.max(abs(B.T@B-np.eye(B.shape[1])))),CFG['basis_tolerance'])
   if not small:check(label+'/basis_gradient',float(np.max(abs((gf/np.linalg.norm(gf))@B))),CFG['basis_tolerance'])
   interlace=float(np.max(abs(ev-full))) if small else max(0,float(np.max(full[:-1]-ev)),float(np.max(ev-full[1:])));check(label+'/interlacing',interlace/max(1,float(np.max(abs(full)))),CFG['eigen_tolerance']);res=H@v-mu*(M@v);res=res if small else res-gf*float(gf@res)/float(gf@gf);check(label+'/eigen_residual',float(np.max(abs(res)))/scale,CFG['eigen_tolerance'])
   for j,value in enumerate(ev):spectra.append({'path':name,'level':level,'index':j,'eigenvalue':repr(float(value)),'threshold':repr(tau),'mode_class':'NEGATIVE' if value< -tau else ('NEAR_ZERO' if abs(value)<=tau else 'POSITIVE')})
   if level=='fine':
    oldH,oldM,oldg,oldmu=saved['coarse'];check(label+'/mass_pullback',float(np.max(abs(S.T@M@S-oldM))),CFG['basis_tolerance']);check(label+'/gradient_pullback',float(np.max(abs(S.T@gf-oldg))),CFG['gradient_agreement_tolerance']);check(label+'/hessian_pullback',float(np.max(abs(S.T@H@S-oldH)))/max(1,float(np.max(abs(oldH)))),CFG['pullback_tolerance']);check(label+'/minimum_order',max(0,mu-oldmu)/max(1,abs(mu),abs(oldmu)),CFG['minimum_order_tolerance'])
   direction_by_precision={};measurements={}
   for digits in CFG['precision']:
    with mp.workdps(digits):
     q=[mp.mpf(float(a)) for a in v];gg=[mp.mpf(a) for a in gm]
     if not small:
      coefficient=dot(gg,q)/dot(gg,gg);q=[a-coefficient*b for a,b in zip(q,gg)]
     qnorm=mp.sqrt(dot(q,q))
     if qnorm<=mp.mpf('1e-8'):raise ValueError('DEGENERATE: direction not substituted')
     maxnode=max(mp.sqrt(q[2*j]**2+q[2*j+1]**2) for j in range(m-1));q=[a/maxnode for a in q];jmax=max(range(len(q)),key=lambda j:abs(q[j]))
     if q[jmax]<0:q=[-a for a in q]
     direction_by_precision[digits]=q;massnorm=mass_quad(q,weights);orth=abs(dot(gg,q))/max(1,mp.sqrt(dot(gg,gg)));check(label+'/'+str(digits)+'/constraint',orth,CFG['mp_constraint_tolerance']);a,b,ux,uy=prepared[digits][kind];vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);dp=[q[2*j]*vv+q[2*j+1]*nn for j in range(m-1)];der=[];cur=[]
     for step in CFG['audit_steps']:
      h=mp.mpf(step);plus=[pts[digits][0]]+[p+h*dq for p,dq in zip(pts[digits][1:-1],dp)]+[pts[digits][-1]];minus=[pts[digits][0]]+[p-h*dq for p,dq in zip(pts[digits][1:-1],dp)]+[pts[digits][-1]];lp=k.reference(plus,kind,ux,uy);lm=k.reference(minus,kind,ux,uy);calls+=2;der.append((lp-lm)/(2*h));cur.append((lp+lm-2*baseL[digits])/(h*h*massnorm))
     slope_error=abs(der[-1])/max(1,abs(baseL[digits]));ray_error=rel(mp.mpf(mu),cur[-1]);check(label+'/'+str(digits)+'/slope',slope_error,CFG['slope_tolerance']);check(label+'/'+str(digits)+'/slope_steps',rel(*der),CFG['slope_steps_tolerance']);check(label+'/'+str(digits)+'/rayleigh',ray_error,CFG['rayleigh_tolerance']);check(label+'/'+str(digits)+'/rayleigh_steps',rel(*cur),CFG['rayleigh_steps_tolerance']);measurements[digits]=(der[-1],cur[-1]);dh=hashlib.sha256(json.dumps([fmt(a) for a in q],separators=(',',':')).encode()).hexdigest();audits.append({'path':name,'level':level,'precision':digits,'vector_sha256':dh,'nodal_max':'1','mass_norm_squared':fmt(massnorm),'archive_slope':fmt(dot(gg,q)),'derivative_1':fmt(der[0]),'derivative_2':fmt(der[1]),'mass_rayleigh_1':fmt(cur[0]),'mass_rayleigh_2':fmt(cur[1]),'rayleigh_error':fmt(ray_error),'constraint_error':fmt(orth)})
   with mp.workdps(120):
    check(label+'/direction_precision',max(abs(a-b) for a,b in zip(direction_by_precision[80],direction_by_precision[120])),CFG['precision_tolerance']);check(label+'/slope_precision',rel(measurements[80][0],measurements[120][0]),CFG['precision_tolerance']);check(label+'/rayleigh_precision',rel(measurements[80][1],measurements[120][1]),CFG['precision_tolerance']);witness=measurements[120][1]< -mp.mpf(CFG['witness_tolerance'])*max(1,abs(mp.mpf(mu)))
   good=all(r['status']=='PASS' for r in checks[cs:]);paths.append({'path':name,'level':level,'lineage':source['lineage'],'segments':m,'dimension':len(gf),'restricted_dimension':len(ev),'route':'SMALL_GRADIENT' if small else 'GRADIENT_RESTRICTED','diagnostics':'PASS' if good else 'INCONCLUSIVE','minimum_status':'UNKNOWN','gradient_norm':repr(float(np.linalg.norm(gf))),'minimum_mass':repr(mu),'threshold':repr(tau),'negative_modes':int(np.sum(ev< -tau)),'near_zero_modes':int(np.sum(abs(ev)<=tau)),'negative_MP_witness':bool(good and witness),'gradient_AD_error':fmt(gradienterr),'gradient_step_error':fmt(steperr)});costs.append({'path':name,'level':level,'AD_hessian_calls':1,'MP_global_length_calls':calls,'MP_local_gradient_calls':gradientcalls,'dense_arrays_archived':0});saved[level]=(H,M,gf,mu);timings.append({'path':name,'level':level,'seconds':time.monotonic()-begin});checkpoint();print(paths[-1],flush=True)
  coarse=next(r for r in paths if r['path']==name and r['level']=='coarse');fine=paths[-1];historic=next(r for r in xp if r['path']==name);comparisons.append({'path':name,'coarse_segments':m0,'fine_segments':2*m0,'coarse_minimum_mass':coarse['minimum_mass'],'fine_minimum_mass':fine['minimum_mass'],'difference':repr(float(fine['minimum_mass'])-float(coarse['minimum_mass'])),'coarse_witness':coarse['negative_MP_witness'],'fine_witness':fine['negative_MP_witness'],'X_minimum_Euclidean':historic['restricted_min'],'comparable_to_X_numbers':False,'diagnostics':'PASS' if coarse['diagnostics']==fine['diagnostics']=='PASS' else 'INCONCLUSIVE'});checkpoint()
 dump(out/'provenance.json',{'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__});dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'PASS' if len(paths)==24 and all(r['diagnostics']=='PASS' for r in paths) and all(r['status']=='PASS' for r in checks) else 'INCONCLUSIVE','sources':len(sources),'meshes':len(paths),'fine_gradients':len(gradients),'audits':len(audits),'spectral_rows':len(spectra),'comparisons':len(comparisons),'checks':len(checks),'passed_checks':sum(r['status']=='PASS' for r in checks),'negative_MP_witnesses':sum(r['negative_MP_witness'] for r in paths),'minimum_certificates':0});checkpoint();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(p.parse_args().out)
