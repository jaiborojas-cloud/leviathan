#!/usr/bin/env python3
"""E16-K: gradiente de primitiva, prolongación exacta y diagnóstico multirrama."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
import autograd.numpy as anp
from autograd import grad,hessian
import mpmath as mp
import numpy as np
import scipy
from scipy.optimize import minimize

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fmt(v):return mp.nstr(v,40)
def err(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
def table(p,rows):
    if not rows:return
    with p.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def make_objective(a,b,m,kind,ux,uy):
    t=np.arange(m+1)/m;v=b-a;normal=np.array([-v[1],v[0]]);base=a+t[:,None]*v
    def length(s):
        p=base+anp.concatenate([anp.zeros(1),s,anp.zeros(1)])[:,None]*normal
        v=p[1:]-p[:-1]
        if kind=='sum':
            u=anp.dot(v,ux)
            return anp.sum(anp.sqrt(anp.sum(u*u,axis=1)))
        up=p[:,0,None,None]*ux+p[:,1,None,None]*uy
        u=anp.einsum('ej,ejk->ek',v,up[:-1]);dd=anp.einsum('ej,ejk->ek',v,up[1:]-up[:-1])
        aa=anp.sum(dd*dd,axis=1)
        if anp.any(aa<=0):return anp.inf
        h=anp.sum(u*dd,axis=1)/aa;r=u-h[:,None]*dd;delta=anp.sum(r*r,axis=1)
        if anp.any(delta<=0):return anp.inf
        width=anp.sqrt(delta/aa)
        def pfun(x):return (x*anp.sqrt(aa*x*x+delta)+delta/anp.sqrt(aa)*anp.arcsinh(x/width))/2
        return anp.sum(pfun(h+1)-pfun(h))
    return length

def points(a,b,s):
    m=len(s)+1;v=b-a;normal=mp.matrix([-v[1],v[0]])
    return [a]+[a+mp.mpf(j+1)/m*v+z*normal for j,z in enumerate(s)]+[b]

def mp_edges(a,b,s,kind,ux,uy):
    pts=points(a,b,s)
    for x,y in zip(pts,pts[1:]):
        v=y-x
        u0=ux if kind=='sum' else x[0]*ux+x[1]*uy
        u1=ux if kind=='sum' else y[0]*ux+y[1]*uy
        yield u0,u1-u0,(v.T*u0).T,(v.T*(u1-u0)).T

def reference_length(a,b,s,kind,ux,uy):
    total=mp.mpf(0)
    for u0,du,u,dd in mp_edges(a,b,s,kind,ux,uy):
        if kind=='sum':total+=mp.sqrt(mp.fsum(z*z for z in u));continue
        aa=mp.fsum(z*z for z in dd)
        if aa<=0:raise ValueError('nonpositive_a')
        h=mp.fsum(x*y for x,y in zip(u,dd))/aa;r=u-h*dd;delta=mp.fsum(z*z for z in r)
        if delta<=0:raise ValueError('nonpositive_delta')
        width=mp.sqrt(delta/aa)
        def primitive(x):return (x*mp.sqrt(aa*x*x+delta)+delta/mp.sqrt(aa)*mp.asinh(x/width))/2
        total+=primitive(1+h)-primitive(h)
    return total

def main(out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for p,h in CFG['sources'].items():assert sha(ROOT.parent/p)==h,p
    data=json.loads((ROOT.parent/'H/data.json').read_text());d=load('d_k',ROOT.parent/'D/scripts/run.py');g=load('g_k',ROOT.parent/'G/scripts/run.py')
    old={r['case']:r for r in csv.DictReader((ROOT.parent/'J/results/run_v1/cases.csv').open())}
    checks=[];searches=[];vertices=[];gradients=[];segments=[];resolutions=[];cases=[]
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        finite=bool(mp.isfinite(e));ok=finite and abs(e)<=mp.mpf(tol)
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rows in [('checks',checks),('searches',searches),('vertices',vertices),('gradients',gradients),('segments',segments),('resolutions',resolutions),('cases',cases)]:table(out/(name+'.csv'),rows)
        if time.monotonic()-started>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_cases':len(cases)})
            raise TimeoutError('time budget; partial tables preserved')
    rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    prepared={}
    for state in sorted(set(k.split('/')[0] for k in CFG['cases'])):
        prepared[state]={}
        for digits in CFG['precision']:
            with mp.workdps(digits):
                theta=[mp.mpf(str(x)) for x in data['states'][state]]
                zz=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels'][CFG['panel']]]
                cv,jc,c,l=d.analytic_mp(theta,zz);prepared[state][digits]=(cv,jc,l)
    def global_spd(a,b,s,kind,ux,uy):
        ok=True;minimum=mp.inf
        for u0,du,u,dd in mp_edges(a,b,s,kind,ux,uy):
            h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h)
            ok=ok and pa['ok'] and pd['ok'];minimum=min(minimum,pa['margin'],pd['margin'])
        return ok,minimum
    def diagnose(case,m,label,s,success,f,df,hess,a,b,kind,ux,uy):
        begin=len(checks)
        with mp.workdps(80):
            smp=[mp.mpf(repr(float(z))) for z in s];gradient_mp=[];fdlow=[];value=None;valid=True
            try:
                value=reference_length(a,b,smp,kind,ux,uy);scale=max(1,abs(value))
                ok_spd,margin=global_spd(a,b,smp,kind,ux,uy)
                for j in range(len(smp)):
                    pair=[]
                    for step in CFG['mp_fd_steps']:
                        step=mp.mpf(step);left=list(smp);right=list(smp);left[j]-=step;right[j]+=step
                        pair.append((reference_length(a,b,right,kind,ux,uy)-reference_length(a,b,left,kind,ux,uy))/(2*step))
                    fdlow.append(pair[0]);gradient_mp.append(pair[1])
                gad=np.asarray(df(s),float)
                fd_error=max(abs(x-y) for x,y in zip(fdlow,gradient_mp))/scale
                ad_error=max(abs(mp.mpf(float(x))-y) for x,y in zip(gad,gradient_mp))/scale
                check(f'{case}/{m}/{label}/mp_fd',fd_error,CFG['mp_fd_agreement_tolerance'],'gradient')
                check(f'{case}/{m}/{label}/ad_gradient',ad_error,CFG['gradient_agreement_tolerance'],'gradient')
                check(f'{case}/{m}/{label}/objective',err(value,mp.mpf(float(f(s)))),CFG['objective_tolerance'],'integration')
                gm=np.array([float(z) for z in gradient_mp]);kkt=float(np.max(np.abs(s-np.clip(s-gm,-.25,.25))))/float(scale)
                free=float(np.max(np.abs(gm)))/float(scale)
                check(f'{case}/{m}/{label}/kkt',kkt,CFG['gradient_tolerance'],'stationarity')
                for j,(z,x,y) in enumerate(zip(gad,fdlow,gradient_mp)):
                    gradients.append({'case':case,'segments':m,'source':label,'index':j,'autograd':repr(float(z)),'mp_fd_1':fmt(x),'mp_fd_2':fmt(y)})
                local=checks[begin:]
                valid=bool(success and ok_spd and all(r['status']=='PASS' for r in local))
            except (ValueError,ZeroDivisionError) as ex:
                scale=mp.mpf(1);valid=False;ok_spd=False;margin=mp.nan;kkt=free=float('inf');ad_error=fd_error=mp.inf
            active=np.minimum(abs(s+.25),abs(s-.25))<=float(CFG['boundary_tolerance'])
            free_indices=np.where(~active)[0]
            try:
                hh=np.asarray(hess(s),float);hh=(hh+hh.T)/2
                eigmin=float(np.linalg.eigvalsh(hh[np.ix_(free_indices,free_indices)])[0])/float(scale) if len(free_indices) else None
            except (ValueError,np.linalg.LinAlgError):eigmin=None
            return {'reference':value,'valid':valid,'spd':ok_spd,'margin':margin,'kkt':kkt,'free_gradient':free,
                    'active':int(sum(active)),'hessian_min':eigmin,'ad_error':ad_error,'fd_error':fd_error}
    def validate_selected(case,m,s,state,ia,ib,kind):
        low={};valid=True;totals={}
        for digits in CFG['precision']:
            with mp.workdps(digits):
                cv,jc,l=prepared[state][digits]
                ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
                a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                smp=[mp.mpf(repr(float(z))) for z in s];total=mp.mpf(0)
                for index,(u0,du,u,dd) in enumerate(mp_edges(a,b,smp,kind,ux,uy)):
                    h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h)
                    q=[mp.fsum(z*z for z in u),2*mp.fsum(x*y for x,y in zip(u,dd)),mp.fsum(z*z for z in dd)]
                    name=f'{case}/{m}/{digits}/segment{index}';reason=''
                    try:
                        value=g.primitive(q);geo=g.geometry(q);qq=[g.quadrature(q,geo,rules[digits][n]) for n in [16,32,64]]
                        check(name+'/coarse',err(qq[0],qq[1]),CFG['coarse_tolerance'],'integration')
                        check(name+'/fine',err(qq[1],qq[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/primitive',err(value,qq[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/reparam',err(value,g.quadrature(q,geo,rules[digits][64],True)),CFG['fine_tolerance'],'integration')
                        total+=value
                    except (ValueError,ZeroDivisionError) as ex:value=None;reason=str(ex);valid=False
                    valid=valid and pa['ok'] and pd['ok']
                    segments.append({'case':case,'mesh_segments':m,'digits':digits,'index':index,'length':fmt(value) if value is not None else '',
                        'reason':reason,'h00_positive':pa['ok'],'det_positive':pd['ok'],'h00_margin':fmt(pa['margin']),'det_margin':fmt(pd['margin']),
                        'h00_depth':pa['depth'],'det_depth':pd['depth']})
                    if digits==80:low[index]=(value,pa['margin'],pd['margin'])
                    else:
                        oldval=low[index]
                        if value is not None and oldval[0] is not None:check(name+'/precision_length',err(value,oldval[0]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_h00',err(pa['margin'],oldval[1]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_det',err(pd['margin'],oldval[2]),CFG['precision_tolerance'],'precision')
                totals[digits]=total
                ref=reference_length(a,b,smp,kind,ux,uy)
                check(f'{case}/{m}/{digits}/reference_primitive',err(total,ref),CFG['precision_tolerance'],'precision')
        return totals[120],valid
    for case in CFG['cases']:
        state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)];case_begin=len(checks);case_res=[];previous=None;previous_value=None
        with mp.workdps(120):
            cv,jc,l=prepared[state][120];ux0=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy0=d.analytic_B(cv,jc,[0,1],kind)[0]*l
            ux_float=np.array(ux0.tolist(),float);uy_float=np.array(uy0.tolist(),float)
        with mp.workdps(80):
            cv,jc,l=prepared[state][80];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
            a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
        baseline,basevalid=validate_selected(case,1,[],state,ia,ib,kind)
        for m in CFG['segments']:
            begin=len(checks);f=make_objective(af,bf,m,kind,ux_float,uy_float);df=grad(f);hh=hessian(f);times=np.arange(1,m)/m
            if previous is None:incumbent=np.zeros(m-1)
            else:
                oldtimes=np.linspace(0,1,len(previous)+2);incumbent=np.interp(times,oldtimes,np.r_[0,previous,0])
                with mp.workdps(80):
                    inherited=reference_length(a,b,[mp.mpf(repr(float(z))) for z in incumbent],kind,ux,uy)
                    check(f'{case}/{m}/embedding',err(inherited,previous_value),CFG['embedding_tolerance'])
            starts=[amplitude*np.sin(harmonic*np.pi*times) for amplitude,harmonic in CFG['starts']]
            if previous is not None:starts.append(incumbent.copy())
            options={k:v for k,v in CFG['optimizer'].items() if k!='method'};runs=[]
            for index,initial in enumerate(starts):
                opt=minimize(f,initial,jac=df,bounds=[tuple(CFG['s_bounds'])]*(m-1),method=CFG['optimizer']['method'],options=options)
                s=np.asarray(opt.x,float);value=float(f(s));di=diagnose(case,m,'start'+str(index),s,bool(opt.success),f,df,hh,a,b,kind,ux,uy)
                searches.append({'case':case,'segments':m,'start':index,'success':bool(opt.success),'message':str(opt.message),'iterations':int(opt.nit),'nfev':int(opt.nfev),
                    'length_float':repr(value),'length_mp':fmt(di['reference']) if di['reference'] is not None else '',
                    'validated':di['valid'],'spd':di['spd'],'minimum_spd_margin':fmt(di['margin']),'kkt':repr(di['kkt']),'free_gradient':repr(di['free_gradient']),
                    'active_nodes':di['active'],'hessian_min_free':repr(di['hessian_min']),'gradient_error':fmt(di['ad_error']),'fd_consistency':fmt(di['fd_error'])})
                for j,z in enumerate(s):vertices.append({'case':case,'segments':m,'source':'start'+str(index),'index':j,'s':repr(float(z))})
                runs.append((value,s,bool(opt.success),di))
            inherited_float=float(f(incumbent));best=min(runs+[(inherited_float,incumbent,True,None)],key=lambda x:x[0] if np.isfinite(x[0]) else np.inf)
            if not np.isfinite(best[0]) or inherited_float-best[0]<=float(CFG['selection_margin'])*max(1,inherited_float):best=(inherited_float,incumbent,True,None)
            selected=best[1];di=best[3] if best[3] is not None else diagnose(case,m,'selected_incumbent',selected,True,f,df,hh,a,b,kind,ux,uy)
            for j,z in enumerate(selected):vertices.append({'case':case,'segments':m,'source':'selected','index':j,'s':repr(float(z))})
            check(f'{case}/{m}/bounds',max(0,float(np.max(np.abs(selected)))-.25),CFG['identity_tolerance'])
            value,valid=validate_selected(case,m,selected,state,ia,ib,kind)
            with mp.workdps(120):
                check(f'{case}/{m}/nonworse_straight',max(0,value-baseline)/max(1,baseline),CFG['nonworse_tolerance'])
                if previous_value is not None:check(f'{case}/{m}/nonworse_inherited',max(0,value-previous_value)/max(1,previous_value),CFG['nonworse_tolerance'])
                if kind=='sum':
                    check(f'{case}/{m}/sum_params',float(np.max(np.abs(selected))),CFG['nonworse_tolerance'])
                    check(f'{case}/{m}/sum_length',err(value,baseline),CFG['nonworse_tolerance'])
                allvalues=[z[3]['reference'] for z in runs]
                spread=(max(allvalues)-min(allvalues))/max(1,value) if all(z is not None for z in allvalues) else mp.inf
                check(f'{case}/{m}/start_spread',spread,CFG['branch_length_tolerance'],'stability')
            allvalid=all(z[2] and z[3]['valid'] for z in runs)
            branches='AGREEMENT' if spread<=mp.mpf(CFG['branch_length_tolerance']) else ('DISTINCT_STATIONARY_CANDIDATES' if allvalid else 'NUMERICAL_OR_OPTIMIZATION_LIMIT')
            local=checks[begin:]
            status='FAIL' if any(z['status']=='FAIL' for z in local) else ('INCONCLUSIVE' if not basevalid or not valid or not allvalid or not di['valid'] or any(z['status']=='INCONCLUSIVE' for z in local) else 'PASS_NUMERICAL')
            row={'case':case,'segments':m,'status':status,'length':fmt(value),'straight_length':fmt(baseline),'start_count':len(runs),
                 'validated_starts':sum(z[3]['valid'] for z in runs),'branches':branches,'start_spread':fmt(spread),'kkt':repr(di['kkt']),
                 'free_gradient':repr(di['free_gradient']),'active_nodes':di['active'],'hessian_min_free':repr(di['hessian_min'])}
            resolutions.append(row);case_res.append((row,value));previous=selected.copy();previous_value=value;checkpoint()
        refine=[]
        with mp.workdps(120):
            for j,tol in enumerate([CFG['refinement_4_8_tolerance'],CFG['refinement_8_16_tolerance']]):
                e=err(case_res[j][1],case_res[j+1][1]);check(case+f'/refinement{j}',e,tol,'refinement');refine.append(e)
        local=checks[case_begin:]
        status='FAIL' if any(z['status']=='FAIL' for z in local) or any(z[0]['status']=='FAIL' for z in case_res) else ('INCONCLUSIVE' if any(z['status']=='INCONCLUSIVE' for z in local) or any(z[0]['status']=='INCONCLUSIVE' for z in case_res) else 'PASS_NUMERICAL')
        with mp.workdps(120):change=(mp.mpf(old[case]['J8_length'])-case_res[-1][1])/mp.mpf(old[case]['J8_length'])
        cases.append({'case':case,'control':kind=='sum','J_status':old[case]['status'],'K_status':status,'K16_length':fmt(case_res[-1][1]),
                      'error_4_8':fmt(refine[0]),'error_8_16':fmt(refine[1]),'relative_change_from_J':fmt(change),'boundary':bool(case_res[-1][0]['active_nodes'])})
        checkpoint()
    cc={s:sum(r['status']==s for r in checks) for s in ['PASS','FAIL','INCONCLUSIVE']}
    counts={s:sum(r['K_status']==s for r in cases) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or cc['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'cases':len(cases),'counts':counts,'resolutions':len(resolutions),'searches':len(searches),'validated_searches':sum(r['validated'] for r in searches),
             'checks':len(checks),'check_counts':cc,'diagnostic_cases':sum(not r['control'] for r in cases),
             'resolved_J_cases':sum(not r['control'] and r['K_status']=='PASS_NUMERICAL' for r in cases),
             'branch_counts':{s:sum(r['branches']==s for r in resolutions) for s in ['AGREEMENT','DISTINCT_STATIONARY_CANDIDATES','NUMERICAL_OR_OPTIMIZATION_LIMIT']}}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'design_commit':'2a1a9d3','config_sha256':sha(ROOT/'config.json'),'script_sha256':sha(Path(__file__)),
                              'sources':CFG['sources'],'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
