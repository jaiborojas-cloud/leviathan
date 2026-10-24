"""Código autorizado y estados exclusivamente sintéticos; sin cargar casos T2."""
import sys
sys.dont_write_bytecode=True
import os,json,csv,hashlib,types,time
from pathlib import Path
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];CFG=json.loads((ROOT/'config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False,ensure_ascii=False)+'\n')
def rows(p):return list(csv.DictReader(p.open()))
def table(p,rs,fields=None):
 if rs or fields:
  with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields or list(rs[0]));w.writeheader();w.writerows(rs)
ALLOWED={str(REPO/CFG['geometry_path']),str(REPO/CFG['audit_path'])};ACCESS={'blocked':0}
def access_guard(event,args):
 if event!='open' or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 path=os.path.abspath(os.fsdecode(args[0]));forbidden=('/experiments/T2_A' in path or '/Repro/T2_A' in path or path.lower().endswith('.npz') or '/docs/archive/' in path and path not in ALLOWED)
 if forbidden:ACCESS['blocked']+=1;raise PermissionError('AF forbids T2 state/data access')
sys.addaudithook(access_guard)
def imports():
 for key in ['geometry','audit']:assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256'],key
 gm=types.ModuleType('geometry');gm.__file__=str(REPO/CFG['geometry_path']);sys.modules['geometry']=gm;exec(compile(Path(gm.__file__).read_text(),gm.__file__,'exec'),gm.__dict__)
 am=types.ModuleType('af_authorized_audit');am.__file__=str(REPO/CFG['audit_path']);exec(compile(Path(am.__file__).read_text(),am.__file__,'exec'),am.__dict__)
 return gm,am
class MPGeometry:
 def __init__(self,M,f):self.M=mp.matrix([[mp.mpf(float(v)) for v in row] for row in M]);self.f=mp.matrix([[mp.mpf(float(v)) for v in row] for row in f]);self.n=len(f)
 def geometry(self,p):
  p=[mp.mpf(v) for v in p];z=[sum(self.f[n,i]*p[i] for i in range(2)) for n in range(self.n)];a=[mp.exp(v-max(z)) for v in z];den=sum(a);a=[v/den for v in a];mu=[sum(a[n]*self.f[n,i] for n in range(self.n)) for i in range(2)];d=[[self.f[n,i]-mu[i] for i in range(2)] for n in range(self.n)];cov=[[sum(a[n]*d[n][i]*d[n][j] for n in range(self.n)) for j in range(2)] for i in range(2)];J=mp.matrix([[a[n]*d[n][i] for i in range(2)] for n in range(self.n)]);H=mp.matrix([[a[n]*(d[n][i]*d[n][j]-cov[i][j]) for i in range(2) for j in range(2)] for n in range(self.n)]);g=J.T*self.M*J;G=g**-1*J.T*self.M*H;normal=H-J*G;K=((normal[:,0].T*self.M*normal[:,3])[0]-(normal[:,1].T*self.M*normal[:,1])[0])/mp.det(g)
  return g,G,K

def generate(gm):
 bases=[];states=[]
 for seed in CFG['seeds']:
  rng=np.random.Generator(np.random.PCG64(seed));f=rng.normal(size=(27,2));f=(f-f.mean(0))/f.std(0);A=np.column_stack([np.ones(27),f]);rad=np.sum(f*f,1);rad-=A@np.linalg.lstsq(A,rad,rcond=None)[0];norm=np.linalg.norm(rad);column=rad*np.sqrt(27)/norm if norm>1e-12 else np.zeros(27);Q=np.column_stack([CFG['radial_Q_amplitude']*column,rng.normal(0,CFG['noise_Q_std'],size=(27,26))]);M=Q@Q.T/27+CFG['base_epsilon']*np.eye(27);K=float(gm.Geometry(M,f).eval([[0.,0.]])[1][0]);bases.append({'seed':seed,'f':f.tolist(),'Q':Q.tolist(),'K_base_center':K,'radial_norm':float(norm)})
  for scale,T in zip(CFG['feature_scales'],CFG['curvature_targets']):
   alpha=max(abs(K),CFG['calibration_floor'])/T;qs=np.sqrt(alpha)*Q;eps=alpha*CFG['base_epsilon'];ms=qs@qs.T/27+eps*np.eye(27);states.append({'id':f'T{int(T)}/seed{seed}','seed':seed,'target':T,'scale':scale,'alpha':alpha,'epsilon':eps,'f':(scale*f).tolist(),'M':ms.tolist(),'calibration_clipped':abs(K)<CFG['calibration_floor']})
 return bases,states
