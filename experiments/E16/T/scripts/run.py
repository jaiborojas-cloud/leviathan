#!/usr/bin/env python3
"""E16-T: diagnóstico local de segundo orden, sin optimización."""
import argparse,csv,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
import mpmath as mp
from autograd import hessian
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fmt(x):return mp.nstr(x,40)
def rel(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rows):
 if rows:
  with p.open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def canonical(v):
 v=np.asarray(v,float);v=v/np.linalg.norm(v)
 if v[np.argmax(abs(v))]<0:v=-v
 return v

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('kernel_t',ROOT.parent/'P/scripts/kernel.py');d=load('d_t',ROOT.parent/'D/scripts/run.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text())
 source=list(csv.DictReader((ROOT.parent/'S/results/run_v1/paths.csv').open()))
 vertices=list(csv.DictReader((ROOT.parent/'S/results/run_v1/vertices.csv').open()))
 gradients=list(csv.DictReader((ROOT.parent/'S/results/run_v1/gradients.csv').open()))
 checks=[];spectra=[];rays=[];paths=[];costs=[];timings=[]
 tables={'checks':checks,'spectra':spectra,'rayleigh':rays,'paths':paths,'costs':costs}
 def check(name,e,tol):
  ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(str(tol)));checks.append({'name':name,'error':fmt(e),'tolerance':str(tol),'status':'PASS' if ok else 'INCONCLUSIVE'});return ok
 def checkpoint():
  for n,rs in tables.items():table(out/(n+'.csv'),rs)
  elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
  dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib'],'timings':timings})
  if elapsed>CFG['budget_seconds'] or rss>CFG['memory_target_mib']:
   dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE','reason':'resource_budget','completed_paths':len(paths)});raise TimeoutError('budget; partial results retained')
 dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE'})
 prepared={}
 for digits in CFG['precision']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels']['P0']]
   cv,jc,c,l=d.analytic_mp(theta,zz)
   prepared[digits]={}
   for kind in ['quadratic','sum']:
    a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][0]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][1]])
    ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
    prepared[digits][kind]=(a,b,ux,uy)
 for old in source:
  name=old['path'];begin=time.monotonic();startcheck=len(checks);m=int(old['segments']);n=m-1;kind='sum' if old['lineage']=='C0' else 'quadratic'
  check(name+'/source_status',0 if old['status']=='PASS_NUMERICAL' else 1,0)
  rr=sorted([r for r in vertices if r['path']==name],key=lambda r:int(r['index']));z=np.array([[float(r['t']),float(r['s'])] for r in rr]);assert len(z)==m+1
  x=k.pack(z,'free');a,b,ux,uy=prepared[80][kind]
  obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float))
  gg=[r for r in gradients if r['path']==name+'/final'];assert len(gg)==len(x)
  gm=np.array([float(r['mp_fd_2']) for r in gg]);box=np.array([[0.,1.],[-.25,.25]]*n)
  physical=float(np.max(abs(x-np.clip(x-gm,box[:,0],box[:,1]))))/max(1,abs(float(old['length'])))
  check(name+'/archived_kkt_identity',abs(physical-float(old['physical_kkt'])),1e-12);check(name+'/source_kkt',physical,CFG['source_kkt_tolerance'])
  margin=float(np.min(np.minimum(x-box[:,0],box[:,1]-x)));interior=margin>CFG['bound_margin']
  chord=z[2:]-z[:-2];norm=np.linalg.norm(chord,axis=1)
  if np.any(norm<=CFG['frame_min_norm']):
   check(name+'/frame',1,0);paths.append({'path':name,'diagnostics':'INCONCLUSIVE','minimum_status':'UNKNOWN','reason':'undefined_frame'});checkpoint();continue
  tangent=chord/norm[:,None];normal=np.column_stack([-tangent[:,1],tangent[:,0]])
  T=np.zeros((2*n,n));N=np.zeros_like(T)
  for j in range(n):T[2*j:2*j+2,j]=tangent[j];N[2*j:2*j+2,j]=normal[j]
  check(name+'/orthonormal_frame',float(np.max(abs(np.column_stack([T,N]).T@np.column_stack([T,N])-np.eye(2*n)))),1e-12)
  raw=np.asarray(hessian(obj.value)(x),float);assert np.all(np.isfinite(raw))
  sym=float(np.max(abs(raw-raw.T)))/max(1,float(np.max(abs(raw))));check(name+'/hessian_symmetry',sym,CFG['symmetry_tolerance']);H=(raw+raw.T)/2
  blocks={'full':H,'tangent':T.T@H@T,'normal':N.T@H@N};eigen={};summary={}
  for label,h in blocks.items():
   vals,vec=np.linalg.eigh((h+h.T)/2);eigen[label]=(vals,vec)
   tau=CFG['spectral_relative_floor']*max(1,float(np.max(abs(vals))));neg=int(np.sum(vals< -tau));zero=int(np.sum(abs(vals)<=tau));pos=int(np.sum(vals>tau))
   classification='NEGATIVE_AT_THRESHOLD' if neg else ('NEAR_SINGULAR' if zero else 'POSITIVE_AT_THRESHOLD')
   summary[label]={'minimum':float(vals[0]),'maximum':float(vals[-1]),'threshold':tau,'negative':neg,'near_zero':zero,'positive':pos,'classification':classification}
   for j,v in enumerate(vals):spectra.append({'path':name,'block':label,'index':j,'eigenvalue':repr(float(v)),'threshold':repr(tau),'mode_class':'NEGATIVE' if v< -tau else ('NEAR_ZERO' if abs(v)<=tau else 'POSITIVE')})
  mixed=T.T@H@N;coupling=float(np.linalg.norm(mixed,'fro'))/max(1,float(np.linalg.norm(H,'fro')))
  tangent_part=float(np.linalg.norm(T.T@eigen['full'][1][:,0])**2)
  if kind=='sum':
   # Exact formula for the Hessian on the straight ordered C0 path.
   frame=np.column_stack([obj.v,obj.normal]);M=frame.T@(obj.ux@obj.ux.T)@frame
   dt=np.diff(z[:,0]);assert np.all(dt>0) and np.max(abs(z[:,1]))<1e-12
   weight=(M[1,1]-M[0,1]**2/M[0,0])/np.sqrt(M[0,0])/dt
   analytic=np.zeros_like(H)
   for edge,w in enumerate(weight):
    for node,sign in [(edge,-1),(edge+1,1)]:
     if 0<node<m:
      for other,sign2 in [(edge,-1),(edge+1,1)]:
       if 0<other<m:analytic[2*(node-1)+1,2*(other-1)+1]+=sign*sign2*w
   check(name+'/C0_analytic_hessian',float(np.max(abs(H-analytic)))/max(1,float(np.max(abs(analytic)))),CFG['analytic_control_tolerance'])
   check(name+'/C0_tangent_null',float(np.max(abs(T.T@H@T)))/max(1,float(np.max(abs(H)))),CFG['analytic_control_tolerance'])
  sine=np.sin(np.pi*np.arange(1,m)/m)
  directions={'full_min':eigen['full'][1][:,0],'tangent_min':T@eigen['tangent'][1][:,0],'normal_min':N@eigen['normal'][1][:,0],'tangent_sine':T@sine,'normal_sine':N@sine}
  localcalls=0;resolved={}
  for direction in CFG['directions']:
   v=canonical(directions[direction]);ray=float(v@H@v);digest=hashlib.sha256(json.dumps(v.tolist(),separators=(',',':')).encode()).hexdigest()
   feasible=all(np.all(x+float(h)*v>=box[:,0]) and np.all(x+float(h)*v<=box[:,1]) and np.all(x-float(h)*v>=box[:,0]) and np.all(x-float(h)*v<=box[:,1]) for h in CFG['fd_steps'])
   byprecision={}
   for digits in CFG['precision']:
    with mp.workdps(digits):
     a,b,ux,uy=prepared[digits][kind];pts=k.mp_points(a,b,z);length=k.reference(pts,kind,ux,uy);localcalls+=1
     check(name+'/'+direction+'/'+str(digits)+'/archived_length',rel(length,mp.mpf(old['length'])),CFG['archived_length_tolerance'])
     displacement=b-a;perp=mp.matrix([-displacement[1],displacement[0]])
     dp=[mp.mpf(float(v[2*j]))*displacement+mp.mpf(float(v[2*j+1]))*perp for j in range(n)]
     second=[]
     for step in CFG['fd_steps']:
      h=mp.mpf(step);plus=[pts[0]]+[p+h*q for p,q in zip(pts[1:-1],dp)]+[pts[-1]];minus=[pts[0]]+[p-h*q for p,q in zip(pts[1:-1],dp)]+[pts[-1]]
      second.append((k.reference(plus,kind,ux,uy)-2*length+k.reference(minus,kind,ux,uy))/(h*h));localcalls+=2
     aderror=rel(mp.mpf(ray),second[-1]);steperror=rel(*second)
     check(name+'/'+direction+'/'+str(digits)+'/AD_MP',aderror,CFG['direction_agreement_tolerance']);check(name+'/'+direction+'/'+str(digits)+'/steps',steperror,CFG['fd_agreement_tolerance'])
     byprecision[digits]=second
     rays.append({'path':name,'direction':direction,'precision':digits,'vector_sha256':digest,'feasible_bilateral':feasible,'ad_rayleigh':repr(ray),'mp_step_1':fmt(second[0]),'mp_step_2':fmt(second[1]),'ad_error':fmt(aderror),'step_error':fmt(steperror),'tangent_fraction':repr(float(np.linalg.norm(T.T@v)**2))})
   with mp.workdps(120):
    pe=max(rel(a,b) for a,b in zip(byprecision[80],byprecision[120]));check(name+'/'+direction+'/precision',pe,CFG['precision_agreement_tolerance'])
    label=direction.removesuffix('_min');resolved[direction]=bool(label in summary and ray< -summary[label]['threshold'] and byprecision[120][-1]< -summary[label]['threshold'] and feasible)
   checkpoint()
  good=all(q['status']=='PASS' for q in checks[startcheck:]);diag='PASS' if good else 'INCONCLUSIVE'
  curvature='NEGATIVE_CURVATURE_OBSERVED' if good and resolved['full_min'] else ('NO_NEGATIVE_AT_THRESHOLD' if good and summary['full']['negative']==0 else 'UNRESOLVED')
  paths.append({'path':name,'lineage':old['lineage'],'arm':old['arm'],'segments':m,'diagnostics':diag,'minimum_status':'UNKNOWN','curvature':curvature,'source_kkt':repr(physical),'box_margin':repr(margin),'interior_at_margin':interior,'full_min':repr(summary['full']['minimum']),'full_max':repr(summary['full']['maximum']),'full_threshold':repr(summary['full']['threshold']),'full_negative':summary['full']['negative'],'full_near_zero':summary['full']['near_zero'],'full_class':summary['full']['classification'],'tangent_min':repr(summary['tangent']['minimum']),'tangent_negative':summary['tangent']['negative'],'tangent_near_zero':summary['tangent']['near_zero'],'normal_min':repr(summary['normal']['minimum']),'normal_negative':summary['normal']['negative'],'normal_near_zero':summary['normal']['near_zero'],'coupling_frobenius_ratio':repr(coupling),'full_min_tangent_fraction':repr(tangent_part),'hessian_symmetry_error':repr(sym)})
  costs.append({'path':name,'AD_hessian_calls':1,'MP_full_length_calls':localcalls,'directions':len(directions),'precisions':len(CFG['precision']),'dense_arrays_archived':0})
  timings.append({'path':name,'seconds':time.monotonic()-begin});checkpoint();print(name,diag,curvature,summary['full'],flush=True)
 count=sum(p['diagnostics']=='PASS' for p in paths)
 dump(out/'provenance.json',{'design_commit':'e73e894','sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__})
 dump(out/'summary.json',{'status':'INCONCLUSIVE','question':'minimum_properties','diagnostics':'PASS' if count==12 and all(q['status']=='PASS' for q in checks) else 'INCONCLUSIVE','paths':len(paths),'validated_diagnostics':count,'checks':len(checks),'passed_checks':sum(q['status']=='PASS' for q in checks),'rayleigh_rows':len(rays),'spectral_rows':len(spectra),'resolved_negative_full':sum(p['curvature']=='NEGATIVE_CURVATURE_OBSERVED' for p in paths),'minimum_certificates':0})
 checkpoint();print(json.dumps(json.loads((out/'summary.json').read_text())),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(parser.parse_args().out)
