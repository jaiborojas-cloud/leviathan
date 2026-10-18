from pathlib import Path
import json,subprocess,sys,os,hashlib,csv,datetime
P=Path(__file__).resolve().parent;W=P.parent;folder='6abb22e29ec88191a8b98568bd0a0899';ledger=P/'persistence_receipts.json'
def persist(paths):
 records=json.loads(ledger.read_text()) if ledger.exists() else json.loads((W/'initial_upload_result.json').read_text())['results']
 latest={r['local_path']:r for r in records if r['status']=='succeeded'};uploads=[]
 for path in paths:
  path=str(Path(path).resolve());old=latest.get(path);u={'local_path':path,'purpose':'replace_library_file' if old else 'create_library_file'}
  if old:u.update(library_file_id=old['library_file_id'],expected_current_version=old['current_version_number'],version_reason='Incremental verified T1-A progress')
  else:u['directory_id']=folder
  uploads.append(u)
 r=subprocess.run([sys.executable,str(W/'helpers/library_upload.py')],input=json.dumps({'uploads':uploads}),text=True,capture_output=True)
 if r.returncode:raise RuntimeError('Persistence failed: '+r.stderr[-1000:])
 payload=json.loads(r.stdout);results=payload['results'];records+=results
 tmp=ledger.with_suffix('.tmp');tmp.write_text(json.dumps(records,indent=2));tmp.replace(ledger)
 if any(x['status']!='succeeded' for x in results):raise RuntimeError('Some persistence items failed; inspect receipts')
 print('PERSISTED',len(results),flush=True)
if __name__=='__main__':persist([P/n for n in sys.argv[1:]])
