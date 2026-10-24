#!/usr/bin/env python3
"""Congelación, controles, censura, bloques y reproducción exacta de AE/versiones."""
from metric_v1 import *
import subprocess,tempfile,os,sys
from scipy.linalg import eigvalsh

def main():
 for name in ['freeze_phase0.csv','freeze_main.csv','freeze_bridge_v2.csv','implementation_phase0.csv','implementation_main.csv','implementation_bridge_v2.csv','manifest.csv']:
  for q in rows(ROOT/name):assert sha(ROOT/q['path'])==q['sha256'],q['path']
 for commit,names in [('343be81',['DESIGN_FROZEN.md','phase0_config.json']),('ba3bb43',['scripts/metric_v1.py','scripts/phase0_v1.py']),('91cc1a2',['DESIGN_FROZEN_MAIN.md','config.json','progress.md']),('b6cbb89',['scripts/numerics_v1.py','scripts/experiment_v1.py']),('d1c40fa',['DESIGN_FROZEN_BRIDGE_v2.md','bridge_v2_config.json']),('bca4621',['scripts/bridge_v2.py'])]:
  for n in names:assert subprocess.check_output(['git','show',commit+':experiments/E16/AE/'+n],cwd=E16.parents[1])==(ROOT/n).read_bytes()
 changed=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=E16.parents[1]).decode().splitlines();assert all(p.startswith('experiments/E16/AE/') or p=='experiments/E16/SINTESIS_S_AD.md' for p in changed)
 for path,h in CFG['sources'].items():assert sha(E16/path)==h,path
 p0=ROOT/'results/phase0_v1';raw=ROOT/'results/main_v1';br=ROOT/'results/bridge_v2';phase=json.loads((p0/'summary.json').read_text());assert phase['status']=='PASS_GEOMETRY' and phase['center']==[0,0] and phase['K_min']<0<phase['K_max'];assert len(rows(p0/'grid.csv'))==90 and all(q['status']=='PASS' and float(q['lambda_min'])>0 for q in rows(p0/'grid.csv'))
 controls=rows(raw/'controls.csv');assert len(controls)==20 and all(q['status']=='PASS' for q in controls);assert all(q['status']=='PASS' for q in rows(br/'controls.csv'))
 rays=rows(raw/'rays.csv');assert len(rays)==1536 and len({(q['n'],q['ray']) for q in rays})==1536;assert all(q['status']=='RIGHT_CENSORED_DOMAIN' and not q['conjugate'] and float(q['coverage'])>0 for q in rays)
 for n in [512,1024]:assert len([q for q in rays if int(q['n'])==n])==n
 mpchecks=rows(raw/'mp_audits.csv');assert len(mpchecks)==4 and all(q['status']=='PASS' and float(q['error_float_MP'])<=1e-5 and float(q['error_MP_steps'])<=1e-5 for q in mpchecks)
 # Reconstruir índice desde bandas archivadas sin volver a derivar Hessianas.
 bands=rows(raw/'normal_bands.csv');spectra=rows(raw/'normal_spectra.csv');indices=rows(raw/'indices.csv');assert len(indices)==36 and sum(q['status']=='PASS_NUMERICAL' for q in indices)==30
 for q in indices:
  ray=next(r for r in rays if r['n']==q['n'] and r['ray']==q['ray'])
  if q['status']=='PASS_NUMERICAL':
   assert float(q['L'])<=float(ray['coverage']) and float(q['gradient'])<=1e-3 and float(q['quadrature_error'])<=1e-5;rr=[b for b in bands if b['case']==q['case']];N=int(rr[0]['dimension']);H=np.zeros((N,N))
   for b in rr:H[int(b['row']),int(b['column'])]=float(b['value'])
   ev=eigvalsh(H);ss=[s for s in spectra if s['case']==q['case']];assert len(ss)==N and np.max(abs(ev-np.array([float(s['eigenvalue']) for s in ss])))/max(1,max(abs(ev)))<1e-9;assert sum(ev< -float(q['threshold']))==int(q['index'])==0;assert abs(float(q['MP_Rayleigh'])-float(q['minimum']))/max(1,abs(float(q['MP_Rayleigh'])))<=1e-4
  else:assert 'RIGHT_CENSORED_TARGET' in q['reason'] and float(q['L'])>float(ray['coverage'])
 # Censura del puente y conservación del descriptor v1, sin confundirlos.
 per=rows(br/'per_ray.csv');bridge=rows(br/'bridge.csv');assert len(per)==1536 and not rows(br/'collisions.csv')
 for b in bridge:
  n=int(b['n']);pp=[r for r in per if r['n']==b['n']];assert len(pp)==n and not b['r_deg'] and not b['A_deg'];assert b['known_no_event_at_fixed']==b['known_event_at_fixed']=='0' and int(b['censored_at_fixed'])==n;assert float(b['fraction_event_free_lower'])==0 and float(b['fraction_event_free_upper'])==1;assert float(b['no_event_on_sampled_front_to'])==.6875<float(b['first_domain_censor']);assert all(float(r['joint_coverage'])==min(float(r['individual_coverage']),float(r['collision_coverage'])) and r['state_at_fixed']=='RIGHT_CENSORED_OR_UNKNOWN' for r in pp)
  rawb=next(r for r in rows(raw/'resolutions.csv') if r['n']==b['n']);assert b['v1_individual_coverage_without_conjugate']==rawb['fraction_at_fixed'];count=sum(float(r['coverage'])>=1 and not r['conjugate'] for r in rays if r['n']==b['n']);assert count/n==float(rawb['fraction_at_fixed'])
 s=json.loads((raw/'summary.json').read_text());assert s['run_status']=='VALID_EXPLORATORY' and all(s[q]=='INCONCLUSIVE' for q in ['Q1','Q2','Q3']);assert all(r['reason']=='NO_OBSERVED_CONJUGATE' for r in rows(raw/'shooting.csv'))
 print('PASS_ARCHIVES: controles, SPD/MP, índices, censura, versiones y alcance',flush=True)
 with tempfile.TemporaryDirectory(prefix='e16ae-') as tmp:
  dest=Path(tmp);env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');(dest/'phase0_config.json').write_bytes((ROOT/'phase0_config.json').read_bytes());code="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import phase0_v1 as p;p.ROOT=Path(sys.argv[2]);p.main()";subprocess.run([sys.executable,'-c',code,str(ROOT/'scripts'),str(dest)],env=env,check=True)
  for p in p0.iterdir():
   if p.name!='resources.json':assert p.read_bytes()==(dest/'results/phase0_v1'/p.name).read_bytes(),p.name
  main_dest=dest/'main';subprocess.run([sys.executable,str(ROOT/'scripts/experiment_v1.py'),'--out',str(main_dest)],env=env,check=True,timeout=2400);br_dest=dest/'bridge';subprocess.run([sys.executable,str(ROOT/'scripts/bridge_v2.py'),'--out',str(br_dest),'--source',str(main_dest)],env=env,check=True)
  for old,new in [(raw,main_dest),(br,br_dest)]:
   for p in old.iterdir():
    if p.name!='resources.json':assert p.read_bytes()==(new/p.name).read_bytes(),str(p)
  print('PASS_REPRODUCTION',{'phase0':json.loads((dest/'results/phase0_v1/resources.json').read_text()),'main':json.loads((main_dest/'resources.json').read_text()),'bridge':json.loads((br_dest/'resources.json').read_text())},flush=True)
if __name__=='__main__':main()
