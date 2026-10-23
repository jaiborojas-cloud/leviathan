#!/usr/bin/env python3
"""Verificación escalar independiente de X y reproducción completa."""
import csv,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
import mpmath as mp
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def main():
 mp.mp.dps=120;cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in csv.DictReader((ROOT/name).open()):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
 for name in ['config.json','DESIGN_FROZEN.md','requirements.txt','freeze_manifest.csv']:assert git('show',f'e773c9d:experiments/E16/X/{name}')==(ROOT/name).read_bytes()
 assert git('show','9acbe96:experiments/E16/X/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allow={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/X/') or p in allow for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 for p in ['experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T','experiments/E16/U','experiments/E16/V','experiments/E16/W']:assert not git('diff',cfg['base_commit'],'--',p)
 paths=rows('paths.csv');sp=rows('spectra.csv');ds=rows('directions.csv');aa=rows('audits.csv');trials=rows('trials.csv');pairs=rows('pairs.csv');checks=rows('checks.csv');costs=rows('costs.csv');comp=rows('comparisons.csv')
 old=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));wa=list(csv.DictReader((ROOT.parent/'W/results/run_v1/audits.csv').open()));assert len(paths)==12 and {r['path'] for r in paths}=={r['path'] for r in old}
 def sign(x):
  tol=mp.mpf(cfg['sign_tolerance']);return 'DESCENT' if x< -tol else ('INCREASE' if x>tol else 'WITHIN_TOLERANCE')
 for p in paths:
  name=p['path'];dim=2*(int(p['segments'])-1);small=p['route']=='SMALL_GRADIENT';spect={}
  for block,size in [('full',dim),('restricted',dim if small else dim-1)]:
   rs=[r for r in sp if r['path']==name and r['block']==block];assert len(rs)==size and [int(r['index']) for r in rs]==list(range(size));vals=np.array([float(r['eigenvalue']) for r in rs]);assert np.all(np.diff(vals)>=0);tau=cfg['spectral_relative_floor']*max(1,float(np.max(abs(vals))));assert all(float(r['threshold'])==tau for r in rs)
   for r,v in zip(rs,vals):assert r['mode_class']==('NEGATIVE' if v< -tau else ('NEAR_ZERO' if abs(v)<=tau else 'POSITIVE'))
   spect[block]=vals
  full,reduced=spect['full'],spect['restricted'];scale=max(1,float(np.max(abs(full))));error=float(np.max(abs(full-reduced))) if small else max(0,float(np.max(full[:-1]-reduced)),float(np.max(reduced-full[1:])))
  c=next(r for r in comp if r['path']==name);assert abs(float(c['interlacing_error'])-error/scale)<1e-15 and error/scale<=float(cfg['eigen_tolerance']);assert float(c['restricted_min'])==float(p['restricted_min'])==reduced[0];tau=cfg['spectral_relative_floor']*max(1,float(np.max(abs(reduced))));assert float(c['restricted_threshold'])==float(p['restricted_threshold'])==tau
  assert int(c['restricted_negative'])==np.sum(reduced< -tau) and int(c['restricted_near_zero'])==np.sum(abs(reduced)<=tau)
  w=next(r for r in wa if r['path']==name and r['family']=='projected' and r['precision']=='120');assert c['W_projected_curvature']==w['curvature_2'] and reduced[0]<=float(w['curvature_2'])+1e-8*max(1,abs(reduced[0]),abs(float(w['curvature_2'])))
  dd=[r for r in ds if r['path']==name];aud=[r for r in aa if r['path']==name];tt=[r for r in trials if r['path']==name];pp=[r for r in pairs if r['path']==name];assert len(dd)==len(aud)==2 and len(tt)==6 and len(pp)==3
  assert len({r['raw_vector_sha256'] for r in dd})==1
  for d in dd:
   assert abs(mp.mpf(d['unit_norm'])-1)<mp.mpf('1e-35') and mp.mpf(d['orthogonality_error'])<=mp.mpf(cfg['mp_orthogonality_tolerance'])
   a=next(r for r in aud if r['precision']==d['precision']);der=mp.mpf(a['derivative_2']);q=mp.mpf(a['curvature_2']);s=mp.mpf(d['archive_slope']);ray=mp.mpf(float(d['ad_rayleigh']));assert abs(abs(der-s)/max(1,abs(der),abs(s))-mp.mpf(a['gradient_error']))<mp.mpf('1e-35');assert abs(abs(q-ray)/max(1,abs(q),abs(ray))-mp.mpf(a['rayleigh_error']))<mp.mpf('1e-25')
  audit120=next(r for r in aud if r['precision']=='120');resolved=p['diagnostics']=='PASS' and reduced[0]< -tau and mp.mpf(audit120['curvature_2'])< -mp.mpf(tau);assert (p['resolved_negative']=='True')==resolved
  for step in cfg['steps']:
   signed=[r for r in tt if r['step']==step];assert len(signed)==2 and {r['sign'] for r in signed}=={'-1','1'};pair=next(r for r in pp if r['step']==step);complete=all(r['state']=='VALID' for r in signed);assert (pair['state']=='VALID')==complete
   for r in signed:
    if r['state']=='VALID':
     delta=mp.mpf(r['delta']);assert r['length_change']==sign(delta) and r['spd']=='True';lo,hi=float(r['geometry_lower']),float(r['geometry_upper']);assert 0<=lo<=hi and r['geometry_status']==('CHANGED' if lo>cfg['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=cfg['geometry_tolerance'] else 'UNRESOLVED'));assert abs(delta-mp.mpf(r['linear_prediction'])-mp.mpf(r['quadratic_prediction'])-mp.mpf(r['taylor_residual']))<mp.mpf('1e-35')
    elif r['state'] in ['INFEASIBLE','DEGENERATE']:assert r['length_change']=='UNKNOWN' and not r['length']
   if complete:
    dm=mp.mpf(next(r['delta'] for r in signed if r['sign']=='-1'));dp=mp.mpf(next(r['delta'] for r in signed if r['sign']=='1'));assert abs(mp.mpf(pair['even_change'])-(dp+dm)/2)<mp.mpf('1e-35') and abs(mp.mpf(pair['odd_change'])-(dp-dm)/2)<mp.mpf('1e-35');assert pair['even_sign']==sign((dp+dm)/2) and int(pair['descent_count'])==int(sign(dm)=='DESCENT')+int(sign(dp)=='DESCENT')
  assert int(p['valid_trials'])==sum(r['state']=='VALID' for r in tt) and int(p['infeasible_trials'])==sum(r['state']=='INFEASIBLE' for r in tt) and p['minimum_status']=='UNKNOWN';assert int(p['negative_even_pairs'])==sum(r['even_sign']=='DESCENT' for r in pp) and int(p['both_descend_pairs'])==sum(r['descent_count']=='2' for r in pp)
  cost=next(r for r in costs if r['path']==name);assert cost['AD_hessian_calls']=='1' and cost['dense_arrays_archived']=='0'
  if all(r['state'] in ['VALID','INFEASIBLE'] for r in tt):assert int(cost['MP_length_calls'])==2+4*len(aud)+2*sum(r['state']=='VALID' for r in tt) and int(cost['MP120_SPD_edges'])==int(p['segments'])*sum(r['state']=='VALID' for r in tt)
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['trials']==len(trials)==72 and summary['pairs']==len(pairs)==36 and summary['directions']==len(ds)==24 and summary['audits']==len(aa)==24 and summary['spectral_rows']==len(sp) and summary['checks']==len(checks) and summary['minimum_certificates']==0
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==11
 with tempfile.TemporaryDirectory(prefix='e16x-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget'];print('PASS_REPRODUCTION: once salidas idénticas; espectros, entrelazado, W, parejas, signos y costes reconstruidos; etapas previas/T2-A intactos.')
if __name__=='__main__':main()
