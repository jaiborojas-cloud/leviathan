from pathlib import Path
import hashlib,json,csv,zipfile
P=Path(__file__).resolve().parent
root=P.parent
reports=[]
for name in ['Leviathan_E15_C1_codigo_resultados','Leviathan_E15_C1_A2_codigo_resultados']:
 zpath=root/'inputs/Leviathan/Repro'/f'{name}.zip'
 d=root/'unpacked'/name/('E15_C1_A2' if '_A2_' in name else 'E15_C1')
 rows=list(csv.DictReader((d/'MANIFEST_SHA256.csv').open()));bad=[]
 for r in rows:
  p=d/r['path']
  if not p.is_file() or len(p.read_bytes())!=int(r['bytes']) or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['path'])
 with zipfile.ZipFile(zpath) as z:crc=z.testzip()
 report=dict(archive=zpath.name,sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),crc_error=crc,manifest_count=len(rows),mismatches=bad)
 if d.name=='E15_C1':
  cps=json.loads((d/'checkpoint_manifest.json').read_text());report['checkpoint_count']=len(cps);report['checkpoint_mismatches']=[r['file'] for r in cps if hashlib.sha256((d/'checkpoints'/r['file']).read_bytes()).hexdigest()!=r['sha256']]
 reports.append(report)
(P/'input_integrity.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
assert all(not r['mismatches'] and r['crc_error'] is None and not r.get('checkpoint_mismatches',[]) for r in reports)
