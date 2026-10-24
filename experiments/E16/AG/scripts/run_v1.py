#!/usr/bin/env python3
"""E16-AG v1: todos los estados y fallos, sin tocar las etapas cerradas."""
from numerics_v1 import *
from concurrent.futures import ProcessPoolExecutor
from scipy.stats import spearmanr
import argparse,resource,platform,scipy

TABLES=['states','rho_resolutions','rho_attempts','ray_steps','refinement','arrays','MP_probes']

def controls(gm,states):
 checks=[]
 def check(name,ok,value):checks.append({'control':name,'status':'PASS' if ok else 'FAIL','value':float(value)})
 # La probabilidad binaria recorre medio segmento, con norma sqrt(2).
 for order in [400,800]:
  t,w=leggauss(order);x=(t+1)/2;s=10*x/(1-x);z=np.exp(-.04*s);val=float(np.sum(w/2*10/(1-x)**2*np.sqrt(2)*.04*z/(1+z)**2));check(f'binary/GL{order}',abs(val-1/np.sqrt(2))<2e-5,val)
 with mp.workdps(80):
  val=mp.quad(lambda s:mp.sqrt(2)*mp.mpf('.04')*mp.exp(-mp.mpf('.04')*s)/(1+mp.exp(-mp.mpf('.04')*s))**2,[0,25,250,mp.inf]);err=abs(val-1/mp.sqrt(2));check('binary/MP80',err<mp.mpf('1e-60'),err)
 f=.04*np.column_stack([np.cos(np.arange(3)*2*np.pi/3),np.sin(np.arange(3)*2*np.pi/3)]);M=np.eye(3);g=gm.Geometry(M,f);rr,_,_=rho_measure(g,M,f,lambda *args:None);W,db,rho,foot=exact_triangle(M);check('triangle3/rho',abs(rr['rho']-1/np.sqrt(6))<2e-5,rr['rho']);check('triangle3/d_border',abs(db-1/np.sqrt(6))<1e-14,db)
 # Carta plana conocida: usando9 duplicados por vértice para el adaptador.
 ff=np.repeat(f,9,axis=0);DD=np.repeat(np.eye(3),9,axis=0);MM=DD@DD.T+1e-6*np.eye(27);gg=gm.Geometry(MM,ff);tr=exponential(gg,MM,ff,np.arange(2048)*2*np.pi/2048,.8,True);db2=exact_triangle(MM)[1];check('triangle3/escape_face',tr['status']=='ESCAPE' and tr['r']<=db2*(1+2e-5) and tr['r']>.99*db2,tr['r']/db2)
 A=np.array([[2,.3],[-.2,.7]]);b=np.array([.6,-.4]);q0=-np.linalg.solve(A,b);check('affine/origin',np.linalg.norm(A@q0+b)<1e-14,np.linalg.norm(A@q0+b))
 for st in [states[0],states[40]]:
  M=np.array(st['M']);f=np.array(st['f']);base,_,_=rho_measure(gm.Geometry(M,f),M,f,lambda *args:None);trans=f@A;changed,_,_=rho_measure(gm.Geometry(M,trans),M,trans,lambda *args:None);err=abs(base['rho']-changed['rho'])/base['rho'];check('affine/'+st['group'],err<2e-5,err)
 # Sólo evalúa geometría sintética de AD/AC, no lanza sus runners.
 d=load_e16('ag_d',ROOT.parent/'D/scripts/run.py');ac=load_e16('ag_ac',ROOT.parent/'AC/scripts/run_v2.py');data=json.loads((ROOT.parent/'H/data.json').read_text())
 with mp.workdps(80):
  th=[mp.mpf(str(x)) for x in data['states']['h00']];inp=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels']['P0']];cv,jc,_,ch=d.analytic_mp(th,inp);ux=d.analytic_B(cv,jc,[1,0],'quadratic')[0]*ch;uy=d.analytic_B(cv,jc,[0,1],'quadratic')[0]*ch
 flat=ac.Metric('quadratic',np.array(ux.tolist(),float),np.array(uy.tolist(),float));p=np.array(data['perspectives'][0]);err=abs(float(flat.geometry(p)[2]));check('AD/flat_K',err<1e-7,err)
 saved=next(x for x in rows(ROOT.parent/'AC/results/run_v2/shooting.csv') if x['path']=='Q0/reference/132' and float(x['rtol'])==1e-12);check('AD/archived_continuous_L',abs(float(saved['L'])-.506971938975)<1e-11,float(saved['L']))
 return checks

