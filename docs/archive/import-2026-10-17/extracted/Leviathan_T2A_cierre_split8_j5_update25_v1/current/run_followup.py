from pathlib import Path
import csv,json,zipfile,hashlib
from concurrent.futures import ProcessPoolExecutor,as_completed
from followup import one_visit,gate
from run_baseline_cohort import atomic_zip
from persist import persist
P=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()

def package(case,step):
 d=P/'future'/f't{step:03d}'/'states'/case;z=P/f'visit_t{step:03d}_{case}.zip'
 atomic_zip(z,[f for f in sorted(d.rglob('*')) if f.is_file() and '.tmp' not in f.name]);return z

def aggregate():
 cohort=list(csv.DictReader((P/'cohort_seeds.csv').open()));outcomes=[];visits=[]
 for row in cohort:
  case=row['trajectory'];rr=[]
  for step in range(25,251,25):
   f=P/'future'/f't{step:03d}'/'states'/case/'visit_complete.json'
   if f.exists():rr.append(json.loads(f.read_text()))
  positive=[r['step'] for r in rr if r['classification']=='GEOMETRIC_NONINJECTIVITY'];unknown=[r for r in rr if r['classification']not in ['INJECTIVE_AT_NOMINAL_RADIUS','GEOMETRIC_NONINJECTIVITY']]
  Y=1 if positive else 0 if len(rr)==10 and not unknown else None
  outcomes.append(dict(trajectory=case,split=row['split'],init=row['init_index'],Y=Y,first_event_step=min(positive) if positive else None,visits_complete=len(rr),unknown_visits=len(unknown),status='COMPLETE' if len(rr)==10 and not unknown else 'INCONCLUSIVE' if unknown else 'PENDING'))
  visits+=rr
 for name,rr in [('outcomes.csv',outcomes),('visits.csv',visits)]:
  fields=sorted({k for r in rr for k in r}) if rr else ['trajectory','step','classification']
  with (P/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
 done=sum(r['status']=='COMPLETE' for r in outcomes);unknown=sum(r['unknown_visits'] for r in outcomes);positives=sum(r['Y']==1 for r in outcomes)
 (P/'progress.md').write_text(f'# T2-A — seguimiento en curso; sin cierre\n\nPredictor basal global cerrado y persistido; ver predictor_lock_persisted.json. Trayectorias completas:{done}/800. Visitas evaluadas:{len(visits)}/8000. Pendientes de visitas:{8000-len(visits)}. Visitas desconocidas:{unknown}. Trayectorias con evento detectado:{positives}. No son aún estimaciones confirmatorias.\n\nÚltima visita válida:'+ (f'{visits[-1]["trajectory"]}/t{visits[-1]["step"]}' if visits else 'lock basal')+'.\n\nReanudar run_followup.py: omite visit_complete.json y conserva checkpoint, Adam,RNG. Comprobar todos los hashes y recibos; guardar cualquier ZIP terminado sin recibo antes de avanzar. No reemplazar errores; nunca convertir pendientes o desconocidos enY0. No analizar confirmación antes de8000 visitas y auditoría final.\n')
 with (P/'manifest.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader()
  for x in sorted(P.iterdir()):
   if x.is_file() and x.name!='manifest.csv':w.writerow(dict(path=x.name,bytes=x.stat().st_size,sha256=sha(x)))
 return outcomes

def main():
 gate();rows=list(csv.DictReader((P/'cohort_seeds.csv').open()))
 records=json.loads((P.parent/'t2_receipts.json').read_text());saved={Path(r['local_path']).name for r in records if r['status']=='succeeded'}
 for step in range(25,251,25):
  for r in rows:
   case=r['trajectory']
   if(P/'future'/f't{step:03d}'/'states'/case/'visit_complete.json').exists() and f'visit_t{step:03d}_{case}.zip'not in saved:persist([package(case,step)])
  pending=[r for r in rows if not(P/'future'/f't{step:03d}'/'states'/r['trajectory']/'visit_complete.json').exists()]
  with ProcessPoolExecutor(max_workers=4) as pool:
   for i in range(0,len(pending),4):
    if(P/'PAUSE_AFTER_BATCH').exists():return
    fs=[pool.submit(one_visit,r,step)for r in pending[i:i+4]]
    for f in as_completed(fs):
     r=f.result();persist([package(r['trajectory'],step)]);print('VISIT_COMMITTED',r['trajectory'],step,r['classification'],flush=True)
    aggregate();persist([P/n for n in ['outcomes.csv','visits.csv','manifest.csv','progress.md']])
 print('FOLLOWUP_COMPLETE_AUDIT_REQUIRED',flush=True)
if __name__=='__main__':main()
