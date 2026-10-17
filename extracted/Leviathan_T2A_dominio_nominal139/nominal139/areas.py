from common import *
from scipy.integrate import simpson
import time
results=[]
for nr in [32,64,128,256]:
 start=time.perf_counter();rings=sol(np.linspace(0,r,nr+1)).T.reshape(nr+1,2,2048,2)[:,0];ar=area7(g,triangles(rings));rec=dict(r=r,rings=nr,rays=2048,area=ar,wall=time.perf_counter()-start);results.append(rec);print(rec,flush=True);(O/'prefix_results.json').write_text(json.dumps(results,indent=2))
nr=1024;rr=np.linspace(0,r,nr+1);dens={s:[] for s in [4,2,1]};max_speed_error=0.
for j,t in enumerate(rr):
 P,V=sol(t).reshape(2,2048,2);w=softmax(P@g.f.T,axis=1);dw=g.f[None,:,:]-np.einsum('nk,ki->ni',w,g.f)[:,None,:];wr=w*np.einsum('nki,ni->nk',dw,V);aa=np.einsum('ni,ij,nj->n',wr,g.M,wr,optimize=True);max_speed_error=max(max_speed_error,float(np.max(abs(aa-1))))
 for stride in [4,2,1]:
  ww=w[::stride];vv=wr[::stride];dt=2*np.pi/len(ww);wt=(np.roll(ww,-1,axis=0)-np.roll(ww,1,axis=0))/(2*dt);bb=np.einsum('ni,ij,nj->n',wt,g.M,wt,optimize=True);ab=np.einsum('ni,ij,nj->n',vv,g.M,wt,optimize=True);dens[stride].append(float(np.sqrt(np.maximum(aa[::stride]*bb-ab**2,0)).sum()*dt))
 if j%256==0:print('density',j,'/1024',flush=True)
res=[]
for s in [4,2,1]:
 for rs in [4,2,1]:res.append(dict(rays=2048//s,radial_intervals=nr//rs,area=float(simpson(np.array(dens[s])[::rs],x=rr[::rs]))))
(O/'intrinsic_area_results.json').write_text(json.dumps(dict(results=res,max_speed_squared_error=max_speed_error),indent=2));np.savez(O/'area_density.npz',r=rr,**{str(k):v for k,v in dens.items()});print(json.dumps(res,indent=2))
