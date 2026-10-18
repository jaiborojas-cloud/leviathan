from pathlib import Path
import csv,json,hashlib,zipfile,os
P=Path('/workspace/scratch/54de7a7b7cce/current/Leviathan/Repro/T2_A');W=Path('/workspace/scratch/54de7a7b7cce/incident_work')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
report=json.loads((P/'incident_split8_j5_update25_v1_verification.json').read_text())
pc=next(x for x in report['archives'] if x['file']=='RIPG_RESULTADOS_PC.zip')
partials=json.loads((P/'followup_partial_snapshot.json').read_text())['partial']
ode=json.loads((P/'ode_resume_index.json').read_text())
doc='Leviathan_T2A_cierre_split8_j5_update25_v1.md'
incident={'schema_version':1,'incident_id':report['incident_id'],'version':1,'date':'2026-10-16','trajectory':'split8_j5_true','step':25,'documentary_closed':True,'status':'INCONCLUSIVE','scientific_resolution':'UNRESOLVED','visit_complete':False,'topological_classification':None,'Y':None,'nominal_radius':None,'A_embed':None,'primary_technical_gate':'INCONCLUSIVE_WHILE_UNRESOLVED','reason':'Possible domain termination before nominal area; no certified nominal disk or frozen topological classification','protocol_changed':False,'retained_in_cohort':True,'predictors_sealed_unchanged':True,'float64_historical_snapshot':ode['latest'],'mpfr_replay':pc['index'],'mpfr_next_accounting_step':140,'mpfr_continue_to_009':False,'recovery':{'root':'/Leviathan/Repro/T2_A','pc_return':'/RIPG_RESULTADOS_PC.zip','pc_return_sha256':pc['sha256'],'base_archive':'origin_mpfr_step_000090.zip','base_sha256':pc['index']['base_sha256'],'base_payload_reverified_this_session':False,'diagnostic_archives':[x for x in report['archives'] if x['file']!='RIPG_RESULTADOS_PC.zip'],'partial_snapshot':partials[0]},'continuation':{'order':'update ascending, then frozen cohort order','first_unresolved_visit':'split8_j5_true/update25','held_visits':['split8_j5_true/update25'],'next_executable_visit':'split8_j7_true/update25','then':['split8_j8_true/update25','split8_j9_true/update25'],'next_partial_snapshot':partials[1],'execution_this_session':False,'launcher_requirement':'Explicit selection respecting hold; do not run legacy generic dispatcher or fabricate visit_complete.json','recovery_of_j7_geometry':'Use latest verified persisted geometry if any; no geometric step inferred from checkpoint-only snapshot'},'table_policy':{'visits.csv':'UNCHANGED: completed-marker records only','outcomes.csv':'UNCHANGED: Y blank, status PENDING; unknown_visits counts unresolved completed-marker records only','cohort_manifest.csv':'UNCHANGED: basal snapshot retained; follow-up status fields stale; consult visit and incident records'},'document':doc,'document_sha256':sha(P/doc),'verification':'incident_split8_j5_update25_v1_verification.json','verification_sha256':sha(P/'incident_split8_j5_update25_v1_verification.json')}
jname='incident_split8_j5_update25_v1.json';(P/jname).write_text(json.dumps(incident,indent=2,ensure_ascii=False)+'\n')
fields=['incident_id','version','date','trajectory','step','documentary_status','scientific_status','topological_classification','Y','visit_complete','technical_gate','next_executable_visit','record','sha256']
with (P/'incident_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(dict(incident_id=incident['incident_id'],version=1,date=incident['date'],trajectory=incident['trajectory'],step=25,documentary_status='CLOSED_DOCUMENTARY',scientific_status='INCONCLUSIVE',topological_classification='',Y='',visit_complete='false',technical_gate='INCONCLUSIVE_WHILE_UNRESOLVED',next_executable_visit='split8_j7_true/update25',record=jname,sha256=sha(P/jname)))
prefix='''# Cierre documental v1 — 2026-10-16 (estado vigente)

Punto1 del roadmap completado DOCUMENTALMENTE. split8_j5_true/update25 permanece no resuelto, pendiente/INCONCLUSIVE técnico; clasificación topológica y Y desconocidos. Ver Leviathan_T2A_cierre_split8_j5_update25_v1.md, incident_split8_j5_update25_v1.json e incident_register.csv. No se creó visit_complete.json ni se asignó outcome.

800/800 basales; sello verificado e intacto. 1/8000 visitas cerradas (split8_j6_true/update25); 0/800 horizontes completos. visits.csv y outcomes.csv intactos: los 800 Y vacíos. unknown_visits heredado cuenta desconocidos en marcadores completados, no todas las visitas pendientes; consultar también incidencias abiertas. cohort_manifest.csv conserva su estado basal histórico.

j5: float64 histórico512 intacto; replay PC PAUSED139, r=.07447265825972331. Paso contable140 NO ejecutado, no continuar hacia.09. La frontera y área diagnósticas no son GEOMETRIC_NONINJECTIVITY ni A_embed. La compuerta técnica permanece INCONCLUSIVE mientras falte resolver la auditoría.

Primera pendiente absoluta: split8_j5_true/update25, retenida. Próxima tarea EJECUTABLE de cohorte: split8_j7_true/update25; luego j8 y j9/update25. Recuperar parciales y verificar hashes sin reentrenar ni repetir j6. El lanzador genérico heredado ignora incidencias: antes de ejecutarlo se requiere selección explícita respetando esta pausa; no fabricar marcadores ni borrar j5. Plan exacto y hashes en el cierre v1. Ninguna visita nueva abierta o calculada en esta sesión.

Integridad de esta sesión:21 entradas consultadas del manifiesto y6 archivos del sello coinciden;17 hashes del retorno PC,13 segmentos contiguos91–139 con CRC válido,31 hashes internos de diagnósticos. Alcance y limitaciones en incident_split8_j5_update25_v1_verification.json. No se repitió la auditoría de800 ZIP ni se reconstruyeron estados numéricos.

Lo siguiente se conserva como historial. Las instrucciones previas de cierre aún pendiente o reanudación automática quedan superadas por este encabezado.

---
'''
(P/'progress.md').write_bytes(prefix.encode()+ (W/'before/progress.md').read_bytes())
with (P/'task_log.csv').open('a',newline='') as f:csv.writer(f).writerow([incident['trajectory'],'DOCUMENTARY_CLOSURE_UPDATE025_DOMAIN_V1','INCONCLUSIVE','','',sha(P/jname)])
road=(W/'before/Leviathan_RIPG_roadmap.md').read_text()
road=road.replace('1. **Próxima tarea: cierre documental del caso no resuelto.**','1. **COMPLETADO DOCUMENTALMENTE (v1,2026-10-16): cierre del caso no resuelto.**').replace('Este roadmap no ejecuta dicho cierre.','Cierre ejecutado en Leviathan_T2A_cierre_split8_j5_update25_v1.md y registrado en incident_register.csv; resolución científica pendiente.').replace('Una vez documentado el caso, identificar la siguiente tarea pendiente mediante manifests.','Caso documentado: primera pendiente absoluta j5/update25 retenida; siguiente ejecutable split8_j7_true/update25, después j8 y j9. Recuperar parciales y respetar la pausa mediante selección explícita; el lanzador genérico heredado no consulta incidencias.')
(P/'Leviathan_RIPG_roadmap.md').write_text(road)
# Build immutable documentary recovery package with pre-edit bytes and current evidence.
zname='Leviathan_T2A_cierre_split8_j5_update25_v1.zip'
pack={}
for f in (W/'before').iterdir():pack['before/'+f.name]=f.read_bytes()
names=[doc,jname,'incident_register.csv','incident_split8_j5_update25_v1_verification.json','progress.md','task_log.csv','Leviathan_RIPG_roadmap.md','protocol.json','Leviathan_RIPG_T2-A0_preregistro.md','visits.csv','outcomes.csv','cohort_manifest.csv','baseline_seal_verification.json','baseline_cutoff_frozen.json','predictors_locked.csv','predictor_lock.json','predictor_lock_persisted.json','seal_baseline_verified.py','ode_resume_index.json','followup_partial_snapshot.json','run_followup.py','followup_bounded_verified.py']
for n in names:pack['current/'+n]=(P/n).read_bytes()
for f in (W/'evidence').iterdir():pack['evidence/'+f.name]=f.read_bytes()
for f in P.glob('*139.zip'):pack['evidence/'+f.name]=f.read_bytes()
for n in ['reconcile.py','close_documentary.py']:pack['documentary_scripts/'+n]=(W/n).read_bytes()
pack['CONTENTS_SHA256.json']=(json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in pack.items()},indent=2)+'\n').encode()
with zipfile.ZipFile(P/zname,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in pack.items():z.writestr(n,b)
with zipfile.ZipFile(P/zname) as z:
 assert z.testzip() is None
 for n,h in json.loads(z.read('CONTENTS_SHA256.json')).items():assert hashlib.sha256(z.read(n)).hexdigest()==h
# Preserve every unrelated manifest row; update changed rows and add only deliverables/evidence gap.
rows=list(csv.DictReader((W/'before/manifest.csv').open()));idx={r['path']:r for r in rows}
changed=[doc,jname,'incident_register.csv','incident_split8_j5_update25_v1_verification.json','progress.md','task_log.csv','Leviathan_RIPG_roadmap.md',zname,'Leviathan_T2A_frontera_paso139.zip']
for n in changed:
 r=dict(path=n,bytes=str((P/n).stat().st_size),sha256=sha(P/n))
 if n in idx:idx[n].update(r)
 else:rows.append(r)
with (P/'manifest.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(rows)
for n in ['visits.csv','outcomes.csv','cohort_manifest.csv']:assert (P/n).read_bytes()==(W/'before'/n).read_bytes()
assert (P/'task_log.csv').read_bytes().startswith((W/'before/task_log.csv').read_bytes())
for n,h in json.loads((P/'baseline_seal_verification.json').read_text())['files'].items():assert sha(P/n)==h
for r in rows:
 f=P/r['path']
 if f.exists():assert sha(f)==r['sha256'] and f.stat().st_size==int(r['bytes']),r['path']
summary={'status':'PASS_DOCUMENTARY_ONLY','zip':zname,'zip_sha256':sha(P/zname),'manifest_sha256':sha(P/'manifest.csv'),'manifest_rows_before':len(idx),'manifest_rows_after':len(rows),'modified':['progress.md','task_log.csv','manifest.csv','Leviathan_RIPG_roadmap.md'],'created':[doc,jname,'incident_register.csv','incident_split8_j5_update25_v1_verification.json',zname],'unchanged':['visits.csv','outcomes.csv','cohort_manifest.csv','protocol.json','predictors_locked.csv'],'next_executable_visit':'split8_j7_true/update25'}
(W/'final_local_verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
# Ordered persistence; the audit was saved incrementally already.
new=[doc,jname,'incident_register.csv',zname];replaced=['Leviathan_RIPG_roadmap.md','task_log.csv','progress.md','manifest.csv'];uploads=[]
for n in new:uploads.append(dict(local_path=str(P/n),purpose='create_library_file',directory_id='6abbf2fa64188191b72ecce030a09e9a',library_artifact_type='report' if n.endswith('.md') else 'other'))
for n in replaced:
 f=P/n;uploads.append(dict(local_path=str(f),purpose='replace_library_file',library_file_id=os.getxattr(f,'user.library-file-id').decode(),expected_current_version=int(os.getxattr(f,'user.library-file-version')),version_reason='Cierre documental v1 j5/update25 INCONCLUSIVE, sin outcome; historial conservado'))
(W/'upload_closure.json').write_text(json.dumps({'uploads':uploads},indent=2))
