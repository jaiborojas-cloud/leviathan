"""Entradas inmutables E16 y guarda AF; no acceso a datos T2."""
import sys,os,time,json,csv,hashlib,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
sys.path.insert(0,str(ROOT.parent/'AG/scripts'))
import ag_common_v1 as ag
import numerics_v1 as agnum
import numpy as np
import mpmath as mp
from scipy.special import softmax,logsumexp
from scipy.spatial import ConvexHull
from numpy.polynomial.legendre import leggauss
CFG=json.loads((ROOT/'config.json').read_text());sha=ag.sha;write=ag.write;table=ag.table;rows=ag.rows

def geometry():
 for key in ['geometry','audit']:assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256']
 return ag.geometry()

def inputs():
 assert sha(REPO/CFG['inputs_path'])==CFG['inputs_sha256']
 answer=json.loads((REPO/CFG['inputs_path']).read_text());assert len(answer)==80
 return answer

class Family:
 def __init__(self,M,f,rho0,B=None):
  self.original_M=np.asarray(M);self.original_f=np.asarray(f);self.rho0=rho0
  if B is None:
   pairs=[(i,j,abs(np.linalg.det(np.array([f[i]-f[0],f[j]-f[0]])))) for i in range(1,len(f)) for j in range(i+1,len(f))];maximum=max(x[2] for x in pairs);i,j=next((i,j) for i,j,v in pairs if v>=maximum*(1-1e-12));B=np.array([f[i]-f[0],f[j]-f[0]])
  self.B=np.asarray(B);self.Binv=np.linalg.inv(self.B)
  unique,index,inverse,counts=np.unique(f,axis=0,return_index=True,return_inverse=True,return_counts=True)
  self.index=index;self.counts=counts;self.inverse=inverse;E=np.eye(len(unique))[inverse]/counts[inverse,None];self.E=E
  self.M=E.T@M@E;self.f=unique@self.Binv;self.c=np.log(counts);self.lam=float(np.linalg.eigvalsh(self.M)[-1])*(1+1e-12)
  hull=ConvexHull(self.f);self.edges=[]
  for normal in hull.equations[:,:2]:
   theta=float(np.arctan2(normal[1],normal[0])%(2*np.pi));z=self.f@np.array([np.cos(theta),np.sin(theta)]);support=np.flatnonzero(max(z)-z<1e-11*max(1,np.ptp(z)));self.edges.append((theta,support))
  self.edges.sort(key=lambda e:e[0])
 def parameters(self,q,theta,support=None):
  q=np.asarray(q);v=np.array([np.cos(theta),np.sin(theta)]);z=self.f@v
  if support is None:support=np.array([int(np.argmax(z))])
  else:support=np.asarray(support,dtype=int)
  top=float(np.max(z[support]));z=z-top;z[support]=0.
  if np.max(z)>1e-10:raise ValueError('SUPPORT_NOT_DOMINANT')
  b=self.c+self.f@q;outside=np.array([i for i in range(len(z)) if i not in support],dtype=int)
  gaps=-z[outside]
  if len(gaps)==0 or np.min(gaps)<=0:raise ValueError('INVALID_DIRECTION_GAPS')
  logZ=logsumexp(b[support]);tol=CFG['tail_bound_relative']*self.rho0
  U=float(max(0.,np.max((b[outside]-logZ+np.log(2*np.sqrt(self.lam)*len(outside)/tol))/gaps)))
  cuts=[0.,U]
  for j,gap in zip(outside,gaps):
   center=(b[j]-logZ)/gap
   for x in [1/gap,8/gap,32/gap,center,center-4/gap,center+4/gap,center-12/gap,center+12/gap]:
    if 0<x<U:cuts.append(float(x))
  cuts=np.array(sorted(set(cuts)));tail=float(2*np.sqrt(self.lam)*np.sum(np.exp(b[outside]-logZ-gaps*U)))
  return b,z,support,cuts,tail
 def speed(self,logits,z):
  a=softmax(logits,axis=-1);beta=a*(z-np.sum(a*z,axis=-1)[...,None]);value=np.einsum('...i,ij,...j->...',beta,self.M,beta,optimize=True)
  if np.min(value)<-1e-25:raise FloatingPointError('NEGATIVE_SPEED')
  return np.sqrt(np.maximum(0,value))
 def fast(self,q,theta,support=None):
  b,z,support,cuts,tail=self.parameters(q,theta,support);x=b-self.c;t,w=GL[32];t=(t+1)/2;segment=float(np.sum(w/2*self.speed(self.c+t[:,None]*x,x)))
  t,w=GL[8];width=np.diff(cuts);s=cuts[:-1,None]+width[:,None]*(t+1)/2;values=self.speed(b+s.reshape(-1,1)*z,z).reshape(len(width),8);ray=float(np.sum(width/2*(values@w)))
  return segment+ray+tail
 def validate(self,q,theta,support=None):
  from scipy.integrate import quad
  import warnings
  b,z,support,cuts,tail=self.parameters(q,theta,support);x=b-self.c;eps=CFG['quad_epsabs_relative']*self.rho0;messages=[]
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always');segment,se=quad(lambda t:float(self.speed(self.c+t*x,x)),0,1,epsabs=eps,epsrel=1e-10,limit=200);ray=re=0.
   for lo,hi in zip(cuts[:-1],cuts[1:]):
    val,err=quad(lambda t:float(self.speed(b+(lo+t*(hi-lo))*z,z))*(hi-lo),0,1,epsabs=eps/max(1,len(cuts)),epsrel=1e-10,limit=100);ray+=val;re+=err
   messages=[str(w.message) for w in caught]
  value=float(segment+ray+tail);return {'length':value,'segment':float(segment),'ray_to_U':float(ray),'tail_bound':tail,'U':float(cuts[-1]),'quad_error':float(se+re),'warnings':' | '.join(messages),'support':support.tolist(),'endpoint_group':softmax(b[support]).tolist(),'cuts':cuts.tolist()}

