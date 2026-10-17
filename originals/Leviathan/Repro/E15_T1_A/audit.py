import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import pathlib,json,time,traceback,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq,minimize_scalar
from shapely import linestrings,STRtree
from shapely.geometry import Polygon
from shapely.ops import unary_union,polygonize
from geometry import Geometry,area7,triangles
P=pathlib.Path(__file__).resolve().parent

def save(p,d):
 def clean(x):
  if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
  if isinstance(x,(list,tuple,np.ndarray)):return [clean(v) for v in x]
  if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
  if isinstance(x,np.integer):return int(x)
  if isinstance(x,np.bool_):return bool(x)
  return x
 p.write_text(json.dumps(clean(d),indent=2,allow_nan=False))
class AuditedGeometry(Geometry):
 def __init__(self,*args):
  super().__init__(*args);self.audit=dict(evaluations=0,min_eigenvalue=float('inf'),max_condition=0.,nonpositive=0,nonfinite=0)
 def jet(self,p):
  z=super().jet(p);e=np.linalg.eigvalsh(z[0]);a=self.audit;a['evaluations']+=len(e);a['min_eigenvalue']=min(a['min_eigenvalue'],float(e.min()));a['max_condition']=max(a['max_condition'],float((e[:,1]/e[:,0]).max()));a['nonpositive']+=int((e<=0).sum());a['nonfinite']+=int((~np.isfinite(e)).sum())
  if a['nonpositive'] or a['nonfinite']:raise FloatingPointError('SPD/nonfinite failure')
  return z

def load(case):
 d=P/'states'/case;z=np.load(d/'state.npz');return d,AuditedGeometry(z['M'],z['f']),json.loads((d/'nominal.json').read_text())['radius']
def winding(b,p):
 v=b-p;w=np.roll(v,-1,axis=0);return float(np.arctan2(v[:,0]*w[:,1]-v[:,1]*w[:,0],np.sum(v*w,1)).sum()/(2*np.pi))
def topology(b,phase):
 n=len(b);seg=linestrings(np.stack([b,np.roll(b,-1,axis=0)],1));pairs=STRtree(seg).query(seg,predicate='intersects');pairs=pairs[:,(pairs[0]<pairs[1])&((pairs[1]-pairs[0])!=1)&((pairs[1]-pairs[0])!=n-1)];xs=[]
 for i,j in pairs.T:
  inter=seg[i].intersection(seg[j])
  for xy in list(inter.coords):
   p=np.array(xy);u=b[(i+1)%n]-b[i];v=b[(j+1)%n]-b[j];t=np.dot(p-b[i],u)/np.dot(u,u);s=np.dot(p-b[j],v)/np.dot(v,v)
   xs.append(dict(segments=[int(i),int(j)],fractions=[t,s],angles=[(phase+(i+t)*2*np.pi/n)%(2*np.pi),(phase+(j+s)*2*np.pi/n)%(2*np.pi)],point=xy,transversality=abs(np.linalg.det(np.array([u,v])))/(np.linalg.norm(u)*np.linalg.norm(v))))
 poly=Polygon(b);e=np.roll(b,-1,axis=0)-b;ee=np.roll(e,-1,axis=0);turn=np.arctan2(e[:,0]*ee[:,1]-e[:,1]*ee[:,0],np.sum(e*ee,1)).sum()/(2*np.pi);faces=list(polygonize(unary_union(seg.tolist())))
 return dict(simple=poly.exterior.is_simple,valid=poly.is_valid,intersections=xs,intersection_count=len(xs),origin_winding=winding(b,np.zeros(2)),turning_number=turn,signed_chart_area=np.sum(b[:,0]*np.roll(b[:,1],-1)-b[:,1]*np.roll(b[:,0],-1))/2,union_chart_area=sum(f.area for f in faces),faces=[dict(chart_area=f.area,winding=winding(b,np.array(f.representative_point().coords[0]))) for f in faces])
