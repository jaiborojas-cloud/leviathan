"""Fuentes permitidas e inputs exclusivamente sintéticos de DIN-D2."""
import sys,os,json,csv,time,hashlib,types,math
from pathlib import Path
from fractions import Fraction as Fr
sys.dont_write_bytecode=True
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];CFG=json.loads((ROOT/'config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def table(p,data):
 if not data:return
 fields=list(dict.fromkeys(k for d in data for k in d))
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for d in data:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in d.items()})
def rows(p):return list(csv.DictReader(p.open()))
ALLOWED={str(REPO/CFG[k+'_path']) for k in ['geometry','rho']};ACCESS={'blocked':0}
def guard(event,args):
 if event!='open' or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 p=os.path.abspath(os.fsdecode(args[0]))
 forbidden=(('/experiments/T2_' in p and p not in ALLOWED) or '/baseline/' in p or '/comparators/' in p or '/cuarentena_X/' in p or p.endswith('predictors_locked.csv') or p.lower().endswith('.npz') or '/docs/archive/' in p and p not in ALLOWED)
 if forbidden:ACCESS['blocked']+=1;raise PermissionError('DIN-D2 prohíbe datos T2')
sys.addaudithook(guard)
def sources():
 modules=[]
 for key,name in [('geometry','geometry'),('rho','din_d2_frozen_rho')]:
  path=REPO/CFG[key+'_path'];assert sha(path)==CFG[key+'_sha256'];mod=types.ModuleType(name);mod.__file__=str(path);sys.modules[name]=mod;exec(compile(path.read_text(),str(path),'exec'),mod.__dict__);modules.append(mod)
 return modules

def fr(x):return Fr(float(x))
def exposed(f):
 ff=[[fr(x) for x in row] for row in f];edges={};dmax=1
 for i in range(len(f)):
  for j in range(i+1,len(f)):
   dx=ff[j][0]-ff[i][0];dy=ff[j][1]-ff[i][1]
   if dx==dy==0:continue
   u=[dy,-dx];values=[(p[0]-ff[i][0])*u[0]+(p[1]-ff[i][1])*u[1] for p in ff]
   dmax=max(dmax,len(f)-len(set(values))+1)
   if max(values)<=0:pass
   elif min(values)>=0:u=[-x for x in u];values=[-x for x in values]
   else:continue
   S=tuple(k for k,v in enumerate(values) if v==0)
   if len(S)==len(f):continue
   edges.setdefault(S,[str(x) for x in u])
 assert len(edges)>=3,'AFFINE_RANK_LESS_THAN_TWO'
 vertices=set()
 for a in edges:
  for b in edges:
   if a!=b and set(a)&set(b):vertices.add(tuple(sorted(set(a)&set(b))))
 faces=sorted(set(edges)|vertices);boundary=set().union(*(set(e) for e in edges));interior=[i for i in range(len(f)) if i not in boundary]
 return {'projection_kernel_max':dmax,'faces':[list(s) for s in faces],'edges':[{'support':list(s),'u':u} for s,u in sorted(edges.items())],'vertices':sorted(set().union(*(set(s) for s in vertices))),'interior':interior}

def coordinate_value(panel,k):
 n=len(panel['f']);m=max([len(s) for s in panel['topology']['faces'] if k in s],default=0)
 return min(Fr(1,n),Fr(1,m)-Fr(1,n) if m else Fr(2)),m

