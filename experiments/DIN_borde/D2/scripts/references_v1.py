"""Referencias MP independientes, con TV exacta en coordenadas y contrastes."""
from common_v1 import *

def mm(x):
 if isinstance(x,(Fr,str)):
  v=Fr(x);return mp.mpf(v.numerator)/v.denominator
 return mp.mpf(float(x))

def projections(panel,u):
 uu=[Fr(x) if isinstance(x,str) else fr(x) for x in u];r=[fr(p[0])*uu[0]+fr(p[1])*uu[1] for p in panel['f']];top=max(r);return [x-top for x in r]

def bisect(h,hi,positive_first=True):
 lo=mp.mpf(0);hi=mp.mpf(hi)
 for _ in range(512):
  if h(hi)<=0:break
  hi*=2
 else:raise ArithmeticError('ROOT_BRACKET_FAILED')
 for _ in range(180):
  mid=(lo+hi)/2
  if h(mid)>0:lo=mid
  else:hi=mid
 return (lo+hi)/2

def coordinate_tv(rr,k):
 n=len(rr);m=rr.count(Fr(0))
 if rr[k]==0:return mm(Fr(1,m)-Fr(1,n)),[]
 if n*rr[k]<=sum(rr):return mp.mpf(1)/n,[]
 r=[mm(x) for x in rr]
 def probabilities(s):
  z=[mp.exp(x*s) for x in r];den=sum(z);return [x/den for x in z]
 root=bisect(lambda s:r[k]-mp.fdot(probabilities(s),r),1/max(-min(r),mp.mpf('1e-80')));peak=probabilities(root)[k]
 return 2*peak-mp.mpf(1)/n,[root]

def contrast_tv(rr,k,j):
 n=len(rr);m=rr.count(Fr(0))
 if rr[k]==rr[j]:return mp.mpf(0),[]
 if max(rr[k],rr[j])==0:return 1/(m*mp.sqrt(2)),[]
 r=[mm(x) for x in rr];lo=min(r[k],r[j]);delta=abs(r[k]-r[j])
 def h(s):
  z=[mp.exp(v*s) for v in r];return lo+delta/(-mp.expm1(-delta*s))-mp.fdot(z,r)/sum(z)
 root=bisect(h,1/max(-min(r),delta));Z=sum(mp.exp(v*root) for v in r);peak=mp.exp(max(r[k],r[j])*root)*(-mp.expm1(-delta*root))/Z/mp.sqrt(2)
 return 2*peak,[root]

def random_vector(case):
 v=[mm(x) for x in case['v']];norm=mp.sqrt(mp.fdot(v,v));return [x/norm for x in v]

def norm(case,beta):
 n=len(beta);kind=case['kind'];k=case.get('k',0)
 if kind=='coordinate':return abs(beta[k])
 if kind=='centered':return abs(beta[k]-sum(beta)/n)/mp.sqrt(1-mp.mpf(1)/n)
 if kind=='constant':return abs(sum(beta))/mp.sqrt(n)
 if kind=='contrast':return abs(beta[k]-beta[case['j']])/mp.sqrt(2)
 if kind=='null_mix':return mp.sqrt(mm(case['lam'])*sum(beta)**2/n+(1-mm(case['lam']))*(beta[k]-beta[case['j']])**2/2)
 if kind=='isotropic':return mp.sqrt(mp.fdot(beta,beta)/n)
 if kind=='perturb':
  residual=sum(beta)**2/n if case['N']=='constant' else mp.fdot(beta,beta)/n;e=mm(case['epsilon']);return mp.sqrt((1-e)*beta[k]**2+e*residual)
 if kind=='random_rank1':return abs(mp.fdot(random_vector(case),beta))
 if kind=='face_projector':
  t=[mp.mpf(1)]*(n-1)+[mp.mpf(-(n-1))];c=mp.fdot(t,beta)/(n*(n-1));return mp.sqrt(sum((x-c*y)**2 for x,y in zip(beta,t))/(n-1))
 raise ValueError(kind)

MPGL={}
def gl(n):
 if n not in MPGL:
  with mp.workdps(80):
   from numpy.polynomial.legendre import leggauss
   xx=[];ww=[]
   for value in leggauss(n)[0]:
    x=mm(value)
    for _ in range(8):
     a=mp.mpf(1);b=x
     for k in range(2,n+1):a,b=b,((2*k-1)*x*b-(k-1)*a)/k
     derivative=n*(x*b-a)/(x*x-1);delta=b/derivative;x-=delta
     if abs(delta)<mp.mpf('1e-75'):break
    a=mp.mpf(1);b=x
    for k in range(2,n+1):a,b=b,((2*k-1)*x*b-(k-1)*a)/k
    derivative=n*(x*b-a)/(x*x-1);xx.append(x);ww.append(2/((1-x*x)*derivative**2))
   MPGL[n]=(xx,ww)
 return MPGL[n]

