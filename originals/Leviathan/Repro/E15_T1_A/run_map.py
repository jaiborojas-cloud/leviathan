import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,time,hashlib,traceback,csv,zipfile,sys
import numpy as np
import audit
from audit import boundary,jacobi,rk,load
from geometry import area7,triangles
from persist import persist
P=Path(__file__).resolve().parent
original_save=audit.save
def atomic_save(p,d):
 t=p.with_suffix(p.suffix+'.tmp');original_save(t,d);t.replace(p)
audit.save=atomic_save
_original_np_save=np.savez_compressed
def atomic_np_save(file,*a,**kw):
 p=Path(file);t=p.with_suffix('.tmp.npz');_original_np_save(t,*a,**kw);t.replace(p)
np.savez_compressed=atomic_np_save

def read_tasks(d,sub):return [json.loads(p.read_text()) for p in sorted((d/sub).glob('*.json'))]
def taskset(case,fn,ns):
 for n in ns:
  for ph in [0,1]:fn(case,n,ph)
def result(case):
 d=P/'states'/case;final=d/'result.json'
 if final.exists():return json.loads(final.read_text())
 start=time.perf_counter();cpu=time.process_time();s,j,r=case.split('_');s=int(s[5:]);j=int(j[1:]);R=json.loads((d/'nominal.json').read_text())['radius'];reuse=(d/'reuse.json').exists()
 row=dict(state=case,split=s,init=j,regime=r,checkpoint=f'wine_split{s}_j{j}_{r}.pt',checkpoint_sha256=hashlib.sha256((d/'checkpoint.pt').read_bytes()).hexdigest(),nominal_radius=R,classification='INCONCLUSIVE',r_inj_lower=None,r_inj_upper=None,A_embed=None,A_embed_ratio=None,A_embed_censored=True,cut_locus_probable=False,reused_A2=reuse,notes='')
 try:
  assert json.loads((d/'reconstruction.json').read_text())['passed']
  if not reuse:
   taskset(case,boundary,[512,1024]);taskset(case,jacobi,[256,512])
  bs=read_tasks(d,'boundary');js=read_tasks(d,'jacobi')
  candidate=any('error' in t for t in bs+js) or any(t.get('first_intersection',{}).get('detected') for t in bs) or any(t.get('root_count',0)>0 or t.get('max_intrinsic_condition',0)>100 or abs(t.get('minimum_signed_determinant',1))<.05 for t in js)
  if candidate and not reuse:
   taskset(case,boundary,[2048,4096,8192]);taskset(case,jacobi,[1024]);taskset(case,rk,[128,256,512])
  bs=read_tasks(d,'boundary');js=read_tasks(d,'jacobi');rs=read_tasks(d,'rk4')
  if candidate and not reuse:
   latest=[b for b in bs if b['n']>=4096 and 'error' not in b];ons=[b['first_intersection']['upper'] for b in latest if b['first_intersection']['detected']];jroots=[x for x in js if x.get('root_count',0)]
   extreme=len(latest)<4 or (0<len(ons)<4) or (ons and max(ons)-min(ons)>1e-4*R) or (ons and not jroots)
   if extreme:taskset(case,boundary,[16384]);bs=read_tasks(d,'boundary')
  tasks=bs+js+rs;errors=[t['error'] for t in tasks if 'error' in t]
  for sub in ['boundary','jacobi','rk4']:
   for p in (d/sub).glob('*.npz'):
    with np.load(p) as a:
     for k in a.files:_=a[k]
  bvalid=[t for t in bs if 'error' not in t];jvalid=[t for t in js if 'error' not in t]
  events=[t for t in bvalid if t['first_intersection']['detected']];conj=[t['conjugate_minimum']['radius'] for t in jvalid if t.get('conjugate_minimum')];maxn=max(t['n'] for t in bvalid);fine=[t for t in bvalid if t['n']>=min(4096,maxn)];fineevents=[t for t in fine if t['first_intersection']['detected']]
  jfine=[t for t in jvalid if t['n']>=min(512,max(x['n'] for x in jvalid))];jfineconj=[t['conjugate_minimum']['radius'] for t in jfine if t.get('conjugate_minimum')]
  stableconj=len(jfineconj)==len(jfine) and bool(jfineconj) and max(jfineconj)-min(jfineconj)<=1e-4*R
  stableboundary=len(fineevents)==len(fine) and bool(fineevents) and max(t['first_intersection']['upper'] for t in fineevents)-min(t['first_intersection']['upper'] for t in fineevents)<=1e-4*R
  rkfine=[t for t in rs if t.get('steps',0)>=256 and 'error' not in t];rkpositive=bool(rkfine) and all(t['topology']['intersection_count']>0 for t in rkfine)
  dets=[]
  for p in (d/'jacobi').glob('*.npz'):
   with np.load(p) as z:dets.append(z['determinant'])
  row.update(first_self_intersection=min((t['first_intersection']['upper'] for t in events),default=None),self_intersections=max((t['topology']['intersection_count'] for t in fine),default=0),minimum_resolution_with_event=min((t['n'] for t in events),default=None),phase_persistence=stableboundary,determinant_sign_change=bool(conj),r_conj=min(conj) if conj else None,r_conj_min_estimate_range=(max(jfineconj)-min(jfineconj)) if jfineconj else None,max_Dexp_condition=max(t['max_intrinsic_condition'] for t in jvalid),min_abs_det_Dexp=min(float(abs(a).min()) for a in dets),min_signed_det_Dexp=min(float(a.min()) for a in dets),max_boundary_resolution=maxn,level=3 if maxn==16384 else 2 if candidate else 1,cut_locus_probable=bool(stableboundary and not conj),errors='; '.join(errors),metric_min_eigenvalue=min(t['audit']['min_eigenvalue'] for t in tasks if 'audit'in t),metric_nonpositive=sum(t.get('audit',{}).get('nonpositive',0) for t in tasks),metric_nonfinite=sum(t.get('audit',{}).get('nonfinite',0) for t in tasks))
  if errors or row['metric_nonpositive'] or row['metric_nonfinite']:row['notes']='Unresolved numerical exception/SPD failure; no replacement.'
  elif stableconj and (not events or (stableboundary and rkpositive)):
   row['classification']='GEOMETRIC_NONINJECTIVITY';row['r_inj_upper']=min(conj+[t['first_intersection']['upper'] for t in events]);row['A_embed_censored']=False
   if reuse:
    a2=P.parent/'unpacked/Leviathan_E15_C1_A2_codigo_resultados/E15_C1_A2/classifications.json';old=next(x for x in json.loads(a2.read_text())['states'] if x['case']==f'j{j}_{r}');row['A_embed']=old['A_embed_estimate_or_censored'];row['area_32_64_relative_difference']=old['A_embed_32_64_relative_difference']
   else:
    _,g,_=load(case);rad=row['r_inj_upper'];sol=g.rays(rad,8192);aa=[area7(g,triangles(sol.sol(np.linspace(0,rad,n+1)).T.reshape(n+1,2,8192,2)[:,0])) for n in [32,64]];row['A_embed']=aa[1];row['area_32_64_relative_difference']=abs(aa[1]/aa[0]-1);np.savez_compressed(d/'embedded_boundary.npz',radius=rad,boundary=sol.sol(rad).reshape(2,8192,2)[0]);atomic_save(d/'embedded_area.json',dict(radius=rad,area32=aa[0],area64=aa[1],note='Numerical initial-family estimate, cut locus earlier not excluded'))
   if row['area_32_64_relative_difference']>.005:row['classification']='INCONCLUSIVE';row['notes']='Area did not converge within frozen tolerance.'
   else:row['notes']='Stable conjugate zero/sign change; numerical r_inj upper only. A_embed estimate does not exclude an earlier cut locus.'
  elif not events and not conj and not candidate:
   row['classification']='INJECTIVE_AT_NOMINAL_RADIUS';row['A_embed']=json.loads((d/'nominal.json').read_text()).get('area_degree5',.02);row['notes']='No sampled loss up to nominal radius; observational right-censoring, no global injectivity certificate.'
  elif reuse and not events and not conj:
   row['classification']='INJECTIVE_AT_NOMINAL_RADIUS';row['A_embed']=.02;row['notes']='Verified A2 controls; no loss up to nominal under stronger tests. Observational censoring only.'
  elif not fineevents and not jfineconj and all(t.get('max_intrinsic_condition',0)<100 for t in jfine) and (events or conj):
   row['classification']='NUMERICAL_FAILURE';row['notes']='Coarse anomaly absent at refined resolutions/phases; discretization-dependent.'
  else:row['notes']='Persistent collision without resolved conjugate or unresolved conditioning/refinement. Cut locus requires independent minimization.'
  if row['A_embed'] is not None:row['A_embed_ratio']=row['A_embed']/.02
  row['task_cpu_seconds']=sum(t.get('cpu_seconds',0) for t in tasks);row['task_seconds_sum']=sum(t.get('seconds',0) for t in tasks)
 except Exception:
  row['notes']='Execution exception, no replacement';row['errors']=traceback.format_exc()
 row.update(new_wall_seconds=time.perf_counter()-start,new_cpu_seconds=time.process_time()-cpu)
 atomic_save(final,row);return row

