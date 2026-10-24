"""Cuadraturas de semirrectas y exponencial con eventos, sin alterar la fuente."""
from ag_common_v1 import *
from scipy.special import softmax
from scipy.integrate import quad,DOP853
from scipy.optimize import minimize_scalar,brentq
from numpy.polynomial.legendre import leggauss

def slopes(f,angles,special=False):
 z=np.array([np.cos(angles),np.sin(angles)]).T@f.T
 if special:
  for row in z:
   top=max(row);row[top-row<1e-13*max(1,np.ptp(row))]=top
 return z-z.max(axis=1)[:,None]

def speed_z(M,z,s):
 a=softmax(np.asarray(s)[...,None]*z,axis=-1);b=a*(z-np.sum(a*z,axis=-1)[...,None]);v=np.einsum('...i,ij,...j->...',b,M,b,optimize=True)
 if np.min(v)<-1e-24:raise FloatingPointError('NEGATIVE_SPEED_SQUARED')
 return np.sqrt(np.maximum(0,v))

def rho_measure(g,M,f,archive,budget=lambda:None,linear=None):
 started=time.monotonic();attempts=[];grids=[];special=special_angles(f)
 # En el control afín, f ya está expresado en la nueva carta.
 for n in CFG['angles']:
  angles=np.arange(n)*2*np.pi/n;angles=np.r_[angles,special];z=slopes(f,angles);z[n:]=slopes(f,np.array(special),True)
  for order in CFG['orders']:
   budget();t,w=leggauss(order);x=(t+1)/2;ss=10*x/(1-x);ww=w/2*10/(1-x)**2;values=[]
   for k in range(0,len(z),32):
    budget();zz=z[k:k+32];dirs=np.column_stack([np.cos(angles[k:k+32]),np.sin(angles[k:k+32])]);points=ss[:,None,None]*dirs[None,:,:]
    jj=g.jac(points.reshape(-1,2)).reshape(order,len(dirs),len(f),2);beta=np.einsum('kdnq,dq->kdn',jj,dirs)
    if k+len(dirs)>n:
     local=max(0,n-k);aa=softmax(ss[:,None,None]*zz[None,local:,:],axis=-1);beta[:,local:]=aa*(zz[None,local:,:]-np.sum(aa*zz[None,local:,:],axis=-1)[...,None])
    metric=np.einsum('kdi,ij,kdj->kd',beta,M,beta,optimize=True);values.extend(np.sum(ww[:,None]*np.sqrt(np.maximum(metric,0)),axis=0))
   values=np.array(values);archive(f'rho_n{n}_o{order}',np.column_stack([angles,values]));ii=int(np.argmin(values));grids.append({'n':n,'order':order,'grid_min':float(min(values[:n])),'augmented_min':float(values[ii]),'theta':float(angles[ii]),'special':bool(ii>=n)})
 reference=grids[-1];theta0=reference['theta'];z_cache={}
 def evaluate(theta,is_special=False):
  budget();theta=float(theta%(2*np.pi));z=slopes(f,np.array([theta]),is_special)[0];gaps=-z[z<0]
  if not len(gaps):raise ValueError('ALL_LOGITS_TIED')
  # Escalas tardías explícitas: impide perder la arista tras un casi empate.
  cuts=[0.]
  for gap in sorted(set(float(x) for x in gaps)):
   cuts.extend([1/gap,10/gap,40/gap])
  upper=(70+max(0,np.log(max(gaps)/min(gaps))))/min(gaps);cuts=sorted(set(x for x in cuts if x<upper))+[upper]
  total=error=0.
  for a,b in zip(cuts[:-1],cuts[1:]):
   val,err=quad(lambda s:float(speed_z(M,z,s)),a,b,epsabs=1e-12*max(1,reference['augmented_min']),epsrel=1e-10,limit=100);total+=val;error+=err
  attempts.append({'theta':theta,'special':is_special,'rho':float(total),'quad_error':float(error),'tail_upper_s':upper})
  return float(total)
 candidates=[(evaluate(theta0,reference['special']),theta0,reference['special'])]
 for theta in special:candidates.append((evaluate(theta,True),theta,True))
 first=min(candidates);opt=minimize_scalar(lambda a:evaluate(a),bounds=(first[1]-2*np.pi/1440,first[1]+2*np.pi/1440),method='bounded',options={'xatol':CFG['angle_xatol'],'maxiter':CFG['angle_maxiter']})
 if opt.success:candidates.append((float(opt.fun),float(opt.x%(2*np.pi)),False))
 best=min(candidates);rho,theta,is_special=best;resolution=max(abs(x['augmented_min']-rho)/rho for x in grids);u=np.array([np.cos(theta),np.sin(theta)]);z=slopes(f,np.array([theta]),is_special)[0]
 probes=[]
 for s in [1.,10.,1/max(-z[z<0])]:
  hp=mp_speed(M,f,u,s,is_special);fp=float(speed_z(M,z,s));probes.append(abs(hp-fp)/max(hp,1e-30))
 status='PASS' if resolution<=CFG['rho_resolution_rel'] and max(probes)<=CFG['numeric_relative_tolerance'] and opt.success else 'INCONCLUSIVE'
 return {'rho':rho,'theta':theta,'special':is_special,'status':status,'resolution_error':resolution,'MP_speed_error':max(probes),'seconds':time.monotonic()-started,'optimizer_success':bool(opt.success)},grids,attempts

