#!/usr/bin/env python3
"""Instrumento congelado bajo prueba: nunca carga datos T2."""
from references_v1 import *
from concurrent.futures import ProcessPoolExecutor
import signal,warnings,traceback,resource,platform,scipy

FIELDS=['rho_borde','err_quad','theta','rho_min_gl','dif_orden','dif_dir','rho_mediana']
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
 if isinstance(x,list):return [clean(v) for v in x]
 if isinstance(x,(float,np.floating)) and not math.isfinite(x):return repr(float(x))
 return x

def native_call(gm,source,M,f):
 start=time.monotonic();raw=None;error='';status='RETURNED'
 with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter('always')
  try:raw=source.rho_borde(gm.Geometry(M,f))
  except Exception as e:status='TIMEOUT' if isinstance(e,TimeoutError) else 'ERROR';error=traceback.format_exc()
 notes=[{'category':w.category.__name__,'message':str(w.message)} for w in caught]
 finite=raw is not None and all(math.isfinite(float(raw[k])) for k in FIELDS)
 if status=='RETURNED' and not finite:status='NONFINITE_DIAGNOSTICS'
 if raw is not None and math.isfinite(raw['rho_borde']) and raw['rho_borde']<0:status='NEGATIVE'
 return {'status':status,'raw':clean(raw),'numeric':raw,'finite':finite,'warnings':notes,'error':error,'seconds':time.monotonic()-start}

def controls():
 answer=[]
 def check(name,ok,value):answer.append({'control':name,'status':'PASS' if ok else 'FAIL','error':float(value)})
 with mp.workdps(80):
  rr=[Fr(0),Fr(0),Fr(-1)];a,_=coordinate_tv(rr,0);b,_=coordinate_tv(rr,2);check('coordinate/triangle_face',abs(a-mp.mpf(1)/6)<mp.mpf('1e-60'),abs(a-mp.mpf(1)/6));check('coordinate/extinction',abs(b-mp.mpf(1)/3)<mp.mpf('1e-60'),abs(b-mp.mpf(1)/3))
  rr=[Fr(-2),Fr(-1),Fr(0)];value,roots=contrast_tv(rr,0,1);r=[mm(x) for x in rr]
  def derivative(s):
   a=[mp.exp(x*s) for x in r];den=sum(a);a=[x/den for x in a];mean=mp.fdot(a,r);return abs((a[0]*(r[0]-mean)-a[1]*(r[1]-mean))/mp.sqrt(2))
  integral=mp.quad(derivative,[0,roots[0],mp.inf]);check('contrast/peak_independent_integral',abs(value-integral)<mp.mpf('1e-40'),abs(value-integral));zero,_=contrast_tv([Fr(-1),Fr(-1),Fr(0)],0,1);check('contrast/identical_projections',zero==0,zero);inc,_=contrast_tv([Fr(0),Fr(-1),Fr(-2)],0,1);check('contrast/monotone',abs(inc-1/mp.sqrt(2))<mp.mpf('1e-60'),abs(inc-1/mp.sqrt(2)))
  # Segunda referencia directa GL80 para el caso suave de la norma isótropa.
  p={'f':[[0.,0.],[1.,0.],[0.,1.]]};c={'kind':'isotropic'};rr=projections(p,['1','0']);got=direct(c,rr);check('direct_MP/convergence',got['status']=='PASS',got['reference_error']);check('direct_MP/analytic_length',abs(mm(got['value'])-mp.sqrt(2)/3)<mp.mpf('1e-12'),abs(mm(got['value'])-mp.sqrt(2)/3))
  cr=[Fr(-1,2),Fr(0),Fr(-2)];value,peak_roots=coordinate_tv(cr,0);rv=[mm(x) for x in cr]
  def coordinate_derivative(t):
   a=[mp.exp(x*t) for x in rv];den=sum(a);a=[x/den for x in a];return abs(a[0]*(rv[0]-mp.fdot(a,rv)))
  integral=mp.quad(coordinate_derivative,[0,peak_roots[0],mp.inf]);check('coordinate/peak_independent_integral',abs(value-integral)<mp.mpf('1e-40'),abs(value-integral))
 return answer

def compare(value,ref):return abs(value-ref)<=CFG['absolute_tolerance']+CFG['relative_tolerance']*abs(ref)

