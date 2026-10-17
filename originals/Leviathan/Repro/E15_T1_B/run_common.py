import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,csv,time,hashlib,traceback,zipfile,tempfile,shutil
import numpy as np
from audit import AuditedGeometry,jacsolve,topology,save as json_save
from persist import persist
P=Path(__file__).resolve().parent;A=Path(json.loads((P/'source_locations.json').read_text())['T1A']);PROTO=json.loads((P/'protocol_T1_B_frozen.json').read_text());RAD=np.array(PROTO['radii'])
OLD={r['state']:r for r in csv.DictReader((P/'T1A_linked_geometry.csv').open())}
def save(path,data):
 with tempfile.NamedTemporaryFile(dir='/tmp',suffix='.json',delete=False) as f:tmp=Path(f.name)
 try:json_save(tmp,data);os.replace(tmp,path)
 finally:
  if tmp.exists():tmp.unlink()
def npzsave(path,**data):
 with tempfile.NamedTemporaryFile(dir='/tmp',suffix='.npz',delete=False) as f:tmp=Path(f.name)
 try:np.savez_compressed(tmp,**data);os.replace(tmp,path)
 finally:
  if tmp.exists():tmp.unlink()
def kappa(det):return np.maximum(1,np.abs(det))/np.minimum(1,np.abs(det))
def task(case,n,phase):
 d=P/'states'/case;dest=d/f'jacobi_n{n}_phase{phase}.json'
 if dest.exists():
  r=json.loads(dest.read_text())
  if 'error'not in r:
   with np.load(dest.with_suffix('.npz')) as z:
    for key in z.files:_=z[key]
  return r
 t=time.perf_counter();cpu=time.process_time();z=np.load(d/'state.npz');g=AuditedGeometry(z['M'],z['f']);theta=(np.arange(n)+phase/2)*2*np.pi/n
 try:
  sol=jacsolve(g,theta,float(RAD[-1]));end=sol.sol(RAD).reshape(6,n,4);det=end[4].T/RAD[:,None];kap=kappa(det);points=end[:2].transpose(2,1,0);Ks=[]
  for pts in points:Ks.append(g.eval(pts)[1])
  tt=np.linspace(0,RAD[-1],513)[1:];dd=sol.sol(tt).reshape(6,n,-1)[4]/tt[None,:];kk=kappa(dd)
  ppmax=[];ppsign=[];ppabs=[]
  for i,r in enumerate(RAD):
   sel=tt<=r;ppmax.append(max(float(kk[:,sel].max()),float(kap[i].max())));ppsign.append(min(float(dd[:,sel].min()),float(det[i].min())));ppabs.append(min(float(abs(dd[:,sel]).min()),float(abs(det[i]).min())))
  npzsave(dest.with_suffix('.npz'),angles=theta,radii=RAD,points=points,determinant=det,kappa=kap,K=np.array(Ks),radial_grid=tt,radial_max_condition=kk.max(0),radial_min_signed_determinant=dd.min(0),radial_min_abs_determinant=abs(dd).min(0))
  r=dict(state=case,n=n,phase=phase,radii=RAD.tolist(),prefix_max_condition=ppmax,prefix_min_signed_det=ppsign,prefix_min_abs_det=ppabs,SPD=g.audit,nfev=sol.nfev,status='PASS')
 except Exception as e:r=dict(state=case,n=n,phase=phase,error=repr(e),traceback=traceback.format_exc(),SPD=g.audit,status='INCONCLUSIVE')
 r.update(wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu);save(dest,r);return r

