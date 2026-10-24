#!/usr/bin/env python3
"""AH: una ejecución con todos los80 estados, presupuestos y testigos."""
from search_v1 import *
from concurrent.futures import ProcessPoolExecutor
import argparse,resource,platform,scipy,warnings

def flexible_table(path,data):
 if not data:return
 fields=list(dict.fromkeys(k for row in data for k in row))
 encoded=[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in data]
 table(path,encoded,fields)

def controls(gm,states):
 result=[]
 def check(name,ok,value):result.append({'control':name,'status':'PASS' if ok else 'FAIL','value':float(value)})
 f=.04*np.column_stack([np.cos(np.arange(3)*2*np.pi/3),np.sin(np.arange(3)*2*np.pi/3)]);F=Family(np.eye(3),f,1/np.sqrt(6));theta,S=F.edges[0];qr=F.validate([0,0],theta,S);hp=MPFamily(F).validate([0,0],theta,S,qr);check('trivial/null_analytic',abs(qr['length']-1/np.sqrt(6))<1e-7,qr['length']);check('trivial/null_MP',hp['MP_status']=='PASS',hp['MP_relative_error'])
 A=np.array([[2,.3],[-.2,.7]]);b=np.array([.6,-.4]);origin=-np.linalg.solve(A,b);check('affine/origin',np.linalg.norm(A@origin+b)<1e-14,np.linalg.norm(A@origin+b))
 for state in [states[0],states[40]]:
  M=np.array(state['M']);f=np.array(state['f']);F=Family(M,f,1.);T=Family(M,f@A,1.);q=[.4,-.7]
  for kind in ['edge','generic']:
   angle,S=F.edges[0]
   if kind=='generic':angle=(angle+F.edges[1][0])/2;S=None
   changed=None if S is None else min(T.edges,key=lambda e:abs(np.angle(np.exp(1j*(e[0]-angle)))))[1]
   first=F.validate(q,angle,S);second=T.validate(q,angle,changed);err=abs(first['length']-second['length'])/first['length'];check('affine/'+state['group']+'/'+kind,err<1e-7,err)
   # Contraste de la fórmula agrupada con J original sin cambiar la fuente.
   Q=F.Binv@np.asarray(q);u=F.Binv@np.array([np.cos(angle),np.sin(angle)]);g=gm.Geometry(M,f);vals=[]
   for t in [.13,.61]:
    beta=g.jac([t*Q])[0]@Q;source=np.sqrt(beta@M@beta);x=F.f@np.asarray(q);grouped=F.speed(F.c+t*x,x);vals.append(abs(float(source)-float(grouped))/max(float(source),1e-30))
   check('source_J/'+state['group']+'/'+kind,max(vals)<1e-7,max(vals))
 # Evaluación instrumental mínima del plano E16: no se ejecutan runners AD/AC.
 d=ag.load_e16('ah_d',ROOT.parent/'D/scripts/run.py');ac=ag.load_e16('ah_ac',ROOT.parent/'AC/scripts/run_v2.py');data=json.loads((ROOT.parent/'H/data.json').read_text())
 with mp.workdps(80):
  th=[mp.mpf(str(x)) for x in data['states']['h00']];inp=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels']['P0']];cv,jc,_,ch=d.analytic_mp(th,inp);ux=d.analytic_B(cv,jc,[1,0],'quadratic')[0]*ch;uy=d.analytic_B(cv,jc,[0,1],'quadratic')[0]*ch
 flat=ac.Metric('quadratic',np.array(ux.tolist(),float),np.array(uy.tolist(),float));err=abs(float(flat.geometry(np.array(data['perspectives'][0]))[2]));check('AD/flat_K',err<1e-7,err)
 saved=next(x for x in rows(ROOT.parent/'AC/results/run_v2/shooting.csv') if x['path']=='Q0/reference/132' and float(x['rtol'])==1e-12);check('AD/archived_L',abs(float(saved['L'])-.506971938975)<1e-11,float(saved['L']))
 return result

