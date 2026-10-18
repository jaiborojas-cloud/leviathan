from pathlib import Path
import json,hashlib,csv,zipfile,collections
P=Path(__file__).resolve().parent;W=P.parent;A=W/'t1b_inputs/Leviathan/Repro/E15_T1_A'
sha=lambda b:hashlib.sha256(b).hexdigest()
report={};pk=A/'summary_and_scripts.zip'
assert sha(pk.read_bytes())==(A/'summary_and_scripts.zip.sha256').read_text().split()[0]
with zipfile.ZipFile(pk) as z:
 assert z.testzip()is None;assert z.read('manifest.csv')==(A/'manifest.csv').read_bytes()
report['T1A_summary_sha256']=sha(pk.read_bytes())
manifest=list(csv.DictReader((A/'manifest.csv').open()));lookup={r['path']:r for r in manifest};zs=sorted(A.glob('split*_j*_*.zip'));assert len(zs)==80
for zp in zs:
 assert sha(zp.read_bytes())==lookup[zp.name]['sha256']
 with zipfile.ZipFile(zp) as z:
  assert z.testzip()is None;z.extractall(A)
with zipfile.ZipFile(A/'common_sources.zip') as z:assert z.testzip()is None;z.extractall(A)
bad=[];missing=[]
for r in manifest:
 f=A/r['path']
 if not f.exists():missing.append(r['path']);continue
 if f.stat().st_size!=int(r['bytes']) or sha(f.read_bytes())!=r['sha256']:bad.append(r['path'])
report.update(T1A_manifest_entries=len(manifest),T1A_manifest_mismatches=bad,T1A_manifest_missing=missing,T1A_state_archives=80)
# Validate original C1 and A2 archived manifests without relying on extracted copies.
for name,expected in [('Leviathan_E15_C1_codigo_resultados','397d0b0d274ffaf72f98b79d8bf3b7c8442cc8916b041a8f5e8cf64a490a7adc'),('Leviathan_E15_C1_A2_codigo_resultados','18dbde0b50fe998274c105ef59618420413d7fbae49100628831527f1fa98648')]:
 f=W/'inputs/Leviathan/Repro'/(name+'.zip');assert sha(f.read_bytes())==expected
 with zipfile.ZipFile(f) as z:
  assert z.testzip()is None;root='E15_C1_A2/' if '_A2_'in name else 'E15_C1/';rr=list(csv.DictReader(z.read(root+'MANIFEST_SHA256.csv').decode().splitlines()));wrong=[r['path'] for r in rr if sha(z.read(root+r['path']))!=r['sha256'] or len(z.read(root+r['path']))!=int(r['bytes'])];assert not wrong
 report[name]={'sha256':expected,'manifest_entries':len(rr),'mismatches':wrong,'CRC':'PASS'}
cpman=json.loads((A/'inherited_checkpoint_manifest.json').read_text());cpchecks=[]
for r in cpman:
 name=r['file'].removeprefix('wine_').removesuffix('.pt');p=A/'states'/name/'checkpoint.pt';assert sha(p.read_bytes())==r['sha256'];cpchecks.append({'state':name,'sha256':r['sha256']})
rows=list(csv.DictReader((A/'state_results.csv').open()));assert len(rows)==80
historical=[n for n in missing if n.endswith('.tmp.npz') and (A/n.replace('.tmp.npz','.npz')).exists()]
blocking_missing=[n for n in missing if n not in historical]
final_arrays=0
for d in (A/'states').iterdir():
 for sub in ['boundary','jacobi','rk4']:
  for f in (d/sub).glob('*.json'):
   if 'error' not in json.loads(f.read_text()):
    with zipfile.ZipFile(f.with_suffix('.npz')) as z:assert z.testzip()is None
    final_arrays+=1
report.update(final_arrays_verified=final_arrays,historical_temporary_absence=historical,scientific_inputs_status='PASS')
report.update(checkpoints=cpchecks,checkpoint_count=len(cpchecks),counts=dict(collections.Counter(x['classification'] for x in rows)),status='PASS_WITH_ARCHIVAL_NOTE' if historical and not bad and not blocking_missing else 'PASS' if not bad and not blocking_missing else 'FAIL')
(P/'input_integrity.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checkpoints'},indent=2));assert not bad and not blocking_missing
