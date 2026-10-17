from pathlib import Path
import json,csv,hashlib,datetime,zipfile
from run_map_postprocess import checkpoint_progress
P=Path(__file__).resolve().parent
checkpoint_progress()
a=json.loads((P/'final_audit.json').read_text());assert a['status']=='PASS'
with (P/'progress.md').open('a') as f:
 f.write('\n## Cierre confirmado\n\nT1-A PASS como mapa observacional:80/80, 0 pendientes;78 INJECTIVE_AT_NOMINAL_RADIUS,2 GEOMETRIC_NONINJECTIVITY,0 NUMERICAL_FAILURE,0 INCONCLUSIVE. True38/2; random40/0.\n\nÚltima tarea completamente terminada: auditoría final80 checkpoints,80 ZIP de estados persistidos y780 arrays finales PASS. Se corrigió únicamente selección de temporales del postprocesador en tres estados, sin cambiar tareas ni integrar otra vez. Ver postprocess_recovery.json y resultados anteriores retenidos.\n\nT1-B poblacional no abierto: sólo los dos positivos A2 conocidos. Serie específica propuesta; aún no ejecutada. C1-A permanece INCONCLUSIVE. C2 no abierto.\n\nNingún estado necesita recalcularse. Los scripts y resultados completos acompañan este cierre. Las asociaciones son descriptivas; censura en38 true y40 random al área nominal0.02. No existe certificado global de inyectividad.\n')
with (P/'failures.md').open('a') as f:
 f.write('\n## Incidencias resueltas de postprocesamiento\n\nTres INCONCLUSIVE operativos iniciales (split2/j0/true,split2/j2/true,split5/j2/true) se debieron a lectura de archivos .tmp.npz residuales. Los archivos finales estaban íntegros. Se corrigió la selección de archivos, con cero cambios en JSON/NPZ de tareas y cero reintegraciones; se conservaron result_before_postprocess_correction.json y los bytes temporales. Resultado final:ningún estado científicamente inconcluso o con fallo numérico.\n')
(P/'progress_080_confirmed.md').write_bytes((P/'progress.md').read_bytes())
# Explicit environment, no runtime secrets.
import numpy,scipy,torch,shapely,sklearn,matplotlib,platform
(P/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'shapely':shapely.__version__,'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__,'workers':4,'threads_per_worker':1},indent=2))
a['script_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.glob('*.py')}
(P/'final_audit.json').write_text(json.dumps(a,indent=2))
manifest=[]
for p in sorted(P.rglob('*')):
 if p.is_file() and p.name not in ['manifest.csv','persistence_receipts.json','summary_and_scripts.zip'] and '__pycache__'not in str(p):manifest.append(dict(path=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
with (P/'manifest.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(manifest)
with zipfile.ZipFile(P/'summary_and_scripts.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(P.iterdir()):
  if p.is_file() and p.name!='persistence_receipts.json' and (p.suffix!='.zip' or p.name=='common_sources.zip'):z.write(p,p.name)
print('Final progress ready',len(manifest),'manifest entries')