def analyse(task):
 st,reference,array_root,deadline=task;start=time.monotonic();gm=geometry();M=np.array(st['M']);f=np.array(st['f']);g=gm.Geometry(M,f);sid=st['id'];data={'states':[],'arrays':[],'rho_resolutions':[],'rho_attempts':[],'optimizers':[],'candidates':[]};sinks=([],[],[]);validated=[]
 row={'state':sid,'group':st['group'],'status':'UNKNOWN','rho0':None,'rho0_grid':None,'rho1':None,'d_border':reference['d_border_exact'] if reference['d_border_exact'] else None,'rho1_over_true':None,'rho1_over_rho0':None,'time_rho0':None,'time_incremental':None,'time_total':None,'baseline_MP':'UNKNOWN','baseline_control':'UNKNOWN','winner_candidate':None,'q1':None,'q2':None,'Q1_P':None,'Q2_P':None,'u1_P':None,'u2_P':None,'support_original':'','endpoint_original':'','numeric_relative_error':None,'evaluations':0,'optimizer_converged':0,'optimizer_total':0,'reason':''}
 if row['d_border'] is not None:row['d_border']=float(row['d_border'])
 def budget():
  if time.monotonic()>deadline or time.monotonic()-start>CFG['per_state_seconds']:raise TimeoutError('FIXED_BUDGET')
 def archive(label,array):
  p=Path(array_root)/(sid.replace('/','_')+'_'+label+'.npy')
  if p.exists():raise FileExistsError(p)
  np.save(p,np.asarray(array),allow_pickle=False);data['arrays'].append({'state':sid,'label':label,'file':p.name,'shape':str(np.asarray(array).shape),'sha256':sha(p)})
 try:
  budget();rr,grids,attempts=agnum.rho_measure(g,M,f,archive,budget);row.update(rho0_grid=rr['rho'],time_rho0=rr['seconds']);increment_start=time.monotonic()
  for a in grids:data['rho_resolutions'].append({'state':sid,**a})
  for a in attempts:data['rho_attempts'].append({'state':sid,**a})
  F=Family(M,f,rr['rho']);original_u=np.array([np.cos(rr['theta']),np.sin(rr['theta'])]);v=F.B@original_u;theta=float(np.arctan2(v[1],v[0])%(2*np.pi));z=F.f@np.array([np.cos(theta),np.sin(theta)]);S=np.flatnonzero(max(z)-z<1e-11*max(1,np.ptp(z))) if rr['special'] else np.array([int(np.argmax(z))]);candidates,optimizers,ev=search(F,theta,S,budget,sinks)
  winner,base,validated=validate_candidates(F,candidates,budget,validated);row['baseline_MP']=base['MP_status'];null_ok=base['MP_status']=='PASS' and abs(base['segment'])<=1e-7*rr['rho'] and abs(base['length']-rr['rho'])/rr['rho']<=1e-7 and abs(base['length']-float(reference['rho']))/float(reference['rho'])<=1e-5
  row['baseline_control']='PASS' if null_ok else 'FAIL';row['rho0']=base['length'] if null_ok else None
  if winner is not None and null_ok and rr['status']=='PASS':
   value=winner['length'];Q=F.Binv@np.array(winner['q']);u=F.Binv@np.array([np.cos(winner['theta']),np.sin(winner['theta'])]);support=winner['support'];full_support=np.flatnonzero(np.isin(F.inverse,support));endpoint=np.zeros(len(F.index));endpoint[support]=winner['endpoint_group'];endpoint_full=F.E@endpoint
   row.update(status='PASS',rho1=value,rho1_over_true=value/row['d_border'] if row['d_border'] else None,rho1_over_rho0=value/row['rho0'],winner_candidate=winner['candidate'],q1=float(winner['q'][0]),q2=float(winner['q'][1]),Q1_P=float(Q[0]),Q2_P=float(Q[1]),u1_P=float(u[0]),u2_P=float(u[1]),support_original=json.dumps(full_support.tolist()),endpoint_original=json.dumps(endpoint_full.tolist()),numeric_relative_error=max(winner['MP_relative_error'],winner['quad_error']/value))
   # Nodos/perfiles de la curva concreta hasta U, con el resto explícito aparte.
   b,z,ss,cuts,tail=F.parameters(winner['q'],winner['theta'],support);x=b-F.c;times=np.linspace(0,1,65);p=times[:,None]*Q;a=softmax(F.c+times[:,None]*x,axis=1)@F.E.T;speed=F.speed(F.c+times[:,None]*x,x);seg=np.column_stack([np.zeros(len(times)),times,p,speed,a]);rates=np.unique(np.r_[cuts,np.concatenate([np.linspace(lo,hi,5) for lo,hi in zip(cuts[:-1],cuts[1:])])]);p=Q+rates[:,None]*u;a=softmax(b+rates[:,None]*z,axis=1)@F.E.T;speed=F.speed(b+rates[:,None]*z,z);ray=np.column_stack([np.ones(len(rates)),rates,p,speed,a]);archive('winner_profile',np.vstack([seg,ray]))
  else:row['reason']='BASELINE_OR_WITNESS_INVALID'
  row.update(time_incremental=time.monotonic()-increment_start,time_total=rr['seconds']+time.monotonic()-increment_start)
 except Exception as e:row['reason']+=';'+type(e).__name__+':'+str(e)
 # Los contenedores mutables preservan intentos aun ante excepción/presupuesto.
 data['candidates']=[{'state':sid,**c} for c in validated];data['optimizers']=[{'state':sid,**o} for o in sinks[2]];row['evaluations']=len(sinks[0]);row['optimizer_total']=len(sinks[2]);row['optimizer_converged']=sum(o['success'] for o in sinks[2]);data['states'].append(row)
 if sinks[0]:archive('fast_evaluations',np.asarray(sinks[0]))
 return data,{'state':sid,'seconds':time.monotonic()-start,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'blocked_T2_reads':ag.af.ACCESS['blocked']}

