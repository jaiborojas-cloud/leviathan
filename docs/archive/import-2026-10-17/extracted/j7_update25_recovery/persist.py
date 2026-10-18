"""Operational persistence adapter; no scientific calculations."""
from pathlib import Path
import os,json,subprocess,sys
ROOT=Path('/workspace/scratch/54de7a7b7cce')
DEST=ROOT/'current/Leviathan/Repro/T2_A'
class PersistenceStopped(BaseException): pass
def persist(files):
 uploads=[]
 for f in map(Path,files):
  assert f.parent==DEST and f.is_file(),str(f)
  x=dict(local_path=str(f))
  try:
   ident=os.getxattr(f,'user.library-file-id').decode()
  except OSError:ident=None
  if ident:
   x.update(purpose='replace_library_file',library_file_id=ident,expected_current_version=int(os.getxattr(f,'user.library-file-version')),version_reason='Avance recuperable j7/update25; j5 retenido sin cambios')
  else:x.update(purpose='create_library_file',directory_id='6abbf2fa64188191b72ecce030a09e9a',library_artifact_type='other')
  uploads.append(x)
 result=subprocess.run([sys.executable,str(ROOT/'.library_j7/library_upload.py')],input=json.dumps({'uploads':uploads}),text=True,capture_output=True)
 if result.returncode:raise PersistenceStopped(result.stderr)
 rr=json.loads(result.stdout)
 if not all(r['status']=='succeeded' for r in rr['results']):raise PersistenceStopped(json.dumps(rr))
 with (ROOT/'j7_run/persistence_receipts.jsonl').open('a') as log:log.write(json.dumps(rr)+'\n')
 print('PERSISTED',len(files),flush=True)
