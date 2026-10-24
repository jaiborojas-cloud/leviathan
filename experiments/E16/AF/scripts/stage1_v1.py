#!/usr/bin/env python3
"""Predictores cortos; nunca calcula desenlaces ni geodésicas de radio Rmax."""
from common_v1 import *
import platform,resource

def main(out):
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);started=time.monotonic();gm,audit=imports();bases,states=generate(gm);write(out/'synthetic_states.json',{'generator':'PCG64','bases':bases,'states':states});records=[]
 for st in states:
  row={'state':st['id'],'seed':st['seed'],'target':st['target'],'scale':st['scale'],'K0':None,'abs_K0':None,'max_abs_K_small':None,'X_max':None,'X_angle':None,'min_j_over_r':None,'MP_K_error':None,'status':'INCONCLUSIVE','reason':''}
  try:
   M=np.array(st['M']);f=np.array(st['f']);geo=gm.Geometry(M,f);g=geo.jet([[0.,0.]])[0][0];angles=np.arange(CFG['predictor_angles'])*2*np.pi/CFG['predictor_angles'];sol=audit.jacsolve(geo,angles,CFG['predictor_rx']);grid=np.linspace(0,CFG['predictor_rho0'],CFG['predictor_rings']);z=sol.sol(grid).reshape(6,len(angles),len(grid));points=z[:2].transpose(1,2,0).reshape(-1,2);da,K=geo.eval(points);idx=int(np.argmax(abs(K)));K0=float(geo.eval([[0.,0.]])[1][0]);jr=sol.sol(CFG['predictor_rx']).reshape(6,len(angles))[4]/CFG['predictor_rx'];condition=np.maximum(1,abs(jr))/np.minimum(1,abs(jr));jmax=int(np.argmax(condition));mp_err=0.
   with mp.workdps(80):
    hp=MPGeometry(M,f)
    for p in [np.zeros(2),points[idx]]:
     km=hp.geometry([mp.mpf(float(x)) for x in p])[2];kf=float(geo.eval([p])[1][0]);mp_err=max(mp_err,float(abs(km-mp.mpf(kf))/max(1,abs(km))))
   ok=bool(np.linalg.eigvalsh(g)[0]>0 and min(jr)>0 and mp_err<=CFG['mp_K_tolerance'] and np.all(np.isfinite(condition)));row.update(K0=K0,abs_K0=abs(K0),max_abs_K_small=float(max(abs(K))),X_max=float(condition[jmax]),X_angle=float(angles[jmax]),min_j_over_r=float(min(jr)),MP_K_error=mp_err,status='PASS' if ok else 'INCONCLUSIVE',reason='' if ok else 'SPD_or_short_Jacobi_or_MP');print(st['id'],row['status'],row['K0'],flush=True)
  except Exception as e:row['reason']=type(e).__name__+':'+str(e)
  records.append(row);table(out/'predictors.csv',records)
 write(out/'predictors_sha256.json',{'predictors.csv':sha(out/'predictors.csv'),'synthetic_states.json':sha(out/'synthetic_states.json')});write(out/'summary.json',{'states':len(records),'passed':sum(q['status']=='PASS' for q in records),'long_geodesics_executed':0,'selection':'all 10 seeds x4 scales; no replacement','predictor_radius':CFG['predictor_rx'],'imported_geometry_sha256':CFG['geometry_sha256'],'imported_audit_sha256':CFG['audit_sha256'],'blocked_prohibited_reads':ACCESS['blocked']});write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'mpmath':mp.__version__,'config_sha256':sha(ROOT/'config.json'),'code_sha256':sha(Path(__file__))});write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/stage1_v1');main(p.parse_args().out)
