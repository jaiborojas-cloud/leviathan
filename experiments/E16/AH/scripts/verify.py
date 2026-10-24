#!/usr/bin/env python3
"""Verifica AH desde archivos y MP ya archivado, sin reintegrar curvas."""
from ah_common import *
from search_v1 import summarize
import subprocess,ast

def main():
 result=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest_v1.csv','manifest.csv']:
  for row in rows(ROOT/name):assert sha(ROOT/row['path'])==row['sha256'],row['path']
 assert subprocess.run(['git','merge-base','--is-ancestor','d62326a','dad765e'],cwd=REPO).returncode==0
 for name in ['DESIGN_FROZEN.md','config.json','THEORY.md']:
  assert subprocess.check_output(['git','show','d62326a:experiments/E16/AH/'+name],cwd=REPO)==(ROOT/name).read_bytes()
 changes=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=REPO).decode().splitlines();assert all(p.startswith('experiments/E16/AH/') for p in changes)
 assert sha(result/'inputs.json')==CFG['inputs_sha256'];states=json.loads((result/'inputs.json').read_text());assert len(states)==80 and len({s['id'] for s in states})==80
 data=rows(result/'states.csv');assert len(data)==80;candidates=rows(result/'candidates.csv');ctrl=rows(result/'controls.csv');assert len(ctrl)==13 and all(c['status']=='PASS' for c in ctrl)
 fields=['rho0','rho0_grid','rho1','d_border','rho1_over_true','rho1_over_rho0','time_rho0','time_incremental','time_total','numeric_relative_error'];parsed=[];alternate=[];maxMP=0.;tails=[]
 for st,r in zip(states,data):
  assert st['id']==r['state'];p=dict(r)
  for k in fields:p[k]=float(p[k]) if p[k] else None
  parsed.append(p)
  if r['status']!='PASS':assert r['reason'];alternate.append(p.copy());continue
  assert r['baseline_control']=='PASS' and r['baseline_MP']=='PASS';assert p['time_total']>=p['time_rho0'] and int(r['evaluations'])<=4096
  cs=[c for c in candidates if c['state']==r['state']];winner=next(c for c in cs if int(c['candidate'])==int(r['winner_candidate']));base=next(c for c in cs if c['branch']=='baseline');assert winner['MP_status']==base['MP_status']=='PASS';assert float(winner['length'])==p['rho1'] and float(base['length'])==p['rho0'];assert p['rho1']==min(float(c['length']) for c in cs if c['MP_status']=='PASS');assert p['rho1']<=p['rho0']
  assert float(winner['MP_relative_error'])<=1e-7;assert float(base['MP_relative_error'])<=1e-7;maxMP=max(maxMP,float(winner['MP_relative_error']),float(base['MP_relative_error']));assert abs(p['rho1_over_rho0']-p['rho1']/p['rho0'])<1e-12
  if st['group']=='triangle':assert abs(p['rho1_over_true']-p['rho1']/p['d_border'])<1e-12
  else:assert p['d_border'] is None
  F=Family(np.array(st['M']),np.array(st['f']),p['rho0_grid']);q=json.loads(winner['q']);support=json.loads(winner['support']);theta=float(winner['theta']);b,z,S,cuts,tail=F.parameters(q,theta,support);assert tail<=1e-14*p['rho0_grid']*(1+1e-8);assert abs(tail-float(winner['tail_bound']))<=1e-10*max(tail,1e-30);tails.append(tail)
  Q=np.array([float(r['Q1_P']),float(r['Q2_P'])]);ids=json.loads(r['support_original']);endpoint=np.array(json.loads(r['endpoint_original']));assert abs(endpoint.sum()-1)<1e-12 and endpoint.min()>=0
  expected=np.zeros(len(endpoint));expected[ids]=softmax(np.array(st['f'])[ids]@Q);assert np.max(abs(endpoint-expected))<1e-12
  alt=p.copy();alt['rho1']=float(winner['MP_high']);alt['rho0']=float(base['MP_high']);alt['rho1_over_rho0']=alt['rho1']/alt['rho0'];alt['rho1_over_true']=alt['rho1']/p['d_border'] if p['d_border'] else None;alternate.append(alt)
 groups,summary=summarize(parsed);summary.update(precontrols=len(ctrl),null_controls_pass=sum(r['baseline_control']=='PASS' for r in data),null_controls_unknown=sum(r['baseline_control']=='UNKNOWN' for r in data))
 if any(r['baseline_control']=='FAIL' for r in data):summary.update(status='INVALID',**{f'Q{i}':'INCONCLUSIVE' for i in range(1,6)})
 assert summary==json.loads((result/'summary.json').read_text())
 _,alt_summary=summarize(alternate)
 for k in ['Q1','Q2','Q3','Q4','Q5']:assert summary[k]==alt_summary[k],k
 arrays=rows(result/'arrays.csv');res=json.loads((result/'resources.json').read_text());base=Path(res['arrays_root'])
 for row in arrays:
  path=base/row['file'];assert sha(path)==row['sha256'];a=np.load(path,mmap_mode='r',allow_pickle=False);assert a.shape==ast.literal_eval(row['shape'])
  if row['label']=='fast_evaluations':assert len(a)<=4096
  if row['label']=='winner_profile':assert np.max(abs(a[:,5:].sum(axis=1)-1))<1e-12 and np.min(a[:,5:])>=0
 for key in ['geometry','audit']:assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256']
 assert sum(r['blocked_T2_reads'] for r in res['worker_resources'])==0
 # Prueba ficticia directa: no abre un archivo prohibido real.
 try:ag.af.access_guard('open',(str(REPO/'experiments/T2_A1/AH_FICTITIOUS_PROBE'),'r'))
 except PermissionError:pass
 else:raise AssertionError('guarda')
 print(json.dumps({'status':'PASS','states':len(data),'precontrols':13,'valid':summary['valid'],'null_controls_pass':summary['null_controls_pass'],'external_arrays_verified':len(arrays),'max_MP_relative_error':maxMP,'tail_bound_max':max(tails) if tails else None,'quad_vs_MP_verdicts':'PASS','guard_probe':'PASS, ficticio sin abrir datos','scientific_T2_reads':0,'curves_reintegrated':False,'design_before_code':'d62326a -> dad765e'},indent=2))
if __name__=='__main__':main()
