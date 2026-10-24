"""Adaptador DOP853 auditado; sin modificar geometry.py/audit.py archivados."""
from common_v1 import *
from scipy.integrate import DOP853,OdeSolution
from scipy.optimize import brentq
from scipy.linalg import eigh
from shapely.geometry import Polygon
from numpy.polynomial.legendre import leggauss
import autograd.numpy as anp
from autograd import grad,hessian

class Trace:
 def __init__(self,sol,last,status,reason,nfev,n):self.sol=sol;self.last=last;self.status=status;self.reason=reason;self.nfev=nfev;self.n=n
 def at(self,r):return self.sol(r).reshape(6,self.n,-1) if np.ndim(r) else self.sol(r).reshape(6,self.n)

def integrate(g,angles,R,budget=lambda:None):
 n=len(angles);h0=g.jet(np.zeros((1,2)))[0][0];v=np.linalg.solve(np.linalg.cholesky(h0).T,np.array([np.cos(angles),np.sin(angles)])).T;initial=np.concatenate([np.zeros((n,2)),v,np.zeros((n,1)),np.ones((n,1))],1).T.ravel();times=[0.];polys=[];status='RIGHT_CENSORED_RMAX';reason='';last=0.;nfev=0
 def rhs(r,y):
  z=y.reshape(6,n).T;p=z[:,:2];vv=z[:,2:4];h,inv,H,cross,G=g.jet(p);e=np.linalg.eigvalsh(h)
  if not np.all(np.isfinite(e)) or e.min()<=0 or max(e[:,1]/e[:,0])>1e12:raise FloatingPointError('SPD_OR_CONDITION')
  normal=H-np.einsum('bni,bijk->bnjk',g.jac(p),G);a,b,c=normal[:,:,0,0],normal[:,:,1,1],normal[:,:,0,1];K=(np.einsum('bn,nm,bm->b',a,g.M,b)-np.einsum('bn,nm,bm->b',c,g.M,c))/np.linalg.det(h);return np.concatenate([vv,-np.einsum('bkij,bi,bj->bk',G,vv,vv),z[:,5,None],(-K*z[:,4])[:,None]],1).T.ravel()
 try:
  solver=DOP853(rhs,0.,initial,R,rtol=CFG['rtol'],atol=CFG['atol'],max_step=R/64)
  while solver.status=='running':
   budget();left=solver.t;solver.step();nfev=solver.nfev
   if solver.status=='failed':raise RuntimeError('DOP853_FAILED')
   dense=solver.dense_output();end=solver.t;p=solver.y.reshape(6,n)[:2];escaped=np.max(abs(p))>=CFG['escape_threshold']
   if escaped:
    end=brentq(lambda r:CFG['escape_threshold']-np.max(abs(dense(r).reshape(6,n)[:2])),left,end,xtol=1e-13);status='ESCAPE'
   times.append(float(end));polys.append(dense);last=float(end)
   if escaped:break
 except Exception as e:status='INCONCLUSIVE_NUMERICAL';reason=type(e).__name__+':'+str(e)
 sol=OdeSolution(np.array(times),polys) if polys else None;return Trace(sol,last,status,reason,nfev,n)

def first_roots(trace):
 if trace.sol is None:return np.full(trace.n,np.nan)
 radii=np.linspace(0,trace.last,CFG['radial_scan']);js=trace.at(radii)[4];roots=np.full(trace.n,np.nan)
 for i in range(trace.n):
  indices=np.where((js[i,1:-1]>0)&(js[i,2:]<=0))[0]
  if len(indices):k=int(indices[0]+1);roots[i]=brentq(lambda r:trace.at(r)[4,i],radii[k],radii[k+1],xtol=1e-13)
 return roots

def first_collision(trace):
 if trace.sol is None:return None
 prev=0.
 for r in np.linspace(0,trace.last,CFG['radial_scan'])[1:]:
  poly=trace.at(r)[:2].T
  if not Polygon(poly).exterior.is_simple:
   lo,hi=prev,float(r)
   for _ in range(28):
    mid=(lo+hi)/2
    if Polygon(trace.at(mid)[:2].T).exterior.is_simple:lo=mid
    else:hi=mid
   return lo,hi
  prev=float(r)
 return None

def mp_check(g,points):
 details=[];good=True
 with mp.workdps(CFG['mp_digits']):
  hp=MPGeometry(g.M,g.f)
  for label,p in points:
   h,G,K=hp.geometry([mp.mpf(float(x)) for x in p]);da,k=g.eval([p]);err=float(abs(K-mp.mpf(float(k[0])))/max(1,abs(K)));de=float(abs(mp.sqrt(mp.det(h))-mp.mpf(float(da[0])))/max(1,mp.sqrt(mp.det(h))));passed=max(err,de)<=CFG['mp_K_tolerance'];good=good and passed;details.append({'location':label,'p1':float(p[0]),'p2':float(p[1]),'K_float':float(k[0]),'K_MP':mp.nstr(K,80),'K_error':err,'density_error':de,'status':'PASS' if passed else 'INCONCLUSIVE'})
 return good,details

