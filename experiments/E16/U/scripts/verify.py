#!/usr/bin/env python3
"""Verifica archivo de U, reconstruye parejas y reproduce sin modificar T/S."""
import csv,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
import mpmath as mp
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def main():
 mp.mp.dps=120;cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'results/run_v1'
 for manifest in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in csv.DictReader((ROOT/manifest).open()):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
 for name in ['config.json','DESIGN_FROZEN.md','requirements.txt','freeze_manifest.csv']:assert git('show',f'78dc7d3:experiments/E16/U/{name}')==(ROOT/name).read_bytes()
 assert git('show','4b73934:experiments/E16/U/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/U/') or p in allowed for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T')
 paths=rows('paths.csv');trials=rows('trials.csv');pairs=rows('pairs.csv');directions=rows('directions.csv');checks=rows('checks.csv');costs=rows('costs.csv')
 sources=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));oldr=list(csv.DictReader((ROOT.parent/'T/results/run_v1/rayleigh.csv').open()));assert len(paths)==12 and {p['path'] for p in paths}=={p['path'] for p in sources}
 def classify(delta):
  tol=mp.mpf(cfg['length_sign_tolerance']);return 'DESCENT' if delta< -tol else ('INCREASE' if delta>tol else 'WITHIN_TOLERANCE')
 for p in paths:
  name=p['path'];own=[r for r in trials if r['path']==name];pp=[r for r in pairs if r['path']==name];dd=[r for r in directions if r['path']==name];assert len(own)==30 and len(pp)==15 and len(dd)==5
  for d in dd:
   old=next(r for r in oldr if r['path']==name and r['direction']==d['direction'] and r['precision']=='120');assert d['vector_sha256']==old['vector_sha256'] and d['T_hash_match']=='True';assert d['rayleigh_MP_archive']==old['mp_step_2']
  for direction in cfg['directions']:
   d=next(r for r in dd if r['direction']==direction)
   for step in cfg['steps']:
    tt=[r for r in own if r['direction']==direction and r['step']==step];assert len(tt)==2 and {r['sign'] for r in tt}=={'-1','1'}
    pair=next(r for r in pp if r['direction']==direction and r['step']==step)
    complete=all(r['state']=='VALID' for r in tt);assert (pair['state']=='VALID')==complete
    for r in tt:
     if r['state']=='VALID':
      delta=mp.mpf(r['delta']);assert r['length_change']==classify(delta) and r['spd']=='True'
      assert mp.mpf(r['precision_error'])<=mp.mpf(cfg['precision_tolerance']);assert mp.mpf(r['geometry_rounding'])<=cfg['geometry_rounding_limit']
      lo,hi=float(r['geometry_lower']),float(r['geometry_upper']);assert 0<=lo<=hi
      assert r['geometry_status']==('CHANGED' if lo>cfg['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=cfg['geometry_tolerance'] else 'UNRESOLVED'))
      assert abs(delta-mp.mpf(r['linear_prediction'])-mp.mpf(r['quadratic_prediction'])-mp.mpf(r['taylor_residual']))<mp.mpf('1e-35')
     elif r['state']=='INFEASIBLE':assert r['length_change']=='UNKNOWN' and not r['delta']
    if complete:
     dm=mp.mpf(next(r['delta'] for r in tt if r['sign']=='-1'));dp=mp.mpf(next(r['delta'] for r in tt if r['sign']=='1'));even=(dp+dm)/2;odd=(dp-dm)/2
     assert abs(even-mp.mpf(pair['even_change']))<mp.mpf('1e-35') and abs(odd-mp.mpf(pair['odd_change']))<mp.mpf('1e-35') and pair['even_sign']==classify(even)
  assert int(p['trials'])==len(own) and int(p['valid'])==sum(r['state']=='VALID' for r in own) and int(p['infeasible'])==sum(r['state']=='INFEASIBLE' for r in own)
  assert int(p['descents'])==sum(r['length_change']=='DESCENT' for r in own) and int(p['changed_geometries'])==sum(r['geometry_status']=='CHANGED' for r in own)
  assert int(p['full_min_negative_even_steps'])==sum(r['direction']=='full_min' and r['even_sign']=='DESCENT' for r in pp)
  cost=next(r for r in costs if r['path']==name);assert cost['AD_hessian_calls']=='1' and cost['dense_arrays_archived']=='0'
  if all(r['state']=='VALID' for r in own):assert int(cost['MP_length_calls'])==62 and int(cost['MP120_SPD_edges'])==30*int(p['segments'])
  assert p['minimum_status']=='UNKNOWN'
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['trials']==len(trials)==360 and summary['pairs']==len(pairs)==180 and summary['directions']==len(directions)==60 and summary['checks']==len(checks) and summary['minimum_certificates']==0
 assert summary['descent_trials']==sum(r['length_change']=='DESCENT' for r in trials) and summary['negative_even_pairs']==sum(r['even_sign']=='DESCENT' for r in pairs)
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==9
 with tempfile.TemporaryDirectory(prefix='e16u-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
  subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget']
 print('PASS_REPRODUCTION: nueve salidas científicas idénticas; parejas, signos, geometría y costes reconstruidos; T/S/T2-A intactos.')
if __name__=='__main__':main()