def checkpoint_progress():
 rows=[json.loads(f.read_text()) for f in sorted((P/'states').glob('*/result.json'))];fields=sorted(set(k for r in rows for k in r))
 with (P/'state_results.csv.tmp').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 (P/'state_results.csv.tmp').replace(P/'state_results.csv')
 tasks=[]
 for d in sorted((P/'states').iterdir()):
  for sub in ['boundary','jacobi','rk4']:
   for p in sorted((d/sub).glob('*.json')):
    x=json.loads(p.read_text());tasks.append(dict(state=d.name,task=sub+'/'+p.name,status='INCONCLUSIVE' if 'error'in x else 'PASS',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),seconds=x.get('seconds'),cpu_seconds=x.get('cpu_seconds'),reused_A2=(d/'reuse.json').exists()))
 with (P/'task_log.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['state','task','status','sha256','seconds','cpu_seconds','reused_A2']);w.writeheader();w.writerows(tasks)
 done={r['state'] for r in rows};pending=[d.name for d in sorted((P/'states').iterdir()) if d.name not in done];counts={c:sum(r['classification']==c for r in rows) for c in ['INJECTIVE_AT_NOMINAL_RADIUS','GEOMETRIC_NONINJECTIVITY','NUMERICAL_FAILURE','INCONCLUSIVE']}
 (P/'progress.md').write_text('# E15-T1-A — progreso recuperable\n\nCompletados: '+str(len(rows))+'/80. Pendientes: '+str(len(pending))+'.\n\nC1-A permanece INCONCLUSIVE. Clasificaciones T1-A: '+json.dumps(counts)+'.\n\nIntegridad: C1 1925/1925; checkpoints80/80; A2 581/581; CRC ambos PASS. Reconstrucción M/f80/80 PASS. SHA ZIP en input_integrity.json.\n\nProtocolo: protocol_T1_A_frozen.json SHA256 '+hashlib.sha256((P/'protocol_T1_A_frozen.json').read_bytes()).hexdigest()+'. P0=(0,0), rho=1e-4, área0.02, radios C1 intactos, DOP853 rtol2e-10 atol2e-12. Compuertas y presupuestos congelados antes del nuevo screening.\n\nÚltima tarea completamente terminada: '+(rows[-1]['state'] if rows else 'reconstrucción80/80')+'.\n\nReanudar: materializar estos archivos y ZIP por estado en la misma carpeta; extraer cada ZIP para obtener states/<id>. Recuperar fuentes de los ZIP C1/A2 verificados, ejecutar setup.py sólo si faltan insumos y reconstruct.py si faltan comprobaciones. Ejecutar python3 run_map.py; los result.json válidos se omiten. No regenerar un resultado confirmado. Los pendientes no cuentan como INCONCLUSIVE completado. Las identidades/versiones se conservan en persistence_receipts.json local; si nueva sesión, recuperar identidades actuales por búsqueda antes de guardar.\n\nPendientes:\n'+', '.join(pending)+'\n\nCompletados:\n'+', '.join(sorted(done))+'\n\nPASS de integridad y reconstrucción; FAIL de estas compuertas:0. Compuerta poblacional: '+('PENDIENTE' if pending else '80 clasificados; revisar cierre y persistencia final')+'.\n')
 failures=[r for r in rows if r['classification']in ['INCONCLUSIVE','NUMERICAL_FAILURE']]
 (P/'failures.md').write_text('# Incidencias y estados no resueltos\n\nRecuperación: copia local ZIP A2 y un NPZ local incompletos tras interrupción; restaurados de archivos con SHA verificado, sin regenerar resultados. Dependencias originales restauradas.\n\n'+('\n\n'.join(r['state']+': '+r['notes']+'\n'+r.get('errors','') for r in failures) if failures else 'Ningún fallo numérico entre estados completados.')+'\n')
 manifest=[]
 for p in sorted(P.rglob('*')):
  if p.is_file() and p.name not in ['manifest.csv','persistence_receipts.json'] and '__pycache__' not in str(p) and not p.name.endswith('.tmp'):
   manifest.append(dict(path=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 with (P/'manifest.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(manifest)
 return rows

def main():
 from concurrent.futures import ProcessPoolExecutor
 assert hashlib.sha256((P/'protocol_T1_A_frozen.json').read_bytes()).hexdigest()==(P/'protocol_T1_A_frozen.sha256').read_text()
 cases=[d.name for d in sorted((P/'states').iterdir()) if not(d/'result.json').exists()]
 # Commit only whole states; at most four states between persistence barriers.
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i in range(0,len(cases),4):
   batch=cases[i:i+4];rows=list(pool.map(result,batch))
   for r in rows:print(r['state'],r['classification'],r.get('r_conj'),r.get('errors',''),flush=True)
   archives=[]
   for name in batch:
    path=P/(name+'.zip');tmp=path.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
     for f in sorted((P/'states'/name).rglob('*')):
      if f.is_file():z.write(f,str(f.relative_to(P)))
    tmp.replace(path);archives.append(path)
   persist(archives);allrows=checkpoint_progress();persist([P/n for n in ['state_results.csv','task_log.csv','failures.md','manifest.csv','progress.md']]);print('COMMITTED',len(allrows),'/80',flush=True)
if __name__=='__main__':main()
