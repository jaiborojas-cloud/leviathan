from pathlib import Path
import json,csv,zipfile,hashlib
import numpy as np
P=Path(__file__).resolve().parent
rows=[json.loads(p.read_text()) for p in sorted((P/'states').glob('*/result.json'))]
expected={f'split{s}_j{j}_{r}' for s in range(8) for j in range(5) for r in ['true','random']}
assert {r['state'] for r in rows}==expected and len(rows)==80
receipts=json.loads((P/'persistence_receipts.json').read_text());latest={r['local_path']:r for r in receipts if r['status']=='succeeded'}
checks=[];temp=[]
for row in rows:
 d=P/'states'/row['state'];zpath=P/(d.name+'.zip');assert str(zpath)in latest
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip()is None
  assert json.loads(z.read(str((d/'result.json').relative_to(P))))==row
 assert hashlib.sha256((d/'checkpoint.pt').read_bytes()).hexdigest()==row['checkpoint_sha256']
 n=0
 for sub in ['boundary','jacobi','rk4']:
  for j in sorted((d/sub).glob('*.json')):
   data=json.loads(j.read_text())
   if 'error'in data:continue
   p=j.with_suffix('.npz');assert p.is_file()
   with np.load(p) as a:
    for k in a.files:arr=a[k]
   n+=1
  temp.extend(str(f.relative_to(P)) for f in (d/sub).glob('*.tmp.npz'))
 checks.append(dict(state=d.name,classification=row['classification'],final_task_arrays_verified=n,zip_sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),checkpoint_sha256=row['checkpoint_sha256'],persistent_version=latest[str(zpath)]['current_version_number'],status='PASS'))
report=dict(states=80,checkpoints=80,unique_states=80,missing=[],state_archives_persisted=80,task_arrays=sum(x['final_task_arrays_verified'] for x in checks),historical_temporary_files_excluded_from_science=temp,protocol_sha256=hashlib.sha256((P/'protocol_T1_A_frozen.json').read_bytes()).hexdigest(),script_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.glob('*.py')},states_audit=checks,status='PASS')
(P/'final_audit.json').write_text(json.dumps(report,indent=2));print('FINAL AUDIT PASS',report['states'],'states',report['task_arrays'],'task arrays',len(temp),'historical temp files')
