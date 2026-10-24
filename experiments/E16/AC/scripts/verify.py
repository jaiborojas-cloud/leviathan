#!/usr/bin/env python3
"""Integridad de versiones, estados, controles, alcance y reproducción AC v2."""
import sys
sys.dont_write_bytecode=True
import csv,json,hashlib,subprocess,tempfile,os
from pathlib import Path
import mpmath as mp
R=Path(__file__).resolve().parents[1];REPO=R.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open()))
def main():
 cfg=json.loads((R/'config_v2.json').read_text());out=R/'results/run_v2'
 for name in ['freeze_manifest.csv','freeze_manifest_v2.csv','implementation_manifest.csv','implementation_manifest_v2.csv','manifest.csv']:
  for x in rows(R/name):assert sha(R/x['path'])==x['sha256'],x
 for p,h in cfg['sources'].items():assert sha(R.parent/p)==h,p
 for commit,names in [('6238a9f',['DESIGN_FROZEN.md','config.json','progress.md']),('735ac0d',['scripts/run_v1.py']),('bd1db17',['DESIGN_FROZEN_v2.md','config_v2.json']),('5d94e7f',['scripts/run_v2.py'])]:
  for name in names:assert subprocess.check_output(['git','show',commit+':experiments/E16/AC/'+name],cwd=REPO)==(R/name).read_bytes()
 changed=subprocess.check_output(['git','diff','--name-only',cfg['base_commit']],cwd=REPO).decode().splitlines();assert all(p.startswith('experiments/E16/AC/') or p=='experiments/E16/SINTESIS_S_AB.md' for p in changed)
 controls=rows(out/'controls.csv');paths=rows(out/'paths.csv');shoot=rows(out/'shooting.csv');assert len(controls)==8 and all(c['status']=='PASS' for c in controls)
 assert len(paths)==12 and {p['path'] for p in paths}=={p['path'] for p in rows(R.parent/'AB/results/run_v1/paths.csv')}
 for p in paths:
  assert p['normal_negative_discrete']==p['witness_tangency']=='UNKNOWN'
  if p['status']=='PASS_NUMERICAL':assert p['shooting_OK']==p['stable']=='True' and float(p['speed_drift'])<=1e-7 and p['conjugates']!='UNKNOWN'
  rr=[q for q in shoot if q['path']==p['path']];assert len(rr)==2 and all(q['success']=='True' and float(q['endpoint_error'])<=1e-8 for q in rr)
 with mp.workdps(80):
  for q in rows(out/'curvature.csv'):assert mp.mpf(q['relative_error'])<=mp.mpf('1e-8')
 summary=json.loads((out/'summary.json').read_text());assert summary['verdict']=='INCONCLUSIVE' and summary['run_valid'] and summary['status']=='VALID_EXPLORATORY'
 assert json.loads((R/'results/run_v1/summary.json').read_text())['status']=='INVALID'
 files=[p.name for p in sorted(out.iterdir()) if p.name!='resources.json'];print('PASS_ARCHIVES',len(files),flush=True)
 with tempfile.TemporaryDirectory(prefix='e16ac-') as temp:
  dest=Path(temp)/'rep';env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');subprocess.run([sys.executable,str(R/'scripts/run_v2.py'),'--out',str(dest)],env=env,check=True,timeout=cfg['budget_seconds'])
  for name in files:assert (out/name).read_bytes()==(dest/name).read_bytes(),name
  print('PASS_REPRODUCTION',json.loads((dest/'resources.json').read_text()),flush=True)
if __name__=='__main__':main()
