#!/usr/bin/env python3
"""Integridad AF, protección de datos T2, archivos externos y reproducción."""
from common_v1 import *
from outcome_numerics_v1 import mp_rayleigh,normal_block
import subprocess,tempfile,ast
from scipy.stats import kendalltau
from scipy.linalg import eigvalsh

def primitive_check():
 # Compara segunda variación MP analítica con FD MP independiente en control n4.
 f=np.array([[.001,.001],[.001,-.001],[-.001,.001],[-.001,-.001]]);M=np.eye(4);points=np.column_stack([np.linspace(0,10,5),np.zeros(5)]);normals=np.column_stack([np.zeros(5),np.ones(5)]);q=np.array([.5,-.25,.75]);cur=mp_rayleigh(M,f,points,normals,q,16)
 with mp.workdps(80):
  ts,ws=mp.gauss_quadrature(16,'legendre');ff=mp.matrix([[mp.mpf(float(x)) for x in r] for r in f]);qq=[0]+list(q)+[0]
  def length(h):
   pp=[mp.matrix([mp.mpf(float(p[0])),h*mp.mpf(float(a))]) for p,a in zip(points,qq)];total=mp.mpf(0)
   for a,b in zip(pp[:-1],pp[1:]):
    v=b-a
    for t,w in zip(ts,ws):
     p=a+(t+1)*v/2;z=ff*p;weights=[mp.exp(z[i]-max(z)) for i in range(4)];ss=sum(weights);weights=[x/ss for x in weights];fv=ff*v;mean=sum(weights[i]*fv[i] for i in range(4));beta=[weights[i]*(fv[i]-mean) for i in range(4)];total+=w*mp.sqrt(sum(x*x for x in beta))/2
   return total
  h=mp.mpf('1e-6');fd=(length(h)+length(-h)-2*length(mp.mpf(0)))/h**2;error=abs(fd-cur)/max(1,abs(cur));assert error<mp.mpf('1e-15'),error
 H,_=normal_block(points,normals,M,f,16);assert abs(float(cur)-float(q@H@q))<1e-10
 # Comprobación de guarda sin abrir ningún archivo ni estado real.
 try:access_guard('open',(str(REPO/'experiments/T2_A/AF_FICTITIOUS_GUARD_TEST'),'r'))
 except PermissionError:pass
 else:raise AssertionError('guard')
 return float(error)

