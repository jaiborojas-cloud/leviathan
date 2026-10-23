#!/usr/bin/env python3
"""Reconstrucción desde archivos y repetición exacta de E16-T."""
import csv,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def main():
 cfg=json.loads((ROOT/'config.json').read_text());out=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in csv.DictReader((ROOT/name).open()):assert sha(ROOT/r['path'])==r['sha256'],r
 for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
 for name in ['config.json','requirements.txt','DESIGN_FROZEN.md','freeze_manifest.csv']:
  assert git('show',f'e73e894:experiments/E16/T/{name}')==(ROOT/name).read_bytes()
 assert git('show','927ca53:experiments/E16/T/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
 assert all(p.startswith('experiments/E16/T/') or p in allowed for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/T2_A1','experiments/E16/S')
 source=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));paths=rows('paths.csv');sp=rows('spectra.csv');ra=rows('rayleigh.csv');checks=rows('checks.csv');cost=rows('costs.csv')
 assert len(paths)==12 and {p['path'] for p in paths}=={p['path'] for p in source}
 for p in paths:
  name=p['path'];n=int(p['segments'])-1;block={}
  for b,size in [('full',2*n),('tangent',n),('normal',n)]:
   r=[z for z in sp if z['path']==name and z['block']==b];assert len(r)==size and [int(z['index']) for z in r]==list(range(size))
   vals=np.array([float(z['eigenvalue']) for z in r]);assert np.all(np.diff(vals)>=0)
   tau=cfg['spectral_relative_floor']*max(1,float(np.max(abs(vals))));assert all(float(z['threshold'])==tau for z in r)
   for z,v in zip(r,vals):assert z['mode_class']==('NEGATIVE' if v< -tau else ('NEAR_ZERO' if abs(v)<=tau else 'POSITIVE'))
   assert int(p[b+'_negative'])==np.sum(vals< -tau) and int(p[b+'_near_zero'])==np.sum(abs(vals)<=tau)
   assert float(p[b+'_min'])==vals[0];block[b]=vals
  full,tt,nn=[block[b] for b in ['full','tangent','normal']]
  scale=max(1,float(np.sum(abs(full))));assert abs(sum(full)-sum(tt)-sum(nn))/scale<1e-10
  assert full[0]<=min(tt[0],nn[0])+1e-8*max(1,abs(full[0]))
  # Orthogonal block decomposition: ||H||F²=||Htt||F²+||Hnn||F²+2||Htn||F².
  total=float(full@full);mixed=max(0,(total-float(tt@tt)-float(nn@nn))/2)
  expected=np.sqrt(mixed)/max(1,np.sqrt(total));actual=float(p['coupling_frobenius_ratio']);assert abs(expected-actual)<1e-7
  rr=[z for z in ra if z['path']==name];assert len(rr)==10
  for direction in cfg['directions']:
   a,b=[next(z for z in rr if z['direction']==direction and int(z['precision'])==digits) for digits in cfg['precision']]
   assert a['vector_sha256']==b['vector_sha256'] and a['ad_rayleigh']==b['ad_rayleigh']
   fraction=float(a['tangent_fraction']);assert -1e-12<=fraction<=1+1e-12
   if direction.startswith('tangent'):assert abs(fraction-1)<1e-12
   if direction.startswith('normal'):assert abs(fraction)<1e-12
   if direction.endswith('_min'):
    label=direction.removesuffix('_min');assert abs(float(a['ad_rayleigh'])-block[label][0])<1e-8*max(1,abs(block[label][0]))
   for z in [a,b]:
    q1,q2=float(z['mp_step_1']),float(z['mp_step_2']);ray=float(z['ad_rayleigh']);assert abs(abs(ray-q2)/max(1,abs(ray),abs(q2))-float(z['ad_error']))<1e-12
    assert abs(abs(q1-q2)/max(1,abs(q1),abs(q2))-float(z['step_error']))<1e-12
  cc=next(z for z in cost if z['path']==name);assert cc['AD_hessian_calls']=='1' and cc['MP_full_length_calls']=='50' and cc['dense_arrays_archived']=='0'
  assert p['minimum_status']=='UNKNOWN'
  own=[z for z in checks if z['name'].startswith(name+'/')];assert (p['diagnostics']=='PASS')==all(z['status']=='PASS' for z in own)
  if p['lineage']=='C0':assert int(p['full_near_zero'])>=n
 for c in checks:assert (c['status']=='PASS')==(abs(float(c['error']))<=float(c['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['status']=='INCONCLUSIVE' and summary['minimum_certificates']==0 and summary['checks']==len(checks) and summary['rayleigh_rows']==len(ra) and summary['spectral_rows']==len(sp)
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==7
 with tempfile.TemporaryDirectory(prefix='e16t-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
  subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget']
 print('PASS_REPRODUCTION: siete salidas científicas idénticas; marcos/espectros/costes reconstruidos; fuentes y T2-A intactos.')
if __name__=='__main__':main()
