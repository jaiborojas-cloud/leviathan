#!/usr/bin/env python3
"""Comprobaciones de archivos AG; no integra geodésicas ni reejecuta etapas."""
from ag_common_v1 import *
from run_v1 import assessment
import subprocess,ast

def main():
 result=ROOT/'results/run_v1'
 for name in ['freeze_manifest.csv','implementation_manifest_v1.csv','manifest.csv']:
  for row in rows(ROOT/name):assert sha(ROOT/row['path'])==row['sha256'],row['path']
 assert subprocess.run(['git','merge-base','--is-ancestor','e9e4034','6f814a2'],cwd=REPO).returncode==0
 for filename in ['DESIGN_FROZEN.md','config.json','THEORY.md']:
  assert subprocess.check_output(['git','show','e9e4034:experiments/E16/AG/'+filename],cwd=REPO)==(ROOT/filename).read_bytes()
 paths=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=REPO).decode().splitlines();assert all(p.startswith('experiments/E16/AG/') for p in paths)
 states=json.loads((result/'inputs.json').read_text());assert len(states)==80 and len({x['id'] for x in states})==80
 original=json.loads((REPO/CFG['af_inputs']).read_text())['states']
 for st,prev in zip(states[40:],original):assert st['M']==prev['M'] and st['f']==prev['f']
 outcome=rows(result/'states.csv');assert len(outcome)==80
 numeric=['rho','d_escape','ratio','ratio_true','escape_to_true','d_border_exact','rho_exact','rho_seconds','exp_seconds','stop_over_rho']
 parsed=[]
 for row in outcome:
  r=dict(row)
  for k in numeric:r[k]=float(r[k]) if r[k] else None
  r['refined_valid']=r['refined_valid']=='True';parsed.append(r)
  if r['ratio'] is not None:assert abs(r['ratio']-r['rho']/r['d_escape'])<1e-10*max(1,r['ratio'])
 controls=rows(result/'controls.csv');assert len(controls)==11 and all(c['status']=='PASS' for c in controls)
 mperrors=[]
 with mp.workdps(80):
  E=mp.matrix([[mp.mpf(1)/9 if i//9==j else 0 for j in range(3)] for i in range(27)]);center=mp.matrix([mp.mpf(1)/3]*3);verts=[mp.matrix([1 if i==j else 0 for i in range(3)]) for j in range(3)]
  for st,r in zip(states[:40],parsed[:40]):
   M=mp.matrix([[mp.mpf(float(x)) for x in line] for line in st['M']]);W=E.T*M*E;distances=[];ends=list(verts)
   for i,j in [(0,1),(1,2),(2,0)]:
    v=verts[j]-verts[i];t=max(0,min(1,((center-verts[i]).T*W*v)[0]/(v.T*W*v)[0]));foot=verts[i]+t*v;delta=center-foot;distances.append(mp.sqrt((delta.T*W*delta)[0]));ends.append((verts[i]+verts[j])/2)
   db=min(distances);rho=min(mp.sqrt(((center-p).T*W*(center-p))[0]) for p in ends);error=max(abs(db-mp.mpf(r['d_border_exact']))/db,abs(rho-mp.mpf(r['rho_exact']))/rho);mperrors.append(float(error));assert error<mp.mpf('1e-10');assert r['control_exact']=='PASS'
 arrays=rows(result/'arrays.csv');res=json.loads((result/'resources.json').read_text());base=Path(res['arrays_root'])
 for row in arrays:
  p=base/row['file'];assert sha(p)==row['sha256'];a=np.load(p,mmap_mode='r',allow_pickle=False);assert a.shape==ast.literal_eval(row['shape'])
 groups,summary=assessment(parsed,True);official=json.loads((result/'summary.json').read_text());assert summary==official
 for key in ['geometry','audit']:assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256']
 assert sum(x['blocked_reads'] for x in res['worker_resources'])==0
 # La guarda se prueba por llamada directa con ruta ficticia; no se abre nada.
 try:af.access_guard('open',(str(REPO/'experiments/T2_A1/AG_FICTITIOUS_PROBE'),'r'))
 except PermissionError:pass
 else:raise AssertionError('guarda T2')
 report={'status':'PASS','states':80,'controls':11,'exact_triangle_MP80_max_relative_error':max(mperrors),'external_arrays_verified':len(arrays),'scientific_code_reexecuted':False,'scientific_T2_reads':0,'guard_fictitious_probe':'PASS','state_and_summary_consistency':'PASS','design_before_code':'e9e4034 -> 6f814a2'}
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