def analyse(task):
 panel,case,array_root,deadline,extra=task;start=time.monotonic();gm,source=sources();f=np.array(panel['f']);M=matrix(case);sid=case['id'];arrays=[];refs={};error='';primary=None;extra_return=None
 def alarm(signum,frame):raise TimeoutError('FIXED_CASE_BUDGET')
 old=signal.signal(signal.SIGALRM,alarm);remaining=min(CFG['per_case_seconds'],max(.001,deadline-time.monotonic()));signal.setitimer(signal.ITIMER_REAL,remaining)
 def archive(label,a):
  target=Path(array_root)/(sid.replace('/','_')+'_'+label+'.npy')
  if target.exists():raise FileExistsError(target)
  np.save(target,np.asarray(a),allow_pickle=False);arrays.append({'state':sid,'label':label,'file':target.name,'shape':str(np.asarray(a).shape),'sha256':sha(target)})
 row={'state':sid,'panel':panel['id'],'form':panel['form'],'kind':case['kind'],'native_status':'UNKNOWN','native_rho':None,'reference_exact':None,'reference_lower':None,'reference_upper':None,'reference_native_direction':None,'reference_method':'','minimum_check':'INCONCLUSIVE','witness_check':'INCONCLUSIVE','Q5':'INCONCLUSIVE','trace':None,'lambda_max':None,'lambda_min':None,'matrix_control':'UNKNOWN','global_reference_control':'UNKNOWN','global_witness_error':None,'pointwise_squared_error':None,'native_seconds':None,'reference_seconds':None,'log_native_over_floor':None,'log_native_over_reference':None,'reason':''}
 try:
  archive('M',M);eig=np.linalg.eigvalsh(M);row.update(trace=float(np.trace(M)),lambda_max=float(eig[-1]),lambda_min=float(eig[0]));beta=gm.Geometry(M,f).jac([[.17,-.23]])[0]@np.array([.6,.8]);q=float(beta@M@beta)
  with mp.workdps(80):factor=norm(case,[mm(x) for x in beta])**2;err=float(abs(mm(q)-factor))
  row['pointwise_squared_error']=err;row['matrix_control']='PASS' if abs(np.trace(M)-1)<1e-12 and eig[0]>=-1e-12 and err<=1e-10 else 'FAIL'
  t=time.monotonic();G=global_reference(panel,case,archive);refs['global']=G;row.update(reference_exact=G['exact'],reference_lower=G['lower'],reference_upper=G['upper']);row['reference_seconds']=time.monotonic()-t
  if G['known_exact']:
   witness_error=abs(G['upper_witness']['value']-G['exact']);row['global_witness_error']=witness_error;row['global_reference_control']=('PASS' if witness_error<=1e-12+1e-8*abs(G['exact']) else 'FAIL') if G['status']=='PASS' else 'UNKNOWN'
  else:row['global_reference_control']='PASS_BRACKET' if G['status']=='PASS' and G['upper']>=G['lower']-1e-12 else 'UNKNOWN'
  primary=native_call(gm,source,M,f);row.update(native_status=primary['status'],native_seconds=primary['seconds']);raw=primary['numeric']
  if raw is not None and math.isfinite(raw['rho_borde']):row['native_rho']=float(raw['rho_borde'])
  if primary['status']!='TIMEOUT' and raw is not None and math.isfinite(raw['theta']):
   t=time.monotonic();u=[math.cos(raw['theta']),math.sin(raw['theta'])];R=direction(panel,case,u,archive,'native_reference_parts');refs['native_direction']=R;row.update(reference_native_direction=R['value'],reference_method=R['method']);row['reference_seconds']+=time.monotonic()-t
   if row['native_rho'] is not None and R['status']=='PASS':row['witness_check']='PASS' if compare(row['native_rho'],R['value']) else 'FAIL'
  if row['native_rho'] is not None:
   value=row['native_rho']
   if G['known_exact']:row['minimum_check']='PASS' if compare(value,G['exact']) else 'FAIL'
   elif G['status']=='PASS':
    tol=CFG['absolute_tolerance']+CFG['relative_tolerance']*max(abs(G['lower']),abs(G['upper']));row['minimum_check']='PASS_BRACKET_ONLY' if G['lower']-tol<=value<=G['upper']+tol else 'FAIL'
   if value>0:row['log_native_over_floor']=math.log(value*len(f));row['log_native_over_reference']=math.log(value/G['exact']) if G['known_exact'] and G['exact'] and G['exact']>0 else None
  if primary['status'] in ['ERROR','NONFINITE_DIAGNOSTICS','NEGATIVE'] or 'FAIL' in [row['minimum_check'],row['witness_check']]:row['Q5']='FAIL'
  elif primary['status']=='RETURNED' and row['minimum_check'] in ['PASS','PASS_BRACKET_ONLY'] and row['witness_check']=='PASS':row['Q5']='PASS'
  if extra and primary['status']=='RETURNED':
   extra_return=native_call(gm,source,4*M,f)
   if extra_return['status']=='RETURNED':extra_return['homogeneity_check']='PASS' if compare(extra_return['numeric']['rho_borde'],2*row['native_rho']) else 'FAIL'
   else:extra_return['homogeneity_check']='INCONCLUSIVE' if extra_return['status']=='TIMEOUT' else 'FAIL'
 except Exception as e:error=traceback.format_exc();row['reason']=type(e).__name__+':'+str(e)
 finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
 if primary is not None:primary.pop('numeric',None)
 if extra_return is not None:extra_return.pop('numeric',None)
 return row,{'state':sid,'native':primary,'homogeneity_4M':extra_return,'reference':refs,'wrapper_error':error},arrays,{'state':sid,'seconds':time.monotonic()-start,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'blocked_T2_reads':ACCESS['blocked']}