def main(out,arrays):
 if out.exists() or arrays.exists():raise FileExistsError('no sobrescribir versiones')
 out.mkdir(parents=True);arrays.mkdir(parents=True);start=time.monotonic();gm=geometry();states=inputs();(out/'inputs.json').write_bytes((REPO/CFG['inputs_path']).read_bytes());ctrl=controls(gm,states);table(out/'controls.csv',ctrl)
 if any(c['status']!='PASS' for c in ctrl):write(out/'summary.json',{'status':'INVALID','reason':'PRECONTROLS_FAILED'});raise RuntimeError('controles fallidos: conservar v1 y congelar nueva versión antes de corregir')
 references=rows(ROOT.parent/'AG/results/run_v1/states.csv');data={k:[] for k in ['states','arrays','rho_resolutions','rho_attempts','optimizers','candidates']};resources=[]
 def save():
  for name,a in data.items():flexible_table(out/(name+'.csv'),a)
  write(out/'resources.json',{'seconds':time.monotonic()-start,'workers':2,'arrays_root':str(arrays),'worker_resources':resources})
 with ProcessPoolExecutor(max_workers=2) as pool:
  tasks=[(s,r,str(arrays),start+CFG['total_seconds']) for s,r in zip(states,references)]
  for st,(tables,timing) in zip(states,pool.map(analyse,tasks,chunksize=1)):
   for k,a in tables.items():data[k].extend(a)
   resources.append(timing);save();r=tables['states'][0];print(st['id'],r['status'],r['rho1_over_true'],r['rho1_over_rho0'],r['reason'],flush=True)
 groups,summary=summarize(data['states']);nulls=[r['baseline_control'] for r in data['states']];valid_controls=all(x=='PASS' for x in nulls)
 summary.update(precontrols=len(ctrl),null_controls_pass=sum(x=='PASS' for x in nulls),null_controls_unknown=sum(x=='UNKNOWN' for x in nulls))
 if any(x=='FAIL' for x in nulls):summary.update(status='INVALID',**{f'Q{i}':'INCONCLUSIVE' for i in range(1,6)})
 table(out/'groups.csv',groups);write(out/'summary.json',summary);write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__,'geometry_sha256':CFG['geometry_sha256'],'audit_sha256':CFG['audit_sha256'],'code_sha256':{p.name:sha(p) for p in (ROOT/'scripts').glob('*.py')},'threads':1});save();print(json.dumps(summary),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'results/run_v1');ap.add_argument('--arrays',type=Path,default=Path(CFG['arrays_root']));a=ap.parse_args();main(a.out,a.arrays)