def initial(g,angles):
 h=g.jet([[0.,0.]])[0][0];v=np.linalg.solve(np.linalg.cholesky(h).T,np.array([np.cos(angles),np.sin(angles)])).T
 return v

def exponential(g,M,f,angles,R,triangular=False,budget=lambda:None,keep=True):
 n=len(angles);v=initial(g,angles);records=[];profiles=[];radii=[];N=np.array([[1,0],[0,1],[-1,-1.]])
 if triangular:
  F=f[::9];W,db,rho,foot=exact_triangle(M);J=g.jac([[0.,0.]])[0];dw=(np.repeat(np.eye(3),9,axis=0).T@J)@v.T;y0=np.r_[np.full((2,n),1/3).ravel(),dw[:2].ravel()]
  def rhs(t,y):return np.r_[y[2*n:],np.zeros(2*n)]
  def native(y):
   q=y.reshape(4,n)[:2];w=np.vstack([q,1-q.sum(axis=0)])
   if np.min(w)<=0:return None
   p=np.linalg.solve(F[:2]-F[2],np.log(w[:2]/w[2]));dq=y.reshape(4,n)[2:];vel=np.empty_like(p)
   # Sólo se archivan q y dq en esta carta, no velocidades P reconstruidas.
   return p
 else:
  y0=np.r_[np.zeros((2,n)).ravel(),v.T.ravel()]
  def rhs(t,y):
   p=y[:2*n].reshape(2,n).T;vv=y[2*n:].reshape(2,n).T;jet=g.jet(p);acc=-np.einsum('bkij,bi,bj->bk',jet[4],vv,vv)
   if not np.isfinite(acc).all():raise FloatingPointError('NONFINITE_CONNECTION')
   return np.r_[vv.T.ravel(),acc.T.ravel()]
  def native(y):return y.reshape(4,n)[:2]
 def criterion(y):
  p=native(y)
  return 1e10 if p is None else float(np.max(abs(p))-150)
 def save(t,y,step):
  if keep and (step<20 or step%20==0):radii.append(float(t));profiles.append(y.reshape(4,n).copy())
 status='UNKNOWN';reason='';last=0.;steps=0;nfev=0;end=y0;first_angle=None;escpoint=None
 try:
  solver=DOP853(rhs,0.,y0,R,rtol=1e-12,atol=1e-14,max_step=R/64);save(0.,y0,0)
  while solver.status=='running':
   budget();left=solver.t;solver.step();steps+=1;nfev=solver.nfev
   if solver.status=='failed':raise FloatingPointError('DOP853_FAILED')
   last=float(solver.t);end=solver.y.copy();p=native(end);maxp=np.inf if p is None else np.max(abs(p));records.append({'step':steps,'r':last,'h':last-left,'max_abs_P':float(maxp) if np.isfinite(maxp) else None})
   if criterion(end)>=0:
    dense=solver.dense_output();last=brentq(lambda t:criterion(dense(t)),left,last,xtol=1e-14);end=dense(last);pp=native(end);i=int(np.argmax(np.max(abs(pp),axis=0)));first_angle=float(angles[i]);escpoint=pp[:,i].tolist();status='ESCAPE';break
   save(last,end,steps)
   if steps>=CFG['steps_max']:status='DRAG_5000';break
  else:status='RHO_HORIZON_CENSORED'
 except TimeoutError as e:status='BUDGET';reason=str(e)
 except Exception as e:status='NUMERICAL_FAILURE';reason=type(e).__name__+':'+str(e)
 if keep:
  radii.append(float(last));profiles.append(end.reshape(4,n).copy())
 return {'status':status,'r':last,'steps':steps,'nfev':nfev,'angle':first_angle,'P':escpoint,'reason':reason,'ray_index':int(np.argmin(np.max(abs(native(end)),axis=0))) if status!='ESCAPE' else int(np.argmax(np.max(abs(native(end)),axis=0))), 'coordinate':'face_w' if triangular else 'natural_P','records':records,'radii':radii,'profiles':profiles}

def refine_escape(g,M,f,coarse,R,triangular,budget):
 attempts=[];theta=coarse['angle']
 if coarse['status']!='ESCAPE':return None,attempts,False
 def value(a):
  tr=exponential(g,M,f,np.array([a]),R,triangular,budget,False);attempts.append({'theta':float(a%(2*np.pi)),'status':tr['status'],'r':tr['r'],'steps':tr['steps'],'reason':tr['reason']})
  return tr['r'] if tr['status']=='ESCAPE' else 10*R
 opt=minimize_scalar(value,bounds=(theta-2*np.pi/2048,theta+2*np.pi/2048),method='bounded',options={'xatol':1e-8,'maxiter':40})
 valid=[a for a in attempts if a['status']=='ESCAPE'];best=min(valid,key=lambda a:a['r']) if valid else None
 return best,attempts,bool(opt.success and best is not None)
