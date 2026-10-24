#!/usr/bin/env python3
"""Control analítico y descriptivo de K, anterior a parte B."""
from common import *
import sympy as sp
import time,platform,resource

def symbolic_K(g,coords):
 inv=g.inv();C=[[[sum([]) for c in range(2)] for b in range(2)] for a in range(2)]
 for a in range(2):
  for b in range(2):
   for c in range(2):C[a][b][c]=(sp.diff(g[a,c],coords[b])+sp.diff(g[a,b],coords[c])-sp.diff(g[b,c],coords[a]))/2
 v=lambda b,c:sp.Matrix([C[a][b][c] for a in range(2)])
 R=sp.diff(g[0,1],coords[0],coords[1])-(sp.diff(g[0,0],coords[1],2)+sp.diff(g[1,1],coords[0],2))/2+(v(0,1).T*inv*v(0,1))[0]-(v(0,0).T*inv*v(1,1))[0]
 return sp.simplify(R/g.det())
def main():
 out=ROOT/'results/part_a_v1'
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);started=time.monotonic();data,k,ac,prep=prepare();R,phi=sp.symbols('R phi',positive=True);w=sp.Function('w')(phi);a,b,c=sp.symbols('a b c');cone=symbolic_K(sp.diag(1,R**2*w**2),(R,phi));constant=symbolic_K(sp.Matrix([[a,b],[b,c]]),(R,phi));write(out/'symbolic.json',{'sympy':sp.__version__,'cone_metric':'diag(1,R^2*w(phi)^2)','cone_K':str(cone),'constant_K':str(constant),'verified':cone==0 and constant==0,'premises':'sum linear immersion; product and quadratic degree-two homogeneous gradient immersion; SPD region only'})
 A=np.array(data['perspectives'][0],float);delta=np.array(data['perspectives'][1],float)-A;J=np.column_stack([delta,[-delta[1],delta[0]]]);records=[];summary=[]
 for kind in ['sum','product','quadratic']:
  metric=float_metric(ac,prep,kind);values=[];ok=True
  for t in np.linspace(*CFG['grid_t']):
   for s in np.linspace(*CFG['grid_s']):
    p=A+J@np.array([t,s]);row={'composition':kind,'t':t,'s':s,'p0':p[0],'p1':p[1],'status':'UNKNOWN','K_float':'','K_MP80':'','K_MP120':'','error_float':'','error_MP':'','reason':''}
    try:
     kval=float(metric.geometry(p)[2]);ks=[]
     for digits in CFG['precisions']:
      with mp.workdps(digits):ks.append(prep[digits][kind][2].geometry(np.array([mp.mpf(float(x)) for x in p],object))[2])
     with mp.workdps(120):e0=abs(mp.mpf(kval)-ks[-1])/max(1,abs(ks[-1]));e1=abs(ks[0]-ks[1])/max(1,abs(ks[1]));passed=e0<=CFG['K_float_tolerance'] and e1<=mp.mpf(CFG['K_MP_tolerance']);row.update(status='PASS' if passed else 'INCONCLUSIVE',K_float=kval,K_MP80=mp.nstr(ks[0],90),K_MP120=mp.nstr(ks[1],110),error_float=float(e0),error_MP=mp.nstr(e1,50));values.append(ks[-1]);ok=ok and passed
    except (ValueError,ZeroDivisionError) as e:row.update(status='NOT_SPD_OR_UNDEFINED',reason=str(e))
    records.append(row)
  summary.append({'composition':kind,'analytic_flat':bool((constant if kind=='sum' else cone)==0),'regular_points':len(values),'K_min_MP120':mp.nstr(min(values),110) if values else '', 'K_max_MP120':mp.nstr(max(values),110) if values else '', 'numerical_status':'PASS' if ok and values else 'INCONCLUSIVE'})
 table(out/'curvature.csv',records);table(out/'summary.csv',summary);write(out/'environment.json',{'python':platform.python_version(),'sympy':sp.__version__,'numpy':np.__version__,'mpmath':mp.__version__,'sources':CFG['sources']});write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024});print(summary,flush=True)
if __name__=='__main__':main()
