#!/usr/bin/env python3
"""E16-U: perturbaciones finitas prospectivas, sin optimización."""
import argparse,csv,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
import mpmath as mp
from autograd import hessian
ROOT=Path(__file__).resolve().parents[1];CFG=json.loads((ROOT/'config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rows(p):return list(csv.DictReader(p.open()))
def fmt(x):return mp.nstr(x,40)
def rel(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rs):
 if rs:
  with p.open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def distances(points,z):
 a=z[:-1];v=np.diff(z,axis=0);vv=np.sum(v*v,axis=1)
 if np.any(vv==0):raise ValueError('zero geometry edge')
 offset=points[:,None,:]-a[None,:,:];t=np.clip(np.sum(offset*v[None,:,:],axis=2)/vv[None,:],0,1)
 return np.sqrt(np.min(np.sum((offset-t[:,:,None]*v[None,:,:])**2,axis=2),axis=1))
def bounds(a,b):
 def samples(z):return np.vstack([z,(z[:-1]+z[1:])/2])
 lower=max(float(np.max(distances(samples(a),b))),float(np.max(distances(samples(b),a))))
 upper=float(np.max(np.linalg.norm(a-b,axis=1))) if len(a)==len(b) else None
 return lower,upper
def sign(value):
 tol=mp.mpf(CFG['length_sign_tolerance']);return 'DESCENT' if value< -tol else ('INCREASE' if value>tol else 'WITHIN_TOLERANCE')

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('kernel_u',ROOT.parent/'P/scripts/kernel.py');d=load('d_u',ROOT.parent/'D/scripts/run.py');g=load('g_u',ROOT.parent/'G/scripts/run.py');tmod=load('t_u',ROOT.parent/'T/scripts/run.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text());oldpaths=rows(ROOT.parent/'S/results/run_v1/paths.csv');oldv=rows(ROOT.parent/'S/results/run_v1/vertices.csv');oldg=rows(ROOT.parent/'S/results/run_v1/gradients.csv');oldr=rows(ROOT.parent/'T/results/run_v1/rayleigh.csv')
 checks=[];directions=[];trials=[];pairs=[];paths=[];costs=[];controls=[];timings=[]
 tables={'checks':checks,'directions':directions,'trials':trials,'pairs':pairs,'paths':paths,'costs':costs,'controls':controls}
 def check(name,e,tol):
  ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(str(tol)));checks.append({'name':name,'error':fmt(e),'tolerance':str(tol),'status':'PASS' if ok else 'INCONCLUSIVE'});return ok
 def checkpoint():
  for name,rs in tables.items():table(out/(name+'.csv'),rs)
  elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;within=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
  dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':within,'timings':timings})
  if not within:
   dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE','reason':'resource_budget','completed_paths':len(paths),'trials':len(trials)});raise TimeoutError('budget; partial results retained')
 dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE'})
 for name,a,b,expected in [('identity',np.array([[0.,0.],[1.,0.]]),np.array([[0.,0.],[1.,0.]]),0.),('straight_redistribution',np.array([[0.,0.],[.3,0.],[1.,0.]]),np.array([[0.,0.],[.7,0.],[1.,0.]]),0.),('translation',np.array([[0.,0.],[1.,0.]]),np.array([[0.,.125],[1.,.125]]),.125)]:
  lo,hi=bounds(a,b);error=abs(lo-expected);check('control/'+name,error,CFG['control_tolerance']);controls.append({'name':name,'lower':repr(lo),'correspondence_upper':repr(hi),'expected_Hausdorff':repr(expected),'error':repr(error)})
 prepared={}
 for digits in CFG['precision']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels']['P0']];cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]={}
   for kind in ['sum','quadratic']:
    a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][0]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][1]])
    ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l;prepared[digits][kind]=(a,b,ux,uy)
 for old in oldpaths:
  name=old['path'];begin=time.monotonic();checkstart=len(checks);trialstart=len(trials);pairstart=len(pairs);m=int(old['segments']);n=m-1;kind='sum' if old['lineage']=='C0' else 'quadratic';lengthcalls=0;spdedges=0
  rr=sorted([r for r in oldv if r['path']==name],key=lambda r:int(r['index']));z=np.array([[float(r['t']),float(r['s'])] for r in rr]);x=k.pack(z,'free')
  a,b,ux,uy=prepared[80][kind];obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float))
  chord=z[2:]-z[:-2];tangent=chord/np.linalg.norm(chord,axis=1)[:,None];normal=np.column_stack([-tangent[:,1],tangent[:,0]]);T=np.zeros((2*n,n));N=np.zeros_like(T)
  for j in range(n):T[2*j:2*j+2,j]=tangent[j];N[2*j:2*j+2,j]=normal[j]
  raw=np.asarray(hessian(obj.value)(x),float);H=(raw+raw.T)/2;blocks={'full':H,'tangent':T.T@H@T,'normal':N.T@H@N};eigen={label:np.linalg.eigh((h+h.T)/2) for label,h in blocks.items()};sine=np.sin(np.pi*np.arange(1,m)/m)
  vecs={'full_min':eigen['full'][1][:,0],'tangent_min':T@eigen['tangent'][1][:,0],'normal_min':N@eigen['normal'][1][:,0],'tangent_sine':T@sine,'normal_sine':N@sine}
  basemp={};basecoords={};basepoints={}
  for digits in CFG['precision']:
   with mp.workdps(digits):
    a,b,ux,uy=prepared[digits][kind];pts=k.mp_points(a,b,z);basemp[digits]=k.reference(pts,kind,ux,uy);lengthcalls+=1;basepoints[digits]=pts
    basecoords[digits]=[(mp.mpf(float(t)),mp.mpf(repr(float(s)))) for t,s in z]
    check(name+'/'+str(digits)+'/source_length',rel(basemp[digits],mp.mpf(old['length'])),CFG['source_length_tolerance'])
  gg=[r for r in oldg if r['path']==name+'/final'];assert len(gg)==len(x)
  for direction in CFG['directions']:
   v=tmod.canonical(vecs[direction]);digest=hashlib.sha256(json.dumps(v.tolist(),separators=(',',':')).encode()).hexdigest();reference=next(r for r in oldr if r['path']==name and r['direction']==direction and r['precision']=='120');same=digest==reference['vector_sha256'];check(name+'/'+direction+'/T_direction_hash',0 if same else 1,0)
   with mp.workdps(120):
    vm=[mp.mpf(float(q)) for q in v];slope=mp.fsum(mp.mpf(r['mp_fd_2'])*q for r,q in zip(gg,vm));ray=mp.mpf(reference['mp_step_2'])
   directions.append({'path':name,'direction':direction,'vector_sha256':digest,'T_hash_match':same,'slope_MP_archive':fmt(slope),'rayleigh_MP_archive':fmt(ray),'tangent_fraction':reference['tangent_fraction']})
   for step in CFG['steps']:
    pairdata={}
    for sg in CFG['signs']:
     result={'path':name,'direction':direction,'step':step,'sign':sg,'state':'UNKNOWN','reason':'','length':'','delta':'','length_change':'UNKNOWN','precision_error':'','spd':'','geometry_lower':'','geometry_upper':'','geometry_status':'UNKNOWN','geometry_rounding':'','linear_prediction':'','quadratic_prediction':'','taylor_residual':''}
     values={};status='VALID';reason='';geom=None
     for digits in CFG['precision']:
      with mp.workdps(digits):
       a,b,ux,uy=prepared[digits][kind];h=mp.mpf(step)*sg;coords=[basecoords[digits][0]]+[(p[0]+h*mp.mpf(float(v[2*j])),p[1]+h*mp.mpf(float(v[2*j+1]))) for j,p in enumerate(basecoords[digits][1:-1])]+[basecoords[digits][-1]]
       if not all(0<=q[0]<=1 and mp.mpf('-.25')<=q[1]<=mp.mpf('.25') for q in coords):status='INFEASIBLE';reason='box';break
       displacement=b-a;perp=mp.matrix([-displacement[1],displacement[0]]);pts=[a+q[0]*displacement+q[1]*perp for q in coords]
       try:
        lengthcalls+=1;values[digits]=k.reference(pts,kind,ux,uy)
        if digits==120:
         spd=True
         for u0,du,u,dd in k.mp_edges(pts,kind,ux,uy):
          pa,pd=g.positive([u0*u0.T,du*u0.T+u0*du.T,du*du.T]);spd=spd and bool(pa and pd);spdedges+=1
         check(name+'/'+direction+'/'+step+'/'+str(sg)+'/SPD',0 if spd else 1,0)
         if not spd:status='INCONCLUSIVE';reason='metric_positivity'
         zp=np.array([[float(q[0]),float(q[1])] for q in coords]);rounding=max(abs(mp.mpf(float(zp[j,axis]))-coords[j][axis]) for j in range(len(coords)) for axis in [0,1]);check(name+'/'+direction+'/'+step+'/'+str(sg)+'/geometry_rounding',rounding,CFG['geometry_rounding_limit'])
         lo,hi=bounds(z,zp);lo=max(0,lo-CFG['geometry_cushion']);hi+=CFG['geometry_cushion'];geom=(lo,hi,rounding)
         check(name+'/'+direction+'/'+step+'/'+str(sg)+'/geometry_bounds',max(0,lo-hi),CFG['control_tolerance'])
         result['spd']=spd
       except (ValueError,ZeroDivisionError) as e:status='INVALID';reason=type(e).__name__+':'+str(e);break
     with mp.workdps(120):
      if len(values)==2:
       pe=rel(values[80],values[120]);agree=check(name+'/'+direction+'/'+step+'/'+str(sg)+'/precision',pe,CFG['precision_tolerance']);status=status if agree else 'INCONCLUSIVE';scale=max(1,abs(basemp[120]));delta=(values[120]-basemp[120])/scale;linear=sg*mp.mpf(step)*slope/scale;quadratic=mp.mpf(step)**2*ray/(2*scale)
       result.update(length=fmt(values[120]),delta=fmt(delta),precision_error=fmt(pe),length_change=sign(delta) if status=='VALID' else 'UNKNOWN',linear_prediction=fmt(linear),quadratic_prediction=fmt(quadratic),taylor_residual=fmt(delta-linear-quadratic))
       if geom:
        lo,hi,rounding=geom;result.update(geometry_lower=repr(lo),geometry_upper=repr(hi),geometry_rounding=fmt(rounding),geometry_status='CHANGED' if lo>CFG['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=CFG['geometry_tolerance'] else 'UNRESOLVED'))
       pairdata[sg]=(delta,status)
     result.update(state=status,reason=reason);trials.append(result)
    pair={'path':name,'direction':direction,'step':step,'state':'INCOMPLETE','even_change':'','odd_change':'','even_sign':'UNKNOWN','odd_linear_residual':'','even_quadratic_residual':'','minus_change':'UNKNOWN','plus_change':'UNKNOWN'}
    with mp.workdps(120):
     if len(pairdata)==2 and all(vv[1]=='VALID' for vv in pairdata.values()):
      dm,dp=pairdata[-1][0],pairdata[1][0];even=(dm+dp)/2;odd=(dp-dm)/2;scale=max(1,abs(basemp[120]));pair.update(state='VALID',even_change=fmt(even),odd_change=fmt(odd),even_sign=sign(even),odd_linear_residual=fmt(odd-mp.mpf(step)*slope/scale),even_quadratic_residual=fmt(even-mp.mpf(step)**2*ray/(2*scale)),minus_change=sign(dm),plus_change=sign(dp))
    pairs.append(pair)
   checkpoint()
  own=trials[trialstart:];ownpairs=pairs[pairstart:];good=all(r['status']=='PASS' for r in checks[checkstart:]) and all(r['state'] in ['VALID','INFEASIBLE'] for r in own)
  paths.append({'path':name,'lineage':old['lineage'],'arm':old['arm'],'segments':m,'diagnostics':'PASS' if good else 'INCONCLUSIVE','minimum_status':'UNKNOWN','trials':len(own),'valid':sum(r['state']=='VALID' for r in own),'infeasible':sum(r['state']=='INFEASIBLE' for r in own),'descents':sum(r['length_change']=='DESCENT' for r in own),'changed_geometries':sum(r['geometry_status']=='CHANGED' for r in own),'full_min_negative_even_steps':sum(r['direction']=='full_min' and r['even_sign']=='DESCENT' for r in ownpairs)})
  costs.append({'path':name,'AD_hessian_calls':1,'MP_length_calls':lengthcalls,'MP120_SPD_edges':spdedges,'directions':5,'dense_arrays_archived':0});timings.append({'path':name,'seconds':time.monotonic()-begin});checkpoint();print(paths[-1],flush=True)
 dump(out/'provenance.json',{'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__})
 dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'PASS' if len(paths)==12 and all(r['diagnostics']=='PASS' for r in paths) and all(r['status']=='PASS' for r in checks) else 'INCONCLUSIVE','paths':len(paths),'directions':len(directions),'trials':len(trials),'pairs':len(pairs),'valid_trials':sum(r['state']=='VALID' for r in trials),'infeasible_trials':sum(r['state']=='INFEASIBLE' for r in trials),'invalid_trials':sum(r['state']=='INVALID' for r in trials),'descent_trials':sum(r['length_change']=='DESCENT' for r in trials),'changed_geometry_trials':sum(r['geometry_status']=='CHANGED' for r in trials),'unresolved_geometry_trials':sum(r['geometry_status']=='UNRESOLVED' for r in trials),'negative_even_pairs':sum(r['even_sign']=='DESCENT' for r in pairs),'checks':len(checks),'passed_checks':sum(r['status']=='PASS' for r in checks),'minimum_certificates':0});checkpoint();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(p.parse_args().out)
