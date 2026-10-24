#!/usr/bin/env python3
"""Nuevas discretizaciones AC: estacionarización y bloques métricos archivados."""
from common import *
import argparse,time,platform,resource
import autograd.numpy as anp
from autograd import grad,hessian
from scipy.optimize import minimize
from scipy.linalg import eigh,eigvalsh
from numpy.polynomial.legendre import leggauss

def main(out):
 if out.exists():raise FileExistsError(out)
 assert (ROOT/'results/part_a_v1/summary.csv').exists(),'A debe preceder B'
 out.mkdir(parents=True);started=time.monotonic();data,k,ac,prep=prepare();stop=load('stop_ad',E16/'S/scripts/stopping.py');A=np.array(data['perspectives'][0],float);B=np.array(data['perspectives'][1],float);delta=B-A;J=np.column_stack([delta,[-delta[1],delta[0]]]);Jinv=np.linalg.inv(J)
 records=[];checks=[];monitors=[];spectra=[];bands=[];vectors=[];audits=[];vertices=[];gradients=[];controls=[]
 tables={'paths':records,'checks':checks,'monitor':monitors,'spectra':spectra,'bands':bands,'negative_vectors':vectors,'audits':audits,'vertices':vertices,'gradients':gradients,'controls':controls}
 def check(case,name,error,tol):
  good=bool(np.isfinite(float(error)) and abs(error)<=tol);checks.append({'case':case,'check':name,'error':str(error),'tolerance':str(tol),'status':'PASS' if good else 'INCONCLUSIVE'});return good
 def save():
  for n,rs in tables.items():table(out/(n+'.csv'),rs)
  write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})
 def budget():
  if time.monotonic()-started>CFG['budget_seconds']:save();raise TimeoutError('budget')
 def store_block(case,label,H,node_dim=1):
  n=len(H);ii=np.arange(n)//node_dim;mask=abs(ii[:,None]-ii[None,:])<=1;err=float(np.max(abs(H[~mask]))) if np.any(~mask) else 0;check(case,'band_locality/'+label,err/max(1,float(np.max(abs(H)))),1e-10)
  for i,j in zip(*np.nonzero(mask)):bands.append({'case':case,'block':label,'row':int(i),'column':int(j),'value':repr(float(H[i,j])),'dimension':n,'node_dim':node_dim})
 def spectral(case,label,H):
  vals,vec=eigh((H+H.T)/2);tau=max(CFG['spectral_absolute'],CFG['spectral_relative']*float(max(abs(vals))))
  for i,x in enumerate(vals):spectra.append({'case':case,'block':label,'index':i,'eigenvalue':repr(float(x)),'threshold':tau,'negative':bool(x< -tau)})
  return vals,vec,tau
 # Instrumento esfera: integral por segmento recto en (latitud,longitud).
 for m in CFG['meshes']:
  for factor,expected in [(.75,0),(1.5,1)]:
   case=f'sphere/{factor}pi/{m}';L=factor*np.pi;n=m-1;x=np.column_stack([np.zeros(m+1),np.linspace(0,L,m+1)])[1:-1].reshape(-1)
   def objective(order):
    nodes,weights=leggauss(order);tt=(nodes+1)/2;ww=weights/2
    def val(xx):
     z=anp.concatenate([anp.array([[0.,0.]]),anp.reshape(xx,(-1,2)),anp.array([[0.,L]])]);dz=z[1:]-z[:-1];lat=z[:-1,0,None]+dz[:,0,None]*tt;v=anp.sqrt(dz[:,0,None]**2+anp.cos(lat)**2*dz[:,1,None]**2);return anp.sum(v*ww)
    return val
   h32=np.asarray(hessian(objective(32))(x),float);h64=np.asarray(hessian(objective(64))(x),float);normal=h32[::2,::2];step=L/m;expectedH=np.diag(np.full(n,2/step-2*step/3))+np.diag(np.full(n-1,-1/step-step/6),1)+np.diag(np.full(n-1,-1/step-step/6),-1);ss=len(checks);check(case,'quadrature',float(np.max(abs(h32-h64)))/max(1,float(np.max(abs(h64)))),1e-9);check(case,'normal_FEM',float(np.max(abs(normal-expectedH)))/max(1,float(np.max(abs(expectedH)))),1e-9);vals,_,tau=spectral(case,'normal',normal);negative=int(sum(vals< -tau));check(case,'normal_index',abs(negative-expected),0);store_block(case,'normal',normal);controls.append({'case':case,'status':'PASS' if all(c['status']=='PASS' for c in checks[ss:]) else 'FAIL','normal_negative':negative,'expected':expected})
 metric=float_metric(ac,prep,'quadratic');shoot=next(q for q in rows(E16/'AC/results/run_v2/shooting.csv') if q['path']=='Q0/reference/132' and float(q['rtol'])==1e-12);unit=np.array([np.cos(float(shoot['angle'])),np.sin(float(shoot['angle']))]);v=float(shoot['L'])*unit/np.sqrt(unit@metric.geometry(A)[0]@unit);geo,L=ac.integrate(metric,A,v,1e-12)
 for kind in ['quadratic','sum']:
  metric=float_metric(ac,prep,kind)
  for m in CFG['meshes']:
   n=m-1;t=np.linspace(0,1,m+1);physical=geo.sol(t)[:2].T if kind=='quadratic' else A+t[:,None]*delta;z=(physical-A)@Jinv.T;z[[0,-1]]=[[0,0],[1,0]];base=z[1:-1].reshape(-1);T0,N0,_=frame(z,J,A,metric)
   for mode in ['LIBRE','COCIENTE']:
    case=f'{kind}/{m}/{mode}';begin=time.monotonic();cs=len(checks);route='UNKNOWN';native_success='';native_status='';reason='';nit=0;result={'case':case,'kind':kind,'segments':m,'mode':mode,'first_order':'INCONCLUSIVE','route':'UNKNOWN','KKT':'','full_KKT':'','minimum_physical':'','minimum_metric':'','minimum_normal':'','minimum_admissible':'','negative_free_metric':'','negative_admissible':'','tangent_fraction_min':'UNKNOWN','tangent_fraction_max':'UNKNOWN','diagnostics':'INCONCLUSIVE','iterations':0,'native_success':'','native_status':'','reason':''}
    try:
     budget();ux,uy,_=prep[80][kind];obj=k.Objective(A,B,'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float));gfun=grad(obj.value);lower=np.tile([0.,-.25],n);upper=np.tile([1.,.25],n)
     if mode=='LIBRE':D=np.eye(2*n);y0=base.copy();offset=np.zeros(2*n);bounds=np.column_stack([lower,upper])
     else:
      D=N0;offset=base.copy();y0=np.zeros(n);bounds=[]
      for j in range(n):
       lo=-float('inf');hi=float('inf')
       for axis in range(2):
        i=2*j+axis;a0=D[i,j]
        if a0!=0:
         ends=sorted([(lower[i]-base[i])/a0,(upper[i]-base[i])/a0]);lo=max(lo,ends[0]);hi=min(hi,ends[1])
       bounds.append([lo,hi])
      bounds=np.array(bounds)
     def unpack(y):return offset+D@y
     def kkt(y,g,value,box):return float(max(abs(y-np.clip(y-g,box[:,0],box[:,1]))))/max(1,abs(float(value)))
     rule=stop.SustainedRule(CFG['monitor_interval'],CFG['streak'],CFG['KKT']);bad=0;stop_hash=''
     def full_gradient(y,save_final=False):
      xx=unpack(y);zz=np.asarray(k.coords(xx,'free',z[:,0]),float);gad=np.asarray(gfun(xx),float);gg=[];errors=[]
      with mp.workdps(80):
       ux,uy,_=prep[80][kind];aa=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][0]]);bb=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][1]]);pts=k.mp_points(aa,bb,zz);vv=bb-aa;nn=mp.matrix([-vv[1],vv[0]]);length=k.reference(pts,kind,ux,uy)
       for j in range(1,m):
        for axis,direction in enumerate([vv,nn]):
         fd=[]
         for step in CFG['gradient_steps']:
          h=mp.mpf(step);fd.append((k.reference([pts[j-1],pts[j]+h*direction,pts[j+1]],kind,ux,uy)-k.reference([pts[j-1],pts[j]-h*direction,pts[j+1]],kind,ux,uy))/(2*h))
         i=2*(j-1)+axis;gg.append(fd[-1]);errors.append(abs(fd[0]-fd[1]))
         if save_final:gradients.append({'case':case,'node':j,'axis':axis,'AD':repr(float(gad[i])),'MP1':mp.nstr(fd[0],50),'MP2':mp.nstr(fd[1],50)})
       e=max(abs(mp.mpf(float(a))-b) for a,b in zip(gad,gg))/max(1,abs(length));fe=max(errors)/max(1,abs(length));ok=check(case,'gradient_AD',e,mp.mpf(str(CFG['gradient_agreement']))) and check(case,'gradient_steps',fe,mp.mpf(CFG['gradient_steps_tolerance']))
      gf=np.array([float(q) for q in gg]);return length,kkt(y,D.T@gf,length,bounds),kkt(xx,gf,length,np.column_stack([lower,upper])),ok
     def audit(y,it,force=False):
      nonlocal bad,stop_hash
      xx=unpack(y);Lad=float(obj.value(xx));adk=kkt(y,D.T@np.asarray(gfun(xx),float),Lad,bounds);res=None;verified=False
      if not force and adk>CFG['AD_screen']:state='SCREENED_NONSTATIONARY'
      else:
       lv,res,full,verified=full_gradient(y);state='STATIONARY' if verified and res<=CFG['KKT'] else ('NONSTATIONARY' if verified else 'UNVERIFIED');bad+=not verified
      requested=rule.observe(it,verified,res if res is not None else float('inf'));digest=hashlib.sha256(np.asarray(y,float).tobytes()).hexdigest()
      if requested:stop_hash=digest
      monitors.append({'case':case,'iteration':it,'AD_KKT':adk,'MP_KKT':res if res is not None else '', 'state':state,'streak':rule.streak,'stop_requested':requested,'point_sha256':digest});save();return requested
     audit(y0,0,True)
     def callback(y):
      nonlocal nit
      nit+=1;budget()
      if nit%CFG['monitor_interval']==0 and audit(y,nit):raise StopIteration
     opt=minimize(lambda y:obj.fun(unpack(y)),y0,jac=lambda y:D.T@np.asarray(gfun(unpack(y)),float),bounds=[tuple(q) for q in bounds],method='L-BFGS-B',options={q:v for q,v in CFG['optimizer'].items() if q!='method'},callback=callback);yy=np.asarray(opt.x,float);xx=unpack(yy);zz=np.asarray(k.coords(xx,'free',z[:,0]),float);length,res,full,ok=full_gradient(yy,True);check(case,'final_KKT',res,CFG['KKT']);route='PHYSICAL_SUSTAINED' if rule.requested else ('NATIVE_VERIFIED' if opt.success else 'UNVERIFIED_TERMINATION');accepted=bool(rule.requested or opt.success);native_success=bool(opt.success);native_status=int(opt.status)
     if rule.requested:check(case,'callback_point',0 if hashlib.sha256(yy.tobytes()).hexdigest()==stop_hash and opt.status==99 else 1,0)
     first=accepted and bad==0 and all(q['status']=='PASS' for q in checks[cs:]);raw=np.asarray(hessian(obj.value)(xx),float);H=(raw+raw.T)/2;T,N,gs=frame(zz,J,A,metric);E=np.column_stack([T,N]);HM=E.T@H@E;HT=T.T@H@T;HN=N.T@H@N;HA=HM if mode=='LIBRE' else D.T@H@D;TN=T.T@H@N;sp={}
     check(case,'hessian_symmetry',float(np.max(abs(raw-raw.T)))/max(1,float(np.max(abs(raw)))),1e-9)
     for label,block,dim in [('physical',H,2),('tangent',HT,1),('normal',HN,1),('admissible',HA,1 if mode=='COCIENTE' else 0),('coupling_TN',TN,1)]:
      if label!='admissible' or mode=='COCIENTE':store_block(case,label,block,dim)
     for label,block in [('physical',H),('metric',HM),('tangent',HT),('normal',HN),('admissible',HA)]:sp[label]=spectral(case,label,block)
     def coefficients(v):
      vv=v.reshape(n,2);aa=np.array([T[2*j:2*j+2,j]@gs[j]@vv[j] for j in range(n)]);bb=np.array([N[2*j:2*j+2,j]@gs[j]@vv[j] for j in range(n)]);return aa,bb,float(aa@aa/(aa@aa+bb@bb))
     fractions=[]
     for label in ['physical','metric','normal','admissible']:
      vals,vec,tau=sp[label]
      for idx in np.flatnonzero(vals< -tau):
       v=vec[:,idx] if label=='physical' else (E@vec[:,idx] if label=='metric' or label=='admissible' and mode=='LIBRE' else (N@vec[:,idx] if label=='normal' else D@vec[:,idx]));aa,bb,fraction=coefficients(v)
       if label=='metric':fractions.append(fraction)
       for j in range(n):vectors.append({'case':case,'block':label,'mode_index':int(idx),'eigenvalue':float(vals[idx]),'threshold':tau,'tangent_fraction':fraction,'node':j+1,'t':float(v[2*j]),'s':float(v[2*j+1]),'T_coefficient':float(aa[j]),'N_coefficient':float(bb[j])})
     for label in ['metric','admissible']:
      vals,vec,tau=sp[label];v=E@vec[:,0] if label=='metric' or mode=='LIBRE' else D@vec[:,0];rr=float(v@H@v);data_mp={}
      for digits in CFG['precisions']:
       with mp.workdps(digits):
        ux,uy,_=prep[digits][kind];aa=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][0]]);bb=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][1]]);pts=k.mp_points(aa,bb,zz);vv=bb-aa;nn=mp.matrix([-vv[1],vv[0]]);dp=[mp.mpf(float(v[2*j]))*vv+mp.mpf(float(v[2*j+1]))*nn for j in range(n)];L0=k.reference(pts,kind,ux,uy);cur=[];slopes=[]
        for step in CFG['direction_steps']:
         h=mp.mpf(step);lp=k.reference([pts[0]]+[p+h*d for p,d in zip(pts[1:-1],dp)]+[pts[-1]],kind,ux,uy);lm=k.reference([pts[0]]+[p-h*d for p,d in zip(pts[1:-1],dp)]+[pts[-1]],kind,ux,uy);cur.append((lp+lm-2*L0)/h**2);slopes.append((lp-lm)/(2*h))
        check(case,label+'/MP_Rayleigh',abs(mp.mpf(rr)-cur[-1])/max(1,abs(cur[-1])),mp.mpf(str(CFG['rayleigh_tolerance'])));check(case,label+'/MP_steps',abs(cur[0]-cur[1])/max(1,abs(cur[-1])),mp.mpf(str(CFG['rayleigh_steps_tolerance'])));data_mp[digits]=cur[-1];audits.append({'case':case,'block':label,'precision':digits,'AD':rr,'MP1':mp.nstr(cur[0],70),'MP2':mp.nstr(cur[1],70),'slope':mp.nstr(slopes[-1],70)})
      with mp.workdps(120):check(case,label+'/MP_precision',abs(data_mp[80]-data_mp[120])/max(1,abs(data_mp[120])),mp.mpf('1e-30'))
     diag=all(q['status']=='PASS' for q in checks[cs:] if q['check']!='final_KKT');result.update(first_order='PASS' if first else 'INCONCLUSIVE',route=route,KKT=res,full_KKT=full,minimum_physical=float(sp['physical'][0][0]),minimum_metric=float(sp['metric'][0][0]),minimum_normal=float(sp['normal'][0][0]),minimum_admissible=float(sp['admissible'][0][0]),negative_free_metric=int(sum(sp['metric'][0]< -sp['metric'][2])),negative_admissible=int(sum(sp['admissible'][0]< -sp['admissible'][2])),tangent_fraction_min=min(fractions) if fractions else 'UNKNOWN',tangent_fraction_max=max(fractions) if fractions else 'UNKNOWN',diagnostics='PASS' if diag else 'INCONCLUSIVE',iterations=nit,native_success=native_success,native_status=native_status)
     for j,p in enumerate(zz):vertices.append({'case':case,'node':j,'t':p[0],'s':p[1]})
     if kind=='sum':
      normal_neg=int(sum(sp['normal'][0]< -sp['normal'][2]));passed=normal_neg==0 and (not fractions or min(fractions)>=CFG['tangent_fraction']) and first and diag;controls.append({'case':case,'status':'PASS' if passed else 'FAIL','normal_negative':normal_neg,'expected':0})
    except Exception as e:
     result['reason']=type(e).__name__+':'+str(e)
     if kind=='sum':controls.append({'case':case,'status':'FAIL','normal_negative':'UNKNOWN','expected':0})
    records.append(result);save();print(result,flush=True)
 valid=len(controls)==12 and all(q['status']=='PASS' for q in controls);quad=[q for q in records if q['kind']=='quadratic'];h2=valid and len(quad)==6 and all(q['first_order']=='PASS' and q['diagnostics']=='PASS' for q in quad)
 for q in quad:
  ns=[s for s in spectra if s['case']==q['case'] and s['block']=='normal' and s['negative']];h2=h2 and not ns
  h2=h2 and (q['negative_admissible']==0 if q['mode']=='COCIENTE' else q['negative_free_metric']>0 and q['tangent_fraction_min']!='UNKNOWN' and q['tangent_fraction_min']>=CFG['tangent_fraction'])
 normal_stable=valid and all(any(s['block']=='normal' and s['negative'] and s['case']==f'quadratic/{m}/LIBRE' for s in spectra) for m in CFG['meshes']);verdict='H2' if h2 else ('H1_CANDIDATE_INSTRUMENT_DEFECT' if normal_stable else 'INCONCLUSIVE')
 write(out/'summary.json',{'verdict':verdict,'status':'VALID_EXPLORATORY' if valid else 'INVALID','controls_pass':sum(q['status']=='PASS' for q in controls),'cases':len(records),'stationary':sum(q['first_order']=='PASS' for q in records),'diagnostics_pass':sum(q['diagnostics']=='PASS' for q in records),'guard':'at least one free negative per mesh required to avoid vacuous attribution'})
 write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'mpmath':mp.__version__,'sources':CFG['sources'],'code_sha256':sha(Path(__file__))});save()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/part_b_v1');main(p.parse_args().out)
