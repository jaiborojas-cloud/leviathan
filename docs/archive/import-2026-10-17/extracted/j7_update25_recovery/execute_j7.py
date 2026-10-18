"""Explicit j7 continuation. Frozen scientific functions; operational imports/IO only."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,csv,hashlib,zipfile,shutil,ast,types,time,traceback
import numpy as np
from scipy.optimize import brentq
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent;P=R.parent/'current/Leviathan/Repro/T2_A';case='split8_j7_true';D=R/'future/t025/states'/case
sys.path.insert(0,str(R/'instrument'))
import audit,geometry,topological_map
from geometry import area7,triangles
from resumable_dop853 import Driver,IntegrationPaused
from persist import persist
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Execute exact AST bodies only. Unneeded training/comparator imports are not executed.
# This neither loads/retrains the neural model nor reconstructs its stored field.
source=ast.parse((R/'baseline_geometry.py').read_text())
nodes=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['saved','field','calibrate']]
assert len(nodes)==3
namespace=dict(np=np,json=json,time=time,audit=audit,area7=area7,triangles=triangles,brentq=brentq,Polygon=Polygon,ROOT=R/'future/t025')
exec(compile(ast.Module(body=nodes,type_ignores=[]),'baseline_geometry.py:frozen_functions','exec'),namespace)
audit.P=topological_map.P=R/'future/t025'
for n,h in json.loads((P/'baseline_seal_verification.json').read_text())['files'].items():assert sha(P/n)==h,n
mr={x['path']:x for x in csv.DictReader((P/'manifest.csv').open())}
for n in ['baseline_geometry.py','resumable_dop853.py','resumable_dop853_validation.json','instrument_sources_resumable.zip']:
 assert sha(P/n)==mr[n]['sha256'],n
partial=next(x for x in json.loads((P/'followup_partial_snapshot.json').read_text())['partial'] if x['trajectory']==case)
for n in ['checkpoint.pt','state.npz']:assert sha(D/n)==partial[n+'_sha256']
assert not(D/'visit_complete.json').exists()
assert json.loads((P/'incident_split8_j5_update25_v1.json').read_text())['scientific_resolution']=='UNRESOLVED'
index_path=P/'ode_resume_split8_j7_update25.json'
index=json.loads(index_path.read_text()) if index_path.exists() else dict(trajectory=case,step=25,status='READY_FROM_PERSISTED_FIELD',snapshots=[])
def manifest_update():
 rows=list(csv.DictReader((P/'manifest.csv').open()));by={r['path']:r for r in rows}
 for f in P.iterdir():
  if f.is_file() and f.name!='manifest.csv' and (f.name in ['progress.md','task_log.csv'] or f.name.startswith(('ode_t025_split8_j7','ode_resume_split8_j7','j7_update25_','visit_t025_split8_j7'))):
   v=dict(path=f.name,bytes=str(f.stat().st_size),sha256=sha(f))
   if f.name in by:by[f.name].update(v)
   else:rows.append(v)
 with (P/'manifest.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(rows)
def checkpoint(z,meta,m):
 archive=P/f'ode_t025_{case}_{z.parent.name}_{z.name}';shutil.copyfile(z,archive)
 entry=dict(archive=archive.name,sha256=sha(archive),restore_archive_to=str(z.relative_to(R)),restore_metadata_to=str(meta.relative_to(R)),metadata=m)
 index['snapshots'].append(entry);index['latest']=entry;index['status']='PARTIAL_NOT_CLASSIFIED'
 index_path.write_text(json.dumps(index,indent=2)+'\n')
 with (P/'task_log.csv').open('a',newline='') as f:csv.writer(f).writerow([case,f'ODE_UPDATE025_{z.parent.name}_STEP{m["steps"]}','PARTIAL_NOT_CLASSIFIED',m['cpu_seconds'],m['wall_seconds'],sha(archive)])
 with (P/'progress.md').open('a') as f:f.write(f'\n## Avance j7/update25 — 2026-10-17 UTC\nPasos aceptados guardados:{m["steps"]}; radio integrado:{m["t"]:.17g}; nfev:{m["nfev"]}. No es radio nominal ni clasificación. Índice:ode_resume_split8_j7_update25.json. J5 permanece retenido PAUSED139; j6 no se repite.\n')
 manifest_update();persist([archive,index_path,P/'task_log.csv',P/'progress.md',P/'manifest.csv'])
driver=Driver(R/'ode_checkpoints'/f't025_{case}',sha(D/'state.npz'),max_new_steps=128,every=32,on_commit=checkpoint)
status='STARTED';started=time.perf_counter();error=None
geometry.solve_ivp=driver
try:
 nominal=namespace['calibrate'](case)
 status='CALIBRATION_COMPLETE_TOPOLOGY_PENDING'
 print('CALIBRATION_COMPLETE',json.dumps(nominal),flush=True)
except IntegrationPaused:
 status='PAUSED_AT_PERSISTED_ACCEPTED_STEP'
except Exception:
 status='CALIBRATION_UNRESOLVED';error=traceback.format_exc();print(error,flush=True)
finally:
 index['status']=status
 if error:index['error']=error
 index_path.write_text(json.dumps(index,indent=2)+'\n')
 summary=dict(trajectory=case,step=25,status=status,error=error,visit_complete=False,classification=None,Y=None,wall_seconds=time.perf_counter()-started,checkpoint_sha256=sha(D/'checkpoint.pt'),field_sha256=sha(D/'state.npz'),last_snapshot=index.get('latest'),j5_held=True)
 (P/'j7_update25_session.json').write_text(json.dumps(summary,indent=2)+'\n')
 archive=P/'j7_update25_recovery.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(D.rglob('*')):
   if f.is_file():z.write(f,str(f.relative_to(R)))
  for n in ['execute_j7.py','persist.py','baseline_geometry.py','resumable_dop853.py','resumable_dop853_validation.json','protocol.json']:z.write(R/n,n)
  for f in (R/'instrument').glob('*.py'):z.write(f,str(f.relative_to(R)))
  z.write(index_path,index_path.name)
  z.write(P/'j7_update25_session.json','j7_update25_session.json')
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 with (P/'progress.md').open('a') as f:f.write(f'\nJ7/update25 cierre de lote: {status}. Sin clasificación ni outcome nuevos. Recuperación:j7_update25_recovery.zip + snapshots del índice específico. No reentrenar.\n')
 manifest_update();persist([archive,index_path,P/'j7_update25_session.json',P/'progress.md',P/'manifest.csv'])
 print('SESSION_END',status,flush=True)
