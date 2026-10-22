#!/usr/bin/env python3
"""E16-P: contraste entre gráficos y polígonos paramétricos."""
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
    k=load('kernel_p',ROOT/'scripts/kernel.py');geo=load('geometry_p',ROOT/'scripts/geometry.py')
    d=load('d_p',ROOT.parent/'D/scripts/run.py');g=load('g_p',ROOT.parent/'G/scripts/run.py');hd=load('hd_p',ROOT.parent/'N/scripts/hausdorff.py')
    groups=json.loads((ROOT/'groups.json').read_text())['groups'];data=json.loads((ROOT.parent/'H/data.json').read_text())
    oldv=list(csv.DictReader((ROOT.parent/'O/results/run_v1/vertices.csv').open()));oldt=list(csv.DictReader((ROOT.parent/'O/results/run_v1/trajectories.csv').open()))
    checks=[];paths=[];vertices=[];gradients=[];segments=[];references=[];release=[];refinements=[];comparisons=[];controls=[];cases=[];saved={}
    tables={'checks':checks,'paths':paths,'vertices':vertices,'gradients':gradients,'segments':segments,'source_references':references,'release_gradients':release,'refinements':refinements,'comparisons':comparisons,'controls':controls,'cases':cases}
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(tol))
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rows in tables.items():table(out/(name+'.csv'),rows)
        if time.monotonic()-started>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_cases':len(cases)})
            raise TimeoutError('time budget; partial evidence preserved')
    for row in hd.controls():
        controls.append({'name':'hausdorff_'+row['name'],'value':repr(row['lower']),'reference':repr(row['expected']),'error':repr(max(0,row['lower']-row['expected'],row['expected']-row['upper']))})
    with mp.workdps(80):
        ux=mp.eye(2);uy=mp.matrix([[0,mp.mpf('.3')],[mp.mpf('.7'),0]])
        for name,pts in [('vertical',[mp.matrix([1,1]),mp.matrix([1,2])]),('general',[mp.matrix([1,1]),mp.matrix([2,1])])]:
            val=k.reference(pts,'quadratic',ux,uy);reversed_value=k.reference(list(reversed(pts)),'quadratic',ux,uy)
            split=k.reference([pts[0],(pts[0]+pts[1])/2,pts[1]],'quadratic',ux,uy)
            for suffix,other in [('reversal',reversed_value),('subdivision',split)]:
                e=err(val,other);check('control/'+name+'/'+suffix,e,CFG['precision_tolerance'])
                controls.append({'name':name+'_'+suffix,'value':fmt(val),'reference':fmt(other),'error':fmt(e)})
    # Only arclength diagnostics are allowed to ignore parameter redistribution.
    acontrol=np.array([[0.,0.],[.3,0.],[1.,0.]]);bcontrol=np.array([[0.,0.],[.1,0.],[.9,0.],[1.,0.]])
    check('control/arc_redistribution',float(np.max(abs(geo.resample(acontrol,257)-geo.resample(bcontrol,257)))),CFG['control_tolerance'])
    prepared={};rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):
            theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][j]] for j in data['panels'][CFG['panel']]]
            cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]=(cv,jc,l);rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    def setup(kind,ia,ib,digits):
        cv,jc,l=prepared[digits];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
        a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        return a,b,ux,uy
    def gradient_check(name,z,arm,obj,kind,ia,ib,rows):
        x=k.pack(z,arm);gad=np.asarray(grad(obj.value)(x),float);fd0=[];fd1=[]
        with mp.workdps(80):
            a,b,ux,uy=setup(kind,ia,ib,80);pts=k.mp_points(a,b,z);v=b-a;normal=mp.matrix([-v[1],v[0]])
            value=k.reference(pts,kind,ux,uy);scale=max(1,abs(value))
            variables=[(j,axis) for j in range(1,len(z)-1) for axis in ([1] if arm=='fixed' else [0,1])]
            for n,(j,axis) in enumerate(variables):
                direction=v if axis==0 else normal;fd=[]
                for step in CFG['mp_fd_steps']:
                    step=mp.mpf(step);plus=pts[j]+step*direction;minus=pts[j]-step*direction
                    vp=k.reference([pts[j-1],plus,pts[j+1]],kind,ux,uy);vm=k.reference([pts[j-1],minus,pts[j+1]],kind,ux,uy)
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
    for group in groups:
        lin=group['lineage'];case=group['case'];state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)]
        r=int(CFG['source_round'][lin]);source=next(z for z in oldt if z['lineage']==lin and int(z['round'])==r)
        rr=sorted([z for z in oldv if z['lineage']==lin and int(z['round'])==r],key=lambda z:int(z['index']))
        original=np.array([[0.,0.]]+[[float(z['t']),float(z['s'])] for z in rr]+[[1.,0.]])
        base=original.copy()
        if lin=='C0':base=np.array([item for j in range(len(original)-1) for item in ([original[j],(original[j]+original[j+1])/2] if j<4 else [original[j]])]+[original[-1]])
        assert len(base)==133
        with mp.workdps(80):
            a,b,ux,uy=setup(kind,ia,ib,80);original_value=k.reference(k.mp_points(a,b,original),kind,ux,uy);base_value=k.reference(k.mp_points(a,b,base),kind,ux,uy)
            e,center,quantum,radius=archived_reference(original_value,source['length'])
            check(lin+'/source_reference',e,CFG['precision_tolerance'],'precision');check(lin+'/source_embedding',err(base_value,original_value),CFG['embedding_tolerance'])
            references.append({'lineage':lin,'source_round':r,'source_segments':len(original)-1,'base_segments':132,'archived_length':source['length'],'computed_length_90digits':mp.nstr(original_value,90),
                'rounding_radius':fmt(radius),'interval_error':fmt(e),'base_length':fmt(base_value),'embedding_error':fmt(err(base_value,original_value))})
        with mp.workdps(120):a,b,ux,uy=setup(kind,ia,ib,120);uxf=np.array(ux.tolist(),float);uyf=np.array(uy.tolist(),float)
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
        diagnostic_obj=k.Objective(af,bf,'free',base[:,0],kind,uxf,uyf)
        baseline_gradient=gradient_check(lin+'/source_release',base,'free',diagnostic_obj,kind,ia,ib,release)
        for arm in CFG['arms']:
            case_begin=len(checks);previous=None;previous_value=None;previous_status=None
            for m in CFG['segments']:
                name=f'{lin}/{arm}/{m}';begin=len(checks)
                reference_source=base if m==132 else k.subdivide(base)
                initial=base.copy() if previous is None else k.subdivide(previous)
                obj=k.Objective(af,bf,arm,initial[:,0],kind,uxf,uyf);x0=k.pack(initial,arm)
                bounds=[tuple(CFG['s_bounds'])]*(m-1) if arm=='fixed' else [bb for j in range(m-1) for bb in [tuple(CFG['t_bounds']),tuple(CFG['s_bounds'])]]
                with mp.workdps(80):
                    a,b,ux,uy=setup(kind,ia,ib,80)
                    try:inherited=k.reference(k.mp_points(a,b,initial),kind,ux,uy)
                    except (ValueError,ZeroDivisionError):inherited=None
                    if previous is not None and inherited is not None and previous_value is not None:check(name+'/embedding',err(inherited,previous_value),CFG['embedding_tolerance'])
                if inherited is None:
                    z=initial;success=False;message='invalid_parent_geometry';nit=nfev=0
                else:
                    opt=minimize(obj.fun,x0,jac=grad(obj.value),bounds=bounds,method=CFG['optimizer']['method'],options={kk:vv for kk,vv in CFG['optimizer'].items() if kk!='method'})
                    z=np.asarray(k.coords(opt.x,arm,initial[:,0]),float);success=bool(opt.success);message=str(opt.message);nit=int(opt.nit);nfev=int(opt.nfev)
                value=None;spd=False;di=None;reason=''
                try:
                    di=gradient_check(name,z,arm,obj,kind,ia,ib,gradients)
                    check(name+'/kkt',di['kkt'],CFG['gradient_tolerance'],'stationarity')
                    value,valid,spd=validate(name,z,kind,ia,ib)
                    with mp.workdps(120):
                        check(name+'/objective',err(value,mp.mpf(float(obj.value(k.pack(z,arm))))),CFG['objective_tolerance'],'integration')
                        check(name+'/nonworse',max(0,value-inherited)/max(1,inherited),CFG['nonworse_tolerance'],'optimization')
                        if kind=='sum':
                            a,b,ux,uy=setup(kind,ia,ib,120)
                            check(name+'/sum_params',float(np.max(abs(z[:,1]))),CFG['control_tolerance'])
                            check(name+'/sum_length',err(value,mp.sqrt(((b-a).T*(ux*ux.T)*(b-a))[0])),CFG['control_tolerance'])
                except (ValueError,ZeroDivisionError,TypeError) as ex:valid=False;reason=type(ex).__name__+': '+str(ex);check(name+'/evaluable',1,0,'integration')
                check(name+'/valid_geometry',0 if valid else 1,0,'integration')
                check(name+'/optimizer_success',0 if success else 1,0,'stationarity')
                box_error=max(0.,float(np.max(-z[:,0])),float(np.max(z[:,0]-1)),float(np.max(abs(z[:,1])-.25)))
                check(name+'/bounds',box_error,CFG['identity_tolerance'])
                check(name+'/endpoints',float(np.max(abs(z[[0,-1]]-np.array([[0.,0.],[1.,0.]])))),CFG['identity_tolerance'])
                local=checks[begin:];status='FAIL' if any(q['status']=='FAIL' for q in local) else ('PASS_NUMERICAL' if valid and all(q['status']=='PASS' for q in local) else 'INCONCLUSIVE')
                desc=geo.descriptors(z,reference_source,CFG)
                paths.append({'path':name,'lineage':lin,'arm':arm,'segments':m,'status':status,'success':success,'message':message,'reason':reason,'iterations':nit,'nfev':nfev,
                    'length':fmt(value) if value is not None else '', 'kkt':repr(di['kkt']) if di else '', 'longitudinal_gradient':repr(di['longitudinal_gradient']) if di else '',
                    'gradient_error':fmt(di['ad_error']) if di else '', 'fd_consistency':fmt(di['fd_error']) if di else '', 'spd':spd,
                    'rejected_zero_edges':obj.rejections['zero_edge'],'rejected_invalid_primitive':obj.rejections['invalid_primitive'],**desc})
                for j,(t,s) in enumerate(z):vertices.append({'path':name,'lineage':lin,'arm':arm,'segments':m,'index':j,'u':repr(j/m),'t':repr(float(t)),'s':repr(float(s))})
                saved[(lin,arm,m)]=(z.copy(),value,status)
                if previous is not None:
                    tb=len(checks);row=compare(f'{lin}_{arm}_132_264',previous,z,previous_value,value,'refinement')
                    check(row['comparison']+'/length',mp.mpf(row['length_difference']),CFG['length_refinement_tolerance'],'refinement')
                    check(row['comparison']+'/hausdorff',float(row['hausdorff_upper']),CFG['hausdorff_tolerance'],'refinement')
                    check(row['comparison']+'/hausdorff_gap',float(row['hausdorff_gap']) if row['hausdorff_gap'] else mp.inf,CFG['hausdorff_gap'],'refinement')
                    row['status']='PASS_NUMERICAL' if all(q['status']=='PASS' for q in checks[tb:]) and status==previous_status=='PASS_NUMERICAL' else 'INCONCLUSIVE'
                    refinements.append(row)
                previous=z.copy();previous_value=value;previous_status=status;checkpoint()
            local=checks[case_begin:];status='FAIL' if any(z['status']=='FAIL' for z in local) else ('PASS_NUMERICAL' if all(z['status']=='PASS' for z in local) else 'INCONCLUSIVE')
            cases.append({'lineage':lin,'arm':arm,'status':status});checkpoint()
        for m in CFG['segments']:
            za,la,_=saved[(lin,'fixed',m)];zb,lb,_=saved[(lin,'free',m)]
            comparisons.append(compare(f'{lin}_fixed_free_{m}',za,zb,la,lb,'between_arms'))
    for arm in CFG['arms']:
        for m in CFG['segments']:
            za,la,_=saved[('Q0',arm,m)];zb,lb,_=saved[('Q1',arm,m)]
            comparisons.append(compare(f'Q0_Q1_{arm}_{m}',za,zb,la,lb,'between_lineages'))
    checkpoint()
    counts={st:sum(z['status']==st for z in cases) for st in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']};cc={st:sum(z['status']==st for z in checks) for st in ['PASS','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if cc['FAIL'] or counts['FAIL'] else ('INCONCLUSIVE' if cc['INCONCLUSIVE'] or counts['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'cases':len(cases),'counts':counts,'paths':len(paths),'validated_paths':sum(z['status']=='PASS_NUMERICAL' for z in paths),
        'optimizations':sum(z['nfev']>0 for z in paths),'refinements':len(refinements),'passed_refinements':sum(z['status']=='PASS_NUMERICAL' for z in refinements),
        'comparisons':len(comparisons),'checks':len(checks),'check_counts':cc,'rejected_trials':sum(z['rejected_zero_edges']+z['rejected_invalid_primitive'] for z in paths)}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'design_commit':'4f9e8e6','implementation':'v1','sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'groups_sha256':sha(ROOT/'groups.json'),
        'scripts':{p.name:sha(p) for p in sorted((ROOT/'scripts').glob('*.py')) if p.name in ['run.py','kernel.py','geometry.py']},'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget});print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
