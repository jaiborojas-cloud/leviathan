# Correct file selection only. Reuse terminal tasks; no integration allowed.
import os
os.environ['T1_REPROCESS']='1'
from pathlib import Path
import json,hashlib,zipfile,time
import run_map_postprocess as runner
P=Path(__file__).resolve().parent

def existing(fn,sub,prefix):
 def wrapped(case,n,ph):
  p=P/'states'/case/sub/f'{prefix}{n}_phase{ph}.json'
  if not p.exists():raise RuntimeError('Refusing to integrate missing task during postprocessing recovery: '+str(p))
  return json.loads(p.read_text())
 return wrapped
runner.boundary=existing(None,'boundary','n');runner.jacobi=existing(None,'jacobi','n');runner.rk=existing(None,'rk4','steps')
rows=[]
for f in sorted((P/'states').glob('*/result.json')):
 old=json.loads(f.read_text())
 if old['classification']!='INCONCLUSIVE' or 'BadZipFile' not in old.get('errors',''):continue
 d=f.parent;before={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob('*') if p.is_file() and p.name!='result.json'}
 archive=d/'result_before_postprocess_correction.json'
 if not archive.exists():archive.write_bytes(f.read_bytes())
 new=runner.result(d.name)
 new['postprocess_correction']='Excluded noncanonical .tmp.npz files. All final task JSON/NPZ reused; no numerical rerun, no state substitution, no rule change.'
 new['new_wall_seconds']+=old['new_wall_seconds'];new['new_cpu_seconds']+=old['new_cpu_seconds']
 changed=[n for n,h in before.items() if hashlib.sha256((d/n).read_bytes()).hexdigest()!=h];assert not changed
 runner.atomic_save(f,new);rows.append(dict(state=d.name,before=old['classification'],after=new['classification'],changed_task_files=changed,retained_previous_result=archive.name))
 # Save revised archive preserving prior result and all original diagnostics.
 zpath=P/(d.name+'.zip');tmp=zpath.with_suffix('.tmp.zip')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(d.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(P)))
 tmp.replace(zpath);runner.persist([zpath]);runner.checkpoint_progress();runner.persist([P/n for n in ['state_results.csv','task_log.csv','failures.md','manifest.csv','progress.md']])
(P/'postprocess_recovery.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
