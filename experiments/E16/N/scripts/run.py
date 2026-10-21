#!/usr/bin/env python3
"""E16-N: nodos graduados y Hausdorff, diagnóstico exploratorio."""
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

def integral_abs(x,y):
    total=0.
    for lo,hi,a,b in zip(x,x[1:],y,y[1:]):
        width=float(hi-lo);aa=abs(float(a));bb=abs(float(b))
        total+=width*(aa*aa+bb*bb)/(2*(aa+bb)) if a*b<0 else width*(aa+bb)/2
    return total

def tail_statistics(t,delta,cut):
    x=np.unique(np.r_[t,cut]);y=np.interp(x,t,delta);inside=x>=cut;outside=x<=cut
    total=integral_abs(x,y);tail=integral_abs(x[inside],y[inside]);peak=float(np.max(np.abs(y)))
    return {'total_mass':total,'tail_fraction':tail/total if total>0 else 0.,'peak':peak,
            'max_inside':float(np.max(np.abs(y[inside]))),'max_outside':float(np.max(np.abs(y[outside]))),
            'outside_ratio':float(np.max(np.abs(y[outside])))/peak if peak>0 else 0.}

def archived_reference(value,text):
    """Distancia al intervalo de redondeo de una referencia de 40 cifras."""
    center=mp.mpf(text)
    if center==0:raise ValueError('archived positive length required')
    quantum=mp.mpf(10)**(Decimal(text).adjusted()+1-40)
    radius=quantum/2
    distance=max(mp.mpf(0),abs(value-center)-radius)/max(1,abs(value),abs(center))
    return distance,center,quantum,radius

