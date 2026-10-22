#!/usr/bin/env python3
"""E16-O: indicador local, refinamiento y perfiles del extremo."""
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
from scipy.optimize import minimize,minimize_scalar

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
    data=json.loads((ROOT.parent/'H/data.json').read_text())
    d=load('d_o',ROOT.parent/'D/scripts/run.py');g=load('g_o',ROOT.parent/'G/scripts/run.py')
    k=load('kernel_o',ROOT/'scripts/grid_kernel.py');ad=load('adaptive_o',ROOT/'scripts/adaptive.py')
    hd=load('hd_o',ROOT.parent/'N/scripts/hausdorff.py');hd.controls();ad.controls()
    source_searches=list(csv.DictReader((ROOT.parent/'N/results/run_v1/trajectories.csv').open()))
    source_vertices=list(csv.DictReader((ROOT.parent/'N/results/run_v1/vertices.csv').open()))
    checks=[];trajectories=[];vertices=[];gradients=[];segments=[];transitions=[];shape_nodes=[];localization=[];cross=[];lineages=[];references=[];probes=[];marking=[];profiles=[];tails=[];saved={}
    tables={'checks':checks,'trajectories':trajectories,'vertices':vertices,'gradients':gradients,'segments':segments,'transitions':transitions,'shape_nodes':shape_nodes,'localization':localization,'cross_candidates':cross,'lineages':lineages,'source_reference_intervals':references,'probes':probes,'marking':marking,'profiles':profiles,'tails':tails}
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(tol))
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rows in tables.items():table(out/(name+'.csv'),rows)
        if time.monotonic()-start>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_lineages':len(lineages)})
            raise TimeoutError('time budget; partial evidence preserved')
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
    def differences(name,t0,s0,t1,s1,comparison_type):
        t,delta,maximum=ad.shape(t0,s0,t1,s1);peak_t=float(t[np.argmax(np.abs(delta))])
        for j,(tt,z) in enumerate(zip(t,delta)):shape_nodes.append({'comparison':name,'type':comparison_type,'index':j,'t':repr(float(tt)),'difference':repr(float(z))})
        diag=tail_statistics(t,delta,CFG['localization_cutoff'])
        label='ZERO_CHANGE' if diag['total_mass']==0 else ('LOCALIZED_AT_END' if diag['tail_fraction']>=CFG['localization_min_mass'] and diag['outside_ratio']<=CFG['localization_max_outside_ratio'] else 'NOT_ESTABLISHED')
        for cut in CFG['tail_cutoffs']:
            z=tail_statistics(t,delta,cut)
            localization.append({'comparison':name,'type':comparison_type,'cutoff':cut,'peak_t':repr(peak_t),**{key:repr(value) for key,value in z.items()},'diagnosis_at_0_9':label})
        a0=np.column_stack([t0,np.r_[0,s0,0]]);a1=np.column_stack([t1,np.r_[0,s1,0]])
        lo,hi,nsplit=hd.hausdorff(a0,a1,float(CFG['hausdorff_gap']),CFG['hausdorff_max_splits'])
        return maximum,peak_t,label,lo,hi,nsplit
    def indicator(lin,round_id,t,s,a,b,kind,ux,uy,af,bf,uxf,uyf):
        scores=[];valid=True;normal=np.array([-(bf-af)[1],(bf-af)[0]]);p=af+t[:,None]*(bf-af)+np.r_[0,s,0][:,None]*normal
        with mp.workdps(80):
            pts=k.points(a,b,[mp.mpf(repr(float(z))) for z in s]);v=b-a;nmp=mp.matrix([-v[1],v[0]])
            for j in range(len(t)-1):
                tm=(t[j]+t[j+1])/2;baseline=(np.r_[0,s,0][j]+np.r_[0,s,0][j+1])/2
                obj=k.midpoint_objective(p[j],p[j+1],af+tm*(bf-af),normal,kind,uxf,uyf)
                opt=minimize_scalar(obj,bounds=tuple(CFG['s_bounds']),method=CFG['probe_scalar']['method'],options={z:x for z,x in CFG['probe_scalar'].items() if z!='method'})
                candidates=[float(opt.x),float(CFG['s_bounds'][0]),float(CFG['s_bounds'][1]),float(baseline)]
                values=[float(obj(z)) for z in candidates];base_value=values[-1]
                chosen=int(np.argmin(values));winner=candidates[chosen];raw_gain=max(0.,base_value-values[chosen])
                parent=k.reference_length(pts[j],pts[j+1],[],kind,ux,uy)
                if raw_gain<=float(CFG['probe_tie_tolerance'])*max(1,float(parent)):winner=float(baseline)
                selected_value=float(obj(winner));gain=max(0.,base_value-selected_value);displacement=abs(winner-baseline)
                middle=a+mp.mpf(float(tm))*v+mp.mpf(repr(winner))*nmp
                ref=k.reference_length(pts[j],middle,[],kind,ux,uy)+k.reference_length(middle,pts[j+1],[],kind,ux,uy)
                error=err(ref,mp.mpf(selected_value));probe_valid=bool(opt.success and mp.isfinite(error) and error<=mp.mpf(CFG['probe_objective_tolerance']))
                check(f'{lin}/{round_id}/probe/{j}/objective',error,CFG['probe_objective_tolerance'],'probe')
                check(f'{lin}/{round_id}/probe/{j}/success',0 if opt.success else 1,0,'probe')
                valid=valid and probe_valid
                score=max(displacement/float(CFG['probe_shape_tolerance']),np.sqrt(gain/float(CFG['probe_gain_tolerance'])))
                scores.append(score)
                probes.append({'lineage':lin,'round':round_id,'segments':len(t)-1,'index':j,'t0':repr(float(t[j])),'t1':repr(float(t[j+1])),
                    's_original':repr(float(baseline)),'s_optimizer':repr(float(opt.x)),'s_selected':repr(winner),
                    'length_optimizer':repr(values[0]),'length_lower_bound':repr(values[1]),'length_upper_bound':repr(values[2]),'length_baseline':repr(base_value),
                    'length_selected':repr(selected_value),'raw_gain':repr(raw_gain),'gain':repr(gain),'displacement':repr(displacement),'score':repr(float(score)),
                    'success':bool(opt.success),'nfev':int(opt.nfev),'mp_selected':fmt(ref),'objective_error':fmt(error),'valid':probe_valid})
        return np.asarray(scores),valid
    def profile(lin,round_id,t,s,a,b,kind,ux,uy,value):
        with mp.workdps(80):
            pts=k.points(a,b,[mp.mpf(repr(float(z))) for z in s]);local=[];euclidean=[];speeds=[]
            for j,(x,y) in enumerate(zip(pts,pts[1:])):
                dt=mp.mpf(float(t[j+1]))-mp.mpf(float(t[j]));v=y-x
                u0=ux if kind=='sum' else x[0]*ux+x[1]*uy;u1=ux if kind=='sum' else y[0]*ux+y[1]*uy
                u=(v.T*u0).T;dd=(v.T*(u1-u0)).T
                density=[mp.sqrt(mp.fsum(z*z for z in u+mp.mpf(q)*dd))/dt for q in ['0','.5','1']]
                slope=(np.r_[0,s,0][j+1]-np.r_[0,s,0][j])/(t[j+1]-t[j]);speed=float(np.hypot(1,slope));length=k.reference_length(x,y,[],kind,ux,uy)
                local.append(length);euclidean.append(speed);speeds.append(max(density))
                profiles.append({'lineage':lin,'round':round_id,'segments':len(t)-1,'index':j,'t0':repr(float(t[j])),'t1':repr(float(t[j+1])),
                    'slope':repr(float(slope)),'euclidean_speed_per_chord':repr(speed),'h_speed_left':fmt(density[0]),'h_speed_mid':fmt(density[1]),'h_speed_right':fmt(density[2]),'length':fmt(length)})
            check(f'{lin}/{round_id}/profile_length',err(mp.fsum(local),value),CFG['precision_tolerance'],'precision')
            for cut in CFG['tail_cutoffs']:
                tail=mp.mpf(0)
                for j,(x,y) in enumerate(zip(pts,pts[1:])):
                    if t[j+1]<=cut:continue
                    if t[j]>=cut:tail+=local[j]
                    else:
                        z=(mp.mpf(str(cut))-mp.mpf(float(t[j])))/(mp.mpf(float(t[j+1]))-mp.mpf(float(t[j])))
                        tail+=k.reference_length(x+z*(y-x),y,[],kind,ux,uy)
                inside=[q for j,q in enumerate(euclidean) if t[j+1]>cut];outside=[q for j,q in enumerate(euclidean) if t[j]<cut]
                j=int(np.argmax(euclidean))
                tails.append({'lineage':lin,'round':round_id,'segments':len(t)-1,'cutoff':cut,'tail_length':fmt(tail),'total_length':fmt(value),'tail_length_fraction':fmt(tail/value),
                    'max_euclidean_speed':repr(max(euclidean)),'peak_t0':repr(float(t[j])),'peak_t1':repr(float(t[j+1])),
                    'max_speed_inside':repr(max(inside)),'max_speed_outside':repr(max(outside)),'max_sampled_h_speed':fmt(max(speeds))})
    for group in groups:
        lin=group['lineage'];case=group['case'];state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)];lineage_begin=len(checks);history=[];transition_valid=[];all_probes_valid=True
        source=next(r for r in source_searches if r['lineage']==lin and r['segments']=='128')
        rr=sorted([r for r in source_vertices if r['lineage']==lin and r['segments']=='128'],key=lambda r:float(r['t']))
        t=np.r_[0,[float(r['t']) for r in rr],1];s=np.array([float(r['s']) for r in rr]);assert len(s)==127
        with mp.workdps(120):
            cv,jc,l=prepared[120];uxf=np.array((d.analytic_B(cv,jc,[1,0],kind)[0]*l).tolist(),float);uyf=np.array((d.analytic_B(cv,jc,[0,1],kind)[0]*l).tolist(),float)
        with mp.workdps(80):
            cv,jc,l=prepared[80];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
            a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
        for round_id in range(CFG['max_rounds']+1):
            begin=len(checks);m=len(t)-1;k.set_nodes(t);f=k.make_objective(af,bf,m,kind,uxf,uyf);df=grad(f)
            if round_id==0:success=source['success']=='True';message='saved_N128_no_reoptimization';nit=nfev=0;optimized=False
            else:
                with mp.workdps(80):
                    inherited=k.reference_length(a,b,[mp.mpf(repr(float(z))) for z in s],kind,ux,uy)
                    check(f'{lin}/{m}/embedding',err(inherited,history[-1]['value']),CFG['embedding_tolerance'])
                opt=minimize(f,s,jac=df,bounds=[tuple(CFG['s_bounds'])]*(m-1),method=CFG['optimizer']['method'],options={z:v for z,v in CFG['optimizer'].items() if z!='method'})
                s=np.asarray(opt.x,float);success=bool(opt.success);message=str(opt.message);nit=int(opt.nit);nfev=int(opt.nfev);optimized=True
            di=diagnose(lin,m,s,success,f,df,a,b,kind,ux,uy);value,valid=validate(lin,m,s,ia,ib,kind)
            check(f'{lin}/{m}/bounds',max(0,float(np.max(np.abs(s)))-.25),CFG['identity_tolerance'])
            with mp.workdps(120):
                if round_id==0:
                    re,center,quantum,radius=archived_reference(value,source['length']);check(f'{lin}/source_reference',re,CFG['precision_tolerance'],'precision')
                    references.append({'lineage':lin,'source_text':source['length'],'computed_90digits':mp.nstr(value,90),'quantum':fmt(quantum),'rounding_radius':fmt(radius),'interval_error':fmt(re)})
                else:check(f'{lin}/{m}/nonworse',max(0,value-inherited)/max(1,inherited),CFG['nonworse_tolerance'])
                if kind=='sum':
                    check(f'{lin}/{m}/sum_params',float(np.max(np.abs(s))),CFG['control_tolerance'])
                    check(f'{lin}/{m}/sum_length',err(value,mp.sqrt(((b-a).T*(ux*ux.T)*(b-a))[0])),CFG['control_tolerance'])
            profile(lin,round_id,t,s,a,b,kind,ux,uy,value)
            local=checks[begin:];status='FAIL' if any(z['status']=='FAIL' for z in local) else ('PASS_NUMERICAL' if valid and di['valid'] and all(z['status']=='PASS' for z in local) else 'INCONCLUSIVE')
            trajectories.append({'lineage':lin,'case':case,'round':round_id,'segments':m,'optimized':optimized,'success':success,'message':message,'iterations':nit,'nfev':nfev,'status':status,'length':fmt(value),
                'kkt':repr(di['kkt']),'gradient_error':fmt(di['ad_error']),'fd_consistency':fmt(di['fd_error']),'spd':di['spd'],'active_nodes':di['active']})
            for j,z in enumerate(s):vertices.append({'lineage':lin,'case':case,'round':round_id,'segments':m,'index':j,'t':repr(float(t[j+1])),'s':repr(float(z))})
            if round_id>0:
                old=history[-1];name=f'{lin}_{round_id-1}_{round_id}';tb=len(checks)
                shape,peak_t,loc,lo,hi,nsplit=differences(name,old['t'],old['s'],t,s,'refinement')
                with mp.workdps(120):le=err(value,old['value'])
                for suffix,e,tol in [('length',le,CFG['length_refinement_tolerance']),('shape',shape,CFG['shape_refinement_tolerance']),('hausdorff',hi,CFG['hausdorff_tolerance']),('hausdorff_gap',hi-lo,CFG['hausdorff_gap'])]:check(name+'/'+suffix,e,tol,'refinement_'+suffix)
                passed=all(z['status']=='PASS' for z in checks[tb:]) and status=='PASS_NUMERICAL' and old['status']=='PASS_NUMERICAL';transition_valid.append(passed)
                transitions.append({'lineage':lin,'round_from':round_id-1,'round_to':round_id,'segments_from':len(old['t'])-1,'segments_to':m,'length_error':fmt(le),'shape_error':repr(shape),'peak_t':repr(peak_t),
                    'hausdorff_lower':repr(lo),'hausdorff_upper':repr(hi),'hausdorff_gap':repr(hi-lo),'hausdorff_splits':nsplit,'localization':loc,'status':'PASS_NUMERICAL' if passed else 'INCONCLUSIVE'})
            history.append({'round':round_id,'t':t.copy(),'s':s.copy(),'value':value,'status':status})
            scores,probe_valid=indicator(lin,round_id,t,s,a,b,kind,ux,uy,af,bf,uxf,uyf);all_probes_valid=all_probes_valid and probe_valid
            terminal_estimate=bool(np.max(scores)<=1)
            stable=len(transition_valid)>=CFG['stable_transitions_required'] and all(transition_valid[-CFG['stable_transitions_required']:])
            zero=bool(np.sum(scores*scores)==0);remaining=min(CFG['max_additions_per_round'],CFG['max_segments']-m)
            chosen,mass=ad.mark(scores,CFG['marking_fraction'],remaining)
            if terminal_estimate and stable:reason='stable_terminal'
            elif zero:reason='zero_indicator'
            elif round_id==CFG['max_rounds']:reason='round_budget'
            elif remaining==0:reason='segment_budget'
            else:reason='refine'
            marking.append({'lineage':lin,'round':round_id,'segments':m,'max_score':repr(float(np.max(scores))),'sum_score_squared':repr(float(np.sum(scores*scores))),
                'terminal_estimate':terminal_estimate,'last_two_stable':stable,'probe_valid':probe_valid,'marked_indices':json.dumps(chosen if reason=='refine' else []),'captured_fraction':repr(mass if reason=='refine' else 0.),'reason':reason})
            checkpoint()
            if reason!='refine':break
            newt=np.unique(np.r_[t,[(t[j]+t[j+1])/2 for j in chosen]]);s=np.interp(newt[1:-1],t,np.r_[0,s,0]);t=newt
        local=checks[lineage_begin:];identity_failed=any(z['status']=='FAIL' for z in local);nonref_failed=any(z['status']!='PASS' for z in local if not z['category'].startswith('refinement_'))
        passed=all(z['status']=='PASS_NUMERICAL' for z in history) and all_probes_valid and not nonref_failed and ((kind=='sum' and zero) or (terminal_estimate and stable))
        status='FAIL' if identity_failed else ('PASS_NUMERICAL' if passed else 'INCONCLUSIVE')
        lineages.append({'lineage':lin,'case':case,'status':status,'final_round':round_id,'final_segments':len(t)-1,'final_length':fmt(value),'terminal_estimate':terminal_estimate,'last_two_stable':stable,'reason':reason})
        saved[lin]=history;checkpoint()
    for round_id in range(max(len(saved['Q0']),len(saved['Q1']))):
        xa=saved['Q0'][min(round_id,len(saved['Q0'])-1)];xb=saved['Q1'][min(round_id,len(saved['Q1'])-1)]
        shape,peak_t,loc,lo,hi,nsplit=differences(f'Q0_Q1_{round_id}',xa['t'],xa['s'],xb['t'],xb['s'],'between_lineages')
        with mp.workdps(120):le=err(xa['value'],xb['value'])
        cross.append({'comparison_round':round_id,'round_Q0':xa['round'],'round_Q1':xb['round'],'segments_Q0':len(xa['t'])-1,'segments_Q1':len(xb['t'])-1,'length_difference':fmt(le),'shape_difference':repr(shape),
            'hausdorff_lower':repr(lo),'hausdorff_upper':repr(hi),'diagnosis':'NUMERICAL_AGREEMENT' if le<=mp.mpf(CFG['group_length_tolerance']) and shape<=float(CFG['group_shape_tolerance']) else 'DIFFERENT_CANDIDATES'})
    checkpoint()
    cc={st:sum(z['status']==st for z in checks) for st in ['PASS','FAIL','INCONCLUSIVE']};counts={st:sum(z['status']==st for z in lineages) for st in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'lineages':len(lineages),'counts':counts,'trajectories':len(trajectories),'validated_trajectories':sum(z['status']=='PASS_NUMERICAL' for z in trajectories),
        'optimizations':sum(z['optimized'] for z in trajectories),'probes':len(probes),'invalid_probes':sum(not z['valid'] for z in probes),'transitions':len(transitions),
        'stable_transitions':sum(z['status']=='PASS_NUMERICAL' for z in transitions),'checks':len(checks),'check_counts':cc}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'design_commit':'6a6c21e','implementation':'v1','sources':CFG['sources'],'config_sha256':sha(ROOT/'config.json'),'groups_sha256':sha(ROOT/'groups.json'),
        'scripts':{z:sha(ROOT/'scripts'/z) for z in ['run.py','grid_kernel.py','adaptive.py']},'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget});print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
