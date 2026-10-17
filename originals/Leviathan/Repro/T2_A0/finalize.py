from pathlib import Path
import json,hashlib,csv,zipfile,shutil
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((P/'design_validation.json').read_text())['status']=='PASS'
(P/'protocol.sha256').write_text(sha(P/'protocol.json')+'  protocol.json\n')
(P/'progress.md').write_text('# T2-A0 completo\n\nProtocolo temporal único congelado;800 candidatos naturales true; t0=5; horizonte250; q=.10.\n\nSe completaron integridad de insumos, sensibilidad binomial y por bloques, scripts de análisis y pruebas sintéticas. Estados neuronales nuevos:0. T2-A NO iniciado. C1-A INCONCLUSIVE intacto.\n\nÚltimo paso válido: congelación de diseño y validación de lógica. Scripts y fuentes en manifest.csv; criterios en protocol.json y preregistro. Próxima ejecución requiere recuperar/verificar este paquete y realizar el replay técnico del adaptador longitudinal antes de nuevos estados. No hay continuación automática.\n')
(P/'script_hashes.json').write_text(json.dumps({f.name:sha(f) for f in sorted(P.glob('*.py'))},indent=2))
exclude={'manifest.csv','T2_A0_preregistro_repro.zip','T2_A0_preregistro_repro.zip.sha256'}
files=[f for f in sorted(P.iterdir()) if f.is_file() and f.name not in exclude]
with (P/'manifest.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(dict(path=x.name,bytes=x.stat().st_size,sha256=sha(x)) for x in files)
with zipfile.ZipFile(P/'T2_A0_preregistro_repro.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files+[P/'manifest.csv']:z.write(f,f.name)
(P/'T2_A0_preregistro_repro.zip.sha256').write_text(sha(P/'T2_A0_preregistro_repro.zip')+'  T2_A0_preregistro_repro.zip\n')
with zipfile.ZipFile(P/'T2_A0_preregistro_repro.zip') as z:
 assert z.testzip() is None
 for r in csv.DictReader((P/'manifest.csv').open()):assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
shutil.copyfile(P/'Leviathan_RIPG_T2-A0_preregistro.md',P.parent/'Leviathan_RIPG_T2-A0_preregistro.md')
print('MANIFEST',len(files),'PROTOCOL_SHA',sha(P/'protocol.json'),'PACKAGE_SHA',sha(P/'T2_A0_preregistro_repro.zip'))
