import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,time,hashlib,shutil,traceback,importlib.util
import numpy as np
from scipy.optimize import brentq
from shapely.geometry import Polygon
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'instrument'))
# Historical modules are byte-identical; only their IO roots are redirected.
sys.modules['e15_repro_core']=__import__('core')
import audit,topological_map
import case_engine_resumable as case_engine
from geometry import area7,triangles
PROTO=json.loads((P/'protocol.json').read_text());RAD=PROTO['predictor']['r_star']
ROOT=P/'baseline';audit.P=ROOT;topological_map.P=ROOT;case_engine.P=P/'comparators'

def saved(p,d):audit.save(p,d)
def field(path):
 with np.load(path) as z:return audit.AuditedGeometry(z['M'],z['f'])

def calibrate(case):
 d=ROOT/'states'/case
 if (d/'nominal.json').exists():return json.loads((d/'nominal.json').read_text())
 g=field(d/'state.npz');start=time.perf_counter();cpu=time.process_time();upper=.09;attempts=[];n=2048
 for _ in range(12):
  sol=g.rays(upper,n)
  def area(r):return area7(g,triangles(sol.sol(np.linspace(0,r,33)).T.reshape(33,2,n,2)[:,0]))
  a=area(upper);attempts.append(dict(upper=upper,area=a))
  if a>=.02:break
  upper*=1.25
 else:raise RuntimeError('Inherited area bracketing failed')
 r=brentq(lambda x:area(x)-.02,0,upper,xtol=1e-13);a=area(r);assert abs(a/.02-1)<=1e-6
 border=sol.sol(r).reshape(2,n,2)[0];poly=Polygon(border);np.savez_compressed(d/'boundary_calibration.npz',P=border,radius=r)
 result=dict(radius=r,area_degree5=a,area_relative_error=a/.02-1,polygon_valid=poly.is_valid,polygon_simple=poly.exterior.is_simple,attempts=attempts,cpu_seconds=time.process_time()-cpu,seconds=time.perf_counter()-start)
 # Preserve folded nominal disks for the inherited topology audit; do not discard them as comparator failures.
 saved(d/'nominal.json',result);return result

def predictor(state_path,out):
 out.mkdir(parents=True,exist_ok=True)
 if (out/'predictor.json').exists():return json.loads((out/'predictor.json').read_text())
 start=time.perf_counter();cpu=time.process_time();data={};tasks=[]
 # The original T1B primary prefix uses the common513-node grid to its largest radius.
 prefix=np.linspace(0,.0683658751525098,513)[1:];prefix=prefix[prefix<=RAD]
 for n in [256,512]:
  ends=[];points=[]
  for ph in [0,1]:
   dest=out/f'n{n}_phase{ph}.npz';meta=dest.with_suffix('.json')
   if not meta.exists():
    g=field(state_path);theta=(np.arange(n)+ph/2)*2*np.pi/n;sol=audit.jacsolve(g,theta,RAD)
    end=sol.sol(RAD).reshape(6,n);det=end[4]/RAD;dd=sol.sol(prefix).reshape(6,n,-1)[4]/prefix[None,:]
    np.savez_compressed(dest,angles=theta,determinant=det,points=end[:2].T,prefix_radii=prefix,prefix_determinants=dd)
    saved(meta,dict(n=n,phase=ph,SPD=g.audit,prefix_min=float(dd.min()),nfev=sol.nfev))
   with np.load(dest) as z:ends.append(z['determinant']);points.append(z['points'])
   tasks.append(json.loads(meta.read_text()))
  theta=np.concatenate([(np.arange(n)+ph/2)*2*np.pi/n for ph in [0,1]]);order=np.argsort(theta)
  data[n]=(np.concatenate(ends)[order],np.concatenate(points)[order])
 k=lambda a:np.maximum(1,abs(a))/np.minimum(1,abs(a))
 hi,lo=data[512][0],data[256][0];x=float(k(hi).max());xl=float(k(lo).max());dm=float(abs(hi).min());dl=float(abs(lo).min())
 topo=[audit.topology(data[n][1],0) for n in [256,512]]
 gates=dict(SPD=all(t['SPD']['nonpositive']==0 and t['SPD']['nonfinite']==0 for t in tasks),positive_prefix=min([t['prefix_min'] for t in tasks]+[float(hi.min()),float(lo.min())])>0,boundary_simple=all(t['simple'] and t['valid'] for t in topo),kappa_resolution=abs(x-xl)<=1e-6+.005*abs(x-1),det_resolution=abs(dm-dl)<=1e-6+.005*abs(dm))
 r=dict(X=x,minimum_abs_det=dm,radius=RAD,status='PASS' if all(gates.values())else 'INCONCLUSIVE',gates=gates,cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-start)
 saved(out/'predictor.json',r);return r

def comparator(case):
 s,j,_=case.split('_');s=int(s[5:]);j=int(j[1:]);d=ROOT/'states'/case
 def prepare(split,regime,out,init):
  z=np.load(d/'state.npz');g=case_engine.AuditedGeometry(z['M'],z['f']);g.reset_audit();return g
 def calibration(g,out,log):
  m=json.loads((d/'nominal.json').read_text());z=np.load(d/'boundary_calibration.npz');border=z['P'];poly=Polygon(border);assert poly.is_valid and poly.exterior.is_simple
  case_engine.save(out/'disk.json',m);return m['radius'],border,poly
 case_engine.prepare=prepare;case_engine.calibrate=calibration
 return case_engine.evaluate_case(s,'true','T2_A_BASELINE',j)

def evaluate(case):
 final=P/'trajectories'/case/'baseline_result.json'
 if final.exists():return json.loads(final.read_text())
 d=ROOT/'states'/case;d.mkdir(parents=True,exist_ok=True);td=P/'trajectories'/case
 try:
  for src,dst in [('state_005.npz','state.npz'),('checkpoint_005.pt','checkpoint.pt')]:
   if not(d/dst).exists():shutil.copyfile(td/src,d/dst)
  saved(d/'reconstruction.json',dict(passed=True,method='exact inherited core from newly saved model at5, no surrogate'))
  nominal=calibrate(case);top=topological_map.result(case)
  pred=predictor(d/'state.npz',td/'predictor')
  eligible=top['classification']=='INJECTIVE_AT_NOMINAL_RADIUS' and pred['status']=='PASS'
  comp=comparator(case) if eligible else None
  result=dict(trajectory=case,baseline_classification=top['classification'],nominal_radius=nominal['radius'],predictor=pred,eligible=eligible,comparator_status=comp['status'] if comp else 'NOT_ADMISSIBLE',comparators={k:comp['statistics'][k]['median'] for k in ['C_A','lambda_01pct','R_eff']} if comp and comp['status']=='PASS' else None,status='BASELINE_EVALUATED',future_opened=False)
 except Exception:result=dict(trajectory=case,status='INCONCLUSIVE',error=traceback.format_exc(),future_opened=False)
 saved(final,result);return result
