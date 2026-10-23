#!/usr/bin/env python3
"""E16-V: transporte de perturbaciones y nodos insertados fijos."""
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
def classify(x):
 t=mp.mpf(CFG['sign_tolerance']);return 'DESCENT' if x< -t else ('INCREASE' if x>t else 'WITHIN_TOLERANCE')
def refine(coords,alpha):
 out=[]
 for p,q in zip(coords[:-1],coords[1:]):out.extend([p,tuple((1-alpha)*a+alpha*b for a,b in zip(p,q))])
 return out+[coords[-1]]
def alpha_of(family):return mp.mpf('.5') if family.endswith('half') else mp.mpf('.25')
def representation(original,perturbed,family):
 if family=='original':return perturbed
 alpha=alpha_of(family)
 if family.startswith('transported'):return refine(perturbed,alpha)
 out=refine(original,alpha);out[::2]=perturbed;return out

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('k_v',ROOT.parent/'P/scripts/kernel.py');d=load('d_v',ROOT.parent/'D/scripts/run.py');g=load('g_v',ROOT.parent/'G/scripts/run.py');tmod=load('t_v',ROOT.parent/'T/scripts/run.py');u=load('u_v',ROOT.parent/'U/scripts/run.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text());sources=rows(ROOT.parent/'S/results/run_v1/paths.csv');vertices=rows(ROOT.parent/'S/results/run_v1/vertices.csv');trows=rows(ROOT.parent/'T/results/run_v1/rayleigh.csv');utrials=rows(ROOT.parent/'U/results/run_v1/trials.csv')
 checks=[];directions=[];trials=[];pairs=[];comparisons=[];paths=[];costs=[];timings=[]
 tables={'checks':checks,'directions':directions,'trials':trials,'pairs':pairs,'comparisons':comparisons,'paths':paths,'costs':costs}
 def check(name,e,tol):
  ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(str(tol)));checks.append({'name':name,'error':fmt(e),'tolerance':str(tol),'status':'PASS' if ok else 'INCONCLUSIVE'});return ok
 def checkpoint():
  for n,rs in tables.items():table(out/(n+'.csv'),rs)
  elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;within=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib'];dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':within,'timings':timings})
  if not within:
   dump(out/'summary.json',{'status':'INCONCLUSIVE','diagnostics':'INCOMPLETE','reason':'resource_budget','paths':len(paths),'trials':len(trials)});raise TimeoutError('budget; partial results retained')
 dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'INCOMPLETE'})
 prepared={}
 for digits in CFG['precision']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels']['P0']];cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]={}
   for kind in ['sum','quadratic']:
    a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][0]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][1]])
    ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l;prepared[digits][kind]=(a,b,ux,uy)
 for old in sources:
  begin=time.monotonic();name=old['path'];m=int(old['segments']);n=m-1;kind='sum' if old['lineage']=='C0' else 'quadratic';startchecks=len(checks);starttrials=len(trials);startpairs=len(pairs);lengthcalls=0;spdedges=0
  rr=sorted([r for r in vertices if r['path']==name],key=lambda r:int(r['index']));z=np.array([[float(r['t']),float(r['s'])] for r in rr]);a,b,ux,uy=prepared[80][kind];obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float))
  raw=np.asarray(hessian(obj.value)(k.pack(z,'free')),float);H=(raw+raw.T)/2;_,vec=np.linalg.eigh(H);v=tmod.canonical(vec[:,0]);digest=hashlib.sha256(json.dumps(v.tolist(),separators=(',',':')).encode()).hexdigest();oldray=next(r for r in trows if r['path']==name and r['direction']=='full_min' and r['precision']=='120');check(name+'/direction_hash',0 if digest==oldray['vector_sha256'] else 1,0)
  basecoords={};baseL={};refbaseL={}
  for digits in CFG['precision']:
   with mp.workdps(digits):
    a,b,ux,uy=prepared[digits][kind];base=[(mp.mpf(float(t)),mp.mpf(repr(float(s)))) for t,s in z];basecoords[digits]=base;vv=b-a;nn=mp.matrix([-vv[1],vv[0]])
    def points(coords):return [a+q[0]*vv+q[1]*nn for q in coords]
    baseL[digits]=k.reference(points(base),kind,ux,uy);lengthcalls+=1;check(name+'/'+str(digits)+'/source_length',rel(baseL[digits],mp.mpf(old['length'])),CFG['identity_tolerance'])
    for alpha in CFG['fractions']:
     refined=refine(base,mp.mpf(alpha));val=k.reference(points(refined),kind,ux,uy);lengthcalls+=1;refbaseL[(digits,alpha)]=val;check(name+'/'+str(digits)+'/base_subdivision_'+alpha,rel(val,baseL[digits]),CFG['identity_tolerance'])
  for family in CFG['families']:
   with mp.workdps(120):
    field=[(mp.mpf(0),mp.mpf(0))]+[(mp.mpf(float(v[2*j])),mp.mpf(float(v[2*j+1]))) for j in range(n)]+[(mp.mpf(0),mp.mpf(0))]
    vf=representation([(mp.mpf(0),mp.mpf(0))]*len(field),field,family);norm=mp.sqrt(mp.fsum(q*q for p in vf for q in p))
    directions.append({'path':name,'family':family,'segments':m if family=='original' else 2*m,'original_vector_sha256':digest,'displacement_norm':fmt(norm),'original_vertex_amplitude_scale':'1'})
  originals={};pairvalues={}
  for family in CFG['families']:
   for step in CFG['steps']:
    signed={}
    for sg in CFG['signs']:
     row={'path':name,'family':family,'segments':m if family=='original' else 2*m,'step':step,'sign':sg,'state':'UNKNOWN','reason':'','length':'','delta':'','length_change':'UNKNOWN','precision_error':'','spd':'','geometry_lower':'','geometry_upper':'','geometry_status':'UNKNOWN','vs_transport_lower':'','vs_transport_upper':'','vs_transport_status':'UNKNOWN','projection_error':''};values={};state='VALID';reason=''
     for digits in CFG['precision']:
      with mp.workdps(digits):
       a,b,ux,uy=prepared[digits][kind];base=basecoords[digits];h=sg*mp.mpf(step);pert=[base[0]]+[(q[0]+h*mp.mpf(float(v[2*j])),q[1]+h*mp.mpf(float(v[2*j+1]))) for j,q in enumerate(base[1:-1])]+[base[-1]];coords=representation(base,pert,family)
       if not all(0<=q[0]<=1 and mp.mpf('-.25')<=q[1]<=mp.mpf('.25') for q in coords):state='INFEASIBLE';reason='box';break
       vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);pts=[a+q[0]*vv+q[1]*nn for q in coords]
       try:
        lengthcalls+=1;values[digits]=k.reference(pts,kind,ux,uy)
        if family.startswith('transported'):
         expected=refine(pert,alpha_of(family));error=max(abs(a-b) for p,q in zip(coords,expected) for a,b in zip(p,q));check(name+'/'+family+'/'+step+'/'+str(sg)+'/'+str(digits)+'/affine_points',error,CFG['identity_tolerance'])
        if digits==120:
         spd=True
         for u0,du,uu,dd in k.mp_edges(pts,kind,ux,uy):
          pa,pd=g.positive([u0*u0.T,du*u0.T+u0*du.T,du*du.T]);spd=spd and bool(pa and pd);spdedges+=1
         check(name+'/'+family+'/'+step+'/'+str(sg)+'/SPD',0 if spd else 1,0);row['spd']=spd
         if not spd:state='INCONCLUSIVE';reason='metric_positivity'
         base_rep=base if family=='original' else refine(base,alpha_of(family));transport=pert if family=='original' else refine(pert,alpha_of(family))
         projected=[np.array([[float(a),float(b)] for a,b in cc]) for cc in [coords,base_rep,transport]];error=max(abs(mp.mpf(float(arr[j,axis]))-cc[j][axis]) for arr,cc in zip(projected,[coords,base_rep,transport]) for j in range(len(cc)) for axis in [0,1]);check(name+'/'+family+'/'+step+'/'+str(sg)+'/projection',error,CFG['rounding_tolerance']);row['projection_error']=fmt(error)
         for prefix,other in [('',projected[1]),('vs_transport_',projected[2])]:
          lo,hi=u.bounds(projected[0],other);lo=max(0,lo-CFG['geometry_cushion']);hi+=CFG['geometry_cushion'];status='CHANGED' if lo>CFG['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=CFG['geometry_tolerance'] else 'UNRESOLVED');key='geometry_' if not prefix else prefix;row.update({key+'lower':repr(lo),key+'upper':repr(hi),key+'status':status});check(name+'/'+family+'/'+step+'/'+str(sg)+'/'+key+'bounds',max(0,lo-hi),1e-12)
       except (ValueError,ZeroDivisionError) as e:state='INVALID';reason=type(e).__name__+':'+str(e);break
     with mp.workdps(120):
      if len(values)==2:
       pe=rel(values[80],values[120]);agree=check(name+'/'+family+'/'+step+'/'+str(sg)+'/precision',pe,CFG['precision_tolerance']);state=state if agree else 'INCONCLUSIVE';delta=(values[120]-baseL[120])/max(1,abs(baseL[120]));row.update(length=fmt(values[120]),delta=fmt(delta),length_change=classify(delta) if state=='VALID' else 'UNKNOWN',precision_error=fmt(pe));signed[sg]=(delta,state)
       if family=='original':originals[(step,sg)]=values[120]
       elif family.startswith('transported'):check(name+'/'+family+'/'+step+'/'+str(sg)+'/length_transport',rel(values[120],originals[(step,sg)]),CFG['identity_tolerance'])
     if family=='original':
      archived=next(r for r in utrials if r['path']==name and r['direction']=='full_min' and r['step']==step and r['sign']==str(sg));check(name+'/'+step+'/'+str(sg)+'/U_state',0 if archived['state']==state else 1,0)
      if row['length']:
       with mp.workdps(120):check(name+'/'+step+'/'+str(sg)+'/U_length',rel(mp.mpf(row['length']),mp.mpf(archived['length'])),CFG['identity_tolerance']);check(name+'/'+step+'/'+str(sg)+'/U_delta',abs(mp.mpf(row['delta'])-mp.mpf(archived['delta'])),CFG['identity_tolerance'])
     row.update(state=state,reason=reason);trials.append(row);checkpoint()
    pair={'path':name,'family':family,'step':step,'state':'INCOMPLETE','even_change':'','odd_change':'','even_sign':'UNKNOWN','vs_original_sign':'UNRESOLVED'}
    with mp.workdps(120):
     if len(signed)==2 and all(q[1]=='VALID' for q in signed.values()):
      dm,dp=signed[-1][0],signed[1][0];even=(dm+dp)/2;odd=(dp-dm)/2;tag=classify(even);pairvalues[(family,step)]=(even,tag);originaltag=pairvalues[('original',step)][1];pair.update(state='VALID',even_change=fmt(even),odd_change=fmt(odd),even_sign=tag,vs_original_sign='SAME' if tag==originaltag else 'CHANGED')
    pairs.append(pair)
  with mp.workdps(120):
   for suffix in ['half','quarter']:
    for step in CFG['steps']:
     p=pairvalues.get(('pinned_'+suffix,step));t=pairvalues.get(('transported_'+suffix,step));comparisons.append({'path':name,'fraction':'.5' if suffix=='half' else '.25','step':step,'state':'VALID' if p and t else 'INCOMPLETE','pinned_even':fmt(p[0]) if p else '', 'transported_even':fmt(t[0]) if t else '', 'difference':fmt(p[0]-t[0]) if p and t else '', 'sign_comparison':'SAME' if p and t and p[1]==t[1] else ('CHANGED' if p and t else 'UNRESOLVED')})
  own=trials[starttrials:];pp=pairs[startpairs:];good=all(r['status']=='PASS' for r in checks[startchecks:]) and all(r['state'] in ['VALID','INFEASIBLE'] for r in own);paths.append({'path':name,'lineage':old['lineage'],'arm':old['arm'],'source_segments':m,'refined_segments':2*m,'diagnostics':'PASS' if good else 'INCONCLUSIVE','minimum_status':'UNKNOWN','trials':len(own),'valid_trials':sum(r['state']=='VALID' for r in own),'infeasible_trials':sum(r['state']=='INFEASIBLE' for r in own),'negative_original_pairs':sum(r['family']=='original' and r['even_sign']=='DESCENT' for r in pp),'negative_transported_pairs':sum(r['family'].startswith('transported') and r['even_sign']=='DESCENT' for r in pp),'negative_pinned_pairs':sum(r['family'].startswith('pinned') and r['even_sign']=='DESCENT' for r in pp)});costs.append({'path':name,'AD_hessian_calls':1,'MP_length_calls':lengthcalls,'MP120_SPD_edges':spdedges,'dense_arrays_archived':0});timings.append({'path':name,'seconds':time.monotonic()-begin});checkpoint();print(paths[-1],flush=True)
 dump(out/'provenance.json',{'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__})
 dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'PASS' if len(paths)==12 and all(r['diagnostics']=='PASS' for r in paths) else 'INCONCLUSIVE','paths':len(paths),'directions':len(directions),'trials':len(trials),'pairs':len(pairs),'comparisons':len(comparisons),'valid_trials':sum(r['state']=='VALID' for r in trials),'infeasible_trials':sum(r['state']=='INFEASIBLE' for r in trials),'invalid_trials':sum(r['state']=='INVALID' for r in trials),'checks':len(checks),'passed_checks':sum(r['status']=='PASS' for r in checks),'minimum_certificates':0});checkpoint();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(p.parse_args().out)