def normal_frame(g,points,velocities):
 h=g.jet(points)[0];hv=np.einsum('bij,bj->bi',h,velocities);normals=np.column_stack([-hv[:,1],hv[:,0]]);normals/=np.sqrt(np.einsum('bi,bij,bj->b',normals,h,normals))[:,None];return normals

def normal_block(points,normals,M,f,order,kind='synthetic',flat_coeff=None,budget=lambda:None):
 tt,ww=leggauss(order);tt=(tt+1)/2;ww=ww/2;n=len(points)-2;H=np.zeros((n,n));gradient=np.zeros(n)
 for i in range(n+1):
  if i%16==0:budget()
  a,b=points[i:i+2];na,nb=normals[i:i+2]
  def value(q):
   left=a+q[0]*na;right=b+q[1]*nb;v=right-left;total=0.
   for t,w in zip(tt,ww):
    p=left+t*v
    if kind=='synthetic':z=anp.dot(f,p);weights=anp.exp(z-anp.max(z));weights=weights/anp.sum(weights);df=anp.dot(f,v)-anp.dot(weights,anp.dot(f,v));d=weights*df;speed=anp.sqrt(anp.dot(d,anp.dot(M,d)))
    elif kind=='sphere':speed=anp.sqrt(v[0]**2+anp.cos(p[0])**2*v[1]**2)
    elif kind=='hyperbolic':speed=anp.sqrt(v[0]**2+anp.exp(2*p[0])*v[1]**2)
    else:AA,BB,CC=flat_coeff;h=p[0]**2*AA+p[0]*p[1]*BB+p[1]**2*CC;speed=anp.sqrt(anp.dot(v,anp.dot(h,v)))
    total=total+w*speed
   return total
  hh=np.asarray(hessian(value)(anp.zeros(2)),float);gg=np.asarray(grad(value)(anp.zeros(2)),float)
  for x,node in enumerate([i-1,i]):
   if 0<=node<n:
    gradient[node]+=gg[x]
    for y,node2 in enumerate([i-1,i]):
     if 0<=node2<n:H[node,node2]+=hh[x,y]
 return (H+H.T)/2,gradient

def mp_rayleigh(M,f,points,normals,vector,order,budget=lambda:None):
 # Segunda derivada analítica de la longitud bajo carta normal lineal.
 with mp.workdps(80):
  MM=mp.matrix([[mp.mpf(float(x)) for x in row] for row in M]);ff=mp.matrix([[mp.mpf(float(x)) for x in row] for row in f]);nn=len(f);ts,ws=mp.gauss_quadrature(order,'legendre');total=mp.mpf(0);qq=[mp.mpf(0)]+[mp.mpf(float(x)) for x in vector]+[mp.mpf(0)]
  for edge,(ap,bp) in enumerate(zip(points[:-1],points[1:])):
   if edge%16==0:budget()
   a=mp.matrix([mp.mpf(float(x)) for x in ap]);b=mp.matrix([mp.mpf(float(x)) for x in bp]);v=b-a;na=qq[edge]*mp.matrix([mp.mpf(float(x)) for x in normals[edge]]);nb=qq[edge+1]*mp.matrix([mp.mpf(float(x)) for x in normals[edge+1]]);dv=nb-na
   for tt,weight in zip(ts,ws):
    t=(tt+1)/2;p=a+t*v;w=na+t*dv;z=[sum(ff[i,j]*p[j] for j in range(2)) for i in range(nn)];aa=[mp.exp(x-max(z)) for x in z];ss=sum(aa);aa=[x/ss for x in aa];mu=[sum(aa[i]*ff[i,j] for i in range(nn)) for j in range(2)];di=[[ff[i,j]-mu[j] for j in range(2)] for i in range(nn)];x=[sum(v[j]*di[i][j] for j in range(2)) for i in range(nn)];y=[sum(dv[j]*di[i][j] for j in range(2)) for i in range(nn)];zz=[sum(w[j]*di[i][j] for j in range(2)) for i in range(nn)];var=sum(aa[i]*zz[i]**2 for i in range(nn));cxz=sum(aa[i]*x[i]*zz[i] for i in range(nn));cyz=sum(aa[i]*y[i]*zz[i] for i in range(nn));third=sum(aa[i]*x[i]*zz[i]**2 for i in range(nn));beta=mp.matrix([aa[i]*x[i] for i in range(nn)]);beta1=mp.matrix([aa[i]*(zz[i]*x[i]+y[i]-cxz) for i in range(nn)]);beta2=mp.matrix([aa[i]*((zz[i]**2-var)*x[i]+2*zz[i]*(y[i]-cxz)-2*cyz-third) for i in range(nn)]);mb=MM*beta;mb1=MM*beta1;F=(beta.T*mb)[0];num=(beta1.T*mb1)[0]+(beta2.T*mb)[0];cross=(beta1.T*mb)[0];total+=weight*(num/mp.sqrt(F)-cross**2/F**mp.mpf('1.5'))/2
  return total