def onset(sol,n,R):
 prev=0.
 for r in np.linspace(0,R,129)[1:]:
  if not Polygon(sol.sol(r).reshape(2,n,2)[0]).exterior.is_simple:
   lo,hi=prev,r
   for _ in range(28):
    mid=(lo+hi)/2
    if Polygon(sol.sol(mid).reshape(2,n,2)[0]).exterior.is_simple:lo=mid
    else:hi=mid
   return dict(detected=True,lower=lo,upper=hi)
  prev=r
 return dict(detected=False,lower=R,upper=None)
def boundary(case,n,ph):
 d,g,R=load(case);out=d/'boundary';out.mkdir(exist_ok=True);dest=out/f'n{n}_phase{ph}.json'
 if dest.exists():return json.loads(dest.read_text())
 start=time.perf_counter();cpu=time.process_time();phase=ph*np.pi/n
 try:
  sol=g.rays(R,n,phase);y=sol.sol(R).reshape(2,n,2);top=topology(y[0],phase);first=onset(sol,n,R);data=dict(boundary=y[0],velocity=y[1],phase=phase)
  if n==16384 and ph==0:
   radii=np.linspace(0,R,65);data.update(radii=radii,path=sol.sol(radii).T.reshape(65,2,n,2))
   if first['detected']:
    b=sol.sol(first['upper']).reshape(2,n,2)[0];save(d/'first_collision.json',dict(radius=first['upper'],topology=topology(b,phase)));np.savez_compressed(d/'first_collision_boundary.npz',boundary=b,radius=first['upper'])
  np.savez_compressed(dest.with_suffix('.npz'),**data);area={}
  if n>=8192 and ph==0:
   rr=first['lower'];area=dict(radius=rr,censored=not first['detected'])
   for nr in [32,64]:area[str(nr)]=area7(g,triangles(sol.sol(np.linspace(0,rr,nr+1)).T.reshape(nr+1,2,n,2)[:,0]))
  result=dict(case=case,n=n,phase_id=ph,phase=phase,R=R,nfev=sol.nfev,topology=top,first_intersection=first,embedded_area=area,audit=g.audit)
 except Exception as e:result=dict(case=case,n=n,phase_id=ph,error=repr(e),traceback=traceback.format_exc(),audit=g.audit)
 result.update(seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu);save(dest,result);return result

def rk(case,steps,ph):
 d,g,R=load(case);out=d/'rk4';out.mkdir(exist_ok=True);dest=out/f'steps{steps}_phase{ph}.json'
 if dest.exists():return json.loads(dest.read_text())
 start=time.perf_counter();cpu=time.process_time();phase=ph*np.pi/2048
 try:
  b=g.rk4(R,2048,steps,phase)[-1];np.savez_compressed(dest.with_suffix('.npz'),boundary=b);result=dict(case=case,n=2048,steps=steps,phase_id=ph,R=R,topology=topology(b,phase),audit=g.audit)
 except Exception as e:result=dict(case=case,steps=steps,phase_id=ph,error=repr(e),traceback=traceback.format_exc(),audit=g.audit)
 result.update(seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu);save(dest,result);return result

def jacsolve(g,angles,R):
 n=len(angles);g0=g.jet(np.zeros((1,2)))[0][0];v=np.linalg.solve(np.linalg.cholesky(g0).T,np.array([np.cos(angles),np.sin(angles)])).T;init=np.concatenate([np.zeros((n,2)),v,np.zeros((n,1)),np.ones((n,1))],1).T.ravel()
 def rhs(t,y):
  z=y.reshape(6,n).T;p=z[:,:2];v=z[:,2:4];gg,gi,H,cross,gamma=g.jet(p);normal=H-np.einsum('bni,bijk->bnjk',g.jac(p),gamma);a,b,c=normal[:,:,0,0],normal[:,:,1,1],normal[:,:,0,1];K=(np.einsum('bn,nm,bm->b',a,g.M,b)-np.einsum('bn,nm,bm->b',c,g.M,c))/np.linalg.det(gg)
  return np.concatenate([v,-np.einsum('bkij,bi,bj->bk',gamma,v,v),z[:,5,None],(-K*z[:,4])[:,None]],1).T.ravel()
 s=solve_ivp(rhs,[0,R],init,method='DOP853',rtol=2e-10,atol=2e-12,dense_output=True)
 if not s.success:raise RuntimeError(s.message)
 return s

