import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,time,json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path('Windows_RIPG_T2A_CP90/source').resolve()))
from geometry import Geometry
from fast_mpfr_acceleration import FastMPFRAcceleration
# Import only definitions; no rerun of prior diagnostics.
text=Path('boundary139/analyze.py').read_text();exec(text[:text.index('results=[];overlap=[]')])
OUT=Path('limit139');original=FastMPFRAcceleration(g);L=np.linalg.cholesky(g.jet(np.zeros((1,2)))[0][0]);records=[]
if (OUT/'angular_results.json').exists():records=json.loads((OUT/'angular_results.json').read_text())
def compute(j,factor=1,bits=169):
 import gmpy2 as gp
 E=FastMPFRAcceleration(g);E.context=gp.context(precision=bits,round=gp.RoundToNearest)
 theta=j*2*np.pi/2048;vel=np.linalg.solve(L.T,np.array([np.cos(theta),np.sin(theta)]));start=time.perf_counter();s=solve_ivp(E.single_rhs,(0,.07),np.r_[0.,0.,vel],method='DOP853',rtol=2e-10*factor,atol=2e-12*factor)
 assert s.success
 P,v=s.y[:,-1].reshape(2,2);a,logb=A@P;b=np.exp(logb);V=np.array([A[0]@v,b*(A[1]@v)]);assert V[1]<0
 sb=solve_ivp(rhs,(b,0),[a,.07,*V],method='DOP853',rtol=2e-10*factor,atol=2e-12*factor);assert sb.success
 aa,rr,va,vb=sb.y[:,-1];w,J,H,G=jet(aa,0)
 return dict(ray_units=j,theta=theta,factor=factor,bits=bits,boundary_r=float(rr),a=float(aa),normal_velocity=float(vb),speed_squared=float(np.array([va,vb])@G@np.array([va,vb])),nfev_origin=s.nfev,nfev_chart=sb.nfev,wall=time.perf_counter()-start)
for j in np.linspace(1773,1778,41):
 if any(x['ray_units']==j and x['factor']==1 for x in records):continue
 rec=compute(float(j));records.append(rec);(OUT/'angular_results.json').write_text(json.dumps(records,indent=2));print(j,rec['boundary_r'],rec['wall'],flush=True)
best=min(records,key=lambda x:x['boundary_r']);checks=[]
for j in sorted(set([1775.,1776.,best['ray_units']])):
 rec=compute(j,.01,266);checks.append(rec);(OUT/'origin_precision_checks.json').write_text(json.dumps(checks,indent=2));print('REFINED',rec,flush=True)
print('MINIMUM',best,flush=True)