def summarize(case):
 d=P/'states'/case;d.mkdir(parents=True,exist_ok=True);final=d/'result.json'
 if final.exists():return json.loads(final.read_text())
 start=time.perf_counter();cpu=time.process_time();old=OLD[case]
 for src,dst in [('state.npz','state.npz'),('checkpoint.pt','checkpoint.pt'),('nominal.json','nominal.json'),('result.json','T1A_result.json')]:
  if not(d/dst).exists():shutil.copyfile(A/'states'/case/src,d/dst)
 assert hashlib.sha256((d/'checkpoint.pt').read_bytes()).hexdigest()==old['checkpoint_sha256']
 rr=[]
 try:
  tasks=[task(case,n,ph) for n in [256,512] for ph in [0,1]]
  if any('error'in t for t in tasks):raise RuntimeError('At least one prescribed Jacobi task failed; no replacement.')
  data={}
  for n in [256,512]:
   zs=[np.load(d/f'jacobi_n{n}_phase{ph}.npz') for ph in [0,1]];theta=np.concatenate([z['angles'] for z in zs]);order=np.argsort(theta);data[n]={k:np.concatenate([z[k] for z in zs],axis=1)[:,order] for k in ['points','determinant','kappa','K']};data[n]['angles']=theta[order]
   for z in zs:z.close()
  nominal=[]
  for ph in [0,1]:
   with np.load(A/'states'/case/'jacobi'/f'n512_phase{ph}.npz') as z:nominal.append(z['determinant'])
  nominal_disk=max(float(kappa(x).max()) for x in nominal);nominal_end=max(float(kappa(x[:,-1]).max()) for x in nominal)
  for i,r in enumerate(RAD):
   lo=data[256];hi=data[512];ks=hi['kappa'][i];ds=hi['determinant'][i];K=hi['K'][i];b=topology(hi['points'][i],0);bl=topology(lo['points'][i],0)
   kmax=float(ks.max());kmlo=float(lo['kappa'][i].max());dm=float(abs(ds).min());dmlo=float(abs(lo['determinant'][i]).min());prefix=max(t['prefix_max_condition'][i] for t in tasks if t['n']==512);prefixsign=min(t['prefix_min_signed_det'][i] for t in tasks if t['n']==512)
   gates=dict(SPD=all(t['SPD']['nonpositive']==0 and t['SPD']['nonfinite']==0 for t in tasks),positive_prefix=prefixsign>0,boundary_simple=bool(b['simple'] and b['valid'] and bl['simple'] and bl['valid']),kappa_resolution=abs(kmax-kmlo)<=1e-6+.005*abs(kmax-1),det_resolution=abs(dm-dmlo)<=1e-6+.005*abs(dm))
   Kabs=np.abs(K);rms=float(np.sqrt(np.mean(K*K)));energy=K*K;total=float(energy.sum());angmax=int(np.argmax(ks))
   row=dict(state=case,split=int(old['split']),init=int(old['init']),regime=old['regime'],T1A_classification=old['classification'],radius_index=i,radius=float(r),primary=i==2,status='PASS' if all(gates.values()) else 'INCONCLUSIVE',kappa_max=kmax,kappa_median=float(np.median(ks)),kappa_q90=float(np.quantile(ks,.9)),kappa_prefix_max=prefix,minimum_abs_det=dm,minimum_signed_det=float(ds.min()),prefix_min_signed_det=prefixsign,det_q10=float(np.quantile(ds,.1)),det_median=float(np.median(ds)),angle_max_kappa=float(hi['angles'][angmax]),fraction_det_below_half=float(np.mean(ds<.5)),K_signed_mean=float(K.mean()),K_rms=rms,K_max_abs=float(Kabs.max()),angular_K_abs_cv=float(Kabs.std()/max(Kabs.mean(),1e-30)),angular_K_std_to_rms=float(K.std()/max(rms,1e-30)),angular_K_peak_to_rms=float(Kabs.max()/max(rms,1e-30)),angular_K_top10_energy=float(np.sort(energy)[-int(np.ceil(len(K)*.1)):].sum()/total) if total else None,kappa_resolution_difference=abs(kmax-kmlo),det_resolution_difference=abs(dm-dmlo),boundary_intersections=b['intersection_count'],nominal_radius=float(old['nominal_radius']),kappa_nominal_disk=nominal_disk,kappa_nominal_endpoint=nominal_end,gates=gates)
   for m in ['C_A','lambda_1pct','lambda_01pct','R_eff','frac50','frac90','r_conj','r_inj_upper','A_embed','A_embed_ratio']:row[m]=float(old[m]) if old.get(m) else None
   row['A_embed_censored']=old['A_embed_censored']=='True';rr.append(row)
  result=dict(state=case,status='PASS' if all(x['status']=='PASS' for x in rr) else 'INCONCLUSIVE',results=rr,checkpoint_sha256=old['checkpoint_sha256'],field_sha256=hashlib.sha256((d/'state.npz').read_bytes()).hexdigest(),tasks=tasks)
 except Exception:result=dict(state=case,status='INCONCLUSIVE',results=rr,error=traceback.format_exc())
 result.update(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu);save(final,result);return result

