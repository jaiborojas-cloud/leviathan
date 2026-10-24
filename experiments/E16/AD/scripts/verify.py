#!/usr/bin/env python3
"""Integridad, reconstrucción de bloques y modos, reproducción prospectiva AD."""
from common import *
import subprocess,tempfile,os,sys
from scipy.linalg import eigvalsh

def main():
 for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
  for r in rows(ROOT/name):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for commit,names in [('a61846b',['config.json','DESIGN_FROZEN.md','requirements.txt','progress.md']),('d35c20c',['scripts/common.py','scripts/part_a_v1.py','scripts/part_b_v1.py'])]:
  for n in names:assert subprocess.check_output(['git','show',commit+':experiments/E16/AD/'+n],cwd=ROOT.parents[2])==(ROOT/n).read_bytes()
 changed=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=ROOT.parents[2]).decode().splitlines();assert all(p.startswith('experiments/E16/AD/') for p in changed)
 for p,h in CFG['sources'].items():assert sha(E16/p)==h
 a=ROOT/'results/part_a_v1';b=ROOT/'results/part_b_v1';assert json.loads((a/'symbolic.json').read_text())['verified'];ar=rows(a/'summary.csv');assert len(ar)==3 and all(q['analytic_flat']=='True' and q['numerical_status']=='PASS' and q['regular_points']=='81' for q in ar)
 control=rows(b/'controls.csv');assert len(control)==12 and all(q['status']=='PASS' for q in control)
 cases=rows(b/'paths.csv');assert len(cases)==12;bs=rows(b/'bands.csv');sp=rows(b/'spectra.csv');nv=rows(b/'negative_vectors.csv');mats={}
 for r in bs:
  key=(r['case'],r['block'])
  if key not in mats:mats[key]=np.zeros((int(r['dimension']),int(r['dimension'])))
  mats[key][int(r['row']),int(r['column'])]=float(r['value'])
 for (case,block),H in mats.items():
  if block=='coupling_TN':continue
  vals=eigvalsh((H+H.T)/2);rr=[q for q in sp if q['case']==case and q['block']==block];assert len(rr)==len(vals);assert np.max(abs(vals-np.array([float(q['eigenvalue']) for q in rr])))/max(1,max(abs(vals)))<1e-9
 for c in cases:
  mm=[q for q in rows(b/'monitor.csv') if q['case']==c['case']];streak=0
  for q in mm:
   if int(q['iteration'])>0:streak=streak+1 if q['state']=='STATIONARY' and float(q['MP_KKT'])<=CFG['KKT'] else 0
   assert int(q['streak'])==streak and (q['stop_requested']=='True')==(streak>=CFG['streak'])
  if c['route']=='PHYSICAL_SUSTAINED':assert c['native_status']=='99' and mm[-1]['stop_requested']=='True' and int(mm[-1]['iteration'])==int(c['iterations'])
  case=c['case'];T=mats[(case,'tangent')];N=mats[(case,'normal')];TN=mats[(case,'coupling_TN')];M=np.block([[T,TN],[TN.T,N]]);mats[(case,'metric')]=M
  eigs=eigvalsh(M);rr=[q for q in sp if q['case']==case and q['block']=='metric'];assert np.max(abs(eigs-np.array([float(q['eigenvalue']) for q in rr])))/max(1,max(abs(eigs)))<1e-9
  if c['mode']=='LIBRE':mats[(case,'admissible')]=M
  if c['first_order']=='PASS':assert float(c['KKT'])<=CFG['KKT'] and c['route'] in ['NATIVE_VERIFIED','PHYSICAL_SUSTAINED']
  # No se exige KKT completo en la carta normal: permanece descriptor distinto.
 for case,block,idx in sorted({(q['case'],q['block'],q['mode_index']) for q in nv}):
  rr=sorted([q for q in nv if q['case']==case and q['block']==block and q['mode_index']==idx],key=lambda q:int(q['node']));tt=np.array([float(q['T_coefficient']) for q in rr]);nn=np.array([float(q['N_coefficient']) for q in rr]);v=np.array([[float(q['t']),float(q['s'])] for q in rr]).reshape(-1);fraction=float(tt@tt/(tt@tt+nn@nn));assert abs(fraction-float(rr[0]['tangent_fraction']))<1e-10
  w=v if block=='physical' else (nn if block=='normal' else np.r_[tt,nn]);H=mats[(case,block)];lam=float(rr[0]['eigenvalue']);assert np.max(abs(H@w-lam*w))/max(1,np.linalg.norm(H,np.inf)*np.linalg.norm(w,np.inf))<1e-7
 for q in rows(b/'checks.csv'):
  if q['status']!='PASS':assert q['check']=='final_KKT',q
 summary=json.loads((b/'summary.json').read_text());assert summary['status']=='VALID_EXPLORATORY'
 quad=[q for q in cases if q['kind']=='quadratic'];h2=all(q['first_order']=='PASS' and q['diagnostics']=='PASS' for q in quad)
 for q in quad:
  negnormal=any(r['case']==q['case'] and r['block']=='normal' and r['negative']=='True' for r in sp);h2=h2 and not negnormal
  h2=h2 and (q['negative_admissible']=='0' if q['mode']=='COCIENTE' else int(q['negative_free_metric'])>0 and q['tangent_fraction_min']!='UNKNOWN' and float(q['tangent_fraction_min'])>=CFG['tangent_fraction'])
 h1=all(any(r['case']==f'quadratic/{m}/LIBRE' and r['block']=='normal' and r['negative']=='True' for r in sp) for m in CFG['meshes'])
 assert summary['verdict']==('H2' if h2 else ('H1_CANDIDATE_INSTRUMENT_DEFECT' if h1 else 'INCONCLUSIVE'))
 print('PASS_ARCHIVES: bandas/espectros, modos, controles, KKT y congelación',flush=True)
 with tempfile.TemporaryDirectory(prefix='e16ad-') as tmp:
  dest=Path(tmp);env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');code="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import part_a_v1 as a;a.ROOT=Path(sys.argv[2]);a.main()";subprocess.run([sys.executable,'-c',code,str(ROOT/'scripts'),str(dest)],env=env,check=True,timeout=CFG['budget_seconds']);aa=dest/'results/part_a_v1'
  for p in a.iterdir():
   if p.name!='resources.json':assert p.read_bytes()==(aa/p.name).read_bytes(),p.name
  bb=dest/'part_b_v1';subprocess.run([sys.executable,str(ROOT/'scripts/part_b_v1.py'),'--out',str(bb)],env=env,check=True,timeout=CFG['budget_seconds']);subprocess.run([sys.executable,str(ROOT/'scripts/archive_control_modes.py'),'--out',str(bb)],env=env,check=True)
  for p in b.iterdir():
   if p.name!='resources.json':assert p.read_bytes()==(bb/p.name).read_bytes(),p.name
  print('PASS_REPRODUCTION',json.loads((bb/'resources.json').read_text()),flush=True)
if __name__=='__main__':main()
