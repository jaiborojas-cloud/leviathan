"""Integración y Hessiana normal por longitud de segmentos, sin selección de ramas."""
from metric_v1 import *
import autograd.numpy as anp
from autograd import grad,hessian
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from numpy.polynomial.legendre import leggauss
MAIN=json.loads((ROOT/'config.json').read_text())

def trace(metric,center,v,length):
 def rhs(s,z):
  h,G,K=metric.geometry(z[:2])
  if np.linalg.cond(h)>MAIN['condition_limit']:raise ValueError('NUMERICAL_CONDITION_LIMIT')
  return np.r_[z[2:4],-np.einsum('ijk,j,k->i',G,z[2:4],z[2:4]),z[5],-float(K)*z[4],z[4]]
 def conjugate(s,z):return z[4]
 def boundary(s,z):return MAIN['region'][1]-max(abs(z[0]),abs(z[1]))
 boundary.terminal=True;boundary.direction=-1
 sol=solve_ivp(rhs,(0,length),np.r_[center,v,0.,1.,0.],method='DOP853',rtol=MAIN['rtol'],atol=MAIN['atol'],max_step=MAIN['max_step'],dense_output=True,events=[conjugate,boundary])
 zeros=[float(x) for x in sol.t_events[0] if x>MAIN['event_margin']];censor=bool(len(sol.t_events[1]));return sol,zeros,censor

def intersections(poly):
 n=len(poly);v=np.roll(poly,-1,axis=0)-poly
 def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for i in range(n-2):
  jj=np.arange(i+2,n)
  if i==0:jj=jj[jj!=n-1]
  if not len(jj):continue
  w=v[jj];den=cross(v[i],w);valid=abs(den)>1e-14
  if not np.any(valid):continue
  js=jj[valid];ww=w[valid];den=den[valid];d=poly[js]-poly[i];t=cross(d,ww)/den;u=cross(d,v[i])/den;good=(t>1e-9)&(t<1-1e-9)&(u>1e-9)&(u<1-1e-9)
  if np.any(good):return (i,int(js[np.flatnonzero(good)[0]]))
 return None

def mp_trace(metric,center,v,length,digits,steps,budget=lambda:None):
 with mp.workdps(digits):
  p=np.array([mp.mpf(float(x)) for x in center],object);vv=np.array([mp.mpf(float(x)) for x in v],object);vv/=mp.sqrt(vv@metric.geometry(p)[0]@vv);z=np.r_[p,vv,mp.mpf(0),mp.mpf(1),mp.mpf(0)];h=mp.mpf(length)/steps;zeros=[]
  def rhs(q):
   _,G,K=metric.geometry(q[:2]);acc=np.array([-sum(G[i,j,k]*q[2+j]*q[2+k] for j in range(2) for k in range(2)) for i in range(2)],object);return np.r_[q[2:4],acc,q[5],-K*q[4],q[4]]
  for i in range(steps):
   if i%128==0:budget()
   a=rhs(z);b=rhs(z+h*a/2);c=rhs(z+h*b/2);d=rhs(z+h*c);new=z+h*(a+2*b+2*c+d)/6
   if i and z[4]*new[4]<0:zeros.append(float((mp.mpf(i)+abs(z[4])/(abs(z[4])+abs(new[4])))*h))
   z=new
  return np.array([float(q) for q in z]),zeros

def ad_metric(metric,kind='soft'):
 if kind=='soft':
  f=anp.array(metric.f);R=anp.array(metric.R)
  def h(p):
   z=anp.dot(f,p);a=anp.exp(z-anp.max(z));a=a/anp.sum(a);mu=anp.dot(a,f);U=anp.dot(anp.transpose(f-mu),a[:,None]*R);return anp.dot(U,anp.transpose(U))
 elif kind=='sphere':
  def h(p):return anp.array([[1.,0.],[0.,anp.cos(p[0])**2]])
 elif kind=='hyperbolic':
  def h(p):return anp.array([[1.,0.],[0.,anp.exp(2*p[0])]])
 elif kind=='flat_ad':
  AA,BB,CC=[anp.array(getattr(metric,q)) for q in ['A','B','C']]
  def h(p):return p[0]**2*AA+p[0]*p[1]*BB+p[1]**2*CC
 else:raise ValueError(kind)
 return h

def normal_block(points,normals,metric,order,kind='soft',budget=lambda:None):
 nodes,weights=leggauss(order);nodes=(nodes+1)/2;weights=weights/2;geth=ad_metric(metric,kind);n=len(points)-2;H=np.zeros((n,n));g=np.zeros(n)
 for i in range(n+1):
  if i%16==0:budget()
  a,b=points[i:i+2];na,nb=normals[i:i+2]
  def length(q):
   left=a+q[0]*na;right=b+q[1]*nb;v=right-left;total=0.
   for t,w in zip(nodes,weights):p=left+t*v;total=total+w*anp.sqrt(anp.dot(v,anp.dot(geth(p),v)))
   return total
  hh=np.asarray(hessian(length)(anp.zeros(2)),float);gg=np.asarray(grad(length)(anp.zeros(2)),float)
  for local,node in enumerate([i-1,i]):
   if 0<=node<n:
    g[node]+=gg[local]
    for local2,node2 in enumerate([i-1,i]):
     if 0<=node2<n:H[node,node2]+=hh[local,local2]
 return (H+H.T)/2,g

def mp_length(metric,points,normals,q,order=16):
 x,w=mp.gauss_quadrature(order,'legendre');total=mp.mpf(0);pp=[np.array([mp.mpf(float(a)) for a in p],object) for p in points];nn=[np.array([mp.mpf(float(a)) for a in v],object) for v in normals];qq=[mp.mpf(0)]+[mp.mpf(a) for a in q]+[mp.mpf(0)];pp=[p+a*n for p,a,n in zip(pp,qq,nn)]
 for a,b in zip(pp[:-1],pp[1:]):
  v=b-a
  for t,ww in zip(x,w):
   p=a+(1+t)*v/2;z=metric.f@p;weights=np.array([mp.exp(a-max(z)) for a in z],object);weights/=sum(weights);d=metric.f-weights@metric.f;u=(weights*(d@v))@metric.R;total+=ww*mp.sqrt(u@u)/2
 return total
