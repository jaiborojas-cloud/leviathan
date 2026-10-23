#!/usr/bin/env python3
"""Rachas independientes, KKT final, elegibilidad y repetición de Z."""
import csv,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
import mpmath as mp
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def point_hash(z):return hashlib.sha256(json.dumps(np.asarray(z,float).tolist(),separators=(',',':'),allow_nan=False).encode()).hexdigest()
def main():
 mp.mp.dps=120;cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in csv.DictReader((ROOT/name).open()):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
 for name in ['config.json','DESIGN_FROZEN.md','requirements.txt','freeze_manifest.csv']:assert git('show',f'18e371b:experiments/E16/Z/{name}')==(ROOT/name).read_bytes()
 assert git('show','145ede6:experiments/E16/Z/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allow={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/Z/') or p in allow for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 for p in ['experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T','experiments/E16/U','experiments/E16/V','experiments/E16/W','experiments/E16/X','experiments/E16/Y']:assert not git('diff',cfg['base_commit'],'--',p)
 paths=rows('paths.csv');vertices=rows('vertices.csv');gradients=rows('gradients.csv');monitor=rows('monitor.csv');sp=rows('spectra.csv');audits=rows('audits.csv');comp=rows('comparisons.csv');checks=rows('checks.csv');costs=rows('costs.csv')
 source=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));yp=list(csv.DictReader((ROOT.parent/'Y/results/run_v1/paths.csv').open()));assert len(paths)==12 and {r['path'] for r in paths}=={r['path'] for r in source}
 for p in paths:
  name=p['path'];old=next(r for r in source if r['path']==name);m=int(p['segments']);assert m==2*int(old['segments']);dim=2*(m-1);mm=[r for r in monitor if r['path']==name];assert mm and int(mm[0]['iteration'])==0;streak=0;last=None;stopped=False
  for r in mm:
   assert not stopped;iteration=int(r['iteration']);state=r['state'];verified=r['MP_verified']=='True';res=float(r['MP_kkt']) if r['MP_kkt'] else float('inf')
   if iteration>0:
    assert iteration%cfg['monitor_interval']==0
    if last is not None and iteration-last!=cfg['monitor_interval']:streak=0
    streak=streak+1 if verified and res<=cfg['KKT_tolerance'] else 0;last=iteration
   if state=='SCREENED_NONSTATIONARY':assert float(r['AD_kkt'])>cfg['AD_screen'] and r['MP_local_calls']==r['MP_global_calls']=='0' and not r['MP_kkt'] and not verified
   elif state in ['STATIONARY','NONSTATIONARY']:
    assert verified and (state=='STATIONARY')==(res<=cfg['KKT_tolerance']) and int(r['MP_local_calls'])==4*dim and r['MP_global_calls']=='1'
   else:assert state=='UNVERIFIED' and not verified
   stopped=streak>=cfg['required_streak'];assert int(r['streak'])==streak and (r['stop_requested']=='True')==stopped
  assert all(int(r['iteration'])<=int(p['iterations']) for r in mm) and int(p['iterations'])<=cfg['optimizer']['maxiter']
  vr=sorted([r for r in vertices if r['path']==name],key=lambda r:int(r['index']));assert len(vr)==m+1;z=np.array([[float(r['t']),float(r['s'])] for r in vr]);assert point_hash(z)==p['final_point_sha256'] and np.array_equal(z[[0,-1]],[[0,0],[1,0]])
  gg=[r for r in gradients if r['path']==name];assert len(gg)==dim;x=z[1:-1].reshape(-1);gm=np.array([float(r['MP_fd_2']) for r in gg]);box=np.array([[0.,1.],[-.25,.25]]*(m-1));assert np.all((x>=box[:,0])&(x<=box[:,1]));res=float(np.max(abs(x-np.clip(x-gm,box[:,0],box[:,1]))))/max(1,abs(float(p['final_length'])));assert abs(res-float(p['final_KKT']))<1e-12
  margin=float(np.min(np.minimum(x-box[:,0],box[:,1]-x)));assert abs(margin-float(p['box_margin']))<1e-15 and (p['interior']=='True')==(margin>cfg['boundary_margin'])
  if p['termination_route']=='PHYSICAL_SUSTAINED':assert stopped and p['native_success']=='False' and p['native_status']=='99' and mm[-1]['point_sha256']==p['final_point_sha256'] and int(mm[-1]['iteration'])==int(p['iterations'])
  elif p['termination_route'] in ['NATIVE_VERIFIED','NATIVE_CONTROL']:assert p['native_success']=='True'
  else:assert p['termination_route']=='UNVERIFIED_TERMINATION' and p['first_order_status']=='INCONCLUSIVE'
  if p['first_order_status']=='PASS':assert res<=cfg['KKT_tolerance'] and p['SPD']=='True' and p['unverified_monitors']=='0' and float(p['gradient_AD_error'])<=float(cfg['gradient_tolerance']) and float(p['gradient_step_error'])<=float(cfg['gradient_steps_tolerance'])
  eigen=[r for r in sp if r['path']==name];aa=[r for r in audits if r['path']==name]
  if p['spectral_status']=='PASS':
   size=dim if p['basis_route']=='SMALL_GRADIENT' else dim-1;assert len(eigen)==size and len(aa)==2
   ev=np.array([float(r['eigenvalue']) for r in eigen]);assert np.all(np.diff(ev)>=0);tau=cfg['spectral_relative_floor']*max(1,float(np.max(abs(ev))));assert float(p['minimum_mass'])==ev[0] and float(p['spectral_threshold'])==tau
   for r,value in zip(eigen,ev):assert float(r['threshold'])==tau and r['mode_class']==('NEGATIVE' if value< -tau else ('NEAR_ZERO' if abs(value)<=tau else 'POSITIVE'))
   a=next(r for r in aa if r['precision']=='120');witness=mp.mpf(a['mass_rayleigh_2'])< -mp.mpf(cfg['witness_tolerance'])*max(1,abs(mp.mpf(float(p['minimum_mass']))));assert (p['negative_MP_witness']=='True')==witness
  eligible=p['first_order_status']=='PASS' and p['spectral_status']=='PASS' and p['interior']=='True';assert (p['stationary_comparison_eligible']=='True')==eligible
  c=next(r for r in comp if r['path']==name);baseline=next(r for r in yp if r['path']==name and r['level']=='fine');assert c['Y_initial_minimum_mass']==baseline['minimum_mass'] and c['Z_final_minimum_mass']==p['minimum_mass'] and c['stationary_comparison_eligible']==p['stationary_comparison_eligible']
  cost=next(r for r in costs if r['path']==name);full=sum(int(r['MP_global_calls'])>0 for r in mm);assert int(cost['full_MP_monitors'])==full and int(cost['screened_monitors'])==sum(r['state']=='SCREENED_NONSTATIONARY' for r in mm)
  if p['spectral_status']=='PASS':assert int(cost['MP_local_calls'])==4*dim*(full+1) and int(cost['MP_global_calls'])==full+2+4*len(aa)
  assert int(cost['additional_AD_gradient_calls'])==len(mm)+1 and int(cost['MP120_SPD_edges'])==m and cost['solver_function_calls']==p['nfev'] and cost['solver_gradient_calls']==p['njev'] and cost['AD_hessian_calls']=='1' and cost['dense_arrays_archived']=='0';assert p['minimum_status']=='UNKNOWN'
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['paths']==len(paths)==12 and summary['monitors']==len(monitor) and summary['checks']==len(checks) and summary['first_order_pass']==sum(p['first_order_status']=='PASS' for p in paths) and summary['stationary_comparison_eligible']==sum(p['stationary_comparison_eligible']=='True' for p in paths) and summary['minimum_certificates']==0
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==11
 with tempfile.TemporaryDirectory(prefix='e16z-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget'];print('PASS_REPRODUCTION: once salidas idénticas; rachas filtradas, KKT, hashes, elegibilidad, espectros y costes reconstruidos; previas/T2-A intactos.')
if __name__=='__main__':main()