def main():
 for name in ['freeze_manifest.csv','implementation_stage1.csv','implementation_stage2.csv','manifest.csv']:
  for r in rows(ROOT/name):assert sha(ROOT/r['path'])==r['sha256'],r['path']
 for commit,names in [('46470bd',['DESIGN_FROZEN.md','config.json','THEORY.md','requirements.txt']),('1698ff8',['scripts/common_v1.py','scripts/stage1_v1.py']),('e798206',['results/stage1_v1/predictors.csv','results/stage1_v1/predictors_sha256.json']),('12cf59c',['scripts/outcome_numerics_v1.py','scripts/stage2_v1.py'])]:
  for name in names:assert subprocess.check_output(['git','show',commit+':experiments/E16/AF/'+name],cwd=REPO)==(ROOT/name).read_bytes()
 assert subprocess.check_output(['git','merge-base','--is-ancestor','e798206','12cf59c'],cwd=REPO)==b''
 changed=subprocess.check_output(['git','diff','--name-only',CFG['base_commit']],cwd=REPO).decode().splitlines();assert all(p.startswith('experiments/E16/AF/') for p in changed)
 gm,audit=imports();p1=ROOT/'results/stage1_v1';p2=ROOT/'results/stage2_v1';frozen=json.loads((p1/'predictors_sha256.json').read_text())
 for n,h in frozen.items():assert sha(p1/n)==h
 states=json.loads((p1/'synthetic_states.json').read_text());assert len(states['states'])==40 and len(states['bases'])==10;pred=rows(p1/'predictors.csv');assert len(pred)==40 and all(p['status']=='PASS' for p in pred)
 for T in CFG['curvature_targets']:
  pp=[p for p in pred if float(p['target'])==T];assert len(pp)==10 and max(abs(abs(float(p['K0']))-T)/T for p in pp)<1e-7
 # Invariancia de K0 al escalar sólo f: control geométrico sin geodésicas.
 b=states['bases'][0];f=np.array(b['f']);Q=np.array(b['Q']);M=Q@Q.T/27+CFG['base_epsilon']*np.eye(27);k1=float(gm.Geometry(M,f).eval([[0,0]])[1][0]);k2=float(gm.Geometry(M,2*f).eval([[0,0]])[1][0]);assert abs(k1-k2)/max(1,abs(k1))<1e-8
 ctrl=rows(p2/'controls.csv');assert len(ctrl)==20 and all(c['status']=='PASS' for c in ctrl);out=rows(p2/'outcomes.csv');assert len(out)==80 and all(len([r for r in out if r['state']==st['id']])==2 for st in states['states']);assert len(rows(p2/'ray_events.csv'))==40*(512+1024)
 arrays=rows(p2/'arrays.csv');res=json.loads((p2/'resources.json').read_text());array_root=Path(res['arrays_root'])
 for a in arrays:
  path=array_root/a['logical_file'];assert sha(path)==a['sha256'];x=np.load(path,allow_pickle=False,mmap_mode='r');assert x.shape==ast.literal_eval(a['shape']);assert np.all(x[:2,:,0]==0) and np.all(x[4,:,0]==0) and np.all(x[5,:,0]==1)
 for r in out:
  if r['status']=='INCONCLUSIVE_NUMERICAL':continue
  assert float(r['coverage'])<=CFG['R_max']+1e-12
  ev=[float(r[k]) for k in ['r_conj','r_col','r_esc'] if r[k]]
  if r['censored']=='True':assert not ev and not r['r_deg'] and not r['A_emb'] and r['type']=='CENSORED_RMAX'
  else:assert ev and float(r['r_deg'])==min(ev)
  if r['A_emb']:assert r['A_at_limit']==r['A64']==r['A_emb']
 mp_rows=rows(p2/'mp_events.csv');assert all(float(r['K_error'])<=CFG['mp_K_tolerance'] and float(r['density_error'])<=CFG['mp_K_tolerance'] for r in mp_rows if r['status']=='PASS')
 morse=rows(p2/'morse.csv');assert len(morse)==240 and all(len([r for r in morse if r['state']==st['id']])==6 for st in states['states'])
 if (p2/'normal_bands.csv').exists():
  bs=rows(p2/'normal_bands.csv');sp=rows(p2/'normal_spectra.csv')
  for case in {b['case'] for b in bs}:
   rr=[b for b in bs if b['case']==case];n=int(rr[0]['dimension']);H=np.zeros((n,n))
   for b in rr:H[int(b['row']),int(b['column'])]=float(b['value'])
   ev=eigvalsh(H);ss=[q for q in sp if q['case']==case];assert len(ev)==len(ss) and np.max(abs(ev-np.array([float(q['eigenvalue']) for q in ss])))/max(1,max(abs(ev)))<1e-9
 # Correlaciones a partir de tabla predictora cerrada, sin excluir desconocidos.
 corr=rows(p2/'correlations.csv')
 for n in CFG['rays']:
  ranks=[];known=True
  for p in pred:
   r=next(x for x in out if x['n']==str(n) and x['state']==p['state'])
   if r['status']=='INCONCLUSIVE_NUMERICAL' or r['MP_status']!='PASS':known=False;break
   ranks.append(CFG['R_max']+1 if r['censored']=='True' else float(r['r_deg']))
  if known:
   for field in ['abs_K0','max_abs_K_small','X_max']:
    tau=kendalltau([float(p[field]) for p in pred],ranks).statistic;s=next(q for q in corr if int(q['n'])==n and q['predictor']==field)
    if np.isfinite(tau):assert abs(tau-float(s['tau_b']))<1e-12
 summary=json.loads((p2/'summary.json').read_text());assert summary['states']==40 and summary['controls_pass']==20 and summary['blocked_prohibited_reads_parent']==summary['blocked_prohibited_reads_workers']==0
 assessed=rows(p2/'state_assessments.csv');unknown_a=sum(r['area_answer']=='?' for r in assessed);unknown_r=sum(r['radius_answer']=='?' for r in assessed);assert summary['area_unknown']==unknown_a and summary['radius_unknown']==unknown_r;assert summary['Q4']==('PASS' if unknown_r<unknown_a else 'FAIL')
 error=primitive_check();print('PASS_ARCHIVES: controles, predictores anteriores, arrays, eventos, bloques y correlaciones; MP_primitive_error',error,flush=True)
 with tempfile.TemporaryDirectory(prefix='e16af-') as tmp:
  dest=Path(tmp);env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');a=dest/'stage1';b=dest/'stage2';arr=dest/'arrays';subprocess.run([sys.executable,str(ROOT/'scripts/stage1_v1.py'),'--out',str(a)],env=env,check=True)
  for q in p1.iterdir():
   if q.name!='resources.json':assert q.read_bytes()==(a/q.name).read_bytes(),q.name
  subprocess.run([sys.executable,str(ROOT/'scripts/stage2_v1.py'),'--out',str(b),'--arrays',str(arr),'--workers','2'],env=env,check=True,timeout=CFG['budget_seconds'])
  for q in p2.iterdir():
   if q.name!='resources.json':assert q.read_bytes()==(b/q.name).read_bytes(),q.name
  print('PASS_REPRODUCTION',{'stage1':json.loads((a/'resources.json').read_text()),'stage2':json.loads((b/'resources.json').read_text()),'external_array_hashes':len(arrays)},flush=True)
if __name__=='__main__':main()
