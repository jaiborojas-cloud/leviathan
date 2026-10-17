"""Exact DOP853 accepted-step checkpointing, restricted to inherited no-event dense rays calls."""
from pathlib import Path
import hashlib,json,os,time,zipfile
import numpy as np,cloudpickle
from scipy.integrate import DOP853,OdeSolution
from scipy.integrate._ivp.ivp import OdeResult
class IntegrationPaused(BaseException):pass
class Driver:
 def __init__(self,root,identity,max_new_steps=128,every=32,on_commit=None):
  self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.identity=identity;self.limit=max_new_steps;self.every=every;self.on_commit=on_commit
 def __call__(self,fun,t_span,y0,method,rtol,atol,dense_output):
  assert method=='DOP853' and dense_output and t_span[0]==0 and rtol==2e-10 and atol==2e-12
  signature=dict(identity=self.identity,t_span=list(t_span),y0_sha256=hashlib.sha256(np.asarray(y0).tobytes()).hexdigest(),method=method,rtol=rtol,atol=atol,dense_output=True)
  key=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()[:20];d=self.root/key;d.mkdir(exist_ok=True)
  metas=sorted(d.glob('step_*.json'))
  if metas:
   m=json.loads(metas[-1].read_text());z=d/m['archive'];assert hashlib.sha256(z.read_bytes()).hexdigest()==m['sha256']
   with zipfile.ZipFile(z)as a:b=cloudpickle.loads(a.read('integration.pkl'))
   assert b['signature']==signature
   # NumPy pickling does not preserve ndarray view aliasing. Restore SciPy's exact workspace view.
   solver=b['solver'];assert np.array_equal(solver.K,solver.K_extended[:solver.n_stages+1])
   solver.K=solver.K_extended[:solver.n_stages+1]
  else:
   solver=DOP853(fun,t_span[0],y0,t_span[1],rtol=rtol,atol=atol)
   b=dict(signature=signature,solver=solver,ts=[t_span[0]],ys=[np.asarray(y0).copy()],interpolants=[],cpu_seconds=0.,wall_seconds=0.)
  solver=b['solver'];start_steps=len(b['interpolants']);start=time.perf_counter();cpu=time.process_time();last_saved=start_steps
  def commit():
   nonlocal start,cpu,last_saved
   b['cpu_seconds']+=time.process_time()-cpu;b['wall_seconds']+=time.perf_counter()-start
   n=len(b['interpolants']);name=f'step_{n:08d}.zip';z=d/name;tmp=z.with_suffix('.tmp')
   with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)as a:a.writestr('integration.pkl',cloudpickle.dumps(b))
   os.replace(tmp,z);m=dict(archive=name,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),steps=n,t=float(solver.t),target=float(solver.t_bound),nfev=solver.nfev,status=solver.status,cpu_seconds=b['cpu_seconds'],wall_seconds=b['wall_seconds'],signature=signature)
   (d/f'step_{n:08d}.json').write_text(json.dumps(m,indent=2))
   if self.on_commit:self.on_commit(z,d/f'step_{n:08d}.json',m)
   print('ODE_CHECKPOINT',n,solver.t,solver.nfev,solver.status,flush=True);last_saved=n;start=time.perf_counter();cpu=time.process_time()
  while solver.status=='running':
   message=solver.step()
   if solver.status=='failed':
    commit();raise RuntimeError(message)
   interpolant=solver.dense_output();b['interpolants'].append(interpolant);b['ts'].append(solver.t);b['ys'].append(solver.y.copy())
   n=len(b['interpolants'])
   if n%self.every==0 or solver.status!='running' or n-start_steps>=self.limit:commit()
   if solver.status=='running' and n-start_steps>=self.limit:raise IntegrationPaused('Accepted-step budget reached; exact solver state persisted; not numerical or geometric failure')
  if solver.status=='failed':raise RuntimeError('Previously persisted integrator failure')
  return OdeResult(t=np.array(b['ts']),y=np.stack(b['ys'],axis=1),sol=OdeSolution(b['ts'],b['interpolants']),t_events=None,y_events=None,nfev=solver.nfev,njev=solver.njev,nlu=solver.nlu,status=0,message='The solver successfully reached the end of the integration interval.',success=True)
