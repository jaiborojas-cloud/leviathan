#!/usr/bin/env python3
"""Verificación algebraica y de archivos; no llama al instrumento ni integra."""
from common_v1 import *
from references_v1 import norm
import subprocess,ast

def main():
 out=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest_v1.csv','manifest.csv']:
  for r in rows(ROOT/name):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 assert subprocess.run(['git','merge-base','--is-ancestor','2269b7f','61e7fe6'],cwd=REPO).returncode==0
 for name in ['DESIGN_FROZEN.md','THEORY.md','config.json']:
  assert subprocess.check_output(['git','show','2269b7f:experiments/DIN_borde/D2/'+name],cwd=REPO)==(ROOT/name).read_bytes()
 changes=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=REPO).decode().splitlines();assert all(x.startswith('experiments/DIN_borde/D2/') for x in changes)
 inp=json.loads((out/'inputs.json').read_text());panels=inp['panels'];cases=inp['cases'];assert len(panels)==12 and len(cases)==210;by_panel={p['id']:p for p in panels};data=rows(out/'states.csv');raw=json.loads((out/'raw_and_references.json').read_text());assert len(data)==len(raw)==210 and len({r['state'] for r in data})==210
 for p in panels:assert exposed(np.array(p['f']))==p['topology']
 all_arrays=rows(out/'arrays.csv');res=json.loads((out/'resources.json').read_text());array_root=Path(res['arrays_root']);counts={k:0 for k in ['PASS','FAIL','INCONCLUSIVE']};known=0;matrix_checks=0;chord_checks=[]
 for case,row,record in zip(cases,data,raw):
  assert case['id']==row['state']==record['state'];p=by_panel[case['panel']];M=np.load(array_root/next(a['file'] for a in all_arrays if a['state']==case['id'] and a['label']=='M'),allow_pickle=False);assert np.array_equal(M,matrix(case));assert abs(M.trace()-1)<1e-12;kind=case['kind'];n=len(M);ell=float(row['lambda_max'])
  if kind in ['coordinate','contrast','constant','centered','random_rank1']:expected=1.
  elif kind=='isotropic':expected=1/n
  elif kind=='null_mix':expected=case['lam']
  elif kind=='face_projector':expected=1/(n-1)
  elif case['N']=='isotropic':expected=1-case['epsilon']+case['epsilon']/n
  else:
   eps=case['epsilon'];expected=(1+math.sqrt(1-4*eps*(1-eps)*(1-1/n)))/2
  assert abs(ell-expected)<1e-10,(case['id'],ell,expected);assert row['matrix_control']=='PASS';matrix_checks+=1
  G=record['reference'].get('global')
  if G and G['known_exact']:
   exact=None
   if kind in ['coordinate','centered','perturb']:
    base,_=coordinate_value(p,case['k']);exact=float(base)
    if kind=='centered':exact/=math.sqrt(1-1/n)
    if kind=='perturb':exact=math.sqrt(1-case['epsilon'])/n if case['N']=='constant' else math.sqrt(1-case['epsilon']+case['epsilon']/(n-1))/n
   elif kind=='isotropic':exact=1/(n*math.sqrt(n-1))
   else:exact=0.
   assert abs(exact-G['exact'])<1e-12;known+=1
   if row['global_reference_control']=='PASS':assert abs(G['upper_witness']['value']-exact)<=1e-12+1e-8*abs(exact)
  counts[row['Q5']]+=1
  if row['Q5']=='FAIL':assert record['native']['status'] in ['ERROR','NEGATIVE','NONFINITE_DIAGNOSTICS'] or 'FAIL' in [row['minimum_check'],row['witness_check']]
  if row['witness_check']=='FAIL':
   R=record['reference']['native_direction'];assert R['status']=='PASS';assert abs(float(row['native_rho'])-R['value'])>CFG['absolute_tolerance']+CFG['relative_tolerance']*abs(R['value'])
   with mp.workdps(80):
    theta=float(record['native']['raw']['theta']);u=[fr(math.cos(theta)),fr(math.sin(theta))];rr=[fr(x[0])*u[0]+fr(x[1])*u[1] for x in p['f']];S=[i for i,x in enumerate(rr) if x==max(rr)];delta=[(mp.mpf(1)/len(S) if i in S else mp.mpf(0))-mp.mpf(1)/n for i in range(n)];bound=norm(case,delta);chord_checks.append({'state':case['id'],'native_rho':float(row['native_rho']),'endpoint_chord_lower':mp.nstr(bound,60),'support':S,'contradiction':float(bound)>float(row['native_rho'])+CFG['absolute_tolerance']+CFG['relative_tolerance']*float(bound)})
 for a in all_arrays:
  path=array_root/a['file'];assert sha(path)==a['sha256'];v=np.load(path,mmap_mode='r',allow_pickle=False);assert v.shape==ast.literal_eval(a['shape'])
 ctrl=rows(out/'controls.csv');assert len(ctrl)==8 and all(c['status']=='PASS' for c in ctrl);summary=json.loads((out/'summary.json').read_text());assert summary['Q5_counts']==counts and summary['states']==210 and summary['status']=='VALID_EXPLORATORY';assert summary['matrix_controls_pass']==210
 assert summary['Q5']==('FAIL' if counts['FAIL'] else ('PASS' if counts['PASS']==210 else 'INCONCLUSIVE'))
 assert all(summary['Q'+str(i)]=='PASS' for i in [1,2,3]) and summary['Q4']=='PASS_DESCRIPTIVE'
 for key in ['geometry','rho']:assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256']
 assert sum(x['blocked_T2_reads'] for x in res['worker_resources'])==0
 try:guard('open',(str(REPO/'experiments/T2_A1/baseline/D2_FICTITIOUS_PROBE'),'r'))
 except PermissionError:pass
 else:raise AssertionError('guarda')
 print(json.dumps({'status':'PASS','panels':12,'states':210,'known_global_values_checked':known,'spectral_and_matrix_checks':matrix_checks,'reference_controls':8,'external_arrays_verified':len(all_arrays),'Q5_counts':counts,'source_hashes':'PASS','native_function_reexecuted':False,'reference_curves_reintegrated':False,'endpoint_checks_for_existing_witness_failures':chord_checks,'guard_probe':'PASS, ficticio sin abrir archivos','scientific_T2_states_read':0,'design_before_code':'2269b7f -> 61e7fe6'},indent=2))
if __name__=='__main__':main()
