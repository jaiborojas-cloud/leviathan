from common import *
from scipy.integrate import solve_ivp
p,v=b['solver']['y'].reshape(2,-1,2);r0=r;N=len(p);M,f=g.M,g.f;logits=p@f.T
C=[];A=[]
for l in logits:
 order=np.argsort(-l,kind='stable');base=int(order[0]);found=False
 for j in range(1,len(order)):
  for k in range(j+1,len(order)):
   mat=np.array([f[order[j]]-f[base],f[order[k]]-f[base]])
   if abs(np.linalg.det(mat))>1e-8:
    coeff=(f-f[base])@np.linalg.inv(mat);coeff[base]=0;coeff[order[j]]=[1,0];coeff[order[k]]=[0,1];C.append(coeff);A.append(mat);found=True;break
  if found:break
C=np.array(C);A=np.array(A);x=np.exp(np.einsum('nij,nj->ni',A,p));V=x*np.einsum('nij,nj->ni',A,v)
def jet(x,V=None):
 if np.any(x<=0):raise ValueError('Boundary crossing forbidden')
 w=softmax(np.einsum('nki,ni->nk',C,np.log(x)),axis=1);B=C/x[:,None,:];J=w[:,:,None]*(B-np.einsum('nk,nki->ni',w,B)[:,None,:]);JM=np.einsum('nki,kl->nli',J,M,optimize=True);G=np.einsum('nki,nkj->nij',J,JM)
 if V is None:return w,J,G
 L=np.einsum('nki,ni->nk',B,V);Lbar=np.einsum('nk,nk->n',w,L);Q=-np.einsum('nki,ni->nk',C,(V/x)**2);Qbar=np.einsum('nk,nk->n',w,Q);var=np.einsum('nk,nk->n',w,(L-Lbar[:,None])**2);Hvv=w*((L-Lbar[:,None])**2+Q-Qbar[:,None]-var[:,None]);acc=-np.linalg.solve(G,np.einsum('nki,nk->ni',JM,Hvv)[...,None])[...,0]
 return w,J,G,acc
def rhs(t,y):
 xx,VV=y.reshape(2,N,2);return np.stack([VV,jet(xx,VV)[3]]).ravel()
rbound=0.07447440068752452;target=rbound-1e-10
w,J,G=jet(x);origw=softmax(logits,axis=1);origJ=origw[:,:,None]*(f[None,:,:]-np.einsum('nk,ki->ni',origw,f)[:,None,:]);T=x[:,:,None]*A;recon=np.einsum('nki,nij->nkj',J,T)
rec={'r0':r0,'target':target,'rbound_reference':rbound,'max_chart_condition':float(np.max(np.linalg.cond(G))),'max_overlap_relative':float(np.max(np.linalg.norm(recon-origJ,axis=(1,2))/np.linalg.norm(origJ,axis=(1,2))))}
ss=solve_ivp(rhs,[r0,target],np.stack([x,V]).ravel(),method='DOP853',rtol=2e-10,atol=2e-12,dense_output=True,first_step=target-r0);assert ss.success;rec.update(nfev=ss.nfev)
def density(t,stride):
 xx,VV=ss.sol(t).reshape(2,N,2);w,J,G=jet(xx);wr=np.einsum('nki,ni->nk',J,VV);w=w[::stride];wr=wr[::stride];dt=2*np.pi/len(w);wt=(np.roll(w,-1,axis=0)-np.roll(w,1,axis=0))/(2*dt);aa=np.einsum('ni,ij,nj->n',wr,M,wr);bb=np.einsum('ni,ij,nj->n',wt,M,wt);ab=np.einsum('ni,ij,nj->n',wr,M,wt);return float(np.sqrt(np.maximum(aa*bb-ab*ab,0)).sum()*dt)
rec['shell']=[]
for stride in [4,2,1]:
 vals=[density(t,stride) for t in np.linspace(r0,target,9)];rec['shell'].append(dict(rays=N//stride,density_min=min(vals),density_max=max(vals),shell_area=float(np.trapezoid(vals,np.linspace(r0,target,9)))))
(O/'local_bundle_results.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
