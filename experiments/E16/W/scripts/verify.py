#!/usr/bin/env python3
"""Reconstrucción independiente escalar y reproducción de W."""
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
 for name in ['config.json','DESIGN_FROZEN.md','requirements.txt','freeze_manifest.csv']:assert git('show',f'dfa1a66:experiments/E16/W/{name}')==(ROOT/name).read_bytes()
 assert git('show','0619132:experiments/E16/W/scripts/run.py')==(ROOT/'scripts/run.py').read_bytes()
 allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'};assert all(p.startswith('experiments/E16/W/') or p in allowed for p in git('diff','--name-only',cfg['base_commit']).decode().splitlines())
 for p in ['experiments/T2_A','experiments/T2_A1','experiments/E16/S','experiments/E16/T','experiments/E16/U','experiments/E16/V']:assert not git('diff',cfg['base_commit'],'--',p)
 paths=rows('paths.csv');ds=rows('directions.csv');audits=rows('audits.csv');trials=rows('trials.csv');pairs=rows('pairs.csv');checks=rows('checks.csv');costs=rows('costs.csv')
 old=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()));oldr=list(csv.DictReader((ROOT.parent/'T/results/run_v1/rayleigh.csv').open()));oldtr=list(csv.DictReader((ROOT.parent/'U/results/run_v1/trials.csv').open()))
 assert len(paths)==12 and {p['path'] for p in paths}=={p['path'] for p in old}
 def sign(x):
  tol=mp.mpf(cfg['sign_tolerance']);return 'DESCENT' if x< -tol else ('INCREASE' if x>tol else 'WITHIN_TOLERANCE')
 for p in paths:
  name=p['path'];dd=[r for r in ds if r['path']==name];aa=[r for r in audits if r['path']==name];tt=[r for r in trials if r['path']==name];pp=[r for r in pairs if r['path']==name];assert len(dd)==4 and len(tt)==12 and len(pp)==6
  oldhash=next(r['vector_sha256'] for r in oldr if r['path']==name and r['direction']=='full_min' and r['precision']=='120');assert all(r['source_vector_sha256']==oldhash for r in dd)
  for digits in cfg['precision']:
   v=next(r for r in dd if r['family']=='original' and int(r['precision'])==digits);w=next(r for r in dd if r['family']=='projected' and int(r['precision'])==digits)
   if w['route']=='DEGENERATE':continue
   assert abs(mp.mpf(w['unit_norm'])-1)<mp.mpf('1e-35') and mp.mpf(w['orthogonality_error'])<=mp.mpf(cfg['orthogonality_tolerance'])
   vn=mp.mpf(v['unit_norm']);gn=mp.mpf(v['gradient_norm']);s=mp.mpf(v['archive_slope']);qn=mp.mpf(w['pre_normalization_norm'])
   if w['route']=='PROJECTED':assert gn>mp.mpf(cfg['gradient_floor']) and abs(qn*qn-vn*vn+s*s/(gn*gn))<mp.mpf('1e-35') and abs(mp.mpf(w['absolute_cosine'])-qn/vn)<mp.mpf('1e-35')
   else:assert w['route']=='SMALL_GRADIENT' and gn<=mp.mpf(cfg['gradient_floor'])
  for r in aa:
   d=next(z for z in dd if z['family']==r['family'] and z['precision']==r['precision']);der=mp.mpf(r['derivative_2']);curv=mp.mpf(r['curvature_2']);s=mp.mpf(d['archive_slope']);ray=mp.mpf(float(d['ad_rayleigh']))
   ge=abs(der-s)/max(1,abs(der),abs(s));re=abs(curv-ray)/max(1,abs(curv),abs(ray));assert abs(ge-mp.mpf(r['gradient_error']))<mp.mpf('1e-35') and abs(re-mp.mpf(r['rayleigh_error']))<mp.mpf('1e-25')
  for family in cfg['families']:
   for step in cfg['steps']:
    signed=[r for r in tt if r['family']==family and r['step']==step];assert len(signed)==2 and {r['sign'] for r in signed}=={'-1','1'};pair=next(r for r in pp if r['family']==family and r['step']==step);complete=all(r['state']=='VALID' for r in signed);assert (pair['state']=='VALID')==complete
    for r in signed:
     if r['state']=='VALID':
      delta=mp.mpf(r['delta']);assert r['length_change']==sign(delta) and r['spd']=='True';assert mp.mpf(r['precision_error'])<=mp.mpf(cfg['precision_tolerance']) and mp.mpf(r['projection_error'])<=cfg['projection_rounding_tolerance'];lo,hi=float(r['geometry_lower']),float(r['geometry_upper']);assert 0<=lo<=hi and r['geometry_status']==('CHANGED' if lo>cfg['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=cfg['geometry_tolerance'] else 'UNRESOLVED'))
      assert abs(delta-mp.mpf(r['linear_prediction'])-mp.mpf(r['quadratic_prediction'])-mp.mpf(r['taylor_residual']))<mp.mpf('1e-35')
     elif r['state'] in ['INFEASIBLE','DEGENERATE']:assert not r['length'] and r['length_change']=='UNKNOWN'
     if family=='original':
      archive=next(z for z in oldtr if z['path']==name and z['direction']=='full_min' and z['step']==step and z['sign']==r['sign']);assert r['state']==archive['state']
      if r['state']=='VALID':assert abs(mp.mpf(r['delta'])-mp.mpf(archive['delta']))<mp.mpf('1e-35')
    if complete:
     dm=mp.mpf(next(r['delta'] for r in signed if r['sign']=='-1'));dp=mp.mpf(next(r['delta'] for r in signed if r['sign']=='1'));assert abs(mp.mpf(pair['even_change'])-(dm+dp)/2)<mp.mpf('1e-35') and abs(mp.mpf(pair['odd_change'])-(dp-dm)/2)<mp.mpf('1e-35');assert pair['even_sign']==sign((dp+dm)/2) and int(pair['descent_count'])==int(sign(dm)=='DESCENT')+int(sign(dp)=='DESCENT')
  assert p['minimum_status']=='UNKNOWN' and int(p['valid_trials'])==sum(r['state']=='VALID' for r in tt) and int(p['infeasible_trials'])==sum(r['state']=='INFEASIBLE' for r in tt)
  assert int(p['projected_negative_even_pairs'])==sum(r['family']=='projected' and r['even_sign']=='DESCENT' for r in pp) and int(p['projected_both_descend_pairs'])==sum(r['family']=='projected' and r['descent_count']=='2' for r in pp)
  c=next(r for r in costs if r['path']==name);assert c['AD_hessian_calls']=='1' and c['dense_arrays_archived']=='0'
  if all(r['state'] in ['VALID','INFEASIBLE'] for r in tt):assert int(c['MP_length_calls'])==2+4*len(aa)+2*sum(r['state']=='VALID' for r in tt) and int(c['MP120_SPD_edges'])==int(p['segments'])*sum(r['state']=='VALID' for r in tt)
 for r in checks:assert (r['status']=='PASS')==(abs(mp.mpf(r['error']))<=mp.mpf(r['tolerance']))
 summary=json.loads((out/'summary.json').read_text());assert summary['trials']==len(trials)==144 and summary['pairs']==len(pairs)==72 and summary['directions']==len(ds)==48 and summary['audits']==len(audits) and summary['checks']==len(checks) and summary['minimum_certificates']==0
 names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==9
 with tempfile.TemporaryDirectory(prefix='e16w-') as tmp:
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
  resource=json.loads((Path(tmp)/'resources.json').read_text());assert resource['within_budget'];print('Reproduction seconds:',resource['seconds'])
 assert json.loads((out/'resources.json').read_text())['within_budget'];print('PASS_REPRODUCTION: nueve salidas idénticas; proyección, pendientes, parejas, signos y costes reconstruidos; S/T/U/V/T2-A intactos.')
if __name__=='__main__':main()