def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
    assert sha(ROOT/'groups.json')==CFG['groups_sha256']
    groups=json.loads((ROOT/'groups.json').read_text())['groups']
    data=json.loads((ROOT.parent/'H/data.json').read_text());d=load('d_m',ROOT.parent/'D/scripts/run.py');g=load('g_m',ROOT.parent/'G/scripts/run.py');k=load('grid_n',ROOT/'scripts/grid_kernel.py')
    source_searches=list(csv.DictReader((ROOT.parent/'M/results/run_v2/trajectories.csv').open()))
    source_vertices=list(csv.DictReader((ROOT.parent/'M/results/run_v2/vertices.csv').open()))
    checks=[];trajectories=[];vertices=[];gradients=[];segments=[];transitions=[];shape_nodes=[];localization=[];cross=[];lineages=[];references=[];saved={}
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(tol))
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rr in [('checks',checks),('trajectories',trajectories),('vertices',vertices),('gradients',gradients),('segments',segments),('transitions',transitions),('shape_nodes',shape_nodes),('localization',localization),('cross_candidates',cross),('lineages',lineages),('source_reference_intervals',references)]:table(out/(name+'.csv'),rr)
        if time.monotonic()-start>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_lineages':len(lineages)})
            raise TimeoutError('time budget; partial evidence preserved')
    def compare_shape(name,coarse,s0,fine,s1,kind):
        t=np.unique(np.r_[k.grid(coarse),k.grid(fine)]);lifted=np.interp(t,k.grid(coarse),np.r_[0,s0,0]);delta=np.interp(t,k.grid(fine),np.r_[0,s1,0])-lifted
        maximum=float(np.max(np.abs(delta)));peak_t=float(t[np.argmax(np.abs(delta))])
        for j,(tt,z) in enumerate(zip(t,delta)):shape_nodes.append({'comparison':name,'type':kind,'coarse_segments':coarse,'fine_segments':fine,'index':j,'t':repr(float(tt)),'difference':repr(float(z))})
        diag=tail_statistics(t,delta,CFG['localization_cutoff'])
        label='ZERO_CHANGE' if diag['total_mass']==0 else ('LOCALIZED_AT_END' if diag['tail_fraction']>=CFG['localization_min_mass'] and diag['outside_ratio']<=CFG['localization_max_outside_ratio'] else 'NOT_ESTABLISHED')
        for cut in CFG['tail_cutoffs']:
            z=tail_statistics(t,delta,cut)
            localization.append({'comparison':name,'type':kind,'cutoff':cut,'max_difference':repr(maximum),'peak_t':repr(peak_t),
                                 **{key:repr(value) for key,value in z.items()},'diagnosis_at_0_9':label})
        return maximum,peak_t,label
    # Auxiliary exact piecewise-linear integration checks in float64.
    check('control/zero',integral_abs(np.array([0.,1.]),np.array([0.,0.])),CFG['control_tolerance'])
    check('control/linear_mass',abs(integral_abs(np.array([0.,1.]),np.array([0.,1.]))-.5),CFG['control_tolerance'])
    check('control/linear_tail',abs(tail_statistics(np.array([0.,1.]),np.array([0.,1.]),.9)['tail_fraction']-.19),CFG['control_tolerance'])
    tx=np.array([0.,.9,.95,1.]);ty=np.array([0.,0.,1.,0.]);diag=tail_statistics(tx,ty,.9)
    check('control/triangle_mass',abs(diag['total_mass']-.05),CFG['control_tolerance'])
    check('control/triangle_tail',abs(diag['tail_fraction']-1),CFG['control_tolerance'])
    check('control/crossing',abs(integral_abs(np.array([0.,1.]),np.array([-.5,.5]))-.25),CFG['control_tolerance'])
    with mp.workdps(120):
        center=mp.mpf('1.25');quantum=mp.mpf('1e-39')
        inside=archived_reference(center+quantum/4,'1.25')[0]
        outside=archived_reference(center+2*quantum,'1.25')[0]
        check('control/archive_inside',inside,CFG['precision_tolerance'])
        check('control/archive_outside_detected',int(outside>mp.mpf(CFG['precision_tolerance']))-1,CFG['control_tolerance'])
    prepared={};rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):
            theta=[mp.mpf(str(x)) for x in data['states']['h00']];zz=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels'][CFG['panel']]]
            cv,jc,c,l=d.analytic_mp(theta,zz);prepared[digits]=(cv,jc,l);rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    def diagnose(lin,m,s,success,f,df,a,b,kind,ux,uy):
        begin=len(checks)
        with mp.workdps(80):
            smp=[mp.mpf(repr(float(z))) for z in s];value=None;ok_spd=True;minimum=mp.inf
            try:
                value=k.reference_length(a,b,smp,kind,ux,uy);scale=max(1,abs(value))
                for u0,du,u,dd in k.mp_edges(a,b,smp,kind,ux,uy):
                    h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h);ok_spd=ok_spd and pa['ok'] and pd['ok'];minimum=min(minimum,pa['margin'],pd['margin'])
                pts=k.points(a,b,smp);normal=mp.matrix([-(b-a)[1],(b-a)[0]]);fd0=[];fd1=[]
                for j in range(len(smp)):
                    pair=[]
                    for step in CFG['mp_fd_steps']:
                        step=mp.mpf(step);plus=pts[j+1]+step*normal;minus=pts[j+1]-step*normal
                        vp=k.reference_length(pts[j],plus,[],kind,ux,uy)+k.reference_length(plus,pts[j+2],[],kind,ux,uy)
                        vm=k.reference_length(pts[j],minus,[],kind,ux,uy)+k.reference_length(minus,pts[j+2],[],kind,ux,uy)
                        pair.append((vp-vm)/(2*step))
                    fd0.append(pair[0]);fd1.append(pair[1])
                gad=np.asarray(df(s),float);ad_error=max(abs(mp.mpf(float(x))-y) for x,y in zip(gad,fd1))/scale;fd_error=max(abs(x-y) for x,y in zip(fd0,fd1))/scale
                check(f'{lin}/{m}/gradient_ad',ad_error,CFG['gradient_agreement_tolerance'],'gradient')
                check(f'{lin}/{m}/gradient_steps',fd_error,CFG['mp_fd_agreement_tolerance'],'gradient')
                check(f'{lin}/{m}/objective',err(value,mp.mpf(float(f(s)))),CFG['objective_tolerance'],'integration')
                gm=np.array([float(x) for x in fd1]);kkt=float(np.max(np.abs(s-np.clip(s-gm,-.25,.25))))/float(scale);free=float(np.max(np.abs(gm)))/float(scale)
                check(f'{lin}/{m}/kkt',kkt,CFG['gradient_tolerance'],'stationarity')
                for j,(x,y,z) in enumerate(zip(gad,fd0,fd1)):gradients.append({'lineage':lin,'segments':m,'index':j,'autograd':repr(float(x)),'mp_fd_1':fmt(y),'mp_fd_2':fmt(z)})
                valid=bool(success and ok_spd and all(z['status']=='PASS' for z in checks[begin:]))
            except (ValueError,ZeroDivisionError):valid=False;ok_spd=False;minimum=mp.nan;ad_error=fd_error=mp.inf;kkt=free=float('inf')
            return {'value':value,'valid':valid,'spd':ok_spd,'minimum':minimum,'ad_error':ad_error,'fd_error':fd_error,'kkt':kkt,'free':free,
                    'active':int(np.sum(np.minimum(abs(s+.25),abs(s-.25))<=float(CFG['boundary_tolerance'])))}
    def validate(lin,m,s,ia,ib,kind):
        low={};valid=True;totals={}
        for digits in CFG['precision']:
            with mp.workdps(digits):
                cv,jc,l=prepared[digits];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
                a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                smp=[mp.mpf(repr(float(z))) for z in s];total=mp.mpf(0)
                for index,(u0,du,u,dd) in enumerate(k.mp_edges(a,b,smp,kind,ux,uy)):
                    h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h);q=[mp.fsum(x*x for x in u),2*mp.fsum(x*y for x,y in zip(u,dd)),mp.fsum(x*x for x in dd)]
                    name=f'{lin}/{m}/{digits}/{index}';reason=''
                    try:
                        value=g.primitive(q);geo=g.geometry(q);qs=[g.quadrature(q,geo,rules[digits][n]) for n in [16,32,64]]
                        check(name+'/coarse',err(qs[0],qs[1]),CFG['coarse_tolerance'],'integration')
                        check(name+'/fine',err(qs[1],qs[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/primitive',err(value,qs[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/reparam',err(value,g.quadrature(q,geo,rules[digits][64],True)),CFG['fine_tolerance'],'integration');total+=value
                    except (ValueError,ZeroDivisionError) as ex:value=None;valid=False;reason=str(ex)
                    valid=valid and pa['ok'] and pd['ok']
                    segments.append({'lineage':lin,'mesh_segments':m,'digits':digits,'index':index,'length':fmt(value) if value is not None else '',
                        'reason':reason,'h00_positive':pa['ok'],'det_positive':pd['ok'],'h00_margin':fmt(pa['margin']),'det_margin':fmt(pd['margin']),'h00_depth':pa['depth'],'det_depth':pd['depth']})
                    if digits==80:low[index]=(value,pa['margin'],pd['margin'])
                    else:
                        prior=low[index]
                        if value is not None and prior[0] is not None:check(name+'/precision_length',err(value,prior[0]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_h00',err(pa['margin'],prior[1]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_det',err(pd['margin'],prior[2]),CFG['precision_tolerance'],'precision')
                totals[digits]=total
                check(f'{lin}/{m}/{digits}/reference',err(total,k.reference_length(a,b,smp,kind,ux,uy)),CFG['precision_tolerance'],'precision')
        return totals[120],valid
    for group in groups:
        lin=group['lineage'];case=group['case'];state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)];lineage_begin=len(checks);history=[]
        source=next(r for r in source_searches if r['lineage']==lin and r['segments']=='32')
        rr=sorted([r for r in source_vertices if r['lineage']==lin and r['segments']=='32'],key=lambda r:int(r['index']))
        previous=np.array([float(r['s']) for r in rr]);assert len(previous)==31
        with mp.workdps(120):
            cv,jc,l=prepared[120];uxf=np.array((d.analytic_B(cv,jc,[1,0],kind)[0]*l).tolist(),float);uyf=np.array((d.analytic_B(cv,jc,[0,1],kind)[0]*l).tolist(),float)
        with mp.workdps(80):
            cv,jc,l=prepared[80];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
            a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float);previous_value=None
        for m in CFG['segments']:
            begin=len(checks);f=k.make_objective(af,bf,m,kind,uxf,uyf);df=grad(f)
            if m==32:
                initial=np.interp(k.grid(m)[1:-1],np.linspace(0,1,33),np.r_[0,previous,0])
            else:
                initial=np.interp(k.grid(m)[1:-1],k.grid(len(previous)+1),np.r_[0,previous,0])
            with mp.workdps(80):
                inherited=k.reference_length(a,b,[mp.mpf(repr(float(x))) for x in initial],kind,ux,uy)
                if m>32:check(f'{lin}/{m}/embedding',err(inherited,previous_value),CFG['embedding_tolerance'])
            options={key:v for key,v in CFG['optimizer'].items() if key!='method'}
            opt=minimize(f,initial,jac=df,bounds=[tuple(CFG['s_bounds'])]*(m-1),method=CFG['optimizer']['method'],options=options)
            s=np.asarray(opt.x,float);success=bool(opt.success);message=str(opt.message);nit=int(opt.nit);nfev=int(opt.nfev);optimized=True
            di=diagnose(lin,m,s,success,f,df,a,b,kind,ux,uy)
            check(f'{lin}/{m}/bounds',max(0,float(np.max(np.abs(s)))-.25),CFG['identity_tolerance'])
            value,valid=validate(lin,m,s,ia,ib,kind)
            with mp.workdps(120):
                check(f'{lin}/{m}/nonworse',max(0,value-inherited)/max(1,inherited),CFG['nonworse_tolerance'])
                if m==32:
                    oldk=load('oldk_n',ROOT.parent/'K/scripts/run.py')
                    original=oldk.reference_length(a,b,[mp.mpf(repr(float(x))) for x in previous],kind,ux,uy)
                    reference_error,center,quantum,radius=archived_reference(original,source['length'])
                    check(f'{lin}/source_reference',reference_error,CFG['precision_tolerance'],'precision')
                    references.append({'lineage':lin,'source_text':source['length'],'computed_90digits':mp.nstr(original,90),
                                       'quantum':fmt(quantum),'rounding_radius':fmt(radius),'scalar_error':fmt(err(original,center)),
                                       'interval_error':fmt(reference_error),'resampled_length':fmt(inherited),'resampling_length_change':fmt(err(inherited,original)),
                                       'resampling_shape_change':repr(float(np.max(np.abs(np.interp(np.unique(np.r_[np.linspace(0,1,33),k.grid(32)]),np.linspace(0,1,33),np.r_[0,previous,0])-np.interp(np.unique(np.r_[np.linspace(0,1,33),k.grid(32)]),k.grid(32),np.r_[0,initial,0])))))})
                if kind=='sum':
                    check(f'{lin}/{m}/sum_params',float(np.max(np.abs(s))),CFG['control_tolerance'])
                    check(f'{lin}/{m}/sum_length',err(value,mp.sqrt(((b-a).T*(ux*ux.T)*(b-a))[0])),CFG['control_tolerance'])
            local=checks[begin:]
            status='FAIL' if any(r['status']=='FAIL' for r in local) else ('INCONCLUSIVE' if not valid or not di['valid'] or any(r['status']=='INCONCLUSIVE' for r in local) else 'PASS_NUMERICAL')
            trajectories.append({'lineage':lin,'case':case,'segments':m,'optimized':optimized,'success':success,'message':message,'iterations':nit,'nfev':nfev,
                'status':status,'length':fmt(value),'kkt':repr(di['kkt']),'free_gradient':repr(di['free']),'active_nodes':di['active'],
                'gradient_error':fmt(di['ad_error']),'fd_consistency':fmt(di['fd_error']),'spd':di['spd'],'minimum_spd_margin':fmt(di['minimum'])})
            for j,z in enumerate(s):vertices.append({'lineage':lin,'case':case,'segments':m,'index':j,'t':repr(float(k.grid(m)[j+1])),'s':repr(float(z))})
            saved[(lin,m)]=(s.copy(),value,status);history.append((m,s.copy(),value,status))
            if m>32:
                oldm,olds,oldlength,oldstatus=history[-2];name=f'{lin}_{oldm}_{m}'
                shape,peak_t,loc=compare_shape(name,oldm,olds,m,s,'refinement')
                with mp.workdps(120):length_error=err(value,oldlength)
                check(name+'/length_refinement',length_error,CFG['length_refinement_tolerance'],'refinement')
                check(name+'/shape_refinement',shape,CFG['shape_refinement_tolerance'],'shape')
                transitions.append({'lineage':lin,'coarse_segments':oldm,'fine_segments':m,'length_error':fmt(length_error),'shape_error':repr(shape),'peak_t':repr(peak_t),'localization':loc})
            previous=s.copy();previous_value=value;checkpoint()
        local=checks[lineage_begin:]
        status='FAIL' if any(r['status']=='FAIL' for r in local) or any(h[3]=='FAIL' for h in history) else ('INCONCLUSIVE' if any(r['status']=='INCONCLUSIVE' for r in local) or any(h[3]=='INCONCLUSIVE' for h in history) else 'PASS_NUMERICAL')
        lineages.append({'lineage':lin,'case':case,'representative_start':group['representative_start'],'status':status,'final_length':fmt(history[-1][2]),'boundary_final':bool(trajectories[-1]['active_nodes'])});checkpoint()
    quad=[group['lineage'] for group in groups if group['case'].endswith('/quadratic')];assert len(quad)==2
    for m in CFG['segments']:
        sa,la,sta=saved[(quad[0],m)];sb,lb,stb=saved[(quad[1],m)]
        name=f'{quad[0]}_{quad[1]}_{m}';shape,peak_t,loc=compare_shape(name,m,sa,m,sb,'between_lineages')
        with mp.workdps(120):le=err(la,lb)
        agreement=le<=mp.mpf(CFG['group_length_tolerance']) and shape<=float(CFG['group_shape_tolerance'])
        cross.append({'lineage_a':quad[0],'lineage_b':quad[1],'segments':m,'length_difference':fmt(le),'shape_difference':repr(shape),'peak_t':repr(peak_t),
                      'diagnosis':'NUMERICAL_AGREEMENT' if agreement else 'DIFFERENT_CANDIDATES','localization':loc})
    checkpoint()
    hd=load('hausdorff_n',ROOT/'scripts/hausdorff.py')
    comparisons=hd.analyze(source_vertices,vertices,CFG)
    table(out/'hausdorff.csv',comparisons)
    for row in comparisons:
        if row['family']=='N_refinement':
            check(row['comparison']+'/hausdorff',row['upper'],CFG['hausdorff_tolerance'],'hausdorff')
            check(row['comparison']+'/hausdorff_gap',row['upper']-row['lower'],CFG['hausdorff_gap'],'hausdorff')
    for row in lineages:
        extra=[x for x in checks if x['category']=='hausdorff' and x['name'].startswith('N_'+row['lineage']+'_')]
        if any(x['status']!='PASS' for x in extra):row['status']='INCONCLUSIVE'
    checkpoint()
    cc={s:sum(r['status']==s for r in checks) for s in ['PASS','FAIL','INCONCLUSIVE']};counts={s:sum(r['status']==s for r in lineages) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or cc['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'lineages':len(lineages),'counts':counts,'trajectories':len(trajectories),'validated_trajectories':sum(r['status']=='PASS_NUMERICAL' for r in trajectories),
             'optimizations':sum(r['optimized'] for r in trajectories),'checks':len(checks),'check_counts':cc,
             'localization_counts':{s:sum(r['localization']==s for r in transitions) for s in ['LOCALIZED_AT_END','NOT_ESTABLISHED','ZERO_CHANGE']},
             'cross_candidate_diagnoses':{str(r['segments']):r['diagnosis'] for r in cross}}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'design_commit':'e21d2f6','implementation':'v1','kernel_sha256':sha(ROOT/'scripts/grid_kernel.py'),'config_sha256':sha(ROOT/'config.json'),'script_sha256':sha(Path(__file__)),'groups_sha256':sha(ROOT/'groups.json'),
                               'hausdorff_sha256':sha(ROOT/'scripts/hausdorff.py'),'sources':CFG['sources'],'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
