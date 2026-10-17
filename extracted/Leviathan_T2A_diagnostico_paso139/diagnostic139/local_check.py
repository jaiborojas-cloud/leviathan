exec(open('diagnostic139/diagnose.py').read().split('chosen=')[0])
from scipy.integrate import solve_ivp
import time
# Independent mpmath RHS, fixed 120 decimal digits; diagnostic copies only.
mp.mp.dps=120;MM=mp.matrix(g.M.tolist());FF=mp.matrix(g.f.tolist())
def rhs(t,y):
 P=mp.matrix(y[:2].tolist());V=mp.matrix(y[2:].tolist());l=FF*P;w=mp.matrix([mp.exp(x-max(l)) for x in l]);w=w/sum(w);mu=FF.T*w
 JJ=mp.matrix([[w[k]*(FF[k,a]-mu[a]) for a in range(2)] for k in range(len(w))]);zz=[sum((FF[k,a]-mu[a])*V[a] for a in range(2)) for k in range(len(w))];z2=sum(w[k]*zz[k]**2 for k in range(len(w)));HH=mp.matrix([w[k]*(zz[k]**2-z2) for k in range(len(w))]);aa=mp.lu_solve(JJ.T*MM*JJ,-JJ.T*MM*HH)
 return np.r_[y[2:],[float(x) for x in aa]]
results=[]
for i in [1775,1776]:
 y=np.r_[p[i],v[i]];t=float(s['t']);h=float(s['h_abs']);sols=[]
 for fun in [fast.single_rhs,rhs]:
  start=__import__('time').perf_counter();sol=solve_ivp(fun,(t,t+h),y,method='DOP853',rtol=2e-10,atol=2e-12,first_step=h,dense_output=True);sols.append(sol);print(i,sol.success,sol.nfev,flush=True)
 grid=np.linspace(t,t+h,513);a,b=[sol.sol(grid) for sol in sols];err=float(np.max(abs(a-b)/(2e-12+2e-10*abs(b))))
 results.append(dict(ray=i,t0=t,t1=t+h,success=[x.success for x in sols],nfev=[x.nfev for x in sols],dense_scaled_error=err,pass_local=bool(err<=1 and all(x.success for x in sols))))
(out/'local_checks.json').write_text(json.dumps(results,indent=2));print(results)
