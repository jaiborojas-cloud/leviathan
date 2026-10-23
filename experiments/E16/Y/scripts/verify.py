#!/usr/bin/env python3
"""Reconstrucción escalar, gradientes nuevos y repetición de E16-Y."""
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
 for name in ['config.json','requirements.txt','DESIGN_FROZEN.md','freeze_manifest.csv']:assert git('show',f'c826975:experiments/E16/Y/{name}')==(ROOT/name).read_bytes()
 assert git('show','f60a896:experiments/E16/Y/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/Y/') or p in allowed for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 for p in ['experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T','experiments/E16/U','experiments/E16/V','experiments/E16/W','experiments/E16/X']:assert not git('diff',cfg['base_commit'],'--',p)
 paths=rows('paths.csv');spectra=rows('spectra.csv');gradients=rows('gradients.csv');audits=rows('audits.csv');comparisons=rows('comparisons.csv');checks=rows('checks.csv');costs=rows('costs.csv');source=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()))
 assert len(paths)==24 and len(comparisons)==12 and {p['path'] for p in paths}=={p['path'] for p in source}
 for original in source:
  name=original['path'];pair=[p for p in paths if p['path']==name];assert len(pair)==2 and {p['level'] for p in pair}=={'coarse','fine'}
  coarse=next(p for p in pair if p['level']=='coarse');fine=next(p for p in pair if p['level']=='fine');assert int(fine['segments'])==2*int(coarse['segments'])==2*int(original['segments'])
  for p in pair:
   level=p['level'];m=int(p['segments']);dim=2*(m-1);small=p['route']=='SMALL_GRADIENT';assert int(p['dimension'])==dim and int(p['restricted_dimension'])==dim-int(not small)
   sp=[r for r in spectra if r['path']==name and r['level']==level];assert len(sp)==int(p['restricted_dimension']) and [int(r['index']) for r in sp]==list(range(len(sp)));ev=np.array([float(r['eigenvalue']) for r in sp]);assert np.all(np.diff(ev)>=0);tau=cfg['spectral_relative_floor']*max(1,float(np.max(abs(ev))));assert float(p['threshold'])==tau and float(p['minimum_mass'])==ev[0]
   for r,v in zip(sp,ev):assert float(r['threshold'])==tau and r['mode_class']==('NEGATIVE' if v< -tau else ('NEAR_ZERO' if abs(v)<=tau else 'POSITIVE'))
   assert int(p['negative_modes'])==np.sum(ev< -tau) and int(p['near_zero_modes'])==np.sum(abs(ev)<=tau)
   aa=[r for r in audits if r['path']==name and r['level']==level];assert len(aa)==2 and {r['precision'] for r in aa}=={'80','120'}
   for a in aa:
    assert a['nodal_max']=='1' and mp.mpf(a['mass_norm_squared'])>0;mu=mp.mpf(float(p['minimum_mass']));q=mp.mpf(a['mass_rayleigh_2']);err=abs(mu-q)/max(1,abs(mu),abs(q));assert abs(err-mp.mpf(a['rayleigh_error']))<mp.mpf('1e-25')
   a=next(r for r in aa if r['precision']=='120');witness=mp.mpf(a['mass_rayleigh_2'])< -mp.mpf(cfg['witness_tolerance'])*max(1,abs(mp.mpf(float(p['minimum_mass']))));assert (p['negative_MP_witness']=='True')==(p['diagnostics']=='PASS' and witness)
   c=next(r for r in costs if r['path']==name and r['level']==level);assert c['AD_hessian_calls']=='1' and c['MP_global_length_calls']=='10' and c['dense_arrays_archived']=='0'
   if level=='fine':
    gg=[r for r in gradients if r['path']==name];assert len(gg)==dim and int(c['MP_local_gradient_calls'])==4*dim;assert [int(r['node']) for r in gg]==[j for j in range(1,m) for axis in [0,1]];assert [r['coordinate'] for r in gg]==['t','s']*(m-1)
    scale=max(1,abs(mp.mpf(original['length'])));ad=max(abs(mp.mpf(float(r['AD']))-mp.mpf(r['MP_fd_2'])) for r in gg)/scale;steps=max(abs(mp.mpf(r['MP_fd_1'])-mp.mpf(r['MP_fd_2'])) for r in gg)/scale
    assert abs(ad-mp.mpf(p['gradient_AD_error']))<mp.mpf('1e-25') and abs(steps-mp.mpf(p['gradient_step_error']))<mp.mpf('1e-25');gn=np.linalg.norm([float(r['MP_fd_2']) for r in gg]);assert abs(gn-float(p['gradient_norm']))<1e-12
   else:assert c['MP_local_gradient_calls']=='0'
   assert p['minimum_status']=='UNKNOWN'
  c=next(r for r in comparisons if r['path']==name);assert c['coarse_minimum_mass']==coarse['minimum_mass'] and c['fine_minimum_mass']==fine['minimum_mass'] and c['comparable_to_X_numbers']=='False';assert abs(float(c['difference'])-float(fine['minimum_mass'])+float(coarse['minimum_mass']))<1e-12
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['meshes']==len(paths)==24 and summary['fine_gradients']==len(gradients)==9480 and summary['audits']==len(audits)==48 and summary['checks']==len(checks) and summary['spectral_rows']==len(spectra) and summary['minimum_certificates']==0
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==9
 with tempfile.TemporaryDirectory(prefix='e16y-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget'];print('PASS_REPRODUCTION: nueve salidas idénticas; dos niveles, gradientes finos, masa, espectros, testigos y costes reconstruidos; fuentes/T2-A intactos.')
if __name__=='__main__':main()
