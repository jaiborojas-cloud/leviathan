from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent;W=P.parent;FOLDER='6abb9e9cf3908191a3e47f82f0f8e84b'
def persist(paths):
 ledger=P/'persistence_receipts.json';records=json.loads(ledger.read_text()) if ledger.exists() else [];latest={r['local_path']:r for r in records if r['status']=='succeeded'};items=[]
 for f in paths:
  f=str(Path(f).resolve());old=latest.get(f);x={'local_path':f,'purpose':'replace_library_file' if old else 'create_library_file'}
  if old:x.update(library_file_id=old['library_file_id'],expected_current_version=old['current_version_number'],version_reason='Incremental verified T1-B results')
  else:x['directory_id']=FOLDER
  items.append(x)
 proc=subprocess.run([sys.executable,str(W/'helpers_t1b/library_upload.py')],input=json.dumps({'uploads':items}),text=True,capture_output=True)
 if proc.returncode:raise RuntimeError('Persistence failed: '+proc.stderr[-500:])
 results=json.loads(proc.stdout)['results'];records+=results;ledger.write_text(json.dumps(records,indent=2))
 if any(x['status']!='succeeded' for x in results):raise RuntimeError('Persistence incomplete; inspect receipts, do not blindly retry')
 print('PERSISTED',len(results),flush=True)
if __name__=='__main__':persist([P/n for n in sys.argv[1:]])
