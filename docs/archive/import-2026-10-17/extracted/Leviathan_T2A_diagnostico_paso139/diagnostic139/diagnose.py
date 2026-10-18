import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,zipfile,hashlib,json,io,pickle,csv
from pathlib import Path
import numpy as np,mpmath as mp
from scipy.integrate import DOP853
sys.path.insert(0,str(Path('Windows_RIPG_T2A_CP90/source').resolve()))
from geometry import Geometry
from fast_mpfr_acceleration import FastMPFRAcceleration
out=Path('diagnostic139')
z=zipfile.ZipFile('upload/RIPG_RESULTADOS_PC.zip');manifest=json.loads(z.read('output/return_manifest.json'));ix=json.loads(z.read('output/index.json'))
for n,h in manifest['files'].items():assert hashlib.sha256(z.read('output/'+n)).hexdigest()==h
segments=[]
for rec in ix['segments']:
 b=z.read('output/'+rec['file']);assert hashlib.sha256(b).hexdigest()==rec['sha256']
 with zipfile.ZipFile(io.BytesIO(b)) as zz:
  assert zz.testzip() is None;segments.append(pickle.loads(zz.read('replay.pkl')))
s=segments[-1]['solver'];p,v=s['y'].reshape(2,-1,2);N=len(p)
scale=s['atol']+s['rtol']*np.maximum(abs(s['y_old']),abs(s['y']))
e5=(s['K'].T@DOP853.E5)/scale;e3=(s['K'].T@DOP853.E3)/scale
con=(e5.reshape(2,N,2)**2).sum(axis=(0,2));order=np.argsort(-con)
err=abs(s['h_previous'])*np.sum(e5**2)/np.sqrt((np.sum(e5**2)+.01*np.sum(e3**2))*len(scale))
with np.load('Windows_RIPG_T2A_CP90/data/state.npz') as a:g=Geometry(a['M'],a['f'])
fast=FastMPFRAcceleration(g)
J=g.jac(p);G=np.einsum('bni,nm,bmj->bij',J,g.M,J,optimize=True)
rows=[]
for i in range(N):rows.append(dict(ray=i,theta=2*np.pi*i/N,error5_fraction=con[i]/con.sum(),p_norm=np.linalg.norm(p[i]),v_norm=np.linalg.norm(v[i]),cond_float=np.linalg.cond(G[i])))
with (out/'all_rays.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def reference(i,dps):
 with mp.workdps(dps):
  M=mp.matrix(g.M.tolist());F=mp.matrix(g.f.tolist());P=mp.matrix(p[i].tolist());V=mp.matrix(v[i].tolist());l=F*P;w=mp.matrix([mp.exp(x-max(l)) for x in l]);w=w/sum(w);mu=F.T*w
  J=mp.matrix([[w[k]*(F[k,a]-mu[a]) for a in range(2)] for k in range(len(w))]);zz=[sum((F[k,a]-mu[a])*V[a] for a in range(2)) for k in range(len(w))];z2=sum(w[k]*zz[k]**2 for k in range(len(w)));H=mp.matrix([w[k]*(zz[k]**2-z2) for k in range(len(w))]);GG=J.T*M*J;acc=mp.lu_solve(GG,-J.T*M*H)
  eig=mp.eigsy((GG+GG.T)/2,eigvals_only=True)
  return np.array([float(x) for x in acc]),dict(cond_mp=float(eig[1]/eig[0]),lambda_min=str(eig[0]),lambda_max=str(eig[1]),speed2=float((V.T*GG*V)[0]),logit_span=float(max(l)-min(l)),weight_min=str(min(w)),p=p[i].tolist(),v=v[i].tolist())
chosen=list(dict.fromkeys(order[:10].tolist()+[0,512,1024,1536]))
checks=[]
for i in chosen:
 a80,m=reference(i,80);a120,_=reference(i,120);af=fast.one(p[i],v[i]);a64=-np.einsum('kij,i,j->k',g.jet(p[i:i+1])[4][0],v[i],v[i]);den=np.maximum(abs(a120),1e-300)
 m.update(ray=i,error5_fraction=float(con[i]/con.sum()),rel80_120=float(np.max(abs(a80-a120)/den)),rel169_120=float(np.max(abs(af-a120)/den)),rel64_120=float(np.max(abs(a64-a120)/den)),acceleration=a120.tolist());checks.append(m)
 print('RAY',i,'share',m['error5_fraction'],'cond',m['cond_mp'],'speed2',m['speed2'],'err169',m['rel169_120'],flush=True)
(out/'precision_checks.json').write_text(json.dumps(checks,indent=2))
history=[]
for d in segments:
 ss=d['solver'];pp,vv=ss['y'].reshape(2,N,2)
 for i in order[:3]:history.append(dict(step=d['start_step']+len(d['steps']),r=float(ss['t']),h=float(ss['h_previous']),ray=int(i),p_norm=float(np.linalg.norm(pp[i])),v_norm=float(np.linalg.norm(vv[i]))))
(out/'history.json').write_text(json.dumps(history,indent=2))
result=dict(step=139,r=float(s['t']),accepted_error_norm=float(err),top1=float(con[order[:1]].sum()/con.sum()),top5=float(con[order[:5]].sum()/con.sum()),top10=float(con[order[:10]].sum()/con.sum()),top_rays=order[:10].tolist(),next_h=float(s['h_abs']),checks=checks)
(out/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
