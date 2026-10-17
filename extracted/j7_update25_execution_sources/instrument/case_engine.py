"""B7/B8 orchestrator. B6 geometry.py and adaptive.py are immutable imports."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[key]='1'
import sys,pathlib,json,time,hashlib,traceback,resource,platform,importlib.metadata
import numpy as np
from scipy.optimize import brentq
from scipy.spatial import Delaunay
from shapely.geometry import Polygon
from shapely import contains_xy
from geometry import Geometry,triangles,area7
from adaptive import integrate
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P/'input/Leviathan_E15_B4_B5_repro/src'))
import torch,e15_repro_core as core
from sklearn.datasets import load_wine
torch.set_num_threads(1)
METRICS=['C_A','lambda_1pct','lambda_01pct','frac50','frac90','R_eff']

def save(path,data):
    # Preserve first-round infinite deltas as null in interoperable JSON.
    def clean(x):
        if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
        if isinstance(x,(tuple,list)): return [clean(v) for v in x]
        if isinstance(x,(float,np.floating)): return float(x) if np.isfinite(x) else None
        if isinstance(x,np.integer): return int(x)
        if isinstance(x,np.bool_): return bool(x)
        return x
    path.write_text(json.dumps(clean(data),indent=2,allow_nan=False))

class AuditedGeometry(Geometry):
    """Observe every metric evaluation without changing its numerical values."""
    def reset_audit(self):
        self.audit=dict(evaluations=0,min_eigenvalue=float('inf'),max_condition=0.,nonfinite=0,nonpositive=0,exceptions=[])
    def jet(self,pts):
        try: result=super().jet(pts)
        except Exception as e:
            self.audit['exceptions'].append(repr(e)); raise
        g=result[0]; eig=np.linalg.eigvalsh(g)
        self.audit['evaluations']+=len(g)
        self.audit['nonfinite']+=int((~np.isfinite(eig)).sum())
        self.audit['nonpositive']+=int((eig[:,0]<=0).sum())
        self.audit['min_eigenvalue']=min(self.audit['min_eigenvalue'],float(eig[:,0].min()))
        self.audit['max_condition']=max(self.audit['max_condition'],float((eig[:,1]/eig[:,0]).max()))
        if self.audit['nonfinite'] or self.audit['nonpositive']: raise FloatingPointError('nonfinite or non-SPD metric')
        return result

def prepare(split,regime,out,init=0):
    path=P/f'checkpoints/wine_split{split}_j{init}_{regime}.pt'
    checkpoint=torch.load(path,weights_only=False); assert checkpoint['target_train_acc']>=.99; model=core.WineMLP();model.load_state_dict(checkpoint['model_state_dict'])
    wine=load_wine();ids=checkpoint['val_indices']; x=(wine.data-checkpoint['scaler_mean'])/checkpoint['scaler_scale']
    X=torch.tensor(x[ids]); y=torch.tensor(wine.target[ids])
    with torch.no_grad(): acc=(model(X).argmax(1)==y).double().mean().item()
    assert acc==checkpoint['val_true_acc']
    R,U,f=core.make_geom_state(model,X,y); M=core.subset_M(R,U,[0,1,2])
    geo=AuditedGeometry(M.numpy(),f.numpy());geo.reset_audit()
    ka=float(core.curvature_fast_single(torch.zeros(2),M,f));kn=float(geo.eval(np.zeros(2))[1][0])
    assert abs(ka-kn)/max(abs(ka),1e-12)<1e-6
    np.savez(out/'state.npz',M=M.numpy(),f=f.numpy())
    np.savez(out/'coalitions.npz',f=f.numpy(),**{f'M_{mask}':core.subset_M(R,U,[i for i in range(3) if mask&(1<<i)]).numpy() for mask in range(1,8)})
    save(out/'checkpoint.json',dict(split=split,init=init,regime=regime,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),split_seed=checkpoint['split_seed'],init_seed=checkpoint['init_seed'],batch_seed=checkpoint['batch_seed'],random_label_seed=checkpoint['random_label_seed'],steps=checkpoint['steps'],val_acc=acc,K0_AD=ka,K0_Gauss=kn,model_retrained=(init!=0)))
    return geo

def calibrate(geo,out,log):
    start=time.perf_counter();upper=.09;attempts=[];nt=2048
    for attempt in range(12):
        sol=geo.rays(upper,nt)
        def calc(r):
            rings=sol.sol(np.linspace(0,r,33)).T.reshape(33,2,nt,2)[:,0]
            return area7(geo,triangles(rings))
        A=calc(upper);attempts.append(dict(upper=upper,area=A,nfev=sol.nfev))
        if A>=.02: break
        upper*=1.25
    else: raise RuntimeError('Area target was not bracketed in 12 deterministic expansions')
    r=brentq(lambda r:calc(r)-.02,0,upper,xtol=1e-13)
    A=calc(r);assert abs(A/.02-1)<=1e-6
    border=sol.sol(r).reshape(2,nt,2)[0]; poly=Polygon(border)
    assert poly.is_valid and poly.exterior.is_simple
    np.savez(out/'boundary_2048.npz',P=border,radius=r)
    disk=dict(radius=r,area_degree5=A,area_relative_error=A/.02-1,angular=nt,seconds=time.perf_counter()-start,bracketing_attempts=attempts,geometry_audit=geo.audit.copy(),polygon_valid=poly.is_valid,polygon_simple=poly.exterior.is_simple)
    save(out/'disk.json',disk);log('DISK '+json.dumps(disk))
    return r,border,poly

def evaluate_case(split,regime,stage,init=0):
    out=P/f'cases/split{split}_init{init}_{regime}';out.mkdir(parents=True,exist_ok=True)
    if (out/'classification.json').exists(): return json.loads((out/'classification.json').read_text())
    start=time.perf_counter();cpu=time.process_time(); rows=[]
    with (out/'execution.log').open('w',buffering=1) as lf:
        def log(s): lf.write(s+'\n');print(f'[{stage} split{split} init{init} {regime}] {s}',flush=True)
        try:
            geo=prepare(split,regime,out,init);r,border,poly=calibrate(geo,out,log)
            for nt,nr in [(64,32),(96,48),(128,64)]:
                for phase_id in [0,1]:
                    phase=phase_id*np.pi/nt;name=f'{nt}x{nr}_phase{phase_id}';t0=time.perf_counter();c0=time.process_time();geo.reset_audit()
                    sol=geo.rays(r,nt,phase)
                    rings=sol.sol(np.linspace(0,r,nr+1)).T.reshape(nr+1,2,nt,2)[:,0]
                    interior=np.concatenate([np.zeros((1,2)),rings[1:-1].reshape(-1,2)])
                    interior=interior[contains_xy(poly,interior[:,0],interior[:,1])]
                    pts=np.concatenate([border,interior]);dt=Delaunay(pts);tr=pts[dt.simplices]
                    inside=contains_xy(poly,tr.mean(1)[:,0],tr.mean(1)[:,1]);tr=tr[inside]
                    bad=sum(not poly.covers(Polygon(t)) for t in tr);assert bad==0
                    a=tr[:,1]-tr[:,0];b=tr[:,2]-tr[:,0];chart_area=np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0]).sum()/2
                    assert abs(chart_area/poly.area-1)<1e-10
                    def progress(m): log(f"{name} round={m['round']} cells={m['cells']} C_A={m['C_A']:.12g} energy_error={m['energy_error_est']:.4g} change={m['relative_change_C']:.4g} conc_change={m['concentration_change']:.4g}")
                    m,h,cells,q=integrate(geo,tr,verbose=progress)
                    assert np.all(np.isfinite(q)) and np.all(q[:,0]>0)
                    converged=len(h)>=2 and all(v['energy_error_est']<.0005 and v['relative_change_C']<.0005 and v['concentration_change']<.001 for v in h[-2:])
                    order=np.argsort(-q[:,1]); idx=np.unique(np.r_[order[:128],np.linspace(0,len(q)-1,min(256,len(q)),dtype=int)])
                    np.savez_compressed(out/(name+'_witness.npz'),triangles=cells[idx],quadrature=q[idx],indices=idx)
                    row=dict(split=split,init=init,regime=regime,source=name,nt=nt,nr=nr,phase=phase,boundary_rays=2048,radius=r,**m,area_absolute_error=m['area']-.02,area_relative_error=m['area']/.02-1,internally_converged=converged,geometry_audit=geo.audit.copy(),seconds=time.perf_counter()-t0,cpu_seconds=time.process_time()-c0,base_triangles=len(tr),triangulation_crossing_count=bad,chart_area_relative_error=chart_area/poly.area-1,quadrature_sha256=hashlib.sha256(q.tobytes()).hexdigest(),triangles_sha256=hashlib.sha256(cells.tobytes()).hexdigest(),history=h)
                    save(out/(name+'.json'),row);rows.append(row)
                    del cells,q
            stats={}
            for k in METRICS:
                v=np.array([d[k] for d in rows]);stats[k]=dict(values=v.tolist(),median=np.median(v),min=v.min(),max=v.max(),relative_range=np.ptp(v)/np.median(v),absolute_range=np.ptp(v),CV=np.std(v,ddof=0)/np.mean(v))
            gates=dict(C_A=stats['C_A']['relative_range']<.005,lambda_1pct=stats['lambda_1pct']['absolute_range']<.005,lambda_01pct=stats['lambda_01pct']['absolute_range']<.005,frac50=stats['frac50']['absolute_range']<1e-5,frac90=stats['frac90']['absolute_range']<1e-5,R_eff=stats['R_eff']['relative_range']<.005)
            internal=all(d['internally_converged'] for d in rows)
            status='INCONCLUSIVE' if not internal else ('PASS' if all(gates.values()) else 'FAIL')
            result=dict(stage=stage,split=split,init=init,regime=regime,status=status,source_count=len(rows),all_sources_internally_converged=internal,primary_CA_status='INCONCLUSIVE' if not internal else ('PASS' if gates['C_A'] else 'FAIL'),gates=gates,statistics=stats,seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,numerical_exceptions=[],area_relative_error_range=[min(d['area_relative_error'] for d in rows),max(d['area_relative_error'] for d in rows)])
        except Exception as e:
            log(traceback.format_exc());result=dict(stage=stage,split=split,init=init,regime=regime,status='INCONCLUSIVE',source_count=len(rows),seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,numerical_exceptions=[repr(e)],traceback=traceback.format_exc())
        save(out/'classification.json',result);log('CLASSIFICATION '+json.dumps(result,default=lambda v:v.item() if isinstance(v,np.generic) else str(v)));return result