GL={n:leggauss(n) for n in [8,32]}
MPGL={}
def mpgl(n):
 if n not in MPGL:
  with mp.workdps(80):
   starts=leggauss(n)[0];nodes=[];weights=[]
   for start in starts:
    x=mp.mpf(float(start))
    for _ in range(8):
     p0=mp.mpf(1);p1=x
     for k in range(2,n+1):p0,p1=p1,((2*k-1)*x*p1-(k-1)*p0)/k
     derivative=n*(x*p1-p0)/(x*x-1);delta=p1/derivative;x-=delta
     if abs(delta)<mp.mpf('1e-75'):break
    p0=mp.mpf(1);p1=x
    for k in range(2,n+1):p0,p1=p1,((2*k-1)*x*p1-(k-1)*p0)/k
    derivative=n*(x*p1-p0)/(x*x-1);nodes.append(x);weights.append(2/((1-x*x)*derivative**2))
   MPGL[n]=(nodes,weights)
 return MPGL[n]

class MPFamily:
 def __init__(self,family):
  self.family=family
  with mp.workdps(80):
   n=len(family.original_M);m=len(family.index);E=mp.matrix([[mp.mpf(1)/int(family.counts[j]) if family.inverse[i]==j else 0 for j in range(m)] for i in range(n)]);MM=mp.matrix([[mp.mpf(float(x)) for x in row] for row in family.original_M]);self.M=E.T*MM*E;self.f=mp.matrix([[mp.mpf(float(x)) for x in family.original_f[i]] for i in family.index]);self.c=[mp.log(int(n)) for n in family.counts]
 def validate(self,q,theta,support,quad_result,budget=lambda:None):
  F=self.family
  with mp.workdps(80):
   Q=F.Binv@np.asarray(q);u=F.Binv@np.array([np.cos(theta),np.sin(theta)]);Q=mp.matrix([mp.mpf(float(x)) for x in Q]);u=mp.matrix([mp.mpf(float(x)) for x in u]);
   if len(support)>1:
    i,j=support[:2];delta=[self.f[j,k]-self.f[i,k] for k in range(2)];normal=mp.matrix([delta[1],-delta[0]])
    if (normal.T*u)[0]<0:normal=-normal
    BB=mp.matrix([[mp.mpf(float(x)) for x in row] for row in F.B]);vv=BB*normal;u=normal/mp.sqrt((vv.T*vv)[0])
   x=list(self.f*Q);zz=list(self.f*u);top=max(zz[i] for i in support);z=[mp.mpf(0) if i in support else zz[i]-top for i in range(len(zz))];b=[a+c for a,c in zip(self.c,x)]
   def speed(offset,zdir):
    top=max(offset);a=[mp.exp(v-top) for v in offset];den=sum(a);a=[v/den for v in a];mean=mp.fdot(a,zdir);beta=mp.matrix([v*(d-mean) for v,d in zip(a,zdir)]);return mp.sqrt((beta.T*self.M*beta)[0])
   def integ(fn,lo,hi,order):
    ts,ws=mpgl(order);mid=(lo+hi)/2;half=(hi-lo)/2;return half*mp.fsum(w*fn(mid+half*t) for t,w in zip(ts,ws))
   results=[]
   for seg_order,ray_order in [(64,16),(128,32)]:
    segment=integ(lambda t:speed([c+t*v for c,v in zip(self.c,x)],x),mp.mpf(0),mp.mpf(1),seg_order);ray=mp.mpf(0)
    for a,d in zip(quad_result['cuts'][:-1],quad_result['cuts'][1:]):
     budget();lo,hi=mp.mpf(float(a)),mp.mpf(float(d));ray+=integ(lambda s:speed([v+s*w for v,w in zip(b,z)],z),lo,hi,ray_order)
    outside=[i for i in range(len(z)) if i not in support];U=mp.mpf(quad_result['U']);logZ=mp.log(sum(mp.exp(b[i]) for i in support));tail=2*mp.sqrt(mp.mpf(F.lam))*sum(mp.exp(b[i]-logZ+z[i]*U) for i in outside);results.append(segment+ray+tail)
   error=float(max(abs(results[1]-results[0]),abs(results[1]-mp.mpf(quad_result['length'])))/results[1]);return {'MP_low':mp.nstr(results[0],80),'MP_high':mp.nstr(results[1],80),'MP_relative_error':error,'MP_status':'PASS' if error<=1e-7 else 'INCONCLUSIVE'}
