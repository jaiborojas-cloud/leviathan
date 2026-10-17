from pathlib import Path
import csv,json,hashlib,zipfile,io,shutil
P=Path('/workspace/scratch/54de7a7b7cce/current/Leviathan/Repro/T2_A')
W=Path('/workspace/scratch/54de7a7b7cce/incident_work')
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=list(csv.DictReader((P/'manifest.csv').open()))
checks=[]
for r in manifest:
 f=P/r['path']
 if f.is_file():
  ok=sha(f.read_bytes())==r['sha256'] and f.stat().st_size==int(r['bytes'])
  checks.append(dict(path=r['path'],sha256=sha(f.read_bytes()),expected=r['sha256'],match=ok));assert ok,r['path']
seal=json.loads((P/'baseline_seal_verification.json').read_text())
for n,h in seal['files'].items():assert sha((P/n).read_bytes())==h,n
cohort=list(csv.DictReader((P/'cohort_manifest.csv').open()))
pred=list(csv.DictReader((P/'predictors_locked.csv').open()))
assert len(cohort)==len(pred)==800
assert len({r['split'] for r in cohort})==160
assert all(r['baseline_status']=='BASELINE_EVALUATED' and r['predictor_status']=='PASS' for r in cohort)
assert [r['trajectory'] for r in cohort]==[f'split{s}_j{5+5*(s-8)+k}_true' for s in range(8,168) for k in range(5)]
visits=list(csv.DictReader((P/'visits.csv').open())); outcomes=list(csv.DictReader((P/'outcomes.csv').open()))
assert len(visits)==1 and visits[0]['trajectory']=='split8_j6_true' and visits[0]['step']=='25'
assert all(r['Y']=='' and r['status']=='PENDING' for r in outcomes)
archives=[]
for f in [P.parent.parent.parent/'RIPG_RESULTADOS_PC.zip',*sorted(P.glob('*139.zip'))]:
 z=zipfile.ZipFile(f);assert z.testzip() is None
 mn=[n for n in z.namelist() if n.endswith('manifest.json')][0]
 m=json.loads(z.read(mn));root=mn.rsplit('/',1)[0];hs=m.get('files',m)
 for n,h in hs.items():assert sha(z.read(root+'/'+n))==h,(f.name,n)
 item=dict(file=f.name,sha256=sha(f.read_bytes()),bytes=f.stat().st_size,crc='PASS',internal_hashes_verified=len(hs))
 if f.name=='RIPG_RESULTADOS_PC.zip':
  assert item['sha256']=='f082f89bd76f94e5bd8060021939008363228aabd0f377d0cd4cfa6eb1ca555b'
  idx=json.loads(z.read('output/index.json'));steps=[]
  for s in idx['segments']:
   data=z.read('output/'+s['file']);assert sha(data)==s['sha256'];zz=zipfile.ZipFile(io.BytesIO(data));assert zz.testzip() is None
   steps+=list(range(s['first_step'],s['last_step']+1))
  assert steps==list(range(91,140));assert idx['step']==139 and idx['status']=='PAUSED'
  item['index']=idx;item['segments_crc_verified']=13
  for n in ['index.json','return_manifest.json','equivalence.json']: (W/'evidence'/('PC_'+n)).write_bytes(z.read('output/'+n))
 archives.append(item)
for n in ['progress.md','task_log.csv','manifest.csv','Leviathan_RIPG_roadmap.md','visits.csv','outcomes.csv','cohort_manifest.csv']:
 shutil.copy2(P/n,W/'before'/n)
report=dict(schema_version=1,incident_id='T2A-split8_j5_true-update25-domain-v1',verification_scope='Documentary byte verification only; no scientific recomputation or new visits',manifest_entries_total=len(manifest),materialized_manifest_entries_verified=len(checks),manifest_checks=checks,archives=archives,baseline_seal_files_verified=seal['files'],cohort_count=800,baseline_evaluated=800,eligible_splits=160,closed_visits=1,complete_horizons=0,unknown_Y_count=800,base90_sha256_reference='de0f854646e9da24402b7adf5ce5ad055cea48230008d622bc0097d44244a987',base90_bytes_reverified_this_session=False,limitations=['Not a new byte audit of all 800 baseline ZIPs; prior full audit retained in seal.','Base90 and float64 step512 bytes not downloaded; recovery hashes verified as references in authenticated indices, not fresh payload verification.','Boundary ZIP absent from current root manifest: internal 10 hashes and CRC verified; new root entry will record observed SHA.'],before_files={n:sha((W/'before'/n).read_bytes()) for n in [x.name for x in (W/'before').iterdir()]})
(P/'incident_split8_j5_update25_v1_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['archives','manifest_checks','baseline_seal_files_verified','before_files']},indent=2))
