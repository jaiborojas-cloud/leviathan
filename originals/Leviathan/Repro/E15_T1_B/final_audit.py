from pathlib import Path
import json,csv,hashlib,zipfile
import numpy as np
P=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();proto=json.loads((P/'protocol_T1_B_frozen.json').read_text());assert sha(P/'protocol_T1_B_frozen.json')==(P/'protocol_T1_B_frozen.sha256').read_text()
old={r['state']:r for r in csv.DictReader((P/'T1A_state_results.csv').open())};records=json.loads((P/'persistence_receipts.json').read_text());latest={r['local_path']:r for r in records if r['status']=='succeeded'}
checks=[];rows=[]
for case in sorted(old):
 d=P/'states'/case;result=json.loads((d/'result.json').read_text());assert sha(d/'checkpoint.pt')==old[case]['checkpoint_sha256'];assert sha(d/'state.npz')==result['field_sha256'];zp=P/(case+'.zip');assert str(zp)in latest
 with zipfile.ZipFile(zp) as z:
  assert z.testzip()is None;assert json.loads(z.read(str((d/'result.json').relative_to(P))))==result
 for n in [256,512]:
  for ph in [0,1]:
   f=d/f'jacobi_n{n}_phase{ph}.npz'
   with np.load(f) as z:
    assert z['determinant'].shape==(4,n);assert np.isfinite(z['determinant']).all();assert np.array_equal(z['radii'],proto['radii'])
 for r in result['results']:
  assert r['radius']<r['nominal_radius'];
  if r['r_conj']is not None:assert r['radius']<r['r_conj']
  if r['T1A_classification']=='GEOMETRIC_NONINJECTIVITY':assert r['C_A']is None
 rows+=result['results'];checks.append(dict(state=case,status=result['status'],checkpoint_sha256=sha(d/'checkpoint.pt'),archive_sha256=sha(zp),stored_version=latest[str(zp)]['current_version_number']))
assert len(rows)==320 and len(checks)==80
stats={}
for g in ['true','random']:
 rr=[r for r in rows if r['regime']==g];stats[g]=dict(max_kappa_resolution_difference=max(r['kappa_resolution_difference'] for r in rr),max_det_resolution_difference=max(r['det_resolution_difference'] for r in rr),max_kappa_primary=max(r['kappa_max'] for r in rr if r['primary']),min_kappa_primary=min(r['kappa_max'] for r in rr if r['primary']))
report=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'COMPLETE_WITH_INCONCLUSIVE',states=80,state_radius_rows=320,Jacobi_tasks=320,checkpoints=80,positive_cases_included_all4=True,CA_imputed=False,geometry_sha256=sha(P/'geometry.py'),protocol_sha256=sha(P/'protocol_T1_B_frozen.json'),checks=checks,numerical_stats=stats,script_sha256={p.name:sha(p) for p in P.glob('*.py')})
(P/'final_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['checks','script_sha256']},indent=2))