def roots(sol,n,R):
 t=np.linspace(0,R,513);j=sol.sol(t).reshape(6,n,-1)[4];rs=np.full(n,np.nan)
 for i in range(n):
  ids=np.where((j[i,1:-1]>0)&(j[i,2:]<=0))[0]
  if len(ids):
   k=ids[0]+1;rs[i]=brentq(lambda r:sol.sol(r).reshape(6,n)[4,i],t[k],t[k+1],xtol=1e-12)
 return rs,t,j

def jacobi(case,n,ph):
 d,g,R=load(case);out=d/'jacobi';out.mkdir(exist_ok=True);dest=out/f'n{n}_phase{ph}.json'
 if dest.exists():return json.loads(dest.read_text())
 start=time.perf_counter();cpu=time.process_time();angles=(np.arange(n)+ph/2)*2*np.pi/n
 try:
  sol=jacsolve(g,angles,R);rs,ts,js=roots(sol,n,R);det=js[:,1:]/ts[None,1:];np.savez_compressed(dest.with_suffix('.npz'),angles=angles,radii=ts,first_roots=rs,determinant=det);minimum=None
  if np.isfinite(rs).any():
   i=int(np.nanargmin(rs));theta=angles[i];h=2*np.pi/n
   def value(a):
    rr,_,_=roots(jacsolve(g,np.array([a]),R),1,R);return rr[0] if np.isfinite(rr[0]) else 2*R
   opt=minimize_scalar(value,bounds=(theta-h,theta+h),method='bounded',options={'xatol':1e-8});minimum=dict(sampled_angle=theta,sampled_radius=rs[i],angle=opt.x%(2*np.pi),radius=opt.fun,success=opt.success)
  result=dict(case=case,n=n,phase_id=ph,R=R,root_count=int(np.isfinite(rs).sum()),conjugate_minimum=minimum,minimum_signed_determinant=float(det.min()),nominal_negative_count=int((js[:,-1]<0).sum()),max_intrinsic_condition=float((np.maximum(1,abs(det))/np.minimum(1,abs(det))).max()),audit=g.audit)
 except Exception as e:result=dict(case=case,n=n,phase_id=ph,error=repr(e),traceback=traceback.format_exc(),audit=g.audit)
 result.update(seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu);save(dest,result);return result

def main():
 from concurrent.futures import ProcessPoolExecutor,as_completed
 assert hashlib.sha256((P/'protocol_A2_frozen.json').read_bytes()).hexdigest()==(P/'protocol_A2_frozen.sha256').read_text();controls=[]
 for K in [0.,1.]:
  t=np.linspace(0,4,1001);s=solve_ivp(lambda t,y:[y[1],-K*y[0]],[0,4],[0,1],t_eval=t,method='DOP853',rtol=2e-10,atol=2e-12);err=float(abs(s.y[0]-(t if K==0 else np.sin(t))).max());assert err<1e-8;controls.append(dict(K=K,max_error=err))
 save(P/'analytic_controls.json',controls);cases=['j1_true','j3_true']+[f'j{j}_{r}' for j in range(5) for r in ['true','random'] if f'j{j}_{r}' not in ['j1_true','j3_true']];tasks=[]
 for fn,ns in [(boundary,[2048,4096,8192,16384]),(jacobi,[256,512,1024]),(rk,[64,128,256,512])]:
  for n in ns:
   for case in cases:
    for ph in [0,1]:tasks.append((fn,case,n,ph))
 start=time.perf_counter();results=[]
 with ProcessPoolExecutor(max_workers=6) as pool:
  fs={pool.submit(x[0],*x[1:]):(x[0].__name__,*x[1:]) for x in tasks}
  for fu in as_completed(fs):
   try:
    r=fu.result();results.append(r);print(fs[fu],r.get('error','OK'),round(r['seconds'],2),flush=True)
   except Exception:print(fs[fu],traceback.format_exc(),flush=True)
 save(P/'run_summary.json',dict(tasks=len(tasks),returned=len(results),wall_seconds=time.perf_counter()-start,cpu_seconds=sum(r['cpu_seconds'] for r in results),exceptions=[r for r in results if 'error' in r]))
if __name__=='__main__':main()