def analyse(task):
 st,array_root,deadline=task;started=time.monotonic();gm=geometry();M=np.array(st['M']);f=np.array(st['f']);g=gm.Geometry(M,f);ts={k:[] for k in TABLES};sid=st['id'];tri=st['group']=='triangle'
 def budget():
  if time.monotonic()>deadline or time.monotonic()-started>CFG['per_state_seconds']:raise TimeoutError('FIXED_BUDGET')
 def archive(label,array):
  target=Path(array_root)/(sid.replace('/','_')+'_'+label+'.npy')
  if target.exists():raise FileExistsError(target)
  np.save(target,np.asarray(array),allow_pickle=False);ts['arrays'].append({'state':sid,'label':label,'file':target.name,'shape':str(np.asarray(array).shape),'sha256':sha(target)})
 row={'state':sid,'group':st['group'],'seed':st['seed'],'scale':st['length_scale'],'K0':None,'M_eigen_min':None,'M_eigen_max':None,'rho':None,'rho_status':'UNKNOWN','rho_seconds':None,'rho_resolution_error':None,'MP_speed_error':None,'d_border_exact':None,'rho_exact':None,'rho_exact_error':None,'d_escape':None,'coarse_escape':None,'escape_status':'UNKNOWN','refined_valid':False,'exp_seconds':None,'steps':None,'stop_radius':None,'face':'','min_weight':None,'max_weight':None,'tail_trend':'UNKNOWN','ratio':None,'ratio_true':None,'escape_to_true':None,'stop_over_rho':None,'Q1':'INCONCLUSIVE','control_exact':'NOT_APPLICABLE','reason':''}
 try:
  budget();eig=np.linalg.eigvalsh(M);row.update(K0=float(g.eval([[0.,0.]])[1][0]),M_eigen_min=float(eig[0]),M_eigen_max=float(eig[-1]))
  rr,grids,attempts=rho_measure(g,M,f,archive,budget)
  row.update(rho=rr['rho'],rho_status=rr['status'],rho_seconds=rr['seconds'],rho_resolution_error=rr['resolution_error'],MP_speed_error=rr['MP_speed_error'])
  for x in grids:ts['rho_resolutions'].append({'state':sid,**x})
  for x in attempts:ts['rho_attempts'].append({'state':sid,**x})
  if tri:
   W,db,re,foot=exact_triangle(M);err=abs(rr['rho']-re)/re;row.update(d_border_exact=db,rho_exact=re,rho_exact_error=err,ratio_true=rr['rho']/db,control_exact='PASS' if err<2e-5 else 'FAIL')
   # Jet en carta q coincide con H: control métrico independiente del IVP.
   F=f[::9];q=np.ones(3)/3;B=np.linalg.solve(F[:2]-F[2],np.array([[1/q[0]+1/q[2],1/q[2]],[1/q[2],1/q[1]+1/q[2]]]))
   H=np.array([[1,0],[0,1],[-1,-1]]).T@W@np.array([[1,0],[0,1],[-1,-1]])
   if np.max(abs(B.T@g.jet([[0,0]])[0][0]@B-H))/max(np.max(abs(H)),1e-30)>2e-5:row['control_exact']='FAIL'
  exp_start=time.monotonic();R=CFG['horizon_rho_factor']*rr['rho'];tr=exponential(g,M,f,np.arange(2048)*2*np.pi/2048,R,tri,budget);row.update(escape_status=tr['status'],steps=tr['steps'],stop_radius=tr['r'],stop_over_rho=tr['r']/rr['rho'],reason=tr['reason'])
  archive('profiles_'+tr['coordinate'],np.array(tr['profiles']).transpose(1,2,0));archive('profile_radii',np.array(tr['radii']))
  for x in tr['records']:ts['ray_steps'].append({'state':sid,**x})
  best,attempts,ok=refine_escape(g,M,f,tr,R,tri,budget)
  for x in attempts:ts['refinement'].append({'state':sid,**x})
  row.update(exp_seconds=time.monotonic()-exp_start,refined_valid=ok)
  if tr['status']=='ESCAPE':
   de=min(tr['r'],best['r']) if best else tr['r'];p=np.array(tr['P']);axis=int(np.argmax(abs(p)));aa=softmax(f@p);row.update(d_escape=de,coarse_escape=tr['r'],ratio=rr['rho']/de,face=('+' if p[axis]>0 else '-')+'P'+str(axis+1),min_weight=float(min(aa)),max_weight=float(max(aa)))
   mins=[]
   for arr in tr['profiles'][-8:]:
    if tri:w=np.r_[arr[:2,tr['ray_index']],1-sum(arr[:2,tr['ray_index']])];mins.append(float(min(w)/9))
    else:mins.append(float(min(softmax(f@arr[:2,tr['ray_index']]))))
   row['tail_trend']='INCIDENT_MIN_WEIGHT_DECREASING' if len(mins)>1 and np.all(np.diff(mins)<=1e-10) else 'UNKNOWN'
   if tri:
    row['escape_to_true']=de/row['d_border_exact']
    if de>row['d_border_exact']*(1+2e-5):row['control_exact']='FAIL'
   if rr['status']=='PASS' and ok:row['Q1']='PASS' if rr['rho']>=de*(1-2e-5) else 'FAIL'
 except Exception as e:row['reason']+=';'+type(e).__name__+':'+str(e)
 ts['states'].append(row)
 return ts,{'state':sid,'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'blocked_reads':af.ACCESS['blocked']}

def assessment(states,control_ok):
 valid=[x for x in states if x['rho_status']=='PASS' and x['refined_valid'] and x['d_escape'] is not None];groups=[]
 for name in ['triangle','AF','ALL']:
  allrows=states if name=='ALL' else [x for x in states if x['group']==name];rr=[x for x in valid if x in allrows];ratios=[x['ratio'] for x in rr];corr=float(spearmanr([x['rho'] for x in rr],[x['d_escape'] for x in rr]).statistic) if len(rr)>2 else None;times=[x['rho_seconds']/x['exp_seconds'] for x in rr if x['rho_seconds'] is not None and x['exp_seconds']]
  groups.append({'group':name,'states':len(allrows),'escapes':sum(x['escape_status']=='ESCAPE' for x in allrows),'valid_pairs':len(rr),'unknown_pairs':len(allrows)-len(rr),'fraction_escape':sum(x['escape_status']=='ESCAPE' for x in allrows)/len(allrows),'median_ratio':float(np.median(ratios)) if ratios else None,'max_ratio':max(ratios) if ratios else None,'spearman':corr if corr is None or np.isfinite(corr) else None,'median_time_rho_over_exp':float(np.median(times)) if times else None})
 total=groups[-1];q1='FAIL' if any(x['Q1']=='FAIL' for x in states) else ('PASS' if len(valid)==80 else 'INCONCLUSIVE');q2='INCONCLUSIVE'
 if total['max_ratio'] is not None:
  if total['median_ratio']>1.2 or total['max_ratio']>2:q2='FAIL'
  elif len(valid)==80:q2='PASS'
 q3='FAIL' if any(x['valid_pairs']>=10 and x['spearman'] is not None and x['spearman']<.9 for x in groups) else ('PASS' if len(valid)==80 and all(x['spearman'] is not None and x['spearman']>=.9 for x in groups) else 'INCONCLUSIVE')
 drag=[x for x in states if x['group']=='AF' and x['escape_status']=='DRAG_5000' and x['rho'] is not None];q4=('PASS_DESCRIPTIVE' if all(.6<=x['stop_over_rho']<=1 for x in drag) else 'FAIL_DESCRIPTIVE') if drag else 'INCONCLUSIVE'
 q5='INCONCLUSIVE'
 if all(x['median_time_rho_over_exp'] is not None for x in groups[:2]):q5='PASS_DESCRIPTIVE' if all(x['median_time_rho_over_exp']<1 for x in groups[:2]) else 'FAIL_DESCRIPTIVE'
 status='VALID_EXPLORATORY' if control_ok else 'INVALID'
 if not control_ok:q1=q2=q3=q4=q5='INCONCLUSIVE'
 return groups,{'status':status,'states':len(states),'valid_pairs':len(valid),'Q1':q1,'Q2':q2,'Q3':q3,'Q4':q4,'Q5':q5,'drag_5000':len(drag),'data_T2':'NONE','true_boundary_AF':'UNKNOWN'}

def main(out,arrays):
 if out.exists() or arrays.exists():raise FileExistsError('no sobrescribir versiones')
 out.mkdir(parents=True);arrays.mkdir(parents=True);started=time.monotonic();gm=geometry();states=inputs();write(out/'inputs.json',states);ctrl=controls(gm,states);table(out/'controls.csv',ctrl)
 if not all(x['status']=='PASS' for x in ctrl):write(out/'summary.json',{'status':'INVALID','reason':'PRECONTROLS_FAILED'});raise RuntimeError('preservar controles fallidos; nueva versión antes de corregir')
 alltables={k:[] for k in TABLES};resources=[]
 def save():
  for k,v in alltables.items():table(out/(k+'.csv'),v)
  write(out/'resources.json',{'seconds':time.monotonic()-started,'arrays_root':str(arrays),'workers':2,'worker_resources':resources})
 with ProcessPoolExecutor(max_workers=2) as pool:
  tasks=[(st,str(arrays),started+CFG['budget_seconds']) for st in states]
  for st,(tables,timing) in zip(states,pool.map(analyse,tasks,chunksize=1)):
   for k,v in tables.items():alltables[k].extend(v)
   resources.append(timing);save();x=tables['states'][0];print(st['id'],x['rho_status'],x['escape_status'],x['ratio'],x['reason'],flush=True)
 groups,summary=assessment(alltables['states'],all(x['control_exact']!='FAIL' for x in alltables['states']));table(out/'groups.csv',groups);write(out/'summary.json',summary)
 write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__,'geometry_sha256':CFG['geometry_sha256'],'audit_sha256':CFG['audit_sha256'],'code_sha256':{p.name:sha(p) for p in sorted((ROOT/'scripts').glob('*v1.py'))},'guard':'AF original intacta','affine_origin':'q0=-A^-1 b; mismo P0 físico'})
 save();print(json.dumps(summary),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'results/run_v1');ap.add_argument('--arrays',type=Path,default=Path(CFG['arrays_root']));args=ap.parse_args();main(args.out,args.arrays)
