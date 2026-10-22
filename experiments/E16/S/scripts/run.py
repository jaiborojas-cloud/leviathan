#!/usr/bin/env python3
"""E16-S: parada física auditada, sin cambiar longitud."""
import argparse
import csv
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
from autograd import grad
import mpmath as mp
import numpy as np
import autograd.numpy as anp
import scipy
from scipy.optimize import minimize

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fmt(x):return mp.nstr(x,40)
def err(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rows):
    if not rows:return
    with p.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def archived_reference(value,text):
    """Distancia al intervalo de redondeo de una referencia de 40 cifras."""
    center=mp.mpf(text)
    if center==0:raise ValueError('archived positive length required')
    quantum=mp.mpf(10)**(Decimal(text).adjusted()+1-40)
    radius=quantum/2
    distance=max(mp.mpf(0),abs(value-center)-radius)/max(1,abs(value),abs(center))
    return distance,center,quantum,radius

def main(out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
    assert sha(ROOT/'groups.json')==CFG['groups_sha256']
    stopping=load('stopping_s',ROOT/'scripts/stopping.py');k=load('kernel_r',ROOT.parent/'P/scripts/kernel.py');geo=load('geo_r',ROOT.parent/'P/scripts/geometry.py')
    d=load('d_r',ROOT.parent/'D/scripts/run.py');g=load('g_r',ROOT.parent/'G/scripts/run.py');hd=load('hd_r',ROOT.parent/'N/scripts/hausdorff.py')
    groups=json.loads((ROOT/'groups.json').read_text())['groups'];data=json.loads((ROOT.parent/'H/data.json').read_text())
    oldv=list(csv.DictReader((ROOT.parent/'Q/results/run_v2/vertices.csv').open()));oldp=list(csv.DictReader((ROOT.parent/'Q/results/run_v2/paths.csv').open()))
    checks=[];paths=[];vertices=[];gradients=[];segments=[];references=[];refinements=[];comparisons=[];controls=[];cases=[];costs=[];audits=[];historical=[];caches=[];saved={};timings={'optimization':[],'monitor':[]}
    tables={'checks':checks,'paths':paths,'vertices':vertices,'gradients':gradients,'segments':segments,'source_references':references,'refinements':refinements,'comparisons':comparisons,'controls':controls,'cases':cases,'audits':audits,'historical':historical,'cached_preconditioners':caches,'costs':costs}
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(tol));checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rows in tables.items():table(out/(name+'.csv'),rows)
        if time.monotonic()-started>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_cases':len(cases)});raise TimeoutError('time budget; partial evidence preserved')
    for row in hd.controls():controls.append({'name':'hausdorff_'+row['name'],'value':repr(row['lower']),'reference':repr(row['expected']),'error':repr(max(0,row['lower']-row['expected'],row['expected']-row['upper']))})
    matrix=np.array([[4.,1.],[1.,2.]]);control_x=np.array([.375,-.125]);control_d=np.array([.25,8.]);control_y=control_x/control_d;box=np.array([[0.,1.],[-.25,.25]])
    control_fun=lambda y:anp.dot(y*control_d,anp.dot(matrix,y*control_d))/2
    expected_grad=control_d*(matrix@control_x)
    for name,e in [('coordinate',float(np.max(abs(control_d*control_y-control_x)))),('bounds',float(np.max(abs((box/control_d[:,None])*control_d[:,None]-box)))),('objective',abs(float(control_fun(control_y))-.5*float(control_x@matrix@control_x))),('chain_rule',float(np.max(abs(np.asarray(grad(control_fun)(control_y))-expected_grad))))]:
        check('control/scaling_'+name,e,CFG['control_tolerance']);controls.append({'name':'scaling_'+name,'value':repr(e),'reference':'0','error':repr(e)})
    acontrol=np.array([[0.,0.],[.3,0.],[1.,0.]]);bcontrol=np.array([[0.,0.],[.1,0.],[.9,0.],[1.,0.]])
    check('control/arc_redistribution',float(np.max(abs(geo.resample(acontrol,257)-geo.resample(bcontrol,257)))),CFG['control_tolerance'])
    with mp.workdps(80):
        ux=mp.eye(2);uy=mp.matrix([[0,mp.mpf('.3')],[mp.mpf('.7'),0]])
        for name,pts in [('vertical',[mp.matrix([1,1]),mp.matrix([1,2])]),('general',[mp.matrix([1,1]),mp.matrix([2,1])])]:
            val=k.reference(pts,'quadratic',ux,uy)
            for suffix,other in [('reversal',k.reference(list(reversed(pts)),'quadratic',ux,uy)),('subdivision',k.reference([pts[0],(pts[0]+pts[1])/2,pts[1]],'quadratic',ux,uy))]:
                e=err(val,other);check('control/'+name+'/'+suffix,e,CFG['precision_tolerance']);controls.append({'name':name+'_'+suffix,'value':fmt(val),'reference':fmt(other),'error':fmt(e)})
    assert stopping.controls()
    control_seen=[]
    weights=np.array([1.,2.,3.,7.,11.]);control_initial=np.array([.8,-.3,.6,-.7,.5])
    def control_callback(xx):
        control_seen.append(np.asarray(xx,float).copy())
        if len(control_seen)==2:raise StopIteration
    control_result=minimize(lambda xx:.5*float(np.sum(weights*xx*xx)),control_initial,jac=lambda xx:weights*xx,bounds=[(-1.,1.)]*5,method='L-BFGS-B',callback=control_callback,options={'maxiter':10,'ftol':0.,'gtol':1e-14})
    for suffix,error in [('status',0 if control_result.status==99 and not control_result.success else 1),('count',abs(len(control_seen)-2)),('state',float(np.max(abs(control_result.x-control_seen[-1]))))]:
        check('control/callback_'+suffix,error,CFG['control_tolerance']);controls.append({'name':'callback_'+suffix,'value':repr(error),'reference':'0','error':repr(error)})
    prepared={};rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):
            theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels'][CFG['panel']]]
            cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]=(cv,jc,l);rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    def setup(kind,ia,ib,digits):
        cv,jc,l=prepared[digits];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
        a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        return a,b,ux,uy
    def gradient_check(name,z,arm,obj,kind,ia,ib,rows,meter=None):
        x=k.pack(z,arm);gad=np.asarray(grad(obj.value)(x),float);fd0=[];fd1=[]
        with mp.workdps(80):
            a,b,ux,uy=setup(kind,ia,ib,80);pts=k.mp_points(a,b,z);v=b-a;normal=mp.matrix([-v[1],v[0]])
            if meter is not None:meter['global']+=1
            value=k.reference(pts,kind,ux,uy);scale=max(1,abs(value))
            variables=[(j,axis) for j in range(1,len(z)-1) for axis in ([1] if arm=='fixed' else [0,1])]
            for n,(j,axis) in enumerate(variables):
                direction=v if axis==0 else normal;fd=[]
                for step in CFG['mp_fd_steps']:
                    step=mp.mpf(step);plus=pts[j]+step*direction;minus=pts[j]-step*direction
                    if meter is not None:meter['local']+=1
                    vp=k.reference([pts[j-1],plus,pts[j+1]],kind,ux,uy)
                    if meter is not None:meter['local']+=1
                    vm=k.reference([pts[j-1],minus,pts[j+1]],kind,ux,uy)
                    fd.append((vp-vm)/(2*step))
                fd0.append(fd[0]);fd1.append(fd[1]);rows.append({'path':name,'index':j,'coordinate':'t' if axis==0 else 's','autograd':repr(float(gad[n])),'mp_fd_1':fmt(fd[0]),'mp_fd_2':fmt(fd[1])})
            aderr=max(abs(mp.mpf(float(x))-y) for x,y in zip(gad,fd1))/scale;fderr=max(abs(x-y) for x,y in zip(fd0,fd1))/scale
            check(name+'/gradient_ad',aderr,CFG['gradient_agreement_tolerance'],'gradient');check(name+'/gradient_steps',fderr,CFG['mp_fd_agreement_tolerance'],'gradient')
            gm=np.array([float(x) for x in fd1]);bounds=np.array([CFG['s_bounds']]*(len(z)-2) if arm=='fixed' else [bb for j in range(len(z)-2) for bb in [CFG['t_bounds'],CFG['s_bounds']]],float)
            residual=np.abs(x-np.clip(x-gm,bounds[:,0],bounds[:,1]))/float(scale)
            return {'value':value,'ad_error':aderr,'fd_error':fderr,'kkt':float(np.max(residual)),'longitudinal_gradient':float(max(abs(gm[::2]))/float(scale)) if arm=='free' else None,
                'transverse_gradient':float(np.max(abs(gm[1::2] if arm=='free' else gm)))/float(scale)}
    def validate(name,z,kind,ia,ib):
        totals={};low={};valid=True;all_spd=True
        for digits in CFG['precision']:
            with mp.workdps(digits):
                a,b,ux,uy=setup(kind,ia,ib,digits);pts=k.mp_points(a,b,z);total=mp.mpf(0)
                for j,(u0,du,u,dd) in enumerate(k.mp_edges(pts,kind,ux,uy)):
                    h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h)
                    q=[mp.fsum(x*x for x in u),2*mp.fsum(x*y for x,y in zip(u,dd)),mp.fsum(x*x for x in dd)]
                    prefix=f'{name}/{digits}/{j}';reason=''
                    try:
                        value=g.primitive(q);geometry=g.geometry(q);qs=[g.quadrature(q,geometry,rules[digits][n]) for n in [16,32,64]]
                        check(prefix+'/coarse',err(qs[0],qs[1]),CFG['coarse_tolerance'],'integration')
                        check(prefix+'/fine',err(qs[1],qs[2]),CFG['fine_tolerance'],'integration')
                        check(prefix+'/primitive',err(value,qs[2]),CFG['fine_tolerance'],'integration')
                        check(prefix+'/reparam',err(value,g.quadrature(q,geometry,rules[digits][64],True)),CFG['fine_tolerance'],'integration');total+=value
                    except (ValueError,ZeroDivisionError) as ex:value=None;valid=False;reason=str(ex)
                    spd=pa['ok'] and pd['ok'];all_spd=all_spd and spd;check(prefix+'/spd',0 if spd else 1,0,'positivity')
                    segments.append({'path':name,'digits':digits,'index':j,'length':fmt(value) if value is not None else '',
                        'reason':reason,'h00_positive':pa['ok'],'det_positive':pd['ok'],'h00_margin':fmt(pa['margin']),'det_margin':fmt(pd['margin']),'h00_depth':pa['depth'],'det_depth':pd['depth']})
                    if digits==80:low[j]=(value,pa['margin'],pd['margin'])
                    else:
                        prior=low[j]
                        if value is not None and prior[0] is not None:check(prefix+'/precision_length',err(value,prior[0]),CFG['precision_tolerance'],'precision')
                        check(prefix+'/precision_h00',err(pa['margin'],prior[1]),CFG['precision_tolerance'],'precision')
                        check(prefix+'/precision_det',err(pd['margin'],prior[2]),CFG['precision_tolerance'],'precision')
                totals[digits]=total
                check(f'{name}/{digits}/reference',err(total,k.reference(pts,kind,ux,uy)),CFG['precision_tolerance'],'precision')
        return totals[120],valid and all_spd,all_spd
    def compare(name,a,b,la,lb,kind):
        try:lo,hi,n,arc=geo.compare(a,b,hd,CFG);ok=True
        except ValueError:lo=hi=arc=float('inf');n=0;ok=False
        with mp.workdps(120):le=err(la,lb) if la is not None and lb is not None else mp.inf
        return {'comparison':name,'type':kind,'length_difference':fmt(le),'hausdorff_lower':repr(lo),'hausdorff_upper':repr(hi),'hausdorff_gap':repr(hi-lo) if ok else '',
            'hausdorff_splits':n,'arc_sampled_difference':repr(arc),'diagnosis':'NUMERICAL_AGREEMENT' if le<=mp.mpf(CFG['group_length_tolerance']) and hi<=float(CFG['hausdorff_tolerance']) else ('DIFFERENT_CANDIDATES' if ok else 'INCONCLUSIVE')}
    def point_hash(z):return hashlib.sha256(json.dumps(np.asarray(z,float).tolist(),separators=(',',':'),allow_nan=False).encode()).hexdigest()
    rconfig=json.loads((ROOT.parent/'R/config.json').read_text())
    for key in ['optimizer','segments','t_bounds','s_bounds','gradient_tolerance']:
        assert CFG[key]==rconfig[key],key
    for p in ['Q/results/run_v2/vertices.csv','Q/results/run_v2/paths.csv','P/scripts/kernel.py']:
        assert CFG['sources'][p]==rconfig['sources'][p],p
    cached_rows=list(csv.DictReader((ROOT.parent/'R/results/run_v1/scales.csv').open()));cache={}
    rpaths=list(csv.DictReader((ROOT.parent/'R/results/run_v1/paths.csv').open()));rverts=list(csv.DictReader((ROOT.parent/'R/results/run_v1/vertices.csv').open()))
    for group in groups:
        lin=group['lineage']
        for m in CFG['segments']:
            rr=[z for z in cached_rows if z['reference']==f'{lin}/{m}'];assert len(rr)==2*(m-1)
            dd=np.array([float(z['scale']) for z in rr]);assert np.all(np.isfinite(dd)) and np.all(dd>0) and np.all(np.frexp(dd)[0]==.5)
            cache[(lin,m)]=dd;caches.append({'reference':f'{lin}/{m}','dimension':len(dd),'min_scale':repr(float(np.min(dd))),'max_scale':repr(float(np.max(dd))),
                'scale_sha256':hashlib.sha256(json.dumps(dd.tolist(),separators=(',',':')).encode()).hexdigest(),'new_hessian_calls':0})
    for group in groups:
        lin=group['lineage'];case=group['case'];state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)]
        source=next(z for z in oldp if z['lineage']==lin and z['arm']=='length' and z['segments']=='132')
        rr=sorted([z for z in oldv if z['lineage']==lin and z['arm']=='length' and z['segments']=='132'],key=lambda z:int(z['index']))
        base=np.array([[float(z['t']),float(z['s'])] for z in rr]);assert len(base)==133
        with mp.workdps(80):
            a,b,ux,uy=setup(kind,ia,ib,80);original=k.reference(k.mp_points(a,b,base),kind,ux,uy);e,center,quantum,radius=archived_reference(original,source['length'])
            check(lin+'/source_reference',e,CFG['precision_tolerance'],'precision');references.append({'lineage':lin,'source_status':source['status'],'archived_length':source['length'],'computed_length_90digits':mp.nstr(original,90),'rounding_radius':fmt(radius),'interval_error':fmt(e)})
        with mp.workdps(120):a,b,ux,uy=setup(kind,ia,ib,120);uxf=np.array(ux.tolist(),float);uyf=np.array(uy.tolist(),float)
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
        for arm in CFG['arms']:
            case_begin=len(checks);previous=None;previous_value=None;previous_status=None
            for m in CFG['segments']:
                name=f'{lin}/{arm}/{m}';begin=len(checks);initial=base.copy() if previous is None else k.subdivide(previous)
                obj=k.Objective(af,bf,'free',initial[:,0],kind,uxf,uyf);x0=k.pack(initial,'free');physical_bounds=np.array([bb for j in range(m-1) for bb in [CFG['t_bounds'],CFG['s_bounds']]],float)
                scale=np.ones_like(x0) if arm=='reference' else cache[(lin,m)];y0=x0/scale;bounds_y=physical_bounds/scale[:,None]
                check(name+'/initial_roundtrip',float(np.max(abs(y0*scale-x0))),CFG['coordinate_identity_tolerance']);check(name+'/bounds_roundtrip',float(np.max(abs(bounds_y*scale[:,None]-physical_bounds))),CFG['coordinate_identity_tolerance'])
                physical_grad=grad(obj.value);solver_fun=lambda yy:obj.fun(scale*yy);solver_grad=lambda yy:scale*np.asarray(physical_grad(scale*yy),float);composite=lambda yy:obj.value(scale*yy)
                check(name+'/initial_objective',abs(float(composite(y0))-float(obj.value(x0)))/max(1,abs(float(obj.value(x0)))),CFG['solver_identity_tolerance'])
                check(name+'/initial_chain_rule',float(np.max(abs(np.asarray(grad(composite)(y0))-solver_grad(y0))))/max(1,float(np.max(abs(solver_grad(y0))))),CFG['chain_rule_tolerance'])
                with mp.workdps(80):
                    a,b,ux,uy=setup(kind,ia,ib,80)
                    try:inherited=k.reference(k.mp_points(a,b,initial),kind,ux,uy)
                    except (ValueError,ZeroDivisionError):inherited=None
                    if previous is not None and inherited is not None and previous_value is not None:check(name+'/embedding',err(inherited,previous_value),CFG['embedding_tolerance'])
                rule=stopping.SustainedRule(CFG['monitor_interval'],CFG['monitor_required_successes'],float(CFG['gradient_tolerance']))
                monitor={'callbacks':0,'audit_count':0,'unverified':0,'stop_hash':'','total_seconds':0.,'callback_seconds':0.,'mp_local':0,'mp_global':0}
                def audit(yy,iteration):
                    ta=time.monotonic();zz=np.asarray(k.coords(scale*np.asarray(yy,float),'free',initial[:,0]),float);audit_begin=len(checks);di0=None;reason='';meter={'local':0,'global':0}
                    try:
                        di0=gradient_check(name+f'/monitor/{iteration}',zz,'free',obj,kind,ia,ib,[],meter)
                        verified=bool(all(q['status']=='PASS' for q in checks[audit_begin:]) and np.isfinite(di0['kkt']))
                    except (ValueError,ZeroDivisionError,TypeError) as ex:
                        verified=False;reason=type(ex).__name__+': '+str(ex);check(name+f'/monitor/{iteration}/evaluable',1,0,'monitor')
                    monitor['audit_count']+=1;monitor['unverified']+=int(not verified);monitor['mp_local']+=meter['local'];monitor['mp_global']+=meter['global']
                    residual=di0['kkt'] if di0 is not None else float('inf');state='UNVERIFIED' if not verified else ('STATIONARY' if residual<=float(CFG['gradient_tolerance']) else 'NONSTATIONARY')
                    requested=rule.observe(iteration,verified,residual);digest=point_hash(zz)
                    if requested:monitor['stop_hash']=digest
                    audits.append({'path':name,'audit_number':monitor['audit_count'],'iteration':iteration,'initial':iteration==0,'state':state,'verified':verified,
                        'physical_kkt':repr(float(residual)),'length':fmt(di0['value']) if di0 is not None else '',
                        'gradient_error':fmt(di0['ad_error']) if di0 is not None else '', 'fd_consistency':fmt(di0['fd_error']) if di0 is not None else '',
                        'streak':rule.streak,'stop_requested':requested,'point_sha256':digest,'MP_local_reference_calls':meter['local'],'MP_global_reference_calls':meter['global'],'reason':reason})
                    table(out/'audits.csv',audits);table(out/'checks.csv',checks)
                    seconds=time.monotonic()-ta;monitor['total_seconds']+=seconds
                    if iteration>0:monitor['callback_seconds']+=seconds
                    timings['monitor'].append({'path':name,'iteration':iteration,'seconds':seconds})
                    if time.monotonic()-started>CFG['budget_seconds']:checkpoint()
                    return requested
                audit(y0,0)
                def monitor_callback(yy):
                    monitor['callbacks']+=1
                    if monitor['callbacks']%CFG['monitor_interval']==0 and audit(yy,monitor['callbacks']):raise StopIteration
                ts=time.monotonic()
                if inherited is None:
                    yy=y0;z=initial;native_success=False;native_status=-1;message='invalid_parent_geometry';nit=nfev=njev=0;solver_value=None
                else:
                    opt=minimize(solver_fun,y0,jac=solver_grad,bounds=[tuple(z) for z in bounds_y],method=CFG['optimizer']['method'],options={kk:vv for kk,vv in CFG['optimizer'].items() if kk!='method'},callback=monitor_callback)
                    yy=np.asarray(opt.x,float);z=np.asarray(k.coords(scale*yy,'free',initial[:,0]),float);native_success=bool(opt.success);native_status=int(opt.status);message=str(opt.message);nit=int(opt.nit);nfev=int(opt.nfev);njev=int(opt.njev);solver_value=float(opt.fun)
                opt_seconds=time.monotonic()-ts;timings['optimization'].append({'path':name,'solver_total_seconds_including_callback':opt_seconds,'monitor_total_seconds_including_initial':monitor['total_seconds'],'callback_audit_seconds':monitor['callback_seconds'],'solver_seconds_excluding_callback_audits':max(0.,opt_seconds-monitor['callback_seconds']),'new_preparation_seconds':0.})
                check(name+'/callback_iteration_count',abs(nit-monitor['callbacks']),0)
                digest=point_hash(z)
                if rule.requested:
                    route='PHYSICAL_SUSTAINED';accepted_termination=True
                    check(name+'/callback_native_status',0 if native_status==99 and not native_success else 1,0)
                    check(name+'/stop_state_identity',0 if digest==monitor['stop_hash'] else 1,0)
                    check(name+'/stop_iteration_identity',abs(nit-rule.stop_iteration),0)
                elif native_success and CFG['native_success_route']:
                    route='NATIVE_CONTROL' if kind=='sum' else 'NATIVE_VERIFIED';accepted_termination=True
                else:route='UNVERIFIED_TERMINATION';accepted_termination=False
                value=None;spd=False;di=None;reason='';valid=False;solver_kkt=None
                try:
                    di=gradient_check(name+'/final',z,'free',obj,kind,ia,ib,gradients);check(name+'/final_physical_kkt',di['kkt'],CFG['gradient_tolerance'],'stationarity')
                    value,valid,spd=validate(name,z,kind,ia,ib)
                    with mp.workdps(120):
                        physical_value=mp.mpf(float(obj.value(k.pack(z,'free'))));check(name+'/physical_objective',err(value,physical_value),CFG['objective_tolerance'],'integration')
                        if solver_value is not None:check(name+'/solver_objective',err(value,mp.mpf(solver_value)),CFG['objective_tolerance'],'integration')
                        check(name+'/nonworse',max(0,value-inherited)/max(1,inherited),CFG['nonworse_tolerance'],'optimization')
                        if kind=='sum':
                            a,b,ux,uy=setup(kind,ia,ib,120);straight=mp.sqrt(((b-a).T*(ux*ux.T)*(b-a))[0]);check(name+'/sum_length',err(value,straight),CFG['control_length_tolerance'],'control');check(name+'/sum_normal',float(np.max(abs(z[:,1]))),CFG['control_normal_tolerance'],'control')
                    gg=solver_grad(yy);solver_kkt=float(np.max(abs(yy-np.clip(yy-gg,bounds_y[:,0],bounds_y[:,1]))))/max(1,abs(float(obj.value(k.pack(z,'free')))))
                    actual=np.asarray(grad(composite)(yy),float);check(name+'/final_chain_rule',float(np.max(abs(actual-gg)))/max(1,float(np.max(abs(actual)))),CFG['chain_rule_tolerance'])
                    check(name+'/final_roundtrip',float(np.max(abs(k.pack(z,'free')/scale-yy))),CFG['coordinate_identity_tolerance'])
                except (ValueError,ZeroDivisionError,TypeError) as ex:reason=type(ex).__name__+': '+str(ex);check(name+'/evaluable',1,0,'integration');valid=False
                check(name+'/valid_geometry',0 if valid else 1,0,'integration');check(name+'/accepted_termination',0 if accepted_termination else 1,0,'termination');check(name+'/all_audits_verified',monitor['unverified'],0,'monitor')
                check(name+'/bounds',max(0.,float(np.max(-z[:,0])),float(np.max(z[:,0]-1)),float(np.max(abs(z[:,1])-.25))),CFG['identity_tolerance']);check(name+'/endpoints',float(np.max(abs(z[[0,-1]]-np.array([[0.,0.],[1.,0.]])))),CFG['identity_tolerance'])
                local=checks[begin:];status='FAIL' if any(q['status']=='FAIL' for q in local) else ('PASS_NUMERICAL' if valid and all(q['status']=='PASS' for q in local) else 'INCONCLUSIVE')
                desc=geo.descriptors(z,base if m==132 else k.subdivide(base),CFG)
                paths.append({'path':name,'lineage':lin,'arm':arm,'segments':m,'status':status,'termination_route':route,'native_success':native_success,'native_status':native_status,'native_message':message,'reason':reason,'iterations':nit,'nfev':nfev,'njev':njev,
                    'length':fmt(value) if value is not None else '', 'physical_kkt':repr(di['kkt']) if di else '', 'solver_kkt':repr(solver_kkt) if solver_kkt is not None else '',
                    'gradient_error':fmt(di['ad_error']) if di else '', 'fd_consistency':fmt(di['fd_error']) if di else '', 'spd':spd,'monitor_audits':monitor['audit_count'],'unverified_audits':monitor['unverified'],'final_streak':rule.streak,'callback_calls':monitor['callbacks'],'final_point_sha256':digest,
                    'rejected_zero_edges':obj.rejections['zero_edge'],'rejected_invalid_primitive':obj.rejections['invalid_primitive'],**desc})
                costs.append({'path':name,'iterations':nit,'solver_function_evaluations':nfev,'solver_gradient_evaluations':njev,'monitor_full_gradients':monitor['audit_count'],
                    'monitor_AD_gradient_evaluations':monitor['audit_count'],'monitor_MP_local_reference_calls':monitor['mp_local'],'monitor_MP_global_reference_calls':monitor['mp_global'],'new_hessian_calls':0})
                for j,(t,s) in enumerate(z):vertices.append({'path':name,'lineage':lin,'arm':arm,'segments':m,'index':j,'u':repr(j/m),'t':repr(float(t)),'s':repr(float(s))})
                saved[(lin,arm,m)]=(z.copy(),value,status)
                if previous is not None:
                    tb=len(checks);row=compare(f'{lin}_{arm}_132_264',previous,z,previous_value,value,'refinement');check(row['comparison']+'/length',mp.mpf(row['length_difference']),CFG['length_refinement_tolerance'],'refinement');check(row['comparison']+'/hausdorff',float(row['hausdorff_upper']),CFG['hausdorff_tolerance'],'refinement');check(row['comparison']+'/hausdorff_gap',float(row['hausdorff_gap']) if row['hausdorff_gap'] else mp.inf,CFG['hausdorff_gap'],'refinement')
                    row['status']='PASS_NUMERICAL' if all(q['status']=='PASS' for q in checks[tb:]) and status==previous_status=='PASS_NUMERICAL' else 'INCONCLUSIVE';refinements.append(row)
                previous=z.copy();previous_value=value;previous_status=status;checkpoint()
            local=checks[case_begin:];status='FAIL' if any(z['status']=='FAIL' for z in local) else ('PASS_NUMERICAL' if all(z['status']=='PASS' for z in local) else 'INCONCLUSIVE');cases.append({'lineage':lin,'arm':arm,'status':status});checkpoint()
        for m in CFG['segments']:
            za,la,_=saved[(lin,'reference',m)];zb,lb,_=saved[(lin,'scaled',m)];comparisons.append(compare(f'{lin}_reference_scaled_{m}',za,zb,la,lb,'between_methods'))
    for arm in CFG['arms']:
        for m in CFG['segments']:
            za,la,_=saved[('Q0',arm,m)];zb,lb,_=saved[('Q1',arm,m)];comparisons.append(compare(f'Q0_Q1_{arm}_{m}',za,zb,la,lb,'between_lineages'))
    for path in paths:
        lin=path['lineage'];arm=path['arm'];m=int(path['segments']);old=next(z for z in rpaths if z['path']==path['path']);rr=sorted([z for z in rverts if z['path']==old['path']],key=lambda z:int(z['index']));zz=np.array([[float(z['t']),float(z['s'])] for z in rr]);new,value,_=saved[(lin,arm,m)]
        with mp.workdps(120):archived_length=mp.mpf(old['length'])
        row=compare(path['path']+'_R_S',zz,new,archived_length,value,'historical_R')
        historical.append({**row,'R_status':old['status'],'R_success':old['success'],'R_iterations':old['iterations'],'R_nfev':old['nfev'],'R_physical_kkt':old['physical_kkt'],
            'S_status':path['status'],'S_route':path['termination_route'],'S_native_success':path['native_success'],'S_iterations':path['iterations'],'S_nfev':path['nfev'],'S_physical_kkt':path['physical_kkt']})
    checkpoint();counts={st:sum(z['status']==st for z in cases) for st in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']};cc={st:sum(z['status']==st for z in checks) for st in ['PASS','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if cc['FAIL'] or counts['FAIL'] else ('INCONCLUSIVE' if cc['INCONCLUSIVE'] or counts['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'cases':len(cases),'counts':counts,'paths':len(paths),'validated_paths':sum(z['status']=='PASS_NUMERICAL' for z in paths),'optimizations':sum(z['nfev']>0 for z in paths),'refinements':len(refinements),'passed_refinements':sum(z['status']=='PASS_NUMERICAL' for z in refinements),'comparisons':len(comparisons),'historical_comparisons':len(historical),
        'audits':len(audits),'audit_states':{state:sum(z['state']==state for z in audits) for state in ['STATIONARY','NONSTATIONARY','UNVERIFIED']},'termination_routes':{route:sum(z['termination_route']==route for z in paths) for route in ['PHYSICAL_SUSTAINED','NATIVE_VERIFIED','NATIVE_CONTROL','UNVERIFIED_TERMINATION']},
        'checks':len(checks),'check_counts':cc,'rejected_trials':sum(z['rejected_zero_edges']+z['rejected_invalid_primitive'] for z in paths)}
    dump(out/'summary.json',summary);dump(out/'provenance.json',{'design_commit':'3b04bbc','implementation':'v1','dependency_commit':CFG['dependency_commit'],'sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'groups_sha256':sha(ROOT/'groups.json'),'scripts':{p.name:sha(p) for p in sorted((ROOT/'scripts').glob('*.py')) if p.name in ['run.py','stopping.py']},'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget,'timings':timings});print(json.dumps(summary|{'seconds':elapsed,'budget':budget}));return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);raise SystemExit(main(parser.parse_args().out))
