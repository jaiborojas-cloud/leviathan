import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,mpmath as mp,json,zipfile,pickle,io,sys
from pathlib import Path
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path('Windows_RIPG_T2A_CP90/source').resolve()))
from geometry import Geometry
O=Path('boundary139');z=zipfile.ZipFile('upload/RIPG_RESULTADOS_PC.zip');ix=json.loads(z.read('output/index.json'));states={}
for rec in ix['segments']:
 if rec['last_step'] in [130,139]:
  d=pickle.loads(zipfile.ZipFile(io.BytesIO(z.read('output/'+rec['file']))).read('replay.pkl'));states[rec['last_step']]=d['solver']
with np.load('Windows_RIPG_T2A_CP90/data/state.npz') as d:M=d['M'];f=d['f']
g=Geometry(M,f)
mp.mp.dps=100
F=mp.matrix(f.tolist());AA=mp.matrix([[F[k,j]-F[13,j] for j in range(2)] for k in [6,20]])
CC=mp.matrix([[F[k,j]-F[13,j] for j in range(2)] for k in range(len(f))])*AA**-1
C=np.array(CC.tolist(),float);C[6]=[1,0];C[13]=[0,0];C[20]=[0,1];A=np.array(AA.tolist(),float)
alpha,beta=C.T
others=[i for i in range(len(f)) if i not in [6,13,20]]
assert min(beta[others])>2

def jet(a,b):
 assert b>=0,b
 t=np.zeros(27);dt=np.zeros((27,2));ht=np.zeros((27,2,2));t[13]=1;t[6]=np.exp(a);dt[6,0]=t[6];ht[6,0,0]=t[6];t[20]=b;dt[20,1]=1
 if b>0:
  for k in others:
   al,be=C[k];tk=np.exp(al*a+be*np.log(b));t[k]=tk;dt[k]=[al*tk,be*np.exp(al*a+(be-1)*np.log(b))];ht[k]=[[al*al*tk,al*dt[k,1]],[al*dt[k,1],be*(be-1)*np.exp(al*a+(be-2)*np.log(b))]]
 S=t.sum();ds=dt.sum(0);hs=ht.sum(0);w=t/S;J=dt/S-t[:,None]*ds/S**2
 H=ht/S-(dt[:,:,None]*ds[None,None,:]+dt[:,None,:]*ds[None,:,None]+t[:,None,None]*hs)/S**2+2*t[:,None,None]*ds[None,:,None]*ds[None,None,:]/S**3
 G=J.T@M@J
 return w,J,H,G

def acc(a,b,V):
 w,J,H,G=jet(a,b);return -np.linalg.solve(G,J.T@M@np.einsum('nij,i,j->n',H,V,V))

def initial(step,i):
 ss=states[step];p,v=ss['y'].reshape(2,-1,2);pp,vv=p[i],v[i];a,logb=A@pp;b=np.exp(logb);V=np.array([A[0]@vv,b*(A[1]@vv)]);return float(ss['t']),a,b,V,pp,vv

def rhs(b,y):
 a,r,va,vb=y;aa=acc(a,b,np.array([va,vb]));return [va/vb,1/vb,aa[0]/vb,aa[1]/vb]
results=[];overlap=[]
for i in [1775,1776]:
 for step in [130,139]:
  r,a,b,V,P,v=initial(step,i);w,J,H,G=jet(a,b);oldJ=g.jac(P)[0];T=np.vstack([A[0],b*A[1]])
  overlap.append(dict(ray=i,step=step,jacobian_relative=float(np.linalg.norm(J@T-oldJ)/np.linalg.norm(oldJ)),metric_chart_condition=float(np.linalg.cond(G)),speed2=float(V@G@V),a=float(a),b=float(b),V=V.tolist(),other_weight=float(w[others].sum())))
  for factor in [1,.01]:
   sol=solve_ivp(rhs,(b,0),[a,r,*V],method='DOP853',rtol=2e-10*factor,atol=2e-12*factor,dense_output=True)
   assert sol.success
   ae,re,vae,vbe=sol.y[:,-1];ww,JJ,HH,GG=jet(ae,0);Vb=np.array([vae,vbe]);wdot=J@V;linear_r=r-w[20]/wdot[20]
   results.append(dict(ray=i,start_step=step,tolerance_factor=factor,boundary_r=float(re),boundary_a=float(ae),boundary_va=float(vae),boundary_vb=float(vbe),boundary_weights={str(k):float(ww[k]) for k in [6,13,20]},boundary_metric_eigenvalues=np.linalg.eigvalsh(GG).tolist(),boundary_metric_condition=float(np.linalg.cond(GG)),boundary_speed2=float(Vb@GG@Vb),nfev=sol.nfev,linear_boundary_r=float(linear_r),success=sol.success))
   if step==130 and factor==1:
    r139,a139,b139,V139,_,_=initial(139,i);match=sol.sol(b139);overlap[-1].update(match139_r_error=float(match[1]-r139),match139_a_error=float(match[0]-a139),match139_velocity_relative=float(np.max(abs(match[2:]-V139)/np.maximum(abs(V139),1e-30))))
   print(results[-1],flush=True)
(O/'results.json').write_text(json.dumps({'chart_matrix':A.tolist(),'coefficients':C.tolist(),'min_other_beta':float(min(beta[others])),'M_eigenvalues':np.linalg.eigvalsh(M).tolist(),'overlap':overlap,'boundary':results},indent=2))
