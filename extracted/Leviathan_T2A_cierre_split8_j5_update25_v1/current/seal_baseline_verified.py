"""Operational seal audit; uses unchanged lock_predictors and primary_analysis.tail. No future execution."""
from pathlib import Path
import csv,json,hashlib,math,datetime,os
from persist import persist
import lock_predictors
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
 p=P/name;t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');os.replace(t,p)
def main():
 assert not(P/'predictor_lock.json').exists(),'Existing seal: inspect and reconcile, do not overwrite'
 initial=json.loads((P/'initial_b800_20261014.json').read_text());assert initial['completed']==800
 protocol=json.loads((P/'protocol.json').read_text());assert sha(P/'protocol.json')==lock_predictors.sha(P/'protocol.json')=='7ce3ec683a392ec3de0a5e8a983ea112684912026d427a5cd4f98fb7003d1f95'
 for n,h in json.loads((P/'script_hashes.json').read_text()).items():assert sha(P/n)==h,n
 assert not list((P/'future').rglob('checkpoint*.pt'))
 rows=list(csv.DictReader((P/'predictors_staging.csv').open()));cohort=list(csv.DictReader((P/'cohort_seeds.csv').open()))
 assert len(rows)==800 and [r['trajectory']for r in rows]==[r['trajectory']for r in cohort]
 for r in rows:
  b=json.loads((P/'trajectories'/r['trajectory']/'baseline_result.json').read_text())
  assert b['future_opened'] is False
  assert r['eligible']==str(b['eligible']) and r['baseline_classification']==b['baseline_classification']
  assert r['predictor_status']==b['predictor']['status'] and r['comparator_status']==b['comparator_status']
  for k,v in [('X',b['predictor']['X']),('C_A',b['comparators']['C_A']),('Lambda_01pct',b['comparators']['lambda_01pct']),('R_eff',b['comparators']['R_eff'])]:assert float(r[k])==v and math.isfinite(v)
  assert b['predictor']['radius']==protocol['predictor']['r_star']
  assert r['predictor_status']==r['comparator_status']=='PASS' and all(b['predictor']['gates'].values())
  assert b['baseline_classification']=='INJECTIVE_AT_NOMINAL_RADIUS' and b['eligible'] is True
 eligible=[r for r in rows if r['eligible']=='True'];n=len(eligible);k=math.ceil(protocol['tail']['q']*n);cutoff=sorted(float(r['X'])for r in eligible)[-k]
 selected=[r['trajectory']for r in eligible if float(r['X'])>=cutoff]
 splits=len(set(r['split']for r in eligible));assert n>=640 and splits>=128 and len(selected)<=.15*n
 frozen=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol_sha256=sha(P/'protocol.json'),staging_sha256=sha(P/'predictors_staging.csv'),candidates=800,eligible=n,eligible_splits=splits,q=.1,nominal_tail_n=k,cutoff_X=cutoff,cutoff_hex=cutoff.hex(),comparison='X >= cutoff; all exact float64 ties included',actual_tail_n=len(selected),tail_fraction=len(selected)/n,selected_trajectories=selected,eligible_trajectories=[r['trajectory']for r in eligible],excluded_trajectories=[],technical_baseline_gate='PASS',future_states_opened=0,predictive_hypothesis_status='NOT_EVALUATED')
 save('baseline_cutoff_frozen.json',frozen)
 persist([P/x for x in ['initial_b800_20261014.json','restoration_b800_original_manifest.csv','restore_b800.py','seal_baseline_verified.py','baseline_cutoff_frozen.json']])
 lock_predictors.main()
 locked=list(csv.DictReader((P/'predictors_locked.csv').open()));assert len(locked)==800
 assert [r['trajectory']for r in locked if r['in_tail_X']=='True']==selected
 for before,after in zip(rows,locked):
  for key in before:
   if key!='locked':assert before[key]==after[key],(before['trajectory'],key)
  assert after['locked']=='True'
 assert (P/'predictor_lock.json').read_bytes()==(P/'predictor_lock_persisted.json').read_bytes()
 seal=dict(status='BASELINE_PREDICTORS_SEALED',candidates=800,eligible=n,eligible_splits=splits,tail_n=len(selected),cutoff_X=cutoff,future_states_opened=0,baseline_zips_verified=800,checkpoints_verified=800,scientific_recalculation=False,files={x:sha(P/x)for x in ['protocol.json','predictors_locked.csv','baseline_cutoff_frozen.json','predictor_lock.json','predictor_lock_persisted.json','seal_baseline_verified.py']})
 save('baseline_seal_verification.json',seal)
 report=f'''# T2-A — cierre de fase basal y sellado de predictores\n\n800/800 auditorías basales completas; 800 ZIP y checkpoints verificados.\nElegibles: {n}, repartidos en {splits} splits. Exclusiones: 0. Compuertas basales y comparadores: PASS.\n\nPredictor primario: κ máximo intrínseco de Dexp en r*=0.05697156262709151, update5. Cola superior congelada: q=10%, {len(selected)} trayectorias. Corte X≥{cutoff!r}; todos los empates exactos incluidos. Comparadores del mismo update5 conservados sin cambios.\n\nTabla, elegibilidad, corte y marcadores de sellado persistidos con SHA-256. Ver baseline_seal_verification.json. Ningún estado futuro ejecutado o abierto. Esto no constituye evidencia predictiva ni PASS de la hipótesis temporal.\n\nSiguiente paso: seguimiento en orden de cohorte, visitas 25,50,…,250, conservando modelo, Adam y RNG. Antes de ejecutar, verificar los hashes del sello y sus recibos; no recalcular basales ni llamar a agregadores basales que sobrescriban este progreso. No detener trayectorias por puntuación, precisión o evento. No tratar visitas pendientes como negativas.\n'''
 (P/'baseline_seal_report.md').write_text(report)
 (P/'progress.md').write_text('# T2-A — basales completas; predictores globales sellados\n\n'+report.split('\n\n',1)[1]+'\nÚltima auditoría basal: split167_j804_true. Pendientes basales: 0. Tareas parciales: ninguna.\nSeguimiento: 0/8000 visitas, 0/800 trayectorias completas; outcomes NO EVALUADOS. Próxima tarea: split8_j5_true / update25.\nProtocolo SHA-256: '+sha(P/'protocol.json')+'\n')
 integrity=json.loads((P/'integrity_current.json').read_text());integrity.update(predictors_globally_locked=True,outcomes_opened=0,next_task='split8_j5_true/update25',baseline_seal_sha256=sha(P/'baseline_seal_verification.json'));save('integrity_current.json',integrity)
 with(P/'task_log.csv').open('a',newline='')as f:csv.writer(f).writerow(['GLOBAL','seal_baseline_predictors','PASS','','',sha(P/'baseline_seal_verification.json')])
 hashes=json.loads((P/'script_hashes.json').read_text());hashes.update({x:sha(P/x)for x in ['restore_b800.py','seal_baseline_verified.py']});save('script_hashes.json',hashes)
 with(P/'manifest.csv').open('w',newline='')as f:
  w=csv.writer(f);w.writerow(['path','sha256','bytes'])
  for x in sorted(P.iterdir()):
   if x.is_file() and x.name!='manifest.csv':w.writerow([x.name,sha(x),x.stat().st_size])
 persist([P/x for x in ['baseline_seal_verification.json','baseline_seal_report.md','integrity_current.json','task_log.csv','script_hashes.json','manifest.csv','progress.md']])
 print(json.dumps(seal,indent=2),flush=True)
if __name__=='__main__':main()