def synthetic():
 panels=[];cases=[];n=CFG['n']
 for si,seed in enumerate(CFG['seeds']):
  rng=np.random.Generator(np.random.PCG64(seed));base=rng.normal(size=(n,2));base=(base-base.mean(0))/base.std(0);inner=rng.normal(size=(20,2));inner=.3*inner/np.maximum(1,np.linalg.norm(inner,axis=1))[:,None];angle=np.arange(6)*2*np.pi/6+.113*(si+1);inside=np.vstack([np.column_stack([np.cos(angle),np.sin(angle)]),inner,np.zeros((1,2))]);xx=(np.arange(26)-13)/16;mass=np.vstack([np.column_stack([xx,(si/8)*xx]),[0.,-1.]])
  for form,f in [('gaussian',base),('interior',inside),('near_collinear',base@np.diag([1.,CFG['near_scale']])),('mass_face',mass)]:
   pid=f'{form}/{seed}';top=exposed(f);kfloor=26 if form in ['interior','mass_face'] else top['interior'][0];ks=[0,13,26] if form=='mass_face' else ([0,26] if form=='interior' else [top['vertices'][0],top['interior'][0]]);pair=[10,13] if form=='mass_face' else top['interior'][:2];assert len(pair)==2
   panel={'id':pid,'form':form,'seed':seed,'f':f.tolist(),'topology':top,'k_floor':kfloor,'contrast_pair':pair};panels.append(panel)
   def add(kind,tag=None,**parameters):cases.append({'id':pid+'/'+(tag or kind),'panel':pid,'form':form,'seed':seed,'kind':kind,**parameters})
   for k in ks:add('coordinate',f'coordinate{k}',k=k)
   add('contrast',k=pair[0],j=pair[1]);add('constant');add('centered',k=kfloor);add('isotropic')
   for lam in CFG['null_lambdas']:add('null_mix',f'null_lambda{lam:g}',k=pair[0],j=pair[1],lam=lam)
   vv=np.random.Generator(np.random.PCG64(seed+999)).normal(size=n);vv-=vv.mean();vv/=np.linalg.norm(vv);add('random_rank1',v=vv.tolist())
   for eps in CFG['epsilons']:
    for N in ['constant','isotropic']:add('perturb',f'perturb_{N}_{eps:g}',k=kfloor,epsilon=eps,N=N)
   if form=='mass_face':add('face_projector')
 assert len(panels)==12 and len(cases)==210
 return panels,cases

def matrix(case,n=27):
 kind=case['kind'];e=np.zeros(n);C=np.ones((n,n))/n
 if 'k' in case:e[case['k']]=1
 if kind=='coordinate':M=np.outer(e,e)
 elif kind=='contrast':
  v=e.copy();v[case['j']]=-1;M=np.outer(v,v)/2
 elif kind=='constant':M=C
 elif kind=='centered':v=e-1/n;M=np.outer(v,v)/(1-1/n)
 elif kind=='isotropic':M=np.eye(n)/n
 elif kind=='null_mix':v=e.copy();v[case['j']]=-1;M=case['lam']*C+(1-case['lam'])*np.outer(v,v)/2
 elif kind=='random_rank1':v=np.array(case['v']);M=np.outer(v,v)/(v@v)
 elif kind=='perturb':M=(1-case['epsilon'])*np.outer(e,e)+case['epsilon']*(C if case['N']=='constant' else np.eye(n)/n)
 elif kind=='face_projector':t=np.r_[np.ones(n-1),-(n-1)];M=(np.eye(n)-np.outer(t,t)/(n*(n-1)))/(n-1)
 else:raise ValueError(kind)
 return M/np.trace(M)

def extinction(panel,k):
 ff=[[fr(x) for x in row] for row in panel['f']];mean=[sum(p[d] for p in ff)/len(ff) for d in range(2)];u=[mean[d]-ff[k][d] for d in range(2)]
 if u==[0,0]:u=[Fr(1),Fr(0)] if len({p[0] for p in ff})>1 else [Fr(0),Fr(1)]
 return [str(x) for x in u]

def zero_direction(panel,k,j):
 ff=panel['f'];d=[fr(ff[k][i])-fr(ff[j][i]) for i in range(2)];u=[d[1],-d[0]]
 if u==[0,0]:return ['1','0']
 rr=[fr(p[0])*u[0]+fr(p[1])*u[1] for p in ff]
 if rr[k]==max(rr):u=[-x for x in u]
 return [str(x) for x in u]
