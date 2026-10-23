#!/usr/bin/env python3
"""E16-W: proyección direccional y contraste de primer orden."""
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
def dot(a,b):return mp.fsum(x*y for x,y in zip(a,b))
def norm(v):return mp.sqrt(dot(v,v))
def classify(x):
 t=mp.mpf(CFG['sign_tolerance']);return 'DESCENT' if x< -t else ('INCREASE' if x>t else 'WITHIN_TOLERANCE')
def projection(v,g):
 gn=norm(g)
 if gn<=mp.mpf(CFG['gradient_floor']):q=v.copy();route='SMALL_GRADIENT'
 else:
  coefficient=dot(g,v)/dot(g,g);q=[a-coefficient*b for a,b in zip(v,g)];route='PROJECTED'
 size=norm(q)
 if size<=mp.mpf(CFG['projection_norm_floor']):return None,'DEGENERATE',size
 w=[qj/size for qj in q];j=max(range(len(w)),key=lambda i:abs(w[i]))
 if w[j]<0:w=[-a for a in w]
 return w,route,size

def main(out):
 started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
 k=load('k_w',ROOT.parent/'P/scripts/kernel.py');d=load('d_w',ROOT.parent/'D/scripts/run.py');gmod=load('g_w',ROOT.parent/'G/scripts/run.py');tmod=load('t_w',ROOT.parent/'T/scripts/run.py');u=load('u_w',ROOT.parent/'U/scripts/run.py')
 data=json.loads((ROOT.parent/'H/data.json').read_text());sources=rows(ROOT.parent/'S/results/run_v1/paths.csv');vertices=rows(ROOT.parent/'S/results/run_v1/vertices.csv');gradients=rows(ROOT.parent/'S/results/run_v1/gradients.csv');trows=rows(ROOT.parent/'T/results/run_v1/rayleigh.csv');utrials=rows(ROOT.parent/'U/results/run_v1/trials.csv')
 checks=[];directions=[];audits=[];trials=[];pairs=[];paths=[];costs=[];timings=[];tables={'checks':checks,'directions':directions,'audits':audits,'trials':trials,'pairs':pairs,'paths':paths,'costs':costs}
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
  begin=time.monotonic();name=old['path'];m=int(old['segments']);n=m-1;kind='sum' if old['lineage']=='C0' else 'quadratic';cs=len(checks);ts=len(trials);ps=len(pairs);lengthcalls=0;spdedges=0
  rr=sorted([r for r in vertices if r['path']==name],key=lambda r:int(r['index']));z=np.array([[float(r['t']),float(r['s'])] for r in rr]);a,b,ux,uy=prepared[80][kind];obj=k.Objective(np.array(a,float).ravel(),np.array(b,float).ravel(),'free',z[:,0],kind,np.array(ux.tolist(),float),np.array(uy.tolist(),float));raw=np.asarray(hessian(obj.value)(k.pack(z,'free')),float);H=(raw+raw.T)/2;_,vec=np.linalg.eigh(H);vf=tmod.canonical(vec[:,0]);digest=hashlib.sha256(json.dumps(vf.tolist(),separators=(',',':')).encode()).hexdigest();oldray=next(r for r in trows if r['path']==name and r['direction']=='full_min' and r['precision']=='120');check(name+'/T_hash',0 if digest==oldray['vector_sha256'] else 1,0)
  gg=[r for r in gradients if r['path']==name+'/final'];assert len(gg)==len(vf);vectors={};basepoints={};basecoords={};baseL={};predictions={};routes={}
  for digits in CFG['precision']:
   with mp.workdps(digits):
    v=[mp.mpf(float(q)) for q in vf];gm=[mp.mpf(r['mp_fd_2']) for r in gg];w,route,qn=projection(v,gm);routes[digits]=route;vectors[(digits,'original')]=v;vectors[(digits,'projected')]=w
    a,b,ux,uy=prepared[digits][kind];basecoords[digits]=[(mp.mpf(float(t)),mp.mpf(repr(float(s)))) for t,s in z];basepoints[digits]=k.mp_points(a,b,z);baseL[digits]=k.reference(basepoints[digits],kind,ux,uy);lengthcalls+=1;check(name+'/'+str(digits)+'/source_length',rel(baseL[digits],mp.mpf(old['length'])),CFG['identity_tolerance'])
    for family in CFG['families']:
     q=vectors[(digits,family)]
     if q is None:
      directions.append({'path':name,'family':family,'precision':digits,'route':'DEGENERATE','source_vector_sha256':digest,'vector_mp_sha256':'','gradient_norm':fmt(norm(gm)),'pre_normalization_norm':fmt(qn),'unit_norm':'','archive_slope':'','orthogonality_error':'','absolute_cosine':'','ad_rayleigh':''});continue
     slope=dot(gm,q);orth=abs(slope)/max(1,norm(gm));ray=float(np.array([float(a) for a in q])@H@np.array([float(a) for a in q]));dh=hashlib.sha256(json.dumps([fmt(a) for a in q],separators=(',',':')).encode()).hexdigest();directions.append({'path':name,'family':family,'precision':digits,'route':route if family=='projected' else 'SOURCE','source_vector_sha256':digest,'vector_mp_sha256':dh,'gradient_norm':fmt(norm(gm)),'pre_normalization_norm':fmt(qn if family=='projected' else norm(v)),'unit_norm':fmt(norm(q)),'archive_slope':fmt(slope),'orthogonality_error':fmt(orth),'absolute_cosine':fmt(abs(dot(v,q))/(norm(v)*norm(q))),'ad_rayleigh':repr(ray)})
     if family=='projected':check(name+'/'+str(digits)+'/unit_norm',abs(norm(q)-1),CFG['orthogonality_tolerance']);check(name+'/'+str(digits)+'/orthogonality',orth,CFG['orthogonality_tolerance'])
     vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);dp=[q[2*j]*vv+q[2*j+1]*nn for j in range(n)];derivatives=[];curvatures=[]
     for step in CFG['audit_steps']:
      h=mp.mpf(step);plus=[basepoints[digits][0]]+[p+h*dq for p,dq in zip(basepoints[digits][1:-1],dp)]+[basepoints[digits][-1]];minus=[basepoints[digits][0]]+[p-h*dq for p,dq in zip(basepoints[digits][1:-1],dp)]+[basepoints[digits][-1]];lp=k.reference(plus,kind,ux,uy);lm=k.reference(minus,kind,ux,uy);lengthcalls+=2;derivatives.append((lp-lm)/(2*h));curvatures.append((lp+lm-2*baseL[digits])/(h*h))
     ge=rel(slope,derivatives[-1]);gs=rel(*derivatives);re=rel(mp.mpf(ray),curvatures[-1]);rs=rel(*curvatures);prefix=name+'/'+family+'/'+str(digits);check(prefix+'/gradient',ge,CFG['gradient_agreement_tolerance']);check(prefix+'/gradient_steps',gs,CFG['gradient_steps_tolerance']);check(prefix+'/rayleigh',re,CFG['rayleigh_agreement_tolerance']);check(prefix+'/rayleigh_steps',rs,CFG['rayleigh_steps_tolerance'])
     if family=='projected':check(prefix+'/small_directional_slope',abs(derivatives[-1])/max(1,abs(baseL[digits])),CFG['directional_slope_tolerance'])
     audits.append({'path':name,'family':family,'precision':digits,'derivative_1':fmt(derivatives[0]),'derivative_2':fmt(derivatives[1]),'curvature_1':fmt(curvatures[0]),'curvature_2':fmt(curvatures[1]),'gradient_error':fmt(ge),'gradient_steps_error':fmt(gs),'rayleigh_error':fmt(re),'rayleigh_steps_error':fmt(rs)});predictions[(digits,family)]=(derivatives[-1],curvatures[-1])
  with mp.workdps(120):
   for family in CFG['families']:
    if vectors[(80,family)] is not None and vectors[(120,family)] is not None:
     check(name+'/'+family+'/vector_precision',max(abs(a-b) for a,b in zip(vectors[(80,family)],vectors[(120,family)])),CFG['direction_precision_tolerance']);check(name+'/'+family+'/derivative_precision',rel(predictions[(80,family)][0],predictions[(120,family)][0]),CFG['precision_tolerance']);check(name+'/'+family+'/curvature_precision',rel(predictions[(80,family)][1],predictions[(120,family)][1]),CFG['precision_tolerance'])
  for family in CFG['families']:
   for step in CFG['steps']:
    signed={}
    for sg in CFG['signs']:
     row={'path':name,'family':family,'step':step,'sign':sg,'state':'UNKNOWN','reason':'','length':'','delta':'','length_change':'UNKNOWN','precision_error':'','spd':'','geometry_lower':'','geometry_upper':'','geometry_status':'UNKNOWN','projection_error':'','linear_prediction':'','quadratic_prediction':'','taylor_residual':''};values={};state='VALID';reason=''
     for digits in CFG['precision']:
      with mp.workdps(digits):
       q=vectors[(digits,family)]
       if q is None:state='DEGENERATE';reason='projection_norm';break
       h=sg*mp.mpf(step);base=basecoords[digits];coords=[base[0]]+[(p[0]+h*q[2*j],p[1]+h*q[2*j+1]) for j,p in enumerate(base[1:-1])]+[base[-1]]
       if not all(0<=p[0]<=1 and mp.mpf('-.25')<=p[1]<=mp.mpf('.25') for p in coords):state='INFEASIBLE';reason='box';break
       a,b,ux,uy=prepared[digits][kind];vv=b-a;nn=mp.matrix([-vv[1],vv[0]]);pts=[a+p[0]*vv+p[1]*nn for p in coords]
       try:
        lengthcalls+=1;values[digits]=k.reference(pts,kind,ux,uy)
        if digits==120:
         spd=True
         for u0,du,uu,dd in k.mp_edges(pts,kind,ux,uy):pa,pd=gmod.positive([u0*u0.T,du*u0.T+u0*du.T,du*du.T]);spd=spd and bool(pa and pd);spdedges+=1
         check(name+'/'+family+'/'+step+'/'+str(sg)+'/SPD',0 if spd else 1,0);row['spd']=spd
         if not spd:state='INCONCLUSIVE';reason='metric_positivity'
         zz=np.array([[float(a),float(b)] for a,b in coords]);error=max(abs(mp.mpf(float(zz[j,axis]))-coords[j][axis]) for j in range(len(coords)) for axis in [0,1]);check(name+'/'+family+'/'+step+'/'+str(sg)+'/projection',error,CFG['projection_rounding_tolerance']);lo,hi=u.bounds(z,zz);lo=max(0,lo-CFG['geometry_cushion']);hi+=CFG['geometry_cushion'];row.update(geometry_lower=repr(lo),geometry_upper=repr(hi),geometry_status='CHANGED' if lo>CFG['geometry_tolerance'] else ('WITHIN_TOLERANCE' if hi<=CFG['geometry_tolerance'] else 'UNRESOLVED'),projection_error=fmt(error));check(name+'/'+family+'/'+step+'/'+str(sg)+'/bounds',max(0,lo-hi),1e-12)
       except (ValueError,ZeroDivisionError) as e:state='INVALID';reason=type(e).__name__+':'+str(e);break
     with mp.workdps(120):
      if len(values)==2:
       pe=rel(values[80],values[120]);agree=check(name+'/'+family+'/'+step+'/'+str(sg)+'/precision',pe,CFG['precision_tolerance']);state=state if agree else 'INCONCLUSIVE';scale=max(1,abs(baseL[120]));delta=(values[120]-baseL[120])/scale;slope,ray=predictions[(120,family)];linear=sg*mp.mpf(step)*slope/scale;quadratic=mp.mpf(step)**2*ray/(2*scale);row.update(length=fmt(values[120]),delta=fmt(delta),length_change=classify(delta) if state=='VALID' else 'UNKNOWN',precision_error=fmt(pe),linear_prediction=fmt(linear),quadratic_prediction=fmt(quadratic),taylor_residual=fmt(delta-linear-quadratic));signed[sg]=(delta,state)
     if family=='original':
      oldtrial=next(r for r in utrials if r['path']==name and r['direction']=='full_min' and r['step']==step and r['sign']==str(sg));check(name+'/'+step+'/'+str(sg)+'/U_state',0 if state==oldtrial['state'] else 1,0)
      if row['length']:
       with mp.workdps(120):check(name+'/'+step+'/'+str(sg)+'/U_length',rel(mp.mpf(row['length']),mp.mpf(oldtrial['length'])),CFG['identity_tolerance']);check(name+'/'+step+'/'+str(sg)+'/U_delta',abs(mp.mpf(row['delta'])-mp.mpf(oldtrial['delta'])),CFG['identity_tolerance'])
     row.update(state=state,reason=reason);trials.append(row)
    pair={'path':name,'family':family,'step':step,'state':'INCOMPLETE','even_change':'','odd_change':'','even_sign':'UNKNOWN','minus_change':'UNKNOWN','plus_change':'UNKNOWN','descent_count':'','even_quadratic_residual':'','odd_linear_residual':''}
    with mp.workdps(120):
     if len(signed)==2 and all(q[1]=='VALID' for q in signed.values()):
      dm,dp=signed[-1][0],signed[1][0];even=(dm+dp)/2;odd=(dp-dm)/2;scale=max(1,abs(baseL[120]));slope,ray=predictions[(120,family)];pair.update(state='VALID',even_change=fmt(even),odd_change=fmt(odd),even_sign=classify(even),minus_change=classify(dm),plus_change=classify(dp),descent_count=int(classify(dm)=='DESCENT')+int(classify(dp)=='DESCENT'),even_quadratic_residual=fmt(even-mp.mpf(step)**2*ray/(2*scale)),odd_linear_residual=fmt(odd-mp.mpf(step)*slope/scale))
    pairs.append(pair)
   checkpoint()
  own=trials[ts:];pp=pairs[ps:];good=all(r['status']=='PASS' for r in checks[cs:]) and all(r['state'] in ['VALID','INFEASIBLE'] for r in own);paths.append({'path':name,'lineage':old['lineage'],'arm':old['arm'],'segments':m,'route':routes[120],'diagnostics':'PASS' if good else 'INCONCLUSIVE','minimum_status':'UNKNOWN','valid_trials':sum(r['state']=='VALID' for r in own),'infeasible_trials':sum(r['state']=='INFEASIBLE' for r in own),'projected_negative_even_pairs':sum(r['family']=='projected' and r['even_sign']=='DESCENT' for r in pp),'projected_both_descend_pairs':sum(r['family']=='projected' and r['descent_count']==2 for r in pp)});costs.append({'path':name,'AD_hessian_calls':1,'MP_length_calls':lengthcalls,'MP120_SPD_edges':spdedges,'dense_arrays_archived':0});timings.append({'path':name,'seconds':time.monotonic()-begin});checkpoint();print(paths[-1],flush=True)
 dump(out/'provenance.json',{'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'run_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'numpy':np.__version__,'mpmath':mp.__version__});dump(out/'summary.json',{'status':'EXPLORATORY','diagnostics':'PASS' if len(paths)==12 and all(r['diagnostics']=='PASS' for r in paths) else 'INCONCLUSIVE','paths':len(paths),'directions':len(directions),'audits':len(audits),'trials':len(trials),'pairs':len(pairs),'valid_trials':sum(r['state']=='VALID' for r in trials),'infeasible_trials':sum(r['state']=='INFEASIBLE' for r in trials),'invalid_trials':sum(r['state']=='INVALID' for r in trials),'checks':len(checks),'passed_checks':sum(r['status']=='PASS' for r in checks),'minimum_certificates':0});checkpoint();print((out/'summary.json').read_text(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/run_v1');main(p.parse_args().out)
