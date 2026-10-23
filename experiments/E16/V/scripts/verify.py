#!/usr/bin/env python3
"""Reconstrucción escalar y reproducción de E16-V sin alterar fuentes."""
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
 for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in csv.DictReader((ROOT/name).open()):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
 for name in ['config.json','DESIGN_FROZEN.md','requirements.txt','freeze_manifest.csv']:assert git('show',f'97c830d:experiments/E16/V/{name}')==(ROOT/name).read_bytes()
 assert git('show','b6f3c38:experiments/E16/V/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/V/') or p in allowed for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 for directory in ['experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T','experiments/E16/U']:assert not git('diff',cfg['base_commit'],'--',directory)
 paths=rows('paths.csv');trials=rows('trials.csv');pairs=rows('pairs.csv');directions=rows('directions.csv');comp=rows('comparisons.csv');checks=rows('checks.csv');costs=rows('costs.csv')
 original=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));oldr=list(csv.DictReader((ROOT.parent/'T/results/run_v1/rayleigh.csv').open()));oldtr=list(csv.DictReader((ROOT.parent/'U/results/run_v1/trials.csv').open()))
 assert len(paths)==12 and {r['path'] for r in paths}=={r['path'] for r in original}
 def classify(v):
  tol=mp.mpf(cfg['sign_tolerance']);return 'DESCENT' if v< -tol else ('INCREASE' if v>tol else 'WITHIN_TOLERANCE')
 for path in paths:
  name=path['path'];m=int(path['source_segments']);assert int(path['refined_segments'])==2*m
  tt=[r for r in trials if r['path']==name];pp=[r for r in pairs if r['path']==name];dd=[r for r in directions if r['path']==name];cc=[r for r in comp if r['path']==name];assert len(tt)==30 and len(pp)==15 and len(dd)==5 and len(cc)==6
  origin_norm=mp.mpf(next(r['displacement_norm'] for r in dd if r['family']=='original'));oldhash=next(r['vector_sha256'] for r in oldr if r['path']==name and r['direction']=='full_min' and r['precision']=='120')
  for r in dd:
   assert r['original_vector_sha256']==oldhash and r['original_vertex_amplitude_scale']=='1';norm=mp.mpf(r['displacement_norm']);assert int(r['segments'])==(m if r['family']=='original' else 2*m)
   if r['family'].startswith('transported'):assert norm>=origin_norm
   else:assert abs(norm-origin_norm)<mp.mpf('1e-35')
  for family in cfg['families']:
   for step in cfg['steps']:
    signed=[r for r in tt if r['family']==family and r['step']==step];assert len(signed)==2 and {r['sign'] for r in signed}=={'-1','1'}
    pair=next(r for r in pp if r['family']==family and r['step']==step);complete=all(r['state']=='VALID' for r in signed);assert (pair['state']=='VALID')==complete
    for r in signed:
     parent=next(z for z in tt if z['family']=='original' and z['step']==step and z['sign']==r['sign']);assert r['state']==parent['state']
     if r['state']=='VALID':
      delta=mp.mpf(r['delta']);assert r['length_change']==classify(delta) and r['spd']=='True';assert mp.mpf(r['precision_error'])<=mp.mpf(cfg['precision_tolerance']) and mp.mpf(r['projection_error'])<=cfg['rounding_tolerance']
      for prefix in ['geometry_','vs_transport_']:
       lo,hi=float(r[prefix+'lower']),float(r[prefix+'upper']);assert 0<=lo<=hi;tag='CHANGED' if lo>cfg['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=cfg['geometry_tolerance'] else 'UNRESOLVED');assert r[prefix+'status']==tag
      if not family.startswith('pinned'):assert r['vs_transport_status']=='WITHIN_TOLERANCE'
      if family.startswith('transported'):assert abs(delta-mp.mpf(parent['delta']))<mp.mpf('1e-35') and abs(mp.mpf(r['length'])-mp.mpf(parent['length']))<mp.mpf('1e-35')
     elif r['state']=='INFEASIBLE':assert not r['length'] and r['length_change']=='UNKNOWN'
     if family=='original':
      archive=next(z for z in oldtr if z['path']==name and z['direction']=='full_min' and z['step']==step and z['sign']==r['sign']);assert r['state']==archive['state']
      if r['state']=='VALID':assert abs(mp.mpf(r['delta'])-mp.mpf(archive['delta']))<mp.mpf('1e-35')
    if complete:
     dm=mp.mpf(next(r['delta'] for r in signed if r['sign']=='-1'));dp=mp.mpf(next(r['delta'] for r in signed if r['sign']=='1'));even=(dm+dp)/2;odd=(dp-dm)/2;assert abs(even-mp.mpf(pair['even_change']))<mp.mpf('1e-35') and abs(odd-mp.mpf(pair['odd_change']))<mp.mpf('1e-35') and pair['even_sign']==classify(even)
     orig=next(r for r in pp if r['family']=='original' and r['step']==step);assert pair['vs_original_sign']==('SAME' if pair['even_sign']==orig['even_sign'] else 'CHANGED')
  for r in cc:
   suffix='half' if r['fraction']=='.5' else 'quarter';p=next(z for z in pp if z['family']=='pinned_'+suffix and z['step']==r['step']);t=next(z for z in pp if z['family']=='transported_'+suffix and z['step']==r['step']);complete=p['state']==t['state']=='VALID';assert (r['state']=='VALID')==complete
   if complete:assert abs(mp.mpf(r['difference'])-mp.mpf(p['even_change'])+mp.mpf(t['even_change']))<mp.mpf('1e-35') and r['sign_comparison']==('SAME' if p['even_sign']==t['even_sign'] else 'CHANGED')
  assert int(path['valid_trials'])==sum(r['state']=='VALID' for r in tt) and int(path['infeasible_trials'])==sum(r['state']=='INFEASIBLE' for r in tt) and path['minimum_status']=='UNKNOWN'
  for label,prefix in [('original','negative_original_pairs'),('transported','negative_transported_pairs'),('pinned','negative_pinned_pairs')]:assert int(path[prefix])==sum(r['family'].startswith(label) and r['even_sign']=='DESCENT' for r in pp)
  c=next(r for r in costs if r['path']==name);assert c['AD_hessian_calls']=='1' and c['dense_arrays_archived']=='0'
  if all(r['state'] in ['VALID','INFEASIBLE'] for r in tt):assert int(c['MP_length_calls'])==6+2*sum(r['state']=='VALID' for r in tt) and int(c['MP120_SPD_edges'])==sum(int(r['segments']) for r in tt if r['state']=='VALID')
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['trials']==len(trials)==360 and summary['pairs']==len(pairs)==180 and summary['comparisons']==len(comp)==72 and summary['directions']==len(directions)==60 and summary['checks']==len(checks) and summary['minimum_certificates']==0
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==9
 with tempfile.TemporaryDirectory(prefix='e16v-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
  subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget'];print('PASS_REPRODUCTION: nueve salidas idénticas; familias, parejas, transporte, U y costes reconstruidos; S/T/U/T2-A intactos.')
if __name__=='__main__':main()
