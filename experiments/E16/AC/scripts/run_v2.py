#!/usr/bin/env python3
"""AC v2: shooting continuo, Gauss analítica y Jacobi normal; sin reauditar AB."""
import sys
sys.dont_write_bytecode=True
import csv,json,hashlib,time,platform,resource,importlib.util,argparse
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];CFG=json.loads((ROOT/'config_v2.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location('source_d_ac',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def table(p,rs):
 if rs:
  with p.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def rows(p):return list(csv.DictReader(p.open()))
class Metric:
 def __init__(self,kind,ux=None,uy=None):
  self.kind=kind
  if ux is not None:self.A=ux@ux.T;self.B=ux@uy.T+uy@ux.T;self.C=uy@uy.T
 def tensors(self,p):
  x,y=p;dtype=object if isinstance(x,mp.mpf) else float;g=np.zeros((2,2),dtype=dtype);d=np.zeros((2,2,2),dtype=dtype);dd=np.zeros((2,2,2,2),dtype=dtype)
  if self.kind in ['sum','quadratic']:
   if self.kind=='sum':g=self.A
   else:
    g=x*x*self.A+x*y*self.B+y*y*self.C;d[0]=2*x*self.A+y*self.B;d[1]=x*self.B+2*y*self.C;dd[0,0]=2*self.A;dd[0,1]=dd[1,0]=self.B;dd[1,1]=2*self.C
  elif self.kind=='sphere':
   cos=mp.cos if dtype==object else np.cos;sin=mp.sin if dtype==object else np.sin
   g[0,0]=1;g[1,1]=cos(x)**2;d[0,1,1]=-sin(2*x);dd[0,0,1,1]=-2*cos(2*x)
  elif self.kind=='hyperbolic':
   exp=mp.exp if dtype==object else np.exp;g[0,0]=1;g[1,1]=exp(2*x);d[0,1,1]=2*g[1,1];dd[0,0,1,1]=4*g[1,1]
  return g,d,dd
 def geometry(self,p):
  g,d,dd=self.tensors(p);det=g[0,0]*g[1,1]-g[0,1]*g[1,0]
  if g[0,0]<=0 or det<=0:raise ValueError('non_SPD')
  inv=np.array([[g[1,1],-g[0,1]],[-g[1,0],g[0,0]]])/det
  C=np.array([[[(d[b,a,c]+d[c,a,b]-d[a,b,c])/2 for c in range(2)] for b in range(2)] for a in range(2)])
  G=(inv@C.reshape(2,4)).reshape(2,2,2)
  R=dd[0,1,0,1]-(dd[1,1,0,0]+dd[0,0,1,1])/2+C[:,0,1]@inv@C[:,0,1]-C[:,0,0]@inv@C[:,1,1]
  return g,G,R/det

def integrate(metric,a,v,rtol,jacobi=True):
 L=float(np.sqrt(v@metric.geometry(a)[0]@v))
 def rhs(t,z):
  _,G,K=metric.geometry(z[:2]);acc=-np.einsum('ijk,j,k->i',G,z[2:4],z[2:4]);return np.r_[z[2:4],acc,z[5],-L*L*K*z[4]]
 def event(t,z):return z[4]
 sol=solve_ivp(rhs,(0,1),np.r_[a,v,0.,L],method='DOP853',rtol=rtol,atol=rtol*CFG['atol_factor'],max_step=CFG['max_step'],dense_output=True,events=event)
 if not sol.success:raise ValueError(sol.message)
 return sol,L

def roots(sol,L):return [float(t*L) for t in sol.t_events[0] if CFG['zero_margin']<t<1-CFG['zero_margin']]
def mp_jacobi(metric,sol,L,digits,n):
 with mp.workdps(digits):
  ll=mp.mpf(L);h=ll/n;ks=[metric.geometry(np.array([mp.mpf(float(x)) for x in sol.sol(i/n)[:2]],dtype=object))[2] for i in range(n+1)];j=mp.mpf(0);v=mp.mpf(1);zeros=[];profile=[]
  for i in range(n):
   k0,k1=ks[i:i+2];km=(k0+k1)/2;a=v;b=-k0*j;c=v+h*b/2;d=-km*(j+h*a/2);e=v+h*d/2;f=-km*(j+h*c/2);g=v+h*f;hh=-k1*(j+h*e);jn=j+h*(a+2*c+2*e+g)/6;vn=v+h*(b+2*d+2*f+hh)/6
   if i and j*jn<0:zeros.append(float((mp.mpf(i)+abs(j)/(abs(j)+abs(jn)))*h))
   j,v=jn,vn;profile.append({'node':i+1,'s':float((i+1)*h),'K':mp.nstr(k1,50),'j':mp.nstr(j,50)})
  return float(j),zeros,profile

def point_segments(points,poly):
 best=np.full(len(points),np.inf)
 for a,b in zip(poly[:-1],poly[1:]):
  v=b-a;vv=float(v@v);u=np.clip((points-a)@v/vv,0,1) if vv else np.zeros(len(points));best=np.minimum(best,np.linalg.norm(points-a-u[:,None]*v,axis=1))
 return float(max(best))

def main(out):
 if out.exists():raise FileExistsError('No sobrescribir resultados; use versión/directorio nuevo')
 out.mkdir(parents=True);start=time.monotonic();r=ROOT.parent
 for p,h in CFG['sources'].items():assert sha(r/p)==h,p
 data=json.loads((r/'H/data.json').read_text());d=load(r/'D/scripts/run.py');prepared={}
 for digits in [50,80]:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states']['h00']];inputs=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels']['P0']];cv,jc,_,chol=d.analytic_mp(theta,inputs);prepared[digits]={}
   for kind in ['sum','quadratic']:
    ux=d.analytic_B(cv,jc,[1,0],kind)[0]*chol;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*chol;prepared[digits][kind]=Metric(kind,np.array(ux.tolist(),object),np.array(uy.tolist(),object))
 metrics={}
 with mp.workdps(80):
  for kind in ['sum','quadratic']:
   ux=d.analytic_B(cv,jc,[1,0],kind)[0]*chol;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*chol;prepared_metric=Metric(kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float));metrics[kind]=prepared_metric
 # Recompute float coefficients from MP80 metric coefficients, not mixed precision state.
 for kind in metrics:
  for key in ['A','B','C']:setattr(metrics[kind],key,np.array(getattr(prepared[80][kind],key),float))
 shooting=[];controls=[];paths=[];attempts=[];curvature=[];mp_profiles=[];profiles=[];events=[]
 def save():
  for name,rs in [('shooting',shooting),('controls',controls),('paths',paths),('attempts',attempts),('curvature',curvature),('mp_profiles',mp_profiles),('profiles',profiles),('events',events)]:table(out/(name+'.csv'),rs)
  if not events:
   with (out/'events.csv').open('w') as f:csv.writer(f).writerow(['path','s','fraction'])
  write(out/'resources.json',{'seconds':time.monotonic()-start,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})
 def check_control(name,kind,L,index):
  try:
   m=Metric(kind);a=np.array([0.,0.]);v=np.array([0.,L]) if kind=='sphere' else np.array([L,0.]);sol,ll=integrate(m,a,v,1e-12);zz=roots(sol,ll);expected=np.sin(L) if kind=='sphere' else np.sinh(L);err=abs(sol.y[4,-1]-expected)/max(1,abs(expected));K=float(m.geometry(a)[2]);ok=len(zz)==index and err<1e-8 and abs(K-(1 if kind=='sphere' else -1))<1e-10 and (not index or abs(zz[0]-np.pi)<1e-8)
   # Independent high precision Jacobi contrast for positive and negative curvature.
   jmp,zmp,_=mp_jacobi(m,sol,ll,80,CFG['control_mp_nodes']);mp_error=abs(jmp-expected)/max(1,abs(expected));ok=ok and len(zmp)==index and mp_error<1e-8 and (not index or abs(zmp[0]-np.pi)<1e-8)
   controls.append({'control':name,'status':'PASS' if ok else 'FAIL','K':K,'index':len(zz),'zero':zz[0] if zz else '', 'error':err,'MP_error':mp_error,'reason':''})
  except Exception as e:controls.append({'control':name,'status':'FAIL','K':'','index':'','zero':'','error':'','MP_error':'','reason':str(e)})
 for name,kind,L,idx in [('sphere_short','sphere',.75*np.pi,0),('sphere_long','sphere',1.5*np.pi,1),('hyperbolic_1','hyperbolic',1.,0),('hyperbolic_10','hyperbolic',10.,0)]:check_control(name,kind,L,idx)
 source=rows(r/'AB/results/run_v1/paths.csv');vertices=rows(r/'AB/results/run_v1/vertices.csv');A=np.array(data['perspectives'][0],float);B=np.array(data['perspectives'][1],float);delta=B-A;normal=np.array([-delta[1],delta[0]]);scale=max(1,np.linalg.norm(delta))
 for old in source:
  name=old['path'];kind='sum' if old['lineage']=='C0' else 'quadratic';m=metrics[kind];begin=time.monotonic();row={'path':name,'source':'AB','segments':old['segments'],'source_KKT':old['final_KKT'],'source_witness':old['negative_MP_witness'],'shooting_OK':False,'L':'','conjugates':'UNKNOWN','normal_negative_discrete':'UNKNOWN','witness_tangency':'UNKNOWN','hausdorff':'','hausdorff_geo_poly':'','hausdorff_poly_geo':'','speed_drift':'','length_difference':'','stable':False,'status':'INCONCLUSIVE','reason':''}
  try:
   if time.monotonic()-start>CFG['budget_seconds']:raise TimeoutError('budget; remaining UNKNOWN')
   vs=sorted([v for v in vertices if v['path']==name],key=lambda v:int(v['index']));z=np.array([[float(v['t']),float(v['s'])] for v in vs]);poly=A+z[:,0,None]*delta+z[:,1,None]*normal;angle=float(np.arctan2(*(poly[1]-poly[0])[::-1]));l0=float(old['final_length']);solutions=[]
   for rt in CFG['rtols']:
    def residual(q):
     if time.monotonic()-start>CFG['budget_seconds']:raise TimeoutError('budget')
     unit=np.array([np.cos(q[0]),np.sin(q[0])]);v=np.exp(q[1])*unit/np.sqrt(unit@m.geometry(A)[0]@unit)
     try:sol,L=integrate(m,A,v,rt);res=(sol.y[:2,-1]-B)/scale
     except Exception as e:attempts.append({'path':name,'rtol':rt,'angle':float(q[0]),'L':float(np.exp(q[1])),'endpoint_error':'','status':'FAILED','reason':str(e)});raise
     attempts.append({'path':name,'rtol':rt,'angle':float(q[0]),'L':L,'endpoint_error':float(np.linalg.norm(res)),'status':'EVALUATED','reason':''});return res
    opt=least_squares(residual,[angle,np.log(l0)],bounds=([angle-CFG['angle_radius'],np.log(l0*.1)],[angle+CFG['angle_radius'],np.log(l0*4)]),jac='3-point',xtol=1e-12,gtol=1e-12,ftol=1e-12,max_nfev=CFG['shoot_max_nfev']);unit=np.array([np.cos(opt.x[0]),np.sin(opt.x[0])]);v=np.exp(opt.x[1])*unit/np.sqrt(unit@m.geometry(A)[0]@unit);sol,L=integrate(m,A,v,rt);err=np.linalg.norm(sol.y[:2,-1]-B)/scale
    shooting.append({'path':name,'rtol':rt,'success':bool(opt.success),'status':int(opt.status),'message':str(opt.message),'nfev':opt.nfev,'njev':opt.njev,'angle':float(opt.x[0]),'L':L,'endpoint_error':float(err)})
    if not opt.success or err>CFG['endpoint_tol']:raise ValueError('shooting_nonconvergence:'+str(opt.message)+':'+str(err))
    solutions.append((sol,L,roots(sol,L)))
   sol,L,zz=solutions[-1];row.update(shooting_OK=True,L=L,conjugates=len(zz));stable=len(zz)==len(solutions[0][2]) and all(abs(a-b)<=CFG['zero_stability']*L for a,b in zip(zz,solutions[0][2]));ts=np.linspace(0,1,CFG['hausdorff_samples']);dense=sol.sol(ts);hd1=point_segments(dense[:2].T,poly);hd2=point_segments(poly,dense[:2].T);hd=max(hd1,hd2);speed=max(abs(float(v@m.geometry(p)[0]@v)/(L*L)-1) for p,v in zip(dense[:2].T,dense[2:4].T));row.update(hausdorff=hd,hausdorff_geo_poly=hd1,hausdorff_poly_geo=hd2,speed_drift=speed,length_difference=L-l0)
   for t,p,j in zip(ts,dense[:2].T,dense[4]):profiles.append({'path':name,'t':float(t),'s':float(t*L),'p0':float(p[0]),'p1':float(p[1]),'j':float(j)})
   for zero in zz:events.append({'path':name,'s':zero,'fraction':zero/L})
   probes=sorted(set([0.,.25,.5,.75,1.]+[min(1,max(0,(s+dh)/L)) for s in zz for dh in [-1e-6*L,0,1e-6*L]]));mpok=True
   for t in probes:
    p=sol.sol(t)[:2];kf=float(m.geometry(p)[2]);vals=[]
    for digits in CFG['mp_digits']:
     with mp.workdps(digits):km=prepared[digits][kind].geometry(np.array([mp.mpf(float(x)) for x in p],object))[2];vals.append(km);curvature.append({'path':name,'t':t,'precision':digits,'K_float':kf,'K_MP':mp.nstr(km,50),'relative_error':float(abs(mp.mpf(kf)-km)/max(1,abs(km)))})
    with mp.workdps(80):mpok=mpok and abs(vals[0]-vals[1])/max(1,abs(vals[1]))<=mp.mpf('1e-40') and abs(mp.mpf(kf)-vals[1])/max(1,abs(vals[1]))<=mp.mpf('1e-8')
   mps=[]
   for digits,n in zip(CFG['mp_digits'],CFG['mp_nodes']):
    jend,zeros,profile=mp_jacobi(prepared[digits][kind],sol,L,digits,n);mps.append((jend,zeros))
    for q in profile:mp_profiles.append({'path':name,'precision':digits,**q})
    stable=stable and len(zeros)==len(zz) and all(abs(a-b)<=1e-5*L for a,b in zip(zeros,zz))
   stable=bool(stable and abs(mps[0][0]-mps[1][0])/max(1,abs(mps[1][0]))<=1e-5 and mpok and hd<=.01*scale and speed<=1e-7 and abs(sol.y[4,-1])>1e-8*max(1,L))
   row.update(stable=stable,status='PASS_NUMERICAL' if stable else 'INCONCLUSIVE',reason='' if stable else 'stability_MP_association_or_endpoint_ambiguity')
   if kind=='sum':controls.append({'control':name,'status':'PASS' if stable and len(zz)==0 and abs(float(m.geometry(A)[2]))<1e-10 else 'FAIL','K':float(m.geometry(A)[2]),'index':len(zz),'zero':'','error':speed,'MP_error':'','reason':''})
  except Exception as e:
   row['reason']=type(e).__name__+':'+str(e)
   if kind=='sum':controls.append({'control':name,'status':'FAIL','K':'','index':'','zero':'','error':'','MP_error':'','reason':row['reason']})
  paths.append(row);save();print(row,flush=True)
 valid=len(controls)==8 and all(c['status']=='PASS' for c in controls)
 write(out/'summary.json',{'verdict':'INCONCLUSIVE','run_valid':valid,'status':'VALID_EXPLORATORY' if valid else 'INVALID','paths':len(paths),'numerical_pass':sum(p['status']=='PASS_NUMERICAL' for p in paths),'reason':'normal blocks and witness tangency not archived for AB; no transfer from T/S','controls_pass':sum(c['status']=='PASS' for c in controls)})
 write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__,'sources':CFG['sources'],'config_sha256':sha(ROOT/'config_v2.json'),'code_sha256':sha(Path(__file__))});save()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v2');main(p.parse_args().out)