def direct(case,rr,archive=lambda *args:None,label='parts'):
 r=[mm(x) for x in rr];n=len(r);support=[i for i,x in enumerate(rr) if x==0];gaps=[-v for v in r if v<0];m=len(support);tol=mp.mpf('1e-20');U=mp.log(2*len(gaps)/(m*tol))/min(gaps);cuts=[mp.mpf(0),U]
 for gap in gaps:cuts.extend(x/gap for x in [1,8,32] if x/gap<U)
 cuts=sorted(set(cuts));v=random_vector(case) if case['kind']=='random_rank1' else None
 def beta(s):
  a=[mp.exp(x*s) for x in r];den=sum(a);a=[x/den for x in a];mean=mp.fdot(a,r);return [x*(d-mean) for x,d in zip(a,r)]
 if v is not None:
  roots=[]
  for a,b in zip(cuts[:-1],cuts[1:]):
   ts=[a+(b-a)*i/8 for i in range(9)];ds=[mp.fdot(v,beta(t)) for t in ts]
   for lo,hi,fl,fh in zip(ts[:-1],ts[1:],ds[:-1],ds[1:]):
    if fl*fh<0:
     for _ in range(160):
      mid=(lo+hi)/2;fm=mp.fdot(v,beta(mid))
      if fm*fl>0:lo=mid;fl=fm
      else:hi=mid
     roots.append((lo+hi)/2)
  cuts=sorted(set(cuts+roots))
 else:roots=[]
 values=[];totals=[mp.mpf(0),mp.mpf(0)]
 for a,b in zip(cuts[:-1],cuts[1:]):
  row=[]
  for order in [16,32]:
   ts,ws=gl(order);mid=(a+b)/2;half=(b-a)/2;value=half*mp.fsum(w*(abs(mp.fdot(v,beta(mid+half*t))) if v is not None else norm(case,beta(mid+half*t))) for t,w in zip(ts,ws));row.append(value);totals[len(row)-1]+=value
  values.append([float(a),float(b),float(row[0]),float(row[1])])
 archive(label,np.array(values));total_low,total_high=totals;tail=2*sum(mp.exp(-gap*U) for gap in gaps)/m;error=abs(total_high-total_low);threshold=mp.mpf('1e-12')+mp.mpf('1e-8')*abs(total_high)
 return {'value':float(total_high+tail),'MP_value':mp.nstr(total_high+tail,80),'reference_error':float(error+tail),'status':'PASS' if error<=threshold else 'INCONCLUSIVE','method':'MP80_GL16_32','cut_count':len(cuts),'root_count':len(roots),'roots':[mp.nstr(x,60) for x in roots],'U':float(U),'tail_bound':float(tail)}

def direction(panel,case,u,archive=lambda *args:None,label='parts'):
 with mp.workdps(80):
  rr=projections(panel,u);kind=case['kind'];roots=[]
  if kind in ['coordinate','centered'] or kind=='perturb' and case['N']=='constant':
   value,roots=coordinate_tv(rr,case['k'])
   if kind=='centered':value/=mp.sqrt(1-mp.mpf(1)/len(rr))
   if kind=='perturb':value*=mp.sqrt(1-mm(case['epsilon']))
  elif kind in ['contrast','null_mix']:
   value,roots=contrast_tv(rr,case['k'],case['j'])
   if kind=='null_mix':value*=mp.sqrt(1-mm(case['lam']))
  elif kind=='constant':value=mp.mpf(0)
  else:return direct(case,rr,archive,label)
  return {'value':float(value),'MP_value':mp.nstr(value,80),'reference_error':0.,'status':'PASS','method':'analytic_TV_MP80','roots':[mp.nstr(x,60) for x in roots],'root_count':len(roots),'cut_count':0,'U':None,'tail_bound':0.}

def endpoint_bound(panel,case):
 n=len(panel['f']);zero=[mp.mpf(1)/n]*n;values=[]
 for S in panel['topology']['faces']:
  delta=[(mp.mpf(1)/len(S) if i in S else mp.mpf(0))-zero[i] for i in range(n)];values.append(norm(case,delta))
 return min(values)

def global_reference(panel,case,archive=lambda *args:None):
 with mp.workdps(80):
  kind=case['kind'];n=len(panel['f']);known=None;u=None
  if kind in ['coordinate','centered','perturb']:
   base,m=coordinate_value(panel,case['k'])
   if kind=='coordinate':known=mm(base)
   elif kind=='centered':known=mm(base)/mp.sqrt(1-mp.mpf(1)/n)
   elif case['N']=='constant':known=mm(base)*mp.sqrt(1-mm(case['epsilon']))
   if known is not None:
    if base==Fr(1,n):u=extinction(panel,case['k'])
    else:u=next(e['u'] for e in panel['topology']['edges'] if case['k'] in e['support'] and len(e['support'])==m)
  if kind in ['contrast','null_mix']:known=mp.mpf(0);u=zero_direction(panel,case['k'],case['j'])
  if kind=='constant':known=mp.mpf(0);u=['1','0']
  if kind=='face_projector':known=mp.mpf(0);u=max(panel['topology']['edges'],key=lambda e:len(e['support']))['u']
  if panel['form']=='mass_face' and (kind=='isotropic' or kind=='perturb' and case['N']=='isotropic'):
   known=1/(n*mp.sqrt(n-1)) if kind=='isotropic' else mp.sqrt(1-mm(case['epsilon'])+mm(case['epsilon'])/(n-1))/n;u=max(panel['topology']['edges'],key=lambda e:len(e['support']))['u']
  lower=known if known is not None else endpoint_bound(panel,case)
  if u is None:u=max(panel['topology']['edges'],key=lambda e:len(e['support']))['u'] if panel['form']=='mass_face' else extinction(panel,panel['k_floor'])
  witness=direction(panel,case,u,archive,'upper_reference_parts');upper=known if known is not None else mm(witness['value'])
  return {'known_exact':known is not None,'exact':float(known) if known is not None else None,'exact_MP':mp.nstr(known,80) if known is not None else None,'lower':float(lower),'upper':float(upper),'upper_u':u,'upper_witness':witness,'status':witness['status']}
