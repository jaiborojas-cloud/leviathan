"""Bounded four-visit follow-up, original scientific one_visit, per-visit ZIP persistence."""
from pathlib import Path
import csv,json,hashlib,zipfile,time,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 from persist import persist
 import followup,run_followup as runner
 from atomic_csv import write_csv
 followup.gate()
 seal=json.loads((P/'baseline_seal_verification.json').read_text())
 for n,h in seal['files'].items():assert sha(P/n)==h,n
 for n,h in json.loads((P/'script_hashes.json').read_text()).items():assert sha(P/n)==h,n
 for r in csv.DictReader((P/'manifest.csv').open()):assert sha(P/r['path'])==r['sha256'],r['path']
 for z in P.glob('baseline_*.zip'):
  with zipfile.ZipFile(z)as a:assert a.testzip()is None
 cohort=list(csv.DictReader((P/'cohort_seeds.csv').open()));assert len(cohort)==800
 for row in cohort:
  d=P/'trajectories'/row['trajectory'];t=json.loads((d/'training_complete.json').read_text());assert sha(d/'checkpoint_005.pt')==t['checkpoint_sha256']
 records=json.loads((P.parent/'t2_receipts.json').read_text());saved={Path(r['local_path']).name for r in records if r['status']=='succeeded'}
 # Recover completed visits by persisting unchanged package; never rerun a completion marker.
 for f in (P/'future').glob('t*/states/*/visit_complete.json'):
  r=json.loads(f.read_text());name=f"visit_t{r['step']:03d}_{r['trajectory']}.zip"
  if name not in saved:persist([runner.package(r['trajectory'],r['step'])])
 pending=[]
 for step in range(25,251,25):
  pending=[r for r in cohort if not(P/'future'/f't{step:03d}'/'states'/r['trajectory']/'visit_complete.json').exists()]
  if pending:break
 target=pending[:4];assert target
 initial={'status':'INTEGRITY_PASS_BEFORE_FOLLOWUP','baselines':800,'seal_verified':True,'first_step':step,'targets':[r['trajectory']for r in target],'opened_before':len(list((P/'future').glob('t*/states/*/visit_complete.json')))}
 (P/'followup_session_initial.json').write_text(json.dumps(initial,indent=2))
 persist([P/'followup_bounded_verified.py',P/'followup_session_initial.json'])
 started=time.perf_counter();new=[]
 with ProcessPoolExecutor(max_workers=4)as pool:
  fs=[pool.submit(followup.one_visit,r,step)for r in target]
  for f in as_completed(fs):
   r=f.result();z=runner.package(r['trajectory'],step)
   with zipfile.ZipFile(z)as a:assert a.testzip()is None
   persist([z]);r['archive_sha256']=sha(z);new.append(r)
   with(P/'task_log.csv').open('a',newline='')as log:csv.writer(log).writerow([r['trajectory'],f'future_visit_t{step:03d}',r['status'],r['cpu_seconds'],r['wall_seconds'],sha(z)])
   persist([P/'task_log.csv']);print('VISIT_COMMITTED',r['trajectory'],step,r['classification'],flush=True)
 runner.aggregate()
 visits=list(csv.DictReader((P/'visits.csv').open()));outcomes=list(csv.DictReader((P/'outcomes.csv').open()))
 for r in visits:
  d=P/'future'/f"t{int(r['step']):03d}"/'states'/r['trajectory']
  if r.get('checkpoint_sha256'):assert sha(d/'checkpoint.pt')==r['checkpoint_sha256']
  if r.get('field_sha256'):assert sha(d/'state.npz')==r['field_sha256']
 for n,h in seal['files'].items():assert sha(P/n)==h,n
 todo=[(t,r['trajectory'])for t in range(25,251,25)for r in cohort if not(P/'future'/f't{t:03d}'/'states'/r['trajectory']/'visit_complete.json').exists()]
 partial=[str(d.relative_to(P))for d in (P/'future').glob('t*/states/*')if not(d/'visit_complete.json').exists()]
 summary=dict(status='FOLLOWUP_PAUSED_STUDY_INCOMPLETE',new_visits=len(new),visits=len(visits),planned_visits=8000,complete_trajectories=sum(r['status']=='COMPLETE'for r in outcomes),next_visit=todo[0]if todo else None,partial=partial,wall_seconds=time.perf_counter()-started,results=new,predictor_seal_unchanged=True)
 (P/'followup_session_f000_f004.json').write_text(json.dumps(summary,indent=2))
 with(P/'progress.md').open('a')as f:f.write('\nBasales:800/800, ZIP/checkpoints basales verificados:800. Sello basal intacto. ZIP de visitas nuevas verificados:'+str(len(new))+'.\nPróxima visita:'+str(summary['next_visit'])+'. Tareas parciales:'+str(partial)+'.\nSesión pausada entre lotes; no analizar resultados confirmatorios. Costes CPU/wall por visita y errores en followup_session_f000_f004.json y task_log.csv.\n')
 integrity=json.loads((P/'integrity_current.json').read_text());integrity.update(outcomes_opened=len(visits),future_visits_complete=len(visits),next_task=summary['next_visit'],partial_future=partial);(P/'integrity_current.json').write_text(json.dumps(integrity,indent=2))
 hashes=json.loads((P/'script_hashes.json').read_text());hashes['followup_bounded_verified.py']=sha(P/'followup_bounded_verified.py');(P/'script_hashes.json').write_text(json.dumps(hashes,indent=2))
 write_csv(P/'manifest.csv',[dict(path=x.name,bytes=x.stat().st_size,sha256=sha(x))for x in sorted(P.iterdir())if x.is_file()and x.name!='manifest.csv'],['path','bytes','sha256'])
 persist([P/n for n in ['outcomes.csv','visits.csv','followup_session_f000_f004.json','integrity_current.json','script_hashes.json','manifest.csv','progress.md']])
 print(json.dumps({k:v for k,v in summary.items()if k!='results'},indent=2),flush=True)
if __name__=='__main__':main()