def main(out,arrays):
 if out.exists() or arrays.exists():raise FileExistsError('preservar versiones')
 out.mkdir(parents=True);arrays.mkdir(parents=True);start=time.monotonic();panels,cases=synthetic();write(out/'inputs.json',{'panels':panels,'cases':cases});ctrl=controls();table(out/'controls.csv',ctrl)
 if any(c['status']=='FAIL' for c in ctrl):write(out/'summary.json',{'status':'INVALID','reason':'REFERENCE_CONTROLS_FAILED'});raise RuntimeError('enmienda congelada antes de corregir referencia; no sobrescribir')
 states=[];raw=[];manifest=[];resources=[];byid={p['id']:p for p in panels}
 def save():
  table(out/'states.csv',states);write(out/'raw_and_references.json',clean(raw));table(out/'arrays.csv',manifest);write(out/'resources.json',{'seconds':time.monotonic()-start,'workers':3,'arrays_root':str(arrays),'worker_resources':resources})
 with ProcessPoolExecutor(max_workers=3) as pool:
  tasks=[(byid[c['panel']],c,str(arrays),start+CFG['total_seconds'],i==0) for i,c in enumerate(cases)]
  for case,(r,detail,arr,timing) in zip(cases,pool.map(analyse,tasks,chunksize=1)):
   states.append(r);raw.append(detail);manifest.extend(arr);resources.append(timing);save();print(case['id'],r['native_status'],r['native_rho'],r['reference_exact'],r['Q5'],flush=True)
 counts={label:sum(x['Q5']==label for x in states) for label in ['PASS','FAIL','INCONCLUSIVE']};valid=all(x['matrix_control']=='PASS' and x['global_reference_control']!='FAIL' for x in states);hom=raw[0]['homogeneity_4M'];q5='FAIL' if counts['FAIL'] or hom and hom.get('homogeneity_check')=='FAIL' else ('PASS' if counts['PASS']==210 else 'INCONCLUSIVE');summary={'status':'VALID_EXPLORATORY' if valid else 'INVALID','states':len(states),'panels':12,'Q1':'PASS','Q2':'PASS','Q3':'PASS','Q4':'PASS_DESCRIPTIVE','Q5':q5,'Q5_counts':counts,'reference_controls_pass':len(ctrl),'matrix_controls_pass':sum(x['matrix_control']=='PASS' for x in states),'homogeneity_native':hom.get('homogeneity_check') if hom else 'UNKNOWN','T2_states_used':0,'theory_note':'Los PASS Q1-Q4 resuelven preguntas condicionales; no afirman el piso universal ni una causa empírica.'}
 if not valid:summary.update(**{f'Q{i}':'INCONCLUSIVE' for i in range(1,6)})
 write(out/'summary.json',summary);write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__,'geometry_sha256':CFG['geometry_sha256'],'rho_sha256':CFG['rho_sha256'],'measurement_code_sha256':{p.name:sha(p) for p in [ROOT/'scripts/common_v1.py',ROOT/'scripts/references_v1.py',Path(__file__)]},'threads':1,'rho_call':'rho_borde(g), defaults originales sin monkeypatch'});save();print(json.dumps(summary),flush=True)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'results/run_v1');ap.add_argument('--arrays',type=Path,default=Path(CFG['arrays_root']));args=ap.parse_args();main(args.out,args.arrays)