def progress():
 states=[json.loads(f.read_text()) for f in sorted((P/'states').glob('*/result.json'))];rows=[r for s in states for r in s['results']];fields=sorted(set(k for r in rows for k in r))
 with (P/'common_radius_results.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 tasks=[]
 for s in states:
  for t in s.get('tasks',[]):tasks.append({k:t.get(k) for k in ['state','n','phase','status','wall_seconds','cpu_seconds','error']})
 with (P/'task_log.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=['state','n','phase','status','wall_seconds','cpu_seconds','error']);w.writeheader();w.writerows(tasks)
 completed={s['state'] for s in states};pending=sorted(set(OLD)-completed);errors=[dict(state=s['state'],error=s.get('error'),failed_radius_gates=[{'radius':r['radius'],'gates':r['gates']} for r in s['results'] if r['status']!='PASS']) for s in states if s['status']!='PASS'];save(P/'errors.json',errors)
 txt=f'# E15-T1-B — progreso\n\nEstados completados:{len(states)}/80; pendientes:{len(pending)}. Filas estado/radio:{len(rows)}/320. Estados con compuerta INCONCLUSIVE:{len(errors)}.\n\nRadios congelados:{RAD.tolist()}; radio principal:{RAD[2]}. SHA protocolo:{hashlib.sha256((P/"protocol_T1_B_frozen.json").read_bytes()).hexdigest()}.\n\nÚltima tarea válida: '+(states[-1]['state'] if states else 'verificación y congelación')+'.\n\nPendientes:'+','.join(pending)+'.\n\nCompletados:'+','.join(sorted(completed))+'.\n\nErrores:errors.json. No se sustituyen estados ni se cambian radios. C1/T1A permanecen intactos. Todos los nuevos result.json y diagnósticos se conservan en paquetes por estado.\n\nReanudar: recuperar archivos de esta carpeta, extraer cada split*.zip; recuperar T1A verificado en source_locations.json (adaptar sólo ruta local, nunca insumos científicos), instalar dependencias de T1A, verificar protocolo SHA, ejecutar run_common.py. Los result.json confirmados se omiten. Si hay resultado local terminado sin recibo de persistencia, guardar ese paquete antes de avanzar; no reintegrar.\n'
 (P/'progress.md').write_text(txt);manifest=[]
 for f in sorted(P.rglob('*')):
  if f.is_file() and f.name not in ['manifest.csv','persistence_receipts.json'] and '__pycache__'not in str(f):manifest.append(dict(path=str(f.relative_to(P)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 with (P/'manifest.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(manifest)
 return states

def main():
 from concurrent.futures import ProcessPoolExecutor
 assert hashlib.sha256((P/'protocol_T1_B_frozen.json').read_bytes()).hexdigest()==(P/'protocol_T1_B_frozen.sha256').read_text()
 cases=[c for c in sorted(OLD) if not(P/'states'/c/'result.json').exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i in range(0,len(cases),4):
   batch=cases[i:i+4];results=list(pool.map(summarize,batch));paths=[]
   for s in results:
    print(s['state'],s['status'],s.get('error',''),flush=True);d=P/'states'/s['state'];zp=P/(d.name+'.zip')
    with tempfile.NamedTemporaryFile(dir='/tmp',suffix='.zip',delete=False) as f:tmp=Path(f.name)
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
     for f in sorted(d.iterdir()):
      if f.is_file():z.write(f,str(f.relative_to(P)))
    os.replace(tmp,zp);paths.append(zp)
   persist(paths);ss=progress();persist([P/n for n in ['common_radius_results.csv','task_log.csv','errors.json','manifest.csv','progress.md']]);print('COMMITTED',len(ss),flush=True)
if __name__=='__main__':main()
