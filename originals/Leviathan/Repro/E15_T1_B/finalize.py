from pathlib import Path
import json,csv,hashlib,zipfile,datetime,platform
from run_common import progress
P=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
progress();audit=json.loads((P/'final_audit.json').read_text());assert audit['status']=='PASS'
with (P/'progress.md').open('a') as f:
 f.write('\n## Cierre confirmado\n\nT1-B completo:80/80 estados,320/320 combinaciones PASS,0 pendientes,0 errores numéricos. Último paso completamente válido: análisis, figuras y auditoría de80 checkpoints/paquetes.\n\nRadio principal0.05697156262709151;rho true nominal0.9717693401903927 y común0.9549184812342706,delta−0.01685085895612215. Positivos j1/j3 ocupan rangos1/2 en r3,pero j3 rangos15/8 en r1/r2. Residuos grandes:7/38 true y1/40 random; no explicación fuerte por anisotropía de borde; no mejora de adimensionales ensayados.\n\nT2: sólo diseño congelado de transportabilidad predictiva,NO EJECUTADO. C1-A INCONCLUSIVE y clases T1-A intactos. Ver cierre y diseño T2.\n\nUna salvedad histórica de manifest T1-A y un conflicto de versión resuelto se documentan en input_integrity.json y persistence_recovery.json. No implicaron sustituciones ni reintegraciones.\n')
(P/'progress_080_confirmed.md').write_bytes((P/'progress.md').read_bytes())
import numpy,scipy,shapely,sklearn,matplotlib
(P/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__,'shapely':shapely.__version__,'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__,'workers':4,'torch':'not needed for immutable saved M/f; checkpoints SHA verified, no new training'},indent=2))
audit['script_sha256']={f.name:sha(f) for f in P.glob('*.py')};(P/'final_audit.json').write_text(json.dumps(audit,indent=2))
manifest=[]
for f in sorted(P.rglob('*')):
 if f.is_file() and f.name not in ['manifest.csv','persistence_receipts.json','summary_and_scripts.zip','summary_and_scripts.zip.sha256'] and '__pycache__'not in str(f):manifest.append(dict(path=str(f.relative_to(P)),bytes=f.stat().st_size,sha256=sha(f)))
with (P/'manifest.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(manifest)
with zipfile.ZipFile(P/'summary_and_scripts.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(P.iterdir()):
  if f.is_file() and f.suffix!='.zip' and f.name not in ['persistence_receipts.json','summary_and_scripts.zip.sha256']:z.write(f,f.name)
(P/'summary_and_scripts.zip.sha256').write_text(sha(P/'summary_and_scripts.zip')+'  summary_and_scripts.zip\n')
print('FINAL MANIFEST',len(manifest))
